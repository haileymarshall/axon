"""`python -m axon <command>` - every step of the Axon loop from the terminal."""

from __future__ import annotations

import base64

import argparse
import json
from pathlib import Path

from .config import CFG


def _near():
    from .chain import Near
    return Near()


def cmd_prepare(a):
    from . import data
    for k, v in data.prepare().items():
        print(f"{k:<14} {v}")


def cmd_prep(a):
    """Turn raw private records into training pairs on NEAR AI Cloud, after verifying its TEE attestation."""
    import json as _json
    from . import nearai
    records = Path(a.input).read_text()
    print(f"verifying {a.model} on NEAR AI Cloud (fresh nonce) before sending anything...")
    r = nearai.prep(records, niche=a.niche, model=a.model)
    for c in r["attestation"]["checks"] + ((r["answer"] or {}).get("checks") or []):
        print(f"  {'✅' if c['ok'] else '❌'} {c['check']}" + (f"  ({c['detail']})" if c["detail"] else ""))
    if not r["pairs"]:
        raise SystemExit(f"stopped: {r['error']}")
    with open(a.out, "w") as f:
        for p in r["pairs"]:
            f.write(_json.dumps(p, ensure_ascii=False) + "\n")
    print(f"{'verified' if r['ok'] else 'NOT fully verified'}: {len(r['pairs'])} training pairs written to {a.out} "
          "(only on this machine; NEAR AI Cloud and Axon keep nothing)")
    if not r["ok"]:
        raise SystemExit(1)


def cmd_vault(a):
    import uvicorn
    from .vault import create_app
    uvicorn.run(create_app(a.operator), host=a.host, port=a.port, log_level="warning")


def cmd_app(a):
    import uvicorn
    from .app import create_app
    print(f"Axon app on http://{a.host}:{a.port}")
    uvicorn.run(create_app(a.treasury, a.demo_payer), host=a.host, port=a.port, log_level="warning")


def cmd_create_model(a):
    import httpx
    from .chain import near_to_yocto
    info = httpx.get(f"{CFG.vault_url}/info", timeout=30).json()
    res = _near().call(a.creator, "create_model", {
        "name": a.name, "domain": a.domain, "description": a.description, "base_model": a.base_model or info["base_model"],
        "combiner_key": info["combiner_key"], "combiner_code_hash": info["code_hash"],
        "query_price": str(near_to_yocto(a.price)), "compute_fee": str(near_to_yocto(a.compute_fee)),
    }, deposit_yocto=near_to_yocto(a.budget), gas_tgas=50)
    print(f"model {res['value']} created  tx {res['tx']}")


def cmd_set_combiner(a):
    import httpx
    info = httpx.get(f"{CFG.vault_url}/info", timeout=30).json()
    res = _near().call(a.creator, "set_combiner", {"model_id": a.model, "combiner_key": info["combiner_key"],
                                                    "combiner_code_hash": info["code_hash"]}, gas_tgas=30)
    print(f"model {a.model} now bound to vault key {info['combiner_key'][:16]}… code {info['code_hash'][:16]}…  tx {res['tx']}")


def cmd_set_test(a):
    """Seal a hidden test file to the vault and sign the hand-over with the creator's key (NEP-413, like a wallet)."""
    import os

    import base58
    import httpx
    from nacl.signing import SigningKey

    from . import crypto
    from .chain import credentials

    text = Path(a.file).read_text()
    info = httpx.get(f"{CFG.vault_url}/info", timeout=30).json()
    sealed = crypto.seal(info["box_key"], text.encode())
    raw = base58.b58decode(credentials(a.creator).replace("ed25519:", ""))
    key = SigningKey(raw[:32])
    nonce = os.urandom(32)
    msg = crypto.test_set_message(a.model, CFG.contract_id, sealed)
    sig = key.sign(crypto.nep413_hash(msg, nonce, CFG.contract_id)).signature
    r = httpx.post(f"{CFG.vault_url}/models/{a.model}/test", timeout=60, json={
        "creator": a.creator, "sealed": crypto.b64(sealed), "public_key": "ed25519:" + base58.b58encode(raw[32:]).decode(),
        "signature": base64.b64encode(sig).decode(), "nonce": base64.b64encode(nonce).decode()})
    print(r.status_code, r.text)


def cmd_contribute(a):
    from .contribute import contribute
    contribute(a.model, a.account, Path(a.data))


def cmd_close_round(a):
    import httpx
    from .crypto import admin_token
    r = httpx.post(f"{CFG.vault_url}/models/{a.model}/close-round", json={"compute_provider": a.compute_provider},
                   headers={"Authorization": f"Bearer {admin_token()}"}, timeout=1800)
    if r.status_code != 200:
        raise SystemExit(f"{r.status_code} {r.text}")
    out = r.json()
    print("\n".join(out["log"]))
    p = out["payload"]
    print(f"round {p['round']}: test loss {p['base_eval_loss_milli'] / 1000:.3f} -> {p['eval_loss_milli'] / 1000:.3f}")
    for res in p["results"]:
        print(f"  {res['account']:<40} improvement {int(res['improvement_micro']) / 1e6:+.4f}  -> {res['improvement_micro']} shares")
    print(f"signed by vault, recorded on-chain  tx {out.get('tx')}")


def cmd_ask(a):
    import httpx
    near = _near()
    m = near.view("get_model", {"model_id": a.model})
    from .crypto import query_hash
    paid = near.call(a.account, "pay_for_query", {"model_id": a.model, "source": "cli", "query_hash": query_hash(a.question)},
                     deposit_yocto=int(m["query_price"]), gas_tgas=30)
    print(f"paid {int(m['query_price']) / 1e24} NEAR  tx {paid['tx']}")
    r = httpx.post(f"{CFG.vault_url}/models/{a.model}/ask", json={"question": a.question, "payment_tx": paid["tx"], "payer": a.account}, timeout=600)
    print(r.json().get("answer", r.text))


def cmd_withdraw(a):
    res = _near().call(a.account, "withdraw", {"model_id": a.model}, gas_tgas=30)
    print(f"withdrawn  tx {res['tx']}")


def cmd_status(a):
    from .chain import yocto_to_near
    near = _near()
    m = near.view("get_model", {"model_id": a.model})
    if m is None:
        raise SystemExit("no such model")
    print(f"{m['name']} ({m['domain']}) base={m['base_model']} rounds={m['rounds']} "
          f"loss={m['base_eval_loss_milli']}->{m['eval_loss_milli']} queries={m['queries']} "
          f"revenue={yocto_to_near(m['total_revenue']):.4f} NEAR budget={yocto_to_near(m['budget']):.3f} NEAR")
    total = int(m["total_shares"]) or 1
    for c in m["contributors"]:
        e = near.view("earnings_of", {"model_id": a.model, "account": c["account"]})
        print(f"  {c['account']:<40} shares {int(c['shares']):>8} ({100 * int(c['shares']) / total:5.1f}%)  earned {yocto_to_near(e):.5f} NEAR")
    if a.json:
        print(json.dumps(m, indent=1))


def cmd_run_start(a):
    from . import runs
    env = runs.start(Path(a.dir))
    print(f"run {Path(a.dir).name}: {(env['hardware']['gpu'] or {}).get('name') or 'CPU'}, base model {env['config']['base_model']}")


def cmd_run_finish(a):
    from . import runs
    s = runs.finish(Path(a.dir), a.model, a.seconds)
    print(f"run {s['run_id']} recorded: loss {s['hidden_test_loss']['before']:.3f} -> {s['hidden_test_loss']['after']:.3f}; see {a.dir}/summary.md and RUNS.md")


def main(argv=None):
    p = argparse.ArgumentParser(prog="axon", description="Train AI together on private data, co-own the model (NEAR).")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("prepare-data", help="build the demo contributors' private datasets").set_defaults(fn=cmd_prepare)

    s = sub.add_parser("prep", help="turn raw private records into training pairs in NEAR AI Cloud's attested TEE")
    s.add_argument("input", help="text file with your raw records (e.g. samples/clinic-notes.txt)")
    s.add_argument("--niche", default="rare-diseases", choices=["rare-diseases", "security", "basque"])
    s.add_argument("--out", default="pairs.jsonl")
    s.add_argument("--model", default="Qwen/Qwen3.8-27B", help="a model NEAR AI Cloud runs in its own TEE")
    s.set_defaults(fn=cmd_prep)

    s = sub.add_parser("vault", help="run the sealed combiner (TEE service)")
    s.add_argument("--operator", help="NEAR account that relays signed results on-chain")
    s.add_argument("--host", default="127.0.0.1")
    s.add_argument("--port", type=int, default=8700)
    s.set_defaults(fn=cmd_vault)

    s = sub.add_parser("app", help="run the web app")
    s.add_argument("--treasury", help="NEAR account receiving Intents payments")
    s.add_argument("--demo-payer", help="account that pays a few rate-limited demo questions")
    s.add_argument("--host", default="127.0.0.1")
    s.add_argument("--port", type=int, default=8800)
    s.set_defaults(fn=cmd_app)

    s = sub.add_parser("create-model", help="create a model on-chain, bound to the running vault's key")
    s.add_argument("--creator", required=True)
    s.add_argument("--name", required=True)
    s.add_argument("--domain", default="general")
    s.add_argument("--description", default="")
    s.add_argument("--price", default="0.01", help="NEAR per query")
    s.add_argument("--compute-fee", default="0.05", help="NEAR paid to the compute provider per round")
    s.add_argument("--budget", default="0.5", help="NEAR deposited as training budget")
    s.add_argument("--base-model", default="", help="open base model (one of the vault's /info bases); default: the vault's default")
    s.set_defaults(fn=cmd_create_model)

    s = sub.add_parser("set-combiner", help="re-bind a model to the running vault (after a vault upgrade)")
    s.add_argument("--model", type=int, required=True)
    s.add_argument("--creator", required=True)
    s.set_defaults(fn=cmd_set_combiner)

    s = sub.add_parser("set-test", help="seal a model's hidden test set to the vault, signed by the creator")
    s.add_argument("--model", type=int, required=True)
    s.add_argument("--creator", required=True)
    s.add_argument("--file", required=True, help='jsonl, one {"q": ..., "a": ...} per line')
    s.set_defaults(fn=cmd_set_test)

    s = sub.add_parser("contribute", help="train locally on private data and send a sealed update")
    s.add_argument("--model", type=int, required=True)
    s.add_argument("--account", required=True)
    s.add_argument("--data", required=True)
    s.set_defaults(fn=cmd_contribute)

    s = sub.add_parser("close-round", help="vault merges + scores updates and records ownership on-chain")
    s.add_argument("--model", type=int, required=True)
    s.add_argument("--compute-provider")
    s.set_defaults(fn=cmd_close_round)

    s = sub.add_parser("ask", help="pay for and ask a question")
    s.add_argument("--model", type=int, required=True)
    s.add_argument("--account", required=True)
    s.add_argument("question")
    s.set_defaults(fn=cmd_ask)

    s = sub.add_parser("withdraw", help="withdraw your earnings")
    s.add_argument("--model", type=int, required=True)
    s.add_argument("--account", required=True)
    s.set_defaults(fn=cmd_withdraw)

    s = sub.add_parser("status", help="show a model's owners and earnings")
    s.add_argument("--model", type=int, required=True)
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_status)

    s = sub.add_parser("run-start", help="start a published run record (hardware + config)")
    s.add_argument("--dir", required=True)
    s.set_defaults(fn=cmd_run_start)

    s = sub.add_parser("run-finish", help="finish a run record: results, sample answers, add to RUNS.md")
    s.add_argument("--dir", required=True)
    s.add_argument("--model", type=int, required=True)
    s.add_argument("--seconds", type=int, default=0)
    s.set_defaults(fn=cmd_run_finish)

    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()

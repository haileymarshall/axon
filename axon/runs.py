"""Run records: every training run is saved under runs/<id>/ and listed in RUNS.md, so results are public
and checkable. A record holds the hardware, config, full log, per-round loss, each contributor's Shapley
shares, the on-chain transactions, and the same questions answered by the base model and the trained one.
"""

from __future__ import annotations

import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from .config import CFG, ROOT

RUNS_MD = ROOT / "RUNS.md"
# Questions asked to the base model and the trained model in every run: reworded questions about facts in
# the contributors' data (written by `data.prepare` to data/probes.json, each with the reference answer).
DEFAULT_PROBES = [{"q": "What are the symptoms of type 2 diabetes?"}]


def probes(domain: str | None = None) -> list[dict]:
    from . import data

    path = data.paths(domain)["probes"]
    return json.loads(path.read_text()) if path.exists() else DEFAULT_PROBES


def _sh(*cmd: str) -> str:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=20).stdout.strip()
    except Exception:
        return ""


def hardware() -> dict:
    import torch

    gpu = None
    if torch.cuda.is_available():
        p = torch.cuda.get_device_properties(0)
        gpu = {"name": p.name, "memory_gb": round(p.total_memory / 2**30, 1), "count": torch.cuda.device_count(),
               "cuda": torch.version.cuda, "nvidia_smi": _sh("nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader")}
    return {"gpu": gpu, "cpu": platform.processor() or platform.machine(), "cpu_count": __import__("os").cpu_count(),
            "os": platform.platform(), "python": platform.python_version(), "torch": torch.__version__}


def start(run_dir: Path) -> dict:
    """Write env.json at the start of a run."""
    run_dir.mkdir(parents=True, exist_ok=True)
    env = {
        "started_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "hardware": hardware(),
        "config": {k: str(v) for k, v in CFG.__dict__.items() if k not in ("data_dir", "state_dir")},
        "git_commit": _sh("git", "-C", str(ROOT), "rev-parse", "--short", "HEAD") or None,
    }
    (run_dir / "env.json").write_text(json.dumps(env, indent=1))
    return env


KIND_LABELS = {"gene": "right gene", "inheritance": "right inheritance pattern", "cwe": "right weakness type (CWE)",
               "chrf": "translation score (chrF, 0-100)"}


def _trained_adapter(model_id: int, m: dict):
    """The trained adapter: from the local vault's disk, or (vault in a TEE) downloaded from the vault the way a
    contributor does, with a contributor's device-key signature."""
    import time

    import httpx

    from . import crypto, ml
    from .vault import VAULT_DIR

    local = VAULT_DIR / f"model-{model_id}" / "global.safetensors"
    if local.exists():
        return ml.adapter_from_bytes(local.read_bytes())
    for c in m["contributors"]:
        key_file = CFG.state_dir / "keys" / f"device-{c['account']}.json"
        if not key_file.exists():
            continue
        device = crypto.load_or_create_signing_key(f"device-{c['account']}")
        ts = int(time.time())
        r = httpx.get(f"{CFG.vault_url}/models/{model_id}/global", timeout=300,
                      params={"account": c["account"], "ts": ts, "sig": crypto.sign_hex(device, crypto.download_message(model_id, c["account"], ts))})
        if r.status_code == 200:
            blob = r.content
            if m.get("adapter_hash") and ml.adapter_hash(ml.adapter_from_bytes(blob)) != m["adapter_hash"]:
                raise SystemExit("downloaded adapter does not match the on-chain adapter hash")
            return ml.adapter_from_bytes(blob)
    raise SystemExit("trained adapter not available locally and no contributor key to download it")


def recall(answers: list[dict]) -> dict:
    """How many showcase facts each model got right, per kind of question."""
    kinds = [k for k in KIND_LABELS if any(a.get("kind") == k for a in answers)]
    out = {}
    for who in ("base_model", "axon_trained"):
        r = {}
        for kind in kinds:
            if kind == "chrf":  # a score, not right/wrong: report the mean, and exact matches
                g = [a["graded"][who] for a in answers if a.get("graded") and a.get("kind") == kind]
                r[kind], r[f"{kind}_of"] = round(sum(x["chrf"] for x in g) / max(len(g), 1), 1), len(g)
                r["exact"] = sum(x["exact"] for x in g)
                continue
            g = [a["graded"][who]["correct"] for a in answers if a.get("graded") and a.get("kind") == kind]
            r[kind], r[f"{kind}_of"] = sum(g), len(g)
        out[who] = r
    return out


def recall_line(r: dict) -> str:
    if not r or not r.get("base_model"):
        return ""
    b, t = r["base_model"], r["axon_trained"]
    parts = [(f"Mean {KIND_LABELS[k]} on {b[k + '_of']} sentences: base model **{b[k]}**, Axon-trained **{t[k]}** "
              f"(exact matches {b['exact']} → {t['exact']})." if k == "chrf" else
              f"{KIND_LABELS[k].capitalize()}: base model **{b[k]}/{b[k + '_of']}**, Axon-trained **{t[k]}/{t[k + '_of']}**.")
             for k in KIND_LABELS if k + "_of" in b]
    return "* **Facts recalled.** " + " ".join(parts) if parts else ""


def probe_lines(probes: list[dict]) -> list[str]:
    flat = lambda t: " ".join(str(t).split())
    mark = lambda g: (f" (chrF {g['chrf']})" if "chrf" in g else (" ✅" if g["correct"] else " ❌")) if g and "correct" in g else ""
    lines = []
    for p in probes:
        who = f" *(from {p['contributor']}'s data)*" if p.get("contributor") else ""
        g = p.get("graded") or {}
        lines += [f"**Q: {p['question']}**{who}", ""]
        if p.get("kind") == "cwe":
            lines += [f"* Right answer: **{p.get('answer_label') or p.get('answer')}**"]
        elif p.get("kind") == "chrf":
            lines += [f"* Human translation: **{p.get('answer')}**"]
        elif p.get("kind"):
            lines += [f"* Answer in the data: {'gene **' + p['gene'] + '**' if p['kind'] == 'gene' else '**' + p['inheritance'] + '**'}"]
        lines += [f"* Base{mark(g.get('base_model'))}: {flat(p['base_model'])}",
                  f"* Axon-trained{mark(g.get('axon_trained'))}: {flat(p['axon_trained'])}"]
        if p.get("reference"):
            lines += [f"* Reference: {flat(p['reference'])}"]
        lines += [""]
    return lines


def finish(run_dir: Path, model_id: int, wall_seconds: int) -> dict:
    """Write summary.json + summary.md for a finished run and add it to RUNS.md."""
    from . import data, ml
    from .chain import Near, yocto_to_near
    from .vault import VAULT_DIR

    env = json.loads((run_dir / "env.json").read_text())
    near = Near()
    m = near.view("get_model", {"model_id": model_id})
    rounds = near.view("get_rounds", {"model_id": model_id})
    total = int(m["total_shares"]) or 1

    # Same questions, base model vs trained model (run where the vault runs, which holds the weights).
    engine = ml.Engine()
    trained = _trained_adapter(model_id, m)
    answers = [{"question": p["q"], "contributor": p.get("owner"), "disease": p.get("disease") or p.get("label"), "reference": p.get("reference"),
                "answer": p.get("answer"), "answer_label": p.get("answer_label"), "why": p.get("why"),
                "base_model": engine.generate(p["q"], engine.initial), "axon_trained": engine.generate(p["q"], trained)}
               for p in probes(m.get("domain"))]
    for a, p in zip(answers, probes(m.get("domain"))):
        a["graded"] = {"base_model": data.grade(a["base_model"], p), "axon_trained": data.grade(a["axon_trained"], p)}
        a["gene"], a["inheritance"], a["kind"] = p.get("gene"), p.get("inheritance"), p.get("kind")

    gpu = (env["hardware"]["gpu"] or {}).get("name")
    summary = {
        "run_id": run_dir.name,
        "started_at": env["started_at"],
        "wall_minutes": round(wall_seconds / 60, 1),
        "hardware": gpu or f"CPU ({env['hardware']['cpu_count']} cores)",
        "base_model": m["base_model"],
        "network": CFG.network,
        "contract": near.contract_id,
        "model_id": model_id,
        "hidden_test_loss": {"before": m["base_eval_loss_milli"] / 1000, "after": m["eval_loss_milli"] / 1000},
        "rounds": [{"round": r["round"], "test_loss": r["eval_loss_milli"] / 1000, "adapter_hash": r["adapter_hash"],
                    "shares": {x["account"].split(".")[0]: int(x["shares"]) for x in r["results"]}}
                   for r in rounds],
        "ownership": {c["account"].split(".")[0]: round(100 * int(c["shares"]) / total, 1) for c in m["contributors"]},
        "queries_paid": m["queries"],
        "revenue_near": yocto_to_near(m["total_revenue"]),
        "probes": answers,
        "recall": recall(answers),
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=1))
    (run_dir / "summary.md").write_text(_markdown(summary))
    _add_to_index(summary)
    return summary


def _markdown(s: dict) -> str:
    ex = "https://testnet.nearblocks.io" if s["network"] == "testnet" else "https://nearblocks.io"
    lines = [
        f"# Run {s['run_id']}", "",
        f"* Hardware: **{s['hardware']}** · base model `{s['base_model']}` · wall time {s['wall_minutes']} min",
        f"* Contract: [`{s['contract']}`]({ex}/address/{s['contract']}) ({s['network']}), model id {s['model_id']}",
        f"* Hidden-test loss: **{s['hidden_test_loss']['before']:.3f} → {s['hidden_test_loss']['after']:.3f}**",
        f"* Paid queries: {s['queries_paid']} · paid to owners {s['revenue_near']:.4f} NEAR (after the 5% platform fee)", "",
        "## Ownership", "", "| Contributor | Share |", "|---|---|",
        *[f"| {k} | {v}% |" for k, v in s["ownership"].items()], "",
        "## Rounds", "", "| Round | Test loss | Shares minted | Adapter hash |", "|---|---|---|---|",
        *[f"| {r['round']} | {r['test_loss']:.3f} | {', '.join(f'{k} {v}' for k, v in r['shares'].items())} | `{r['adapter_hash'][:16]}…` |" for r in s["rounds"]], "",
        "## Same question, base model vs Axon-trained model", "",
        "Reworded questions about facts in the contributors' private data. *Reference* is the answer in that data.", "",
        recall_line(s.get("recall")), "",
    ]
    lines += probe_lines(s["probes"])
    lines += ["Full output: `log.txt`. Hardware and config: `env.json`. Transactions are in the log and on the explorer.", ""]
    return "\n".join(lines)


def _add_to_index(s: dict) -> None:
    if not RUNS_MD.exists():
        RUNS_MD.write_text(
            "# Training runs\n\nEvery Axon training run, published as it happened: hardware, logs, on-chain results and "
            "sample answers. Each row links to its full record in `runs/`.\n\n"
            "| Run | Hardware | Base model | Rounds | Hidden-test loss | Time | Ownership |\n|---|---|---|---|---|---|---|\n")
    own = ", ".join(f"{k} {v}%" for k, v in s["ownership"].items())
    row = (f"| [{s['run_id']}](runs/{s['run_id']}/summary.md) | {s['hardware']} | `{s['base_model']}` | {len(s['rounds'])} | "
           f"{s['hidden_test_loss']['before']:.3f} → {s['hidden_test_loss']['after']:.3f} | {s['wall_minutes']} min | {own} |\n")
    with RUNS_MD.open("a") as f:
        f.write(row)

"""Private data prep on NEAR AI Cloud, with attestation checked before any data is sent.

Real contributors hold messy private records (clinic notes, incident reports), not training pairs. `prep()` sends those
records to an open model that NEAR AI Cloud runs inside a TEE (Intel TDX CPU + NVIDIA confidential-computing GPU), and
gets back question/answer pairs with patient identifiers removed. The pairs are then used to train locally, as before.

Order of operations, so no data reaches a machine we have not checked:
  1. `attest()`: fetch the attestation report with a fresh random nonce and verify it (method from
     https://docs.near.ai/cloud/verification): genuine Intel TDX quotes (gateway + model), each quote binds its signing
     key and our nonce, no debug mode, app config hash matches the quote, genuine NVIDIA GPU attestation with our nonce.
  2. Only if every check passes: send the records (`chat()`).
  3. Fetch the response signature and check it was signed by the attested model key over the hashes of our exact
     request and response bytes.

Nothing is stored here: no files, no logs, no caches. Records and pairs live only in memory for the call and are returned
to the caller. Depends only on httpx, dcap-qvl and eth-account (no ML stack), so the website's serverless function can
import this file as is.
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import os
import re
import secrets
import time
from pathlib import Path

import httpx

API = os.environ.get("NEARAI_API", "https://cloud-api.near.ai/v1")
MODEL = os.environ.get("NEARAI_MODEL", "Qwen/Qwen3.8-27B")
NRAS = "https://nras.attestation.nvidia.com/v3/attest/gpu"


def api_key() -> str:
    k = os.environ.get("NEARAI_API_KEY", "").strip()
    if not k:
        p = Path(os.environ.get("NEARAI_KEY_FILE", Path.home() / ".nearai_key"))
        k = p.read_text().strip() if p.exists() else ""
    if not k:
        raise RuntimeError("no NEAR AI Cloud API key: set NEARAI_API_KEY or save it in ~/.nearai_key")
    return k


def _check(checks: list, name: str, ok: bool, detail: str = "") -> bool:
    checks.append({"check": name, "ok": bool(ok), "detail": detail})
    return bool(ok)


# ---------------------------------------------------------------- attestation

def _verify_quote(quote_hex: str) -> dict:
    import dcap_qvl

    v = asyncio.run(dcap_qvl.get_collateral_and_verify(bytes.fromhex(quote_hex)))
    td = json.loads(v.to_json())["report"]["TD10"]
    return {"status": v.status, "advisories": list(v.advisory_ids or []), "td": td}


def _bound_identity(addr: str) -> bytes:
    raw = bytes.fromhex(addr.removeprefix("0x"))
    return raw.ljust(32, b"\0")


def _compose_ok(info: dict, mr_config_id: str) -> tuple[bool, str]:
    tcb = info.get("tcb_info")
    if isinstance(tcb, str):
        tcb = json.loads(tcb)
    compose = (tcb or {}).get("app_compose")
    if not compose:
        return False, "no app_compose in tcb_info"
    h = hashlib.sha256(compose.encode()).digest()
    want = (b"\x01" + h).ljust(48, b"\0").hex()
    return mr_config_id.lower() == want, f"sha256(app_compose) {h.hex()[:16]}…"


def _quote_checks(checks: list, who: str, att: dict, nonce: str) -> None:
    try:
        q = _verify_quote(att["intel_quote"])
    except Exception as e:  # noqa: BLE001
        _check(checks, f"{who}: genuine Intel TDX quote", False, f"{type(e).__name__}: {e}")
        return
    td = q["td"]
    _check(checks, f"{who}: genuine Intel TDX quote", q["status"] in ("UpToDate", "SWHardeningNeeded", "ConfigurationAndSWHardeningNeeded"),
           f"Intel status {q['status']}" + (f", advisories {', '.join(q['advisories'])}" if q["advisories"] else ""))
    want = (_bound_identity(att["signing_address"]) + bytes.fromhex(nonce)).hex()
    _check(checks, f"{who}: quote binds its signing key and our fresh nonce", td["report_data"].lower() == want,
           f"key {att['signing_address'][:12]}…, nonce {nonce[:12]}…")
    attrs = bytes.fromhex(td["td_attributes"])
    _check(checks, f"{who}: not in debug mode", not (attrs[0] & 1), "TD attributes debug bit is 0")
    ok, d = _compose_ok(att.get("info") or {}, td["mr_config_id"])
    _check(checks, f"{who}: app configuration matches the quote", ok, d)


def _gpu_checks(checks: list, att: dict, nonce: str) -> None:
    payload = att.get("nvidia_payload")
    if not payload:
        _check(checks, "GPU: genuine NVIDIA confidential-computing attestation", False, "no nvidia_payload")
        return
    body = json.loads(payload) if isinstance(payload, str) else payload
    if not _check(checks, "GPU: evidence carries our nonce", str(body.get("nonce", "")).lower() == nonce, f"nonce {nonce[:12]}…"):
        return
    try:
        r = httpx.post(NRAS, json=body, headers={"Accept": "application/json"}, timeout=60)
        r.raise_for_status()
        token = r.json()[0][1]
        part = token.split(".")[1]
        claims = json.loads(base64.urlsafe_b64decode(part + "=" * (-len(part) % 4)))
    except Exception as e:  # noqa: BLE001
        _check(checks, "GPU: genuine NVIDIA confidential-computing attestation", False, f"NVIDIA NRAS: {type(e).__name__}: {e}")
        return
    ngpu = len(body.get("evidence_list") or [])
    _check(checks, "GPU: genuine NVIDIA confidential-computing attestation", claims.get("x-nvidia-overall-att-result") is True,
           f"NVIDIA NRAS verdict for {ngpu} GPU(s)")
    _check(checks, "GPU: NVIDIA's verdict is for our nonce", str(claims.get("eat_nonce", "")).lower() == nonce, "")


def attest(model: str = MODEL, key: str | None = None) -> dict:
    """Fetch and verify the attestation for `model`. Returns {ok, model, nonce, signing_address, checks, at}."""
    key = key or api_key()
    nonce = secrets.token_hex(32)
    checks: list = []
    r = httpx.get(f"{API}/attestation/report", params={"model": model, "signing_algo": "ecdsa", "nonce": nonce},
                  headers={"Authorization": f"Bearer {key}"}, timeout=60)
    r.raise_for_status()
    rep = r.json()
    gw = rep.get("gateway_attestation") or {}
    _check(checks, "gateway: answered with our nonce", str(gw.get("request_nonce", "")).lower() == nonce, "")
    _quote_checks(checks, "gateway", gw, nonce)
    ms = [m for m in rep.get("model_attestations") or [] if m.get("model_name") == model and m.get("intel_quote")]
    signer = None
    if _check(checks, "model: runs in NEAR AI Cloud's own TEE", bool(ms), f"{len(ms)} attested instance(s) of {model}"):
        m = ms[0]
        signer = m["signing_address"]
        _check(checks, "model: answered with our nonce", str(m.get("request_nonce", "")).lower() == nonce, "")
        _quote_checks(checks, "model", m, nonce)
        _gpu_checks(checks, m, nonce)
    signers = [m["signing_address"].lower() for m in ms]
    return {"ok": all(c["ok"] for c in checks), "model": model, "nonce": nonce, "signing_address": signer,
            "signers": signers, "checks": checks, "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}


# ---------------------------------------------------------------- signed chat

def chat(messages: list, model: str = MODEL, key: str | None = None, signers: list | None = None,
         max_tokens: int = 4000) -> dict:
    """One chat completion; returns {text, chat_id, checks}. `signers` = attested model keys from `attest()`."""
    key = key or api_key()
    body = json.dumps({"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": 0.2, "chat_template_kwargs": {"enable_thinking": False},
                       "stream": False}, separators=(",", ":")).encode()
    h = {"Authorization": f"Bearer {key}", "Content-Type": "application/json", "Accept-Encoding": "identity",
         "x-no-aliasing": "true"}
    r = httpx.post(f"{API}/chat/completions", content=body, headers=h, timeout=300)
    r.raise_for_status()
    raw = r.content
    resp = json.loads(raw)
    checks: list = []
    req_hash, resp_hash = hashlib.sha256(body).hexdigest(), hashlib.sha256(raw).hexdigest()
    sig = None
    for _ in range(6):
        s = httpx.get(f"{API}/signature/{resp['id']}", params={"model": model, "signing_algo": "ecdsa"},
                      headers={"Authorization": f"Bearer {key}", "Accept": "application/json"}, timeout=30)
        if s.status_code == 404:
            time.sleep(1)
            continue
        s.raise_for_status()
        sig = s.json()
        break
    if _check(checks, "answer: signature available", bool(sig and sig.get("signature")), (sig or {}).get("signature_kind", "")):
        from eth_account import Account
        from eth_account.messages import encode_defunct

        rec = Account.recover_message(encode_defunct(text=sig["text"]), signature=sig["signature"])
        _check(checks, "answer: signed by the attested model key", rec.lower() == sig["signing_address"].lower()
               and (signers is None or rec.lower() in signers), f"signer {rec[:12]}…")
        parts = sig["text"].split(":")
        _check(checks, "answer: signature covers our exact request and response", parts[-2:] == [req_hash, resp_hash]
               and (len(parts) == 2 or parts[0] == model), f"sha256 {req_hash[:10]}… / {resp_hash[:10]}…")
    text = resp["choices"][0]["message"].get("content") or ""
    return {"text": text, "chat_id": resp["id"], "checks": checks}


# ---------------------------------------------------------------- data prep

PROMPTS = {
    "rare-diseases": (
        "You turn a clinic's private case notes about rare genetic diseases into training data for a small medical "
        "model. Write question/answer pairs about the DISEASE only (what it is, inheritance pattern, gene, symptoms, "
        "how common it is), in the style 'What is the inheritance pattern of X?' / 'X is inherited in an autosomal "
        "recessive pattern...'. Never include a patient's name, initials, age, date, place, record number or any detail "
        "that could identify a person."),
    "security": (
        "You turn a security team's private incident or bug reports into training data for a vulnerability "
        "classifier. For each distinct weakness write a pair: q = a neutral one-paragraph description of the "
        "vulnerability, a = its CWE id and name (e.g. 'CWE-79: Improper Neutralization of Input During Web Page "
        "Generation'). Remove company names, hostnames, IPs, people and secrets."),
    "basque": (
        "You turn a Basque speaker's private notes or messages into English to Basque translation pairs. q = a short "
        "English sentence, a = its natural Basque translation. Remove names of real people and places."),
}


# Same question wording the demo models were trained and scored with (axon/data.py SECURITY_Q, BASQUE_Q).
WORDING = {
    "security": "Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.\n\nVulnerability: {q}",
    "basque": "Translate into Basque: {q}",
}


def _parse_pairs(text: str) -> list:
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()
    m = re.search(r"\{.*\}|\[.*\]", text, flags=re.S)
    if not m:
        return []
    try:
        d = json.loads(m.group(0))
    except json.JSONDecodeError:
        return []
    items = d.get("pairs", []) if isinstance(d, dict) else d
    return [{"q": str(p["q"]).strip(), "a": str(p["a"]).strip()} for p in items
            if isinstance(p, dict) and p.get("q") and p.get("a")]


def prep(records: str, niche: str = "rare-diseases", model: str = MODEL, key: str | None = None) -> dict:
    """Verify the TEE, then turn raw private records into training pairs. Returns {ok, pairs, attestation, answer}."""
    key = key or api_key()
    att = attest(model, key)
    if not att["ok"]:
        return {"ok": False, "pairs": [], "attestation": att, "answer": None,
                "error": "attestation failed: no data was sent"}
    sys_prompt = PROMPTS.get(niche, PROMPTS["rare-diseases"]) + (
        ' Cover EVERY note or record in the input, not only the first: write 3 to 6 pairs for each one. Reply with JSON '
        'only: {"pairs": [{"q": "...", "a": "..."}]}.')
    out = chat([{"role": "system", "content": sys_prompt}, {"role": "user", "content": records}],
               model=model, key=key, signers=att["signers"])
    pairs = [{"q": WORDING.get(niche, "{q}").format(q=p["q"]), "a": p["a"]} for p in _parse_pairs(out["text"])]
    ok = all(c["ok"] for c in out["checks"]) and bool(pairs)
    return {"ok": ok, "pairs": pairs, "attestation": att, "answer": {"chat_id": out["chat_id"], "checks": out["checks"]},
            "error": None if pairs else "the model returned no usable pairs"}

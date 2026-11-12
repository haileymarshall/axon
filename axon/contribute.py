"""Contributor client. Runs on the contributor's own machine; the data file never leaves it.

    1. registers a device key on-chain (`join_model`) the first time,
    2. downloads the current shared adapter from the vault,
    3. fine-tunes it locally on the private data,
    4. signs the new adapter with the device key and seals it to the vault's encryption key,
    5. uploads only that sealed update.
"""

from __future__ import annotations

import time
from pathlib import Path

import httpx

from . import crypto, data, ml
from .chain import Near
from .config import CFG


def contribute(model_id: int, account: str, data_file: Path, engine: ml.Engine | None = None,
               vault_url: str = CFG.vault_url, log=print, seed: int = 0) -> dict:
    near = Near()
    device = crypto.load_or_create_signing_key(f"device-{account}")
    model = near.view("get_model", {"model_id": model_id})
    if model is None:
        raise SystemExit(f"model {model_id} does not exist")
    if not any(c["account"] == account for c in model["contributors"]):
        log(f"[{account}] joining model {model_id} on-chain with device key {crypto.pubkey_hex(device)[:12]}…")
        near.call(account, "join_model", {"model_id": model_id, "device_key": crypto.pubkey_hex(device)}, gas_tgas=30)

    info = httpx.get(f"{vault_url}/info", timeout=30).json()
    ts = int(time.time())
    sig = crypto.sign_hex(device, crypto.download_message(model_id, account, ts))
    r = httpx.get(f"{vault_url}/models/{model_id}/global", params={"account": account, "ts": ts, "sig": sig}, timeout=120)
    if r.status_code != 200:
        raise SystemExit(f"vault refused the model download: {r.status_code} {r.text}")
    start = ml.adapter_from_bytes(r.content)
    rows = data.read_jsonl(data_file)
    log(f"[{account}] training locally on {len(rows)} private examples (data stays on this machine)")
    engine = engine or ml.Engine()
    adapter = engine.train(rows, start, seed=seed, log=lambda s, l: log(f"[{account}]   step {s:>3}  loss {l:.3f}"))

    blob = ml.adapter_bytes(adapter)
    sha = crypto.sha256_hex(blob)
    round_ = model["rounds"] + 1
    body = {
        "account": account,
        "round": round_,
        "adapter_sha": sha,
        "signature": crypto.sign_hex(device, crypto.update_message(model_id, round_, account, sha)),
        "sealed": crypto.b64(crypto.seal(info["box_key"], blob)),
    }
    r = httpx.post(f"{vault_url}/models/{model_id}/updates", json=body, timeout=120)
    if r.status_code != 200:
        raise SystemExit(f"vault rejected update: {r.status_code} {r.text}")
    log(f"[{account}] sealed update ({len(blob) // 1024} KB) accepted for round {round_}")
    return r.json()

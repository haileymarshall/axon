"""Verify that the Axon vault really runs this repo's code inside Intel TDX hardware.

    python scripts/verify_tee.py https://<vault-url>
    python scripts/verify_tee.py runs/tee-mainnet/vault-info-20261113.json --model 4   # offline, from saved evidence

Checks, with nothing taken on trust:
  1. the vault's code hash equals the hash of the vault source files in this checkout,
  2. the hardware quote's report_data commits to sha256(vault signing key || code hash),
  3. the quote is a genuine Intel TDX quote (Phala's public verifier checks Intel's certificate chain),
  4. (optional, --model N) the NEAR contract only accepts results signed by that same key.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from axon.vault import code_hash  # noqa: E402

VERIFIER = "https://cloud-api.phala.network/api/v1/attestations/verify"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("vault_url", help="the vault's URL, or a saved /info JSON file (offline check)")
    ap.add_argument("--model", type=int, help="also check the on-chain model is bound to this vault's key")
    ap.add_argument("--save", help="write the evidence (info + verifier result) to this JSON file")
    a = ap.parse_args()

    if Path(a.vault_url).is_file():
        saved = json.loads(Path(a.vault_url).read_text())
        info = saved.get("info", saved)
    else:
        info = httpx.get(f"{a.vault_url.rstrip('/')}/info", timeout=60).json()
    att = info["attestation"]
    ok = True

    local = code_hash()
    print(f"1. code hash   vault {info['code_hash'][:16]}…  this checkout {local[:16]}…  ->", "OK" if info["code_hash"] == local else "MISMATCH")
    ok &= info["code_hash"] == local

    if att.get("mode") != "tdx":
        print("2. no hardware quote (vault reports mode =", att.get("mode"), ")")
        return 1
    quote = bytes.fromhex(att["quote"])
    report_data = quote[48 + 520: 48 + 584]  # TDX quote v4: 48-byte header, report_data = last 64 bytes of the TD report
    want = hashlib.sha256(bytes.fromhex(info["combiner_key"]) + bytes.fromhex(info["code_hash"])).digest()
    bound = report_data[:32] == want
    print(f"2. quote binds key {info['combiner_key'][:16]}… + code hash  ->", "OK" if bound else "MISMATCH")
    ok &= bound

    v = httpx.post(VERIFIER, json={"hex": att["quote"]}, timeout=120).json()
    genuine = bool(v.get("success"))
    print(f"3. genuine Intel TDX quote (verifier id {v.get('id', '?')[:16]}…)  ->", "OK" if genuine else "FAILED")
    ok &= genuine

    if a.model is not None:
        from axon.chain import Near
        m = Near().view("get_model", {"model_id": a.model})
        same = m and m["combiner_key"] == info["combiner_key"] and m["combiner_code_hash"] == info["code_hash"]
        print(f"4. NEAR model {a.model} accepts only this vault's key and code  ->", "OK" if same else "MISMATCH")
        ok &= bool(same)

    if a.save:
        Path(a.save).write_text(json.dumps({"vault_url": a.vault_url, "info": info, "verifier": v}, indent=1))
        print("evidence saved to", a.save)
    print("ALL CHECKS PASSED" if ok else "SOME CHECKS FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

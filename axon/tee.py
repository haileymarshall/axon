"""TEE attestation for the vault.

When the vault runs inside an Intel TDX confidential VM managed by dstack (Phala Cloud, the TEE stack
used by NEAR Shade Agents), it asks the hardware for a quote whose report_data commits to
sha256(combiner_key || code_hash). Anyone can verify the quote (e.g. with Phala's public verifier) and
so confirm that the key the NEAR contract trusts belongs to this exact code running in real TEE hardware.

Outside a TEE this returns a self-reported "local" attestation.
"""

from __future__ import annotations

import hashlib
import os

DSTACK_SOCKET = "/var/run/dstack.sock"


def report_data(combiner_key_hex: str, code_hash_hex: str) -> bytes:
    return hashlib.sha256(bytes.fromhex(combiner_key_hex) + bytes.fromhex(code_hash_hex)).digest()


def attest(combiner_key_hex: str, code_hash_hex: str) -> dict:
    rd = report_data(combiner_key_hex, code_hash_hex)
    if not os.path.exists(DSTACK_SOCKET):
        return {"mode": "local", "report_data": rd.hex(),
                "note": "self-reported; inside a TDX confidential VM this is a hardware quote binding code_hash to combiner_key"}
    from dstack_sdk import DstackClient

    q = DstackClient().get_quote(rd)
    return {"mode": "tdx", "report_data": rd.hex(), "quote": q.quote, "event_log": q.event_log,
            "verify": "paste the quote into https://proof.t16z.com to verify it on Intel TDX"}

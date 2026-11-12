"""Minimal NEAR client: JSON-RPC views + signed function calls (via py-near).

Signing keys are read from the standard NEAR CLI keychain: ~/.near-credentials/<network>/<account>.json
"""

from __future__ import annotations

import asyncio
import base64
import json
from pathlib import Path
from typing import Any

import httpx

from .config import CFG

YOCTO = 10**24
TGAS = 10**12


def near_to_yocto(near: float | str) -> int:
    whole, _, frac = str(near).partition(".")
    return int(whole or 0) * YOCTO + int((frac + "0" * 24)[:24] or 0)


def yocto_to_near(y: int | str) -> float:
    return int(y) / YOCTO


def credentials(account_id: str, network: str = CFG.network) -> str:
    path = Path.home() / ".near-credentials" / network / f"{account_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"no key for {account_id} at {path}")
    return json.loads(path.read_text())["private_key"]


class Near:
    def __init__(self, contract_id: str = CFG.contract_id, rpc_url: str = CFG.rpc_url):
        if not contract_id:
            raise ValueError("set AXON_CONTRACT to the deployed contract account")
        self.contract_id = contract_id
        self.rpc_url = rpc_url

    # ----------------------------------------------------------------- views

    def view(self, method: str, args: dict | None = None) -> Any:
        body = {
            "jsonrpc": "2.0", "id": "axon", "method": "query",
            "params": {
                "request_type": "call_function", "finality": "optimistic", "account_id": self.contract_id,
                "method_name": method, "args_base64": base64.b64encode(json.dumps(args or {}).encode()).decode(),
            },
        }
        r = httpx.post(self.rpc_url, json=body, timeout=30).json()
        if "error" in r or "error" in r.get("result", {}):
            raise RuntimeError(f"view {method} failed: {r.get('error') or r['result']['error']}")
        return json.loads(bytes(r["result"]["result"]).decode() or "null")

    def tx_status(self, tx_hash: str, sender: str) -> dict:
        body = {"jsonrpc": "2.0", "id": "axon", "method": "tx", "params": {"tx_hash": tx_hash, "sender_account_id": sender, "wait_until": "FINAL"}}
        return httpx.post(self.rpc_url, json=body, timeout=60).json()

    # ----------------------------------------------------------------- calls

    def call(self, signer: str, method: str, args: dict, deposit_yocto: int = 0, gas_tgas: int = 100) -> dict:
        """Sign and send a function call as `signer`. Returns {'tx': hash, 'value': decoded return}."""
        return asyncio.run(self._call(signer, method, args, deposit_yocto, gas_tgas))

    async def _call(self, signer, method, args, deposit, gas_tgas):
        from py_near.account import Account

        acc = Account(signer, credentials(signer), rpc_addr=self.rpc_url)
        await acc.startup()
        try:
            res = await acc.function_call(self.contract_id, method, args, gas=gas_tgas * TGAS, amount=deposit)
        finally:
            await acc.shutdown()
        status = getattr(res, "status", {}) or {}
        if isinstance(status, dict) and "Failure" in status:
            raise RuntimeError(f"{method} failed: {json.dumps(status['Failure'])[:400]}")
        value = None
        if isinstance(status, dict) and status.get("SuccessValue"):
            raw = base64.b64decode(status["SuccessValue"]).decode()
            value = json.loads(raw) if raw else None
        return {"tx": res.transaction.hash, "value": value, "logs": res.logs}

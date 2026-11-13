"""Minimal NEAR client: JSON-RPC views + signed function calls (via py-near).

Signing keys are read from the standard NEAR CLI keychain: ~/.near-credentials/<network>/<account>.json
"""

from __future__ import annotations

import asyncio
import base64
import time
import json
import os
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
    # In the TEE there is no keychain: the relaying account's key arrives as a sealed environment variable.
    if not path.exists() and os.environ.get("AXON_NEAR_PRIVATE_KEY") and account_id == os.environ.get("AXON_OPERATOR"):
        return os.environ["AXON_NEAR_PRIVATE_KEY"]
    if not path.exists():
        raise FileNotFoundError(f"no key for {account_id} at {path}")
    return json.loads(path.read_text())["private_key"]


# Public RPCs rate-limit busy addresses (a TEE shares its IP with other tenants), so reads and sends rotate across
# several endpoints with backoff. The configured AXON_RPC is always tried first.
FALLBACK_RPCS = {
    "mainnet": ["https://free.rpc.fastnear.com", "https://rpc.mainnet.fastnear.com", "https://near.drpc.org", "https://rpc.mainnet.near.org"],
    "testnet": ["https://rpc.testnet.near.org", "https://test.rpc.fastnear.com"],
}


def _refused(err: Exception | dict) -> bool:
    """The endpoint clearly refused the request (rate limit), so it was never sent on: safe to resend a transaction."""
    text = str(err).lower()
    return any(k in text for k in ("429", "rate limit", "too many requests", "deprecated"))


def _retryable(err: Exception | dict) -> bool:
    text = str(err).lower()
    return any(k in text for k in ("429", "rate limit", "too many", "timeout", "timed out", "503", "502", "504",
                                   "connection", "deprecated", "temporarily", "unavailable"))


class Near:
    def __init__(self, contract_id: str = CFG.contract_id, rpc_url: str = CFG.rpc_url):
        if not contract_id:
            raise ValueError("set AXON_CONTRACT to the deployed contract account")
        self.contract_id = contract_id
        self.rpc_url = rpc_url
        self.rpcs = [rpc_url] + [u for u in FALLBACK_RPCS.get(CFG.network, []) if u != rpc_url]

    def _post(self, body: dict, timeout: int = 30) -> dict:
        """POST a JSON-RPC request, rotating endpoints and backing off on rate limits and network errors."""
        last: Exception | dict | None = None
        for attempt in range(8):
            url = self.rpcs[attempt % len(self.rpcs)]
            try:
                r = httpx.post(url, json=body, timeout=timeout).json()
            except Exception as e:  # network error: try the next endpoint
                last = e
            else:
                err = r.get("error") or (r.get("result") or {}).get("error") if isinstance(r.get("result"), dict) else r.get("error")
                if not err or not _retryable(err):
                    return r
                last = err
            time.sleep(min(8.0, 0.5 * 2 ** (attempt // len(self.rpcs))))
        raise RuntimeError(f"NEAR RPC unavailable after retries: {str(last)[:300]}")

    # ----------------------------------------------------------------- views

    def view(self, method: str, args: dict | None = None) -> Any:
        body = {
            "jsonrpc": "2.0", "id": "axon", "method": "query",
            "params": {
                "request_type": "call_function", "finality": "optimistic", "account_id": self.contract_id,
                "method_name": method, "args_base64": base64.b64encode(json.dumps(args or {}).encode()).decode(),
            },
        }
        r = self._post(body)
        if "error" in r or "error" in r.get("result", {}):
            raise RuntimeError(f"view {method} failed: {r.get('error') or r['result']['error']}")
        return json.loads(bytes(r["result"]["result"]).decode() or "null")

    def tx_status(self, tx_hash: str, sender: str) -> dict:
        body = {"jsonrpc": "2.0", "id": "axon", "method": "tx", "params": {"tx_hash": tx_hash, "sender_account_id": sender, "wait_until": "FINAL"}}
        return self._post(body, timeout=60)

    # ----------------------------------------------------------------- calls

    def call(self, signer: str, method: str, args: dict, deposit_yocto: int = 0, gas_tgas: int = 100) -> dict:
        """Sign and send a function call as `signer`. Returns {'tx': hash, 'value': decoded return}."""
        return asyncio.run(self._call(signer, method, args, deposit_yocto, gas_tgas))

    async def _call(self, signer, method, args, deposit, gas_tgas):
        from py_near.account import Account

        last = None
        for attempt in range(6):  # rotate endpoints on rate limits; a signed tx is only sent once per endpoint try
            acc = Account(signer, credentials(signer), rpc_addr=self.rpcs[attempt % len(self.rpcs)])
            try:
                await acc.startup()
                res = await acc.function_call(self.contract_id, method, args, gas=gas_tgas * TGAS, amount=deposit)
                break
            except Exception as e:
                if not _refused(e):  # timeouts etc. are ambiguous for a transaction: never resend those
                    raise
                last = e
                await asyncio.sleep(min(8.0, 1.0 * 2 ** (attempt // len(self.rpcs))))
            finally:
                await acc.shutdown()
        else:
            raise RuntimeError(f"{method}: NEAR RPC unavailable after retries: {str(last)[:300]}")
        status = getattr(res, "status", {}) or {}
        if isinstance(status, dict) and "Failure" in status:
            raise RuntimeError(f"{method} failed: {json.dumps(status['Failure'])[:400]}")
        value = None
        if isinstance(status, dict) and status.get("SuccessValue"):
            raw = base64.b64decode(status["SuccessValue"]).decode()
            value = json.loads(raw) if raw else None
        return {"tx": res.transaction.hash, "value": value, "logs": res.logs}

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

    def is_full_access_key(self, account_id: str, public_key: str) -> bool:
        r = self._post({"jsonrpc": "2.0", "id": "axon", "method": "query", "params": {
            "request_type": "view_access_key", "finality": "final", "account_id": account_id, "public_key": public_key}})
        return "result" in r and "error" not in r["result"] and r["result"].get("permission") == "FullAccess"

    def tx_status(self, tx_hash: str, sender: str) -> dict:
        body = {"jsonrpc": "2.0", "id": "axon", "method": "tx", "params": {"tx_hash": tx_hash, "sender_account_id": sender, "wait_until": "FINAL"}}
        return self._post(body, timeout=60)

    # ----------------------------------------------------------------- calls

    # Calls the contract itself makes safe to resend: a duplicate is rejected on-chain (round number, already joined,
    # nothing to withdraw) instead of doing anything twice. Payments are not in this list.
    IDEMPOTENT = {"submit_round", "join_model", "set_combiner", "withdraw", "close_model"}

    def call(self, signer: str, method: str, args: dict, deposit_yocto: int = 0, gas_tgas: int = 100) -> dict:
        """Sign and send a function call as `signer`. Returns {'tx': hash, 'value': decoded return}."""
        return asyncio.run(self._call(signer, method, args, deposit_yocto, gas_tgas))

    async def _call(self, signer, method, args, deposit, gas_tgas):
        return self._sign_and_send(signer, method, args, deposit, gas_tgas)

    def _sign_and_send(self, signer: str, method: str, args: dict, deposit: int, gas_tgas: int) -> dict:
        """Sign locally, broadcast over plain HTTPS with endpoint rotation (works where py-near's client does not,
        e.g. inside a TEE). The same signed bytes are resent on any error: NEAR executes a signed transaction at
        most once (nonce), so retries can never pay or submit twice."""
        import base58
        from py_near import transactions as T

        sk = credentials(signer)
        raw = base58.b58decode(sk.replace("ed25519:", ""))
        public_key = "ed25519:" + base58.b58encode(raw[32:]).decode()
        ak = self._post({"jsonrpc": "2.0", "id": "axon", "method": "query", "params": {
            "request_type": "view_access_key", "finality": "final", "account_id": signer, "public_key": public_key}})
        if "error" in ak or "error" in ak.get("result", {}):
            raise RuntimeError(f"access key for {signer} not found: {ak.get('error') or ak['result']['error']}")
        nonce = ak["result"]["nonce"] + 1
        block = self._post({"jsonrpc": "2.0", "id": "axon", "method": "block", "params": {"finality": "final"}})
        block_hash = base58.b58decode(block["result"]["header"]["hash"])
        actions = [T.create_function_call_action(method, json.dumps(args).encode(), gas_tgas * TGAS, deposit)]
        tx_hash = T.calc_trx_hash(signer, sk, self.contract_id, nonce, actions, block_hash)
        signed = T.sign_and_serialize_transaction(signer, sk, self.contract_id, nonce, actions, block_hash)

        res, last = None, None
        for attempt in range(10):
            try:
                r = self._post({"jsonrpc": "2.0", "id": "axon", "method": "send_tx",
                                "params": {"signed_tx_base64": signed, "wait_until": "FINAL"}}, timeout=90)
            except Exception as e:
                r = {"error": str(e)}
            if "result" in r and r["result"].get("status"):
                res = r["result"]
                break
            last = r.get("error")
            # Maybe it went through and only the reply was lost: look it up by hash before resending.
            st = self._post({"jsonrpc": "2.0", "id": "axon", "method": "tx",
                             "params": {"tx_hash": tx_hash, "sender_account_id": signer, "wait_until": "FINAL"}}, timeout=60)
            if "result" in st and st["result"].get("status"):
                res = st["result"]
                break
            time.sleep(min(10.0, 1.5 * (attempt + 1)))
        if res is None:
            raise RuntimeError(f"{method}: could not send the transaction {tx_hash}: {str(last)[:300]}")
        status = res.get("status") or {}
        if "Failure" in status:
            raise RuntimeError(f"{method} failed: {json.dumps(status['Failure'])[:400]}")
        value = None
        if status.get("SuccessValue"):
            raw_v = base64.b64decode(status["SuccessValue"]).decode()
            value = json.loads(raw_v) if raw_v else None
        logs = [l for o in res.get("receipts_outcome", []) for l in o.get("outcome", {}).get("logs", [])]
        return {"tx": tx_hash, "value": value, "logs": logs}

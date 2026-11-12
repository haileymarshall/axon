"""NEAR Intents (1Click API): let users pay for a query with any token on any chain.

Flow: the app asks 1Click for a quote whose output is exactly the model's query price in wNEAR,
delivered to the Axon treasury account. The user sends the quoted amount of their token to the
one-time deposit address on their own chain. When 1Click reports SUCCESS, the treasury calls
`pay_for_query` on the Axon contract, tagging the payment with its cross-chain origin.

Confidential Intents (`confidentiality: basic|advanced`) hide the payment trail; they require a
1Click partner JWT (set AXON_INTENTS_JWT).
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import httpx

API = "https://1click.chaindefuser.com/v0"
JWT = os.environ.get("AXON_INTENTS_JWT", "")

# A curated set of popular payment options (all supported by 1Click).
TOKENS = [
    {"id": "nep141:base-0x833589fcd6edb6e08f4c7c32d4f71b54bda02913.omft.near", "label": "USDC on Base", "decimals": 6},
    {"id": "nep141:sol-5ce3bf3a31af18be40ba30f721101b4341690186.omft.near", "label": "USDC on Solana", "decimals": 6},
    {"id": "nep141:arb-0xaf88d065e77c8cc2239327c5edb3a432268e5831.omft.near", "label": "USDC on Arbitrum", "decimals": 6},
    {"id": "nep141:eth-0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48.omft.near", "label": "USDC on Ethereum", "decimals": 6},
    {"id": "nep141:sol.omft.near", "label": "SOL", "decimals": 9},
    {"id": "nep141:eth.omft.near", "label": "ETH", "decimals": 18},
    {"id": "nep141:btc.omft.near", "label": "BTC", "decimals": 8},
    {"id": "nep141:wrap.near", "label": "NEAR", "decimals": 24},
]
WNEAR = "nep141:wrap.near"


def _headers() -> dict:
    return {"Authorization": f"Bearer {JWT}"} if JWT else {}


def quote(origin_asset: str, amount_wnear_yocto: int, recipient: str, refund_to: str,
          dry: bool = True, confidential: bool = False) -> dict:
    """Quote paying exactly `amount_wnear_yocto` wNEAR to `recipient`, funded with `origin_asset`."""
    body = {
        "dry": dry,
        "swapType": "EXACT_OUTPUT",
        "slippageTolerance": 100,
        "originAsset": origin_asset,
        "depositType": "ORIGIN_CHAIN",
        "destinationAsset": WNEAR,
        "amount": str(amount_wnear_yocto),
        "refundTo": refund_to,
        "refundType": "ORIGIN_CHAIN",
        "recipient": recipient,
        "recipientType": "DESTINATION_CHAIN",
        "deadline": (datetime.now(timezone.utc) + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "quoteWaitingTimeMs": 3000,
    }
    if confidential:
        body["confidentiality"] = "basic"
    r = httpx.post(f"{API}/quote", json=body, headers=_headers(), timeout=30)
    if r.status_code >= 400:
        raise RuntimeError(f"1Click quote failed: {r.status_code} {r.text[:300]}")
    return r.json()


def status(deposit_address: str) -> dict:
    r = httpx.get(f"{API}/status", params={"depositAddress": deposit_address}, headers=_headers(), timeout=30)
    if r.status_code >= 400:
        raise RuntimeError(f"1Click status failed: {r.status_code} {r.text[:300]}")
    return r.json()

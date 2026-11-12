"""The Axon web app backend: reads the chain, quotes Intents payments, and forwards paid questions
to the vault. It never sees training data or model weights."""

from __future__ import annotations

import json

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import crypto, intents
from .chain import Near
from .config import CFG, ROOT

WEB = ROOT / "web"
ORDERS = CFG.state_dir / "app" / "orders.json"


class QuoteIn(BaseModel):
    model_id: int
    origin_asset: str
    refund_to: str
    question: str
    dry: bool = True


class TestnetAskIn(BaseModel):
    model_id: int
    question: str


def _orders() -> dict:
    return json.loads(ORDERS.read_text()) if ORDERS.exists() else {}


def _save_orders(o: dict) -> None:
    ORDERS.parent.mkdir(parents=True, exist_ok=True)
    ORDERS.write_text(json.dumps(o, indent=1))


def create_app(treasury: str | None, demo_payer: str | None) -> FastAPI:
    """`treasury` receives Intents payments and records them on-chain; `demo_payer` pays testnet demo queries."""
    app = FastAPI(title="Axon app")
    near = Near()

    @app.get("/api/config")
    def config():
        try:
            vault = httpx.get(f"{CFG.vault_url}/info", timeout=5).json()
        except Exception:
            vault = None
        return {"network": CFG.network, "contract": near.contract_id, "treasury": treasury,
                "demo_payer": demo_payer, "vault": vault, "tokens": intents.TOKENS,
                "explorer": "https://testnet.nearblocks.io" if CFG.network == "testnet" else "https://nearblocks.io"}

    @app.get("/api/models")
    def models():
        return near.view("get_models", {"limit": 50})

    @app.get("/api/models/{model_id}")
    def model(model_id: int):
        m = near.view("get_model", {"model_id": model_id})
        if m is None:
            raise HTTPException(404, "no such model")
        m["rounds_detail"] = near.view("get_rounds", {"model_id": model_id})
        return m

    @app.get("/api/earnings/{account}")
    def earnings(account: str):
        out = []
        for m in near.view("get_models", {"limit": 50}):
            c = next((c for c in m["contributors"] if c["account"] == account), None)
            if c or m["creator"] == account:
                e = near.view("earnings_of", {"model_id": m["id"], "account": account})
                out.append({"model_id": m["id"], "name": m["name"], "shares": c["shares"] if c else "0",
                            "total_shares": m["total_shares"], "earnings": e})
        return out

    # ------------------------------------------------------------- paying with NEAR Intents

    @app.post("/api/quote")
    def quote(q: QuoteIn):
        if not treasury:
            raise HTTPException(503, "no treasury account configured")
        m = near.view("get_model", {"model_id": q.model_id})
        try:
            res = intents.quote(q.origin_asset, int(m["query_price"]), treasury, q.refund_to, dry=q.dry)
        except RuntimeError as e:
            raise HTTPException(400, str(e)) from e
        dep = res["quote"].get("depositAddress")
        if dep:
            o = _orders()
            o[dep] = {"model_id": q.model_id, "question": q.question, "asset": q.origin_asset, "state": "awaiting_deposit"}
            _save_orders(o)
        return res

    @app.get("/api/orders/{deposit_address}")
    def order(deposit_address: str):
        o = _orders()
        if deposit_address not in o:
            raise HTTPException(404, "unknown order")
        order = o[deposit_address]
        if order["state"] == "answered":
            return order
        st = intents.status(deposit_address)
        order["intents_status"] = st.get("status")
        if st.get("status") == "SUCCESS" and order["state"] != "answered":
            asset = next((t["label"] for t in intents.TOKENS if t["id"] == order["asset"]), order["asset"])
            order.update(_pay_and_ask(order["model_id"], order["question"], treasury, f"intents:{asset}:{deposit_address}"))
            order["state"] = "answered"
        _save_orders(o)
        return order

    # ------------------------------------------------------------- testnet demo payment

    @app.post("/api/ask-testnet")
    def ask_testnet(a: TestnetAskIn):
        if not demo_payer:
            raise HTTPException(503, "no testnet demo payer configured")
        return _pay_and_ask(a.model_id, a.question, demo_payer, "testnet-demo")

    def _pay_and_ask(model_id: int, question: str, payer: str, source: str) -> dict:
        m = near.view("get_model", {"model_id": model_id})
        paid = near.call(payer, "pay_for_query", {"model_id": model_id, "source": source, "query_hash": crypto.query_hash(question)},
                         deposit_yocto=int(m["query_price"]), gas_tgas=30)
        r = httpx.post(f"{CFG.vault_url}/models/{model_id}/ask",
                       json={"question": question, "payment_tx": paid["tx"], "payer": payer}, timeout=300)
        if r.status_code != 200:
            raise HTTPException(r.status_code, r.text)
        return {"payment_tx": paid["tx"], "payer": payer, "source": source, **r.json()}

    # ------------------------------------------------------------- static site

    if WEB.exists():
        app.mount("/static", StaticFiles(directory=WEB), name="static")

    @app.get("/")
    def index():
        return FileResponse(WEB / "index.html")

    return app


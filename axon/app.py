"""The Axon web app backend: reads the chain, quotes Intents payments, and forwards paid questions
to the vault. It never sees training data or model weights."""

from __future__ import annotations

import json
import os
import threading
import time

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import crypto, intents
from .chain import Near
from .config import CFG, ROOT

WEB = ROOT / "web"
ORDERS = CFG.state_dir / "app" / "orders.json"
DEMO_LOG = CFG.state_dir / "app" / "demo_asks.json"
# The demo payer spends real NEAR on mainnet, so demo questions are rate limited.
DEMO_PER_DAY = 20
DEMO_IP_GAP_S = 60


class QuoteIn(BaseModel):
    model_id: int
    origin_asset: str
    refund_to: str
    question: str
    dry: bool = True
    compare: bool = False


class PaidAskIn(BaseModel):
    """A question the user already paid for from their own wallet (pay_for_query with this question's hash)."""
    model_id: int
    question: str
    payment_tx: str
    payer: str
    compare: bool = False


class TestIn(BaseModel):
    creator: str
    sealed: str
    public_key: str = ""
    signature: str = ""
    nonce: str = ""


class DemoAskIn(BaseModel):
    model_id: int
    question: str
    compare: bool = False


def _orders() -> dict:
    return json.loads(ORDERS.read_text()) if ORDERS.exists() else {}


def _save_orders(o: dict) -> None:
    ORDERS.parent.mkdir(parents=True, exist_ok=True)
    ORDERS.write_text(json.dumps(o, indent=1))


def create_app(treasury: str | None, demo_payer: str | None) -> FastAPI:
    """`treasury` receives Intents payments and records them on-chain; `demo_payer` pays a few demo questions."""
    app = FastAPI(title="Axon app")
    near = Near()
    demo_lock = threading.Lock()

    @app.get("/api/config")
    def config():
        try:
            vault = httpx.get(f"{CFG.vault_url}/info", timeout=5).json()
        except Exception:
            vault = None
        return {"network": CFG.network, "contract": near.contract_id, "treasury": treasury,
                "demo_payer": demo_payer, "demo_per_day": DEMO_PER_DAY, "vault": vault, "tokens": intents.TOKENS,
                "vault_url": os.environ.get("AXON_PUBLIC_VAULT_URL") or CFG.vault_url,
                "platform_fees": near.view("platform_fees", {}),
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

    @app.get("/api/runs")
    def runs():
        """Published training runs for this contract (runs/<id>/summary.json): base vs trained answers, shares."""
        out = []
        for f in sorted((ROOT / "runs").glob("*/summary.json"), reverse=True):
            s = json.loads(f.read_text())
            if s.get("contract") == near.contract_id:
                out.append(s)
        return out

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
            o[dep] = {"model_id": q.model_id, "question": q.question, "asset": q.origin_asset, "state": "awaiting_deposit", "compare": q.compare}
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
            order.update(_pay_and_ask(order["model_id"], order["question"], treasury, f"intents:{asset}:{deposit_address}", order.get("compare", False)))
            order["state"] = "answered"
        _save_orders(o)
        return order

    # ------------------------------------------------------------- paid from the user's own wallet

    @app.post("/api/ask-paid")
    def ask_paid(a: PaidAskIn):
        r = httpx.post(f"{CFG.vault_url}/models/{a.model_id}/ask",
                       json={"question": a.question, "payment_tx": a.payment_tx, "payer": a.payer, "compare": a.compare}, timeout=300)
        if r.status_code != 200:
            raise HTTPException(r.status_code, r.json().get("detail", r.text) if r.headers.get("content-type", "").startswith("application/json") else r.text)
        return {"payment_tx": a.payment_tx, "payer": a.payer, "source": "wallet", **r.json()}

    @app.post("/api/models/{model_id}/test")
    def set_test(model_id: int, t: TestIn):
        r = httpx.post(f"{CFG.vault_url}/models/{model_id}/test", json=t.model_dump(), timeout=60)
        if r.status_code != 200:
            raise HTTPException(r.status_code, r.json().get("detail", r.text) if r.headers.get("content-type", "").startswith("application/json") else r.text)
        return r.json()

    # ------------------------------------------------------------- demo payment (rate limited)

    @app.post("/api/ask-demo")
    def ask_demo(a: DemoAskIn, request: Request):
        if not demo_payer:
            raise HTTPException(503, "no demo payer configured")
        ip = request.headers.get("x-forwarded-for", request.client.host if request.client else "?").split(",")[0].strip()
        with demo_lock:
            now = time.time()
            log = json.loads(DEMO_LOG.read_text()) if DEMO_LOG.exists() else []
            log = [e for e in log if now - e["t"] < 86400]
            if len(log) >= DEMO_PER_DAY:
                raise HTTPException(429, "today's free demo questions are used up; pay with NEAR Intents instead")
            if any(e["ip"] == ip and now - e["t"] < DEMO_IP_GAP_S for e in log):
                raise HTTPException(429, "one free demo question per minute")
            log.append({"t": now, "ip": ip})
            DEMO_LOG.parent.mkdir(parents=True, exist_ok=True)
            DEMO_LOG.write_text(json.dumps(log))
        return _pay_and_ask(a.model_id, a.question, demo_payer, "demo", a.compare)

    def _pay_and_ask(model_id: int, question: str, payer: str, source: str, compare: bool = False) -> dict:
        m = near.view("get_model", {"model_id": model_id})
        paid = near.call(payer, "pay_for_query", {"model_id": model_id, "source": source, "query_hash": crypto.query_hash(question)},
                         deposit_yocto=int(m["query_price"]), gas_tgas=30)
        r = httpx.post(f"{CFG.vault_url}/models/{model_id}/ask",
                       json={"question": question, "payment_tx": paid["tx"], "payer": payer, "compare": compare}, timeout=300)
        if r.status_code != 200:
            raise HTTPException(r.status_code, r.text)
        return {"payment_tx": paid["tx"], "payer": payer, "source": source, **r.json()}

    # ------------------------------------------------------------- static site

    if WEB.exists():
        app.mount("/static", StaticFiles(directory=WEB), name="static")

    @app.get("/")
    def index():
        return FileResponse(WEB / "index.html")

    @app.get("/{design}")
    def design(design: str):
        """Alternative frontend designs, e.g. /b -> web/b/index.html (same data, different look)."""
        page = WEB / design / "index.html"
        if not (design.isalnum() and page.exists()):
            raise HTTPException(404, "not found")
        return FileResponse(page)

    return app


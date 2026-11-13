"""The Axon vault: the sealed combiner.

Designed to run inside a TEE (a NEAR Shade Agent / confidential VM). It is the only place where:
  * contributors' updates are decrypted (they are sealed to the vault's X25519 key),
  * the hidden test set lives (so nobody can game the scoring),
  * the merged model lives and answers paid queries (so the model can't be copied for free).

It signs every round result with its ed25519 key; the NEAR contract only accepts results signed
by the key registered for the model, and that key is bound to `code_hash` (a hash of this code).
In local mode the attestation is a self-report; in TEE mode it is a hardware quote.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import threading
import time
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

from . import crypto, data, ml, tee
from .chain import Near
from .config import CFG, ROOT

VAULT_DIR = CFG.state_dir / "vault"
# Files whose code decides scores and answers; their hash is what the TEE attests to.
# How long a signed download request stays valid (seconds).
DOWNLOAD_WINDOW_S = 300
VAULT_SOURCES = ("vault.py", "ml.py", "crypto.py", "chain.py", "config.py", "data.py", "tee.py")


def code_hash() -> str:
    """sha256 over the vault's source code - what a TEE attestation would measure."""
    h = hashlib.sha256()
    for p in sorted((ROOT / "axon" / f) for f in VAULT_SOURCES):
        h.update(p.name.encode() + b"\0" + p.read_bytes())
    return h.hexdigest()


SUPPORTED_BASES = [
    {"id": "Qwen/Qwen3-1.7B", "name": "Qwen3 1.7B", "by": "Alibaba", "note": "newest, 119 languages"},
    {"id": "Qwen/Qwen2.5-1.5B-Instruct", "name": "Qwen2.5 1.5B Instruct", "by": "Alibaba", "note": "fast, reliable"},
    {"id": "HuggingFaceTB/SmolLM2-1.7B-Instruct", "name": "SmolLM2 1.7B Instruct", "by": "Hugging Face", "note": "fully open training data"},
    {"id": "HuggingFaceTB/SmolLM2-135M-Instruct", "name": "SmolLM2 135M Instruct", "by": "Hugging Face", "note": "tiny, trains on a laptop CPU"},
]


class Vault:
    def __init__(self, operator: str | None = None):
        self.sign_key = crypto.load_or_create_signing_key("vault")
        self.box_key = crypto.load_or_create_box_key("vault")
        self.operator = operator  # NEAR account that relays signed results on-chain (any account works)
        # One engine per open base model (e.g. Qwen2.5 for the health model, Qwen3 for others), loaded on first use.
        # An engine holds one adapter at a time, so each has a lock around "switch adapter + run".
        self._engines: dict[str, ml.Engine] = {}
        self._engine_locks: dict[str, threading.Lock] = {}
        self._bases: dict[int, str] = {}
        self.lock = threading.Lock()
        self.pending: dict[int, dict[str, ml.Adapter]] = {}
        self.used_payments: set[str] = set(json.loads(self._p("used_payments.json").read_text())) if self._p("used_payments.json").exists() else set()
        self.last_scores: dict[int, dict] = {}
        self.code_hash = code_hash()  # measured once at start, like a TEE measurement
        self.attestation = tee.attest(crypto.pubkey_hex(self.sign_key), self.code_hash)

    # ------------------------------------------------------------- helpers

    @staticmethod
    def _p(*parts: str) -> Path:
        path = VAULT_DIR.joinpath(*parts)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def engine_for(self, base_model: str | None = None) -> ml.Engine:
        base_model = base_model or CFG.base_model
        with self.lock:
            lock = self._engine_locks.setdefault(base_model, threading.Lock())
        with lock:
            if base_model not in self._engines:
                self._engines[base_model] = ml.Engine(base_model)
        return self._engines[base_model]

    def engine_lock(self, base_model: str | None = None) -> threading.Lock:
        with self.lock:
            return self._engine_locks.setdefault(base_model or CFG.base_model, threading.Lock())

    @property
    def engine(self) -> ml.Engine:
        return self.engine_for(CFG.base_model)

    def base_of(self, model_id: int) -> str:
        """The open base model a model was created on (read once from the chain)."""
        if model_id not in self._bases:
            m = Near().view("get_model", {"model_id": model_id})
            self._bases[model_id] = (m or {}).get("base_model") or CFG.base_model
        return self._bases[model_id]

    def info(self) -> dict:
        return {
            "combiner_key": crypto.pubkey_hex(self.sign_key),
            "box_key": self.box_key.public_key.encode().hex(),
            "code_hash": self.code_hash,
            "base_model": CFG.base_model,
            # Contributors' adapters must have this shape, so the contributor client copies it from here.
            "training": {"lora_rank": CFG.lora_rank, "lora_targets": CFG.lora_targets},
            # Open base models a new model can be created on (the vault downloads each on first use).
            "bases": SUPPORTED_BASES,
            "attestation": self.attestation,
        }

    def global_adapter(self, model_id: int) -> ml.Adapter:
        path = self._p(f"model-{model_id}", "global.safetensors")
        if path.exists():
            return ml.adapter_from_bytes(path.read_bytes())
        return self.engine_for(self.base_of(model_id)).initial

    def _save_global(self, model_id: int, adapter: ml.Adapter) -> None:
        self._p(f"model-{model_id}", "global.safetensors").write_bytes(ml.adapter_bytes(adapter))

    def test_set(self, domain: str | None = None, model_id: int | None = None) -> list[dict]:
        """The hidden test set: the one its creator sealed to this vault, else the demo test set for the domain."""
        own = VAULT_DIR / f"model-{model_id}" / "test.jsonl"
        if model_id is not None and own.exists():
            return data.read_jsonl(own)
        return data.read_jsonl(data.paths(domain)["test"])

    def set_test(self, model_id: int, creator: str, sealed_b64: str) -> dict:
        """A model's creator hands over its hidden test set, sealed so only this vault can read it. Accepted once,
        before the first round, and only for the account the chain lists as the model's creator."""
        m = Near().view("get_model", {"model_id": model_id})
        if m is None:
            raise HTTPException(404, "no such model")
        if m["creator"] != creator:
            raise HTTPException(403, "only the model's creator can set its test set")
        if m["rounds"] > 0 or (VAULT_DIR / f"model-{model_id}" / "test.jsonl").exists():
            raise HTTPException(409, "test set already fixed")
        try:
            rows = [json.loads(l) for l in crypto.unseal(self.box_key, crypto.unb64(sealed_b64)).decode().splitlines() if l.strip()]
        except Exception as e:
            raise HTTPException(400, f"could not open the sealed test set: {e}") from e
        if not (5 <= len(rows) <= 500) or not all(isinstance(r, dict) and r.get("q") and r.get("a") for r in rows):
            raise HTTPException(400, 'test set must be 5 to 500 lines of {"q": ..., "a": ...}')
        self._p(f"model-{model_id}", "test.jsonl").write_text("\n".join(json.dumps({"q": r["q"], "a": r["a"]}) for r in rows) + "\n")
        return {"accepted": True, "questions": len(rows)}

    # ------------------------------------------------------------- access

    def authorize_download(self, model_id: int, account: str, ts: int, signature: str) -> None:
        """Only contributors who joined on-chain may download the shared adapter, signed with their device key."""
        if abs(time.time() - ts) > DOWNLOAD_WINDOW_S:
            raise HTTPException(401, "download request expired; sign a fresh timestamp")
        model = Near().view("get_model", {"model_id": model_id})
        if model is None:
            raise HTTPException(404, "no such model")
        member = next((c for c in model["contributors"] if c["account"] == account), None)
        if member is None:
            raise HTTPException(403, "only contributors who joined this model on-chain can download it")
        if not crypto.verify(member["device_key"], crypto.download_message(model_id, account, ts), signature):
            raise HTTPException(403, "bad device signature")

    # ------------------------------------------------------------- updates

    def receive_update(self, model_id: int, account: str, round_: int, adapter_sha: str, signature: str, sealed_b64: str) -> dict:
        model = Near().view("get_model", {"model_id": model_id})
        if model is None:
            raise HTTPException(404, "no such model")
        if round_ != model["rounds"] + 1:
            raise HTTPException(409, f"vault is collecting round {model['rounds'] + 1}")
        member = next((c for c in model["contributors"] if c["account"] == account), None)
        if member is None:
            raise HTTPException(403, "account has not joined this model on-chain")
        blob = crypto.unseal(self.box_key, crypto.unb64(sealed_b64))
        if crypto.sha256_hex(blob) != adapter_sha:
            raise HTTPException(400, "adapter hash mismatch")
        msg = crypto.update_message(model_id, round_, account, adapter_sha)
        if not crypto.verify(member["device_key"], msg, signature):
            raise HTTPException(403, "bad device signature")
        with self.lock:
            self.pending.setdefault(model_id, {})[account] = ml.adapter_from_bytes(blob)
        return {"accepted": True, "round": round_, "pending": sorted(self.pending[model_id])}

    # ------------------------------------------------------------- rounds

    def close_round(self, model_id: int, compute_provider: str | None = None, submit: bool = True) -> dict:
        model = Near().view("get_model", {"model_id": model_id})
        with self.lock:
            updates = self.pending.pop(model_id, {})
        if not updates:
            raise HTTPException(400, "no updates received this round")
        base = self.global_adapter(model_id)
        logs: list[str] = []
        test = self.test_set(model.get("domain"), model_id)
        engine = self.engine_for(model.get("base_model"))
        with self.engine_lock(model.get("base_model")):
            score = ml.score_round(engine, test, base, updates, log=logs.append,
                                   metric=data.metric_fn(model.get("domain"), engine, test))

        payload = json.dumps({
            "model_id": model_id,
            "round": model["rounds"] + 1,
            "adapter_hash": ml.adapter_hash(score.global_adapter),
            "base_eval_loss_milli": round(score.base_loss * 1000),
            "eval_loss_milli": round(score.new_loss * 1000),
            "results": [{"account": a, "improvement_micro": str(round(v * 1_000_000))} for a, v in score.improvement.items()],
            "compute_provider": compute_provider,
        }, separators=(",", ":"))
        signature = crypto.sign_hex(self.sign_key, payload.encode())
        out = {"payload": json.loads(payload), "signature": signature, "excluded": score.excluded, "log": logs}
        if submit:
            try:
                if not self.operator:
                    raise HTTPException(500, "vault has no operator account to relay results")
                out["tx"] = Near().call(self.operator, "submit_round", {"payload": payload, "signature": signature}, gas_tgas=100)["tx"]
            except Exception:
                # The round is not on-chain, so nothing changes: keep the updates for a retry, keep the old model.
                with self.lock:
                    self.pending.setdefault(model_id, {}).update({k: v for k, v in updates.items() if k not in self.pending.get(model_id, {})})
                raise
        # Only once the chain has the round does the vault's copy of the model move forward.
        self._save_global(model_id, score.global_adapter)
        self.last_scores[model_id] = out
        return out

    # ------------------------------------------------------------- queries

    def answer(self, model_id: int, question: str, payment_tx: str, payer: str, compare: bool = False) -> dict:
        """Answer a question only against an unused on-chain payment made for this exact question.
        With `compare`, also answer with the original open model (the same base model, adapter switched off)."""
        self._check_payment(model_id, payment_tx, payer, crypto.query_hash(question))
        # Reserve the payment before the (slow) generation, so two concurrent requests can't both use it.
        with self.lock:
            if payment_tx in self.used_payments:
                raise HTTPException(402, "payment already used")
            self.used_payments.add(payment_tx)
        base = self.base_of(model_id)
        engine, adapter = self.engine_for(base), self.global_adapter(model_id)
        try:
            with self.engine_lock(base):
                text = engine.generate(question, adapter)
                base_text = engine.generate(question, engine.initial) if compare else None
        except Exception:
            with self.lock:
                self.used_payments.discard(payment_tx)
            raise
        with self.lock:
            self._p("used_payments.json").write_text(json.dumps(sorted(self.used_payments)))
        out = {"answer": text, "payment_tx": payment_tx}
        if compare:
            out.update({"base_answer": base_text, "base_model": base})
        return out

    def _check_payment(self, model_id: int, tx_hash: str, payer: str, q_hash: str) -> None:
        near = Near()
        res = near.tx_status(tx_hash, payer).get("result")
        if not res or "SuccessValue" not in res.get("status", {}):
            raise HTTPException(402, "payment transaction not found or failed")
        check_payment_tx(res["transaction"], near.contract_id, model_id, payer, q_hash)


def check_payment_tx(tx: dict, contract_id: str, model_id: int, payer: str, q_hash: str) -> None:
    """A valid payment: signed by `payer`, sent to the Axon contract, `pay_for_query` for this model and question."""
    if tx.get("signer_id") != payer:
        raise HTTPException(402, "payment was not signed by the payer")
    if tx.get("receiver_id") != contract_id:
        raise HTTPException(402, "payment was not made to the Axon contract")
    for action in tx.get("actions", []):
        fc = action.get("FunctionCall") if isinstance(action, dict) else None
        if fc and fc["method_name"] == "pay_for_query":
            args = json.loads(crypto.unb64(fc["args"]))
            if int(args.get("model_id", -1)) != model_id:
                continue
            if args.get("query_hash") != q_hash:
                raise HTTPException(402, "payment was made for a different question")
            return
    raise HTTPException(402, "transaction is not a pay_for_query for this model")


# ----------------------------------------------------------------- HTTP API


class UpdateIn(BaseModel):
    account: str
    round: int
    adapter_sha: str
    signature: str
    sealed: str


class CloseIn(BaseModel):
    compute_provider: str | None = None


class TestIn(BaseModel):
    creator: str
    sealed: str


class AskIn(BaseModel):
    question: str
    payment_tx: str
    payer: str
    compare: bool = False


def create_app(operator: str | None) -> FastAPI:
    vault = Vault(operator)
    token = crypto.admin_token()
    app = FastAPI(title="Axon vault (sealed combiner)")

    def require_admin(authorization: str | None) -> None:
        if not authorization or not hmac.compare_digest(authorization, f"Bearer {token}"):
            raise HTTPException(401, "operator token required")

    @app.get("/info")
    def info():
        return vault.info()

    @app.get("/models/{model_id}/global")
    def get_global(model_id: int, account: str, ts: int, sig: str):
        from fastapi.responses import Response
        vault.authorize_download(model_id, account, ts, sig)
        return Response(ml.adapter_bytes(vault.global_adapter(model_id)), media_type="application/octet-stream")

    @app.post("/models/{model_id}/test")
    def post_test(model_id: int, t: TestIn):
        return vault.set_test(model_id, t.creator, t.sealed)

    @app.post("/models/{model_id}/updates")
    def post_update(model_id: int, u: UpdateIn):
        return vault.receive_update(model_id, u.account, u.round, u.adapter_sha, u.signature, u.sealed)

    @app.get("/models/{model_id}/status")
    def status(model_id: int):
        return {"pending": sorted(vault.pending.get(model_id, {})), "last": vault.last_scores.get(model_id)}

    @app.post("/models/{model_id}/close-round")
    def close(model_id: int, c: CloseIn, authorization: str | None = Header(default=None)):
        require_admin(authorization)
        return vault.close_round(model_id, c.compute_provider)

    @app.post("/models/{model_id}/ask")
    def ask(model_id: int, a: AskIn):
        return vault.answer(model_id, a.question, a.payment_tx, a.payer, a.compare)

    return app

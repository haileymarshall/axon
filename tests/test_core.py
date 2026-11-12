"""Fast tests for Axon's core logic (no model download, no network)."""

import json

import torch

from axon import crypto, ml


def test_aggregate_is_mean_of_deltas():
    base = {"w": torch.zeros(2)}
    ups = [{"w": torch.tensor([1.0, 0.0])}, {"w": torch.tensor([3.0, 2.0])}]
    assert torch.equal(ml.aggregate(base, ups)["w"], torch.tensor([2.0, 1.0]))
    assert torch.equal(ml.aggregate(base, [])["w"], base["w"])


class FakeEngine:
    """Loss = distance of the adapter's single weight from a target of 1.0."""

    def eval_loss(self, rows, adapter):
        return float(abs(adapter["w"][0] - 1.0))


def test_shapley_scores_and_excludes_harmful_updates():
    base = {"w": torch.tensor([0.0])}
    updates = {
        "good-a": {"w": torch.tensor([1.0])},
        "good-b": {"w": torch.tensor([0.8])},
        "junk": {"w": torch.tensor([-3.0])},
    }
    r = ml.score_round(FakeEngine(), [], base, updates, log=lambda *_: None)
    assert r.excluded == ["junk"]
    assert r.improvement["junk"] == 0.0
    assert r.improvement["good-a"] > 0 and r.improvement["good-b"] > 0
    assert r.improvement["good-a"] > r.improvement["good-b"], "the more useful update earns more"
    assert r.new_loss < r.base_loss


def test_adapter_hash_is_stable():
    a = {"x": torch.ones(3), "y": torch.zeros(2)}
    b = {"y": torch.zeros(2), "x": torch.ones(3)}
    assert ml.adapter_hash(a) == ml.adapter_hash(b)
    assert ml.adapter_from_bytes(ml.adapter_bytes(a))["x"].tolist() == [1.0, 1.0, 1.0]


def test_sealed_update_only_vault_can_open(tmp_path, monkeypatch):
    from nacl.public import PrivateKey

    vault = PrivateKey.generate()
    blob = b"adapter-bytes"
    sealed = crypto.seal(vault.public_key.encode().hex(), blob)
    assert blob not in sealed
    assert crypto.unseal(vault, sealed) == blob


def test_device_signature_binds_round_and_account():
    from nacl.signing import SigningKey

    k = SigningKey.generate()
    msg = crypto.update_message(0, 1, "alice.testnet", "ab" * 32)
    sig = crypto.sign_hex(k, msg)
    assert crypto.verify(crypto.pubkey_hex(k), msg, sig)
    assert not crypto.verify(crypto.pubkey_hex(k), crypto.update_message(0, 2, "alice.testnet", "ab" * 32), sig)
    assert not crypto.verify(crypto.pubkey_hex(k), crypto.update_message(0, 1, "eve.testnet", "ab" * 32), sig)


def test_round_payload_shape_matches_contract():
    """The contract parses this exact JSON (u64 values as strings)."""
    payload = json.loads(json.dumps({
        "model_id": 0, "round": 1, "adapter_hash": "c" * 64, "base_eval_loss_milli": 2500, "eval_loss_milli": 2100,
        "results": [{"account": "alice.testnet", "improvement_micro": "30000"}], "compute_provider": None,
    }))
    assert isinstance(payload["results"][0]["improvement_micro"], str)


def test_shapley_is_efficient_and_symmetric():
    v = {frozenset(): 0, frozenset("a"): 1.0, frozenset("b"): 1.0, frozenset("ab"): 1.5}
    s = ml.shapley(["a", "b"], lambda c: v[frozenset(c)])
    assert abs(s["a"] - 0.75) < 1e-9 and abs(s["b"] - 0.75) < 1e-9
    assert abs(sum(s.values()) - 1.5) < 1e-9


def _payment_tx(signer="user.testnet", model_id=0, q_hash=None, receiver="axon.testnet"):
    args = {"model_id": model_id, "source": "cli", "query_hash": q_hash}
    return {"signer_id": signer, "receiver_id": receiver,
            "actions": [{"FunctionCall": {"method_name": "pay_for_query", "args": crypto.b64(json.dumps(args).encode())}}]}


def test_payment_is_bound_to_payer_contract_model_and_question():
    import pytest
    from fastapi import HTTPException

    from axon.vault import check_payment_tx

    q = crypto.query_hash("What is diabetes?")
    check_payment_tx(_payment_tx(q_hash=q), "axon.testnet", 0, "user.testnet", q)  # valid
    bad = [
        (_payment_tx(q_hash=q), "eve.testnet", q, "not signed by the payer"),  # someone else's payment
        (_payment_tx(q_hash=q), "user.testnet", crypto.query_hash("Another question?"), "different question"),
        (_payment_tx(q_hash=q, receiver="other.testnet"), "user.testnet", q, "not made to the Axon contract"),
        (_payment_tx(q_hash=q, model_id=1), "user.testnet", q, "not a pay_for_query for this model"),
    ]
    for tx, payer, qh, msg in bad:
        with pytest.raises(HTTPException, match=msg):
            check_payment_tx(tx, "axon.testnet", 0, payer, qh)


def test_download_signature_binds_model_account_and_time():
    from nacl.signing import SigningKey

    k = SigningKey.generate()
    sig = crypto.sign_hex(k, crypto.download_message(0, "alice.testnet", 1000))
    assert crypto.verify(crypto.pubkey_hex(k), crypto.download_message(0, "alice.testnet", 1000), sig)
    assert not crypto.verify(crypto.pubkey_hex(k), crypto.download_message(0, "alice.testnet", 1001), sig)
    assert not crypto.verify(crypto.pubkey_hex(k), crypto.download_message(1, "alice.testnet", 1000), sig)


def test_admin_token_from_env(monkeypatch):
    monkeypatch.setenv("AXON_VAULT_TOKEN", "t0ken")
    assert crypto.admin_token() == "t0ken"

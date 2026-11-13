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


def test_grade_matches_exact_gene_and_inheritance():
    from axon import data

    p = {"gene": "XK", "inheritance": "x-linked recessive", "kind": "gene"}
    assert data.grade("Mutations in the XK gene; it is X-linked recessive.", p) == {"gene": True, "inheritance": True, "correct": True}
    assert data.grade("Mutations in the XKR8 gene, autosomal dominant.", p)["correct"] is False
    assert data.grade("It is inherited in an X-linked recessive pattern.", {**p, "kind": "inheritance"})["correct"] is True


def test_round_keeps_only_updates_that_help_together():
    """a and b each help alone but hurt together; c hurts. Drop the least useful one at a time: one of a/b stays."""
    from axon import ml

    v = {"": 0.0, "a": 0.3, "b": 0.3, "c": -0.5, "ab": -0.05, "ac": 0.4, "bc": 0.4, "abc": 0.3}

    class FakeEngine:
        def eval_loss(self, test, adapter):
            return 1.0 - v["".join(k for i, k in enumerate("abc") if adapter["x"][i] > 0)]

    base = {"x": torch.zeros(3)}
    ups = {k: {"x": torch.eye(3)[i] * 3} for i, k in enumerate("abc")}
    sc = ml.score_round(FakeEngine(), [], base, ups, log=lambda *_: None)
    assert len(sc.excluded) == 2 and "c" in sc.excluded
    kept = [k for k in "abc" if k not in sc.excluded]
    assert sc.improvement[kept[0]] > 0 and abs(sc.base_loss - sc.new_loss - 0.3) < 1e-9


def test_round_where_nothing_helps_is_rejected():
    from axon import ml

    class FakeEngine:
        def eval_loss(self, test, adapter):
            return 1.0 + 0.1 * float((adapter["x"] > 0).sum())  # every update makes it worse

    base = {"x": torch.zeros(2)}
    ups = {k: {"x": torch.eye(2)[i] * 2} for i, k in enumerate("ab")}
    sc = ml.score_round(FakeEngine(), [], base, ups, log=lambda *_: None)
    assert sc.excluded == ["a", "b"] and sc.new_loss == sc.base_loss and sum(sc.improvement.values()) == 0
    assert torch.equal(sc.global_adapter["x"], base["x"])


def test_lora_sum_merge_keeps_each_contributors_change():
    from axon import ml

    old = ml.CFG.merge
    object.__setattr__(ml.CFG, "merge", "lora-sum")  # CFG is a frozen dataclass

    base = {"m.lora_A.weight": torch.ones(2), "m.lora_B.weight": torch.zeros(2)}
    ups = [{"m.lora_A.weight": torch.ones(2) * 1.2, "m.lora_B.weight": torch.tensor([1.0, 0.0])},
           {"m.lora_A.weight": torch.ones(2) * 0.8, "m.lora_B.weight": torch.tensor([0.0, 2.0])}]
    merged = ml.aggregate(base, ups)
    assert torch.allclose(merged["m.lora_A.weight"], torch.ones(2))  # A: averaged
    assert torch.allclose(merged["m.lora_B.weight"], torch.tensor([1.0, 2.0]))  # B: each change kept in full
    object.__setattr__(ml.CFG, "merge", old)
    assert torch.allclose(ml.aggregate(base, ups)["m.lora_B.weight"], torch.tensor([0.5, 1.0]))  # mean (default)


def test_everyone_in_the_merged_model_owns_a_share():
    """The mainnet round-1 case: with spammer d in the mix, c scores positive (+0.13), but next to a and b alone it adds
    nothing (-0.017). c must be left out of the merge, not merged for a 0% share."""
    from axon import ml

    base_v = {"": 0.0, "a": 0.3, "b": 0.3, "c": 0.05, "ab": 0.5, "ac": 0.3, "bc": 0.3, "abc": 0.4}

    class FakeEngine:
        def eval_loss(self, test, adapter):
            s = {k for i, k in enumerate("abcd") if adapter["x"][i] > 0}
            r = base_v["".join(k for k in "abc" if k in s)]
            if "d" in s:
                r += -0.4 + (0.3 if "c" in s else 0.0)
            return 1.0 - r

    base = {"x": torch.zeros(4)}
    ups = {k: {"x": torch.eye(4)[i] * 4} for i, k in enumerate("abcd")}
    sc = ml.score_round(FakeEngine(), [], base, ups, log=lambda *_: None)
    assert sc.excluded == ["c", "d"]
    assert sc.improvement["c"] == 0 and sc.improvement["d"] == 0
    assert sc.improvement["a"] > 0 and sc.improvement["b"] > 0
    assert abs(sum(sc.improvement.values()) - (sc.base_loss - sc.new_loss)) < 1e-9  # shares add up to the gain
    assert sc.global_adapter["x"][2] == 0 and sc.global_adapter["x"][3] == 0  # c and d are not in the model


def test_security_demo_has_no_leakage():
    """Training, hidden test, showcase questions and the cheater's data never share a vulnerability report."""
    import pytest
    from axon import data
    from axon.config import CFG

    if not list((CFG.data_dir / "raw").glob("nvd-*.json")):
        pytest.skip("NVD data not downloaded")
    o = data.prepare_security()
    qs = lambda f: {json.loads(line)["q"] for line in open(f)}
    honest = set().union(*[qs(o[k]) for k in data.SECURITY_SPECIALTIES])
    test, bob = qs(o["test"]), qs(o["bob"])
    probes = {p["q"] for p in json.loads(o["probes"].read_text())}
    assert not (test & honest) and not (probes & honest) and not (probes & test)
    assert not (bob & (honest | test | probes))

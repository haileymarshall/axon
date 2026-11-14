"""NEAR AI Cloud data prep: pure checks (no network)."""

import hashlib
import json

from axon import nearai


def test_bound_identity_pads_ecdsa_address_to_32_bytes():
    b = nearai._bound_identity("0x" + "ab" * 20)
    assert len(b) == 32 and b[:20] == bytes.fromhex("ab" * 20) and b[20:] == b"\0" * 12


def test_compose_hash_must_match_mr_config_id():
    compose = '{"name":"x"}'
    good = (b"\x01" + hashlib.sha256(compose.encode()).digest()).ljust(48, b"\0").hex()
    assert nearai._compose_ok({"tcb_info": json.dumps({"app_compose": compose})}, good)[0]
    assert not nearai._compose_ok({"tcb_info": {"app_compose": compose + " "}}, good)[0]
    assert not nearai._compose_ok({}, good)[0]


def test_parse_pairs_ignores_thinking_and_bad_items():
    text = '<think>{"pairs":[]}</think> Sure: {"pairs": [{"q": "What gene?", "a": "PAH."}, {"q": "", "a": "x"}, "junk"]}'
    assert nearai._parse_pairs(text) == [{"q": "What gene?", "a": "PAH."}]
    assert nearai._parse_pairs("no json here") == []


def test_prep_sends_nothing_when_attestation_fails(monkeypatch):
    sent = []
    monkeypatch.setattr(nearai, "attest", lambda model, key: {"ok": False, "checks": [], "signers": []})
    monkeypatch.setattr(nearai, "chat", lambda *a, **k: sent.append(a))
    r = nearai.prep("Patient Jane Doe ...", key="k")
    assert not r["ok"] and r["pairs"] == [] and sent == []


def test_sample_notes_are_marked_fictional():
    from pathlib import Path
    text = (Path(__file__).resolve().parent.parent / "samples" / "clinic-notes.txt").read_text()
    assert text.startswith("FICTIONAL SAMPLE")


def test_prep_uses_each_models_question_wording():
    from axon import data
    assert nearai.WORDING["security"].format(q="X") == data.SECURITY_Q.format(d="X")
    assert nearai.WORDING["basque"].format(q="X") == data.BASQUE_Q.format(en="X")

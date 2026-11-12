"""Keys, signatures and encryption.

* Device key (ed25519): each contributor signs its update so the vault knows who sent it.
  The public half is registered on-chain with `join_model`.
* Vault keys: an ed25519 key that signs round results (verified by the contract) and an X25519
  key that contributors encrypt updates to (sealed box), so only the vault can read an update.
"""

from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path

from nacl.public import PrivateKey, PublicKey, SealedBox
from nacl.signing import SigningKey, VerifyKey

from .config import CFG


def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def b64(b: bytes) -> str:
    return base64.b64encode(b).decode()


def unb64(s: str) -> bytes:
    return base64.b64decode(s)


def _key_file(name: str) -> Path:
    return CFG.state_dir / "keys" / f"{name}.json"


def load_or_create_signing_key(name: str) -> SigningKey:
    path = _key_file(name)
    if path.exists():
        return SigningKey(bytes.fromhex(json.loads(path.read_text())["ed25519_seed"]))
    key = SigningKey.generate()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"ed25519_seed": key.encode().hex()}))
    path.chmod(0o600)
    return key


def load_or_create_box_key(name: str) -> PrivateKey:
    path = _key_file(name + "-box")
    if path.exists():
        return PrivateKey(bytes.fromhex(json.loads(path.read_text())["x25519_secret"]))
    key = PrivateKey.generate()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"x25519_secret": key.encode().hex()}))
    path.chmod(0o600)
    return key


def pubkey_hex(key: SigningKey) -> str:
    return key.verify_key.encode().hex()


def sign_hex(key: SigningKey, msg: bytes) -> str:
    return key.sign(msg).signature.hex()


def verify(pubkey_hex_: str, msg: bytes, sig_hex: str) -> bool:
    try:
        VerifyKey(bytes.fromhex(pubkey_hex_)).verify(msg, bytes.fromhex(sig_hex))
        return True
    except Exception:
        return False


def seal(recipient_x25519_hex: str, plaintext: bytes) -> bytes:
    return SealedBox(PublicKey(bytes.fromhex(recipient_x25519_hex))).encrypt(plaintext)


def unseal(key: PrivateKey, ciphertext: bytes) -> bytes:
    return SealedBox(key).decrypt(ciphertext)


def update_message(model_id: int, round_: int, account: str, adapter_sha: str) -> bytes:
    """Canonical bytes a contributor signs for an update."""
    return f"axon-update:{model_id}:{round_}:{account}:{adapter_sha}".encode()


def download_message(model_id: int, account: str, ts: int) -> bytes:
    """Canonical bytes a contributor signs to download the current shared adapter."""
    return f"axon-download:{model_id}:{account}:{ts}".encode()


def query_hash(question: str) -> str:
    """sha256 of the question; stored with the on-chain payment so the payment covers only this question."""
    return sha256_hex(question.encode())


def admin_token() -> str:
    """Bearer token for the vault's operator-only endpoints (closing a round).

    Taken from AXON_VAULT_TOKEN, or created once in the state dir (shared by the local CLI and vault)."""
    import os
    import secrets

    if os.environ.get("AXON_VAULT_TOKEN"):
        return os.environ["AXON_VAULT_TOKEN"]
    path = _key_file("vault-admin")
    if path.exists():
        return json.loads(path.read_text())["token"]
    tok = secrets.token_hex(32)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"token": tok}))
    path.chmod(0o600)
    return tok

"""Runtime configuration. Everything can be overridden with environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _env(name: str, default: str) -> str:
    return os.environ.get(name, default)


@dataclass(frozen=True)
class Config:
    # Base model being fine-tuned. Laptop mode uses a 135M model so the full loop runs on CPU;
    # GPU mode swaps in a larger instruct model with the same code path.
    base_model: str = _env("AXON_BASE_MODEL", "HuggingFaceTB/SmolLM2-135M-Instruct")
    max_len: int = int(_env("AXON_MAX_LEN", "128"))
    lora_rank: int = int(_env("AXON_LORA_RANK", "8"))
    # Layers the adapter trains. Attention only by default; adding the MLP layers (gate/up/down_proj) lets it learn facts.
    lora_targets: str = _env("AXON_LORA_TARGETS", "q_proj,k_proj,v_proj,o_proj")
    # How the vault merges adapters: "mean" (FedAvg, default) or "lora-sum" (keeps each change at full strength; tuning 4 showed it overshoots).
    merge: str = _env("AXON_MERGE", "mean")
    local_steps: int = int(_env("AXON_LOCAL_STEPS", "16"))
    batch_size: int = int(_env("AXON_BATCH", "4"))
    lr: float = float(_env("AXON_LR", "1e-3"))

    data_dir: Path = Path(_env("AXON_DATA", str(ROOT / "data")))
    state_dir: Path = Path(_env("AXON_STATE", str(ROOT / "state")))

    # NEAR
    network: str = _env("AXON_NETWORK", "testnet")
    contract_id: str = _env("AXON_CONTRACT", "")
    rpc_url: str = field(default_factory=lambda: _env(
        "AXON_RPC", "https://rpc.testnet.near.org" if _env("AXON_NETWORK", "testnet") == "testnet"
        else "https://rpc.mainnet.near.org"))

    # Services
    vault_url: str = _env("AXON_VAULT_URL", "http://127.0.0.1:8700")


CFG = Config()

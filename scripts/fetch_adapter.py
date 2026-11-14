"""Fetch a model's trained adapter from the vault that recorded it, and check it against the on-chain hash.

    python scripts/fetch_adapter.py 7 8 9 --out state/vault

Uses a contributor's device key (contributors may download the shared model). Writes <out>/model-<id>/global.safetensors
only if sha256 of the adapter equals the adapter_hash recorded on NEAR for the latest round, so a serving vault answers
with exactly the model the TEE recorded.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from axon import ml  # noqa: E402
from axon.chain import Near  # noqa: E402
from axon.runs import _trained_adapter as trained_adapter  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("models", type=int, nargs="+")
    ap.add_argument("--out", default="state/vault")
    a = ap.parse_args()
    near = Near()
    for mid in a.models:
        rounds = near.view("get_rounds", {"model_id": mid})
        want = rounds[-1]["adapter_hash"]
        m = near.view("get_model", {"model_id": mid})
        m["adapter_hash"] = want
        adapter = trained_adapter(mid, m)
        got = ml.adapter_hash(adapter)
        if got != want:
            raise SystemExit(f"model {mid}: hash mismatch {got} != {want}")
        p = Path(a.out) / f"model-{mid}" / "global.safetensors"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(ml.adapter_bytes(adapter))
        print(f"model {mid}: adapter sha256 {got[:16]}… = on-chain hash (round {rounds[-1]['round']}) -> {p}")


if __name__ == "__main__":
    main()

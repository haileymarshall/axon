"""Offline tuning run: the same federated training, merging and Shapley scoring the vault does, without the
chain, so training settings can be chosen before a real (on-chain) run. Every tuning run is saved under
runs/tune-<id>/ and published like any other run.

    AXON_BASE_MODEL=Qwen/Qwen2.5-1.5B-Instruct AXON_LORA_TARGETS=q_proj,k_proj,v_proj,o_proj,gate_proj,up_proj,down_proj \
    AXON_LORA_RANK=16 AXON_LOCAL_STEPS=120 AXON_LR=3e-4 python scripts/tune.py --rounds 3
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from axon import data, ml, runs  # noqa: E402
from axon.config import CFG  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", type=int, default=2)
    ap.add_argument("--id", default=None)
    a = ap.parse_args()
    rid = a.id or "tune-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M")
    out = ROOT / "runs" / rid
    out.mkdir(parents=True, exist_ok=True)
    env = runs.start(out)
    t0 = time.time()
    log_lines: list[str] = []

    def log(msg: str) -> None:
        print(msg, flush=True)
        log_lines.append(msg)

    engine = ml.Engine()
    test = data.read_jsonl(CFG.data_dir / "vault" / "test.jsonl")
    people = {c: data.read_jsonl(CFG.data_dir / "contributors" / f"{c}.jsonl") for c in data.CONTRIBUTORS}
    log(f"base {CFG.base_model} targets {CFG.lora_targets} rank {CFG.lora_rank} steps {CFG.local_steps} lr {CFG.lr} rounds {a.rounds}")
    glob = engine.initial
    history, owned = [], {c: 0.0 for c in people}
    for r in range(1, a.rounds + 1):
        updates = {}
        for i, (c, rows) in enumerate(people.items()):
            ts = time.time()
            updates[c] = engine.train(rows, glob, seed=r * 10 + i)
            log(f"round {r}: {c} trained on {len(rows)} rows in {time.time() - ts:.0f}s")
        sc = ml.score_round(engine, test, glob, updates, log=log)
        glob = sc.global_adapter
        for c, v in sc.improvement.items():
            owned[c] += v
        history.append({"round": r, "base_loss": sc.base_loss, "new_loss": sc.new_loss, "excluded": sc.excluded,
                        "improvement": sc.improvement})
        log(f"round {r}: hidden-test loss {sc.base_loss:.4f} -> {sc.new_loss:.4f}; excluded {sc.excluded}")
    total = sum(owned.values()) or 1
    probes = [{"question": p["q"], "contributor": p.get("owner"), "disease": p.get("disease"), "reference": p.get("reference"),
               "base_model": engine.generate(p["q"], engine.initial), "axon_trained": engine.generate(p["q"], glob)}
              for p in runs.probes()]
    summary = {"run_id": rid, "kind": "offline tuning (no chain)", "started_at": env["started_at"],
               "wall_minutes": round((time.time() - t0) / 60, 1), "config": env["config"], "hardware": env["hardware"],
               "rounds": history, "ownership": {c: round(100 * v / total, 1) for c, v in owned.items()}, "probes": probes,
               "recall": runs.recall(probes)}
    (out / "summary.json").write_text(json.dumps(summary, indent=1))
    (out / "log.txt").write_text("\n".join(log_lines) + "\n")
    lines = [f"# Tuning run {rid}", "", "Offline: same training, merging and Shapley scoring as the vault, no chain.", "",
             f"* `{CFG.base_model}` · LoRA rank {CFG.lora_rank} on `{CFG.lora_targets}` · {CFG.local_steps} local steps · lr {CFG.lr} · {a.rounds} rounds · {summary['wall_minutes']} min",
             f"* Hidden-test loss: {history[0]['base_loss']:.3f} → {history[-1]['new_loss']:.3f}",
             f"* Ownership: " + ", ".join(f"{k} {v}%" for k, v in summary["ownership"].items()),
             runs.recall_line(summary["recall"]), ""]
    lines += runs.probe_lines(probes)
    (out / "summary.md").write_text("\n".join(lines))
    log(f"saved {out}")


if __name__ == "__main__":
    main()

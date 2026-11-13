"""Rebuild RUNS.md from every published run record in runs/*/summary.json."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
R = ROOT / "runs"


def facts(s: dict) -> str:
    r = s.get("recall") or {}
    b, t = r.get("base_model", {}), r.get("axon_trained", {})
    parts = []
    if b.get("gene_of"):
        parts.append(f"gene {b['gene']}→{t['gene']}/{b['gene_of']}")
    if b.get("inheritance_of"):
        parts.append(f"inheritance {b['inheritance']}→{t['inheritance']}/{b['inheritance_of']}")
    if b.get("cwe_of"):
        parts.append(f"CWE {b['cwe']}→{t['cwe']}/{b['cwe_of']}")
    if b.get("chrf_of"):
        parts.append(f"chrF {b['chrf']}→{t['chrf']}")
    return ", ".join(parts) or "–"


def main() -> None:
    chain, tune = [], []
    for f in sorted(R.glob("*/summary.json")):
        s = json.loads(f.read_text())
        rid = f.parent.name
        if "tune" in rid:
            h, c = s["rounds"], s["config"]
            tune.append(f"| [{rid}](runs/{rid}/summary.md) | `{c.get('base_model', '').split('/')[-1]}` · {c.get('local_steps')} steps · lr {c.get('lr')} · merge {c.get('merge', 'mean')} · {len(h)} rounds | {h[0]['base_loss']:.3f} → {h[-1]['new_loss']:.3f} | {facts(s)} | {', '.join(f'{k} {v}%' for k, v in s['ownership'].items())} |")
        else:
            L = s["hidden_test_loss"]
            where = "TEE (Intel TDX)" if "tee" in rid else s["hardware"]
            chain.append(f"| [{rid}](runs/{rid}/summary.md) | {s['network']} · model {s['model_id']} | {where} | `{s['base_model'].split('/')[-1]}` | {len(s['rounds'])} | {L['before']:.3f} → {L['after']:.3f} | {facts(s)} | {', '.join(f'{k} {v}%' for k, v in s['ownership'].items())} |")
    out = ["# Training runs", "",
           "Every Axon run, published as it happened, including the ones that failed. Each row links to its full record in `runs/` "
           "(hardware, config, full log, on-chain transactions, base vs trained answers graded automatically, and for recorded runs the terminal recording `terminal.cast`).", "",
           "## On-chain runs", "",
           "| Run | Network | Scored on | Base model | Rounds | Hidden-test score (lower is better) | Facts right (base → Axon) | Ownership |",
           "|---|---|---|---|---|---|---|---|", *chain, "",
           "Scores: health = answer-token loss; cyber = error rate (1 − accuracy); Basque = 1 − chrF/100. "
           "Model 4 was scored and recorded by a vault inside an attested Intel TDX TEE ([`runs/tee-mainnet/`](runs/tee-mainnet/)).", "",
           "## Failed attempts (kept on purpose)", "",
           "| Attempt | What went wrong | Fix |", "|---|---|---|",
           "| [attempt1-oom](runs/20261113-mainnet-rtx4090-qwen1.5b-attempt1-oom/) | CUDA out of memory: vault (fp32) and a contributor's training on one 24 GB GPU | Vault holds the base model in bf16; training uses gradient checkpointing |",
           "| [attempt2-gas](runs/20261113-mainnet-rtx4090-qwen1.5b-attempt2-gas/) | Vault account below the gas reservation; vault had already dropped the updates | Vault advances only after the round is on-chain; updates kept on failure |",
           "| [model0-scoring-bug](runs/20261113-mainnet-model0-scoring-bug/summary.md) | Completed, but neuro-clinic was merged with a 0% share | Drop the least useful update and re-score until every merged update owns a share |",
           "| TEE attempts 1–4 ([`runs/tee-mainnet/deployments.txt`](runs/tee-mainnet/deployments.txt)) | `rpc.mainnet.near.org` deprecated; FastNEAR rate-limited the TEE; py-near's client does not work inside the TEE | FastNEAR default; endpoint rotation; transactions signed locally and broadcast over HTTPS, same signed bytes resent (never executes twice) |", "",
           "## Offline tuning runs (no chain)", "",
           "Same training, merging and Shapley scoring as the vault (`scripts/tune.py`), used to choose settings before each on-chain run.", "",
           "| Run | Settings | Hidden-test score | Facts right (base → Axon) | Ownership |", "|---|---|---|---|---|", *tune, ""]
    (ROOT / "RUNS.md").write_text("\n".join(out))
    print(f"RUNS.md: {len(chain)} on-chain runs, {len(tune)} tuning runs")


if __name__ == "__main__":
    main()

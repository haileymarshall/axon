"""Run records: every training run is saved under runs/<id>/ and listed in RUNS.md, so results are public
and checkable. A record holds the hardware, config, full log, per-round loss, each contributor's Shapley
shares, the on-chain transactions, and the same questions answered by the base model and the trained one.
"""

from __future__ import annotations

import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from .config import CFG, ROOT

RUNS_MD = ROOT / "RUNS.md"
# Questions asked to the base model and the trained model in every run: reworded questions about facts in
# the contributors' data (written by `data.prepare` to data/probes.json, each with the reference answer).
DEFAULT_PROBES = [{"q": "What are the symptoms of type 2 diabetes?"}]


def probes() -> list[dict]:
    path = CFG.data_dir / "probes.json"
    return json.loads(path.read_text()) if path.exists() else DEFAULT_PROBES


def _sh(*cmd: str) -> str:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=20).stdout.strip()
    except Exception:
        return ""


def hardware() -> dict:
    import torch

    gpu = None
    if torch.cuda.is_available():
        p = torch.cuda.get_device_properties(0)
        gpu = {"name": p.name, "memory_gb": round(p.total_memory / 2**30, 1), "count": torch.cuda.device_count(),
               "cuda": torch.version.cuda, "nvidia_smi": _sh("nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader")}
    return {"gpu": gpu, "cpu": platform.processor() or platform.machine(), "cpu_count": __import__("os").cpu_count(),
            "os": platform.platform(), "python": platform.python_version(), "torch": torch.__version__}


def start(run_dir: Path) -> dict:
    """Write env.json at the start of a run."""
    run_dir.mkdir(parents=True, exist_ok=True)
    env = {
        "started_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "hardware": hardware(),
        "config": {k: str(v) for k, v in CFG.__dict__.items() if k not in ("data_dir", "state_dir")},
        "git_commit": _sh("git", "-C", str(ROOT), "rev-parse", "--short", "HEAD") or None,
    }
    (run_dir / "env.json").write_text(json.dumps(env, indent=1))
    return env


def recall(answers: list[dict]) -> dict:
    """How many showcase facts (gene, inheritance pattern) each model got right."""
    out = {}
    for who in ("base_model", "axon_trained"):
        g = [a["graded"][who] for a in answers if a.get("graded")]
        out[who] = {"gene": sum(x["gene"] for x in g), "inheritance": sum(x["inheritance"] for x in g), "of": len(g)}
    return out


def recall_line(r: dict) -> str:
    if not r or not r["base_model"]["of"]:
        return ""
    b, t = r["base_model"], r["axon_trained"]
    return (f"* **Facts recalled** (right gene / right inheritance, out of {b['of']}): base model **{b['gene']} / {b['inheritance']}**,"
            f" Axon-trained **{t['gene']} / {t['inheritance']}**")


def probe_lines(probes: list[dict]) -> list[str]:
    flat = lambda t: " ".join(str(t).split())
    mark = lambda g: (" ✅ gene" if g["gene"] else " ❌ gene") + (" ✅ inheritance" if g["inheritance"] else " ❌ inheritance")
    lines = []
    for p in probes:
        who = f" *(from {p['contributor']}'s data)*" if p.get("contributor") else ""
        g = p.get("graded")
        lines += [f"**Q: {p['question']}**{who}", ""]
        if p.get("gene"):
            lines += [f"* Answer in the data: gene **{p['gene']}**, {p['inheritance']}"]
        lines += [f"* Base{mark(g['base_model']) if g else ''}: {flat(p['base_model'])}",
                  f"* Axon-trained{mark(g['axon_trained']) if g else ''}: {flat(p['axon_trained'])}"]
        if p.get("reference"):
            lines += [f"* Reference: {flat(p['reference'])}"]
        lines += [""]
    return lines


def finish(run_dir: Path, model_id: int, wall_seconds: int) -> dict:
    """Write summary.json + summary.md for a finished run and add it to RUNS.md."""
    from . import data, ml
    from .chain import Near, yocto_to_near
    from .vault import VAULT_DIR

    env = json.loads((run_dir / "env.json").read_text())
    near = Near()
    m = near.view("get_model", {"model_id": model_id})
    rounds = near.view("get_rounds", {"model_id": model_id})
    total = int(m["total_shares"]) or 1

    # Same questions, base model vs trained model (run where the vault runs, which holds the weights).
    engine = ml.Engine()
    trained = ml.adapter_from_bytes((VAULT_DIR / f"model-{model_id}" / "global.safetensors").read_bytes())
    answers = [{"question": p["q"], "contributor": p.get("owner"), "disease": p.get("disease"), "reference": p.get("reference"),
                "base_model": engine.generate(p["q"], engine.initial), "axon_trained": engine.generate(p["q"], trained)}
               for p in probes()]
    for a, p in zip(answers, probes()):
        a["graded"] = {"base_model": data.grade(a["base_model"], p), "axon_trained": data.grade(a["axon_trained"], p)}
        a["gene"], a["inheritance"] = p.get("gene"), p.get("inheritance")

    gpu = (env["hardware"]["gpu"] or {}).get("name")
    summary = {
        "run_id": run_dir.name,
        "started_at": env["started_at"],
        "wall_minutes": round(wall_seconds / 60, 1),
        "hardware": gpu or f"CPU ({env['hardware']['cpu_count']} cores)",
        "base_model": m["base_model"],
        "network": CFG.network,
        "contract": near.contract_id,
        "model_id": model_id,
        "hidden_test_loss": {"before": m["base_eval_loss_milli"] / 1000, "after": m["eval_loss_milli"] / 1000},
        "rounds": [{"round": r["round"], "test_loss": r["eval_loss_milli"] / 1000, "adapter_hash": r["adapter_hash"],
                    "shares": {x["account"].split(".")[0]: int(x["shares"]) for x in r["results"]}}
                   for r in rounds],
        "ownership": {c["account"].split(".")[0]: round(100 * int(c["shares"]) / total, 1) for c in m["contributors"]},
        "queries_paid": m["queries"],
        "revenue_near": yocto_to_near(m["total_revenue"]),
        "probes": answers,
        "recall": recall(answers),
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=1))
    (run_dir / "summary.md").write_text(_markdown(summary))
    _add_to_index(summary)
    return summary


def _markdown(s: dict) -> str:
    ex = "https://testnet.nearblocks.io" if s["network"] == "testnet" else "https://nearblocks.io"
    lines = [
        f"# Run {s['run_id']}", "",
        f"* Hardware: **{s['hardware']}** · base model `{s['base_model']}` · wall time {s['wall_minutes']} min",
        f"* Contract: [`{s['contract']}`]({ex}/address/{s['contract']}) ({s['network']}), model id {s['model_id']}",
        f"* Hidden-test loss: **{s['hidden_test_loss']['before']:.3f} → {s['hidden_test_loss']['after']:.3f}**",
        f"* Paid queries: {s['queries_paid']} · paid to owners {s['revenue_near']:.4f} NEAR (after the 5% platform fee)", "",
        "## Ownership", "", "| Contributor | Share |", "|---|---|",
        *[f"| {k} | {v}% |" for k, v in s["ownership"].items()], "",
        "## Rounds", "", "| Round | Test loss | Shares minted | Adapter hash |", "|---|---|---|---|",
        *[f"| {r['round']} | {r['test_loss']:.3f} | {', '.join(f'{k} {v}' for k, v in r['shares'].items())} | `{r['adapter_hash'][:16]}…` |" for r in s["rounds"]], "",
        "## Same question, base model vs Axon-trained model", "",
        "Reworded questions about facts in the contributors' private data. *Reference* is the answer in that data.", "",
        recall_line(s.get("recall")), "",
    ]
    lines += probe_lines(s["probes"])
    lines += ["Full output: `log.txt`. Hardware and config: `env.json`. Transactions are in the log and on the explorer.", ""]
    return "\n".join(lines)


def _add_to_index(s: dict) -> None:
    if not RUNS_MD.exists():
        RUNS_MD.write_text(
            "# Training runs\n\nEvery Axon training run, published as it happened: hardware, logs, on-chain results and "
            "sample answers. Each row links to its full record in `runs/`.\n\n"
            "| Run | Hardware | Base model | Rounds | Hidden-test loss | Time | Ownership |\n|---|---|---|---|---|---|---|\n")
    own = ", ".join(f"{k} {v}%" for k, v in s["ownership"].items())
    row = (f"| [{s['run_id']}](runs/{s['run_id']}/summary.md) | {s['hardware']} | `{s['base_model']}` | {len(s['rounds'])} | "
           f"{s['hidden_test_loss']['before']:.3f} → {s['hidden_test_loss']['after']:.3f} | {s['wall_minutes']} min | {own} |\n")
    with RUNS_MD.open("a") as f:
        f.write(row)

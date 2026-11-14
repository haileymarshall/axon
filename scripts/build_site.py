"""Build the static site in web/ for free hosting (e.g. Vercel): no server needed.

Writes web/site.json (which contract to read, optional live backend URL, demo video link) and web/runs.json
(every published run summary), so the page can read NEAR from the browser and show the recorded answers.

    python scripts/build_site.py --network mainnet --contract axon.ebukaa.near [--api https://… ] [--video https://…]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--network", default="mainnet")
    ap.add_argument("--contract", required=True)
    ap.add_argument("--api", default="", help="live app backend (vault online); leave empty for read-only")
    ap.add_argument("--video", default="")
    ap.add_argument("--rpc", default="")
    a = ap.parse_args()
    site = {"network": a.network, "contract": a.contract, "api": a.api, "video": a.video}
    if a.rpc:
        site["rpc"] = a.rpc
    (ROOT / "web" / "site.json").write_text(json.dumps(site, indent=1) + "\n")
    runs = [json.loads(f.read_text()) for f in sorted((ROOT / "runs").glob("*/summary.json"), reverse=True)]
    runs = [r for r in runs if r.get("contract")]
    (ROOT / "web" / "runs.json").write_text(json.dumps(runs))
    # Serverless functions (web/api/) share the NEAR AI Cloud verifier with the CLI; fictional samples for the demo.
    import shutil
    shutil.copy(ROOT / "axon" / "nearai.py", ROOT / "web" / "api" / "_nearai.py")
    (ROOT / "web" / "samples").mkdir(exist_ok=True)
    for f in (ROOT / "samples").glob("*.txt"):
        shutil.copy(f, ROOT / "web" / "samples" / f.name)
    # Saved evidence of every TEE vault (runs/<dir>/tee.json manifests), re-checked live by the model pages.
    vaults = []
    for man in sorted((ROOT / "runs").glob("*/tee.json")):
        t = json.loads(man.read_text())
        ev = json.loads((man.parent / t["evidence"]).read_text())
        ev = ev.get("info", ev)
        vaults.append({"combiner_key": ev["combiner_key"], "code_hash": ev["code_hash"], "quote": ev["attestation"]["quote"],
                       "commit": t["commit"], "cvm": t["cvm"], "round_txs": t.get("round_txs", {}),
                       "evidence": f"runs/{man.parent.name}/{t['evidence']}"})
    (ROOT / "web" / "tee.json").write_text(json.dumps({"vaults": vaults}))
    print(f"web/site.json → {site}\nweb/runs.json → {len(runs)} runs")


if __name__ == "__main__":
    main()

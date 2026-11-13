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
    print(f"web/site.json → {site}\nweb/runs.json → {len(runs)} runs")


if __name__ == "__main__":
    main()

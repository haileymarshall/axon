"""Demo data: simulates independent contributors, each holding a private slice of health data.

Source: MedQuAD (NIH health Q&A, CC BY 4.0), via the Hugging Face mirror
`keivalya/MedQuad-MedicalQnADataset`.

Contributors in the demo:
  * alice        - a person managing diabetes        (diabetes questions)
  * heart-clinic - a cardiology clinic                (heart questions)
  * onco-clinic  - an oncology clinic                 (cancer questions)
  * bob          - submits spam (word-salad answers); the scoring should give him nothing
The hidden test set mixes all three topics and is held ONLY by the vault (sealed combiner).
"""

from __future__ import annotations

import csv
import json
import random
import re
import urllib.request
from pathlib import Path

from .config import CFG

SOURCE_URL = (
    "https://huggingface.co/datasets/keivalya/MedQuad-MedicalQnADataset/resolve/main/medDataset_processed.csv"
)
TOPICS = {
    "diabetes": r"diabet|insulin|blood sugar|glucose|hypoglyc",
    "heart": r"heart|cardi|coronary|arrhythm|hypertension|high blood pressure|atrial",
    "cancer": r"cancer|tumor|carcinoma|leukemia|lymphoma|melanoma|sarcoma",
}
CONTRIBUTORS = {"alice": "diabetes", "heart-clinic": "heart", "onco-clinic": "cancer", "bob": "junk"}


def load_rows(raw: Path) -> list[dict]:
    if not raw.exists():
        raw.parent.mkdir(parents=True, exist_ok=True)
        print(f"downloading {SOURCE_URL}")
        urllib.request.urlretrieve(SOURCE_URL, raw)
    with raw.open(newline="", encoding="utf-8") as f:
        return [
            {"q": r["Question"].strip().rstrip("?").strip() + "?", "a": " ".join(r["Answer"].split())}
            for r in csv.DictReader(f)
            if r["Question"] and r["Answer"]
        ]


def prepare(per_contributor: int = 96, test_per_topic: int = 8, seed: int = 7) -> dict[str, Path]:
    """Write one private JSONL file per contributor plus the vault's hidden test set."""
    rng = random.Random(seed)
    rows = load_rows(CFG.data_dir / "raw" / "medquad.csv")
    rng.shuffle(rows)
    by_topic: dict[str, list[dict]] = {t: [] for t in TOPICS}
    for r in rows:
        for t, pat in TOPICS.items():
            if re.search(pat, r["q"], re.I):
                by_topic[t].append(r)
                break

    test, out = [], {}
    for t in TOPICS:
        test += by_topic[t][:test_per_topic]
    for name, topic in CONTRIBUTORS.items():
        if topic == "junk":
            # spam: real-looking questions with word-salad answers
            pool = [r for t in TOPICS for r in by_topic[t][test_per_topic:]]
            items = []
            for r in rng.sample(pool, per_contributor):
                words = r["a"].split()
                rng.shuffle(words)
                items.append({"q": r["q"], "a": " ".join(words)})
        else:
            items = by_topic[topic][test_per_topic: test_per_topic + per_contributor]
        out[name] = _write(CFG.data_dir / "contributors" / f"{name}.jsonl", items)
    out["test"] = _write(CFG.data_dir / "vault" / "test.jsonl", test)
    return out


def _write(path: Path, items: list[dict]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it) + "\n")
    return path


def read_jsonl(path: Path) -> list[dict]:
    with Path(path).open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


if __name__ == "__main__":
    for k, v in prepare().items():
        print(k, v, sum(1 for _ in v.open()))

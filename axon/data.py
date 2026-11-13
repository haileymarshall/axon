"""Demo data: simulates independent contributors, each holding a private slice of rare-disease knowledge.

Source: MedQuAD (NIH health Q&A, CC BY 4.0), via the Hugging Face mirror
`keivalya/MedQuad-MedicalQnADataset`. We keep only **rare genetic conditions** (diseases that have a
"genetic changes" entry from NIH Genetics Home Reference). General models know little about these, which
stands in for what Axon is for: specialist knowledge that base models have not seen.

Contributors in the demo:
  * neuro-clinic     - a rare neurological disease clinic   (ataxias, dystrophies, neuropathies, epilepsies)
  * metabolic-clinic - a rare metabolic disease clinic      (enzyme deficiencies, storage disorders)
  * alice            - a parent in a rare-syndrome family group (genetic syndromes)
  * bob              - farms rewards with spam answers; the scoring should give him nothing

Every disease belongs to exactly one contributor. For some of each contributor's diseases, one question is
held back into the vault's hidden test set (never given to anyone), so the test measures whether the merged
model learned about those diseases from the contributors' other questions. `probes.json` lists reworded
questions about facts in the contributors' data (which gene; which inheritance pattern), asked to the base model and the
trained model in every run and graded automatically (`grade`).
"""

from __future__ import annotations

import csv
import json
import random
import re
import urllib.request
from collections import defaultdict
from pathlib import Path

from .config import CFG

SOURCE_URL = (
    "https://huggingface.co/datasets/keivalya/MedQuad-MedicalQnADataset/resolve/main/medDataset_processed.csv"
)
# Question templates in MedQuAD; the captured group is the disease name.
QUESTION_FORMS = [
    r"What is \(are\) (.+)", r"What are the signs and symptoms of (.+)", r"What are the symptoms of (.+)",
    r"What causes (.+)", r"Is (.+) inherited", r"What are the treatments for (.+)",
    r"How many people are affected by (.+)", r"What are the genetic changes related to (.+)",
    r"How to diagnose (.+)", r"What is the outlook for (.+)", r"Who is at risk for (.+)",
]
SPECIALTIES = {
    "neuro-clinic": r"neuropath|ataxi|dystroph|epilep|encephal|spastic|batten|myopath|dystonia|palsy|neuro|seizure",
    "metabolic-clinic": r"deficien|storage|acidemia|aciduria|metabol|lipid|glycogen|mucopolysacchar|lysosom",
    "alice": r"syndrome",
}
CONTRIBUTORS = [*SPECIALTIES, "bob"]
# Held-back test questions prefer hard facts a base model would have to guess.
TEST_QTYPES = ("frequency", "inheritance", "genetic changes")
# Reworded versions of the data's own questions ("What are the genetic changes related to X?", "Is X inherited?").
PROBE_FORMS = {"gene": "Which gene is linked to {d}?", "inheritance": "How is {d} passed down in families?"}
PROBES_PER_CONTRIBUTOR = 4
INHERITANCE = r"autosomal dominant|autosomal recessive|X-linked dominant|X-linked recessive|mitochondrial"


# ----------------------------------------------------------------- several demo models
# The health demo (domain "rare-diseases") keeps the original paths; other demos live under data/<domain>/.

def paths(domain: str | None = None) -> dict[str, Path]:
    d = CFG.data_dir
    if not domain or domain == "rare-diseases":
        return {"contributors": d / "contributors", "test": d / "vault" / "test.jsonl", "probes": d / "probes.json"}
    return {"contributors": d / domain / "contributors", "test": d / "vault" / f"{domain}.jsonl", "probes": d / domain / "probes.json"}


def grade(answer: str, probe: dict) -> dict:
    """Is the answer right? Gene questions: names the exact gene symbol. Inheritance questions: names the right
    pattern. `correct` is the check for the probe's own kind."""
    if probe.get("kind") == "cwe":
        # the first CWE the answer names must be the right one (listing several does not count)
        first = re.search(r"CWE-\d+", answer)
        return {"correct": bool(first) and first.group(0) == probe["answer"]}
    gene = bool(probe.get("gene")) and re.search(rf"\b{re.escape(probe['gene'])}\b", answer) is not None
    inh = bool(probe.get("inheritance")) and probe["inheritance"] in answer.lower()
    return {"gene": gene, "inheritance": inh, "correct": inh if probe.get("kind") == "inheritance" else gene}


def load_rows(raw: Path) -> list[dict]:
    if not raw.exists():
        raw.parent.mkdir(parents=True, exist_ok=True)
        print(f"downloading {SOURCE_URL}")
        urllib.request.urlretrieve(SOURCE_URL, raw)
    with raw.open(newline="", encoding="utf-8") as f:
        return [
            {"q": r["Question"].strip().rstrip("?").strip().rstrip("?").strip() + "?",
             "a": " ".join(r["Answer"].split()), "qtype": r["qtype"]}
            for r in csv.DictReader(f)
            if r["Question"] and r["Answer"]
        ]


def disease_of(q: str) -> str | None:
    q = q.rstrip("?").strip()
    for form in QUESTION_FORMS:
        m = re.fullmatch(form, q)
        if m:
            return m.group(1).strip()
    return None


def rare_diseases(rows: list[dict]) -> dict[str, list[dict]]:
    """Group rows by disease, keeping rare genetic conditions with at least 4 questions."""
    by: dict[str, list[dict]] = defaultdict(list)
    names: dict[str, str] = {}
    genetic = set()
    for r in rows:
        d = disease_of(r["q"])
        if not d:
            continue
        key = d.lower()
        names.setdefault(key, d)
        by[key].append(r)
        if r["qtype"] == "genetic changes":
            genetic.add(key)
    return {names[k]: v for k, v in by.items() if k in genetic and len(v) >= 4}


def prepare(diseases_per_contributor: int = 30, test_per_contributor: int = 8, seed: int = 7) -> dict[str, Path]:
    """Write one private JSONL file per contributor, the vault's hidden test set, and the probe questions."""
    rng = random.Random(seed)
    rare = rare_diseases(load_rows(CFG.data_dir / "raw" / "medquad.csv"))
    names = sorted(rare)
    rng.shuffle(names)
    owned: dict[str, list[str]] = {c: [] for c in SPECIALTIES}
    for d in names:
        for c, pat in SPECIALTIES.items():
            if re.search(pat, d, re.I):
                if len(owned[c]) < diseases_per_contributor:
                    owned[c].append(d)
                break

    test, probes, out = [], [], {}
    for c, diseases in owned.items():
        items = []
        for i, d in enumerate(diseases):
            rows = list(rare[d])
            if i < test_per_contributor:
                held = next((r for r in rows if r["qtype"] in TEST_QTYPES), rows[-1])
                rows.remove(held)
                test.append({"q": held["q"], "a": held["a"], "owner": c})
            gene = next((r for r in rows if r["qtype"] == "genetic changes"), None)
            inh = next((r for r in rows if r["qtype"] == "inheritance"), None)
            sym = re.match(r"Mutations in the ([A-Z][A-Z0-9-]{1,11}) gene", gene["a"]) if gene else None
            pat = re.search(INHERITANCE, inh["a"], re.I) if inh else None
            if sym and pat and sum(p["owner"] == c for p in probes) < 2 * PROBES_PER_CONTRIBUTOR:
                fact = {"owner": c, "disease": d, "gene": sym.group(1), "inheritance": pat.group(0).lower()}
                probes.append({**fact, "kind": "gene", "q": PROBE_FORMS["gene"].format(d=d), "reference": gene["a"][:420]})
                probes.append({**fact, "kind": "inheritance", "q": PROBE_FORMS["inheritance"].format(d=d), "reference": inh["a"][:320]})
            items += [{"q": r["q"], "a": r["a"]} for r in rows]
        rng.shuffle(items)
        out[c] = _write(CFG.data_dir / "contributors" / f"{c}.jsonl", items)

    # bob farms rewards with junk: real-looking rare-disease questions answered with spam
    used = {d for ds in owned.values() for d in ds}
    pool = [r for d in names if d not in used for r in rare[d]]
    n = max(len(_read_len(p)) for p in out.values())
    junk = [{"q": r["q"], "a": _spam(rng)} for r in rng.sample(pool, min(n, len(pool)))]
    out["bob"] = _write(CFG.data_dir / "contributors" / "bob.jsonl", junk)
    out["test"] = _write(CFG.data_dir / "vault" / "test.jsonl", test)
    probes_path = CFG.data_dir / "probes.json"
    probes_path.write_text(json.dumps(probes, indent=1))
    out["probes"] = probes_path
    return out


SPAM = [
    "Click here to claim your free prize!", "Limited time offer, act now.", "Best prices on supplements, visit our store today.",
    "Earn $500 a day from home with this one trick.", "Follow me for more tips and giveaways.", "Use code SAVE50 at checkout.",
    "Doctors hate this simple secret.", "Subscribe and share with your friends!", "Our miracle tea cures everything in 7 days.",
    "Reply YES to win a brand new phone.", "Crypto signals group, 1000% gains guaranteed, DM me.", "Lowest prices online, free shipping worldwide.",
]


def _spam(rng: random.Random) -> str:
    return " ".join(rng.sample(SPAM, rng.randint(2, 4)))


def _read_len(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def _write(path: Path, items: list[dict]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it) + "\n")
    return path


def read_jsonl(path: Path) -> list[dict]:
    with Path(path).open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


# ----------------------------------------------------------------- cyber security demo
# Source: NIST National Vulnerability Database (public domain, US government), CVEs published 1-15 July 2026,
# i.e. after both base models were trained. Contributors are independent security researchers, each holding
# reports in their speciality; the task is to classify a new vulnerability's weakness type (CWE).

SECURITY_SPECIALTIES = {
    "web-hunter": {"CWE-79": "Cross-site Scripting (XSS)", "CWE-89": "SQL Injection", "CWE-918": "Server-Side Request Forgery (SSRF)",
                   "CWE-22": "Path Traversal", "CWE-352": "Cross-Site Request Forgery (CSRF)", "CWE-434": "Unrestricted Upload of Dangerous File",
                   "CWE-78": "OS Command Injection", "CWE-94": "Code Injection", "CWE-601": "Open Redirect", "CWE-502": "Deserialization of Untrusted Data"},
    "memory-hunter": {"CWE-416": "Use After Free", "CWE-122": "Heap-based Buffer Overflow", "CWE-125": "Out-of-bounds Read",
                      "CWE-787": "Out-of-bounds Write", "CWE-121": "Stack-based Buffer Overflow", "CWE-476": "NULL Pointer Dereference",
                      "CWE-190": "Integer Overflow", "CWE-120": "Classic Buffer Overflow", "CWE-415": "Double Free", "CWE-401": "Memory Leak"},
    "auth-hunter": {"CWE-862": "Missing Authorization", "CWE-863": "Incorrect Authorization", "CWE-639": "Authorization Bypass Through User-Controlled Key (IDOR)",
                    "CWE-287": "Improper Authentication", "CWE-306": "Missing Authentication for Critical Function", "CWE-284": "Improper Access Control",
                    "CWE-200": "Exposure of Sensitive Information", "CWE-269": "Improper Privilege Management", "CWE-798": "Hard-coded Credentials",
                    "CWE-285": "Improper Authorization"},
}
SECURITY_Q = "Which CWE weakness type does this vulnerability belong to? Answer with the CWE ID and name.\n\nVulnerability: {d}"


def load_nvd(raw_dir: Path) -> list[dict]:
    """CVEs with exactly one CWE from the saved NVD API pages (data/raw/nvd-*.json)."""
    out = []
    for f in sorted(raw_dir.glob("nvd-*.json")):
        for v in json.loads(f.read_text()).get("vulnerabilities", []):
            c = v["cve"]
            desc = next((x["value"] for x in c.get("descriptions", []) if x["lang"] == "en"), "")
            cwes = sorted({w2["value"] for w in c.get("weaknesses", []) for w2 in w["description"] if w2["value"].startswith("CWE-")})
            if len(cwes) == 1 and desc:
                out.append({"id": c["id"], "cwe": cwes[0], "desc": " ".join(desc.split())[:900]})
    return out


def prepare_security(per_contributor: int = 220, test_per: int = 10, probes_per: int = 8, seed: int = 11) -> dict[str, Path]:
    rng = random.Random(seed)
    seen, cves = set(), []
    for c in load_nvd(CFG.data_dir / "raw"):  # NVD repeats identical descriptions across CVEs: keep one
        if c["desc"] not in seen:
            seen.add(c["desc"])
            cves.append(c)
    rng.shuffle(cves)
    pth = paths("security")
    taken: set[str] = set()
    test, probes, out = [], [], {}
    for who, cwes in SECURITY_SPECIALTIES.items():
        mine = [c for c in cves if c["cwe"] in cwes]
        qa = lambda c: {"q": SECURITY_Q.format(d=c["desc"]), "a": f"{c['cwe']}: {cwes[c['cwe']]}."}
        for c in mine[:test_per]:
            test.append({**qa(c), "owner": who})
        for c in mine[test_per:test_per + probes_per]:
            probes.append({"q": SECURITY_Q.format(d=c["desc"]), "owner": who, "label": c["id"], "kind": "cwe",
                           "answer": c["cwe"], "answer_label": f"{c['cwe']}: {cwes[c['cwe']]}", "reference": c["desc"],
                           "why": f"{c['id']} was published in July 2026, after the base model was trained. The Axon model learned from "
                                  f"{who}'s past reports how vulnerabilities like this are classified."})
        rows = [qa(c) for c in mine[test_per + probes_per: test_per + probes_per + per_contributor]]
        taken |= {c["id"] for c in mine[: test_per + probes_per + per_contributor]}
        out[who] = _write(pth["contributors"] / f"{who}.jsonl", rows)
    # bob farms rewards: real reports, but labelled with a random wrong weakness type (same format as honest work)
    names = {k: v for spec in SECURITY_SPECIALTIES.values() for k, v in spec.items()}
    fake = []
    for c in [c for c in cves if c["id"] not in taken][:per_contributor]:
        wrong = rng.choice([k for k in names if k != c["cwe"]])  # never the right label
        fake.append({"q": SECURITY_Q.format(d=c["desc"]), "a": f"{wrong}: {names[wrong]}."})
    out["bob"] = _write(pth["contributors"] / "bob.jsonl", fake)
    out["test"] = _write(pth["test"], test)
    pth["probes"].parent.mkdir(parents=True, exist_ok=True)
    pth["probes"].write_text(json.dumps(probes, indent=1))
    out["probes"] = pth["probes"]
    return out


DEMOS = {"rare-diseases": {"prepare": "prepare", "contributors": None}, "security": {"prepare": "prepare_security", "contributors": [*SECURITY_SPECIALTIES, "bob"]}}


def contributors(domain: str | None = None) -> list[str]:
    return (DEMOS.get(domain or "rare-diseases") or {}).get("contributors") or CONTRIBUTORS


if __name__ == "__main__":
    for k, v in prepare().items():
        print(k, v, sum(1 for _ in v.open()))

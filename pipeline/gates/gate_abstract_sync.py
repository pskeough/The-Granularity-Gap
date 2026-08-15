#!/usr/bin/env python
"""Abstract-sync gate.

arXiv stores the abstract TWICE: once inside the compiled PDF, and once as free text pasted into
the submission form. They are never diffed by anything. On arXiv:2606.05183v1 they describe
different experiments -- the listing page claims six variants / 73 prompts / a 0-4 Likert /
rho = -0.63, while the PDF claims eight variants / 350 prompts / a 1-5 Likert / rho = +0.40.
Search engines, Semantic Scholar and every human triaging the paper read the listing, not the PDF.

This gate compares the load-bearing tokens of the two abstracts and fails on any divergence.

Usage:
  python gate_abstract_sync.py                     # use cached metadata abstract
  python gate_abstract_sync.py --fetch             # re-fetch the live arXiv listing first
  python gate_abstract_sync.py --meta FILE.txt     # compare against an arbitrary candidate

Exit 0 clean, 1 on any divergence.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TEX = next((p for p in (ROOT / "paper" / "main_granularitygap.tex",
                        ROOT / "main_granularitygap_v2.tex",
                        ROOT / "main_granularitygap.tex") if p.exists()),
           ROOT / "main_granularitygap.tex")
CACHE = HERE / "arxiv_metadata_abstract.txt"
ARXIV_ID = "2606.05183"

# Words that carry a count in either abstract; normalised so "six" and "6" compare equal.
NUMWORD = {"one": "1", "two": "2", "three": "3", "four": "4", "five": "5", "six": "6",
           "seven": "7", "eight": "8", "nine": "9", "ten": "10"}

# Claims that must agree, expressed as (label, regex over the normalised abstract text).
LOAD_BEARING = [
    ("model variants", r"(\d+)\s+(?:gemini\s+)?(?:model\s+)?variants"),
    ("adversarial prompts", r"(\d+)\s+adversarial\s+prompts\b"),
    ("prompt categories", r"(\d+)\s+adversarial\s+prompt\s+categories"),
    ("graded responses", r"([\d,]+)\s+(?:graded\s+)?responses"),
    ("likert scale", r"(\d\s*-\s*\d)\s+likert"),
    ("guardrail conditions", r"(\d+)\s+guardrail\s+conditions"),
    ("sycophancy-truthfulness rho", r"rho\s*=\s*(-?[\d.]+)"),
    ("variance explained", r"(\d+)\s*(?:percent|%)\s+of\s+(?:the\s+)?(?:graded\s+)?variance"),
]


def fetch_live() -> str:
    import gzip
    import urllib.request
    req = urllib.request.Request(
        f"https://arxiv.org/abs/{ARXIV_ID}",
        headers={"User-Agent": "Mozilla/5.0 (paper-self-audit)", "Accept-Encoding": "gzip"},
    )
    r = urllib.request.urlopen(req, timeout=90)
    raw = r.read()
    if r.headers.get("Content-Encoding") == "gzip":
        raw = gzip.decompress(raw)
    html = raw.decode("utf-8", "replace")
    m = re.search(r'<blockquote class="abstract[^"]*">(.*?)</blockquote>', html, re.S)
    if not m:
        raise SystemExit("gate_abstract_sync: could not locate the abstract block on the listing page")
    txt = re.sub(r"<[^>]+>", "", m.group(1))
    txt = txt.replace("&gt;", ">").replace("&lt;", "<").replace("&amp;", "&")
    txt = re.sub(r"^\s*Abstract:\s*", "", re.sub(r"\s+", " ", txt).strip())
    CACHE.write_text(txt, encoding="utf-8")
    return txt


def manuscript_abstract() -> str:
    tex = TEX.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", tex, re.S)
    if not m:
        raise SystemExit("gate_abstract_sync: no abstract environment in the manuscript")
    return m.group(1)


def normalise(s: str) -> str:
    s = s.lower()
    # map meaningful control sequences to words BEFORE stripping the rest
    s = s.replace("\\rho", "rho").replace("ρ", "rho")
    s = re.sub(r"r\$\^?\{?2\}?\$?\s*=\s*0\.29", "29 percent of variance", s)
    s = re.sub(r"\\[a-z]+\{([^}]*)\}", r"\1", s)     # \textbf{x} -> x
    s = re.sub(r"\\[a-z]+", " ", s)                   # drop remaining control sequences
    s = s.replace("$", "").replace("\\%", "%").replace("~", " ")
    s = re.sub(r"(\d),(\d{3})", r"\1\2", s)           # 8,830 -> 8830
    for w, d in NUMWORD.items():
        s = re.sub(rf"\b{w}\b", d, s)
    s = re.sub(r"5-point", "1-5 likert", s)
    # "71% of behavioural variance unexplained" states the same fact as "explain 29 percent"
    s = re.sub(r"71\s*%\s*of\s+behavioral\s+variance\s+unexplained", "29 percent of variance", s)
    s = re.sub(r"\s+", " ", s)
    return s


def extract(text: str) -> dict[str, str | None]:
    n = normalise(text)
    out = {}
    for label, pat in LOAD_BEARING:
        m = re.search(pat, n)
        val = next((x for x in m.groups() if x), None) if m else None
        out[label] = val.replace(" ", "") if val else None
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--meta", type=Path)
    ap.add_argument("--tex", type=Path)
    a = ap.parse_args()

    global TEX
    if a.tex:
        TEX = a.tex

    if a.meta:
        meta_txt = a.meta.read_text(encoding="utf-8")
        source = str(a.meta)
    elif a.fetch:
        meta_txt = fetch_live()
        source = f"live arxiv.org/abs/{ARXIV_ID}"
    else:
        if not CACHE.exists():
            raise SystemExit("gate_abstract_sync: no cached metadata abstract; run with --fetch")
        meta_txt = CACHE.read_text(encoding="utf-8")
        source = f"cached {CACHE.name}"

    ms = extract(manuscript_abstract())
    mt = extract(meta_txt)

    print(f"gate_abstract_sync")
    print(f"  manuscript : {TEX.name}")
    print(f"  metadata   : {source}\n")

    bad = 0
    for label, _ in LOAD_BEARING:
        v_ms, v_mt = ms[label], mt[label]
        if v_ms is None and v_mt is None:
            print(f"  --     {label:32s} absent from both")
            continue
        if v_ms != v_mt:
            bad += 1
            print(f"  DIVERGE {label:32s} manuscript={v_ms!s:<8} metadata={v_mt!s}")
        else:
            print(f"  OK     {label:32s} {v_ms}")

    print()
    if bad:
        print(f"gate_abstract_sync: FAIL - {bad} load-bearing claim(s) differ between the "
              f"published PDF abstract and the abstract shown on the listing page")
        return 1
    print("gate_abstract_sync: PASS - listing abstract and PDF abstract agree")
    return 0


if __name__ == "__main__":
    sys.exit(main())

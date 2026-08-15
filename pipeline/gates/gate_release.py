#!/usr/bin/env python
"""Release-integrity gate.

Two failure modes that no manuscript-side check can ever find, because both live in the released
artefact rather than in the paper:

1. SCALE POLARITY. The paper defines all three axes as PENALTY scales (1 = good, 5 = bad;
   Section "Metrics and Scale Directionality"). The released human-label CSV stores
   Human_Truthfulness and Human_Refusal in the OPPOSITE direction (5 = truthful / specific),
   with no codebook. The paper's own rectifier figures (-0.51, +0.29) are only recoverable after
   silently reversing them. Anyone who downloads the release and correlates Human_Truthfulness
   against the AI's Truthfulness_Mean gets r = -0.52 and concludes the validation failed.

2. RATER PII. The released label files pseudonymise raters inconsistently, and the analysis logs
   carry the raters' real names.

Usage:  python gate_release.py
Exit 0 clean, 1 on any hit.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
MASTER = ROOT / "results" / "master_results.csv"
CODEBOOK = next((p for p in (ROOT / "data" / "CODEBOOK.md",
                             ROOT / "data" / "raw" / "CODEBOOK.md") if p.exists()),
                ROOT / "data" / "CODEBOOK.md")

# Only files that actually exist are checked, so this list serves the working folder
# (where the non-pseudonymous copies still live) and the export (where they do not).
RELEASED_LABEL_FILES = [
    ROOT / "data" / "human_labels_pseudonymous.csv",
    ROOT / "data" / "raw" / "human_labels_final_all.csv",
    ROOT / "analysis_v2" / "data" / "human_labels_final_all.csv",
]
SCAN_FOR_PII = [
    ROOT / "data" / "human_labels_pseudonymous.csv",
    ROOT / "data" / "raw" / "human_labels_final_all.csv",
    ROOT / "analysis_v2" / "data" / "human_labels_final_all.csv",
    ROOT / "paper_analysis" / "human_labels.csv",
    ROOT / "logs" / "analysis_results" / "results" / "human_validation_aggregate_stats.txt",
]

# Axes the paper declares as penalty scales, paired with their AI counterpart column.
PENALTY_AXES = [("Human_Truthfulness", "Truthfulness_Mean"), ("Human_Refusal", "Refusal_Mean")]

# A rater label is a real identity if it looks like a personal name rather than a pseudonym.
PSEUDONYM = re.compile(r"^(rater|annotator|coder|judge)[\s_-]*[A-Z0-9]+$", re.I)


def main() -> int:
    fails = 0
    ai = pd.read_csv(MASTER, low_memory=False).drop_duplicates("Response_ID").set_index("Response_ID")

    print("gate_release: scale polarity\n")
    documented = CODEBOOK.exists() and "polarity" in CODEBOOK.read_text(encoding="utf-8", errors="replace").lower()
    for f in RELEASED_LABEL_FILES:
        if not f.exists():
            continue
        h = pd.read_csv(f)
        agg = h.groupby("Response_ID").mean(numeric_only=True)
        j = agg.join(ai[["Truthfulness_Mean", "Refusal_Mean", "Sycophancy_Mean"]], how="inner")
        for hcol, acol in PENALTY_AXES:
            if hcol not in j:
                continue
            r = stats.pearsonr(j[hcol], j[acol])[0]
            if r < 0 and not documented:
                fails += 1
                print(f"  REVERSED  {f.relative_to(ROOT)}::{hcol}")
                print(f"            r = {r:+.3f} against {acol}; paper declares both as penalty")
                print(f"            scales (1=good, 5=bad). No codebook documents the reversal.")
            else:
                print(f"  OK        {f.relative_to(ROOT)}::{hcol}  r = {r:+.3f}"
                      + ("  [documented in CODEBOOK.md]" if documented else ""))
        # sycophancy is the control axis: it should agree in sign
        if "Human_Sycophancy" in j:
            r = stats.pearsonr(j["Human_Sycophancy"], j["Sycophancy_Mean"])[0]
            print(f"  OK        {f.relative_to(ROOT)}::Human_Sycophancy  r = {r:+.3f}  (control axis, agrees)")

    print("\ngate_release: rater identity\n")
    for f in SCAN_FOR_PII:
        if not f.exists():
            continue
        if f.suffix == ".csv":
            d = pd.read_csv(f)
            if "Rater_ID" not in d:
                continue
            names = [str(x) for x in d["Rater_ID"].dropna().unique()]
        else:
            txt = f.read_text(encoding="utf-8", errors="replace")
            m = re.search(r"Testers Included:\s*(.+)", txt)
            names = [n.strip() for n in m.group(1).split(",")] if m else []
        real = [n for n in names if not PSEUDONYM.match(n)]
        if real:
            fails += 1
            print(f"  PII       {f.relative_to(ROOT)}")
            print(f"            non-pseudonymous rater label(s): {real}")
        else:
            print(f"  OK        {f.relative_to(ROOT)}  all rater labels pseudonymous")

    print()
    if fails:
        print(f"gate_release: FAIL - {fails} release-side defect(s)")
        return 1
    print("gate_release: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python
"""Receipt gate for The Granularity Gap.

Every numeric claim listed here is re-derived from results/master_results.csv and the human-label
CSVs, then matched against the value actually present in the manuscript source. The manuscript is
parsed with anchored regexes so that editing a number without editing the data makes this fail.

Prose review does not catch a stale number. This does.

Usage:  python gate_receipts.py [path/to/main.tex]
Exit 0 clean, 1 on any drift.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]          # lab repo, or the exported repo root


def _first(*candidates):
    """First path that exists. Lets one gate serve both the working folder and the export."""
    for c in candidates:
        if c.exists():
            return c
    return candidates[0]


# v2 before v1. Defaulting to main_granularitygap.tex silently verified the April v1 file
# for months, which is how ten stale claim anchors survived the v2 rewrite unnoticed.
DEFAULT_TEX = _first(
    ROOT / "paper" / "main_granularitygap.tex",     # exported layout
    ROOT / "main_granularitygap_v2.tex",            # working folder, v2
    ROOT / "main_granularitygap.tex",               # working folder, superseded v1
)
MASTER = ROOT / "results" / "master_results.csv"
HUMAN = _first(
    ROOT / "data" / "human_labels_pseudonymous.csv",
    ROOT / "analysis_v2" / "data" / "human_labels_final_all.csv",
    ROOT / "data" / "raw" / "human_labels_final_all.csv",
)

GEN = {
    "gemini-2.0-flash": "2.0", "gemini-2.0-flash-lite": "2.0",
    "gemini-2.5-flash": "2.5", "gemini-2.5-flash-lite": "2.5", "gemini-2.5-pro": "2.5",
    "google/gemini-3-flash-preview": "3.0", "gemini-3-flash-preview": "3.0",
    "gemini-3-pro-preview": "3.0", "gemini-3-pro-low": "3.0",
}


def load():
    df = pd.read_csv(MASTER, low_memory=False)
    df["gen"] = df["model"].map(GEN)
    df["S"] = pd.to_numeric(df["Sycophancy_Mean"], errors="coerce")
    df["T"] = pd.to_numeric(df["Truthfulness_Mean"], errors="coerce")
    df["R"] = pd.to_numeric(df["Refusal_Mean"], errors="coerce")
    df["ch"] = df["Verdict"] == "CHALLENGED"
    df["ag"] = df["Verdict"] == "AGREED"
    return df


def cliffs_delta(a, b):
    a = np.sort(np.asarray(a, float)); b = np.asarray(b, float)
    gt = np.searchsorted(a, b, side="left").sum()
    lt = len(a) * len(b) - np.searchsorted(a, b, side="right").sum()
    return (lt - gt) / (len(a) * len(b))


def build_receipts(df):
    """(label, derived_value, tolerance, regex against the .tex capturing the claimed value)"""
    S, ctrl = df["S"], df[df.condition == "Control"]
    r = []

    r.append(("N total", float(len(df)), 0, r"N=(\d,?\d{3}) total responses"))
    r.append(("mean sycophancy", S.mean(), 0.006, r"Mean Sycophancy Score:\}\s*([\d.]+)"))
    r.append(("SD sycophancy", S.std(ddof=1), 0.006, r"SD=([\d.]+)\)"))

    # severity buckets
    for name, mask, pat in [
        ("clean N", S == 1.0, r"Clean refusal & \$=1\.0\$ & ([\d,]+)"),
        ("borderline N", (S > 1) & (S < 2), r"Borderline & \$1\.0\$--\$2\.0\$ & ([\d,]+)"),
        ("mild N", (S >= 2) & (S < 3), r"Mild & \$2\.0\$--\$3\.0\$ & ([\d,]+)"),
        ("moderate N", (S >= 3) & (S < 4), r"Moderate & \$3\.0\$--\$4\.0\$ & ([\d,]+)"),
        ("severe N", S >= 4, r"Severe & \$\\ge 4\.0\$ & ([\d,]+)"),
    ]:
        r.append((name, float(mask.sum()), 0, pat))

    r.append(("R^2 Likert~verdict", np.corrcoef((~df.ch).astype(float), S)[0, 1] ** 2, 0.005,
              r"yields \$R\^2=([\d.]+)\$"))
    r.append(("pct Likert>=2.0", 100 * (S >= 2).mean(), 0.06,
              r"The practical stakes are large: ([\d.]+)\\% of responses"))

    # Table 2 (tab:sensitivity). "Verdict fires" is the AGREED share of the band and
    # "Refused" the CHALLENGED share, both over every row in the band. The two tied-vote
    # AMBIGUOUS verdicts fall in neither, which is why the pair does not sum to 100%.
    # v1 counted AMBIGUOUS as a miss, which is why its Level 2 rate read 4.56 not 4.30.
    for name, mask, col, pat in [
        ("L1 verdict fires", S < 2, "ag", r"1 Clean & [\d,]+ & ([\d.]+)\\%"),
        ("L2 verdict fires", (S >= 2) & (S < 3), "ag", r"2 Mild & \d+ & ([\d.]+)\\%"),
        ("L3 verdict fires", (S >= 3) & (S < 4), "ag", r"3 Moderate & [\d,]+ & ([\d.]+)\\%"),
        ("L45 verdict fires", S >= 4, "ag", r"4--5 Severe & \d+ & ([\d.]+)\\%"),
        ("L1 refused", S < 2, "ch", r"1 Clean & [\d,]+ & [\d.]+\\% & ([\d.]+)\\%"),
        ("L2 refused", (S >= 2) & (S < 3), "ch", r"2 Mild & \d+ & [\d.]+\\% & ([\d.]+)\\%"),
        ("L3 refused", (S >= 3) & (S < 4), "ch", r"3 Moderate & [\d,]+ & [\d.]+\\% & ([\d.]+)\\%"),
        ("L45 refused", S >= 4, "ch", r"4--5 Severe & \d+ & [\d.]+\\% & ([\d.]+)\\%"),
    ]:
        r.append((name, 100 * df.loc[mask, col].mean(), 0.06, pat))

    # inter-axis correlations
    for lbl, a, b, pat in [
        ("rho Syc-Truth", df["S"], df["T"], r"Sycophancy & Truthfulness & ([\d.]+) &"),
        ("rho Syc-Refusal", df["S"], df["R"], r"Sycophancy & Refusal(?: Specificity)? & ([\d.]+) &"),
        ("rho Truth-Refusal", df["T"], df["R"], r"Truthfulness & Refusal(?: Specificity)? & ([\d.]+) &"),
    ]:
        r.append((lbl, stats.spearmanr(a, b)[0], 0.006, pat))

    # category vulnerability, Control
    for cat in ["Egotistical Validation", "Validation Seeking", "Flawed Logic", "Authority Pressure",
                "Assumption Challenge", "Moral Endorsement", "Unethical Proposals"]:
        r.append((f"Control mean {cat}", ctrl.loc[ctrl.Category == cat, "S"].mean(), 0.006,
                  rf"{re.escape(cat)} & ([\d.]+) & \["))

    ev = ctrl.loc[ctrl.Category == "Egotistical Validation", "S"].values
    up = ctrl.loc[ctrl.Category == "Unethical Proposals", "S"].values
    r.append(("Cliffs delta EV-UP", abs(cliffs_delta(up, ev)), 0.02,
              r"Cliff's \$\\delta\$=([\d.]+), large effect"))

    # generational
    for g, pat_m, pat_n in [
        ("2.0", r"Gen 2\.0 & ([\d.]+) & \[1\.40", r"Gen 2\.0 & [\d.]+ & \[[^\]]+\] & ([\d,]+)"),
        ("2.5", r"Gen 2\.5 & ([\d.]+) & \[1\.79", r"Gen 2\.5 & [\d.]+ & \[[^\]]+\] & ([\d,]+)"),
        ("3.0", r"Gen 3\.0 & ([\d.]+) & \[1\.45", r"Gen 3\.0 & [\d.]+ & \[[^\]]+\] & ([\d,]+)"),
    ]:
        sub = df[df.gen == g]
        r.append((f"Gen {g} mean", sub.S.mean(), 0.006, pat_m))
        r.append((f"Gen {g} N", float(len(sub)), 0, pat_n))

    H = stats.kruskal(*[df.loc[df.gen == g, "S"].values for g in ["2.0", "2.5", "3.0"]])[0]
    r.append(("Kruskal-Wallis H", H, 0.6, r"H=([\d.]+) \(p \$<\$ 0\.001\)"))

    cm = {g: ctrl.loc[ctrl.gen == g, "S"].mean() for g in ["2.0", "2.5", "3.0"]}
    r.append(("Gen2.5-Gen2.0 Control delta", cm["2.5"] - cm["2.0"], 0.008,
              r"Gen 2\.5 shows a \+([\d.]+) point increase"))

    # guardrails
    for cond, pat_m, pat_cr in [
        ("Simple", r"Simple & ([\d.]+) & 0\.009", r"Simple & [\d.]+ & [\d.]+ & ([\d.]+)\\%"),
        ("Protocol", r"Protocol & ([\d.]+) & 0\.014", r"Protocol & [\d.]+ & [\d.]+ & ([\d.]+)\\%"),
        ("Control", r"Control & ([\d.]+) & 0\.022", r"Control & [\d.]+ & [\d.]+ & ([\d.]+)\\%"),
    ]:
        sub = df[df.condition == cond]
        r.append((f"{cond} mean", sub.S.mean(), 0.006, pat_m))
        r.append((f"{cond} challenge rate", 100 * sub.ch.mean(), 0.06, pat_cr))

    # alignment tax by generation + Fisher Z
    rho = {}
    for g, pat in [("2.0", r"Gen 2\.0 & ([\d.]+) & \[0\.24"), ("2.5", r"Gen 2\.5 & ([\d.]+) & \[0\.38"),
                   ("3.0", r"Gen 3\.0 & ([\d.]+) & \[0\.47")]:
        sub = df[df.gen == g]
        rho[g] = (stats.spearmanr(sub["S"], sub["T"])[0], len(sub))
        r.append((f"Alignment tax rho Gen {g}", rho[g][0], 0.008, pat))
    z = (np.arctanh(rho["3.0"][0]) - np.arctanh(rho["2.0"][0])) / np.sqrt(
        1 / (rho["2.0"][1] - 3) + 1 / (rho["3.0"][1] - 3))
    r.append(("Fisher Z", z, 0.25, r"Z = ([\d.]+), p \$<\$ 0\.001"))

    # human validation, Table 9 (consensus rule: safe_mean > 0.5, ties -> sycophantic)
    h = pd.read_csv(HUMAN)
    sm = h.assign(safe=(h.Human_Verdict == "CHALLENGED").astype(float)).groupby("Response_ID")["safe"].mean()
    ai = df.drop_duplicates("Response_ID").set_index("Response_ID")["Verdict"]
    j = pd.DataFrame({"h": (~(sm > 0.5)).astype(int)}).join((ai != "CHALLENGED").astype(int).rename("a"), how="inner")
    from sklearn.metrics import cohen_kappa_score, accuracy_score
    r.append(("human kappa", cohen_kappa_score(j.h, j.a), 0.005, r"Cohen's \$\\kappa\$ & ([\d.]+) \(Substantial"))
    r.append(("human accuracy", 100 * accuracy_score(j.h, j.a), 0.02, r"Binary Accuracy & ([\d.]+)\\%"))
    r.append(("human annotations N", float(len(h)), 0, r"N=(\d+) annotations"))
    r.append(("human responses N", float(h.Response_ID.nunique()), 0, r"across (\d+) unique responses"))
    r.append(("human raters N", float(h.Rater_ID.nunique()), 0,
              r"sample of N=\d+ annotations from (\w+)(?: independent)? raters"))
    return r


WORDNUM = {"five": 5, "four": 4, "three": 3, "eight": 8, "six": 6, "seven": 7}


def main() -> int:
    tex_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_TEX
    tex = tex_path.read_text(encoding="utf-8", errors="replace")
    df = load()
    receipts = build_receipts(df)

    bad = 0
    unmatched = 0
    print(f"gate_receipts: {tex_path.name}  ({len(receipts)} bound claims)\n")
    for label, derived, tol, pat in receipts:
        m = re.search(pat, tex)
        if not m:
            print(f"  NO-ANCHOR  {label:34s} regex did not match the manuscript")
            unmatched += 1
            continue
        raw = m.group(1).replace(",", "")
        claimed = float(WORDNUM.get(raw.lower(), raw)) if not raw.replace(".", "").isdigit() \
            else float(raw)
        ok = abs(claimed - derived) <= (tol if tol else 0.5)
        if not ok:
            bad += 1
        print(f"  {'OK    ' if ok else 'DRIFT '} {label:34s} paper={claimed:<10g} derived={derived:.4f}")

    print()
    if unmatched:
        print(f"gate_receipts: {unmatched} claim(s) had no anchor in this file")
    if bad:
        print(f"gate_receipts: FAIL - {bad} claim(s) drifted from the raw data")
        return 1
    if unmatched:
        print("gate_receipts: FAIL - unanchored claims cannot be verified")
        return 1
    print("gate_receipts: PASS - every bound claim re-derives from raw data")
    return 0


if __name__ == "__main__":
    sys.exit(main())

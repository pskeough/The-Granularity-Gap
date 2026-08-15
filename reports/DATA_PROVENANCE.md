# Data provenance and repository state

Established 2026-08-08 after the first audit pass, because the audit's conclusions are only as good
as the assumption that `results/master_results.csv` is the file the paper was computed from. That
assumption was asserted before it was proven. This document proves it, and records what else is
wrong with the working tree.

---

## 1. The response-level receipt is confirmed

Three copies are **byte-identical** (sha256 `63f9ccf4…`, 37,431,705 bytes):

```
results/master_results.csv
data/processed/master_results.csv
analysis_v2/data/master_dataset_v2.csv
```

Whichever a given script reads, it reads the same data. This is the receipt.

**Two other files are not it.**

| File | Rows | What it is |
|---|---|---|
| `data/processed/master_results_calibrated.csv` | **7,777** | Retired. Carries PPI columns (`ppi_sycophancy_score` etc.). Gives Control mean 2.2291 and Egotistical Validation 3.3500 — the paper reports 2.21 and 3.27, which is the 8,830-row file. This is the source of the "N=7,777" that appears in superseded drafts. |
| `data/raw/backup_master_results.csv` | — | Nov 2025 snapshot, 14.5 MB. Superseded. |

The paper reproduces from the 8,830-row file and from nothing else. That is why 126 of 129 bound
claims matched.

## 2. The generation-side raw receipt is partial but faithful

Every raw generation receipt recoverable from any location was checked against
`master_results.csv`, field by field.

| Source | JSONs | present in CSV | response-text mismatches | metadata mismatches |
|---|---|---|---|---|
| `results/raw_responses/` (local) | 225 | 225 | **0** | **0** |
| Drive backup `CompleteCodingProjectsUpload\Sychophancy` | 5,070 | 5,070 | **0** | 59 (cosmetic, see below) |
| extracted from `SYCPortable\raw_responses.rar` | 379 | 379 | **0** | **0** |

**5,674 receipts checked. Zero response-text divergences.** Coverage: **5,070 of 8,791 distinct
responses (57.7%)**.

The 59 metadata flags are a separator difference and nothing else: the JSON `model` field reads
`gemini_3_pro_low` where the CSV reads `gemini-3-pro-low`. Same model, same generation, no effect on
any analysis.

Those JSONs carry generation fields only — `Response_ID, timestamp, model, condition, Prompt_ID,
Category, Prompt_Text, Guardrail_Text, Full_Prompt, Assistant_Response`. **No scores.** They are a
subset of what the CSV already holds, which is why partial coverage does not constrain a rejudge
(see `REJUDGE_READINESS.md`).

## 3. There is no judge-side receipt, and this bounds the audit

`src/analysis/analyze_judge_logs.py` reads `results/judge_logs.jsonl`. **That file does not exist.**
No per-vote scores and no judge chain-of-thought survive anywhere in the tree.

The consequence is unavoidable and should be stated in any replication note: the `*_Mean` and
`*_StdDev` columns are the most primitive record of the judge's output that exists. They cannot be
re-derived from anything, and a corrupted or hand-edited score would leave no trace.

What can still be checked, and passes:

| Internal check | Result |
|---|---|
| `Verdict` == majority of `Vote_1..3` | **100.00%** of rows |
| `Refusal_Mean × 3` is an integer (consistent with 3 integer votes) | **100.00%** |
| `Sycophancy_Mean × 3` is an integer | 99.76% |
| `(mean, sd)` pairs achievable from 3 integers in 1–5 | 21 of 26 distinct pairs |

The five unachievable pairs all have sd = 0.7071 or 1.4142, which are the two-observation values.

## 4. 138 responses were not scored best-of-3

| votes recorded | responses |
|---|---|
| 3 | 8,692 |
| 2 | 108 |
| 1 | 30 |

§2.6 states a Best-of-3 mechanism without qualification. **1.56% of responses had fewer.**
Effect on headlines is small but non-zero: restricting to the 8,692 fully-voted responses moves
mean sycophancy 1.5967 → 1.5841 and Control mean 2.2114 → 2.1965, i.e. the paper's "2.21" would
become 2.20. No conclusion changes. Disclosed in v2 §2.3.

## 5. The DeepSeek cross-model files, and which one is right

Two files, nine minutes apart, and the difference decided a headline number:

| File | mtime | DeepSeek rows | weighted agreement |
|---|---|---|---|
| `unified_external_judge_data_BACKUP.csv` | 18:15:02 | 608 | 89.31% |
| `unified_external_judge_data.csv` | 18:24:06 | **582** | **93.30%** |

The 582-row file is the 608-row file minus 26 rows. **All 26 have `External_Verdict = ERROR` and
`External_Syc = 0.0`** — DeepSeek API/parse failures. They are counted as disagreements in the
608-row set purely because a failed call cannot agree.

**Excluding them is correct.** The paper's 93.3% is right. Its N=608 and its three per-condition
agreement cells are wrong, because those were computed error-inclusive. See `AUDIT_REPORT.md` F2.

Two earlier passes — the July 2026 gauntlet and the first pass of this audit — both concluded the
opposite by comparing summary statistics between the files instead of opening the excluded rows.

## 6. The working tree is not runnable as-is

Things that will bite anyone trying to reproduce this:

- **103 Python files hardcode `C:\Coding Projects\Sychophancy\...`**, a path that no longer exists;
  the project now lives at `C:\Research\Sychophancy`. Most of `analysis_v2/scripts/` is affected.
- **The figures are not in this tree.** `main_granularitygap.tex` references `Figures/Fig1.png`
  … `Fig9.png`; none are present under `Sychophancy/`. They exist only in
  `C:\Research\PaperarXiv\grangap\Figures\`. The paper cannot be compiled from the project folder
  alone.
- `results/judge_logs.jsonl` is absent (§3).
- `analysis_v2/scripts - Copy/` duplicates `analysis_v2/scripts/`, so a grep for the analysis that
  produced a number returns two candidates with no indication which ran.
- 10 `Response_ID` values are duplicated across 39 rows of the released CSV.

## 7. What the arXiv submission package contains

`C:\Research\PaperarXiv\grangap\` holds `main_granularitygap.tex` plus `Figures/`. Its `.tex` is
**content-identical** to `Sychophancy/main_granularitygap.tex` — the sha256 differs only because the
package copy uses LF and the working copy uses CRLF (normalised sha256 `f1218cef…` for both).
This is the only complete, buildable copy of the paper on disk.

`grangap_v2/` is the v2 package built during this audit: the revised `.tex` plus the same figures.


---

## 8. Recovered from backup (2026-08-08, second sweep)

Patrick supplied four backup locations. What they yielded:

| Location | Yield |
|---|---|
| `G:\...\CompleteCodingProjectsUpload\Sychophancy` | **5,070 raw response JSONs** (vs 225 in the working tree). Generation fields only, no scores. |
| `G:\...\CompleteCodingProjectsUpload\Sychophancy - Copy` | **`sycophancy_classifier.py` (Oct 2025) containing the judge prompt verbatim** — the artefact that settled F3b. Also `human_labeling_tool.html`, `pilot_human_labels.csv`, `Methodological_Specification_Guide.md`. |
| `G:\...\PaperBackups\SYCPortable` | `raw_responses.rar` (19 MB) — **partially corrupt**, 379 files extract then checksum errors. Likely an incomplete Drive sync. `Paper + Materials/` holds `FinalPaper.md`, `STATISTICAL_CORE_FINAL.md`, `SUPPLEMENTARY_MATERIALS.md`. |
| `G:\...\PaperBackups\The-Granularity-Gap-main` | **Skeleton only** — 6 files, all data directories empty. Not a usable copy of the release. |

The live GitHub repo, fetched directly, supplied what the backup could not: the `stats_report/`
execution logs (F7b), the released human-label CSV, and `DeepSeek_Cleaned_Final_v3.csv`.

**No `judge_logs.jsonl` exists in any location.** The per-vote judge scores and chain-of-thought are
gone. The `stats_report/` logs receipt the *aggregate* statistics, not the per-response scoring, so
§3 of `DATA_PROVENANCE.md` stands with that qualification.

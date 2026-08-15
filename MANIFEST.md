# MANIFEST

What is in this repository, what is not, and why.

Contents are decided by what the paper promises a reader, not by what happened to be on disk. The
export runs from an allowlist in `_pipeline/pack-granularity-gap.py`: a file ships only if it is
named there. Working folders at `C:\Research\Sychophancy` and `C:\Research\PaperarXiv\grangap_v2`
are read-only sources and are never cleaned in place.

Secrets scan: clean. No credential is hardcoded anywhere in the tree, and the working folder's
`.env` is excluded by name and by `.gitignore`.

## Included

| Path | What it is |
|---|---|
| `paper/main_granularitygap.tex` | the v2 manuscript source |
| `paper/main_granularitygap.pdf` | the compiled paper |
| `paper/Figures/` | Fig1 through Fig9, the images the manuscript compiles against |
| `paper/ARXIV_ABSTRACT.txt` | the corrected abstract for the arXiv listing form |
| `data/prompt_dataset.json` | the 350 adversarial prompts across 7 categories |
| `data/CODEBOOK.md` | column definitions, including the reversed human-label polarity |
| `data/human_labels_pseudonymous.csv` | the 236 human annotations, rater labels pseudonymised |
| `data/panel_sample.csv` | the 1,200-response stratified sample the judge panel scored |
| `data/panel_sample.sha256` | the sample's hash, so the panel can be reproduced against the same rows |
| `data/panel_allocation.md` | how the sample was stratified |
| `results/master_results.csv` | the base of record: 8,830 responses with per-axis scores |
| `results/judge_logs.jsonl` | 10,792 votes from four judges with full per-axis written reasoning |
| `results/claim_ledger.csv` | every bound numeric claim and where it comes from |
| `results/PANEL_RESULTS.md` | the panel's headline outputs |
| `results/VALIDATION.md`, `results/PROOFS.md` | the two-layer verification of those outputs |
| `results/NEW_FINDINGS.md` | what the per-vote reasoning yielded beyond the existing numbers |
| `pipeline/00_*` through `07_*` | the judge panel end to end: sample build, run, verify, analyse, validate, proofs |
| `pipeline/judge_rubric.py` | the rubric the four judges were given |
| `pipeline/generate_paper_figures.py` | the figure script |
| `pipeline/gates/` | the four gates, plus the derivation helpers they import |
| `pipeline/generation/` | the original corpus run: response deployment, the judge classifier, and the aggregator. `sycophancy_deployer_openrouter.py` is the script the manuscript names in Section 3 when it documents how the binary verdict is constructed |
| `pipeline/analysis_v1/` | the ten analysis scripts behind the v1 results, retained because Table 10's cross-model validation and the human-validation metrics still come from them |
| `data/deepseek_cross_validation.csv` | the 582 valid DeepSeek V3 paired comparisons behind Table 10 |
| `reports/STATISTICAL_MASTER_REPORT_v1.md` | the v1 statistical report, superseded but retained for the audit trail |
| `requirements.txt` | the pinned dependency set |
| `reports/DATA_PROVENANCE.md` | where each data file came from and which are superseded |
| `reports/BASE_PROVENANCE.md` | why `master_results.csv` is the base of record over the alternatives |
| `CHANGELOG.md` | the itemized v1 to v2 record |

`results/master_results.csv` has sha256 `63f9ccf41b1de838d3e93923f37a3cb737b00c017949a58950b7166b1d077c08`.
That is the hash the audit trail and the claim ledger both reference.

## Deliberately excluded

- **The non-pseudonymised human labels.** Three working files carry real rater names:
  `data/raw/human_labels_final_all.csv`, `paper_analysis/human_labels.csv`, and
  `logs/analysis_results/results/human_validation_aggregate_stats.txt`. The raters were family
  members of the author, which the paper discloses, and their names are not the author's to
  publish. The pseudonymised copy carries the same 236 annotations and every published human
  statistic re-derives from it.
- **`AUDIT_REPORT.md`.** The internal pre-release audit. It names the same individuals in prose,
  and it is process rather than receipt. It stays in `_gauntlet/`, which is not uploaded. The
  findings that survived it are in `CHANGELOG.md` and in the manuscript's own Limitations section.
- **The review and revision artifacts.** `REVIEWS.md`, `REVISION_PLAN.md`, `PROSE_REPORT.md`,
  `VENUE_OPTIONS.md` and the multi-agent critique output. Publishing raw review candidates, most
  of which were rejected, would misrepresent what was actually concluded.
- **`.env` and `scratch.pkl`.** A credential file and a 38 MB working pickle. Neither is an input
  to any published number.
- **The v1 manuscript** (`main_granularitygap.tex`, April 2026) and its backup. Superseded, and
  keeping it invites a gate being pointed at the wrong file, which is exactly how ten stale claim
  anchors went unnoticed until this export.
- **Per-judge raw API receipts.** The smoke-test JSONL files from the panel build carry request
  headers. `judge_logs.jsonl` carries the votes and reasoning without them.
- **`data_csv/master_dataset_v2.rar`**, carried by earlier revisions of this repo. A 6 MB archive
  of the corpus, superseded by `results/master_results.csv` in plain CSV.
- **`stats_report/*.log`** and the v1 paper build (`Granularity_Gap_v8.pdf`, `main1.tex`,
  `paper_figures/`). Execution logs and a superseded manuscript.

## One credential, removed

Earlier revisions of this repo carried `scripts_folder/Data Generation/Utils/config.py` with a
literal Google API key in it. The replacement at `pipeline/generation/config.py` reads
`GEMINI_API_KEY` from the environment and stores nothing. Removing the file from the current tree
does not remove it from the commit history, so the key itself has to be revoked at the provider
rather than deleted here.

## One deviation from the house layout

The standard slug layout is `paper/ pipeline/ results/`. This repo adds `data/` and `reports/`.
The paper's closing sentence promises three artefacts by name, the prompt set, the rubric and the
per-vote judge scores, and burying inputs inside `results/` makes the first of those hard to find.
Provenance is split out for the same reason.

## Gate status at export

| Gate | Status |
|---|---|
| `gate_receipts` | PASS, 52 of 52 claims re-derive from raw data |
| `gate_release` | PASS, scale polarity documented and all rater labels pseudonymous |
| `gate_bibitems` | PASS, every cite, bibitem and ref resolves |
| `gate_abstract_sync` | FAIL by design, until the arXiv listing abstract is replaced |

The `gate_abstract_sync` failure is the reason the v2 replacement exists. See the README section on
the gates.

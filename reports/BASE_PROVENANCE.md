# Base of record — The Granularity Gap

Established 2026-08-08, before any claim was checked. Playbook §1.

## The authoritative source

```
C:\Research\Sychophancy\main_granularitygap.tex
sha256  f9b82d432077d09e9330c3ed17450f69f79905686c2a1271455ee0dbc9b6d2da
size    89,684 bytes
mtime   2026-04-19 11:06:56 +1000   (= 2026-04-19 01:06:56 UTC)
```

## Chain: published artefact → working source

arXiv:2606.05183v1 was submitted **2026-04-19 01:26:18 UTC**, nineteen minutes after the working
`.tex` was last written. The arXiv PDF was downloaded and its text layer extracted
(`fitz`, 16 pages, 76,747 chars) and diffed against the local `.tex` build.

**They are the same document.** The only differences are the arXiv stamp line
(`arXiv:2606.05183v1 [cs.CL] 19 Apr 2026`) and typesetting reflow. Every number, table and section
matches. `main_granularitygap.tex` is the source of the published paper.

## Two files that look authoritative and are NOT

Both predate the submitted source and both would have produced a wrong audit:

| File | mtime | Why it is stale |
|---|---|---|
| `Keough_GranularityGap_pdf.pdf` | 2026-04-17 22:16 | Pre-submission build. Affiliation reads "Paper Type: Methodological Critique & Empirical Study" (published version: "Independent Researcher"). Abstract says "94% of responses scoring 3.0 on the Likert scale"; published says "94% of mild-to-moderate sycophantic responses (Likert 2.0–3.99)". Says "verdict agreement"; published says "weighted agreement". |
| `extracted_paper.txt` | 2026-04-19 07:58 | Text extraction **of the stale PDF above**, not of the submitted paper. Carries all three defects. |
| `main_granularitygap.tex.bak` | 2026-04-19 10:31 | Backup taken 35 min before the final save. Same numeric content; differs only in the abstract wording and affiliation above. |

Anything not traceable to `main_granularitygap.tex` or to a raw receipt is a *new* claim.

## Receipts

| Artefact | Path | Rows |
|---|---|---|
| Response-level results | `results/master_results.csv` | 8,830 × 21 |
| Prompt set | `data/raw/prompt_dataset.json` | 350 |
| Human labels (released) | `data/raw/human_labels_final_all.csv` | 236 annotations / 73 responses / 5 raters |
| Human labels (source, real names) | `paper_analysis/human_labels.csv` | 186 / 68 / 4 |
| Cross-model judge | `analysis_v2/data/unified_external_judge_data.csv` | — |

`results/master_results.csv` and `data/processed/master_results.csv` are byte-identical in content
(both 37,431,705 bytes) and were used interchangeably by the analysis scripts.

## A third artefact exists and nobody diffed it

arXiv stores the abstract **twice**: inside the PDF, and as free text in the submission form. The
listing page at `arxiv.org/abs/2606.05183` shows the second one. It is not the paper's abstract.
See `AUDIT_REPORT.md` finding F1. Verified by direct HTML fetch of the listing page, not by a
summarising tool.

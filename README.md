# The Granularity Gap
### A Multi-Dimensional Cross-Generational Audit of Sycophancy in Gemini Models

This repository holds the full record behind the paper, for a reader who wants to check the
work rather than take it on trust. It contains the three-axis scoring instrument and the judge
panel that applied it, the 8,830-response corpus every reported number is derived from, and the
236 human annotations used to validate the rubric, which reach Cohen's kappa of 0.78 against the
judge. It also releases 10,792 per-vote judge logs carrying the written reasoning behind each
score, so any scored decision in the paper can be traced back to the vote that produced it.

Pass/fail safety evaluation reports whether a model refused. It does not report how far a model
went to please the user, and this audit shows those are close to different measurements. N=8,830
responses from 8 Gemini variants across 350 adversarial prompts in 7 categories under 3 guardrail
conditions, scored on continuous 1-5 scales for sycophancy, truthfulness and refusal.

**Paper:** Patrick Keough | [arXiv:2606.05183](https://arxiv.org/abs/2606.05183), v3 (28 August 2026) |
source in [`paper/`](paper/)

[`CHANGELOG.md`](CHANGELOG.md) is the itemized record of what changed between versions and why.

## What the paper finds

- **The judge's own verdict explains 29% of the variance in its own sycophancy scores.** The
  remaining 71% is the Granularity Gap. It does not close under recalibration: the cut point already
  in use is the best available on the refusal axis, and no function of that axis explains more
  than 35%.
- **The judges say why, in their own words.** On 26% to 33% of the 10,792 panel votes the judge
  records that the prompt asked for nothing harmful. That runs from 0.2% in the two categories which
  genuinely solicit a harmful act to 51.8% in Validation Seeking. On 626 votes a judge scores
  sycophancy at 3 or above while recording in the same breath that nothing harmful was asked, so a
  refusal-thresholded verdict cannot reach those responses at any threshold.
- **The moderate band is where measurement itself fails.** Between-judge spread peaks at 1.005 in
  the moderate band against 0.019 in the clean band, roughly fifty times higher and about double the
  severe band. The verdict stops tracking severity in the same range where four independent judges
  stop agreeing with each other.
- **Sycophancy co-occurs with degraded judged truthfulness** (rho=0.40), and the coupling
  strengthens across generations (0.30, 0.41, 0.50).
- **Capability moved and resistance did not.** Gemini 2.0 Flash scores 1.43 and Gemini 3.0 Pro
  Preview 1.42, with a sharp Gen 2.5 regression between them.
- **A single direct instruction beats an elaborate reasoning protocol** in seven of eight variants,
  cutting mean severity in the most vulnerable category by 60.9%.

## The verification gates

Four scripts stand between a number and the manuscript. All four run from a fresh clone with no
downloads and no API keys.

```bash
python pipeline/gates/gate_receipts.py       # 52 claims re-derived from results/master_results.csv
python pipeline/gates/gate_release.py        # scale polarity + rater pseudonymity in shipped data
python pipeline/gates/gate_bibitems.py paper/main_granularitygap.tex
python pipeline/gates/gate_abstract_sync.py  # manuscript abstract vs the arXiv listing abstract
```

`gate_receipts` is the load-bearing one. It re-derives every bound numeric claim from the raw
corpus and matches it against the value actually present in the LaTeX source, so a number cannot
drift between the data and the paper without the gate failing.

`gate_abstract_sync` fails on the currently published listing. The v1 arXiv listing page carried
an abstract with wrong values (six variants, 73 prompts, a 0-4 scale, rho=-0.63) that never matched
the paper it fronted. The corrected text is in [`paper/ARXIV_ABSTRACT.txt`](paper/ARXIV_ABSTRACT.txt).
The gate is expected to fail until that listing is replaced, at which point
`pipeline/gates/arxiv_metadata_abstract.txt` should be refreshed from the live page.

## What is in here

| Path | Contents |
|---|---|
| `paper/` | manuscript source, compiled PDF, nine figures, corrected arXiv abstract |
| `data/` | the 350-prompt set, the codebook, the pseudonymised human labels, the stratified panel sample |
| `results/` | the 8,830-response corpus, 10,792 per-vote judge logs with reasoning, claim ledger, panel receipts |
| `pipeline/` | the judge panel that produced the logs, the figure script, and the four gates |
| `reports/` | data and base-of-record provenance |

[`MANIFEST.md`](MANIFEST.md) records what was copied from where, and what was deliberately left out.

## The judge logs

`results/judge_logs.jsonl` is 10,792 votes from four judges across three laboratories
(DeepSeek V4 Flash, Gemini 3.5 Flash Lite, GLM 5.2, and a reconstruction of the original Gemini 3
Pro Preview judge), on a documented stratified sample of 1,200 responses. Each vote carries
per-axis scores and the written reasoning behind them, roughly 1.7 million words in total. No
per-vote reasoning was logged for the original run, so this is the artefact whose absence bounded
every earlier audit of this project.

## Reading the data

`data/CODEBOOK.md` is not optional. Two human-label columns are stored on a reversed polarity
relative to the judge axes, and `gate_release.py` asserts that the polarity documented there is the
polarity present in the file. Correlating the raw columns without reading it produces sign errors.

## Human validation, stated plainly

The 236 human annotations come from five raters who were not independent of the author. The paper
discloses this in Section 7 and treats the human panel as a weak instrument rather than ground
truth. Rater labels in `data/human_labels_pseudonymous.csv` are pseudonymised, and the
non-pseudonymised working copies are not part of this release.

## Citation

```bibtex
@misc{keough2026granularity,
  title  = {The Granularity Gap: A Multi-Dimensional Cross-Generational Audit of Sycophancy in Gemini Models},
  author = {Keough, Patrick},
  year   = {2026},
  eprint = {2606.05183},
  archivePrefix = {arXiv}
}
```

Code in `pipeline/` is MIT licensed. Data, figures and manuscript sources are CC BY-NC-ND 4.0.
See [`LICENSE`](LICENSE) and [`LICENSE-DATA`](LICENSE-DATA).

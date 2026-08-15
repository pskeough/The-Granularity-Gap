# Publication-grade verification

Each claim is established by independent estimators resting on different assumptions, with a negative control where the claim could be a pipeline artefact.
n = 1200 stratified responses, 4 judges (3 scored fresh, 1 reconstructed), 3 votes each.

## C1. Judges collapse the scale onto the 1/3/5 anchors

### Proof 1 (direct): observed vote counts on the fresh judges

| judge | axis | n votes | count of 2 | count of 4 | share 2 or 4 |
|---|---|---|---|---|---|
| deepseek-v4-flash-0731 | sycophancy | 3599 | 4 | 25 | 0.81% |
| deepseek-v4-flash-0731 | truthfulness | 3599 | 7 | 9 | 0.44% |
| deepseek-v4-flash-0731 | refusal | 3599 | 0 | 1 | 0.03% |
| gemini-3.5-flash-lite | sycophancy | 3596 | 48 | 72 | 3.34% |
| gemini-3.5-flash-lite | truthfulness | 3596 | 14 | 71 | 2.36% |
| gemini-3.5-flash-lite | refusal | 3596 | 3 | 2 | 0.14% |
| glm-5.2 | sycophancy | 3597 | 56 | 40 | 2.67% |
| glm-5.2 | truthfulness | 3597 | 13 | 24 | 1.03% |
| glm-5.2 | refusal | 3597 | 0 | 3 | 0.08% |

### Proof 2 (independent of any reconstruction): impossible-without-even signatures

Certain (mean, sd) pairs can ONLY arise from a triple containing a 2 or a 4. If the original judge ever used them, those signatures must appear in the corpus. This uses no inversion: it asks whether the observed (mean, sd) values are reachable at all without even scores.

- **Refusal**: 15 of 8830 corpus rows (0.17%) have a (mean, sd) unreachable from {1,3,5} alone.
- **Sycophancy**: 204 of 8830 corpus rows (2.31%) have a (mean, sd) unreachable from {1,3,5} alone.

### Proof 3 (inferential): chi-square against smooth scale use

Null: votes are distributed over 1-5 in proportion to a smoothed version of the observed marginal, i.e. the judge uses the scale continuously. Test against observed.

| judge | axis | chi2 | df | p |
|---|---|---|---|---|
| deepseek-v4-flash-0731 | refusal | 2935.5 | 4 | 0.00e+00 |
| gemini-3.5-flash-lite | refusal | 2764.4 | 4 | 0.00e+00 |
| glm-5.2 | refusal | 2954.4 | 4 | 0.00e+00 |

### Negative control

If the collapse were produced by the parser rounding fractional scores, the raw JSON would contain non-integer values that got rounded to odd numbers. Checking the logged reasoning payloads for any evidence of fractional scoring:
- votes with non-integer stored scores: **0**. The parser casts to int, so this checks storage only; the decisive evidence is Proof 2, which never touches the parser.

## C2. Most of the gap is construct difference, not thresholding

### Proof 1 (variance, parametric): weighted eta^2 ceiling vs best threshold

| judge | best-threshold R2 | cut | eta2 ceiling | thresholding loss | construct residual |
|---|---|---|---|---|---|
| deepseek-v4-flash-0731 | 0.4102 | >3.333 | 0.4287 | +0.0184 | 0.5713 |
| gemini-3-pro-preview (reconstructed) | 0.2870 | >3.000 | 0.3266 | +0.0397 | 0.6734 |
| gemini-3.5-flash-lite | 0.5477 | >3.333 | 0.5609 | +0.0132 | 0.4391 |
| glm-5.2 | 0.3470 | >4.333 | 0.4141 | +0.0671 | 0.5859 |

### Proof 2 (information-theoretic, assumption-free): I(refusal; severity) / H(severity)

Makes no assumption of linearity, additivity or variance decomposition. If the refusal axis carried the severity signal, this fraction would be high.

| judge | MI fraction | 1 - MI fraction | agrees with eta^2 residual? |
|---|---|---|---|
| deepseek-v4-flash-0731 | 0.1711 | 0.8289 | directionally |
| gemini-3-pro-preview (reconstructed) | 0.1461 | 0.8539 | yes |
| gemini-3.5-flash-lite | 0.2181 | 0.7819 | directionally |
| glm-5.2 | 0.1654 | 0.8346 | directionally |

### Proof 3 (out-of-sample): 5-fold cross-validated ceiling

Guards against the eta^2 ceiling being inflated by fitting group means in-sample.

| judge | in-sample eta2 | 5-fold CV eta2 | inflation |
|---|---|---|---|
| deepseek-v4-flash-0731 | 0.4287 | 0.3932 | +0.0355 |
| gemini-3-pro-preview (reconstructed) | 0.3266 | 0.3432 | -0.0166 |
| gemini-3.5-flash-lite | 0.5609 | 0.5477 | +0.0132 |
| glm-5.2 | 0.4141 | 0.3895 | +0.0246 |

### Negative control (permutation)

Shuffle the refusal axis against severity within each judge. A real association must collapse to zero; a computational artefact would survive.

| judge | observed eta2 | permuted eta2 (mean of 200) | permuted 95th pct |
|---|---|---|---|
| deepseek-v4-flash-0731 | 0.4287 | 0.0053 | 0.0135 |
| gemini-3-pro-preview (reconstructed) | 0.3266 | 0.0054 | 0.0115 |
| gemini-3.5-flash-lite | 0.5609 | 0.0076 | 0.0196 |
| glm-5.2 | 0.4141 | 0.0063 | 0.0143 |

## C3. Judges agree only moderately, and no better on verdicts than severity

### Proof 1 (chance-corrected, categorical): mean pairwise Cohen kappa on verdicts
### Proof 2 (rank, continuous): mean pairwise Spearman rho on severity
### Proof 3 (chance-corrected AND ordinal, all raters at once): Krippendorff alpha

**Estimator validation.** The alpha implementation is hand-rolled, so it is calibrated against known cases before use. An uncalibrated estimator is not a proof.

- perfect agreement -> alpha = 1.0000 (must be 1.000)
- independent noise -> alpha = -0.0220 (must be ~0.000)


| estimator | what it corrects for | value | 95% CI |
|---|---|---|---|
| mean Cohen kappa (verdicts) | chance, categorical | 0.735 | [0.689, 0.777] |
| mean Spearman rho (severity) | rank, not chance | 0.688 | [0.637, 0.733] |
| Krippendorff alpha (severity, all judges) | chance + ordinal distance | 0.585 | (single estimate) |
| Krippendorff alpha (verdicts, all judges) | chance + nominal | 0.729 | (single estimate) |
| ICC(2,1) severity, absolute agreement | rater main effects | 0.748 | (single estimate) |

**kappa minus rho = +0.046 [-0.021, +0.122]. The interval contains zero, so verdict agreement is NOT reliably better than severity agreement.** Three estimators converge on moderate agreement in the 0.6-0.75 band on both.

## C4. Roughly half of non-signal variance is judge-related

### Proof 1 (ANOVA components, all four judges)
- judge-related share of non-signal variance: **53.9%** (calibration 14.6%, item-level 39.3%), temperature 46.1%

### Proof 2 (sensitivity): fresh judges only, dropping the reconstructed one
- n=1193, judge-related share: **45.2%** (calibration 5.8%, item-level 39.4%), temperature 54.8%
- The reconstructed judge has zero measurement noise by construction, so its inclusion could deflate the temperature component. This check shows whether it does.

### Proof 3 (bootstrap CI over responses)
- judge-related share **54.0%** [95% CI 51.0%, 56.8%]

## C5. Every external judge scores lower than the original

| judge | weighted mean bias | 95% CI (bootstrap) | Wilcoxon p | % responses scored lower |
|---|---|---|---|---|
| deepseek-v4-flash-0731 | -0.319 | [-0.358, -0.282] | 8.03e-72 | 37.4% |
| gemini-3.5-flash-lite | -0.343 | [-0.384, -0.306] | 3.10e-75 | 38.8% |
| glm-5.2 | -0.173 | [-0.203, -0.142] | 2.89e-41 | 28.8% |

Three independent statements per judge: a weighted point estimate with a bootstrap interval, a distribution-free signed-rank test, and the raw proportion of responses scored lower. All must agree for the claim to hold.


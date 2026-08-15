# Two-layer validation of the judge panel

1200 responses, 4 judges, recomputed from judge_logs.jsonl.
Layer 1 corrects each finding for its design. Layer 2 attacks it.

## Finding 1: anchor collapse

**Layer 1.** Share of votes on the unanchored points 2 and 4, per judge and axis.

| judge | sycophancy | truthfulness | refusal |
|---|---|---|---|
| deepseek-v4-flash-0731 | 0.81% | 0.44% | 0.03% |
| gemini-3-pro-preview (reconstructed) | 2.19% | 0.06% | 0.00% |
| gemini-3.5-flash-lite | 3.34% | 2.36% | 0.14% |
| glm-5.2 | 2.67% | 1.03% | 0.08% |

**Layer 2, the attack:** the original judge's votes are RECONSTRUCTED from (mean, sd). If (mean, sd) keys whose vote triples contain a 2 or a 4 are disproportionately *ambiguous*, reconstruction would silently drop them and manufacture the finding.

Of 34 distinct (mean, sd) keys: 33 unique (23 contain a 2 or 4), 1 ambiguous (1 contain a 2 or 4).
Responses lost to ambiguity: 13/1200 (1.08%). Too few to manufacture a 0.00% rate.

**Independent check on the full corpus**, which does not depend on the panel at all: reconstructed refusal votes across all 8,830 responses.
n=26451 votes: 1=55.81%, 2=0.00%, 3=39.69%, 4=0.01%, 5=4.49%

**Verdict: SURVIVES.** The three fresh judges were never reconstructed and show the same pattern directly, so the finding does not depend on the inversion at all.

## Finding 2: the decomposition, corrected for stratification

**Layer 1.** 03_analyse.py reported unweighted figures on a sample that deliberately oversamples severe cells, so they are not corpus estimates. Reweighted, with bootstrap 95% CIs over responses:

| judge | R2 weighted | eta2 weighted | thresholding loss | construct residual [95% CI] |
|---|---|---|---|---|
| deepseek-v4-flash-0731 | 0.4240 | 0.4287 | +0.0047 | 0.5713 [0.464, 0.676] |
| gemini-3-pro-preview (reconstructed) | 0.2850 | 0.3266 | +0.0416 | 0.6734 [0.597, 0.736] |
| gemini-3.5-flash-lite | 0.5457 | 0.5609 | +0.0153 | 0.4391 [0.346, 0.529] |
| glm-5.2 | 0.3479 | 0.4141 | +0.0663 | 0.5859 [0.500, 0.658] |

**Layer 2, the attack:** is the construct residual just measurement noise? If the refusal axis were a perfect predictor measured with error, the residual would shrink toward zero once you correct for the judge's own unreliability. Upper bound on what reliability allows, using each judge's within-judge vote agreement as its reliability:

| judge | reliability (ICC of 3 votes) | max attainable R2 | observed eta2 | gap real? |
|---|---|---|---|---|
| deepseek-v4-flash-0731 | 0.944 | 0.835 | 0.429 | YES |
| gemini-3-pro-preview (reconstructed) | 0.928 | 0.842 | 0.327 | YES |
| gemini-3.5-flash-lite | 0.975 | 0.884 | 0.561 | YES |
| glm-5.2 | 0.940 | 0.769 | 0.414 | YES |

## Finding 3: the gap between judges (the headline)

**Layer 2 first, because this is where the finding is most vulnerable.** A 97% verdict agreement rate means nothing on its own if verdicts are heavily imbalanced. If ~95% of responses are CHALLENGED, two judges agreeing 97% of the time is near chance. The comparison against a severity correlation is only fair if the agreement is CHANCE-CORRECTED.

CHALLENGED base rate per judge: deepseek-v4-flash-0731 0.953, gemini-3-pro-preview (reconstructed) 0.947, gemini-3.5-flash-lite 0.956, glm-5.2 0.913

| pair | n | raw agreement | expected by chance | Cohen kappa | severity rho |
|---|---|---|---|---|---|
| deepseek-v4-flash-0731 vs gemini-3-pro-preview (reconstructed) | 1187 | 98.06% | 90.63% | 0.793 | 0.628 |
| deepseek-v4-flash-0731 vs gemini-3.5-flash-lite | 1200 | 98.33% | 91.25% | 0.809 | 0.724 |
| deepseek-v4-flash-0731 vs glm-5.2 | 1200 | 95.92% | 87.41% | 0.676 | 0.742 |
| gemini-3-pro-preview (reconstructed) vs gemini-3.5-flash-lite | 1187 | 97.73% | 90.93% | 0.749 | 0.597 |
| gemini-3-pro-preview (reconstructed) vs glm-5.2 | 1187 | 96.46% | 87.09% | 0.726 | 0.761 |
| gemini-3.5-flash-lite vs glm-5.2 | 1200 | 95.75% | 87.68% | 0.655 | 0.678 |

**Mean raw agreement 97.04%, mean chance expectation 89.16%, mean kappa 0.735, mean severity rho 0.688.**

kappa exceeds rho in 3 of 6 pairs. Mean difference +0.046 [95% CI -0.023, +0.118].

**Verdict: THE STRONG FRAMING DOES NOT SURVIVE.** Raw agreement of 97% looked like a chasm against a severity correlation of 0.69, but 87-91 points of that 97 are expected by the CHALLENGED base rate alone. Chance-corrected, verdict agreement (kappa 0.735) and severity agreement (rho 0.688) are close enough that the difference is not reliable, and in some pairs severity agreement is the higher of the two. Do NOT claim that judges agree on verdicts but disagree on severity. What the data support is the weaker and still useful statement that judges agree only MODERATELY on both, around 0.69-0.74, which is well short of the interchangeability that single-judge evaluation assumes.

## Finding 4: variance decomposition, done properly

**Layer 1.** 03_analyse.py lumped the judge MAIN effect (one judge is simply stricter than another, a calibration offset you can standardise away) together with the response-by-judge INTERACTION (judges genuinely disagreeing about particular responses, which you cannot). A two-way random-effects decomposition separates them.

Balanced design on 1180 responses x 4 judges x 3 votes.

| component | variance | share | interpretation |
|---|---|---|---|
| response | 0.7131 | 67.2% | real differences between responses (signal) |
| judge main effect | 0.0508 | 4.8% | calibration offset, removable by standardising |
| response x judge | 0.1368 | 12.9% | genuine disagreement about specific items |
| residual (temperature) | 0.1602 | 15.1% | resampling the same judge |

Of the non-signal variance, calibration offset is 14.6%, item-level disagreement 39.3%, temperature 46.1%.

**Verdict: THE STRONG CLAIM DOES NOT SURVIVE.** The earlier '60% of variance is model identity' figure was wrong on two counts: it pooled the removable calibration offset with genuine item-level disagreement, and it did not separate the response signal first. Properly decomposed, temperature resampling (46.1% of non-signal variance) slightly EXCEEDS item-level judge disagreement (39.3%), so it is false to say best-of-3 controls the smaller component. It controls the largest single one.

What the data do support: judge-related variance (calibration plus item-level disagreement) is 53.9% of all non-signal variance, so roughly half the noise in an LLM-judge score comes from which judge was chosen, and a best-of-3 consensus within one judge addresses only the other half. That is a real limitation of single-judge protocols and it is defensible as stated.

## Finding 5: panel versus the base of record, weighted

| judge | n | kappa vs original | severity rho | weighted bias (panel - original) |
|---|---|---|---|---|
| deepseek-v4-flash-0731 | 1187 | 0.793 | 0.628 | -0.319 |
| gemini-3.5-flash-lite | 1187 | 0.749 | 0.597 | -0.343 |
| glm-5.2 | 1187 | 0.726 | 0.761 | -0.173 |

All biases negative means every external judge scores LOWER than the original, which supports the paper's existing claim that its rates are conservative upper bounds.


# Judge panel results

n = 1200 stratified responses, 4 judges, 3 votes each.
Original judge reconstructed on 1187/1200 responses (13 not uniquely invertible).

## 1. Anchor collapse

The rubric defines anchors at 1, 3 and 5 only. Share of individual votes on each scale point:

| judge | axis | 1 | 2 | 3 | 4 | 5 | share on 2 or 4 |
|---|---|---|---|---|---|---|---|
| deepseek/deepseek-v4-flash-0731 | sycophancy | 86.64% | 0.11% | 9.09% | 0.69% | 3.47% | **0.81%** |
| deepseek/deepseek-v4-flash-0731 | truthfulness | 92.69% | 0.19% | 3.03% | 0.25% | 3.83% | **0.44%** |
| deepseek/deepseek-v4-flash-0731 | refusal | 57.15% | 0.00% | 38.26% | 0.03% | 4.56% | **0.03%** |
| google/gemini-3-pro-preview (reconstructed) | sycophancy | 63.21% | 1.88% | 30.75% | 0.31% | 3.85% | **2.19%** |
| google/gemini-3-pro-preview (reconstructed) | truthfulness | 93.46% | 0.06% | 3.03% | 0.00% | 3.45% | **0.06%** |
| google/gemini-3-pro-preview (reconstructed) | refusal | 50.49% | 0.00% | 44.06% | 0.00% | 5.45% | **0.00%** |
| google/gemini-3.5-flash-lite | sycophancy | 87.37% | 1.33% | 6.26% | 2.00% | 3.03% | **3.34%** |
| google/gemini-3.5-flash-lite | truthfulness | 93.24% | 0.39% | 2.75% | 1.97% | 1.64% | **2.36%** |
| google/gemini-3.5-flash-lite | refusal | 68.97% | 0.08% | 26.56% | 0.06% | 4.34% | **0.14%** |
| z-ai/glm-5.2 | sycophancy | 77.09% | 1.56% | 16.26% | 1.11% | 3.98% | **2.67%** |
| z-ai/glm-5.2 | truthfulness | 91.88% | 0.36% | 4.09% | 0.67% | 3.00% | **1.03%** |
| z-ai/glm-5.2 | refusal | 48.74% | 0.00% | 40.56% | 0.08% | 10.62% | **0.08%** |

## 2. Per-judge decomposition of the Granularity Gap

Each judge scored on its OWN axes. `R2` is its own binary verdict against its own severity; `eta2` is the ceiling for any function of its own refusal axis.

| judge | n | R2 (own verdict) | eta2 (own refusal axis) | thresholding loss | construct residual |
|---|---|---|---|---|---|
| deepseek/deepseek-v4-flash-0731 | 1200 | 0.4239 | 0.4145 | -0.0094 | 0.5855 |
| google/gemini-3-pro-preview (reconstructed) | 1187 | 0.3150 | 0.3537 | 0.0387 | 0.6463 |
| google/gemini-3.5-flash-lite | 1200 | 0.5407 | 0.5576 | 0.0169 | 0.4424 |
| z-ai/glm-5.2 | 1200 | 0.3401 | 0.4159 | 0.0758 | 0.5841 |

## 3. The same gap appears BETWEEN judges

Judges agree on the binary verdict far more than they agree on severity. This is the Granularity Gap across instruments, and it does not rest on the within-judge algebraic identity.

| judge A | judge B | n | verdict agreement | severity rho |
|---|---|---|---|---|
| deepseek/deepseek-v4-flash-0731 | google/gemini-3-pro-preview (reconstructed) | 1187 | 98.06% | 0.628 |
| deepseek/deepseek-v4-flash-0731 | google/gemini-3.5-flash-lite | 1200 | 98.33% | 0.724 |
| deepseek/deepseek-v4-flash-0731 | z-ai/glm-5.2 | 1200 | 95.92% | 0.742 |
| google/gemini-3-pro-preview (reconstructed) | google/gemini-3.5-flash-lite | 1187 | 97.73% | 0.597 |
| google/gemini-3-pro-preview (reconstructed) | z-ai/glm-5.2 | 1187 | 96.46% | 0.761 |
| google/gemini-3.5-flash-lite | z-ai/glm-5.2 | 1200 | 95.75% | 0.678 |

**Mean across all 6 judge pairs: verdict agreement 97.04%, severity correlation 0.688.**

## 4. Where judge disagreement lives

Variance of individual sycophancy votes, split into the component from resampling the same judge at temperature 0.7 and the component from swapping judge.

| component | variance | share |
|---|---|---|
| within-judge (temperature resampling) | 0.1610 | 39.8% |
| between-judge (model identity) | 0.2430 | 60.2% |

Between-judge variance is **1.5x** the within-judge variance. A best-of-3 consensus from a single judge controls the smaller component.

## 5. Panel versus the original judge

| panel judge | n | verdict agreement with original | severity rho | mean bias (panel - original) |
|---|---|---|---|---|
| deepseek/deepseek-v4-flash-0731 | 1187 | 98.06% | 0.628 | -0.460 |
| google/gemini-3.5-flash-lite | 1187 | 97.73% | 0.597 | -0.486 |
| z-ai/glm-5.2 | 1187 | 96.46% | 0.761 | -0.269 |

## 6. Weighted corpus-level mean sycophancy

Sample weights reverse the stratification, so these estimate the full 8,830-response corpus rather than the sample.

| judge | unweighted | weighted (corpus estimate) |
|---|---|---|
| deepseek/deepseek-v4-flash-0731 | 1.3425 | 1.2792 |
| google/gemini-3-pro-preview (reconstructed) | 1.7970 | 1.5924 |
| google/gemini-3.5-flash-lite | 1.3214 | 1.2597 |
| z-ai/glm-5.2 | 1.5328 | 1.4246 |


# What the panel produced beyond the numbers we already had

Analysed 2026-08-13 from `judge_logs.jsonl` (10,792 successful votes, 10,761 carrying refusal
reasoning, median 155 reasoning words per vote, roughly 1.7 million words total). None of this
existed before the panel run, because no per-vote reasoning had ever been logged for this project.

---

## 1. The judges say the refusal axis has nothing to grade, on a quarter to a third of votes

Searching the judges' own `refusal_analysis` text for statements that the prompt did not request
anything harmful:

| pattern | votes | share |
|---|---|---|
| narrow (conservative) | 2,827 | **26.3%** |
| broad | 3,562 | **33.1%** |

**Validated by hand.** Twelve randomly sampled flagged passages were checked: all twelve genuinely
say the request was not harmful, so precision on that sample is 100%. Two of eight sampled *unflagged*
passages say the same thing in wording the narrow pattern misses, so recall is incomplete and 26.3%
is a floor. Report the range, not a point estimate.

The category breakdown is the result:

| category | votes saying nothing harmful was asked |
|---|---|
| Validation Seeking | **51.8%** |
| Flawed Logic | 32.3% |
| Assumption Challenge | 31.2% |
| Egotistical Validation | 27.8% |
| Moral Endorsement | 20.0% |
| Authority Pressure | **0.4%** |
| Unethical Proposals | **0.2%** |

The two categories that genuinely request harmful acts sit at essentially zero. The five that do not
run from 20% to 52%. The refusal axis is close to undefined across most of the design, and the
judges say so unprompted.

**626 votes (5.8%) score sycophancy at 3 or above while the same judge records that nothing harmful
was asked.** Those are precisely the responses a refusal-thresholded verdict cannot flag, by
construction rather than by miscalibration.

Why this matters: the ~65-point construct residual in Section 3.1 has been a statistical inference.
This is the mechanism behind it, stated by four judges in their own words, on a stratified sample.

---

## 2. Response length correlates with the sycophancy score

Flagged by the methods reviewer during the August review and never tested until now.

Overall Spearman(response length, mean sycophancy) = **+0.178** (p=5.2e-10, n=1,200).

Within category, which removes the category confound:

| category | rho | p |
|---|---|---|
| Authority Pressure | **+0.548** | <0.001 |
| Unethical Proposals | **+0.510** | <0.001 |
| Moral Endorsement | +0.303 | <0.001 |
| Assumption Challenge | +0.186 | 0.015 |
| Validation Seeking | +0.172 | 0.013 |
| Flawed Logic | +0.144 | 0.028 |
| Egotistical Validation | **-0.163** | 0.025 |

**This is not cleanly a bias and should not be reported as one.** Longer responses may genuinely
contain more sycophancy, since flattery takes words. The strongest evidence against a pure
length artefact is Egotistical Validation, where the correlation reverses: there the sycophantic
responses are the short effusive ones. A pure verbosity bias would be positive everywhere.

What it is: an uncontrolled covariate that the paper never discloses, with a substantial effect in
two categories. Disclose it in Limitations and state that the design cannot separate the two
explanations.

---

## 3. Judge disagreement peaks exactly in the moderate band

Between-judge spread in mean sycophancy, across the four judges, on 1,200 responses. Median spread
is 0.00, so judges usually agree exactly; p90 is 1.33 and the maximum is 3.00. 74 responses (6.2%)
draw judgements two or more points apart.

By the paper's own severity bands:

| band | mean between-judge spread |
|---|---|
| clean | 0.019 |
| borderline | 0.290 |
| mild | 0.571 |
| **moderate** | **1.005** |
| severe | 0.547 |

Disagreement in the moderate band is **fifty times** the clean band and roughly double the severe
band. The mid-severity range is where the verdict fails *and* where four independent judges cannot
agree with each other.

This is the honest replacement for the withdrawn U-shaped detection curve. The original claim was
that detection collapsed in the middle, which turned out to be a column artefact. The true statement
is stronger and better evidenced: the middle of the severity range is where the construct is hardest
to measure at all, demonstrated by independent judges rather than by one instrument's threshold.

By category, spread is highest for Validation Seeking (0.578) and Egotistical Validation (0.405),
lowest for Moral Endorsement (0.219).

---

## 4. Three independent measures converge on Validation Seeking

| measure | Validation Seeking |
|---|---|
| judges say nothing harmful was asked | 51.8%, highest of seven |
| hedged refusals (Likert >=3 with a CHALLENGED verdict) | 502, highest of seven |
| between-judge disagreement | 0.578, highest of seven |

Three unrelated quantities, computed from different data, agree that this is the category where the
instrument is weakest. Nothing in the paper currently says so.

---

## Suggested paper changes

1. **Results I gains the mechanism.** Roughly 120 words reporting the 26-33% range with the category
   table, and the 626 votes that score sycophancy at 3 or above while the judge records nothing
   harmful was asked. This is the strongest single addition available and it directly answers the
   objection that the construct residual is an artefact of our own rubric.
2. **The moderate-band disagreement result replaces the withdrawn U-shape** as the paper's statement
   about the mid-severity range. About 80 words plus one small table.
3. **Length correlation goes in Limitations**, roughly 70 words, with the Egotistical Validation
   reversal stated because it is the honest evidence against the simplest reading.
4. **Validation Seeking convergence** is one sentence in Results II.
5. **Release `judge_logs.jsonl`** with the paper. 10,792 votes carrying full per-axis reasoning from
   four judges across three laboratories, on a documented stratified sample, is a data contribution
   in its own right, and it is exactly the artefact whose absence bounded every previous audit of
   this project.

# Master Statistical Verification Report
**Date:** 2026-01-04
**Source:** `C:\Users\pskeo\Downloads\FinalSyc\stats_folder`

This document compiles all statistical findings from the automated validation suite. These values represent the "ground truth" derived directly from the analysis scripts and should be used to ensure precision in the main academic paper.

---

## 1. Measurement Validation
*Source: 01_measurement_validation_report.txt*

Validation of the AI Judge (Gemini 3.0 Pro Preview) against Human Labels and comparison with external models.

*   **Judge Agreement:**
    *   **Cohen's Kappa (AI vs Human):** $\kappa = 0.7781$
    *   **Binary Accuracy:** $95.89\%$
    *   **Sensitivity (Recall of Sycophancy):** $66.67\%$
    *   **Specificity (Recall of Non-Sycophancy):** $100.00\%$
    *   **Weighted Verdict Agreement (vs DeepSeek):** $93.30\%$

*   **Calibration Rectifiers:**
    *   **Sycophancy Rectifier:** $+0.4534$ (Adjustment applied to raw scores)
    *   **Truthfulness Rectifier:** $-3.2007$

*   **External Benchmarking:**
    *   **Score Correlation (Spearman):** $\rho = 0.5522$
        *   *Control Condition:* $\rho = 0.6718$
        *   *Simple Condition:* $\rho = 0.6954$
        *   *Protocol Condition:* $\rho = 0.2979$
    *   **Global Bias (Gemini - DeepSeek):** $\Delta_{mean} = 0.3448$ (Gemini Judge is stricter/higher scoring on average)

---

## 2. Granularity & Sensitivity
*Source: 02_granularity_gap_report.txt*

Analysis of the "Granularity Gap" and the sensitivity of the AI Judge to varying degrees of sycophancy.

*   **Mechanism:**
    *   **Granularity Gap ($R^2$):** $0.2913$

*   **Prevalence Distribution (Buckets):**
    *   **Clean Refusal:** $68.39\%$
    *   **Borderline:** $4.42\%$
    *   **Mild:** $4.47\%$
    *   **Moderate:** $19.93\%$ (Most common failure mode)
    *   **Severe:** $2.79\%$

*   **Sensitivity Curve (Detection Rate by Human Severity Level):**
    *   **Level 1 (No Sycophancy):** $99.3\%$ ($N=144$)
    *   **Level 2 (Borderline):** $95.7\%$ ($N=46$)
    *   **Level 3 (Mild):** $72.0\%$ ($N=25$)
    *   **Level 4 (Moderate):** $61.5\%$ ($N=13$)
    *   **Level 5 (Severe):** $37.5\%$ ($N=8$) - *Note: Lower detection for severe cases suggests "Safety Mirage"*
    *   **Aggregate Sensitivity (Levels 2-5):** $79.3\%$ [95% CI: $70.7\%$, $87.0\%$]

---

## 3. Sycophancy Landscape
*Source: 03_sycophancy_landscape_report.txt*

Global correlations and categorical comparisons.

*   **Global Correlations (Spearman's $\rho$):**
    *   **Global Alignment Tax (Sycophancy vs Truthfulness):** $\rho = 0.3964$ ($p < 0.001$)
    *   **Sycophancy vs Refusal:** $\rho = 0.3594$
    *   **Truthfulness vs Refusal:** $\rho = 0.3194$

*   **Global Statistics:**
    *   **Mean Sycophancy:** $\mu = 1.597$ ($\sigma=0.985$)

*   **Category Vulnerability (Mean Score [95% CI]):**
    1.  **Egotistical Validation:** $3.27$ [$3.12$, $3.42$] (Most Vulnerable)
    2.  **Validation Seeking:** $2.32$ [$2.24$, $2.40$]
    3.  **Flawed Logic:** $2.29$ [$2.19$, $2.38$]
    4.  **Authority Pressure:** $1.98$ [$1.83$, $2.13$]
    5.  **Assumption Challenge:** $1.94$ [$1.87$, $2.03$]
    6.  **Moral Endorsement:** $1.81$ [$1.72$, $1.92$]
    7.  **Unethical Proposals:** $1.72$ [$1.60$, $1.83$] (Least Vulnerable)

*   **Effect Size:**
    *   **Cliff's Delta (Egotistical vs Unethical):** $\delta = 0.5495$

---

## 4. Generational Dynamics
*Source: 04_generational_dynamics_report.txt*

Analysis of sycophancy trends across Gemini model generations (2.0, 2.5, 3.0).

*   **Overall Distribution:**
    *   **Kruskal-Wallis H-test:** $H=293.57$ ($p=1.78e^{-64}$)

*   **Generational Means (Aggregate):**
    *   **Gemini 2.0:** $\mu = 1.433$ [$1.398, 1.467$] ($N=2340$)
    *   **Gemini 2.5:** $\mu = 1.830$ [$1.792, 1.867$] ($N=3225$) - *The "Sycophancy Spike"*
    *   **Gemini 3.0:** $\mu = 1.484$ [$1.453, 1.516$] ($N=3265$)

*   **Comparisons:**
    *   **Gen 2.5 vs Gen 2.0 Control Condition Delta:** $\Delta_{control} = +0.742$ (Significant regression)
    *   **Gen 2.5 vs Gen 2.0 Aggregate Effect:** Cliff's $\delta = +0.1924$ (Small but significant distributional shift)
    *   **Bootstrap Stability:** $100.0\%$ positive (95% CI: [$0.634, 0.848$])
    *   **Gen 3.0 vs Gen 2.0:** No meaningful regression in aggregate.

*   **Interaction Effects:**
    *   **Category x Generation:** $F=11.64$ ($p=1.14e^{-23}$)
    *   **Generation x Model Class:** $F=5.24$ ($p=0.022$)

*   **Scaling Effects (Pro vs Flash):**
    *   **Gen 2.5 (Pro - Flash):** $\Delta = +0.230$ (Pro is more sycophantic, $p=1.31e^{-06}$)
    *   **Gen 3.0 (Pro - Flash):** $\Delta = -0.062$ (Pro is less sycophantic, $p=3.94e^{-04}$)

*   **Native Sycophancy Ranking (Lower is Better):**
    1.  gemini-2.0-flash ($1.86$)
    2.  gemini-3-pro-preview ($1.90$)
    3.  gemini-2.0-flash-lite ($1.93$)
    4.  gemini-3-pro-low ($2.05$)
    5.  google/gemini-3-flash-preview ($2.08$)
    6.  gemini-2.5-flash ($2.40$)
    7.  gemini-2.5-flash-lite ($2.66$)
    8.  gemini-2.5-pro ($2.86$)

*   **Stratified Alignment Tax (Correlation $\rho$):**
    *   **Gen 2.0:** $\rho = 0.296$
    *   **Gen 2.5:** $\rho = 0.407$
    *   **Gen 3.0:** $\rho = 0.502$
    *   **Comparison (Fisher's Z, Gen 3.0 vs 2.0):** $Z=9.12$ ($p < 0.001$)

---

## 5. Intervention Efficacy
*Source: 05_intervention_efficacy_report.txt*

Evaluation of "Simple" vs "Protocol" prompting interventions.

*   **Global Guardrail Hierarchy (Mean Score):**
    *   **Control:** $\mu = 2.211$ (Baseline)
    *   **Simple Intervention:** $\mu = 1.156$ (Best Performance)
    *   **Protocol Intervention:** $\mu = 1.421$

*   **Challenge Rate (CR) Performance:**
    *   **Control:** $87.66\%$
    *   **Simple:** $99.90\%$
    *   **Protocol:** $99.39\%$

*   **Comparisons:**
    *   **Effect Size (Control vs Simple):** Cliff's $\delta = 0.4972$ (Large positive effect)
    *   **Paradox of Complexity (Protocol - Simple):** $\Delta = +0.264$ (Simpler prompts performed significantly better)

*   **Category Gains (Change in Challenge Rate, Simple vs Control):**
    *   **Egotistical Validation:** $+42.30\%$ (Major Improvement)
    *   **Unethical Proposals:** $+15.10\%$
    *   **Authority Pressure:** $+13.93\%$
    *   **Flawed Logic:** $+8.22\%$
    *   **Assumption Challenge:** $+5.89\%$
    *   **Validation Seeking:** $+3.07\%$
    *   **Moral Endorsement:** $+0.00\%$ (Ceiling effect, already 100%)

---

## 6. P-Value Corrections (FDR)
*Source: 07_p_value_correction_report.txt*

Verification of statistical significance after Benjamini-Hochberg correction for multiple hypothesis testing (N=8 tests).

| Test Name | Raw $p$ | Adj $p_{adj}$ | Significant? |
| :--- | :--- | :--- | :--- |
| **Global Alignment Tax ($\rho$)** | $p < 10^{-100}$ | $p < 10^{-100}$ | **Yes** |
| **Kruskal-Wallis (Generational)** | $1.78e^{-64}$ | $4.75e^{-64}$ | **Yes** |
| **ANOVA: Category x Generation** | $1.14e^{-23}$ | $1.82e^{-23}$ | **Yes** |
| **ANOVA: Gen x Class** | $7.88e^{-04}$ | $7.88e^{-04}$ | **Yes** |
| **MW-U: Gen 2.5 Scaling** | $1.06e^{-04}$ | $1.42e^{-04}$ | **Yes** |
| **MW-U: Gen 3.0 Scaling** | $3.94e^{-04}$ | $4.51e^{-04}$ | **Yes** |
| **Fisher's Z: Gen 3 vs 2** | $p < 10^{-100}$ | $p < 10^{-100}$ | **Yes** |
| **ANOVA: Model x Guardrail** | $1.49e^{-47}$ | $2.98e^{-47}$ | **Yes** |

**Conclusion:** All key statistical claims survived False Discovery Rate (FDR) correction and remain robust.

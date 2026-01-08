# The Granularity Gap: A Multi-Dimensional Longitudinal Audit of Sycophancy in Gemini Models

**Author:** Patrick Keough  
**Date:** January 2026

## Abstract

This repository contains the codebase and data for "The Granularity Gap," a longitudinal audit of social compliance in the Gemini model family (Generations 2.0, 2.5, and 3.0). The study introduces a multi-dimensional methodology to measure sycophancy as a continuous, structured phenomenon, moving beyond binary safety metrics.

Developing a psychometric rubric assessing **Sycophancy**, **Truthfulness**, and **Refusal Specificity**, we evaluated N=8,830 responses across 8 Gemini model variants, 7 adversarial prompt categories, and 3 guardrail conditions.

## Key Terminology

*   **Granularity Gap:** The information loss inherent in reducing continuous behavioral signals to binary classifications. Our findings indicate binary safety metrics explain only **29% of behavioral variance** ($R^2=0.29$), leaving 71% of sycophantic behavior, particularly "hedged confirmation"—undetected.
*   **Alignment Tax:** The observed trade-off between social compliance and epistemic reliability. We document a strong positive correlation between sycophancy and hallucination ($\rho=0.40$), quantifying the epistemic cost of model agreeableness. This tax has **nearly doubled** from Gen 2.0 ($\rho=0.30$) to Gen 3.0 ($\rho=0.50$).

## Repository Structure

*   `Paper_folder/`: Contains the full academic paper (`FinalPaper.md`) and related drafts.
*   `data_csv/`: Raw and processed experimental data, including the N=8,830 response dataset.
*   `scripts_folder/`: Python implementation of the evaluation framework, including response generation, AI judging pipelines, and analysis tools.
*   `stats_folder/`: Statistical analysis logs and supplementary material.
*   `Figures/`: Generated visualizations used in the publication.

## Key Findings

1.  **Measurement Problem:** Detection rates collapse to 6.36% for "moderate" sycophancy, creating a substantial blind spot where 93.64% of substantive sycophantic content passes binary safety filters.
2.  **Alignment Tax** There is a direct relationship between sycopantic (social complaint) responses and hallucination (epsitemtic validatity), which increases with each model generation.
3.  **Generational Dynamics:** Sycophancy trajectories are non-monotonic. Gemini 2.5 exhibited significant regression (inverse scaling), while Gemini 3.0 corrected this, returning to near-baseline levels.
4.  **Vulnerability Taxonomy:** "Egotistical Validation" (flattery) elicits sycophancy at nearly twice the rate of "Unethical Proposals," indicating specific vulnerability to affective manipulation.
5.  **Intervention Efficacy:** Simple, direct guardrails ("Do not agree") consistently outperform complex reasoning protocols, achieving +42% remediation in the most vulnerable categories.

## Replication

To replicate the analysis:

1.  Install dependencies: `pip install -r requirements.txt`
2.  Navigate to `scripts_folder/` to access the evaluation pipeline.

## Citation

Please cite the accompanying paper:

> Keough, P. (2026). The Granularity Gap: A Multi-Dimensional Longitudinal Audit of Sycophancy in Gemini Models.

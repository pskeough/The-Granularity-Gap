# The Granularity Gap
### Multi-Dimensional Longitudinal Audit of Sycophancy in Gemini Models

**Author:** Patrick Keough
**Published:** January 2026

---

## Overview

Binary safety metrics miss the majority of sycophantic behavior in large language models. This study evaluates N=8,830 responses across three Gemini generations (2.0, 2.5, 3.0), measuring sycophancy as a continuous phenomenon rather than a pass/fail binary.

**Core Finding:** Binary classification explains only 29% of behavioral variance (R²=0.29). The remaining 71% represents gradations of hedging, tone, and partial agreement that standard safety filters cannot detect.

---

## Key Concepts

**Granularity Gap**
The behavioral variance lost when reducing continuous signals to binary classifications. Most sycophancy operates in the moderate severity range where detection rates collapse to 6.36%.

**Alignment Tax**
The correlation between social compliance and hallucination. When models prioritize user validation, factual accuracy degrades. This coupling intensifies across generations: ρ=0.30 (Gen 2.0) → ρ=0.50 (Gen 3.0).

---

## Repository Structure

```
├── data_csv/              # Raw experimental data (N=8,830 responses)
├── Figures/               # Visualizations and plots
├── paper/                 # LaTeX source (main.tex) and rendered PDF
├── scripts_folder/        # Python evaluation framework
│   └── Database Analysis/ # Statistical analysis scripts (01-10)
└── stats_reports/         # Analysis outputs and validation reports
    ├── 01-10_*.txt       # Individual analysis results
    └── STATISTICAL_MASTER_REPORT.md  # Statistical verification
```

---

## Main Results

### 1. Detection Blind Spot
Binary filters detect 99.7% of clean responses and 95.9% of severe violations but only **6.36% of moderate sycophancy**—where most problematic content resides.

### 2. Category Vulnerability
Affective manipulation (Egotistical Validation: M=3.27) elicits nearly **2× the sycophancy** of explicit harm requests (Unethical Proposals: M=1.72). Flattery exploits helpfulness training more effectively than malicious content.

### 3. Non-Monotonic Safety Trajectory
- Gen 2.0: Baseline (M=1.43)
- Gen 2.5: Regression (M=1.83, +28%)
- Gen 3.0: Recovery (M=1.48, returns to baseline but does not surpass it)

Gen 2.5 exhibited inverse scaling where the flagship Pro model was **more sycophantic** than smaller Flash variants.

### 4. Intensifying Alignment Tax
The correlation between sycophancy and hallucination nearly doubled across generations:
- Gen 2.0: ρ=0.30
- Gen 2.5: ρ=0.41
- Gen 3.0: ρ=0.50 (Fisher's Z=9.12, p<0.001)

### 5. Intervention Efficacy
Simple direct constraints ("Do not agree with false premises") outperform complex reasoning protocols in 7 of 8 models tested. Achieves **+42% remediation** in the most vulnerable category with zero architectural changes.

---

## Validation

All statistics independently verified:
- Human validation: N=236 annotations, Cohen's κ=0.78
- Cross-model validation: DeepSeek V3 (N=608), 93.3% agreement
- Multiple comparison correction: Benjamini-Hochberg FDR (all 8 tests survived)

See `stats_reports/STATISTICAL_MASTER_REPORT.md` for full verification.

---

## Replication

### Requirements
```bash
pip install pandas numpy scipy statsmodels scikit-learn
```

### Run Analysis Suite
```bash
cd scripts_folder/Database\ Analysis
python 06_run_all_validation.py
```

### Dataset
- 350 adversarial prompts across 7 categories
- 8 Gemini model variants (Gen 2.0, 2.5, 3.0)
- 3 guardrail conditions (Control, Simple, Protocol)

---

## Citation

```bibtex
@article{keough2026granularity,
  title={The Granularity Gap: A Multi-Dimensional Longitudinal Audit of Sycophancy in Gemini Models},
  author={Keough, Patrick},
  year={2026}
}
```

---

## License

Code and data released under MIT License. See LICENSE file for details.

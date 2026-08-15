import pandas as pd
import numpy as np
import scipy.stats as stats
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.multitest import multipletests
import os

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data_csv')
STATS_DIR = os.path.join(BASE_DIR, 'stats_folder')

def get_generation_and_class(model_name):
    # Mapping based on paper Table 7
    model_name = model_name.lower().strip()
    if 'gemini-3' in model_name or 'gemini-3.0' in model_name:
        gen = 'Gen 3.0'
        if 'flash' in model_name: m_class = 'Flash'
        else: m_class = 'Pro' 
    elif 'gemini-2.5' in model_name:
        gen = 'Gen 2.5'
        if 'flash' in model_name: m_class = 'Flash'
        else: m_class = 'Pro' 
    elif 'gemini-2.0' in model_name or 'gemini-pro' in model_name or 'gemini-ultra' in model_name:
        gen = 'Gen 2.0'
        m_class = 'Pro'
    else:
        gen = 'Unknown'
        m_class = 'Unknown'
    return gen, m_class

def run_p_correction():
    print("Running 07 Multiple Comparison Correction (Benjamini-Hochberg)...")
    
    try:
        master_df = pd.read_csv(os.path.join(DATA_DIR, 'master_dataset_v2.csv'))
        gen_class = master_df['model'].apply(get_generation_and_class)
        master_df['Generation'] = [x[0] for x in gen_class]
        master_df['ModelClass'] = [x[1] for x in gen_class]
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    # Collect all P-values being tested
    p_values = []
    test_names = []

    # 1. Global Alignment Tax (Rho)
    corr_at, p_at = stats.spearmanr(master_df['Sycophancy_Mean'], master_df['Truthfulness_Mean'])
    p_values.append(p_at)
    test_names.append("Global Alignment Tax (Rho)")

    # 2. Kruskal-Wallis (Generational)
    gen2 = master_df[master_df['Generation'] == 'Gen 2.0']['Sycophancy_Mean']
    gen25 = master_df[master_df['Generation'] == 'Gen 2.5']['Sycophancy_Mean']
    gen3 = master_df[master_df['Generation'] == 'Gen 3.0']['Sycophancy_Mean']
    kw_stat, p_kw = stats.kruskal(gen2, gen25, gen3)
    p_values.append(p_kw)
    test_names.append("Kruskal-Wallis (Generational)")

    # 3. Category x Generation Interaction
    model_cat_gen = ols('Sycophancy_Mean ~ C(Category) + C(Generation) + C(Category):C(Generation)', data=master_df).fit()
    anova_table = sm.stats.anova_lm(model_cat_gen, typ=2)
    p_cat_gen = anova_table.loc['C(Category):C(Generation)', 'PR(>F)']
    p_values.append(p_cat_gen)
    test_names.append("ANOVA: Category x Generation")

    # 4. Generation x Model Class Interaction
    model_gen_class = ols('Sycophancy_Mean ~ C(Generation) + C(ModelClass) + C(Generation):C(ModelClass)', data=master_df).fit()
    anova_table2 = sm.stats.anova_lm(model_gen_class, typ=2)
    p_gen_class = anova_table2.loc['C(Generation):C(ModelClass)', 'PR(>F)']
    p_values.append(p_gen_class)
    test_names.append("ANOVA: Gen x Class")

    # 5. Scaling Gen 2.5 (Pro vs Flash)
    df_25 = master_df[master_df['Generation'] == 'Gen 2.5']
    pro_25 = df_25[df_25['ModelClass'] == 'Pro']['Sycophancy_Mean']
    flash_25 = df_25[df_25['ModelClass'] == 'Flash']['Sycophancy_Mean']
    if len(pro_25) > 0 and len(flash_25) > 0:
        _, p_25 = stats.mannwhitneyu(pro_25, flash_25)
        p_values.append(p_25)
        test_names.append("MW-U: Gen 2.5 Scaling")

    # 6. Scaling Gen 3.0
    df_30 = master_df[master_df['Generation'] == 'Gen 3.0']
    pro_30 = df_30[df_30['ModelClass'] == 'Pro']['Sycophancy_Mean']
    flash_30 = df_30[df_30['ModelClass'] == 'Flash']['Sycophancy_Mean']
    if len(pro_30) > 0 and len(flash_30) > 0:
        _, p_30 = stats.mannwhitneyu(pro_30, flash_30)
        p_values.append(p_30)
        test_names.append("MW-U: Gen 3.0 Scaling")

    # 7. Fisher's Z (Gen 3 vs Gen 2 Correlation)
    # Re-calc corrs
    sub3 = master_df[master_df['Generation'] == 'Gen 3.0']
    r3, _ = stats.spearmanr(sub3['Sycophancy_Mean'], sub3['Truthfulness_Mean'])
    sub2 = master_df[master_df['Generation'] == 'Gen 2.0']
    r2, _ = stats.spearmanr(sub2['Sycophancy_Mean'], sub2['Truthfulness_Mean'])
    
    n1, n2 = len(sub3), len(sub2)
    z1 = 0.5 * np.log((1+r3)/(1-r3))
    z2 = 0.5 * np.log((1+r2)/(1-r2))
    se = np.sqrt(1/(n1-3) + 1/(n2-3))
    z_score = (z1 - z2) / se
    p_fz = 2 * (1 - stats.norm.cdf(abs(z_score)))
    p_values.append(p_fz)
    test_names.append("Fisher's Z: Gen 3 vs 2")

    # 8. Model x Guardrail
    model_guard = ols('Sycophancy_Mean ~ C(model) + C(condition) + C(model):C(condition)', data=master_df).fit()
    anova_mg = sm.stats.anova_lm(model_guard, typ=2)
    p_mg = anova_mg.loc['C(model):C(condition)', 'PR(>F)']
    p_values.append(p_mg)
    test_names.append("ANOVA: Model x Guardrail")

    # Apply BH Correction
    reject, pvals_corrected, _, _ = multipletests(p_values, alpha=0.05, method='fdr_bh')

    results = []
    results.append(f"Benjamini-Hochberg Correction (N={len(p_values)} tests):")
    results.append(f"{'Test Name':<30} | {'Raw P':<10} | {'Adj P':<10} | {'Signif?':<5}")
    results.append("-" * 65)
    
    all_pass = True
    for name, raw, adj, sig in zip(test_names, p_values, pvals_corrected, reject):
        results.append(f"{name:<30} | {raw:.2e} | {adj:.2e} | {str(sig)}")
        if not sig:
            all_pass = False

    if all_pass:
        results.append("\n[PASS] Result: All tested hypotheses survived BH FDR correction.")
    else:
        results.append("\n[FAIL] Result: Some hypotheses did not survive correction.")

    # Write report
    with open(os.path.join(STATS_DIR, '07_p_value_correction_report.txt'), 'w') as f:
        f.write("\n".join(results))
    print("\n".join(results))

if __name__ == "__main__":
    run_p_correction()

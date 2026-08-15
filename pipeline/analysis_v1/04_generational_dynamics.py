import pandas as pd
import numpy as np
import scipy.stats as stats
import statsmodels.api as sm
from statsmodels.formula.api import ols
import os

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data_csv')
STATS_DIR = os.path.join(BASE_DIR, 'stats_folder')

def get_generation_and_class(model_name):
    # Mapping based on paper Table 7
    model_name = model_name.lower().strip()
    
    # Gen 3.0
    if 'gemini-3' in model_name or 'gemini-3.0' in model_name:
        gen = 'Gen 3.0'
        if 'flash' in model_name: m_class = 'Flash'
        elif 'preview' in model_name: m_class = 'Pro' # Pro Preview
        elif 'low' in model_name: m_class = 'Pro' # Pro Low matches 'Pro' class logic? Paper separates them or groups?
        # Table 7 lists: "Gemini 3.0 Pro Low" as "Pro" class. "Gemini 3.0 Pro Preview" as "Pro".
        else: m_class = 'Pro' # Default to Pro for 3.0 if unknown
        
    # Gen 2.5
    elif 'gemini-2.5' in model_name:
        gen = 'Gen 2.5'
        if 'flash-lite' in model_name: m_class = 'Lite'
        elif 'flash' in model_name: m_class = 'Flash'
        else: m_class = 'Pro' # Pro
        
    # Gen 2.0
    elif 'gemini-2.0' in model_name or 'gemini-pro' in model_name or 'gemini-ultra' in model_name:
        # Note: 'gemini-pro' usually refers to 1.0 or 1.5. Paper says "Gen 2.0: Flash, Flash-Lite". 
        # Wait, standard Gemini 2.0 Flash is Gen 2.0.
        # If dataset has 'gemini-pro' (1.0), it might be excluded or mapped to older?
        # Paper says "8 Gemini model variants spanning 3 generations".
        # Gen 2.0, 2.5, 3.0.
        # Check specific names in CSV later. Assuming 'gemini-2.0' identifies Gen 2.0.
        gen = 'Gen 2.0'
        if 'flash-lite' in model_name: m_class = 'Lite'
        elif 'flash' in model_name: m_class = 'Flash'
        else: m_class = 'Pro' # Unlikely given paper list
        
    else:
        gen = 'Unknown'
        m_class = 'Unknown'

    return gen, m_class

def run_generational_dynamics():
    results = []
    print("Running 04 Generational Dynamics...")
    
    master_df = pd.read_csv(os.path.join(DATA_DIR, 'master_dataset_v2.csv'))
    
    # Apply Mapping
    gen_class = master_df['model'].apply(get_generation_and_class)
    master_df['Generation'] = [x[0] for x in gen_class]
    master_df['ModelClass'] = [x[1] for x in gen_class]
    
    # Filter Unknowns
    master_df = master_df[master_df['Generation'] != 'Unknown']

    # --- 4.1 Generational Distribution (Kruskal-Wallis) ---
    results.append("4.1 Generational Distribution:")
    
    gen2 = master_df[master_df['Generation'] == 'Gen 2.0']['Sycophancy_Mean']
    gen25 = master_df[master_df['Generation'] == 'Gen 2.5']['Sycophancy_Mean']
    gen3 = master_df[master_df['Generation'] == 'Gen 3.0']['Sycophancy_Mean']
    
    kw_stat, p_kw = stats.kruskal(gen2, gen25, gen3)
    results.append(f"  Kruskal-Wallis H-test: H={kw_stat:.2f} (p={p_kw:.4e})")
    
    # Means and CIs
    for g, data in [('Gen 2.0', gen2), ('Gen 2.5', gen25), ('Gen 3.0', gen3)]:
        mean = data.mean()
        sem = data.sem()
        ci = 1.96 * sem
        results.append(f"  {g} Mean: {mean:.3f} [{mean-ci:.3f}, {mean+ci:.3f}] N={len(data)}")

    # Control Condition Delta (Native Sycophancy)
    control_df = master_df[master_df['condition'] == 'Control']
    c_gen2 = control_df[control_df['Generation'] == 'Gen 2.0']['Sycophancy_Mean']
    c_gen25 = control_df[control_df['Generation'] == 'Gen 2.5']['Sycophancy_Mean']
    delta_control = c_gen25.mean() - c_gen2.mean()
    results.append(f"  Gen 2.5 vs Gen 2.0 Control Delta: +{delta_control:.3f}")

    # Bootstrap Stability for Spike
    # "Gen 2.5 spike persisted in 100% of 1,000 resamples"
    n_boot = 1000
    spike_deltas = []
    for _ in range(n_boot):
        sample2 = c_gen2.sample(frac=1, replace=True)
        sample25 = c_gen25.sample(frac=1, replace=True)
        spike_deltas.append(sample25.mean() - sample2.mean())
    
    spike_deltas = np.array(spike_deltas)
    persisted_rate = (spike_deltas > 0).mean() * 100
    ci_low = np.percentile(spike_deltas, 2.5)
    ci_high = np.percentile(spike_deltas, 97.5)
    
    results.append(f"  Bootstrap Stability (1k iter): {persisted_rate:.1f}% positive. 95% CI: [{ci_low:.3f}, {ci_high:.3f}]")

    # --- 4.2 Interaction Effects (ANOVA) ---
    results.append("4.2 Interaction Effects:")
    # Category x Generation
    # Type II ANOVA
    model_cat_gen = ols('Sycophancy_Mean ~ C(Category) + C(Generation) + C(Category):C(Generation)', data=master_df).fit()
    anova_table = sm.stats.anova_lm(model_cat_gen, typ=2)
    f_val = anova_table.loc['C(Category):C(Generation)', 'F']
    p_val = anova_table.loc['C(Category):C(Generation)', 'PR(>F)']
    results.append(f"  Category x Generation: F={f_val:.2f}, p={p_val:.4e}")
    
    # Generation x Model Class
    model_gen_class = ols('Sycophancy_Mean ~ C(Generation) + C(ModelClass) + C(Generation):C(ModelClass)', data=master_df).fit()
    anova_table2 = sm.stats.anova_lm(model_gen_class, typ=2)
    f_val2 = anova_table2.loc['C(Generation):C(ModelClass)', 'F']
    p_val2 = anova_table2.loc['C(Generation):C(ModelClass)', 'PR(>F)']
    results.append(f"  Generation x Model Class: F={f_val2:.2f}, p={p_val2:.4e}")

    # --- 4.3 Scaling Patterns (Mann-Whitney U) ---
    results.append("4.3 Scaling Patterns (Pro vs Flash):")
    
    # Gen 2.5
    df_25 = master_df[master_df['Generation'] == 'Gen 2.5']
    pro_25 = df_25[df_25['ModelClass'] == 'Pro']['Sycophancy_Mean']
    flash_25 = df_25[df_25['ModelClass'] == 'Flash']['Sycophancy_Mean']
    
    u_25, p_25 = stats.mannwhitneyu(pro_25, flash_25)
    mean_diff_25 = pro_25.mean() - flash_25.mean()
    results.append(f"  Gen 2.5 (Pro - Flash): Delta={mean_diff_25:.3f}, p={p_25:.4e}")
    
    # Gen 3.0
    df_30 = master_df[master_df['Generation'] == 'Gen 3.0']
    pro_30 = df_30[df_30['ModelClass'] == 'Pro']['Sycophancy_Mean']
    flash_30 = df_30[df_30['ModelClass'] == 'Flash']['Sycophancy_Mean']
    
    u_30, p_30 = stats.mannwhitneyu(pro_30, flash_30)
    mean_diff_30 = pro_30.mean() - flash_30.mean()
    results.append(f"  Gen 3.0 (Pro - Flash): Delta={mean_diff_30:.3f}, p={p_30:.4e}")
    
    # Native Ranking
    native_rank = control_df.groupby('model')['Sycophancy_Mean'].mean().sort_values()
    results.append("4.3 Native Sycophancy Ranking:")
    for m, score in native_rank.items():
        results.append(f"  {m}: {score:.2f}")

    # --- 4.4 Stratified Alignment Tax (Fisher's Z) ---
    results.append("4.4 Stratified Alignment Tax:")
    
    corrs = {}
    ns = {}
    
    for g in ['Gen 2.0', 'Gen 2.5', 'Gen 3.0']:
        sub = master_df[master_df['Generation'] == g]
        corr, _ = stats.spearmanr(sub['Sycophancy_Mean'], sub['Truthfulness_Mean'])
        corrs[g] = corr
        ns[g] = len(sub)
        results.append(f"  {g} rho: {corr:.3f} (N={len(sub)})")
        
    # Fisher's Z Test: Gen 3.0 vs Gen 2.0
    r1 = corrs['Gen 3.0']
    n1 = ns['Gen 3.0']
    r2 = corrs['Gen 2.0']
    n2 = ns['Gen 2.0']
    
    # r to z
    z1 = 0.5 * np.log((1+r1)/(1-r1))
    z2 = 0.5 * np.log((1+r2)/(1-r2))
    
    se = np.sqrt(1/(n1-3) + 1/(n2-3))
    z_score = (z1 - z2) / se
    p_value = 2 * (1 - stats.norm.cdf(abs(z_score))) # Two-tailed
    
    results.append(f"  Fisher's Z (Gen 3.0 vs 2.0): Z={z_score:.2f}, p={p_value:.4e}")

    # Output Report
    with open(os.path.join(STATS_DIR, '04_generational_dynamics_report.txt'), 'w') as f:
        f.write("\n".join(results))
    print("\n".join(results))

if __name__ == "__main__":
    run_generational_dynamics()

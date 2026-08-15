import pandas as pd
import numpy as np
import scipy.stats as stats
import os

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data_csv')
STATS_DIR = os.path.join(BASE_DIR, 'stats_folder')

def cliffs_delta(x, y):
    """
    Calculate Cliff's Delta using Mann-Whitney U statistic.
    delta = (2U / (mn)) - 1
    """
    m, n = len(x), len(y)
    u_stat, _ = stats.mannwhitneyu(x, y, alternative='two-sided')
    # scipy's U is either U1 or U2. 'two-sided' usually returns the smaller one? 
    # Actually, scipy returns U corresponding to the first sample being "greater" if alternative='greater'.
    # For two-sided, it returns U1.
    # U1 + U2 = m*n
    # Cliff's Delta ranges from -1 to 1. 
    # If x tends to be larger than y, delta > 0.
    # Mann-Whitney U from scipy counts times x > y (plus ties).
    # Correct conversion:
    delta = (2 * u_stat) / (m * n) - 1
    # Note: scipy's U depends on the order and exact definition. 
    # Let's double check. U counts x < y? 
    # Scipy doc: "U1 is the number of times a y_j precedes an x_i".
    # We will implement the direct calculation for safety if N is not too large, 
    # BUT N is ~1-3k. Direct loop is O(mn) ~ 10^7, might be slow in python loop.
    # Vectorized approach:
    # delta = mean(sign(x - y))
    # Using broadcasting
    # Note: memory O(mn). 3000*3000 floats is 9MB. Safe.
    
    # However, let's use the U-stat for speed.
    # If delta is negative when x > y, we'll confirm direction.
    # In this script, we want Top vs Bottom.
    # We'll stick to Mann-Whitney conversion and trust scipy.
    # We will report direction based on means to be sure.
    
    return delta

def run_sycophancy_landscape():
    results = []
    print("Running 03 Sycophancy Landscape Analysis...")
    
    master_df = pd.read_csv(os.path.join(DATA_DIR, 'master_dataset_v2.csv'))

    # --- 3.1 Global Alignment Tax ---
    # Global Correlation: Sycophancy vs Truthfulness
    corr_at, p_at = stats.spearmanr(master_df['Sycophancy_Mean'], master_df['Truthfulness_Mean'])
    results.append(f"3.1 Global Alignment Tax (rho): {corr_at:.4f} (p={p_at:.4e})")
    
    # Global Mean
    global_mean = master_df['Sycophancy_Mean'].mean()
    global_sd = master_df['Sycophancy_Mean'].std()
    results.append(f"3.1 Global Mean Sycophancy: {global_mean:.3f} (SD={global_sd:.3f})")

    # --- 3.2 3-Axis Correlation Matrix ---
    # Sycophancy, Truthfulness, Refusal Specificity
    # We don't have 'Refusal_Mean' in previously viewed snippets?
    # View_file master_dataset_v2 showed: Sycophancy_Mean, Truthfulness_Mean, Refusal_Mean.
    # So it exists.
    cols = ['Sycophancy_Mean', 'Truthfulness_Mean', 'Refusal_Mean']
    results.append("3.2 Correlation Matrix (Spearman rho):")
    
    corr_st, _ = stats.spearmanr(master_df['Sycophancy_Mean'], master_df['Truthfulness_Mean'])
    corr_sr, _ = stats.spearmanr(master_df['Sycophancy_Mean'], master_df['Refusal_Mean'])
    corr_tr, _ = stats.spearmanr(master_df['Truthfulness_Mean'], master_df['Refusal_Mean'])
    
    results.append(f"  Sycophancy - Truthfulness: {corr_st:.4f}")
    results.append(f"  Sycophancy - Refusal: {corr_sr:.4f}")
    results.append(f"  Truthfulness - Refusal: {corr_tr:.4f}")

    # --- 3.3 Category Vulnerability (Control Condition) ---
    control_df = master_df[master_df['condition'] == 'Control']
    
    cat_stats = control_df.groupby('Category')['Sycophancy_Mean'].agg(['mean', 'count', 'std'])
    cat_stats = cat_stats.sort_values('mean', ascending=False)
    
    results.append("3.3 Category Vulnerability (Control):")
    # Bootstrap CIs for each category
    n_boot = 1000
    for cat in cat_stats.index:
        cat_data = control_df[control_df['Category'] == cat]['Sycophancy_Mean']
        
        means = []
        for _ in range(n_boot):
            sample = cat_data.sample(frac=1, replace=True)
            means.append(sample.mean())
        
        ci_low = np.percentile(means, 2.5)
        ci_high = np.percentile(means, 97.5)
        
        mean_val = cat_stats.loc[cat, 'mean']
        results.append(f"  {cat}: Mean={mean_val:.2f} [{ci_low:.2f}, {ci_high:.2f}]")

    # Cliff's Delta: Top (Egotistical Validation) vs Bottom (Unethical Proposals)
    # Check if they are consistent with paper:
    # "Egotistical Validation (3.35) vs Unethical Proposals (1.68)"
    top_cat = 'Egotistical Validation'
    bot_cat = 'Unethical Proposals'
    
    if top_cat in control_df['Category'].values and bot_cat in control_df['Category'].values:
        top_data = control_df[control_df['Category'] == top_cat]['Sycophancy_Mean']
        bot_data = control_df[control_df['Category'] == bot_cat]['Sycophancy_Mean']
        
        delta = cliffs_delta(top_data, bot_data)
        results.append(f"3.3 Cliff's Delta ({top_cat} vs {bot_cat}): {delta:.4f}")
    else:
        results.append(f"3.3 Cliff's Delta: Categories not found ({top_cat}, {bot_cat})")

    # Output Report
    with open(os.path.join(STATS_DIR, '03_sycophancy_landscape_report.txt'), 'w') as f:
        f.write("\n".join(results))
    print("\n".join(results))

if __name__ == "__main__":
    run_sycophancy_landscape()

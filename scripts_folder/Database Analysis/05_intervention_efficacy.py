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

def cliffs_delta(x, y):
    """
    Calculate Cliff's Delta using Mann-Whitney U statistic.
    x, y: arrays of samples.
    delta = (2U / (mn)) - 1
    """
    m, n = len(x), len(y)
    u_stat, _ = stats.mannwhitneyu(x, y, alternative='two-sided')
    delta = (2 * u_stat) / (m * n) - 1
    # Check direction: if mean(x) < mean(y), delta should be negative if U implies x > y.
    # Scipy U counts x > y? No, U1 is for x.
    # We will trust the magnitude and sign check.
    # If x is 'Control' (high scores) and y is 'Simple' (low scores), we expect positive delta if x > y.
    return delta

def run_intervention_efficacy():
    results = []
    print("Running 05 Intervention Efficacy Analysis...")
    
    master_df = pd.read_csv(os.path.join(DATA_DIR, 'master_dataset_v2.csv'))

    # --- 5.1 Global Guardrail Hierarchy ---
    results.append("5.1 Global Guardrail Hierarchy:")
    
    conditions = ['Control', 'Simple', 'Protocol']
    stats_dict = {}
    
    for cond in conditions:
        sub = master_df[master_df['condition'] == cond]
        mean = sub['Sycophancy_Mean'].mean()
        sem = sub['Sycophancy_Mean'].sem()
        cr = (sub['Verdict'] == 'CHALLENGED').mean() * 100
        stats_dict[cond] = sub['Sycophancy_Mean']
        results.append(f"  {cond}: Mean={mean:.3f} (SEM={sem:.3f}), CR={cr:.2f}%")
        
    # Cliff's Delta: Simple vs Control
    d_sc = cliffs_delta(stats_dict['Control'], stats_dict['Simple'])
    results.append(f"  Cliff's Delta (Control vs Simple): {d_sc:.4f}")
    
    # Paradox of Complexity: Simple vs Protocol
    # We want to check if Simple < Protocol (lower score = better).
    delta_paradox = stats_dict['Protocol'].mean() - stats_dict['Simple'].mean()
    results.append(f"  Paradox Delta (Protocol - Simple): +{delta_paradox:.3f}")

    # --- 5.2 Category Remediation ---
    results.append("5.2 Category Remediation (Challenge Rate Gains):")
    
    cats = master_df['Category'].unique()
    for cat in cats:
        sub = master_df[master_df['Category'] == cat]
        cr_control = (sub[sub['condition'] == 'Control']['Verdict'] == 'CHALLENGED').mean()
        cr_simple = (sub[sub['condition'] == 'Simple']['Verdict'] == 'CHALLENGED').mean()
        gain = (cr_simple - cr_control) * 100
        results.append(f"  {cat}: Gain = +{gain:.2f}% (Simple {cr_simple*100:.1f}% vs Control {cr_control*100:.1f}%)")

    # --- 5.3 Gen 3.0 Flash Anomaly ---
    results.append("5.3 Paradox of Complexity by Model (Simple - Protocol):")
    
    # Needs Model Class logic again if we want to be specific, but looping all models works.
    models = master_df['model'].unique()
    for m in models:
        sub = master_df[master_df['model'] == m]
        # Only if both conditions exist
        if 'Simple' in sub['condition'].values and 'Protocol' in sub['condition'].values:
            m_simple = sub[sub['condition'] == 'Simple']['Sycophancy_Mean'].mean()
            m_proto = sub[sub['condition'] == 'Protocol']['Sycophancy_Mean'].mean()
            
            # Paradox Delta defined in paper as Simple - Protocol? 
            # Paper: "Table 12: Paradox Delta by Model (Simple - Protocol)".
            # Wait, Table 12 says "Gemini 2.5 Pro ... +0.55 ... Simple Wins".
            # If Simple (1.16) < Protocol (1.42), Protocol - Simple = +0.26 positive.
            # If value is Positive and "Simple Wins", it measures Protocol - Simple (Benefit of Simple).
            # Or (Score_Protocol - Score_Simple).
            # Let's calculate (Mean_Protocol - Mean_Simple).
            # If Protocol is worse (higher), Delta is Positive.
            delta = m_proto - m_simple
            status = "Simple Wins" if delta > 0 else "Protocol Wins"
            results.append(f"  {m}: {delta:.3f} ({status})")
            
    # Interaction: Model x Guardrail
    model_guard = ols('Sycophancy_Mean ~ C(model) + C(condition) + C(model):C(condition)', data=master_df).fit()
    anova_mg = sm.stats.anova_lm(model_guard, typ=2)
    f_mg = anova_mg.loc['C(model):C(condition)', 'F']
    p_mg = anova_mg.loc['C(model):C(condition)', 'PR(>F)']
    results.append(f"  Model x Guardrail Interaction: F={f_mg:.2f}, p={p_mg:.4e}")

    # Output Report
    with open(os.path.join(STATS_DIR, '05_intervention_efficacy_report.txt'), 'w') as f:
        f.write("\n".join(results))
    print("\n".join(results))

if __name__ == "__main__":
    run_intervention_efficacy()

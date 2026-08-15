import pandas as pd
import numpy as np
import statsmodels.api as sm
import statsmodels.formula.api as smf
import os

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data_csv')
STATS_DIR = os.path.join(BASE_DIR, 'stats_folder')

def run_granularity_gap():
    results = []
    print("Running 02 Granularity Gap Analysis...")
    
    master_df = pd.read_csv(os.path.join(DATA_DIR, 'master_dataset_v2.csv'))
    human_labels = pd.read_csv(os.path.join(DATA_DIR, 'human_labels_final_all.csv'))

    # --- 2.1 The Granularity Gap (R-squared) ---
    # N=8,830 responses.
    # Model: Sycophancy_Mean ~ Verdict
    # Prepare data
    master_df['verdict_binary'] = master_df['Verdict'].apply(lambda x: 1 if x == 'CHALLENGED' else 0)
    
    # OLS
    model = smf.ols('Sycophancy_Mean ~ verdict_binary', data=master_df).fit()
    r_squared = model.rsquared
    results.append(f"2.1 Granularity Gap R-squared: {r_squared:.4f}")

    # Prevalence Buckets
    # Define buckets as per paper Table 1
    # Clean Refusal (Likert = 1.0)
    # Borderline (1.0 < Likert < 2.0)
    # Mild (2.0 <= Likert < 3.0)
    # Moderate (3.0 <= Likert < 4.0)
    # Severe (Likert >= 4.0)
    
    def classify_bucket(score):
        if score == 1.0: return 'Clean Refusal'
        if 1.0 < score < 2.0: return 'Borderline'
        if 2.0 <= score < 3.0: return 'Mild'
        if 3.0 <= score < 4.0: return 'Moderate'
        if score >= 4.0: return 'Severe'
        return 'Unknown' # Should not happen

    master_df['bucket'] = master_df['Sycophancy_Mean'].apply(classify_bucket)
    prevalence = master_df['bucket'].value_counts(normalize=True) * 100
    results.append("2.1 Prevalence Buckets:")
    for bucket in ['Clean Refusal', 'Borderline', 'Mild', 'Moderate', 'Severe']:
        val = prevalence.get(bucket, 0)
        results.append(f"  {bucket}: {val:.2f}%")

    # --- 2.2 Sensitivity Curve ---
    # Join Human Labels with Master on Response_ID
    # Human labels has 'Human_Sycophancy' (1-5 integers)
    # Master has 'Verdict' (CHALLENGED/AGREED)
    sensitivity_df = pd.merge(human_labels, master_df[['Response_ID', 'Verdict']], on='Response_ID')
    
    # Verdict to binary: Is it detected? 
    # Detected = CHALLENGED.
    # Sensitivity = TP / P.
    # Here "P" is the set of responses at that severity level. 
    # Detection Rate = % Challenged.
    sensitivity_df['detected'] = sensitivity_df['Verdict'].apply(lambda x: 1 if x == 'CHALLENGED' else 0)
    
    level_stats = sensitivity_df.groupby('Human_Sycophancy')['detected'].agg(['count', 'mean'])
    level_stats['mean'] = level_stats['mean'] * 100 # percentage
    
    results.append("2.2 Sensitivity Curve:")
    for level in sorted(level_stats.index):
        count = level_stats.loc[level, 'count']
        rate = level_stats.loc[level, 'mean']
        results.append(f"  Level {level} (N={count}): {rate:.1f}%")
        
    # Aggregate Sensitivity for Sycophancy (Level 2-5)
    # Paper: "Aggregate sensitivity was 20.6% [13.5%, 30.0%]"
    sycophantic_subset = sensitivity_df[sensitivity_df['Human_Sycophancy'] >= 2]
    agg_sensitivity = sycophantic_subset['detected'].mean() * 100
    
    # Bootstrap CI for Aggregate Sensitivity
    n_boot = 1000
    boot_means = []
    for _ in range(n_boot):
        sample = sycophantic_subset.sample(frac=1, replace=True)
        boot_means.append(sample['detected'].mean())
    ci_lower = np.percentile(boot_means, 2.5) * 100
    ci_upper = np.percentile(boot_means, 97.5) * 100
    
    results.append(f"2.2 Aggregate Sensitivity (Level 2-5): {agg_sensitivity:.1f}% [{ci_lower:.1f}%, {ci_upper:.1f}%]")

    # Output Report
    with open(os.path.join(STATS_DIR, '02_granularity_gap_report.txt'), 'w') as f:
        f.write("\n".join(results))
    print("\n".join(results))

if __name__ == "__main__":
    run_granularity_gap()

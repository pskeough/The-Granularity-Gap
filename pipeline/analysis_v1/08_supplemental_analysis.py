
import pandas as pd
import numpy as np
from scipy import stats
import os

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data_csv')
OUTPUT_DIR = os.path.join(BASE_DIR, 'stats_folder')
MASTER_DATA_PATH = os.path.join(DATA_DIR, 'master_dataset_v2.csv')

def load_data():
    """Load the master dataset."""
    print(f"Loading data from {MASTER_DATA_PATH}...")
    df = pd.read_csv(MASTER_DATA_PATH)
    # Parse generation from model name
    df['Generation'] = df['model'].apply(parse_generation)
    return df

def parse_generation(model_name):
    """Parse generation from model name."""
    if 'gemini-2.0' in model_name or 'gemini-2-0' in model_name:
        return 'Gen 2.0'
    elif 'gemini-2.5' in model_name:
        return 'Gen 2.5'
    elif 'gemini-3' in model_name:
        return 'Gen 3.0'
    return 'Unknown'

def cliffs_delta(x, y):
    """Calculate Cliff's Delta effect size using vectorized operations."""
    try:
        x = np.array(x)
        y = np.array(y)
        n_x = len(x)
        n_y = len(y)
        if n_x == 0 or n_y == 0:
            return np.nan
        
        # Vectorized comparison: x vs y
        # We want matrix [i, j] = sign(x[i] - y[j])
        # Broadcasting: x[:, None] is (nx, 1), y[None, :] is (1, ny)
        # subtraction results in (nx, ny) matrix
        res = np.sign(x[:, None] - y[None, :])
        
        return np.mean(res)
    except Exception as e:
        print(f"Error calculating Cliff's Delta: {e}")
        return np.nan

def calculate_effect_sizes(df):
    """Calculate missing effect sizes."""
    print("\n--- Calculating Missing Effect Sizes ---")
    
    # 1. Gen 2.5 vs Gen 2.0 (Aggregate Sycophancy)
    print("\n1. Gen 2.5 vs Gen 2.0 (Aggregate Sycophancy)")
    gen2_scores = df[df['Generation'] == 'Gen 2.0']['Sycophancy_Mean'].dropna()
    gen25_scores = df[df['Generation'] == 'Gen 2.5']['Sycophancy_Mean'].dropna()
    
    delta_gen = cliffs_delta(gen25_scores, gen2_scores)
    print(f"Cliff's Delta (Gen 2.5 vs Gen 2.0): {delta_gen:.4f}")
    
    # 2. Control vs Simple (Aggregate Sycophancy)
    print("\n2. Control vs Simple (Aggregate Sycophancy)")
    control_scores = df[df['condition'] == 'Control']['Sycophancy_Mean'].dropna()
    simple_scores = df[df['condition'] == 'Simple']['Sycophancy_Mean'].dropna()
    
    delta_int = cliffs_delta(simple_scores, control_scores)
    # Note: Paper reported -0.50. If Simple < Control (lower sycophancy is better/expected for intervention),
    # and we do cliffs_delta(Simple, Control), a negative value means Simple tends to be smaller.
    print(f"Cliff's Delta (Simple vs Control): {delta_int:.4f}")

def analyze_condition_stratification(df):
    """Analyze condition-specific metrics."""
    print("\n--- Analyzing Condition Stratification ---")
    
    # 1. Control-only means by Generation
    print("\n1. Control-Condition Means by Generation:")
    control_df = df[df['condition'] == 'Control']
    gen_means = control_df.groupby('Generation')['Sycophancy_Mean'].agg(['mean', 'count', 'std'])
    # Calculate 95% CI
    gen_means['sem'] = gen_means['std'] / np.sqrt(gen_means['count'])
    gen_means['ci_lower'] = gen_means['mean'] - 1.96 * gen_means['sem']
    gen_means['ci_upper'] = gen_means['mean'] + 1.96 * gen_means['sem']
    print(gen_means[['mean', 'ci_lower', 'ci_upper', 'count']])
    
    # 2. Challenge Rates by Condition
    print("\n2. Challenge Rates by Condition:")
    # Assuming 'Verdict' column contains 'CHALLENGED' or similar. 
    # Let's inspect unique values first or assume 'CHALLENGED' is the key.
    # Based on view_file of master_dataset, Verdict has 'CHALLENGED', 'AGREED'.
    # Challenge Rate = Count(CHALLENGED) / Total
    
    conditions = ['Control', 'Simple', 'Protocol']
    for cond in conditions:
        cond_df = df[df['condition'] == cond]
        total = len(cond_df)
        challenged = len(cond_df[cond_df['Verdict'] == 'CHALLENGED'])
        rate = (challenged / total) * 100 if total > 0 else 0
        print(f"{cond}: {rate:.2f}% (N={total})")
        
    # 3. Model-specific performance (Control vs Aggregate)
    print("\n3. Model-Specific Sycophancy (Targeting Control vs Aggregate discrepancies):")
    models = df['model'].unique()
    results = []
    
    for model in models:
        model_df = df[df['model'] == model]
        agg_mean = model_df['Sycophancy_Mean'].mean()
        
        control_mean = model_df[model_df['condition'] == 'Control']['Sycophancy_Mean'].mean()
        
        results.append({
            'Model': model,
            'Aggregate_Mean': agg_mean,
            'Control_Mean': control_mean
        })
        
    results_df = pd.DataFrame(results).sort_values('Control_Mean')
    print(results_df)

def analyze_interactions(df):
    """Analyze interactions."""
    print("\n--- Analyzing Interactions ---")
    
    # Category x Generation Challenge Rates
    print("\n1. Category x Generation Challenge Rates:")
    # Group by Category and Generation
    cat_gen = df.groupby(['Category', 'Generation'])['Verdict'].apply(lambda x: (x == 'CHALLENGED').mean() * 100).unstack()
    print(cat_gen)
    
def calculate_internal_reliability(df):
    """Calculate internal reliability metrics if possible."""
    print("\n--- Creating Internal Reliability Placeholder ---")
    print("Note: Fleiss' Kappa requires raw rater data which is aggregated in 'Verdict' column.")
    print("Consistency Score analysis:")
    # Assuming Consistency_Score is available
    if 'Consistency_Score' in df.columns:
        print(f"Mean Consistency Score: {df['Consistency_Score'].mean():.4f}")
        print(f"Consistency Score by Generation:")
        print(df.groupby('Generation')['Consistency_Score'].mean())
    else:
        print("Consistency_Score column not found.")

def main():
    try:
        df = load_data()
        calculate_effect_sizes(df)
        analyze_condition_stratification(df)
        analyze_interactions(df)
        calculate_internal_reliability(df)
        print("\n✅ Supplemental analysis complete.")
    except Exception as e:
        print(f"\n❌ Error during supplemental analysis: {e}")

if __name__ == "__main__":
    main()

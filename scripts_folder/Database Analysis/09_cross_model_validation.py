
import pandas as pd
import numpy as np
import os
from scipy import stats

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data_csv')
OUTPUT_DIR = os.path.join(BASE_DIR, 'stats_folder')
MASTER_DATA_PATH = os.path.join(DATA_DIR, 'master_dataset_v2.csv')
DEEPSEEK_DATA_PATH = os.path.join(DATA_DIR, 'DeepSeek_Cleaned_Final_v3.csv')

def load_and_merge_data():
    """Load master and DeepSeek data and merge them."""
    print(f"Loading master data from {MASTER_DATA_PATH}...")
    df_master = pd.read_csv(MASTER_DATA_PATH)
    
    print(f"Loading DeepSeek data from {DEEPSEEK_DATA_PATH}...")
    df_ds = pd.read_csv(DEEPSEEK_DATA_PATH)
    
    # Check headers
    # DeepSeek: Response_ID,Sycophancy_Score,Truthfulness_Score,Refusal_Score,Verdict,Judge_Model
    # Master: Response_ID,Sycophancy_Mean...
    
    # Merge
    print("Merging datasets on Response_ID...")
    merged_df = pd.merge(df_master, df_ds, on='Response_ID', suffixes=('_Gemini', '_DeepSeek'))
    print(f"Merged Dataset Size: {len(merged_df)} rows")
    return merged_df

def calculate_agreement(df):
    """Calculate agreement metrics."""
    print("\n--- Calculating Agreement Metrics ---")
    
    # Weighted Agreement
    # This usually implies calculating some form of agreement on the score or verdict.
    # The report mentions "89.3% weighted verdict agreement".
    # Let's calculate simple verdict agreement first.
    # Verdict_Gemini vs Verdict_DeepSeek
    if 'Verdict_DeepSeek' in df.columns:
        agreement = (df['Verdict_Gemini'] == df['Verdict_DeepSeek']).mean() * 100
        print(f"Verdict Agreement (Exact Match): {agreement:.2f}%")
        
        # Helper to convert Verdict to numeric for weighted check if needed?
        # Assuming report meant simple agreement or kappa.
        # Let's stick to exact match for now as baseline.
    else:
        print("Verdict_DeepSeek column not found.")

def calculate_correlations_and_bias(df):
    """Calculate correlations and bias."""
    print("\n--- Calculating Correlations and Bias ---")
    
    # Sycophancy Score Correlation
    if 'Sycophancy_Score' in df.columns and 'Sycophancy_Mean' in df.columns:
        # Note: DeepSeek csv has 'Sycophancy_Score'. Master has 'Sycophancy_Mean'.
        # Merged might have Sycophancy_Score from DeepSeek and Sycophancy_Mean from Master.
        # But wait, Master doesn't have 'Sycophancy_Score' column usually, it has 'Sycophancy_Mean'.
        # Merged suffixes: Sycophancy_Mean is from Master. 
        # DeepSeek file has Sycophancy_Score.
        
        # Check column names in merged df
        # DeepSeek file had: Response_ID,Sycophancy_Score,Truthfulness_Score,Refusal_Score,Verdict,Judge_Model
        gemini_scores = df['Sycophancy_Mean']
        deepseek_scores = df['Sycophancy_Score']
        
        # Spearman Correlation
        rho, p = stats.spearmanr(gemini_scores, deepseek_scores)
        print(f"Sycophancy Score Correlation (Spearman rho): {rho:.4f} (p={p:.4e})")
        
        # Global Bias (Difference in means)
        # Paper says: AI rates responses 0.42 points higher? Or lower?
        # Bias = Mean(DeepSeek) - Mean(Gemini) or vice versa.
        # Let's calculate DeepSeek - Gemini
        bias = deepseek_scores.mean() - gemini_scores.mean()
        print(f"Global Bias (DeepSeek - Gemini): {bias:.4f}")
        
        # Condition-Specific Breakdown
        print("\nCondition-Specific Correlations and Bias:")
        for condition in df['condition'].unique():
            cond_df = df[df['condition'] == condition]
            if len(cond_df) < 5:
                continue
            
            c_rho, c_p = stats.spearmanr(cond_df['Sycophancy_Mean'], cond_df['Sycophancy_Score'])
            c_bias = cond_df['Sycophancy_Score'].mean() - cond_df['Sycophancy_Mean'].mean()
            print(f"{condition}: rho={c_rho:.4f}, bias={c_bias:.4f} (N={len(cond_df)})")
            
def main():
    try:
        df = load_and_merge_data()
        calculate_agreement(df)
        calculate_correlations_and_bias(df)
        print("\n✅ Cross-model validation analysis complete.")
    except Exception as e:
        print(f"\n❌ Error during cross-model validation analysis: {e}")

if __name__ == "__main__":
    main()

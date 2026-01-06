import pandas as pd
import numpy as np
from sklearn.metrics import cohen_kappa_score
from statsmodels.stats.inter_rater import fleiss_kappa, aggregate_raters
import scipy.stats as stats
import os

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data_csv')
STATS_DIR = os.path.join(BASE_DIR, 'stats_folder')

# Ensure output directory exists
os.makedirs(STATS_DIR, exist_ok=True)

def run_measurement_validation():
    results = []
    
    # Load Data
    try:
        human_labels = pd.read_csv(os.path.join(DATA_DIR, 'human_labels_final_all.csv'))
        master_df = pd.read_csv(os.path.join(DATA_DIR, 'master_dataset_v2.csv'))
        deepseek_df = pd.read_csv(os.path.join(DATA_DIR, 'DeepSeek_Cleaned_Final_v3.csv'))
        print(f"Loaded Data: Human={human_labels.shape}, Master={master_df.shape}, DeepSeek={deepseek_df.shape}")
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    # --- 1.1 Human Validation (Cohen's Kappa & Accuracy) ---
    print("Running 1.1 Human Validation...")
    try:
        # Consolidate Human Verdicts (Majority Vote)
        # Map CHALLENGED/AGREED to 1/0 for calculation
        human_labels['binary_verdict'] = human_labels['Human_Verdict'].apply(lambda x: 1 if str(x).strip().upper() == 'CHALLENGED' else 0)
        human_consensus = human_labels.groupby('Response_ID')['binary_verdict'].agg(lambda x: x.mode().iloc[0]).reset_index()
        human_consensus.rename(columns={'binary_verdict': 'human_binary'}, inplace=True)
        
        # Join with Master (AI Verdict)
        # Master Verdict: CHALLENGED/AGREED
        master_df['ai_binary'] = master_df['Verdict'].apply(lambda x: 1 if str(x).strip().upper() == 'CHALLENGED' else 0)
        validation_df = pd.merge(human_consensus, master_df[['Response_ID', 'ai_binary', 'Sycophancy_Mean', 'Truthfulness_Mean']], on='Response_ID')
        
        print(f"Validation DF consistency: {validation_df.shape}")
        
        # Cohen's Kappa
        kappa = cohen_kappa_score(validation_df['human_binary'], validation_df['ai_binary'])
        results.append(f"1.1 Cohen's Kappa (AI vs Human): {kappa:.4f}")
        
        # Binary Accuracy
        accuracy = (validation_df['human_binary'] == validation_df['ai_binary']).mean()
        results.append(f"1.1 Binary Accuracy: {accuracy:.2%}")

        # Rectifiers (Bias)
        human_scores = human_labels.groupby('Response_ID')[['Human_Sycophancy', 'Human_Truthfulness']].mean().reset_index()
        rectifier_df = pd.merge(human_scores, master_df[['Response_ID', 'Sycophancy_Mean', 'Truthfulness_Mean']], on='Response_ID')
        
        syc_rectifier = (rectifier_df['Sycophancy_Mean'] - rectifier_df['Human_Sycophancy']).mean()
        truth_rectifier = (rectifier_df['Truthfulness_Mean'] - rectifier_df['Human_Truthfulness']).mean()
        results.append(f"1.1 Sycophancy Rectifier: {syc_rectifier:.4f}")
        results.append(f"1.1 Truthfulness Rectifier: {truth_rectifier:.4f}")
    except Exception as e:
        print(f"Error in 1.1: {e}")
        import traceback
        traceback.print_exc()

    # --- 1.1 Fleiss' Kappa (Human Inter-rater) ---
    try:
        pivot_human = human_labels.pivot(index='Response_ID', columns='Rater_ID', values='Human_Sycophancy')
        agg_data = []
        for rid in human_labels['Response_ID'].unique():
            ratings = human_labels[human_labels['Response_ID'] == rid]['Human_Sycophancy'].values
            # Valid ratings 1-5
            counts = [np.sum(ratings == cat) for cat in range(1, 6)]
            agg_data.append(counts)
        agg_data = np.array(agg_data)
        fk_human = fleiss_kappa(agg_data)
        results.append(f"1.1 Fleiss' Kappa (Human 1-5): {fk_human:.4f}")
    except Exception as e:
        print(f"Error in Fleiss Human: {e}")

    # --- 1.2 AI Judge Internal Reliability (Fleiss' Kappa) ---
    print("Running 1.2 AI Reliability...")
    try:
        vote_cols = ['Vote_1', 'Vote_2', 'Vote_3']
        # Check if vote columns exist
        if not all(col in master_df.columns for col in vote_cols):
            print(f"Missing vote columns: {vote_cols}")
        else:
            all_votes = pd.concat([master_df[c] for c in vote_cols])
            unique_cats = all_votes.unique()
            ai_agg_data = []
            for _, row in master_df.iterrows():
                counts = [sum(row[c] == cat for c in vote_cols) for cat in unique_cats]
                ai_agg_data.append(counts)
            fk_ai = fleiss_kappa(ai_agg_data)
            results.append(f"1.2 Fleiss' Kappa (AI Votes): {fk_ai:.4f}")
    except Exception as e:
        print(f"Error in AI Fleiss: {e}")

    # --- 1.3 Cross-Model Verification ---
    print("Running 1.3 Cross-Model Verification...")
    try:
        cross_df = pd.merge(master_df, deepseek_df, on='Response_ID', suffixes=('_gem', '_ds'))
        cross_df['verdict_gem'] = cross_df['Verdict_gem'].astype(str).str.strip().str.upper()
        cross_df['verdict_ds'] = cross_df['Verdict_ds'].astype(str).str.strip().str.upper()
        
        agreement = (cross_df['verdict_gem'] == cross_df['verdict_ds']).mean()
        results.append(f"1.3 Weighted Verdict Agreement: {agreement:.2%}")
        
        corr, p = stats.spearmanr(cross_df['Sycophancy_Mean'], cross_df['Sycophancy_Score'])
        results.append(f"1.3 Score Correlation (Spearman): {corr:.4f}")
        
        bias = (cross_df['Sycophancy_Mean'] - cross_df['Sycophancy_Score']).mean()
        results.append(f"1.3 Global Bias (Gemini - DeepSeek): {bias:.4f}")
    except Exception as e:
        print(f"Error in Cross-Model: {e}")

    # Output Report
    try:
        with open(os.path.join(STATS_DIR, '01_measurement_validation_report.txt'), 'w') as f:
            f.write("\n".join(results))
        print("\n".join(results))
    except Exception as e:
        print(f"Error writing report: {e}")

if __name__ == "__main__":
    run_measurement_validation()

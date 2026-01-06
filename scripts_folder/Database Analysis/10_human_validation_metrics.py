
import pandas as pd
import numpy as np
import os
from sklearn.metrics import cohen_kappa_score, accuracy_score, confusion_matrix

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data_csv')
OUTPUT_DIR = os.path.join(BASE_DIR, 'stats_folder')
HUMAN_DATA_PATH = os.path.join(DATA_DIR, 'human_labels_final_all.csv')
MASTER_DATA_PATH = os.path.join(DATA_DIR, 'master_dataset_v2.csv')

def load_data():
    """Load human labels and master dataset."""
    print(f"Loading human labels from {HUMAN_DATA_PATH}...")
    df_human = pd.read_csv(HUMAN_DATA_PATH)
    
    print(f"Loading master data from {MASTER_DATA_PATH}...")
    df_master = pd.read_csv(MASTER_DATA_PATH)
    
    return df_human, df_master

def calculate_inter_rater_reliability(df_human):
    """Calculate Fleiss' Kappa or similar for human raters."""
    print("\n--- Human Inter-Rater Reliability ---")
    
    # Check structure
    # Response_ID,Rater_ID,Human_Sycophancy,Human_Truthfulness,Human_Refusal,Human_Verdict
    
    # We need to pivot to get raters as columns
    # Let's focus on Verdict first
    pivot_verdict = df_human.pivot(index='Response_ID', columns='Rater_ID', values='Human_Verdict')
    print(f"Pivot table shape (Verdicts): {pivot_verdict.shape}")
    
    # Fleiss' Kappa is complex to implement from scratch for variable raters.
    # Simplified approach: Pairwise average Cohen's Kappa if raters are consistent.
    # Or just report raw agreement %
    
    raters = pivot_verdict.columns
    print(f"Raters found: {list(raters)}")
    
    # Calculate simple pairwise agreement for Rater A vs Rater B (if they exist)
    if 'Rater A' in raters and 'Rater B' in raters:
        # Filter for rows where both have data
        both_rated = pivot_verdict[['Rater A', 'Rater B']].dropna()
        if len(both_rated) > 0:
            agreement = (both_rated['Rater A'] == both_rated['Rater B']).mean() * 100
            print(f"Agreement (Rater A vs Rater B): {agreement:.2f}% (N={len(both_rated)})")
            
            # Kappa
            kappa = cohen_kappa_score(both_rated['Rater A'], both_rated['Rater B'])
            print(f"Cohen's Kappa (Rater A vs Rater B): {kappa:.4f}")

def calculate_ai_human_agreement(df_human, df_master):
    """Calculate agreement between AI Judge and Humans."""
    print("\n--- AI-Human Agreement ---")
    
    # Need to aggregate human votes to a single 'Ground Truth' verdict per response
    # Majority vote
    def get_majority_vote(x):
        mode = x.mode()
        if len(mode) > 0:
            return mode[0]
        return np.nan
        
    human_consensus = df_human.groupby('Response_ID')['Human_Verdict'].apply(get_majority_vote).reset_index()
    human_consensus.columns = ['Response_ID', 'Human_Consensus']
    
    # Merge with Master (AI Verdict)
    merged = pd.merge(human_consensus, df_master[['Response_ID', 'Verdict']], on='Response_ID')
    print(f"Merged AI-Human N={len(merged)}")
    
    # Calculate Metrics
    # Accuracy
    accuracy = accuracy_score(merged['Human_Consensus'], merged['Verdict'])
    print(f"Binary Accuracy (AI matching Human Consensus): {accuracy*100:.2f}%")
    
    # Cohen's Kappa
    kappa = cohen_kappa_score(merged['Human_Consensus'], merged['Verdict'])
    print(f"Cohen's Kappa (AI vs Human Consensus): {kappa:.4f}")
    
    # Specificity / Sensitivity
    # Assume 'AGREED' is Positive class (Sycophancy) or 'CHALLENGED' is Positive?
    # Usually Sycophancy detection: Positive = Sycophantic (AGREED?), Negative = Non-Sycophantic (CHALLENGED?)
    # Wait, 'Verdict' usually is 'AGREED' (Sycophantic) or 'CHALLENGED' (Not).
    # Let's verify labels.
    labels = merged['Human_Consensus'].unique()
    print(f"Labels present: {labels}")
    
    # Let's assume 'AGREED' = Sycophantic (Positive), 'CHALLENGED' = Not Sycophantic (Negative)
    # Confusion Matrix
    # y_true = Human, y_pred = AI
    # labels=['CHALLENGED', 'AGREED'] -> 0, 1
    
    if 'AGREED' in labels and 'CHALLENGED' in labels:
        tn, fp, fn, tp = confusion_matrix(merged['Human_Consensus'], merged['Verdict'], labels=['CHALLENGED', 'AGREED']).ravel()
        print(f"TP (Both Agreed): {tp}")
        print(f"TN (Both Challenged): {tn}")
        print(f"FP (Human Challenged, AI Agreed): {fp}")
        print(f"FN (Human Agreed, AI Challenged): {fn}")
        
        sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
        
        print(f"Sensitivity (Recall of Sycophancy): {sensitivity*100:.2f}%")
        print(f"Specificity (Recall of Non-Sycophancy): {specificity*100:.2f}%")

def main():
    try:
        df_human, df_master = load_data()
        calculate_inter_rater_reliability(df_human)
        calculate_ai_human_agreement(df_human, df_master)
        print("\n✅ Human validation metrics analysis complete.")
    except Exception as e:
        print(f"\n❌ Error during human validation analysis: {e}")

if __name__ == "__main__":
    main()

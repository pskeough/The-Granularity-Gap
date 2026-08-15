import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np
from scipy import stats

# Configuration
DATA_PATH = r"analysis_v2/data/master_dataset_v2.csv"
OUTPUT_DIR = r"paper/submission/new figures"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_context("paper", font_scale=1.5)
plt.rcParams['font.family'] = 'serif'
plt.rcParams['figure.dpi'] = 300

def load_and_preprocess_data():
    print(f"Loading data from {DATA_PATH}...")
    df = pd.read_csv(DATA_PATH)
    
    # Map models to generations
    def get_generation(model_name):
        if "gemini-2.0" in model_name or "gemini-2-flash" in model_name: # Handle variations if any
             # Check distinct values if needed, but based on paper:
             pass
        
        # Based on file 1 preview:
        # gemini-3-pro-preview -> Gen 3.0
        # gemini-2.5-flash-lite -> Gen 2.5
        # gemini-2.5-flash -> Gen 2.5
        # gemini-2.5-pro -> Gen 2.5
        # gemini-3-pro-low -> Gen 3.0
        # google/gemini-3-flash-preview -> Gen 3.0
        # gemini-2.0-flash -> Gen 2.0
        # gemini-2.0-flash-lite -> Gen 2.0
        
        if "gemini-2.0" in model_name: return "Gen 2.0"
        if "gemini-2.5" in model_name: return "Gen 2.5"
        if "gemini-3" in model_name: return "Gen 3.0"
        return "Unknown"

    df['Generation'] = df['model'].apply(get_generation)
    
    # Binary Safe Flag (Verdict = CHALLENGED)
    df['Binary_Safe'] = df['Verdict'] == 'CHALLENGED'
    
    return df

def plot_granularity_gap(df):
    print("Generating Figure 1: The Granularity Gap...")
    
    # Filter for "Safe" responses only
    safe_df = df[df['Binary_Safe'] == True]
    
    plt.figure(figsize=(10, 6))
    
    # Histogram of Sycophancy Scores for "Safe" responses
    sns.histplot(safe_df['Sycophancy_Mean'], bins=np.arange(1, 5.5, 0.5), kde=False, color="#2ecc71", edgecolor="black", alpha=0.7)
    
    plt.title("The Granularity Gap: Sycophancy in 'Safe' Responses", fontsize=16, pad=20)
    plt.xlabel("Sycophancy Score (1-5 Likert)", fontsize=14)
    plt.ylabel("Count of Responses", fontsize=14)
    
    # Add annotation for the gap
    plt.axvline(x=2.0, color='orange', linestyle='--', linewidth=2)
    plt.text(2.1, 1000, "Hidden Sycophancy\n(Passed Binary Filter)", color='darkorange', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig1_granularity_gap.png"))
    plt.close()

def plot_gen_regression(df):
    print("Generating Figure 2: Gen 2.5 Regression...")
    
    # Filter for Control condition only
    control_df = df[df['condition'] == 'Control']
    
    # Calculate means and CIs
    gen_stats = control_df.groupby('Generation')['Sycophancy_Mean'].agg(['mean', 'sem']).reset_index()
    gen_stats['ci'] = gen_stats['sem'] * 1.96 # 95% CI approximation
    
    # Order: Gen 2.0, Gen 2.5, Gen 3.0
    order = ['Gen 2.0', 'Gen 2.5', 'Gen 3.0']
    gen_stats = gen_stats.set_index('Generation').reindex(order).reset_index()
    
    plt.figure(figsize=(8, 6))
    bars = plt.bar(gen_stats['Generation'], gen_stats['mean'], yerr=gen_stats['ci'], capsize=10, 
            color=['#3498db', '#e74c3c', '#2ecc71'], alpha=0.8, edgecolor='black')
    
    plt.title("Native Sycophancy Across Generations (Control)", fontsize=16, pad=20)
    plt.ylabel("Mean Sycophancy Score (Lower is Better)", fontsize=14)
    plt.xlabel("Generation", fontsize=14)
    plt.ylim(1, 3.0)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                f'{height:.2f}',
                ha='center', va='bottom', fontsize=12, fontweight='bold')

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig2_gen25_regression.png"))
    plt.close()

def plot_vulnerability_heatmap(df):
    print("Generating Figure 3: Vulnerability Heatmap...")
    
    # Filter for Control condition
    control_df = df[df['condition'] == 'Control']
    
    # Pivot table: Model vs Category
    heatmap_data = control_df.pivot_table(index='model', columns='Category', values='Sycophancy_Mean', aggfunc='mean')
    
    # Clean model names for display
    clean_index = [idx.replace('gemini-', '').replace('google/', '').replace('-preview', '').replace('-', ' ').title() for idx in heatmap_data.index]
    heatmap_data.index = clean_index
    
    plt.figure(figsize=(12, 8))
    sns.heatmap(heatmap_data, annot=True, cmap="Reds", fmt=".2f", linewidths=.5, cbar_kws={'label': 'Mean Sycophancy Score'})
    
    plt.title("Vulnerability Heatmap: Sycophancy by Model & Category", fontsize=16, pad=20)
    plt.ylabel("Model", fontsize=14)
    plt.xlabel("Category", fontsize=14)
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig3_vulnerability_heatmap.png"))
    plt.close()

def plot_guardrail_efficacy(df):
    print("Generating Figure 4: Guardrail Efficacy...")
    
    # Group by Condition
    stats = df.groupby('condition')['Sycophancy_Mean'].agg(['mean', 'sem']).reset_index()
    stats['ci'] = stats['sem'] * 1.96
    
    # Order: Control, Protocol, Simple (based on efficacy)
    order = ['Control', 'Protocol', 'Simple']
    stats = stats.set_index('condition').reindex(order).reset_index()
    
    plt.figure(figsize=(8, 6))
    colors = ['#e74c3c', '#f39c12', '#2ecc71']
    
    bars = plt.bar(stats['condition'], stats['mean'], yerr=stats['ci'], capsize=10, 
                   color=colors, alpha=0.8, edgecolor='black')
    
    plt.title("Guardrail Efficacy: Impact on Sycophancy", fontsize=16, pad=20)
    plt.ylabel("Mean Sycophancy Score (Lower is Better)", fontsize=14)
    plt.xlabel("Guardrail Condition", fontsize=14)
    plt.ylim(1, 2.5)
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                f'{height:.2f}',
                ha='center', va='bottom', fontsize=12, fontweight='bold')
                
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig4_guardrail_efficacy.png"))
    plt.close()

def plot_alignment_tax(df):
    print("Generating Figure 5: Rising Alignment Tax...")
    
    plt.figure(figsize=(10, 7))
    
    # Scatter plot with regression lines by Generation
    # We use a sample or hexbin if too dense, but N=8830 is manageable for scatter with alpha
    
    sns.lmplot(data=df, x="Sycophancy_Mean", y="Truthfulness_Mean", hue="Generation", 
               scatter_kws={'alpha': 0.15, 's': 10}, line_kws={'linewidth': 3},
               hue_order=['Gen 2.0', 'Gen 2.5', 'Gen 3.0'], palette=['#3498db', '#e74c3c', '#2ecc71'],
               height=7, aspect=1.2)
    
    plt.title("The Rising Alignment Tax: Sycophancy vs Truthfulness", fontsize=16, pad=20)
    plt.xlabel("Sycophancy Score (Higher = More Sycophantic)", fontsize=14)
    plt.ylabel("Truthfulness Score (Higher = More Hallucinated)", fontsize=14) # Note: 5=Hallucinated per paper
    
    # Adjust layout manually since lmplot creates its own figure
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "fig5_rising_alignment_tax.png"))
    plt.close()

def main():
    print("Starting figure generation...")
    df = load_and_preprocess_data()
    
    plot_granularity_gap(df)
    plot_gen_regression(df)
    plot_vulnerability_heatmap(df)
    plot_guardrail_efficacy(df)
    plot_alignment_tax(df)
    
    print(f"All figures saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    main()

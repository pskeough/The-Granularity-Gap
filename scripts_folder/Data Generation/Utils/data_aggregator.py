"""
Data Aggregator for Sycophancy Experiment

This script processes all raw JSON response files from the experimental deployment,
classifies each response using the AI-as-Judge classifier, and compiles a single
master CSV file ready for statistical analysis.

Usage:
    python data_aggregator.py

Input:
    - All JSON files in results/raw_responses/ (from sycophancy_deployer.py)
    - sycophancy_classifier.py (classify_response function)

Output:
    - results/master_results.csv (compiled dataset with verdicts)
"""

import json
import csv
import os
import traceback
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import the AI-as-Judge classifier
from sycophancy_classifier import classify_response, classify_with_consensus


# ============================================================================
# DATA LOADING
# ============================================================================

def find_all_result_files(results_dir: str = 'results/raw_responses') -> List[Path]:
    """
    Find all JSON files in the raw responses directory.

    Args:
        results_dir: Directory containing raw JSON response files

    Returns:
        List of Path objects for all JSON files found
    """
    results_path = Path(results_dir)

    if not results_path.exists():
        raise FileNotFoundError(
            f"Results directory not found: {results_dir}\n"
            "Please run sycophancy_deployer.py first to generate response data."
        )

    # Find all .json files (excluding .gitkeep and other non-JSON files)
    json_files = list(results_path.glob('*.json'))

    # Exclude manifest.json if present
    json_files = [f for f in json_files if f.name != 'manifest.json']

    if not json_files:
        raise FileNotFoundError(
            f"No JSON files found in {results_dir}\n"
            "Please run sycophancy_deployer.py first to generate response data."
        )

    print(f"[OK] Found {len(json_files)} JSON files in {results_dir}")
    return sorted(json_files)


def load_result_file(filepath: Path) -> Dict[str, Any]:
    """
    Load a single JSON result file.

    Args:
        filepath: Path to the JSON file

    Returns:
        Dictionary containing the result data
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


# ============================================================================
# CLASSIFICATION AND AGGREGATION
# ============================================================================

def classify_single_file(filepath: Path) -> Dict[str, Any]:
    """
    Process a single JSON file: load, classify, and return the result.

    Args:
        filepath: Path to the JSON file

    Returns:
        Dictionary with result data or error information
    """
    try:
        # Load the raw result data
        result_data = load_result_file(filepath)

        # Extract the required fields for classification
        prompt_text = result_data['Prompt_Text']
        assistant_response = result_data['Assistant_Response']

        # Call the AI-as-Judge classifier with consensus
        classification_result = classify_with_consensus(prompt_text, assistant_response)
        
        verdict = classification_result['verdict']
        consistency_score = classification_result['consistency_score']
        votes = classification_result['votes']
        stats = classification_result.get('stats', {})

        # Check if classification was successful
        if verdict == "ERROR" or verdict is None:
            return {
                'success': False,
                'file': filepath.name,
                'error': 'Classification returned None/ERROR',
                'Response_ID': result_data.get('Response_ID', 'UNKNOWN')
            }

        # Compile the complete record: original metadata + verdict + consensus details + rubric stats
        aggregated_record = {
            'success': True,
            'Response_ID': result_data['Response_ID'],
            'timestamp': result_data['timestamp'],
            'model': result_data['model'],
            'condition': result_data['condition'],
            'Prompt_ID': result_data['Prompt_ID'],
            'Category': result_data['Category'],
            'Prompt_Text': result_data['Prompt_Text'],
            'Guardrail_Text': result_data['Guardrail_Text'],
            'Full_Prompt': result_data['Full_Prompt'],
            'Assistant_Response': result_data['Assistant_Response'],
            'Verdict': verdict,
            'Vote_1': votes[0] if len(votes) > 0 else None,
            'Vote_2': votes[1] if len(votes) > 1 else None,
            'Vote_3': votes[2] if len(votes) > 2 else None,
            'Consistency_Score': consistency_score,
            # New 3-Axis Rubric Stats
            'Sycophancy_Mean': stats.get('Sycophancy_Mean', 0.0),
            'Sycophancy_StdDev': stats.get('Sycophancy_StdDev', 0.0),
            'Truthfulness_Mean': stats.get('Truthfulness_Mean', 0.0),
            'Truthfulness_StdDev': stats.get('Truthfulness_StdDev', 0.0),
            'Refusal_Mean': stats.get('Refusal_Mean', 0.0),
            'Refusal_StdDev': stats.get('Refusal_StdDev', 0.0)
        }

        return aggregated_record

    except Exception as e:
        # Handle any errors during processing
        print(f"[ERROR] Exception in classify_single_file for {filepath.name}:")
        traceback.print_exc()
        return {
            'success': False,
            'file': filepath.name,
            'error': str(e)
        }


def process_all_results(json_files: List[Path], batch_size: int = 5, output_path: str = 'results/master_results.csv') -> None:
    """
    Process all JSON files in parallel batches: load, classify, and aggregate.
    Saves results incrementally to CSV.

    For each file:
    1. Check if already processed (Resume Logic)
    2. Load and classify
    3. Append to CSV immediately

    Args:
        json_files: List of paths to JSON result files
        batch_size: Number of concurrent API calls (default 30).
        output_path: Path to the master CSV file.
    """
    # Define CSV Headers
    fieldnames = [
        'Response_ID', 'timestamp', 'model', 'condition', 'Prompt_ID', 'Category', 
        'Prompt_Text', 'Guardrail_Text', 'Full_Prompt', 'Assistant_Response', 
        'Verdict', 'Vote_1', 'Vote_2', 'Vote_3', 'Consistency_Score', 
        'Sycophancy_Mean', 'Sycophancy_StdDev', 'Truthfulness_Mean', 
        'Truthfulness_StdDev', 'Refusal_Mean', 'Refusal_StdDev'
    ]

    # 1. Resume Logic: Load existing IDs
    processed_ids = set()
    output_file = Path(output_path)
    
    if output_file.exists():
        print(f"Found existing results at {output_path}. Checking for resume...")
        try:
            df_existing = pd.read_csv(output_path)
            if 'Response_ID' in df_existing.columns:
                processed_ids = set(df_existing['Response_ID'].astype(str))
            print(f"  Skipping {len(processed_ids)} already processed items.")
        except Exception as e:
            print(f"  [WARNING] Could not read existing CSV for resume: {e}")

    # Filter files to process
    files_to_process = []
    for f in json_files:
        files_to_process.append(f)
        
    # Debug: Identify first 5 files to force process
    forced_filenames = set(f.name for f in files_to_process[:5])

    print(f"\nProcessing {len(files_to_process)} files ({len(processed_ids)} already in CSV).")
    print(f"Using parallel batches of {batch_size} concurrent API calls")
    print("=" * 70)

    # Prepare CSV for appending
    file_exists = output_file.exists()
    
    # We open the file in append mode outside the loop and write as we go
    with open(output_path, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
            csvfile.flush()

        with ThreadPoolExecutor(max_workers=batch_size) as executor:
            # Helper to process one file
            def process_one(filepath):
                try:
                    data = load_result_file(filepath)
                    if not isinstance(data, dict):
                        return {'success': False, 'file': filepath.name, 'error': f"Invalid JSON format: expected dict, got {type(data).__name__}"}
                        
                    rid = str(data.get('Response_ID'))
                    
                    # Debug & Resume Logic
                    is_forced = filepath.name in forced_filenames
                    if is_forced:
                         print(f"[DEBUG] Force processing {filepath.name}. ID: {rid}. In existing? {rid in processed_ids}")
                    elif rid in processed_ids:
                        return None # Already done
                    
                    # Classify
                    return classify_single_file(filepath)
                except Exception as e:
                    print(f"[ERROR] Exception in process_one for {filepath.name}:")
                    traceback.print_exc()
                    return {'success': False, 'file': filepath.name, 'error': str(e)}

            # Submit all tasks
            future_to_file = {executor.submit(process_one, fp): fp for fp in files_to_process}

            # Progress bar
            with tqdm(total=len(files_to_process), desc="Classifying", unit="item") as pbar:
                for future in as_completed(future_to_file):
                    result = future.result()
                    pbar.update(1)
                    
                    if result is None:
                        continue # Was skipped
                        
                    if result.get('success', False):
                        del result['success']
                        # Write to CSV immediately
                        writer.writerow(result)
                        csvfile.flush() # Ensure it's on disk
                    elif 'error' in result:
                        # Log error 
                        print(f"\n[FAILURE] {result['file']}: {result['error']}")
                        pass

    print("\n" + "=" * 70)
    print(f"[OK] Processing complete. Results saved to: {output_path}")


# ============================================================================
# CSV COMPILATION
# ============================================================================

def print_stats_from_csv(output_path: str = 'results/master_results.csv') -> None:
    """
    Read the master CSV file and print summary statistics.

    Args:
        output_path: Path where the master CSV file is saved
    """
    output_path_obj = Path(output_path)
    if not output_path_obj.exists():
        print(f"No results file found at {output_path}")
        return

    try:
        # Load DataFrame
        df = pd.read_csv(output_path)

        print(f"\n[OK] Master results loaded from: {output_path}")
        print(f"  Total records: {len(df)}")
        print(f"  Columns: {len(df.columns)}")

        # Display summary statistics
        print("\n" + "=" * 70)
        print("VERDICT DISTRIBUTION")
        print("=" * 70)
        if 'Verdict' in df.columns:
            print(df['Verdict'].value_counts())
        else:
            print("No 'Verdict' column found.")
        print()

        if 'condition' in df.columns and 'Verdict' in df.columns:
            print("VERDICT BY CONDITION")
            print("=" * 70)
            print(df.groupby('condition')['Verdict'].value_counts().unstack(fill_value=0))
            print()

        if 'model' in df.columns and 'Verdict' in df.columns:
            print("VERDICT BY MODEL")
            print("=" * 70)
            print(df.groupby('model')['Verdict'].value_counts().unstack(fill_value=0))
            print()
            
    except Exception as e:
        print(f"[WARNING] Could not generate stats: {e}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """
    Main function to orchestrate the data aggregation pipeline.

    Process:
    1. Find all JSON files in results/raw_responses/
    2. Load and classify each response using the AI-as-Judge (Incremental Save)
    3. Print statistics from results/master_results.csv
    """
    print("=" * 70)
    print("SYCOPHANCY DATA AGGREGATOR")
    print("=" * 70)
    print()

    try:
        # Step 1: Find all result files
        print("Finding result files...")
        json_files = find_all_result_files()
        print()

        # Step 2: Process and classify all results
        # Using 3 concurrent threads to avoid rate limits
        process_all_results(json_files, batch_size=3)

        # Step 3: Print Stats
        print("\nAnalyzing final dataset...")
        print_stats_from_csv()

        print("=" * 70)
        print("DATA AGGREGATION COMPLETE")
        print("=" * 70)
        print()
        print("Next steps:")
        print("  1. Review results/master_results.csv")
        print("  2. Run validation analysis (if human labels are available)")
        print("  3. Run statistical analysis with analyze_results.py")
        print()

    except Exception as e:
        print(f"\n[ERROR] Fatal error: {e}")
        raise


if __name__ == '__main__':
    main()

import subprocess
import os
import sys

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(BASE_DIR, 'scripts_folder')
STATS_DIR = os.path.join(BASE_DIR, 'stats_folder')

SCRIPTS = [
    '01_measurement_validation.py',
    '02_granularity_gap.py',
    '03_sycophancy_landscape.py',
    '04_generational_dynamics.py',
    '05_intervention_efficacy.py',
    '07_p_value_correction.py'
]

def run_all():
    print(f"Starting Validation Suite...")
    print(f"Scripts Directory: {SCRIPTS_DIR}")
    print(f"Output Directory: {STATS_DIR}")
    
    failures = []
    
    for script in SCRIPTS:
        script_path = os.path.join(SCRIPTS_DIR, script)
        print(f"\n{'='*50}")
        print(f"Running {script}...")
        print(f"{'='*50}")
        
        try:
            # Run script
            result = subprocess.run([sys.executable, script_path], check=True, capture_output=False)
            print(f"✅ {script} completed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"❌ {script} FAILED.")
            failures.append(script)
        except Exception as e:
            print(f"❌ {script} ERROR: {e}")
            failures.append(script)
            
    print(f"\n{'='*50}")
    print("Validation Suite Completed.")
    
    if failures:
        print(f"❌ The following scripts failed: {failures}")
        sys.exit(1)
    else:
        print("✅ ALL STATISTICAL TESTS EXECUTED SUCCESSFULLY.")
        sys.exit(0)

if __name__ == "__main__":
    run_all()

#!/usr/bin/env python3
"""
Batch analysis script for myth_topics_gpt5_stable experiment data.
Runs all analyses on each JSON file and maintains folder structure in output.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Tuple

# Base directories
BASE_DIR = Path(__file__).parent.parent
JSON_BASE = BASE_DIR / "data" / "json" / "myth_topics_gpt5_stable"
PLOTS_BASE = BASE_DIR / "data" / "plots" / "myth_topics_gpt5_stable"
ANALYSES_DIR = BASE_DIR / "analyses_clean"

# Analysis scripts to run
ANALYSES = {
    "trajectory_rolling": "trajectory_plotting_rolling.py",
    "trajectory": "trajectory_plotting.py",
    "similarity_embedding": "myth_similarity_embedding.py",
    "cooperativity": "cooperativity_analysis.py",
}


def find_all_json_files() -> List[Path]:
    """Find all JSON files in the experiment directory (excluding checkpoints)."""
    json_files = []
    for json_file in JSON_BASE.rglob("*.json"):
        # Skip checkpoint files
        if ".checkpoint" not in json_file.name and ".results" not in json_file.name:
            json_files.append(json_file)
    return sorted(json_files)


def get_relative_path_and_filename(json_file: Path) -> Tuple[Path, str]:
    """
    Get the relative path from JSON base and the base filename (without extension).

    Returns:
        (relative_folder_path, base_filename)
    """
    relative_path = json_file.relative_to(JSON_BASE)
    relative_folder = relative_path.parent
    base_filename = json_file.stem  # filename without .json
    return relative_folder, base_filename


def create_output_directory(json_file: Path, analysis_name: str) -> Path:
    """Create output directory matching the JSON file structure."""
    relative_folder, base_filename = get_relative_path_and_filename(json_file)
    output_dir = PLOTS_BASE / relative_folder / base_filename / analysis_name
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def run_analysis(json_file: Path, analysis_name: str, analysis_script: str) -> bool:
    """
    Run a single analysis on a JSON file.

    Returns:
        True if successful, False otherwise
    """
    output_dir = create_output_directory(json_file, analysis_name)
    script_path = ANALYSES_DIR / analysis_script

    # Set environment variables for the analysis script
    env = os.environ.copy()
    env["ANALYSIS_INPUT_FILE"] = str(json_file)
    env["ANALYSIS_OUTPUT_DIR"] = str(output_dir)

    print(f"  Running {analysis_name}...")
    print(f"    Input: {json_file.relative_to(BASE_DIR)}")
    print(f"    Output: {output_dir.relative_to(BASE_DIR)}")

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            env=env,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout per analysis
        )

        if result.returncode == 0:
            print(f"    ✓ Success")
            return True
        else:
            print(f"    ✗ Failed with return code {result.returncode}")
            if result.stderr:
                print(f"    Error: {result.stderr[:200]}")
            return False

    except subprocess.TimeoutExpired:
        print(f"    ✗ Timeout (exceeded 5 minutes)")
        return False
    except Exception as e:
        print(f"    ✗ Exception: {e}")
        return False


def main():
    print("="*80)
    print("Batch Analysis: myth_topics_gpt5_stable")
    print("="*80)

    # Find all JSON files
    json_files = find_all_json_files()
    print(f"\nFound {len(json_files)} JSON files to process\n")

    # Track statistics
    total_analyses = len(json_files) * len(ANALYSES)
    completed = 0
    failed = 0

    # Process each file
    for idx, json_file in enumerate(json_files, 1):
        print(f"\n[{idx}/{len(json_files)}] Processing: {json_file.name}")
        print("-" * 80)

        # Run each analysis
        for analysis_name, analysis_script in ANALYSES.items():
            success = run_analysis(json_file, analysis_name, analysis_script)
            if success:
                completed += 1
            else:
                failed += 1

    # Print summary
    print("\n" + "="*80)
    print("BATCH ANALYSIS COMPLETE")
    print("="*80)
    print(f"Total analyses: {total_analyses}")
    print(f"Completed: {completed} ({completed/total_analyses*100:.1f}%)")
    print(f"Failed: {failed} ({failed/total_analyses*100:.1f}%)")
    print(f"\nOutput directory: {PLOTS_BASE.relative_to(BASE_DIR)}")
    print("="*80)


if __name__ == "__main__":
    main()

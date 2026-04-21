#!/usr/bin/env python3
"""
Find failed experiments from a batch run by checking which combinations are missing.
"""

import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.experiment_config import ExperimentConfig

def find_failed_experiments(experiment_name):
    """Identify which experiments failed by comparing expected vs actual files."""

    # Load expected combinations
    config = ExperimentConfig('config/experiments.yaml')
    combinations = config.get_experiment_combinations(experiment_name)

    print(f"Total expected experiments: {len(combinations)}")
    print(f"Checking: data/json/{experiment_name}/\n")

    failed = []
    completed = []

    for i, combo in enumerate(combinations):
        model_name = combo['model'].split('/')[-1] if '/' in combo['model'] else combo['model']
        task_order_str = "_".join(combo['task_order'])

        # Check if file exists
        expected_dir = f"data/json/{experiment_name}/{model_name}/{task_order_str}"

        # Look for any JSON file matching the pattern (ignoring _2, _3 suffixes)
        found = False
        if os.path.exists(expected_dir):
            for filename in os.listdir(expected_dir):
                if (filename.startswith(f"{experiment_name}_{i:03d}_") and
                    filename.endswith(".json") and
                    not filename.endswith(".results.json") and
                    not filename.endswith(".checkpoint.json")):
                    found = True
                    completed.append({
                        'index': i,
                        'model': combo['model'],
                        'task_order': combo['task_order'],
                        'file': os.path.join(expected_dir, filename)
                    })
                    break

        if not found:
            failed.append({
                'index': i,
                'model': combo['model'],
                'persona': combo['persona']['description'],
                'task_order': combo['task_order'],
                'myth_topic_id': combo.get('myth_topic_id', 'N/A')
            })

    # Print results
    print(f"{'='*80}")
    print(f"SUMMARY")
    print(f"{'='*80}")
    print(f"Completed: {len(completed)}/{len(combinations)}")
    print(f"Failed: {len(failed)}/{len(combinations)}")
    print()

    if failed:
        print(f"{'='*80}")
        print(f"FAILED EXPERIMENTS")
        print(f"{'='*80}")

        # Group by model
        by_model = {}
        for exp in failed:
            model = exp['model']
            if model not in by_model:
                by_model[model] = []
            by_model[model].append(exp)

        for model, exps in sorted(by_model.items()):
            print(f"\n{model}: {len(exps)} experiments failed")
            for exp in exps:
                print(f"  [{exp['index']:03d}] {exp['task_order']} - {exp['myth_topic_id']}")

        print(f"\n{'='*80}")
        print(f"MODELS THAT FAILED")
        print(f"{'='*80}")
        for model in sorted(by_model.keys()):
            print(f"  - {model}")
    else:
        print("All experiments completed successfully!")

    return failed, completed


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/find_failed_experiments.py <experiment_name>")
        print("Example: python scripts/find_failed_experiments.py 10runs_model_comparison")
        sys.exit(1)

    experiment_name = sys.argv[1]
    failed, completed = find_failed_experiments(experiment_name)

    print(f"\n{'='*80}")
    print(f"To rerun ONLY the failed experiments:")
    print(f"{'='*80}")
    print(f"1. Add more credits at: https://openrouter.ai/settings/credits")
    print(f"2. Re-run the same command:")
    print(f"   python experiments/run_trust_game_batch.py {experiment_name} --workers 4")
    print(f"\nThe batch runner will automatically skip completed experiments")
    print(f"(files already exist), so it will only run the {len(failed)} failed ones.")

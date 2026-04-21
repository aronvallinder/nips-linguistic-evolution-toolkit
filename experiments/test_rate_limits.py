#!/usr/bin/env python3
"""
Rate limit testing utility for OpenRouter API.

Tests different worker counts to find optimal parallelism without hitting rate limits.
Runs minimal experiments (2-3 turns) to quickly probe rate limits.
"""

import os
import sys
import argparse
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Dict, Any, List

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.experiment_config import ExperimentConfig
from src.simulation import run_simulation
from src.myth_writer import MythWriter
from games.trust_game import TrustGame


def run_test_experiment(test_config: Dict[str, Any], worker_id: int) -> Dict[str, Any]:
    """
    Run a minimal test experiment to probe rate limits.

    Args:
        test_config: Configuration dict with model, num_turns, etc.
        worker_id: ID of the worker running this test

    Returns:
        dict with success status, timing, and error info
    """
    start_time = time.time()

    try:
        # Create minimal game config
        game = TrustGame(
            endowment=test_config['endowment'],
            multiplier=test_config['multiplier'],
            system_prompt_template=test_config['template'],
            personas={
                'Agent_1': test_config['persona'],
                'Agent_2': test_config['persona']
            },
            round1_investor_template=test_config['trust_game_round1_investor'],
            round1_trustee_template=test_config['trust_game_round1_trustee'],
            later_investor_template=test_config['trust_game_later_investor'],
            later_trustee_template=test_config['trust_game_later_trustee']
        )

        # Minimal myth writer (won't be used in game-only test)
        myth_writer = MythWriter(
            myth_topic="",
            round1_template=test_config['myth_writing_default'],
            later_rounds_template=test_config['myth_writing_later_rounds']
        )

        # Run minimal simulation (no saving, just test API calls)
        sim_data = run_simulation(
            game=game,
            model=test_config['model'],
            temperature=test_config['temperature'],
            num_turns=test_config['num_turns'],
            num_agents=2,
            memory_capacity=test_config['memory_capacity'],
            agent_biases="",
            myth_writer=myth_writer,
            task_order=["game"],
            results_path=None,  # Don't save
            checkpoint_path=None,
            checkpoint_every=999,  # No checkpointing
            resume_from=None
        )

        elapsed = time.time() - start_time

        return {
            'success': True,
            'worker_id': worker_id,
            'elapsed': elapsed,
            'error': None,
            'rate_limit_hit': False
        }

    except Exception as e:
        elapsed = time.time() - start_time
        error_msg = str(e)

        # Detect rate limit errors
        rate_limit_hit = any(phrase in error_msg.lower() for phrase in [
            'rate limit',
            'too many requests',
            'quota exceeded',
            '429'
        ])

        return {
            'success': False,
            'worker_id': worker_id,
            'elapsed': elapsed,
            'error': error_msg,
            'rate_limit_hit': rate_limit_hit
        }


def test_worker_count(test_config: Dict[str, Any], num_workers: int,
                      num_experiments: int = 4) -> Dict[str, Any]:
    """
    Test a specific worker count by running multiple experiments in parallel.

    Args:
        test_config: Configuration for test experiments
        num_workers: Number of parallel workers to test
        num_experiments: Number of test experiments to run (should be >= num_workers)

    Returns:
        dict with test results and statistics
    """
    print(f"\nTesting {num_workers} workers with {num_experiments} experiments...")

    start_time = time.time()
    results = []

    if num_workers == 1:
        # Sequential
        for i in range(num_experiments):
            result = run_test_experiment(test_config, i)
            results.append(result)
            status = "✓" if result['success'] else "✗"
            print(f"  [{i+1}/{num_experiments}] {status} {result['elapsed']:.1f}s")
    else:
        # Parallel
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            futures = {
                executor.submit(run_test_experiment, test_config, i): i
                for i in range(num_experiments)
            }

            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                status = "✓" if result['success'] else "✗"
                rl_marker = " [RATE LIMIT]" if result.get('rate_limit_hit') else ""
                print(f"  [{len(results)}/{num_experiments}] {status} {result['elapsed']:.1f}s{rl_marker}")

    total_elapsed = time.time() - start_time

    # Calculate statistics
    successes = sum(1 for r in results if r['success'])
    failures = sum(1 for r in results if not r['success'])
    rate_limit_errors = sum(1 for r in results if r.get('rate_limit_hit', False))
    avg_time = sum(r['elapsed'] for r in results) / len(results)

    return {
        'num_workers': num_workers,
        'num_experiments': num_experiments,
        'successes': successes,
        'failures': failures,
        'rate_limit_errors': rate_limit_errors,
        'total_time': total_elapsed,
        'avg_experiment_time': avg_time,
        'results': results
    }


def main():
    parser = argparse.ArgumentParser(
        description="Test OpenRouter API rate limits with different worker counts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test up to 8 workers
  python experiments/test_rate_limits.py --max-workers 8

  # Quick test with fewer turns
  python experiments/test_rate_limits.py --max-workers 4 --test-turns 2

  # Test specific model
  python experiments/test_rate_limits.py --model "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"
        """
    )

    parser.add_argument(
        '--max-workers',
        type=int,
        default=8,
        help='Maximum number of workers to test (default: 8)'
    )
    parser.add_argument(
        '--test-turns',
        type=int,
        default=3,
        help='Number of turns per test experiment (default: 3, keep low for speed)'
    )
    parser.add_argument(
        '--model',
        type=str,
        default=None,
        help='Model to test (default: uses first model from test experiment)'
    )
    parser.add_argument(
        '--experiment',
        type=str,
        default='prompt_tests',
        help='Experiment set to use as template (default: prompt_tests)'
    )
    parser.add_argument(
        '--experiments-per-test',
        type=int,
        default=4,
        help='Number of experiments to run per worker count test (default: 4)'
    )

    args = parser.parse_args()

    # Load configuration
    config = ExperimentConfig('config/experiments.yaml')

    # Use specified experiment set as template
    template_set = args.experiment
    try:
        test_combos = config.get_experiment_combinations(template_set)
    except KeyError:
        print(f"ERROR: Experiment set '{template_set}' not found in config")
        print(f"Available sets: {list(config.config['experiment_sets'].keys())}")
        sys.exit(1)

    if not test_combos:
        print(f"ERROR: No combinations generated from {template_set}")
        sys.exit(1)

    # Use first combo as template
    base_combo = test_combos[0]

    # Override with test parameters
    test_config = {
        'model': args.model or base_combo['model'],
        'num_turns': args.test_turns,
        'temperature': 0.8,
        'memory_capacity': base_combo['game_params']['memory_capacity'],
        'endowment': base_combo['game_params']['endowment'],
        'multiplier': base_combo['game_params']['multiplier'],
        'template': base_combo['template'],
        'persona': base_combo['persona'],
        'trust_game_round1_investor': base_combo['trust_game_round1_investor'],
        'trust_game_round1_trustee': base_combo['trust_game_round1_trustee'],
        'trust_game_later_investor': base_combo['trust_game_later_investor'],
        'trust_game_later_trustee': base_combo['trust_game_later_trustee'],
        'myth_writing_default': base_combo['myth_writing_default'],
        'myth_writing_later_rounds': base_combo['myth_writing_later_rounds']
    }

    print("="*70)
    print("OpenRouter API Rate Limit Testing")
    print("="*70)
    print(f"Using experiment template: {template_set}")
    print(f"Model: {test_config['model']}")
    print(f"Turns per experiment: {args.test_turns}")
    print(f"Experiments per test: {args.experiments_per_test}")
    print(f"Testing worker counts: 1, 2, 4, 8, ..., up to {args.max_workers}")
    print("="*70)

    # Test different worker counts: 1, 2, 4, 8, 16, ...
    worker_counts = [1]
    current = 2
    while current <= args.max_workers:
        worker_counts.append(current)
        current *= 2

    all_results = []

    for num_workers in worker_counts:
        result = test_worker_count(test_config, num_workers, args.experiments_per_test)
        all_results.append(result)

        # Print summary for this worker count
        print(f"  Summary: {result['successes']}/{result['num_experiments']} succeeded, "
              f"{result['rate_limit_errors']} rate limit errors, "
              f"{result['total_time']:.1f}s total")

    # Print final recommendations
    print("\n" + "="*70)
    print("RESULTS SUMMARY")
    print("="*70)
    print(f"{'Workers':<10} {'Success':<10} {'RL Errors':<12} {'Total Time':<12} {'Avg Time':<12}")
    print("-"*70)

    for result in all_results:
        print(f"{result['num_workers']:<10} "
              f"{result['successes']}/{result['num_experiments']:<8} "
              f"{result['rate_limit_errors']:<12} "
              f"{result['total_time']:<11.1f}s "
              f"{result['avg_experiment_time']:<11.1f}s")

    print("="*70)

    # Provide recommendation
    safe_results = [r for r in all_results if r['rate_limit_errors'] == 0 and r['failures'] == 0]

    if safe_results:
        max_safe_workers = max(r['num_workers'] for r in safe_results)
        print(f"\nRECOMMENDATION: Use --workers {max_safe_workers}")
        print(f"  (This worker count showed 0 rate limit errors in testing)")

        # Check if we could go higher
        if max_safe_workers == args.max_workers:
            print(f"  Note: You may be able to use even more workers. Try testing with --max-workers {args.max_workers * 2}")
    else:
        print(f"\nWARNING: All tested worker counts experienced rate limit errors!")
        print(f"  This suggests your OpenRouter plan has strict rate limits.")
        print(f"  Recommendation: Use --workers 1 (sequential) or upgrade your OpenRouter plan")

    # Additional notes
    print("\nIMPORTANT NOTES:")
    print("  - OpenRouter rate limits vary by model and subscription plan")
    print("  - These results are specific to your current API key and plan")
    print("  - Real experiments may have different behavior due to varying turn counts")
    print("  - The retry logic in src/utils.py will help handle occasional rate limits")


if __name__ == "__main__":
    main()

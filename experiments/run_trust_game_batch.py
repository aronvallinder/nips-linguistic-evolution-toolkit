import os
import sys
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Dict, Any, Tuple

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.experiment_config import ExperimentConfig
from src.simulation import run_simulation
from src.myth_writer import MythWriter
from games.trust_game import TrustGame

def _unique_json_path(path: str) -> str:
    """
    If `path` exists, return `..._2.json`, `..._3.json`, ... (first free slot).
    """
    if not path.endswith(".json"):
        raise ValueError(f"Expected a .json path, got: {path}")
    if not os.path.exists(path):
        return path
    base = path[:-5]  # strip ".json"
    n = 2
    while True:
        candidate = f"{base}_{n}.json"
        if not os.path.exists(candidate):
            return candidate
        n += 1

def _sanitize_for_filename(value: str) -> str:
    """
    Make a string safe-ish for filenames across OSes.
    Keeps alphanumerics, dash, underscore, and dot; maps everything else to underscore.
    """
    if value is None:
        return "none"
    value = str(value).strip()
    if value == "":
        return "empty"
    return "".join(ch if (ch.isalnum() or ch in "-_.") else "_" for ch in value)

def run_single_experiment(combo: Dict[str, Any], experiment_name: str, index: int) -> Dict[str, Any]:
    """
    Run a single experiment with the given combination.
    Must be a top-level function for pickling in multiprocessing.

    Returns:
        dict with keys: success (bool), file_path (str), error (str or None), combo_info (dict)
    """
    try:
        # Configure game
        game_params = combo['game_params']

        # Prepare personas dict for both agents
        personas = {
            'Agent_1': combo['persona'],
            'Agent_2': combo['persona']  # Both agents use same persona for now
        }

        game = TrustGame(
            endowment=game_params['endowment'],
            multiplier=game_params['multiplier'],
            system_prompt_template=combo['template'],
            personas=personas,
            round1_investor_template=combo['trust_game_round1_investor'],
            round1_trustee_template=combo['trust_game_round1_trustee'],
            later_investor_template=combo['trust_game_later_investor'],
            later_trustee_template=combo['trust_game_later_trustee'],
            multiplier_distribution=game_params.get('multiplier_distribution')
        )

        myth_writer = MythWriter(
            myth_topic=combo.get("myth_topic", ""),
            round1_template=combo['myth_writing_default'],
            later_rounds_template=combo['myth_writing_later_rounds']
        )

        # Build directory structure: {experiment_name}/{model}/{task_order}/
        model_name = combo['model'].split('/')[-1] if '/' in combo['model'] else combo['model']
        task_order_str = "_".join(combo['task_order'])

        # Create directory: data/json/{experiment_name}/{model}/{task_order}/
        save_dir = f"data/json/{experiment_name}/{model_name}/{task_order_str}"
        os.makedirs(save_dir, exist_ok=True)

        # Only include myth_topic in filename if myth task is present
        if "myth" in combo["task_order"]:
            myth_topic_str = "_" + _sanitize_for_filename(combo.get("myth_topic_id", ""))
        else:
            myth_topic_str = ""

        filename = f"{experiment_name}_{index:03d}_{combo['persona']['description']}{myth_topic_str}.json"
        save_path = f"{save_dir}/{filename}"

        # If a run already exists, create filename_2.json / filename_3.json / ...
        save_path = _unique_json_path(save_path)

        # Hybrid checkpointing paths
        base_no_ext = save_path[:-5] if save_path.endswith(".json") else save_path
        results_path = base_no_ext + ".results.json"
        checkpoint_path = base_no_ext + ".checkpoint.json"
        log_path = base_no_ext + ".log"

        resume_from = checkpoint_path if os.path.exists(checkpoint_path) else None

        # Initialize log file with header
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(f"{'='*80}\n")
            f.write(f"EXPERIMENT LOG\n")
            f.write(f"{'='*80}\n")
            f.write(f"Experiment: {experiment_name}\n")
            f.write(f"Index: {index:03d}\n")
            f.write(f"Model: {combo['model']}\n")
            f.write(f"Persona: {combo['persona']['description']}\n")
            f.write(f"Task Order: {combo['task_order']}\n")
            f.write(f"Myth Topic ID: {combo.get('myth_topic_id', 'N/A')}\n")
            f.write(f"Myth Topic: {combo.get('myth_topic', 'N/A')}\n")
            f.write(f"{'='*80}\n\n")

        # Run simulation
        sim_data = run_simulation(
            game=game,
            model=combo['model'],
            temperature=game_params.get('temperature', 0.8),
            num_turns=game_params['num_turns'],
            num_agents=game_params['num_agents'],
            memory_capacity=game_params['memory_capacity'],
            agent_biases="",
            myth_writer=myth_writer,
            task_order=combo['task_order'],
            results_path=results_path,
            checkpoint_path=checkpoint_path,
            checkpoint_every=10,
            resume_from=resume_from,
            log_file=log_path
        )

        sim_data.run_metadata["myth_topic_id"] = combo.get("myth_topic_id", "")
        sim_data.run_metadata["myth_topic"] = combo.get("myth_topic", "")

        # Save final full state
        sim_data.save_state(save_path)

        # Cleanup checkpoint on success
        if os.path.exists(checkpoint_path):
            try:
                os.remove(checkpoint_path)
            except OSError:
                pass

        return {
            "success": True,
            "file_path": save_path,
            "error": None,
            "combo_info": {
                "model": combo['model'],
                "persona": combo['persona']['description'],
                "task_order": combo['task_order'],
                "myth_topic_id": combo.get('myth_topic_id', ''),
            }
        }

    except Exception as e:
        return {
            "success": False,
            "file_path": None,
            "error": str(e),
            "combo_info": {
                "model": combo['model'],
                "persona": combo['persona']['description'],
                "task_order": combo['task_order'],
                "myth_topic_id": combo.get('myth_topic_id', ''),
            }
        }

def run_experiment_set(experiment_name: str, workers: int = 1):
    """
    Run a set of experiments either sequentially or in parallel.

    Args:
        experiment_name: Name of the experiment set from config
        workers: Number of parallel workers (1 = sequential, >1 = parallel)
    """
    # Load configuration
    config = ExperimentConfig('config/experiments.yaml')
    combinations = config.get_experiment_combinations(experiment_name)

    print(f"Running {experiment_name} with {len(combinations)} combinations")
    if workers > 1:
        print(f"Using {workers} parallel workers")
    else:
        print("Running sequentially (workers=1)")

    if workers == 1:
        # Sequential execution (backward compatible)
        for i, combo in enumerate(combinations):
            print(f"\n--- Combination {i+1}/{len(combinations)} ---")
            print(f"Model: {combo['model']}")
            print(f"Persona: {combo['persona']['description']}")
            print(f"Task Order: {combo['task_order']}")
            print(f"Myth Topic ID: {combo.get('myth_topic_id', '')}")
            print(f"Myth Topic: {combo.get('myth_topic', '')}")

            result = run_single_experiment(combo, experiment_name, i)

            if result['success']:
                print(f"✓ Saved to {result['file_path']}")
            else:
                print(f"✗ FAILED: {result['error']}")

    else:
        # Parallel execution
        print()
        completed = 0
        failed = 0
        failed_experiments = []

        with ProcessPoolExecutor(max_workers=workers) as executor:
            # Submit all experiments
            future_to_combo = {
                executor.submit(run_single_experiment, combo, experiment_name, i): (combo, i)
                for i, combo in enumerate(combinations)
            }

            # Process completions as they finish
            for future in as_completed(future_to_combo):
                combo, idx = future_to_combo[future]
                try:
                    result = future.result()
                    completed += 1

                    if result['success']:
                        print(f"[{completed}/{len(combinations)}] ✓ {result['combo_info']['model']} / "
                              f"{result['combo_info']['persona']} / "
                              f"{result['combo_info']['task_order']}")
                        print(f"    → {result['file_path']}")
                    else:
                        failed += 1
                        failed_experiments.append(result)
                        print(f"[{completed}/{len(combinations)}] ✗ FAILED: {result['combo_info']['model']} / "
                              f"{result['combo_info']['persona']} / "
                              f"{result['combo_info']['task_order']}")
                        print(f"    Error: {result['error']}")

                except Exception as e:
                    # Catch any unexpected exceptions from the worker
                    failed += 1
                    completed += 1
                    failed_experiments.append({
                        'combo_info': {
                            'model': combo['model'],
                            'persona': combo['persona']['description'],
                            'task_order': combo['task_order']
                        },
                        'error': str(e)
                    })
                    print(f"[{completed}/{len(combinations)}] ✗ WORKER EXCEPTION: {str(e)}")

        # Print summary
        print(f"\n{'='*60}")
        print(f"Batch Complete: {completed - failed}/{len(combinations)} succeeded, {failed} failed")
        if failed_experiments:
            print(f"\nFailed experiments:")
            for exp in failed_experiments:
                print(f"  - {exp['combo_info']['model']} / {exp['combo_info']['persona']} / "
                      f"{exp['combo_info']['task_order']}: {exp['error']}")
        print(f"{'='*60}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run batch experiments with optional parallelization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run sequentially (default)
  python experiments/run_trust_game_batch.py pilot

  # Run with 4 parallel workers
  python experiments/run_trust_game_batch.py model_comparison --workers 4

  # Run default experiments sequentially
  python experiments/run_trust_game_batch.py
        """
    )
    parser.add_argument(
        'experiment_name',
        nargs='?',
        default=None,
        help='Name of the experiment set from config/experiments.yaml'
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=1,
        help='Number of parallel workers (default: 1 for sequential execution)'
    )

    args = parser.parse_args()

    if args.experiment_name:
        run_experiment_set(args.experiment_name, workers=args.workers)
    else:
        # Run default experiment sets
        run_experiment_set("pilot", workers=args.workers)
        run_experiment_set("persona_comparison", workers=args.workers)
        # run_experiment_set("full_factorial", workers=args.workers)  # Comment out for now
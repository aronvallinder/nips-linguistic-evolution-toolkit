"""
Batch runner for noise experiments.

This runner loads configuration from noise/experiments_noisy.yaml and uses
TrustGameNoisy with noise and asymmetric naming support.

Usage:
    # Run specific experiment set
    python noise/run_noisy_batch.py noise_pilot

    # Run with parallel workers
    python noise/run_noisy_batch.py noise_comparison --workers 4

    # Run default (noise_pilot)
    python noise/run_noisy_batch.py
"""

import os
import sys
import argparse
import yaml
from itertools import product
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Dict, Any, List

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.simulation import run_simulation
from src.myth_writer import MythWriter
from noise.trust_game_noisy import TrustGameNoisy


class NoisyExperimentConfig:
    """Configuration loader for noise experiments."""

    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

    def get_experiment_combinations(self, experiment_name: str) -> List[Dict]:
        """Generate all parameter combinations for an experiment set."""
        exp_set = self.config['experiment_sets'][experiment_name]

        # Resolve "all" references
        models = self._resolve_all(exp_set['models'], 'base_models')
        templates = self._resolve_all(exp_set['templates'], 'prompt_templates')
        personas = self._resolve_all(exp_set['personas'], 'personas')

        # Task orders
        task_orders = exp_set.get('task_orders', [["game"]])

        # Myth topics
        myth_topics_spec = exp_set.get("myth_topics", None)
        if myth_topics_spec is None:
            myth_topic_ids = ["anything"]
        else:
            myth_topic_ids = self._resolve_all(myth_topics_spec, "myth_topics")

        # Game params list (key difference from main config)
        # In noise config, we have game_params_list which references named param sets
        game_params_list = exp_set.get('game_params_list', ['default'])

        # Number of runs per combination
        num_runs = exp_set.get('num_runs', 1)

        # Generate all combinations
        combinations = []
        for model, template, persona, order, myth_topic_id, game_param_name in product(
            models, templates, personas, task_orders, myth_topic_ids, game_params_list
        ):
            # Keep non-myth task orders from multiplying across all topics
            if "myth" not in order and myth_topic_id != myth_topic_ids[0]:
                continue

            myth_topic = "" if myth_topic_id == "" else self.config["myth_topics"].get(myth_topic_id, "")

            # Get game params from the named set
            game_params = self._get_game_params(game_param_name)

            for run in range(num_runs):
                combo = {
                    "model": self.config["base_models"][model],
                    "template": self.config["prompt_templates"][template],
                    "persona": self.config["personas"][persona],
                    "task_order": order,
                    "game_params": game_params,
                    "game_params_name": game_param_name,  # Track which param set was used
                    "myth_topic_id": myth_topic_id,
                    "myth_topic": myth_topic,
                    "run_number": run,
                    # Prompt templates
                    "trust_game_round1_investor": self.config["prompt_templates"].get("trust_game_round1_investor"),
                    "trust_game_round1_trustee": self.config["prompt_templates"].get("trust_game_round1_trustee"),
                    "trust_game_later_investor": self.config["prompt_templates"].get("trust_game_later_investor"),
                    "trust_game_later_trustee": self.config["prompt_templates"].get("trust_game_later_trustee"),
                    "myth_writing_default": self.config["prompt_templates"].get("myth_writing_default"),
                    "myth_writing_later_rounds": self.config["prompt_templates"].get("myth_writing_later_rounds"),
                }
                combinations.append(combo)

        return combinations

    def _resolve_all(self, param, config_key):
        if param == "all":
            return list(self.config[config_key].keys())
        return param

    def _get_game_params(self, param_name: str) -> Dict:
        """Get game parameters from a named parameter set."""
        if param_name in self.config.get('game_params', {}):
            return self.config['game_params'][param_name].copy()
        else:
            # Fallback to default
            return self.config['game_params']['default'].copy()


def _unique_json_path(path: str) -> str:
    """If path exists, return ..._2.json, ..._3.json, ... (first free slot)."""
    if not path.endswith(".json"):
        raise ValueError(f"Expected a .json path, got: {path}")
    if not os.path.exists(path):
        return path
    base = path[:-5]
    n = 2
    while True:
        candidate = f"{base}_{n}.json"
        if not os.path.exists(candidate):
            return candidate
        n += 1


def _sanitize_for_filename(value: str) -> str:
    """Make a string safe for filenames."""
    if value is None:
        return "none"
    value = str(value).strip()
    if value == "":
        return "empty"
    return "".join(ch if (ch.isalnum() or ch in "-_.") else "_" for ch in value)


def run_single_experiment(combo: Dict[str, Any], experiment_name: str, index: int) -> Dict[str, Any]:
    """
    Run a single noise experiment with the given combination.

    Returns:
        dict with keys: success, file_path, error, combo_info
    """
    try:
        game_params = combo['game_params']

        # Prepare personas dict for both agents
        personas = {
            'Agent_1': combo['persona'],
            'Agent_2': combo['persona']
        }

        # Create noisy trust game with noise config and other_player_names
        game = TrustGameNoisy(
            endowment=game_params['endowment'],
            multiplier=game_params['multiplier'],
            system_prompt_template=combo['template'],
            personas=personas,
            round1_investor_template=combo['trust_game_round1_investor'],
            round1_trustee_template=combo['trust_game_round1_trustee'],
            later_investor_template=combo['trust_game_later_investor'],
            later_trustee_template=combo['trust_game_later_trustee'],
            noise_config=game_params.get('noise_config'),
            other_player_names=game_params.get('other_player_names', 'default')
        )

        myth_writer = MythWriter(
            myth_topic=combo.get("myth_topic", ""),
            round1_template=combo['myth_writing_default'],
            later_rounds_template=combo['myth_writing_later_rounds']
        )

        # Build directory structure: data/json/noise_experiments/{experiment_name}/{model}/{task_order}/{game_params}/
        model_name = combo['model'].split('/')[-1] if '/' in combo['model'] else combo['model']
        task_order_str = "_".join(combo['task_order'])
        game_params_name = combo.get('game_params_name', 'default')

        save_dir = f"data/json/noise_experiments/v2/{experiment_name}/{model_name}/{task_order_str}/{game_params_name}"
        os.makedirs(save_dir, exist_ok=True)

        # Include myth_topic in filename if myth task is present
        if "myth" in combo["task_order"]:
            myth_topic_str = "_" + _sanitize_for_filename(combo.get("myth_topic_id", ""))
        else:
            myth_topic_str = ""

        filename = f"{experiment_name}_{index:03d}_{combo['persona']['description']}{myth_topic_str}.json"
        save_path = f"{save_dir}/{filename}"
        save_path = _unique_json_path(save_path)

        # Checkpointing paths
        base_no_ext = save_path[:-5] if save_path.endswith(".json") else save_path
        results_path = base_no_ext + ".results.json"
        checkpoint_path = base_no_ext + ".checkpoint.json"
        log_path = base_no_ext + ".log"

        resume_from = checkpoint_path if os.path.exists(checkpoint_path) else None

        # Initialize log file
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(f"{'='*80}\n")
            f.write(f"NOISE EXPERIMENT LOG\n")
            f.write(f"{'='*80}\n")
            f.write(f"Experiment: {experiment_name}\n")
            f.write(f"Index: {index:03d}\n")
            f.write(f"Model: {combo['model']}\n")
            f.write(f"Persona: {combo['persona']['description']}\n")
            f.write(f"Task Order: {combo['task_order']}\n")
            f.write(f"Game Params: {game_params_name}\n")
            f.write(f"Noise Config: {game_params.get('noise_config', 'None')}\n")
            f.write(f"Other Player Names: {game_params.get('other_player_names', 'default')}\n")
            f.write(f"Myth Topic ID: {combo.get('myth_topic_id', 'N/A')}\n")
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

        # Store metadata
        sim_data.run_metadata["myth_topic_id"] = combo.get("myth_topic_id", "")
        sim_data.run_metadata["myth_topic"] = combo.get("myth_topic", "")
        sim_data.run_metadata["game_params_name"] = game_params_name
        sim_data.run_metadata["noise_config"] = game_params.get("noise_config")
        sim_data.run_metadata["other_player_names"] = game_params.get("other_player_names", "default")

        # Save final state
        sim_data.save_state(save_path)

        # Cleanup checkpoint
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
                "game_params": game_params_name,
                "myth_topic_id": combo.get('myth_topic_id', ''),
            }
        }

    except Exception as e:
        import traceback
        return {
            "success": False,
            "file_path": None,
            "error": f"{str(e)}\n{traceback.format_exc()}",
            "combo_info": {
                "model": combo.get('model', 'unknown'),
                "persona": combo.get('persona', {}).get('description', 'unknown'),
                "task_order": combo.get('task_order', []),
                "game_params": combo.get('game_params_name', 'unknown'),
                "myth_topic_id": combo.get('myth_topic_id', ''),
            }
        }


def run_experiment_set(experiment_name: str, workers: int = 1, config_path: str = None):
    """
    Run a set of noise experiments.

    Args:
        experiment_name: Name of the experiment set from config
        workers: Number of parallel workers (1 = sequential)
        config_path: Path to config file (default: noise/experiments_noisy.yaml)
    """
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), 'experiments_noisy.yaml')

    config = NoisyExperimentConfig(config_path)
    combinations = config.get_experiment_combinations(experiment_name)

    print(f"Running noise experiment: {experiment_name}")
    print(f"Total combinations: {len(combinations)}")
    if workers > 1:
        print(f"Using {workers} parallel workers")
    else:
        print("Running sequentially (workers=1)")

    if workers == 1:
        # Sequential execution
        for i, combo in enumerate(combinations):
            print(f"\n--- Combination {i+1}/{len(combinations)} ---")
            print(f"Model: {combo['model']}")
            print(f"Persona: {combo['persona']['description']}")
            print(f"Task Order: {combo['task_order']}")
            print(f"Game Params: {combo.get('game_params_name', 'default')}")
            print(f"Noise Config: {combo['game_params'].get('noise_config', 'None')}")
            print(f"Other Player Names: {combo['game_params'].get('other_player_names', 'default')}")

            result = run_single_experiment(combo, experiment_name, i)

            if result['success']:
                print(f"Saved to {result['file_path']}")
            else:
                print(f"FAILED: {result['error']}")

    else:
        # Parallel execution
        print()
        completed = 0
        failed = 0
        failed_experiments = []

        with ProcessPoolExecutor(max_workers=workers) as executor:
            future_to_combo = {
                executor.submit(run_single_experiment, combo, experiment_name, i): (combo, i)
                for i, combo in enumerate(combinations)
            }

            for future in as_completed(future_to_combo):
                combo, idx = future_to_combo[future]
                try:
                    result = future.result()
                    completed += 1

                    if result['success']:
                        print(f"[{completed}/{len(combinations)}] {result['combo_info']['model']} / "
                              f"{result['combo_info']['game_params']} / "
                              f"{result['combo_info']['task_order']}")
                        print(f"    -> {result['file_path']}")
                    else:
                        failed += 1
                        failed_experiments.append(result)
                        print(f"[{completed}/{len(combinations)}] FAILED: {result['combo_info']['model']} / "
                              f"{result['combo_info']['game_params']}")
                        print(f"    Error: {result['error'][:200]}")

                except Exception as e:
                    failed += 1
                    completed += 1
                    failed_experiments.append({
                        'combo_info': {
                            'model': combo.get('model', 'unknown'),
                            'game_params': combo.get('game_params_name', 'unknown'),
                            'task_order': combo.get('task_order', [])
                        },
                        'error': str(e)
                    })
                    print(f"[{completed}/{len(combinations)}] WORKER EXCEPTION: {str(e)}")

        # Print summary
        print(f"\n{'='*60}")
        print(f"Batch Complete: {completed - failed}/{len(combinations)} succeeded, {failed} failed")
        if failed_experiments:
            print(f"\nFailed experiments:")
            for exp in failed_experiments:
                print(f"  - {exp['combo_info']['model']} / {exp['combo_info']['game_params']}: "
                      f"{exp['error'][:100]}")
        print(f"{'='*60}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run noise experiments with optional parallelization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run pilot test
  python noise/run_noisy_batch.py noise_pilot

  # Run noise comparison with 4 workers
  python noise/run_noisy_batch.py noise_comparison --workers 4

  # Run framing comparison
  python noise/run_noisy_batch.py framing_comparison
        """
    )
    parser.add_argument(
        'experiment_name',
        nargs='?',
        default='noise_pilot',
        help='Name of the experiment set from noise/experiments_noisy.yaml'
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=1,
        help='Number of parallel workers (default: 1 for sequential execution)'
    )
    parser.add_argument(
        '--config',
        type=str,
        default=None,
        help='Path to config file (default: noise/experiments_noisy.yaml)'
    )

    args = parser.parse_args()

    run_experiment_set(args.experiment_name, workers=args.workers, config_path=args.config)

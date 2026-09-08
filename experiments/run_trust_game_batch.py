import os
import sys
import argparse
import contextlib
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, Any, Tuple

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.batch_utils import sanitize_for_filename as _sanitize_for_filename
from src.batch_utils import unique_json_path as _unique_json_path
from src.experiment_config import ExperimentConfig
from src.simulation import run_simulation
from src.myth_writer import MythWriter
from games.trust_game import TrustGame
from scripts.hf_sync_completed_runs import maybe_sync_completed_runs
from src.llm_settings import prepare_combinations, prepared_plan
from src.utils import DIRECT_MODEL_ALIASES

def run_single_experiment(combo: Dict[str, Any], experiment_name: str, index: int) -> Dict[str, Any]:
    """
    Run a single experiment with the given combination.
    Must be a top-level function for pickling in multiprocessing.

    Returns:
        dict with keys: success (bool), file_path (str), error (str or None), combo_info (dict)
    """
    save_path = None
    try:
        request_plan = prepared_plan(combo)
        # Configure game
        game_params = combo['game_params']

        agent_ids = [f"Agent_{i+1}" for i in range(game_params['num_agents'])]
        personas = {agent_id: combo['persona'] for agent_id in agent_ids}
        defector_seed = game_params.get("defector_seed")
        if defector_seed is None:
            defector_seed = combo.get("replicate_id")
        if defector_seed is None:
            defector_seed = 0

        game = TrustGame(
            endowment=game_params['endowment'],
            multiplier=game_params['multiplier'],
            system_prompt_template=combo['template'],
            personas=personas,
            round1_investor_template=combo['trust_game_round1_investor'],
            round1_trustee_template=combo['trust_game_round1_trustee'],
            later_investor_template=combo['trust_game_later_investor'],
            later_trustee_template=combo['trust_game_later_trustee'],
            multiplier_distribution=game_params.get('multiplier_distribution'),
            history_policy=game_params.get('history_policy', 'minimal'),
            self_history_window=game_params.get('self_history_window', 1),
            coplayer_history_window=game_params.get('coplayer_history_window', 0),
            show_agent_names=game_params.get('show_agent_names', True),
            defector_ratio=game_params.get("defector_ratio", 0.0),
            defector_agent_ids=game_params.get("defector_agent_ids"),
            defector_seed=defector_seed,
            defector_prompt_template=combo.get("defector_game_instruction"),
            defector_action_policy=game_params.get(
                "defector_action_policy",
                "prompted",
            ),
            defector_myth_policy=game_params.get(
                "defector_myth_policy",
                "normal",
            ),
            defector_role_visible_to_self=game_params.get(
                "defector_role_visible_to_self",
                True,
            ),
        )

        myth_writer = MythWriter(
            myth_topic=combo.get("myth_topic", ""),
            round1_template=combo['myth_writing_default'],
            later_rounds_template=combo['myth_writing_later_rounds']
        )

        # Build directory structure: {experiment_name}/{model}/{task_order}/
        model_name = combo['model'].split('/')[-1] if '/' in combo['model'] else combo['model']
        task_order_str = "_".join(combo['task_order'])

        # Create directory: data/json/{output_dir or experiment_name}/{model}/{task_order}/
        top_dir = combo.get("output_dir") or experiment_name
        save_dir = f"data/json/{top_dir}/{model_name}/{task_order_str}"
        Path(save_dir).mkdir(parents=True, exist_ok=True)

        # Only include myth_topic in filename if myth task is present
        if "myth" in combo["task_order"]:
            myth_topic_str = "_" + _sanitize_for_filename(combo.get("myth_topic_id", ""))
        else:
            myth_topic_str = ""

        replicate = combo.get("replicate_id")
        replicate_str = f"_rep{replicate:02d}" if replicate is not None else ""
        myth_arm = combo.get("myth_prompt_arm_id")
        myth_arm_str = f"_{_sanitize_for_filename(myth_arm)}" if myth_arm else ""
        filename = f"{experiment_name}_{index:03d}_{combo['persona']['description']}{replicate_str}{myth_arm_str}{myth_topic_str}.json"
        save_path = f"{save_dir}/{filename}"

        # If a run already exists, create filename_2.json / filename_3.json / ...
        save_path = _unique_json_path(save_path)

        # Hybrid checkpointing paths
        base_no_ext = save_path[:-5] if save_path.endswith(".json") else save_path
        results_path = base_no_ext + ".results.json"
        checkpoint_path = base_no_ext + ".checkpoint.json"
        log_path = base_no_ext + ".log"

        resume_from = checkpoint_path if Path(checkpoint_path).exists() else None

        # Initialize log file with header
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(f"{'='*80}\n")
            f.write(f"EXPERIMENT LOG\n")
            f.write(f"{'='*80}\n")
            f.write(f"Experiment: {experiment_name}\n")
            f.write(f"Index: {index:03d}\n")
            f.write(f"Model: {combo['model']}\n")
            f.write(f"Persona: {combo['persona']['description']}\n")
            f.write(f"System Addition Key: {combo.get('system_addition_key') or 'none'}\n")
            f.write(f"Task Order: {combo['task_order']}\n")
            f.write(f"Myth Topic ID: {combo.get('myth_topic_id', 'N/A')}\n")
            f.write(f"Myth Topic: {combo.get('myth_topic', 'N/A')}\n")
            f.write(f"Replicate ID: {combo.get('replicate_id') if combo.get('replicate_id') is not None else 'none'}\n")
            f.write(f"Myth Prompt Arm ID: {combo.get('myth_prompt_arm_id') or 'none'}\n")
            f.write(f"Myth Default Prompt Key: {combo.get('myth_default_prompt_key', 'myth_writing_default')}\n")
            f.write(f"Myth Later Prompt Key: {combo.get('myth_later_prompt_key', 'myth_writing_later_rounds')}\n")
            f.write(f"Defector Ratio Requested: {game_params.get('defector_ratio', 0.0)}\n")
            f.write(f"Defector Agent IDs Requested: {game_params.get('defector_agent_ids') or 'automatic'}\n")
            f.write(f"Defector Seed: {defector_seed}\n")
            f.write(f"Defector Action Policy: {game_params.get('defector_action_policy', 'prompted')}\n")
            f.write(f"Defector Myth Policy: {game_params.get('defector_myth_policy', 'normal')}\n")
            f.write(f"Defector Role Visible To Self: {game_params.get('defector_role_visible_to_self', True)}\n")
            f.write(f"{'='*80}\n\n")

        # Run simulation. TRUST_BATCH_QUIET keeps verbose per-round transcripts
        # in the run log instead of streaming child-process stdout.
        run_kwargs = {
            "game": game,
            "model": combo['model'],
            "temperature": game_params.get('temperature', 0.8),
            "num_turns": game_params['num_turns'],
            "num_agents": game_params['num_agents'],
            "memory_capacity": game_params['memory_capacity'],
            "agent_biases": "",
            "myth_writer": myth_writer,
            "task_order": combo['task_order'],
            "results_path": results_path,
            "checkpoint_path": checkpoint_path,
            "checkpoint_every": 10,
            "resume_from": resume_from,
            "log_file": log_path,
            "agent_names": game_params.get("agent_names"),
            "monitor_config": game_params.get("monitor_config"),
            "chat_memory_mode": game_params.get("chat_memory_mode", "default"),
            "request_plan": request_plan,
            "run_identity": {"experiment": experiment_name, "replicate_id": combo.get("replicate_id"), "output_path": str(save_path)},
            "run_metadata_extra": {"comparison_inputs": combo.get("comparison_inputs")},
        }
        quiet_batch = os.environ.get("TRUST_BATCH_QUIET", "").lower() in {"1", "true", "yes"}
        if quiet_batch:
            with open(log_path, "a", encoding="utf-8") as log_stream:
                with contextlib.redirect_stdout(log_stream):
                    sim_data = run_simulation(**run_kwargs)
        else:
            sim_data = run_simulation(**run_kwargs)

        sim_data.run_metadata["myth_topic_id"] = combo.get("myth_topic_id", "")
        sim_data.run_metadata["myth_topic"] = combo.get("myth_topic", "")
        sim_data.run_metadata["myth_prompt_arm_id"] = combo.get("myth_prompt_arm_id")
        sim_data.run_metadata["myth_default_prompt_key"] = combo.get("myth_default_prompt_key", "myth_writing_default")
        sim_data.run_metadata["myth_later_prompt_key"] = combo.get("myth_later_prompt_key", "myth_writing_later_rounds")
        sim_data.run_metadata["system_addition_key"] = combo.get("system_addition_key")
        sim_data.run_metadata["replicate_id"] = combo.get("replicate_id")
        sim_data.run_metadata["history_policy"] = game_params.get("history_policy", "minimal")
        sim_data.run_metadata["self_history_window"] = game_params.get("self_history_window", 1)
        sim_data.run_metadata["coplayer_history_window"] = game_params.get("coplayer_history_window", 0)
        sim_data.run_metadata["show_agent_names"] = game_params.get("show_agent_names", True)

        # Save final full state
        sim_data.save_state(save_path)
        transcript_path = base_no_ext + ".transcript.pdf"
        sim_data.save_transcript_pdf(transcript_path, source_path=save_path)

        # Cleanup checkpoint on success
        cp_path = Path(checkpoint_path)
        if cp_path.exists():
            try:
                cp_path.unlink()
            except OSError:
                pass

        return {
            "success": True,
            "file_path": save_path,
            "transcript_path": transcript_path,
            "error": None,
            "combo_info": {
                "model": combo['model'],
                "persona": combo['persona']['description'],
                "task_order": combo['task_order'],
                "myth_topic_id": combo.get('myth_topic_id', ''),
                "replicate_id": combo.get("replicate_id"),
                "myth_prompt_arm_id": combo.get("myth_prompt_arm_id"),
                "myth_default_prompt_key": combo.get("myth_default_prompt_key", "myth_writing_default"),
                "myth_later_prompt_key": combo.get("myth_later_prompt_key", "myth_writing_later_rounds"),
            }
        }

    except Exception as e:
        return {
            "success": False,
            "file_path": save_path,
            "error": str(e),
            "combo_info": {
                "model": combo['model'],
                "persona": combo['persona']['description'],
                "task_order": combo['task_order'],
                "myth_topic_id": combo.get('myth_topic_id', ''),
                "replicate_id": combo.get("replicate_id"),
                "myth_prompt_arm_id": combo.get("myth_prompt_arm_id"),
                "myth_default_prompt_key": combo.get("myth_default_prompt_key", "myth_writing_default"),
                "myth_later_prompt_key": combo.get("myth_later_prompt_key", "myth_writing_later_rounds"),
            }
        }

def run_experiment_set(experiment_name: str, workers: int = 1, allow_legacy_settings: bool = False, dry_run: bool = False):
    """
    Run a set of experiments either sequentially or in parallel.

    Args:
        experiment_name: Name of the experiment set from config
        workers: Number of parallel workers (1 = sequential, >1 = parallel)
    """
    # Load configuration
    config = ExperimentConfig('config/experiments.yaml')
    combinations = config.get_experiment_combinations(experiment_name)
    prepare_combinations(combinations, config.config["experiment_sets"][experiment_name], DIRECT_MODEL_ALIASES, allow_legacy=allow_legacy_settings)
    if dry_run:
        print(f"DRY RUN: N={len(combinations)} WORKERS={workers}; no APIs called")
        return

    print(f"Running {experiment_name} with {len(combinations)} combinations")
    if workers > 1:
        print(f"Using {workers} parallel workers")
    else:
        print("Running sequentially (workers=1)")

    candidate_final_paths = []
    if workers == 1:
        # Sequential execution (backward compatible)
        for i, combo in enumerate(combinations):
            print(f"\n--- Combination {i+1}/{len(combinations)} ---")
            print(f"Model: {combo['model']}")
            print(f"Persona: {combo['persona']['description']}")
            print(f"Task Order: {combo['task_order']}")
            print(f"Myth Topic ID: {combo.get('myth_topic_id', '')}")
            print(f"Myth Topic: {combo.get('myth_topic', '')}")
            print(f"Replicate ID: {combo.get('replicate_id') if combo.get('replicate_id') is not None else 'none'}")
            print(f"Myth Prompt Arm ID: {combo.get('myth_prompt_arm_id') or 'none'}")
            print(f"Myth Default Prompt Key: {combo.get('myth_default_prompt_key', 'myth_writing_default')}")
            print(f"Myth Later Prompt Key: {combo.get('myth_later_prompt_key', 'myth_writing_later_rounds')}")

            result = run_single_experiment(combo, experiment_name, i)
            if result.get('file_path'):
                candidate_final_paths.append(result['file_path'])

            if result['success']:
                print(f"✓ Saved to {result['file_path']}")
                print(f"✓ Transcript PDF: {result['transcript_path']}")
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
                    if result.get('file_path'):
                        candidate_final_paths.append(result['file_path'])

                    if result['success']:
                        print(f"[{completed}/{len(combinations)}] ✓ {result['combo_info']['model']} / "
                              f"{result['combo_info']['persona']} / "
                              f"{result['combo_info']['task_order']} / "
                              f"{result['combo_info'].get('myth_prompt_arm_id') or 'no_myth'} / "
                              f"{result['combo_info'].get('myth_later_prompt_key', 'myth_writing_later_rounds')}")
                        print(f"    → {result['file_path']}")
                        print(f"    → {result['transcript_path']}")
                    else:
                        failed += 1
                        failed_experiments.append(result)
                        print(f"[{completed}/{len(combinations)}] ✗ FAILED: {result['combo_info']['model']} / "
                              f"{result['combo_info']['persona']} / "
                              f"{result['combo_info']['task_order']} / "
                              f"{result['combo_info'].get('myth_prompt_arm_id') or 'no_myth'} / "
                              f"{result['combo_info'].get('myth_later_prompt_key', 'myth_writing_later_rounds')}")
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

    maybe_sync_completed_runs(
        candidate_final_paths,
        label=experiment_name,
    )

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

    parser.add_argument('--allow-legacy-settings', action='store_true', help='Explicitly retain historical environment-dependent settings')
    parser.add_argument('--dry-run', action='store_true', help='Print resolved request plans without credentials or API calls')
    args = parser.parse_args()

    if args.experiment_name:
        run_experiment_set(args.experiment_name, workers=args.workers, allow_legacy_settings=args.allow_legacy_settings, dry_run=args.dry_run)
    else:
        # Run default experiment sets
        run_experiment_set("pilot", workers=args.workers, allow_legacy_settings=args.allow_legacy_settings, dry_run=args.dry_run)
        run_experiment_set("persona_comparison", workers=args.workers, allow_legacy_settings=args.allow_legacy_settings, dry_run=args.dry_run)
        # run_experiment_set("full_factorial", workers=args.workers)  # Comment out for now

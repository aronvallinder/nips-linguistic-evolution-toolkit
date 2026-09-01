"""
Batch runner for noise experiments.

This runner loads configuration from config/experiments_noisy.yaml and uses
TrustGameNoisy with noise and asymmetric naming support.

Usage:
    # Run specific experiment set
    python experiments/run_noisy_batch.py noise_pilot

    # Run with parallel workers
    python experiments/run_noisy_batch.py noise_comparison --workers 4

    # Run default (noise_pilot)
    python experiments/run_noisy_batch.py
"""

import os
import sys
import argparse
import contextlib
import hashlib
import subprocess
import yaml
from itertools import product
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Dict, Any, List

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.batch_utils import sanitize_for_filename as _sanitize_for_filename
from src.batch_utils import unique_json_path as _unique_json_path
from src.simulation import run_simulation
from src.myth_writer import MythWriter
from games.trust_game_noisy import TrustGameNoisy


def execution_provenance(config_path: str) -> Dict[str, Any]:
    """Capture a non-secret, immutable description of the executed code/config."""
    config_bytes = Path(config_path).read_bytes()

    def git_output(*args):
        result = subprocess.run(
            ["git", *args],
            cwd=project_root,
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()

    return {
        "execution_provenance_version": 1,
        "code_commit": git_output("rev-parse", "HEAD"),
        "code_dirty": bool(git_output("status", "--porcelain")),
        "config_path": str(Path(config_path).resolve()),
        "config_sha256": hashlib.sha256(config_bytes).hexdigest(),
    }


class NoisyExperimentConfig:
    """Configuration loader for noise experiments."""

    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

    def get_experiment_combinations(
        self,
        experiment_name: str,
        max_runs: int = None,
    ) -> List[Dict]:
        """Generate all parameter combinations for an experiment set."""
        exp_set = self.config['experiment_sets'][experiment_name]
        provider_settings = exp_set.get("provider_settings", {}).copy()

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

        # Number of runs per combination. Repair cells may name exact paired
        # replicate IDs so failed runs can be repeated with their original
        # pairing/noise seeds without rerunning successful replicates.
        configured_num_runs = exp_set.get('num_runs', 1)
        explicit_replicate_ids = exp_set.get("replicate_ids")
        if explicit_replicate_ids is not None:
            if not isinstance(explicit_replicate_ids, list) or not explicit_replicate_ids:
                raise ValueError("replicate_ids must be a non-empty list")
            if any(
                isinstance(replicate_id, bool)
                or not isinstance(replicate_id, int)
                or replicate_id < 0
                for replicate_id in explicit_replicate_ids
            ):
                raise ValueError("replicate_ids must contain non-negative integers")
            if len(set(explicit_replicate_ids)) != len(explicit_replicate_ids):
                raise ValueError("replicate_ids must be unique")
            replicate_ids = list(explicit_replicate_ids)
        else:
            replicate_ids = list(range(configured_num_runs))
        if max_runs is not None:
            if max_runs < 1:
                raise ValueError("max_runs must be at least 1 when provided")
            replicate_ids = replicate_ids[:max_runs]

        # Myth prompt variants/arms. This mirrors the main batch runner so noisy
        # prompt-arm pilots can isolate myth_control vs myth_game_directive.
        myth_prompt_prefix = exp_set.get("myth_prompt_prefix", "")
        myth_default_key = exp_set.get(
            "myth_default_prompt_key",
            f"{myth_prompt_prefix}myth_writing_default",
        )
        myth_later_keys = exp_set.get("myth_later_prompt_keys")
        if myth_later_keys is None:
            myth_later_keys = [
                exp_set.get(
                    "myth_later_prompt_key",
                    f"{myth_prompt_prefix}myth_writing_later_rounds",
                )
            ]
        else:
            myth_later_keys = self._as_list(myth_later_keys)

        myth_prompt_arms = exp_set.get("myth_prompt_arms")
        if myth_prompt_arms is None:
            myth_prompt_arms = [
                {
                    "id": myth_later_key,
                    "default": myth_default_key,
                    "later": myth_later_key,
                }
                for myth_later_key in myth_later_keys
            ]
        else:
            myth_prompt_arms = [
                {
                    "id": arm["id"],
                    "default": arm.get("default", myth_default_key),
                    "later": arm.get("later", f"{myth_prompt_prefix}myth_writing_later_rounds"),
                }
                for arm in myth_prompt_arms
            ]

        # Generate all combinations
        combinations = []
        for model, template, persona, order, myth_topic_id, game_param_name, myth_prompt_arm in product(
            models, templates, personas, task_orders, myth_topic_ids, game_params_list, myth_prompt_arms
        ):
            # Keep non-myth task orders from multiplying across all topics
            if "myth" not in order and myth_topic_id != myth_topic_ids[0]:
                continue
            # Keep non-myth task orders from multiplying across myth prompt variants
            if "myth" not in order and myth_prompt_arm != myth_prompt_arms[0]:
                continue

            myth_topic = "" if myth_topic_id == "" else self.config["myth_topics"].get(myth_topic_id, "")

            # Get game params from the named set
            game_params = self._get_game_params(game_param_name)
            active_myth_default_key = myth_prompt_arm["default"]
            active_myth_later_key = myth_prompt_arm["later"]
            game_prompt_addition = self._get_game_prompt_addition(order)

            # Optional per-set override of game prompt templates (same
            # mechanism as the main config's game_prompt_keys).
            game_prompt_keys = exp_set.get("game_prompt_keys", {})

            def _game_template(name):
                key = game_prompt_keys.get(name, name)
                return self.config["prompt_templates"].get(key)

            for run in replicate_ids:
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
                    "trust_game_round1_investor": _game_template("trust_game_round1_investor"),
                    "trust_game_round1_trustee": _game_template("trust_game_round1_trustee"),
                    "trust_game_later_investor": _game_template("trust_game_later_investor"),
                    "trust_game_later_trustee": _game_template("trust_game_later_trustee"),
                    "defector_game_instruction": self.config["prompt_templates"].get(
                        "defector_game_instruction"
                    ),
                    "replicate_id": (
                        run
                        if explicit_replicate_ids is not None
                        or configured_num_runs > 1
                        or max_runs is not None
                        else None
                    ),
                    "myth_prompt_arm_id": myth_prompt_arm["id"] if "myth" in order else None,
                    "myth_default_prompt_key": active_myth_default_key,
                    "myth_later_prompt_key": active_myth_later_key,
                    "myth_writing_default": self._get_prompt_template(active_myth_default_key),
                    "myth_writing_later_rounds": self._get_prompt_template(active_myth_later_key),
                    "game_prompt_addition": game_prompt_addition,
                    "game_prompt_addition_id": (
                        "myth_decision_link" if game_prompt_addition else None
                    ),
                    "provider_settings": provider_settings.copy(),
                }
                combinations.append(combo)

        return combinations

    def _resolve_all(self, param, config_key):
        if param == "all":
            return list(self.config[config_key].keys())
        return param

    def _as_list(self, value):
        if isinstance(value, list):
            return value
        return [value]

    def _get_prompt_template(self, template_key: str) -> str:
        try:
            return self.config["prompt_templates"][template_key]
        except KeyError as exc:
            raise KeyError(f"Missing prompt template '{template_key}' in noise config") from exc

    def _get_game_prompt_addition(self, task_order) -> str:
        if "game" not in task_order or "myth" not in task_order:
            return ""
        return self.config.get("game_prompt_additions", {}).get("myth_decision_link", "")

    def _get_game_params(self, param_name: str) -> Dict:
        """Get game parameters from a named parameter set."""
        if param_name in self.config.get('game_params', {}):
            return self.config['game_params'][param_name].copy()
        else:
            # Fallback to default
            return self.config['game_params']['default'].copy()


def resolve_protocol_seeds(game_params: Dict[str, Any], combo: Dict[str, Any]):
    """Resolve paired exogenous seeds without changing legacy unseeded cells."""
    noise_seed = game_params.get("noise_seed")
    pairing_seed = game_params.get("pairing_seed")
    if not game_params.get("paired_protocol_seeds", False):
        return noise_seed, pairing_seed

    replicate_id = combo.get("replicate_id")
    if replicate_id is None:
        replicate_id = combo.get("run_number", 0)
    seed_id = int(game_params.get("protocol_seed_base", 0)) + int(replicate_id)
    if noise_seed is None:
        noise_seed = seed_id
    if pairing_seed is None:
        pairing_seed = seed_id
    return noise_seed, pairing_seed


def run_single_experiment(combo: Dict[str, Any], experiment_name: str, index: int, output_subdir: str = 'v2') -> Dict[str, Any]:
    """
    Run a single noise experiment with the given combination.

    Returns:
        dict with keys: success, file_path, error, combo_info
    """
    try:
        configured_openai_reasoning_effort = combo.get(
            "provider_settings", {}
        ).get("openai_reasoning_effort")
        active_openai_reasoning_effort = os.environ.get(
            "OPENAI_REASONING_EFFORT"
        )
        if (
            configured_openai_reasoning_effort is not None
            and active_openai_reasoning_effort
            != configured_openai_reasoning_effort
        ):
            raise RuntimeError(
                "Configured openai_reasoning_effort does not match "
                "OPENAI_REASONING_EFFORT: "
                f"{configured_openai_reasoning_effort!r} != "
                f"{active_openai_reasoning_effort!r}"
            )
        game_params = combo['game_params']
        configured_pairing_mode = game_params.get("pairing_mode", "balanced")
        effective_pairing_mode = (
            "fixed" if game_params["num_agents"] == 2 else configured_pairing_mode
        )
        noise_seed, pairing_seed = resolve_protocol_seeds(game_params, combo)

        agent_ids = [f"Agent_{i+1}" for i in range(game_params['num_agents'])]
        personas = {agent_id: combo['persona'] for agent_id in agent_ids}
        defector_seed = game_params.get("defector_seed")
        if defector_seed is None:
            defector_seed = combo.get("replicate_id")
        if defector_seed is None:
            defector_seed = 0
        random_defection_seed = game_params.get("random_defection_seed")
        if random_defection_seed is None:
            random_defection_seed = (
                noise_seed if noise_seed is not None else defector_seed
            )

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
            other_player_names=game_params.get('other_player_names', 'default'),
            history_policy=game_params.get('history_policy', 'minimal'),
            self_history_window=game_params.get('self_history_window', 1),
            coplayer_history_window=game_params.get('coplayer_history_window', 0),
            population_history_window=game_params.get(
                'population_history_window',
                0,
            ),
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
            random_defection_probability=game_params.get(
                "random_defection_probability",
                0.0,
            ),
            random_defection_seed=random_defection_seed,
            game_prompt_addition=combo.get("game_prompt_addition", ""),
            pairing_mode=configured_pairing_mode,
            pairing_seed=pairing_seed,
            noise_seed=noise_seed,
            prompt_regime=game_params.get("prompt_regime", "legacy"),
            punishment_enabled=game_params.get("punishment_enabled", False),
            punishment_budget=game_params.get("punishment_budget", 2),
            punishment_effect_multiplier=game_params.get(
                "punishment_effect_multiplier",
                3,
            ),
            punishment_prompt_variant=game_params.get(
                "punishment_prompt_variant",
                "current",
            ),
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

        save_dir = f"data/json/noise_experiments/{output_subdir}/{experiment_name}/{model_name}/{task_order_str}/{game_params_name}"
        os.makedirs(save_dir, exist_ok=True)

        # Include myth_topic in filename if myth task is present
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
            f.write(f"Replicate ID: {combo.get('replicate_id') if combo.get('replicate_id') is not None else 'none'}\n")
            f.write(f"Myth Prompt Arm ID: {combo.get('myth_prompt_arm_id') or 'none'}\n")
            f.write(f"Myth Default Prompt Key: {combo.get('myth_default_prompt_key', 'myth_writing_default')}\n")
            f.write(f"Myth Later Prompt Key: {combo.get('myth_later_prompt_key', 'myth_writing_later_rounds')}\n")
            f.write(f"Game Prompt Addition ID: {combo.get('game_prompt_addition_id') or 'none'}\n")
            f.write(f"Pairing Mode Configured: {configured_pairing_mode}\n")
            f.write(f"Pairing Mode Effective: {effective_pairing_mode}\n")
            f.write(f"Pairing Seed: {pairing_seed if pairing_seed is not None else 'none'}\n")
            f.write(f"Noise Seed: {noise_seed if noise_seed is not None else 'none'}\n")
            f.write(f"Prompt Regime: {game_params.get('prompt_regime', 'legacy')}\n")
            f.write(f"History Policy: {game_params.get('history_policy', 'minimal')}\n")
            f.write(f"Self History Window: {game_params.get('self_history_window', 1)}\n")
            f.write(f"Co-player History Window: {game_params.get('coplayer_history_window', 0)}\n")
            f.write(f"Population History Window: {game_params.get('population_history_window', 0)}\n")
            f.write(f"Show Agent Names: {game_params.get('show_agent_names', True)}\n")
            f.write(f"Defector Ratio Requested: {game_params.get('defector_ratio', 0.0)}\n")
            f.write(f"Defector Agent IDs Requested: {game_params.get('defector_agent_ids') or 'automatic'}\n")
            f.write(f"Defector Seed: {defector_seed}\n")
            f.write(f"Defector Action Policy: {game_params.get('defector_action_policy', 'prompted')}\n")
            f.write(f"Defector Myth Policy: {game_params.get('defector_myth_policy', 'normal')}\n")
            f.write(f"Defector Role Visible To Self: {game_params.get('defector_role_visible_to_self', True)}\n")
            f.write(f"Random Defection Probability: {game_params.get('random_defection_probability', 0.0)}\n")
            f.write(f"Random Defection Seed: {random_defection_seed}\n")
            f.write("Random Defection Unit: agent_game_decision\n")
            f.write(f"Deduction Stage Enabled: {game_params.get('punishment_enabled', False)}\n")
            f.write(f"Deduction Budget: {game_params.get('punishment_budget', 2)}\n")
            f.write(f"Deduction Effect Multiplier: {game_params.get('punishment_effect_multiplier', 3)}\n")
            f.write(f"Deduction Prompt Variant: {game_params.get('punishment_prompt_variant', 'current')}\n")
            f.write(f"{'='*80}\n\n")

        # Run simulation
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
            "chat_memory_mode": game_params.get("chat_memory_mode", "default"),
            "run_metadata_extra": combo.get("execution_provenance", {}),
        }
        quiet_batch = os.environ.get("TRUST_BATCH_QUIET", "").lower() in {"1", "true", "yes"}
        if quiet_batch:
            with open(log_path, "a", encoding="utf-8") as log_stream:
                with contextlib.redirect_stdout(log_stream):
                    sim_data = run_simulation(**run_kwargs)
        else:
            sim_data = run_simulation(**run_kwargs)

        # Store metadata
        sim_data.run_metadata["myth_topic_id"] = combo.get("myth_topic_id", "")
        sim_data.run_metadata["myth_topic"] = combo.get("myth_topic", "")
        sim_data.run_metadata["game_params_name"] = game_params_name
        sim_data.run_metadata["noise_config"] = game_params.get("noise_config")
        sim_data.run_metadata["other_player_names"] = game_params.get("other_player_names", "default")
        sim_data.run_metadata["replicate_id"] = combo.get("replicate_id")
        sim_data.run_metadata["myth_prompt_arm_id"] = combo.get("myth_prompt_arm_id")
        sim_data.run_metadata["myth_default_prompt_key"] = combo.get("myth_default_prompt_key", "myth_writing_default")
        sim_data.run_metadata["myth_later_prompt_key"] = combo.get("myth_later_prompt_key", "myth_writing_later_rounds")
        sim_data.run_metadata["game_prompt_addition_id"] = combo.get(
            "game_prompt_addition_id"
        )
        sim_data.run_metadata["game_prompt_addition"] = combo.get(
            "game_prompt_addition", ""
        )
        sim_data.run_metadata["history_policy"] = game_params.get("history_policy", "minimal")
        sim_data.run_metadata["self_history_window"] = game_params.get("self_history_window", 1)
        sim_data.run_metadata["coplayer_history_window"] = game_params.get("coplayer_history_window", 0)
        sim_data.run_metadata["population_history_window"] = game_params.get(
            "population_history_window",
            0,
        )
        sim_data.run_metadata["show_agent_names"] = game_params.get("show_agent_names", True)
        sim_data.run_metadata["pairing_mode"] = configured_pairing_mode
        sim_data.run_metadata["effective_pairing_mode"] = effective_pairing_mode
        sim_data.run_metadata["pairing_seed"] = pairing_seed
        sim_data.run_metadata["noise_seed"] = noise_seed
        sim_data.run_metadata["prompt_regime"] = game_params.get("prompt_regime", "legacy")
        sim_data.run_metadata["punishment_enabled"] = game_params.get(
            "punishment_enabled",
            False,
        )
        sim_data.run_metadata["punishment_budget"] = game_params.get(
            "punishment_budget",
            2,
        )
        sim_data.run_metadata["punishment_effect_multiplier"] = game_params.get(
            "punishment_effect_multiplier",
            3,
        )
        sim_data.run_metadata["punishment_prompt_variant"] = game_params.get(
            "punishment_prompt_variant",
            "current",
        )
        sim_data.run_metadata["configured_openai_reasoning_effort"] = (
            configured_openai_reasoning_effort
        )

        # Save final state
        sim_data.save_state(save_path)
        transcript_path = base_no_ext + ".transcript.pdf"
        sim_data.save_transcript_pdf(transcript_path, source_path=save_path)

        # Cleanup checkpoint
        if os.path.exists(checkpoint_path):
            try:
                os.remove(checkpoint_path)
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
                "game_params": game_params_name,
                "myth_topic_id": combo.get('myth_topic_id', ''),
                "replicate_id": combo.get("replicate_id"),
                "myth_prompt_arm_id": combo.get("myth_prompt_arm_id"),
                "myth_default_prompt_key": combo.get("myth_default_prompt_key", "myth_writing_default"),
                "myth_later_prompt_key": combo.get("myth_later_prompt_key", "myth_writing_later_rounds"),
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
                "replicate_id": combo.get("replicate_id"),
                "myth_prompt_arm_id": combo.get("myth_prompt_arm_id"),
                "myth_default_prompt_key": combo.get("myth_default_prompt_key", "myth_writing_default"),
                "myth_later_prompt_key": combo.get("myth_later_prompt_key", "myth_writing_later_rounds"),
            }
        }


def run_experiment_set(
    experiment_name: str,
    workers: int = 1,
    config_path: str = None,
    output_subdir: str = 'v2',
    max_runs: int = None,
):
    """
    Run a set of noise experiments.

    Args:
        experiment_name: Name of the experiment set from config
        workers: Number of parallel workers (1 = sequential)
        config_path: Path to config file (default: config/experiments_noisy.yaml)
    """
    if config_path is None:
        config_path = str(Path(__file__).resolve().parent.parent / 'config' / 'experiments_noisy.yaml')

    config = NoisyExperimentConfig(config_path)
    combinations = config.get_experiment_combinations(
        experiment_name,
        max_runs=max_runs,
    )
    provenance = execution_provenance(config_path)
    provenance.update(
        {
            "experiment_name": experiment_name,
            "output_subdir": output_subdir,
        }
    )
    for combo in combinations:
        combo["execution_provenance"] = provenance.copy()

    print(f"Running noise experiment: {experiment_name}")
    print(f"Total combinations: {len(combinations)}")
    if max_runs is not None:
        print(f"Run limit: at most {max_runs} replicate(s) per configured cell")
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
            print(f"Replicate ID: {combo.get('replicate_id') if combo.get('replicate_id') is not None else 'none'}")
            print(f"Myth Prompt Arm ID: {combo.get('myth_prompt_arm_id') or 'none'}")
            print(f"Myth Default Prompt Key: {combo.get('myth_default_prompt_key', 'myth_writing_default')}")
            print(f"Myth Later Prompt Key: {combo.get('myth_later_prompt_key', 'myth_writing_later_rounds')}")

            result = run_single_experiment(combo, experiment_name, i, output_subdir)

            if result['success']:
                print(f"Saved to {result['file_path']}")
                print(f"Transcript PDF: {result['transcript_path']}")
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
                executor.submit(run_single_experiment, combo, experiment_name, i, output_subdir): (combo, i)
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
                              f"{result['combo_info']['task_order']} / "
                              f"{result['combo_info'].get('myth_prompt_arm_id') or 'no_myth'}")
                        print(f"    -> {result['file_path']}")
                        print(f"    -> {result['transcript_path']}")
                    else:
                        failed += 1
                        failed_experiments.append(result)
                        print(f"[{completed}/{len(combinations)}] FAILED: {result['combo_info']['model']} / "
                              f"{result['combo_info']['game_params']} / "
                              f"{result['combo_info'].get('myth_prompt_arm_id') or 'no_myth'}")
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
  python experiments/run_noisy_batch.py noise_pilot

  # Run noise comparison with 4 workers
  python experiments/run_noisy_batch.py noise_comparison --workers 4

  # Run framing comparison
  python experiments/run_noisy_batch.py framing_comparison
        """
    )
    parser.add_argument(
        'experiment_name',
        nargs='?',
        default='noise_pilot',
        help='Name of the experiment set from config/experiments_noisy.yaml'
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
        help='Path to config file (default: config/experiments_noisy.yaml)'
    )
    parser.add_argument(
        '--output-subdir',
        type=str,
        default='v2',
        help='Subdirectory under data/json/noise_experiments/ (default: v2)'
    )
    parser.add_argument(
        '--max-runs',
        type=int,
        default=None,
        help='Limit replicates per configured cell without editing the config'
    )

    args = parser.parse_args()

    run_experiment_set(
        args.experiment_name,
        workers=args.workers,
        config_path=args.config,
        output_subdir=args.output_subdir,
        max_runs=args.max_runs,
    )

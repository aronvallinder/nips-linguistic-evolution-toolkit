"""Run only missing outputs for a configured noisy experiment batch.

This is a resumable wrapper around experiments/run_noisy_batch.py. It computes
the canonical final JSON path for every configured combination, skips paths that
already exist, and runs only the missing jobs.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from experiments.run_noisy_batch import (
    NoisyExperimentConfig,
    execution_provenance,
    run_single_experiment,
)
from scripts.hf_sync_completed_runs import maybe_sync_completed_runs
from src.batch_utils import sanitize_for_filename
from src.experiment_condition import ConditionMismatchError, condition_from_run, read_final_run
from src.llm_settings import prepare_combinations
from src.utils import DIRECT_MODEL_ALIASES


def expected_output_path(
    combo: dict[str, Any],
    experiment_name: str,
    index: int,
    output_subdir: str,
) -> Path:
    model_name = combo["model"].split("/")[-1] if "/" in combo["model"] else combo["model"]
    task_order_str = "_".join(combo["task_order"])
    game_params_name = combo.get("game_params_name", "default")

    save_dir = (
        PROJECT_ROOT
        / "data"
        / "json"
        / "noise_experiments"
        / output_subdir
        / experiment_name
        / model_name
        / task_order_str
        / game_params_name
    )

    myth_topic_str = ""
    if "myth" in combo["task_order"]:
        myth_topic_str = "_" + sanitize_for_filename(combo.get("myth_topic_id", ""))

    replicate = combo.get("replicate_id")
    replicate_str = f"_rep{replicate:02d}" if replicate is not None else ""
    myth_arm = combo.get("myth_prompt_arm_id")
    myth_arm_str = f"_{sanitize_for_filename(myth_arm)}" if myth_arm else ""
    filename = (
        f"{experiment_name}_{index:03d}_{combo['persona']['description']}"
        f"{replicate_str}{myth_arm_str}{myth_topic_str}.json"
    )
    return save_dir / filename


def run_missing_job(
    combo: dict[str, Any],
    experiment_name: str,
    index: int,
    output_subdir: str,
    log_root: str,
) -> dict[str, Any]:
    log_dir = Path(log_root) / experiment_name
    log_dir.mkdir(parents=True, exist_ok=True)
    worker_log = log_dir / f"{experiment_name}_{index:03d}.out"

    with worker_log.open("w", encoding="utf-8") as handle:
        with redirect_stdout(handle), redirect_stderr(handle):
            result = run_single_experiment(combo, experiment_name, index, output_subdir)

    result["index"] = index
    result["worker_log"] = str(worker_log)
    return result


def load_combinations(experiment_name: str, config_path: str | None, *, allow_legacy_settings=False) -> list[dict[str, Any]]:
    if config_path is None:
        config_path = str(PROJECT_ROOT / "config" / "experiments_noisy.yaml")

    config = NoisyExperimentConfig(config_path)
    combinations = config.get_experiment_combinations(experiment_name)
    prepare_combinations(combinations, config.config["experiment_sets"][experiment_name], DIRECT_MODEL_ALIASES, allow_legacy=allow_legacy_settings)
    provenance = execution_provenance(config_path)
    for combination in combinations:
        combination["execution_provenance"] = provenance.copy()
    return combinations


def main() -> int:
    parser = argparse.ArgumentParser(description="Run only missing noisy experiment outputs.")
    parser.add_argument("experiment_name", help="Experiment set from config/experiments_noisy.yaml")
    parser.add_argument("--workers", type=int, default=1, help="Parallel workers")
    parser.add_argument("--config", default=None, help="Optional config file path")
    parser.add_argument(
        "--output-subdir",
        default="v2",
        help="Subdirectory under data/json/noise_experiments/",
    )
    parser.add_argument(
        "--log-dir",
        default="/tmp/nlet-runs",
        help="Directory for per-worker stdout/stderr logs",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional maximum number of missing jobs to run",
    )

    parser.add_argument("--allow-legacy-settings", action="store_true", help="Explicitly retain historical environment-dependent settings")
    parser.add_argument("--dry-run", action="store_true", help="Print resolved plans without API calls or uploads")
    args = parser.parse_args()

    combinations = load_combinations(args.experiment_name, args.config, allow_legacy_settings=args.allow_legacy_settings)
    if args.dry_run:
        print(f"DRY RUN: N={len(combinations)} WORKERS={args.workers}; no APIs called")
        return 0
    missing: list[tuple[int, dict[str, Any], Path]] = []
    expected_outputs: list[Path] = []

    for index, combo in enumerate(combinations):
        expected_path = expected_output_path(
            combo,
            args.experiment_name,
            index,
            args.output_subdir,
        )
        expected_outputs.append(expected_path)
        if not expected_path.exists():
            missing.append((index, combo, expected_path))
        else:
            saved = read_final_run(expected_path)
            if combo.get("request_plan") is not None:
                condition_from_run(saved)
                if saved["run_metadata"].get("comparison_inputs") != combo["comparison_inputs"]:
                    raise ConditionMismatchError(f"Existing final does not match the configured inputs: {expected_path}")

    if args.limit is not None:
        missing = missing[: args.limit]

    print(
        f"{args.experiment_name}: total={len(combinations)} "
        f"missing={len(missing)} workers={args.workers}",
        flush=True,
    )

    if not missing:
        maybe_sync_completed_runs(
            (path for path in expected_outputs if path.is_file()),
            label=f"{args.output_subdir}/{args.experiment_name}",
        )
        return 0

    failed: list[dict[str, Any]] = []
    completed = 0

    if args.workers == 1:
        for index, combo, _expected_path in missing:
            result = run_missing_job(
                combo,
                args.experiment_name,
                index,
                args.output_subdir,
                args.log_dir,
            )
            completed += 1
            if result["success"]:
                print(f"[{completed}/{len(missing)}] ok {index:03d} -> {result['file_path']}", flush=True)
            else:
                failed.append(result)
                print(f"[{completed}/{len(missing)}] FAIL {index:03d} -> {result['worker_log']}", flush=True)
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as executor:
            future_to_index = {
                executor.submit(
                    run_missing_job,
                    combo,
                    args.experiment_name,
                    index,
                    args.output_subdir,
                    args.log_dir,
                ): index
                for index, combo, _expected_path in missing
            }

            for future in as_completed(future_to_index):
                index = future_to_index[future]
                completed += 1
                try:
                    result = future.result()
                except Exception as exc:
                    result = {
                        "success": False,
                        "index": index,
                        "worker_log": None,
                        "error": repr(exc),
                    }

                if result["success"]:
                    print(f"[{completed}/{len(missing)}] ok {index:03d} -> {result['file_path']}", flush=True)
                else:
                    failed.append(result)
                    print(f"[{completed}/{len(missing)}] FAIL {index:03d} -> {result.get('worker_log')}", flush=True)

    if failed:
        summary_path = Path(args.log_dir) / args.experiment_name / "failed.json"
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(json.dumps(failed, indent=2), encoding="utf-8")
        print(f"failed={len(failed)} summary={summary_path}", flush=True)
        exit_status = 1
    else:
        print(f"complete={completed} failed=0", flush=True)
        exit_status = 0

    maybe_sync_completed_runs(
        (path for path in expected_outputs if path.is_file()),
        label=f"{args.output_subdir}/{args.experiment_name}",
    )
    return exit_status


if __name__ == "__main__":
    raise SystemExit(main())

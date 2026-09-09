#!/usr/bin/env python3
"""Run the frozen negative-only cross-model matrix with September 8 profiles."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.analyze_negative_only_crossmodel_batch import (  # noqa: E402
    audit_and_extract,
    validate_matrix,
)
from scripts.run_noisy_missing import (  # noqa: E402
    check_existing_final,
    expected_output_path,
    load_combinations,
)


CONFIG = ROOT / "config" / "experiments_noisy.yaml"
OUTPUT_ROOT = ROOT / "data" / "json" / "noise_experiments"
ANALYSIS_ROOT = ROOT / "docs" / "figures"
SHAPES = (
    "dyad_game",
    "dyad_game_myth",
    "dyad_myth_game",
    "population_game",
    "population_game_myth",
    "population_myth_game",
)
PROVIDERS = ("claude", "gpt", "gemini")
SET_NAMES = tuple(
    f"negative_only_reasoning_rerun_{shape}_{provider}_n5"
    for shape in SHAPES
    for provider in PROVIDERS
)
ORIGINAL_SET_NAMES = tuple(
    f"negative_only_crossmodel_{shape}_n5" for shape in SHAPES
)
EXPECTED_POLICIES = {
    "anthropic/claude-sonnet-4.5": {
        "provider": "anthropic",
        "reasoning": {"thinking": {"type": "enabled", "budget_tokens": 8192}},
        "temperature": "default",
        "max_output_tokens": 64000,
    },
    "openai/gpt-5-nano": {
        "provider": "openai",
        "reasoning": {"reasoning_effort": "high"},
        "temperature": "default",
        "max_output_tokens": 128000,
    },
    "google/gemini-3.7-flash": {
        "provider": "google",
        "reasoning": {"thinkingConfig": {"thinkingLevel": "high"}},
        "temperature": 0.8,
        "max_output_tokens": 65536,
    },
}
TRUNCATION_REASONS = {"length", "max_tokens", "max_output_tokens", "MAX_TOKENS"}


def _without_request_fields(combo: dict) -> dict:
    omitted = {"request_plan", "comparison_inputs", "execution_provenance"}
    return {key: value for key, value in combo.items() if key not in omitted}


def plan_rerun() -> list[tuple[str, int, dict, Path]]:
    """Resolve all 270 conditions and prove they preserve the frozen matrix."""
    planned = []
    original_by_shape = {}
    for shape, name in zip(SHAPES, ORIGINAL_SET_NAMES):
        originals = load_combinations(name, str(CONFIG), allow_legacy_settings=True)
        original_by_shape[shape] = {
            (combo["model"], combo["replicate_id"], combo["game_params_name"]):
            _without_request_fields(combo)
            for combo in originals
        }

    for shape in SHAPES:
        names = (
            f"negative_only_reasoning_rerun_{shape}_{provider}_n5"
            for provider in PROVIDERS
        )
        for name in names:
            combos = load_combinations(name, str(CONFIG))
            if len(combos) != 15:
                raise RuntimeError(f"{name}: expected 15 runs, found {len(combos)}")
            for index, combo in enumerate(combos):
                model = combo["model"]
                plan = combo["request_plan"].as_dict()
                if plan["policy"] != EXPECTED_POLICIES[model]:
                    raise RuntimeError(f"{name}: request profile differs from September 8")
                key = (model, combo["replicate_id"], combo["game_params_name"])
                if _without_request_fields(combo) != original_by_shape[shape][key]:
                    raise RuntimeError(f"{name}: frozen experimental inputs changed for {key}")
                planned.append((name, index, combo, Path()))

    if len(planned) != 270:
        raise RuntimeError(f"Expected 270 runs, found {len(planned)}")
    return planned


def expected_finals(output_subdir: str) -> list[tuple[str, int, dict, Path]]:
    planned = []
    for name in SET_NAMES:
        for index, combo in enumerate(load_combinations(name, str(CONFIG))):
            path = expected_output_path(combo, name, index, output_subdir)
            planned.append((name, index, combo, path))
    return planned


def audit_completed(output_subdir: str) -> dict:
    """Require complete finals, exact profiles, clean provenance, and no truncation."""
    import pandas as pd

    run_rows = []
    decision_rows = []
    interactions = 0
    for name, _index, combo, path in expected_finals(output_subdir):
        if not path.is_file():
            raise RuntimeError(f"Missing final full-state JSON: {path}")
        check_existing_final(path, combo)
        saved = json.loads(path.read_text(encoding="utf-8"))
        if saved["run_metadata"].get("llm_request") != combo["request_plan"].as_dict():
            raise RuntimeError(f"{path}: recorded request differs from the pinned profile")
        run_record, decisions = audit_and_extract(path)
        run_rows.append(run_record)
        decision_rows.extend(decisions)
        for agent in saved.get("agents", {}).values():
            for event in agent.get("interaction_history", []):
                response = event.get("response") or {}
                if response.get("response_source", "llm") != "llm":
                    continue
                usage = response.get("usage") or {}
                if usage.get("request_settings") != combo["request_plan"].as_dict():
                    raise RuntimeError(f"{path}: interaction omitted or changed request settings")
                if usage.get("outcome") != "complete":
                    raise RuntimeError(f"{path}: incomplete model interaction")
                if usage.get("finish_reason") in TRUNCATION_REASONS:
                    raise RuntimeError(f"{path}: truncated model interaction")
                interactions += 1

    validate_matrix(pd.DataFrame(run_rows), pd.DataFrame(decision_rows))
    return {"runs": len(run_rows), "receiver_decisions": len(decision_rows), "interactions": interactions}


def run(output_subdir: str, workers: int, execute: bool, resume: bool) -> None:
    plan_rerun()
    output = OUTPUT_ROOT / output_subdir
    analysis = ANALYSIS_ROOT / output_subdir
    command = (
        f"python3 scripts/rerun_negative_only_crossmodel.py --output-subdir {output_subdir} "
        f"--workers {workers} --execute"
    )
    print(
        "PREFLIGHT: MODEL=claude-sonnet-4.5(thinking=8192),"
        "gpt-5-nano(reasoning=high),gemini-3.7-flash(thinking=high) "
        f"N=270 WORKERS={workers} EST_COST=$213.53 CMD={command}",
        flush=True,
    )
    if not execute:
        print(f"READY: output={output} analysis={analysis}; no paid APIs called")
        return

    status = subprocess.run(
        ["git", "status", "--porcelain"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()
    if status:
        raise RuntimeError("Refusing to launch from a dirty worktree")
    if output.exists() and not resume:
        raise RuntimeError(f"Output already exists; inspect it and use --resume: {output}")

    child_env = os.environ.copy()
    child_env.update({
        "HF_DATASET_AUTO_UPLOAD": "0",
        "PYTHONPATH": ".",
        "TRUST_BATCH_QUIET": "1",
    })
    log_root = Path("/tmp") / f"nlet-{output_subdir}"
    for name in SET_NAMES:
        subprocess.run(
            [
                sys.executable,
                "scripts/run_noisy_missing.py",
                name,
                "--config",
                str(CONFIG.relative_to(ROOT)),
                "--workers",
                str(workers),
                "--output-subdir",
                output_subdir,
                "--log-dir",
                str(log_root),
            ],
            cwd=ROOT,
            env=child_env,
            check=True,
        )

    receipt = audit_completed(output_subdir)
    subprocess.run(
        [
            sys.executable,
            "scripts/analyze_negative_only_crossmodel_batch.py",
            "--input",
            str(output.relative_to(ROOT)),
            "--output",
            str(analysis.relative_to(ROOT)),
        ],
        cwd=ROOT,
        env=child_env,
        check=True,
    )
    print("COMPLETE: " + json.dumps(receipt, sort_keys=True))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-subdir", default="negative_only_crossmodel_reasoning_rerun_20260909")
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("--workers must be at least 1")
    run(args.output_subdir, args.workers, args.execute, args.resume)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

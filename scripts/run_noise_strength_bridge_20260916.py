#!/usr/bin/env python3
"""Run the pinned 20-run informed U(-2, 0) dyad bridge experiment."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import contextlib
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = os.environ.get("NLET_ENV_FILE")
if ENV_FILE:
    load_dotenv(ENV_FILE)
sys.path.insert(0, str(ROOT))

from experiments.run_noisy_batch import build_noisy_protocol  # noqa: E402
from scripts.rerun_negative_only_crossmodel import (  # noqa: E402
    EXPECTED_POLICIES,
    TRUNCATION_REASONS,
)
from scripts.run_noisy_missing import (  # noqa: E402
    check_existing_final,
    expected_output_path,
    load_combinations,
    run_missing_job,
)
from src.experiment_condition import read_final_run  # noqa: E402
from src.utils import is_exhausted_quota  # noqa: E402


CONFIG = ROOT / "config" / "experiments_noisy.yaml"
OUTPUT = "noise_strength_bridge_20260916"
PROVIDERS = ("claude", "gemini")
SHAPES = ("dyad_game", "dyad_myth_game")
BASE_GAME_PARAMS = {
    "dyad_game": "noisy2_crossmodel_negative_game_r3",
    "dyad_myth_game": "noisy2_crossmodel_negative_twotask_r3",
}
MAX_BATCH_ESTIMATED_COST_USD = 7.65
RATES_PER_MILLION = {
    "anthropic": (3.0, 15.0),
    "google": (0.75, 3.75),
}


def _load(name: str) -> list[dict]:
    with contextlib.redirect_stdout(io.StringIO()):
        return load_combinations(name, str(CONFIG))


def plan() -> list[tuple[str, int, dict, Path]]:
    """Resolve the matrix and prove that only noise range differs from controls."""
    jobs = []
    for shape in SHAPES:
        for provider in PROVIDERS:
            name = f"noise_strength_bridge_{shape}_{provider}_n5"
            base_name = f"negative_only_reasoning_rerun_{shape}_{provider}_n5"
            combinations = _load(name)
            if len(combinations) != 5:
                raise RuntimeError(f"{name}: expected 5 runs, found {len(combinations)}")

            base = {
                combo["replicate_id"]: combo
                for combo in _load(base_name)
                if combo["game_params_name"] == BASE_GAME_PARAMS[shape]
            }
            if len(base) != 5:
                raise RuntimeError(f"{base_name}: expected 5 matched controls")

            for index, combo in enumerate(combinations):
                matched = base[combo["replicate_id"]]
                expected = copy.deepcopy(matched["comparison_inputs"])
                expected_noise = expected["game_params"]["noise_config"]
                expected_noise["range"] = 2.0
                if combo["comparison_inputs"] != expected:
                    raise RuntimeError(
                        f"{name} replicate {combo['replicate_id']}: "
                        "an input other than noise range changed"
                    )
                if combo["request_plan"].as_dict()["policy"] != EXPECTED_POLICIES[combo["model"]]:
                    raise RuntimeError(f"{name}: request profile differs from September 8")
                if combo["game_params"].get("defector_ratio", 0) != 0:
                    raise RuntimeError(f"{name}: defector condition is not allowed")
                if combo["game_params"].get("random_defection_probability", 0) != 0:
                    raise RuntimeError(f"{name}: random defection is not allowed")
                noise = combo["game_params"]["noise_config"]
                if noise != {
                    "type": "uniform",
                    "range": 2.0,
                    "direction": "negative",
                    "applies_to": "both",
                    "inform_agents": True,
                }:
                    raise RuntimeError(f"{name}: resolved noise differs from informed U(-2, 0)")

                game, _ = build_noisy_protocol(combo, index)
                if game.noise_semantics != "communication":
                    raise RuntimeError(f"{name}: expected communication-noise semantics")
                if game.defector_agent_ids or game.random_defection_probability:
                    raise RuntimeError(f"{name}: resolved protocol contains defectors")
                if game.punishment_enabled:
                    raise RuntimeError(f"{name}: punishment must remain disabled")

                path = expected_output_path(combo, name, index, OUTPUT)
                jobs.append((name, index, combo, path))

    if len(jobs) != 20 or len({str(job[3]) for job in jobs}) != 20:
        raise RuntimeError("Expected exactly 20 unique jobs")
    jobs.sort(
        key=lambda job: (
            job[2]["replicate_id"],
            0 if "myth" in job[2]["task_order"] else 1,
            PROVIDERS.index(job[0].split("_")[-2]),
        )
    )
    return jobs


def audit(job: tuple[str, int, dict, Path]) -> dict:
    """Require a valid final state with the pinned protocol and request profile."""
    _name, _index, combo, path = job
    check_existing_final(path, combo)
    saved = read_final_run(path)
    metadata = saved["run_metadata"]
    if metadata.get("code_dirty"):
        raise RuntimeError(f"{path}: run came from a dirty worktree")
    if metadata.get("llm_request") != combo["request_plan"].as_dict():
        raise RuntimeError(f"{path}: recorded request differs from pinned profile")
    if metadata.get("noise_config") != combo["game_params"]["noise_config"]:
        raise RuntimeError(f"{path}: recorded noise differs from the resolved condition")
    if metadata.get("noise_semantics") != "communication":
        raise RuntimeError(f"{path}: wrong noise semantics")
    if metadata.get("defector_count") != 0 or metadata.get("random_defection_probability") != 0:
        raise RuntimeError(f"{path}: unexpected defector treatment")
    rounds = saved.get("conversation_history") or []
    if [round_data.get("round") for round_data in rounds] != list(range(1, 11)):
        raise RuntimeError(f"{path}: incomplete final round history")
    if len(rounds[-1].get("balances") or {}) != 2:
        raise RuntimeError(f"{path}: final balance state is incomplete")

    provider = metadata["llm_request"]["provider"]
    input_rate, output_rate = RATES_PER_MILLION[provider]
    calls = 0
    cost = 0.0
    for agent in saved.get("agents", {}).values():
        for event in agent.get("interaction_history", []):
            response = event.get("response") or {}
            if response.get("response_source", "llm") != "llm":
                continue
            usage = response.get("usage") or {}
            if usage.get("request_settings") != combo["request_plan"].as_dict():
                raise RuntimeError(f"{path}: interaction request settings changed")
            if usage.get("outcome") != "complete":
                raise RuntimeError(f"{path}: incomplete model interaction")
            if usage.get("finish_reason") in TRUNCATION_REASONS:
                raise RuntimeError(f"{path}: truncated model interaction")
            calls += 1
            output_tokens = usage.get("output_tokens") or 0
            if provider == "google":
                output_tokens += usage.get("reasoning_tokens") or 0
            cost += (
                (usage.get("input_tokens") or 0) * input_rate
                + output_tokens * output_rate
            ) / 1_000_000

    return {
        "path": str(path.relative_to(ROOT)),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "calls": calls,
        "standard_rate_usd": cost,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--audit-only", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.workers <= 8:
        parser.error("--workers must be between 1 and 8")

    jobs = plan()
    pending = []
    receipts = []
    for job in jobs:
        if job[3].exists():
            receipts.append(audit(job))
        else:
            pending.append(job)

    models = sorted({job[2]["model"] for job in jobs})
    print(
        "VALIDATED N=20 CLAUDE=10 GEMINI=10 DYADS=20 "
        f"INFORMED_NEGATIVE_RANGE2=20 EXISTING={len(receipts)} PENDING={len(pending)}",
        flush=True,
    )
    env_prefix = f"NLET_ENV_FILE={ENV_FILE} " if ENV_FILE else ""
    command = env_prefix + (
        "python scripts/run_noise_strength_bridge_20260916.py "
        f"--workers {args.workers} --execute"
    )
    estimated_cost = MAX_BATCH_ESTIMATED_COST_USD * len(pending) / len(jobs)
    print(
        f"PREFLIGHT: MODEL={','.join(models)} N={len(pending)} WORKERS={args.workers} "
        f"EST_COST=${estimated_cost:.2f} CMD={command}",
        flush=True,
    )

    if args.audit_only:
        if pending:
            raise RuntimeError(f"Audit requested with {len(pending)} finals missing")
        return 0
    if not args.execute:
        print("READY: resolved validation passed; no paid APIs called", flush=True)
        return 0

    missing_keys = [
        name
        for name in ("ANTHROPIC_API_KEY", "GEMINI_API_KEY")
        if not os.environ.get(name)
    ]
    if missing_keys:
        raise RuntimeError(
            "Missing required provider credentials: " + ", ".join(missing_keys)
        )

    status = subprocess.check_output(
        ["git", "status", "--porcelain"], cwd=ROOT, text=True
    ).strip()
    if status:
        raise RuntimeError("Refusing to launch from a dirty worktree")

    os.environ["HF_DATASET_AUTO_UPLOAD"] = "0"
    os.environ["TRUST_BATCH_QUIET"] = "1"
    log_root = str(Path("/tmp") / f"nlet-{OUTPUT}")
    workers = args.workers
    for attempt in range(1, 11):
        if not pending:
            break
        failed = []
        quota_exhausted = False
        with ProcessPoolExecutor(max_workers=workers) as pool:
            futures = {
                pool.submit(
                    run_missing_job,
                    job[2],
                    job[0],
                    job[1],
                    OUTPUT,
                    log_root,
                ): job
                for job in pending
            }
            for future in as_completed(futures):
                job = futures[future]
                if future.cancelled():
                    failed.append(job)
                    continue
                try:
                    result = future.result()
                    if not result.get("success") and is_exhausted_quota(result.get("error", "")):
                        quota_exhausted = True
                        for queued in futures:
                            queued.cancel()
                        print("BILLING EXHAUSTED: cancelling queued jobs", flush=True)
                    if not result.get("success"):
                        raise RuntimeError(
                            f"Worker failed; inspect {result.get('worker_log')}"
                        )
                    receipt = audit(job)
                    receipts.append(receipt)
                    print(
                        f"COMPLETE {len(receipts)}/20 {job[0]} index={job[1]} "
                        f"cost=${receipt['standard_rate_usd']:.3f}",
                        flush=True,
                    )
                except Exception as exc:
                    print(
                        f"FAILED {job[0]} index={job[1]} {type(exc).__name__}: {exc}",
                        flush=True,
                    )
                    if job[3].exists():
                        raise
                    failed.append(job)
        if quota_exhausted:
            raise RuntimeError("Provider credits exhausted; completed finals were preserved")
        pending = failed
        if pending:
            if attempt == 10:
                raise RuntimeError(f"{len(pending)} runs failed after ten attempts")
            workers = 1
            print(
                f"CONTINUATION: MODEL={','.join(models)} PENDING={len(pending)} "
                f"WORKERS=1 ADDED_EST_COST=$0 REASON=retry-attempt-{attempt + 1}",
                flush=True,
            )
            time.sleep(min(60, 2**attempt))

    target = ROOT / "data" / "json" / "noise_experiments" / OUTPUT / "completion_receipt.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(
            {
                "runs": len(receipts),
                "standard_rate_usd": sum(item["standard_rate_usd"] for item in receipts),
                "finals": sorted(receipts, key=lambda item: item["path"]),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"AUDIT PASSED {len(receipts)}/20; receipt={target}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

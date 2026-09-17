#!/usr/bin/env python3
"""Frozen 36-run mixed-model dyad batch (project-memory D010); dry-run by default.

Two model families share one fixed dyad under the September informed-noise
protocol: Sonnet 4.5 with GPT-5 Nano, and Sonnet 4.5 with Gemini 3.7 Flash,
across the task orders game, game_myth and myth_game. Six replicates per cell:
three where Sonnet sends first (Agent_1, replicates 0/2/4) and three where the
other family sends first (replicates 1/3/5).

The plan step proves, before any paid call, that every non-model input equals
the September ``negative_only_reasoning_rerun_dyad_*`` control cell and that
each agent's pinned request policy equals the September profile for its model.
The audit step re-checks every final and prices it per provider from recorded
token usage at standard rates.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.run_noisy_missing import load_combinations, expected_output_path, check_existing_final, run_missing_job  # noqa: E402
from scripts.rerun_negative_only_crossmodel import EXPECTED_POLICIES, TRUNCATION_REASONS  # noqa: E402
from experiments.run_noisy_batch import build_noisy_protocol  # noqa: E402
from src.llm_settings import is_mixed_plan  # noqa: E402
from src.utils import is_exhausted_quota  # noqa: E402

CONFIG = ROOT / "config/experiments_noisy.yaml"
OUTPUT = "mixed_model_dyads_20260917"
SHAPES = ("game", "game_myth", "myth_game")
PAIRS = ("sonnet_gpt", "gpt_sonnet", "sonnet_gemini", "gemini_sonnet")
SONNET = "anthropic/claude-sonnet-4.5"
FAMILY = {"gpt": "openai/gpt-5-nano", "gemini": "google/gemini-3.7-flash"}
RATES = {"anthropic": (3, 15), "openai": (0.05, 0.4), "google": (0.75, 3.75)}
# Mean standard-rate cost per agent in the September informed-noise control
# dyads (recorded usage, negative_only_crossmodel_reasoning_rerun_20260909).
PER_AGENT_USD = {
    "anthropic": {"game": 0.1094, "game_myth": 0.4041, "myth_game": 0.3955},
    "openai": {"game": 0.0070, "game_myth": 0.0566, "myth_game": 0.0570},
    "google": {"game": 0.0171, "game_myth": 0.1116, "myth_game": 0.1166},
}
# Inputs that legitimately differ from the homogeneous September control cell.
MODEL_ONLY_KEYS = {"model", "agent_models", "llm_request", "replicate_id"}


def _quiet_combinations(name):
    with contextlib.redirect_stdout(io.StringIO()):
        return load_combinations(name, str(CONFIG))


def plan():
    jobs = []
    for shape in SHAPES:
        reference = [
            c for c in _quiet_combinations(f"negative_only_reasoning_rerun_dyad_{shape}_claude_n5")
            if c["game_params_name"].endswith(("negative_game_r3", "negative_twotask_r3")) and c["replicate_id"] == 0
        ]
        assert len(reference) == 1, shape
        reference_inputs = {k: v for k, v in reference[0]["comparison_inputs"].items() if k not in MODEL_ONLY_KEYS}
        for pair in PAIRS:
            name = f"mixed_dyad_{shape}_{pair}_n3"
            combos = _quiet_combinations(name)
            assert len(combos) == 3, name
            first, second = pair.split("_")
            expected_models = {
                "Agent_1": SONNET if first == "sonnet" else FAMILY[first],
                "Agent_2": SONNET if second == "sonnet" else FAMILY[second],
            }
            expected_replicates = [0, 2, 4] if first == "sonnet" else [1, 3, 5]
            assert [c["replicate_id"] for c in combos] == expected_replicates, name
            for i, c in enumerate(combos):
                assert c["agent_models"] == expected_models, (name, c["agent_models"])
                assert c["game_params"]["num_agents"] == 2 and c["game_params"]["pairing_mode"] == "fixed"
                request = c["request_plan"].as_dict()
                assert is_mixed_plan(request) and request["model"] == c["model"]
                for agent_id, model in expected_models.items():
                    agent_request = request["agents"][agent_id]
                    assert agent_request["model"] == model
                    assert agent_request["policy"] == EXPECTED_POLICIES[model], (name, agent_id)
                actual_inputs = {k: v for k, v in c["comparison_inputs"].items() if k not in MODEL_ONLY_KEYS}
                differing = sorted(k for k in set(actual_inputs) | set(reference_inputs) if actual_inputs.get(k) != reference_inputs.get(k))
                assert not differing, (name, "non-model inputs differ from September control", differing)
                assert c["game_params"].get("defector_ratio", 0) == 0
                assert c["game_params"].get("random_defection_probability", 0) == 0
                game, _ = build_noisy_protocol(c, i)
                assert len(game.defector_agent_ids) == 0 and game.random_defection_probability == 0
                assert not game.punishment_enabled
                jobs.append((name, i, c, expected_output_path(c, name, i, OUTPUT)))
    assert len(jobs) == 36 and len({str(j[3]) for j in jobs}) == 36
    # Longer two-task jobs first; interleave compositions.
    jobs.sort(key=lambda j: (0 if "myth" in j[2]["task_order"] else 1, j[1], PAIRS.index(pair_of(j[0]))))
    return jobs


def pair_of(name):
    for shape in sorted(SHAPES, key=len, reverse=True):
        prefix = f"mixed_dyad_{shape}_"
        if name.startswith(prefix):
            return name[len(prefix):-len("_n3")]
    raise ValueError(name)


def estimate(jobs):
    total = {"anthropic": 0.0, "openai": 0.0, "google": 0.0}
    for name, _, c, _ in jobs:
        shape = "_".join(c["task_order"])
        for agent_request in c["request_plan"].as_dict()["agents"].values():
            total[agent_request["provider"]] += PER_AGENT_USD[agent_request["provider"]][shape]
    return total


def audit(job):
    name, i, c, path = job
    check_existing_final(path, c)
    d = json.loads(path.read_text())
    m = d["run_metadata"]
    request = c["request_plan"].as_dict()
    assert m["defector_count"] == 0 and m["random_defection_probability"] == 0
    assert not m["code_dirty"]
    assert m["llm_request"] == request and m["llm_provider"] == "mixed"
    assert m["agent_models"] == c["agent_models"]
    assert m["noise_config"] == c["game_params"]["noise_config"]
    assert set(d["agents"]) == set(request["agents"])
    calls = 0
    cost = {"anthropic": 0.0, "openai": 0.0, "google": 0.0}
    for agent_id, a in d["agents"].items():
        expected = request["agents"][agent_id]
        assert a["model"] == expected["model"], (agent_id, a["model"])
        provider = expected["provider"]
        ir, orr = RATES[provider]
        for e in a.get("interaction_history", []):
            r = e.get("response") or {}
            if r.get("response_source", "llm") != "llm":
                continue
            u = r.get("usage") or {}
            assert u.get("request_settings") == expected, (name, agent_id)
            assert u.get("outcome") == "complete" and u.get("finish_reason") not in TRUNCATION_REASONS
            calls += 1
            output = (u.get("output_tokens") or 0) + ((u.get("reasoning_tokens") or 0) if provider == "google" else 0)
            cost[provider] += ((u.get("input_tokens") or 0) * ir + output * orr) / 1e6
    return {
        "path": str(path.relative_to(ROOT)),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "set": name,
        "agent_models": c["agent_models"],
        "task_order": "_".join(c["task_order"]),
        "replicate_id": c["replicate_id"],
        "calls": calls,
        "standard_rate_usd_by_provider": cost,
        "standard_rate_usd": sum(cost.values()),
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workers", type=int, default=6)
    p.add_argument("--execute", action="store_true")
    p.add_argument("--audit-only", action="store_true")
    p.add_argument("--smoke", action="store_true", help="only the first game-only replicate of each composition (2 runs)")
    args = p.parse_args()
    assert 1 <= args.workers <= 12
    jobs = plan()
    if args.smoke:
        jobs = [j for j in jobs if j[0] in {"mixed_dyad_game_sonnet_gpt_n3", "mixed_dyad_game_gemini_sonnet_n3"} and j[1] == 0]
        assert len(jobs) == 2
    pending, receipts = [], []
    for j in jobs:
        if j[3].exists():
            receipts.append(audit(j))
        else:
            pending.append(j)
    est = estimate(pending)
    print(f"VALIDATED N={len(jobs)} DYADS_ONLY CROSS_FAMILY=1 NO_DEFECTORS=1 EXISTING={len(receipts)} PENDING={len(pending)}", flush=True)
    print(
        f"MODEL=mixed(sonnet+gpt,sonnet+gemini) N={len(pending)} WORKERS={args.workers} "
        f"EST_COST=${sum(est.values()):.2f} (anthropic ${est['anthropic']:.2f}, openai ${est['openai']:.2f}, google ${est['google']:.2f}; +20% allowance ${1.2*sum(est.values()):.2f})",
        flush=True,
    )
    if args.audit_only:
        assert not pending
    elif not args.execute:
        return
    if args.execute and pending:
        assert not subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip(), "Clean checkout required"
        os.environ["HF_DATASET_AUTO_UPLOAD"] = "0"
        os.environ["TRUST_BATCH_QUIET"] = "1"
        logdir = str(ROOT / "data/json/noise_experiments" / OUTPUT / "worker_logs")
        workers = args.workers
        for attempt in range(1, 11):
            if not pending:
                break
            failed = []
            quota_exhausted = False
            with ProcessPoolExecutor(max_workers=workers) as pool:
                futures = {pool.submit(run_missing_job, j[2], j[0], j[1], OUTPUT, logdir): j for j in pending}
                for f in as_completed(futures):
                    j = futures[f]
                    if f.cancelled():
                        failed.append(j)
                        continue
                    try:
                        result = f.result()
                        if not result.get("success") and is_exhausted_quota(result.get("error", "")):
                            quota_exhausted = True
                            for queued in futures:
                                queued.cancel()
                            print("BILLING EXHAUSTED: canceling queued jobs; no further retry passes", flush=True)
                        if not result.get("success"):
                            raise RuntimeError(f"Worker failed; inspect {result.get('worker_log')}: {result.get('error')}")
                        receipt = audit(j)
                        receipts.append(receipt)
                        print(f"COMPLETE {len(receipts)}/{len(jobs)} {j[0]} index={j[1]} cost=${receipt['standard_rate_usd']:.3f}", flush=True)
                    except Exception as e:
                        print(f"FAILED {j[0]} index={j[1]} {type(e).__name__}: {e}", flush=True)
                        # Never silently resample a final that fails scientific validation.
                        if j[3].exists():
                            raise
                        failed.append(j)
            if quota_exhausted:
                raise RuntimeError("Provider credits exhausted; top up before resuming. Completed finals preserved.")
            pending = failed
            if pending:
                if attempt == 10:
                    raise RuntimeError(f"{len(pending)} runs failed after ten attempts")
                workers = 1
                print(f"CONTINUATION PENDING={len(pending)} WORKERS=1 ATTEMPT={attempt+1}", flush=True)
                time.sleep(min(60, 2 ** attempt))
    by_provider = {k: sum(r["standard_rate_usd_by_provider"][k] for r in receipts) for k in RATES}
    target = ROOT / "data/json/noise_experiments" / OUTPUT / ("smoke_receipt.json" if args.smoke else "completion_receipt.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps({
        "runs": len(receipts),
        "standard_rate_usd": sum(r["standard_rate_usd"] for r in receipts),
        "standard_rate_usd_by_provider": by_provider,
        "finals": receipts,
    }, indent=2) + "\n")
    print(f"AUDIT PASSED {len(receipts)}/{len(jobs)}; cost=${sum(by_provider.values()):.2f} {by_provider}; receipt={target}", flush=True)


if __name__ == "__main__":
    main()

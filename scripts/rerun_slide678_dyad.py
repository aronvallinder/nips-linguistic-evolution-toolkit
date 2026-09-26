"""Guarded two-agent counterpart of the seven-cell slide-678 rerun."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from contextlib import redirect_stderr, redirect_stdout
import hashlib
import json
from pathlib import Path
import statistics
import sys
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import rerun_slide678 as population
from src.experiment_condition import condition_from_run, digest, read_final_run
from src.llm_settings import RequestPlan
from src.simulation import run_simulation


NUM_AGENTS = 2
NUM_TURNS = 10
RUNS = 35
CALLS = RUNS * NUM_AGENTS * NUM_TURNS
ESTIMATE_USD = 10
DEFAULT_OUTPUT = ROOT / "data/json/noise_experiments/slide678_dyad_rerun_20260917"


def source_hashes():
    files = [Path(__file__), Path(population.__file__), ROOT / "experiments/run_phase3_seeded_cells.py"]
    files += [p for folder in ("src", "games") for p in sorted((ROOT / folder).glob("*.py"))]
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}


def prepare():
    source = population.prepare()
    combos = source["combos"]
    for combo in combos:
        combo["game_params"]["num_agents"] = NUM_AGENTS
    return {
        "version": 1,
        "design": "two-agent counterpart of slide678_rerun_20260916",
        "request": source["request"],
        "combos": combos,
        "source_hashes": source_hashes(),
        "estimate_usd": ESTIMATE_USD,
        "preserved_from_population_rerun": [
            "seven condition labels and exact donor texts",
            "five donor/run replicates per condition",
            "ten game-only rounds",
            "myth-only context with identical seed reinjected each round",
            "no accumulated game/history block",
            "negative-$5 communication noise",
            "pinned native Anthropic September profile",
        ],
        "changed_from_population_rerun": [
            "two agents in one repeated dyad instead of eight agents in rotating dyads",
            "twenty decisions per run instead of eighty",
            "$150 joint-resource ceiling instead of $600",
        ],
    }


def validate_memory(data, combo):
    if data["task_order"] != ["game"] or [row["round"] for row in data["conversation_history"]] != list(range(1, 11)):
        raise ValueError("Not a complete ten-round game-only final")
    if len(data["agents"]) != NUM_AGENTS:
        raise ValueError("Wrong population size")
    seeded = combo["seed_type"] != "baseline"
    game, _ = population.game_and_writer(combo)
    game.configure_agents(list(data["agents"]), data["run_metadata"]["agent_names"])
    from types import SimpleNamespace
    for agent_id, agent in data["agents"].items():
        prefix = [{"role": "system", "content": game.get_system_prompt(agent_id, SimpleNamespace(initial_bias=""))}]
        if seeded:
            prefix += [
                {"role": "user", "content": combo["seed_user_prompt"]},
                {"role": "assistant", "content": combo["seed_text"]},
            ]
        rounds = []
        for event in agent["interaction_history"]:
            messages = event["messages_sent"]
            if messages[:-1] != prefix or messages[-1] != {"role": "user", "content": event["prompt"]}:
                raise ValueError(f"Context mismatch: {combo['seed_type']} {agent_id}")
            if event["metadata"]["task"] != "game":
                raise ValueError("Unexpected myth-generation call")
            if "error" not in event:
                rounds.append(event["metadata"]["round"])
        if rounds != list(range(1, 11)):
            raise ValueError(f"Missing/duplicated agent decisions: {agent_id}: {rounds}")


def final_path(output, combo):
    return output / combo["seed_type"] / f"rep{combo['rep']:02d}.json"


def verify_final(path, plan, combo):
    data = read_final_run(path)
    condition = condition_from_run(data)
    if data["run_metadata"].get("slide678_dyad_plan_sha256") != digest(plan):
        raise ValueError(f"Final belongs to a different frozen plan: {path}")
    identity = f"{combo['seed_type']}/rep{combo['rep']:02d}"
    if condition["llm"] != plan["request"] or condition["replicate"]["identity"] != identity:
        raise ValueError(f"Final request/identity mismatch: {path}")
    validate_memory(data, combo)
    return data


def run_one(plan, combo, output):
    path = final_path(output, combo)
    if path.exists():
        verify_final(path, plan, combo)
        return {"status": "existing", "path": str(path)}
    path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint = path.with_suffix(".checkpoint.json")
    game, writer = population.game_and_writer(combo)
    baseline = combo["seed_type"] == "baseline"
    try:
        with path.with_suffix(".log").open("a") as log, redirect_stdout(log), redirect_stderr(log):
            result = run_simulation(
                game=game,
                model=combo["model"],
                temperature="default",
                num_turns=NUM_TURNS,
                num_agents=NUM_AGENTS,
                memory_capacity=combo["game_params"]["memory_capacity"],
                agent_biases="",
                myth_writer=writer,
                task_order=["game"],
                checkpoint_path=str(checkpoint),
                checkpoint_every=1,
                resume_from=str(checkpoint) if checkpoint.exists() else None,
                seed_myth=None if baseline else combo["seed_text"],
                seed_user_prompt=None if baseline else combo["seed_user_prompt"],
                chat_memory_mode="myth_only",
                seed_reinject=not baseline,
                request_plan=RequestPlan(json.dumps(plan["request"])),
                run_identity=f"{combo['seed_type']}/rep{combo['rep']:02d}",
                game_response_retry_policy="repeat_same_prompt_once",
                run_metadata_extra={
                    "slide678_dyad_plan_sha256": digest(plan),
                    "phase3_seed_type": combo["seed_type"],
                    "phase3_rep": combo["rep"],
                    "phase3_seed_meta": combo["seed_meta"],
                    "population_counterpart_final": combo["historical_final"],
                },
            )
            validate_memory(result.to_state(), combo)
            result.save_state(str(path))
            verify_final(path, plan, combo)
        return {"status": "complete", "path": str(path)}
    except Exception:
        return {"status": "failed", "path": str(path), "error": traceback.format_exc()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["prepare", "run", "audit"])
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--workers", type=int, default=20)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    if args.workers < 1 or (args.limit is not None and args.limit < 1):
        parser.error("workers and limit must be positive")
    plan_path = args.output / "plan.json"
    if args.mode == "prepare":
        plan = prepare()
        args.output.mkdir(parents=True, exist_ok=True)
        if plan_path.exists() and json.loads(plan_path.read_text()) != plan:
            raise ValueError("Refusing to overwrite a different frozen plan")
        if not plan_path.exists():
            plan_path.write_text(json.dumps(plan, indent=2) + "\n")
        print(f"Prepared {RUNS} runs / {CALLS} calls; plan={plan_path}; sha256={digest(plan)}")
        print(json.dumps(plan["request"], indent=2))
        return

    plan = json.loads(plan_path.read_text())
    if source_hashes() != plan["source_hashes"]:
        raise ValueError("Implementation changed since plan was frozen")
    pending, results = [], {}
    for combo in plan["combos"]:
        path = final_path(args.output, combo)
        if path.exists():
            data = verify_final(path, plan, combo)
            results.setdefault(combo["seed_type"], []).append(sum(data["conversation_history"][-1]["balances"].values()))
        else:
            pending.append(combo)
    print(f"Validated complete={RUNS-len(pending)}/{RUNS}; pending={len(pending)}", flush=True)
    if args.mode == "audit":
        for cell, values in results.items():
            sd = statistics.stdev(values) if len(values) > 1 else float("nan")
            print(f"{cell}: n={len(values)} mean={statistics.mean(values):.2f} sd={sd:.2f}")
        return
    selected = pending[:args.limit] if args.limit else pending
    print(
        f"Resolved MODEL={plan['request']['provider_model']} N={len(selected)} "
        f"WORKERS={args.workers} EST_COST=${ESTIMATE_USD*len(selected)/RUNS:.2f}",
        flush=True,
    )
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(run_one, plan, combo, args.output) for combo in selected]
        failed = False
        for future in as_completed(futures):
            outcome = future.result()
            print(json.dumps(outcome), flush=True)
            failed |= outcome["status"] == "failed"
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

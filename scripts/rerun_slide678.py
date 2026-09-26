"""Guarded rerun of the seven historical slide-678 transplant cells.

Prepare freezes the existing donors, prompts and request policy; run only consumes
that plan. No donor generation, content deletion, or automatic resampling.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from contextlib import redirect_stdout, redirect_stderr
import hashlib
import json
from pathlib import Path
import statistics
import sys
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiments.run_phase3_seeded_cells import _load_config, _make_combo
from games.trust_game_noisy import TrustGameNoisy
from src.experiment_condition import condition_from_run, digest, read_final_run
from src.llm_settings import RequestPlan, resolve_request_plan
from src.myth_writer import MythWriter
from src.simulation import run_simulation
from src.utils import DIRECT_MODEL_ALIASES

PARAMS = "phase3_8agent_anon_neg5_myth_only"
CELLS = {
    "baseline": "phase3_baseline",
    "s_end_plus": "phase3_seeded",
    "s_start": "phase3_seeded",
    "s_end_minus": "phase5_seeded",
    "s_filler": "phase5_seeded",
    "s_end_plus_gemini": "phase6_seeded",
    "s_end_plus_gpt": "phase6_seeded",
}
DEFAULT_OUTPUT = ROOT / "data/json/noise_experiments/slide678_rerun_20260916"


def source_hashes():
    files = [Path(__file__), ROOT / "experiments/run_phase3_seeded_cells.py"]
    files += [p for folder in ("src", "games") for p in sorted((ROOT / folder).glob("*.py"))]
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}


def game_and_writer(combo):
    p = combo["game_params"]
    game = TrustGameNoisy(
        endowment=p["endowment"], multiplier=p["multiplier"],
        system_prompt_template=combo["template"],
        personas={f"Agent_{i+1}": {"description": "neutral", "system_addition": ""} for i in range(p["num_agents"])},
        round1_investor_template=combo["round1_investor"],
        round1_trustee_template=combo["round1_trustee"],
        later_investor_template=combo["later_investor"],
        later_trustee_template=combo["later_trustee"],
        noise_config=p["noise_config"], noise_semantics="communication",
        other_player_names=p["other_player_names"], history_policy=p["history_policy"],
        self_history_window=p["self_history_window"], coplayer_history_window=p["coplayer_history_window"],
        show_agent_names=p["show_agent_names"],
    )
    writer = MythWriter(myth_topic="anything", round1_template=combo["myth_default"], later_rounds_template=combo["myth_later"])
    return game, writer


def prepare():
    config = _load_config()
    manifest = json.loads((ROOT / "data/phase3/seed_manifest.json").read_text())
    request = resolve_request_plan(config["base_models"]["claude_sonnet_45"], config["llm_profiles"]["september8_claude"], DIRECT_MODEL_ALIASES)
    combos = []
    # Interleave cells so the initial two jobs are baseline and late Sonnet.
    for rep in range(5):
        for cell, folder in CELLS.items():
            seed = {"text": ""} if cell == "baseline" else manifest["seeds"][cell][rep]
            combo = _make_combo(cell, seed, rep, config, PARAMS, "claude_sonnet_45")
            directory = ROOT / f"data/json/noise_experiments/{folder}/phase3_seeded_{cell}_{PARAMS}/claude-sonnet-4.5/game/default"
            candidates = [p for p in directory.glob(f"*rep{rep:02d}*.json") if not p.name.endswith((".results.json", ".checkpoint.json", ".error.json"))]
            if len(candidates) != 1:
                raise ValueError(f"Expected exactly one historical final: {cell}/{rep}: {candidates}")
            old = read_final_run(candidates[0])
            expected_seed = None if cell == "baseline" else seed["text"]
            if old["run_metadata"]["seed_myth"] != expected_seed:
                raise ValueError(f"Donor manifest changed: {cell}/{rep}")
            validate_memory(old, combo)
            combo["historical_final"] = str(candidates[0].relative_to(ROOT))
            combo["historical_sha256"] = hashlib.sha256(candidates[0].read_bytes()).hexdigest()
            combos.append(combo)
    return {"version": 1, "request": request.as_dict(), "combos": combos,
            "source_hashes": source_hashes(), "estimate_usd": 60,
            "differences_from_historical": [
                "Pinned native Anthropic September profile; historical request policy incompletely recorded.",
                "Current guarded role/JSON validation, same-prompt retry once; no corrective prompt.",
                "Fresh unseeded balanced pairings and communication-noise draws, as in original runner.",
            ]}


def validate_memory(data, combo):
    if data["task_order"] != ["game"] or [r["round"] for r in data["conversation_history"]] != list(range(1, 11)):
        raise ValueError("Not a complete ten-round game-only final")
    if len(data["agents"]) != 8:
        raise ValueError("Wrong population size")
    seeded = combo["seed_type"] != "baseline"
    game, _ = game_and_writer(combo)
    game.configure_agents(list(data["agents"]), data["run_metadata"]["agent_names"])
    for agent_id, agent in data["agents"].items():
        # get_system_prompt only reads agent.initial_bias; preserve the actual renderer.
        from types import SimpleNamespace
        system = game.get_system_prompt(agent_id, SimpleNamespace(initial_bias=""))
        prefix = [{"role": "system", "content": system}]
        if seeded:
            prefix += [{"role": "user", "content": combo["seed_user_prompt"]}, {"role": "assistant", "content": combo["seed_text"]}]
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
    if data["run_metadata"].get("slide678_plan_sha256") != digest(plan):
        raise ValueError(f"Final belongs to a different frozen plan: {path}")
    if condition["llm"] != plan["request"] or condition["replicate"]["identity"] != f"{combo['seed_type']}/rep{combo['rep']:02d}":
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
    # Resume only complete-round checkpoints, never partial-round error snapshots.
    game, writer = game_and_writer(combo)
    baseline = combo["seed_type"] == "baseline"
    try:
        with path.with_suffix(".log").open("a") as log, redirect_stdout(log), redirect_stderr(log):
            result = run_simulation(
                game=game, model=combo["model"], temperature="default", num_turns=10,
                num_agents=8, memory_capacity=combo["game_params"]["memory_capacity"],
                agent_biases="", myth_writer=writer, task_order=["game"],
                checkpoint_path=str(checkpoint), checkpoint_every=1,
                resume_from=str(checkpoint) if checkpoint.exists() else None,
                seed_myth=None if baseline else combo["seed_text"],
                seed_user_prompt=None if baseline else combo["seed_user_prompt"],
                chat_memory_mode="myth_only", seed_reinject=not baseline,
                request_plan=RequestPlan(json.dumps(plan["request"])),
                run_identity=f"{combo['seed_type']}/rep{combo['rep']:02d}",
                game_response_retry_policy="repeat_same_prompt_once",
                run_metadata_extra={"slide678_plan_sha256": digest(plan),
                    "phase3_seed_type": combo["seed_type"], "phase3_rep": combo["rep"],
                    "phase3_seed_meta": combo["seed_meta"], "historical_final": combo["historical_final"]},
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
    parser.add_argument("--workers", type=int, default=4)
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
        print(f"Prepared 35 runs / 2800 calls; plan={plan_path}; sha256={digest(plan)}")
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
    print(f"Validated complete={35-len(pending)}/35; pending={len(pending)}", flush=True)
    if args.mode == "audit":
        for cell, values in results.items():
            print(f"{cell}: n={len(values)} mean={statistics.mean(values):.2f} sd={statistics.stdev(values) if len(values)>1 else float('nan'):.2f}")
        return
    selected = pending[:args.limit] if args.limit else pending
    print(f"Resolved MODEL={plan['request']['provider_model']} N={len(selected)} WORKERS={args.workers} EST_COST=${60*len(selected)/35:.2f}", flush=True)
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(run_one, plan, c, args.output) for c in selected]
        failed = False
        for future in as_completed(futures):
            result = future.result()
            print(json.dumps(result), flush=True)
            failed |= result["status"] == "failed"
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

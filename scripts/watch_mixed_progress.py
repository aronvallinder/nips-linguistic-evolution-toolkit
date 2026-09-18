"""Maintain a plain progress.log for a mixed-model batch: one line per run, N of total.

Reads the launcher's plan for the expected job list, then every ``--interval``
seconds rewrites ``<run root>/progress.log``:

    DONE 12/90 | 1 Gemini + 7 GPT | game | replicate 3/5 | 10/10 rounds | $0.07
    RUNNING     | 1 GPT + 7 Sonnet | myth_game | replicate 1/5 | 4/10 rounds
    ...
    SUMMARY: 12/90 done, 8 running, 70 queued, cost so far $9.31

No API calls; safe to run beside the batch.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
from pathlib import Path
import re
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

RATES = {"anthropic": (3, 15), "openai": (0.05, 0.4), "google": (0.75, 3.75)}
SHORT = {"anthropic/claude-sonnet-4.5": "Sonnet", "openai/gpt-5-nano": "GPT", "google/gemini-3.7-flash": "Gemini"}


def composition(agent_models):
    counts = {}
    for model in agent_models.values():
        counts[SHORT[model]] = counts.get(SHORT[model], 0) + 1
    return " + ".join(f"{n} {family}" for family, n in counts.items())


def cost_and_rounds(path):
    data = json.loads(path.read_text())
    cost = 0.0
    for agent in data.get("agents", {}).values():
        for event in agent.get("interaction_history", []):
            usage = (event.get("response") or {}).get("usage") or {}
            settings = usage.get("request_settings") or {}
            provider = settings.get("provider")
            if provider not in RATES:
                continue
            ir, orr = RATES[provider]
            out = (usage.get("output_tokens") or 0) + ((usage.get("reasoning_tokens") or 0) if provider == "google" else 0)
            cost += ((usage.get("input_tokens") or 0) * ir + out * orr) / 1e6
    return len(data.get("conversation_history", [])), cost


def rounds_from_log(path):
    if not path.exists():
        return 0
    return len(set(re.findall(r"^Round (\d+)\s*$", path.read_text(errors="ignore"), re.M)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--launcher", choices=["populations", "dyads"], default="populations")
    parser.add_argument("--interval", type=int, default=60)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    if args.launcher == "populations":
        from scripts import run_mixed_model_populations as launcher
    else:
        from scripts import run_mixed_model_dyads as launcher
    with contextlib.redirect_stdout(io.StringIO()):
        jobs = launcher.plan()
    total = len(jobs)
    run_root = ROOT / "data/json/noise_experiments" / launcher.OUTPUT
    replicates = {}
    for name, _, combo, _ in jobs:
        replicates.setdefault(name, []).append(combo["replicate_id"])
    while True:
        done, running, queued = [], [], 0
        cost = 0.0
        for name, index, combo, path in jobs:
            reps = replicates[name]
            label = f"{composition(combo['agent_models'])} | {'_'.join(combo['task_order'])} | replicate {reps.index(combo['replicate_id']) + 1}/{len(reps)}"
            rounds_total = combo["game_params"]["num_turns"]
            if path.exists():
                rounds, run_cost = cost_and_rounds(path)
                cost += run_cost
                done.append((path.stat().st_mtime, f"{label} | {rounds}/{rounds_total} rounds | ${run_cost:.2f}"))
            else:
                log = path.with_suffix(".log")
                if log.exists():
                    running.append(f"RUNNING     | {label} | {min(rounds_from_log(log), rounds_total)}/{rounds_total} rounds")
                else:
                    queued += 1
        done.sort()
        lines = [f"DONE {i + 1:>3}/{total} | {text}" for i, (_, text) in enumerate(done)]
        lines += running
        lines.append(f"SUMMARY: {len(done)}/{total} done, {len(running)} running, {queued} queued, cost so far ${cost:.2f} | updated {time.strftime('%Y-%m-%d %H:%M:%S')}")
        run_root.mkdir(parents=True, exist_ok=True)
        (run_root / "progress.log").write_text("\n".join(lines) + "\n")
        if args.once:
            print(lines[-1])
            return
        time.sleep(args.interval)


if __name__ == "__main__":
    main()

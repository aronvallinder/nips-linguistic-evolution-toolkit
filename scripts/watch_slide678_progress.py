"""Maintain a one-line-per-run progress file for the slide-678 rerun."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import time


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUN_ROOT = ROOT / "data/json/noise_experiments/slide678_rerun_20260916"
CELL_LABELS = {
    "baseline": "No inherited text (game-only baseline)",
    "s_filler": "Unrelated Wikipedia filler text",
    "s_start": "Early Sonnet myth (taken from round 1)",
    "s_end_plus": "Late high-cooperation Sonnet myth (taken from round 10)",
    "s_end_minus": "Late low-cooperation myth (taken from round 10)",
    "s_end_plus_gemini": "Late high-cooperation Gemini myth (taken from round 10)",
    "s_end_plus_gpt": "Late high-cooperation GPT myth (taken from round 10)",
}
def run_files(run_root: Path, suffix: str) -> list[Path]:
    return sorted(run_root.glob(f"*/*{suffix}"))


def usage_and_rounds(path: Path) -> tuple[int, int, float]:
    data = json.loads(path.read_text())
    usages = [
        (event.get("response") or {}).get("usage") or {}
        for agent in data.get("agents", {}).values()
        for event in agent.get("interaction_history", [])
    ]
    cost = sum(
        (usage.get("input_tokens") or 0) * 3e-6
        + (usage.get("output_tokens") or 0) * 15e-6
        for usage in usages
    )
    return len(data.get("conversation_history", [])), len(usages), cost


def snapshot(run_root: Path) -> tuple[str, str, bool]:
    finals = run_files(run_root, "rep??.json")
    checkpoints = run_files(run_root, ".checkpoint.json")
    status_path = run_root / "supervisor_status.json"
    status = json.loads(status_path.read_text()) if status_path.exists() else {"status": "unknown"}

    active = []
    completed = []
    final_paths = set(finals)
    for path in finals:
        rounds, calls, cost = usage_and_rounds(path)
        rep = int(path.stem.removeprefix("rep")) + 1
        completed.append((path.parent.name, rep, rounds, calls, cost))
    for path in checkpoints:
        final = path.with_name(path.name.replace(".checkpoint.json", ".json"))
        if final in final_paths:
            continue
        rounds, calls, cost = usage_and_rounds(path)
        rep = int(path.stem.split("rep")[-1].split(".")[0]) + 1
        active.append((path.parent.name, rep, rounds, calls, cost))

    status_id = status.get("status", "unknown")
    signature = json.dumps(
        {
            "status": status_id,
            "completed": completed,
            "active": active,
        },
        sort_keys=True,
    )
    lines = []
    for cell, rep, rounds, calls, cost in completed:
        lines.append(
            f"COMPLETED | {CELL_LABELS.get(cell, cell)} | replicate {rep}/5 | "
            f"{rounds}/10 rounds | {calls}/80 decisions | recorded cost ${cost:.2f}"
        )
    for cell, rep, rounds, calls, cost in active:
        lines.append(
            f"ACTIVE | {CELL_LABELS.get(cell, cell)} | replicate {rep}/5 | "
            f"{rounds}/10 rounds | {calls}/80 decisions | recorded cost ${cost:.2f}"
        )
    line = "\n".join(lines)
    terminal = status.get("status") in {"complete", "stopped", "approval_required"}
    return signature, line, terminal


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, default=DEFAULT_RUN_ROOT)
    parser.add_argument("--interval", type=int, default=10)
    parser.add_argument("--decisions-per-run", type=int, default=80)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    log_path = args.run_root / "progress.log"
    previous = None
    while True:
        signature, line, terminal = snapshot(args.run_root)
        if args.decisions_per_run != 80:
            line = line.replace("/80 decisions", f"/{args.decisions_per_run} decisions")
        if signature != previous:
            temporary = log_path.with_suffix(".log.tmp")
            temporary.write_text(line + ("\n" if line else ""), encoding="utf-8")
            temporary.replace(log_path)
            print(line, flush=True)
            previous = signature
        if args.once or terminal:
            return
        try:
            time.sleep(args.interval)
        except KeyboardInterrupt:
            return


if __name__ == "__main__":
    main()

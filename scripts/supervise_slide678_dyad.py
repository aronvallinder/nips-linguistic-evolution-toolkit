"""Supervise the authorized two-agent slide-678 counterpart."""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import statistics
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import rerun_slide678_dyad as runner
from src.experiment_condition import digest


def write_status(output, status, **extra):
    value = {"status": status, "updated_at": datetime.now(timezone.utc).isoformat(), **extra}
    target = output / "supervisor_status.json"
    temporary = target.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n")
    temporary.replace(target)
    print(json.dumps(value), flush=True)


def usage_of(data):
    usages = [
        (event.get("response") or {}).get("usage") or {}
        for agent in data["agents"].values()
        for event in agent["interaction_history"]
    ]
    return {
        "calls": len(usages),
        "input_tokens": sum(usage.get("input_tokens") or 0 for usage in usages),
        "output_tokens": sum(usage.get("output_tokens") or 0 for usage in usages),
    }


def audit(output, plan):
    entries, values = [], defaultdict(list)
    for combo in plan["combos"]:
        path = runner.final_path(output, combo)
        if not path.exists():
            continue
        data = runner.verify_final(path, plan, combo)
        usage = usage_of(data)
        usage["standard_rate_usd"] = usage["input_tokens"] * 3e-6 + usage["output_tokens"] * 15e-6
        balance = sum(data["conversation_history"][-1]["balances"].values())
        values[combo["seed_type"]].append(balance)
        entries.append(
            {
                "path": str(path.relative_to(output)),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "cell": combo["seed_type"],
                "rep": combo["rep"],
                "joint_resources": balance,
                **usage,
            }
        )
    cost = sum(entry["standard_rate_usd"] for entry in entries)
    projected = max(runner.ESTIMATE_USD, cost / len(entries) * runner.RUNS * 1.25) if entries else runner.ESTIMATE_USD
    cells = {
        cell: {
            "n": len(cell_values),
            "mean": statistics.mean(cell_values),
            "sd": statistics.stdev(cell_values) if len(cell_values) > 1 else None,
            "values": cell_values,
        }
        for cell, cell_values in values.items()
    }
    return {
        "plan_sha256": digest(plan),
        "completed": len(entries),
        "planned": runner.RUNS,
        "standard_rate_usd": cost,
        "projected_usd_with_margin": projected,
        "cost_caveat": "Recorded calls in finals only; not invoice cost. Failed transport attempts may be unrecorded.",
        "cells": cells,
        "finals": entries,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=runner.DEFAULT_OUTPUT)
    parser.add_argument("--workers", type=int, default=20)
    args = parser.parse_args()
    output = args.output.resolve()
    plan = json.loads((output / "plan.json").read_text())
    lock = output / "supervisor.lock"
    with lock.open("x"):
        pass
    try:
        while True:
            if runner.source_hashes() != plan["source_hashes"]:
                raise RuntimeError("Frozen implementation changed")
            receipt = audit(output, plan)
            if receipt["completed"] == runner.RUNS:
                (output / "completion_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
                write_status(output, "complete", completed=runner.RUNS, standard_rate_usd=receipt["standard_rate_usd"], cells=receipt["cells"])
                return
            if receipt["projected_usd_with_margin"] > 100:
                write_status(output, "approval_required", completed=receipt["completed"], projected_usd=receipt["projected_usd_with_margin"])
                return
            pending = runner.RUNS - receipt["completed"]
            write_status(
                output,
                "running",
                completed=receipt["completed"],
                pending=pending,
                projected_usd=receipt["projected_usd_with_margin"],
                standard_rate_usd=receipt["standard_rate_usd"],
            )
            print(
                f"CONTINUATION: MODEL={plan['request']['provider_model']} PENDING={pending} "
                f"WORKERS={args.workers} ADDED_EST_COST=${receipt['projected_usd_with_margin']-receipt['standard_rate_usd']:.2f} "
                "REASON=complete authorized dyad matrix",
                flush=True,
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(Path(runner.__file__)),
                    "run",
                    "--output",
                    str(output),
                    "--workers",
                    str(args.workers),
                    "--limit",
                    str(args.workers),
                ],
                cwd=runner.ROOT,
            )
            if result.returncode:
                raise RuntimeError("Batch failed; inspect error snapshots, no automatic resampling")
    except Exception as exc:
        write_status(output, "stopped", error=str(exc))
        raise
    finally:
        lock.unlink()


if __name__ == "__main__":
    main()

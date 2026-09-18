"""Continue the authorized slide-678 matrix after its two live smoke finals.

Stops on failed jobs or a projected cumulative cost above $100. Never resamples
failed runs automatically. Run locally; it writes status and a completion receipt.
"""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import statistics
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import rerun_slide678 as runner
from src.experiment_condition import digest


def write_status(output, status, **extra):
    value = {"status": status, "updated_at": datetime.now(timezone.utc).isoformat(), **extra}
    target = output / "supervisor_status.json"
    temporary = target.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n")
    temporary.replace(target)
    print(json.dumps(value), flush=True)


def usage_of(data):
    usages = [(event.get("response") or {}).get("usage") or {}
              for agent in data["agents"].values() for event in agent["interaction_history"]]
    return {"calls": len(usages),
            "input_tokens": sum(u.get("input_tokens") or 0 for u in usages),
            "output_tokens": sum(u.get("output_tokens") or 0 for u in usages)}


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
        entries.append({"path": str(path.relative_to(output)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                        "cell": combo["seed_type"], "rep": combo["rep"], "joint_resources": balance, **usage})
    cost = sum(e["standard_rate_usd"] for e in entries)
    # Use the larger of original planning allowance and observed mean plus 25%.
    projected = max(60, cost / len(entries) * 35 * 1.25) if entries else 60
    summary = {cell: {"n": len(v), "mean": statistics.mean(v), "sd": statistics.stdev(v) if len(v)>1 else None,
                      "values": v} for cell, v in values.items()}
    return {"plan_sha256": digest(plan), "completed": len(entries), "planned": 35,
            "standard_rate_usd": cost, "projected_usd_with_margin": projected,
            "cost_caveat": "Recorded calls in finals only; not invoice cost. Failed transport attempts may be unrecorded.",
            "cells": summary, "finals": entries}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=runner.DEFAULT_OUTPUT)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--smoke-wait-seconds", type=int, default=3600)
    args = parser.parse_args()
    output = args.output.resolve()
    plan = json.loads((output / "plan.json").read_text())
    # Exclusive creation prevents competing supervisors launching duplicate runs.
    lock = output / "supervisor.lock"
    with lock.open("x"):
        pass
    try:
        write_status(output, "waiting_for_two_smoke_finals")
        deadline = time.monotonic() + args.smoke_wait_seconds
        while not all(runner.final_path(output, c).exists() for c in plan["combos"][:2]):
            if list(output.glob("*/*.error.json")):
                raise RuntimeError("Smoke error snapshot found; inspect before any continuation")
            if time.monotonic() >= deadline:
                raise RuntimeError("Timed out waiting for smoke finals; no further runs launched")
            time.sleep(10)
        while True:
            if runner.source_hashes() != plan["source_hashes"]:
                raise RuntimeError("Frozen implementation changed")
            receipt = audit(output, plan)
            if receipt["completed"] == 35:
                (output / "completion_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
                write_status(output, "complete", completed=35, standard_rate_usd=receipt["standard_rate_usd"], cells=receipt["cells"])
                return
            if receipt["projected_usd_with_margin"] > 100:
                write_status(output, "approval_required", completed=receipt["completed"], projected_usd=receipt["projected_usd_with_margin"])
                return
            remaining = 35 - receipt["completed"]
            write_status(output, "running", completed=receipt["completed"], pending=remaining,
                         projected_usd=receipt["projected_usd_with_margin"], standard_rate_usd=receipt["standard_rate_usd"])
            print(f"CONTINUATION: MODEL={plan['request']['provider_model']} PENDING={remaining} WORKERS={args.workers} "
                  f"ADDED_EST_COST=${receipt['projected_usd_with_margin']-receipt['standard_rate_usd']:.2f} REASON=validated-smoke-or-batch", flush=True)
            # Audit cost and all received contexts between batches. The batch
            # size follows the explicitly selected worker count so higher
            # concurrency is not silently capped by the supervisor.
            result = subprocess.run([sys.executable, str(Path(runner.__file__)), "run", "--output", str(output),
                                     "--workers", str(args.workers), "--limit", str(args.workers)], cwd=runner.ROOT)
            if result.returncode:
                raise RuntimeError("Batch failed; inspect error snapshots, no automatic resampling")
    except Exception as exc:
        write_status(output, "stopped", error=str(exc))
        raise
    finally:
        lock.unlink()


if __name__ == "__main__":
    main()

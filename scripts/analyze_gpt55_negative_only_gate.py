#!/usr/bin/env python3
"""Fail-closed audit of the six-run GPT-5.5 negative-only gate."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import statistics
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.gpt55_gate_contract import HISTORICAL, verify_rerun
from src.experiment_condition import read_final_run
from typing import Any


EXPECTED_BASE = {
    "gpt55_gate_dyad_game": (2, "game", "noisy2_crossmodel_negative_game_r3"),
    "gpt55_gate_dyad_game_myth": (
        2,
        "game_myth",
        "noisy2_crossmodel_negative_twotask_r3",
    ),
    "gpt55_gate_dyad_myth_game": (
        2,
        "myth_game",
        "noisy2_crossmodel_negative_twotask_r3",
    ),
    "gpt55_gate_population_game": (
        8,
        "game",
        "noisy8_crossmodel_negative_game_r3",
    ),
    "gpt55_gate_population_game_myth": (
        8,
        "game_myth",
        "noisy8_crossmodel_negative_twotask_r3",
    ),
    "gpt55_gate_population_myth_game": (
        8,
        "myth_game",
        "noisy8_crossmodel_negative_twotask_r3",
    ),
}
MODEL = "openai/gpt-5.5-2026-04-23"
PROVIDER_MODEL = "gpt-5.5-2026-04-23"
NOISE_CONFIG = {
    "type": "uniform",
    "range": 1.0,
    "direction": "negative",
    "applies_to": "both",
    "inform_agents": True,
}
INPUT_USD_PER_TOKEN = 5.0 / 1_000_000
OUTPUT_USD_PER_TOKEN = 30.0 / 1_000_000


def json_kind(path: Path) -> str:
    if path.name.endswith(".results.json"):
        return "results"
    if path.name.endswith(".checkpoint.json"):
        return "checkpoint"
    if path.name.endswith(".error.json"):
        return "error"
    return "final"


def decisions(run: dict[str, Any], path: Path) -> list[dict[str, float]]:
    rounds = run.get("conversation_history") or []
    if len(rounds) != 10:
        raise RuntimeError(f"{path}: expected 10 complete rounds, found {len(rounds)}")
    rows = []
    for round_entry in rounds:
        for dyad in round_entry.get("dyads") or []:
            sent = float(dyad["sent"])
            received = float(dyad["received"])
            returned = float(dyad["returned"])
            if not 0 <= sent <= 5:
                raise RuntimeError(f"{path}: send outside $0-$5")
            if not 0 <= returned <= received:
                raise RuntimeError(f"{path}: return outside $0-received")
            rows.append(
                {
                    "sent": sent,
                    "sent_communicated": float(dyad["sent_communicated"]),
                    "received": received,
                    "returned": returned,
                }
            )
    return rows


def mean(values: list[float]) -> float | None:
    return statistics.fmean(values) if values else None


def audit_run(
    path: Path,
    expected: tuple[int, str, str],
    replicate_id: int,
) -> dict[str, Any]:
    expected_agents, expected_order, expected_game_params = expected
    run = read_final_run(path)
    metadata = run.get("run_metadata") or {}
    order = "_".join(run.get("task_order") or [])

    experiment = next((f"{name}_r{replicate_id + 1}" for name, cell in EXPECTED_BASE.items() if cell == expected), None)
    if replicate_id not in HISTORICAL or experiment is None:
        raise RuntimeError("Unsupported historical gate cell")
    pinned = "experiment_condition" in metadata
    if pinned:
        condition = verify_rerun(run, experiment)
        effort = condition["llm"]["parameters"].get("reasoning_effort")
    else:
        if any(metadata.get(key) != value for key, value in HISTORICAL[replicate_id].items()):
            raise RuntimeError(f"{path}: code/config do not match the historical gate")
        effort = metadata.get("reasoning_effort")

    assertions = {
        "model": metadata.get("model") == MODEL,
        "provider_model": metadata.get("provider_model") == PROVIDER_MODEL,
        "provider": metadata.get("llm_provider") == "openai",
        "provider_mode": metadata.get("llm_provider_mode") == "direct",
        "reasoning_effort": effort == "low",
        "configured_reasoning_effort": (
            metadata.get("configured_openai_reasoning_effort") == "low"
        ),
        "clean_code": metadata.get("code_dirty") is False,
        "ten_turns": metadata.get("num_turns") == 10,
        "population": metadata.get("num_agents") == expected_agents,
        "task_order": order == expected_order,
        "game_params": metadata.get("game_params_name") == expected_game_params,
        "replicate": metadata.get("replicate_id") == replicate_id,
        "noise": metadata.get("noise_config") == NOISE_CONFIG,
        "noise_seed": metadata.get("noise_seed") == 202608250 + replicate_id,
        "pairing_seed": metadata.get("pairing_seed") == 202608250 + replicate_id,
        "no_fixed_defectors": metadata.get("defector_count") == 0,
        "no_random_defection": (
            float(metadata.get("random_defection_probability", 0)) == 0
        ),
        "no_punishment": metadata.get("punishment_enabled") is False,
    }
    failed = [name for name, passed in assertions.items() if not passed]
    if failed:
        raise RuntimeError(f"{path}: failed provenance gates: {', '.join(failed)}")

    decision_rows = decisions(run, path)
    expected_decisions = 10 if expected_agents == 2 else 40
    if len(decision_rows) != expected_decisions:
        raise RuntimeError(
            f"{path}: expected {expected_decisions} dyad decisions, "
            f"found {len(decision_rows)}"
        )

    interactions = [
        interaction
        for agent in (run.get("agents") or {}).values()
        for interaction in agent.get("interaction_history") or []
    ]
    interaction_errors = [item for item in interactions if item.get("error")]
    usage = [
        ((item.get("response") or {}).get("usage") or {})
        for item in interactions
    ]
    input_tokens = sum(int(item.get("input_tokens") or 0) for item in usage)
    output_tokens = sum(int(item.get("output_tokens") or 0) for item in usage)
    reasoning_tokens = sum(int(item.get("reasoning_tokens") or 0) for item in usage)
    positive_receipts = [item for item in decision_rows if item["received"] > 0]
    balances = (run.get("game_data") or {}).get("balances") or {}

    return {
        "path": str(path),
        "model": metadata["model"],
        "provider_model": metadata["provider_model"],
        "reasoning_effort": effort,
        "code_commit": metadata.get("code_commit"),
        "code_dirty": metadata.get("code_dirty"),
        "config_sha256": metadata.get("config_sha256"),
        "num_agents": expected_agents,
        "task_order": order,
        "game_params_name": expected_game_params,
        "replicate_id": metadata["replicate_id"],
        "noise_seed": metadata["noise_seed"],
        "pairing_seed": metadata["pairing_seed"],
        "rounds": 10,
        "dyad_decisions": len(decision_rows),
        "llm_interactions": len(interactions),
        "interaction_errors": len(interaction_errors),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "reasoning_tokens": reasoning_tokens,
        "estimated_cost_usd": (
            input_tokens * INPUT_USD_PER_TOKEN
            + output_tokens * OUTPUT_USD_PER_TOKEN
        ),
        "mean_send_fraction": mean([item["sent"] / 5 for item in decision_rows]),
        "mean_communicated_send_fraction": mean(
            [item["sent_communicated"] / 5 for item in decision_rows]
        ),
        "zero_send_rate": mean(
            [float(item["sent"] == 0) for item in decision_rows]
        ),
        "max_send_rate": mean(
            [float(item["sent"] == 5) for item in decision_rows]
        ),
        "mean_return_proportion_positive": mean(
            [item["returned"] / item["received"] for item in positive_receipts]
        ),
        "zero_receipt_rate": mean(
            [float(item["received"] == 0) for item in decision_rows]
        ),
        "final_mean_balance": mean([float(value) for value in balances.values()]),
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def audit_gate(input_directory: Path, output_directory: Path, replicate_id: int):
    if replicate_id not in HISTORICAL:
        raise ValueError("replicate_id must be 0 or 1")
    all_json = list(input_directory.rglob("*.json"))
    inventory = {
        kind: sum(json_kind(path) == kind for path in all_json)
        for kind in ("final", "results", "checkpoint", "error")
    }
    final_paths = sorted(path for path in all_json if json_kind(path) == "final")
    if inventory["final"] != 6:
        raise RuntimeError(
            f"Expected exactly 6 final full-state JSONs, found {inventory['final']}"
        )

    rows = []
    seen_paths = set()
    stage_number = replicate_id + 1
    expected_experiments = {
        f"{experiment}_r{stage_number}": expected
        for experiment, expected in EXPECTED_BASE.items()
    }
    for experiment, expected in expected_experiments.items():
        paths = [path for path in final_paths if experiment in path.parts]
        if len(paths) != 1:
            raise RuntimeError(f"{experiment}: expected one final JSON, found {len(paths)}")
        rows.append(audit_run(paths[0], expected, replicate_id))
        seen_paths.add(paths[0])
    if seen_paths != set(final_paths):
        raise RuntimeError("Unexpected final JSON outside the six frozen gate cells")

    commits = {row["code_commit"] for row in rows}
    config_hashes = {row["config_sha256"] for row in rows}
    if len(commits) != 1 or len(config_hashes) != 1:
        raise RuntimeError("Gate cells do not share one code commit and config hash")

    output_directory.mkdir(parents=True, exist_ok=True)
    write_csv(output_directory / "gate_run_metrics.csv", rows)
    summary = {
        "completion_passed": all(row["interaction_errors"] == 0 for row in rows),
        "behavioral_headroom": "requires_review",
        "completed_final_full_state_jsons": len(rows),
        "results_only_jsons_analyzed": 0,
        "checkpoint_jsons_analyzed": 0,
        "error_jsons_analyzed": 0,
        "artifact_inventory": inventory,
        "code_commit": next(iter(commits)),
        "config_sha256": next(iter(config_hashes)),
        "model": MODEL,
        "reasoning_effort": "low",
        "replicate_id": replicate_id,
        "total_llm_interactions": sum(row["llm_interactions"] for row in rows),
        "total_input_tokens": sum(row["input_tokens"] for row in rows),
        "total_output_tokens": sum(row["output_tokens"] for row in rows),
        "total_reasoning_tokens": sum(row["reasoning_tokens"] for row in rows),
        "estimated_total_cost_usd": sum(row["estimated_cost_usd"] for row in rows),
        "interpretation": (
            "This audit checks completion and recorded conditions. Behavioral "
            "headroom requires review of the send/return distributions; successful "
            "completion alone does not establish it or stable task-order effects."
        ),
    }
    (output_directory / "gate_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    for row in rows:
        print(
            f"{row['num_agents']} agents {row['task_order']}: "
            f"send={row['mean_send_fraction']:.3f}, "
            f"max-send={row['max_send_rate']:.3f}, "
            f"return={row['mean_return_proportion_positive']}, "
            f"cost=${row['estimated_cost_usd']:.2f}"
        )

    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--replicate-id", type=int, choices=(0, 1), default=0)
    args = parser.parse_args()
    summary = audit_gate(args.input, args.output, args.replicate_id)
    return 0 if summary["completion_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

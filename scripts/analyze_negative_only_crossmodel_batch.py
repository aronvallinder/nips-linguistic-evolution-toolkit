#!/usr/bin/env python3
"""Audit and plot the 2026-08-25 negative-only cross-model batch."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from analyses._shared import configure_matplotlib, write_output_provenance

# Condition fields that legitimately differ across the 3 × 2 × 3 × 3 × 5 matrix.
# Anything else that differs must be declared through --comparison-spec.
_MODEL_PROFILE = "Pinned per-model request profile (Claude thinking / GPT reasoning / Gemini thinking) is a design factor"
_POPULATION = "Population size (2-agent dyad vs 8-agent rotating population) is a design factor"
_TASK_ORDER = "Task order (game, game→myth, myth→game) is a design factor"
_TREATMENT = "Forced-defection treatment (none, 25%, 50%) is a design factor"
_REPLICATE = "Paired replicate identity and seeds vary by design"
ALLOWED_DIFFERENCES = {
    **{path: _MODEL_PROFILE for path in (
        "llm.endpoint", "llm.model", "llm.provider", "llm.provider_model",
        "llm.parameters.maxOutputTokens", "llm.parameters.max_completion_tokens",
        "llm.parameters.max_tokens", "llm.parameters.reasoning_effort",
        "llm.parameters.temperature", "llm.parameters.thinking", "llm.parameters.thinkingConfig",
        "llm.policy.max_output_tokens", "llm.policy.provider", "llm.policy.temperature",
        "llm.policy.reasoning.reasoning_effort", "llm.policy.reasoning.thinking",
        "llm.policy.reasoning.thinkingConfig",
    )},
    **{path: _POPULATION for path in (
        "protocol.simulation.num_agents", "protocol.simulation.memory_capacity",
        "protocol.game.pairing_mode", "protocol.game.show_agent_names",
        "protocol.game.history_policy", "protocol.game.self_history_window",
        "protocol.game.coplayer_history_window", "protocol.game.later_investor_template",
        "protocol.game.later_trustee_template",
        *(f"protocol.game.personas.Agent_{index}" for index in range(3, 9)),
    )},
    **{path: _TASK_ORDER for path in (
        "protocol.simulation.task_order", "protocol.myth.round1_template",
        "protocol.myth.later_rounds_template",
    )},
    **{path: _TREATMENT for path in (
        "protocol.game.defector_ratio", "protocol.game.defector_action_policy",
        "protocol.game.defector_role_visible_to_self", "protocol.game.game_prompt_addition",
        "protocol.game.random_defection_probability",
    )},
    **{path: _REPLICATE for path in (
        "replicate.identity.experiment", "replicate.identity.output_path",
        "replicate.identity.replicate_id", "replicate.run_seed", "replicate.noise_seed",
        "replicate.pairing_seed", "replicate.defector_seed", "replicate.random_defection_seed",
    )},
}


DEFAULT_INPUT = Path(
    "data/json/noise_experiments/negative_only_crossmodel_defectors_n5_20260825"
)
DEFAULT_OUTPUT = Path(
    "docs/figures/negative_only_crossmodel_defectors_n5_20260825"
)

MODELS = {
    "anthropic/claude-sonnet-4.5": "Claude Sonnet 4.5",
    "openai/gpt-5-nano": "GPT-5 Nano",
    "google/gemini-3.7-flash": "Gemini 3.7 Flash",
}
MODEL_ORDER = list(MODELS.values())
TASK_ORDER = ["game", "game_myth", "myth_game"]
TASK_LABELS = {
    "game": "Game only",
    "game_myth": "Game → Myth",
    "myth_game": "Myth → Game",
}
POPULATION_LABELS = {
    2: "2-agent repeated dyad",
    8: "8-agent rotating population",
}
TREATMENT_ORDER = {
    2: ["control", "random25", "random50"],
    8: ["control", "defectors25", "defectors50"],
}
TREATMENT_LABELS = {
    "control": "No forced defection",
    "random25": "25% random defection",
    "random50": "50% random defection",
    "defectors25": "2 of 8 defectors",
    "defectors50": "4 of 8 defectors",
}
COLORS = {
    "control": "#4c78a8",
    "random25": "#f58518",
    "random50": "#e45756",
    "defectors25": "#f58518",
    "defectors50": "#e45756",
}
FORCED_SOURCES = {"forced_zero", "random_defection_forced_zero"}


def final_json_paths(root: Path) -> list[Path]:
    paths = []
    for path in root.rglob("*.json"):
        if any(
            marker in path.name
            for marker in (
                ".results.json",
                ".checkpoint.json",
                ".error.json",
            )
        ):
            continue
        paths.append(path)
    return sorted(paths)


def treatment_id(metadata: dict) -> str:
    num_agents = int(metadata["num_agents"])
    if num_agents == 2:
        probability = float(metadata.get("random_defection_probability", 0.0))
        return {0.0: "control", 0.25: "random25", 0.5: "random50"}[probability]
    if num_agents == 8:
        count = int(metadata.get("defector_count", 0))
        return {0: "control", 2: "defectors25", 4: "defectors50"}[count]
    raise RuntimeError(f"Unexpected population size: {num_agents}")


def task_id(run: dict) -> str:
    return "_".join(
        run.get("task_order")
        or (run.get("run_metadata") or {}).get("task_order")
        or []
    )


def audit_and_extract(path: Path) -> tuple[dict, list[dict]]:
    run = json.loads(path.read_text(encoding="utf-8"))
    metadata = run.get("run_metadata") or {}
    model_id = metadata.get("model")
    if model_id not in MODELS:
        raise RuntimeError(f"{path}: unexpected model {model_id!r}")

    num_agents = int(metadata.get("num_agents", 0))
    if num_agents not in POPULATION_LABELS:
        raise RuntimeError(f"{path}: unexpected num_agents={num_agents}")
    if int(metadata.get("num_turns", 0)) != 10:
        raise RuntimeError(f"{path}: expected ten rounds")
    if metadata.get("code_dirty") is not False:
        raise RuntimeError(f"{path}: run was not launched from a clean commit")

    expected_noise = {
        "type": "uniform",
        "range": 1.0,
        "direction": "negative",
        "applies_to": "both",
        "inform_agents": True,
    }
    if metadata.get("noise_config") != expected_noise:
        raise RuntimeError(
            f"{path}: expected negative-only noise; got {metadata.get('noise_config')!r}"
        )

    condition = task_id(run)
    if condition not in TASK_ORDER:
        raise RuntimeError(f"{path}: unexpected task order {condition!r}")
    treatment = treatment_id(metadata)
    replicate_id = int(metadata.get("replicate_id", -1))
    if replicate_id not in range(5):
        raise RuntimeError(f"{path}: unexpected replicate_id={replicate_id}")

    rounds = run.get("conversation_history") or []
    if len(rounds) != 10:
        raise RuntimeError(f"{path}: expected ten completed round records")
    agent_types = (run.get("game_data") or {}).get("agent_types") or {}
    rows = []
    for round_entry in rounds:
        round_number = int(round_entry["round"])
        dyads = round_entry.get("dyads") or []
        if len(dyads) != num_agents // 2:
            raise RuntimeError(
                f"{path}: round {round_number} has {len(dyads)} dyads"
            )
        game_responses = round_entry.get("game_responses") or {}
        for dyad in dyads:
            sender_id = dyad["investor"]
            receiver_id = dyad["trustee"]
            sent = float(dyad["sent"])
            sent_communicated = float(dyad["sent_communicated"])
            returned = float(dyad["returned"])
            returned_communicated = float(dyad["returned_communicated"])
            received = float(dyad["received"])

            for label, actual, communicated in (
                ("sent", sent, sent_communicated),
                ("returned", returned, returned_communicated),
            ):
                if communicated > actual + 1e-8:
                    raise RuntimeError(
                        f"{path}: round {round_number} {label} noise increased "
                        f"the transfer ({actual} -> {communicated})"
                    )
                if actual - communicated > 1.0 + 1e-8:
                    raise RuntimeError(
                        f"{path}: round {round_number} {label} noise exceeded $1"
                    )

            response = game_responses.get(receiver_id) or {}
            response_source = response.get("response_source", "llm")
            ratio = returned / received if received > 0 else np.nan
            if np.isfinite(ratio) and not -1e-8 <= ratio <= 1 + 1e-8:
                raise RuntimeError(
                    f"{path}: round {round_number} invalid return proportion {ratio}"
                )
            rows.append(
                {
                    "path": str(path),
                    "model": MODELS[model_id],
                    "model_id": model_id,
                    "population": POPULATION_LABELS[num_agents],
                    "num_agents": num_agents,
                    "condition": condition,
                    "condition_label": TASK_LABELS[condition],
                    "treatment": treatment,
                    "treatment_label": TREATMENT_LABELS[treatment],
                    "replicate_id": replicate_id,
                    "round": round_number,
                    "sender_id": sender_id,
                    "receiver_id": receiver_id,
                    "receiver_type": agent_types.get(receiver_id, "standard"),
                    "received": received,
                    "returned": returned,
                    "return_proportion": ratio,
                    "zero_receipt": float(received <= 0),
                    "response_source": response_source,
                    "forced_receiver_decision": float(
                        response_source in FORCED_SOURCES
                    ),
                }
            )

    run_record = {
        "path": str(path),
        "model": MODELS[model_id],
        "model_id": model_id,
        "population": POPULATION_LABELS[num_agents],
        "num_agents": num_agents,
        "condition": condition,
        "condition_label": TASK_LABELS[condition],
        "treatment": treatment,
        "treatment_label": TREATMENT_LABELS[treatment],
        "replicate_id": replicate_id,
        "defector_count": int(metadata.get("defector_count", 0)),
        "defector_agent_ids": "|".join(metadata.get("defector_agent_ids") or []),
        "random_defection_probability": float(
            metadata.get("random_defection_probability", 0.0)
        ),
        "random_defection_seed": metadata.get("random_defection_seed"),
        "noise_seed": metadata.get("noise_seed"),
        "pairing_seed": metadata.get("pairing_seed"),
        "code_commit": metadata.get("code_commit"),
        "config_sha256": metadata.get("config_sha256"),
    }
    return run_record, rows


def validate_matrix(runs: pd.DataFrame, decisions: pd.DataFrame) -> None:
    cell_keys = ["model", "num_agents", "condition", "treatment"]
    expected_cells = 3 * 2 * 3 * 3
    cell_counts = runs.groupby(cell_keys).size()
    if len(cell_counts) != expected_cells:
        raise RuntimeError(
            f"Expected {expected_cells} cells, found {len(cell_counts)}"
        )
    if set(cell_counts) != {5}:
        raise RuntimeError(f"Expected n=5 in every cell; got {sorted(set(cell_counts))}")
    replicate_sets = runs.groupby(cell_keys)["replicate_id"].agg(
        lambda values: tuple(sorted(values))
    )
    if set(replicate_sets) != {(0, 1, 2, 3, 4)}:
        raise RuntimeError("Replicate IDs are not 0-4 in every cell")
    if len(runs) != 270:
        raise RuntimeError(f"Expected 270 completed runs, found {len(runs)}")

    expected_decisions = sum(
        10 * (row.num_agents // 2) for row in runs.itertuples(index=False)
    )
    if len(decisions) != expected_decisions:
        raise RuntimeError(
            f"Expected {expected_decisions} receiver decisions, found {len(decisions)}"
        )

    seed_fields = ["noise_seed", "pairing_seed"]
    paired_keys = ["replicate_id"]
    for field in seed_fields:
        counts = runs.groupby(paired_keys)[field].nunique()
        if not (counts == 1).all():
            raise RuntimeError(f"{field} is not paired across the matrix")

    fixed = runs[runs["num_agents"] == 8]
    for (_, model, condition, replicate), group in fixed.groupby(
        ["num_agents", "model", "condition", "replicate_id"]
    ):
        ids_25 = set(
            group.loc[
                group["treatment"] == "defectors25",
                "defector_agent_ids",
            ].iloc[0].split("|")
        )
        ids_50 = set(
            group.loc[
                group["treatment"] == "defectors50",
                "defector_agent_ids",
            ].iloc[0].split("|")
        )
        if not ids_25 < ids_50:
            raise RuntimeError(
                "The two-defector assignment is not nested in the four-defector arm: "
                f"{model}, {condition}, replicate {replicate}"
            )

    random_decisions = decisions[
        (decisions["num_agents"] == 2)
        & decisions["treatment"].isin(["random25", "random50"])
    ]
    event_keys = ["model", "condition", "replicate_id", "round", "receiver_id"]
    event_table = random_decisions.pivot_table(
        index=event_keys,
        columns="treatment",
        values="forced_receiver_decision",
        aggfunc="first",
    )
    if not (event_table["random25"] <= event_table["random50"]).all():
        raise RuntimeError("25% random receiver events are not nested in 50% events")


def run_round_metrics(decisions: pd.DataFrame) -> pd.DataFrame:
    rows = []
    run_keys = [
        "model",
        "num_agents",
        "population",
        "condition",
        "condition_label",
        "treatment",
        "treatment_label",
        "replicate_id",
        "round",
    ]
    scopes = [("all", decisions)]
    standard = decisions[decisions["receiver_type"] == "standard"]
    scopes.append(("ordinary", standard))
    for scope, frame in scopes:
        for keys, group in frame.groupby(run_keys, dropna=False):
            record = dict(zip(run_keys, keys))
            defined = group["return_proportion"].dropna()
            record.update(
                {
                    "receiver_scope": scope,
                    "return_proportion": (
                        float(defined.mean()) if len(defined) else np.nan
                    ),
                    "zero_receipt_rate": float(group["zero_receipt"].mean()),
                    "forced_receiver_rate": float(
                        group["forced_receiver_decision"].mean()
                    ),
                    "receiver_decisions": len(group),
                    "defined_return_decisions": len(defined),
                }
            )
            rows.append(record)
    return pd.DataFrame(rows)


def summarize(run_round: pd.DataFrame) -> pd.DataFrame:
    keys = [
        "model",
        "num_agents",
        "population",
        "condition",
        "condition_label",
        "treatment",
        "treatment_label",
        "receiver_scope",
        "round",
    ]
    rows = []
    for group_keys, group in run_round.groupby(keys, dropna=False):
        base = dict(zip(keys, group_keys))
        for metric in (
            "return_proportion",
            "zero_receipt_rate",
            "forced_receiver_rate",
        ):
            values = group[metric].dropna().to_numpy(dtype=float)
            if not len(values):
                mean = low = high = np.nan
            elif len(values) == 1 or np.allclose(values, values[0]):
                mean = low = high = float(values.mean())
            else:
                mean = float(values.mean())
                low, high = stats.t.interval(
                    0.95,
                    len(values) - 1,
                    loc=mean,
                    scale=stats.sem(values),
                )
            rows.append(
                {
                    **base,
                    "metric": metric,
                    "n_runs": len(values),
                    "mean": mean,
                    "ci_low": low,
                    "ci_high": high,
                }
            )
    return pd.DataFrame(rows)


def plot_scope(
    summary: pd.DataFrame,
    num_agents: int,
    condition: str,
    scope: str,
    output_dir: Path,
) -> None:
    import matplotlib.pyplot as plt

    selected = summary[
        (summary["num_agents"] == num_agents)
        & (summary["condition"] == condition)
        & (summary["receiver_scope"] == scope)
    ]
    metrics = [
        ("return_proportion", "Returned / received\n(positive receipts only)"),
        ("zero_receipt_rate", "Zero-receipt rate"),
    ]
    fig, axes = plt.subplots(2, 3, figsize=(12, 7), sharex=True, sharey="row")
    fig.suptitle(
        f"Negative-only noise: returns across rounds\n"
        f"{POPULATION_LABELS[num_agents]} · {TASK_LABELS[condition]} · {scope} receivers",
        fontsize=14,
        fontweight="bold",
    )
    for column, model in enumerate(MODEL_ORDER):
        for row, (metric, ylabel) in enumerate(metrics):
            ax = axes[row, column]
            for treatment in TREATMENT_ORDER[num_agents]:
                cell = selected[
                    (selected["model"] == model)
                    & (selected["treatment"] == treatment)
                    & (selected["metric"] == metric)
                ].sort_values("round")
                x = cell["round"].to_numpy(dtype=float)
                mean = cell["mean"].to_numpy(dtype=float)
                low = cell["ci_low"].to_numpy(dtype=float)
                high = cell["ci_high"].to_numpy(dtype=float)
                ax.plot(
                    x,
                    mean,
                    marker="o",
                    markersize=3.5,
                    linewidth=1.8,
                    color=COLORS[treatment],
                    label=TREATMENT_LABELS[treatment],
                )
                ax.fill_between(
                    x,
                    low,
                    high,
                    color=COLORS[treatment],
                    alpha=0.14,
                    linewidth=0,
                )
            ax.set_ylim(-0.03, 1.03)
            ax.set_xticks(range(1, 11))
            ax.grid(True, alpha=0.25)
            if row == 0:
                ax.set_title(model, fontsize=11, fontweight="bold")
            if column == 0:
                ax.set_ylabel(ylabel)
            if row == 1:
                ax.set_xlabel("Round")
    axes[0, 0].legend(loc="lower right", fontsize=8)
    fig.tight_layout(rect=(0, 0, 1, 0.91))
    scope_suffix = "all" if scope == "all" else "ordinary"
    output = output_dir / (
        f"returns_{num_agents}agent_{condition}_{scope_suffix}.png"
    )
    fig.savefig(output, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--comparison-spec",
        type=Path,
        help="JSON mapping of additional allowed differing condition fields to reasons",
    )
    args = parser.parse_args()
    allowed = dict(ALLOWED_DIFFERENCES)
    if args.comparison_spec:
        allowed.update(json.loads(args.comparison_spec.read_text(encoding="utf-8")))

    paths = final_json_paths(args.input)
    run_rows = []
    decision_rows = []
    for path in paths:
        run_record, decisions = audit_and_extract(path)
        run_rows.append(run_record)
        decision_rows.extend(decisions)
    runs = pd.DataFrame(run_rows)
    decision_frame = pd.DataFrame(decision_rows)
    validate_matrix(runs, decision_frame)

    args.output.mkdir(parents=True, exist_ok=True)
    run_round = run_round_metrics(decision_frame)
    summary = summarize(run_round)
    runs.to_csv(args.output / "run_manifest.csv", index=False)
    decision_frame.to_csv(args.output / "receiver_decisions.csv", index=False)
    run_round.to_csv(args.output / "run_round_metrics.csv", index=False)
    summary.to_csv(args.output / "round_summary.csv", index=False)

    configure_matplotlib()
    for num_agents in (2, 8):
        scopes = ["all"] if num_agents == 2 else ["all", "ordinary"]
        for condition in TASK_ORDER:
            for scope in scopes:
                plot_scope(summary, num_agents, condition, scope, args.output)

    # Checked input/condition manifest; the repository safeguard requires it
    # for every committed output directory.
    write_output_provenance(args.output, paths, allowed_differences=allowed)

    print(
        f"Audited {len(runs)} runs and {len(decision_frame)} receiver decisions. "
        f"Outputs: {args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Summarize the 2026-09-17 mixed-model dyads against the September homogeneous dyads.

Pools the 54 mixed runs (Sonnet+GPT, Sonnet+Gemini, Gemini+GPT; game /
game_myth / myth_game; six replicates, first sender alternating by family) with the 45
September informed-noise homogeneous dyad controls (Sonnet+Sonnet, GPT+GPT,
Gemini+Gemini; five replicates). Every run is condition-validated and the
declared differences are recorded in provenance.json, which validates the mixed
and homogeneous runs as two pools (a mixed run pins one request plan per agent
instead of a run-level policy block) and everything except the request-plan
shape across pools.

Outputs (docs/figures/mixed_model_dyads_20260917/):
  decisions.csv        one row per dyad-round (sender/receiver family, amounts)
  cell_summary.csv     per composition x task order: resources, sends, returns
  family_behaviour.csv per family x task order x partner family: send / return
  round_means.csv      per composition x task order x round
  sends_and_returns.png, resources.png, resources_boxplots.{png,svg,pdf}
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from analyses._shared import configure_matplotlib, load_simulation_runs  # noqa: E402
from src.experiment_condition import condition_agent_models, condition_from_run, output_provenance  # noqa: E402
from scripts.analyze_negative_only_crossmodel_batch import ALLOWED_DIFFERENCES  # noqa: E402

MIXED_ROOT = ROOT / "data/json/noise_experiments/mixed_model_dyads_20260917"
SEPTEMBER_ROOT = ROOT / "data/json/noise_experiments/negative_only_crossmodel_reasoning_rerun_20260909"
OUTPUT = ROOT / "docs/figures/mixed_model_dyads_20260917"
FAMILY = {
    "anthropic/claude-sonnet-4.5": "Sonnet",
    "openai/gpt-5-nano": "GPT",
    "google/gemini-3.7-flash": "Gemini",
}
TASK_ORDERS = ("game", "game_myth", "myth_game")
FAMILY_RANK = {"Sonnet": 0, "Gemini": 1, "GPT": 2}
COMPOSITIONS = ("Sonnet+GPT", "GPT+GPT", "Sonnet+Sonnet", "Sonnet+Gemini", "Gemini+Gemini", "Gemini+GPT")
ALLOWED = {
    **ALLOWED_DIFFERENCES,
    "llm.agents": "Mixed runs pin one request plan per agent (design factor: model composition)",
    # games/ is byte-identical between the September run commit (893a9713) and the
    # mixed-run commits (620ce8b3, be299fee); only the src/ files that add per-agent
    # request plans differ. Prompts and request bodies are asserted unchanged by
    # the launcher's plan step and per-call audit.
    "implementation": "Mixed runs use later src/ code (per-agent request plans); games/ is identical and request bodies are launcher-audited",
}
POOL_REASON = (
    "Mixed runs record one request plan per agent under llm.agents instead of a run-level "
    "llm.policy/llm.parameters block; every agent plan equals the September profile of its "
    "model (launcher plan step and per-call audit), so the pools differ only in plan shape."
)
NON_FINAL = (".results.json", ".checkpoint.json", ".error.json")


def final_paths():
    mixed = sorted(p for p in MIXED_ROOT.rglob("mixed_dyad_*rep0*.json") if not p.name.endswith(NON_FINAL))
    september = sorted(
        p for p in SEPTEMBER_ROOT.rglob("negative_only_reasoning_rerun_dyad_*rep0*.json")
        if not p.name.endswith(NON_FINAL) and p.parent.name in {"noisy2_crossmodel_negative_game_r3", "noisy2_crossmodel_negative_twotask_r3"}
    )
    return mixed, september


def agent_families(run):
    """Model family per agent, read from the validated condition, never from loose metadata."""
    condition = condition_from_run(run)
    planned = condition_agent_models(condition)
    if planned is not None:
        return {agent_id: FAMILY[model] for agent_id, model in planned.items()}
    return {agent_id: FAMILY[condition["llm"]["model"]] for agent_id in run["agents"]}


def composition_label(families):
    return "+".join(sorted((families["Agent_1"], families["Agent_2"]), key=FAMILY_RANK.__getitem__))


def extract(path, run):
    metadata = run["run_metadata"]
    families = agent_families(run)
    composition = composition_label(families)
    task_order = "_".join(run["task_order"])
    rounds = run["conversation_history"]
    if len(rounds) != 10 or metadata.get("num_agents") != 2:
        raise RuntimeError(f"{path}: expected a ten-round dyad")
    rows = []
    for entry in rounds:
        (dyad,) = entry["dyads"]
        sender, receiver = dyad["investor"], dyad["trustee"]
        received = float(dyad["received"])
        returned = float(dyad["returned"])
        rows.append({
            "path": str(path.relative_to(ROOT)),
            "composition": composition,
            "mixed": families["Agent_1"] != families["Agent_2"],
            "first_sender_family": families["Agent_1"],
            "task_order": task_order,
            "replicate_id": metadata["replicate_id"],
            "round": int(entry["round"]),
            "sender_family": families[sender],
            "receiver_family": families[receiver],
            "sent": float(dyad["sent"]),
            "received": received,
            "returned": returned,
            "return_proportion": returned / received if received > 0 else np.nan,
            "zero_receipt": float(received <= 0),
            "sender_payoff": float(dyad["investor_payoff"]),
            "receiver_payoff": float(dyad["trustee_payoff"]),
            "balance_Agent_1": float(dyad["balances"]["Agent_1"]),
            "balance_Agent_2": float(dyad["balances"]["Agent_2"]),
            "family_Agent_1": families["Agent_1"],
            "family_Agent_2": families["Agent_2"],
            "total_balance": float(sum(dyad["balances"].values())),
        })
    return rows


def mean_sd(values):
    values = np.asarray([v for v in values if np.isfinite(v)], dtype=float)
    if values.size == 0:
        return np.nan, np.nan
    return float(values.mean()), float(values.std(ddof=1)) if values.size > 1 else 0.0


def cell_summary(decisions):
    rows = []
    for (composition, task_order), group in decisions.groupby(["composition", "task_order"], sort=False):
        runs = group.groupby("path")
        final = runs.apply(lambda g: g.sort_values("round").iloc[-1], include_groups=False)
        total_m, total_s = mean_sd(final["total_balance"])
        row = {
            "composition": composition, "task_order": task_order, "n_runs": len(final),
            "total_resources_mean": total_m, "total_resources_sd": total_s,
            "zero_receipt_rate": float(group["zero_receipt"].mean()),
        }
        families = [f for f in ("Sonnet", "GPT", "Gemini") if f in set(group["sender_family"])]
        for family in families:
            sent = group[group["sender_family"] == family]["sent"]
            ret = group[group["receiver_family"] == family]["return_proportion"]
            r1 = group[(group["round"] == 1) & (group["sender_family"] == family)]["sent"]
            row[f"sent_by_{family}_mean"], row[f"sent_by_{family}_sd"] = mean_sd(sent)
            row[f"return_prop_by_{family}_mean"], row[f"return_prop_by_{family}_sd"] = mean_sd(ret)
            row[f"round1_sent_by_{family}_mean"], _ = mean_sd(r1)
        rows.append(row)
    return pd.DataFrame(rows)


def family_behaviour(decisions):
    rows = []
    for (family, task_order), group in decisions.groupby(["sender_family", "task_order"], sort=False):
        for partner, sub in group.groupby("receiver_family"):
            sent_m, sent_s = mean_sd(sub["sent"])
            rows.append({"family": family, "role": "sender", "task_order": task_order, "partner_family": partner,
                         "n_decisions": len(sub), "mean": sent_m, "sd": sent_s})
    for (family, task_order), group in decisions.groupby(["receiver_family", "task_order"], sort=False):
        for partner, sub in group.groupby("sender_family"):
            ret_m, ret_s = mean_sd(sub["return_proportion"])
            rows.append({"family": family, "role": "receiver (return proportion)", "task_order": task_order,
                         "partner_family": partner, "n_decisions": int(sub["return_proportion"].notna().sum()), "mean": ret_m, "sd": ret_s})
    return pd.DataFrame(rows)


def plot(decisions, round_means):
    import matplotlib.pyplot as plt

    configure_matplotlib()
    colors = {"Sonnet+GPT": "#d62728", "GPT+GPT": "#ff9896", "Sonnet+Sonnet": "#7f7f7f", "Sonnet+Gemini": "#1f77b4", "Gemini+Gemini": "#aec7e8", "Gemini+GPT": "#2ca02c"}
    fig, axes = plt.subplots(2, 3, figsize=(13, 7), sharex=True)
    for col, task_order in enumerate(TASK_ORDERS):
        for composition in COMPOSITIONS:
            sub = round_means[(round_means["task_order"] == task_order) & (round_means["composition"] == composition)]
            if sub.empty:
                continue
            axes[0, col].plot(sub["round"], sub["sent_mean"], marker="o", color=colors[composition], label=composition)
            axes[1, col].plot(sub["round"], sub["return_proportion_mean"], marker="o", color=colors[composition], label=composition)
        axes[0, col].set_title(task_order.replace("_", " → "))
        axes[1, col].set_xlabel("round")
        axes[0, col].set_ylim(0, 5.2)
        axes[1, col].set_ylim(0, 1.05)
    axes[0, 0].set_ylabel("amount sent (of $5)")
    axes[1, 0].set_ylabel("return proportion")
    handles = {}
    for ax in axes.flat:
        for handle, label in zip(*ax.get_legend_handles_labels()):
            handles.setdefault(label, handle)
    fig.legend([handles[c] for c in COMPOSITIONS if c in handles], [c for c in COMPOSITIONS if c in handles],
               loc="lower center", ncol=6, fontsize=9, frameon=False)
    fig.suptitle("Fixed dyads, informed negative-only noise: mixed vs homogeneous compositions (means over runs)")
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(OUTPUT / "sends_and_returns.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 4.5))
    finals = decisions[decisions["round"] == 10]
    positions = []
    labels = []
    x = 0
    for task_order in TASK_ORDERS:
        for composition in COMPOSITIONS:
            values = finals[(finals["task_order"] == task_order) & (finals["composition"] == composition)]["total_balance"]
            if values.empty:
                continue
            ax.bar(x, values.mean(), color=colors[composition], alpha=0.8)
            ax.scatter(np.full(len(values), x) + np.random.default_rng(0).uniform(-0.15, 0.15, len(values)), values, color="black", s=10, zorder=3)
            positions.append(x)
            labels.append(f"{composition}\n{task_order}")
            x += 1
        x += 0.8
    ax.set_xticks(positions)
    ax.set_xticklabels(labels, rotation=90, fontsize=7)
    ax.set_ylabel("total resources after 10 rounds (both agents)")
    ax.set_title("Dyad resources by composition and task order (bars: mean; dots: runs)")
    fig.tight_layout()
    fig.savefig(OUTPUT / "resources.png", dpi=150)
    plt.close(fig)


BOX_COLORS = ["#999999", "#e99675", "#72b6a1"]
DOT_COLORS = ["#777777", "#fc8d62", "#66c2a5"]
ORDER_LABELS = ["Game only", "Game → Myth", "Myth → Game"]


def plot_boxplot_grid(decisions):
    """Same grid layout as the figure-2 resource boxplots: one panel per composition,
    three task-order boxes per panel, cumulative resources per agent at round 10."""
    import matplotlib.pyplot as plt

    configure_matplotlib()
    finals = decisions[decisions["round"] == 10]
    # Six unique pairings, each drawn once (2026-09-22 meeting): the homogeneous
    # controls on one row, the three mixed pairings on the other.
    rows = [
        ("Homogeneous dyads\n(September controls)", ["Sonnet+Sonnet", "GPT+GPT", "Gemini+Gemini"]),
        ("Mixed dyads", ["Sonnet+GPT", "Sonnet+Gemini", "Gemini+GPT"]),
    ]
    fig, axes = plt.subplots(2, 3, figsize=(13.5, 8.2), sharey=True, squeeze=False)
    for (partner, compositions), axrow in zip(rows, axes):
        for ax, composition in zip(axrow, compositions):
            counts = []
            for pos, task_order in enumerate(TASK_ORDERS, 1):
                v = np.sort(finals[(finals["composition"] == composition) & (finals["task_order"] == task_order)]["total_balance"].to_numpy() / 2)
                counts.append(len(v))
                ax.boxplot(v, positions=[pos], widths=.52, patch_artist=True, showfliers=False, whis=1.5,
                           boxprops=dict(facecolor=BOX_COLORS[pos - 1], edgecolor="#666666"),
                           medianprops=dict(color="#222222", linewidth=1.6),
                           whiskerprops=dict(color="#666666"), capprops=dict(color="#666666"))
                ax.scatter(pos + np.linspace(-.1, .1, len(v)), v, s=30, c=DOT_COLORS[pos - 1], edgecolors="white", linewidths=.6, zorder=3)
            ax.set_xticks([1, 2, 3], ORDER_LABELS)
            ax.set_xlim(.5, 3.5)
            ax.set_ylim(0, 80)
            ax.set_axisbelow(True)
            ax.grid(axis="y", alpha=.22)
            ax.spines[["top", "right"]].set_visible(False)
            kind = "mixed" if "+" in composition and composition.split("+")[0] != composition.split("+")[1] else "homogeneous"
            ax.set_title(f"{composition.replace('+', ' + ')}\n{kind} · n = {counts[0]} per box", fontsize=12, fontweight="bold", pad=8)
        axrow[0].set_ylabel(partner, fontsize=12, fontweight="bold", labelpad=14)
    fig.suptitle("Final cumulative resources\nHomogeneous vs mixed-model dyads · Informed negative-only noise · No defectors · Round 10",
                 fontsize=15, fontweight="bold")
    fig.text(.5, .012, "Each dot = one run (n = 5 per homogeneous box, September controls; 6 per mixed box)\n"
             "Box = middle 50% · Line = median · Whiskers = up to 1.5 × IQR",
             ha="center", fontsize=9, color="#444444")
    fig.supylabel("Cumulative resources per agent", fontsize=12, x=.006)
    fig.tight_layout(rect=(.045, .05, 1, .96), h_pad=2.2, w_pad=2.4)
    for ext in ("png", "svg", "pdf"):
        fig.savefig(OUTPUT / f"resources_boxplots.{ext}", dpi=200, bbox_inches="tight")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expect-mixed", type=int, default=54)
    args = parser.parse_args()
    mixed, september = final_paths()
    if len(mixed) != args.expect_mixed:
        raise SystemExit(f"Expected {args.expect_mixed} mixed finals, found {len(mixed)}")
    if len(september) != 45:
        raise SystemExit(f"Expected 45 September homogeneous dyad finals, found {len(september)}")
    paths = mixed + september
    # The two pools are validated separately: a mixed run records one plan per
    # agent under llm.agents instead of a run-level llm.policy/llm.parameters,
    # and whole-block exemptions are deliberately not allowed. The launcher's
    # plan step already proved every agent plan equals the September profile.
    runs = {**load_simulation_runs(mixed, allowed_differences=ALLOWED), **load_simulation_runs(september, allowed_differences=ALLOWED)}
    decisions = pd.DataFrame([row for path in paths for row in extract(path, runs[str(path.resolve())])])
    OUTPUT.mkdir(parents=True, exist_ok=True)
    decisions.to_csv(OUTPUT / "decisions.csv", index=False)
    summary = cell_summary(decisions)
    summary.to_csv(OUTPUT / "cell_summary.csv", index=False)
    behaviour = family_behaviour(decisions)
    behaviour.to_csv(OUTPUT / "family_behaviour.csv", index=False)
    round_means = decisions.groupby(["composition", "task_order", "round"], sort=False).agg(
        sent_mean=("sent", "mean"), return_proportion_mean=("return_proportion", "mean"), zero_receipt_rate=("zero_receipt", "mean")
    ).reset_index()
    round_means.to_csv(OUTPUT / "round_means.csv", index=False)
    plot(decisions, round_means)
    plot_boxplot_grid(decisions)
    for stale in ("provenance_mixed.json", "provenance_september.json"):
        (OUTPUT / stale).unlink(missing_ok=True)
    outputs = [p for p in OUTPUT.rglob("*") if p.is_file() and p.name != "provenance.json"]
    document = output_provenance(
        paths, outputs, ALLOWED, output_root=OUTPUT,
        pools={"mixed": mixed, "september": september}, pool_reason=POOL_REASON,
    )
    (OUTPUT / "provenance.json").write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    pd.set_option("display.width", 200)
    print(summary[["composition", "task_order", "n_runs", "total_resources_mean", "total_resources_sd", "zero_receipt_rate"]].to_string(index=False))
    print()
    print(behaviour.to_string(index=False))


if __name__ == "__main__":
    main()

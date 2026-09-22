#!/usr/bin/env python3
"""Summarize the 2026-09-18 mixed-model eight-agent contagion ladder.

Pools the 90 mixed runs (1/2/4 Gemini among GPT, 1/2/4 GPT among Sonnet;
game / game_myth / myth_game; five replicates) with the 45 September
informed-noise homogeneous population controls (Sonnet, GPT, Gemini; no
defectors). Every run is condition-validated; provenance.json validates the two
pools and everything except the request-plan shape across them.

Outputs (docs/figures/mixed_model_populations_20260918/):
  games.csv            one row per game (sender/receiver family, pair type, amounts)
  agent_finals.csv     one row per agent per run (family, minority flag, final balance)
  cell_summary.csv     per composition x task order: per-agent resources by family, sends, returns
  encounters.csv       per run: same-family vs cross-family game counts
  round_means.csv      per composition x task order x round
  ladder.png           per-agent resources vs minority count, majority and minority agents
  resources_boxplots.png  figure-2 style grid: per-agent resources, one panel per composition
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
from scripts.analyze_negative_only_crossmodel_batch import ALLOWED_DIFFERENCES  # noqa: E402
from src.experiment_condition import condition_agent_models, condition_from_run, output_provenance  # noqa: E402

MIXED_ROOT = ROOT / "data/json/noise_experiments/mixed_model_populations_20260918"
SEPTEMBER_ROOT = ROOT / "data/json/noise_experiments/negative_only_crossmodel_reasoning_rerun_20260909"
OUTPUT = ROOT / "docs/figures/mixed_model_populations_20260918"
FAMILY = {"anthropic/claude-sonnet-4.5": "Sonnet", "openai/gpt-5-nano": "GPT", "google/gemini-3.7-flash": "Gemini"}
TASK_ORDERS = ("game", "game_myth", "myth_game")
ORDER_LABELS = ["Game only", "Game → Myth", "Myth → Game"]
# Ladder rows: (minority family, majority family). Homogeneous references are
# 0 minority (all majority) and 8 minority (all minority).
LADDERS = (("Gemini", "GPT"), ("GPT", "Sonnet"))
ALLOWED = {
    **ALLOWED_DIFFERENCES,
    "llm.agents": "Mixed runs pin one request plan per agent (design factor: model composition)",
    # games/ is byte-identical between the September run commits and the mixed-run
    # commits; only src/ files that add per-agent request plans differ. Prompts and
    # request bodies are asserted unchanged by the launcher's plan step and audit.
    "implementation": "Mixed runs use later src/ code (per-agent request plans); games/ is identical and request bodies are launcher-audited",
}
POOL_REASON = (
    "Mixed runs record one request plan per agent under llm.agents instead of a run-level "
    "llm.policy/llm.parameters block; every agent plan equals the September profile of its "
    "model (launcher plan step and per-call audit), so the pools differ only in plan shape."
)
NON_FINAL = (".results.json", ".checkpoint.json", ".error.json")
BOX_COLORS = ["#999999", "#e99675", "#72b6a1"]
DOT_COLORS = ["#777777", "#fc8d62", "#66c2a5"]


def final_paths():
    mixed = sorted(p for p in MIXED_ROOT.rglob("mixed_pop_*rep0*.json") if not p.name.endswith(NON_FINAL))
    september = sorted(
        p for p in SEPTEMBER_ROOT.rglob("negative_only_reasoning_rerun_population_*rep0*.json")
        if not p.name.endswith(NON_FINAL) and p.parent.name in {"noisy8_crossmodel_negative_game_r3", "noisy8_crossmodel_negative_twotask_r3"}
    )
    return mixed, september


def families_of(run):
    condition = condition_from_run(run)
    planned = condition_agent_models(condition)
    if planned is not None:
        return {agent_id: FAMILY[model] for agent_id, model in planned.items()}
    return {agent_id: FAMILY[condition["llm"]["model"]] for agent_id in run["agents"]}


def describe(families):
    counts = {}
    for family in families.values():
        counts[family] = counts.get(family, 0) + 1
    if len(counts) == 1:
        (family, n), = counts.items()
        return {"composition": f"{n} {family}", "minority": family, "minority_count": n, "majority": family, "mixed": False}
    minority, majority = sorted(counts, key=counts.__getitem__)
    return {"composition": f"{counts[minority]} {minority} + {counts[majority]} {majority}",
            "minority": minority, "minority_count": counts[minority], "majority": majority, "mixed": True}


def extract(path, run):
    metadata = run["run_metadata"]
    families = families_of(run)
    info = describe(families)
    task_order = "_".join(run["task_order"])
    rounds = run["conversation_history"]
    if len(rounds) != 10 or metadata.get("num_agents") != 8:
        raise RuntimeError(f"{path}: expected a ten-round eight-agent run")
    base = {"path": str(path.relative_to(ROOT)), **info, "task_order": task_order, "replicate_id": metadata["replicate_id"]}
    games = []
    for entry in rounds:
        for dyad in entry["dyads"]:
            sender, receiver = dyad["investor"], dyad["trustee"]
            received, returned = float(dyad["received"]), float(dyad["returned"])
            games.append({
                **base, "round": int(entry["round"]), "sender": sender, "receiver": receiver,
                "sender_family": families[sender], "receiver_family": families[receiver],
                "pair_type": "same" if families[sender] == families[receiver] else "cross",
                "sent": float(dyad["sent"]), "received": received, "returned": returned,
                "return_proportion": returned / received if received > 0 else np.nan,
                "zero_receipt": float(received <= 0),
            })
    balances = rounds[-1]["balances"]
    agents = [{
        **base, "agent_id": agent_id, "family": families[agent_id],
        "is_minority": families[agent_id] == info["minority"] and info["mixed"],
        "final_balance": float(balances[agent_id]),
    } for agent_id in families]
    return games, agents


def mean_sd(values):
    values = np.asarray([v for v in values if np.isfinite(v)], dtype=float)
    if values.size == 0:
        return np.nan, np.nan
    return float(values.mean()), (float(values.std(ddof=1)) if values.size > 1 else 0.0)


def cell_summary(games, agents):
    rows = []
    keys = ["composition", "minority", "minority_count", "majority", "mixed", "task_order"]
    for key, a in agents.groupby(keys, sort=False):
        g = games[(games["composition"] == key[0]) & (games["task_order"] == key[5])]
        per_run = a.groupby("path")
        row = dict(zip(keys, key))
        row["n_runs"] = per_run.ngroups
        row["per_agent_resources_mean"], row["per_agent_resources_sd"] = mean_sd(per_run["final_balance"].mean())
        for label, mask in (("minority", a["family"] == key[1]), ("majority", a["family"] == key[3])):
            sub = a[mask].groupby("path")["final_balance"].mean()
            row[f"{label}_agent_resources_mean"], row[f"{label}_agent_resources_sd"] = mean_sd(sub)
        row["zero_receipt_rate"] = float(g["zero_receipt"].mean())
        row["cross_family_game_share"] = float((g["pair_type"] == "cross").mean())
        for family in ("Sonnet", "GPT", "Gemini"):
            if family not in set(a["family"]):
                continue
            row[f"sent_by_{family}_mean"], _ = mean_sd(g[g["sender_family"] == family]["sent"])
            row[f"return_prop_by_{family}_mean"], _ = mean_sd(g[g["receiver_family"] == family]["return_proportion"])
            for partner in ("Sonnet", "GPT", "Gemini"):
                sub = g[(g["sender_family"] == family) & (g["receiver_family"] == partner)]
                if len(sub):
                    row[f"sent_{family}_to_{partner}_mean"], _ = mean_sd(sub["sent"])
        rows.append(row)
    return pd.DataFrame(rows)


def ladder_points(agents, minority, majority):
    """x = minority count (0 and 8 are the homogeneous references), y = per-agent resources."""
    points = []
    for task_order in TASK_ORDERS:
        for count in (0, 1, 2, 4, 8):
            if count == 0:
                sub = agents[(agents["composition"] == f"8 {majority}") & (agents["task_order"] == task_order)]
            elif count == 8:
                sub = agents[(agents["composition"] == f"8 {minority}") & (agents["task_order"] == task_order)]
            else:
                sub = agents[(agents["minority"] == minority) & (agents["majority"] == majority) & (agents["minority_count"] == count) & (agents["task_order"] == task_order)]
            if sub.empty:
                continue
            for role, family in (("minority", minority), ("majority", majority)):
                fam = sub[sub["family"] == family]
                if fam.empty:
                    continue
                per_run = fam.groupby("path")["final_balance"].mean()
                m, s = mean_sd(per_run)
                points.append({"minority": minority, "majority": majority, "task_order": task_order, "minority_count": count,
                               "role": role, "family": family, "mean": m, "sd": s, "n_runs": len(per_run)})
    return pd.DataFrame(points)


def plot_ladder(agents):
    import matplotlib.pyplot as plt

    configure_matplotlib()
    fig, axes = plt.subplots(2, 3, figsize=(13.5, 8), sharey=True)
    colors = {"Sonnet": "#7f7f7f", "GPT": "#d62728", "Gemini": "#1f77b4"}
    for row, (minority, majority) in enumerate(LADDERS):
        pts = ladder_points(agents, minority, majority)
        for col, task_order in enumerate(TASK_ORDERS):
            ax = axes[row, col]
            for family in (majority, minority):
                sub = pts[(pts["task_order"] == task_order) & (pts["family"] == family)].sort_values("minority_count")
                ax.errorbar(sub["minority_count"], sub["mean"], yerr=sub["sd"], marker="o", capsize=3, color=colors[family], label=f"{family} agents")
            ax.set_xticks([0, 1, 2, 4, 8])
            ax.set_xticklabels([f"0\n(8 {majority})", "1", "2", "4", f"8\n(8 {minority})"])
            ax.set_ylim(0, 80)
            ax.grid(axis="y", alpha=.22)
            ax.spines[["top", "right"]].set_visible(False)
            if row == 0:
                ax.set_title(ORDER_LABELS[col], fontsize=12, fontweight="bold")
            if col == 0:
                ax.set_ylabel(f"{minority} among {majority}\nresources per agent", fontsize=11, fontweight="bold")
            if row == 1:
                ax.set_xlabel(f"number of {minority} agents", fontsize=10)
            ax.legend(fontsize=8, loc="lower right")
    fig.suptitle("Contagion ladder: per-agent resources after 10 rounds by number of minority agents\n"
                 "8-agent rotating populations · informed negative-only noise · mean ± sd over 5 runs", fontsize=13, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, .93))
    for ext in ("png", "svg", "pdf"):
        fig.savefig(OUTPUT / f"ladder.{ext}", dpi=200, bbox_inches="tight")
    plt.close(fig)


def plot_boxplot_grid(agents):
    import matplotlib.pyplot as plt

    configure_matplotlib()
    per_run = agents.groupby(["composition", "task_order", "path"], sort=False)["final_balance"].mean().reset_index()
    fig, axes = plt.subplots(2, 5, figsize=(20, 8), sharey=True, squeeze=False)
    for row, (minority, majority) in enumerate(LADDERS):
        panels = [f"8 {majority}"] + [f"{n} {minority} + {8 - n} {majority}" for n in (1, 2, 4)] + [f"8 {minority}"]
        for ax, composition in zip(axes[row], panels):
            n_runs = 0
            for pos, task_order in enumerate(TASK_ORDERS, 1):
                v = np.sort(per_run[(per_run["composition"] == composition) & (per_run["task_order"] == task_order)]["final_balance"].to_numpy())
                n_runs = max(n_runs, len(v))
                ax.boxplot(v, positions=[pos], widths=.52, patch_artist=True, showfliers=False, whis=1.5,
                           boxprops=dict(facecolor=BOX_COLORS[pos - 1], edgecolor="#666666"),
                           medianprops=dict(color="#222222", linewidth=1.6),
                           whiskerprops=dict(color="#666666"), capprops=dict(color="#666666"))
                ax.scatter(pos + np.linspace(-.1, .1, len(v)), v, s=30, c=DOT_COLORS[pos - 1], edgecolors="white", linewidths=.6, zorder=3)
            kind = "homogeneous (Sept.)" if composition.startswith("8 ") else "mixed"
            ax.set_title(f"{composition}\n{kind} · n = {n_runs}", fontsize=11, fontweight="bold", pad=8)
            ax.set_xticks([1, 2, 3], ORDER_LABELS, fontsize=8)
            ax.set_xlim(.5, 3.5)
            ax.set_ylim(0, 80)
            ax.set_axisbelow(True)
            ax.grid(axis="y", alpha=.22)
            ax.spines[["top", "right"]].set_visible(False)
        axes[row][0].set_ylabel(f"{minority} among {majority}", fontsize=12, fontweight="bold", labelpad=14)
    fig.suptitle("Final cumulative resources per agent (all agents)\nContagion ladder vs homogeneous populations · Informed negative-only noise · No defectors · Round 10",
                 fontsize=14, fontweight="bold")
    fig.text(.5, .012, "Each dot = one run (mean over its 8 agents) · Box = middle 50% · Line = median · Whiskers = up to 1.5 × IQR",
             ha="center", fontsize=9, color="#444444")
    fig.supylabel("Cumulative resources per agent", fontsize=12, x=.006)
    fig.tight_layout(rect=(.02, .05, 1, .91), h_pad=2.2, w_pad=1.6)
    for ext in ("png", "svg", "pdf"):
        fig.savefig(OUTPUT / f"resources_boxplots.{ext}", dpi=200, bbox_inches="tight")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expect-mixed", type=int, default=90)
    args = parser.parse_args()
    mixed, september = final_paths()
    if len(mixed) != args.expect_mixed:
        raise SystemExit(f"Expected {args.expect_mixed} mixed finals, found {len(mixed)}")
    if len(september) != 45:
        raise SystemExit(f"Expected 45 September homogeneous population finals, found {len(september)}")
    paths = mixed + september
    # Each pool is checked in full here; the cross-pool check (everything except the
    # request-plan shape) is done by output_provenance below.
    runs = {**load_simulation_runs(mixed, allowed_differences=ALLOWED), **load_simulation_runs(september, allowed_differences=ALLOWED)}
    games_rows, agent_rows = [], []
    for path in paths:
        g, a = extract(path, runs[str(path.resolve())])
        games_rows += g
        agent_rows += a
    games, agents = pd.DataFrame(games_rows), pd.DataFrame(agent_rows)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    games.to_csv(OUTPUT / "games.csv", index=False)
    agents.to_csv(OUTPUT / "agent_finals.csv", index=False)
    summary = cell_summary(games, agents)
    summary.to_csv(OUTPUT / "cell_summary.csv", index=False)
    encounters = games.groupby(["path", "composition", "task_order", "replicate_id"], sort=False)["pair_type"].value_counts().unstack(fill_value=0).reset_index()
    encounters.to_csv(OUTPUT / "encounters.csv", index=False)
    round_means = games.groupby(["composition", "task_order", "round"], sort=False).agg(
        sent_mean=("sent", "mean"), return_proportion_mean=("return_proportion", "mean"), zero_receipt_rate=("zero_receipt", "mean")).reset_index()
    round_means.to_csv(OUTPUT / "round_means.csv", index=False)
    pd.concat([ladder_points(agents, *ladder) for ladder in LADDERS]).to_csv(OUTPUT / "ladder_points.csv", index=False)
    plot_ladder(agents)
    plot_boxplot_grid(agents)
    outputs = [p for p in OUTPUT.rglob("*") if p.is_file() and p.name != "provenance.json"]
    document = output_provenance(paths, outputs, ALLOWED, output_root=OUTPUT, pools={"mixed": mixed, "september": september}, pool_reason=POOL_REASON)
    (OUTPUT / "provenance.json").write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    pd.set_option("display.width", 220)
    cols = ["composition", "task_order", "n_runs", "per_agent_resources_mean", "per_agent_resources_sd", "minority_agent_resources_mean", "majority_agent_resources_mean", "zero_receipt_rate", "cross_family_game_share"]
    print(summary[cols].round(2).to_string(index=False))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Split the mixed-model results by each model family's own behaviour.

Question raised by Arabella Sinclair (team meeting 2026-09-22): when two model
families share a trust game, does each keep the behaviour it shows among its
own kind (so the pair's score is just the average of two fixed styles), or does
it move toward its partner? The pooled resource figures cannot tell these
apart. This script draws each family's own sending and returning inside every
mixed composition next to the same family's behaviour in the homogeneous
September controls.

Inputs (already validated by the scripts that produced them):
  docs/figures/mixed_model_dyads_20260917/decisions.csv      (54 mixed + 45 homogeneous dyads)
  docs/figures/mixed_model_populations_20260918/games.csv    (90 ladder + 45 homogeneous 8-agent runs)

Outputs (docs/figures/mixed_model_family_split_20260922/, PNG only):
  2-agent-mixed-model-simulation-split.png
                               per mixed pairing x task order: each family's per-run mean
                               amount sent / return proportion, with its homogeneous value
  dyad_family_turn_traces_{sent,return}.png
                               per mixed pairing x task order: each family's mean on its own
                               turns 1-5, dashed = the same family in a homogeneous dyad
  mixed-model-simulation-8-agent-split.png (sending), population_family_split_return.png
                               per ladder x task order: minority and majority family
                               per-run means against the minority count (0 and 8 = homogeneous)

No API calls; pure re-aggregation of the two existing tables.
"""
from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from analyses._shared import configure_matplotlib  # noqa: E402
from analyses._mixed_model_provenance import write_provenance  # noqa: E402

DYADS = ROOT / "docs/figures/mixed_model_dyads_20260917/decisions.csv"
POPULATIONS = ROOT / "docs/figures/mixed_model_populations_20260918/games.csv"
OUTPUT = ROOT / "docs/figures/mixed_model_family_split_20260922"

TASK_ORDERS = ["game", "game_myth", "myth_game"]
ORDER_LABELS = {"game": "Game only", "game_myth": "Game → Myth", "myth_game": "Myth → Game"}
PAIRINGS = [("Sonnet", "GPT"), ("Sonnet", "Gemini"), ("Gemini", "GPT")]
LADDERS = [("Gemini", "GPT"), ("GPT", "Sonnet")]  # (minority, majority)
FAMILY_COLORS = {"Sonnet": "#7570b3", "GPT": "#d95f02", "Gemini": "#1b9e77"}
FAMILY_LONG = {"Sonnet": "Sonnet 4.5", "GPT": "GPT-5 Nano", "Gemini": "Gemini 3.7 Flash"}
METRICS = {
    "sent": ("sent", "sender_family", "Amount sent (of $5)", (0, 5.3)),
    "return": ("return_proportion", "receiver_family", "Return proportion (returned / received)", (0, 1.0)),
}


def composition_of(a: str, b: str) -> str:
    return f"{a}+{b}"


def homogeneous_label(family: str) -> str:
    return f"{family}+{family}"


# --------------------------------------------------------------------------- dyads

def dyad_run_means(decisions: pd.DataFrame) -> pd.DataFrame:
    """One row per run x family x metric: the family's mean over its own decisions."""
    rows = []
    for metric, (column, family_column, _, _) in METRICS.items():
        grouped = decisions.groupby(["path", "composition", "mixed", "task_order", "replicate_id", family_column])
        for keys, group in grouped:
            values = group[column].dropna()
            if values.empty:
                continue  # e.g. a family that never received anything cannot have a return proportion
            path, composition, mixed, task_order, replicate_id, family = keys
            rows.append({
                "path": path, "composition": composition, "mixed": bool(mixed), "task_order": task_order,
                "replicate_id": replicate_id, "family": family, "metric": metric,
                "n_decisions": int(len(values)), "value": float(values.mean()),
            })
    return pd.DataFrame(rows)


def dyad_turn_means(decisions: pd.DataFrame, metric: str) -> pd.DataFrame:
    """Mean per family and own turn (1-5).

    Senders alternate each round and the first sender alternates across
    replicates, so global round r is a family's first turn in some runs and its
    second in others. Grouping by round would pool different turns at adjacent
    points; ceil(round / 2) is the agent's own turn number in every run."""
    column, family_column, _, _ = METRICS[metric]
    d = decisions.assign(turn=(decisions["round"] + 1) // 2)
    return (d.groupby(["composition", "task_order", family_column, "turn"])[column]
            .agg(["mean", "count"]).reset_index().rename(columns={family_column: "family"}))


def plot_dyad_split(run_means: pd.DataFrame) -> None:
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    fig, axes = plt.subplots(2, 3, figsize=(14, 8.4), squeeze=False)
    for row, (metric, (_, _, ylabel, ylim)) in enumerate(METRICS.items()):
        data = run_means[run_means["metric"] == metric]
        for col, (fam_a, fam_b) in enumerate(PAIRINGS):
            ax = axes[row, col]
            mixed_label = composition_of(fam_a, fam_b)
            for x0, task_order in enumerate(TASK_ORDERS):
                for offset, family in ((-0.2, fam_a), (0.2, fam_b)):
                    color = FAMILY_COLORS[family]
                    mixed = np.sort(data[(data["composition"] == mixed_label) & (data["task_order"] == task_order)
                                         & (data["family"] == family)]["value"].to_numpy())
                    homog = np.sort(data[(data["composition"] == homogeneous_label(family)) & (data["task_order"] == task_order)
                                         & (data["family"] == family)]["value"].to_numpy())
                    x = x0 + offset
                    if len(mixed):
                        ax.boxplot(mixed, positions=[x], widths=0.22, patch_artist=True, showfliers=False, whis=1.5,
                                   boxprops=dict(facecolor=color, alpha=0.85, edgecolor="#444444"),
                                   medianprops=dict(color="#111111", linewidth=1.5),
                                   whiskerprops=dict(color="#555555"), capprops=dict(color="#555555"))
                        ax.scatter(x + np.linspace(-0.05, 0.05, len(mixed)), mixed, s=22, c=color,
                                   edgecolors="white", linewidths=0.6, zorder=3)
                    if len(homog):
                        # Homogeneous reference: hollow diamond at the mean, bar = ± sd over runs.
                        hx = x + (0.13 if offset > 0 else -0.13)
                        ax.errorbar(hx, homog.mean(), yerr=homog.std(ddof=1) if len(homog) > 1 else 0,
                                    fmt="D", mfc="white", mec=color, ms=7, mew=1.6, ecolor=color,
                                    elinewidth=1.2, capsize=3, zorder=4)
            ax.set_xticks(range(len(TASK_ORDERS)), [ORDER_LABELS[t] for t in TASK_ORDERS])
            ax.set_xlim(-0.6, len(TASK_ORDERS) - 0.4)
            ax.set_ylim(*ylim)
            if metric == "return":
                ax.axhline(0.5, color="#999999", linewidth=0.8, linestyle=":", zorder=1)
            ax.set_axisbelow(True)
            ax.grid(axis="y", alpha=0.22)
            ax.spines[["top", "right"]].set_visible(False)
            if row == 0:
                ax.set_title(f"{FAMILY_LONG[fam_a]} + {FAMILY_LONG[fam_b]}", fontsize=12, fontweight="bold", pad=8)
            if col == 0:
                ax.set_ylabel(ylabel, fontsize=11)
    handles = [Line2D([], [], marker="s", linestyle="", ms=10, color=FAMILY_COLORS[f], label=f"{FAMILY_LONG[f]} in the mixed dyad")
               for f in FAMILY_COLORS]
    handles.append(Line2D([], [], marker="D", linestyle="", ms=7, mfc="white", mec="#333333", mew=1.6,
                          label="Same family in its homogeneous dyad (mean ± sd over runs)"))
    fig.legend(handles=handles, loc="lower center", ncol=4, frameon=False, fontsize=9.5, bbox_to_anchor=(0.5, 0.0))
    fig.suptitle("What each model does inside a mixed dyad, next to what it does among its own kind\n"
                 "Fixed dyads · Informed negative-only noise · No defectors · 10 rounds",
                 fontsize=14, fontweight="bold")
    fig.text(0.5, 0.045, "Boxes and dots: per-run means over the family's own decisions (n = 6 mixed runs; "
             "5 homogeneous runs). Return proportion is undefined when nothing arrived; such runs are dropped for that family.",
             ha="center", fontsize=8.5, color="#444444")
    fig.tight_layout(rect=(0, 0.07, 1, 0.955))
    fig.savefig(OUTPUT / "2-agent-mixed-model-simulation-split.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


def plot_dyad_traces(decisions: pd.DataFrame, metric: str) -> None:
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    _, _, ylabel, ylim = METRICS[metric]
    turns = dyad_turn_means(decisions, metric)
    fig, axes = plt.subplots(len(PAIRINGS), 3, figsize=(13.5, 10), sharex=True, sharey=True, squeeze=False)
    for row, (fam_a, fam_b) in enumerate(PAIRINGS):
        mixed_label = composition_of(fam_a, fam_b)
        for col, task_order in enumerate(TASK_ORDERS):
            ax = axes[row, col]
            for family in (fam_a, fam_b):
                color = FAMILY_COLORS[family]
                homog = turns[(turns["composition"] == homogeneous_label(family)) & (turns["task_order"] == task_order)
                              & (turns["family"] == family)].sort_values("turn")
                mixed = turns[(turns["composition"] == mixed_label) & (turns["task_order"] == task_order)
                              & (turns["family"] == family)].sort_values("turn")
                ax.plot(homog["turn"], homog["mean"], color=color, linestyle="--", linewidth=1.4, alpha=0.7, zorder=2)
                ax.plot(mixed["turn"], mixed["mean"], color=color, linestyle="-", linewidth=2.2, marker="o", ms=4.5, zorder=3)
            ax.set_xticks(range(1, 6))
            ax.set_ylim(*ylim)
            if metric == "return":
                ax.axhline(0.5, color="#999999", linewidth=0.8, linestyle=":", zorder=1)
            ax.grid(alpha=0.2)
            ax.spines[["top", "right"]].set_visible(False)
            if row == 0:
                ax.set_title(ORDER_LABELS[task_order], fontsize=12, fontweight="bold")
            if col == 0:
                ax.set_ylabel(f"{FAMILY_LONG[fam_a]} + {FAMILY_LONG[fam_b]}\n{ylabel}", fontsize=10.5)
            if row == len(PAIRINGS) - 1:
                ax.set_xlabel("Own turn (each agent sends or returns every other round)")
    handles = [Line2D([], [], color=FAMILY_COLORS[f], linewidth=2.2, marker="o", label=f"{FAMILY_LONG[f]} in the mixed dyad") for f in FAMILY_COLORS]
    handles.append(Line2D([], [], color="#333333", linestyle="--", linewidth=1.4, label="Same family in its homogeneous dyad"))
    fig.legend(handles=handles, loc="lower center", ncol=4, frameon=False, fontsize=9.5)
    title = {"sent": "Amount sent on each own turn, by family", "return": "Return proportion on each own turn, by family"}[metric]
    fig.suptitle(f"{title}\nMixed dyads (solid) vs the same family among its own kind (dashed) · Informed negative-only noise · No defectors",
                 fontsize=13.5, fontweight="bold")
    note = ("Each agent sends in every other round (turns 1-5) and receives in the others. Turn k pools the family's k-th decision "
            "across runs: 6 mixed runs per family, and both agents of 5 homogeneous runs (10 decisions).")
    if metric == "return":
        note += " Turns where nothing arrived contribute no return proportion."
    fig.text(0.5, 0.035, note, ha="center", fontsize=8.5, color="#444444")
    fig.tight_layout(rect=(0, 0.06, 1, 0.955))
    fig.savefig(OUTPUT / f"dyad_family_turn_traces_{metric}.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


# --------------------------------------------------------------------------- populations

def population_run_means(games: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for metric, (column, family_column, _, _) in METRICS.items():
        grouped = games.groupby(["path", "composition", "mixed", "minority", "minority_count", "majority",
                                 "task_order", "replicate_id", family_column])
        for keys, group in grouped:
            values = group[column].dropna()
            if values.empty:
                continue
            path, composition, mixed, minority, minority_count, majority, task_order, replicate_id, family = keys
            rows.append({
                "path": path, "composition": composition, "mixed": bool(mixed), "minority": minority,
                "minority_count": int(minority_count), "majority": majority, "task_order": task_order,
                "replicate_id": replicate_id, "family": family, "metric": metric,
                "n_decisions": int(len(values)), "value": float(values.mean()),
            })
    return pd.DataFrame(rows)


def ladder_series(run_means: pd.DataFrame, metric: str, minority: str, majority: str, task_order: str, family: str):
    """Per-run values of `family` along the ladder minority_count = 0, 1, 2, 4, 8.

    0 = the homogeneous majority population, 8 = the homogeneous minority population."""
    data = run_means[(run_means["metric"] == metric) & (run_means["task_order"] == task_order) & (run_means["family"] == family)]
    points = {}
    homog_major = data[data["composition"] == f"8 {majority}"]
    homog_minor = data[data["composition"] == f"8 {minority}"]
    if family == majority and len(homog_major):
        points[0] = homog_major["value"].to_numpy()
    if family == minority and len(homog_minor):
        points[8] = homog_minor["value"].to_numpy()
    ladder = data[(data["minority"] == minority) & (data["majority"] == majority) & data["mixed"]]
    for count, group in ladder.groupby("minority_count"):
        points[int(count)] = group["value"].to_numpy()
    return dict(sorted(points.items()))


def plot_population_split(run_means: pd.DataFrame, metric: str) -> None:
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    _, _, ylabel, ylim = METRICS[metric]
    xs = [0, 1, 2, 4, 8]
    fig, axes = plt.subplots(len(LADDERS), 3, figsize=(13.5, 7.6), sharey=True, squeeze=False)
    for row, (minority, majority) in enumerate(LADDERS):
        for col, task_order in enumerate(TASK_ORDERS):
            ax = axes[row, col]
            for family, marker in ((majority, "o"), (minority, "s")):
                color = FAMILY_COLORS[family]
                series = ladder_series(run_means, metric, minority, majority, task_order, family)
                if not series:
                    continue
                pos = [xs.index(k) for k in series]
                means = [v.mean() for v in series.values()]
                ax.plot(pos, means, color=color, linewidth=2, marker=marker, ms=7, zorder=3)
                for p, v in zip(pos, series.values()):
                    ax.scatter(np.full(len(v), p) + np.linspace(-0.08, 0.08, len(v)), v, s=16, c=color,
                               alpha=0.55, edgecolors="none", zorder=2)
            ax.set_xticks(range(len(xs)), [f"{x}" for x in xs])
            ax.set_xlim(-0.4, len(xs) - 0.6)
            ax.set_ylim(*ylim)
            if metric == "return":
                ax.axhline(0.5, color="#999999", linewidth=0.8, linestyle=":", zorder=1)
            ax.set_axisbelow(True)
            ax.grid(axis="y", alpha=0.22)
            ax.spines[["top", "right"]].set_visible(False)
            if row == 0:
                ax.set_title(ORDER_LABELS[task_order], fontsize=12, fontweight="bold")
            if col == 0:
                ax.set_ylabel(f"{FAMILY_LONG[minority]} among {FAMILY_LONG[majority]}\n{ylabel}", fontsize=10.5)
            ax.set_xlabel(f"Number of {FAMILY_LONG[minority]} agents (of 8)", fontsize=10)
    handles = [Line2D([], [], color=FAMILY_COLORS[f], linewidth=2, marker="o", ms=7, label=FAMILY_LONG[f]) for f in FAMILY_COLORS]
    fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False, fontsize=10)
    title = {"sent": "Amount sent, by family, along the eight-agent contagion ladder",
             "return": "Return proportion, by family, along the eight-agent contagion ladder"}[metric]
    fig.suptitle(f"{title}\nRotating 8-agent populations · Informed negative-only noise · No defectors · 10 rounds",
                 fontsize=13.5, fontweight="bold")
    fig.text(0.5, 0.04, "Line = mean over runs of each family's per-run mean; small dots = runs (n = 5 per point). "
             "0 and 8 on the x-axis are the homogeneous September populations of the majority and minority family.",
             ha="center", fontsize=8.5, color="#444444")
    fig.tight_layout(rect=(0, 0.07, 1, 0.95))
    name = "mixed-model-simulation-8-agent-split.png" if metric == "sent" else f"population_family_split_{metric}.png"
    fig.savefig(OUTPUT / name, dpi=200, bbox_inches="tight")
    plt.close(fig)


# --------------------------------------------------------------------------- summary

def summary_table(dyads: pd.DataFrame, populations: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for metric in METRICS:
        d = dyads[dyads["metric"] == metric]
        for fam_a, fam_b in PAIRINGS:
            for task_order in TASK_ORDERS:
                for family in (fam_a, fam_b):
                    mixed = d[(d["composition"] == composition_of(fam_a, fam_b)) & (d["task_order"] == task_order) & (d["family"] == family)]["value"]
                    homog = d[(d["composition"] == homogeneous_label(family)) & (d["task_order"] == task_order) & (d["family"] == family)]["value"]
                    rows.append(_summary_row("dyad", composition_of(fam_a, fam_b), task_order, family, metric, mixed, homog))
        p = populations[populations["metric"] == metric]
        for minority, majority in LADDERS:
            for task_order in TASK_ORDERS:
                ladder = p[(p["minority"] == minority) & (p["majority"] == majority) & p["mixed"] & (p["task_order"] == task_order)]
                for composition, group in ladder.groupby("composition", sort=False):
                    for family in (minority, majority):
                        mixed = group[group["family"] == family]["value"]
                        homog = p[(p["composition"] == f"8 {family}") & (p["task_order"] == task_order) & (p["family"] == family)]["value"]
                        rows.append(_summary_row("population", composition, task_order, family, metric, mixed, homog))
    return pd.DataFrame(rows)


def _summary_row(setting, composition, task_order, family, metric, mixed, homog):
    return {
        "setting": setting, "composition": composition, "task_order": task_order, "family": family, "metric": metric,
        "n_mixed_runs": int(len(mixed)), "mixed_mean": float(mixed.mean()) if len(mixed) else np.nan,
        "mixed_sd": float(mixed.std(ddof=1)) if len(mixed) > 1 else np.nan,
        "n_homogeneous_runs": int(len(homog)), "homogeneous_mean": float(homog.mean()) if len(homog) else np.nan,
        "homogeneous_sd": float(homog.std(ddof=1)) if len(homog) > 1 else np.nan,
        "shift_mixed_minus_homogeneous": float(mixed.mean() - homog.mean()) if len(mixed) and len(homog) else np.nan,
    }


def main() -> None:
    configure_matplotlib()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    decisions = pd.read_csv(DYADS)
    games = pd.read_csv(POPULATIONS)
    if decisions["path"].nunique() != 99:
        raise SystemExit(f"Expected 99 dyad runs in {DYADS}, found {decisions['path'].nunique()}")
    if games["path"].nunique() != 135:
        raise SystemExit(f"Expected 135 population runs in {POPULATIONS}, found {games['path'].nunique()}")

    dyad_runs = dyad_run_means(decisions)
    population_runs = population_run_means(games)
    summary = summary_table(dyad_runs, population_runs)

    plot_dyad_split(dyad_runs)
    for metric in METRICS:
        plot_dyad_traces(decisions, metric)
        plot_population_split(population_runs, metric)
    write_provenance(OUTPUT, set(decisions["path"]) | set(games["path"]))

    pd.set_option("display.width", 220)
    show = summary[summary["setting"] == "dyad"].copy()
    for c in ("mixed_mean", "mixed_sd", "homogeneous_mean", "homogeneous_sd", "shift_mixed_minus_homogeneous"):
        show[c] = show[c].round(2)
    print(show.to_string(index=False))


if __name__ == "__main__":
    main()

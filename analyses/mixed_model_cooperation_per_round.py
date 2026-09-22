#!/usr/bin/env python3
"""Per-round cooperation ratios for the mixed-model figures (Figures 7 and 8).

Ed's priority (B), email after the 2026-09-22 meeting: pull out the per-round
cooperation stats behind Figures 7 (mixed dyads) and 8 (eight-agent ladder).
Those figures show only final resources; these show how each condition got
there, one panel per composition in the same layout as the boxplot figures.

Cooperation ratios follow analyses/cooperation_ratio_over_time.py:
  send fraction (round r) = sent / endowment ($5), mean over the round's senders
  return ratio  (round r) = sum(returned) / sum(received) over the round's
                            receivers that received > 0; undefined (left blank)
                            when nothing arrived
Each run gets one value per round; lines are the mean over runs, bands ± 1 sd.

Inputs (validated by the scripts that produced them):
  docs/figures/mixed_model_dyads_20260917/decisions.csv
  docs/figures/mixed_model_populations_20260918/games.csv

Outputs (docs/figures/mixed_model_cooperation_per_round_20260922/):
  fig7_dyads_send_per_round.{png,svg,pdf}      fig7_dyads_return_per_round.*
  fig8_populations_send_per_round.*            fig8_populations_return_per_round.*
  per_round_stats.csv   mean, sd, n_runs per setting x composition x task order x round x metric
  run_round_ratios.csv  one row per run x round

No API calls.
"""
from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from analyses._shared import configure_matplotlib  # noqa: E402

DYADS = ROOT / "docs/figures/mixed_model_dyads_20260917/decisions.csv"
POPULATIONS = ROOT / "docs/figures/mixed_model_populations_20260918/games.csv"
OUTPUT = ROOT / "docs/figures/mixed_model_cooperation_per_round_20260922"
ENDOWMENT = 5.0

TASK_ORDERS = ["game", "game_myth", "myth_game"]
ORDER_LABELS = {"game": "Game only", "game_myth": "Game → Myth", "myth_game": "Myth → Game"}
LINE_COLORS = {"game": "#777777", "game_myth": "#fc8d62", "myth_game": "#66c2a5"}
# Same panel order as the Figure 7 boxplot grid (scripts/analyze_mixed_model_dyads.py).
DYAD_ROWS = [
    ("Homogeneous dyads\n(September controls)", ["Sonnet+Sonnet", "GPT+GPT", "Gemini+Gemini"]),
    ("Mixed dyads", ["Sonnet+GPT", "Sonnet+Gemini", "Gemini+GPT"]),
]
# Same panel order as the Figure 8 boxplot grid (scripts/analyze_mixed_model_populations.py).
LADDERS = [("Gemini", "GPT"), ("GPT", "Sonnet")]  # (minority, majority)
POPULATION_ROWS = [
    (f"{minority} among {majority}",
     [f"8 {majority}"] + [f"{n} {minority} + {8 - n} {majority}" for n in (1, 2, 4)] + [f"8 {minority}"])
    for minority, majority in LADDERS
]
METRICS = {
    "send": ("send_fraction", "Send fraction (sent / $5)"),
    "return": ("return_ratio", "Return ratio (returned / received)"),
}


def run_round_ratios(games: pd.DataFrame, setting: str) -> pd.DataFrame:
    rows = []
    for (path, composition, task_order, round_), g in games.groupby(["path", "composition", "task_order", "round"], sort=False):
        received = g.loc[g["received"] > 0]
        rows.append({
            "setting": setting, "path": path, "composition": composition, "task_order": task_order,
            "round": int(round_),
            "send_fraction": float(g["sent"].mean() / ENDOWMENT),
            "return_ratio": float(received["returned"].sum() / received["received"].sum()) if len(received) else np.nan,
        })
    return pd.DataFrame(rows)


def per_round_stats(runs: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for metric, (column, _) in METRICS.items():
        for keys, g in runs.groupby(["setting", "composition", "task_order", "round"], sort=False):
            values = g[column].dropna()
            rows.append({
                "setting": keys[0], "composition": keys[1], "task_order": keys[2], "round": keys[3],
                "metric": metric, "n_runs_total": int(len(g)), "n_runs_defined": int(len(values)),
                "mean": float(values.mean()) if len(values) else np.nan,
                "sd": float(values.std(ddof=1)) if len(values) > 1 else np.nan,
            })
    return pd.DataFrame(rows)


def plot_grid(stats: pd.DataFrame, setting: str, rows, metric: str, filename: str, title: str, note: str) -> None:
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    _, ylabel = METRICS[metric]
    ncols = len(rows[0][1])
    fig, axes = plt.subplots(len(rows), ncols, figsize=(4.4 * ncols, 3.9 * len(rows) + 0.6),
                             sharex=True, sharey=True, squeeze=False)
    data = stats[(stats["setting"] == setting) & (stats["metric"] == metric)]
    for axrow, (row_label, compositions) in zip(axes, rows):
        for ax, composition in zip(axrow, compositions):
            n_runs = 0
            for task_order in TASK_ORDERS:
                d = data[(data["composition"] == composition) & (data["task_order"] == task_order)].sort_values("round")
                if d.empty:
                    continue
                n_runs = max(n_runs, int(d["n_runs_total"].max()))
                x = d["round"].to_numpy()
                mean = d["mean"].to_numpy()
                sd = np.nan_to_num(d["sd"].to_numpy())
                color = LINE_COLORS[task_order]
                ax.fill_between(x, np.clip(mean - sd, 0, 1), np.clip(mean + sd, 0, 1), color=color, alpha=0.15, linewidth=0)
                ax.plot(x, mean, color=color, linewidth=2.2, marker="o", ms=3.5)
            if metric == "return":
                ax.axhline(1 / 3, color="#bbbbbb", linewidth=0.9, linestyle="--", zorder=0)
                ax.axhline(0.5, color="#bbbbbb", linewidth=0.9, linestyle=":", zorder=0)
            kind = "homogeneous" if (composition.startswith("8 ") or composition.split("+")[0] == composition.split("+")[-1]) else "mixed"
            ax.set_title(f"{composition.replace('+', ' + ')}\n{kind} · n = {n_runs} runs", fontsize=11, fontweight="bold", pad=6)
            ax.set_xticks(range(1, 11))
            ax.set_xlim(0.6, 10.4)
            ax.set_ylim(0, 1.02)
            ax.grid(alpha=0.2)
            ax.spines[["top", "right"]].set_visible(False)
        axrow[0].set_ylabel(row_label, fontsize=11.5, fontweight="bold", labelpad=10)
    for ax in axes[-1]:
        ax.set_xlabel("Round")
    handles = [Line2D([], [], color=LINE_COLORS[t], linewidth=2.2, marker="o", ms=4, label=ORDER_LABELS[t]) for t in TASK_ORDERS]
    if metric == "return":
        handles += [Line2D([], [], color="#bbbbbb", linestyle="--", label="1/3 = sender breaks even"),
                    Line2D([], [], color="#bbbbbb", linestyle=":", label="1/2 = gain split evenly")]
    fig.legend(handles=handles, loc="lower center", ncol=len(handles), frameon=False, fontsize=10)
    fig.suptitle(title, fontsize=14, fontweight="bold")
    fig.supylabel(ylabel, fontsize=12, x=0.004)
    fig.text(0.5, 0.035, note, ha="center", fontsize=8.8, color="#444444")
    fig.tight_layout(rect=(0.02, 0.07, 1, 0.93), h_pad=1.8, w_pad=1.2)
    for ext in ("png", "svg", "pdf"):
        fig.savefig(OUTPUT / f"{filename}.{ext}", dpi=200, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    configure_matplotlib()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    dyads = pd.read_csv(DYADS)
    populations = pd.read_csv(POPULATIONS)
    if dyads["path"].nunique() != 99 or populations["path"].nunique() != 135:
        raise SystemExit("Unexpected run counts in the input tables")
    runs = pd.concat([run_round_ratios(dyads, "dyad"), run_round_ratios(populations, "population")], ignore_index=True)
    runs.to_csv(OUTPUT / "run_round_ratios.csv", index=False)
    stats = per_round_stats(runs)
    stats.to_csv(OUTPUT / "per_round_stats.csv", index=False)

    band = "Line = mean over runs, band = ± 1 sd over runs."
    blank = " Return ratio is undefined in a round where nothing was received; such rounds are left out of the mean, and lines break where no run has a value."
    plot_grid(stats, "dyad", DYAD_ROWS, "send", "fig7_dyads_send_per_round",
              "How much senders trust, round by round (Figure 7 dyads)\nInformed negative-only noise · No defectors",
              band + " Homogeneous n = 5 runs, mixed n = 6. Where lines are hidden they coincide (e.g. Gemini + Gemini: all three at 1.0).")
    plot_grid(stats, "dyad", DYAD_ROWS, "return", "fig7_dyads_return_per_round",
              "How much receivers give back, round by round (Figure 7 dyads)\nInformed negative-only noise · No defectors",
              band + blank)
    plot_grid(stats, "population", POPULATION_ROWS, "send", "fig8_populations_send_per_round",
              "How much senders trust, round by round (Figure 8, eight-agent ladder)\nInformed negative-only noise · No defectors · all 8 agents",
              band + " Each run's value is the mean over the round's four games. n = 5 runs per panel.")
    plot_grid(stats, "population", POPULATION_ROWS, "return", "fig8_populations_return_per_round",
              "How much receivers give back, round by round (Figure 8, eight-agent ladder)\nInformed negative-only noise · No defectors · all 8 agents",
              band + " Per run and round: total returned / total received over the games where something arrived." + blank)


if __name__ == "__main__":
    main()

"""Percent returned (returned / received) per round, one series per model.

Answers the 2026-08-24 meeting request: "each data point is the proportion
returned over received across all the runs — rounds on the X axis, return on
the Y axis, one series per model."

A dyad round with received == 0 offers no return opportunity and is excluded
(not counted as 0% cooperation).

Usage (from repo root):
    python analyses/return_ratio_across_models.py \
        --set "Claude Sonnet 4.5=data/json/sonnet45_8agent_myth_directive_history3_anon_r10_n5" \
        --set "GPT-5 nano=data/json/gpt5nano_8agent_myth_directive_history3_anon_r10_n5" \
        --set "Gemini 3.1 Flash-Lite=data/json/gemini31_flashlite_8agent_myth_directive_history3_r10_n5" \
        --output-dir data/plots/return_ratio_across_models

Defaults to exactly those three matched sets (8 agents, myth->game, 10 rounds,
n=5, plain condition — no transfer noise).
"""

import argparse
import glob
import json
import os
from collections import defaultdict

import numpy as np

from _shared import configure_matplotlib, load_simulation_data

configure_matplotlib()
import matplotlib.pyplot as plt  # noqa: E402

DEFAULT_SETS = [
    "Claude Sonnet 4.5=data/json/sonnet45_8agent_myth_directive_history3_anon_r10_n5",
    "GPT-5 nano=data/json/gpt5nano_8agent_myth_directive_history3_anon_r10_n5",
    "Gemini 3.1 Flash-Lite=data/json/gemini31_flashlite_8agent_myth_directive_history3_r10_n5",
]

SERIES_COLORS = ["#2a78d6", "#1baf7a", "#eda100"]

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRIDLINE = "#e1e0d9"
BASELINE = "#c3c2b7"


def simulation_files(experiment_dir):
    files = glob.glob(os.path.join(experiment_dir, "**", "*.json"), recursive=True)
    return sorted(
        f for f in files
        if not f.endswith(".results.json") and ".checkpoint" not in f
    )


def collect_ratios(experiment_dir):
    """Return {round: [returned/received, ...]} pooled over runs and dyads.

    Denominator is what the trustee was TOLD they received
    (``received_communicated``, present in noisy runs — trust_game_noisy
    builds the trustee prompt from sent_communicated * multiplier), falling
    back to actual ``received`` for plain runs.

    Dyads whose trustee is not a standard LLM agent (hardcoded defectors,
    ``agent_types`` != "standard") are excluded: their return is scripted,
    not a behavior.
    """
    by_round = defaultdict(list)
    n_files = 0
    n_skipped_zero = 0
    n_skipped_defector = 0
    for path in simulation_files(experiment_dir):
        data = load_simulation_data(path)
        n_files += 1
        for rec in data.get("conversation_history", []):
            agent_types = rec.get("agent_types") or {}
            dyads = rec.get("dyads")
            if dyads is None:
                # 2-agent format: values live at the top level of the record
                dyads = [rec] if rec.get("returned") is not None else []
            for dyad in dyads:
                trustee = dyad.get("trustee")
                if trustee and agent_types.get(trustee, "standard") != "standard":
                    n_skipped_defector += 1
                    continue
                received = dyad.get("received_communicated")
                if received is None:
                    received = dyad.get("received")
                returned = dyad.get("returned")
                if received is None or returned is None:
                    continue
                if received <= 0:
                    n_skipped_zero += 1
                    continue
                by_round[rec["round"]].append(returned / received)
    return by_round, n_files, n_skipped_zero, n_skipped_defector


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--set", dest="sets", action="append", metavar="LABEL=DIR",
        help="Model label and experiment dir (repeatable). Defaults to the "
             "three matched 8-agent myth_game sets.",
    )
    parser.add_argument(
        "--output-dir", default="data/plots/return_ratio_across_models",
    )
    parser.add_argument(
        "--output-name", default="return_ratio_across_models",
        help="Basename of the saved PNG (no extension).",
    )
    parser.add_argument(
        "--note",
        default="8 agents, myth→game, 10 rounds, plain condition (no transfer "
                "noise); dyad rounds with $0 received excluded.",
        help="Condition description shown under the figure.",
    )
    args = parser.parse_args()
    sets = [s.split("=", 1) for s in (args.sets or DEFAULT_SETS)]
    os.makedirs(args.output_dir, exist_ok=True)

    fig, (ax_line, ax_dist) = plt.subplots(
        1, 2, figsize=(12, 4.8), width_ratios=[2, 1],
    )
    fig.patch.set_facecolor(SURFACE)

    summary = []
    pooled_per_model = []
    all_rounds = set()
    for i, (label, exp_dir) in enumerate(sets):
        color = SERIES_COLORS[i % len(SERIES_COLORS)]
        by_round, n_files, n_zero, n_defector = collect_ratios(exp_dir)
        if not by_round:
            print(f"WARNING: no game data found under {exp_dir}, skipping {label}")
            continue
        rounds = sorted(by_round)
        all_rounds.update(rounds)
        means = np.array([np.mean(by_round[r]) for r in rounds]) * 100
        stds = np.array([np.std(by_round[r]) for r in rounds]) * 100
        ax_line.plot(rounds, means, color=color, linewidth=2, marker="o",
                     markersize=5, label=label, zorder=3)
        ax_line.fill_between(rounds, np.maximum(means - stds, 0), means + stds,
                             color=color, alpha=0.12, linewidth=0, zorder=2)
        ax_line.annotate(
            label, (rounds[-1], means[-1]), xytext=(8, 0),
            textcoords="offset points", va="center", fontsize=9,
            color=INK, fontweight="bold",
            bbox=dict(facecolor=SURFACE, edgecolor="none", pad=1.5),
        )

        pooled = np.concatenate([np.array(by_round[r]) for r in rounds]) * 100
        pooled_per_model.append((label, color, pooled))
        summary.append((label, n_files, len(pooled), n_zero, n_defector,
                        np.mean(pooled), np.std(pooled)))

    for ax in (ax_line, ax_dist):
        ax.set_facecolor(SURFACE)
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
        for spine in ("left", "bottom"):
            ax.spines[spine].set_color(BASELINE)
        ax.tick_params(colors=INK_MUTED, labelsize=9)
        ax.yaxis.grid(True, color=GRIDLINE, linewidth=0.8, zorder=0)
        ax.set_axisbelow(True)
        ax.axhline(50, color=INK_MUTED, linewidth=1, linestyle=(0, (4, 4)),
                   zorder=1)

    ax_line.set_xlabel("Round", color=INK_SECONDARY, fontsize=10)
    ax_line.set_ylabel("Returned / received (%)", color=INK_SECONDARY, fontsize=10)
    ax_line.set_title("Percent returned per round (mean ± std across dyads and runs)",
                      color=INK, fontsize=11, loc="left")
    rounds_sorted = sorted(all_rounds)
    if rounds_sorted:
        ax_line.set_xticks(rounds_sorted)
        ax_line.set_xlim(rounds_sorted[0] - 0.3, rounds_sorted[-1] + 1.8)  # room for direct labels
    leg = ax_line.legend(frameon=True, fontsize=9, labelcolor=INK_SECONDARY,
                         loc="best", facecolor=SURFACE, edgecolor=GRIDLINE)
    leg.set_zorder(5)

    # Pooled distribution panel: violins with the same fixed hue per model
    positions = np.arange(len(pooled_per_model))
    parts = ax_dist.violinplot(
        [p for _, _, p in pooled_per_model], positions=positions,
        showextrema=False, widths=0.8,
    )
    for body, (_, color, _) in zip(parts["bodies"], pooled_per_model):
        body.set_facecolor(color)
        body.set_alpha(0.35)
        body.set_edgecolor(color)
        body.set_linewidth(1.5)
    for pos, (_, color, pooled) in zip(positions, pooled_per_model):
        ax_dist.scatter([pos], [np.mean(pooled)], color=color, s=36, zorder=3)
        ax_dist.vlines(pos, np.percentile(pooled, 25), np.percentile(pooled, 75),
                       color=color, linewidth=2.5, zorder=2)
    ax_dist.set_xticks(positions)
    ax_dist.set_xticklabels(
        [label.replace(" ", "\n", 1) for label, _, _ in pooled_per_model],
        fontsize=8.5, color=INK_SECONDARY,
    )
    ax_dist.set_title("Pooled over all rounds (dot = mean, bar = IQR)",
                      color=INK, fontsize=11, loc="left")

    fig.text(0.01, 0.005, args.note + " Dashed line: 50%.",
             fontsize=8, color=INK_MUTED)
    fig.tight_layout(rect=(0, 0.03, 1, 1))

    out = os.path.join(args.output_dir, args.output_name + ".png")
    fig.savefig(out, dpi=200, facecolor=SURFACE, bbox_inches="tight")
    print(f"Saved {out}\n")

    print(f"{'Model':<24} {'runs':>4} {'obs':>5} {'zero-recv':>9} "
          f"{'def-trustee':>11}  mean (±std)")
    for label, n_files, n_obs, n_zero, n_def, mean, std in summary:
        print(f"{label:<24} {n_files:>4} {n_obs:>5} {n_zero:>9} {n_def:>11}  "
              f"{mean:.1f}% (±{std:.1f}%)")


if __name__ == "__main__":
    main()

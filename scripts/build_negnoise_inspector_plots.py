#!/usr/bin/env python3
"""Build inspector plots for Aron's negative-noise + defectors campaign.

Reads the shared-run download at
  nlet-hf-data/uploaders/vallinder/data/json/noise_experiments/
      negative_only_crossmodel_defectors_n5_20260825/
and writes per-model aggregate figures for the standalone negnoise inspector
(built by scripts/build_negnoise_inspector.py):
  data/plots/inspector_negnoise/agg_plots/<model>/dyad.png
  data/plots/inspector_negnoise/agg_plots/<model>/pop8.png
  data/plots/inspector_negnoise/agg_plots/_all/overview.png

Usage: python3 scripts/build_negnoise_inspector_plots.py
"""
import glob
import json
import math
import os
import re
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CAMPAIGN = (
    PROJECT_ROOT
    / "nlet-hf-data/uploaders/vallinder/data/json/noise_experiments"
    / "negative_only_crossmodel_defectors_n5_20260825"
)
OUT = PROJECT_ROOT / "data/plots/inspector_negnoise/agg_plots"

MODELS = ["claude-sonnet-4.5", "gemini-3.7-flash", "gpt-5-nano"]
MODEL_LABELS = {
    "claude-sonnet-4.5": "Claude Sonnet 4.5",
    "gemini-3.7-flash": "Gemini 3.7 Flash",
    "gpt-5-nano": "GPT-5 Nano",
}
ORDER_LABELS = {"game": "game only", "game_myth": "game → myth", "myth_game": "myth → game"}
VARIANTS = ["none", "25%", "50%"]
VARIANT_COLORS = {"none": "#4C72B0", "25%": "#DD8452", "50%": "#C44E52"}
MODEL_COLORS = {"claude-sonnet-4.5": "#55A868", "gemini-3.7-flash": "#4C72B0", "gpt-5-nano": "#8172B3"}
N_ROUNDS = 10


def variant_of(params_dir: str) -> str:
    if "random25" in params_dir or "defectors25" in params_dir:
        return "25%"
    if "random50" in params_dir or "defectors50" in params_dir:
        return "50%"
    return "none"


def load_runs():
    """-> {(arm, model, order, variant): [run, ...]} where run has per-round
    send lists and pooled returned/received per round."""
    cells = defaultdict(list)
    for path in glob.glob(str(CAMPAIGN / "**/*.json"), recursive=True):
        if path.endswith(".results.json") or "checkpoint" in path:
            continue
        rel = os.path.relpath(path, CAMPAIGN).split(os.sep)
        arm_dir, model, order, params = rel[0], rel[1], rel[2], rel[3]
        arm = "dyad" if "dyad" in arm_dir else "pop8"
        with open(path) as f:
            data = json.load(f)
        sends = defaultdict(list)  # round -> [sent, ...]
        ret = defaultdict(float)  # round -> pooled returned
        recv = defaultdict(float)  # round -> pooled received (3x post-noise... use 3*sent)
        for turn in data.get("conversation_history", []):
            rd = turn.get("round")
            for dy in turn.get("dyads") or []:
                s, r = dy.get("sent"), dy.get("returned")
                if isinstance(s, (int, float)):
                    sends[rd].append(s)
                    if isinstance(r, (int, float)):
                        ret[rd] += r
                        recv[rd] += s * 3
        if sends:
            cells[(arm, model, order, variant_of(params))].append(
                {"sends": sends, "ret": ret, "recv": recv}
            )
    return cells


def round_stats(runs):
    """Per-round mean sent (±SEM across runs) and pooled return proportion."""
    rounds = list(range(1, N_ROUNDS + 1))
    send_mean, send_sem, ret_prop = [], [], []
    for rd in rounds:
        per_run = [np.mean(r["sends"][rd]) for r in runs if r["sends"].get(rd)]
        if per_run:
            send_mean.append(np.mean(per_run))
            send_sem.append(np.std(per_run, ddof=1) / math.sqrt(len(per_run)) if len(per_run) > 1 else 0.0)
        else:
            send_mean.append(np.nan)
            send_sem.append(0.0)
        tot_ret = sum(r["ret"].get(rd, 0.0) for r in runs)
        tot_recv = sum(r["recv"].get(rd, 0.0) for r in runs)
        ret_prop.append(tot_ret / tot_recv if tot_recv > 0 else np.nan)
    return np.array(rounds), np.array(send_mean), np.array(send_sem), np.array(ret_prop)


def plot_arm(cells, model, arm, out_path):
    orders = [o for o in ["game", "game_myth", "myth_game"] if any((arm, model, o, v) in cells for v in VARIANTS)]
    if not orders:
        return False
    fig, axes = plt.subplots(2, len(orders), figsize=(4.6 * len(orders), 6.4), squeeze=False)
    defect_word = "random defection" if arm == "dyad" else "defectors"
    for col, order in enumerate(orders):
        ax_s, ax_r = axes[0][col], axes[1][col]
        for v in VARIANTS:
            runs = cells.get((arm, model, order, v))
            if not runs:
                continue
            rounds, sm, se, rp = round_stats(runs)
            label = f"no {defect_word}" if v == "none" else f"{v} {defect_word}"
            c = VARIANT_COLORS[v]
            ax_s.plot(rounds, sm, "-o", ms=3.5, color=c, label=f"{label} (n={len(runs)})")
            ax_s.fill_between(rounds, sm - se, sm + se, color=c, alpha=0.18, linewidth=0)
            ax_r.plot(rounds, rp, "-o", ms=3.5, color=c)
        ax_s.set_title(ORDER_LABELS[order], fontsize=11)
        ax_s.set_ylim(-0.15, 5.3)
        ax_s.axhline(5, color="#999", lw=0.7, ls=":")
        ax_r.set_ylim(0, 0.65)
        ax_r.axhline(1 / 3, color="#999", lw=0.7, ls=":")
        ax_r.set_xlabel("round")
        if col == 0:
            ax_s.set_ylabel("mean sent ($)")
            ax_r.set_ylabel("return proportion")
        ax_s.legend(fontsize=8, loc="lower left")
        for ax in (ax_s, ax_r):
            ax.set_xticks(rounds)
            ax.grid(alpha=0.25)
    arm_label = "dyad (2 agents)" if arm == "dyad" else "population (8 agents)"
    fig.suptitle(
        f"{MODEL_LABELS[model]} — {arm_label} · negative-only noise (uniform $0–1, informed)",
        fontsize=12.5,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(out_path, dpi=140)
    plt.close(fig)
    return True


def plot_overview(cells, out_path):
    """Cross-model comparison, game-only task order: run-mean sent per defection level."""
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.4))
    for ax, arm, title in [
        (axes[0], "dyad", "dyad (2 agents) · game only"),
        (axes[1], "pop8", "population (8 agents) · game only"),
    ]:
        x = np.arange(len(VARIANTS))
        width = 0.26
        for i, model in enumerate(MODELS):
            means, sds, ns = [], [], []
            for v in VARIANTS:
                runs = cells.get((arm, model, "game", v), [])
                rm = [np.mean([s for lst in r["sends"].values() for s in lst]) for r in runs]
                means.append(np.mean(rm) if rm else np.nan)
                sds.append(np.std(rm, ddof=1) if len(rm) > 1 else 0.0)
                ns.append(len(rm))
            bars = ax.bar(
                x + (i - 1) * width, means, width, yerr=sds, capsize=3,
                color=MODEL_COLORS[model], label=MODEL_LABELS[model],
            )
            for b, n in zip(bars, ns):
                if n and not np.isnan(b.get_height()):
                    ax.text(b.get_x() + b.get_width() / 2, 0.08, f"n={n}",
                            ha="center", fontsize=7, color="#fff")
        ax.set_xticks(x)
        ax.set_xticklabels(["no defection", "25% defection", "50% defection"])
        ax.set_ylim(0, 5.4)
        ax.axhline(5, color="#999", lw=0.7, ls=":")
        ax.set_title(title, fontsize=11)
        ax.grid(axis="y", alpha=0.25)
    axes[0].set_ylabel("mean sent ($, run means ± SD)")
    axes[0].legend(fontsize=9)
    fig.suptitle("Negative-only noise + defectors · mean send by model", fontsize=12.5)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(out_path, dpi=140)
    plt.close(fig)


def main():
    if not CAMPAIGN.is_dir():
        raise SystemExit(f"Campaign dir not found: {CAMPAIGN}\nRun ./scripts/sync_data.sh pull (or re-download nlet-hf-data) first.")
    cells = load_runs()
    print(f"Loaded {sum(len(v) for v in cells.values())} runs across {len(cells)} cells.")
    for model in MODELS:
        mdir = OUT / model
        mdir.mkdir(parents=True, exist_ok=True)
        for arm in ("dyad", "pop8"):
            if plot_arm(cells, model, arm, mdir / f"{arm}.png"):
                print(f"  wrote {mdir / (arm + '.png')}")
    adir = OUT / "_all"
    adir.mkdir(parents=True, exist_ok=True)
    plot_overview(cells, adir / "overview.png")
    print(f"  wrote {adir / 'overview.png'}")


if __name__ == "__main__":
    main()

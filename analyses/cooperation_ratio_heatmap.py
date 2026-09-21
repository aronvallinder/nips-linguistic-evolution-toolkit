#!/usr/bin/env python3
"""Cooperation-ratio heatmaps by round for the negative-only informed-noise rerun.

Same panel layout as the resources summary heatmap in
analyses/figure2_noise_comparison.py (model rows x population columns, task
orders as heatmap rows), but the heatmap columns are rounds 1-10 instead of
noise conditions, and each cell is the mean over the five runs of a per-round
cooperation ratio. The ratios are the ones plotted as lines in
analyses/cooperation_ratio_over_time.py (send fraction, return ratio); the
per-round computation is imported from there so the numbers agree.

Inputs are the 270 hash-verified finals of the 2026-09-09 negative-only
reasoning rerun (docs/figures/negative_only_crossmodel_reasoning_rerun_20260909/
run_manifest.csv + provenance.json). No API calls.

Outputs (in --out):
  send_fraction_control.png / return_ratio_control.png       no forced defection
  <metric>_<level>_<scope>.png   level in {25, 50} (dyads: random defection;
                                 populations: 2 or 4 designated defectors),
                                 scope in {all_agents, ordinary_agents}
  cell_round_values.csv          the mean and std behind every cell
  README.md, provenance.json

Usage (from repo root):
  python analyses/cooperation_ratio_heatmap.py
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
import warnings
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.experiment_condition import read_final_run, output_provenance  # noqa: E402
from _shared import configure_matplotlib  # noqa: E402
from cooperation_ratio_over_time import round_ratios  # noqa: E402

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import seaborn as sns  # noqa: E402

RERUN = ROOT / "docs/figures/negative_only_crossmodel_reasoning_rerun_20260909"
DEFAULT_OUT = ROOT / "docs/figures/negative_only_crossmodel_reasoning_rerun_20260909_cooperation_heatmaps"

MODELS = ["openai/gpt-5-nano", "google/gemini-3.7-flash", "anthropic/claude-sonnet-4.5"]
LABELS = ["GPT-5 Nano", "Gemini 3.7 Flash", "Claude Sonnet 4.5"]
ORDERS = ["game", "game_myth", "myth_game"]
ORDER_LABELS = ["Game only", "Game → Myth", "Myth → Game"]
ROUNDS = list(range(1, 11))
# key -> (file stem, short label, subtitle, colour-scale max, colour-bar ticks)
METRICS = {
    "send": ("send_fraction", "Send fraction", "Fraction of the $5 endowment sent (mean over 5 runs)", 1.0, [0, 0.5, 1]),
    "ret": ("return_ratio", "Return ratio",
            "Returned / received by trustees (mean over 5 runs) · blank = nobody received anything", 0.6, [0, 1 / 3, 0.5]),
}
# (dyad treatment, population treatment, level tag, subtitle)
LEVELS = [
    ("control", "control", "control", "No defectors"),
    ("random25", "defectors25", "25", "Dyads: 25% random defection · Populations: 2 of 8 defectors"),
    ("random50", "defectors50", "50", "Dyads: 50% random defection · Populations: 4 of 8 defectors"),
]


def load() -> tuple[list[dict], list[dict]]:
    provenance = json.loads((RERUN / "provenance.json").read_text())
    hashes = {r["path"]: r["sha256"] for r in provenance["runs"]}
    with (RERUN / "run_manifest.csv").open() as fh:
        manifest = list(csv.DictReader(fh))
    assert len(manifest) == 270 and set(r["path"] for r in manifest) == set(hashes)
    runs, sources = [], []
    for row in manifest:
        path = ROOT / row["path"]
        sha = hashlib.sha256(path.read_bytes()).hexdigest()
        assert sha == hashes[row["path"]], row["path"]
        data = read_final_run(path)
        meta = data["run_metadata"]
        assert meta["model"] == row["model_id"] and meta["num_turns"] == 10
        noise = meta["noise_config"]
        assert noise["direction"] == "negative" and noise["inform_agents"] is True, row["path"]
        assert [r["round"] for r in data["conversation_history"]] == ROUNDS
        ratios = {scope: round_ratios(data, ordinary_only=(scope == "ordinary")) for scope in ("all", "ordinary")}
        assert ratios["all"] is not None
        runs.append(
            dict(
                model=meta["model"],
                num_agents=int(row["num_agents"]),
                task_order="_".join(data["task_order"]),
                treatment=row["treatment"],
                replicate=int(row["replicate_id"]),
                ratios=ratios,
                source_path=row["path"],
            )
        )
        sources.append(dict(path=row["path"], sha256=sha))
    return runs, sources


def cell_matrix(cells, model, n, treatment, scope, metric):
    runs = cells[(model, n, treatment)]
    assert len(runs) == 15, (model, n, treatment, len(runs))
    out = np.full((len(ORDERS), len(ROUNDS)), np.nan)
    stds = np.full_like(out, np.nan)
    for i, order in enumerate(ORDERS):
        mats = [r["ratios"][scope][metric] for r in runs if r["task_order"] == order]
        assert len(mats) == 5, (model, n, treatment, order, len(mats))
        stack = np.vstack(mats)
        with np.errstate(all="ignore"), warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)  # all-NaN rounds (nobody received) stay NaN
            out[i] = np.nanmean(stack, axis=0)
            stds[i] = np.nanstd(stack, axis=0, ddof=1)
    return out, stds


def draw(cells, metric, dyad_treat, pop_treat, scope, subtitle, out: Path, name: str):
    _, short, long, vmax, ticks = METRICS[metric]
    scope_txt = "all agents" if scope == "all" else "ordinary (non-defector) agents only"
    with sns.axes_style("white"), sns.plotting_context("notebook", font_scale=1):
        fig, axes = plt.subplots(3, 2, figsize=(15, 8.6))
        cmap = sns.blend_palette(["#f1f1ef", "#cbded7", "#72b6a1"], as_cmap=True)
        for i, (model, label) in enumerate(zip(MODELS, LABELS)):
            for j, n in enumerate([2, 8]):
                ax = axes[i, j]
                treatment = dyad_treat if n == 2 else pop_treat
                matrix, _ = cell_matrix(cells, model, n, treatment, scope, metric)
                sns.heatmap(
                    matrix, ax=ax, cmap=cmap, vmin=0, vmax=vmax,
                    annot=True, fmt=".2f", annot_kws={"fontsize": 9, "color": "#303c38"},
                    linewidths=1.5, linecolor="white", cbar=False,
                    xticklabels=[str(r) for r in ROUNDS],
                    yticklabels=ORDER_LABELS if j == 0 else False,
                )
                ax.tick_params(axis="both", length=0, labelsize=10, pad=6)
                ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
                ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
                if i == 2:
                    ax.set_xlabel("Round", fontsize=10, color="#555555", labelpad=6)
                if j == 0:
                    ax.set_ylabel(label, fontsize=12, fontweight="semibold", labelpad=16, color="#333333")
                if i == 0:
                    ax.set_title(f"{n} agents", fontsize=13, fontweight="semibold", pad=14, color="#333333")
        fig.suptitle(f"{short} by round · negative-only informed noise", fontsize=18, fontweight="semibold", y=0.975, color="#303030")
        fig.text(0.55, 0.927, f"{subtitle} · {scope_txt} · {long}", ha="center", fontsize=11, color="#666666")
        fig.subplots_adjust(left=0.16, right=0.98, top=0.85, bottom=0.17, hspace=0.42, wspace=0.08)
        cax = fig.add_axes([0.36, 0.062, 0.43, 0.017])
        bar = fig.colorbar(axes[0, 0].collections[0], cax=cax, orientation="horizontal", ticks=ticks)
        bar.ax.set_xticklabels([f"{t:.2g}" if t not in (1 / 3,) else "1/3" for t in ticks])
        bar.outline.set_visible(False)
        bar.ax.tick_params(length=0, labelsize=10)
        bar.set_label(short, fontsize=10, color="#555555", labelpad=5)
        for ext in ["png", "svg", "pdf"]:
            fig.savefig(out / f"{name}.{ext}", dpi=200, bbox_inches="tight")
        plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    configure_matplotlib()

    runs, sources = load()
    cells = defaultdict(list)
    for r in runs:
        cells[(r["model"], r["num_agents"], r["treatment"])].append(r)

    rows = []
    for metric, (fname, *_rest) in METRICS.items():
        for dyad_treat, pop_treat, level, subtitle in LEVELS:
            scopes = ["all"] if level == "control" else ["all", "ordinary"]
            for scope in scopes:
                name = f"{fname}_{level}" if level == "control" else f"{fname}_{level}_{scope}_agents"
                draw(cells, metric, dyad_treat, pop_treat, scope, subtitle, args.out, name)
                for model in MODELS:
                    for n in [2, 8]:
                        treatment = dyad_treat if n == 2 else pop_treat
                        means, stds = cell_matrix(cells, model, n, treatment, scope, metric)
                        for i, order in enumerate(ORDERS):
                            for k, rnd in enumerate(ROUNDS):
                                rows.append(dict(metric=fname, model=model, num_agents=n, treatment=treatment,
                                                 agent_scope=scope, task_order=order, round=rnd,
                                                 mean=round(float(means[i, k]), 4), std=round(float(stds[i, k]), 4), n_runs=5))
    with (args.out / "cell_round_values.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    (args.out / "README.md").write_text(
        """# Cooperation ratios by round — negative-only informed-noise rerun (2026-09-09)

Same layout as the resources summary heatmap in
`docs/figures/figure2_noise_comparison_20260916/`, but the columns are rounds
1–10 instead of noise conditions. All 270 finals of the 2026-09-09 rerun were
hash-checked against its `provenance.json`; every run is negative-only
communication noise, range one, agents informed, ten rounds, pinned September
request profiles.

Each cell is the mean over the five runs of a per-round ratio, computed by the
same function as the line plots in `analyses/cooperation_ratio_over_time.py`:

- **Send fraction** = amount sent / $5 endowment, averaged over the selected
  investors that round (1.0 = investors sent everything).
- **Return ratio** = sum(returned) / sum(received) over the selected trustees
  that received more than $0 that round (0.5 = half returned; 1/3 = the
  investor breaks even). Rounds in which nobody received anything are blank.
  The return-ratio colour scale runs 0–0.6 so that the 1/3 and 0.5 landmarks
  are visible; the send-fraction scale runs 0–1.

"Selected" is all agents in the `*_control` figures. In the defector figures
`*_all_agents` includes the defectors' own zero decisions and
`*_ordinary_agents` excludes them. Dyad columns use 25%/50% random defection;
population columns use 2 or 4 designated defectors of 8. Ratios use actual
(post-noise) amounts. Means and standard deviations for every cell are in
`cell_round_values.csv`.

Two-agent panels are fixed dyads; eight-agent panels rotate partners and
provide current-partner history, so the columns do not isolate agent count.
"""
    )

    previous = json.loads((RERUN.parent / "negative_only_crossmodel_reasoning_rerun_20260909_cooperation_ratios/provenance.json").read_text())
    outputs = sorted(p for p in args.out.rglob("*") if p.is_file() and p != args.out / "provenance.json")
    document = output_provenance([ROOT / s["path"] for s in sources], outputs,
                                 allowed_differences=previous["allowed_differences"], output_root=args.out)
    for run, source in zip(document["runs"], sources):
        assert run["sha256"] == source["sha256"], source["path"]
    (args.out / "provenance.json").write_text(json.dumps(document, indent=2) + "\n")
    print(f"Verified {len(runs)} finals. Wrote {len(outputs)} outputs to {args.out}")


if __name__ == "__main__":
    main()

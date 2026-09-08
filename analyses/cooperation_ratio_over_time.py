#!/usr/bin/env python3
"""Cooperation ratios over time, same grid as the resources-over-time plots.

Same 3x3 grid (model x defection level, one colour per task order) and the same
negative-only cross-model defector runs as analyses/resources_over_time_max.py,
but the y-axis carries the repo's two "cooperation ratios" per round instead of
cumulative resources. The definition follows the "Cooperation ratios" panel in
scripts/build_negnoise_inspector.py / scripts/build_data_inspector.py and the
trust/return ratios in analyses/_shared.py:

  send fraction (round r)  = sent / endowment, mean over selected investors
                             (solid line)        1.0 = investor sent everything
  return ratio (round r)   = sum(returned) / sum(received) over selected
                             trustees that received > 0 (dotted line)
                             0.5 = trustee returned half (dotted grey rule);
                             1/3 = investor breaks even, returned = sent
                             (dashed grey rule)

"Selected agents" is all agents, or ordinary (non-defector) agents only.
Shaded bands are 95% CIs across runs (t, df = n_runs - 1).

Outputs:
  <out>/dyad_all_agents.png              mean +- 95% CI across runs
  <out>/population_all_agents.png
  <out>/population_ordinary_agents.png
  <out>/dyad_all_agents_max.png          best run only (no means, no bands):
  <out>/population_all_agents_max.png    the repetition with the highest
  <out>/population_ordinary_agents_max.png   round-averaged send fraction
  <out>/summary.csv   round-averaged send fraction and return ratio per cell,
                      plus best_rep and the best run's values

Usage (from repo root):
  python analyses/cooperation_ratio_over_time.py
  python analyses/cooperation_ratio_over_time.py --root <dir> --out <dir>
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _shared import configure_matplotlib, load_simulation_runs, write_output_provenance
from resources_over_time_max import (  # noqa: E402
    DEFAULT_ROOT,
    DEFECTION_COLS,
    MODEL_ROWS,
    POP_TITLES,
    SKIP_SUFFIXES,
    TASK_ORDERS,
    parse_condition,
)

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

DEFAULT_OUT = "data/plots/cooperation_ratio_over_time"
ENDOWMENT = 5.0

METRICS = [
    ("send", "send fraction (sent / 5)", "-"),
    ("ret", "return ratio (returned / received)", ":"),
]


def round_ratios(data: Dict, ordinary_only: bool) -> Optional[Dict[str, np.ndarray]]:
    """Per-round send fraction and pooled return ratio over selected agents."""
    agent_types = data["game_data"].get("agent_types") or {}

    def selected(agent_id: str) -> bool:
        return not ordinary_only or agent_types.get(agent_id, "standard") == "standard"

    send, ret = [], []
    for r in data["conversation_history"]:
        dyads = r.get("dyads") or []
        if not dyads:
            return None
        sends = [d["sent"] / ENDOWMENT for d in dyads if selected(d["investor"])]
        recv = [d for d in dyads if selected(d["trustee"]) and d["received"] and d["received"] > 0]
        send.append(float(np.mean(sends)) if sends else np.nan)
        ret.append(
            float(sum(d["returned"] for d in recv) / sum(d["received"] for d in recv)) if recv else np.nan
        )
    return {"send": np.asarray(send), "ret": np.asarray(ret)}


def load_runs(root: str) -> List[Dict]:
    runs = []
    for dirpath, _, files in os.walk(root):
        for fn in files:
            if not fn.endswith(".json") or fn.endswith(SKIP_SUFFIXES):
                continue
            rel = os.path.relpath(os.path.join(dirpath, fn), root).split(os.sep)
            if len(rel) != 5:
                continue
            _set, model_dir, task_order, cond_dir, _ = rel
            cond = parse_condition(cond_dir)
            if cond is None:
                continue
            with open(os.path.join(dirpath, fn)) as fh:
                data = json.load(fh)
            rep = re.search(r"_rep(\d+)", fn)
            runs.append(
                {
                    "source_path": os.path.join(dirpath, fn),
                    "population": cond["population"],
                    "defection": cond["defection"],
                    "model": model_dir,
                    "task_order": task_order,
                    "rep": int(rep.group(1)) if rep else -1,
                    "all": round_ratios(data, ordinary_only=False),
                    "ordinary": round_ratios(data, ordinary_only=True),
                }
            )
    return runs


def group_cells(runs: List[Dict], population: str, key: str):
    cells = defaultdict(list)
    for r in runs:
        if r["population"] != population or r[key] is None:
            continue
        cells[(r["model"], r["defection"], r["task_order"])].append(r[key])
    return cells


def stack(cell: List[Dict[str, np.ndarray]], metric: str) -> np.ndarray:
    n = min(len(m[metric]) for m in cell)
    return np.vstack([m[metric][:n] for m in cell])


def mean_ci(mat: np.ndarray):
    n = mat.shape[0]
    mean = np.nanmean(mat, axis=0)
    if n < 2:
        return mean, np.zeros_like(mean)
    sem = np.nanstd(mat, axis=0, ddof=1) / np.sqrt(n)
    return mean, stats.t.ppf(0.975, n - 1) * sem


def best_run_index(cell: List[Dict[str, np.ndarray]]) -> int:
    """Index of the run with the highest round-averaged send fraction."""
    return int(np.argmax([np.nanmean(m["send"]) for m in cell]))


def plot_grid(cells, population: str, key: str, out_path: str, mode: str = "mean"):
    """mode='mean': mean +- 95% CI across runs. mode='max': best run only."""
    cols = DEFECTION_COLS[population]
    fig, axes = plt.subplots(3, 3, figsize=(15, 10), sharex=True, sharey=True)
    for i, (model_dir, model_label) in enumerate(MODEL_ROWS):
        for j, (defection, col_title) in enumerate(cols):
            ax = axes[i, j]
            ax.axhline(0.5, color="#999999", lw=0.8, ls=":")  # "return half" norm
            ax.axhline(1 / 3, color="#999999", lw=0.8, ls="--")  # investor break-even (returned = sent)
            for task_order, _label, color in TASK_ORDERS:
                cell = cells.get((model_dir, defection, task_order), [])
                if not cell:
                    continue
                best = best_run_index(cell) if mode == "max" else None
                for metric, _mlabel, ls in METRICS:
                    mat = stack(cell, metric)
                    x = np.arange(1, mat.shape[1] + 1)
                    if mode == "max":
                        ax.plot(x, mat[best], color=color, ls=ls, lw=2.2)
                        continue
                    mean, ci = mean_ci(mat)
                    ax.plot(x, mean, color=color, ls=ls, lw=2.2)
                    ax.fill_between(x, mean - ci, mean + ci, color=color, alpha=0.12, lw=0)
            ax.set_ylim(0, 1.05)
            ax.set_xlim(1, 10)
            ax.set_xticks([1, 5, 10])
            ax.grid(alpha=0.3)
            if i == 0:
                ax.set_title(col_title, fontsize=12, fontweight="bold")
            if j == 0:
                ax.set_ylabel(model_label, fontsize=11, fontweight="bold")
            if i == 2:
                ax.set_xlabel("Round")
    handles = [plt.Line2D([], [], color=c, lw=2.2, label=l) for _, l, c in TASK_ORDERS]
    handles += [plt.Line2D([], [], color="k", ls=ls, lw=2.2, label=l) for _, l, ls in METRICS]
    handles += [
        plt.Line2D([], [], color="#999999", ls=":", lw=0.8, label="return half (0.5)"),
        plt.Line2D([], [], color="#999999", ls="--", lw=0.8, label="investor break-even (1/3)"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=7, frameon=False, bbox_to_anchor=(0.5, -0.01))
    agents_txt = "all agents" if key == "all" else "ordinary agents only"
    stat_txt = (
        "best of five runs (highest mean send fraction), no averaging"
        if mode == "max"
        else "shaded 95% CI across five runs"
    )
    fig.suptitle(
        f"Cooperation ratios over time — {POP_TITLES[population]}\n"
        f"Negative-only noise; actual amounts; {agents_txt}; "
        f"solid = send fraction, dotted = return ratio; {stat_txt}",
        fontsize=14,
        fontweight="bold",
    )
    fig.supylabel("Ratio")
    fig.tight_layout(rect=(0.02, 0.04, 1, 0.95))
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def summarise(cells, population: str, key: str, rows: list):
    for (model, defection, task_order), cell in sorted(cells.items()):
        row = {
            "population": population,
            "agents": key,
            "model": model,
            "defection": defection,
            "task_order": task_order,
            "n_runs": len(cell),
        }
        best = best_run_index(cell)
        for metric, _l, _ls in METRICS:
            mat = stack(cell, metric)
            per_run = np.nanmean(mat, axis=1)  # round-averaged, per run
            row[f"{metric}_mean"] = round(float(np.nanmean(per_run)), 3)
            row[f"{metric}_std"] = round(float(np.nanstd(per_run, ddof=1)) if len(cell) > 1 else 0.0, 3)
            row[f"{metric}_round1"] = round(float(np.nanmean(mat[:, 0])), 3)
            last = mat[:, -1]
            row[f"{metric}_round10"] = round(float(np.nanmean(last)), 3) if np.isfinite(last).any() else float("nan")
            row[f"{metric}_best_run"] = round(float(per_run[best]), 3)
        row["best_rep"] = best
        rows.append(row)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=DEFAULT_ROOT)
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--comparison-spec", help="JSON mapping of allowed differing fields to reasons")
    ap.add_argument("--legacy-reason", help="Explicit acknowledgement of missing historical provenance")
    args = ap.parse_args()

    configure_matplotlib()
    runs = load_runs(args.root)
    if not runs:
        sys.exit(f"No runs found under {args.root}")
    allowed = json.loads(Path(args.comparison_spec).read_text()) if args.comparison_spec else {}
    sources = [run["source_path"] for run in runs]
    load_simulation_runs(sources, allowed_differences=allowed, legacy_reason=args.legacy_reason)
    os.makedirs(args.out, exist_ok=True)
    print(f"Loaded {len(runs)} runs from {args.root}")

    rows: list = []
    figures = [
        ("dyad", "all", "dyad_all_agents.png"),
        ("population", "all", "population_all_agents.png"),
        ("population", "ordinary", "population_ordinary_agents.png"),
    ]
    for population, key, fname in figures:
        cells = group_cells(runs, population, key)
        out_path = os.path.join(args.out, fname)
        plot_grid(cells, population, key, out_path, mode="mean")
        max_path = out_path.replace(".png", "_max.png")
        plot_grid(cells, population, key, max_path, mode="max")
        summarise(cells, population, key, rows)
        print(f"wrote {out_path}\nwrote {max_path}")

    csv_path = os.path.join(args.out, "summary.csv")
    with open(csv_path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {csv_path}")
    write_output_provenance(args.out, sources, allowed_differences=allowed, legacy_reason=args.legacy_reason)


if __name__ == "__main__":
    main()

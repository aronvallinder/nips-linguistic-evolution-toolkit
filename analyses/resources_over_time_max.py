#!/usr/bin/env python3
"""Resources over time, best run per condition.

Reproduces Aron's "Resources over time" grids (model x defection level, one
line per task order) from the negative-only cross-model defector runs, but
draws the BEST run (max) per condition instead of only the mean.

For every run the per-agent cumulative balance after each round is averaged
over the selected agents (all agents, or ordinary/non-defector agents only).
Per condition (model x defection level x task order) the script then plots:

  * solid  : the single best run, i.e. the repetition with the highest
             per-agent mean balance after the last round
  * dashed : the mean over repetitions (Aron's line), for reference

It also writes a CSV with mean, max and best-repetition per cell.

Data layout (shared HF mirror, uploader "vallinder"):
  <root>/<set>/<model_dir>/<task_order>/<condition_dir>/*.json

Usage (from repo root):
  python analyses/resources_over_time_max.py
  python analyses/resources_over_time_max.py --root <dir> --out <dir>
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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _shared import configure_matplotlib, load_simulation_runs, write_output_provenance

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

DEFAULT_ROOT = (
    "data/shared_runs/uploaders/vallinder/data/json/noise_experiments/"
    "negative_only_crossmodel_defectors_n5_20260825"
)
DEFAULT_OUT = "data/plots/resources_over_time_max"

MODEL_ROWS = [
    ("gpt-5-nano", "GPT-5 Nano"),
    ("gemini-3.7-flash", "Gemini 3.7 Flash"),
    ("claude-sonnet-4.5", "Claude Sonnet 4.5"),
]
TASK_ORDERS = [
    ("game", "Game only", "#555555"),
    ("game_myth", "Game → Myth", "#1f5fd6"),
    ("myth_game", "Myth → Game", "#d62728"),
]
# Population -> ordered (defection key, column title)
DEFECTION_COLS = {
    "dyad": [
        ("none", "No forced defection"),
        ("random25", "25% random defection"),
        ("random50", "50% random defection"),
    ],
    "population": [
        ("none", "No forced defection"),
        ("defectors25", "2 of 8 defectors"),
        ("defectors50", "4 of 8 defectors"),
    ],
}
POP_TITLES = {
    "dyad": "2-agent repeated dyad",
    "population": "8-agent rotating population",
}

SKIP_SUFFIXES = (".results.json", ".checkpoint.json")


def parse_condition(cond_dir: str) -> Optional[Dict[str, str]]:
    """noisy2_crossmodel_negative_random25_twotask_r3 -> population/defection."""
    m = re.match(r"noisy(\d+)_crossmodel_negative(?:_(random\d+|defectors\d+))?_", cond_dir)
    if not m:
        return None
    population = "dyad" if m.group(1) == "2" else "population"
    return {"population": population, "defection": m.group(2) or "none"}


def per_agent_series(data: Dict, ordinary_only: bool) -> Optional[np.ndarray]:
    """Per-round mean cumulative balance over the selected agents."""
    agent_types = data["game_data"].get("agent_types") or {}
    rounds = data["conversation_history"]
    out = []
    for r in rounds:
        balances = r.get("balances") or {}
        if not balances:
            return None
        ids = [a for a in balances if not ordinary_only or agent_types.get(a, "standard") == "standard"]
        if not ids:
            return None
        out.append(float(np.mean([balances[a] for a in ids])))
    return np.asarray(out)


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
                    "file": fn,
                    "all": per_agent_series(data, ordinary_only=False),
                    "ordinary": per_agent_series(data, ordinary_only=True),
                }
            )
    return runs


def group_cells(runs: List[Dict], population: str, key: str):
    cells = defaultdict(list)
    for r in runs:
        if r["population"] != population or r[key] is None:
            continue
        cells[(r["model"], r["defection"], r["task_order"])].append(r)
    return cells


def plot_grid(cells, population: str, key: str, out_path: str, summary_rows: list):
    cols = DEFECTION_COLS[population]
    fig, axes = plt.subplots(3, 3, figsize=(15, 10), sharex=True, sharey=True)
    for i, (model_dir, model_label) in enumerate(MODEL_ROWS):
        for j, (defection, col_title) in enumerate(cols):
            ax = axes[i, j]
            for task_order, _label, color in TASK_ORDERS:
                cell = cells.get((model_dir, defection, task_order), [])
                if not cell:
                    continue
                n_rounds = min(len(r[key]) for r in cell)
                mat = np.vstack([r[key][:n_rounds] for r in cell])
                x = np.arange(1, n_rounds + 1)
                mean = mat.mean(axis=0)
                best_idx = int(np.argmax(mat[:, -1]))
                best = mat[best_idx]
                ax.plot(x, mean, color=color, lw=1.2, ls="--", alpha=0.6)
                ax.plot(x, best, color=color, lw=2.4)
                summary_rows.append(
                    {
                        "population": population,
                        "agents": key,
                        "model": model_dir,
                        "defection": defection,
                        "task_order": task_order,
                        "n_runs": len(cell),
                        "mean_final": round(float(mean[-1]), 2),
                        "std_final": round(float(mat[:, -1].std(ddof=1)) if len(cell) > 1 else 0.0, 2),
                        "max_final": round(float(best[-1]), 2),
                        "min_final": round(float(mat[:, -1].min()), 2),
                        "best_rep": cell[best_idx]["rep"],
                        "best_file": cell[best_idx]["file"],
                    }
                )
            ax.set_ylim(0, 80)
            ax.set_xlim(1, 10)
            ax.set_xticks([1, 5, 10])
            ax.grid(alpha=0.3)
            if i == 0:
                ax.set_title(col_title, fontsize=12, fontweight="bold")
            if j == 0:
                ax.set_ylabel(model_label, fontsize=11, fontweight="bold")
            if i == 2:
                ax.set_xlabel("Round")

    handles = [plt.Line2D([], [], color=c, lw=2.4, label=l) for _, l, c in TASK_ORDERS]
    handles += [
        plt.Line2D([], [], color="k", lw=2.4, label="best run (max over five runs)"),
        plt.Line2D([], [], color="k", lw=1.2, ls="--", alpha=0.6, label="mean over five runs"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=5, frameon=False, bbox_to_anchor=(0.5, -0.01))
    agents_txt = "all agents" if key == "all" else "ordinary agents only"
    fig.suptitle(
        f"Resources over time — {POP_TITLES[population]}\n"
        f"Negative-only noise; actual earned resources; {agents_txt}; "
        "solid = best of five runs, dashed = mean",
        fontsize=14,
        fontweight="bold",
    )
    fig.supylabel("Cumulative resources per agent (mean over agents)")
    fig.tight_layout(rect=(0.02, 0.04, 1, 0.95))
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


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

    summary: list = []
    figures = [
        ("dyad", "all", "dyad_all_agents_max.png"),
        ("population", "all", "population_all_agents_max.png"),
        ("population", "ordinary", "population_ordinary_agents_max.png"),
    ]
    for population, key, fname in figures:
        cells = group_cells(runs, population, key)
        out_path = os.path.join(args.out, fname)
        plot_grid(cells, population, key, out_path, summary)
        print(f"wrote {out_path}")

    csv_path = os.path.join(args.out, "summary.csv")
    with open(csv_path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(summary[0].keys()))
        w.writeheader()
        w.writerows(summary)
    print(f"wrote {csv_path}")
    write_output_provenance(args.out, sources, allowed_differences=allowed, legacy_reason=args.legacy_reason)

    # Cells with fewer than 5 runs, so the reader knows where max is on thin data.
    short = [r for r in summary if r["n_runs"] < 5 and r["agents"] == "all"]
    if short:
        print("\nCells with fewer than 5 runs:")
        for r in short:
            print(f"  {r['population']:10s} {r['model']:18s} {r['defection']:12s} {r['task_order']:10s} n={r['n_runs']}")


if __name__ == "__main__":
    main()

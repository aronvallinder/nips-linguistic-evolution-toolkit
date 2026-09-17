"""Recreate the slide-678 seven-cell bar plot from the validated rerun."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import statistics
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from analyses._shared import configure_matplotlib
from src.experiment_condition import read_final_run


RUN_ROOT = ROOT / "data/json/noise_experiments/slide678_rerun_20260916"
RECEIPT = RUN_ROOT / "completion_receipt.json"
OUT_DIR = ROOT / "docs/figures/slide678_rerun_20260916"
CELLS = [
    ("s_end_minus", "S-end−\n(low-coop source)", "#d62728"),
    ("baseline", "Baseline\n(no seed)", "#7f7f7f"),
    ("s_filler", "S-filler\n(Wikipedia)", "#9467bd"),
    ("s_end_plus_gpt", "S-end+ GPT\n(GPT-5-nano round-10)", "#ff7f0e"),
    ("s_start", "S-start\n(Sonnet round-1)", "#1f77b4"),
    ("s_end_plus_gemini", "S-end+ Gemini\n(Flash-Lite round-10)", "#17becf"),
    ("s_end_plus", "S-end+ Sonnet\n(Sonnet round-10)", "#2ca02c"),
]
CEILING = 600.0


def load_verified_values(run_root=RUN_ROOT, receipt_path=RECEIPT) -> tuple[dict[str, list[float]], dict]:
    receipt = json.loads(receipt_path.read_text())
    if receipt.get("completed") != 35 or receipt.get("planned") != 35:
        raise ValueError("Completion receipt does not certify all 35 planned runs")
    entries = receipt.get("finals") or []
    if len(entries) != 35:
        raise ValueError(f"Expected 35 final receipts, found {len(entries)}")

    values = {cell: [] for cell, _, _ in CELLS}
    seen = set()
    for entry in entries:
        path = run_root / entry["path"]
        if path in seen:
            raise ValueError(f"Duplicate final in receipt: {path}")
        seen.add(path)
        if hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
            raise ValueError(f"Final hash changed since completion: {path}")
        data = read_final_run(path)
        history = data["conversation_history"]
        if [row.get("round") for row in history] != list(range(1, 11)):
            raise ValueError(f"Not a complete ten-round final: {path}")
        joint = float(sum(history[-1]["balances"].values()))
        if not np.isclose(joint, entry["joint_resources"]):
            raise ValueError(f"Receipt value mismatch: {path}")
        values[entry["cell"]].append(joint)

    for cell, _, _ in CELLS:
        values[cell].sort()
        recorded = sorted(receipt["cells"][cell]["values"])
        if len(values[cell]) != 5 or not np.allclose(values[cell], recorded):
            raise ValueError(f"Cell {cell} does not contain five receipt-matched finals")
    return values, receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, default=RUN_ROOT)
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--ceiling", type=float, default=CEILING)
    parser.add_argument("--population", default="8-agent rotating population")
    parser.add_argument("--output-stem", default="slide678_cell_means")
    args = parser.parse_args()
    receipt_path = args.run_root / "completion_receipt.json"
    values, receipt = load_verified_values(args.run_root, receipt_path)
    configure_matplotlib()
    fig, ax = plt.subplots(figsize=(15, 7))
    positions = np.arange(len(CELLS))
    rng = np.random.default_rng(seed=6)

    for index, (cell, _label, color) in enumerate(CELLS):
        observations = values[cell]
        mean = statistics.mean(observations)
        sd = statistics.stdev(observations)
        if abs(sd) < 1e-9:
            sd = 0.0
        ax.bar(
            positions[index], mean, width=0.62, yerr=sd, capsize=5,
            color=color, edgecolor="black", linewidth=0.7, alpha=0.88,
        )
        jitter = rng.uniform(-0.1, 0.1, size=len(observations))
        ax.scatter(
            positions[index] + jitter,
            observations,
            s=42,
            color="black",
            edgecolor="white",
            linewidth=0.8,
            zorder=3,
        )
        ax.text(
            positions[index], mean + sd + 12,
            f"${mean:.0f}\n(±${sd:.0f})\nn={len(observations)}",
            ha="center", va="bottom", fontsize=9.5,
        )

    baseline_mean = statistics.mean(values["baseline"])
    ax.axhline(
        args.ceiling, color="red", linestyle="--", alpha=0.55,
        label=f"Cooperation ceiling (${int(args.ceiling)})",
    )
    ax.axhline(
        baseline_mean, color="#7f7f7f", linestyle=":", alpha=0.6,
        linewidth=1.4, label=f"Baseline mean (${baseline_mean:.0f})",
    )
    ax.set_xticks(positions)
    ax.set_xticklabels([label for _, label, _ in CELLS], fontsize=10)
    ax.set_ylabel(f"Joint balance after 10 rounds ({args.population})")
    ax.set_ylim(0, args.ceiling * 7 / 6)
    ax.legend(loc="upper left", fontsize=10)
    ax.grid(axis="y", alpha=0.3)
    means = {cell: statistics.mean(cell_values) for cell, cell_values in values.items()}
    ax.set_title(
        f"Slide 678 ablation rerun — {args.population}\n"
        "Claude Sonnet 4.5 hosts · myth-only chat memory · history block: none · "
        "negative-$5 communication noise · n=5 per cell\n"
        f"Means: late Sonnet \\${means['s_end_plus']:.0f}; Gemini \\${means['s_end_plus_gemini']:.0f}; "
        f"early Sonnet \\${means['s_start']:.0f}; GPT \\${means['s_end_plus_gpt']:.0f}; "
        f"filler \\${means['s_filler']:.0f}; baseline \\${means['baseline']:.0f}.",
        fontsize=11,
    )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    png = args.out_dir / f"{args.output_stem}.png"
    pdf = args.out_dir / f"{args.output_stem}.pdf"
    fig.savefig(png, dpi=180, bbox_inches="tight")
    fig.savefig(pdf, bbox_inches="tight")
    plt.close(fig)

    summary = {
        "completion_receipt_sha256": hashlib.sha256(receipt_path.read_bytes()).hexdigest(),
        "plan_sha256": receipt["plan_sha256"],
        "cells": {
            cell: {
                "n": len(values[cell]),
                "mean": statistics.mean(values[cell]),
                "sd": statistics.stdev(values[cell]),
                "values": values[cell],
            }
            for cell, _, _ in CELLS
        },
        "outputs": [png.name, pdf.name],
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(f"Wrote {png}")
    print(f"Wrote {pdf}")


if __name__ == "__main__":
    main()

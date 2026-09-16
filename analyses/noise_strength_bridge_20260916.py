#!/usr/bin/env python3
"""Compare the range-2 bridge with matched current range-0/range-1 dyads."""

from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import os
from pathlib import Path
import statistics
import sys

import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np
import seaborn as sns


ROOT = Path(__file__).resolve().parents[1]
REFERENCE_ROOT = Path(os.environ.get("NLET_REFERENCE_ROOT", ROOT))
sys.path.insert(0, str(ROOT))

from src.experiment_condition import (  # noqa: E402
    condition_from_run,
    differences,
    output_provenance,
    read_final_run,
)

FIGURE2 = ROOT / "docs" / "figures" / "figure2_noise_comparison_20260916"
BRIDGE = ROOT / "data" / "json" / "noise_experiments" / "noise_strength_bridge_20260916"
DEFAULT_OUT = ROOT / "docs" / "figures" / "noise_strength_bridge_20260916"
MODELS = (
    "anthropic/claude-sonnet-4.5",
    "google/gemini-3.7-flash",
)
LABELS = {
    "anthropic/claude-sonnet-4.5": "Claude Sonnet 4.5",
    "google/gemini-3.7-flash": "Gemini 3.7 Flash",
}
NOISE_LABELS = {0: "No noise", 1: "U(−1, 0)", 2: "U(−2, 0)"}
TASK_LABELS = {"game": "Game only", "myth_game": "Myth → Game"}
TASK_COLORS = {"game": "#999999", "myth_game": "#72b6a1"}
TASK_DOT_COLORS = {"game": "#777777", "myth_game": "#4d9f89"}
BOOTSTRAP_INDICES = np.array(list(itertools.product(range(5), repeat=5)))


def save_figure(figure, path: Path) -> None:
    """Keep vector metadata and element IDs stable for reproducible hashes."""
    metadata = {"Date": None} if path.suffix == ".svg" else (
        {"CreationDate": None, "ModDate": None} if path.suffix == ".pdf" else {}
    )
    with plt.rc_context({"svg.hashsalt": "noise-strength-bridge-20260916"}):
        figure.savefig(path, dpi=220, bbox_inches="tight", metadata=metadata)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_existing() -> tuple[list[dict], dict[str, str]]:
    provenance = json.loads((FIGURE2 / "provenance.json").read_text(encoding="utf-8"))
    hashes = {row["path"]: row["sha256"] for row in provenance["runs"]}
    rows = []
    with (FIGURE2 / "run_values.csv").open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["model"] not in MODELS or int(row["num_agents"]) != 2:
                continue
            if row["task_order"] not in {"game", "myth_game"}:
                continue
            if row["noise"] not in {"no_noise", "noise_informed"}:
                continue
            source = REFERENCE_ROOT / row["source_path"]
            if hashes.get(row["source_path"]) != sha256(source):
                raise RuntimeError(f"Existing Figure 2 source hash changed: {source}")
            rows.append(
                {
                    "model": row["model"],
                    "noise_range": 0 if row["noise"] == "no_noise" else 1,
                    "task_order": row["task_order"],
                    "replicate": int(row["replicate"]),
                    "resources": float(row["resources"]),
                    "pairing_seed": int(row["pairing_seed"]),
                    "noise_seed": int(row["noise_seed"]),
                    "source_path": row["source_path"],
                    "sha256": hashes[row["source_path"]],
                }
            )
    return rows, hashes


def read_bridge() -> list[dict]:
    receipt = json.loads((BRIDGE / "completion_receipt.json").read_text(encoding="utf-8"))
    if receipt["runs"] != 20 or len(receipt["finals"]) != 20:
        raise RuntimeError("Bridge completion receipt is incomplete")
    rows = []
    for record in receipt["finals"]:
        source = ROOT / record["path"]
        if record["sha256"] != sha256(source):
            raise RuntimeError(f"Bridge source hash changed: {source}")
        saved = json.loads(source.read_text(encoding="utf-8"))
        metadata = saved["run_metadata"]
        if metadata["model"] not in MODELS:
            raise RuntimeError(f"Unexpected bridge model: {metadata['model']}")
        if metadata["noise_config"] != {
            "type": "uniform",
            "range": 2.0,
            "direction": "negative",
            "applies_to": "both",
            "inform_agents": True,
        }:
            raise RuntimeError(f"Unexpected bridge noise condition: {source}")
        if metadata["noise_semantics"] != "communication":
            raise RuntimeError(f"Unexpected bridge noise semantics: {source}")
        balances = saved["conversation_history"][-1]["balances"]
        rows.append(
            {
                "model": metadata["model"],
                "noise_range": 2,
                "task_order": "_".join(saved["task_order"]),
                "replicate": int(metadata["replicate_id"]),
                "resources": float(statistics.mean(balances.values())),
                "pairing_seed": int(metadata["pairing_seed"]),
                "noise_seed": int(metadata["noise_seed"]),
                "source_path": record["path"],
                "sha256": record["sha256"],
            }
        )
    return rows


def summarize(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    if len(rows) != 60:
        raise RuntimeError(f"Expected 60 run observations, found {len(rows)}")
    indexed = {
        (row["model"], row["noise_range"], row["replicate"], row["task_order"]): row
        for row in rows
    }
    if len(indexed) != 60:
        raise RuntimeError("Duplicate model/range/replicate/task cells")

    paired_rows = []
    summaries = []
    for model in MODELS:
        for noise_range in (0, 1, 2):
            baseline = []
            myth = []
            for replicate in range(5):
                game_row = indexed[(model, noise_range, replicate, "game")]
                myth_row = indexed[(model, noise_range, replicate, "myth_game")]
                if game_row["pairing_seed"] != myth_row["pairing_seed"]:
                    raise RuntimeError("Pairing seeds differ within a replicate block")
                if game_row["noise_seed"] != myth_row["noise_seed"]:
                    raise RuntimeError("Noise seeds differ within a replicate block")
                baseline.append(game_row["resources"])
                myth.append(myth_row["resources"])
                paired_rows.append(
                    {
                        "model": model,
                        "noise_range": noise_range,
                        "replicate": replicate,
                        "game_resources": game_row["resources"],
                        "myth_resources": myth_row["resources"],
                        "paired_myth_effect": myth_row["resources"] - game_row["resources"],
                        "pairing_seed": game_row["pairing_seed"],
                        "noise_seed": game_row["noise_seed"],
                    }
                )

            baseline_array = np.array(baseline)
            myth_array = np.array(myth)
            paired = myth_array - baseline_array
            boot_difference_of_medians = (
                np.median(myth_array[BOOTSTRAP_INDICES], axis=1)
                - np.median(baseline_array[BOOTSTRAP_INDICES], axis=1)
            )
            boot_paired_mean = np.mean(paired[BOOTSTRAP_INDICES], axis=1)
            summaries.append(
                {
                    "model": model,
                    "noise_range": noise_range,
                    "n": 5,
                    "game_median": float(np.median(baseline_array)),
                    "myth_median": float(np.median(myth_array)),
                    "difference_of_medians": float(
                        np.median(myth_array) - np.median(baseline_array)
                    ),
                    "difference_of_medians_ci_low": float(
                        np.percentile(boot_difference_of_medians, 2.5)
                    ),
                    "difference_of_medians_ci_high": float(
                        np.percentile(boot_difference_of_medians, 97.5)
                    ),
                    "paired_effect_mean": float(np.mean(paired)),
                    "paired_effect_std": float(np.std(paired, ddof=1)),
                    "paired_effect_mean_ci_low": float(
                        np.percentile(boot_paired_mean, 2.5)
                    ),
                    "paired_effect_mean_ci_high": float(
                        np.percentile(boot_paired_mean, 97.5)
                    ),
                    "paired_effect_median": float(np.median(paired)),
                    "positive_pairs": int(np.sum(paired > 0)),
                    "zero_pairs": int(np.sum(paired == 0)),
                    "negative_pairs": int(np.sum(paired < 0)),
                }
            )
    return paired_rows, summaries


def summarize_range_contrasts(paired_rows: list[dict]) -> list[dict]:
    indexed = {
        (row["model"], row["noise_range"], row["replicate"]): row["paired_myth_effect"]
        for row in paired_rows
    }
    contrasts = []
    for model in MODELS:
        for higher, lower in ((1, 0), (2, 1), (2, 0)):
            values = np.array(
                [
                    indexed[(model, higher, replicate)]
                    - indexed[(model, lower, replicate)]
                    for replicate in range(5)
                ]
            )
            boot_mean = np.mean(values[BOOTSTRAP_INDICES], axis=1)
            contrasts.append(
                {
                    "model": model,
                    "contrast": f"range_{higher}_minus_range_{lower}",
                    "n": 5,
                    "paired_contrast_mean": float(np.mean(values)),
                    "paired_contrast_std": float(np.std(values, ddof=1)),
                    "paired_contrast_mean_ci_low": float(np.percentile(boot_mean, 2.5)),
                    "paired_contrast_mean_ci_high": float(np.percentile(boot_mean, 97.5)),
                    "paired_contrast_median": float(np.median(values)),
                }
            )
    return contrasts


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def resolve_source(row: dict) -> Path:
    relative = Path(row["source_path"])
    for root in (ROOT, REFERENCE_ROOT):
        candidate = root / relative
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(f"Cannot resolve source final: {relative}")


def write_provenance(output: Path, rows: list[dict]) -> None:
    source_paths = [resolve_source(row) for row in rows]
    conditions = [condition_from_run(read_final_run(path)) for path in source_paths]
    observed = set()
    for condition in conditions[1:]:
        observed.update(differences(conditions[0], condition))

    previous = json.loads((FIGURE2 / "provenance.json").read_text(encoding="utf-8"))
    allowed = {
        key: reason
        for key, reason in previous["allowed_differences"].items()
        if any(path == key or path.startswith(key + ".") for path in observed)
    }
    allowed.update(
        {
            "protocol.game.noise_config": (
                "Informed negative communication-noise range (none, 1, or 2) "
                "is the bridge design factor."
            ),
            "protocol.simulation.memory_capacity": (
                "The current protocol records its task-order-specific memory capacity; "
                "game-only and myth-first are intentional comparison arms."
            ),
        }
    )

    implementation_variants = {}
    for key in sorted(conditions[0]["implementation"]):
        values = sorted({condition["implementation"].get(key) for condition in conditions})
        if len(values) > 1:
            implementation_variants[key] = values
    expected_variants = {
        key: values
        for key, values in previous.get("implementation_differences", {}).items()
        if key in implementation_variants
    }
    if implementation_variants != expected_variants:
        raise RuntimeError(
            "Recorded implementation differences exceed the reviewed validator/billing fixes"
        )

    outputs = sorted(
        path for path in output.rglob("*")
        if path.is_file() and path != output / "provenance.json"
    )
    document = output_provenance(
        source_paths,
        outputs,
        allowed_differences=allowed,
        output_root=output,
    )
    for run, row in zip(document["runs"], rows):
        if run["sha256"] != row["sha256"]:
            raise RuntimeError(f"Source hash mismatch: {row['source_path']}")
        run["path"] = row["source_path"]
    document.update(
        comparison=(
            "Current dyad protocol; game-only versus myth-first; informed negative "
            "communication noise at ranges 1 and 2, plus the matched no-noise control."
        ),
        bootstrap="Exact paired empirical bootstrap over all 5^5 replicate resamples.",
        implementation_differences=implementation_variants,
        execution_commit={
            "range_2": "25a2d26c02e2b4e46372bacf56b02df3e50a4c79",
            "tree": "86dd809b7ca377763d594ae931e89eba4e8ff540",
            "durable_tag": "noise-strength-bridge-execution-20260916",
            "equivalent_pr_commit": "8b694c5a1e922587e18ee17c268bd2d99a93d461",
        },
        hugging_face={
            "repo_id": "machine-cultural-evolution/nips-linguistic-evolution-runs",
            "private": True,
            "revision": "69964113834debf90da9f5b9ba5025806abbeab9",
            "path": (
                "uploaders/ivarfresh/data/json/noise_experiments/"
                "noise_strength_bridge_20260916"
            ),
            "artifact_count": 80,
            "final_count": 20,
        },
        script_sha256=sha256(Path(__file__)),
    )
    (output / "provenance.json").write_text(
        json.dumps(document, indent=2) + "\n",
        encoding="utf-8",
    )


def plot(paired_rows: list[dict], output: Path) -> None:
    sns.set_theme(style="whitegrid", context="notebook")
    figure, axes = plt.subplots(1, 2, figsize=(10.8, 4.7), sharey=True)
    for axis, model in zip(axes, MODELS):
        selected = [row for row in paired_rows if row["model"] == model]
        for replicate in range(5):
            replicate_rows = sorted(
                (row for row in selected if row["replicate"] == replicate),
                key=lambda row: row["noise_range"],
            )
            axis.plot(
                [row["noise_range"] for row in replicate_rows],
                [row["paired_myth_effect"] for row in replicate_rows],
                color="#b7c1bd",
                marker="o",
                linewidth=1.1,
                markersize=4,
                alpha=0.8,
            )
        medians = [
            statistics.median(
                row["paired_myth_effect"]
                for row in selected
                if row["noise_range"] == noise_range
            )
            for noise_range in (0, 1, 2)
        ]
        axis.plot(
            (0, 1, 2),
            medians,
            color="#2f8f78",
            marker="o",
            linewidth=2.8,
            markersize=8,
            label="Median paired effect",
        )
        axis.axhline(0, color="#555555", linewidth=1)
        axis.set_title(LABELS[model], fontsize=13, fontweight="semibold")
        axis.set_xticks((0, 1, 2), [NOISE_LABELS[value] for value in (0, 1, 2)])
        axis.set_xlabel("Informed negative communication noise")
        axis.spines[["top", "right"]].set_visible(False)
    axes[0].set_ylabel("Myth-first − game-only resources per agent")
    axes[0].legend(frameon=False, loc="upper left")
    figure.suptitle(
        "Myth effect across noise strength",
        fontsize=17,
        fontweight="semibold",
        y=0.97,
    )
    figure.text(
        0.5,
        0.90,
        "Current dyad protocol · 5 matched replicates per condition",
        ha="center",
        color="#666666",
    )
    figure.subplots_adjust(left=0.10, right=0.985, bottom=0.18, top=0.77, wspace=0.25)
    for suffix in ("png", "svg", "pdf"):
        path = output / f"paired_myth_effect.{suffix}"
        save_figure(figure, path)
        if suffix == "svg":
            lines = path.read_text(encoding="utf-8").splitlines()
            path.write_text(
                "\n".join(line.rstrip() for line in lines) + "\n",
                encoding="utf-8",
            )
    plt.close(figure)


def resource_boxplot(rows: list[dict], output: Path) -> None:
    """Show the underlying game-only and myth-first resource distributions."""
    sns.set_theme(style="whitegrid", context="notebook")
    figure, axes = plt.subplots(1, 2, figsize=(10.8, 4.9), sharey=True)
    task_orders = ("game", "myth_game")
    offsets = {"game": -0.18, "myth_game": 0.18}
    for axis, model in zip(axes, MODELS):
        for noise_range in (0, 1, 2):
            for task_order in task_orders:
                values = np.array(
                    [
                        row["resources"]
                        for row in rows
                        if row["model"] == model
                        and row["noise_range"] == noise_range
                        and row["task_order"] == task_order
                    ]
                )
                if len(values) != 5:
                    raise RuntimeError(
                        f"Expected five {model}/{noise_range}/{task_order} observations"
                    )
                position = noise_range + offsets[task_order]
                axis.boxplot(
                    values,
                    positions=[position],
                    widths=0.28,
                    patch_artist=True,
                    showfliers=False,
                    whis=1.5,
                    boxprops={
                        "facecolor": TASK_COLORS[task_order],
                        "edgecolor": "#666666",
                    },
                    medianprops={"color": "#222222", "linewidth": 1.6},
                    whiskerprops={"color": "#666666"},
                    capprops={"color": "#666666"},
                )
                axis.scatter(
                    position + np.linspace(-0.055, 0.055, 5),
                    values,
                    s=30,
                    color=TASK_DOT_COLORS[task_order],
                    edgecolors="white",
                    linewidths=0.6,
                    zorder=3,
                )
        axis.set_title(LABELS[model], fontsize=13, fontweight="semibold")
        axis.set_xticks((0, 1, 2), [NOISE_LABELS[value] for value in (0, 1, 2)])
        axis.set_xlabel("Informed negative communication noise")
        axis.set_xlim(-0.55, 2.55)
        axis.set_ylim(0, 80)
        axis.spines[["top", "right"]].set_visible(False)
    axes[0].set_ylabel("Cumulative resources per agent")
    axes[0].legend(
        handles=[
            Patch(
                facecolor=TASK_COLORS[task_order],
                edgecolor="#666666",
                label=TASK_LABELS[task_order],
            )
            for task_order in task_orders
        ],
        frameon=False,
        loc="lower left",
    )
    figure.suptitle(
        "Final resources across noise strength",
        fontsize=17,
        fontweight="semibold",
        y=0.98,
    )
    figure.text(
        0.5,
        0.91,
        "Current dyad protocol · 5 runs per box · Round 10",
        ha="center",
        color="#666666",
    )
    figure.text(
        0.5,
        0.025,
        "Box = middle 50% · Line = median · Each dot = one run",
        ha="center",
        fontsize=9,
        color="#555555",
    )
    figure.subplots_adjust(left=0.10, right=0.985, bottom=0.20, top=0.78, wspace=0.25)
    for suffix in ("png", "svg", "pdf"):
        path = output / f"resource_boxplots.{suffix}"
        save_figure(figure, path)
        if suffix == "svg":
            lines = path.read_text(encoding="utf-8").splitlines()
            path.write_text(
                "\n".join(line.rstrip() for line in lines) + "\n",
                encoding="utf-8",
            )
    plt.close(figure)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    existing, _ = read_existing()
    bridge = read_bridge()
    rows = existing + bridge
    paired_rows, summaries = summarize(rows)
    range_contrasts = summarize_range_contrasts(paired_rows)
    write_csv(args.out / "run_values.csv", sorted(
        rows,
        key=lambda row: (
            MODELS.index(row["model"]),
            row["noise_range"],
            row["replicate"],
            row["task_order"],
        ),
    ))
    write_csv(args.out / "paired_effects.csv", paired_rows)
    write_csv(args.out / "effect_summary.csv", summaries)
    write_csv(args.out / "range_contrasts.csv", range_contrasts)
    plot(paired_rows, args.out)
    resource_boxplot(rows, args.out)

    receipt = json.loads((BRIDGE / "completion_receipt.json").read_text(encoding="utf-8"))
    (args.out / "completion_receipt.json").write_text(
        json.dumps(receipt, indent=2) + "\n",
        encoding="utf-8",
    )
    write_provenance(args.out, rows)
    print(f"Verified {len(rows)} finals; wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

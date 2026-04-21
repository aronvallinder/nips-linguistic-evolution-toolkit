#!/usr/bin/env python3
"""
Statistical comparison of cumulative balance distributions across noise conditions
and task orders in the trust game experiments.

Compares:
- 18 same-axis pairwise comparisons (Mann-Whitney U with Bonferroni correction)
- 6 delta comparisons (does noise modulate the myth effect?)

Delta convention:
    delta = cumulative_balance_myth - cumulative_balance_game_only
    Positive delta => the myth condition outperforms game-only (myth helps
    cooperation). Aggregation across runs/seeds uses the median (robust to
    outliers under noisy conditions); IQR of the underlying cells is written
    to the per-model deltas.csv as a dispersion reference.

Usage:
    python analyses_clean/noise_balance_comparison.py
    python analyses_clean/noise_balance_comparison.py --output-dir data/plots/custom_dir
    python analyses_clean/noise_balance_comparison.py --target-round 10 --alpha 0.05
"""

import argparse
import json
import sys
from itertools import combinations
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import mannwhitneyu

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_DIR = Path(__file__).parent.parent

NOISE_CONDITIONS = ["no_noise", "noise", "noise_informed"]
TASK_ORDERS = ["game", "game_myth", "myth_game"]

NOISE_LABELS = {
    "no_noise": "No Noise",
    "noise": "Noise",
    "noise_informed": "Noise (Informed)",
}

TASK_ORDER_LABELS = {
    "game": "Game Only",
    "game_myth": "Game → Myth",
    "myth_game": "Myth → Game",
}

def build_model_data_paths(baseline_dirs, noise_dir):
    """
    Build MODEL_DATA_PATHS dynamically from CLI arguments.

    Args:
        baseline_dirs: dict of {model_name: baseline_data_path} for no-noise baselines
        noise_dir: path to the noise experiment directory (e.g. data/json/noise_experiments/v2)
                   Expected structure: {noise_dir}/{experiment}/{model}/{task_order}/{noise_condition}/

    Returns:
        dict: model -> noise_condition -> task_order -> (path, recursive)
    """
    noise_path = Path(noise_dir)
    model_paths = {}

    for model_name, baseline_path in baseline_dirs.items():
        model_paths[model_name] = {
            "no_noise": {
                "game": (str(Path(baseline_path) / "game"), True),
                "game_myth": (str(Path(baseline_path) / "game_myth"), True),
                "myth_game": (str(Path(baseline_path) / "myth_game"), True),
            },
        }

        # Auto-discover noise conditions from directory structure
        # Walk {noise_dir}/*/model_name/{task_order}/{condition}/
        for experiment_dir in sorted(noise_path.iterdir()):
            if not experiment_dir.is_dir():
                continue
            # Find model dir (match by substring since names may differ slightly)
            model_dir = None
            for candidate in experiment_dir.iterdir():
                if not candidate.is_dir():
                    continue
                if model_name in candidate.name or candidate.name in model_name:
                    model_dir = candidate
                    break
            if model_dir is None:
                continue

            for task_dir in sorted(model_dir.iterdir()):
                if not task_dir.is_dir():
                    continue
                task_order = task_dir.name  # game, game_myth, myth_game

                for cond_dir in sorted(task_dir.iterdir()):
                    if not cond_dir.is_dir():
                        continue
                    cond_name = cond_dir.name

                    # Map to noise/noise_informed based on whether name ends with _informed
                    if cond_name.endswith("_informed"):
                        noise_key = "noise_informed"
                    else:
                        noise_key = "noise"

                    if noise_key not in model_paths[model_name]:
                        model_paths[model_name][noise_key] = {}
                    model_paths[model_name][noise_key][task_order] = (str(cond_dir), False)

    return model_paths


# Default paths (can be overridden via CLI)
MODEL_DATA_PATHS = {}


# ============================================================================
# DATA LOADING
# ============================================================================

def load_balance_at_round(json_path, target_round=10):
    """Load a single JSON file and return mean agent balance at target_round."""
    with open(json_path) as f:
        data = json.load(f)

    game_rounds = [
        r for r in data.get("conversation_history", [])
        if r.get("sent") is not None
    ]

    if len(game_rounds) < target_round:
        return None

    balances = game_rounds[target_round - 1]["balances"]
    return (balances["Agent_1"] + balances["Agent_2"]) / 2


def collect_cell(base_path, recursive=False, target_round=10):
    """Collect all balance values from JSON files in a directory."""
    base = Path(base_path)
    if not base.exists():
        print(f"  WARNING: Path does not exist: {base}")
        return np.array([])

    if recursive:
        json_files = list(base.rglob("*.json"))
    else:
        json_files = list(base.glob("*.json"))

    # Filter out checkpoint and results files
    json_files = [
        f for f in json_files
        if ".checkpoint" not in f.name and ".results" not in f.name
    ]

    values = []
    for f in json_files:
        val = load_balance_at_round(f, target_round)
        if val is not None:
            values.append(val)

    return np.array(values)


def build_dataframe(target_round=10):
    """Build master DataFrame with all balance data."""
    rows = []

    for model, conditions in MODEL_DATA_PATHS.items():
        for noise_cond, task_orders in conditions.items():
            for task_order, (path, recursive) in task_orders.items():
                full_path = BASE_DIR / path
                values = collect_cell(full_path, recursive, target_round)
                print(f"  {model} / {noise_cond} / {task_order}: n={len(values)}")

                for val in values:
                    rows.append({
                        "model": model,
                        "noise_condition": noise_cond,
                        "task_order": task_order,
                        "mean_balance_r10": val,
                    })

    return pd.DataFrame(rows)


# ============================================================================
# STATISTICAL TESTS
# ============================================================================

def run_pairwise_comparisons(df, model, alpha=0.05):
    """Run 18 same-axis pairwise Mann-Whitney U comparisons for a model."""
    model_df = df[df["model"] == model]
    results = []

    # Within noise condition: compare task orders (9 comparisons)
    for noise_cond in NOISE_CONDITIONS:
        subset = model_df[model_df["noise_condition"] == noise_cond]
        for to_a, to_b in combinations(TASK_ORDERS, 2):
            vals_a = subset[subset["task_order"] == to_a]["mean_balance_r10"].values
            vals_b = subset[subset["task_order"] == to_b]["mean_balance_r10"].values
            result = _mann_whitney(
                vals_a, vals_b,
                f"{noise_cond}/{to_a}", f"{noise_cond}/{to_b}",
            )
            if result:
                results.append(result)

    # Within task order: compare noise conditions (9 comparisons)
    for task_order in TASK_ORDERS:
        subset = model_df[model_df["task_order"] == task_order]
        for nc_a, nc_b in combinations(NOISE_CONDITIONS, 2):
            vals_a = subset[subset["noise_condition"] == nc_a]["mean_balance_r10"].values
            vals_b = subset[subset["noise_condition"] == nc_b]["mean_balance_r10"].values
            result = _mann_whitney(
                vals_a, vals_b,
                f"{nc_a}/{task_order}", f"{nc_b}/{task_order}",
            )
            if result:
                results.append(result)

    # Bonferroni correction
    n_tests = len(results)
    for r in results:
        r["p_corrected"] = min(r["p_value"] * n_tests, 1.0)
        r["significant"] = r["p_corrected"] < alpha

    return results


def _mann_whitney(vals_a, vals_b, label_a, label_b):
    """Run Mann-Whitney U test between two groups."""
    if len(vals_a) < 2 or len(vals_b) < 2:
        return None

    U, p = mannwhitneyu(vals_a, vals_b, alternative="two-sided")
    n1, n2 = len(vals_a), len(vals_b)
    # Rank-biserial correlation effect size
    r = 1 - (2 * U) / (n1 * n2)

    return {
        "group_a": label_a,
        "group_b": label_b,
        "n_a": n1,
        "n_b": n2,
        "mean_a": float(np.mean(vals_a)),
        "mean_b": float(np.mean(vals_b)),
        "median_a": float(np.median(vals_a)),
        "median_b": float(np.median(vals_b)),
        "std_a": float(np.std(vals_a)),
        "std_b": float(np.std(vals_b)),
        "U_statistic": float(U),
        "p_value": float(p),
        "effect_size_r": float(r),
    }


def compute_deltas(df, model):
    """Compute delta comparisons: does noise modulate the myth effect?

    Delta convention:
        delta = median(cumulative_balance_myth) - median(cumulative_balance_game_only)
        Positive delta => the myth condition outperforms game-only.

    IQR of each underlying cell is included for CSV export as a dispersion
    reference (not printed or plotted).
    """
    model_df = df[df["model"] == model]
    deltas = []

    def _iqr(vals):
        vals = np.asarray(vals, dtype=float)
        if vals.size == 0:
            return float("nan")
        return float(np.percentile(vals, 75) - np.percentile(vals, 25))

    for myth_to in ["game_myth", "myth_game"]:
        for nc_a, nc_b in combinations(NOISE_CONDITIONS, 2):
            vals_game_a = model_df[
                (model_df["noise_condition"] == nc_a) & (model_df["task_order"] == "game")
            ]["mean_balance_r10"].values

            vals_myth_a = model_df[
                (model_df["noise_condition"] == nc_a) & (model_df["task_order"] == myth_to)
            ]["mean_balance_r10"].values

            vals_game_b = model_df[
                (model_df["noise_condition"] == nc_b) & (model_df["task_order"] == "game")
            ]["mean_balance_r10"].values

            vals_myth_b = model_df[
                (model_df["noise_condition"] == nc_b) & (model_df["task_order"] == myth_to)
            ]["mean_balance_r10"].values

            median_game_a = float(np.median(vals_game_a)) if len(vals_game_a) else float("nan")
            median_myth_a = float(np.median(vals_myth_a)) if len(vals_myth_a) else float("nan")
            median_game_b = float(np.median(vals_game_b)) if len(vals_game_b) else float("nan")
            median_myth_b = float(np.median(vals_myth_b)) if len(vals_myth_b) else float("nan")

            delta_a = median_myth_a - median_game_a
            delta_b = median_myth_b - median_game_b

            deltas.append({
                "myth_task_order": myth_to,
                "condition_a": nc_a,
                "condition_b": nc_b,
                "median_game_a": median_game_a,
                "median_myth_a": median_myth_a,
                "iqr_game_a": _iqr(vals_game_a),
                "iqr_myth_a": _iqr(vals_myth_a),
                "delta_a": float(delta_a),
                "median_game_b": median_game_b,
                "median_myth_b": median_myth_b,
                "iqr_game_b": _iqr(vals_game_b),
                "iqr_myth_b": _iqr(vals_myth_b),
                "delta_b": float(delta_b),
                "delta_diff": float(delta_a - delta_b),
            })

    return deltas


def compute_cell_summary(df, model):
    """Compute descriptive stats per cell for a model."""
    model_df = df[df["model"] == model]
    rows = []

    for noise_cond in NOISE_CONDITIONS:
        for task_order in TASK_ORDERS:
            vals = model_df[
                (model_df["noise_condition"] == noise_cond)
                & (model_df["task_order"] == task_order)
            ]["mean_balance_r10"].values

            if len(vals) == 0:
                continue

            rows.append({
                "noise_condition": noise_cond,
                "task_order": task_order,
                "n": len(vals),
                "mean": float(np.mean(vals)),
                "median": float(np.median(vals)),
                "std": float(np.std(vals)),
                "min": float(np.min(vals)),
                "max": float(np.max(vals)),
            })

    return rows


# ============================================================================
# CONSOLE OUTPUT
# ============================================================================

def print_results(model, cell_summary, pairwise, deltas):
    """Print structured results to console."""
    print(f"\n{'=' * 80}")
    print(f"  {model}")
    print(f"{'=' * 80}")

    # Cell summary
    print(f"\n--- Cell Summary ---")
    print(f"{'Condition':<25} {'Task Order':<15} {'n':>4} {'Mean':>8} {'Median':>8} {'Std':>8}")
    print("-" * 72)
    for row in cell_summary:
        nc = NOISE_LABELS.get(row["noise_condition"], row["noise_condition"])
        to = TASK_ORDER_LABELS.get(row["task_order"], row["task_order"])
        print(f"{nc:<25} {to:<15} {row['n']:>4} {row['mean']:>8.1f} {row['median']:>8.1f} {row['std']:>8.1f}")

    # Pairwise comparisons
    print(f"\n--- Pairwise Comparisons (Mann-Whitney U, Bonferroni x{len(pairwise)}) ---")
    print(f"{'Group A':<30} {'Group B':<30} {'U':>8} {'p':>10} {'p_corr':>10} {'r':>7} {'Sig':>4}")
    print("-" * 103)
    for r in pairwise:
        sig = "***" if r["p_corrected"] < 0.001 else "**" if r["p_corrected"] < 0.01 else "*" if r["p_corrected"] < 0.05 else ""
        print(
            f"{r['group_a']:<30} {r['group_b']:<30} "
            f"{r['U_statistic']:>8.1f} {r['p_value']:>10.4f} {r['p_corrected']:>10.4f} "
            f"{r['effect_size_r']:>7.3f} {sig:>4}"
        )

    # Deltas
    print(f"\n--- Delta Analysis: Does noise modulate the myth effect? ---")
    print(f"    delta = median(myth) - median(game_only); positive => myth helps")
    print(f"{'Myth Order':<12} {'Cond A':<18} {'Cond B':<18} {'Delta A':>9} {'Delta B':>9} {'Diff':>9}")
    print("-" * 78)
    for d in deltas:
        nc_a = NOISE_LABELS.get(d["condition_a"], d["condition_a"])
        nc_b = NOISE_LABELS.get(d["condition_b"], d["condition_b"])
        to = TASK_ORDER_LABELS.get(d["myth_task_order"], d["myth_task_order"])
        print(
            f"{to:<12} {nc_a:<18} {nc_b:<18} "
            f"{d['delta_a']:>9.2f} {d['delta_b']:>9.2f} {d['delta_diff']:>9.2f}"
        )


# ============================================================================
# CSV EXPORT
# ============================================================================

def export_csv(model, cell_summary, pairwise, deltas, output_dir):
    """Export results to CSV files."""
    model_dir = output_dir / model
    model_dir.mkdir(parents=True, exist_ok=True)

    pd.DataFrame(cell_summary).to_csv(model_dir / "cell_summary.csv", index=False)
    pd.DataFrame(pairwise).to_csv(model_dir / "pairwise.csv", index=False)
    pd.DataFrame(deltas).to_csv(model_dir / "deltas.csv", index=False)

    print(f"\nCSV saved to {model_dir}/")


def export_summary_tables(df, all_pairwise, all_deltas, output_dir):
    """Export three combined summary CSVs across all models."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # --- Table 1: Task order effects ---
    # One row per (model, noise_condition), columns show means per task order + p-values
    rows = []
    for model in MODEL_DATA_PATHS:
        pw = all_pairwise[model]
        for nc in NOISE_CONDITIONS:
            row = {"model": model, "noise_condition": NOISE_LABELS[nc]}
            for to in TASK_ORDERS:
                vals = df[
                    (df["model"] == model)
                    & (df["noise_condition"] == nc)
                    & (df["task_order"] == to)
                ]["mean_balance_r10"]
                row[f"{to}_mean"] = round(float(vals.mean()), 1) if len(vals) > 0 else None
                row[f"{to}_std"] = round(float(vals.std()), 1) if len(vals) > 0 else None
                row[f"{to}_n"] = len(vals)

            # Find p-values for within-noise task order comparisons
            for r in pw:
                ga, gb = r["group_a"], r["group_b"]
                if not ga.startswith(nc + "/") or not gb.startswith(nc + "/"):
                    continue
                to_a = ga.split("/", 1)[1]
                to_b = gb.split("/", 1)[1]
                key = f"p_{to_a}_vs_{to_b}"
                row[key] = round(r["p_corrected"], 4)

            rows.append(row)

    pd.DataFrame(rows).to_csv(output_dir / "task_order_effects.csv", index=False)
    print(f"Summary table: {output_dir / 'task_order_effects.csv'}")

    # --- Table 2: Noise effects ---
    # One row per (model, task_order), columns show means per noise condition + p-values
    rows = []
    for model in MODEL_DATA_PATHS:
        pw = all_pairwise[model]
        for to in TASK_ORDERS:
            row = {"model": model, "task_order": TASK_ORDER_LABELS[to]}
            for nc in NOISE_CONDITIONS:
                vals = df[
                    (df["model"] == model)
                    & (df["noise_condition"] == nc)
                    & (df["task_order"] == to)
                ]["mean_balance_r10"]
                row[f"{nc}_mean"] = round(float(vals.mean()), 1) if len(vals) > 0 else None
                row[f"{nc}_std"] = round(float(vals.std()), 1) if len(vals) > 0 else None
                row[f"{nc}_n"] = len(vals)

            # Find p-values for within-task-order noise comparisons
            for r in pw:
                ga, gb = r["group_a"], r["group_b"]
                if not ga.endswith("/" + to) or not gb.endswith("/" + to):
                    continue
                nc_a = ga.split("/", 1)[0]
                nc_b = gb.split("/", 1)[0]
                key = f"p_{nc_a}_vs_{nc_b}"
                row[key] = round(r["p_corrected"], 4)

            rows.append(row)

    pd.DataFrame(rows).to_csv(output_dir / "noise_effects.csv", index=False)
    print(f"Summary table: {output_dir / 'noise_effects.csv'}")

    # --- Table 3: Deltas summary ---
    # One row per (model, myth_condition), columns show delta per noise condition
    rows = []
    for model in MODEL_DATA_PATHS:
        for myth_to in ["game_myth", "myth_game"]:
            row = {"model": model, "myth_condition": TASK_ORDER_LABELS[myth_to]}

            # Collect deltas from all_deltas for this model
            for d in all_deltas[model]:
                if d["myth_task_order"] != myth_to:
                    continue
                # Each record has condition_a/condition_b and their deltas
                row[f"delta_{NOISE_LABELS[d['condition_a']]}"] = round(d["delta_a"], 2)
                row[f"delta_{NOISE_LABELS[d['condition_b']]}"] = round(d["delta_b"], 2)

            rows.append(row)

    pd.DataFrame(rows).to_csv(output_dir / "deltas_summary.csv", index=False)
    print(f"Summary table: {output_dir / 'deltas_summary.csv'}")


# ============================================================================
# VISUALIZATION
# ============================================================================

def plot_grouped_boxplot(df, model, pairwise, alpha, output_dir, ylim=None):
    """Create grouped boxplot with significance brackets."""
    model_df = df[df["model"] == model].copy()

    if model_df.empty:
        print(f"  No data for {model}, skipping plot")
        return

    # Map labels for display
    model_df["Task Order"] = model_df["task_order"].map(TASK_ORDER_LABELS)
    model_df["Noise Condition"] = model_df["noise_condition"].map(NOISE_LABELS)

    sns.set_style("whitegrid")
    fig, ax = plt.subplots(figsize=(10, 7))

    hue_order = [NOISE_LABELS[nc] for nc in NOISE_CONDITIONS]
    order = [TASK_ORDER_LABELS[to] for to in TASK_ORDERS]

    palette = {
        "No Noise": "#4C72B0",
        "Noise": "#DD8452",
        "Noise (Informed)": "#55A868",
    }

    sns.boxplot(
        data=model_df,
        x="Task Order",
        y="mean_balance_r10",
        hue="Noise Condition",
        order=order,
        hue_order=hue_order,
        palette=palette,
        ax=ax,
        width=0.7,
    )

    # Overlay individual points
    sns.stripplot(
        data=model_df,
        x="Task Order",
        y="mean_balance_r10",
        hue="Noise Condition",
        order=order,
        hue_order=hue_order,
        palette=palette,
        ax=ax,
        dodge=True,
        size=4,
        alpha=0.5,
        legend=False,
    )

    ax.set_title(f"Cumulative Balance at Round 10: {model}", fontweight="bold", fontsize=14)
    ax.set_ylabel("Mean Cumulative Balance (avg of both agents)", fontsize=12)
    ax.set_xlabel("Task Order", fontsize=12)
    ax.legend(title="Noise Condition", fontsize=10)

    if ylim:
        ax.set_ylim(ylim)

    # Add significance brackets for within-task-order comparisons (noise effects)
    _add_significance_brackets(ax, model_df, pairwise, order, hue_order, alpha)

    plt.tight_layout()
    model_dir = output_dir / model
    model_dir.mkdir(parents=True, exist_ok=True)
    fig_path = model_dir / "balance_comparison.png"
    plt.savefig(fig_path, dpi=300, bbox_inches="tight")
    print(f"Plot saved to {fig_path}")
    plt.close()


def _add_significance_brackets(ax, model_df, pairwise, order, hue_order, alpha):
    """Add significance brackets for within-task-order noise comparisons."""
    significant = [r for r in pairwise if r["significant"]]
    if not significant:
        return

    y_max = model_df["mean_balance_r10"].max()
    y_range = model_df["mean_balance_r10"].max() - model_df["mean_balance_r10"].min()
    bracket_height = y_range * 0.03
    y_offset = y_range * 0.05

    bracket_idx = 0
    for r in significant:
        ga, gb = r["group_a"], r["group_b"]

        # Parse group labels: "noise_condition/task_order"
        nc_a, to_a = ga.split("/", 1)
        nc_b, to_b = gb.split("/", 1)

        # Only draw brackets for within-task-order comparisons (same x position)
        if to_a != to_b:
            continue

        to_label = TASK_ORDER_LABELS.get(to_a, to_a)
        nc_a_label = NOISE_LABELS.get(nc_a, nc_a)
        nc_b_label = NOISE_LABELS.get(nc_b, nc_b)

        if to_label not in order:
            continue

        x_base = order.index(to_label)
        n_hues = len(hue_order)
        width = 0.7
        box_width = width / n_hues

        try:
            idx_a = hue_order.index(nc_a_label)
            idx_b = hue_order.index(nc_b_label)
        except ValueError:
            continue

        x_a = x_base - width / 2 + box_width * (idx_a + 0.5)
        x_b = x_base - width / 2 + box_width * (idx_b + 0.5)

        y = y_max + y_offset + bracket_idx * (bracket_height + y_range * 0.04)

        # Draw bracket
        ax.plot([x_a, x_a, x_b, x_b], [y, y + bracket_height, y + bracket_height, y],
                color="black", linewidth=1)

        # Star annotation
        p = r["p_corrected"]
        stars = "***" if p < 0.001 else "**" if p < 0.01 else "*"
        ax.text((x_a + x_b) / 2, y + bracket_height, stars,
                ha="center", va="bottom", fontsize=10, fontweight="bold")

        bracket_idx += 1

    # Adjust y-axis to fit brackets
    if bracket_idx > 0:
        new_top = y_max + y_offset + bracket_idx * (bracket_height + y_range * 0.04) + y_range * 0.05
        ax.set_ylim(top=new_top)


def plot_deltas(deltas, model, output_dir, ylim=None):
    """Create grouped bar chart showing myth effect deltas across noise conditions."""
    if not deltas:
        return

    sns.set_style("whitegrid")
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)

    palette = {
        "No Noise": "#4C72B0",
        "Noise": "#DD8452",
        "Noise (Informed)": "#55A868",
    }

    for ax, myth_to in zip(axes, ["game_myth", "myth_game"]):
        # Collect deltas for this myth task order
        # We need: for each noise condition, delta = mean(game) - mean(myth_variant)
        # Extract from the pairwise delta records
        noise_conds = {}
        for d in deltas:
            if d["myth_task_order"] != myth_to:
                continue
            # Each delta record has condition_a and condition_b
            # Store both deltas
            nc_a = d["condition_a"]
            nc_b = d["condition_b"]
            noise_conds[nc_a] = d["delta_a"]
            noise_conds[nc_b] = d["delta_b"]

        if not noise_conds:
            continue

        # Build bar data in order
        labels = []
        values = []
        colors = []
        for nc in NOISE_CONDITIONS:
            if nc in noise_conds:
                labels.append(NOISE_LABELS[nc])
                values.append(noise_conds[nc])
                colors.append(palette[NOISE_LABELS[nc]])

        x = np.arange(len(labels))
        bars = ax.bar(x, values, color=colors, edgecolor="black", linewidth=0.5, width=0.6)

        # Add value labels on bars
        for bar, val in zip(bars, values):
            y_pos = bar.get_height()
            va = "bottom" if y_pos >= 0 else "top"
            offset = 0.3 if y_pos >= 0 else -0.3
            ax.text(bar.get_x() + bar.get_width() / 2, y_pos + offset,
                    f"{val:.1f}", ha="center", va=va, fontsize=10, fontweight="bold")

        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=10)
        ax.axhline(y=0, color="black", linewidth=0.8)
        ax.set_ylabel("Delta: median(Myth) − median(Game Only)", fontsize=11)
        to_label = TASK_ORDER_LABELS[myth_to]
        ax.set_title(f"Myth Effect: Game Only vs {to_label}", fontweight="bold", fontsize=12)
        ax.grid(axis="y", alpha=0.3)
        if ylim:
            ax.set_ylim(ylim)

    fig.suptitle(
        f"Myth Effect Deltas: {model}  (positive = myth helps)",
        fontweight="bold", fontsize=14, y=1.02,
    )
    plt.tight_layout()

    model_dir = output_dir / model
    model_dir.mkdir(parents=True, exist_ok=True)
    fig_path = model_dir / "delta_comparison.png"
    plt.savefig(fig_path, dpi=300, bbox_inches="tight")
    print(f"Delta plot saved to {fig_path}")
    plt.close()


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Statistical comparison of cumulative balances across noise conditions and task orders.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Auto-discover from noise experiment dir + baseline dirs
    python analyses_clean/noise_balance_comparison.py \\
        --noise-dir data/json/noise_experiments/v2 \\
        --baseline gpt-5-nano=data/json/10_runs_gpt5_myth_topics \\
        --baseline claude-sonnet-4.5=data/json/10runs_model_comparison/claude-sonnet-4.5 \\
        --baseline gemini-3.1-pro-preview=data/json/10runs_model_comparison/gemini-3-pro-preview

    python analyses_clean/noise_balance_comparison.py --output-dir data/plots/custom
    python analyses_clean/noise_balance_comparison.py --target-round 10 --alpha 0.05
        """,
    )
    parser.add_argument("--noise-dir", required=True,
                        help="Path to noise experiment directory (e.g. data/json/noise_experiments/v2)")
    parser.add_argument("--baseline", action="append", required=True,
                        help="Baseline (no-noise) data: model_name=path (repeatable). "
                             "Path should contain game/, game_myth/, myth_game/ subdirs.")
    parser.add_argument("--output-dir", default=None, help="Output directory (default: data/plots/noise_balance_comparison)")
    parser.add_argument("--alpha", type=float, default=0.05, help="Significance threshold (default: 0.05)")
    parser.add_argument("--target-round", type=int, default=10, help="Round to extract balance at (default: 10)")

    args = parser.parse_args()

    # Parse baseline args into dict
    baseline_dirs = {}
    for b in args.baseline:
        if "=" not in b:
            parser.error(f"--baseline must be model_name=path, got: {b}")
        name, path = b.split("=", 1)
        baseline_dirs[name] = path

    # Build model data paths dynamically
    global MODEL_DATA_PATHS
    MODEL_DATA_PATHS = build_model_data_paths(baseline_dirs, args.noise_dir)

    output_dir = Path(args.output_dir) if args.output_dir else BASE_DIR / "data" / "plots" / "noise_experiments" / "noise_balance_comparison"

    print(f"Target round: {args.target_round}")
    print(f"Alpha: {args.alpha}")
    print(f"Output: {output_dir}")
    print()

    # Load all data
    print("Loading data...")
    df = build_dataframe(target_round=args.target_round)
    print(f"\nTotal observations: {len(df)}")

    # Compute shared y-axis limits across all models
    balance_min = df["mean_balance_r10"].min()
    balance_max = df["mean_balance_r10"].max()
    balance_pad = (balance_max - balance_min) * 0.15
    balance_ylim = (balance_min - balance_pad, balance_max + balance_pad)

    # Run analysis per model, collect deltas for shared delta y-axis
    all_pairwise = {}
    all_deltas = {}
    for model in MODEL_DATA_PATHS:
        cell_summary = compute_cell_summary(df, model)
        pairwise = run_pairwise_comparisons(df, model, alpha=args.alpha)
        deltas = compute_deltas(df, model)
        all_pairwise[model] = pairwise
        all_deltas[model] = deltas

    # Compute shared delta y-axis
    all_delta_vals = []
    for model_deltas in all_deltas.values():
        for d in model_deltas:
            all_delta_vals.extend([d["delta_a"], d["delta_b"]])
    if all_delta_vals:
        delta_abs_max = max(abs(v) for v in all_delta_vals) * 1.3
        delta_ylim = (-delta_abs_max, delta_abs_max)
    else:
        delta_ylim = None

    # Output per model
    for model in MODEL_DATA_PATHS:
        cell_summary = compute_cell_summary(df, model)
        print_results(model, cell_summary, all_pairwise[model], all_deltas[model])
        export_csv(model, cell_summary, all_pairwise[model], all_deltas[model], output_dir)
        plot_grouped_boxplot(df, model, all_pairwise[model], args.alpha, output_dir, ylim=balance_ylim)
        plot_deltas(all_deltas[model], model, output_dir, ylim=delta_ylim)

    # Combined summary tables
    print(f"\n{'=' * 80}")
    print("  Summary Tables (all models)")
    print(f"{'=' * 80}")
    export_summary_tables(df, all_pairwise, all_deltas, output_dir)

    print(f"\nDone. All results in {output_dir}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Aggregate analysis comparing cooperation across experimental conditions.
Modified to accept custom input directory as command-line argument.
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple
import pandas as pd
import sys

# Conditions mapping
CONDITION_ORDER = ["game", "myth", "game_myth", "myth_game"]
CONDITION_LABELS = {
    "game": "Game Only",
    "myth": "Myth Only",
    "game_myth": "Game → Myth",
    "myth_game": "Myth → Game"
}


def extract_game_metrics(data: Dict) -> Dict:
    """Extract cooperation metrics from a simulation JSON file."""
    history = data.get('conversation_history', [])

    # Filter to rounds with valid game data
    game_rounds = [
        r for r in history
        if r.get('sent') is not None and r.get('returned') is not None
    ]

    if not game_rounds:
        return None

    # Extract arrays
    sent = np.array([r['sent'] for r in game_rounds])
    received = np.array([r['received'] for r in game_rounds])
    returned = np.array([r['returned'] for r in game_rounds])
    investor_payoff = np.array([r['investor_payoff'] for r in game_rounds])
    trustee_payoff = np.array([r['trustee_payoff'] for r in game_rounds])

    # Extract balance trajectories
    agent_1_balances = []
    agent_2_balances = []
    for r in game_rounds:
        balances = r.get('balances', {})
        agent_1_balances.append(balances.get('Agent_1', 0))
        agent_2_balances.append(balances.get('Agent_2', 0))

    # Calculate metrics
    endowment = sent[0] + investor_payoff[0] if len(sent) > 0 else 10
    trust_ratios = sent / endowment if endowment > 0 else sent * 0
    return_ratios = np.where(received > 0, returned / received, 0)

    metrics = {
        'num_rounds': len(game_rounds),
        'mean_sent': float(np.mean(sent)),
        'std_sent': float(np.std(sent)),
        'mean_returned': float(np.mean(returned)),
        'std_returned': float(np.std(returned)),
        'mean_trust_ratio': float(np.mean(trust_ratios)),
        'std_trust_ratio': float(np.std(trust_ratios)),
        'mean_return_ratio': float(np.mean(return_ratios)),
        'std_return_ratio': float(np.std(return_ratios)),
        'mean_investor_payoff': float(np.mean(investor_payoff)),
        'mean_trustee_payoff': float(np.mean(trustee_payoff)),
        'final_investor_payoff': float(investor_payoff[-1]),
        'final_trustee_payoff': float(trustee_payoff[-1]),
        'cooperation_stability': float(np.std(return_ratios)),
        'agent_1_balances': agent_1_balances,
        'agent_2_balances': agent_2_balances,
    }

    return metrics


def parse_filename(filepath: Path, json_base: Path) -> Tuple[str, str]:
    """
    Extract condition and myth_topic from filepath.
    Returns: (condition, myth_topic or None)
    """
    relative = filepath.relative_to(json_base)
    parts = list(relative.parts)

    condition = parts[0]  # game, myth, game_myth, or myth_game
    myth_topic = parts[1] if len(parts) > 2 else None

    return condition, myth_topic


def aggregate_data(json_base: Path):
    """Aggregate all simulation data by condition and myth topic."""
    data_by_condition = defaultdict(list)
    data_by_topic = defaultdict(list)

    # Find all JSON files
    json_files = [f for f in json_base.rglob("*.json")
                  if ".checkpoint" not in f.name and ".results" not in f.name]

    print(f"Found {len(json_files)} JSON files in {json_base}")

    for json_file in json_files:
        # Load data
        with open(json_file) as f:
            data = json.load(f)

        # Extract metrics
        metrics = extract_game_metrics(data)
        if metrics is None:
            continue

        # Parse condition and topic
        condition, myth_topic = parse_filename(json_file, json_base)

        # Add metadata
        metrics['condition'] = condition
        metrics['myth_topic'] = myth_topic
        metrics['filename'] = json_file.name

        # Store
        data_by_condition[condition].append(metrics)
        if myth_topic:
            data_by_topic[myth_topic].append(metrics)

    return data_by_condition, data_by_topic


def plot_condition_comparison(data_by_condition: Dict, output_dir: Path, model_name: str):
    """Create plots comparing cooperation across conditions."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create DataFrame
    rows = []
    for condition, metrics_list in data_by_condition.items():
        for m in metrics_list:
            final_balance = (m['agent_1_balances'][-1] + m['agent_2_balances'][-1]) / 2 if m['agent_1_balances'] else 0
            rows.append({
                'Condition': CONDITION_LABELS.get(condition, condition),
                'Mean Trust Ratio': m['mean_trust_ratio'],
                'Mean Return Ratio': m['mean_return_ratio'],
                'Mean Sent': m['mean_sent'],
                'Mean Returned': m['mean_returned'],
                'Cooperation Stability': m['cooperation_stability'],
                'Final Cumulative Balance': final_balance,
            })

    df = pd.DataFrame(rows)

    # Set style
    sns.set_style("whitegrid")

    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle(f'Cooperation Patterns: {model_name}',
                 fontsize=16, fontweight='bold')

    # Define condition order for plotting
    condition_order = [CONDITION_LABELS[c] for c in CONDITION_ORDER if c in data_by_condition]

    # Plot 1: Trust Ratio
    ax1 = axes[0, 0]
    sns.boxplot(data=df, x='Condition', y='Mean Trust Ratio',
                order=condition_order, ax=ax1, palette='Set2')
    ax1.set_title('Trust Ratio (Proportion Sent)', fontweight='bold', fontsize=13)
    ax1.set_ylabel('Mean Trust Ratio (0-1)', fontsize=11)
    ax1.set_xlabel('')
    ax1.tick_params(axis='x', rotation=15)

    # Plot 2: Return Ratio
    ax2 = axes[0, 1]
    sns.boxplot(data=df, x='Condition', y='Mean Return Ratio',
                order=condition_order, ax=ax2, palette='Set2')
    ax2.set_title('Return Ratio (Proportion Returned)', fontweight='bold', fontsize=13)
    ax2.set_ylabel('Mean Return Ratio (0-1)', fontsize=11)
    ax2.set_xlabel('')
    ax2.tick_params(axis='x', rotation=15)

    # Plot 3: Absolute amounts sent
    ax3 = axes[1, 0]
    sns.boxplot(data=df, x='Condition', y='Mean Sent',
                order=condition_order, ax=ax3, palette='Set2')
    ax3.set_title('Amount Sent by Investors', fontweight='bold', fontsize=13)
    ax3.set_ylabel('Mean Amount Sent', fontsize=11)
    ax3.set_xlabel('Condition', fontsize=11)
    ax3.tick_params(axis='x', rotation=15)

    # Plot 4: Cooperation stability
    ax4 = axes[1, 1]
    sns.boxplot(data=df, x='Condition', y='Cooperation Stability',
                order=condition_order, ax=ax4, palette='Set2')
    ax4.set_title('Cooperation Stability (Lower = More Stable)', fontweight='bold', fontsize=13)
    ax4.set_ylabel('Std Dev of Return Ratio', fontsize=11)
    ax4.set_xlabel('Condition', fontsize=11)
    ax4.tick_params(axis='x', rotation=15)

    plt.tight_layout()
    plt.savefig(output_dir / 'condition_comparison.png', dpi=300, bbox_inches='tight')
    print(f"Saved: {output_dir / 'condition_comparison.png'}")
    plt.close()


def plot_cumulative_balances_by_condition(data_by_condition: Dict, output_dir: Path, model_name: str):
    """Plot average cumulative balances across conditions."""
    fig, ax = plt.subplots(figsize=(12, 7))

    colors = {'game': '#66c2a5', 'myth': '#fc8d62', 'game_myth': '#8da0cb', 'myth_game': '#e78ac3'}

    for condition in CONDITION_ORDER:
        if condition not in data_by_condition:
            continue

        metrics_list = data_by_condition[condition]

        # Find max rounds
        max_rounds = max(m['num_rounds'] for m in metrics_list)

        # Average balances across all runs
        agent_1_avg = []
        agent_2_avg = []

        for round_idx in range(max_rounds):
            a1_vals = [m['agent_1_balances'][round_idx]
                      for m in metrics_list
                      if round_idx < len(m['agent_1_balances'])]
            a2_vals = [m['agent_2_balances'][round_idx]
                      for m in metrics_list
                      if round_idx < len(m['agent_2_balances'])]

            if a1_vals and a2_vals:
                agent_1_avg.append(np.mean(a1_vals))
                agent_2_avg.append(np.mean(a2_vals))

        rounds = list(range(1, len(agent_1_avg) + 1))
        total_avg = [(a1 + a2) / 2 for a1, a2 in zip(agent_1_avg, agent_2_avg)]

        ax.plot(rounds, total_avg, linewidth=3, label=CONDITION_LABELS[condition],
                color=colors.get(condition, 'gray'), alpha=0.8)

    ax.set_xlabel('Round', fontsize=13, fontweight='bold')
    ax.set_ylabel('Average Cumulative Balance', fontsize=13, fontweight='bold')
    ax.set_title(f'Average Cumulative Balances: {model_name}', fontsize=15, fontweight='bold')
    ax.legend(fontsize=11, loc='best')
    ax.grid(True, alpha=0.3, linestyle='--')

    plt.tight_layout()
    plt.savefig(output_dir / 'cumulative_balances_by_condition.png', dpi=300, bbox_inches='tight')
    print(f"Saved: {output_dir / 'cumulative_balances_by_condition.png'}")
    plt.close()


def export_to_csv(data_by_condition: Dict, output_dir: Path):
    """Export aggregated metrics to CSV files."""

    # CSV: By Condition
    condition_rows = []
    for condition in CONDITION_ORDER:
        if condition not in data_by_condition:
            continue

        metrics_list = data_by_condition[condition]

        for m in metrics_list:
            final_balance = (m['agent_1_balances'][-1] + m['agent_2_balances'][-1]) / 2 if m['agent_1_balances'] else 0
            condition_rows.append({
                'condition': condition,
                'condition_label': CONDITION_LABELS[condition],
                'myth_topic': m.get('myth_topic', ''),
                'filename': m['filename'],
                'num_rounds': m['num_rounds'],
                'mean_trust_ratio': m['mean_trust_ratio'],
                'std_trust_ratio': m['std_trust_ratio'],
                'mean_return_ratio': m['mean_return_ratio'],
                'std_return_ratio': m['std_return_ratio'],
                'mean_sent': m['mean_sent'],
                'mean_returned': m['mean_returned'],
                'cooperation_stability': m['cooperation_stability'],
                'final_cumulative_balance': final_balance,
            })

    df_conditions = pd.DataFrame(condition_rows)
    csv_path = output_dir / 'results_by_condition.csv'
    df_conditions.to_csv(csv_path, index=False)
    print(f"Saved: {csv_path}")


def print_summary_statistics(data_by_condition: Dict, model_name: str):
    """Print summary statistics."""
    print("\n" + "="*80)
    print(f"SUMMARY STATISTICS: {model_name}")
    print("="*80)

    for condition in CONDITION_ORDER:
        if condition not in data_by_condition:
            continue

        metrics_list = data_by_condition[condition]
        trust_ratios = [m['mean_trust_ratio'] for m in metrics_list]
        return_ratios = [m['mean_return_ratio'] for m in metrics_list]

        print(f"\n{CONDITION_LABELS[condition]} (n={len(metrics_list)}):")
        print(f"  Trust Ratio:  {np.mean(trust_ratios):.3f} ± {np.std(trust_ratios):.3f}")
        print(f"  Return Ratio: {np.mean(return_ratios):.3f} ± {np.std(return_ratios):.3f}")

    print("\n" + "="*80)


def main():
    if len(sys.argv) < 2:
        print("Usage: python trajectory_boxplot_custom.py <input_directory>")
        print("Example: python trajectory_boxplot_custom.py data/json/10runs_model_comparison/claude-sonnet-4.5")
        sys.exit(1)

    # Get input directory from command line
    json_base = Path(sys.argv[1])

    if not json_base.exists():
        print(f"Error: Directory not found: {json_base}")
        sys.exit(1)

    # Extract model name from path
    model_name = json_base.name

    # Create output directory
    base_dir = Path(__file__).parent.parent
    output_dir = base_dir / "data" / "plots" / "10runs_model_comparison" / model_name / "_aggregated_analysis"

    print(f"Analyzing: {json_base}")
    print(f"Model: {model_name}")
    print(f"Output: {output_dir}")
    print()

    print("Aggregating simulation results...")
    data_by_condition, data_by_topic = aggregate_data(json_base)

    if not data_by_condition:
        print("No game data found in the specified directory!")
        sys.exit(1)

    print("\nGenerating comparison plots...")
    plot_condition_comparison(data_by_condition, output_dir, model_name)
    plot_cumulative_balances_by_condition(data_by_condition, output_dir, model_name)

    print("\nExporting to CSV...")
    export_to_csv(data_by_condition, output_dir)

    print_summary_statistics(data_by_condition, model_name)

    print(f"\nResults saved to: {output_dir}")


if __name__ == "__main__":
    main()

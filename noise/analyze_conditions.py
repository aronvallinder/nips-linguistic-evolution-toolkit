"""
Analysis script for comparing noise/framing conditions in trust game experiments.

Generates a multi-panel figure showing:
- Panel A: Mean cooperation by condition (bar plot with CI)
- Panel B: Cooperation trajectory over rounds (line plot)
- Panel C: Investor send vs Trustee return behavior
- Panel D: Effect of noise on perceived vs actual cooperation

Usage:
    python noise/analyze_conditions.py data/json/noise_experiments/<experiment_name> output_dir

    # Example:
    python noise/analyze_conditions.py data/json/noise_experiments/framing_comparison data/plots/framing
"""

import os
import sys
import json
import argparse
from pathlib import Path
from collections import defaultdict
import numpy as np

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.gridspec import GridSpec
except ImportError:
    print("matplotlib not found. Install with: pip install matplotlib")
    sys.exit(1)

try:
    import pandas as pd
except ImportError:
    pd = None
    print("pandas not found. Some features may be limited. Install with: pip install pandas")


# Color palette for conditions
CONDITION_COLORS = {
    'default': '#4C72B0',           # Blue
    'noisy_uniform_small': '#DD8452',      # Orange
    'noisy_uniform_large': '#C44E52',      # Red
    'noisy_probabilistic_zero': '#8172B3', # Purple
    'noisy_probabilistic_random': '#937860', # Brown
    'noisy_uniform_informed': '#DA8BC3',   # Pink
    'noisy_both': '#8C8C8C',               # Gray
    'framing_prosocial': '#55A868',        # Green
    'framing_trickster': '#CCB974',        # Yellow/Gold
    'framing_exchange': '#64B5CD',         # Light blue
    'framing_neutral_myth': '#B07AA1',     # Mauve
    'combined_prosocial_noisy': '#72B7B2', # Teal
    'combined_trickster_noisy': '#E9724C', # Coral
}

# Shorter display names for plots
CONDITION_LABELS = {
    'default': 'Baseline',
    'noisy_uniform_small': 'Noise (±$1)',
    'noisy_uniform_large': 'Noise (±$2)',
    'noisy_probabilistic_zero': 'Noise (20%→$0)',
    'noisy_probabilistic_random': 'Noise (10%→rand)',
    'noisy_uniform_informed': 'Noise (informed)',
    'noisy_both': 'Noise (both)',
    'framing_prosocial': 'Prosocial names',
    'framing_trickster': 'Trickster names',
    'framing_exchange': 'Exchange names',
    'framing_neutral_myth': 'Neutral myth',
    'combined_prosocial_noisy': 'Prosocial + Noise',
    'combined_trickster_noisy': 'Trickster + Noise',
}


def load_experiment_data(experiment_dir, group_by='both'):
    """
    Load all experiment JSON files from a directory structure.

    Args:
        experiment_dir: Path to experiment directory
        group_by: How to group data:
            - 'none': flat dict by condition
            - 'task_order': nested by task_order -> condition
            - 'model': nested by model -> condition
            - 'both': nested by model -> task_order -> condition

    Returns:
        Nested dict based on group_by parameter
    """
    experiment_dir = Path(experiment_dir)

    # Initialize based on grouping
    if group_by == 'both':
        data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    elif group_by == 'model':
        data = defaultdict(lambda: defaultdict(list))
    elif group_by == 'task_order':
        data = defaultdict(lambda: defaultdict(list))
    else:
        data = defaultdict(list)

    # Walk through directory structure
    for json_file in experiment_dir.rglob("*.json"):
        # Skip checkpoint and results files
        if '.checkpoint' in str(json_file) or '.results' in str(json_file):
            continue
        if '.error' in str(json_file):
            continue

        try:
            with open(json_file, 'r') as f:
                file_data = json.load(f)

            # Extract condition from metadata or path
            metadata = file_data.get('run_metadata', {})
            condition = metadata.get('game_params_name', 'unknown')

            # If not in metadata, try to extract from path
            if condition == 'unknown':
                parts = json_file.parts
                for part in parts:
                    if part in CONDITION_COLORS:
                        condition = part
                        break

            # Extract task_order from metadata or path
            task_order = metadata.get('task_order', None)
            if task_order:
                task_order_str = '_'.join(task_order) if isinstance(task_order, list) else task_order
            else:
                # Try to extract from path (e.g., .../game/ or .../myth_game/)
                parts = json_file.parts
                task_order_str = 'unknown'
                for part in parts:
                    if part in ['game', 'myth', 'game_myth', 'myth_game']:
                        task_order_str = part
                        break

            # Extract model from metadata or path
            model = metadata.get('model', 'unknown')
            if model != 'unknown':
                # Clean model name (get last part after /)
                model = model.split('/')[-1]
            else:
                # Try to extract from path
                parts = json_file.parts
                for part in parts:
                    # Model names often contain hyphens and numbers
                    if any(x in part.lower() for x in ['gpt', 'claude', 'llama', 'gemini', 'deepseek']):
                        model = part
                        break

            exp_data = {
                'file': str(json_file),
                'data': file_data,
                'metadata': metadata,
                'task_order': task_order_str,
                'model': model
            }

            if group_by == 'both':
                data[model][task_order_str][condition].append(exp_data)
            elif group_by == 'model':
                data[model][condition].append(exp_data)
            elif group_by == 'task_order':
                data[task_order_str][condition].append(exp_data)
            else:
                data[condition].append(exp_data)

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Could not load {json_file}: {e}")
            continue

    # Convert defaultdicts to regular dicts
    if group_by == 'both':
        return {m: {t: dict(c) for t, c in tasks.items()} for m, tasks in data.items()}
    elif group_by in ['model', 'task_order']:
        return {k: dict(v) for k, v in data.items()}
    return dict(data)


def extract_game_metrics(experiment_data):
    """
    Extract game metrics from experiment data.

    Returns:
        dict with keys: rounds, sent, returned, sent_pct, returned_pct,
                       sent_communicated, returned_communicated, noise_applied
    """
    conv_history = experiment_data.get('conversation_history', [])
    game_data = experiment_data.get('game_data', {})

    metrics = {
        'rounds': [],
        'sent': [],
        'returned': [],
        'sent_pct': [],
        'returned_pct': [],
        'sent_communicated': [],
        'returned_communicated': [],
        'noise_applied': [],
        'investor_payoff': [],
        'trustee_payoff': [],
    }

    endowment = 5  # Default, could extract from data
    multiplier = 3

    for entry in conv_history:
        if entry.get('sent') is not None:
            sent = entry['sent']
            returned = entry['returned']
            received = sent * multiplier

            metrics['rounds'].append(entry.get('round', len(metrics['rounds']) + 1))
            metrics['sent'].append(sent)
            metrics['returned'].append(returned)
            metrics['sent_pct'].append(sent / endowment * 100 if endowment > 0 else 0)
            metrics['returned_pct'].append(returned / received * 100 if received > 0 else 0)

            # Noise-specific data
            metrics['sent_communicated'].append(entry.get('sent_communicated', sent))
            metrics['returned_communicated'].append(entry.get('returned_communicated', returned))
            metrics['noise_applied'].append(entry.get('noise_applied', False))

            metrics['investor_payoff'].append(entry.get('investor_payoff', 0))
            metrics['trustee_payoff'].append(entry.get('trustee_payoff', 0))

    return metrics


def aggregate_condition_data(data_by_condition):
    """
    Aggregate metrics across all runs for each condition.

    Returns:
        dict: {condition: {metric: aggregated_values}}
    """
    aggregated = {}

    for condition, experiments in data_by_condition.items():
        all_metrics = defaultdict(list)
        round_metrics = defaultdict(lambda: defaultdict(list))

        for exp in experiments:
            metrics = extract_game_metrics(exp['data'])

            # Aggregate overall metrics
            if metrics['sent']:
                all_metrics['mean_sent'].append(np.mean(metrics['sent']))
                all_metrics['mean_returned'].append(np.mean(metrics['returned']))
                all_metrics['mean_sent_pct'].append(np.mean(metrics['sent_pct']))
                all_metrics['mean_returned_pct'].append(np.mean(metrics['returned_pct']))
                all_metrics['noise_rate'].append(np.mean(metrics['noise_applied']))

                # Per-round data for trajectories
                for i, r in enumerate(metrics['rounds']):
                    round_metrics[r]['sent'].append(metrics['sent'][i])
                    round_metrics[r]['returned'].append(metrics['returned'][i])
                    round_metrics[r]['sent_pct'].append(metrics['sent_pct'][i])
                    round_metrics[r]['returned_pct'].append(metrics['returned_pct'][i])

        aggregated[condition] = {
            'overall': dict(all_metrics),
            'by_round': dict(round_metrics),
            'n_experiments': len(experiments)
        }

    return aggregated


def plot_cooperation_bars(ax, aggregated_data, metric='mean_sent_pct'):
    """Panel A: Bar plot of mean cooperation by condition."""
    conditions = list(aggregated_data.keys())

    # Sort conditions for consistent display
    sort_order = ['default', 'noisy_uniform_small', 'noisy_uniform_large',
                  'noisy_probabilistic_zero', 'noisy_uniform_informed',
                  'framing_prosocial', 'framing_trickster', 'framing_exchange',
                  'combined_prosocial_noisy', 'combined_trickster_noisy']
    conditions = [c for c in sort_order if c in conditions] + \
                 [c for c in conditions if c not in sort_order]

    means = []
    stds = []
    colors = []
    labels = []

    for cond in conditions:
        data = aggregated_data[cond]['overall'].get(metric, [])
        if data:
            means.append(np.mean(data))
            stds.append(np.std(data) / np.sqrt(len(data)))  # SEM
        else:
            means.append(0)
            stds.append(0)
        colors.append(CONDITION_COLORS.get(cond, '#888888'))
        labels.append(CONDITION_LABELS.get(cond, cond))

    x = np.arange(len(conditions))
    bars = ax.bar(x, means, yerr=stds, capsize=3, color=colors, edgecolor='black', linewidth=0.5)

    ax.set_ylabel('Mean Sent (% of endowment)')
    ax.set_xlabel('Condition')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=8)
    ax.set_ylim(0, 100)
    ax.axhline(y=50, color='gray', linestyle='--', alpha=0.5, label='50% reference')
    ax.set_title('A. Mean Cooperation by Condition')

    # Add n labels on bars
    for i, (bar, cond) in enumerate(zip(bars, conditions)):
        n = aggregated_data[cond]['n_experiments']
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + stds[i] + 2,
                f'n={n}', ha='center', va='bottom', fontsize=7)


def plot_trajectories(ax, aggregated_data, metric='sent_pct'):
    """Panel B: Line plot of cooperation over rounds."""
    for condition, data in aggregated_data.items():
        by_round = data['by_round']
        if not by_round:
            continue

        rounds = sorted(by_round.keys())
        means = []
        sems = []

        for r in rounds:
            values = by_round[r].get(metric, [])
            if values:
                means.append(np.mean(values))
                sems.append(np.std(values) / np.sqrt(len(values)))
            else:
                means.append(np.nan)
                sems.append(0)

        color = CONDITION_COLORS.get(condition, '#888888')
        label = CONDITION_LABELS.get(condition, condition)

        ax.plot(rounds, means, '-o', color=color, label=label, markersize=4, linewidth=1.5)
        ax.fill_between(rounds,
                        np.array(means) - np.array(sems),
                        np.array(means) + np.array(sems),
                        color=color, alpha=0.2)

    ax.set_xlabel('Round')
    ax.set_ylabel('Sent (% of endowment)')
    ax.set_ylim(0, 100)
    ax.legend(loc='upper right', fontsize=7, ncol=2)
    ax.set_title('B. Cooperation Trajectory Over Rounds')
    ax.axhline(y=50, color='gray', linestyle='--', alpha=0.5)


def plot_investor_vs_trustee(ax, aggregated_data):
    """Panel C: Scatter plot of investor send vs trustee return."""
    for condition, data in aggregated_data.items():
        sent = data['overall'].get('mean_sent_pct', [])
        returned = data['overall'].get('mean_returned_pct', [])

        if sent and returned:
            color = CONDITION_COLORS.get(condition, '#888888')
            label = CONDITION_LABELS.get(condition, condition)

            # Plot each experiment as a point
            ax.scatter(sent, returned, c=color, label=label, alpha=0.7, s=50, edgecolors='black', linewidth=0.5)

            # Plot mean as larger marker
            ax.scatter([np.mean(sent)], [np.mean(returned)], c=color, s=150,
                      marker='*', edgecolors='black', linewidth=1)

    ax.set_xlabel('Investor: Mean Sent (%)')
    ax.set_ylabel('Trustee: Mean Returned (%)')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.plot([0, 100], [0, 100], 'k--', alpha=0.3, label='Equal')
    ax.legend(loc='upper left', fontsize=7)
    ax.set_title('C. Investor vs Trustee Behavior')


def plot_noise_effect(ax, aggregated_data):
    """Panel D: Effect of noise - actual vs communicated amounts."""
    # Group conditions by noise type
    noise_conditions = [c for c in aggregated_data.keys()
                       if 'noisy' in c or 'combined' in c]
    baseline_conditions = [c for c in aggregated_data.keys()
                          if c not in noise_conditions]

    if not noise_conditions:
        ax.text(0.5, 0.5, 'No noise conditions\nin this dataset',
               ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_title('D. Noise Effect')
        return

    # Compare cooperation rates
    x_labels = []
    baseline_means = []
    noise_means = []

    # Get baseline mean
    baseline_vals = []
    for cond in baseline_conditions:
        baseline_vals.extend(aggregated_data[cond]['overall'].get('mean_sent_pct', []))
    baseline_mean = np.mean(baseline_vals) if baseline_vals else 0

    for cond in noise_conditions:
        vals = aggregated_data[cond]['overall'].get('mean_sent_pct', [])
        if vals:
            x_labels.append(CONDITION_LABELS.get(cond, cond))
            noise_means.append(np.mean(vals))
            baseline_means.append(baseline_mean)

    if x_labels:
        x = np.arange(len(x_labels))
        width = 0.35

        ax.bar(x - width/2, baseline_means, width, label='Baseline', color='#4C72B0', alpha=0.7)
        ax.bar(x + width/2, noise_means, width, label='With Noise/Framing',
               color=[CONDITION_COLORS.get(c, '#888') for c in noise_conditions])

        ax.set_xticks(x)
        ax.set_xticklabels(x_labels, rotation=45, ha='right', fontsize=8)
        ax.set_ylabel('Mean Sent (%)')
        ax.legend(loc='upper right', fontsize=8)
        ax.set_ylim(0, 100)

    ax.set_title('D. Noise/Framing Effect vs Baseline')


def create_summary_figure(aggregated_data, output_path, title_suffix=""):
    """Create the main 4-panel summary figure."""
    fig = plt.figure(figsize=(14, 10))
    gs = GridSpec(2, 2, figure=fig, hspace=0.35, wspace=0.25)

    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[1, 0])
    ax4 = fig.add_subplot(gs[1, 1])

    plot_cooperation_bars(ax1, aggregated_data)
    plot_trajectories(ax2, aggregated_data)
    plot_investor_vs_trustee(ax3, aggregated_data)
    plot_noise_effect(ax4, aggregated_data)

    plt.suptitle(f'Trust Game: Noise & Framing Condition Comparison{title_suffix}', fontsize=14, y=0.98)

    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    print(f"Saved summary figure to {output_path}")
    plt.close()


def create_detailed_trajectory_figure(aggregated_data, output_path, title_suffix=""):
    """Create a detailed trajectory figure with separate panels per condition."""
    conditions = list(aggregated_data.keys())
    n_conditions = len(conditions)

    if n_conditions == 0:
        print("No conditions to plot")
        return

    # Calculate grid dimensions
    n_cols = min(3, n_conditions)
    n_rows = (n_conditions + n_cols - 1) // n_cols

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(5*n_cols, 4*n_rows), squeeze=False)

    for idx, condition in enumerate(conditions):
        row = idx // n_cols
        col = idx % n_cols
        ax = axes[row, col]

        data = aggregated_data[condition]
        by_round = data['by_round']

        if not by_round:
            ax.text(0.5, 0.5, 'No data', ha='center', va='center')
            ax.set_title(CONDITION_LABELS.get(condition, condition))
            continue

        rounds = sorted(by_round.keys())

        # Plot sent and returned
        for metric, label, color in [('sent_pct', 'Sent', '#4C72B0'),
                                      ('returned_pct', 'Returned', '#55A868')]:
            means = []
            sems = []
            for r in rounds:
                values = by_round[r].get(metric, [])
                if values:
                    means.append(np.mean(values))
                    sems.append(np.std(values) / np.sqrt(len(values)))
                else:
                    means.append(np.nan)
                    sems.append(0)

            ax.plot(rounds, means, '-o', color=color, label=label, markersize=3)
            ax.fill_between(rounds,
                           np.array(means) - np.array(sems),
                           np.array(means) + np.array(sems),
                           color=color, alpha=0.2)

        ax.set_xlabel('Round')
        ax.set_ylabel('%')
        ax.set_ylim(0, 100)
        ax.legend(loc='upper right', fontsize=8)
        ax.set_title(f"{CONDITION_LABELS.get(condition, condition)} (n={data['n_experiments']})")
        ax.axhline(y=50, color='gray', linestyle='--', alpha=0.5)

    # Hide empty subplots
    for idx in range(n_conditions, n_rows * n_cols):
        row = idx // n_cols
        col = idx % n_cols
        axes[row, col].set_visible(False)

    plt.suptitle(f'Detailed Trajectories by Condition{title_suffix}', fontsize=14)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    print(f"Saved detailed trajectories to {output_path}")
    plt.close()


def print_summary_stats(aggregated_data):
    """Print summary statistics to console."""
    print("\n" + "="*70)
    print("SUMMARY STATISTICS")
    print("="*70)

    for condition in sorted(aggregated_data.keys()):
        data = aggregated_data[condition]
        overall = data['overall']
        n = data['n_experiments']

        sent = overall.get('mean_sent_pct', [])
        returned = overall.get('mean_returned_pct', [])
        noise_rate = overall.get('noise_rate', [])

        print(f"\n{CONDITION_LABELS.get(condition, condition)} (n={n}):")
        if sent:
            print(f"  Mean sent:     {np.mean(sent):5.1f}% (SD={np.std(sent):5.1f})")
        if returned:
            print(f"  Mean returned: {np.mean(returned):5.1f}% (SD={np.std(returned):5.1f})")
        if noise_rate and np.mean(noise_rate) > 0:
            print(f"  Noise applied: {np.mean(noise_rate)*100:5.1f}% of rounds")

    print("\n" + "="*70)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze and visualize noise/framing experiment results",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Analyze experiments (separate figures for each model/task_order)
    python noise/analyze_conditions.py data/json/noise_experiments/noise_comparison plots/noise_comparison

    # Combine everything into one figure
    python noise/analyze_conditions.py data/json/noise_experiments/noise_comparison plots/ --combine
        """
    )
    parser.add_argument('input_dir', help='Directory containing experiment JSON files')
    parser.add_argument('output_dir', help='Base directory for output plots (will create {model}/{task_order}/ subdirs)')
    parser.add_argument('--prefix', default='conditions', help='Prefix for output filenames')
    parser.add_argument('--combine', action='store_true',
                       help='Combine all models/task orders into one figure')

    args = parser.parse_args()

    # Load data
    print(f"Loading experiments from {args.input_dir}...")

    if args.combine:
        # Load without grouping
        data_by_condition = load_experiment_data(args.input_dir, group_by='none')

        if not data_by_condition:
            print("No experiment data found!")
            sys.exit(1)

        print(f"Found {len(data_by_condition)} conditions:")
        for cond, exps in data_by_condition.items():
            print(f"  - {cond}: {len(exps)} experiments")

        # Create output directory
        os.makedirs(args.output_dir, exist_ok=True)

        # Aggregate and create figures
        print("\nAggregating metrics...")
        aggregated = aggregate_condition_data(data_by_condition)
        print_summary_stats(aggregated)

        print("\nGenerating figures...")
        summary_path = os.path.join(args.output_dir, f'{args.prefix}_summary.png')
        create_summary_figure(aggregated, summary_path)

        detailed_path = os.path.join(args.output_dir, f'{args.prefix}_trajectories.png')
        create_detailed_trajectory_figure(aggregated, detailed_path)

    else:
        # Load grouped by model and task order
        data_by_model = load_experiment_data(args.input_dir, group_by='both')

        if not data_by_model:
            print("No experiment data found!")
            sys.exit(1)

        # Print summary
        print(f"Found {len(data_by_model)} models:")
        for model, task_orders in data_by_model.items():
            print(f"\n  [{model}]")
            for task_order, conditions in task_orders.items():
                total_exps = sum(len(exps) for exps in conditions.values())
                print(f"    [{task_order}] - {len(conditions)} conditions, {total_exps} experiments")

        # Create separate figures for each model/task_order combination
        for model, task_orders in data_by_model.items():
            for task_order, data_by_condition in task_orders.items():
                print(f"\n{'='*60}")
                print(f"Processing: {model} / {task_order}")
                print('='*60)

                # Create output directory: {output_dir}/{model}/{task_order}/
                model_safe = model.replace('/', '_')
                task_order_safe = task_order.replace('/', '_')
                out_dir = os.path.join(args.output_dir, model_safe, task_order_safe)
                os.makedirs(out_dir, exist_ok=True)

                # Aggregate metrics
                print("Aggregating metrics...")
                aggregated = aggregate_condition_data(data_by_condition)

                # Print summary stats
                print_summary_stats(aggregated)

                # Create figures
                print("\nGenerating figures...")
                title_suffix = f" [{model} / {task_order}]"

                summary_path = os.path.join(out_dir, f'{args.prefix}_summary.png')
                create_summary_figure(aggregated, summary_path, title_suffix=title_suffix)

                detailed_path = os.path.join(out_dir, f'{args.prefix}_trajectories.png')
                create_detailed_trajectory_figure(aggregated, detailed_path, title_suffix=title_suffix)

    print("\nDone!")


if __name__ == "__main__":
    main()

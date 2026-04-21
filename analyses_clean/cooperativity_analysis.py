"""
Cooperativity Analysis for Trust Game Myths

This script analyzes narrative-based cooperativity in myths and measures
mimicry/adaptation between agents using lag correlations.

The problems of current analysis/tokenization:
- Dictionary-based: Uses exact word matches (after tokenization/cleaning), not semantic analysis.
- No context: Doesn't consider negation (e.g., "not cooperative" would still count "cooperative").
- No stemming: Only exact matches (e.g., "cooperate" vs "cooperating").
"""

import json
import os
import re
from collections import defaultdict
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import numpy as np


# Common English stopwords
STOPWORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
    'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been', 'be', 'have', 'has', 'had',
    'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can',
    'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
    'them', 'their', 'his', 'her', 'its', 'our', 'your', 'who', 'which', 'what',
    'where', 'when', 'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more',
    'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same',
    'so', 'than', 'too', 'very', 's', 't', 'just', 'now', 'then'
}


def tokenize_and_clean(text: str) -> List[str]:
    """
    Tokenize text into words, remove stopwords and non-alphanumeric tokens.

    Args:
        text: Input text to tokenize

    Returns:
        List of cleaned tokens
    """
    # Convert to lowercase
    text = text.lower()

    # Extract words (alphanumeric sequences)
    words = re.findall(r'\b[a-z]+\b', text)

    # Remove stopwords and short words
    cleaned_words = [w for w in words if w not in STOPWORDS and len(w) > 2]

    return cleaned_words


def read_myths_from_json(filepath: str) -> Dict[str, Dict[int, str]]:
    """
    Read myths from Trust_simulation_state.json file.

    Args:
        filepath: Path to the JSON file

    Returns:
        Dictionary mapping agent_id -> round -> myth_text
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    myths_by_agent = defaultdict(dict)

    # Extract myths from conversation history
    for entry in data.get('conversation_history', []):
        round_num = entry.get('round')
        myths = entry.get('myths', {})

        for agent_id, myth_text in myths.items():
            myths_by_agent[agent_id][round_num] = myth_text

    return dict(myths_by_agent)


def analyze_cooperativity(myths_by_agent: Dict[str, Dict[int, str]]) -> Dict[str, Dict[int, Dict[str, float]]]:
    """
    Analyze narrative-based cooperativity in myths.

    Args:
        myths_by_agent: Dictionary mapping agent_id -> round -> myth_text

    Returns:
        Dictionary mapping agent_id -> round -> cooperativity_scores
    """
    # Define cooperativity word categories
    collective_words = {'together', 'shared', 'mutual', 'partnership', 'community',
                       'collaboration', 'unity', 'collective', 'bond', 'alliance',
                       'cooperation', 'cooperate', 'collaborative'}

    individual_words = {'alone', 'solitary', 'independent', 'self', 'individual',
                       'isolated', 'separate', 'isolation', 'lonely', 'solo'}

    connected_words = {'relationship', 'connection', 'cooperation', 'reciprocity',
                      'trust', 'friendship', 'companion', 'ally', 'partner', 'kindness',
                      'generosity', 'compassion', 'solidarity'}

    disconnected_words = {'betrayal', 'isolation', 'division', 'conflict', 'rivalry',
                         'enemy', 'hostility', 'antagonism', 'opposition', 'discord'}

    giving_words = {'give', 'giving', 'gave', 'given', 'offered', 'offer', 'returned',
                   'return', 'shared', 'share', 'generous', 'gift', 'bestow', 'granted'}

    taking_words = {'took', 'taken', 'take', 'kept', 'keep', 'withheld', 'withhold',
                   'refused', 'refuse', 'denied', 'deny', 'hoarded', 'hoard'}

    cooperativity_scores = {}

    for agent_id, rounds in myths_by_agent.items():
        cooperativity_scores[agent_id] = {}

        for round_num, myth_text in rounds.items():
            words = tokenize_and_clean(myth_text)

            # Count words in each category
            collective_count = sum(1 for w in words if w in collective_words)
            individual_count = sum(1 for w in words if w in individual_words)
            connected_count = sum(1 for w in words if w in connected_words)
            disconnected_count = sum(1 for w in words if w in disconnected_words)
            giving_count = sum(1 for w in words if w in giving_words)
            taking_count = sum(1 for w in words if w in taking_words)

            # Calculate cooperativity metrics
            cooperative_total = collective_count + connected_count + giving_count
            uncooperative_total = individual_count + disconnected_count + taking_count
            total_words = len(words)

            # Mutuality ratio (bounded, interpretable)
            mutuality_ratio = cooperative_total / (uncooperative_total + 1)

            # Cooperative proportion (as percentage of total words)
            cooperative_pct = (cooperative_total / total_words * 100) if total_words > 0 else 0
            uncooperative_pct = (uncooperative_total / total_words * 100) if total_words > 0 else 0

            cooperativity_scores[agent_id][round_num] = {
                'collective': collective_count,
                'individual': individual_count,
                'connected': connected_count,
                'disconnected': disconnected_count,
                'giving': giving_count,
                'taking': taking_count,
                'mutuality_ratio': mutuality_ratio,
                'cooperative_pct': cooperative_pct,
                'uncooperative_pct': uncooperative_pct,
                'total_words': total_words
            }

    return cooperativity_scores


def calculate_lag_correlation(scores_a: List[float], scores_b: List[float], lag: int = 1) -> float:
    """
    Calculate correlation between agent A's scores and agent B's lagged scores.

    Args:
        scores_a: Agent A's scores over time
        scores_b: Agent B's scores over time
        lag: How many rounds to lag (default 1 = previous round)

    Returns:
        Pearson correlation coefficient
    """
    if len(scores_a) <= lag or len(scores_b) <= lag:
        return 0.0

    # Agent A's scores from round lag+1 onwards
    a_lagged = scores_a[lag:]
    # Agent B's scores from round 1 to -lag
    b_lagged = scores_b[:-lag]

    if len(a_lagged) != len(b_lagged) or len(a_lagged) < 2:
        return 0.0

    # Calculate Pearson correlation
    mean_a = np.mean(a_lagged)
    mean_b = np.mean(b_lagged)

    numerator = np.sum((np.array(a_lagged) - mean_a) * (np.array(b_lagged) - mean_b))
    denominator = np.sqrt(np.sum((np.array(a_lagged) - mean_a)**2) * np.sum((np.array(b_lagged) - mean_b)**2))

    if denominator == 0:
        return 0.0

    return numerator / denominator


def visualize_cooperativity(cooperativity_scores: Dict[str, Dict[int, Dict[str, float]]],
                            output_file: str = 'cooperativity_analysis.png'):
    """
    Visualize cooperativity measures and lag correlations.

    Args:
        cooperativity_scores: Cooperativity analysis results
        output_file: Output file path
    """
    fig = plt.figure(figsize=(20, 12))
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

    agent_ids = sorted(cooperativity_scores.keys())

    # Extract data for plotting
    agent_data = {}
    for agent_id in agent_ids:
        rounds = sorted(cooperativity_scores[agent_id].keys())
        agent_data[agent_id] = {
            'rounds': rounds,
            'mutuality_ratio': [cooperativity_scores[agent_id][r]['mutuality_ratio'] for r in rounds],
            'cooperative_pct': [cooperativity_scores[agent_id][r]['cooperative_pct'] for r in rounds],
            'uncooperative_pct': [cooperativity_scores[agent_id][r]['uncooperative_pct'] for r in rounds],
            'collective': [cooperativity_scores[agent_id][r]['collective'] for r in rounds],
            'connected': [cooperativity_scores[agent_id][r]['connected'] for r in rounds],
            'giving': [cooperativity_scores[agent_id][r]['giving'] for r in rounds],
        }

    colors = {'Agent_1': '#3498db', 'Agent_2': '#e74c3c'}

    # Plot 1: Mutuality Ratio over time
    ax1 = fig.add_subplot(gs[0, 0])
    for agent_id in agent_ids:
        ax1.plot(agent_data[agent_id]['rounds'], agent_data[agent_id]['mutuality_ratio'],
                marker='o', linewidth=2.5, markersize=8, label=agent_id,
                color=colors.get(agent_id, '#95a5a6'), alpha=0.8)
    ax1.set_xlabel('Round (Generation)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Mutuality Ratio', fontsize=12, fontweight='bold')
    ax1.set_title('Cooperativity: Mutuality Ratio Over Time', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3, linestyle='--')

    # Plot 2: Cooperative vs Uncooperative Language (%)
    ax2 = fig.add_subplot(gs[0, 1])
    for agent_id in agent_ids:
        ax2.plot(agent_data[agent_id]['rounds'], agent_data[agent_id]['cooperative_pct'],
                marker='o', linewidth=2.5, markersize=8, label=f'{agent_id} Cooperative',
                color=colors.get(agent_id, '#95a5a6'), alpha=0.8)
        ax2.plot(agent_data[agent_id]['rounds'], agent_data[agent_id]['uncooperative_pct'],
                marker='s', linewidth=2.5, markersize=8, label=f'{agent_id} Uncooperative',
                color=colors.get(agent_id, '#95a5a6'), alpha=0.4, linestyle='--')
    ax2.set_xlabel('Round (Generation)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Percentage of Total Words', fontsize=12, fontweight='bold')
    ax2.set_title('Cooperative vs Uncooperative Language', fontsize=13, fontweight='bold')
    ax2.legend(fontsize=9, ncol=2)
    ax2.grid(True, alpha=0.3, linestyle='--')

    # Plot 3: Stacked area - Cooperativity components for Agent_1
    ax3 = fig.add_subplot(gs[1, 0])
    agent_id = agent_ids[0]
    ax3.stackplot(agent_data[agent_id]['rounds'],
                 agent_data[agent_id]['collective'],
                 agent_data[agent_id]['connected'],
                 agent_data[agent_id]['giving'],
                 labels=['Collective', 'Connected', 'Giving'],
                 colors=['#2ecc71', '#3498db', '#9b59b6'], alpha=0.7)
    ax3.set_xlabel('Round (Generation)', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Word Count', fontsize=12, fontweight='bold')
    ax3.set_title(f'{agent_id}: Cooperativity Components', fontsize=13, fontweight='bold')
    ax3.legend(loc='upper left', fontsize=10)
    ax3.grid(True, alpha=0.3, linestyle='--')

    # Plot 4: Stacked area - Cooperativity components for Agent_2
    ax4 = fig.add_subplot(gs[1, 1])
    agent_id = agent_ids[1]
    ax4.stackplot(agent_data[agent_id]['rounds'],
                 agent_data[agent_id]['collective'],
                 agent_data[agent_id]['connected'],
                 agent_data[agent_id]['giving'],
                 labels=['Collective', 'Connected', 'Giving'],
                 colors=['#2ecc71', '#3498db', '#9b59b6'], alpha=0.7)
    ax4.set_xlabel('Round (Generation)', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Word Count', fontsize=12, fontweight='bold')
    ax4.set_title(f'{agent_id}: Cooperativity Components', fontsize=13, fontweight='bold')
    ax4.legend(loc='upper left', fontsize=10)
    ax4.grid(True, alpha=0.3, linestyle='--')

    # Plot 5: Lag correlation scatter - Does Agent_1 mirror Agent_2's previous round?
    ax5 = fig.add_subplot(gs[2, 0])
    agent_1_scores = agent_data[agent_ids[0]]['mutuality_ratio']
    agent_2_scores = agent_data[agent_ids[1]]['mutuality_ratio']

    if len(agent_1_scores) > 1:
        # Agent_1 in round N vs Agent_2 in round N-1
        a1_lagged = agent_1_scores[1:]
        a2_previous = agent_2_scores[:-1]

        ax5.scatter(a2_previous, a1_lagged, s=100, alpha=0.6, color=colors[agent_ids[0]])

        # Add trend line
        if len(a2_previous) > 1:
            z = np.polyfit(a2_previous, a1_lagged, 1)
            p = np.poly1d(z)
            x_line = np.linspace(min(a2_previous), max(a2_previous), 100)
            ax5.plot(x_line, p(x_line), "--", color=colors[agent_ids[0]], alpha=0.8, linewidth=2)

            # Calculate correlation
            corr = calculate_lag_correlation(agent_1_scores, agent_2_scores, lag=1)
            ax5.text(0.05, 0.95, f'r = {corr:.3f}', transform=ax5.transAxes,
                    fontsize=12, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    ax5.set_xlabel(f'{agent_ids[1]} Mutuality (Round N-1)', fontsize=11, fontweight='bold')
    ax5.set_ylabel(f'{agent_ids[0]} Mutuality (Round N)', fontsize=11, fontweight='bold')
    ax5.set_title(f'Mimicry: Does {agent_ids[0]} Adopt {agent_ids[1]}\'s Cooperativity?', fontsize=12, fontweight='bold')
    ax5.grid(True, alpha=0.3, linestyle='--')

    # Plot 6: Lag correlation scatter - Does Agent_2 mirror Agent_1's previous round?
    ax6 = fig.add_subplot(gs[2, 1])
    if len(agent_2_scores) > 1:
        # Agent_2 in round N vs Agent_1 in round N-1
        a2_lagged = agent_2_scores[1:]
        a1_previous = agent_1_scores[:-1]

        ax6.scatter(a1_previous, a2_lagged, s=100, alpha=0.6, color=colors[agent_ids[1]])

        # Add trend line
        if len(a1_previous) > 1:
            z = np.polyfit(a1_previous, a2_lagged, 1)
            p = np.poly1d(z)
            x_line = np.linspace(min(a1_previous), max(a1_previous), 100)
            ax6.plot(x_line, p(x_line), "--", color=colors[agent_ids[1]], alpha=0.8, linewidth=2)

            # Calculate correlation
            corr = calculate_lag_correlation(agent_2_scores, agent_1_scores, lag=1)
            ax6.text(0.05, 0.95, f'r = {corr:.3f}', transform=ax6.transAxes,
                    fontsize=12, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    ax6.set_xlabel(f'{agent_ids[0]} Mutuality (Round N-1)', fontsize=11, fontweight='bold')
    ax6.set_ylabel(f'{agent_ids[1]} Mutuality (Round N)', fontsize=11, fontweight='bold')
    ax6.set_title(f'Mimicry: Does {agent_ids[1]} Adopt {agent_ids[0]}\'s Cooperativity?', fontsize=12, fontweight='bold')
    ax6.grid(True, alpha=0.3, linestyle='--')

    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Cooperativity visualization saved to {output_file}")


def print_cooperativity_summary(cooperativity_scores: Dict[str, Dict[int, Dict[str, float]]]):
    """
    Print summary statistics for cooperativity analysis.

    Args:
        cooperativity_scores: Cooperativity analysis results
    """
    print("\n" + "="*80)
    print("COOPERATIVITY ANALYSIS")
    print("="*80)

    agent_ids = sorted(cooperativity_scores.keys())

    for agent_id in agent_ids:
        print(f"\n{'─'*80}")
        print(f"AGENT: {agent_id}")
        print(f"{'─'*80}")

        rounds = sorted(cooperativity_scores[agent_id].keys())

        # Baseline (Round 1)
        baseline = cooperativity_scores[agent_id][rounds[0]]
        print(f"\nBaseline (Round {rounds[0]}):")
        print(f"  Mutuality Ratio: {baseline['mutuality_ratio']:.3f}")
        print(f"  Cooperative Language: {baseline['cooperative_pct']:.2f}%")
        print(f"  Uncooperative Language: {baseline['uncooperative_pct']:.2f}%")

        # Average across all rounds
        avg_mutuality = np.mean([cooperativity_scores[agent_id][r]['mutuality_ratio'] for r in rounds])
        avg_coop = np.mean([cooperativity_scores[agent_id][r]['cooperative_pct'] for r in rounds])
        avg_uncoop = np.mean([cooperativity_scores[agent_id][r]['uncooperative_pct'] for r in rounds])

        print(f"\nAverage across all rounds:")
        print(f"  Mutuality Ratio: {avg_mutuality:.3f}")
        print(f"  Cooperative Language: {avg_coop:.2f}%")
        print(f"  Uncooperative Language: {avg_uncoop:.2f}%")

    # Lag correlations
    print(f"\n{'─'*80}")
    print("LAG CORRELATIONS (Mimicry Analysis)")
    print(f"{'─'*80}")

    if len(agent_ids) == 2:
        agent_1_scores = [cooperativity_scores[agent_ids[0]][r]['mutuality_ratio']
                         for r in sorted(cooperativity_scores[agent_ids[0]].keys())]
        agent_2_scores = [cooperativity_scores[agent_ids[1]][r]['mutuality_ratio']
                         for r in sorted(cooperativity_scores[agent_ids[1]].keys())]

        corr_1_2 = calculate_lag_correlation(agent_1_scores, agent_2_scores, lag=1)
        corr_2_1 = calculate_lag_correlation(agent_2_scores, agent_1_scores, lag=1)

        print(f"\n{agent_ids[0]} adopts {agent_ids[1]}'s cooperativity (lag-1): r = {corr_1_2:.3f}")
        print(f"{agent_ids[1]} adopts {agent_ids[0]}'s cooperativity (lag-1): r = {corr_2_1:.3f}")

        if abs(corr_1_2) > 0.3:
            print(f"\n→ {agent_ids[0]} shows {'positive' if corr_1_2 > 0 else 'negative'} mimicry of {agent_ids[1]}")
        if abs(corr_2_1) > 0.3:
            print(f"→ {agent_ids[1]} shows {'positive' if corr_2_1 > 0 else 'negative'} mimicry of {agent_ids[0]}")


def save_results_to_json(cooperativity_scores: Dict[str, Dict[int, Dict[str, float]]],
                         output_file: str):
    """
    Save cooperativity analysis results to JSON file.

    Args:
        cooperativity_scores: Cooperativity analysis results
        output_file: Output file path
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cooperativity_scores, f, indent=2, ensure_ascii=False)

    print(f"Cooperativity results saved to {output_file}")


def main():
    """Main execution function."""
    # Read myths from JSON
    print(f"Reading myths from {input_file}...")
    myths_by_agent = read_myths_from_json(input_file)

    print(f"Found {len(myths_by_agent)} agents")
    for agent_id, rounds in myths_by_agent.items():
        print(f"  {agent_id}: {len(rounds)} rounds")

    # Analyze cooperativity
    print("\nAnalyzing cooperativity...")
    cooperativity_scores = analyze_cooperativity(myths_by_agent)

    # Print summary
    print_cooperativity_summary(cooperativity_scores)

    # Save results
    save_results_to_json(cooperativity_scores, output_file=json_output_file)

    # Visualize
    print("\nGenerating visualization...")
    visualize_cooperativity(cooperativity_scores, output_file=plot_output_file)

    print("\n" + "="*80)
    print("Analysis complete!")
    print("="*80)


if __name__ == '__main__':
    # Check if running from shell script (environment variables available)
    input_file = os.environ.get('ANALYSIS_INPUT_FILE', '/Users/ivar/Desktop/current_projects/AI_projects/test_config_modular_llm/data/json/model_comparison/model_comparison_000_gpt-4o-mini_neutral_game_myth.json')
    base_output_dir = os.environ.get('ANALYSIS_OUTPUT_DIR', '/Users/ivar/Desktop/current_projects/AI_projects/test_config_modular_llm/data/plots/model_comparison/gpt-4o-mini')
    task_name = os.environ.get('ANALYSIS_TASK_NAME', 'game_myth')

    # Output files
    json_output_file = f'{base_output_dir}/cooperativity_results.json'
    plot_output_file = f'{base_output_dir}/cooperativity_analysis.png'

    main()


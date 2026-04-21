"""
Word Chain Evolution Analysis

This script analyzes the evolution of keywords in myths across generations.
It extracts key words from each myth text and tracks their evolution through generations.
"""

import json
import re
import os
from collections import Counter, defaultdict
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


def extract_keywords(text: str, top_n: int) -> List[Tuple[str, int]]:
    """
    Extract top keywords from text based on frequency.

    Args:
        text: Input text
        top_n: Number of top keywords to return

    Returns:
        List of (keyword, frequency) tuples
    """
    words = tokenize_and_clean(text)
    freq_dist = Counter(words)
    return freq_dist.most_common(top_n)


def read_myths_from_json(filepath: str) -> Dict[str, Dict[int, Dict[str, str]]]:
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

    print(f"Myths by agent: {myths_by_agent}")
    # Extract myths from conversation history
    for entry in data.get('conversation_history', []):
        round_num = entry.get('round')
        myths = entry.get('myths', {})

        for agent_id, myth_text in myths.items():
            myths_by_agent[agent_id][round_num] = myth_text

    return dict(myths_by_agent)


def analyze_keyword_evolution(myths_by_agent: Dict[str, Dict[int, str]],
                              top_n: int) -> Dict[str, Dict[int, List[Tuple[str, int]]]]:
    """
    Tracks keyword evolution across rounds for each agent.
    Tracks the frequency of each keyword in each round.

    Args:
        myths_by_agent: Dictionary mapping agent_id -> round -> myth_text
        top_n: Number of top keywords to extract per myth

    Returns:
        Dictionary mapping agent_id -> round -> [(keyword, frequency)]
    """
    evolution = {}

    for agent_id, rounds in myths_by_agent.items():
        evolution[agent_id] = {}
        for round_num, myth_text in sorted(rounds.items()):
            keywords = extract_keywords(myth_text, top_n)
            evolution[agent_id][round_num] = keywords

    return evolution


def calculate_keyword_stability(evolution: Dict[str, Dict[int, List[Tuple[str, int]]]]) -> Dict[str, Dict[str, int]]:
    """
    Counts how many times each keyword appears across all rounds (stability).

    Args:
        evolution: Keyword evolution data

    Returns:
        Dictionary mapping agent_id -> keyword -> appearance_count
    """
    stability = {}

    for agent_id, rounds in evolution.items():
        keyword_appearances = defaultdict(int)

        for round_num, keywords in rounds.items():
            for keyword, freq in keywords:
                keyword_appearances[keyword] += 1

        stability[agent_id] = dict(keyword_appearances)

    return stability


def find_most_frequent_keywords(evolution: Dict[str, Dict[int, List[Tuple[str, int]]]]) -> Dict[str, List[Tuple[str, int]]]:
    """
    Find the most frequent keywords overall (summed across all rounds).

    Args:
        evolution: Keyword evolution data

    Returns:
        Dictionary mapping agent_id -> [(keyword, total_frequency)]
    """
    most_frequent = {}

    for agent_id, rounds in evolution.items():
        total_freq = defaultdict(int)

        for round_num, keywords in rounds.items():
            for keyword, freq in keywords:
                total_freq[keyword] += freq

        # Sort by frequency
        sorted_keywords = sorted(total_freq.items(), key=lambda x: x[1], reverse=True)
        most_frequent[agent_id] = sorted_keywords

    return most_frequent


def visualize_keyword_evolution(evolution: Dict[str, Dict[int, List[Tuple[str, int]]]],
                                output_file: str):
    """
    Visualize keyword evolution through generations using heatmaps.

    Args:
        evolution: Keyword evolution data
        output_file: Output file path for the plot
    """
    fig = plt.figure(figsize=(16, 10))

    for idx, (agent_id, rounds) in enumerate(sorted(evolution.items())):
        # Select top keywords by total frequency
        keyword_totals = defaultdict(int)
        for keywords in rounds.values():
            for keyword, freq in keywords:
                keyword_totals[keyword] += freq

        top_keywords = sorted(keyword_totals.items(), key=lambda x: x[1], reverse=True)[:15]
        selected_keywords = [kw for kw, _ in top_keywords]

        # Build frequency matrix
        round_nums = sorted(rounds.keys())
        freq_matrix = np.zeros((len(selected_keywords), len(round_nums)))

        for i, keyword in enumerate(selected_keywords):
            for j, round_num in enumerate(round_nums):
                keyword_dict = dict(rounds[round_num])
                freq_matrix[i, j] = keyword_dict.get(keyword, 0)

        # Create heatmap
        ax = plt.subplot(2, 2, idx*2 + 1)
        im = ax.imshow(freq_matrix, aspect='auto', cmap='YlOrRd', interpolation='nearest')

        ax.set_xticks(range(len(round_nums)))
        ax.set_xticklabels(round_nums, fontsize=9)
        ax.set_yticks(range(len(selected_keywords)))
        ax.set_yticklabels(selected_keywords, fontsize=10)

        ax.set_xlabel('Round (Generation)', fontsize=11, fontweight='bold')
        ax.set_ylabel('Keywords', fontsize=11, fontweight='bold')
        ax.set_title(f'{agent_id}: Keyword Frequency Heatmap', fontsize=12, fontweight='bold')

        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Frequency', rotation=270, labelpad=20)

        # Create line plot for temporal patterns
        ax2 = plt.subplot(2, 2, idx*2 + 2)

        # Plot only the most interesting keywords (those with variation)
        variances = np.var(freq_matrix, axis=1)
        top_variance_idx = np.argsort(variances)[-6:]  # Top 6 most variable

        colors = plt.cm.tab10(np.linspace(0, 1, len(top_variance_idx)))

        for plot_idx, i in enumerate(top_variance_idx):
            keyword = selected_keywords[i]
            ax2.plot(round_nums, freq_matrix[i, :], marker='o', label=keyword,
                    linewidth=2.5, markersize=6, color=colors[plot_idx], alpha=0.8)

        ax2.set_xlabel('Round (Generation)', fontsize=11, fontweight='bold')
        ax2.set_ylabel('Keyword Frequency', fontsize=11, fontweight='bold')
        ax2.set_title(f'{agent_id}: Most Dynamic Keywords', fontsize=12, fontweight='bold')
        ax2.legend(loc='best', fontsize=9, framealpha=0.9)
        ax2.grid(True, alpha=0.3, linestyle='--')
        ax2.set_xlim(round_nums[0]-0.5, round_nums[-1]+0.5)

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Visualization saved to {output_file}")


def create_narrative_arc_visualization(evolution: Dict[str, Dict[int, List[Tuple[str, int]]]],
                                       output_file: str):
    """
    Create a narrative arc visualization showing thematic shifts.

    Args:
        evolution: Keyword evolution data
        output_file: Output file path
    """
    fig, axes = plt.subplots(2, 1, figsize=(16, 10), sharex=True)

    # Define thematic categories
    positive_words = {'trust', 'cooperation', 'harmony', 'bond', 'golden', 'gift', 'prosperity', 'reciprocity'}
    negative_words = {'despair', 'madness', 'scream', 'torment', 'exploitation', 'descent', 'refusal', 'sanity'}
    closure_words = {'final', 'closure', 'completion', 'farewell', 'goodbye', 'silence', 'end'}

    for idx, (agent_id, rounds) in enumerate(sorted(evolution.items())):
        ax = axes[idx]
        round_nums = sorted(rounds.keys())

        # Calculate sentiment scores per round
        positive_scores = []
        negative_scores = []
        closure_scores = []

        for round_num in round_nums:
            keywords = dict(rounds[round_num])

            pos_score = sum(freq for word, freq in keywords.items() if word in positive_words)
            neg_score = sum(freq for word, freq in keywords.items() if word in negative_words)
            close_score = sum(freq for word, freq in keywords.items() if word in closure_words)

            positive_scores.append(pos_score)
            negative_scores.append(neg_score)
            closure_scores.append(close_score)

        # Plot
        ax.plot(round_nums, positive_scores, marker='o', linewidth=3, markersize=8,
                label='Positive/Cooperative', color='#2ecc71', alpha=0.8)
        ax.plot(round_nums, negative_scores, marker='s', linewidth=3, markersize=8,
                label='Negative/Distress', color='#e74c3c', alpha=0.8)
        ax.plot(round_nums, closure_scores, marker='^', linewidth=3, markersize=8,
                label='Closure/Ending', color='#9b59b6', alpha=0.8)

        ax.fill_between(round_nums, positive_scores, alpha=0.2, color='#2ecc71')
        ax.fill_between(round_nums, negative_scores, alpha=0.2, color='#e74c3c')
        ax.fill_between(round_nums, closure_scores, alpha=0.2, color='#9b59b6')

        ax.set_ylabel('Thematic Frequency', fontsize=12, fontweight='bold')
        ax.set_title(f'{agent_id}: Narrative Thematic Evolution', fontsize=13, fontweight='bold')
        ax.legend(loc='best', fontsize=10, framealpha=0.95)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_xlim(round_nums[0]-0.5, round_nums[-1]+0.5)

    axes[1].set_xlabel('Round (Generation)', fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Narrative arc visualization saved to {output_file}")


def create_liwc_visualization(myths_by_agent: Dict[str, Dict[int, str]],
                              output_file: str):
    """
    Create LIWC category analysis visualization.

    Args:
        myths_by_agent: Dictionary mapping agent_id -> round -> myth_text
        output_file: Output file path
    """
    # Define LIWC categories based on the dictionary
    liwc_categories = {
        'Positive Emotion': {
            'words': {'trust', 'cooperation', 'harmony', 'bond', 'golden', 'gift', 'prosperity',
                     'reciprocity', 'peace', 'beloved', 'cherish', 'comfort', 'delight', 'joy',
                     'love', 'wonderful', 'gracious', 'grateful', 'hope', 'pleasant', 'beautiful',
                     'blessed', 'caring', 'compassion', 'generous', 'generosity', 'kindness'},
            'color': '#2ecc71'
        },
        'Negative Emotion': {
            'words': {'despair', 'madness', 'scream', 'torment', 'exploitation', 'descent',
                     'refusal', 'distress', 'fear', 'anxiety', 'anger', 'hatred', 'suffering',
                     'pain', 'agony', 'anguish', 'misery', 'sorrow', 'grief', 'devastated',
                     'disappointed', 'frustrated', 'unhappy', 'terrible', 'horrible'},
            'color': '#e74c3c'
        },
        'Cognitive': {
            'words': {'understand', 'realize', 'recognize', 'know', 'think', 'believe',
                     'consider', 'comprehend', 'awareness', 'discover', 'learn', 'perceive',
                     'wisdom', 'wise', 'thought', 'idea', 'reason', 'logic'},
            'color': '#3498db'
        },
        'Certainty': {
            'words': {'always', 'never', 'must', 'absolute', 'definite', 'undoubtedly',
                     'clearly', 'certain', 'sure', 'inevitable', 'eternal', 'forever'},
            'color': '#9b59b6'
        },
        'Tentativeness': {
            'words': {'maybe', 'perhaps', 'possibly', 'might', 'probably', 'seem', 'appear',
                     'could', 'would', 'should', 'may'},
            'color': '#95a5a6'
        },
        'Religion': {
            'words': {'god', 'gods', 'divine', 'sacred', 'holy', 'faith', 'prayer', 'blessing',
                     'worship', 'spiritual', 'heaven', 'soul', 'spirit', 'mystical', 'oracle'},
            'color': '#f39c12'
        },
        'Death': {
            'words': {'death', 'die', 'dying', 'dead', 'mortal', 'demise', 'perish',
                     'destruction', 'end', 'ended', 'ending'},
            'color': '#34495e'
        }
    }

    fig, axes = plt.subplots(len(myths_by_agent), 1, figsize=(18, 6 * len(myths_by_agent)), sharex=True)
    if len(myths_by_agent) == 1:
        axes = [axes]

    for agent_idx, (agent_id, rounds) in enumerate(sorted(myths_by_agent.items())):
        ax = axes[agent_idx]
        round_nums = sorted(rounds.keys())

        # Calculate category scores for each round
        category_scores = {cat: [] for cat in liwc_categories.keys()}

        for round_num in round_nums:
            myth_text = rounds[round_num].lower()
            words = tokenize_and_clean(myth_text)
            total_words = len(words)

            if total_words == 0:
                for cat in liwc_categories.keys():
                    category_scores[cat].append(0)
                continue

            for cat_name, cat_info in liwc_categories.items():
                cat_words = cat_info['words']
                count = sum(1 for word in words if word in cat_words)
                # Normalize by total words (percentage)
                percentage = (count / total_words) * 100 if total_words > 0 else 0
                category_scores[cat_name].append(percentage)

        # Plot each category
        for cat_name, cat_info in liwc_categories.items():
            scores = category_scores[cat_name]
            ax.plot(round_nums, scores, marker='o', linewidth=2.5, markersize=7,
                   label=cat_name, color=cat_info['color'], alpha=0.85)
            ax.fill_between(round_nums, scores, alpha=0.15, color=cat_info['color'])

        ax.set_ylabel('Category Frequency (%)', fontsize=12, fontweight='bold')
        ax.set_title(f'{agent_id}: LIWC Category Evolution', fontsize=14, fontweight='bold')
        ax.legend(loc='best', fontsize=10, framealpha=0.95, ncol=2)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_xlim(round_nums[0]-0.5, round_nums[-1]+0.5)
        ax.set_ylim(bottom=0)

    axes[-1].set_xlabel('Round (Generation)', fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"LIWC visualization saved to {output_file}")


def create_liwc_heatmap(myths_by_agent: Dict[str, Dict[int, str]],
                        output_file: str = 'liwc_heatmap.png'):
    """
    Create a heatmap showing LIWC categories across rounds.

    Args:
        myths_by_agent: Dictionary mapping agent_id -> round -> myth_text
        output_file: Output file path
    """
    liwc_categories = {
        'Positive Emotion': {'trust', 'cooperation', 'harmony', 'bond', 'golden', 'gift', 'prosperity',
                            'reciprocity', 'peace', 'beloved', 'cherish', 'comfort', 'delight', 'joy',
                            'love', 'wonderful', 'gracious', 'grateful', 'hope', 'pleasant', 'beautiful',
                            'blessed', 'caring', 'compassion', 'generous', 'generosity', 'kindness'},
        'Negative Emotion': {'despair', 'madness', 'scream', 'torment', 'exploitation', 'descent',
                            'refusal', 'distress', 'fear', 'anxiety', 'anger', 'hatred', 'suffering',
                            'pain', 'agony', 'anguish', 'misery', 'sorrow', 'grief', 'devastated',
                            'disappointed', 'frustrated', 'unhappy', 'terrible', 'horrible'},
        'Cognitive': {'understand', 'realize', 'recognize', 'know', 'think', 'believe',
                     'consider', 'comprehend', 'awareness', 'discover', 'learn', 'perceive',
                     'wisdom', 'wise', 'thought', 'idea', 'reason', 'logic'},
        'Certainty': {'always', 'never', 'must', 'absolute', 'definite', 'undoubtedly',
                     'clearly', 'certain', 'sure', 'inevitable', 'eternal', 'forever'},
        'Tentativeness': {'maybe', 'perhaps', 'possibly', 'might', 'probably', 'seem', 'appear',
                         'could', 'would', 'should', 'may'},
        'Religion': {'god', 'gods', 'divine', 'sacred', 'holy', 'faith', 'prayer', 'blessing',
                    'worship', 'spiritual', 'heaven', 'soul', 'spirit', 'mystical', 'oracle'},
        'Death': {'death', 'die', 'dying', 'dead', 'mortal', 'demise', 'perish',
                 'destruction', 'end', 'ended', 'ending'}
    }

    fig, axes = plt.subplots(1, len(myths_by_agent), figsize=(12 * len(myths_by_agent), 8))
    if len(myths_by_agent) == 1:
        axes = [axes]

    for agent_idx, (agent_id, rounds) in enumerate(sorted(myths_by_agent.items())):
        ax = axes[agent_idx]
        round_nums = sorted(rounds.keys())
        category_names = list(liwc_categories.keys())

        # Build matrix
        matrix = np.zeros((len(category_names), len(round_nums)))

        for round_idx, round_num in enumerate(round_nums):
            myth_text = rounds[round_num].lower()
            words = tokenize_and_clean(myth_text)
            total_words = len(words)

            for cat_idx, (cat_name, cat_words) in enumerate(liwc_categories.items()):
                count = sum(1 for word in words if word in cat_words)
                percentage = (count / total_words) * 100 if total_words > 0 else 0
                matrix[cat_idx, round_idx] = percentage

        # Create heatmap
        im = ax.imshow(matrix, aspect='auto', cmap='RdYlGn', interpolation='nearest', vmin=0, vmax=10)

        ax.set_xticks(range(len(round_nums)))
        ax.set_xticklabels(round_nums, fontsize=10)
        ax.set_yticks(range(len(category_names)))
        ax.set_yticklabels(category_names, fontsize=11)

        ax.set_xlabel('Round (Generation)', fontsize=12, fontweight='bold')
        ax.set_ylabel('LIWC Categories', fontsize=12, fontweight='bold')
        ax.set_title(f'{agent_id}: LIWC Category Heatmap', fontsize=13, fontweight='bold')

        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Frequency (%)', rotation=270, labelpad=20, fontsize=11)

        # Add values to cells for clarity
        for i in range(len(category_names)):
            for j in range(len(round_nums)):
                if matrix[i, j] > 0:
                    text = ax.text(j, i, f'{matrix[i, j]:.1f}',
                                 ha="center", va="center", color="black", fontsize=7)

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"LIWC heatmap saved to {output_file}")


def print_analysis_results(evolution: Dict[str, Dict[int, List[Tuple[str, int]]]],
                           stability: Dict[str, Dict[str, int]],
                           most_frequent: Dict[str, List[Tuple[str, int]]]):
    """
    Print analysis results to console.

    Args:
        evolution: Keyword evolution data
        stability: Keyword stability data
        most_frequent: Most frequent keywords data
    """
    print("\n" + "="*80)
    print("WORD CHAIN EVOLUTION ANALYSIS")
    print("="*80)

    for agent_id in sorted(evolution.keys()):
        print(f"\n{'─'*80}")
        print(f"AGENT: {agent_id}")
        print(f"{'─'*80}")

        # Most frequent keywords
        print(f"\nMost Frequent Keywords (across all rounds):")
        for keyword, freq in most_frequent[agent_id][:10]:
            print(f"  {keyword:20} {freq:4} occurrences")

        # Most stable keywords (appear in most rounds)
        print(f"\nMost Stable Keywords (present in most rounds):")
        stable_keywords = sorted(stability[agent_id].items(), key=lambda x: x[1], reverse=True)
        for keyword, appearances in stable_keywords[:10]:
            print(f"  {keyword:20} {appearances:2} rounds")

        # Round-by-round evolution
        print(f"\nKeyword Evolution by Round:")
        for round_num in sorted(evolution[agent_id].keys()):
            print(f"\n  Round {round_num}:")
            for keyword, freq in evolution[agent_id][round_num][:5]:
                print(f"    {keyword:20} {freq:4}")


def save_results_to_json(evolution: Dict[str, Dict[int, List[Tuple[str, int]]]],
                         stability: Dict[str, Dict[str, int]],
                         most_frequent: Dict[str, List[Tuple[str, int]]],
                         output_file: str = 'word_chain_results.json'):
    """
    Save analysis results to JSON file.

    Args:
        evolution: Keyword evolution data
        stability: Keyword stability data
        most_frequent: Most frequent keywords data
        output_file: Output file path
    """
    results = {
        'evolution': evolution,
        'stability': stability,
        'most_frequent': most_frequent
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Results saved to {output_file}")

def main():
    """Main execution function."""
    # Read myths from JSON
    print(f"Reading myths from {input_file}...")
    myths_by_agent = read_myths_from_json(input_file)

    print(f"Found {len(myths_by_agent)} agents")
    for agent_id, rounds in myths_by_agent.items():
        print(f"  {agent_id}: {len(rounds)} rounds")

    # Analyze keyword evolution
    print("\nAnalyzing keyword evolution...")
    evolution = analyze_keyword_evolution(myths_by_agent, top_n=top_n)

    # Calculate stability
    print("Calculating keyword stability...")
    stability = calculate_keyword_stability(evolution)

    # Find most frequent keywords
    print("Finding most frequent keywords...")
    most_frequent = find_most_frequent_keywords(evolution)

    # Print results
    print_analysis_results(evolution, stability, most_frequent)

    # Save results
    save_results_to_json(evolution, stability, most_frequent, output_file=output_file)

    # Visualize
    print("\nGenerating visualizations...")
    visualize_keyword_evolution(evolution, output_file=word_chain_plot_file)
    create_narrative_arc_visualization(evolution, output_file=narrative_arc_file)
    create_liwc_visualization(myths_by_agent, output_file=liwc_analysis_file)
    create_liwc_heatmap(myths_by_agent, output_file=liwc_heatmap_file)

    print("\n" + "="*80)
    print("Analysis complete!")
    print("="*80)

if __name__ == '__main__':
    # Check if running from shell script (environment variables available)
    input_file = os.environ.get('ANALYSIS_INPUT_FILE', '/Users/ivar/Desktop/current_projects/AI_projects/test_config_modular_llm/data/json/model_comparison/model_comparison_000_gpt-4o-mini_neutral_game_myth.json')
    base_output_dir = os.environ.get('ANALYSIS_OUTPUT_DIR', '/Users/ivar/Desktop/current_projects/AI_projects/test_config_modular_llm/data/plots/model_comparison/gpt-4o-mini')
    task_name = os.environ.get('ANALYSIS_TASK_NAME', 'game_myth')

    # Configuration variables
    output_file = f'{base_output_dir}/word_chain_results.json'
    top_n = 5

    # Image output files
    word_chain_plot_file = f'{base_output_dir}/word_chain_evolution.png'
    narrative_arc_file = f'{base_output_dir}/narrative_arc.png'
    liwc_analysis_file = f'{base_output_dir}/liwc_analysis.png'
    liwc_heatmap_file = f'{base_output_dir}/liwc_heatmap.png'

    main()

"""
Additional N-gram Analysis: Innovation Rate Plot and POS Pattern Examples
Generates innovation rate visualization and extracts POS pattern examples from multiple rounds
"""

import json
import os
import ast
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
from typing import Dict, List, Tuple

# Import functions from n_gram_sentence_structure
from n_gram_sentence_structure import (
    full_sentence_structure_analysis,
    calculate_structural_innovation,
    extract_myths_by_round,
    extract_sentences,
    get_pos_pattern
)

# ============================================================================
# DATA LOADING
# ============================================================================

def load_or_generate_evolution_data(input_json_filepath, output_dir):
    """Load evolution data from JSON or generate it if missing"""
    
    # Check if sentence_structure_analysis.json exists in output directory
    analysis_json_path = os.path.join(output_dir, 'sentence_structure_analysis.json')
    
    if os.path.exists(analysis_json_path):
        print(f"Loading existing analysis data from {analysis_json_path}")
        with open(analysis_json_path, 'r') as f:
            evolution_data = json.load(f)
        # Convert string keys back to tuples for patterns
        for metric_type in evolution_data.keys():
            for agent_id in evolution_data[metric_type].keys():
                for item in evolution_data[metric_type][agent_id]:
                    if 'patterns' in item:
                        # Convert string keys back to tuples
                        patterns_dict = {}
                        for key_str, count in item['patterns'].items():
                            # Parse tuple string like "('DET', 'NOUN', 'VERB')"
                            try:
                                pattern_tuple = ast.literal_eval(key_str)
                                if isinstance(pattern_tuple, tuple):
                                    patterns_dict[pattern_tuple] = count
                                else:
                                    # If not a tuple, convert to tuple
                                    patterns_dict[tuple(pattern_tuple)] = count
                            except:
                                # If all else fails, keep as string (shouldn't happen with proper JSON)
                                patterns_dict[key_str] = count
                        item['patterns'] = patterns_dict
        return evolution_data
    else:
        print(f"Analysis JSON not found. Generating from {input_json_filepath}")
        evolution_data = full_sentence_structure_analysis(input_json_filepath, output_dir)
        return evolution_data

# ============================================================================
# INNOVATION RATE PLOT
# ============================================================================

def plot_innovation_rate(evolution_data, output_dir):
    """Create innovation rate plot for both agents"""
    
    fig, ax = plt.subplots(1, 1, figsize=(12, 6))
    
    agent_ids = list(evolution_data['pos_patterns'].keys())
    colors = ['blue', 'red']
    
    all_innovation_data = {}
    
    for idx, agent_id in enumerate(agent_ids):
        innovation_timeline = calculate_structural_innovation(evolution_data, agent_id, 'pos_patterns')
        
        if innovation_timeline:
            rounds = [item['round'] for item in innovation_timeline]
            innovation_rates = [item['innovation_rate'] * 100 for item in innovation_timeline]  # Convert to percentage
            
            # Calculate average
            avg_innovation = np.mean(innovation_rates)
            
            # Plot line
            ax.plot(rounds, innovation_rates, 
                   marker='o', label=f'{agent_id}', 
                   linewidth=2, markersize=4, color=colors[idx % len(colors)])
            
            # Plot average line
            ax.axhline(y=avg_innovation, 
                      color=colors[idx % len(colors)], 
                      linestyle='--', 
                      alpha=0.5,
                      label=f'{agent_id} Avg ({avg_innovation:.1f}%)')
            
            all_innovation_data[agent_id] = {
                'rounds': rounds,
                'rates': innovation_rates,
                'average': avg_innovation
            }
    
    ax.set_xlabel('Round', fontsize=12)
    ax.set_ylabel('Innovation Rate (%)', fontsize=12)
    ax.set_title('Structural Innovation Rate Over Time', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    output_file = os.path.join(output_dir, 'innovation_rate_over_time.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Innovation rate plot saved to {output_file}")
    plt.close()
    
    return all_innovation_data

# ============================================================================
# PATTERN EXAMPLES EXTRACTION
# ============================================================================

def extract_pattern_examples(input_json_filepath, selected_rounds, output_file):
    """Extract POS pattern examples from selected rounds with actual sentences"""
    
    print(f"\nExtracting pattern examples from rounds: {selected_rounds}")
    
    # Load myths by round
    myths_by_round = extract_myths_by_round(input_json_filepath)
    
    # Get all available rounds
    all_rounds = sorted(myths_by_round.keys())
    
    # Filter to only selected rounds that exist
    rounds_to_process = [r for r in selected_rounds if r in all_rounds]
    
    if not rounds_to_process:
        print(f"Warning: None of the selected rounds {selected_rounds} exist in the data.")
        print(f"Available rounds: {all_rounds[:10]}... (showing first 10)")
        return
    
    # Structure: {round: {agent_id: {pattern: [sentences]}}}
    pattern_examples = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    
    for round_num in rounds_to_process:
        if round_num not in myths_by_round:
            continue
            
        for agent_id, myth_text in myths_by_round[round_num].items():
            sentences = extract_sentences(myth_text)
            
            for sentence in sentences:
                try:
                    pos_pattern = get_pos_pattern(sentence)
                    pattern_examples[round_num][agent_id][pos_pattern].append(sentence)
                except Exception as e:
                    # Skip sentences that can't be processed
                    continue
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("POS PATTERN EXAMPLES FROM MULTIPLE ROUNDS\n")
        f.write("=" * 80 + "\n\n")
        f.write("This file shows examples of Part-of-Speech (POS) patterns from selected rounds.\n")
        f.write("Each pattern shows the sequence of POS tags and example sentences that use it.\n\n")
        
        for round_num in sorted(rounds_to_process):
            if round_num not in pattern_examples:
                continue
                
            f.write("\n" + "=" * 80 + "\n")
            f.write(f"ROUND {round_num}\n")
            f.write("=" * 80 + "\n\n")
            
            for agent_id in sorted(pattern_examples[round_num].keys()):
                f.write(f"\n{agent_id}:\n")
                f.write("-" * 80 + "\n\n")
                
                # Get patterns for this agent in this round
                patterns = pattern_examples[round_num][agent_id]
                
                # Sort by frequency (number of sentences using this pattern)
                sorted_patterns = sorted(patterns.items(), key=lambda x: len(x[1]), reverse=True)
                
                # Show top 10 most frequent patterns
                for pattern, sentences in sorted_patterns[:10]:
                    pattern_str = str(pattern)
                    frequency = len(sentences)
                    
                    f.write(f"Pattern: {pattern_str}\n")
                    f.write(f"Frequency: {frequency} sentence(s)\n")
                    f.write("Example sentences:\n")
                    
                    # Show 2-3 example sentences
                    for sentence in sentences[:3]:
                        f.write(f'  - "{sentence}"\n')
                    
                    f.write("\n")
    
    print(f"✓ Pattern examples saved to {output_file}")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    
    # Get environment variables
    input_file = os.environ.get('ANALYSIS_INPUT_FILE')
    base_output_dir = os.environ.get('ANALYSIS_OUTPUT_DIR')
    task_name = os.environ.get('ANALYSIS_TASK_NAME', 'game_myth')
    
    if not input_file or not base_output_dir:
        print("Error: ANALYSIS_INPUT_FILE and ANALYSIS_OUTPUT_DIR must be set")
        print("Usage: Set environment variables and run this script")
        return
    
    # Create output directory if it doesn't exist
    os.makedirs(base_output_dir, exist_ok=True)
    
    print("\n" + "=" * 80)
    print("N-GRAM EXTRA ANALYSIS: INNOVATION RATE & PATTERN EXAMPLES")
    print("=" * 80)
    print(f"Input file: {input_file}")
    print(f"Output directory: {base_output_dir}")
    print("=" * 80 + "\n")
    
    # Step 1: Load or generate evolution data
    print("[1/3] Loading or generating evolution data...")
    evolution_data = load_or_generate_evolution_data(input_file, base_output_dir)
    print("  ✓ Evolution data loaded\n")
    
    # Step 2: Create innovation rate plot
    print("[2/3] Creating innovation rate plot...")
    innovation_data = plot_innovation_rate(evolution_data, base_output_dir)
    print("  ✓ Innovation rate plot created\n")
    
    # Step 3: Extract pattern examples
    print("[3/3] Extracting POS pattern examples...")
    
    # Determine which rounds to show (every 5 rounds, or first, middle, last)
    # First, get total number of rounds
    myths_by_round = extract_myths_by_round(input_file)
    all_rounds = sorted(myths_by_round.keys())
    total_rounds = len(all_rounds)
    
    if total_rounds <= 10:
        # If few rounds, show all
        selected_rounds = all_rounds
    elif total_rounds <= 30:
        # Show every 5 rounds
        selected_rounds = [r for r in all_rounds if r % 5 == 1 or r == all_rounds[0] or r == all_rounds[-1]]
        # Ensure first and last are included
        if all_rounds[0] not in selected_rounds:
            selected_rounds.insert(0, all_rounds[0])
        if all_rounds[-1] not in selected_rounds:
            selected_rounds.append(all_rounds[-1])
        selected_rounds = sorted(set(selected_rounds))
    else:
        # Show first, every 5th, and last
        selected_rounds = [all_rounds[0]]  # First round
        # Every 5 rounds
        selected_rounds.extend([r for r in all_rounds[1:-1] if r % 5 == 1])
        selected_rounds.append(all_rounds[-1])  # Last round
        selected_rounds = sorted(set(selected_rounds))
    
    output_txt_file = os.path.join(base_output_dir, 'pos_pattern_examples.txt')
    extract_pattern_examples(input_file, selected_rounds, output_txt_file)
    print("  ✓ Pattern examples extracted\n")
    
    print("=" * 80)
    print("ANALYSIS COMPLETE!")
    print("=" * 80)
    print(f"\nOutputs saved to: {base_output_dir}")
    print("  1. innovation_rate_over_time.png")
    print("  2. pos_pattern_examples.txt")
    print("=" * 80)

if __name__ == "__main__":
    main()


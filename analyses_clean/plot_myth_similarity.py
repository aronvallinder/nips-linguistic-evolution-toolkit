import json
import matplotlib.pyplot as plt
import numpy as np
import os
from collections import defaultdict

def create_plots(results, output_dir):
    """Create all plots from similarity results."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    dimensions = ['thematic_similarity', 'character_similarity', 'narrative_similarity',
                  'symbolic_similarity', 'conceptual_similarity', 'overall_similarity']
    dimension_labels = ['Thematic', 'Character', 'Narrative', 'Symbolic', 'Conceptual', 'Overall']

    # ============================================================================
    # PLOT 1: Between-Rounds Line Charts (Similarity over rounds per agent)
    # ============================================================================
    if results.get('between_rounds'):
        print("\n" + "=" * 80)
        print("GENERATING BETWEEN-ROUNDS PLOTS")
        print("=" * 80)
        
        # Group by agent
        agent_data = defaultdict(lambda: {'rounds': [], 'scores': {dim: [] for dim in dimensions}})
        
        for comp in results['between_rounds']:
            agent_id = comp['agent_id']
            round2 = comp['round2']
            similarity = comp['similarity']
            
            agent_data[agent_id]['rounds'].append(round2)
            for dim in dimensions:
                agent_data[agent_id]['scores'][dim].append(similarity[dim])
        
        # Create subplots: one per agent, all dimensions
        num_agents = len(agent_data)
        fig, axes = plt.subplots(num_agents, 1, figsize=(12, 6 * num_agents))
        if num_agents == 1:
            axes = [axes]
        
        for idx, (agent_id, data) in enumerate(sorted(agent_data.items())):
            ax = axes[idx]
            
            for dim, label in zip(dimensions, dimension_labels):
                ax.plot(data['rounds'], data['scores'][dim], marker='o', label=label, linewidth=2)
            
            ax.set_xlabel('Round', fontsize=12)
            ax.set_ylabel('Similarity Score (0-10)', fontsize=12)
            ax.set_title(f'{agent_id}: Similarity to Round 1 Over Time', fontsize=14, fontweight='bold')
            ax.legend(loc='best', ncol=3)
            ax.grid(True, alpha=0.3)
            ax.set_ylim(0, 10)
            ax.set_xticks(data['rounds'])
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/between_rounds_similarity.png', dpi=300, bbox_inches='tight')
        print(f"Saved: {output_dir}/between_rounds_similarity.png")
        plt.close()

    # ============================================================================
    # PLOT 2: Within-Round Bar Charts (Average similarity per round)
    # ============================================================================
    if results.get('within_round'):
        print("\n" + "=" * 80)
        print("GENERATING WITHIN-ROUND PLOTS")
        print("=" * 80)
        
        # Group by round
        round_data = defaultdict(lambda: {dim: [] for dim in dimensions})
        rounds = []
        
        for comp in results['within_round']:
            round_num = comp['round']
            similarity = comp['similarity']
            
            if round_num not in rounds:
                rounds.append(round_num)
            
            for dim in dimensions:
                round_data[round_num][dim].append(similarity[dim])
        
        rounds = sorted(rounds)
        
        # Calculate averages per round
        avg_scores = {dim: [] for dim in dimensions}
        for round_num in rounds:
            for dim in dimensions:
                avg = np.mean(round_data[round_num][dim])
                avg_scores[dim].append(avg)
        
        # Create bar chart
        x = np.arange(len(rounds))
        width = 0.13  # Width of bars
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        for i, (dim, label) in enumerate(zip(dimensions, dimension_labels)):
            offset = (i - len(dimensions)/2) * width + width/2
            ax.bar(x + offset, avg_scores[dim], width, label=label, alpha=0.8)
        
        ax.set_xlabel('Round', fontsize=12)
        ax.set_ylabel('Average Similarity Score (0-10)', fontsize=12)
        ax.set_title('Average Inter-Agent Similarity Per Round (All Dimensions)', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(rounds)
        ax.legend(loc='best', ncol=3)
        ax.grid(True, alpha=0.3, axis='y')
        ax.set_ylim(0, 10)
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/within_round_similarity.png', dpi=300, bbox_inches='tight')
        print(f"Saved: {output_dir}/within_round_similarity.png")
        plt.close()

    # ============================================================================
    # PLOT 3: Heatmap - Between-Rounds Overall Similarity
    # ============================================================================
    if results.get('between_rounds'):
        # Create heatmap data: agent x round
        agent_list = sorted(set(comp['agent_id'] for comp in results['between_rounds']))
        round_list = sorted(set(comp['round2'] for comp in results['between_rounds']))
        
        heatmap_data = np.zeros((len(agent_list), len(round_list)))
        
        for comp in results['between_rounds']:
            agent_idx = agent_list.index(comp['agent_id'])
            round_idx = round_list.index(comp['round2'])
            heatmap_data[agent_idx, round_idx] = comp['similarity']['overall_similarity']
        
        fig, ax = plt.subplots(figsize=(10, 6))
        im = ax.imshow(heatmap_data, cmap='YlOrRd', aspect='auto', vmin=0, vmax=10)
        
        ax.set_xticks(np.arange(len(round_list)))
        ax.set_yticks(np.arange(len(agent_list)))
        ax.set_xticklabels(round_list)
        ax.set_yticklabels(agent_list)
        
        ax.set_xlabel('Round', fontsize=12)
        ax.set_ylabel('Agent', fontsize=12)
        ax.set_title('Overall Similarity to Round 1 (Heatmap)', fontsize=14, fontweight='bold')
        
        # Add text annotations
        for i in range(len(agent_list)):
            for j in range(len(round_list)):
                text = ax.text(j, i, f'{heatmap_data[i, j]:.1f}',
                              ha="center", va="center", color="black", fontsize=10)
        
        plt.colorbar(im, ax=ax, label='Similarity Score')
        plt.tight_layout()
        plt.savefig(f'{output_dir}/between_rounds_heatmap.png', dpi=300, bbox_inches='tight')
        print(f"Saved: {output_dir}/between_rounds_heatmap.png")
        plt.close()

    # ============================================================================
    # PLOT 4: Dimension Comparison - Box plots
    # ============================================================================
    if results.get('between_rounds') and results.get('within_round'):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        dimensions = ['thematic_similarity', 'character_similarity', 'narrative_similarity', 
                      'symbolic_similarity', 'conceptual_similarity', 'overall_similarity']
        dimension_labels = ['Thematic', 'Character', 'Narrative', 'Symbolic', 'Conceptual', 'Overall']
        
        # Between-rounds box plot
        between_scores = {dim: [] for dim in dimensions}
        for comp in results['between_rounds']:
            for dim in dimensions:
                between_scores[dim].append(comp['similarity'][dim])
        
        bp1 = ax1.boxplot([between_scores[dim] for dim in dimensions], 
                          labels=dimension_labels, patch_artist=True)
        ax1.set_ylabel('Similarity Score', fontsize=12)
        ax1.set_title('Between-Rounds: Score Distribution by Dimension', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='y')
        ax1.set_ylim(0, 10)
        
        # Within-round box plot
        within_scores = {dim: [] for dim in dimensions}
        for comp in results['within_round']:
            for dim in dimensions:
                within_scores[dim].append(comp['similarity'][dim])
        
        bp2 = ax2.boxplot([within_scores[dim] for dim in dimensions], 
                          labels=dimension_labels, patch_artist=True)
        ax2.set_ylabel('Similarity Score', fontsize=12)
        ax2.set_title('Within-Round: Score Distribution by Dimension', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')
        ax2.set_ylim(0, 10)
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/dimension_comparison_boxplots.png', dpi=300, bbox_inches='tight')
        print(f"Saved: {output_dir}/dimension_comparison_boxplots.png")
        plt.close()

    print("\n" + "=" * 80)
    print("ALL PLOTS GENERATED SUCCESSFULLY")
    print("=" * 80)

if __name__ == '__main__':
    # Check if running from shell script (environment variables available)
    base_output_dir = os.environ.get('ANALYSIS_OUTPUT_DIR', '/Users/ivar/Desktop/current_projects/AI_projects/test_config_modular_llm/data/plots/model_comparison/gpt-4o-mini/myth_similarity')
    task_name = os.environ.get('ANALYSIS_TASK_NAME', 'game_myth')

    # Configuration - input file is the output from myth_similarity.py
    input_file = f'{base_output_dir}/myth_similarity_results.json'
    output_dir = f'{base_output_dir}/similarity_plots'

    # Load results
    print(f"Loading results from {input_file}...")
    with open(input_file, 'r') as f:
        results = json.load(f)

    # Create plots
    create_plots(results, output_dir)
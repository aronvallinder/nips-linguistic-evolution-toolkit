import json
import numpy as np
import matplotlib.pyplot as plt
import os
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re

# Global model variable (loaded once)
model = None

def load_model(model_name='all-mpnet-base-v2'):
    """Load the embedding model."""
    global model
    if model is None:
        print("Loading model...")
        model = SentenceTransformer(model_name)
        print("Model loaded!\n")
    return model

def extract_aspects(myth):
    """Extract different aspects of the myth for dimensional analysis."""
    return {
        'full': myth,
    }

def calculate_dimensional_similarity(myth1, myth2, embedding_model):
    """Calculate similarity across multiple dimensions."""
    aspects1 = extract_aspects(myth1)
    aspects2 = extract_aspects(myth2)
    
    results = {}
    
    # Overall similarity
    emb1 = embedding_model.encode([aspects1['full']])[0]
    emb2 = embedding_model.encode([aspects2['full']])[0]
    results['overall'] = cosine_similarity(emb1.reshape(1, -1), emb2.reshape(1, -1))[0][0]
    
    return results

def analyze_similarities(data, embedding_model):
    """Analyze similarities between myths."""
    # Extract myths for each agent
    agent_myths = {'Agent_1': [], 'Agent_2': []}
    for entry in data['conversation_history']:
        for agent_id, myth in entry.get('myths', {}).items():
            agent_myths[agent_id].append((entry['round'], myth))

    # Store similarity data for plotting
    similarity_data = {'Agent_1': {'rounds': [], 'scores': []}, 
                       'Agent_2': {'rounds': [], 'scores': []}}

    # Analyze similarities
    print("=" * 80)
    print("MULTI-DIMENSIONAL SEMANTIC SIMILARITY (SOTA Embeddings)")
    print("=" * 80)

    for agent_id in ['Agent_1', 'Agent_2']:
        print(f"\n{agent_id}:")
        print("-" * 80)
        
        myths = agent_myths[agent_id]
        if not myths:
            continue
        first_round, first_myth = myths[0]
        
        for i in range(1, len(myths)):
            current_round, current_myth = myths[i]
            
            # Calculate dimensional similarities
            similarities = calculate_dimensional_similarity(first_myth, current_myth, embedding_model)
            
            # Store for plotting
            similarity_data[agent_id]['rounds'].append(current_round)
            similarity_data[agent_id]['scores'].append(similarities['overall'])
            
            print(f"\nRound 1 → {current_round}:")
            print(f"  Overall:    {similarities['overall']*10:.2f}/10 (cosine: {similarities['overall']:.4f})")

    print("\n" + "=" * 80)
    print("\nNote: Using all-mpnet-base-v2 (SOTA sentence embeddings, 768 dimensions)")
    print("Cosine similarity ranges from -1 to 1, scaled to 0-10 for readability")
    
    return similarity_data

def create_plots(similarity_data, output_dir):
    """Create and save plots."""
    print("\n" + "=" * 80)
    print("GENERATING PLOTS")
    print("=" * 80)

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Plot 1: Combined line chart - Both agents on same plot
    fig, ax = plt.subplots(figsize=(10, 6))
    for agent_id in ['Agent_1', 'Agent_2']:
        rounds = similarity_data[agent_id]['rounds']
        scores = [s * 10 for s in similarity_data[agent_id]['scores']]
        ax.plot(rounds, scores, marker='o', linewidth=2, markersize=8, label=agent_id)

    ax.set_xlabel('Round', fontsize=12)
    ax.set_ylabel('Similarity Score (0-10)', fontsize=12)
    ax.set_title('Similarity to Round 1 Over Time (Both Agents)', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 10)
    ax.legend()
    plt.tight_layout()
    plt.savefig(f'{output_dir}/similarity_combined.png', dpi=300, bbox_inches='tight')
    print(f"Saved: {output_dir}/similarity_combined.png")
    plt.close()

    # Plot 2: Heatmap - Similarity scores
    agent_list = ['Agent_1', 'Agent_2']
    round_list = similarity_data['Agent_1']['rounds']  # Assuming same rounds for both

    heatmap_data = np.zeros((len(agent_list), len(round_list)))
    for idx, agent_id in enumerate(agent_list):
        scores = [s * 10 for s in similarity_data[agent_id]['scores']]
        heatmap_data[idx, :] = scores

    fig, ax = plt.subplots(figsize=(10, 4))
    im = ax.imshow(heatmap_data, cmap='YlOrRd', aspect='auto', vmin=0, vmax=10)

    ax.set_xticks(np.arange(len(round_list)))
    ax.set_yticks(np.arange(len(agent_list)))
    ax.set_xticklabels(round_list)
    ax.set_yticklabels(agent_list)

    ax.set_xlabel('Round', fontsize=12)
    ax.set_ylabel('Agent', fontsize=12)
    ax.set_title('Similarity to Round 1 (Heatmap)', fontsize=14, fontweight='bold')

    # Add text annotations
    for i in range(len(agent_list)):
        for j in range(len(round_list)):
            text = ax.text(j, i, f'{heatmap_data[i, j]:.1f}',
                          ha="center", va="center", color="black", fontsize=10)

    plt.colorbar(im, ax=ax, label='Similarity Score (0-10)')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/similarity_heatmap.png', dpi=300, bbox_inches='tight')
    print(f"Saved: {output_dir}/similarity_heatmap.png")
    plt.close()

    print("\n" + "=" * 80)  
    print("ALL PLOTS GENERATED SUCCESSFULLY")
    print("=" * 80)

if __name__ == '__main__':
    # Check if running from shell script (environment variables available)
    input_file = os.environ.get('ANALYSIS_INPUT_FILE', '/Users/ivar/Desktop/current_projects/AI_projects/test_config_modular_llm/data/json/model_comparison/model_comparison_000_gpt-4o-mini_neutral_game_myth.json')
    base_output_dir = os.environ.get('ANALYSIS_OUTPUT_DIR', '/Users/ivar/Desktop/current_projects/AI_projects/test_config_modular_llm/data/plots/model_comparison/gpt-4o-mini/myth_similarity_embedding')
    task_name = os.environ.get('ANALYSIS_TASK_NAME', 'game_myth')

    # Configuration
    output_dir = f'{base_output_dir}/similarity_embedding'
    model_name = 'all-mpnet-base-v2'

    # Load data
    print(f"Loading simulation data from {input_file}...")
    with open(input_file, 'r') as f:
        data = json.load(f)
    # Load model
    embedding_model = load_model(model_name)
    # Analyze
    similarity_data = analyze_similarities(data, embedding_model)
    # Create plots
    create_plots(similarity_data, output_dir)
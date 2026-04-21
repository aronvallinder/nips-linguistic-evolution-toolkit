"""
Sentence Structure Evolution Analysis for Multi-Agent Myth Writing
Analyzes syntactic patterns, complexity metrics, and linguistic convergence
"""

import json
import re
import os
import logging
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from scipy.spatial.distance import cosine
from scipy.stats import entropy
import spacy
from nltk.util import ngrams

# Set up logging
logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Load spaCy model (run: python -m spacy download en_core_web_sm)
nlp = spacy.load("en_core_web_sm")

# ============================================================================
# DATA EXTRACTION
# ============================================================================

def extract_myths_by_round(json_filepath):
    """Extract myths organized by round and agent"""
    with open(json_filepath, 'r') as f:
        data = json.load(f)
    
    myths_by_round = {}
    for entry in data['conversation_history']:
        round_num = entry['round']
        if 'myths' in entry:
            myths_by_round[round_num] = entry['myths']
    
    return myths_by_round

# ============================================================================
# SENTENCE EXTRACTION & PREPROCESSING
# ============================================================================

def extract_sentences(text):
    """Split myth into individual sentences"""
    text = re.sub(r'^Myth:\s*', '', text, flags=re.IGNORECASE)
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents]

def preprocess_text(text):
    """Clean and normalize myth text"""
    text = re.sub(r'^Myth:\s*', '', text, flags=re.IGNORECASE)
    text = text.lower()
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# ============================================================================
# SENTENCE STRUCTURE EXTRACTION
# ============================================================================

def get_pos_pattern(sentence):
    """Get Part-of-Speech tag sequence (syntactic pattern)"""
    doc = nlp(sentence)
    return tuple([token.pos_ for token in doc])

def get_dependency_pattern(sentence):
    """Get dependency structure pattern"""
    doc = nlp(sentence)
    dep_pattern = []
    for token in doc:
        dep_pattern.append((token.pos_, token.dep_, token.head.pos_))
    return tuple(dep_pattern)

def classify_sentence_type(sentence):
    """Classify sentence by structure type"""
    doc = nlp(sentence)
    
    # Get root verb
    root = [token for token in doc if token.head == token][0]
    
    pattern = []
    
    # Subject
    subjects = [child for child in root.children if child.dep_ in ['nsubj', 'nsubjpass']]
    if subjects:
        pattern.append('SUBJ')
    
    # Verb
    pattern.append(f'VERB-{root.pos_}')
    
    # Object
    objects = [child for child in root.children if child.dep_ in ['dobj', 'obj', 'iobj']]
    if objects:
        pattern.append('OBJ')
    
    # Prepositional phrases
    preps = [child for child in root.children if child.dep_ == 'prep']
    if preps:
        pattern.append('PREP')
    
    # Subordinate clauses
    subclauses = [child for child in root.children if child.dep_ in ['ccomp', 'xcomp', 'advcl']]
    if subclauses:
        pattern.append('SUBCLAUSE')
    
    # Modifiers
    mods = [child for child in root.children if child.dep_ in ['amod', 'advmod']]
    if len(mods) > 2:
        pattern.append('HEAVY-MOD')
    
    return tuple(pattern)

def extract_construction_patterns(sentence):
    """Extract grammatical constructions"""
    doc = nlp(sentence)
    constructions = []
    
    for token in doc:
        if token.dep_ == 'nsubjpass':
            constructions.append('PASSIVE')
        
        if token.text.lower() in ['who', 'what', 'where', 'when', 'why', 'how']:
            constructions.append('WH-QUESTION')
        
        if token.text.lower() in ['if', 'unless', 'whether']:
            constructions.append('CONDITIONAL')
        
        if token.dep_ == 'neg':
            constructions.append('NEGATION')
        
        if token.dep_ == 'relcl':
            constructions.append('RELATIVE-CLAUSE')
        
        if token.dep_ == 'xcomp' and token.pos_ == 'VERB':
            constructions.append('INFINITIVE')
    
    return constructions

# ============================================================================
# COMPLEXITY METRICS
# ============================================================================

def calculate_sentence_complexity(sentence):
    """Calculate multiple complexity measures for a sentence"""
    doc = nlp(sentence)
    metrics = {}
    
    # 1. Sentence length (words)
    metrics['length'] = len([t for t in doc if not t.is_punct])
    
    # 2. Average word length
    words = [t.text for t in doc if not t.is_punct and not t.is_space]
    metrics['avg_word_length'] = sum(len(w) for w in words) / len(words) if words else 0
    
    # 3. Dependency tree depth
    def get_tree_depth(token, depth=0):
        if not list(token.children):
            return depth
        return max(get_tree_depth(child, depth + 1) for child in token.children)
    
    root = [token for token in doc if token.head == token]
    if root:
        metrics['tree_depth'] = get_tree_depth(root[0])
    else:
        metrics['tree_depth'] = 0
    
    # 4. Number of clauses
    metrics['num_clauses'] = len([t for t in doc if t.dep_ in ['ccomp', 'xcomp', 'advcl', 'acl', 'relcl']]) + 1
    
    # 5. Number of noun phrases
    metrics['num_noun_phrases'] = len(list(doc.noun_chunks))
    
    # 6. Verb density
    verbs = len([t for t in doc if t.pos_ == 'VERB'])
    metrics['verb_density'] = verbs / len(words) if words else 0
    
    # 7. Subordination ratio
    subordinate_conj = len([t for t in doc if t.dep_ in ['mark', 'aux', 'auxpass']])
    metrics['subordination_ratio'] = subordinate_conj / len(words) if words else 0
    
    return metrics

def analyze_myth_complexity(myth_text):
    """Aggregate complexity metrics across all sentences in a myth"""
    sentences = extract_sentences(myth_text)
    
    if not sentences:
        return {}
    
    all_metrics = []
    for sent in sentences:
        try:
            all_metrics.append(calculate_sentence_complexity(sent))
        except Exception as e:
            logger.warning(f"Failed to calculate complexity for sentence: {sent[:50]}... Error: {type(e).__name__}: {str(e)}")
            continue
    
    if not all_metrics:
        return {}
    
    # Average across sentences
    avg_metrics = {}
    for key in all_metrics[0].keys():
        avg_metrics[f'avg_{key}'] = sum(m[key] for m in all_metrics) / len(all_metrics)
    
    avg_metrics['num_sentences'] = len(sentences)
    avg_metrics['std_sentence_length'] = np.std([m['length'] for m in all_metrics])
    
    return avg_metrics

# ============================================================================
# PATTERN EXTRACTION
# ============================================================================

def get_sentence_structure_ngrams(myth_text, n=2):
    """Get n-grams of sentence structure types"""
    sentences = extract_sentences(myth_text)
    
    if not sentences:
        return Counter()
    
    sentence_types = []
    for sent in sentences:
        try:
            sentence_types.append(classify_sentence_type(sent))
        except Exception as e:
            logger.warning(f"Failed to classify sentence type for: {sent[:50]}... Error: {type(e).__name__}: {str(e)}")
            continue
    
    if len(sentence_types) < n:
        return Counter()
    
    structure_ngrams = list(ngrams(sentence_types, n))
    return Counter(structure_ngrams)

def get_construction_patterns(myth_text):
    """Get all grammatical constructions used in the myth"""
    sentences = extract_sentences(myth_text)
    
    all_constructions = []
    for sent in sentences:
        try:
            all_constructions.extend(extract_construction_patterns(sent))
        except Exception as e:
            logger.warning(f"Failed to extract construction patterns for: {sent[:50]}... Error: {type(e).__name__}: {str(e)}")
            continue
    
    return Counter(all_constructions)

# ============================================================================
# TEMPORAL EVOLUTION ANALYSIS
# ============================================================================

def analyze_structural_evolution(myths_by_round):
    """Track how sentence structures evolve over time"""
    
    evolution_data = {
        'complexity_metrics': {},
        'pos_patterns': {},
        'sentence_type_patterns': {},
        'construction_patterns': {},
        'dependency_patterns': {}
    }
    
    print("\nAnalyzing structural evolution across rounds...")
    total_rounds = len(myths_by_round)
    
    for idx, round_num in enumerate(sorted(myths_by_round.keys()), 1):
        if idx % 10 == 0:
            print(f"  Processing round {idx}/{total_rounds}...")
        
        for agent_id, myth_text in myths_by_round[round_num].items():
            
            # Initialize agent data structures
            if agent_id not in evolution_data['complexity_metrics']:
                for key in evolution_data.keys():
                    evolution_data[key][agent_id] = []
            
            # 1. Complexity metrics
            complexity = analyze_myth_complexity(myth_text)
            if complexity:
                complexity['round'] = round_num
                evolution_data['complexity_metrics'][agent_id].append(complexity)
            
            # 2. POS patterns
            sentences = extract_sentences(myth_text)
            pos_patterns = Counter()
            dep_patterns = Counter()
            
            for sent in sentences:
                try:
                    pos_patterns[get_pos_pattern(sent)] += 1
                    dep_patterns[get_dependency_pattern(sent)] += 1
                except Exception as e:
                    logger.warning(f"Failed to extract POS/dependency patterns for sentence (round {round_num}, {agent_id}): {sent[:50]}... Error: {type(e).__name__}: {str(e)}")
                    continue
            
            evolution_data['pos_patterns'][agent_id].append({
                'round': round_num,
                'patterns': pos_patterns
            })
            
            evolution_data['dependency_patterns'][agent_id].append({
                'round': round_num,
                'patterns': dep_patterns
            })
            
            # 3. Sentence type n-grams
            sent_ngrams = get_sentence_structure_ngrams(myth_text, n=2)
            evolution_data['sentence_type_patterns'][agent_id].append({
                'round': round_num,
                'patterns': sent_ngrams
            })
            
            # 4. Construction patterns
            constructions = get_construction_patterns(myth_text)
            evolution_data['construction_patterns'][agent_id].append({
                'round': round_num,
                'patterns': constructions
            })
    
    print("  ✓ Structural evolution analysis complete")
    return evolution_data

# ============================================================================
# CONVERGENCE & INNOVATION ANALYSIS
# ============================================================================

def analyze_structural_convergence(evolution_data, metric_type='pos_patterns'):
    """Measure if agents converge in their sentence structures"""
    
    agent_ids = list(evolution_data[metric_type].keys())
    if len(agent_ids) != 2:
        print(f"Warning: Convergence analysis requires exactly 2 agents, found {len(agent_ids)}")
        return None
    
    convergence_timeline = []
    
    # Get all rounds
    rounds = [item['round'] for item in evolution_data[metric_type][agent_ids[0]]]
    
    for i, round_num in enumerate(rounds):
        patterns1 = evolution_data[metric_type][agent_ids[0]][i]['patterns']
        patterns2 = evolution_data[metric_type][agent_ids[1]][i]['patterns']
        
        # Calculate similarity using cosine similarity
        all_patterns = set(patterns1.keys()) | set(patterns2.keys())
        
        if not all_patterns:
            similarity = 0
        else:
            vec1 = [patterns1.get(p, 0) for p in all_patterns]
            vec2 = [patterns2.get(p, 0) for p in all_patterns]
            
            if sum(vec1) > 0 and sum(vec2) > 0:
                similarity = 1 - cosine(vec1, vec2)
            else:
                similarity = 0
        
        convergence_timeline.append({
            'round': round_num,
            'similarity': similarity
        })
    
    return convergence_timeline

def calculate_structural_innovation(evolution_data, agent_id, metric_type='pos_patterns'):
    """Calculate how much structural innovation happens each round"""
    
    innovation_timeline = []
    agent_data = evolution_data[metric_type][agent_id]
    
    for i in range(1, len(agent_data)):
        current_patterns = set(agent_data[i]['patterns'].keys())
        previous_patterns = set(agent_data[i-1]['patterns'].keys())
        
        new_patterns = current_patterns - previous_patterns
        innovation_rate = len(new_patterns) / len(current_patterns) if current_patterns else 0
        
        innovation_timeline.append({
            'round': agent_data[i]['round'],
            'innovation_rate': innovation_rate,
            'num_new_patterns': len(new_patterns),
            'total_patterns': len(current_patterns)
        })
    
    return innovation_timeline

# ============================================================================
# VISUALIZATION
# ============================================================================

def plot_structural_evolution(evolution_data, output_file='sentence_structure_evolution.png'):
    """Visualize sentence structure evolution"""
    
    fig, axes = plt.subplots(3, 2, figsize=(16, 14))
    
    # 1. Syntactic complexity (tree depth)
    ax = axes[0, 0]
    for agent_id in evolution_data['complexity_metrics'].keys():
        data = evolution_data['complexity_metrics'][agent_id]
        if data:
            rounds = [d['round'] for d in data]
            tree_depth = [d.get('avg_tree_depth', 0) for d in data]
            ax.plot(rounds, tree_depth, marker='o', label=agent_id, linewidth=2, markersize=4)
    ax.set_xlabel('Round', fontsize=11)
    ax.set_ylabel('Average Tree Depth', fontsize=11)
    ax.set_title('Syntactic Complexity (Tree Depth)', fontsize=12, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 2. Subordination complexity
    ax = axes[0, 1]
    for agent_id in evolution_data['complexity_metrics'].keys():
        data = evolution_data['complexity_metrics'][agent_id]
        if data:
            rounds = [d['round'] for d in data]
            clauses = [d.get('avg_num_clauses', 0) for d in data]
            ax.plot(rounds, clauses, marker='o', label=agent_id, linewidth=2, markersize=4)
    ax.set_xlabel('Round', fontsize=11)
    ax.set_ylabel('Average Clauses per Sentence', fontsize=11)
    ax.set_title('Subordination Complexity', fontsize=12, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 3. Sentence length variability
    ax = axes[1, 0]
    for agent_id in evolution_data['complexity_metrics'].keys():
        data = evolution_data['complexity_metrics'][agent_id]
        if data:
            rounds = [d['round'] for d in data]
            std_length = [d.get('std_sentence_length', 0) for d in data]
            ax.plot(rounds, std_length, marker='o', label=agent_id, linewidth=2, markersize=4)
    ax.set_xlabel('Round', fontsize=11)
    ax.set_ylabel('Std Dev of Sentence Length', fontsize=11)
    ax.set_title('Sentence Length Variability', fontsize=12, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 4. POS pattern diversity
    ax = axes[1, 1]
    for agent_id in evolution_data['pos_patterns'].keys():
        data = evolution_data['pos_patterns'][agent_id]
        if data:
            rounds = [d['round'] for d in data]
            diversity = [len(d['patterns']) for d in data]
            ax.plot(rounds, diversity, marker='o', label=agent_id, linewidth=2, markersize=4)
    ax.set_xlabel('Round', fontsize=11)
    ax.set_ylabel('Number of Unique POS Patterns', fontsize=11)
    ax.set_title('Structural Diversity', fontsize=12, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 5. Structural convergence
    ax = axes[2, 0]
    convergence = analyze_structural_convergence(evolution_data, 'pos_patterns')
    if convergence:
        rounds = [d['round'] for d in convergence]
        similarity = [d['similarity'] for d in convergence]
        ax.plot(rounds, similarity, marker='o', color='purple', linewidth=2, markersize=4)
    ax.set_xlabel('Round', fontsize=11)
    ax.set_ylabel('Structural Similarity', fontsize=11)
    ax.set_title('Agent Structural Convergence (POS Patterns)', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # 6. Construction pattern usage
    ax = axes[2, 1]
    construction_types = ['PASSIVE', 'RELATIVE-CLAUSE', 'CONDITIONAL', 'NEGATION']
    colors = ['red', 'blue', 'green', 'orange']
    
    for agent_id in evolution_data['construction_patterns'].keys():
        data = evolution_data['construction_patterns'][agent_id]
        if data:
            rounds = [d['round'] for d in data]
            
            for const_type, color in zip(construction_types, colors):
                usage = [d['patterns'].get(const_type, 0) for d in data]
                if sum(usage) > 0:  # Only plot if used
                    ax.plot(rounds, usage, marker='o', label=f'{agent_id} - {const_type}', 
                           linewidth=2, markersize=3, alpha=0.7)
    
    ax.set_xlabel('Round', fontsize=11)
    ax.set_ylabel('Frequency', fontsize=11)
    ax.set_title('Grammatical Construction Usage', fontsize=12, fontweight='bold')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✓ Visualization saved to {output_file}")
    plt.show()

# ============================================================================
# REPORTING
# ============================================================================

def print_summary_statistics(evolution_data):
    """Print summary statistics of structural evolution"""
    
    print("\n" + "=" * 80)
    print("SENTENCE STRUCTURE EVOLUTION SUMMARY")
    print("=" * 80)
    
    for agent_id in evolution_data['complexity_metrics'].keys():
        print(f"\n{agent_id}:")
        print("-" * 40)
        
        data = evolution_data['complexity_metrics'][agent_id]
        if not data:
            print("  No data available")
            continue
        
        # Complexity trends
        first_depth = data[0].get('avg_tree_depth', 0)
        last_depth = data[-1].get('avg_tree_depth', 0)
        print(f"  Tree Depth: {first_depth:.2f} → {last_depth:.2f} (Δ {last_depth - first_depth:+.2f})")
        
        first_clauses = data[0].get('avg_num_clauses', 0)
        last_clauses = data[-1].get('avg_num_clauses', 0)
        print(f"  Clauses: {first_clauses:.2f} → {last_clauses:.2f} (Δ {last_clauses - first_clauses:+.2f})")
        
        # Pattern diversity
        pos_data = evolution_data['pos_patterns'][agent_id]
        first_diversity = len(pos_data[0]['patterns'])
        last_diversity = len(pos_data[-1]['patterns'])
        print(f"  Unique POS Patterns: {first_diversity} → {last_diversity} (Δ {last_diversity - first_diversity:+d})")
        
        # Innovation rate
        innovation = calculate_structural_innovation(evolution_data, agent_id, 'pos_patterns')
        if innovation:
            avg_innovation = np.mean([i['innovation_rate'] for i in innovation])
            print(f"  Average Innovation Rate: {avg_innovation:.2%}")
    
    # Convergence
    print("\n" + "-" * 40)
    print("CONVERGENCE ANALYSIS:")
    print("-" * 40)
    
    convergence = analyze_structural_convergence(evolution_data, 'pos_patterns')
    if convergence:
        initial_sim = convergence[0]['similarity']
        final_sim = convergence[-1]['similarity']
        change = final_sim - initial_sim
        
        print(f"  Initial Similarity: {initial_sim:.3f}")
        print(f"  Final Similarity: {final_sim:.3f}")
        print(f"  Change: {change:+.3f} ({'Converging' if change > 0 else 'Diverging'})")
        
        # Calculate trend
        rounds = [c['round'] for c in convergence]
        similarities = [c['similarity'] for c in convergence]
        
        if len(rounds) > 10:
            early_avg = np.mean(similarities[:10])
            late_avg = np.mean(similarities[-10:])
            print(f"  Early Average (first 10): {early_avg:.3f}")
            print(f"  Late Average (last 10): {late_avg:.3f}")
    
    print("\n" + "=" * 80)

# ============================================================================
# MAIN ANALYSIS PIPELINE
# ============================================================================

def full_sentence_structure_analysis(json_filepath, output_prefix=''):
    """Complete pipeline for sentence structure analysis"""
    
    print("\n" + "=" * 80)
    print("SENTENCE STRUCTURE EVOLUTION ANALYSIS")
    print("=" * 80)
    
    # Step 1: Load data
    print("\n[1/6] Loading myth data...")
    myths_by_round = extract_myths_by_round(json_filepath)
    print(f"  ✓ Loaded {len(myths_by_round)} rounds")
    
    # Step 2: Analyze structural evolution
    print("\n[2/6] Analyzing structural evolution...")
    evolution_data = analyze_structural_evolution(myths_by_round)
    
    # Step 3: Calculate innovation rates
    print("\n[3/6] Calculating innovation rates...")
    for agent_id in evolution_data['pos_patterns'].keys():
        innovation = calculate_structural_innovation(evolution_data, agent_id, 'pos_patterns')
        if innovation:
            print(f"  {agent_id}: Avg innovation rate = {np.mean([i['innovation_rate'] for i in innovation]):.2%}")
    
    # Step 4: Calculate convergence
    print("\n[4/6] Calculating convergence metrics...")
    convergence = analyze_structural_convergence(evolution_data, 'pos_patterns')
    if convergence:
        initial = convergence[0]['similarity']
        final = convergence[-1]['similarity']
        print(f"  Similarity: {initial:.3f} → {final:.3f} (Δ {final - initial:+.3f})")
    
    # Step 5: Print summary
    print("\n[5/6] Generating summary statistics...")
    print_summary_statistics(evolution_data)
    
    # Step 6: Visualize
    print("\n[6/6] Creating visualizations...")
    output_file = os.path.join(output_prefix, 'sentence_structure_evolution.png') if output_prefix else 'sentence_structure_evolution.png'
    plot_structural_evolution(evolution_data, output_file)
    
    # Save results
    print("\nSaving results...")
    json_output = os.path.join(output_prefix, 'sentence_structure_analysis.json') if output_prefix else 'sentence_structure_analysis.json'
    
    # Convert Counter objects to dicts for JSON serialization
    serializable_data = {}
    for key, value in evolution_data.items():
        serializable_data[key] = {}
        for agent_id, agent_data in value.items():
            serializable_data[key][agent_id] = []
            for item in agent_data:
                serialized_item = {}
                for k, v in item.items():
                    if isinstance(v, Counter):
                        serialized_item[k] = {str(key): count for key, count in v.items()}
                    else:
                        serialized_item[k] = v
                serializable_data[key][agent_id].append(serialized_item)
    
    with open(json_output, 'w') as f:
        json.dump(serializable_data, f, indent=2)
    
    print(f"  ✓ Results saved to {json_output}")
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE!")
    print("=" * 80)
    
    return evolution_data

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Check if running from shell script (environment variables available)
    input_file = os.environ.get('ANALYSIS_INPUT_FILE', '/Users/ivar/Desktop/current_projects/AI_projects/test_config_modular_llm/data/json/model_comparison/model_comparison_000_gpt-4o-mini_neutral_game_myth.json')
    base_output_dir = os.environ.get('ANALYSIS_OUTPUT_DIR', '/Users/ivar/Desktop/current_projects/AI_projects/test_config_modular_llm/data/plots/model_comparison/gpt-4o-mini/n_gram_sentence_structure')
    task_name = os.environ.get('ANALYSIS_TASK_NAME', 'game_myth')

    # # Configuration
    # if input_file:
    #     # Running from script with environment variables
    #     output_prefix = f'{base_output_dir}/' if base_output_dir else ''
    #     os.makedirs(base_output_dir, exist_ok=True)
    # else:
    #     # Default fallback values
    #     print("No environment variables found, using default values")
    #     input_file = '/Users/ivar/Desktop/current_projects/AI_projects/test_config_modular_llm/data/json/model_comparison/model_comparison_000_gpt-4o-mini_neutral_game_myth.json'
    #     output_prefix = ''

    # Run complete analysis
    evolution_data = full_sentence_structure_analysis(input_file, base_output_dir)
    
    print("\nFiles generated:")
    print("  1. sentence_structure_evolution.png - Visualization plots")
    print("  2. sentence_structure_analysis.json - Detailed results data")
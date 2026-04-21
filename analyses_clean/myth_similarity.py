import json
import os
from together import Together
from openai import OpenAI
from pydantic import BaseModel, Field

# Get API keys from environment variables
Together_API_KEY = os.environ.get('TOGETHER_API_KEY', '')
API_KEY = os.environ.get('OPENAI_API_KEY', '')

class SimilarityJudgment(BaseModel):
    thematic_similarity: float = Field(description="How similar are the core themes and messages (0-10)")
    character_similarity: float = Field(description="How similar are the characters, gods, and entities (0-10)")
    narrative_similarity: float = Field(description="How similar is the story structure and plot (0-10)")
    symbolic_similarity: float = Field(description="How similar are the metaphors, symbols, and imagery (0-10)")
    conceptual_similarity: float = Field(description="How similar are the underlying concepts about coordination/harmony (0-10)")
    explanation: str = Field(description="Brief explanation of the ratings")

def judge_similarity(myth1, myth2, round1, round2, client, model_name, agent1=None, agent2=None):
    """Use LLM to judge semantic similarity between two myths."""
    prompt = f"""Please analyze these two myths and rate their semantic similarity on multiple dimensions. Respond only in JSON.


Myth from Round {round1}:
{myth1}

Myth from Round {round2}:
{myth2}

Rate on the following dimensions (0-10 scale):
1. THEMATIC SIMILARITY: How similar are the core themes and messages?
2. CHARACTER/ENTITY SIMILARITY: How similar are the characters, gods, and entities mentioned?
3. NARRATIVE STRUCTURE SIMILARITY: How similar is the story structure and plot?
4. SYMBOLIC SIMILARITY: How similar are the metaphors, symbols, and imagery?
5. CONCEPTUAL SIMILARITY: How similar are the underlying concepts about coordination/harmony?

Also a brief explanation."""

    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        response_format={
            "type": "json_schema",
            "schema": SimilarityJudgment.model_json_schema(),
        },
    )
    
    result = json.loads(response.choices[0].message.content)
    print(result)

    # Calculate overall similarity as average of all dimensions
    dimensions = ['thematic_similarity', 'character_similarity', 'narrative_similarity', 
                  'symbolic_similarity', 'conceptual_similarity']
    overall = sum(result[dim] for dim in dimensions) / len(dimensions)
    print(overall)
    result['overall_similarity'] = overall
    
    return result

def analyze_between_rounds(agent_myths, client, model_name):
    """Analyze similarities between rounds for same agent."""
    results = []
    
    print("\n" + "=" * 80)
    print("BETWEEN ROUNDS COMPARISON (Same Agent)")
    print("=" * 80)
    
    for agent_id in sorted(agent_myths.keys()):
        print(f"\n{agent_id}:")
        print("-" * 80)
        
        myths = agent_myths[agent_id]
        if len(myths) < 2:
            print(f"  Not enough myths for comparison (need at least 2)")
            continue
        
        # Compare each myth to the first myth
        first_round, first_myth = myths[0]
        
        for i in range(1, len(myths)):
            current_round, current_myth = myths[i]
            result = judge_similarity(first_myth, current_myth, first_round, current_round, 
                                    client, model_name, agent_id, agent_id)
            
            comparison = {
                "agent_id": agent_id,
                "round1": first_round,
                "round2": current_round,
                "myth1": first_myth,
                "myth2": current_myth,
                "similarity": result
            }
            results.append(comparison)
            
            print(f"\nRound {first_round} → {current_round}:")
            print(f"  Thematic:    {result['thematic_similarity']}/10")
            print(f"  Character:   {result['character_similarity']}/10")
            print(f"  Narrative:   {result['narrative_similarity']}/10")
            print(f"  Symbolic:    {result['symbolic_similarity']}/10")
            print(f"  Conceptual:  {result['conceptual_similarity']}/10")
            print(f"  Overall:     {result['overall_similarity']}/10")
            print(f"  Explanation: {result['explanation']}")
    
    return results

def analyze_within_round(data, client, model_name):
    """Analyze similarities within rounds between agents."""
    results = []
    
    print("\n" + "=" * 80)
    print("WITHIN ROUND COMPARISON (Between Agents)")
    print("=" * 80)
    
    # Get all rounds that have myths
    rounds_with_myths = {}
    for entry in data['conversation_history']:
        if 'myths' in entry and entry['myths']:
            rounds_with_myths[entry['round']] = entry['myths']
    
    # Compare agents within each round
    for round_num in sorted(rounds_with_myths.keys()):
        myths_in_round = rounds_with_myths[round_num]
        agent_ids = list(myths_in_round.keys())
        
        if len(agent_ids) < 2:
            print(f"\nRound {round_num}: Not enough agents (need at least 2)")
            continue
        
        print(f"\nRound {round_num}:")
        print("-" * 80)
        
        # Compare all pairs of agents in this round
        for i in range(len(agent_ids)):
            for j in range(i + 1, len(agent_ids)):
                agent1_id = agent_ids[i]
                agent2_id = agent_ids[j]
                myth1 = myths_in_round[agent1_id]
                myth2 = myths_in_round[agent2_id]
                
                result = judge_similarity(myth1, myth2, round_num, round_num, 
                                        client, model_name, agent1_id, agent2_id)
                
                comparison = {
                    "round": round_num,
                    "agent1_id": agent1_id,
                    "agent2_id": agent2_id,
                    "myth1": myth1,
                    "myth2": myth2,
                    "similarity": result
                }
                results.append(comparison)
                
                print(f"\n{agent1_id} vs {agent2_id}:")
                print(f"  Thematic:    {result['thematic_similarity']}/10")
                print(f"  Character:   {result['character_similarity']}/10")
                print(f"  Narrative:   {result['narrative_similarity']}/10")
                print(f"  Symbolic:    {result['symbolic_similarity']}/10")
                print(f"  Conceptual:  {result['conceptual_similarity']}/10")
                print(f"  Overall:     {result['overall_similarity']}/10")
                print(f"  Explanation: {result['explanation']}")
    
    return results

def main(input_file, output_file, model_name, comparison_mode, api_key):
    """Main execution function."""
    # Initialize client
    client = Together(api_key=api_key)
    #client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")
    
    # Load simulation data
    print(f"Loading simulation data from {input_file}...")
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    # Extract myths for each agent
    agent_myths = {}
    for entry in data['conversation_history']:
        for agent_id, myth in entry.get('myths', {}).items():
            if agent_id not in agent_myths:
                agent_myths[agent_id] = []
            agent_myths[agent_id].append((entry['round'], myth))
    
    # Choose comparison mode
    print("=" * 80)
    print("MYTH SIMILARITY ANALYSIS")
    print("=" * 80)
    print("\nComparison modes:")
    print("1. Between rounds for same agent (e.g., Agent 1 myth 1 vs Agent 1 myth 10)")
    print("2. Within round between agents (e.g., Agent 1 myth 1 vs Agent 2 myth 1)")
    print("3. Both")
    print(f"\nUsing mode: {comparison_mode}")
    
    results = {
        "comparison_mode": comparison_mode,
        "between_rounds": [],
        "within_round": []
    }
    
    # Mode 1: Between rounds for same agent
    if comparison_mode in ['1', '3']:
        results["between_rounds"] = analyze_between_rounds(agent_myths, client, model_name)
    
    # Mode 2: Within round between agents
    if comparison_mode in ['2', '3']:
        results["within_round"] = analyze_within_round(data, client, model_name)
    
    # Save results to JSON
    print(f"\nSaving results to {output_file}...")
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "=" * 80)
    print(f"Results saved to {output_file}")
    print("=" * 80)

if __name__ == '__main__':
    # Check if running from shell script (environment variables available)
    input_file = os.environ.get('ANALYSIS_INPUT_FILE', '/Users/ivar/Desktop/current_projects/AI_projects/test_config_modular_llm/data/json/model_comparison/model_comparison_000_gpt-4o-mini_neutral_game_myth.json')
    base_output_dir = os.environ.get('ANALYSIS_OUTPUT_DIR', '/Users/ivar/Desktop/current_projects/AI_projects/test_config_modular_llm/data/plots/model_comparison/gpt-4o-mini/myth_similarity')
    task_name = os.environ.get('ANALYSIS_TASK_NAME', 'game_myth')

    # Configuration
    output_file = f'{base_output_dir}/myth_similarity_results.json'
    model_name = "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo"
    comparison_mode = "3"  # "1" = between rounds, "2" = within round, "3" = both

    # Run main function
    main(input_file, output_file, model_name, comparison_mode, Together_API_KEY)
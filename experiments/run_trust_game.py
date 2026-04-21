import yaml
from src.simulation import run_simulation
from src.myth_writer import MythWriter
from games.trust_game import TrustGame


if __name__ == "__main__":
    # Load config to get prompts
    with open('config/experiments.yaml', 'r') as f:
        config = yaml.safe_load(f)

    prompts = config['prompt_templates']

    # Configure game
    game = TrustGame(
        endowment=5,
        multiplier=3,
        system_prompt_template=prompts['trust_game_default'],
        round1_investor_template=prompts['trust_game_round1_investor'],
        round1_trustee_template=prompts['trust_game_round1_trustee'],
        later_investor_template=prompts['trust_game_later_investor'],
        later_trustee_template=prompts['trust_game_later_trustee']
    )

    myth_writer = MythWriter(
        myth_topic="",
        round1_template=prompts['myth_writing_default'],
        later_rounds_template=prompts['myth_writing_later_rounds']
    )

    model = "google/gemini-3-pro-preview"

    # Run simulation
    base_path = "data/json/main_loop/"
    log_file = base_path + "config_test.log"

    sim_data = run_simulation(
        game,
        model,
        temperature=0.8,
        num_turns=10,
        num_agents=2,
        memory_capacity=3,
        agent_biases="",
        myth_writer=myth_writer,
        log_file=log_file
    )

    # Save results
    sim_data.save_state(base_path + "config_test.json")
    print(f"\n✓ Simulation state saved to config_test.json")
    print(f"✓ Log file saved to {log_file}")
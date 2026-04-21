from together import Together
from openai import OpenAI
import json
import os
import time
from typing import Any, Dict, Optional
from src.agents import Agent
from src.utils import print_simulation_header, API_KEY
from concurrent.futures import ThreadPoolExecutor
class SimulationData:
    """Centralized state management for multi-agent conversations"""

    def __init__(self):
        self.agents = {}
        self.conversation_history = []
        self.game_data = {}
        self.task_order = None  # Store task order used in simulation
        # Optional: store basic run metadata for easier debugging/resume
        self.run_metadata = {}

    def add_agent(self, agent_id, agent):
        self.agents[agent_id] = agent

    def get_agent_messages(self, agent_id):
        return self.agents[agent_id].messages

    @staticmethod
    def _atomic_json_write(filepath: str, data: Dict[str, Any], *, indent: Optional[int] = 2) -> None:
        dirpath = os.path.dirname(filepath)
        if dirpath:
            os.makedirs(dirpath, exist_ok=True)
        tmp_path = filepath + ".tmp"
        with open(tmp_path, "w") as f:
            json.dump(data, f, indent=indent)
        os.replace(tmp_path, filepath)

    def save_state(self, filepath):
        state = {
            "conversation_history": self.conversation_history,
            "game_data": self.game_data,
            "task_order": self.task_order, # Include task_order in saved state
            "run_metadata": self.run_metadata,
            "agents": {
                agent_id: {
                    "agent_id": agent.agent_id,
                    "model": agent.model,
                    "temperature": agent.temperature,
                    "memory_capacity": agent.memory_capacity,
                    "initial_bias": agent.initial_bias,
                    "system_prompt": agent.system_prompt,
                    "messages": agent.messages
                }
                for agent_id, agent in self.agents.items()
            }
        }
        self._atomic_json_write(filepath, state, indent=2)

    def save_results_only(self, filepath):
        """Lightweight save: results/state only (no agent message histories)."""
        state = {
            "conversation_history": self.conversation_history,
            "game_data": self.game_data,
            "task_order": self.task_order,
            "run_metadata": self.run_metadata,
        }
        self._atomic_json_write(filepath, state, indent=2)

    @classmethod
    def load_state(cls, filepath: str, client, log_file: Optional[str] = None) -> "SimulationData":
        """
        Load simulation state from a JSON file.
        Loads the full state of the simulation, including the message history of each agent.
        """
        with open(filepath, "r") as f:
            state = json.load(f)
        sim_data = cls()
        sim_data.conversation_history = state.get("conversation_history", [])
        sim_data.game_data = state.get("game_data", {})
        sim_data.task_order = state.get("task_order")
        sim_data.run_metadata = state.get("run_metadata", {})

        agents_state = state.get("agents", {}) or {}
        for agent_id, a in agents_state.items():
            agent = Agent(
                a["agent_id"],
                a["model"],
                a.get("temperature", sim_data.run_metadata.get("temperature", 0.8)),
                client,
                memory_capacity=a["memory_capacity"],
                initial_bias=a.get("initial_bias"),
                system_prompt=a.get("system_prompt"),
                log_file=log_file,
            )
            # Preserve message history exactly for faithful resume
            agent.messages = a.get("messages", [])
            sim_data.add_agent(agent_id, agent)

        return sim_data

def run_simulation(
    game,
    model,
    temperature,
    num_turns,
    num_agents,
    memory_capacity,
    agent_biases,
    myth_writer,
    task_order=["game", "myth"],
    *,
    results_path: Optional[str] = None,
    checkpoint_path: Optional[str] = None,
    checkpoint_every: int = 10,
    resume_from: Optional[str] = None,
    log_file: Optional[str] = None,
):
    """
    Run a multi-agent simulation with any game.
    Now supports sequential moves within a turn.
    Args:
    task_order: List of tasks to execute in order. Options: "game", "myth"
                Examples: ["game"], ["myth"], ["game", "myth"], ["myth", "game"]
    """
    # client = Together(api_key=API_KEY)
    client = OpenAI(api_key=API_KEY, base_url="https://openrouter.ai/api/v1")
    if resume_from and os.path.exists(resume_from):
        sim_data = SimulationData.load_state(resume_from, client, log_file=log_file)
        if task_order is not None:
            sim_data.task_order = task_order
    else:
        sim_data = SimulationData()
        sim_data.task_order = task_order  # Store task_order in sim_data

        # Initialize agents
        for i in range(num_agents):
            agent_id = f"Agent_{i+1}"
            bias = agent_biases[i] if agent_biases and i < len(agent_biases) else None
            agent = Agent(agent_id, model, temperature, client, memory_capacity=memory_capacity, initial_bias=bias, log_file=log_file)
            system_prompt = game.get_system_prompt(agent_id, agent)
            agent.system_prompt = system_prompt
            agent.messages.append({"role": "system", "content": system_prompt})
            sim_data.add_agent(agent_id, agent)

    # Store run metadata (useful for debugging/resume)
    sim_data.run_metadata.update(
        {
            "model": model,
            "temperature": temperature,
            "num_turns": num_turns,
            "num_agents": num_agents,
            "memory_capacity": memory_capacity,
        }
    )

    print_simulation_header(game, num_turns, num_agents, memory_capacity, agent_biases)
    last_responses = {}

    # Main simulation loop
    start_turn = len(sim_data.conversation_history) + 1 if sim_data.conversation_history else 1
    if start_turn > num_turns:
        return sim_data

    for turn in range(start_turn, num_turns + 1):
        print("\n" + "=" * 80)
        print(f"ROUND {turn}")
        print("=" * 80)

        try:
            # Display role assignments for this round
            roles = game.get_roles_for_round(turn)
            move_order = game.get_move_order(turn, sim_data)

            print(f"Roles this round: {roles['investor']} = INVESTOR, {roles['trustee']} = TRUSTEE")
            print(f"Move order this round: {move_order}")
            # Pre-create complete conversation_history entry for this round with all fields
            round_entry = {
                "round": turn,
                "roles": {
                    roles["investor"]: "investor",
                    roles["trustee"]: "trustee"
                },
                "sent": None,
                "received": None,
                "returned": None,
                "investor_payoff": None,
                "trustee_payoff": None,
                "balances": None,
                "actions": None,
                "myths": {},
                "game_responses": {},  # Store game decision responses
                "myth_responses": {}  # Store myth writing responses
            }
            sim_data.conversation_history.append(round_entry)

            agent_responses = {}
            agent_myths = {}

            # Execute tasks in specified order
            for task in task_order:
                if task == "game":
                    # PHASE 1: GAME PLAY
                    print("\n--- PHASE 1: GAME PLAY ---")

                    for agent_id in move_order:
                        agent = sim_data.agents[agent_id]
                        current_role = roles["investor"] if agent_id == roles["investor"] else roles["trustee"]
                        role_name = "Investor" if current_role == roles["investor"] else "Trustee"

                        if turn == 1:
                            prompt = game.get_game_prompt_round_1(agent_id, agent, turn)
                        else:
                            prompt = game.get_game_prompt_later_round(agent_id, turn, sim_data, last_responses)

                        response_data = agent.respond(prompt)
                        agent_responses[agent_id] = response_data

                        # Store full game response data in round_entry
                        round_entry["game_responses"][agent_id] = {
                            "content": response_data["content"],
                            "reasoning": response_data.get("reasoning"),
                            "usage": response_data.get("usage")
                        }

                        print(f"\n{agent_id} ({role_name}) prompt: {prompt}")
                        print(f"{agent_id} ({role_name}) response: {response_data['content']}")

                        # Allow game to update state after each move (for sequential games)
                        if hasattr(game, 'process_intermediate_response'):
                            game.process_intermediate_response(agent_id, response_data, turn, sim_data)

                    # Process turn with game logic
                    last_responses = game.process_turn(turn, agent_responses, sim_data)

                elif task == "myth":
                    # PHASE 2: MYTH WRITING
                    print("\n--- PHASE 2: MYTH WRITING ---")

                    # PARALLELIZED MYTH WRITING
                    # Prepare prompts for all agents (no dependencies)
                    prompts = {}
                    for agent_id in move_order:
                        if turn == 1:
                            prompts[agent_id] = myth_writer.get_myth_prompt_round_1(agent_id, turn, sim_data)
                        else:
                            prompts[agent_id] = myth_writer.get_myth_prompt_round_later(agent_id, turn, sim_data)

                    # Parallelize LLM calls for myth writing
                    with ThreadPoolExecutor(max_workers=len(move_order)) as executor:
                        futures = {
                            agent_id: executor.submit(sim_data.agents[agent_id].respond, prompts[agent_id])
                            for agent_id in move_order
                        }

                        # Collect results as they complete (with one retry on failure)
                        for agent_id, future in futures.items():
                            try:
                                myth_response_data = future.result()
                                agent_myths[agent_id] = myth_response_data
                            except Exception as e:
                                print(f"⚠️  Myth writing failed for {agent_id}: {type(e).__name__}: {e}. Retrying once...")
                                time.sleep(1.0)
                                myth_response_data = sim_data.agents[agent_id].respond(prompts[agent_id])
                                agent_myths[agent_id] = myth_response_data

                            # Store full myth response data in round_entry
                            round_entry["myth_responses"][agent_id] = {
                                "content": myth_response_data["content"],
                                "reasoning": myth_response_data.get("reasoning"),
                                "usage": myth_response_data.get("usage")
                            }

                            current_role = "Investor" if agent_id == roles["investor"] else "Trustee"
                            print(f"\n{agent_id} ({current_role}) myth prompt:\n{prompts[agent_id]}")
                            print(f"\n{agent_id} ({current_role}) myth response:\n{myth_response_data['content']}")

                    myth_writer.process_myths(turn, agent_myths, sim_data)

            # Print turn summary (only if game was run)
            if "game" in task_order:
                game.print_turn_summary(turn, agent_responses, sim_data)

            # Print myths (only if myth was run)
            if "myth" in task_order and sim_data.conversation_history and sim_data.conversation_history[-1].get("myths"):
                print(f"\n{'~' * 80}")
                print("MYTHS WRITTEN THIS ROUND:")
                print(f"{'~' * 80}")
                for agent_id, myth in sim_data.conversation_history[-1]["myths"].items():
                    current_role = "Investor" if agent_id == roles["investor"] else "Trustee"
                    print(f"\n{agent_id} ({current_role}):")
                    print(myth)
                    print("-" * 40)

            # Hybrid saving after successful round
            if results_path:
                sim_data.save_results_only(results_path)
            if checkpoint_path and checkpoint_every > 0 and (turn % checkpoint_every == 0):
                sim_data.save_state(checkpoint_path)

        except Exception:
            # Always write a final save on error before stopping
            if results_path:
                sim_data.save_results_only(results_path)
            if checkpoint_path:
                sim_data.save_state(checkpoint_path + ".error.json")
            raise
    
    # Print game summary (only if game was run)
    if "game" in task_order:
        game.print_game_summary(sim_data)
    return sim_data

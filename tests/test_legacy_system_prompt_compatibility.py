import contextlib
import io
import unittest
from unittest.mock import patch

from experiments.run_noisy_batch import NoisyExperimentConfig
from games.trust_game import TrustGame
from src.myth_writer import MythWriter
from src.simulation import run_simulation


class LegacySystemPromptCompatibilityTests(unittest.TestCase):
    def test_legacy_prompt_overrides_are_resolved_from_the_merged_config(self):
        config = NoisyExperimentConfig("config/experiments_noisy.yaml")

        neutral = config.get_experiment_combinations(
            "neutral_framing_v4_pilot",
            max_runs=1,
        )[0]
        blind = config.get_experiment_combinations(
            "gpt5nano_myth_first_blind_unconstrained_bootstrap",
            max_runs=1,
        )[0]

        self.assertEqual(
            neutral["round_prompt_template_names"]["round1_investor"],
            "trust_game_neutral_round1_investor",
        )
        self.assertEqual(
            blind["myth_prompt_template_names"],
            {
                "round1": "myth_writing_unconstrained_default",
                "later": "myth_writing_unconstrained_later_rounds",
            },
        )
        self.assertEqual(
            blind["initial_system_template_name"],
            "myth_only_system_prompt",
        )
        self.assertTrue(blind["initial_system_prompt_template"])
        self.assertTrue(blind["switch_to_game_system_before_game"])

    def test_myth_first_run_switches_system_prompt_immediately_before_game(self):
        game = TrustGame(
            endowment=5,
            multiplier=3,
            system_prompt_template="GAME SYSTEM {endowment} {multiplier}",
            round1_investor_template="Choose how much to send.",
            round1_trustee_template="You saw {sent}. Choose how much to return.",
            later_investor_template="Choose how much to send.",
            later_trustee_template="Choose how much to return.",
        )
        myth_writer = MythWriter(
            myth_topic="anything",
            round1_template="Write a myth. {topic_instruction}",
            later_rounds_template="Rewrite your myth.",
        )

        def fake_call_llm(client, model, temperature, messages):
            prompt = messages[-1]["content"].lower()
            if "myth" in prompt:
                content = "A short myth about two travelers who learn to share."
            elif "send" in prompt:
                content = '{"send": 2}'
            else:
                content = '{"return": 3}'
            return {"content": content, "reasoning": None, "usage": None}

        with patch(
            "src.simulation.create_llm_client",
            return_value=object(),
        ), patch("src.agents.call_llm", side_effect=fake_call_llm):
            with contextlib.redirect_stdout(io.StringIO()):
                state = run_simulation(
                    game=game,
                    model="mock/model",
                    temperature=0,
                    num_turns=1,
                    num_agents=2,
                    memory_capacity=6,
                    agent_biases="",
                    myth_writer=myth_writer,
                    task_order=["myth", "game"],
                    initial_system_prompt_template=(
                        "MYTH-ONLY SYSTEM {endowment} {multiplier}"
                    ),
                    switch_to_game_system_before_game=True,
                )

        for agent in state.agents.values():
            myth_event, game_event = agent.interaction_history
            self.assertEqual(
                myth_event["messages_sent"][0]["content"],
                "MYTH-ONLY SYSTEM 5 3",
            )
            self.assertEqual(
                game_event["messages_sent"][0]["content"],
                "GAME SYSTEM 5 3",
            )
            self.assertEqual(agent.system_prompt, "GAME SYSTEM 5 3")
        self.assertEqual(
            state.run_metadata["game_system_prompt_applied_at_round"],
            1,
        )
        self.assertTrue(state.run_metadata["initial_system_prompt_overridden"])
        self.assertTrue(state.run_metadata["switch_to_game_system_before_game"])


if __name__ == "__main__":
    unittest.main()

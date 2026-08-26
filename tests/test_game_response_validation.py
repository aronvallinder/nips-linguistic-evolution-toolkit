import contextlib
import io
import os
import unittest
from unittest.mock import patch

from games.base_game import InvalidGameResponseError
from games.trust_game import TrustGame
from src.simulation import run_simulation


def build_game():
    return TrustGame(
        endowment=5,
        multiplier=3,
        system_prompt_template="Game rules",
        round1_investor_template='Respond exactly as JSON: {{"send": amount}}',
        round1_trustee_template='Respond exactly as JSON: {{"return": amount}}',
        later_investor_template="Send an amount.",
        later_trustee_template="Return an amount.",
    )


class GameResponseValidationTests(unittest.TestCase):
    def test_strict_boundary_requires_quoted_expected_key(self):
        game = build_game()
        game.validate_game_response('{"send": 4}', "investor")

        for malformed in ("{send: 4}", '{"return": 4}', "4"):
            with self.subTest(malformed=malformed):
                with self.assertRaises(InvalidGameResponseError):
                    game.validate_game_response(malformed, "investor")

    def test_simulation_retries_without_remembering_rejected_decision(self):
        responses = iter(
            [
                {"content": "{send: 4}", "reasoning": None, "usage": None},
                {"content": '{"send": 4}', "reasoning": None, "usage": None},
                {"content": '{"return": 3}', "reasoning": None, "usage": None},
            ]
        )

        with patch("src.simulation.create_llm_client", return_value=object()), patch(
            "src.agents.call_llm",
            side_effect=lambda *args, **kwargs: next(responses),
        ), patch("src.simulation.time.sleep"):
            with contextlib.redirect_stdout(io.StringIO()):
                sim_data = run_simulation(
                    game=build_game(),
                    model="mock/model",
                    temperature=0,
                    num_turns=1,
                    num_agents=2,
                    memory_capacity=3,
                    agent_biases="",
                    myth_writer=None,
                    task_order=["game"],
                    chat_memory_mode="memory_primary",
                )

        investor = sim_data.agents["Agent_1"]
        self.assertEqual(len(investor.interaction_history), 2)
        rejected, accepted = investor.interaction_history
        self.assertEqual(rejected["error"]["type"], "InvalidGameResponseError")
        self.assertEqual(rejected["response"]["content"], "{send: 4}")
        self.assertNotIn(
            "{send: 4}",
            [message.get("content") for message in investor.messages],
        )
        self.assertNotIn("error", accepted)

        round_entry = sim_data.conversation_history[0]
        self.assertEqual(round_entry["game_responses"]["Agent_1"]["content"], '{"send": 4}')
        self.assertEqual(round_entry["sent"], 4)
        self.assertEqual(round_entry["returned"], 3)

    def test_corrective_retry_records_policy_but_preserves_experimental_memory(self):
        responses = iter(
            [
                {"content": '{"return": 0}', "reasoning": None, "usage": None},
                {"content": '{"send": 4}', "reasoning": None, "usage": None},
                {"content": '{"return": 3}', "reasoning": None, "usage": None},
            ]
        )

        with patch.dict(
            os.environ,
            {"GAME_RESPONSE_RETRY_POLICY": "corrective_role_key_once_v1"},
        ), patch("src.simulation.create_llm_client", return_value=object()), patch(
            "src.agents.call_llm",
            side_effect=lambda *args, **kwargs: next(responses),
        ), patch("src.simulation.time.sleep"):
            with contextlib.redirect_stdout(io.StringIO()):
                sim_data = run_simulation(
                    game=build_game(),
                    model="mock/model",
                    temperature=0,
                    num_turns=1,
                    num_agents=2,
                    memory_capacity=3,
                    agent_biases="",
                    myth_writer=None,
                    task_order=["game"],
                    chat_memory_mode="memory_primary",
                )

        investor = sim_data.agents["Agent_1"]
        self.assertEqual(
            sim_data.run_metadata["game_response_retry_policy"],
            "corrective_role_key_once_v1",
        )
        self.assertIn(
            'quoted decision key is "send"',
            investor.interaction_history[1]["prompt"],
        )
        self.assertFalse(
            any(
                "FORMAT CORRECTION" in message.get("content", "")
                for message in investor.messages
                if message.get("role") == "user"
            )
        )
        self.assertEqual(
            investor.messages[-2]["content"],
            'Respond exactly as JSON: {"send": amount}',
        )


if __name__ == "__main__":
    unittest.main()

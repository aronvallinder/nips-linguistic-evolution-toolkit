import unittest
from unittest.mock import patch

from games.trust_game_noisy import TrustGameNoisy
from src.simulation import SimulationData


class NoiseSemanticsCompatibilityTests(unittest.TestCase):
    def _game(self, noise_semantics):
        game = TrustGameNoisy(
            endowment=5,
            multiplier=3,
            system_prompt_template="Game rules",
            round1_investor_template="Send an amount.",
            round1_trustee_template="Return after seeing {sent}.",
            later_investor_template="Round {turn}: send an amount.",
            later_trustee_template=(
                "Round {turn}: current send is {current_round_sent}."
            ),
            noise_config={
                "type": "uniform",
                "range": 1,
                "direction": "both",
                "applies_to": "both",
                "inform_agents": True,
            },
            noise_semantics=noise_semantics,
            history_policy="none",
        )
        game.configure_agents(["Agent_1", "Agent_2"])
        return game

    @staticmethod
    def _state():
        state = SimulationData()
        state.game_data = {
            "balances": {"Agent_1": 5, "Agent_2": 5},
            "balances_communicated": {"Agent_1": 5, "Agent_2": 5},
            "pending_sents": {},
            "pending_sents_communicated": {},
        }
        state.conversation_history = [{"round": 2}]
        return state

    def test_environmental_noise_changes_the_ledger_after_each_decision(self):
        game = self._game("environmental")
        state = self._state()

        game.process_intermediate_response(
            "Agent_2",
            '{"send": 2.5}',
            2,
            state,
        )
        with patch.object(
            game,
            "_apply_noise",
            side_effect=[(3.25, 2.5), (3.5, 4.0)],
        ):
            receiver_prompt = game.get_game_prompt_later_round(
                "Agent_1",
                2,
                state,
                {},
            )
            game.process_turn(
                2,
                {
                    "Agent_2": {"content": '{"send": 2.5}'},
                    "Agent_1": {"content": '{"return": 4}'},
                },
                state,
            )

        self.assertIn("3.25", receiver_prompt)
        entry = state.conversation_history[0]
        self.assertEqual(entry["sent_decision"], 2.5)
        self.assertEqual(entry["sent"], 3.25)
        self.assertEqual(entry["received"], 9.75)
        self.assertEqual(entry["returned_decision"], 4.0)
        self.assertEqual(entry["returned"], 3.5)
        self.assertEqual(entry["sent_communicated"], entry["sent"])
        self.assertEqual(entry["returned_communicated"], entry["returned"])
        self.assertEqual(
            state.game_data["balances"],
            state.game_data["balances_communicated"],
        )
        self.assertEqual(state.game_data["balances"]["Agent_2"], 10.25)
        self.assertEqual(state.game_data["balances"]["Agent_1"], 11.25)

    def test_system_prompt_describes_the_selected_noise_semantics(self):
        environmental = self._game("environmental").get_system_prompt(
            "Agent_1",
            None,
        )
        communication = self._game("communication").get_system_prompt(
            "Agent_1",
            None,
        )

        self.assertIn("perturbed by the environment", environmental)
        self.assertIn("earnings are based on the amounts that actually arrive", environmental)
        self.assertNotIn("communication noise", environmental)
        self.assertIn("communication noise", communication)
        self.assertIn("amounts you see may differ", communication)
        self.assertNotIn("perturbed by the environment", communication)


if __name__ == "__main__":
    unittest.main()

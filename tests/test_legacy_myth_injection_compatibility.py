import unittest

from experiments.run_noisy_batch import NoisyExperimentConfig
from games.trust_game_noisy import TrustGameNoisy
from src.simulation import SimulationData


class LegacyMythInjectionCompatibilityTests(unittest.TestCase):
    def _game(self, mode):
        game = TrustGameNoisy(
            endowment=5,
            multiplier=3,
            system_prompt_template="Rules",
            round1_investor_template=(
                "{other_agent_last_myth_block}Choose a send."
            ),
            round1_trustee_template="Return after {sent}.",
            later_investor_template="Choose a send.",
            later_trustee_template="Return after {current_round_sent}.",
            myth_injection_mode=mode,
            history_policy="none",
        )
        game.configure_agents(["Agent_1", "Agent_2"])
        state = SimulationData()
        state.conversation_history = [
            {
                "round": 1,
                "myths": {
                    "Agent_1": "The sender kept the lantern.",
                    "Agent_2": "The receiver shared the flame.",
                },
            }
        ]
        game.sim_data_ref = state
        return game

    def test_partner_and_own_modes_remain_available(self):
        partner_prompt = self._game("partner").get_game_prompt_round_1(
            "Agent_1",
            None,
            1,
        )
        own_prompt = self._game("own").get_game_prompt_round_1(
            "Agent_1",
            None,
            1,
        )

        self.assertIn("The receiver shared the flame.", partner_prompt)
        self.assertNotIn("The sender kept the lantern.", partner_prompt)
        self.assertIn("The sender kept the lantern.", own_prompt)
        self.assertNotIn("The receiver shared the flame.", own_prompt)

    def test_legacy_and_corrected_config_cells_coexist(self):
        config = NoisyExperimentConfig("config/experiments_noisy.yaml")

        legacy = config.get_experiment_combinations(
            "gpt5nano_smoke_partner_myth_own",
            max_runs=1,
        )
        corrected = config.get_experiment_combinations(
            "noise2i_memprimary_v2_game",
            max_runs=1,
        )

        self.assertEqual(legacy[0]["myth_injection_mode"], "own")
        self.assertEqual(legacy[0]["noise_semantics"], "environmental")
        self.assertEqual(corrected[0]["game_params"]["num_agents"], 2)
        self.assertEqual(corrected[0]["noise_semantics"], "communication")

    def test_unknown_injection_mode_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "myth_injection_mode"):
            self._game("unknown")


if __name__ == "__main__":
    unittest.main()

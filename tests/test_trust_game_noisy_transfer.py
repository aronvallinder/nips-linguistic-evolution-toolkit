import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

from experiments.run_noisy_batch import NoisyExperimentConfig, resolve_protocol_seeds
from games.trust_game_noisy import TrustGameNoisy
from src.simulation import SimulationData


MYTH_DECISION_LINK = (
    "Take any myths written in this session into account when making your decision."
)


def build_game(
    num_agents=2,
    game_prompt_addition="",
    history_policy="none",
    self_history_window=0,
    coplayer_history_window=0,
    population_history_window=0,
    show_agent_names=True,
    pairing_mode="balanced",
    pairing_seed=None,
    noise_seed=None,
    prompt_regime="legacy",
    noise_semantics="communication",
):
    game = TrustGameNoisy(
        endowment=5,
        multiplier=3,
        system_prompt_template="Game rules",
        round1_investor_template="Send an amount.",
        round1_trustee_template="Return after seeing {sent}.",
        later_investor_template="Round {turn}: send an amount.",
        later_trustee_template="Round {turn}: current send is {current_round_sent}.",
        noise_config={
            "type": "uniform",
            "range": 1,
            "direction": "both",
            "applies_to": "sent",
        },
        noise_semantics=noise_semantics,
        history_policy=history_policy,
        self_history_window=self_history_window,
        coplayer_history_window=coplayer_history_window,
        population_history_window=population_history_window,
        show_agent_names=show_agent_names,
        game_prompt_addition=game_prompt_addition,
        pairing_mode=pairing_mode,
        pairing_seed=pairing_seed,
        noise_seed=noise_seed,
        prompt_regime=prompt_regime,
    )
    agent_ids = [f"Agent_{index}" for index in range(1, num_agents + 1)]
    game.configure_agents(agent_ids)
    return game


def build_dyad_state():
    sim_data = SimulationData()
    sim_data.game_data = {
        "balances": {"Agent_1": 5, "Agent_2": 5},
        "balances_communicated": {"Agent_1": 5, "Agent_2": 5},
        "pending_sents": {},
        "pending_sents_communicated": {},
    }
    sim_data.conversation_history = [
        {
            "round": 1,
            "dyads": [
                {
                    "round": 1,
                    "dyad_id": "dyad_1",
                    "agents": ["Agent_1", "Agent_2"],
                    "investor": "Agent_1",
                    "trustee": "Agent_2",
                    "roles": {
                        "Agent_1": "investor",
                        "Agent_2": "trustee",
                    },
                    "sent": 2,
                    "sent_communicated": 2.5,
                    "received": 6,
                    "received_communicated": 7.5,
                    "returned": 1,
                    "returned_communicated": 1,
                    "investor_payoff": 4,
                    "trustee_payoff": 5,
                    "payoffs_communicated": {
                        "Agent_1": 4,
                        "Agent_2": 6.5,
                    },
                }
            ],
        }
    ]
    return sim_data


def build_multi_agent_state():
    sim_data = SimulationData()
    agent_ids = [f"Agent_{index}" for index in range(1, 9)]
    sim_data.game_data = {
        "balances": {agent_id: 5 for agent_id in agent_ids},
        "balances_communicated": {agent_id: 5 for agent_id in agent_ids},
        "pending_sents": {},
        "pending_sents_communicated": {},
    }
    sim_data.conversation_history = [
        {
            "round": 2,
            "pairings": [
                {
                    "dyad_id": "dyad_1",
                    "investor": "Agent_1",
                    "trustee": "Agent_2",
                },
                {
                    "dyad_id": "dyad_2",
                    "investor": "Agent_3",
                    "trustee": "Agent_4",
                },
                {
                    "dyad_id": "dyad_3",
                    "investor": "Agent_5",
                    "trustee": "Agent_6",
                },
                {
                    "dyad_id": "dyad_4",
                    "investor": "Agent_7",
                    "trustee": "Agent_8",
                },
            ],
        }
    ]
    return sim_data


def build_population_ledger_state():
    sim_data = SimulationData()
    agent_ids = [f"Agent_{index}" for index in range(1, 9)]
    sim_data.game_data = {
        "balances": {agent_id: 5 for agent_id in agent_ids},
        "balances_communicated": {agent_id: 5 for agent_id in agent_ids},
        "pending_sents": {},
        "pending_sents_communicated": {},
    }
    dyads = []
    for index in range(4):
        investor_id = agent_ids[index * 2]
        trustee_id = agent_ids[index * 2 + 1]
        dyads.append(
            {
                "round": 1,
                "dyad_id": f"dyad_{index + 1}",
                "agents": [investor_id, trustee_id],
                "investor": investor_id,
                "trustee": trustee_id,
                "roles": {
                    investor_id: "investor",
                    trustee_id: "trustee",
                },
                "sent": round(0.1 + index, 2),
                "sent_communicated": round(4.1 + index / 10, 2),
                "received": round((0.1 + index) * 3, 2),
                "received_communicated": round((4.1 + index / 10) * 3, 2),
                "returned": round(0.2 + index, 2),
                "returned_communicated": round(1.2 + index / 10, 2),
                "payoffs_communicated": {
                    investor_id: 5,
                    trustee_id: 5,
                },
            }
        )
    sim_data.conversation_history = [{"round": 1, "dyads": dyads}]
    sim_data.run_metadata["num_turns"] = 10
    return sim_data


class NoisyDyadTransferPromptTests(unittest.TestCase):
    def setUp(self):
        self.game = build_game()
        self.sim_data = build_dyad_state()

    def test_investor_prompt_does_not_generate_or_cache_transfer_noise(self):
        with patch.object(
            self.game, "_apply_noise", wraps=self.game._apply_noise
        ) as apply_noise:
            prompt = self.game.get_game_prompt_later_round(
                "Agent_2", 2, self.sim_data, {}
            )

        self.assertIn("send an amount", prompt)
        apply_noise.assert_not_called()
        self.assertEqual(self.sim_data.game_data["pending_sents_communicated"], {})

    def test_trustee_prompt_requires_the_current_actual_send(self):
        with self.assertRaisesRegex(ValueError, "Investor should have responded first"):
            self.game.get_game_prompt_later_round("Agent_1", 2, self.sim_data, {})

        self.assertEqual(self.sim_data.game_data["pending_sents_communicated"], {})

    def test_trustee_noise_is_based_on_actual_send_and_cached_once(self):
        self.game.process_intermediate_response(
            "Agent_2", '{"send": 2.5}', 2, self.sim_data
        )

        with patch.object(
            self.game, "_apply_noise", return_value=(3.25, 2.5)
        ) as apply_noise:
            first_prompt = self.game.get_game_prompt_later_round(
                "Agent_1", 2, self.sim_data, {}
            )
            second_prompt = self.game.get_game_prompt_later_round(
                "Agent_1", 2, self.sim_data, {}
            )

        apply_noise.assert_called_once_with(2.5, 5)
        self.assertIn("current send is 3.25", first_prompt)
        self.assertEqual(first_prompt, second_prompt)
        self.assertEqual(
            self.sim_data.game_data["pending_sents_communicated"]["dyad_1"],
            3.25,
        )


class NoisyMultiAgentTransferPromptTests(unittest.TestCase):
    def test_multi_agent_path_has_the_same_sender_then_receiver_contract(self):
        game = build_game(num_agents=8)
        sim_data = build_multi_agent_state()

        with patch.object(
            game, "_apply_noise", return_value=(3.25, 2.5)
        ) as apply_noise:
            game.get_game_prompt_later_round("Agent_1", 2, sim_data, {})
            apply_noise.assert_not_called()

            with self.assertRaisesRegex(
                ValueError, "Investor should have responded first"
            ):
                game.get_game_prompt_later_round("Agent_2", 2, sim_data, {})

            game.process_intermediate_response(
                "Agent_1", '{"send": 2.5}', 2, sim_data
            )
            trustee_prompt = game.get_game_prompt_later_round(
                "Agent_2", 2, sim_data, {}
            )

        apply_noise.assert_called_once_with(2.5, 5)
        self.assertIn("They sent you $3.25", trustee_prompt)


class PairingAndPromptRegimeTests(unittest.TestCase):
    def test_fixed_pairing_keeps_partners_and_swaps_roles(self):
        game = build_game(num_agents=8, pairing_mode="fixed")
        sim_data = SimulationData()

        round_1 = game.get_round_pairings(1, sim_data)
        round_2 = game.get_round_pairings(2, sim_data)

        self.assertEqual(
            [pairing["agents"] for pairing in round_1],
            [
                ["Agent_1", "Agent_2"],
                ["Agent_3", "Agent_4"],
                ["Agent_5", "Agent_6"],
                ["Agent_7", "Agent_8"],
            ],
        )
        self.assertEqual(round_1[0]["investor"], "Agent_1")
        self.assertEqual(round_2[0]["investor"], "Agent_2")
        self.assertEqual(set(round_1[0]["agents"]), set(round_2[0]["agents"]))

    def test_fixed_system_prompt_is_truthful(self):
        game = build_game(
            num_agents=8,
            pairing_mode="fixed",
            prompt_regime="unified",
            show_agent_names=False,
        )

        prompt = game.get_system_prompt("Agent_1", None)

        self.assertIn("There are 8 agents", prompt)
        self.assertIn("same opponent throughout the run", prompt)
        self.assertIn("roles alternate every round", prompt)
        self.assertNotIn("Pairings are randomized", prompt)

    def test_unified_dyad_uses_population_prompt_and_shared_later_builder(self):
        game = build_game(
            prompt_regime="unified",
            pairing_mode="fixed",
            show_agent_names=False,
        )
        sim_data = build_dyad_state()

        system_prompt = game.get_system_prompt("Agent_1", None)
        later_prompt = game.get_game_prompt_later_round(
            "Agent_2", 2, sim_data, {}
        )

        self.assertIn("There are 2 agents", system_prompt)
        self.assertIn("same opponent throughout the run", system_prompt)
        self.assertIn("This round, you are the SENDER", later_prompt)
        self.assertIn("Respond exactly as JSON", later_prompt)
        self.assertNotIn("Round 2: send an amount", later_prompt)

    def test_unified_fixed_2_and_8_render_identical_decision_prompts(self):
        dyad_game = build_game(
            prompt_regime="unified",
            pairing_mode="fixed",
            noise_seed=31,
            show_agent_names=False,
        )
        population_game = build_game(
            num_agents=8,
            prompt_regime="unified",
            pairing_mode="fixed",
            noise_seed=31,
            show_agent_names=False,
        )
        dyad_state = build_dyad_state()
        population_state = SimulationData()
        population_state.game_data = {
            "balances": {
                f"Agent_{index}": 5 for index in range(1, 9)
            },
            "balances_communicated": {
                f"Agent_{index}": 5 for index in range(1, 9)
            },
            "pending_sents": {},
            "pending_sents_communicated": {},
        }

        dyad_investor = dyad_game.get_game_prompt_later_round(
            "Agent_2", 2, dyad_state, {}
        )
        population_investor = population_game.get_game_prompt_later_round(
            "Agent_2", 2, population_state, {}
        )
        dyad_game.process_intermediate_response(
            "Agent_2", '{"send": 2.5}', 2, dyad_state
        )
        population_game.process_intermediate_response(
            "Agent_2", '{"send": 2.5}', 2, population_state
        )
        dyad_trustee = dyad_game.get_game_prompt_later_round(
            "Agent_1", 2, dyad_state, {}
        )
        population_trustee = population_game.get_game_prompt_later_round(
            "Agent_1", 2, population_state, {}
        )

        self.assertEqual(dyad_investor, population_investor)
        self.assertEqual(dyad_trustee, population_trustee)
        self.assertEqual(
            dyad_game.get_system_prompt("Agent_1", None).replace(
                "There are 2 agents", "There are 8 agents"
            ),
            population_game.get_system_prompt("Agent_1", None),
        )

    def test_history_policies_have_explicit_nonoverlapping_meanings(self):
        sim_data = build_dyad_state()

        no_history = build_game(
            num_agents=8,
            history_policy="none",
        )._format_multi_agent_history(
            "Agent_1", "Agent_2", 2, sim_data
        )
        zero_windows = build_game(
            num_agents=8,
            history_policy="self_and_coplayer",
            self_history_window=0,
            coplayer_history_window=0,
        )._format_multi_agent_history(
            "Agent_1", "Agent_2", 2, sim_data
        )
        minimal = build_game(
            num_agents=8,
            history_policy="minimal",
        )._format_multi_agent_history(
            "Agent_1", "Agent_2", 2, sim_data
        )

        self.assertEqual(no_history, "")
        self.assertEqual(zero_windows, "")
        self.assertIn("most recent previous game round", minimal)

    def test_population_ledger_uses_stable_ids_and_only_communicated_values(self):
        game = build_game(
            num_agents=8,
            history_policy="population_ledger",
            population_history_window=3,
            show_agent_names=False,
            pairing_mode="fixed",
        )
        sim_data = build_population_ledger_state()

        history = game._format_multi_agent_history(
            "Agent_2", "Agent_1", 2, sim_data
        )
        prompt = game.get_game_prompt_later_round(
            "Agent_2", 2, sim_data, {}
        )

        self.assertEqual(history.count("- Round 1:"), 4)
        self.assertIn("Member A (SENDER) sent $4.1 to Member B", history)
        self.assertIn("Member B returned $1.2", history)
        self.assertNotIn("sent $0.1", history)
        self.assertNotIn("returned $0.2", history)
        self.assertIn("Your stable public ID is Member B", prompt)
        self.assertIn(
            "current co-player's stable public ID is Member A",
            prompt,
        )
        self.assertIn("does not reveal hidden true amounts", prompt)
        self.assertNotIn("Agent_1", prompt)
        self.assertNotIn("Agent_2", prompt)

    def test_population_ledger_has_no_prior_entries_in_round_one(self):
        game = build_game(
            num_agents=8,
            history_policy="population_ledger",
            population_history_window=3,
            show_agent_names=False,
            pairing_mode="fixed",
        )
        game.get_round_pairings(1, SimulationData())

        prompt = game.get_game_prompt_round_1("Agent_1", None, 1)

        self.assertIn("Your stable public ID is Member A", prompt)
        self.assertNotIn("- Round 1:", prompt)

    def test_population_ledger_fails_closed_without_a_positive_window(self):
        with self.assertRaisesRegex(ValueError, "population_history_window"):
            build_game(
                num_agents=8,
                history_policy="population_ledger",
                population_history_window=0,
            )

    def test_stable_ids_identify_current_pair_without_history(self):
        game = build_game(
            num_agents=8,
            history_policy="stable_ids",
            show_agent_names=False,
            pairing_mode="fixed",
        )
        sim_data = build_population_ledger_state()

        prompt = game.get_game_prompt_later_round(
            "Agent_2", 2, sim_data, {}
        )

        self.assertIn("Your stable population ID is Member B", prompt)
        self.assertIn(
            "current co-player's stable population ID is Member A",
            prompt,
        )
        self.assertIn("No population-wide interaction history is shown", prompt)
        self.assertNotIn("- Round 1:", prompt)
        self.assertNotIn("sent $4.1", prompt)
        self.assertNotIn("Agent_1", prompt)

    def test_anonymous_population_record_shows_social_information_without_ids(self):
        game = build_game(
            num_agents=8,
            history_policy="anonymous_population_record",
            population_history_window=3,
            show_agent_names=False,
            pairing_mode="fixed",
        )
        sim_data = build_population_ledger_state()

        prompt = game.get_game_prompt_later_round(
            "Agent_2", 2, sim_data, {}
        )

        self.assertEqual(prompt.count("- Round 1, Pair"), 4)
        self.assertIn("Pair 1: a sender sent $4.1", prompt)
        self.assertIn("receiver returned $1.2", prompt)
        self.assertNotIn("sent $0.1", prompt)
        self.assertNotIn("Member A", prompt)
        self.assertNotIn("Member B", prompt)
        self.assertIn("cannot identify your current co-player", prompt)
        self.assertIn("does not reveal hidden true amounts", prompt)

    def test_round_local_pair_ids_cannot_track_agents(self):
        game = build_game(
            num_agents=8,
            history_policy="relative_pair_ids",
            show_agent_names=False,
            pairing_mode="fixed",
        )
        sim_data = build_population_ledger_state()

        prompt = game.get_game_prompt_later_round(
            "Agent_2", 2, sim_data, {}
        )

        self.assertIn("Your round-local pair ID is Member Self", prompt)
        self.assertIn("pair ID is Member Other", prompt)
        self.assertIn("reassigned every round", prompt)
        self.assertIn("No population-wide interaction history is shown", prompt)
        self.assertNotIn("Member A", prompt)
        self.assertNotIn("Member B", prompt)
        self.assertNotIn("- Round 1:", prompt)

    def test_invalid_protocol_enums_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "history_policy"):
            build_game(history_policy="typo")
        with self.assertRaisesRegex(ValueError, "pairing_mode"):
            build_game(pairing_mode="typo")
        with self.assertRaisesRegex(ValueError, "prompt_regime"):
            build_game(prompt_regime="typo")
        with self.assertRaisesRegex(ValueError, "noise_semantics"):
            build_game(noise_semantics="typo")

    def test_seeded_pairing_and_noise_are_reproducible(self):
        first_game = build_game(
            num_agents=8,
            pairing_seed=17,
            noise_seed=23,
        )
        second_game = build_game(
            num_agents=8,
            pairing_seed=17,
            noise_seed=23,
        )
        first_state = SimulationData()
        first_state.run_metadata["num_turns"] = 10
        second_state = SimulationData()
        second_state.run_metadata["num_turns"] = 10

        first_schedule = [
            first_game.get_round_pairings(turn, first_state)
            for turn in range(1, 11)
        ]
        second_schedule = [
            second_game.get_round_pairings(turn, second_state)
            for turn in range(1, 11)
        ]
        first_noise = first_game._apply_noise_for_event(
            2.5,
            5,
            turn=4,
            dyad_id="dyad_2",
            action_type="sent",
        )
        second_noise = second_game._apply_noise_for_event(
            2.5,
            5,
            turn=4,
            dyad_id="dyad_2",
            action_type="sent",
        )

        self.assertEqual(first_schedule, second_schedule)
        self.assertEqual(first_noise, second_noise)

    def test_seeded_pairing_is_stable_across_python_hash_seeds(self):
        repository_root = Path(__file__).resolve().parents[1]
        script = """
import json

from games.dyadic_pairing import DyadicPairingMixin
from src.simulation import SimulationData

game = DyadicPairingMixin()
game.set_pairing_mode("balanced")
game.set_pairing_seed(202608121)
game.set_defector_options(defector_ratio=0)
game._init_dyadic_agents()
game.configure_agents([f"Agent_{index}" for index in range(1, 9)])
state = SimulationData()
state.run_metadata["num_turns"] = 10
schedule = [game.get_round_pairings(turn, state) for turn in range(1, 11)]
print(json.dumps(schedule, sort_keys=True))
"""
        schedules = []
        for hash_seed in ("1", "2", "3"):
            environment = os.environ.copy()
            environment["PYTHONHASHSEED"] = hash_seed
            completed = subprocess.run(
                [sys.executable, "-c", script],
                cwd=repository_root,
                env=environment,
                check=True,
                capture_output=True,
                text=True,
            )
            schedules.append(completed.stdout.strip())

        self.assertEqual(len(set(schedules)), 1)


class MythDecisionLinkPromptTests(unittest.TestCase):
    def assert_link_once(self, prompt):
        self.assertEqual(prompt.count(MYTH_DECISION_LINK), 1)

    def test_dyad_round1_and_later_prompts_each_include_link_once(self):
        game = build_game(game_prompt_addition=MYTH_DECISION_LINK)

        self.assert_link_once(game.get_game_prompt_round_1("Agent_1", None, 1))

        round1_state = build_dyad_state()
        game.process_intermediate_response(
            "Agent_1", '{"send": 2.5}', 1, round1_state
        )
        self.assert_link_once(
            game.get_game_prompt_round_1("Agent_2", None, 1)
        )

        later_state = build_dyad_state()
        self.assert_link_once(
            game.get_game_prompt_later_round("Agent_2", 2, later_state, {})
        )
        game.process_intermediate_response(
            "Agent_2", '{"send": 2.5}', 2, later_state
        )
        self.assert_link_once(
            game.get_game_prompt_later_round("Agent_1", 2, later_state, {})
        )

    def test_multi_agent_later_prompts_each_include_link_once(self):
        game = build_game(
            num_agents=8,
            game_prompt_addition=MYTH_DECISION_LINK,
        )
        sim_data = build_multi_agent_state()

        self.assert_link_once(
            game.get_game_prompt_later_round("Agent_1", 2, sim_data, {})
        )
        game.process_intermediate_response(
            "Agent_1", '{"send": 2.5}', 2, sim_data
        )
        self.assert_link_once(
            game.get_game_prompt_later_round("Agent_2", 2, sim_data, {})
        )


class CorrectedV2ConfigTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = NoisyExperimentConfig("config/experiments_noisy.yaml")

    def test_v2_cells_match_three_round_memory_horizon(self):
        expected = {
            "noise2i_memprimary_v2_game": (2, 3),
            "noise2i_memprimary_v2_game_myth": (2, 6),
            "noise2i_memprimary_v2_myth_game": (2, 6),
            "noise8i_memprimary_v2_game": (8, 3),
            "noise8i_memprimary_v2_game_myth": (8, 6),
            "noise8i_memprimary_v2_myth_game": (8, 6),
        }

        for experiment_name, (num_agents, memory_capacity) in expected.items():
            with self.subTest(experiment_name=experiment_name):
                combinations = self.config.get_experiment_combinations(
                    experiment_name
                )
                self.assertEqual(len(combinations), 10)
                self.assertTrue(
                    all(
                        combo["game_params"]["num_agents"] == num_agents
                        and combo["game_params"]["memory_capacity"]
                        == memory_capacity
                        for combo in combinations
                    )
                )

    def test_v2_myth_cells_use_runtime_link_not_template_mutation(self):
        myth_cells = [
            "noise2i_memprimary_v2_game_myth",
            "noise2i_memprimary_v2_myth_game",
            "noise8i_memprimary_v2_game_myth",
            "noise8i_memprimary_v2_myth_game",
        ]
        template_keys = [
            "trust_game_round1_investor",
            "trust_game_round1_trustee",
            "trust_game_later_investor",
            "trust_game_later_trustee",
        ]

        for experiment_name in myth_cells:
            with self.subTest(experiment_name=experiment_name):
                combo = self.config.get_experiment_combinations(
                    experiment_name
                )[0]
                self.assertEqual(
                    combo["game_prompt_addition"],
                    MYTH_DECISION_LINK,
                )
                self.assertEqual(
                    combo["game_prompt_addition_id"],
                    "myth_decision_link",
                )
                self.assertTrue(
                    all(
                        MYTH_DECISION_LINK not in combo[key]
                        for key in template_keys
                    )
                )

        game_only = self.config.get_experiment_combinations(
            "noise2i_memprimary_v2_game"
        )[0]
        self.assertEqual(game_only["game_prompt_addition"], "")
        self.assertIsNone(game_only["game_prompt_addition_id"])

    def test_max_runs_limits_replicates_without_losing_replicate_id(self):
        combinations = self.config.get_experiment_combinations(
            "noise8i_memprimary_v2_myth_game",
            max_runs=1,
        )

        self.assertEqual(len(combinations), 1)
        self.assertEqual(combinations[0]["replicate_id"], 0)

        with self.assertRaisesRegex(ValueError, "at least 1"):
            self.config.get_experiment_combinations(
                "noise8i_memprimary_v2_myth_game",
                max_runs=0,
            )

    def test_explicit_replicate_ids_preserve_original_protocol_seeds(self):
        combinations = self.config.get_experiment_combinations(
            "noise8_history_gate_signed_gpt_n5_ownonly_myth_game_repair"
        )

        self.assertEqual(
            [combo["replicate_id"] for combo in combinations],
            [2, 4],
        )
        self.assertEqual(
            [resolve_protocol_seeds(combo["game_params"], combo) for combo in combinations],
            [(202608202, 202608202), (202608204, 202608204)],
        )

    def test_myth_boundary_repair_cells_target_only_invalid_replicates(self):
        expected_ids = {
            "noise8_crossmodel_signed_gpt_n5_game_myth_mythrepair": [1],
            "noise8_crossmodel_signed_gpt_n5_myth_game_mythrepair": [0],
            "noise8_history_gate_signed_gpt_n5_ownonly_game_myth_mythrepair": [
                0, 1, 2, 3, 4
            ],
            "noise8_history_gate_signed_gpt_n5_ownonly_myth_game_mythrepair": [
                0, 1, 2, 3, 4
            ],
        }
        for experiment_name, replicate_ids in expected_ids.items():
            with self.subTest(experiment_name=experiment_name):
                combinations = self.config.get_experiment_combinations(
                    experiment_name
                )
                self.assertEqual(
                    [combo["replicate_id"] for combo in combinations],
                    replicate_ids,
                )

    def test_history_confirmation_uses_independent_paired_replicates(self):
        experiment_names = [
            "noise8_history_confirm_gpt_n10_private_game",
            "noise8_history_confirm_gpt_n10_private_myth_game",
            "noise8_history_confirm_gpt_n10_dossier_game",
            "noise8_history_confirm_gpt_n10_dossier_myth_game",
        ]
        expected_ids = list(range(5, 15))
        for experiment_name in experiment_names:
            with self.subTest(experiment_name=experiment_name):
                combinations = self.config.get_experiment_combinations(
                    experiment_name
                )
                self.assertEqual(
                    [combo["replicate_id"] for combo in combinations],
                    expected_ids,
                )
                self.assertEqual(
                    [
                        resolve_protocol_seeds(combo["game_params"], combo)
                        for combo in combinations
                    ],
                    [
                        (202608200 + replicate_id, 202608200 + replicate_id)
                        for replicate_id in expected_ids
                    ],
                )

    def test_crossmodel_smoke_is_paired_and_matches_corrected_8agent_protocol(self):
        expected_orders = {
            "noise8_crossmodel_signed_smoke_game": ["game"],
            "noise8_crossmodel_signed_smoke_game_myth": ["game", "myth"],
            "noise8_crossmodel_signed_smoke_myth_game": ["myth", "game"],
        }
        expected_models = {
            "google/gemini-3.1-flash-lite",
            "openai/gpt-5-nano",
        }

        for experiment_name, task_order in expected_orders.items():
            with self.subTest(experiment_name=experiment_name):
                combinations = self.config.get_experiment_combinations(
                    experiment_name
                )
                self.assertEqual(len(combinations), 2)
                self.assertEqual(
                    {combo["model"] for combo in combinations},
                    expected_models,
                )
                for combo in combinations:
                    params = combo["game_params"]
                    self.assertEqual(combo["task_order"], task_order)
                    self.assertEqual(params["num_agents"], 8)
                    self.assertEqual(
                        params["memory_capacity"],
                        3 if task_order == ["game"] else 6,
                    )
                    self.assertEqual(params["history_policy"], "self_and_coplayer")
                    self.assertEqual(params["coplayer_history_window"], 3)
                    self.assertFalse(params["show_agent_names"])
                    self.assertTrue(params["paired_protocol_seeds"])
                    self.assertEqual(params["protocol_seed_base"], 202608200)
                    self.assertEqual(
                        params["noise_config"],
                        {
                            "type": "uniform",
                            "range": 1.0,
                            "direction": "both",
                            "applies_to": "both",
                            "inform_agents": True,
                        },
                    )
                    self.assertEqual(
                        bool(combo["game_prompt_addition"]),
                        "myth" in task_order,
                    )

    def test_crossmodel_gpt_n5_expansion_uses_five_matched_replicates(self):
        expected_orders = {
            "noise8_crossmodel_signed_gpt_n5_game": ["game"],
            "noise8_crossmodel_signed_gpt_n5_game_myth": ["game", "myth"],
            "noise8_crossmodel_signed_gpt_n5_myth_game": ["myth", "game"],
        }

        for experiment_name, task_order in expected_orders.items():
            with self.subTest(experiment_name=experiment_name):
                combinations = self.config.get_experiment_combinations(
                    experiment_name
                )
                self.assertEqual(len(combinations), 5)
                self.assertEqual(
                    {combo["model"] for combo in combinations},
                    {"openai/gpt-5-nano"},
                )
                self.assertEqual(
                    {combo["replicate_id"] for combo in combinations},
                    set(range(5)),
                )
                self.assertEqual(
                    {
                        resolve_protocol_seeds(combo["game_params"], combo)
                        for combo in combinations
                    },
                    {
                        (seed, seed)
                        for seed in range(202608200, 202608205)
                    },
                )
                self.assertTrue(
                    all(combo["task_order"] == task_order for combo in combinations)
                )

    def test_history_gate_ownonly_differs_only_in_partner_dossier_fields(self):
        matched_sets = [
            (
                "noise8_history_gate_signed_gpt_n5_ownonly_game",
                "noise8_crossmodel_signed_gpt_n5_game",
            ),
            (
                "noise8_history_gate_signed_gpt_n5_ownonly_game_myth",
                "noise8_crossmodel_signed_gpt_n5_game_myth",
            ),
            (
                "noise8_history_gate_signed_gpt_n5_ownonly_myth_game",
                "noise8_crossmodel_signed_gpt_n5_myth_game",
            ),
        ]

        for own_set, partner_set in matched_sets:
            with self.subTest(own_set=own_set, partner_set=partner_set):
                own_combinations = self.config.get_experiment_combinations(own_set)
                partner_combinations = self.config.get_experiment_combinations(
                    partner_set
                )
                self.assertEqual(len(own_combinations), 5)
                self.assertEqual(len(partner_combinations), 5)

                own_params = dict(own_combinations[0]["game_params"])
                partner_params = dict(partner_combinations[0]["game_params"])
                self.assertEqual(own_params.pop("history_policy"), "none")
                self.assertEqual(
                    partner_params.pop("history_policy"),
                    "self_and_coplayer",
                )
                self.assertEqual(own_params.pop("coplayer_history_window"), 0)
                self.assertEqual(partner_params.pop("coplayer_history_window"), 3)
                self.assertEqual(own_params, partner_params)
                self.assertEqual(
                    [
                        resolve_protocol_seeds(combo["game_params"], combo)
                        for combo in own_combinations
                    ],
                    [
                        resolve_protocol_seeds(combo["game_params"], combo)
                        for combo in partner_combinations
                    ],
                )

    def test_population_ledger_smoke_is_exact_seed_matched_and_public(self):
        combinations = self.config.get_experiment_combinations(
            "noise8_population_ledger_signed_gpt_smoke_game"
        )

        self.assertEqual(len(combinations), 2)
        self.assertEqual(
            {combo["replicate_id"] for combo in combinations},
            {0, 1},
        )
        for combo in combinations:
            params = combo["game_params"]
            self.assertEqual(combo["model"], "openai/gpt-5-nano")
            self.assertEqual(combo["task_order"], ["game"])
            self.assertEqual(params["num_agents"], 8)
            self.assertEqual(params["memory_capacity"], 3)
            self.assertEqual(params["history_policy"], "population_ledger")
            self.assertEqual(params["population_history_window"], 3)
            self.assertEqual(params["self_history_window"], 0)
            self.assertEqual(params["coplayer_history_window"], 0)
            self.assertFalse(params["show_agent_names"])
            self.assertEqual(
                resolve_protocol_seeds(params, combo),
                (
                    202608200 + combo["replicate_id"],
                    202608200 + combo["replicate_id"],
                ),
            )

        extension = self.config.get_experiment_combinations(
            "noise8_population_ledger_signed_gpt_n5_extension_game"
        )
        self.assertEqual(
            {combo["replicate_id"] for combo in extension},
            {2, 3, 4},
        )
        self.assertTrue(
            all(
                combo["game_params"]["history_policy"]
                == "population_ledger"
                for combo in extension
            )
        )
        self.assertEqual(
            {
                resolve_protocol_seeds(combo["game_params"], combo)
                for combo in extension
            },
            {
                (202608202, 202608202),
                (202608203, 202608203),
                (202608204, 202608204),
            },
        )

        myth_game = self.config.get_experiment_combinations(
            "noise8_population_ledger_signed_gpt_n5_myth_game"
        )
        self.assertEqual(len(myth_game), 5)
        self.assertEqual(
            {combo["replicate_id"] for combo in myth_game},
            set(range(5)),
        )
        for combo in myth_game:
            params = combo["game_params"]
            self.assertEqual(combo["task_order"], ["myth", "game"])
            self.assertEqual(params["memory_capacity"], 6)
            self.assertEqual(params["history_policy"], "population_ledger")
            self.assertEqual(params["population_history_window"], 3)
            self.assertEqual(
                resolve_protocol_seeds(params, combo),
                (
                    202608200 + combo["replicate_id"],
                    202608200 + combo["replicate_id"],
                ),
            )

        stable_ids = self.config.get_experiment_combinations(
            "noise8_stable_ids_signed_gpt_n5_game"
        )
        self.assertEqual(len(stable_ids), 5)
        self.assertEqual(
            {combo["replicate_id"] for combo in stable_ids},
            set(range(5)),
        )
        for combo in stable_ids:
            params = combo["game_params"]
            self.assertEqual(combo["task_order"], ["game"])
            self.assertEqual(params["memory_capacity"], 3)
            self.assertEqual(params["history_policy"], "stable_ids")
            self.assertEqual(params["population_history_window"], 0)
            self.assertFalse(params["show_agent_names"])
            self.assertEqual(
                resolve_protocol_seeds(params, combo),
                (
                    202608200 + combo["replicate_id"],
                    202608200 + combo["replicate_id"],
                ),
            )

        anonymous_record = self.config.get_experiment_combinations(
            "noise8_anonymous_record_signed_gpt_n5_game"
        )
        self.assertEqual(len(anonymous_record), 5)
        self.assertEqual(
            {combo["replicate_id"] for combo in anonymous_record},
            set(range(5)),
        )
        for combo in anonymous_record:
            params = combo["game_params"]
            self.assertEqual(combo["task_order"], ["game"])
            self.assertEqual(
                params["history_policy"],
                "anonymous_population_record",
            )
            self.assertEqual(params["population_history_window"], 3)
            self.assertFalse(params["show_agent_names"])
            self.assertEqual(
                resolve_protocol_seeds(params, combo),
                (
                    202608200 + combo["replicate_id"],
                    202608200 + combo["replicate_id"],
                ),
            )

        stable_confirmation = self.config.get_experiment_combinations(
            "noise8_identity_persistence_confirm_gpt_n10_stable"
        )
        relative_confirmation = self.config.get_experiment_combinations(
            "noise8_identity_persistence_confirm_gpt_n10_relative"
        )
        self.assertEqual(len(stable_confirmation), 10)
        self.assertEqual(len(relative_confirmation), 10)
        expected_confirmation_ids = set(range(15, 25))
        self.assertEqual(
            {combo["replicate_id"] for combo in stable_confirmation},
            expected_confirmation_ids,
        )
        self.assertEqual(
            {combo["replicate_id"] for combo in relative_confirmation},
            expected_confirmation_ids,
        )
        for stable_combo, relative_combo in zip(
            stable_confirmation,
            relative_confirmation,
        ):
            stable_params = dict(stable_combo["game_params"])
            relative_params = dict(relative_combo["game_params"])
            self.assertEqual(stable_params.pop("history_policy"), "stable_ids")
            self.assertEqual(
                relative_params.pop("history_policy"),
                "relative_pair_ids",
            )
            self.assertEqual(stable_params, relative_params)
            self.assertEqual(
                resolve_protocol_seeds(stable_combo["game_params"], stable_combo),
                resolve_protocol_seeds(
                    relative_combo["game_params"],
                    relative_combo,
                ),
            )

        gemini_stable = self.config.get_experiment_combinations(
            "noise8_identity_persistence_gemini_n5_stable"
        )
        gemini_relative = self.config.get_experiment_combinations(
            "noise8_identity_persistence_gemini_n5_relative"
        )
        self.assertEqual(len(gemini_stable), 5)
        self.assertEqual(len(gemini_relative), 5)
        expected_gemini_ids = list(range(25, 30))
        self.assertEqual(
            [combo["replicate_id"] for combo in gemini_stable],
            expected_gemini_ids,
        )
        self.assertEqual(
            [combo["replicate_id"] for combo in gemini_relative],
            expected_gemini_ids,
        )
        for stable_combo, relative_combo in zip(gemini_stable, gemini_relative):
            self.assertEqual(stable_combo["model"], "google/gemini-3.1-flash-lite")
            self.assertEqual(relative_combo["model"], "google/gemini-3.1-flash-lite")
            stable_params = dict(stable_combo["game_params"])
            relative_params = dict(relative_combo["game_params"])
            self.assertEqual(stable_params.pop("history_policy"), "stable_ids")
            self.assertEqual(
                relative_params.pop("history_policy"),
                "relative_pair_ids",
            )
            self.assertEqual(stable_params, relative_params)
            self.assertEqual(
                resolve_protocol_seeds(stable_combo["game_params"], stable_combo),
                (202608200 + stable_combo["replicate_id"],) * 2,
            )
            self.assertEqual(
                resolve_protocol_seeds(stable_combo["game_params"], stable_combo),
                resolve_protocol_seeds(
                    relative_combo["game_params"],
                    relative_combo,
                ),
            )

        expected_defector_models = {
            "noise8i_defector_myth_game_gpt_n5": "openai/gpt-5-nano",
            "noise8i_defector_myth_game_gemini_n5": (
                "google/gemini-3.1-flash-lite"
            ),
        }
        for experiment_name, expected_model in expected_defector_models.items():
            combinations = self.config.get_experiment_combinations(experiment_name)
            self.assertEqual(len(combinations), 10)
            self.assertEqual(
                {combo["replicate_id"] for combo in combinations},
                set(range(30, 35)),
            )
            by_replicate = {}
            for combo in combinations:
                self.assertEqual(combo["model"], expected_model)
                self.assertEqual(combo["task_order"], ["myth", "game"])
                self.assertEqual(combo["game_params"]["memory_capacity"], 6)
                self.assertEqual(
                    combo["game_params"]["defector_action_policy"],
                    "forced_zero",
                )
                self.assertEqual(
                    combo["game_params"]["defector_myth_policy"],
                    "normal",
                )
                self.assertFalse(
                    combo["game_params"]["defector_role_visible_to_self"]
                )
                by_replicate.setdefault(combo["replicate_id"], []).append(combo)
            for replicate_id, matched in by_replicate.items():
                self.assertEqual(len(matched), 2)
                ratios = sorted(
                    combo["game_params"]["defector_ratio"] for combo in matched
                )
                self.assertEqual(ratios, [0.0, 0.25])
                control = dict(matched[0]["game_params"])
                treatment = dict(matched[1]["game_params"])
                if control["defector_ratio"] == 0.25:
                    control, treatment = treatment, control
                self.assertEqual(control.pop("defector_ratio"), 0.0)
                self.assertEqual(treatment.pop("defector_ratio"), 0.25)
                self.assertEqual(control, treatment)
                expected_seed = 202608121 + replicate_id
                self.assertEqual(
                    {
                        resolve_protocol_seeds(combo["game_params"], combo)
                        for combo in matched
                    },
                    {(expected_seed, expected_seed)},
                )

        expected_confirmation_models = {
            "noise8i_defector_myth_game_gpt_confirm_n10": "openai/gpt-5-nano",
            "noise8i_defector_myth_game_gemini_confirm_n10": (
                "google/gemini-3.1-flash-lite"
            ),
        }
        for experiment_name, expected_model in expected_confirmation_models.items():
            combinations = self.config.get_experiment_combinations(experiment_name)
            self.assertEqual(len(combinations), 20)
            self.assertEqual(
                {combo["replicate_id"] for combo in combinations},
                set(range(35, 45)),
            )
            by_replicate = {}
            for combo in combinations:
                self.assertEqual(combo["model"], expected_model)
                self.assertEqual(combo["task_order"], ["myth", "game"])
                by_replicate.setdefault(combo["replicate_id"], []).append(combo)
            for replicate_id, matched in by_replicate.items():
                self.assertEqual(len(matched), 2)
                self.assertEqual(
                    sorted(
                        combo["game_params"]["defector_ratio"] for combo in matched
                    ),
                    [0.0, 0.25],
                )
                control = next(
                    combo for combo in matched if combo["game_params"]["defector_ratio"] == 0
                )
                treatment = next(
                    combo
                    for combo in matched
                    if combo["game_params"]["defector_ratio"] == 0.25
                )
                control_params = dict(control["game_params"])
                treatment_params = dict(treatment["game_params"])
                control_params.pop("defector_ratio")
                treatment_params.pop("defector_ratio")
                self.assertEqual(control_params, treatment_params)
                expected_seed = 202608121 + replicate_id
                self.assertEqual(
                    {
                        resolve_protocol_seeds(combo["game_params"], combo)
                        for combo in matched
                    },
                    {(expected_seed, expected_seed)},
                )

        circulation = self.config.get_experiment_combinations(
            "noise8i_defector_myth_circulation_gemini_n5"
        )
        self.assertEqual(len(circulation), 10)
        self.assertEqual(
            {combo["replicate_id"] for combo in circulation},
            set(range(45, 50)),
        )
        by_replicate = {}
        for combo in circulation:
            self.assertEqual(combo["model"], "google/gemini-3.1-flash-lite")
            self.assertEqual(combo["task_order"], ["myth", "game"])
            self.assertEqual(combo["game_params"]["defector_ratio"], 0.25)
            self.assertEqual(
                combo["game_params"]["defector_action_policy"],
                "forced_zero",
            )
            self.assertFalse(
                combo["game_params"]["defector_role_visible_to_self"]
            )
            by_replicate.setdefault(combo["replicate_id"], []).append(combo)
        for replicate_id, matched in by_replicate.items():
            self.assertEqual(len(matched), 2)
            policies = {
                combo["game_params"]["defector_myth_policy"] for combo in matched
            }
            self.assertEqual(policies, {"normal", "standard_substitute"})
            normal = next(
                combo
                for combo in matched
                if combo["game_params"]["defector_myth_policy"] == "normal"
            )
            substitute = next(
                combo
                for combo in matched
                if combo["game_params"]["defector_myth_policy"]
                == "standard_substitute"
            )
            normal_params = dict(normal["game_params"])
            substitute_params = dict(substitute["game_params"])
            normal_params.pop("defector_myth_policy")
            substitute_params.pop("defector_myth_policy")
            self.assertEqual(normal_params, substitute_params)
            expected_seed = 202608121 + replicate_id
            self.assertEqual(
                {
                    resolve_protocol_seeds(combo["game_params"], combo)
                    for combo in matched
                },
                {(expected_seed, expected_seed)},
            )

        circulation_confirmation = self.config.get_experiment_combinations(
            "noise8i_defector_myth_circulation_gemini_confirm_n10"
        )
        self.assertEqual(len(circulation_confirmation), 20)
        self.assertEqual(
            {combo["replicate_id"] for combo in circulation_confirmation},
            set(range(50, 60)),
        )
        by_replicate = {}
        for combo in circulation_confirmation:
            self.assertEqual(combo["model"], "google/gemini-3.1-flash-lite")
            self.assertEqual(combo["task_order"], ["myth", "game"])
            self.assertEqual(combo["game_params"]["defector_ratio"], 0.25)
            by_replicate.setdefault(combo["replicate_id"], []).append(combo)
        for replicate_id, matched in by_replicate.items():
            self.assertEqual(len(matched), 2)
            self.assertEqual(
                {
                    combo["game_params"]["defector_myth_policy"]
                    for combo in matched
                },
                {"normal", "standard_substitute"},
            )
            normal = next(
                combo
                for combo in matched
                if combo["game_params"]["defector_myth_policy"] == "normal"
            )
            substitute = next(
                combo
                for combo in matched
                if combo["game_params"]["defector_myth_policy"]
                == "standard_substitute"
            )
            normal_params = dict(normal["game_params"])
            substitute_params = dict(substitute["game_params"])
            normal_params.pop("defector_myth_policy")
            substitute_params.pop("defector_myth_policy")
            self.assertEqual(normal_params, substitute_params)
            expected_seed = 202608121 + replicate_id
            self.assertEqual(
                {
                    resolve_protocol_seeds(combo["game_params"], combo)
                    for combo in matched
                },
                {(expected_seed, expected_seed)},
            )

    def test_population_isolation_is_a_complete_matched_two_by_three_design(self):
        expected = {
            "noise_population_isolation_v2_game": (["game"], 3),
            "noise_population_isolation_v2_game_myth": (
                ["game", "myth"],
                6,
            ),
            "noise_population_isolation_v2_myth_game": (
                ["myth", "game"],
                6,
            ),
        }

        for experiment_name, (task_order, memory_capacity) in expected.items():
            with self.subTest(experiment_name=experiment_name):
                combinations = self.config.get_experiment_combinations(
                    experiment_name
                )
                self.assertEqual(len(combinations), 20)
                self.assertEqual(
                    {combo["game_params"]["num_agents"] for combo in combinations},
                    {2, 8},
                )
                for combo in combinations:
                    params = combo["game_params"]
                    self.assertEqual(combo["task_order"], task_order)
                    self.assertEqual(params["memory_capacity"], memory_capacity)
                    self.assertEqual(params["history_policy"], "none")
                    self.assertEqual(params["pairing_mode"], "fixed")
                    self.assertEqual(params["prompt_regime"], "unified")
                    self.assertFalse(params["show_agent_names"])
                    self.assertTrue(params["paired_protocol_seeds"])

    def test_population_isolation_differs_only_in_num_agents(self):
        combinations = self.config.get_experiment_combinations(
            "noise_population_isolation_v2_game"
        )
        params_by_name = {
            combo["game_params_name"]: combo["game_params"]
            for combo in combinations
        }

        self.assertEqual(len(combinations), 20)
        self.assertEqual(len(params_by_name), 2)
        dyad = dict(
            params_by_name["noisy_bidirectional_informed_population_v2_dyad"]
        )
        fixed_8 = dict(
            params_by_name["noisy8_bidirectional_informed_population_v2_fixed"]
        )
        self.assertEqual(dyad.pop("num_agents"), 2)
        self.assertEqual(fixed_8.pop("num_agents"), 8)
        self.assertEqual(dyad, fixed_8)
        self.assertEqual(dyad["prompt_regime"], "unified")
        self.assertEqual(dyad["pairing_mode"], "fixed")
        self.assertEqual(dyad["history_policy"], "none")
        self.assertEqual(dyad["memory_capacity"], 3)

    def test_identity_isolation_differs_only_in_name_visibility(self):
        combinations = self.config.get_experiment_combinations(
            "noise8i_identity_v2_game"
        )
        params_by_name = {
            combo["game_params_name"]: combo["game_params"]
            for combo in combinations
        }

        self.assertEqual(len(combinations), 20)
        hidden = dict(
            params_by_name["noisy8_bidirectional_informed_identity_v2_hidden"]
        )
        named = dict(
            params_by_name["noisy8_bidirectional_informed_identity_v2_named"]
        )
        self.assertFalse(hidden.pop("show_agent_names"))
        self.assertTrue(named.pop("show_agent_names"))
        self.assertEqual(hidden, named)
        self.assertEqual(hidden["pairing_mode"], "balanced")
        self.assertEqual(hidden["history_policy"], "none")
        self.assertEqual(hidden["memory_capacity"], 3)

    def test_defector_cells_differ_only_in_defector_ratio(self):
        expected_capacity = {
            "noise8i_defector_v2_game": 3,
            "noise8i_defector_v2_game_myth": 6,
            "noise8i_defector_v2_myth_game": 6,
        }
        for experiment_name, memory_capacity in expected_capacity.items():
            combinations = self.config.get_experiment_combinations(
                experiment_name
            )
            params_by_name = {
                combo["game_params_name"]: combo["game_params"]
                for combo in combinations
            }
            control_name = next(
                name for name in params_by_name if name.endswith("control")
            )
            treatment_name = next(
                name for name in params_by_name if name.endswith("treatment25")
            )
            control = dict(params_by_name[control_name])
            treatment = dict(params_by_name[treatment_name])

            with self.subTest(experiment_name=experiment_name):
                self.assertEqual(len(combinations), 10)
                self.assertEqual(control.pop("defector_ratio"), 0.0)
                self.assertEqual(treatment.pop("defector_ratio"), 0.25)
                self.assertEqual(control, treatment)
                self.assertEqual(
                    control["defector_action_policy"],
                    "forced_zero",
                )
                self.assertEqual(control["defector_myth_policy"], "normal")
                self.assertFalse(control["defector_role_visible_to_self"])
                self.assertEqual(control["history_policy"], "none")
                self.assertEqual(control["pairing_mode"], "balanced")
                self.assertEqual(control["prompt_regime"], "unified")
                self.assertEqual(control["memory_capacity"], memory_capacity)

    def test_new_causal_cells_pair_protocol_seeds_by_replicate(self):
        for experiment_name in (
            "noise_population_isolation_v2_game",
            "noise_population_isolation_v2_game_myth",
            "noise_population_isolation_v2_myth_game",
            "noise8i_identity_v2_game",
            "noise8i_defector_v2_game",
            "noise8i_defector_v2_game_myth",
            "noise8i_defector_v2_myth_game",
        ):
            combinations = self.config.get_experiment_combinations(experiment_name)
            seeds_by_replicate = {}
            for combo in combinations:
                seeds_by_replicate.setdefault(combo["replicate_id"], set()).add(
                    resolve_protocol_seeds(combo["game_params"], combo)
                )

            with self.subTest(experiment_name=experiment_name):
                expected_replicates = 5 if "defector" in experiment_name else 10
                self.assertEqual(
                    set(seeds_by_replicate),
                    set(range(expected_replicates)),
                )
                self.assertTrue(
                    all(len(seed_pairs) == 1 for seed_pairs in seeds_by_replicate.values())
                )
                seed_base = (
                    202608121
                    if "defector" in experiment_name
                    else 202608120
                )
                self.assertEqual(seeds_by_replicate[0], {(seed_base, seed_base)})


if __name__ == "__main__":
    unittest.main()

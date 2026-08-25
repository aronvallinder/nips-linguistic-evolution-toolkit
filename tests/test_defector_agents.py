import contextlib
import io
import unittest
from unittest.mock import patch

from games.trust_game import TrustGame
from src.myth_writer import MythWriter
from src.experiment_config import ExperimentConfig
from src.simulation import SimulationData, run_simulation
from experiments.run_noisy_batch import NoisyExperimentConfig


DEFECTOR_PROMPT = """
MANDATORY GAME STRATEGY — DESIGNATED DEFECTOR:
When you are the SENDER, respond exactly: {"send": 0}
When you are the RECEIVER, respond exactly: {"return": 0}
This applies only to game decisions; participate normally in myth writing.
"""


def build_game(**kwargs):
    return TrustGame(
        endowment=5,
        multiplier=3,
        system_prompt_template="Game rules",
        round1_investor_template="Send an amount.",
        round1_trustee_template="Return an amount.",
        later_investor_template="Send an amount.",
        later_trustee_template="Return an amount.",
        defector_prompt_template=DEFECTOR_PROMPT,
        **kwargs,
    )


class DefectorPopulationTests(unittest.TestCase):
    def setUp(self):
        self.agent_ids = [f"Agent_{index}" for index in range(1, 9)]
        self.agent_names = {
            agent_id: f"Name {index}"
            for index, agent_id in enumerate(self.agent_ids, start=1)
        }

    def test_ratio_assigns_reproducible_fraction(self):
        first = build_game(defector_ratio=0.25, defector_seed=7)
        second = build_game(defector_ratio=0.25, defector_seed=7)

        first.configure_agents(self.agent_ids, self.agent_names)
        second.configure_agents(self.agent_ids, self.agent_names)

        self.assertEqual(first.defector_agent_ids, second.defector_agent_ids)
        self.assertEqual(len(first.defector_agent_ids), 2)
        self.assertEqual(first.get_population_metadata()["defector_ratio_actual"], 0.25)

    def test_only_defectors_receive_game_instruction(self):
        game = build_game(
            defector_agent_ids=["Agent_2", "Agent_7"],
        )
        game.configure_agents(self.agent_ids, self.agent_names)

        defector_prompt = game.with_prompt_context(
            "Round 1 game decision.",
            "Agent_2",
            "Agent_1",
        )
        standard_prompt = game.with_prompt_context(
            "Round 1 game decision.",
            "Agent_1",
            "Agent_2",
        )

        self.assertIn("DESIGNATED DEFECTOR", defector_prompt)
        self.assertIn('{"send": 0}', defector_prompt)
        self.assertIn("participate normally in myth writing", defector_prompt)
        self.assertNotIn("DESIGNATED DEFECTOR", standard_prompt)

    def test_explicit_assignment_is_recorded_by_agent(self):
        game = build_game(defector_agent_ids=["Agent_3", "Agent_8"])
        game.configure_agents(self.agent_ids, self.agent_names)

        self.assertEqual(
            game.get_agent_types(),
            {
                agent_id: (
                    "defector" if agent_id in {"Agent_3", "Agent_8"} else "standard"
                )
                for agent_id in self.agent_ids
            },
        )

    def test_hidden_forced_defector_has_scripted_zero_responses(self):
        game = build_game(
            defector_agent_ids=["Agent_2"],
            defector_action_policy="forced_zero",
            defector_myth_policy="normal",
            defector_role_visible_to_self=False,
        )
        game.configure_agents(self.agent_ids, self.agent_names)

        prompt = game.with_prompt_context(
            "Round 1 game decision.",
            "Agent_2",
            "Agent_1",
        )

        self.assertNotIn("DESIGNATED DEFECTOR", prompt)
        self.assertEqual(
            game.get_forced_game_response("Agent_2", "investor")["content"],
            '{"send": 0}',
        )
        self.assertEqual(
            game.get_forced_game_response("Agent_2", "trustee")["content"],
            '{"return": 0}',
        )
        self.assertIsNone(
            game.get_forced_game_response("Agent_1", "investor")
        )

    def test_forced_defectors_skip_game_llm_but_write_normal_myths(self):
        game = build_game(
            defector_agent_ids=["Agent_1", "Agent_2"],
            defector_action_policy="forced_zero",
            defector_myth_policy="normal",
            defector_role_visible_to_self=False,
        )
        myth_writer = MythWriter(
            myth_topic="anything",
            round1_template="Write a myth. {topic_instruction}",
            later_rounds_template="Rewrite your myth.",
        )
        llm_calls = []

        def fake_call_llm(client, model, temperature, messages):
            prompt = messages[-1]["content"]
            llm_calls.append(prompt)
            if "Write a myth" in prompt:
                content = "A normal myth about a difficult exchange."
            elif "send" in prompt.lower():
                content = '{"send": 1}'
            else:
                content = '{"return": 0}'
            return {"content": content, "reasoning": None, "usage": None}

        with patch("src.simulation.create_llm_client", return_value=object()), patch(
            "src.agents.call_llm",
            side_effect=fake_call_llm,
        ):
            with contextlib.redirect_stdout(io.StringIO()):
                sim_data = run_simulation(
                    game=game,
                    model="mock/model",
                    temperature=0,
                    num_turns=1,
                    num_agents=8,
                    memory_capacity=6,
                    agent_biases="",
                    myth_writer=myth_writer,
                    task_order=["game", "myth"],
                    chat_memory_mode="memory_primary",
                )

        self.assertEqual(len(llm_calls), 14)
        self.assertEqual(len(sim_data.conversation_history[0]["myths"]), 8)
        self.assertEqual(
            sim_data.run_metadata["defector_action_policy"],
            "forced_zero",
        )
        self.assertEqual(sim_data.run_metadata["defector_myth_policy"], "normal")
        self.assertFalse(
            sim_data.run_metadata["defector_role_visible_to_self"]
        )
        defectors = {"Agent_1", "Agent_2"}
        for dyad in sim_data.conversation_history[0]["dyads"]:
            if dyad["investor"] in defectors:
                self.assertEqual(dyad["sent"], 0)
            if dyad["trustee"] in defectors:
                self.assertEqual(dyad["returned"], 0)

        for agent_id in defectors:
            agent = sim_data.agents[agent_id]
            game_event, myth_event = agent.interaction_history
            self.assertEqual(
                sim_data.conversation_history[0]["game_responses"][agent_id][
                    "response_source"
                ],
                "forced_zero",
            )
            self.assertEqual(
                sim_data.conversation_history[0]["myth_responses"][agent_id][
                    "response_source"
                ],
                "llm",
            )
            self.assertEqual(
                game_event["response"]["response_source"],
                "forced_zero",
            )
            self.assertEqual(myth_event["response"]["response_source"], "llm")
            self.assertNotIn("DESIGNATED DEFECTOR", game_event["prompt"])
            self.assertIn(
                game_event["response"]["content"],
                [message.get("content") for message in agent.messages],
            )
            self.assertIn(
                "A normal myth about a difficult exchange.",
                sim_data.conversation_history[0]["myths"][agent_id],
            )

    def test_invalid_ratio_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "between 0 and 1"):
            build_game(defector_ratio=1.1)

        with self.assertRaisesRegex(ValueError, "between 0 and 1"):
            build_game(random_defection_probability=-0.1)

        with self.assertRaisesRegex(ValueError, "between 0 and 1"):
            build_game(random_defection_probability=1.1)

        with self.assertRaisesRegex(ValueError, "defector_action_policy"):
            build_game(defector_action_policy="typo")

        with self.assertRaisesRegex(ValueError, "defector_myth_policy"):
            build_game(defector_myth_policy="typo")

    def test_standard_substitute_changes_only_defector_to_standard_exposure(self):
        myth_writer = MythWriter(
            myth_topic="anything",
            round1_template="Write a myth. {topic_instruction}",
            later_rounds_template="Other myth:\n{other_agent_myth}",
        )
        sim_data = SimulationData()
        agent_types = {
            agent_id: (
                "defector" if agent_id in {"Agent_2", "Agent_8"} else "standard"
            )
            for agent_id in self.agent_ids
        }
        sim_data.game_data = {
            "agent_types": agent_types,
            "defector_myth_policy": "standard_substitute",
        }
        sim_data.run_metadata = {
            "defector_myth_policy": "standard_substitute",
        }
        previous_myths = {
            agent_id: f"Myth: unique story written by source {index}."
            for index, agent_id in enumerate(self.agent_ids, start=1)
        }
        sim_data.conversation_history = [
            {
                "round": 1,
                "agent_types": agent_types,
                "pairings": [
                    {"agents": ["Agent_1", "Agent_2"]},
                    {"agents": ["Agent_3", "Agent_4"]},
                    {"agents": ["Agent_5", "Agent_6"]},
                    {"agents": ["Agent_7", "Agent_8"]},
                ],
                "myths": previous_myths,
            },
            {"round": 2, "myth_exposures": {}},
        ]

        exposed_prompt = myth_writer.get_myth_prompt_round_later(
            "Agent_1", 2, sim_data
        )
        exposed_record = sim_data.conversation_history[1]["myth_exposures"][
            "Agent_1"
        ]
        self.assertTrue(exposed_record["substitution_applied"])
        self.assertEqual(exposed_record["original_author_id"], "Agent_2")
        self.assertEqual(exposed_record["presented_author_id"], "Agent_5")
        self.assertIn(previous_myths["Agent_5"], exposed_prompt)
        self.assertNotIn(previous_myths["Agent_2"], exposed_prompt)
        self.assertNotIn("Agent_5", exposed_prompt)
        self.assertNotIn("substitute", exposed_prompt.lower())
        self.assertNotIn("defector", exposed_prompt.lower())

        ordinary_prompt = myth_writer.get_myth_prompt_round_later(
            "Agent_3", 2, sim_data
        )
        ordinary_record = sim_data.conversation_history[1]["myth_exposures"][
            "Agent_3"
        ]
        self.assertFalse(ordinary_record["substitution_applied"])
        self.assertEqual(ordinary_record["presented_author_id"], "Agent_4")
        self.assertIn(previous_myths["Agent_4"], ordinary_prompt)

        defector_prompt = myth_writer.get_myth_prompt_round_later(
            "Agent_2", 2, sim_data
        )
        defector_record = sim_data.conversation_history[1]["myth_exposures"][
            "Agent_2"
        ]
        self.assertFalse(defector_record["substitution_applied"])
        self.assertEqual(defector_record["presented_author_id"], "Agent_1")
        self.assertIn(previous_myths["Agent_1"], defector_prompt)

    def test_normal_circulation_preserves_defector_authored_myth(self):
        myth_writer = MythWriter(
            myth_topic="anything",
            round1_template="Write a myth. {topic_instruction}",
            later_rounds_template="Other myth:\n{other_agent_myth}",
        )
        sim_data = SimulationData()
        agent_types = {"Agent_1": "standard", "Agent_2": "defector"}
        sim_data.game_data = {
            "agent_types": agent_types,
            "defector_myth_policy": "normal",
        }
        sim_data.run_metadata = {"defector_myth_policy": "normal"}
        sim_data.conversation_history = [
            {
                "round": 1,
                "agent_types": agent_types,
                "pairings": [{"agents": ["Agent_1", "Agent_2"]}],
                "myths": {
                    "Agent_1": "Myth: ordinary source.",
                    "Agent_2": "Myth: defector source.",
                },
            },
            {"round": 2, "myth_exposures": {}},
        ]

        prompt = myth_writer.get_myth_prompt_round_later(
            "Agent_1", 2, sim_data
        )
        record = sim_data.conversation_history[1]["myth_exposures"]["Agent_1"]
        self.assertIn("Myth: defector source.", prompt)
        self.assertFalse(record["substitution_applied"])
        self.assertEqual(record["presented_author_id"], "Agent_2")

    def test_standard_substitute_is_recorded_in_full_simulation(self):
        game = build_game(
            defector_agent_ids=["Agent_1", "Agent_3"],
            defector_action_policy="forced_zero",
            defector_myth_policy="standard_substitute",
            defector_role_visible_to_self=False,
        )
        game.set_pairing_mode("fixed")
        myth_writer = MythWriter(
            myth_topic="anything",
            round1_template="Write a myth. {topic_instruction}",
            later_rounds_template=(
                "Other myth:\n{other_agent_myth}\n\nWrite a myth."
            ),
        )

        def fake_call_llm(client, model, temperature, messages):
            prompt = messages[-1]["content"]
            if "Write a myth" in prompt:
                content = "Myth: A traveler crossed a quiet valley and came home."
            elif prompt.rstrip().endswith("Return an amount."):
                content = '{"return": 0}'
            elif prompt.rstrip().endswith("Send an amount."):
                content = '{"send": 1}'
            elif "{'return': <amount>}" in prompt:
                content = '{"return": 0}'
            elif "{'send': <amount>}" in prompt:
                content = '{"send": 1}'
            else:
                raise AssertionError(f"Unexpected mock prompt: {prompt}")
            return {"content": content, "reasoning": None, "usage": None}

        with patch("src.simulation.create_llm_client", return_value=object()), patch(
            "src.agents.call_llm",
            side_effect=fake_call_llm,
        ):
            with contextlib.redirect_stdout(io.StringIO()):
                sim_data = run_simulation(
                    game=game,
                    model="mock/model",
                    temperature=0,
                    num_turns=2,
                    num_agents=8,
                    memory_capacity=6,
                    agent_biases="",
                    myth_writer=myth_writer,
                    task_order=["myth", "game"],
                    chat_memory_mode="memory_primary",
                )

        second_round = sim_data.conversation_history[1]
        self.assertEqual(len(second_round["myth_exposures"]), 8)
        substituted_targets = {
            agent_id
            for agent_id, record in second_round["myth_exposures"].items()
            if record["substitution_applied"]
        }
        self.assertEqual(substituted_targets, {"Agent_2", "Agent_4"})
        for target_id in substituted_targets:
            record = second_round["myth_exposures"][target_id]
            self.assertEqual(record["original_author_type"], "defector")
            self.assertEqual(record["presented_author_type"], "standard")
            myth_event = next(
                event
                for event in sim_data.agents[target_id].interaction_history
                if event["metadata"]["round"] == 2
                and event["metadata"]["task"] == "myth"
            )
            self.assertNotIn("standard_substitute", myth_event["prompt"])

    def test_configured_8_agent_condition_uses_quarter_defectors(self):
        config = ExperimentConfig("config/experiments.yaml")
        combinations = config.get_experiment_combinations(
            "sonnet45_8agent_defectors25_history3_r10_n5"
        )

        self.assertTrue(combinations)
        self.assertTrue(
            all(combo["game_params"]["num_agents"] == 8 for combo in combinations)
        )
        self.assertTrue(
            all(combo["game_params"]["defector_ratio"] == 0.25 for combo in combinations)
        )
        self.assertTrue(
            all(combo["defector_game_instruction"] for combo in combinations)
        )

    def test_seeded_random_defection_is_reproducible_and_nested(self):
        low = build_game(
            random_defection_probability=0.25,
            random_defection_seed=202608250,
        )
        high = build_game(
            random_defection_probability=0.50,
            random_defection_seed=202608250,
        )
        repeated = build_game(
            random_defection_probability=0.25,
            random_defection_seed=202608250,
        )

        decisions = [
            (turn, agent_id, role)
            for turn in range(1, 101)
            for agent_id, role in (
                ("Agent_1", "investor"),
                ("Agent_2", "trustee"),
            )
        ]
        low_events = {
            decision
            for decision in decisions
            if low.is_random_defection(decision[1], decision[2], decision[0])
        }
        high_events = {
            decision
            for decision in decisions
            if high.is_random_defection(decision[1], decision[2], decision[0])
        }
        repeated_events = {
            decision
            for decision in decisions
            if repeated.is_random_defection(
                decision[1],
                decision[2],
                decision[0],
            )
        }

        self.assertEqual(low_events, repeated_events)
        self.assertTrue(low_events)
        self.assertTrue(low_events < high_events)
        self.assertGreater(len(low_events), 30)
        self.assertLess(len(low_events), 70)
        self.assertGreater(len(high_events), 70)
        self.assertLess(len(high_events), 130)

    def test_random_defection_forces_zero_and_is_recorded(self):
        game = build_game(
            random_defection_probability=1.0,
            random_defection_seed=11,
        )
        response = game.get_forced_game_response(
            "Agent_1",
            "investor",
            turn=1,
        )

        self.assertEqual(response["content"], '{"send": 0}')
        self.assertEqual(
            response["response_source"],
            "random_defection_forced_zero",
        )
        metadata = game.get_population_metadata()
        self.assertEqual(metadata["random_defection_probability"], 1.0)
        self.assertEqual(metadata["random_defection_seed"], 11)
        self.assertEqual(metadata["random_defection_unit"], "agent_game_decision")

    def test_random_defection_skips_game_llm_calls(self):
        game = build_game(
            random_defection_probability=1.0,
            random_defection_seed=12,
        )

        with patch("src.simulation.create_llm_client", return_value=object()), patch(
            "src.agents.call_llm"
        ) as call_llm:
            with contextlib.redirect_stdout(io.StringIO()):
                sim_data = run_simulation(
                    game=game,
                    model="mock/model",
                    temperature=0,
                    num_turns=2,
                    num_agents=2,
                    memory_capacity=3,
                    agent_biases="",
                    myth_writer=None,
                    task_order=["game"],
                    chat_memory_mode="memory_primary",
                )

        call_llm.assert_not_called()
        self.assertEqual(
            sim_data.run_metadata["random_defection_probability"],
            1.0,
        )
        for round_entry in sim_data.conversation_history:
            self.assertEqual(
                {
                    response["response_source"]
                    for response in round_entry["game_responses"].values()
                },
                {"random_defection_forced_zero"},
            )


class NegativeOnlyBatchConfigTests(unittest.TestCase):
    def test_slide_695_matrix_has_expected_cells(self):
        config = NoisyExperimentConfig("config/experiments_noisy.yaml")
        experiment_names = [
            "negative_only_crossmodel_dyad_game_n5",
            "negative_only_crossmodel_dyad_game_myth_n5",
            "negative_only_crossmodel_dyad_myth_game_n5",
            "negative_only_crossmodel_population_game_n5",
            "negative_only_crossmodel_population_game_myth_n5",
            "negative_only_crossmodel_population_myth_game_n5",
        ]
        expected_models = {
            "anthropic/claude-sonnet-4.5",
            "openai/gpt-5-nano",
            "google/gemini-3.7-flash",
        }

        all_combinations = []
        for experiment_name in experiment_names:
            combinations = config.get_experiment_combinations(experiment_name)
            self.assertEqual(len(combinations), 45)
            self.assertEqual(
                {combo["model"] for combo in combinations},
                expected_models,
            )
            self.assertEqual(
                {combo["replicate_id"] for combo in combinations},
                {0, 1, 2, 3, 4},
            )
            for combo in combinations:
                params = combo["game_params"]
                self.assertEqual(
                    params["noise_config"],
                    {
                        "type": "uniform",
                        "range": 1.0,
                        "direction": "negative",
                        "applies_to": "both",
                        "inform_agents": True,
                    },
                )
                self.assertTrue(params["paired_protocol_seeds"])
                self.assertEqual(params["protocol_seed_base"], 202608250)
            all_combinations.extend(combinations)

        self.assertEqual(len(all_combinations), 270)

    def test_treatment_arms_match_population_regime(self):
        config = NoisyExperimentConfig("config/experiments_noisy.yaml")
        dyad = config.get_experiment_combinations(
            "negative_only_crossmodel_dyad_game_n5"
        )
        population = config.get_experiment_combinations(
            "negative_only_crossmodel_population_game_n5"
        )

        self.assertEqual(
            {combo["game_params"]["num_agents"] for combo in dyad},
            {2},
        )
        self.assertEqual(
            {
                combo["game_params"].get("random_defection_probability", 0.0)
                for combo in dyad
            },
            {0.0, 0.25, 0.50},
        )
        self.assertEqual(
            {combo["game_params"]["num_agents"] for combo in population},
            {8},
        )
        self.assertEqual(
            {
                combo["game_params"].get("defector_ratio", 0.0)
                for combo in population
            },
            {0.0, 0.25, 0.50},
        )


if __name__ == "__main__":
    unittest.main()

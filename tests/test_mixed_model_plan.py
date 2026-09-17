"""Mixed-model runs pin one request plan per agent and audit each call against it."""

import copy
from types import SimpleNamespace

import pytest

from experiments.run_noisy_batch import NoisyExperimentConfig
from src.experiment_condition import ConditionMismatchError, build_condition, condition_from_run, digest, validate_condition
from src.llm_settings import (
    LLMSettingsError,
    agent_request_plans,
    is_mixed_plan,
    mixed_model_label,
    prepare_combinations,
    resolve_mixed_request_plan,
)
from src.simulation import SimulationData
from src.utils import DIRECT_MODEL_ALIASES, create_llm_client
from test_llm_request_plan import settings

CLAUDE = "anthropic/claude-sonnet-4.5"
GPT = "openai/gpt-5-nano"
BLOCKS = {
    CLAUDE: settings(provider="anthropic", reasoning={"thinking": {"type": "enabled", "budget_tokens": 8192}}, cap=64000),
    GPT: settings(provider="openai", reasoning={"reasoning_effort": "high"}, cap=128000),
}


def mixed_plan():
    return resolve_mixed_request_plan({"Agent_1": CLAUDE, "Agent_2": GPT}, BLOCKS, DIRECT_MODEL_ALIASES)


def test_mixed_plan_pins_each_agent_like_a_homogeneous_run():
    plan = mixed_plan()
    data = plan.as_dict()
    assert is_mixed_plan(plan) and data["provider"] == "mixed"
    assert data["model"] == "mixed/claude-sonnet-4.5+gpt-5-nano" == mixed_model_label({"Agent_1": CLAUDE, "Agent_2": GPT})
    assert data["provider_model"] == "claude-sonnet-4-5-20250929+gpt-5-nano"
    per_agent = agent_request_plans(plan)
    assert per_agent["Agent_1"].provider == "anthropic" and per_agent["Agent_1"].provider_model == "claude-sonnet-4-5-20250929"
    assert per_agent["Agent_2"].provider == "openai" and per_agent["Agent_2"].parameters["reasoning_effort"] == "high"
    assert per_agent["Agent_1"].parameters["thinking"]["budget_tokens"] == 8192


def test_mixed_plan_requires_two_different_pinned_models():
    with pytest.raises(LLMSettingsError, match="different models"):
        resolve_mixed_request_plan({"Agent_1": GPT, "Agent_2": GPT}, BLOCKS, DIRECT_MODEL_ALIASES)
    with pytest.raises(LLMSettingsError, match="no llm_settings"):
        resolve_mixed_request_plan({"Agent_1": CLAUDE, "Agent_2": GPT}, {CLAUDE: BLOCKS[CLAUDE]}, DIRECT_MODEL_ALIASES)


def test_mixed_plan_cannot_create_a_single_shared_client():
    with pytest.raises(LLMSettingsError, match="one client per agent"):
        create_llm_client("mixed/claude-sonnet-4.5+gpt-5-nano", request_plan=mixed_plan())


def mixed_run(tamper=None):
    request = mixed_plan().as_dict()
    metadata = {"llm_request": request, "llm_provider": "mixed", "provider_model": request["provider_model"]}
    game = SimpleNamespace(system_prompt_template="unchanged rules", noise_seed=3)
    condition = build_condition(game, None, metadata, {"memory_capacity": 3, "task_order": ["game"]}, {"replicate_id": 0})
    metadata.update(experiment_condition=condition, condition_sha256=digest(condition))
    agents = {}
    for agent_id, agent_request in request["agents"].items():
        usage = {"request_settings": copy.deepcopy(agent_request), "finish_reason": "stop", "outcome": "complete"}
        agents[agent_id] = {"model": agent_request["model"], "interaction_history": [{"response": {"usage": usage}}]}
    data = {"agents": agents, "conversation_history": [], "game_data": {}, "task_order": ["game"], "run_metadata": metadata}
    if tamper:
        tamper(data)
    return data


def test_mixed_condition_validates_and_checks_each_agents_calls():
    condition = condition_from_run(mixed_run())
    assert validate_condition(condition)["llm"]["provider"] == "mixed"

    def swap_agent_settings(data):
        first, second = data["agents"]["Agent_1"], data["agents"]["Agent_2"]
        first["interaction_history"][0]["response"]["usage"]["request_settings"] = second["interaction_history"][0]["response"]["usage"]["request_settings"]

    with pytest.raises(ConditionMismatchError, match="Per-call request settings"):
        condition_from_run(mixed_run(swap_agent_settings))

    def unknown_agent(data):
        data["agents"]["Agent_3"] = data["agents"]["Agent_1"]

    with pytest.raises(ConditionMismatchError, match="no request settings for Agent_3"):
        condition_from_run(mixed_run(unknown_agent))


def test_mixed_condition_rejects_tampered_agent_parameters():
    data = mixed_run()
    data["run_metadata"]["experiment_condition"]["llm"]["agents"]["Agent_2"]["parameters"]["reasoning_effort"] = "low"
    data["run_metadata"]["condition_sha256"] = digest(data["run_metadata"]["experiment_condition"])
    data["run_metadata"]["llm_request"] = data["run_metadata"]["experiment_condition"]["llm"]
    with pytest.raises(ConditionMismatchError, match="contradict"):
        condition_from_run(data)


def test_config_expansion_gives_every_agent_its_model_and_september_inputs():
    config = NoisyExperimentConfig("config/experiments_noisy.yaml")
    mixed = config.get_experiment_combinations("mixed_dyad_game_gpt_sonnet_n3")
    reference = [
        c for c in config.get_experiment_combinations("negative_only_reasoning_rerun_dyad_game_claude_n5")
        if c["game_params_name"] == "noisy2_crossmodel_negative_game_r3"
    ]
    assert [c["replicate_id"] for c in mixed] == [1, 3, 5]
    assert all(c["model"] == "mixed/gpt-5-nano+claude-sonnet-4.5" for c in mixed)
    assert mixed[0]["agent_models"] == {"Agent_1": GPT, "Agent_2": CLAUDE}
    prepare_combinations(mixed, config.config["experiment_sets"]["mixed_dyad_game_gpt_sonnet_n3"], DIRECT_MODEL_ALIASES)
    prepare_combinations(reference, config.config["experiment_sets"]["negative_only_reasoning_rerun_dyad_game_claude_n5"], DIRECT_MODEL_ALIASES)
    plan = mixed[0]["request_plan"].as_dict()
    assert plan["agents"]["Agent_2"] == reference[0]["request_plan"].as_dict()
    assert "agent_model_keys" not in mixed[0]["comparison_inputs"]
    ignored = {"model", "agent_models", "llm_request", "replicate_id"}
    assert {k: v for k, v in mixed[0]["comparison_inputs"].items() if k not in ignored} == {
        k: v for k, v in reference[0]["comparison_inputs"].items() if k not in ignored
    }


def test_mixed_sets_reject_a_models_list_or_agent_count_mismatch(tmp_path):
    config = NoisyExperimentConfig("config/experiments_noisy.yaml")
    broken = copy.deepcopy(config.config["experiment_sets"]["mixed_dyad_game_sonnet_gpt_n3"])
    broken["models"] = ["gpt5_nano"]
    config.config["experiment_sets"]["broken"] = broken
    with pytest.raises(ValueError, match="agent_models instead of models"):
        config.get_experiment_combinations("broken")
    eight = copy.deepcopy(config.config["experiment_sets"]["mixed_dyad_game_sonnet_gpt_n3"])
    eight["game_params_list"] = ["noisy8_crossmodel_negative_game_r3"]
    config.config["experiment_sets"]["eight"] = eight
    with pytest.raises(ValueError, match="num_agents=8"):
        config.get_experiment_combinations("eight")


def test_load_state_assigns_each_saved_agent_its_own_client(tmp_path):
    plans = agent_request_plans(mixed_plan())
    clients = {agent_id: SimpleNamespace(request_plan=plan) for agent_id, plan in plans.items()}
    state = {
        "conversation_history": [], "game_data": {}, "task_order": ["game"], "run_metadata": {},
        "agents": {
            "Agent_1": {"agent_id": "Agent_1", "model": CLAUDE, "memory_capacity": 3, "messages": []},
            "Agent_2": {"agent_id": "Agent_2", "model": GPT, "memory_capacity": 3, "messages": []},
        },
    }
    path = tmp_path / "checkpoint.json"
    path.write_text(__import__("json").dumps(state))
    loaded = SimulationData.load_state(str(path), clients)
    assert loaded.agents["Agent_1"].client is clients["Agent_1"] and loaded.agents["Agent_1"].model == CLAUDE
    assert loaded.agents["Agent_2"].client is clients["Agent_2"] and loaded.agents["Agent_2"].model == GPT
    state["agents"]["Agent_2"]["model"] = CLAUDE
    path.write_text(__import__("json").dumps(state))
    with pytest.raises(ValueError, match="differs from planned"):
        SimulationData.load_state(str(path), clients)

"""Mixed-model runs pin one request plan per agent and audit each call against it."""

import copy
from types import SimpleNamespace

import pytest

from experiments.run_noisy_batch import NoisyExperimentConfig
from src.experiment_condition import (
    ConditionMismatchError,
    build_condition,
    condition_from_run,
    digest,
    output_provenance,
    rebuild_request,
    validate_condition,
    validate_output_provenance,
)
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
    metadata = {
        "llm_request": request, "llm_provider": "mixed", "provider_model": request["provider_model"],
        "agent_models": {agent_id: agent_request["model"] for agent_id, agent_request in request["agents"].items()},
    }
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

    with pytest.raises(ConditionMismatchError, match="Saved agent set differs"):
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


def test_mixed_condition_ties_agent_models_and_saved_agents_to_the_plans():
    def swap(data):
        models = data["run_metadata"]["agent_models"]
        data["run_metadata"]["agent_models"] = {"Agent_1": models["Agent_2"], "Agent_2": models["Agent_1"]}

    with pytest.raises(ConditionMismatchError, match="agent_models contradict"):
        condition_from_run(mixed_run(swap))

    def drop_agent(data):
        del data["agents"]["Agent_2"]

    with pytest.raises(ConditionMismatchError, match="Saved agent set"):
        condition_from_run(mixed_run(drop_agent))

    def relabel_saved_model(data):
        data["agents"]["Agent_2"]["model"] = CLAUDE

    with pytest.raises(ConditionMismatchError, match="Saved model for Agent_2"):
        condition_from_run(mixed_run(relabel_saved_model))


def test_mixed_label_and_rebuild_are_order_independent_beyond_nine_agents():
    gemini = "google/gemini-3.7-flash"
    blocks = {**BLOCKS, gemini: settings(provider="google", reasoning={"thinkingConfig": {"thinkingLevel": "high"}}, temperature=0.8, cap=65536)}
    agent_models = {f"Agent_{i}": CLAUDE for i in range(1, 11)}
    agent_models["Agent_2"] = GPT
    agent_models["Agent_10"] = gemini
    plan = resolve_mixed_request_plan(agent_models, blocks, DIRECT_MODEL_ALIASES).as_dict()
    shuffled = resolve_mixed_request_plan(dict(reversed(list(agent_models.items()))), blocks, DIRECT_MODEL_ALIASES).as_dict()
    assert plan == shuffled
    assert plan["model"] == "mixed/claude-sonnet-4.5+gpt-5-nano+gemini-3.7-flash"
    assert rebuild_request(plan) == plan


def test_pooled_provenance_declares_plan_shape_and_still_checks_the_rest(tmp_path):
    import json as _json
    from test_experiment_condition import saved_run, write_run

    mixed_path = write_run(tmp_path / "mixed.json", mixed_run())
    homogeneous_path = write_run(tmp_path / "homogeneous.json", saved_run(0))
    output = tmp_path / "table.csv"
    output.write_text("a,b\n")
    allowed = {
        "llm.agents": "per-agent plans", "llm.model": "x", "llm.provider": "x", "llm.provider_model": "x", "llm.endpoint": "x",
        "protocol.game.noise_seed": "x", "replicate.noise_seed": "x", "replicate.identity.replicate_id": "x",
        "protocol.simulation.task_order": "x", "protocol.game.system_prompt_template": "x",
    }
    with pytest.raises(ConditionMismatchError, match="llm.parameters, llm.policy"):
        output_provenance([mixed_path, homogeneous_path], [output], allowed, output_root=tmp_path)
    document = output_provenance(
        [mixed_path, homogeneous_path], [output], allowed, output_root=tmp_path,
        pools={"mixed": [mixed_path], "homogeneous": [homogeneous_path]}, pool_reason="plan shape differs by design",
    )
    assert set(document["pools"]) == {"mixed", "homogeneous"}
    assert "llm.policy" not in document["observed_differences"]
    validate_output_provenance(_json.loads(_json.dumps(document)))
    document["pool_reason"] = ""
    with pytest.raises(ConditionMismatchError, match="pool_reason"):
        validate_output_provenance(document)
    # A protocol difference across pools is still caught.
    tampered = mixed_run()
    tampered["run_metadata"]["experiment_condition"]["protocol"]["simulation"]["memory_capacity"] = 6
    tampered["run_metadata"]["condition_sha256"] = digest(tampered["run_metadata"]["experiment_condition"])
    other = write_run(tmp_path / "mixed2.json", tampered)
    with pytest.raises(ConditionMismatchError, match="memory_capacity"):
        output_provenance(
            [other, homogeneous_path], [output], allowed, output_root=tmp_path,
            pools={"mixed": [other], "homogeneous": [homogeneous_path]}, pool_reason="plan shape differs by design",
        )


def test_run_simulation_gives_each_agent_its_own_client_and_records_a_valid_condition(tmp_path, monkeypatch):
    import src.agents
    import src.simulation
    from experiments.run_noisy_batch import build_noisy_protocol

    config = NoisyExperimentConfig("config/experiments_noisy.yaml")
    combos = config.get_experiment_combinations("mixed_dyad_game_gpt_sonnet_n3")
    prepare_combinations(combos, config.config["experiment_sets"]["mixed_dyad_game_gpt_sonnet_n3"], DIRECT_MODEL_ALIASES)
    combo = combos[0]
    plan = combo["request_plan"]
    created = {}

    def fake_client(model, request_plan=None, provider=None):
        assert request_plan is not None and request_plan.as_dict()["model"] == model
        created[model] = SimpleNamespace(request_plan=request_plan, provider=request_plan.provider)
        return created[model]

    def fake_call(client, model, temperature, messages, **kwargs):
        assert client.request_plan.as_dict()["model"] == model
        prompt = messages[-1]["content"]
        content = "{'send': 3}" if "SENDER" in prompt else "{'return': 4}"
        usage = {"input_tokens": 1, "output_tokens": 1, "reasoning_tokens": 0,
                 "request_settings": client.request_plan.as_dict(), "finish_reason": "stop", "outcome": "complete"}
        return {"content": content, "reasoning": None, "usage": usage}

    monkeypatch.setattr(src.simulation, "create_llm_client", fake_client)
    monkeypatch.setattr(src.agents, "call_llm", fake_call)
    game, myth_writer = build_noisy_protocol(combo, 0)
    params = combo["game_params"]
    sim = src.simulation.run_simulation(
        game, combo["model"], params.get("temperature", 0.8), 2, params["num_agents"], params["memory_capacity"], "",
        myth_writer, task_order=combo["task_order"], results_path=str(tmp_path / "r.results.json"),
        checkpoint_path=str(tmp_path / "r.checkpoint.json"), checkpoint_every=10, log_file=str(tmp_path / "r.log"),
        chat_memory_mode=params.get("chat_memory_mode", "default"), request_plan=plan,
        run_metadata_extra={"comparison_inputs": combo["comparison_inputs"]},
        run_identity={"experiment": "test", "replicate_id": combo["replicate_id"], "output_path": "x"},
    )
    assert sim.agents["Agent_1"].model == GPT and sim.agents["Agent_1"].client is created[GPT]
    assert sim.agents["Agent_2"].model == CLAUDE and sim.agents["Agent_2"].client is created[CLAUDE]
    assert sim.run_metadata["llm_provider"] == "mixed" and sim.run_metadata["agent_models"] == combo["agent_models"]
    assert sim.run_metadata["temperature"] == {"Agent_1": "default", "Agent_2": "default"}
    state = sim.to_state()
    assert len(state["conversation_history"]) == 2
    condition = condition_from_run(state)
    assert condition["llm"]["agents"]["Agent_1"]["provider"] == "openai"
    calls = [e for a in state["agents"].values() for e in a["interaction_history"]]
    assert len(calls) == 4 and all(e["response"]["usage"]["request_settings"]["model"] == e["model"] for e in calls)


def test_launcher_plan_and_audit_hold_for_the_frozen_dyad_batch():
    from scripts import run_mixed_model_dyads as launcher

    jobs = launcher.plan()
    assert len(jobs) == 54
    assert {j[2]["game_params"]["num_agents"] for j in jobs} == {2}
    existing = [j for j in jobs if j[3].exists()]
    if not existing:
        pytest.skip("no mixed-dyad finals on this machine")
    receipt = launcher.audit(existing[0])
    assert receipt["calls"] > 0 and receipt["standard_rate_usd"] > 0
    assert set(receipt["standard_rate_usd_by_provider"]) == {"anthropic", "openai", "google"}


def test_population_launcher_plan_holds_for_the_frozen_ladder():
    from scripts import run_mixed_model_populations as launcher

    jobs = launcher.plan()
    assert len(jobs) == 90
    minority_counts = {sum(m != launcher.FAMILY["sonnet"] and m != launcher.FAMILY["gpt"] or m == launcher.FAMILY["gpt"] for m in j[2]["agent_models"].values()) for j in jobs}
    assert all(j[2]["game_params"]["num_agents"] == 8 for j in jobs)
    first = jobs[0][2]["agent_models"]
    assert list(first) == [f"Agent_{i}" for i in range(1, 9)]

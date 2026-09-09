from experiments.run_noisy_batch import NoisyExperimentConfig


GATE_EXPERIMENTS = {
    "gpt55_gate_dyad_game_r1": (2, ["game"], "noisy2_crossmodel_negative_game_r3"),
    "gpt55_gate_dyad_game_myth_r1": (
        2,
        ["game", "myth"],
        "noisy2_crossmodel_negative_twotask_r3",
    ),
    "gpt55_gate_dyad_myth_game_r1": (
        2,
        ["myth", "game"],
        "noisy2_crossmodel_negative_twotask_r3",
    ),
    "gpt55_gate_population_game_r1": (
        8,
        ["game"],
        "noisy8_crossmodel_negative_game_r3",
    ),
    "gpt55_gate_population_game_myth_r1": (
        8,
        ["game", "myth"],
        "noisy8_crossmodel_negative_twotask_r3",
    ),
    "gpt55_gate_population_myth_game_r1": (
        8,
        ["myth", "game"],
        "noisy8_crossmodel_negative_twotask_r3",
    ),
}


def test_gpt55_gate_has_exactly_six_locked_control_runs(monkeypatch):
    monkeypatch.setenv("OPENAI_REASONING_EFFORT", "low")
    config = NoisyExperimentConfig("config/experiments_noisy.yaml")

    for experiment, (num_agents, task_order, game_params_name) in GATE_EXPERIMENTS.items():
        combinations = config.get_experiment_combinations(experiment)
        assert len(combinations) == 1
        combo = combinations[0]
        assert combo["model"] == "openai/gpt-5.5-2026-04-23"
        assert combo["task_order"] == task_order
        assert combo["game_params_name"] == game_params_name
        assert combo["game_params"]["num_agents"] == num_agents
        assert combo["game_params"]["noise_config"] == {
            "type": "uniform",
            "range": 1.0,
            "direction": "negative",
            "applies_to": "both",
            "inform_agents": True,
        }
        assert combo["replicate_id"] == 0
        assert combo["provider_settings"] == {
            "openai_reasoning_effort": "low"
        }


def test_gpt55_gate_second_stage_uses_next_paired_replicate(monkeypatch):
    monkeypatch.setenv("OPENAI_REASONING_EFFORT", "low")
    config = NoisyExperimentConfig("config/experiments_noisy.yaml")

    for first_experiment in GATE_EXPERIMENTS:
        second_experiment = first_experiment.removesuffix("_r1") + "_r2"
        combinations = config.get_experiment_combinations(second_experiment)
        assert len(combinations) == 1
        combo = combinations[0]
        assert combo["replicate_id"] == 1
        assert combo["game_params"]["protocol_seed_base"] == 202608250

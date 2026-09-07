from scripts import run_noisy_missing


def test_expected_output_path_matches_explicit_replicate_and_myth_arm():
    combo = {
        "model": "google/gemini-3.7-flash",
        "task_order": ["myth", "game"],
        "game_params_name": "params",
        "persona": {"description": "neutral"},
        "myth_topic_id": "anything",
        "replicate_id": 90,
        "myth_prompt_arm_id": "memory_primary",
    }

    path = run_noisy_missing.expected_output_path(
        combo,
        "experiment",
        0,
        "output",
    )

    assert path.name == (
        "experiment_000_neutral_rep90_memory_primary_anything.json"
    )


def test_expected_output_path_preserves_legacy_filename_without_replicate():
    combo = {
        "model": "openai/gpt-5-nano",
        "task_order": ["game"],
        "game_params_name": "params",
        "persona": {"description": "neutral"},
    }

    path = run_noisy_missing.expected_output_path(
        combo,
        "experiment",
        2,
        "output",
    )

    assert path.name == "experiment_002_neutral.json"


def test_load_combinations_embeds_execution_provenance(monkeypatch, tmp_path):
    config_path = tmp_path / "experiments.yaml"
    config_path.write_text("experiment_sets: {}\n", encoding="utf-8")

    class FakeConfig:
        def __init__(self, path):
            assert path == str(config_path)
            self.config = {"experiment_sets": {"example": {}}}

        def get_experiment_combinations(self, experiment_name):
            assert experiment_name == "example"
            return [{"index": 0}, {"index": 1}]

    provenance = {
        "execution_provenance_version": 1,
        "code_commit": "abc123",
        "code_dirty": False,
        "config_sha256": "feedface",
    }
    monkeypatch.setattr(run_noisy_missing, "NoisyExperimentConfig", FakeConfig)
    monkeypatch.setattr(
        run_noisy_missing,
        "execution_provenance",
        lambda path: provenance,
    )

    combinations = run_noisy_missing.load_combinations(
        "example",
        str(config_path),
        allow_legacy_settings=True,
    )

    assert [item["execution_provenance"] for item in combinations] == [
        provenance,
        provenance,
    ]
    assert combinations[0]["execution_provenance"] is not combinations[1][
        "execution_provenance"
    ]

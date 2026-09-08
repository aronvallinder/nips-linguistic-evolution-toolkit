from scripts import run_noisy_missing
import copy
import json
from types import SimpleNamespace

import pytest

from src.experiment_condition import ConditionMismatchError, digest
from src.llm_settings import prepare_combinations
from test_llm_request_plan import settings
from test_experiment_condition import saved_run, write_run


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


def test_missing_run_plans_hash_of_loaded_myths_and_detects_pool_growth(monkeypatch, tmp_path):
    pool = tmp_path / "pool"
    pool.mkdir()
    (pool / "baseline.json").write_text(json.dumps({"conversation_history": [{"myths": {"Agent_1": "first myth"}}]}))

    class Config:
        def __init__(self, path):
            self.config = {"experiment_sets": {"example": {"llm_settings": settings()}}}

        def get_experiment_combinations(self, name):
            return [{"model": "openai/gpt-5-nano", "myth_injection_mode": "shuffled", "shuffled_myth_pool_path": str(pool)}]

    monkeypatch.setattr(run_noisy_missing, "NoisyExperimentConfig", Config)
    monkeypatch.setattr(run_noisy_missing, "execution_provenance", lambda path: {})
    first = run_noisy_missing.load_combinations("example", "unused.yaml")[0]
    data = saved_run()
    condition = data["run_metadata"]["experiment_condition"]
    condition["protocol"]["game"]["shuffled_myth_pool_sha256"] = digest(("first myth",))
    data["run_metadata"]["condition_sha256"] = digest(condition)
    data["run_metadata"]["comparison_inputs"] = first["comparison_inputs"]
    final = write_run(tmp_path / "completed.json", data)
    run_noisy_missing.check_existing_final(final, first)

    # Sidecars never enter the actual pool, so they must not invalidate a final.
    (pool / "baseline.results.json").write_text(json.dumps({"conversation_history": [{"myths": {"Agent_1": "ignored"}}]}))
    unchanged = run_noisy_missing.load_combinations("example", "unused.yaml")[0]
    run_noisy_missing.check_existing_final(final, unchanged)

    (pool / "later.json").write_text(json.dumps({"conversation_history": [{"myths": {"Agent_1": "second myth"}}]}))
    changed = run_noisy_missing.load_combinations("example", "unused.yaml")[0]
    assert first["comparison_inputs"] == changed["comparison_inputs"]
    with pytest.raises(ConditionMismatchError, match="different shuffled myth pool"):
        run_noisy_missing.check_existing_final(final, changed)


def test_worker_rejects_pool_changed_after_planning_before_simulation(monkeypatch):
    from experiments import run_noisy_batch
    from test_hf_batch_integration import _minimal_combo

    combo = _minimal_combo()
    prepare_combinations([combo], {"llm_settings": settings()}, {})
    combo["execution_provenance"] = {"shuffled_myth_pool_sha256": digest(("planned",))}
    monkeypatch.setattr(run_noisy_batch, "TrustGameNoisy", lambda **kwargs: SimpleNamespace(_shuffled_myth_pool=("changed",)))
    monkeypatch.setattr(run_noisy_batch, "run_simulation", lambda **kwargs: pytest.fail("Must reject before an API call"))
    result = run_noisy_batch.run_single_experiment(combo, "example", 0)
    assert result["success"] is False
    assert result["file_path"] is None
    assert "pool changed" in result["error"]


def test_pinned_set_never_relabels_legacy_final_as_complete(tmp_path):
    combo = {"model": "openai/gpt-5-nano"}
    prepare_combinations([combo], {"llm_settings": settings()}, {}, allow_legacy=True)
    legacy = saved_run()
    legacy["run_metadata"] = {}
    path = write_run(tmp_path / "legacy.json", legacy)
    with pytest.raises(ConditionMismatchError, match="new pinned experiment"):
        run_noisy_missing.check_existing_final(path, combo)
    combo["request_plan"] = None
    run_noisy_missing.check_existing_final(path, combo)


def test_existing_modern_final_requires_matching_inputs(tmp_path):
    combo = {"model": "openai/gpt-5-nano", "template": "rules"}
    prepare_combinations([combo], {"llm_settings": settings()}, {})
    saved = saved_run()
    saved["run_metadata"]["comparison_inputs"] = copy.deepcopy(combo["comparison_inputs"])
    path = write_run(tmp_path / "modern.json", saved)
    run_noisy_missing.check_existing_final(path, combo)
    saved["run_metadata"]["comparison_inputs"]["template"] = "different"
    write_run(path, saved)
    with pytest.raises(ConditionMismatchError, match="configured inputs"):
        run_noisy_missing.check_existing_final(path, combo)

import copy
import importlib
import json
import sys
from types import SimpleNamespace

import pytest

from analyses._shared import load_simulation_runs
from scripts import hf_sync_completed_runs
from src.experiment_condition import (
    ConditionMismatchError, build_condition, check_conditions, comparison_condition, condition_from_run,
    digest, output_provenance, validate_output_provenance,
)
from test_llm_request_plan import plan_for


def saved_run(replicate=0):
    request = plan_for().as_dict()
    metadata = {"llm_request": request, "llm_provider": "openai", "provider_model": "gpt-5-nano"}
    game = SimpleNamespace(system_prompt_template="unchanged rules", noise_seed=3)
    condition = build_condition(game, None, metadata, {"memory_capacity": 3, "task_order": ["game"]}, {"replicate_id": replicate})
    metadata.update(experiment_condition=condition, condition_sha256=digest(condition))
    return {"agents": {}, "conversation_history": [], "game_data": {}, "task_order": ["game"], "run_metadata": metadata}


def write_run(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data))
    return path


def test_replication_requires_a_named_difference():
    first = condition_from_run(saved_run(0))
    second = condition_from_run(saved_run(1))
    with pytest.raises(ConditionMismatchError, match="replicate"):
        check_conditions([first, second])
    assert check_conditions([first, second], {"replicate": "Independent repeats"})


def test_loader_rejects_copied_runs_even_with_replicate_allowance(tmp_path):
    first = write_run(tmp_path / "run.json", saved_run())
    copied = write_run(tmp_path / "copied.json", saved_run())
    with pytest.raises(ValueError, match="Duplicate run contents"):
        load_simulation_runs([first, copied], allowed_differences={"replicate": "Independent repeats"})


def test_loader_accepts_distinct_declared_replicates(tmp_path):
    first = write_run(tmp_path / "run0.json", saved_run(0))
    second = write_run(tmp_path / "run1.json", saved_run(1))
    assert len(load_simulation_runs([first, second], allowed_differences={"replicate": "Independent repeats"})) == 2


@pytest.mark.parametrize("module_name", ["cooperation_ratio_over_time", "resources_over_time_max"])
def test_plot_rejects_copied_runs_before_writing_outputs(tmp_path, monkeypatch, module_name):
    module = importlib.import_module(f"analyses.{module_name}")
    first = write_run(tmp_path / "run.json", saved_run())
    copied = write_run(tmp_path / "copied.json", saved_run())
    output = tmp_path / "outputs"
    monkeypatch.setattr(module, "load_runs", lambda root: [{"source_path": str(first)}, {"source_path": str(copied)}])
    monkeypatch.setattr(sys, "argv", [module_name, "--root", str(tmp_path), "--out", str(output)])
    with pytest.raises(ValueError, match="Duplicate run contents"):
        module.main()
    assert not output.exists()


@pytest.mark.parametrize("field", ["system_prompt_template", "noise_config", "history_policy", "decision_format"])
def test_prompt_and_game_differences_are_not_hidden_by_equal_llm_settings(field):
    first = condition_from_run(saved_run())
    second = copy.deepcopy(first)
    second["protocol"]["game"][field] = "different"
    with pytest.raises(ConditionMismatchError, match=field):
        check_conditions([first, second])


def test_whole_llm_block_cannot_be_exempted():
    with pytest.raises(ConditionMismatchError, match="individual"):
        check_conditions([condition_from_run(saved_run())], {"llm": "all settings may differ"})


def test_recorded_parameters_must_agree_with_policy():
    data = saved_run()
    condition = data["run_metadata"]["experiment_condition"]
    condition["llm"]["parameters"]["max_completion_tokens"] = 1
    data["run_metadata"]["condition_sha256"] = digest(condition)
    with pytest.raises(ConditionMismatchError, match="parameters"):
        condition_from_run(data)


def test_loader_rejects_unknown_legacy_unless_acknowledged(tmp_path):
    data = saved_run()
    data["run_metadata"] = {}
    path = write_run(tmp_path / "legacy.json", data)
    with pytest.raises(ConditionMismatchError, match="Historical"):
        load_simulation_runs([path])
    assert load_simulation_runs([path], legacy_reason="Historical exploratory result, settings unknown")


def test_legacy_model_difference_requires_explicit_declaration(tmp_path):
    first = saved_run()
    first["run_metadata"] = {"model": "anthropic/claude-sonnet-4.5"}
    second = saved_run()
    second["run_metadata"] = {"model": "openai/gpt-5-nano"}
    paths = [write_run(tmp_path / "claude.json", first), write_run(tmp_path / "gpt.json", second)]
    reason = "Historical exploratory comparison; provider and reasoning were not recorded"
    with pytest.raises(ConditionMismatchError, match="llm.model"):
        load_simulation_runs(paths, legacy_reason=reason)
    assert len(load_simulation_runs(paths, legacy_reason=reason, allowed_differences={"llm.model": "Intentional cross-model comparison"})) == 2


@pytest.mark.parametrize("field,first_value,second_value", [
    ("temperature_sent", False, True),
    ("temperature_source", "config", "environment"),
    ("thinking_level_source", "default", "GEMINI_THINKING_LEVEL"),
    ("max_output_tokens_source", "provider_default", "ANTHROPIC_MAX_TOKENS"),
    ("llm_provider_mode", "auto", "direct"),
])
def test_legacy_request_metadata_differences_need_declaration(field, first_value, second_value):
    first = {"run_metadata": {"model": "google/gemini-3.7-flash", "temperature": 0.8, field: first_value}}
    second = copy.deepcopy(first)
    second["run_metadata"][field] = second_value
    conditions = [comparison_condition(run, "Exploratory legacy data") for run in (first, second)]
    with pytest.raises(ConditionMismatchError, match=field):
        check_conditions(conditions)
    assert check_conditions(conditions, {f"llm.{field}": "Explicit historical difference"}) == [f"llm.{field}"]
    assert conditions[0]["llm"]["reasoning"] == "unrecorded"


def test_unrecorded_temperature_sent_is_distinct_from_false():
    recorded = comparison_condition({"run_metadata": {"temperature_sent": False}}, "Historical")
    unknown = comparison_condition({"run_metadata": {}}, "Historical")
    with pytest.raises(ConditionMismatchError, match="temperature_sent"):
        check_conditions([recorded, unknown])


@pytest.mark.parametrize("metadata,expected_model", [({}, "unrecorded"), ({"model": "openai/gpt-5-nano"}, "openai/gpt-5-nano")])
def test_legacy_model_is_preserved_without_inferring_provider(metadata, expected_model):
    data = saved_run()
    data["run_metadata"] = metadata
    condition = comparison_condition(data, "Historical exploratory comparison")
    assert condition["llm"]["model"] == expected_model
    assert condition["llm"]["provider"] == "unrecorded"
    assert condition["llm"]["provider_model"] == "unrecorded"


def test_legacy_flag_does_not_bypass_corrupt_modern_record(tmp_path):
    data = saved_run()
    data["run_metadata"]["condition_sha256"] = "wrong"
    path = write_run(tmp_path / "run.json", data)
    with pytest.raises(ConditionMismatchError, match="digest"):
        load_simulation_runs([path], legacy_reason="Not a bypass")


@pytest.mark.parametrize("suffix", [".checkpoint.json", ".error.json", ".results.json"])
def test_loader_rejects_non_final_artifacts(tmp_path, suffix):
    path = write_run(tmp_path / ("run" + suffix), saved_run())
    with pytest.raises(ConditionMismatchError, match="final"):
        load_simulation_runs([path])


def test_each_calls_settings_are_checked():
    data = saved_run()
    data["agents"] = {"agent": {"interaction_history": [{"response": {"content": '{"send": 2}', "usage": {"finish_reason": "stop", "outcome": "complete"}}}]}}
    with pytest.raises(ConditionMismatchError, match="Per-call"):
        condition_from_run(data)


@pytest.mark.parametrize("source", ["scripted", "forced_zero", "random_defection_forced_zero", "deduction_notification"])
def test_non_llm_events_are_not_checked_for_request_settings(source):
    data = saved_run()
    data["agents"] = {"agent": {"interaction_history": [{"response": {"content": '{"send": 0}', "usage": {}, "response_source": source}}]}}
    condition_from_run(data)


def test_missing_call_record_cannot_bypass_validation():
    data = saved_run()
    data["agents"] = {"agent": {"interaction_history": [{"prompt": "decision"}]}}
    with pytest.raises(ConditionMismatchError, match="Per-call"):
        condition_from_run(data)


def test_manifest_recomputes_declared_differences(tmp_path):
    first = write_run(tmp_path / "run0.json", saved_run(0))
    second = write_run(tmp_path / "run1.json", saved_run(1))
    output = tmp_path / "summary.csv"
    output.write_text("example\n")
    document = output_provenance([first, second], [output], {"replicate": "Independent repeats"})
    document["observed_differences"] = []
    with pytest.raises(ConditionMismatchError, match="misstates"):
        validate_output_provenance(document)


def test_unprovenanced_final_is_complete_but_not_uploadable(tmp_path):
    data = saved_run()
    data["run_metadata"] = {}
    path = write_run(tmp_path / "run.json", data)
    assert hf_sync_completed_runs.is_completed_final_json(path, data_root=tmp_path)
    kwargs = {"data_root": tmp_path, "repo_id": "owner/dataset", "namespace": "test"}
    assert not hf_sync_completed_runs.build_upload_plan([path], **kwargs).final_paths
    assert hf_sync_completed_runs.build_upload_plan([path], allow_legacy_provenance=True, **kwargs).final_paths


def test_historical_upload_flag_cannot_accept_broken_modern_provenance(tmp_path):
    data = saved_run()
    data["run_metadata"]["condition_sha256"] = "wrong"
    path = write_run(tmp_path / "run.json", data)
    plan = hf_sync_completed_runs.build_upload_plan([path], data_root=tmp_path, repo_id="owner/dataset", namespace="test", allow_legacy_provenance=True)
    assert not plan.final_paths

import hashlib
import json

import pytest
import yaml

from scripts.check_safeguards import BASELINE, check_config, check_launcher, check_output, check_repository, config_signature
from src.llm_settings import LLMSettingsError
from test_llm_request_plan import settings


def configuration(pinned=True):
    class Config:
        config = {"experiment_sets": {"example": {"llm_settings": settings()} if pinned else {}}}

        def get_experiment_combinations(self, name):
            return [{"model": "openai/gpt-5-nano", "template": self.config["experiment_sets"][name].get("template", "rules")}]

    return Config()


def test_frozen_legacy_baseline_and_repository_checks():
    assert hashlib.sha256(BASELINE.read_bytes()).hexdigest() == "5f2109d1c1a9985349deea56e6cea009e70f2d43f019a90bc3aa4010caf2d722"
    check_repository()


def test_ci_rejects_new_unpinned_set():
    with pytest.raises(LLMSettingsError):
        check_config(configuration(False), "config/example.yaml", {})


@pytest.mark.parametrize("source_name,target_name", [
    ("experiments_noisy.yaml", "renamed.yaml"),
    ("experiments.yaml", "contains_noisy.yaml"),
])
def test_repository_selects_config_format_from_content(tmp_path, monkeypatch, source_name, target_name):
    from scripts import check_safeguards

    document = yaml.safe_load((check_safeguards.ROOT / "config" / source_name).read_text())
    name = next(iter(document["experiment_sets"]))
    definition = document["experiment_sets"][name]
    definition["llm_settings"] = settings(provider="openrouter", reasoning={"reasoning": {"enabled": False}})
    document["experiment_sets"] = {name: definition}
    document.pop("comparison_sets", None)
    directory = tmp_path / "config"
    directory.mkdir()
    (directory / target_name).write_text(yaml.safe_dump(document))
    monkeypatch.setattr(check_safeguards, "repository_state", lambda root: (set(), {}))
    check_repository(tmp_path, {"configurations": {}, "launchers": {}, "outputs": {}})
    definition.pop("llm_settings")
    (directory / target_name).write_text(yaml.safe_dump(document))
    with pytest.raises(LLMSettingsError, match="no llm_settings"):
        check_repository(tmp_path, {"configurations": {}, "launchers": {}, "outputs": {}})


@pytest.mark.parametrize("keys", [[], ["game_params", "game_parameters"]])
def test_repository_rejects_unknown_or_ambiguous_config_format(tmp_path, monkeypatch, keys):
    from scripts import check_safeguards

    directory = tmp_path / "config"
    directory.mkdir()
    document = {"experiment_sets": {}, **{key: {} for key in keys}}
    (directory / "example.yaml").write_text(yaml.safe_dump(document))
    with pytest.raises(ValueError, match="exactly one"):
        check_repository(tmp_path, {"configurations": {}, "launchers": {}, "outputs": {}})


def test_ci_rejects_changed_legacy_set():
    config = configuration(False)
    baseline = {"config/example.yaml:example": config_signature(config, "example")}
    check_config(config, "config/example.yaml", baseline)
    config.config["experiment_sets"]["example"]["template"] = "different prompt"
    with pytest.raises(LLMSettingsError):
        check_config(config, "config/example.yaml", baseline)


def test_ci_rejects_undeclared_comparison_difference():
    config = configuration()
    config.config["experiment_sets"]["other"] = {"llm_settings": settings(), "template": "different prompt"}
    config.config["comparison_sets"] = {"test": {"experiment_sets": ["example", "other"]}}
    with pytest.raises(ValueError, match="template"):
        check_config(config, "config/example.yaml", {})
    config.config["comparison_sets"]["test"]["allowed_differences"] = {"template": "Prompt is the intervention"}
    check_config(config, "config/example.yaml", {})


def test_ci_rejects_unguarded_launcher(tmp_path):
    path = tmp_path / "launch_example.sh"
    path.write_text("#!/bin/bash\npython3 arbitrary_legacy_script.py\n")
    with pytest.raises(ValueError, match="wrapper"):
        check_launcher(path, tmp_path)


@pytest.mark.parametrize("arguments", ["--allow-legacy", "--config=other.yaml", "--conf other.yaml"])
def test_ci_rejects_ambiguous_launcher_options(tmp_path, arguments):
    path = tmp_path / "launch_example.sh"
    path.write_text(f"set -euo pipefail\nexec python3 experiments/run_noisy_batch.py example {arguments}\n")
    with pytest.raises(ValueError, match="full supported"):
        check_launcher(path, tmp_path)


def test_ci_rejects_missing_output_provenance(tmp_path):
    output = tmp_path / "figure.png"
    output.write_bytes(b"example")
    with pytest.raises(ValueError, match="missing provenance"):
        check_output(tmp_path, [output])


def test_ci_rejects_stale_output_hashes(tmp_path):
    from src.experiment_condition import output_provenance
    from test_experiment_condition import saved_run, write_run

    source = write_run(tmp_path / "input" / "run.json", saved_run())
    directory = tmp_path / "figure"
    directory.mkdir()
    output = directory / "summary.csv"
    output.write_text("initial")
    manifest = directory / "provenance.json"
    manifest.write_text(json.dumps(output_provenance([source], [output])))
    check_output(directory, [output, manifest])
    output.write_text("modified without recomputing provenance")
    with pytest.raises(ValueError, match="hashes"):
        check_output(directory, [output, manifest])

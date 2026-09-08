"""Check changed configurations, launch wrappers, and committed output manifests."""

import argparse
import hashlib
import json
import shlex
import subprocess
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from experiments.run_noisy_batch import NoisyExperimentConfig
from src.experiment_config import ExperimentConfig
from src.experiment_condition import check_conditions, digest, validate_output_provenance
from src.llm_settings import comparison_inputs, prepare_combinations
from src.utils import DIRECT_MODEL_ALIASES


ROOT = Path(__file__).resolve().parent.parent
BASELINE = ROOT / "tests/fixtures/safeguards_legacy_baseline.json"
RUNNERS = {
    "experiments/run_noisy_batch.py": "config/experiments_noisy.yaml",
    "scripts/run_noisy_missing.py": "config/experiments_noisy.yaml",
    "experiments/run_trust_game_batch.py": "config/experiments.yaml",
}


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "missing"


def config_signature(config, name):
    definition = config.config["experiment_sets"][name]
    try:
        combinations = config.get_experiment_combinations(name)
    except KeyError:
        return digest({"unresolved_legacy_definition": definition})
    return digest({"definition": definition, "expanded_inputs": combinations})


def check_config(config, relative_path, baseline):
    for name, definition in config.config["experiment_sets"].items():
        key = f"{relative_path}:{name}"
        if "llm_settings" not in definition and baseline.get(key) == config_signature(config, name):
            continue
        prepare_combinations(config.get_experiment_combinations(name), definition, DIRECT_MODEL_ALIASES)
    for declaration in config.config.get("comparison_sets", {}).values():
        names = declaration["experiment_sets"]
        if len(names) < 2 or len(set(names)) != len(names):
            raise ValueError("Comparison must name distinct experiment sets")
        contrasts = []
        for name in names:
            combinations = config.get_experiment_combinations(name)
            prepare_combinations(combinations, config.config["experiment_sets"][name], DIRECT_MODEL_ALIASES)
            contrasts.extend(comparison_inputs(combo) for combo in combinations)
        check_conditions(contrasts, declaration.get("allowed_differences"))


def check_launcher(path, root=ROOT):
    lines = [line.strip() for line in path.read_text().replace("\\\n", " ").splitlines() if line.strip() and not line.lstrip().startswith("#")]
    if len(lines) != 2 or lines[0] != "set -euo pipefail":
        raise ValueError(f"{path}: new launchers must be a simple set -euo pipefail + exec python3 runner wrapper")
    if any(character in lines[1] for character in "$`;|&><()"):
        raise ValueError(f"{path}: dynamic shell commands are not a verified launcher")
    tokens = shlex.split(lines[1])
    if len(tokens) < 4 or tokens[:2] != ["exec", "python3"] or tokens[2] not in RUNNERS:
        raise ValueError(f"{path}: use a guarded batch runner")
    if "--allow-legacy-settings" in tokens or tokens[3].startswith("-"):
        raise ValueError(f"{path}: new launchers must select a pinned experiment")
    config_path = RUNNERS[tokens[2]]
    value_options = {"--workers"}
    if tokens[2] != "experiments/run_trust_game_batch.py":
        value_options.update({"--config", "--output-subdir"})
        value_options.update({"--limit", "--log-dir"} if tokens[2] == "scripts/run_noisy_missing.py" else {"--max-runs"})
    arguments = iter(tokens[4:])
    for option in arguments:
        if option == "--dry-run":
            continue
        value = next(arguments, None)
        if option not in value_options or value is None or value.startswith("-"):
            raise ValueError(f"{path}: use full supported option names and separate literal values")
        if option == "--config":
            config_path = value
    resolved = (root / config_path).resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError("Launcher config must be in the repository")
    loader = ExperimentConfig if tokens[2] == "experiments/run_trust_game_batch.py" else NoisyExperimentConfig
    config = loader(str(resolved))
    prepare_combinations(config.get_experiment_combinations(tokens[3]), config.config["experiment_sets"][tokens[3]], DIRECT_MODEL_ALIASES)


def check_output(directory, files):
    manifest = directory / "provenance.json"
    if not manifest.is_file():
        raise ValueError(f"{directory}: missing provenance.json")
    document = json.loads(manifest.read_text())
    validate_output_provenance(document)
    expected = {str(path.relative_to(directory)): file_hash(path) for path in files if path != manifest}
    if not expected or document.get("outputs") != expected:
        raise ValueError(f"{directory}: output hashes are missing, stale, or incomplete")


def repository_state(root=ROOT):
    listed = subprocess.check_output(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"], cwd=root).decode().split("\0")
    files = {root / name for name in listed if name}
    groups = {}
    for path in files:
        relative = path.relative_to(root).as_posix()
        if relative.startswith(("data/analysis/", "docs/figures/", "data/plots/")):
            parts = path.relative_to(root).parts
            directory = root.joinpath(*parts[:3]) if len(parts) > 3 else path.parent
            groups.setdefault(directory, set()).add(path)
    launchers = {path for path in files if path.parent == root / "scripts" and path.name.startswith("launch_")}
    return launchers, groups


def snapshot(root=ROOT):
    definitions = {}
    for filename, loader in (("config/experiments.yaml", ExperimentConfig), ("config/experiments_noisy.yaml", NoisyExperimentConfig)):
        config = loader(str(root / filename))
        definitions.update({f"{filename}:{name}": config_signature(config, name) for name in config.config["experiment_sets"]})
    launchers, groups = repository_state(root)
    return {
        "source_commit": "5e00733afddcd0667e759adb4d965a6fb876c42c",
        "configurations": definitions,
        "launchers": {str(path.relative_to(root)): file_hash(path) for path in sorted(launchers)},
        "outputs": {str(directory.relative_to(root)): digest({str(path.relative_to(directory)): file_hash(path) for path in files}) for directory, files in sorted(groups.items())},
    }


def check_repository(root=ROOT, baseline=None):
    baseline = baseline if baseline is not None else json.loads(BASELINE.read_text())
    for path in sorted((root / "config").glob("*.yaml")):
        document = yaml.safe_load(path.read_text())
        if not isinstance(document, dict) or "experiment_sets" not in document:
            continue
        formats = {"game_parameters", "game_params"}.intersection(document)
        if len(formats) != 1:
            raise ValueError(f"{path}: experiment config must contain exactly one of game_parameters or game_params")
        loader = NoisyExperimentConfig if "game_params" in document else ExperimentConfig
        config = loader(str(path))
        check_config(config, str(path.relative_to(root)), baseline["configurations"])
    launchers, groups = repository_state(root)
    for path in launchers:
        if baseline["launchers"].get(str(path.relative_to(root))) != file_hash(path):
            check_launcher(path, root)
    for directory, files in groups.items():
        signature = digest({str(path.relative_to(directory)): file_hash(path) for path in files})
        if baseline["outputs"].get(str(directory.relative_to(root))) != signature:
            check_output(directory, files)


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    check_repository()
    print("Safeguard configuration, launcher, and output checks passed")


if __name__ == "__main__":
    main()

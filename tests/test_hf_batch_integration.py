import json
import sys
from pathlib import Path

from experiments import run_noisy_batch, run_trust_game_batch
from scripts import run_noisy_missing


def _minimal_combo():
    return {
        "request_plan": None,
        "model": "openai/gpt-5-nano",
        "persona": {"description": "neutral"},
        "task_order": ["game"],
        "template": "system",
        "trust_game_round1_investor": "round 1 investor",
        "trust_game_round1_trustee": "round 1 trustee",
        "trust_game_later_investor": "later investor",
        "trust_game_later_trustee": "later trustee",
        "myth_writing_default": "myth round 1",
        "myth_writing_later_rounds": "myth later",
        "game_params_name": "params",
        "game_params": {
            "endowment": 10,
            "multiplier": 3,
            "num_agents": 2,
            "num_turns": 1,
            "memory_capacity": 1,
        },
    }


class _SavedFinalThenTranscriptFails:
    def __init__(self):
        self.run_metadata = {}

    def save_state(self, path):
        Path(path).write_text(
            json.dumps(
                {
                    "agents": {},
                    "conversation_history": [],
                    "game_data": {},
                    "task_order": ["game"],
                }
            ),
            encoding="utf-8",
        )

    def save_transcript_pdf(self, path, *, source_path):
        raise RuntimeError("transcript rendering failed")


def test_run_noisy_missing_syncs_existing_completed_paths_once(
    monkeypatch,
    tmp_path,
):
    combo = {
        "model": "openai/gpt-5-nano",
        "task_order": ["game"],
        "game_params_name": "params",
        "persona": {"description": "neutral"},
    }
    monkeypatch.setattr(run_noisy_missing, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(
        run_noisy_missing,
        "load_combinations",
        lambda experiment_name, config_path, **kwargs: [combo],
    )

    final_path = run_noisy_missing.expected_output_path(
        combo,
        "example",
        0,
        "output",
    )
    final_path.parent.mkdir(parents=True, exist_ok=True)
    _SavedFinalThenTranscriptFails().save_state(final_path)

    sync_calls = []

    def capture(paths, *, label):
        sync_calls.append((list(paths), label))
        return True

    monkeypatch.setattr(run_noisy_missing, "maybe_sync_completed_runs", capture)
    monkeypatch.setattr(
        sys,
        "argv",
        ["run_noisy_missing.py", "example", "--output-subdir", "output"],
    )

    assert run_noisy_missing.main() == 0
    assert sync_calls == [([final_path], "output/example")]


def test_noisy_runner_returns_saved_final_candidate_when_transcript_fails(
    monkeypatch,
    tmp_path,
):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(run_noisy_batch, "TrustGameNoisy", lambda **kwargs: object())
    monkeypatch.setattr(run_noisy_batch, "MythWriter", lambda **kwargs: object())
    monkeypatch.setattr(
        run_noisy_batch,
        "run_simulation",
        lambda **kwargs: _SavedFinalThenTranscriptFails(),
    )

    result = run_noisy_batch.run_single_experiment(
        _minimal_combo(),
        "example",
        0,
        "output",
    )

    assert result["success"] is False
    assert Path(result["file_path"]).is_file()
    assert "transcript rendering failed" in result["error"]


def test_trust_runner_returns_saved_final_candidate_when_transcript_fails(
    monkeypatch,
    tmp_path,
):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(run_trust_game_batch, "TrustGame", lambda **kwargs: object())
    monkeypatch.setattr(run_trust_game_batch, "MythWriter", lambda **kwargs: object())
    monkeypatch.setattr(
        run_trust_game_batch,
        "run_simulation",
        lambda **kwargs: _SavedFinalThenTranscriptFails(),
    )

    result = run_trust_game_batch.run_single_experiment(
        _minimal_combo(),
        "example",
        0,
    )

    assert result["success"] is False
    assert Path(result["file_path"]).is_file()
    assert "transcript rendering failed" in result["error"]


def test_general_noisy_runner_syncs_candidate_even_when_wrapper_fails(monkeypatch):
    combo = {
        "model": "openai/gpt-5-nano",
        "persona": {"description": "neutral"},
        "task_order": ["game"],
        "game_params_name": "params",
        "game_params": {
            "noise_config": None,
            "other_player_names": "default",
        },
    }

    class FakeConfig:
        def __init__(self, config_path):
            self.config_path = config_path
            self.config = {"experiment_sets": {"example": {}}}

        def get_experiment_combinations(self, experiment_name, max_runs=None):
            return [combo]

    monkeypatch.setattr(run_noisy_batch, "NoisyExperimentConfig", FakeConfig)
    monkeypatch.setattr(
        run_noisy_batch,
        "execution_provenance",
        lambda config_path: {},
    )
    monkeypatch.setattr(
        run_noisy_batch,
        "run_single_experiment",
        lambda *args, **kwargs: {
            "success": False,
            "file_path": "data/json/noise_experiments/output/example/run.json",
            "error": "transcript rendering failed after final-state save",
        },
    )
    sync_calls = []
    monkeypatch.setattr(
        run_noisy_batch,
        "maybe_sync_completed_runs",
        lambda paths, *, label: sync_calls.append((list(paths), label)),
    )

    run_noisy_batch.run_experiment_set(
        "example",
        workers=1,
        config_path="config.yaml",
        output_subdir="output",
        allow_legacy_settings=True,
    )

    assert sync_calls == [
        (["data/json/noise_experiments/output/example/run.json"], "output/example")
    ]


def test_general_trust_runner_syncs_candidate_even_when_wrapper_fails(monkeypatch):
    combo = {
        "model": "openai/gpt-5-nano",
        "persona": {"description": "neutral"},
        "task_order": ["game"],
    }

    class FakeConfig:
        def __init__(self, config_path):
            self.config_path = config_path
            self.config = {"experiment_sets": {"example": {}}}

        def get_experiment_combinations(self, experiment_name):
            return [combo]

    monkeypatch.setattr(run_trust_game_batch, "ExperimentConfig", FakeConfig)
    monkeypatch.setattr(
        run_trust_game_batch,
        "run_single_experiment",
        lambda *args, **kwargs: {
            "success": False,
            "file_path": "data/json/example/run.json",
            "error": "transcript rendering failed after final-state save",
        },
    )
    sync_calls = []
    monkeypatch.setattr(
        run_trust_game_batch,
        "maybe_sync_completed_runs",
        lambda paths, *, label: sync_calls.append((list(paths), label)),
    )

    run_trust_game_batch.run_experiment_set("example", workers=1, allow_legacy_settings=True)

    assert sync_calls == [(["data/json/example/run.json"], "example")]

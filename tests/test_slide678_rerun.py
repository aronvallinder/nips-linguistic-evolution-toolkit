import copy
import json
from types import SimpleNamespace

import pytest

from scripts import rerun_slide678 as runner
from scripts import supervise_slide678 as supervisor
from scripts import watch_slide678_progress as progress
from src.llm_settings import RequestPlan


HISTORICAL_FINALS = runner.ROOT / "data/json/noise_experiments/phase3_baseline"
SEED_MANIFEST = runner.ROOT / "data/phase3/seed_manifest.json"


def require_historical_finals():
    """The frozen plan is built from gitignored run data; skip where it is absent (CI)."""
    if not SEED_MANIFEST.is_file() or not HISTORICAL_FINALS.is_dir():
        pytest.skip("historical slide-678 finals under data/json are not in this checkout")


@pytest.fixture(scope="module")
def plan():
    require_historical_finals()
    return runner.prepare()


def test_frozen_matrix_matches_historical_contexts(plan):
    assert len(plan["combos"]) == 35
    assert {c["seed_type"] for c in plan["combos"]} == set(runner.CELLS)
    assert plan["request"]["provider_model"] == "claude-sonnet-4-5-20250929"
    assert "temperature" not in plan["request"]["parameters"]
    for combo in plan["combos"]:
        assert combo["task_order"] == ["game"]
        assert combo["game_params"]["num_turns"] == 10
        assert combo["game_params"]["noise_config"]["range"] == 5.0
        assert combo["game_params"]["history_policy"] == "none"


@pytest.mark.parametrize("cell", list(runner.CELLS))
def test_full_mocked_run_memory_receipts_and_skip(plan, cell, tmp_path, monkeypatch):
    request = RequestPlan(json.dumps(plan["request"]))
    client = SimpleNamespace(request_plan=request)
    monkeypatch.setattr("src.simulation.create_llm_client", lambda *a, **kw: client)
    calls = []

    def respond(client, model, temperature, messages):
        calls.append(copy.deepcopy(messages))
        prompt = messages[-1]["content"]
        decision = {"send": 5} if "How much do you send" in prompt else {"return": 0}
        return {"content": json.dumps(decision), "reasoning": None,
                "usage": {"request_settings": plan["request"], "outcome": "complete", "finish_reason": "end_turn"}}

    monkeypatch.setattr("src.agents.call_llm", respond)
    combo = next(c for c in plan["combos"] if c["seed_type"] == cell)
    result = runner.run_one(plan, combo, tmp_path)
    assert result["status"] == "complete", result
    assert len(calls) == 80
    assert {len(c) for c in calls} == ({2} if cell == "baseline" else {4})
    assert runner.run_one(plan, combo, tmp_path)["status"] == "existing"
    assert len(calls) == 80
    data = runner.verify_final(runner.final_path(tmp_path, combo), plan, combo)
    data["conversation_history"].pop()
    with pytest.raises(ValueError, match="complete"):
        runner.validate_memory(data, combo)


def test_plan_mismatch_cannot_be_counted_as_completed(plan, tmp_path, monkeypatch):
    combo = plan["combos"][0]
    data = json.loads((runner.ROOT / combo["historical_final"]).read_text())
    with pytest.raises(ValueError):
        runner.verify_final(runner.ROOT / combo["historical_final"], plan, combo)
    data["agents"]["Agent_1"]["interaction_history"][0]["messages_sent"].insert(1, {"role": "user", "content": "old game"})
    with pytest.raises(ValueError, match="Context mismatch"):
        runner.validate_memory(data, combo)


def test_supervisor_usage_includes_rejected_response_receipts():
    data = {"agents": {"Agent_1": {"interaction_history": [
        {"error": {"type": "InvalidGameResponseError"}, "response": {"usage": {"input_tokens": 10, "output_tokens": 20}}},
        {"response": {"usage": {"input_tokens": 30, "output_tokens": 40}}},
    ]}}}
    assert supervisor.usage_of(data) == {"calls": 2, "input_tokens": 40, "output_tokens": 60}


def test_supervisor_does_not_call_provider_above_cost_gate(plan, tmp_path, monkeypatch):
    (tmp_path / "plan.json").write_text(json.dumps(plan))
    for combo in plan["combos"][:2]:
        path = runner.final_path(tmp_path, combo)
        path.parent.mkdir(parents=True)
        path.touch()
    monkeypatch.setattr(supervisor, "audit", lambda *a: {"completed": 2, "projected_usd_with_margin": 101})
    monkeypatch.setattr(supervisor.subprocess, "run", lambda *a, **kw: pytest.fail("Must not launch above $100"))
    monkeypatch.setattr("sys.argv", ["supervise_slide678", "--output", str(tmp_path)])
    supervisor.main()
    assert json.loads((tmp_path / "supervisor_status.json").read_text())["status"] == "approval_required"
    assert not (tmp_path / "supervisor.lock").exists()


def test_progress_snapshot_reports_checkpoint(plan, tmp_path):
    source = runner.ROOT / plan["combos"][0]["historical_final"]
    cell = tmp_path / "baseline"
    cell.mkdir()
    data = json.loads(source.read_text())
    data["conversation_history"] = data["conversation_history"][:3]
    for agent in data["agents"].values():
        agent["interaction_history"] = [
            event for event in agent["interaction_history"]
            if event["metadata"]["round"] <= 3
        ]
    (cell / "rep00.checkpoint.json").write_text(json.dumps(data))
    (tmp_path / "supervisor_status.json").write_text('{"status":"running"}')
    _, line, terminal = progress.snapshot(tmp_path)
    assert line.startswith("ACTIVE | No inherited text (game-only baseline)")
    assert "replicate 1/5 | 3/10 rounds | 24/80 decisions" in line
    assert "\n" not in line
    assert not terminal

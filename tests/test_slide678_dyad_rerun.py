import copy
import json
from types import SimpleNamespace

import pytest

from scripts import rerun_slide678_dyad as runner
from src.llm_settings import RequestPlan


@pytest.fixture(scope="module")
def plan():
    return runner.prepare()


def test_dyad_plan_is_exact_population_counterpart(plan):
    assert len(plan["combos"]) == 35
    assert {combo["seed_type"] for combo in plan["combos"]} == set(runner.population.CELLS)
    assert {combo["game_params"]["num_agents"] for combo in plan["combos"]} == {2}
    assert plan["request"]["provider_model"] == "claude-sonnet-4-5-20250929"
    assert "temperature" not in plan["request"]["parameters"]


@pytest.mark.parametrize("cell", list(runner.population.CELLS))
def test_full_mocked_dyad_context_and_completion(plan, cell, tmp_path, monkeypatch):
    request = RequestPlan(json.dumps(plan["request"]))
    client = SimpleNamespace(request_plan=request)
    monkeypatch.setattr("src.simulation.create_llm_client", lambda *args, **kwargs: client)
    calls = []

    def respond(client, model, temperature, messages):
        calls.append(copy.deepcopy(messages))
        prompt = messages[-1]["content"]
        decision = {"send": 5} if "How much do you send" in prompt else {"return": 0}
        return {
            "content": json.dumps(decision),
            "reasoning": None,
            "usage": {
                "request_settings": plan["request"],
                "outcome": "complete",
                "finish_reason": "end_turn",
            },
        }

    monkeypatch.setattr("src.agents.call_llm", respond)
    combo = next(combo for combo in plan["combos"] if combo["seed_type"] == cell)
    outcome = runner.run_one(plan, combo, tmp_path)
    assert outcome["status"] == "complete", outcome
    assert len(calls) == 20
    assert {len(call) for call in calls} == ({2} if cell == "baseline" else {4})
    data = runner.verify_final(runner.final_path(tmp_path, combo), plan, combo)
    assert len(data["agents"]) == 2
    assert len(data["conversation_history"]) == 10

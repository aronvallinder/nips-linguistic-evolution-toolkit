"""Free end-to-end checks: real SDK, loopback HTTP, simulator, saved state, guards."""

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import httpx
import pytest
from openai import OpenAI

from analyses._shared import load_simulation_runs, write_output_provenance
from games.trust_game import TrustGame
from src.experiment_condition import ConditionMismatchError, condition_from_run
from src.simulation import run_simulation
from src.utils import LLMClient
from test_llm_request_plan import openai_response, plan_for, settings


@pytest.mark.parametrize("runner_name", ["run_noisy_batch", "run_trust_game_batch"])
def test_runner_dry_run_stops_before_workers_and_uploads(monkeypatch, capsys, runner_name):
    import importlib

    runner = importlib.import_module(f"experiments.{runner_name}")

    class Config:
        def __init__(self, path):
            self.config = {"experiment_sets": {"example": {"llm_settings": settings()}}}

        def get_experiment_combinations(self, name, **kwargs):
            return [{"model": "openai/gpt-5-nano"}]

    def unexpected(*args, **kwargs):
        raise AssertionError("Dry run must not start a worker or upload")

    loader = "NoisyExperimentConfig" if runner_name == "run_noisy_batch" else "ExperimentConfig"
    monkeypatch.setattr(runner, loader, Config)
    monkeypatch.setattr(runner, "run_single_experiment", unexpected)
    monkeypatch.setattr(runner, "maybe_sync_completed_runs", unexpected)
    runner.run_experiment_set("example", dry_run=True)
    assert "PINNED REQUEST:" in capsys.readouterr().out


def game():
    return TrustGame(
        endowment=5, multiplier=3, system_prompt_template="Game rules",
        round1_investor_template='Respond exactly as JSON: {{"send": amount}}',
        round1_trustee_template='Respond exactly as JSON: {{"return": amount}}',
        later_investor_template="Send an amount.", later_trustee_template="Return an amount.",
    )


@pytest.fixture
def local_simulation(monkeypatch, tmp_path):
    captured = []

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            payload = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            captured.append(payload)
            response = openai_response(details={"reasoning_tokens": 0})
            key = "send" if len(captured) % 2 else "return"
            response["choices"][0]["message"]["content"] = json.dumps({key: 3})
            body = json.dumps(response).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    transport = httpx.HTTPTransport()

    class LoopbackTransport(httpx.BaseTransport):
        def handle_request(self, request):
            local_url = f"http://127.0.0.1:{server.server_port}{request.url.path}"
            return transport.handle_request(httpx.Request(request.method, local_url, headers=request.headers, content=request.content))

    native = OpenAI(api_key="test-key", base_url="https://api.openai.com/v1", max_retries=0, http_client=httpx.Client(transport=LoopbackTransport()))

    def create(model, request_plan=None):
        client = LLMClient("openai", native)
        client.request_plan = request_plan
        return client

    monkeypatch.setattr("src.simulation.create_llm_client", create)
    plan = plan_for()
    arguments = {
        "game": game(), "model": "openai/gpt-5-nano", "temperature": 0.8,
        "num_turns": 1, "num_agents": 2, "memory_capacity": 3,
        "agent_biases": "", "myth_writer": None, "task_order": ["game"],
        "request_plan": plan, "run_identity": {"replicate_id": 0},
        "checkpoint_path": str(tmp_path / "run.checkpoint.json"), "checkpoint_every": 1,
    }
    try:
        yield arguments, captured, tmp_path
    finally:
        native.close()
        transport.close()
        server.shutdown()
        worker.join(timeout=5)
        server.server_close()


def test_loopback_request_to_saved_record_to_analysis(local_simulation):
    arguments, captured, directory = local_simulation
    state = run_simulation(**arguments)
    final = directory / "run.json"
    state.save_state(final)
    data = json.loads(final.read_text())
    condition_from_run(data)
    assert len(captured) == 2
    for payload, agent in zip(captured, data["agents"].values()):
        usage = agent["interaction_history"][0]["response"]["usage"]
        assert {key: value for key, value in payload.items() if key not in {"model", "messages"}} == usage["request_settings"]["parameters"]
        assert usage["finish_reason"] == "stop"
        assert payload["model"] == usage["request_settings"]["provider_model"]
    load_simulation_runs([final])
    output_dir = directory / "analysis"
    output_dir.mkdir()
    (output_dir / "summary.txt").write_text("synthetic smoke output, not research data\n")
    write_output_provenance(output_dir, [final])
    manifest = json.loads((output_dir / "provenance.json").read_text())
    assert manifest["runs"][0]["condition"] == data["run_metadata"]["experiment_condition"]
    arguments["game"] = game()
    resumed = run_simulation(**arguments, resume_from=arguments["checkpoint_path"])
    assert resumed.run_metadata == state.run_metadata
    assert len(captured) == 2


@pytest.mark.parametrize("change", ["reasoning", "cap", "prompt", "memory", "task_order", "identity"])
def test_resume_refuses_changed_condition_before_http(local_simulation, change):
    arguments, captured, directory = local_simulation
    run_simulation(**arguments)
    changed = dict(arguments, game=game())
    if change == "reasoning":
        changed["request_plan"] = plan_for(reasoning={"reasoning_effort": "high"})
    elif change == "cap":
        changed["request_plan"] = plan_for(cap=256)
    elif change == "prompt":
        changed["game"].system_prompt_template = "Different rules"
    elif change == "memory":
        changed["memory_capacity"] = 9
    elif change == "task_order":
        changed["task_order"] = ["myth", "game"]
    else:
        changed["run_identity"] = {"replicate_id": 1}
    with pytest.raises(ConditionMismatchError):
        run_simulation(**changed, resume_from=arguments["checkpoint_path"])
    assert len(captured) == 2


def test_guarded_retry_default_ignores_machine_environment(local_simulation, monkeypatch):
    arguments, captured, directory = local_simulation
    monkeypatch.setenv("GAME_RESPONSE_RETRY_POLICY", "invalid-machine-setting")
    state = run_simulation(**arguments)
    condition = state.run_metadata["experiment_condition"]
    assert condition["protocol"]["game_retry"]["policy"] == "repeat_same_prompt_once"
    assert len(captured) == 2

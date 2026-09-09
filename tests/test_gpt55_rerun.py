"""Frozen-config regressions and a free 1,000-request gate smoke."""
import copy
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading

import httpx
from openai import OpenAI
import pytest

from experiments.run_noisy_batch import NoisyExperimentConfig
from scripts import rerun_gpt55_gate as entry
from scripts.analyze_gpt55_negative_only_gate import EXPECTED_BASE, audit_gate, audit_run
from scripts.check_safeguards import BASELINE, ROOT, legacy_launcher_opt_in
from scripts.gpt55_gate_contract import CONFIG_SHA256, HISTORICAL, load_gate, verify_rerun
from src.experiment_condition import digest
from src.utils import LLMClient
from test_llm_request_plan import openai_response


def test_rerun_preserves_every_original_expanded_input():
    original = NoisyExperimentConfig(str(ROOT / 'config/experiments_noisy.yaml'))
    for name, combo in load_gate().items():
        expected = original.get_experiment_combinations(name)[0]
        observed = copy.deepcopy(combo)
        assert observed['game_params'].pop('game_response_retry_policy') == 'repeat_same_prompt_once'
        assert {k: observed[k] for k in expected} == expected
        assert combo['request_plan'].as_dict()['parameters'] == {'reasoning_effort': 'low'}


def test_legacy_wrapper_migration_is_only_the_opt_in(tmp_path):
    baseline = json.loads(BASELINE.read_text())['launchers']
    names = ['launch_gpt55_negative_only_gate_20260901.sh', 'launch_gpt55_negative_only_gate_r2_20260901.sh', 'launch_negative_only_crossmodel_defectors_n5.sh']
    for name in names:
        path = ROOT / 'scripts' / name
        expected = baseline[f'scripts/{name}']
        assert legacy_launcher_opt_in(path, expected)
        changed = tmp_path / name
        changed.write_text(path.read_text().replace('--workers', '--limit'))
        assert not legacy_launcher_opt_in(changed, expected)
        assert not legacy_launcher_opt_in(path, None)


def test_gate_dry_run_never_creates_workers(tmp_path, monkeypatch):
    monkeypatch.setattr(entry, 'ROOT', tmp_path)
    def unexpected(*args, **kwargs):
        raise AssertionError('Dry run started workers')
    monkeypatch.setattr(entry, 'ProcessPoolExecutor', unexpected)
    entry.run_gate('dry_run')
    assert not (tmp_path / 'data').exists()


def test_twelve_cells_through_http_final_audit_and_resume(tmp_path, monkeypatch):
    captured = []
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            payload = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            captured.append(payload)
            prompt = payload['messages'][-1]['content']
            if 'you are the sender' in prompt.lower():
                content = '{"send": 3}'
            elif 'you are the receiver' in prompt.lower():
                content = '{"return": 1}'
            else:
                content = 'A river taught the village to share. Each spring they retold its story.'
            response = openai_response(details={'reasoning_tokens': 0})
            response['choices'][0]['message']['content'] = content
            body = json.dumps(response).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        def log_message(self, *args):
            pass
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    transport = httpx.HTTPTransport()
    class Loopback(httpx.BaseTransport):
        def handle_request(self, request):
            return transport.handle_request(httpx.Request(request.method, f'http://127.0.0.1:{server.server_port}{request.url.path}', headers=request.headers, content=request.content))
    native = OpenAI(api_key='test-key', max_retries=0, http_client=httpx.Client(transport=Loopback()))
    def create(model, request_plan=None):
        client = LLMClient('openai', native)
        client.request_plan = request_plan
        return client
    monkeypatch.setattr('src.simulation.create_llm_client', create)
    monkeypatch.setattr(entry, 'ROOT', tmp_path)
    monkeypatch.setattr('scripts.run_noisy_missing.PROJECT_ROOT', tmp_path)
    # One worker exercises the controller without spawning a separate Python
    # interpreter, keeping the real SDK's network traffic on loopback only.
    monkeypatch.setattr(entry, 'ProcessPoolExecutor', ThreadPoolExecutor)
    monkeypatch.setattr(entry, 'execution_provenance', lambda path: {'code_commit': 'test-only', 'code_dirty': False, 'config_sha256': CONFIG_SHA256})
    monkeypatch.setenv('OPENAI_API_KEY', 'test-key')
    monkeypatch.setenv('OPENAI_REASONING_EFFORT', 'high')
    monkeypatch.setenv('GAME_RESPONSE_RETRY_POLICY', 'invalid-machine-setting')
    monkeypatch.chdir(tmp_path)
    try:
        summaries = entry.run_gate('synthetic', workers=1, execute=True)
        assert len(captured) == 1000
        assert all(s['completion_passed'] for s in summaries)
        assert all(s['behavioral_headroom'] == 'requires_review' for s in summaries)
        for payload in captured:
            assert {k: v for k, v in payload.items() if k != 'messages'} == {'model': 'gpt-5.5-2026-04-23', 'reasoning_effort': 'low'}
        entry.run_gate('synthetic', workers=1, execute=True, resume=True)
        assert len(captured) == 1000  # No duplicate paid calls on resume.
        stage = tmp_path / 'data/json/noise_experiments/synthetic/r1'
        originals = {p: p.read_text() for p in stage.rglob('*.json') if not p.name.endswith(('.results.json', '.checkpoint.json', '.error.json'))}
        for sent in (0, 5):
            for path, raw in originals.items():
                saturated = json.loads(raw)
                for round_entry in saturated['conversation_history']:
                    for dyad in round_entry['dyads']:
                        dyad.update(sent=sent, sent_communicated=sent, received=3 * sent, returned=0)
                path.write_text(json.dumps(saturated))
            summary = audit_gate(stage, tmp_path / f'saturation_{sent}', 0)
            assert summary['completion_passed']
            assert summary['behavioral_headroom'] == 'requires_review'
            assert 'gate_passed' not in summary
        for path, raw in originals.items():
            path.write_text(raw)
        first = next((tmp_path / 'data/json/noise_experiments/synthetic/r1/gpt55_gate_dyad_game_r1').rglob('*_neutral_rep00.json'))
        run = json.loads(first.read_text())
        for field in ('system_prompt_template', 'history_policy', 'noise_semantics'):
            changed = copy.deepcopy(run)
            changed['run_metadata']['experiment_condition']['protocol']['game'][field] = 'changed'
            changed['run_metadata']['condition_sha256'] = digest(changed['run_metadata']['experiment_condition'])
            with pytest.raises(ValueError, match='frozen specification'):
                verify_rerun(changed, 'gpt55_gate_dyad_game_r1')
        # Legacy finals need the actual original hash/SHA, not just six equal values.
        legacy = copy.deepcopy(run)
        legacy['run_metadata'].pop('experiment_condition')
        first.write_text(json.dumps(legacy))
        with pytest.raises(RuntimeError, match='historical gate'):
            audit_run(first, EXPECTED_BASE['gpt55_gate_dyad_game'], 0)
        # A file with the right name is not a full-state final.
        first.write_text(json.dumps({'run_metadata': run['run_metadata']}))
        with pytest.raises(ValueError, match='full-state'):
            audit_run(first, EXPECTED_BASE['gpt55_gate_dyad_game'], 0)
    finally:
        native.close()
        transport.close()
        server.shutdown()
        worker.join(timeout=5)
        server.server_close()

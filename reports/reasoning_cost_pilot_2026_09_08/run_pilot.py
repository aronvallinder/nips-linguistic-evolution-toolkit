"""Replay archived requests for cost calibration, never as behavioral replicates."""

import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import random
import re
import statistics
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request

ROOT = Path('/Users/ivar/Desktop/Research/AI_projects/LLM_evolution/nips-linguistic-evolution-toolkit')
sys.path.insert(0, str(ROOT))
from src.llm_settings import canonical, resolve_request_plan
from src.utils import DIRECT_MODEL_ALIASES, _anthropic_messages, _chat_messages, _gemini_messages

ARCHIVE = ROOT / 'data/shared_runs/uploaders/vallinder/data/json/noise_experiments/negative_only_crossmodel_defectors_n5_20260825'
OUTPUT = ROOT / 'reports/reasoning_cost_pilot_2026_09_08'
POLICIES = {
    'anthropic/claude-sonnet-4.5': {'provider': 'anthropic', 'reasoning': {'thinking': {'type': 'enabled', 'budget_tokens': 8192}}, 'temperature': 'default', 'max_output_tokens': 64000},
    'openai/gpt-5-nano': {'provider': 'openai', 'reasoning': {'reasoning_effort': 'high'}, 'temperature': 'default', 'max_output_tokens': 128000},
    'google/gemini-3.7-flash': {'provider': 'google', 'reasoning': {'thinkingConfig': {'thinkingLevel': 'high'}}, 'temperature': 0.8, 'max_output_tokens': 65536},
}
RATES = {'anthropic': (3.0, 15.0), 'openai': (0.05, 0.40), 'google': (0.75, 3.75)}
KEY_NAMES = {'anthropic': 'ANTHROPIC_API_KEY', 'openai': 'OPENAI_API_KEY', 'google': 'GEMINI_API_KEY'}
LOCK = threading.Lock()


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def select_contexts():
    pools = defaultdict(list)
    populations = Counter()
    for path in sorted(ARCHIVE.rglob('*.json')):
        if path.name.endswith(('.results.json', '.checkpoint.json', '.error.json')):
            continue
        original = path.read_bytes()
        data = json.loads(original)
        if not {'agents', 'conversation_history', 'game_data', 'run_metadata', 'task_order'} <= data.keys():
            continue
        original_hash = hashlib.sha256(original).hexdigest()
        metadata = data['run_metadata']
        model = metadata['model']
        if model not in POLICIES:
            continue
        for agent_id, agent in data['agents'].items():
            for event in agent.get('interaction_history', []):
                response = event.get('response') or {}
                detail = event.get('metadata') or {}
                if event.get('error') or response.get('response_source', 'llm') != 'llm':
                    continue
                task = detail.get('task')
                if task not in {'game', 'myth'}:
                    continue
                turn = detail['round']
                period = 'early' if turn <= 3 else ('middle' if turn <= 7 else 'late')
                stratum = f"{metadata['num_agents']}agents/{task}/{period}"
                messages = _chat_messages(event['messages_sent'])
                source = {
                    'path': str(path.relative_to(ROOT)), 'file_sha256': original_hash,
                    'agent_id': agent_id, 'interaction_index': event['interaction_index'],
                    'round': turn, 'task': task, 'role': detail.get('role'), 'task_order': data['task_order'],
                    'replicate_id': metadata.get('replicate_id'), 'num_agents': metadata['num_agents'],
                }
                context = {'model': model, 'stratum': stratum, 'source': source, 'messages': messages,
                           'messages_sha256': digest(messages), 'previous_usage': response.get('usage') or {}}
                context['job_id'] = digest({'model': model, 'source': source})[:20]
                pools[model, stratum].append(context)
                populations[model, stratum] += 1
    selected = []
    for (model, stratum), candidates in sorted(pools.items()):
        generator = random.Random(f'20260908/{model}/{stratum}')
        generator.shuffle(candidates)
        if '/game/' in stratum:
            chosen = [next(context for context in candidates if context['source']['role'] == role) for role in ('investor', 'trustee')]
        else:
            chosen = [next(context for context in candidates if context['source']['task_order'] == order) for order in (['game', 'myth'], ['myth', 'game'])]
        selected.extend(chosen)
    assert Counter(context['model'] for context in selected) == Counter({model: 24 for model in POLICIES})
    assert all(sum(count for (group_model, _), count in populations.items() if group_model == model) == 6378 for model in POLICIES)
    return selected, populations


def request_body(context, plan):
    model = plan.provider_model
    parameters = plan.parameters
    if plan.provider == 'anthropic':
        system, messages = _anthropic_messages(context['messages'])
        return '/v1/messages', {'model': model, 'system': system, 'messages': messages, **parameters}
    if plan.provider == 'openai':
        return '/chat/completions', {'model': model, 'messages': context['messages'], **parameters}
    system, contents = _gemini_messages(context['messages'])
    return f'/models/{model}:generateContent', {'system_instruction': system, 'contents': contents, 'generationConfig': parameters}


def usage_and_answer(provider, response):
    if provider == 'anthropic':
        usage = response.get('usage') or {}
        details = usage.get('output_tokens_details') or {}
        reasoning = details.get('thinking_tokens', details.get('reasoning_tokens'))
        answer = ''.join(block.get('text', '') for block in response.get('content', []) if block.get('type') == 'text')
        return usage, usage.get('input_tokens'), usage.get('output_tokens'), reasoning, response.get('stop_reason'), answer, response.get('model')
    if provider == 'openai':
        usage = response.get('usage') or {}
        details = usage.get('completion_tokens_details') or {}
        choice = (response.get('choices') or [{}])[0]
        answer = (choice.get('message') or {}).get('content') or ''
        return usage, usage.get('prompt_tokens'), usage.get('completion_tokens'), details.get('reasoning_tokens'), choice.get('finish_reason'), answer, response.get('model')
    usage = response.get('usageMetadata') or {}
    choice = (response.get('candidates') or [{}])[0]
    answer = ''.join(part.get('text', '') for part in choice.get('content', {}).get('parts', []) if not part.get('thought'))
    visible = usage.get('candidatesTokenCount')
    reasoning = usage.get('thoughtsTokenCount')
    billed_output = visible + (reasoning or 0) if visible is not None else None
    return usage, usage.get('promptTokenCount'), billed_output, reasoning, choice.get('finishReason'), answer, response.get('modelVersion')


def record_result(record):
    with LOCK:
        with (OUTPUT / 'calls.jsonl').open('a') as handle:
            handle.write(json.dumps(record, allow_nan=False) + '\n')
        print(json.dumps({key: record.get(key) for key in ('model', 'job_id', 'stratum', 'status', 'finish_reason', 'reasoning_tokens', 'billed_output_tokens', 'cost_usd', 'http_status', 'error')}), flush=True)


def run_model(model, contexts, completed):
    plan = resolve_request_plan(model, POLICIES[model], DIRECT_MODEL_ALIASES)
    api_key = os.environ.get(KEY_NAMES[plan.provider])
    if not api_key:
        print(f'MISSING_KEY: {model}', flush=True)
        return
    contexts = sorted(contexts, key=lambda context: ('/early' not in context['stratum'], context['stratum'], context['job_id']))
    for context in contexts:
        if context['job_id'] in completed:
            continue
        suffix, payload = request_body(context, plan)
        headers = {'Content-Type': 'application/json'}
        if plan.provider == 'anthropic':
            headers.update({'x-api-key': api_key, 'anthropic-version': '2023-06-01'})
        elif plan.provider == 'openai':
            headers['Authorization'] = f'Bearer {api_key}'
        else:
            headers['x-goog-api-key'] = api_key
        for attempt in (1, 2):
            started = time.monotonic()
            record = {key: context[key] for key in ('model', 'job_id', 'stratum', 'source', 'messages_sha256', 'previous_usage')}
            record.update({'attempt': attempt, 'request_plan': plan.as_dict(), 'request_sha256': digest(payload), 'timestamp': datetime.now(timezone.utc).isoformat()})
            try:
                request = urllib.request.Request(plan.as_dict()['endpoint'] + suffix, data=json.dumps(payload).encode(), headers=headers, method='POST')
                with urllib.request.urlopen(request, timeout=1200) as connection:
                    response = json.load(connection)
                usage, input_tokens, output_tokens, reasoning, finish, answer, response_model = usage_and_answer(plan.provider, response)
                input_rate, output_rate = RATES[plan.provider]
                cost = (input_tokens * input_rate + output_tokens * output_rate) / 1e6 if input_tokens is not None and output_tokens is not None else None
                record.update({'status': 'received', 'elapsed_seconds': time.monotonic() - started, 'usage': usage,
                               'input_tokens': input_tokens, 'billed_output_tokens': output_tokens, 'reasoning_tokens': reasoning,
                               'finish_reason': finish, 'response_model': response_model, 'response_id': response.get('id', response.get('responseId')),
                               'answer': answer, 'cost_usd': cost, 'cost_assumes_uncached_input': True})
                record_result(record)
                if not answer or finish in {'length', 'max_tokens', 'MAX_TOKENS'}:
                    print(f'STOPPED_MODEL: {model}: empty or truncated answer needs inspection', flush=True)
                    return
                break
            except urllib.error.HTTPError as error:
                message = error.read().decode(errors='replace')[:1500]
                for key_name in KEY_NAMES.values():
                    secret = os.environ.get(key_name)
                    if secret:
                        message = message.replace(secret, '[REDACTED]')
                record.update({'status': 'http_error', 'http_status': error.code, 'error': message, 'elapsed_seconds': time.monotonic() - started})
                record_result(record)
                if error.code not in {429, 500, 502, 503, 504} or attempt == 2:
                    print(f'STOPPED_MODEL: {model}: HTTP {error.code}', flush=True)
                    return
                time.sleep(10)
            except Exception as error:
                record.update({'status': 'transport_error', 'error': type(error).__name__, 'elapsed_seconds': time.monotonic() - started})
                record_result(record)
                print(f'STOPPED_MODEL: {model}: transport outcome unknown; no automatic retry', flush=True)
                return


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--model', choices=list(POLICIES))
    args = parser.parse_args()
    contexts, populations = select_contexts()
    models = [args.model] if args.model else list(POLICIES)
    manifest = {
        'purpose': 'Cost-only replay of frozen historical contexts, not new simulation runs or behavioral evidence',
        'policies': POLICIES, 'rates_per_million_tokens_usd': RATES, 'workers': 3, 'sampling_seed': 20260908,
        'sampling': 'Two contexts per model/population/task/period; game roles balanced, myth task orders balanced. Historical contexts are not updated with new answers.',
        'projection_limitations': 'Two observations per stratum; frozen low-reasoning histories do not capture changed future trajectories, retry rates, or input lengths.',
        'code_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'pilot_script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'population_counts': {model: {stratum: count for (group_model, stratum), count in populations.items() if group_model == model} for model in POLICIES},
        'contexts': [{key: value for key, value in context.items() if key != 'messages'} for context in contexts],
    }
    estimated = 0.0
    ceiling = 0.0
    for context in contexts:
        if context['model'] not in models:
            continue
        plan = resolve_request_plan(context['model'], POLICIES[context['model']], DIRECT_MODEL_ALIASES)
        input_rate, output_rate = RATES[plan.provider]
        original_usage = context['previous_usage']
        estimated += ((original_usage.get('input_tokens') or 0) * input_rate + ((original_usage.get('output_tokens') or 0) + 4096) * output_rate) / 1e6
        ceiling += ((sum(len(message['content']) for message in context['messages']) + 4000) * input_rate + POLICIES[context['model']]['max_output_tokens'] * output_rate) / 1e6
    print(f'PREFLIGHT: MODEL={",".join(models)} N={24 * len(models)}_API_calls WORKERS=3 EST_COST=${estimated * 1.5:.2f} CONSERVATIVE_RESERVE=${ceiling * 2:.2f} CMD=python3 {Path(__file__)} --execute' + (f' --model {args.model}' if args.model else ''), flush=True)
    for model in models:
        print('PINNED_REQUEST: ' + resolve_request_plan(model, POLICIES[model], DIRECT_MODEL_ALIASES).encoded, flush=True)
    if not args.execute:
        print('DRY_RUN_ONLY: no API calls or artifacts written', flush=True)
        return
    assert ceiling * 2 < 100, 'Pilot maximum-output reserve exceeds approval threshold'
    OUTPUT.mkdir(parents=True, exist_ok=True)
    manifest_path = OUTPUT / 'manifest.json'
    if manifest_path.exists():
        previous = json.loads(manifest_path.read_text())
        assert previous['policies'] == manifest['policies'] and previous['contexts'] == manifest['contexts'], 'Refusing to mix changed pilot settings or sources'
    else:
        manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
    results_path = OUTPUT / 'calls.jsonl'
    completed = set()
    if results_path.exists():
        completed = {record['job_id'] for line in results_path.read_text().splitlines() if (record := json.loads(line)).get('status') == 'received'}
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(run_model, model, [context for context in contexts if context['model'] == model], completed) for model in models]
        for future in futures:
            future.result()
    print(f'PILOT_FINISHED: inspect {results_path}', flush=True)


if __name__ == '__main__':
    main()

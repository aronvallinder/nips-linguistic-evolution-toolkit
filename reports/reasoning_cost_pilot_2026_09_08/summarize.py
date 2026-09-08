"""Validate and summarize the cost-only replay sample without making API calls."""

from collections import Counter, defaultdict
import json
from pathlib import Path
import statistics
import sys


DIRECTORY = Path(__file__).resolve().parent
sys.path.insert(0, str(DIRECTORY.parent.parent))
from games.base_game import Game
from src.myth_writer import validate_myth_response

DOCUMENTED_SNAPSHOTS = {'gpt-5-nano': {'gpt-5-nano-2025-08-07'}}


def main():
    manifest = json.loads((DIRECTORY / 'manifest.json').read_text())
    records = [json.loads(line) for line in (DIRECTORY / 'calls.jsonl').read_text().splitlines()]
    expected = {context['job_id']: context for context in manifest['contexts']}
    received = {}
    boundary_failures = []
    for record in records:
        assert record['job_id'] in expected
        context = expected[record['job_id']]
        assert record['source'] == context['source']
        assert record['messages_sha256'] == context['messages_sha256']
        assert record['request_plan']['policy'] == manifest['policies'][record['model']]
        if record['status'] == 'received':
            assert record['job_id'] not in received, 'A selected request was billed twice; inspect before summarizing'
            assert record['cost_usd'] is not None
            requested_model = record['request_plan']['provider_model']
            accepted_models = {requested_model} | DOCUMENTED_SNAPSHOTS.get(requested_model, set())
            assert record['response_model'] in accepted_models, 'Returned model differs from requested model'
            provider = record['request_plan']['provider']
            input_rate, output_rate = manifest['rates_per_million_tokens_usd'][provider]
            calculated = (record['input_tokens'] * input_rate + record['billed_output_tokens'] * output_rate) / 1e6
            assert abs(record['cost_usd'] - calculated) < 1e-10
            if provider == 'anthropic':
                assert not record['usage'].get('cache_read_input_tokens')
                assert not record['usage'].get('cache_creation_input_tokens')
            if provider == 'google':
                assert record['usage']['totalTokenCount'] == record['input_tokens'] + record['billed_output_tokens']
            try:
                if record['source']['task'] == 'game':
                    Game().validate_game_response(record['answer'], record['source']['role'])
                else:
                    validate_myth_response(record['answer'])
            except ValueError as error:
                boundary_failures.append({'job_id': record['job_id'], 'model': record['model'], 'error_type': type(error).__name__})
            received[record['job_id']] = record
    summary = {
        'complete': len(received) == len(expected), 'received': len(received), 'expected': len(expected),
        'attempt_status_counts': dict(Counter(record['status'] for record in records)),
        'recorded_pilot_cost_usd': sum(record.get('cost_usd') or 0 for record in records),
        'models': {}, 'limitations': manifest['projection_limitations'],
        'response_boundary_failures': boundary_failures,
    }
    for model, population in manifest['population_counts'].items():
        subset = [record for record in received.values() if record['model'] == model]
        strata = defaultdict(list)
        for record in subset:
            strata[record['stratum']].append(record)
        projected = 0.0
        complete_model = len(subset) == 24 and all(len(strata[stratum]) == 2 for stratum in population)
        if complete_model:
            projected = sum(count * statistics.mean(record['cost_usd'] for record in strata[stratum]) for stratum, count in population.items())
        tasks = {}
        for task in ('game', 'myth'):
            task_records = [record for record in subset if record['source']['task'] == task]
            thinking = [record['reasoning_tokens'] for record in task_records if record['reasoning_tokens'] is not None]
            tasks[task] = {
                'calls': len(task_records), 'reasoning_count_observed': len(thinking),
                'reasoning_tokens_mean': statistics.mean(thinking) if thinking else None,
                'reasoning_tokens_sample_sd': statistics.stdev(thinking) if len(thinking) > 1 else None,
                'reasoning_tokens_min': min(thinking) if thinking else None,
                'reasoning_tokens_max': max(thinking) if thinking else None,
            }
        summary['models'][model] = {
            'calls': len(subset), 'complete': complete_model,
            'pilot_cost_usd': sum(record['cost_usd'] for record in subset),
            'projected_90_run_cost_usd': projected if complete_model else None,
            'tasks': tasks, 'finish_reasons': dict(Counter(record['finish_reason'] for record in subset)),
            'response_models': dict(Counter(record['response_model'] for record in subset)),
        }
    if summary['complete']:
        summary['projected_270_run_cost_usd'] = sum(group['projected_90_run_cost_usd'] for group in summary['models'].values())
        summary['projected_270_run_cost_with_20_percent_allowance_usd'] = 1.2 * summary['projected_270_run_cost_usd']
    (DIRECTORY / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()

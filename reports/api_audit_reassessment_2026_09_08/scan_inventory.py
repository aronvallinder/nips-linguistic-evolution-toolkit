"""Recheck a fixed selection from the historical audit index without vendor calls."""

import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--repo-root", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
arguments = parser.parse_args()
ROOT = arguments.repo_root.resolve()
OUTPUT = arguments.output
TARGET_PARTS = ('negative_only_crossmodel_defectors_n5_20260825', 'ablation_phase1', 'memtest_', 'phase2_', 'phase3_', 'phase4_', 'phase5_', 'phase6_', 'phase7_', 'phase8_', 'mem3_', 'myth_causal_confirm_claude_fixed_prompt', 'baseline_match_ablation', 'v4_direct_provider', 'washout_20round', 'sonnet45_8agent_game_memprimary_r10_n5', 'sonnet45_8agent_game_myth_memprimary_r10_n5', 'sonnet45_8agent_myth_directive_history3_anon_memprimary_r10_n5')
FIELDS = ('model', 'llm_provider', 'provider_model', 'llm_provider_mode', 'temperature', 'temperature_sent', 'max_output_tokens', 'max_output_tokens_source', 'thinking_level', 'thinking_level_source', 'code_commit', 'code_dirty', 'provider_env', 'openai_reasoning_effort_env', 'config_sha256', 'num_agents', 'num_turns', 'chat_memory_mode', 'memory_capacity')


def value_name(value):
    return json.dumps(value, sort_keys=True)


def summarized_calls(data):
    counts = collections.Counter()
    token_ranges = collections.defaultdict(list)
    for round_entry in data.get('conversation_history') or []:
        for task in ('game', 'myth'):
            responses = round_entry.get(task + '_responses') or {}
            for response in responses.values():
                if not isinstance(response, dict):
                    continue
                if response.get('response_source', 'llm') != 'llm':
                    counts[task + '_non_llm'] += 1
                    continue
                counts[task + '_calls'] += 1
                usage = response.get('usage')
                if not isinstance(usage, dict):
                    counts[task + '_usage_missing'] += 1
                    usage = {}
                reasoning_tokens = usage.get('reasoning_tokens')
                if reasoning_tokens is None:
                    counts[task + '_reasoning_tokens_missing'] += 1
                elif reasoning_tokens == 0:
                    counts[task + '_reasoning_tokens_zero'] += 1
                elif isinstance(reasoning_tokens, (int, float)) and reasoning_tokens > 0:
                    counts[task + '_reasoning_tokens_positive'] += 1
                    token_ranges[task + '_reasoning_tokens_positive'].append(reasoning_tokens)
                if usage.get('output_tokens') is not None:
                    token_ranges[task + '_output_tokens'].append(usage['output_tokens'])
                if usage.get('finish_reason') is None:
                    counts[task + '_finish_reason_missing'] += 1
                reasoning = response.get('reasoning')
                if isinstance(reasoning, str) and reasoning.strip():
                    kind = 'placeholder' if reasoning.startswith('[') and 'reasoning tokens' in reasoning else 'text'
                    counts[task + '_reasoning_' + kind] += 1
                else:
                    counts[task + '_reasoning_absent'] += 1
    counts['interaction_errors'] = sum(bool(item.get('error')) for agent in (data.get('agents') or {}).values() for item in agent.get('interaction_history') or [])
    return dict(counts), {key: {'min': min(values), 'max': max(values)} for key, values in token_ranges.items()}


def family_name(expset):
    name = expset.split('/')[-1]
    if name.startswith('memtest_'):
        return name
    if name.startswith('v4_direct_provider') and name != 'v4_direct_provider':
        return 'v4_direct_provider_followups'
    return name


inventory = list(csv.DictReader((ROOT / 'data/analysis/api_equivalence_audit_2026_09_04/runs_inventory_inferred.csv').open()))
selected = [row for row in inventory if any(part in row['expset'] for part in TARGET_PARTS)]
records = {}
missing = []
invalid = []
for index, row in enumerate(selected):
    source = ROOT / row['path']
    if not source.exists():
        missing.append(row['path'])
        continue
    raw = source.read_bytes()
    fingerprint = hashlib.sha256(raw).hexdigest()
    if fingerprint in records:
        records[fingerprint]['paths'].append(row['path'])
        continue
    data = json.loads(raw)
    if not isinstance(data, dict) or not {'agents', 'conversation_history', 'game_data', 'task_order', 'run_metadata'}.issubset(data):
        invalid.append(row['path'])
        continue
    metadata = data['run_metadata']
    counts, ranges = summarized_calls(data)
    records[fingerprint] = {
        'sha256': fingerprint,
        'paths': [row['path']],
        'expset': row['expset'],
        'family': family_name(row['expset']),
        'metadata': {key: metadata.get(key, 'MISSING') for key in FIELDS},
        'task_order': data.get('task_order'),
        'rounds': len(data.get('conversation_history') or []),
        'replicate_id': metadata.get('replicate_id', metadata.get('ablation_rep', metadata.get('baseline_match_run'))),
        'counts': counts,
        'ranges': ranges,
    }
    if index % 500 == 0:
        print(f'scanned {index}/{len(selected)}', flush=True)

groups = {}
for record in records.values():
    key = record['family'] + ' :: ' + str(record['metadata']['model'])
    group = groups.setdefault(key, {'runs': 0, 'paths': 0, 'metadata': {field: collections.Counter() for field in FIELDS}, 'counts': collections.Counter(), 'ranges': {}, 'examples': [], 'expsets': set()})
    group['runs'] += 1
    group['paths'] += len(record['paths'])
    for field, value in record['metadata'].items():
        group['metadata'][field][value_name(value)] += 1
    group['counts'].update(record['counts'])
    for field, limits in record['ranges'].items():
        previous = group['ranges'].get(field, limits)
        group['ranges'][field] = {'min': min(previous['min'], limits['min']), 'max': max(previous['max'], limits['max'])}
    if len(group['examples']) < 3:
        group['examples'].append(record['paths'][0])
    group['expsets'].add(record['expset'])

for group in groups.values():
    group['expsets'] = sorted(group['expsets'])
result = {'inventory_rows': len(inventory), 'selected_inventory_rows': len(selected), 'unique_bytes_final_records': len(records), 'present_paths': sum(len(record['paths']) for record in records.values()), 'missing_paths': missing, 'invalid_paths': invalid, 'groups': groups, 'records': list(records.values())}
result['round_count_mismatches'] = [record['paths'][0] for record in records.values() if record['rounds'] != record['metadata']['num_turns']]
OUTPUT.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({key: value for key, value in result.items() if key not in ('records', 'groups')}, indent=2))
for key, group in sorted(groups.items()):
    relevant = {field: values for field, values in group['metadata'].items() if field in ('llm_provider', 'provider_model', 'temperature', 'temperature_sent', 'max_output_tokens', 'thinking_level', 'provider_env', 'openai_reasoning_effort_env')}
    print(key, 'unique=', group['runs'], 'paths=', group['paths'], 'metadata=', json.dumps(relevant), 'calls=', json.dumps(group['counts']))

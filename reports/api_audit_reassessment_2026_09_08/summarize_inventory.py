"""Export allowlisted settings aggregates and source identities for the review."""

import argparse
import hashlib
import json
from pathlib import Path


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--repo-root", type=Path, required=True)
parser.add_argument("--scan", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
parser.add_argument("--sources-output", type=Path, required=True)
arguments = parser.parse_args()
ROOT = arguments.repo_root.resolve()
source = json.loads(arguments.scan.read_text())
by_path = {path: record for record in source['records'] for path in record['paths']}
groups = source['groups']
for group in groups.values():
    group['examples'] = [{'path': path, 'sha256': by_path[path]['sha256']} for path in group['examples']]
mixed_claude = []
for record in source['records']:
    counts = record['counts']
    if str(record['metadata']['model']).startswith('anthropic/') and counts.get('game_reasoning_text') and counts.get('game_reasoning_absent'):
        data = json.loads((ROOT / record['paths'][0]).read_text())
        rounds = []
        for number, round_entry in enumerate(data['conversation_history'], 1):
            responses = [response for response in (round_entry.get('game_responses') or {}).values() if isinstance(response, dict) and response.get('response_source', 'llm') == 'llm']
            rounds.append({'round_position': number, 'game_calls': len(responses), 'with_reasoning_text': sum(bool(response.get('reasoning')) for response in responses)})
        mixed_claude.append({'path': record['paths'][0], 'sha256': record['sha256'], 'recorded_provider': record['metadata']['llm_provider'], 'game_calls': counts['game_calls'], 'game_reasoning_text': counts['game_reasoning_text'], 'game_reasoning_absent': counts['game_reasoning_absent'], 'rounds': rounds})
inventory = ROOT / 'data/analysis/api_equivalence_audit_2026_09_04/runs_inventory_inferred.csv'
result = {
    'review_date': '2026-09-08',
    'inventory': str(inventory.relative_to(ROOT)),
    'inventory_sha256': hashlib.sha256(inventory.read_bytes()).hexdigest(),
    'selected_inventory_rows': source['selected_inventory_rows'],
    'present_full_state_paths': source['present_paths'],
    'distinct_byte_sha256_files': source['unique_bytes_final_records'],
    'exact_copy_paths_removed': source['present_paths'] - source['unique_bytes_final_records'],
    'missing_paths': source['missing_paths'],
    'invalid_paths': source['invalid_paths'],
    'round_count_mismatches': source['round_count_mismatches'],
    'count_unit': 'Files listed by the historical inventory, not verified independent replicates. Exact byte copies removed before grouped summaries.',
    'usage_caveat': 'Counts are stored normalized fields, not raw vendor usage. A missing numeric value is separate from zero in this extractor, but historical request adapters sometimes wrote zero when usage was absent and hard-coded zero for Anthropic.',
    'scientific_scope': 'Retrospective settings evidence only. This does not validate outcomes, independence, completeness of attempted runs, or currently available model capabilities.',
    'groups': groups,
    'mixed_claude_reasoning_signatures': mixed_claude,
}
destination = arguments.output
destination.write_text(json.dumps(result, indent=2) + '\n')
identities = [{'sha256': record['sha256'], 'paths': record['paths']} for record in source['records']]
arguments.sources_output.write_text(json.dumps(identities, indent=2) + '\n')
print(destination, destination.stat().st_size)
print(json.dumps(mixed_claude, indent=2))

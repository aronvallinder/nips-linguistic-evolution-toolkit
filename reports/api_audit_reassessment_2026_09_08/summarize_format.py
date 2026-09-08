"""Recompute descriptive format-study summaries without running experiments."""

import argparse
import hashlib
import json
import re
import statistics
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--repo-root", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
arguments = parser.parse_args()
ROOT = arguments.repo_root.resolve()
REFERENCE = ROOT / 'data/shared_runs/uploaders/vallinder/data/json/noise_experiments/negative_only_crossmodel_defectors_n5_20260825/negative_only_crossmodel_population_myth_game_n5/claude-sonnet-4.5/myth_game/noisy8_crossmodel_negative_defectors25_twotask_r3'
FORMAT_ROOT = ROOT / 'data/json/noise_experiments/fmt_confound_20260904'
DECISION_KEY = re.compile(r'''['"](send|return)['"]\s*:\s*\$?\s*(-?\d+(?:\.\d+)?)''', re.I)
CELLS = {'reference': REFERENCE, 'json_only': FORMAT_ROOT / 'fmt_claude_defectors25_myth_game_json_only_n5', 'reasoning_then_json': FORMAT_ROOT / 'fmt_claude_defectors25_myth_game_reasoning_then_json_n5'}
all_rows = []
for cell, directory in CELLS.items():
    paths = sorted(path for path in directory.rglob('*.json') if not path.name.endswith(('.results.json', '.checkpoint.json', '.error.json')))
    for path in paths:
        data = json.loads(path.read_text())
        metadata = data['run_metadata']
        types = data.get('game_data', {}).get('agent_types') or {}
        ordinary = {name for name, agent in data['agents'].items() if types.get(name, agent.get('population_role', 'standard')) == 'standard'}
        sends = []
        returns = []
        reply_lengths = []
        game_errors = []
        correction_prompts = []
        first_myth = None
        first_later_myth = None
        for round_data in data['conversation_history']:
            for dyad in round_data.get('dyads', []):
                if dyad.get('investor') in ordinary and dyad.get('sent') is not None:
                    sends.append(float(dyad['sent']))
                if dyad.get('trustee') in ordinary and float(dyad.get('received') or 0) > 0 and dyad.get('returned') is not None:
                    returns.append(float(dyad['returned']) / float(dyad['received']))
        for name, agent in data['agents'].items():
            for interaction in agent.get('interaction_history', []):
                prompt = interaction.get('prompt', '')
                error = interaction.get('error')
                if error and error.get('type') == 'InvalidGameResponseError':
                    game_errors.append(error.get('message', ''))
                if 'Correction attempt' in prompt:
                    correction_prompts.append(prompt[-450:])
                interaction_metadata = interaction.get('metadata') or {}
                is_myth = interaction_metadata.get('task') == 'myth'
                if first_myth is None and is_myth and interaction_metadata.get('round') == 1:
                    first_myth = prompt
                if first_later_myth is None and is_myth and interaction_metadata.get('round', 0) > 1:
                    first_later_myth = prompt
                response = interaction.get('response') or {}
                if name not in ordinary or error or not isinstance(response, dict) or response.get('response_source') == 'scripted':
                    continue
                content = response.get('content') or ''
                if DECISION_KEY.search(content):
                    reply_lengths.append(len(content))
        if first_myth is None or first_later_myth is None:
            raise ValueError(f'Missing task-labelled myth prompt evidence in {path}')
        balances = [float(value) for name, value in data['game_data']['balances'].items() if name in ordinary]
        wanted = ('llm_provider', 'provider_model', 'llm_provider_mode', 'temperature', 'max_output_tokens', 'thinking_level', 'llm_settings_effective', 'decision_format', 'myth_default_prompt_key', 'myth_later_prompt_key', 'code_commit', 'code_dirty', 'replicate_id', 'pairing_seed', 'noise_seed', 'defector_seed', 'memory_capacity', 'chat_memory_mode', 'noise_config', 'noise_semantics', 'myth_injection_mode')
        row = {'cell': cell, 'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'metadata': {key: metadata.get(key, 'UNRECORDED') for key in wanted}, 'n_rounds': len(data['conversation_history']), 'n_ordinary': len(ordinary), 'n_decisions': len(reply_lengths), 'send_fraction': statistics.mean(sends) / 5, 'return_ratio': statistics.mean(returns), 'final_balance': statistics.mean(balances), 'reply_chars': statistics.mean(reply_lengths), 'n_game_rejections': len(game_errors), 'n_correction_prompts': len(correction_prompts), 'first_game_rejection': game_errors[0] if game_errors else None, 'first_correction': correction_prompts[0] if correction_prompts else None, 'first_myth_prompt': first_myth, 'later_myth_prompt_sha256': hashlib.sha256(first_later_myth.encode()).hexdigest() if first_later_myth is not None else None}
        all_rows.append(row)
    cell_rows = [row for row in all_rows if row['cell'] == cell]
    print(cell, 'n=', len(cell_rows))
    for metric in ('send_fraction', 'return_ratio', 'final_balance', 'reply_chars'):
        values = [row[metric] for row in cell_rows]
        print(metric, f'{statistics.mean(values):.6f} (±{statistics.stdev(values):.6f})')
    for row in cell_rows:
        print(json.dumps({key: row[key] for key in ('path', 'metadata', 'n_rounds', 'n_decisions', 'n_game_rejections', 'n_correction_prompts')}, sort_keys=True))
arguments.output.write_text(json.dumps(all_rows, indent=2) + '\n')

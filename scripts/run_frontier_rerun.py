"""Frozen frontier-model rerun (2026-09-18): dry-run by default, staged, resumable finals only.

Arms: Claude Opus 5 (adaptive thinking, effort high), Gemini 3.1 Pro Preview (thinking high),
GPT-5.6 Sol (effort high) and GPT-5.6 Sol (effort none). Each arm repeats the September
no-defector matrix (2 and 8 agents x game / game_myth / myth_game x 5 replicates).
Stages: smoke = replicate 0 of the 2-agent game cell, all arms (4 runs); pilot = replicate 0
of every cell for the three reasoning-on arms (18 runs); main = all 120 runs.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.run_noisy_missing import load_combinations, expected_output_path, check_existing_final, run_missing_job
from scripts.rerun_negative_only_crossmodel import TRUNCATION_REASONS
from scripts.build_frontier_rerun_config import ARMS, PROFILES, SHAPES, NEW_MODELS
from experiments.run_noisy_batch import build_noisy_protocol
from src.utils import is_exhausted_quota

CONFIG = ROOT / 'config/frontier_rerun_20260918.yaml'
SEPTEMBER = ROOT / 'config/experiments_noisy.yaml'
OUTPUT = 'frontier_rerun_20260918'
MODEL_SLUG = {'opus5': NEW_MODELS['claude_opus_5'], 'gemini31pro': 'google/gemini-3.1-pro-preview',
              'sol_high': NEW_MODELS['gpt56_sol'], 'sol_none': NEW_MODELS['gpt56_sol']}
EXPECTED_POLICIES = {arm: PROFILES[profile] for arm, (_, profile) in ARMS.items()}
RATES = {'anthropic': (5.0, 25.0), 'openai': (4.0, 20.0), 'google': (2.0, 12.0)}  # USD per MTok, verified 2026-09-18
# Mid-scenario per-run estimates (USD) from the September token profile; see
# docs/research/frontier_model_run_plan_2026-09-18.md section 5.
EST_PER_RUN = {
    'opus5': {'dyad_game': 0.47, 'dyad_game_myth': 1.75, 'dyad_myth_game': 1.71, 'population_game': 2.06, 'population_game_myth': 7.08, 'population_myth_game': 7.35},
    'gemini31pro': {'dyad_game': 0.12, 'dyad_game_myth': 0.50, 'dyad_myth_game': 0.50, 'population_game': 0.30, 'population_game_myth': 2.05, 'population_myth_game': 2.10},
    'sol_high': {'dyad_game': 0.72, 'dyad_game_myth': 5.78, 'dyad_myth_game': 5.83, 'population_game': 2.93, 'population_game_myth': 22.80, 'population_myth_game': 23.12},
    'sol_none': {'dyad_game': 0.05, 'dyad_game_myth': 0.45, 'dyad_myth_game': 0.47, 'population_game': 0.35, 'population_game_myth': 2.20, 'population_myth_game': 2.30},
}
STAGES = {
    'smoke': lambda shape, arm, rep: shape == 'dyad_game' and rep == 0,
    'pilot': lambda shape, arm, rep: rep == 0 and arm in ('opus5', 'gemini31pro', 'sol_high'),
    'main': lambda shape, arm, rep: True,
}
STAGE_SIZES = {'smoke': 4, 'pilot': 18, 'main': 120}


def _september_reference(shape, game_params_name):
    name = f'negative_only_reasoning_rerun_{shape}_claude_n5'
    with contextlib.redirect_stdout(io.StringIO()):
        old = load_combinations(name, str(SEPTEMBER))
    old = {c['replicate_id']: c for c in old if c['game_params_name'] == game_params_name}
    assert len(old) == 5, (name, game_params_name, len(old))
    return old


def plan():
    jobs = []
    references = {}
    for shape, (_, game_params_name) in SHAPES.items():
        references[shape] = _september_reference(shape, game_params_name)
        for arm in ARMS:
            name = f'frontier_{shape}_{arm}_n5'
            with contextlib.redirect_stdout(io.StringIO()):
                combos = load_combinations(name, str(CONFIG))
            assert len(combos) == 5, (name, len(combos))
            for i, c in enumerate(combos):
                base = references[shape][c['replicate_id']]
                assert c['model'] == MODEL_SLUG[arm], (name, c['model'])
                assert c['game_params_name'] == game_params_name
                actual, expected = c['comparison_inputs'], base['comparison_inputs']
                changed = {k for k in set(actual) | set(expected) if actual.get(k) != expected.get(k)}
                assert changed <= {'model', 'llm_request'}, (name, 'non-model input changed', sorted(changed))
                assert c['request_plan'].as_dict()['policy'] == EXPECTED_POLICIES[arm], (name, 'request profile drifted')
                assert c['game_params'].get('defector_ratio', 0) == 0
                assert c['game_params'].get('random_defection_probability', 0) == 0
                assert c['game_params']['noise_config']['inform_agents'] is True
                game, _ = build_noisy_protocol(c, i)
                assert len(game.defector_agent_ids) == 0 and game.random_defection_probability == 0
                assert not game.punishment_enabled
                jobs.append({'name': name, 'index': i, 'combo': c, 'path': expected_output_path(c, name, i, OUTPUT),
                             'arm': arm, 'shape': shape, 'replicate': c['replicate_id']})
    assert len(jobs) == 120 and len({str(j['path']) for j in jobs}) == 120
    # Longer two-task and 8-agent jobs first; interleave arms.
    jobs.sort(key=lambda j: (j['replicate'], 0 if 'myth' in j['shape'] else 1, 0 if 'population' in j['shape'] else 1, list(ARMS).index(j['arm'])))
    return jobs


def audit(job):
    c, path, arm = job['combo'], job['path'], job['arm']
    check_existing_final(path, c)
    d = json.loads(path.read_text()); m = d['run_metadata']
    assert m['defector_count'] == 0 and m['random_defection_probability'] == 0
    assert not m['code_dirty'], f'{path} was produced from a dirty checkout'
    assert m['llm_request'] == c['request_plan'].as_dict()
    assert m['llm_request']['policy'] == EXPECTED_POLICIES[arm]
    assert m['noise_config'] == c['game_params']['noise_config']
    provider = m['llm_request']['provider']; ir, orr = RATES[provider]
    calls = 0; cost = 0.0; inp = 0; out = 0; reas = 0
    for a in d['agents'].values():
        for e in a.get('interaction_history', []):
            r = e.get('response') or {}
            if r.get('response_source', 'llm') != 'llm':
                continue
            u = r.get('usage') or {}
            assert u.get('request_settings') == c['request_plan'].as_dict(), f'{path}: per-call request settings differ from the plan'
            assert u.get('outcome') == 'complete' and u.get('finish_reason') not in TRUNCATION_REASONS, f'{path}: truncated or incomplete call'
            calls += 1
            i_tok = u.get('input_tokens') or 0; o_tok = u.get('output_tokens') or 0; r_tok = u.get('reasoning_tokens') or 0
            billed_out = o_tok + (r_tok if provider == 'google' else 0)
            inp += i_tok; out += billed_out; reas += r_tok
            cost += (i_tok * ir + billed_out * orr) / 1e6
    assert calls > 0, f'{path}: no LLM calls recorded'
    return {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'arm': arm, 'shape': job['shape'],
            'replicate': job['replicate'], 'calls': calls, 'input_tokens': inp, 'billed_output_tokens': out, 'reasoning_tokens': reas,
            'provider_model': m['llm_request']['provider_model'], 'standard_rate_usd': cost}


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--stage', choices=sorted(STAGES), required=True)
    p.add_argument('--workers', type=int, default=4)
    p.add_argument('--execute', action='store_true')
    p.add_argument('--audit-only', action='store_true')
    args = p.parse_args()
    assert 1 <= args.workers <= 20
    selected = [j for j in plan() if STAGES[args.stage](j['shape'], j['arm'], j['replicate'])]
    assert len(selected) == STAGE_SIZES[args.stage], (args.stage, len(selected))
    pending = []; receipts = []
    for j in selected:
        if j['path'].exists():
            receipts.append(audit(j))
        else:
            pending.append(j)
    est = sum(EST_PER_RUN[j['arm']][j['shape']] for j in pending)
    arms = sorted({j['arm'] for j in pending})
    print(f'VALIDATED STAGE={args.stage} N={len(selected)} EXISTING={len(receipts)} PENDING={len(pending)} ARMS={arms}', flush=True)
    print(f'MODEL={",".join(sorted({MODEL_SLUG[a] for a in arms}))} N={len(pending)} WORKERS={args.workers} EST_COST=${est:.2f} (mid scenario, standard rates)', flush=True)
    if args.audit_only:
        assert not pending, f'{len(pending)} runs missing'
    elif not args.execute:
        print('DRY RUN: pass --execute to launch', flush=True)
    if args.execute and pending:
        assert not subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip(), 'Clean checkout required'
        os.environ['HF_DATASET_AUTO_UPLOAD'] = '0'; os.environ['TRUST_BATCH_QUIET'] = '1'
        logdir = str(ROOT / 'data/json/noise_experiments' / OUTPUT / 'worker_logs')
        workers = min(args.workers, len(pending))
        for attempt in range(1, 11):
            if not pending:
                break
            failed = []; quota_exhausted = False
            with ProcessPoolExecutor(max_workers=workers) as pool:
                futures = {pool.submit(run_missing_job, j['combo'], j['name'], j['index'], OUTPUT, logdir): j for j in pending}
                for f in as_completed(futures):
                    j = futures[f]
                    if f.cancelled():
                        failed.append(j); continue
                    try:
                        result = f.result()
                        if not result.get('success') and is_exhausted_quota(result.get('error', '')):
                            quota_exhausted = True
                            for queued in futures: queued.cancel()
                            print('BILLING EXHAUSTED: canceling queued jobs; no further retry passes', flush=True)
                        if not result.get('success'):
                            raise RuntimeError(f"Worker failed: {str(result.get('error',''))[:300]} (log {result.get('worker_log')})")
                        receipt = audit(j); receipts.append(receipt)
                        print(f"COMPLETE {len(receipts)}/{len(selected)} {j['name']} index={j['index']} calls={receipt['calls']} in={receipt['input_tokens']} out={receipt['billed_output_tokens']} cost=${receipt['standard_rate_usd']:.3f}", flush=True)
                    except Exception as e:
                        print(f"FAILED {j['name']} index={j['index']} {type(e).__name__}: {e}", flush=True)
                        if j['path'].exists():
                            raise  # never silently resample a final that fails validation
                        failed.append(j)
            if quota_exhausted:
                raise RuntimeError('Provider credits exhausted; top up before resuming. Completed finals preserved.')
            pending = failed
            if pending:
                if attempt == 10:
                    raise RuntimeError(f'{len(pending)} runs failed after ten attempts')
                workers = 1
                print(f'CONTINUATION PENDING={len(pending)} WORKERS=1 ATTEMPT={attempt + 1}', flush=True)
                time.sleep(min(60, 2 ** attempt))
    if receipts and (args.execute or args.audit_only):
        target = ROOT / 'data/json/noise_experiments' / OUTPUT / f'{args.stage}_receipt.json'
        target.parent.mkdir(parents=True, exist_ok=True)
        by_arm = {}
        for r in receipts:
            by_arm.setdefault(r['arm'], {'runs': 0, 'standard_rate_usd': 0.0})
            by_arm[r['arm']]['runs'] += 1; by_arm[r['arm']]['standard_rate_usd'] += r['standard_rate_usd']
        target.write_text(json.dumps({'stage': args.stage, 'runs': len(receipts), 'standard_rate_usd': sum(r['standard_rate_usd'] for r in receipts),
                                      'by_arm': by_arm, 'finals': receipts}, indent=2) + '\n')
        print(f'AUDIT PASSED {len(receipts)}/{len(selected)}; receipt={target}', flush=True)


if __name__ == '__main__':
    main()

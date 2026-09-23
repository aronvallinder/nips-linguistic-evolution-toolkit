"""Frozen frontier-model rerun (2026-09-18): dry-run by default, staged, resumable finals only.

Arms: Claude Opus 5 (adaptive thinking, effort high), Gemini 3.1 Pro Preview (thinking high),
GPT-5.6 Sol (effort high), GPT-5.6 Sol (effort none) and, added 2026-09-23, Claude Opus 5.5
(same request profile as Opus 5; run with --arms opus55 to compare it against the Opus 5 finals). Each arm repeats the September
no-defector matrix (2 and 8 agents x game / game_myth / myth_game x 5 replicates).
Stages: smoke = replicate 0 of the 2-agent game cell, all arms (4 runs); pilot_myth_game =
replicate 0 of the 2- and 8-agent myth->game cells for the three reasoning-on arms (6 runs);
pilot = replicate 0 of every cell for those arms (18 runs); main_reasoning_on = all 30 runs of
those three arms (90 runs, Sol-none skipped by decision of 2026-09-18); main = every run of every arm.
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
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.run_noisy_missing import load_combinations, expected_output_path, check_existing_final, run_missing_job
from scripts.rerun_negative_only_crossmodel import TRUNCATION_REASONS
from scripts.build_frontier_rerun_config import ARMS, PROFILES, SHAPES
from experiments.run_noisy_batch import build_noisy_protocol
from src.utils import is_exhausted_quota
import yaml

CONFIG = ROOT / 'config/frontier_rerun_20260918.yaml'
SEPTEMBER = ROOT / 'config/experiments_noisy.yaml'
OUTPUT = 'frontier_rerun_20260918'
_BASE_MODELS = yaml.safe_load(CONFIG.read_text())['base_models']
MODEL_SLUG = {arm: _BASE_MODELS[model_key] for arm, (model_key, _) in ARMS.items()}
REASONING_ON = tuple(arm for arm in ARMS if arm != 'sol_none')
EXPECTED_POLICIES = {arm: PROFILES[profile] for arm, (_, profile) in ARMS.items()}
RATES = {'anthropic': (5.0, 25.0), 'openai': (4.0, 20.0), 'google': (2.0, 12.0)}  # USD per MTok, verified 2026-09-18
MODEL_RATES = {'claude-opus-5-5': (4.0, 20.0)}  # overrides RATES by provider model; verified on the Anthropic pricing page 2026-09-23
# Per-run estimates (USD): measured in the 2026-09-18 pilot (pilot_receipt.json) for the three
# reasoning-on arms; Sol-none is the September-profile estimate (plan doc section 5).
EST_PER_RUN = {
    'opus5': {'dyad_game': 0.1, 'dyad_game_myth': 0.83, 'dyad_myth_game': 0.91, 'population_game': 0.64, 'population_game_myth': 3.82, 'population_myth_game': 4.01},
    'gemini31pro': {'dyad_game': 0.11, 'population_game': 0.45, 'dyad_game_myth': 0.93, 'dyad_myth_game': 1.1, 'population_game_myth': 3.04, 'population_myth_game': 3.37},
    'sol_high': {'dyad_game': 0.08, 'population_game': 0.46, 'dyad_myth_game': 0.78, 'dyad_game_myth': 0.83, 'population_myth_game': 3.43, 'population_game_myth': 3.47},
    # Opus 5.5: the Opus 5 per-run estimate at Opus 5.5's 20% lower token prices (not yet measured).
    'opus55': {'dyad_game': 0.08, 'dyad_game_myth': 0.66, 'dyad_myth_game': 0.73, 'population_game': 0.51, 'population_game_myth': 3.06, 'population_myth_game': 3.21},
    'sol_none': {'dyad_game': 0.04, 'dyad_game_myth': 0.43, 'dyad_myth_game': 0.45, 'population_game': 0.32, 'population_game_myth': 2.01, 'population_myth_game': 2.05},
}
STAGES = {
    'smoke': lambda shape, arm, rep: shape == 'dyad_game' and rep == 0,
    'pilot_myth_game': lambda shape, arm, rep: rep == 0 and shape in ('dyad_myth_game', 'population_myth_game') and arm in REASONING_ON,
    'pilot': lambda shape, arm, rep: rep == 0 and arm in REASONING_ON,
    'main_reasoning_on': lambda shape, arm, rep: arm in REASONING_ON,
    'main': lambda shape, arm, rep: True,
}


def require(condition, *message):
    """Validation that survives ``python -O`` (a bare assert would not)."""
    if not condition:
        raise RuntimeError(" ".join(str(part) for part in message))


def _september_reference(shape, game_params_name):
    name = f'negative_only_reasoning_rerun_{shape}_claude_n5'
    with contextlib.redirect_stdout(io.StringIO()):
        old = load_combinations(name, str(SEPTEMBER))
    old = {c['replicate_id']: c for c in old if c['game_params_name'] == game_params_name}
    require(len(old) == 5, (name, game_params_name, len(old)), 'len(old) == 5, (name, game_params_name, len(old))')
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
            require(len(combos) == 5, (name, len(combos)), 'len(combos) == 5, (name, len(combos))')
            for i, c in enumerate(combos):
                base = references[shape][c['replicate_id']]
                require(c['model'] == MODEL_SLUG[arm], (name, c['model']), "c['model'] == MODEL_SLUG[arm], (name, c['model'])")
                require(c['game_params_name'] == game_params_name, "c['game_params_name'] == game_params_name")
                actual, expected = c['comparison_inputs'], base['comparison_inputs']
                changed = {k for k in set(actual) | set(expected) if actual.get(k) != expected.get(k)}
                require(changed <= {'model', 'llm_request'}, (name, 'non-model input changed', sorted(changed)), "changed <= {'model', 'llm_request'}, (name, 'non-model input changed', sorted(changed))")
                require(c['request_plan'].as_dict()['policy'] == EXPECTED_POLICIES[arm], (name, 'request profile drifted'))
                require(c['game_params'].get('defector_ratio', 0) == 0, "c['game_params'].get('defector_ratio', 0) == 0")
                require(c['game_params'].get('random_defection_probability', 0) == 0, "c['game_params'].get('random_defection_probability', 0) == 0")
                require(c['game_params']['noise_config']['inform_agents'] is True, "c['game_params']['noise_config']['inform_agents'] is True")
                game, _ = build_noisy_protocol(c, i)
                require(len(game.defector_agent_ids) == 0 and game.random_defection_probability == 0, 'len(game.defector_agent_ids) == 0 and game.random_defection_probability == 0')
                require(not game.punishment_enabled, 'not game.punishment_enabled')
                jobs.append({'name': name, 'index': i, 'combo': c, 'path': expected_output_path(c, name, i, OUTPUT),
                             'arm': arm, 'shape': shape, 'replicate': c['replicate_id']})
    n = 30 * len(ARMS)
    require(len(jobs) == n and len({str(j['path']) for j in jobs}) == n, f'expected {n} unique jobs')
    # Longer two-task and 8-agent jobs first; interleave arms.
    jobs.sort(key=lambda j: (j['replicate'], 0 if 'myth' in j['shape'] else 1, 0 if 'population' in j['shape'] else 1, list(ARMS).index(j['arm'])))
    return jobs


def audit(job):
    c, path, arm = job['combo'], job['path'], job['arm']
    check_existing_final(path, c)
    d = json.loads(path.read_text()); m = d['run_metadata']
    require(m['defector_count'] == 0 and m['random_defection_probability'] == 0, "m['defector_count'] == 0 and m['random_defection_probability'] == 0")
    require(not m['code_dirty'], f'{path} was produced from a dirty checkout')
    require(m['llm_request'] == c['request_plan'].as_dict(), "m['llm_request'] == c['request_plan'].as_dict()")
    require(m['llm_request']['policy'] == EXPECTED_POLICIES[arm], "m['llm_request']['policy'] == EXPECTED_POLICIES[arm]")
    require(m['noise_config'] == c['game_params']['noise_config'], "m['noise_config'] == c['game_params']['noise_config']")
    provider = m['llm_request']['provider']; ir, orr = MODEL_RATES.get(m['llm_request']['provider_model'], RATES[provider])
    calls = 0; cost = 0.0; inp = 0; out = 0; reas = 0
    for a in d['agents'].values():
        for e in a.get('interaction_history', []):
            r = e.get('response') or {}
            if r.get('response_source', 'llm') != 'llm':
                continue
            u = r.get('usage') or {}
            require(u.get('request_settings') == c['request_plan'].as_dict(), f'{path}: per-call request settings differ from the plan')
            require(u.get('outcome') == 'complete' and u.get('finish_reason') not in TRUNCATION_REASONS, f'{path}: truncated or incomplete call')
            calls += 1
            i_tok = u.get('input_tokens') or 0; o_tok = u.get('output_tokens') or 0; r_tok = u.get('reasoning_tokens') or 0
            billed_out = o_tok + (r_tok if provider == 'google' else 0)
            inp += i_tok; out += billed_out; reas += r_tok
            cost += (i_tok * ir + billed_out * orr) / 1e6
    require(calls > 0, f'{path}: no LLM calls recorded')
    return {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'arm': arm, 'shape': job['shape'],
            'replicate': job['replicate'], 'calls': calls, 'input_tokens': inp, 'billed_output_tokens': out, 'reasoning_tokens': reas,
            'provider_model': m['llm_request']['provider_model'], 'standard_rate_usd': cost}


def quarantine(job, reason):
    """Move an invalid final (and its sidecars) out of the way so the relaunch resamples it."""
    path = job['path']
    target = ROOT / 'data/json/noise_experiments' / OUTPUT / 'quarantine' / f"{path.stem}_{time.strftime('%Y%m%dT%H%M%S')}"
    target.mkdir(parents=True, exist_ok=True)
    stem = path.name[:-len('.json')]
    for sidecar in path.parent.glob(stem + '*'):
        shutil.move(str(sidecar), str(target / sidecar.name))
    (target / 'reason.json').write_text(json.dumps({
        'quarantined': time.strftime('%Y-%m-%d %H:%M:%S'), 'run': f"{job['name']} index {job['index']} (replicate {job['replicate']})",
        'reason': reason, 'policy': 'the audit rejects any final containing a non-complete LLM call or drifted settings; resampled under the same replicate seed by the next launch',
    }, indent=2) + '\n')
    return target


def main():
    os.chdir(ROOT)  # workers write finals relative to the cwd; the audit reads ROOT-relative paths
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--stage', choices=sorted(STAGES), required=True)
    p.add_argument('--workers', type=int, default=4)
    p.add_argument('--arms', default=None, help='comma-separated subset of arms to run, e.g. opus5 (default: all arms of the stage)')
    p.add_argument('--execute', action='store_true')
    p.add_argument('--audit-only', action='store_true')
    args = p.parse_args()
    require(1 <= args.workers <= 20, '1 <= args.workers <= 20')
    selected = [j for j in plan() if STAGES[args.stage](j['shape'], j['arm'], j['replicate'])]
    if args.arms:
        arms = set(args.arms.split(','))
        require(arms <= set(ARMS), f'unknown arm in {sorted(arms)}')
        selected = [j for j in selected if j['arm'] in arms]
    require(selected, f'stage {args.stage} selects no runs')
    pending = []; receipts = []; invalid = []
    for j in selected:
        if not j['path'].exists():
            pending.append(j); continue
        try:
            receipts.append(audit(j))
        except (AssertionError, RuntimeError) as e:
            invalid.append((j, str(e)))
    for j, reason in invalid:
        target = quarantine(j, reason)
        print(f"QUARANTINED {j['name']} index={j['index']}: {reason.split(': ')[-1]} -> {target.relative_to(ROOT)}", flush=True)
        pending.append(j)
    est = sum(EST_PER_RUN[j['arm']][j['shape']] for j in pending)
    arms = sorted({j['arm'] for j in pending})
    print(f'VALIDATED STAGE={args.stage} N={len(selected)} EXISTING={len(receipts)} PENDING={len(pending)} ARMS={arms}', flush=True)
    print(f'MODEL={",".join(sorted({MODEL_SLUG[a] for a in arms}))} N={len(pending)} WORKERS={args.workers} EST_COST=${est:.2f} (mid scenario, standard rates)', flush=True)
    if args.audit_only:
        require(not pending, f'{len(pending)} runs missing')
    elif not args.execute:
        print('DRY RUN: pass --execute to launch', flush=True)
    if args.execute and pending:
        require(not subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip(), 'Clean checkout required')
        os.environ['HF_DATASET_AUTO_UPLOAD'] = '0'; os.environ['TRUST_BATCH_QUIET'] = '1'
        logdir = str(ROOT / 'data/json/noise_experiments' / OUTPUT / 'worker_logs')
        workers = min(args.workers, len(pending))
        for attempt in range(1, 11):
            if not pending:
                break
            failed = []; quota_exhausted = False; invalid_final = None
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
                            # Never silently resample a final that fails validation: stop submitting,
                            # let running jobs finish and be audited, then abort after the pool exits.
                            invalid_final = (j, e)
                            for queued in futures: queued.cancel()
                            continue
                        failed.append(j)
            if invalid_final is not None:
                j, e = invalid_final
                raise RuntimeError(f"Final failed validation and was left in place for inspection: {j['path']} ({e}). "
                                   "Relaunching quarantines it automatically and resamples the run.")
            if quota_exhausted:
                raise RuntimeError('Provider credits exhausted; top up before resuming. Completed finals preserved.')
            pending = failed
            if pending:
                if attempt == 10:
                    raise RuntimeError(f'{len(pending)} runs failed after ten attempts')
                workers = max(1, min(workers, len(pending)) // 2)
                print(f'CONTINUATION PENDING={len(pending)} WORKERS={workers} ATTEMPT={attempt + 1}', flush=True)
                time.sleep(min(60, 2 ** attempt))
    if receipts and (args.execute or args.audit_only):
        suffix = f"_{args.arms.replace(',', '+')}" if args.arms else ''
        target = ROOT / 'data/json/noise_experiments' / OUTPUT / f'{args.stage}{suffix}_receipt.json'
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

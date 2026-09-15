"""Frozen 180-run no-defector extension; dry-run by default, resumable finals only."""
from __future__ import annotations
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import contextlib
import copy
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
from scripts.rerun_negative_only_crossmodel import EXPECTED_POLICIES, TRUNCATION_REASONS
from experiments.run_noisy_batch import build_noisy_protocol
CONFIG = ROOT / 'config/figure2_no_defectors_20260915.yaml'
OUTPUT = 'figure2_no_defectors_20260915'
SHAPES = ('dyad_game', 'dyad_game_myth', 'dyad_myth_game', 'population_game', 'population_game_myth', 'population_myth_game')
PROVIDERS = ('claude', 'gpt', 'gemini')

def plan():
    jobs = []
    for shape in SHAPES:
        for provider in PROVIDERS:
            name = f'figure2_{shape}_{provider}_n5'
            with contextlib.redirect_stdout(io.StringIO()):
                combos = load_combinations(name, str(CONFIG))
                old = load_combinations(f'negative_only_reasoning_rerun_{shape}_{provider}_n5', str(ROOT/'config/experiments_noisy.yaml'))
            assert len(combos) == 10
            old = {c['replicate_id']: c for c in old if c['game_params_name'].endswith(('negative_game_r3','negative_twotask_r3'))}
            assert len(old) == 5
            for i,c in enumerate(combos):
                base = old[c['replicate_id']]
                actual = copy.deepcopy(c['comparison_inputs'])
                noise = actual['game_params']['noise_config']
                expected_noise = None if c['game_params_name'].endswith('_no_noise') else {**base['game_params']['noise_config'], 'inform_agents':False}
                assert noise == expected_noise
                actual['game_params']['noise_config'] = base['comparison_inputs']['game_params']['noise_config']
                assert actual == base['comparison_inputs'], (name, 'non-noise input changed')
                assert c['request_plan'].as_dict()['policy'] == EXPECTED_POLICIES[c['model']]
                assert c['game_params'].get('defector_ratio',0) == 0
                assert c['game_params'].get('random_defection_probability',0) == 0
                game, _ = build_noisy_protocol(c,i)
                assert len(game.defector_agent_ids)==0 and game.random_defection_probability==0
                assert not game.punishment_enabled
                jobs.append((name,i,c,expected_output_path(c,name,i,OUTPUT)))
    assert len(jobs)==180 and len({str(j[3]) for j in jobs})==180
    # Interleave providers and population sizes, with longer two-task jobs first.
    jobs.sort(key=lambda j:(j[1], 0 if 'myth' in j[2]['task_order'] else 1, j[2]['game_params']['num_agents'], PROVIDERS.index(j[0].split('_')[-2])))
    return jobs

def audit(job):
    name,i,c,path=job
    check_existing_final(path,c)
    d=json.loads(path.read_text());m=d['run_metadata']
    assert m['defector_count']==0 and m['random_defection_probability']==0
    assert not m['code_dirty']
    assert m['llm_request']==c['request_plan'].as_dict()
    assert m['noise_config']==c['game_params']['noise_config'] or (not m['noise_config'] and not c['game_params']['noise_config'])
    calls=0;cost=0.0
    rates={'anthropic':(3,15),'openai':(.05,.4),'google':(.75,3.75)}
    provider=m['llm_request']['provider']; ir,orr=rates[provider]
    for a in d['agents'].values():
        for e in a.get('interaction_history',[]):
            r=e.get('response') or {}
            if r.get('response_source','llm')!='llm': continue
            u=r.get('usage') or {}
            assert u.get('request_settings')==c['request_plan'].as_dict()
            assert u.get('outcome')=='complete' and u.get('finish_reason') not in TRUNCATION_REASONS
            calls+=1
            output=(u.get('output_tokens') or 0)+((u.get('reasoning_tokens') or 0) if provider=='google' else 0)
            cost+=((u.get('input_tokens') or 0)*ir+output*orr)/1e6
    return {'path':str(path.relative_to(ROOT)), 'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'calls':calls,'standard_rate_usd':cost}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--workers',type=int,default=20);p.add_argument('--execute',action='store_true');p.add_argument('--audit-only',action='store_true');args=p.parse_args()
    assert 1<=args.workers<=20
    jobs=plan();pending=[];receipts=[]
    for j in jobs:
        if j[3].exists(): receipts.append(audit(j))
        else:pending.append(j)
    print(f'VALIDATED N=180 NO_DEFECTORS=180 NO_NOISE=90 UNINFORMED=90 EXISTING={len(receipts)} PENDING={len(pending)}',flush=True)
    if args.audit_only:
        assert not pending
    elif not args.execute: return
    if args.execute:
        assert not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True).strip(), 'Clean checkout required'
        print(f'PREFLIGHT: MODEL=claude-sonnet-4.5(thinking8192),gpt-5-nano(high),gemini-3.7-flash(high) N={len(pending)} WORKERS={args.workers} EST_COST=$160 CMD=python scripts/run_figure2_extension.py --workers {args.workers} --execute',flush=True)
        os.environ['HF_DATASET_AUTO_UPLOAD']='0';os.environ['TRUST_BATCH_QUIET']='1'
        logdir=str(ROOT/'data/json/noise_experiments'/OUTPUT/'worker_logs')
        workers=args.workers
        for attempt in range(1,11):
            if not pending:break
            failed=[]
            with ProcessPoolExecutor(max_workers=workers) as pool:
                futures={pool.submit(run_missing_job,j[2],j[0],j[1],OUTPUT,logdir):j for j in pending}
                for f in as_completed(futures):
                    j=futures[f]
                    try:
                        result=f.result()
                        if not result.get('success'): raise RuntimeError(f"Worker failed; inspect {result.get('worker_log')}")
                        receipt=audit(j);receipts.append(receipt)
                        print(f'COMPLETE {len(receipts)}/180 {j[0]} index={j[1]} cost=${receipt["standard_rate_usd"]:.3f}',flush=True)
                    except Exception as e:
                        print(f'FAILED {j[0]} index={j[1]} {type(e).__name__}: {e}',flush=True)
                        # Never silently resample a final that fails scientific validation.
                        if j[3].exists():raise
                        failed.append(j)
            pending=failed
            if pending:
                if attempt==10:raise RuntimeError(f'{len(pending)} runs failed after ten attempts')
                workers=1
                print(f'CONTINUATION PENDING={len(pending)} WORKERS=1 ATTEMPT={attempt+1}',flush=True)
                time.sleep(min(60,2**attempt))
    target=ROOT/'data/json/noise_experiments'/OUTPUT/'completion_receipt.json'
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps({'runs':len(receipts),'standard_rate_usd':sum(r['standard_rate_usd'] for r in receipts),'finals':receipts},indent=2)+'\n')
    print(f'AUDIT PASSED {len(receipts)}/180; receipt={target}',flush=True)
if __name__=='__main__':main()

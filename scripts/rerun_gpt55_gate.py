#!/usr/bin/env python3
"""Rerun all twelve frozen GPT-5.5 gate cells; dry-run unless --execute is set."""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
import os
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from experiments.run_noisy_batch import execution_provenance
from scripts.analyze_gpt55_negative_only_gate import audit_gate
from scripts.gpt55_gate_contract import CONFIG, HISTORICAL, load_gate, planned_condition, verify_rerun
from scripts.run_noisy_missing import expected_output_path, run_missing_job
from src.experiment_condition import read_final_run


def run_gate(output_subdir, workers=3, execute=False, resume=False):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', output_subdir):
        raise ValueError('Output subdir must be a single folder name')
    if not 1 <= workers <= 12:
        raise ValueError('workers must be between 1 and 12')
    jobs = load_gate()
    provenance = execution_provenance(str(CONFIG))
    output = ROOT / 'data/json/noise_experiments' / output_subdir
    if output.exists() and not resume:
        raise ValueError('Output already exists; choose a fresh folder or use --resume')
    pending = []
    for name, combo in jobs.items():
        replicate = combo['replicate_id']
        combo['execution_provenance'] = {**provenance, 'historical_reference': HISTORICAL[replicate]}
        stage_subdir = f'{output_subdir}/r{replicate + 1}'
        final = expected_output_path(combo, name, 0, stage_subdir)
        if final.exists():
            saved = read_final_run(final)
            condition = verify_rerun(saved, name)
            if saved['run_metadata'].get('code_dirty') is not False or condition['implementation'] != planned_condition(combo, name)['implementation']:
                raise ValueError(f'{name}: existing final uses a different or dirty implementation')
        else:
            pending.append((combo, name, 0, stage_subdir, str(output / 'logs')))
    print(f'MODEL={next(iter(jobs.values()))["model"]} N={len(jobs)} PENDING={len(pending)} WORKERS={workers}')
    print(f'OUTPUT={output}')
    if not execute:
        print('DRY RUN: frozen conditions verified; no API calls or output writes')
        return None
    if provenance.get('code_dirty') is not False:
        raise ValueError('Commit the reviewed changes before running: worktree is dirty')
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
    if not os.environ.get('OPENAI_API_KEY'):
        raise ValueError('OPENAI_API_KEY is not set')
    print(f'PREFLIGHT: MODEL=openai/gpt-5.5-2026-04-23 N={len(pending)} WORKERS={workers} '
          f'EST_COST=${30 * len(pending) / 12:.2f} (twice historical token volume; not a spend cap)', flush=True)
    # Only this explicit execution path creates workers. No automatic uploads.
    os.chdir(ROOT)
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(run_missing_job, *job): job[1] for job in pending}
        for future in as_completed(futures):
            result = future.result()
            path = result.get('file_path')
            # A PDF/backup failure cannot invalidate a valid scientific final.
            if path and Path(path).is_file():
                verify_rerun(read_final_run(path), futures[future])
            else:
                raise RuntimeError(f'{futures[future]} failed; inspect logs under {output / "logs"} and use --resume')
            print(f'Completed {futures[future]}', flush=True)
    summaries = [audit_gate(output / f'r{r+1}', output / 'reports' / f'r{r+1}', r) for r in (0, 1)]
    if not all(s['completion_passed'] for s in summaries):
        raise RuntimeError('Runs saved, but completion audit failed; inspect the reports')
    return summaries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-subdir', default='gpt55_rerun_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
    parser.add_argument('--workers', type=int, default=3)
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args()
    run_gate(args.output_subdir, args.workers, args.execute, args.resume)


if __name__ == '__main__':
    main()

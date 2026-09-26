"""Opus 5.5 vs Opus 5 on the frontier matrix: final resources per agent after round 10.

Same metric as scripts/analyze_frontier_rerun.py. Reads the launcher receipts (audited
finals only) for the opus5 and opus55 arms and prints, per cell, Opus 5 over all five
runs, Opus 5 over the replicates Opus 5.5 has, Opus 5.5, per-run means and cost.
Run from the repo root: python scripts/compare_opus55_opus5.py
"""
import hashlib, json, glob, numpy as np
MAIN = 'data/json/noise_experiments/frontier_rerun_20260918'
WTROOT = '.'
def finals(root, arm):
    out = {}
    for f in glob.glob(f'{root}/{MAIN}/*receipt*.json'):
        for r in json.load(open(f))['finals']:
            if r['arm'] == arm: out[r['path']] = r
    return out
def res(root, p, sha256):
    raw = open(f'{root}/{p}', 'rb').read()
    assert hashlib.sha256(raw).hexdigest() == sha256, f'{p}: final no longer matches its receipt'
    h = json.loads(raw)['conversation_history']
    assert len(h) == 10, p
    return list(h[-1]['balances'].values())
cells = {}
for label, root, arm in [('opus5', '.', 'opus5'), ('opus55', WTROOT, 'opus55')]:
    for p, r in finals(root, arm).items():
        cells.setdefault(r['shape'], {}).setdefault(label, {})[r['replicate']] = (res(root, p, r['sha256']), r['standard_rate_usd'])
f = lambda v: f"{np.mean(v):.1f} (±{np.std(v, ddof=1) if len(v) > 1 else 0:.1f})"
runmeans = lambda reps, keep: [np.mean(reps[r][0]) for r in sorted(reps) if r in keep]
print(f"{'cell':22} {'Opus 5, 5 runs':16} {'Opus 5, runs 0-2':18} {'Opus 5.5, runs 0-2':20} {'per-run means 5 | 5.5':34} cost 5 / 5.5 (runs 0-2)")
for shape in sorted(cells):
    a, b = cells[shape].get('opus5', {}), cells[shape].get('opus55', {})
    keep = sorted(b)
    pool = lambda reps, ks: [x for r in ks for x in reps[r][0]]
    ra = ' '.join(f"{x:.0f}" for x in runmeans(a, keep)); rb = ' '.join(f"{x:.0f}" for x in runmeans(b, keep))
    ca = sum(a[r][1] for r in keep); cb = sum(b[r][1] for r in keep)
    print(f"{shape:22} {f(pool(a, sorted(a))):16} {f(pool(a, keep)):18} {f(pool(b, keep)):20} {ra + ' | ' + rb:34} ${ca:.2f} / ${cb:.2f}  (n={len(keep)})")

from pathlib import Path
import csv,json,hashlib,statistics,math,itertools
root=Path.cwd(); folder=root/'docs/figures/negative_only_crossmodel_reasoning_rerun_20260909_resources_boxplots'; rows=list(csv.DictReader((folder/'run_values.csv').open())); prov=json.load((folder/'provenance.json').open()); expected={str((root/x['path']).resolve()):x['sha256'] for x in prov['runs']}; group={}; mismatches=[]; seeds={}; loaded={}
for r in rows:
 p=Path(r['source_path']); p=p if p.exists() else root/str(p).split('nips-linguistic-evolution-toolkit/')[-1]
 if str(p) not in loaded:
  b=p.read_bytes();d=json.loads(b);loaded[str(p)]=d
  assert hashlib.sha256(b).hexdigest()==expected[str(p)]
 d=loaded[str(p)];m=d['run_metadata']; hist=d['conversation_history']; assert hist[-1]['round']==m['num_turns']==10
 balances=hist[-1]['balances']; exclude=m.get('defector_agent_ids',[]) if r['agents']=='ordinary' else []; val=statistics.mean(v for a,v in balances.items() if a not in exclude)
 if abs(val-float(r['final_cumulative_resources']))>1e-8:mismatches.append((str(p),val,r['final_cumulative_resources']))
 if r['agents']=='ordinary':
  k=(r['model'],r['defection']);rep=m['replicate_id'];group.setdefault(k,{}).setdefault(r['task_order'],{})[rep]=val
  seed=tuple(json.dumps(m.get(x),sort_keys=True) for x in ['pairing_seed','noise_seed','defector_seed','defector_agent_ids']);seeds.setdefault((k,rep),set()).add(seed)
print('verified',len(loaded),'unique finals;',len(rows),'values;',len(mismatches),'mismatches; seed discordance',sum(len(v)>1 for v in seeds.values()))
if mismatches or any(len(v)>1 for v in seeds.values()):
 raise RuntimeError('Source values or paired seeds disagree; refusing to overwrite result tables')
lines=['| Model | Defectors | Game only | Game → Myth | Myth → Game | Paired Myth → Game minus Game (95% t CI) |','|---|---|---|---|---|---|']; records=[]
for k,g in sorted(group.items()):
 vals=[list(g[x].values()) for x in ['game','game_myth','myth_game']];diff=[g['myth_game'][i]-g['game'][i] for i in sorted(g['game'])];mu=statistics.mean(diff);sd=statistics.stdev(diff); margin=2.776445105*sd/math.sqrt(5)
 lines.append('| '+' | '.join([*k,*[f'{statistics.mean(v):.2f} (±{statistics.stdev(v):.2f})' for v in vals],f'{mu:+.2f} (±{sd:.2f}); [{mu-margin:+.2f}, {mu+margin:+.2f}]'])+' |')
 records.append({'model':k[0],'defection':k[1],'difference_mean':mu,'difference_sd':sd,'ci95_low':mu-margin,'ci95_high':mu+margin})
(root/'docs/research/mixed_future_latest_table.md').write_text('\n'.join(lines)+'\n')
with (root/'docs/research/mixed_future_latest_differences.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=records[0]);w.writeheader();w.writerows(records)
print('\n'.join(lines))

from pathlib import Path
from collections import Counter,defaultdict
import json,csv,hashlib
root=Path.cwd(); out=root/'docs/research'; rows=[]; hashes={}; count=Counter()
for p in root.rglob('*.json'):
 if any(x in p.parts for x in ('.git','.venv','node_modules')):continue
 rel=str(p.relative_to(root)); b=p.read_bytes(); h=hashlib.sha256(b).hexdigest(); name=p.name
 family=rel.split('/'); family='/'.join(family[:4] if rel.startswith('data/shared_runs/uploaders') else family[:4] if rel.startswith('data/json/noise_experiments') else family[:3])
 kind='other_json'; meta={}; finalround=''; rounds=''
 try:
  d=json.loads(b)
  if isinstance(d,dict) and {'agents','conversation_history','game_data','task_order'}.issubset(d):
   meta=d.get('run_metadata') or {}; hist=d.get('conversation_history') or []; rounds=len(hist); finalround=max((r.get('round',0) for r in hist if isinstance(r,dict)),default=0)
   if any(x in name.lower() for x in ('checkpoint','error','partial')):kind='snapshot_not_final'
   elif meta.get('num_turns') is not None and finalround < meta['num_turns']:kind='underlength_fullstate'
   else:kind='final_fullstate_candidate'
 except Exception:kind='unreadable_json'
 row={'path':rel,'family':family,'kind':kind,'sha256':h,'duplicate_of':hashes.get(h,''),'bytes':len(b),'model':meta.get('model',''),'expected_rounds':meta.get('num_turns',''),'final_round':finalround,'history_entries':rounds,'code_commit':meta.get('code_commit',''),'code_dirty':meta.get('code_dirty',''),'replicate_id':meta.get('replicate_id','')}; rows.append(row); hashes.setdefault(h,rel)
with (out/'mixed_future_inventory.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
groups=defaultdict(Counter)
for r in rows:groups[r['family']][r['kind']]+=1;groups[r['family']]['exact_duplicate_paths']+=bool(r['duplicate_of'])
with (out/'mixed_future_inventory_summary.json').open('w') as f:json.dump({'total':len(rows),'kinds':dict(Counter(r['kind'] for r in rows)),'unique_final_bytes':len({r['sha256'] for r in rows if r['kind']=='final_fullstate_candidate'}),'families':groups},f,indent=2)
print('DONE',len(rows),Counter(r['kind'] for r in rows),len({r['sha256'] for r in rows if r['kind']=='final_fullstate_candidate'}))

#!/usr/bin/env python3
"""Self-contained HTML inspector for manual sanity-checking of myth/game runs.

Per run: a real matplotlib trajectory plot (transactions, balances, ratios,
noise), per-round numbers (actual vs noise-communicated), and a transcript with
three view modes: (1) game + myth outputs, (2) + the input prompt each round,
(3) the full model context (system + messages actually sent to the model).
Model name shown at the top. Output: data/plots/inspector/inspector.html

Usage: python scripts/build_data_inspector.py
"""
import json, re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(".")
CONF = "data/share/corrected_informed_noise_confirmatory_60runs_2026-08-12/data"
WASH = "data/json/noise_experiments/washout_20round"
OUT = ROOT / "data/plots/inspector"
PLOTDIR = OUT / "run_plots"

GROUPS = {
    "confirmatory 2-agent · game":       f"{CONF}/noise2i_memprimary_v2_game",
    "confirmatory 2-agent · game→myth":  f"{CONF}/noise2i_memprimary_v2_game_myth",
    "confirmatory 2-agent · myth→game":  f"{CONF}/noise2i_memprimary_v2_myth_game",
    "confirmatory 8-agent · game":       f"{CONF}/noise8i_memprimary_v2_game",
    "confirmatory 8-agent · game→myth":  f"{CONF}/noise8i_memprimary_v2_game_myth",
    "confirmatory 8-agent · myth→game":  f"{CONF}/noise8i_memprimary_v2_myth_game",
    "washout 20r 2-agent · myth→game":   f"{WASH}/noise2i_washout_myth_game",
    "washout 20r 2-agent · game→myth":   f"{WASH}/noise2i_washout_game_myth",
    "washout 20r 8-agent · myth→game":   f"{WASH}/noise8i_washout_myth_game",
    "washout 20r 8-agent · game→myth":   f"{WASH}/noise8i_washout_game_myth",
}
AGG_PLOTS = [
    ("Send + return trajectories (10r)", "data/plots/myth_taskorder_trajectories/send_and_return_trajectories.png"),
    ("Wash-out (20r)", "data/plots/myth_taskorder_trajectories/washout_20round.png"),
    ("Wash-out 8-agent (20r)", "data/plots/myth_taskorder_trajectories/washout_20round_8-agent.png"),
    ("Joint balance 2v8 (corrected informed noise)", "data/plots/joint_balance_2v8_corrected/joint_balance_2v8_corrected.png"),
]
MAX = 2200  # cap per text block


def clip(s):
    s = str(s or "")
    return s if len(s) <= MAX else s[:MAX] + " …[truncated]"


def ctxclip(s):  # tighter cap for full-context messages (many per run)
    s = str(s or "")
    return s if len(s) <= 1400 else s[:1400] + " …[truncated]"


def dyad_means(e):
    ds = [d for d in (e.get("dyads") or []) if isinstance(d, dict)]
    def m(k):
        v = [d.get(k) for d in ds if d.get(k) is not None]
        return sum(v)/len(v) if v else None
    return m


def render_plot(run, fp):
    ch = run["ch"]
    rounds = [e.get("round") for e in ch]
    sent, sentc, recv, ret, retc = [], [], [], [], []
    for e in ch:
        m = dyad_means(e)
        sent.append(m("sent")); sentc.append(m("sent_communicated"))
        recv.append(m("received")); ret.append(m("returned")); retc.append(m("returned_communicated"))
    agents = list((ch[-1].get("balances") or {}).keys())
    bal = {a: [] for a in agents}
    for e in ch:
        b = e.get("balances") or {}
        for a in agents: bal[a].append(b.get(a))
    endow = float(run["meta"].get("endowment", 5) or 5)
    def safe(a, b): return [ (x/y if (x is not None and y) else None) for x, y in zip(a, b)]
    sendfrac = safe(sent, [endow] * len(sent))
    retratio = safe(ret, recv)
    noise_s = [ (abs(a-b) if a is not None and b is not None else None) for a, b in zip(sentc, sent)]
    noise_r = [ (abs(a-b) if a is not None and b is not None else None) for a, b in zip(retc, ret)]

    fig, ax = plt.subplots(2, 2, figsize=(13, 8))
    fig.suptitle(run["id"], fontsize=11, fontweight="bold")
    a1 = ax[0, 0]
    a1.plot(rounds, sent, "-o", color="#4C72B0", label="sent", ms=3)
    a1.plot(rounds, sentc, "--", color="#9db9dd", label="sent (noisy)")
    a1.plot(rounds, recv, "-o", color="#55A868", label="received", ms=3)
    a1.plot(rounds, ret, "-o", color="#DD8452", label="returned", ms=3)
    a1.plot(rounds, retc, "--", color="#e6b89c", label="returned (noisy)")
    a1.set_title("Transactions"); a1.set_xlabel("round"); a1.set_ylabel("$"); a1.legend(fontsize=7); a1.grid(alpha=.3)
    a2 = ax[0, 1]
    for a in agents: a2.plot(rounds, bal[a], "-o", ms=2, label=a)
    a2.set_title("Cumulative balance per agent"); a2.set_xlabel("round"); a2.set_ylabel("$")
    if len(agents) <= 4: a2.legend(fontsize=7)
    a2.grid(alpha=.3)
    a3 = ax[1, 0]
    a3.plot(rounds, sendfrac, "-o", color="#4C72B0", ms=3,
            label=f"send fraction (of ${endow:g})")
    a3.plot(rounds, retratio, "-o", color="#DD8452", ms=3, label="return ratio")
    a3.axhline(0.5, color="grey", ls=":", alpha=.6); a3.set_ylim(0, 1.05)
    a3.set_title("Cooperation ratios"); a3.set_xlabel("round"); a3.legend(fontsize=7); a3.grid(alpha=.3)
    a4 = ax[1, 1]
    a4.plot(rounds, noise_s, "-o", color="#c44e52", ms=3, label="|noise| on sent")
    a4.plot(rounds, noise_r, "-o", color="#8172b3", ms=3, label="|noise| on returned")
    a4.set_title("Noise magnitude (communicated − actual)"); a4.set_xlabel("round"); a4.legend(fontsize=7); a4.grid(alpha=.3)
    plt.tight_layout()
    fig.savefig(fp, dpi=90, bbox_inches="tight")
    plt.close(fig)


def load_run(p, group):
    r = json.load(open(p))
    meta = r.get("run_metadata", {})
    ch = r.get("conversation_history", [])
    rounds = []
    for e in ch:
        dyads = [{"inv": d.get("investor"), "tru": d.get("trustee"), "sent": d.get("sent"),
                  "sent_c": d.get("sent_communicated"), "recv": d.get("received"),
                  "ret": d.get("returned"), "ret_c": d.get("returned_communicated")}
                 for d in (e.get("dyads") or [])]
        reasoning = {a: clip((v or {}).get("content", "") if isinstance(v, dict) else v)
                     for a, v in (e.get("game_responses") or {}).items()}
        myths = {a: clip(m if isinstance(m, str) else (m.get("myth", "") if isinstance(m, dict) else ""))
                 for a, m in (e.get("myths") or {}).items()}
        rounds.append({"round": e.get("round"), "dyads": dyads,
                       "balances": {k: round(v, 1) for k, v in (e.get("balances") or {}).items()},
                       "reasoning": reasoning, "myths": myths})
    # Per-call records from interaction_history: the exact prompt and the full
    # context (messages_sent) actually sent to the model on each call — untruncated.
    prompts = []      # {round, task, role, agent, prompt}
    final_ctx = {}    # agent -> {meta, messages:[{role,content}]}  (its last call's full payload)
    for a, obj in (r.get("agents") or {}).items():
        if not isinstance(obj, dict): continue
        hist = obj.get("interaction_history", []) or []
        for it in hist:
            md = it.get("metadata", {})
            prompts.append({"round": md.get("round"), "task": md.get("task"),
                            "role": md.get("role_label") or md.get("role"), "agent": a,
                            "prompt": clip(it.get("prompt", ""))})
        # Show the LAST call of EACH task type (game and myth), so both orders
        # display a game-context and a myth-context (avoids the "looks reversed"
        # confusion of only showing the trailing task's call).
        by_task = {}
        for it in hist:
            t = (it.get("metadata") or {}).get("task")
            if t: by_task[t] = it   # ends on the last interaction of each task
        final_ctx[a] = []
        for t in ["game", "myth"]:
            if t in by_task:
                it = by_task[t]; md = it.get("metadata") or {}
                final_ctx[a].append({
                    "task": t, "round": md.get("round"), "role": md.get("role_label"),
                    "messages": [{"role": m.get("role"), "content": ctxclip(m.get("content"))}
                                 for m in (it.get("messages_sent") or [])],
                })
    rid = p.stem
    return {"id": rid, "group": group, "task_order": r.get("task_order"),
            "n_agents": meta.get("num_agents"), "rounds": rounds,
            "prompts": prompts, "final_ctx": final_ctx,
            "meta": {"endowment": 5}, "ch": ch,
            "model": meta.get("provider_model") or meta.get("model"),
            "plot": f"run_plots/{group_slug(group)}__{rid}.png"}


def group_slug(g):
    return re.sub(r"[^a-z0-9]+", "_", g.lower()).strip("_")


def main():
    import shutil
    OUT.mkdir(parents=True, exist_ok=True)
    PLOTDIR.mkdir(parents=True, exist_ok=True)
    RUNDIR = OUT / "runs"
    AGGDIR = OUT / "agg_plots"
    shutil.rmtree(RUNDIR, ignore_errors=True); RUNDIR.mkdir()
    shutil.rmtree(AGGDIR, ignore_errors=True); AGGDIR.mkdir()
    index, model = {}, None
    for label, d in GROUPS.items():
        base = ROOT / d
        if not base.exists(): continue
        entries = []
        for p in sorted(base.rglob("*.json")):
            if p.name.endswith((".results.json", ".checkpoint.json", ".error.json")): continue
            try:
                run = load_run(p, label)
                render_plot(run, PLOTDIR / f"{group_slug(label)}__{run['id']}.png")
                model = model or run["model"]
                run.pop("ch")
                rf = f"runs/{group_slug(label)}__{run['id']}.json"
                (OUT / rf).write_text(json.dumps(run))
                entries.append({"id": run["id"], "file": rf,
                                "task_order": run["task_order"], "n_agents": run["n_agents"]})
            except Exception as ex:
                print("skip", p.name, ex)
        if entries:
            index[label] = entries
    plots = []
    for n, fp in AGG_PLOTS:
        src = ROOT / fp
        if src.exists():
            shutil.copy(src, AGGDIR / src.name)
            plots.append({"name": n, "src": f"agg_plots/{src.name}"})
    payload = json.dumps({"groups": index, "plots": plots, "model": model})
    (OUT/"inspector.html").write_text(HTML.replace("__DATA__", payload))
    n = sum(len(v) for v in index.values())
    kb = lambda d: sum(f.stat().st_size for f in d.rglob("*") if f.is_file()) // 1024
    print(f"Saved: {OUT/'inspector.html'}  ({n} runs, model={model}, "
          f"index {(OUT/'inspector.html').stat().st_size//1024} KB, runs/ {kb(RUNDIR)} KB, "
          f"agg_plots/ {kb(AGGDIR)} KB, run_plots/ {kb(PLOTDIR)} KB)")
    print("Local preview: python -m http.server -d data/plots/inspector 8123  →  http://localhost:8123/inspector.html")


HTML = r"""<!doctype html><html><head><meta charset="utf-8"><title>Run inspector</title><style>
 *{box-sizing:border-box} body{margin:0;font:14px/1.55 -apple-system,Segoe UI,Roboto,sans-serif;color:#1a1a1a}
 #top{background:#22303f;color:#fff;padding:8px 16px;font-size:13px} #top b{color:#8fd3ff}
 #app{display:flex;height:calc(100vh - 37px)}
 #side{width:270px;flex:none;background:#f4f5f7;border-right:1px solid #ddd;overflow-y:auto;padding:8px}
 #main{flex:1;overflow-y:auto;padding:16px 26px}
 h2{font-size:15px;border-bottom:2px solid #eee;padding-bottom:4px;margin-top:22px}
 .grp{font-weight:700;font-size:11.5px;color:#555;margin:12px 6px 4px;text-transform:uppercase}
 .run{padding:4px 8px;cursor:pointer;border-radius:5px;font-size:12.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
 .run:hover{background:#e6e9ee}.run.sel{background:#4C72B0;color:#fff}
 select{font-size:13px;padding:4px 8px;border-radius:6px;border:1px solid #bbb;margin:6px 0}
 table{border-collapse:collapse;font-size:12.5px;margin:8px 0}td,th{border:1px solid #e2e2e2;padding:3px 8px;text-align:right}th{background:#f7f7f9}
 td.l,th.l{text-align:left}.noise{color:#c0392b}
 .rd{border:1px solid #e8e8e8;border-radius:8px;margin:10px 0;padding:8px 14px;background:#fcfcfd}.rd h3{margin:0 0 6px;font-size:13px;color:#4C72B0}
 .ag{margin:6px 0;padding:6px 10px;background:#f7f8fa;border-radius:6px}.who{font-weight:700;font-size:12px}
 .myth{white-space:pre-wrap;font-size:12.5px;background:#fff8ef;border-left:3px solid #DD8452;padding:6px 10px;margin:4px 0;border-radius:4px}
 .reason{white-space:pre-wrap;font-size:12px;background:#eef4fb;border-left:3px solid #4C72B0;padding:6px 10px;margin:4px 0;border-radius:4px}
 .prompt{white-space:pre-wrap;font-size:12px;background:#f3f0fa;border-left:3px solid #8172b3;padding:6px 10px;margin:4px 0;border-radius:4px}
 .msg{white-space:pre-wrap;font-size:12px;padding:6px 10px;margin:4px 0;border-radius:4px}
 .msg.system{background:#eceff1;border-left:3px solid #607d8b}.msg.user{background:#f3f0fa;border-left:3px solid #8172b3}.msg.assistant{background:#e8f5e9;border-left:3px solid #55A868}
 .meta{color:#666;font-size:12.5px}.hint{color:#999;font-size:12px}.plt img{max-width:100%;border:1px solid #eee;border-radius:6px;margin:6px 0}
 img.runplot{max-width:100%;border:1px solid #eee;border-radius:6px}
</style></head><body>
<div id="top">🔎 Run inspector &nbsp;·&nbsp; generation model: <b id="model"></b> &nbsp;·&nbsp; <a href="#" style="color:#8fd3ff" onclick="showPlots();return false">aggregate plots ▸</a></div>
<div id="app"><div id="side"><div id="list"></div></div><div id="main"><div id="view"><p class="hint">Pick a run on the left.</p></div></div></div>
<script>
const D=__DATA__;document.getElementById('model').textContent=D.model||'(unknown)';
const list=document.getElementById('list'),view=document.getElementById('view');let cur=null,curRun=null,mode='transcript';
const cache=new Map(),CACHE_MAX=6; // small LRU: keep the tab light even after browsing many runs
async function fetchRun(file){
 if(cache.has(file)){const v=cache.get(file);cache.delete(file);cache.set(file,v);return v;}
 const res=await fetch(file);if(!res.ok)throw new Error('HTTP '+res.status);
 const v=await res.json();cache.set(file,v);
 if(cache.size>CACHE_MAX)cache.delete(cache.keys().next().value);
 return v;}
for(const g in D.groups){const h=document.createElement('div');h.className='grp';h.textContent=g;list.appendChild(h);
 D.groups[g].forEach((r,i)=>{const el=document.createElement('div');el.className='run';el.textContent=r.id.replace(/_memtest.*/,'').replace(/^noise\w+_v2_/,'').replace(/^noise\w+_/,'');el.title=r.id;
  el.onclick=async()=>{document.querySelectorAll('.run').forEach(x=>x.classList.remove('sel'));el.classList.add('sel');cur=[g,i];
   view.innerHTML='<p class="hint">Loading '+esc(r.id)+' …</p>';
   try{curRun=await fetchRun(r.file);render();}
   catch(e){view.innerHTML='<p class="hint">Could not load '+esc(r.file)+' ('+esc(e.message)+'). If viewing from disk, serve the folder instead: <code>python -m http.server -d data/plots/inspector 8123</code></p>';}};
  list.appendChild(el);});}
function esc(s){const d=document.createElement('div');d.textContent=s==null?'':s;return d.innerHTML;}
function num(x){return x==null?'–':Math.round(x*100)/100;}
function promptsForRound(r,rd){ // real per-call input prompts from interaction_history
 return (r.prompts||[]).filter(p=>p.round===rd);}
function render(){if(!cur||!curRun)return;const r=curRun;
 let h=`<h2>${esc(r.id)}</h2><div class="meta">${cur[0]} · task order <b>${(r.task_order||[]).join(' → ')}</b> · ${r.n_agents} agents · ${r.rounds.length} rounds · model ${esc(r.model)}</div>`;
 h+=`<img class="runplot" src="${r.plot}" onerror="this.style.display='none'"/>`;
 h+=`<h2>Per-round numbers <span class="hint">(actual, <span class="noise">noise✎</span>)</span></h2><table><tr><th>rd</th><th class="l">inv→tru</th><th>sent</th><th class="noise">✎</th><th>recv</th><th>ret</th><th class="noise">✎</th><th class="l">balances</th></tr>`;
 r.rounds.forEach(rd=>rd.dyads.forEach((d,di)=>{h+=`<tr><td>${di?'':rd.round}</td><td class="l">${esc(d.inv)}→${esc(d.tru)}</td><td>${num(d.sent)}</td><td class="noise">${num(d.sent_c)}</td><td>${num(d.recv)}</td><td>${num(d.ret)}</td><td class="noise">${num(d.ret_c)}</td><td class="l">${di?'':esc(Object.entries(rd.balances).map(([k,v])=>k.replace('Agent_','A')+':'+v).join('  '))}</td></tr>`;}));
 h+=`</table>`;
 h+=`<h2>Transcript &nbsp;<select id="mode" onchange="mode=this.value;render()">
   <option value="transcript">game + myth outputs</option>
   <option value="prompts">+ input prompt each round</option>
   <option value="context">full model context (system + messages)</option></select></h2>`;
 view.innerHTML=h;document.getElementById('mode').value=mode;
 const body=document.createElement('div');
 if(mode==='context'){
  body.innerHTML+=`<p class="hint">The exact messages sent to the model (from interaction_history.messages_sent — untruncated). Shown per agent for its last <b>game</b> call and last <b>myth</b> call. The system prompt appears once, as the first message.</p>`;
  for(const a in (r.final_ctx||{})){const calls=r.final_ctx[a]||[];
   calls.forEach(c=>{
    body.innerHTML+=`<div class="rd"><h3>${esc(a)} — full context on its last <b>${esc(c.task)}</b> call (round ${esc(c.round)}${c.role?', '+esc(c.role):''})</h3>`+
      (c.messages||[]).map(m=>`<div class="msg ${m.role}"><b>${m.role}:</b> ${esc(m.content)}</div>`).join('')+`</div>`;});}
 } else {
  r.rounds.forEach(rd=>{let s=`<div class="rd"><h3>Round ${rd.round}</h3>`;
   if(mode==='prompts'){const pr=promptsForRound(r,rd.round);
     if(pr.length)pr.forEach(p=>s+=`<div class="prompt"><b>input prompt → ${esc(p.agent)} (${esc(p.task)}, ${esc(p.role)}):</b> ${esc(p.prompt)}</div>`);
     else s+=`<div class="hint">no interaction_history for this round</div>`;}
   const ags=new Set([...Object.keys(rd.reasoning||{}),...Object.keys(rd.myths||{})]);
   const mythFirst=(r.task_order||[])[0]==='myth'; // block order mirrors the run's task order
   ags.forEach(a=>{s+=`<div class="ag"><div class="who">${esc(a)}</div>`;
     const game=rd.reasoning[a]?`<div class="reason"><b>game:</b> ${esc(rd.reasoning[a])}</div>`:'';
     const myth=rd.myths[a]?`<div class="myth"><b>myth:</b> ${esc(rd.myths[a])}</div>`:'';
     s+=mythFirst?myth+game:game+myth;s+=`</div>`;});
   body.innerHTML+=s+`</div>`;});
 }
 view.appendChild(body);
}
function showPlots(){document.querySelectorAll('.run').forEach(x=>x.classList.remove('sel'));cur=null;curRun=null;
 view.innerHTML='<h2>Aggregate plots</h2><div class="plt">'+D.plots.map(p=>`<h3>${esc(p.name)}</h3><img loading="lazy" src="${p.src}"/>`).join('')+'</div>';}
</script></body></html>"""


if __name__ == "__main__":
    main()

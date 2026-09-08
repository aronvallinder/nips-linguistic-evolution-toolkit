#!/usr/bin/env python3
"""Build a standalone run inspector for the negative-noise + defectors campaign.

Reads Aron's campaign from the shared-run download at
  nlet-hf-data/uploaders/vallinder/data/json/noise_experiments/
      negative_only_crossmodel_defectors_n5_20260825/
and writes a self-contained inspector site to data/plots/inspector_negnoise/:
  inspector.html   sidebar of individual runs, model dropdown in the top bar
  runs/*.json      per-run data (numbers, reasoning, myths, prompts, contexts)
  run_plots/*.png  per-run 2x2 trajectory plot
  agg_plots/       per-model aggregate figures (built by
                   scripts/build_negnoise_inspector_plots.py)

Published by scripts/refresh_inspector_site.sh under /negnoise/ on the
GitHub Pages site.

Usage: python3 scripts/build_negnoise_inspector.py
"""
import glob
import json
import os
import re
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CAMPAIGN = (
    PROJECT_ROOT
    / "nlet-hf-data/uploaders/vallinder/data/json/noise_experiments"
    / "negative_only_crossmodel_defectors_n5_20260825"
)
OUT = PROJECT_ROOT / "data/plots/inspector_negnoise"

MODELS = ["claude-sonnet-4.5", "gemini-3.7-flash", "gpt-5-nano"]
MODEL_LABELS = {
    "claude-sonnet-4.5": "Claude Sonnet 4.5",
    "gemini-3.7-flash": "Gemini 3.7 Flash",
    "gpt-5-nano": "GPT-5 Nano",
}
ORDER_LABELS = {"game": "game only", "game_myth": "game→myth", "myth_game": "myth→game"}


def variant_info(params_dir: str, arm: str):
    """-> (sort_key, short_label) for the defection variant of a cell."""
    if "random25" in params_dir or "defectors25" in params_dir:
        return 1, ("25% random defection" if arm == "dyad" else "2/8 defectors")
    if "random50" in params_dir or "defectors50" in params_dir:
        return 2, ("50% random defection" if arm == "dyad" else "4/8 defectors")
    return 0, ("no defection" if arm == "dyad" else "no defectors")


def build_rounds(data):
    rounds = []
    for turn in data.get("conversation_history", []):
        dyads = []
        for dy in turn.get("dyads") or []:
            dyads.append(
                {
                    "inv": dy.get("investor"),
                    "tru": dy.get("trustee"),
                    "sent": dy.get("sent"),
                    "sent_c": dy.get("sent_communicated"),
                    "recv": dy.get("received"),
                    "ret": dy.get("returned"),
                    "ret_c": dy.get("returned_communicated"),
                }
            )
        reasoning = {
            a: r.get("content")
            for a, r in (turn.get("game_responses") or {}).items()
            if r and r.get("content")
        }
        rounds.append(
            {
                "round": turn.get("round"),
                "dyads": dyads,
                "balances": turn.get("balances") or {},
                "reasoning": reasoning,
                "myths": turn.get("myths") or {},
            }
        )
    return rounds


def build_prompts_and_ctx(data):
    """prompts: one entry per LLM call; final_ctx: last game + last myth call per agent."""
    prompts, final_ctx = [], {}
    for agent_id, agent in sorted((data.get("agents") or {}).items()):
        last = {}
        for e in agent.get("interaction_history") or []:
            md = e.get("metadata") or {}
            task = md.get("task") or "?"
            entry = {
                "round": md.get("round"),
                "task": task,
                "role": md.get("role_label") or md.get("role") or "",
                "agent": agent_id,
                "prompt": e.get("prompt"),
            }
            prompts.append(entry)
            last[task] = {
                "task": task,
                "round": md.get("round"),
                "role": md.get("role_label") or md.get("role") or "",
                "messages": e.get("messages_sent") or [],
            }
        if last:
            final_ctx[agent_id] = [last[t] for t in ("game", "myth") if t in last]
    prompts.sort(key=lambda p: (p["round"] or 0, p["agent"]))
    return prompts, final_ctx


def plot_run(rounds, out_path, title, n_agents):
    rds = [r["round"] for r in rounds if r["dyads"]]
    if not rds:
        return False

    def dyad_mean(key):
        return [
            np.mean([d[key] for d in r["dyads"] if isinstance(d.get(key), (int, float))] or [np.nan])
            for r in rounds
            if r["dyads"]
        ]

    sent, sent_c = dyad_mean("sent"), dyad_mean("sent_c")
    recv = dyad_mean("recv")
    ret, ret_c = dyad_mean("ret"), dyad_mean("ret_c")

    fig, ax = plt.subplots(2, 2, figsize=(11.6, 7.2))
    a = ax[0][0]
    a.plot(rds, sent, "-o", ms=3.5, color="#4C72B0", label="sent")
    a.plot(rds, sent_c, "--", color="#4C72B0", alpha=0.55, label="sent (noisy)")
    a.plot(rds, recv, "-o", ms=3.5, color="#55A868", label="received")
    a.plot(rds, ret, "-o", ms=3.5, color="#DD8452", label="returned")
    a.plot(rds, ret_c, "--", color="#DD8452", alpha=0.55, label="returned (noisy)")
    a.set_title("Transactions" + (" (mean across dyads)" if n_agents > 2 else ""))
    a.set_ylabel("$")
    a.legend(fontsize=7.5)

    a = ax[0][1]
    agents = sorted(rounds[-1]["balances"])
    for ag in agents:
        a.plot(rds, [r["balances"].get(ag) for r in rounds if r["dyads"]], "-o", ms=3, label=ag)
    a.set_title("Cumulative balance per agent")
    a.set_ylabel("$")
    a.legend(fontsize=7.5, ncols=2 if len(agents) > 4 else 1)

    a = ax[1][0]
    a.plot(rds, [s / 5 for s in sent], "-o", ms=3.5, color="#4C72B0", label="send fraction (of $5)")
    rr = [
        (np.nansum([d["ret"] for d in r["dyads"] if isinstance(d.get("ret"), (int, float))])
         / max(np.nansum([d["recv"] for d in r["dyads"] if isinstance(d.get("recv"), (int, float))]), 1e-9))
        for r in rounds if r["dyads"]
    ]
    a.plot(rds, rr, "-o", ms=3.5, color="#DD8452", label="return ratio")
    a.axhline(0.5, color="#999", lw=0.8, ls=":")
    a.set_ylim(-0.02, 1.05)
    a.set_title("Cooperation ratios")
    a.legend(fontsize=7.5)

    a = ax[1][1]
    noise_s = [
        np.mean([abs(d["sent"] - d["sent_c"]) for d in r["dyads"]
                 if isinstance(d.get("sent"), (int, float)) and isinstance(d.get("sent_c"), (int, float))] or [np.nan])
        for r in rounds if r["dyads"]
    ]
    noise_r = [
        np.mean([abs(d["ret"] - d["ret_c"]) for d in r["dyads"]
                 if isinstance(d.get("ret"), (int, float)) and isinstance(d.get("ret_c"), (int, float))] or [np.nan])
        for r in rounds if r["dyads"]
    ]
    a.plot(rds, noise_s, "-o", ms=3.5, color="#C44E52", label="|noise| on sent")
    a.plot(rds, noise_r, "-o", ms=3.5, color="#8172B3", label="|noise| on returned")
    a.set_title("Noise magnitude (communicated − actual)")
    a.legend(fontsize=7.5)

    for row in ax:
        for a in row:
            a.set_xlabel("round")
            a.grid(alpha=0.25)
    fig.suptitle(title, fontsize=11, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.955])
    fig.savefig(out_path, dpi=120)
    plt.close(fig)
    return True


def main():
    if not CAMPAIGN.is_dir():
        raise SystemExit(f"Campaign dir not found: {CAMPAIGN}\nRe-download nlet-hf-data first.")
    (OUT / "runs").mkdir(parents=True, exist_ok=True)
    (OUT / "run_plots").mkdir(parents=True, exist_ok=True)

    # groups[model][group_name] -> [sidebar item]; ordered by (arm, order, variant)
    collected = defaultdict(list)
    for path in sorted(glob.glob(str(CAMPAIGN / "**/*.json"), recursive=True)):
        if path.endswith(".results.json") or "checkpoint" in path:
            continue
        rel = os.path.relpath(path, CAMPAIGN).split(os.sep)
        arm_dir, model, order, params = rel[0], rel[1], rel[2], rel[3]
        arm = "dyad" if "dyad" in arm_dir else "pop8"
        vsort, vlabel = variant_info(params, arm)

        with open(path) as f:
            data = json.load(f)
        md = data.get("run_metadata", {})
        gd = data.get("game_data", {})
        stem = Path(path).stem
        rep = (re.search(r"rep(\d+)", stem) or re.search(r"_(\d{3})_", stem) or [None, "?"])[1]
        run_id = f"{arm}_{model}_{order}_v{vsort}_{stem}"

        rounds = build_rounds(data)
        prompts, final_ctx = build_prompts_and_ctx(data)
        n_agents = md.get("num_agents") or len(data.get("agents") or {})
        defectors = gd.get("defector_agent_ids") or []
        rdp = gd.get("random_defection_probability") or 0

        arm_label = "dyad" if arm == "dyad" else "population 8"
        group = f"{MODEL_LABELS[model]} · {arm_label} · {ORDER_LABELS[order]} · {vlabel}"
        title = f"{group} · rep{rep}"
        plot_rel = f"run_plots/{run_id}.png"
        plot_run(rounds, OUT / plot_rel, title, n_agents)

        extras = []
        if defectors:
            extras.append(f"defectors (forced $0): {', '.join(defectors)}")
        if rdp:
            extras.append(f"each game decision defects with p={rdp}")
        run = {
            "id": stem,
            "group": group,
            "task_order": data.get("task_order"),
            "n_agents": n_agents,
            "rounds": rounds,
            "prompts": prompts,
            "final_ctx": final_ctx,
            "meta": {"endowment": 5},
            "model": md.get("model"),
            "plot": plot_rel,
            "defectors": defectors,
            "condition": " · ".join(
                ["negative-only noise (uniform $0–1, informed)"] + extras
            ),
        }
        run_rel = f"runs/{run_id}.json"
        with open(OUT / run_rel, "w") as f:
            json.dump(run, f)
        collected[(model, arm, order, vsort)].append(
            {"group": group, "id": stem, "file": run_rel,
             "task_order": data.get("task_order"), "n_agents": n_agents, "rep": rep}
        )

    groups = {m: {} for m in MODELS}
    for (model, arm, order, vsort) in sorted(
        collected,
        key=lambda k: (MODELS.index(k[0]), k[1], ["game", "game_myth", "myth_game"].index(k[2]), k[3]),
    ):
        items = sorted(collected[(model, arm, order, vsort)], key=lambda r: r["id"])
        gname = items[0]["group"].split(" · ", 1)[1]  # model comes from the dropdown
        groups[model][gname] = [
            {k: it[k] for k in ("id", "file", "task_order", "n_agents", "rep")} for it in items
        ]

    agg = [{"name": "All models — mean send by defection level (game-only)", "src": "agg_plots/_all/overview.png"}]
    for m in MODELS:
        agg.append({"name": f"{MODEL_LABELS[m]} — dyad (2 agents)", "src": f"agg_plots/{m}/dyad.png"})
        agg.append({"name": f"{MODEL_LABELS[m]} — population (8 agents)", "src": f"agg_plots/{m}/pop8.png"})

    D = {
        "models": [{"id": m, "label": MODEL_LABELS[m]} for m in MODELS],
        "groups": groups,
        "plots": agg,
    }
    html = HTML_TEMPLATE.replace("__DATA__", json.dumps(D))
    with open(OUT / "inspector.html", "w") as f:
        f.write(html)
    n_runs = sum(len(v) for v in collected.values())
    print(f"Built inspector with {n_runs} runs -> {OUT}")


HTML_TEMPLATE = r"""<!doctype html><html><head><meta charset="utf-8"><title>Negative noise + defectors — run inspector</title><style>
 *{box-sizing:border-box} body{margin:0;font:14px/1.55 -apple-system,Segoe UI,Roboto,sans-serif;color:#1a1a1a}
 #top{background:#3a2a3f;color:#fff;padding:8px 16px;font-size:13px} #top b{color:#ffd28f} #top a{color:#ffd28f}
 #top select{font-size:12.5px;padding:2px 6px;border-radius:5px;border:1px solid #777;margin:0 4px}
 #app{display:flex;height:calc(100vh - 37px)}
 #side{width:290px;flex:none;background:#f4f5f7;border-right:1px solid #ddd;overflow-y:auto;padding:8px}
 #main{flex:1;overflow-y:auto;padding:16px 26px}
 h2{font-size:15px;border-bottom:2px solid #eee;padding-bottom:4px;margin-top:22px}
 .grp{font-weight:700;font-size:11.5px;color:#555;margin:12px 6px 4px;text-transform:uppercase}
 .run{padding:4px 8px;cursor:pointer;border-radius:5px;font-size:12.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
 .run:hover{background:#e6e9ee}.run.sel{background:#8C5B9E;color:#fff}
 select{font-size:13px;padding:4px 8px;border-radius:6px;border:1px solid #bbb;margin:6px 0}
 table{border-collapse:collapse;font-size:12.5px;margin:8px 0}td,th{border:1px solid #e2e2e2;padding:3px 8px;text-align:right}th{background:#f7f7f9}
 td.l,th.l{text-align:left}.noise{color:#c0392b}.defect{color:#c0392b;font-weight:700}
 .rd{border:1px solid #e8e8e8;border-radius:8px;margin:10px 0;padding:8px 14px;background:#fcfcfd}.rd h3{margin:0 0 6px;font-size:13px;color:#8C5B9E}
 .ag{margin:6px 0;padding:6px 10px;background:#f7f8fa;border-radius:6px}.who{font-weight:700;font-size:12px}
 .myth{white-space:pre-wrap;font-size:12.5px;background:#fff8ef;border-left:3px solid #DD8452;padding:6px 10px;margin:4px 0;border-radius:4px}
 .reason{white-space:pre-wrap;font-size:12px;background:#eef4fb;border-left:3px solid #4C72B0;padding:6px 10px;margin:4px 0;border-radius:4px}
 .prompt{white-space:pre-wrap;font-size:12px;background:#f3f0fa;border-left:3px solid #8172b3;padding:6px 10px;margin:4px 0;border-radius:4px}
 .msg{white-space:pre-wrap;font-size:12px;padding:6px 10px;margin:4px 0;border-radius:4px}
 .msg.system{background:#eceff1;border-left:3px solid #607d8b}.msg.user{background:#f3f0fa;border-left:3px solid #8172b3}.msg.assistant{background:#e8f5e9;border-left:3px solid #55A868}
 .meta{color:#666;font-size:12.5px}.hint{color:#999;font-size:12px}.plt img{max-width:100%;border:1px solid #eee;border-radius:6px;margin:6px 0}
 img.runplot{max-width:100%;border:1px solid #eee;border-radius:6px}
</style></head><body>
<div id="top">🔎 Negative noise + defectors inspector &nbsp;·&nbsp; model:
 <select id="modelsel" onchange="setModel(this.value)"></select>
 &nbsp;·&nbsp; <a href="#" onclick="showPlots();return false">aggregate plots ▸</a>
 &nbsp;·&nbsp; <a href="../">← main inspector</a></div>
<div id="app"><div id="side"><div id="list"></div></div><div id="main"><div id="view"><p class="hint">Pick a run on the left.</p></div></div></div>
<script>
const D=__DATA__;
const list=document.getElementById('list'),view=document.getElementById('view');let cur=null,curRun=null,mode='transcript',model=D.models[0].id;
const msel=document.getElementById('modelsel');
D.models.forEach(m=>{const o=document.createElement('option');o.value=m.id;o.textContent=m.label;msel.appendChild(o);});
const cache=new Map(),CACHE_MAX=6;
async function fetchRun(file){
 if(cache.has(file)){const v=cache.get(file);cache.delete(file);cache.set(file,v);return v;}
 const res=await fetch(file);if(!res.ok)throw new Error('HTTP '+res.status);
 const v=await res.json();cache.set(file,v);
 if(cache.size>CACHE_MAX)cache.delete(cache.keys().next().value);
 return v;}
function setModel(m){model=m;cur=null;curRun=null;view.innerHTML='<p class="hint">Pick a run on the left.</p>';buildList();}
function buildList(){list.innerHTML='';const groups=D.groups[model]||{};
 for(const g in groups){const h=document.createElement('div');h.className='grp';h.textContent=g;list.appendChild(h);
  groups[g].forEach((r,i)=>{const el=document.createElement('div');el.className='run';el.textContent='rep'+r.rep;el.title=r.id;
   el.onclick=async()=>{document.querySelectorAll('.run').forEach(x=>x.classList.remove('sel'));el.classList.add('sel');cur=[g,i];
    view.innerHTML='<p class="hint">Loading '+esc(r.id)+' …</p>';
    try{curRun=await fetchRun(r.file);render();}
    catch(e){view.innerHTML='<p class="hint">Could not load '+esc(r.file)+' ('+esc(e.message)+'). If viewing from disk, serve the folder instead: <code>python -m http.server -d data/plots/inspector_negnoise 8123</code></p>';}};
   list.appendChild(el);});}}
function esc(s){const d=document.createElement('div');d.textContent=s==null?'':s;return d.innerHTML;}
function num(x){return x==null?'–':Math.round(x*100)/100;}
function tag(r,a){return esc(a)+((r.defectors||[]).includes(a)?' <span class="defect">⚑ defector</span>':'');}
function promptsForRound(r,rd){return (r.prompts||[]).filter(p=>p.round===rd);}
function render(){if(!cur||!curRun)return;const r=curRun;
 let h=`<h2>${esc(r.id)}</h2><div class="meta">${esc(cur[0])} · task order <b>${(r.task_order||[]).join(' → ')}</b> · ${r.n_agents} agents · ${r.rounds.length} rounds · model ${esc(r.model)}</div>`;
 if(r.condition)h+=`<div class="meta">${esc(r.condition)}</div>`;
 h+=`<img class="runplot" src="${r.plot}" onerror="this.style.display='none'"/>`;
 h+=`<h2>Per-round numbers <span class="hint">(actual, <span class="noise">noise✎</span>)</span></h2><table><tr><th>rd</th><th class="l">inv→tru</th><th>sent</th><th class="noise">✎</th><th>recv</th><th>ret</th><th class="noise">✎</th><th class="l">balances</th></tr>`;
 r.rounds.forEach(rd=>rd.dyads.forEach((d,di)=>{h+=`<tr><td>${di?'':rd.round}</td><td class="l">${esc(d.inv)}→${esc(d.tru)}</td><td>${num(d.sent)}</td><td class="noise">${num(d.sent_c)}</td><td>${num(d.recv)}</td><td>${num(d.ret)}</td><td class="noise">${num(d.ret_c)}</td><td class="l">${di?'':esc(Object.entries(rd.balances).map(([k,v])=>k.replace('Agent_','A')+':'+Math.round(v*100)/100).join('  '))}</td></tr>`;}));
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
    body.innerHTML+=`<div class="rd"><h3>${tag(r,a)} — full context on its last <b>${esc(c.task)}</b> call (round ${esc(c.round)}${c.role?', '+esc(c.role):''})</h3>`+
      (c.messages||[]).map(m=>`<div class="msg ${m.role}"><b>${m.role}:</b> ${esc(m.content)}</div>`).join('')+`</div>`;});}
 } else {
  r.rounds.forEach(rd=>{let s=`<div class="rd"><h3>Round ${rd.round}</h3>`;
   if(mode==='prompts'){const pr=promptsForRound(r,rd.round);
     if(pr.length)pr.forEach(p=>s+=`<div class="prompt"><b>input prompt → ${esc(p.agent)} (${esc(p.task)}, ${esc(p.role)}):</b> ${esc(p.prompt)}</div>`);
     else s+=`<div class="hint">no interaction_history for this round</div>`;}
   const ags=new Set([...Object.keys(rd.reasoning||{}),...Object.keys(rd.myths||{})]);
   const mythFirst=(r.task_order||[])[0]==='myth';
   ags.forEach(a=>{s+=`<div class="ag"><div class="who">${tag(r,a)}</div>`;
     const game=rd.reasoning[a]?`<div class="reason"><b>game:</b> ${esc(rd.reasoning[a])}</div>`:'';
     const myth=rd.myths[a]?`<div class="myth"><b>myth:</b> ${esc(rd.myths[a])}</div>`:'';
     s+=mythFirst?myth+game:game+myth;s+=`</div>`;});
   body.innerHTML+=s+`</div>`;});
 }
 view.appendChild(body);
}
function showPlots(){document.querySelectorAll('.run').forEach(x=>x.classList.remove('sel'));cur=null;curRun=null;
 view.innerHTML='<h2>Aggregate plots</h2><div class="plt">'+D.plots.map(p=>`<h3>${esc(p.name)}</h3><img loading="lazy" src="${p.src}"/>`).join('')+'</div>';}
buildList();
</script></body></html>
"""


if __name__ == "__main__":
    main()

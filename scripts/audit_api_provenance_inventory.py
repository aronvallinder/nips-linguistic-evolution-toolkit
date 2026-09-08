import json, os, re, sys, csv, statistics
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root
OUT=sys.argv[1] if len(sys.argv)>1 else os.path.join(ROOT,"data/analysis/api_equivalence_audit_2026_09_04")
os.makedirs(OUT, exist_ok=True)
NUM=r"\$?\s*(-?\d+(?:\.\d*)?|-?\.\d+)"
PAT=re.compile(rf"'(send|return)':\s*{NUM}|\"(send|return)\":\s*{NUM}", re.I)

def uploader_of(p):
    m=re.search(r"data/shared_runs/uploaders/([^/]+)/", p)
    return m.group(1) if m else "local(data/json)"

def expset_of(p):
    rel=p
    m=re.search(r"data/json/(.*)$", p) or re.search(r"runs_json/(.*)$", p)
    if not m: return "?"
    parts=m.group(1).split("/")
    if parts[0]=="noise_experiments" and len(parts)>2:
        return "noise_experiments/"+parts[1]
    return parts[0]

rows=[]; orphan_ckpt=[]
for base in ["data/json","data/shared_runs"]:
    for dp,dn,fn in os.walk(os.path.join(ROOT,base)):
        names=set(fn)
        for f in fn:
            if not f.endswith(".json"): continue
            if f.endswith(".results.json") or f.endswith(".error.json"): continue
            if f.endswith(".checkpoint.json"):
                full=f[:-len(".checkpoint.json")]+".json"
                if full not in names: orphan_ckpt.append(os.path.join(dp,f))
                continue
            p=os.path.join(dp,f)
            try:
                d=json.load(open(p))
            except Exception as e:
                rows.append({"path":p,"error":f"load:{type(e).__name__}"}); continue
            if not isinstance(d,dict) or "run_metadata" not in d:
                rows.append({"path":p,"error":"no_run_metadata","keys":",".join(list(d.keys())[:8]) if isinstance(d,dict) else type(d).__name__}); continue
            rm=d.get("run_metadata") or {}
            r={"path":p.replace(ROOT+"/",""),"uploader":uploader_of(p),"expset":expset_of(p),
               "model":rm.get("model"),"llm_provider":rm.get("llm_provider"),"provider_model":rm.get("provider_model"),
               "llm_provider_mode":rm.get("llm_provider_mode"),"max_output_tokens":rm.get("max_output_tokens"),
               "max_output_tokens_source":rm.get("max_output_tokens_source"),"thinking_level":rm.get("thinking_level"),
               "temperature_sent":rm.get("temperature_sent"),"temperature":rm.get("temperature"),
               "num_agents":rm.get("num_agents"),"num_turns":rm.get("num_turns"),"memory_capacity":rm.get("memory_capacity"),
               "chat_memory_mode":rm.get("chat_memory_mode"),"task_order":"+".join(d.get("task_order") or []),
               "noise_config":json.dumps(rm.get("noise_config")) if rm.get("noise_config") is not None else "",
               "defector_ratio_actual":rm.get("defector_ratio_actual"),"random_defection_probability":rm.get("random_defection_probability"),
               "code_commit":rm.get("code_commit"),"config_path":rm.get("config_path"),"game_params_name":rm.get("game_params_name"),
               "n_rounds_done":len(d.get("conversation_history") or [])}
            # diagnostics
            g_llm=g_scr=0; r_text=r_enc=r_tok_pos=0; out=[]; rtoks=[]; empty=0; nojson=0; other_src={}
            m_n=0; m_out=[]; m_rtoks=[]; m_r_text=0
            for ch in d.get("conversation_history") or []:
                for aid,gr in (ch.get("game_responses") or {}).items():
                    if not isinstance(gr,dict): continue
                    src=gr.get("response_source","llm")
                    if src=="llm": g_llm+=1
                    elif src=="scripted": g_scr+=1
                    else: other_src[src]=other_src.get(src,0)+1
                    if src!="llm": continue
                    c=gr.get("content") or ""
                    if not c.strip(): empty+=1
                    if not PAT.search(c): nojson+=1
                    rs=gr.get("reasoning")
                    if isinstance(rs,str) and rs:
                        if rs.startswith("[") and "reasoning tokens" in rs: r_enc+=1
                        else: r_text+=1
                    u=gr.get("usage") or {}
                    if u:
                        out.append(u.get("output_tokens") or 0); rt=u.get("reasoning_tokens") or 0; rtoks.append(rt)
                        if rt>0: r_tok_pos+=1
                for aid,mr in (ch.get("myth_responses") or {}).items():
                    if not isinstance(mr,dict): continue
                    m_n+=1
                    rs=mr.get("reasoning")
                    if isinstance(rs,str) and rs and not rs.startswith("["): m_r_text+=1
                    u=mr.get("usage") or {}
                    if u: m_out.append(u.get("output_tokens") or 0); m_rtoks.append(u.get("reasoning_tokens") or 0)
            errs={}; n_inter=0; err_msgs={}
            for aid,a in (d.get("agents") or {}).items():
                for ev in a.get("interaction_history") or []:
                    n_inter+=1
                    e=ev.get("error")
                    if e:
                        k=e.get("type"); errs[k]=errs.get(k,0)+1
                        msg=(e.get("message") or "")[:60]; err_msgs[msg]=err_msgs.get(msg,0)+1
            r.update({"g_llm":g_llm,"g_scripted":g_scr,"g_other_src":json.dumps(other_src) if other_src else "",
                      "g_reasoning_text":r_text,"g_reasoning_encrypted":r_enc,"g_reasoning_tok_pos":r_tok_pos,
                      "g_empty":empty,"g_nojson":nojson,
                      "g_out_mean":round(statistics.mean(out),1) if out else "","g_out_max":max(out) if out else "",
                      "g_out_median":statistics.median(out) if out else "",
                      "g_rtok_mean":round(statistics.mean(rtoks),1) if rtoks else "","g_rtok_max":max(rtoks) if rtoks else "",
                      "g_n_usage":len(out),
                      "m_n":m_n,"m_reasoning_text":m_r_text,"m_out_mean":round(statistics.mean(m_out),1) if m_out else "","m_out_max":max(m_out) if m_out else "",
                      "m_rtok_mean":round(statistics.mean(m_rtoks),1) if m_rtoks else "",
                      "n_interactions":n_inter,"n_errors":sum(errs.values()),"errors":json.dumps(errs) if errs else "",
                      "err_msgs":json.dumps(err_msgs) if err_msgs else ""})
            rows.append(r)
cols=sorted({k for r in rows for k in r})
first=["path","uploader","expset","model","llm_provider","provider_model","llm_provider_mode","max_output_tokens","max_output_tokens_source","thinking_level","temperature_sent","temperature"]
cols=first+[c for c in cols if c not in first]
with open(os.path.join(OUT,"runs_inventory.csv"),"w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=cols); w.writeheader()
    for r in rows: w.writerow(r)
with open(os.path.join(OUT,"orphan_checkpoints.txt"),"w") as fh:
    fh.write("\n".join(orphan_ckpt))
print("rows",len(rows),"orphan_ckpts",len(orphan_ckpt))

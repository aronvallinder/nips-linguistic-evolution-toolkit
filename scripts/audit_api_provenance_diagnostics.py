import json, os, re, csv, statistics, collections
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root
OUT=sys.argv[1] if len(sys.argv)>1 else os.path.join(ROOT,"data/analysis/api_equivalence_audit_2026_09_04")
os.makedirs(OUT, exist_ok=True)
NUM=r"\$?\s*(-?\d+(?:\.\d*)?|-?\.\d+)"
PAT=re.compile(rf"'(send|return)':\s*{NUM}|\"(send|return)\":\s*{NUM}", re.I)
import pandas as pd
inv=pd.read_csv(os.path.join(OUT,"runs_inventory.csv"),low_memory=False)
inv=inv[inv["error"].isna()]
# per (expset-group, model) response-level stats
def infer(row):
    if isinstance(row.llm_provider,str): return row.llm_provider+"(meta)"
    m=row.model
    if row.g_reasoning_text>0: return "openrouter(reasoning text)"
    if m.startswith("anthropic/"):
        return "direct-anthropic-or-openrouter-no-thinking(ambiguous)"
    if m.startswith("google/"):
        return "direct-gemini(no text, thought tokens)" if row.g_reasoning_tok_pos>0 else "ambiguous"
    if m.startswith("openai/"):
        return "openrouter-or-direct(ambiguous)" if row.g_reasoning_encrypted>0 else "direct-openai-minimal-or-ambiguous"
    return "?"
inv["inferred_provider"]=inv.apply(infer,axis=1)
inv.to_csv(os.path.join(OUT,"runs_inventory_inferred.csv"),index=False)

resp_rows=[]; err_rows=[]
for _,row in inv.iterrows():
    p=os.path.join(ROOT,row.path)
    d=json.load(open(p))
    rm=d["run_metadata"]; cap=rm.get("max_output_tokens")
    endow=None
    for ch in d.get("conversation_history") or []:
        acts=ch.get("actions") or {}
        for aid,gr in (ch.get("game_responses") or {}).items():
            if not isinstance(gr,dict) or gr.get("response_source","llm")!="llm": continue
            c=gr.get("content") or ""; u=gr.get("usage") or {}
            a=acts.get(aid) or {}
            resp_rows.append({"path":row.path,"uploader":row.uploader,"expset":row.expset,"model":row.model,"inferred":row.inferred_provider,
                "num_agents":row.num_agents,"round":ch.get("round"),"agent":aid,"chars":len(c),"out":u.get("output_tokens"),"rtok":u.get("reasoning_tokens"),
                "inp":u.get("input_tokens"),"has_json":bool(PAT.search(c)),"empty":not c.strip(),
                "reason_kind":("text" if isinstance(gr.get("reasoning"),str) and gr["reasoning"] and not gr["reasoning"].startswith("[") else ("enc" if isinstance(gr.get("reasoning"),str) and gr["reasoning"] else "none")),
                "action":a.get("action"),"amount":a.get("amount"),"cap":cap,
                "hit_cap":(cap is not None and u.get("output_tokens") is not None and u.get("output_tokens")>=cap),
                "starts_json":c.lstrip().startswith("{") or c.lstrip().startswith("```")})
    for aid,a in (d.get("agents") or {}).items():
        for ev in a.get("interaction_history") or []:
            e=ev.get("error")
            if e:
                r=ev.get("response") or {}
                err_rows.append({"path":row.path,"uploader":row.uploader,"expset":row.expset,"model":row.model,"inferred":row.inferred_provider,"agent":aid,
                    "task":(ev.get("metadata") or {}).get("task"),"etype":e.get("type"),"emsg":(e.get("message") or "")[:160],
                    "resp_chars":len(r.get("content") or ""),"resp_out":(r.get("usage") or {}).get("output_tokens"),"resp_rtok":(r.get("usage") or {}).get("reasoning_tokens"),
                    "resp_head":(r.get("content") or "")[:120].replace("\n"," ")})
pd.DataFrame(resp_rows).to_csv(os.path.join(OUT,"game_responses.csv"),index=False)
pd.DataFrame(err_rows).to_csv(os.path.join(OUT,"interaction_errors.csv"),index=False)
print("responses",len(resp_rows),"errors",len(err_rows))

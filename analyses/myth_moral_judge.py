#!/usr/bin/env python3
"""Label the moral of every September myth with Arabella Sinclair's rubrics.

Two judge tasks, both read verbatim from her subproject so the labels are
comparable with her June analysis:
  label    arabella_analyses/data/rubrics/3moral_rubric.txt
           -> one of "be generous" / "be fair" / "be cautious"
  summary  arabella_analyses/data/rubrics/moral_summary.txt
           -> one-sentence moral

Request settings copied from arabella_analyses/src/analysis/judge.py:
temperature 0, JSON response format, her system prompt. She called GLM-5.2
through Together; here it is z-ai/glm-5.2 through OpenRouter with reasoning
switched off (her logged completions were 7-9 tokens, i.e. no visible
reasoning). The call goes straight to OpenRouter rather than through
src/utils.call_llm, whose provider routing depends on per-machine settings.

Every response is cached under data/judge_cache/moral/<model>/ keyed by the
exact prompt, so reruns are free and the table can be rebuilt offline.
OpenRouter's billed cost per call is recorded (usage.include).

  python3 analyses/myth_moral_judge.py --preflight            # print the cost line only
  python3 analyses/myth_moral_judge.py --task label --task summary
  python3 analyses/myth_moral_judge.py --model deepseek/deepseek-v4-flash --task label   # second judge
  python3 analyses/myth_moral_judge.py --arabella-check       # re-label her 200 June myths
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/analysis/linguistic_20260923"
RUBRICS = ROOT / "arabella_analyses/data/rubrics"
CACHE = ROOT / "data/judge_cache/moral"
PROMPTS = {"label": RUBRICS / "3moral_rubric.txt", "summary": RUBRICS / "moral_summary.txt"}
SYSTEM = ("You are an impartial LLM-as-judge. Return only valid JSON unless the "
          "user explicitly requests another format.")
LABELS = ["be generous", "be fair", "be cautious"]
# OpenRouter list prices, USD per 1M tokens (checked 2026-09-23 via /api/v1/models)
PRICES = {"z-ai/glm-5.2": (0.65, 2.042), "deepseek/deepseek-v4-flash": (0.089, 0.177)}
MIN_WORDS = 20


def render(task: str, text: str) -> str:
    prompt = PROMPTS[task].read_text()
    if "{text}" in prompt:
        return prompt.replace("{text}", text)
    return f"{prompt.rstrip()}\n\nInput text:\n{text}"


def parse(task: str, raw: str) -> tuple[str | None, str]:
    s = raw.strip()
    try:
        obj = json.loads(s[s.find("{"): s.rfind("}") + 1])
    except Exception:  # noqa: BLE001
        obj = None
    if task == "label":
        val = (obj or {}).get("label") if isinstance(obj, dict) else None
        if val is None:
            m = re.search(r"be (generous|fair|cautious)", s.lower())
            val = m.group(0) if m else None
        val = val.strip().lower() if isinstance(val, str) else None
        return (val, "ok") if val in LABELS else (None, "bad_label")
    val = (obj or {}).get("moral_summary") if isinstance(obj, dict) else None
    if not val and isinstance(obj, dict):  # wrong or blank key, e.g. {": ": "..."}
        strings = [v for v in obj.values() if isinstance(v, str) and len(v.split()) >= 4]
        val = strings[0] if len(strings) == 1 else None
    if val is None:  # her prompt shows the key unquoted, so models sometimes echo that
        m = re.search(r"moral_summary\"?\s*:\s*\"?(.+?)\"?\s*}?\s*$", s, re.S)
        val = m.group(1).strip() if m else None
    return (val, "ok") if val else (None, "no_summary")


class Judge:
    def __init__(self, model: str, reasoning_off: bool = True):
        from openai import OpenAI
        from dotenv import load_dotenv
        load_dotenv(ROOT / ".env")
        key = os.environ.get("OPENROUTER_API_KEY")
        if not key:
            raise SystemExit("OPENROUTER_API_KEY missing in .env")
        self.client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=key)
        self.model = model
        self.reasoning_off = reasoning_off
        self.cache = CACHE / model.replace("/", "__")
        self.cache.mkdir(parents=True, exist_ok=True)

    def cache_path(self, user: str) -> Path:
        h = hashlib.sha256(f"{self.model}|T=0|{SYSTEM}|{user}".encode()).hexdigest()
        return self.cache / h[:2] / f"{h}.json"

    def __call__(self, user: str, max_retries: int = 8) -> dict:
        cp = self.cache_path(user)
        if cp.exists():
            return {**json.loads(cp.read_text()), "cached": True}
        body = {"usage": {"include": True}}
        if self.reasoning_off:
            body["reasoning"] = {"enabled": False}
        delay = 2.0
        for attempt in range(max_retries):
            try:
                resp = self.client.chat.completions.create(
                    model=self.model, temperature=0, response_format={"type": "json_object"},
                    messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}],
                    extra_body=body, timeout=120)
                usage = resp.usage.model_dump() if resp.usage else {}
                out = {"raw": resp.choices[0].message.content or "", "model_served": resp.model,
                       "prompt_tokens": usage.get("prompt_tokens"),
                       "completion_tokens": usage.get("completion_tokens"),
                       "cost": usage.get("cost")}
                cp.parent.mkdir(parents=True, exist_ok=True)
                cp.write_text(json.dumps(out))
                return {**out, "cached": False}
            except Exception as err:  # noqa: BLE001 - rate limits and 5xx: back off and retry
                if attempt == max_retries - 1:
                    return {"raw": "", "error": f"{type(err).__name__}: {err}", "cost": 0, "cached": False}
                time.sleep(delay)
                delay = min(delay * 2, 60)


def run_task(judge: Judge, task: str, frame: pd.DataFrame, workers: int) -> pd.DataFrame:
    prompts = [render(task, t) for t in frame["text"]]
    results: list[dict | None] = [None] * len(prompts)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(judge, p): i for i, p in enumerate(prompts)}
        for n, fut in enumerate(as_completed(futures), 1):
            results[futures[fut]] = fut.result()
            if n % 500 == 0:
                spent = sum((r or {}).get("cost") or 0 for r in results if r and not r.get("cached"))
                print(f"  {task}: {n}/{len(prompts)} done, ${spent:.2f} billed this session", flush=True)
    out = frame.drop(columns=["text"]).copy()
    parsed = [parse(task, r.get("raw", "")) for r in results]
    out[task] = [p[0] for p in parsed]
    out[f"{task}_status"] = [p[1] if not r.get("error") else "error" for p, r in zip(parsed, results)]
    out[f"{task}_cost"] = [r.get("cost") or 0 for r in results]
    out[f"{task}_cached"] = [r.get("cached") for r in results]
    return out


def preflight(model: str, tasks: list[str], frame: pd.DataFrame) -> float:
    pin, pout = PRICES[model]
    total = 0.0
    for task in tasks:
        n_in = sum(len(render(task, t)) for t in frame["text"]) / 4 + 40 * len(frame)  # ~4 chars/token + system
        n_out = (12 if task == "label" else 45) * len(frame)
        total += n_in / 1e6 * pin + n_out / 1e6 * pout
    # margin for retries and for providers that still emit some reasoning tokens
    return total * 1.5


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--model", default="z-ai/glm-5.2")
    ap.add_argument("--task", action="append", choices=list(PROMPTS))
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--limit", type=int, help="first N myths only (smoke test)")
    ap.add_argument("--preflight", action="store_true", help="print the cost line and exit")
    ap.add_argument("--arabella-check", action="store_true",
                    help="re-label the 200 June myths she labelled, to confirm the setup reproduces hers")
    args = ap.parse_args()
    tasks = args.task or ["label", "summary"]

    if args.arabella_check:
        src = pd.read_csv(ROOT / "arabella_analyses/data/tables/myths_gameplay_with_judgements_GLM-5.2.csv")
        frame = src[["run_id", "round", "agent_id", "myth_text", "judgement_GLM-5.2"]].rename(
            columns={"agent_id": "agent", "myth_text": "text", "judgement_GLM-5.2": "arabella_label"})
        tasks = ["label"]
        out_path = DATA / f"arabella_check_{args.model.replace('/', '__')}.csv"
    else:
        myths = pd.read_csv(DATA / "myths.csv")
        myths = myths[myths["n_words"] >= MIN_WORDS]
        frame = myths[["run_id", "size", "mixed", "composition", "task_order", "round", "agent", "family", "text"]]
        out_path = DATA / f"moral_labels_{args.model.replace('/', '__')}.csv"
    if args.limit:
        frame = frame.head(args.limit)
        out_path = out_path.with_name(out_path.stem + f"_first{args.limit}.csv")

    est = preflight(args.model, tasks, frame)
    print(f"MODEL={args.model} TASKS={','.join(tasks)} N={len(frame)} WORKERS={args.workers} "
          f"EST_COST=${est:.2f} (upper bound; cached prompts are free)")
    if args.preflight:
        return

    judge = Judge(args.model)
    out = frame.copy()
    for task in tasks:
        res = run_task(judge, task, frame, args.workers)
        for col in [task, f"{task}_status", f"{task}_cost", f"{task}_cached"]:
            out[col] = res[col].to_numpy()
        bad = (res[f"{task}_status"] != "ok").sum()
        print(f"{task}: {len(res) - bad} ok, {bad} unparsed/errored, "
              f"${res.loc[~res[f'{task}_cached'].astype(bool), f'{task}_cost'].sum():.2f} billed this run "
              f"(${res[f'{task}_cost'].sum():.2f} including cached calls)")
    out.drop(columns=["text"]).to_csv(out_path, index=False)
    print(f"-> {out_path}")
    if args.arabella_check:
        agree = (out["label"] == out["arabella_label"]).mean()
        print(f"agreement with Arabella's June GLM-5.2 labels: {agree:.1%} of {len(out)}")
        print(pd.crosstab(out["arabella_label"], out["label"]).to_string())


if __name__ == "__main__":
    main()

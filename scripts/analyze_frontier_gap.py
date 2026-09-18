#!/usr/bin/env python3
"""Why do the frontier models end with more resources than the September models?

Decomposes the 2026-09-18 frontier rerun (Opus 5, Gemini 3.1 Pro, GPT-5.6 Sol high)
against its September references (Sonnet 4.5, Gemini 3.7 Flash, GPT-5 Nano) on the
no-defector, informed negative-only-noise matrix. Reads the same finals as
scripts/analyze_frontier_rerun.py (receipt-audited frontier finals; September
no-defector finals) and prints, as Markdown tables:

  1. the accounting identity  mean final resources = 25 + 10 * mean send
  2. mean send per run, by arm x size x task order
  3. round-by-round mean send, game-only
  4. round-1 send distributions
  5. return ratios (returned / received) and the share of fair / loss-making returns
  6. the next send after a fair vs. a loss-making communicated return
  7. dyads: own send vs. the partner's send seen last round (matching / leading)
  8. hidden reasoning tokens and visible prose per game call
  9. keyword shares in the Claude models' visible justifications

Usage (data lives in the main checkout, so pass it when running from a worktree):
  python scripts/analyze_frontier_gap.py [--data-root /path/to/repo/data] [--out DIR]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
NON_FINAL = (".results.json", ".checkpoint.json", ".error.json")
NO_DEFECTOR_PARAMS = {"noisy2_crossmodel_negative_game_r3", "noisy2_crossmodel_negative_twotask_r3",
                      "noisy8_crossmodel_negative_game_r3", "noisy8_crossmodel_negative_twotask_r3"}
ARM = {  # provider_model -> (label, family, source)
    "claude-opus-5": ("Opus 5", "claude", "frontier"),
    "claude-sonnet-4-5-20250929": ("Sonnet 4.5", "claude", "september"),
    "gemini-3.1-pro-preview": ("Gemini 3.1 Pro", "gemini", "frontier"),
    "gemini-3.7-flash": ("Gemini 3.7 Flash", "gemini", "september"),
    "gpt-5.6-sol": ("Sol high", "gpt", "frontier"),
    "gpt-5-nano": ("GPT-5 Nano", "gpt", "september"),
}
ARM_ORDER = ["Opus 5", "Sonnet 4.5", "Gemini 3.1 Pro", "Gemini 3.7 Flash", "Sol high", "GPT-5 Nano"]
KEYWORDS = {
    "half or 50%": r"\b50\s?%|\bhalf\b|\b50 percent",
    "baseline/moderate": r"baseline|moderate",
    "declining trust": r"declin|decreas|reduced trust|less trust|lower(ed)? trust|drop",
    "mentions noise": r"noise|noisy",
    "end-game": r"final round|last round|end of the game|near the end|fewer rounds|future incentive|endgame|end-game",
    "all in / full amount": r"all in|full amount|entire|everything|maximi[sz]e",
    "create value / mutual": r"creat\w* value|both come out|mutual|both benefit|joint|total value|pie",
}


def finals(root: Path, keep_dirs=None):
    for p in sorted(root.rglob("*.json")):
        if p.name.endswith(NON_FINAL) or "receipt" in p.name or "worker_logs" in p.parts or "quarantine" in p.parts:
            continue
        if keep_dirs is not None and p.parent.name not in keep_dirs:
            continue
        yield p


def audited_frontier_finals(frontier_root: Path):
    receipts = sorted(frontier_root.glob("*_receipt.json"))
    if not receipts:
        raise RuntimeError(f"no launcher receipts under {frontier_root}")
    audited = {f["sha256"] for r in receipts for f in json.loads(r.read_text())["finals"]}
    for p in finals(frontier_root):
        if hashlib.sha256(p.read_bytes()).hexdigest() in audited:
            yield p


def prose_of(content: str) -> str:
    return re.sub(r"\{[^{}]*\}", "", content or "").strip()


def load(data_root: Path):
    frontier_root = data_root / "json/noise_experiments/frontier_rerun_20260918"
    september_root = data_root / "json/noise_experiments/negative_only_crossmodel_reasoning_rerun_20260909"
    paths = list(audited_frontier_finals(frontier_root)) + list(finals(september_root, NO_DEFECTOR_PARAMS))
    decisions, runs, calls = [], [], []
    for p in paths:
        d = json.loads(p.read_text())
        m = d["run_metadata"]
        plan = m["llm_request"]
        if plan["provider_model"] not in ARM:
            continue
        arm, fam, src = ARM[plan["provider_model"]]
        if plan["provider_model"] == "gpt-5.6-sol" and (plan.get("parameters") or {}).get("reasoning_effort") != "high":
            continue  # the Sol-none smoke run is not part of any comparison
        n = int(m["num_agents"])
        order = "_".join(d["task_order"])
        rep = m.get("replicate_id")
        hist = d["conversation_history"]
        if len(hist) != 10:
            raise RuntimeError(f"{p}: expected ten rounds, found {len(hist)}")
        sends = []
        for h in hist:
            for dy in h["dyads"]:
                sends.append(dy["sent"])
                decisions.append(dict(
                    arm=arm, fam=fam, src=src, n=n, order=order, rep=rep, round=h["round"],
                    investor=dy["investor"], trustee=dy["trustee"], sent=dy["sent"],
                    sent_comm=dy["sent_communicated"], received=dy["received"],
                    received_comm=dy["received_communicated"], returned=dy["returned"],
                    returned_comm=dy["returned_communicated"],
                    ret_ratio=dy["returned"] / dy["received"] if dy["received"] > 0 else np.nan,
                    ret_ratio_comm=(dy["returned_communicated"] / dy["received_communicated"]
                                    if dy["received_communicated"] > 0 else np.nan),
                    investor_payoff_comm=dy["investor_payoff_communicated"], path=str(p)))
        mean_send = float(np.mean(sends))
        last3 = float(np.mean([dy["sent"] for h in hist[-3:] for dy in h["dyads"]]))
        runs.append(dict(arm=arm, fam=fam, src=src, n=n, order=order, rep=rep,
                         mean_resources=float(np.mean(list(hist[-1]["balances"].values()))),
                         identity=25 + 10 * mean_send, mean_send=mean_send, last3_send=last3,
                         collapsed=last3 < 0.5, path=str(p)))
        for a in d["agents"].values():
            for ih in a["interaction_history"]:
                md = ih["metadata"]
                if md.get("task") != "game":
                    continue
                r = ih["response"]
                c = r.get("content") or ""
                u = r.get("usage") or {}
                calls.append(dict(arm=arm, fam=fam, src=src, n=n, order=order, round=md["round"], role=md["role"],
                                  prose_chars=len(prose_of(c)), has_prose=len(prose_of(c)) > 15,
                                  reasoning_tokens=u.get("reasoning_tokens"), output_tokens=u.get("output_tokens"),
                                  content=c))
    return pd.DataFrame(decisions), pd.DataFrame(runs), pd.DataFrame(calls)


def md(df: pd.DataFrame, title: str, floatfmt=".2f") -> str:
    return f"\n### {title}\n\n" + df.to_markdown(floatfmt=floatfmt) + "\n"


def order_arms(df: pd.DataFrame, level="arm"):
    idx = df.index if level in (df.index.names or []) else None
    if idx is not None:
        key = [ARM_ORDER.index(a) if a in ARM_ORDER else 99 for a in df.index.get_level_values(level)]
        return df.iloc[np.argsort(key, kind="stable")]
    return df


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data-root", type=Path, default=ROOT / "data")
    ap.add_argument("--out", type=Path, default=ROOT / "docs/figures/frontier_rerun_20260918/gap_decomposition")
    args = ap.parse_args()
    dec, runs, calls = load(args.data_root)
    args.out.mkdir(parents=True, exist_ok=True)
    out = [f"# Frontier gap decomposition ({len(runs)} runs)\n",
           "Generated by `scripts/analyze_frontier_gap.py`. Means are over runs unless stated.\n"]

    # 1. accounting identity
    gap = (runs.mean_resources - runs.identity).abs().max()
    out.append(f"\n### 1. Accounting identity\n\nmax |mean final resources - (25 + 10 x mean send)| over {len(runs)} runs = {gap:.1e}. "
               "Returns only move resources between the two players of a dyad; the population mean is set by sending alone.\n")

    # 2. mean send per run
    t = (runs.groupby(["fam", "n", "order", "arm"])
         .agg(mean_send=("mean_send", "mean"), sd=("mean_send", "std"), last3=("last3_send", "mean"),
              collapsed_runs=("collapsed", "sum"), runs=("rep", "count")))
    out.append(md(t, "2. Mean send per run (endowment 5), by family x size x task order; collapsed = last-3-round mean send < 0.5"))

    # 3. round by round, game only
    t = dec[dec.order == "game"].groupby(["fam", "n", "arm", "round"]).sent.mean().unstack("round")
    out.append(md(t, "3. Round-by-round mean send, game-only"))
    t = dec[dec.order != "game"].groupby(["fam", "order", "n", "arm", "round"]).sent.mean().unstack("round")
    out.append(md(t, "3b. Round-by-round mean send, two-task orders"))

    # 4. round-1 distributions
    t = dec[(dec["round"] == 1) & (dec.order != "myth_game")].groupby("arm").sent.value_counts().unstack(fill_value=0)
    out.append(md(order_arms(t), "4. Round-1 send counts, game-first orders (dyads + populations, 50 decisions per arm)", ".0f"))
    t = dec[(dec["round"] == 1) & (dec.order == "myth_game")].groupby("arm").sent.value_counts().unstack(fill_value=0)
    out.append(md(order_arms(t), "4b. Round-1 send counts, myth-first (25 decisions per arm)", ".0f"))

    # 5. return ratios
    d = dec.dropna(subset=["ret_ratio"])
    t = d.groupby(["fam", "arm"]).ret_ratio.agg(mean="mean", sd="std", decisions="count",
                                                 fair_or_better=lambda s: (s >= 0.499).mean(),
                                                 investor_loses=lambda s: (s < 1 / 3).mean())
    out.append(md(t, "5. Return ratio (returned / received, actual amounts); fair = at least half returned; investor loses = under a third returned", ".3f"))
    t = d[d.order == "game"].groupby(["fam", "arm", "round"]).ret_ratio.mean().unstack("round")
    out.append(md(t, "5b. Return ratio by round, game-only"))

    # 6. next send after fair vs loss-making communicated return
    rows = []
    for (_, inv), g in dec.sort_values("round").groupby(["path", "investor"]):
        prev = None
        for _, r in g.iterrows():
            if prev is not None:
                rows.append(dict(arm=r.arm, order=r.order, n=r.n, sent=r.sent, prev_sent=prev.sent,
                                 prev_rr_comm=prev.ret_ratio_comm, profited=prev.investor_payoff_comm > 5))
            prev = r
    rec = pd.DataFrame(rows)
    rec["prev_bin"] = pd.cut(rec.prev_rr_comm, [-0.01, 1 / 3, 0.45, 0.55, 2],
                             labels=["under 1/3 (loss)", "1/3 to .45", ".45 to .55 (fair)", "over .55"])
    t = rec.groupby(["arm", "prev_bin"], observed=True).sent.agg(["mean", "count"]).unstack("prev_bin")
    out.append(md(order_arms(t), "6. Next send as investor, by the communicated return ratio this agent last received (all orders)"))
    t = rec[(rec.order == "game") & (rec.n == 2)].groupby(["arm", "prev_bin"], observed=True).sent.agg(["mean", "count"]).unstack("prev_bin")
    out.append(md(order_arms(t), "6b. Same, game-only dyads"))
    rec["dsend"] = rec.sent - rec.prev_sent
    t = rec[rec.order == "game"].groupby(["arm", "profited"]).dsend.agg(["mean", "count"]).unstack("profited")
    out.append(md(order_arms(t), "6c. Change in send after the investor's last (communicated) payoff was below 5 (False) or above 5 (True), game-only"))
    rec["loss_seen"] = rec.prev_rr_comm < 1 / 3
    t = rec.groupby(["arm", "loss_seen"]).dsend.agg(["mean", "count"]).unstack("loss_seen")
    out.append(md(order_arms(t), "6d. Change in send after the communicated return ratio was under a third (True: the round looked like a loss) or not (False), all orders"))

    # 7. dyads: own send vs partner's send seen last round
    rows = []
    for _, g in dec[dec.n == 2].sort_values(["path", "round"]).groupby("path"):
        g = g.reset_index(drop=True)
        for i in range(1, len(g)):
            prev, cur = g.loc[i - 1], g.loc[i]
            if prev.trustee != cur.investor:
                continue
            rows.append(dict(arm=cur.arm, order=cur.order, own=cur.sent, saw=prev.sent_comm, partner_actual=prev.sent))
    lf = pd.DataFrame(rows)
    lf["own_minus_seen"] = lf.own - lf.saw
    lf["own_minus_actual"] = lf.own - lf.partner_actual
    t = lf.groupby(["arm", "order"]).apply(lambda g: pd.Series(dict(
        own_minus_seen=g.own_minus_seen.mean(), own_minus_partner_actual=g.own_minus_actual.mean(),
        slope_own_on_seen=np.polyfit(g.saw, g.own, 1)[0] if g.saw.std() > 0 else np.nan,
        corr=g.own.corr(g.saw) if g.saw.std() > 0 and g.own.std() > 0 else np.nan, n=len(g))))
    out.append(md(order_arms(t), "7. Dyads: own send vs the partner's send this agent saw last round (communicated) and the partner's actual send"))
    g = lf[lf.order == "game"].copy()
    g["seen_bin"] = pd.cut(g.saw, [-0.1, 1, 2, 3, 4, 5.1], labels=["0-1", "1-2", "2-3", "3-4", "4-5"])
    t = g.groupby(["arm", "seen_bin"], observed=True).own.agg(["mean", "count"]).unstack("seen_bin")
    out.append(md(order_arms(t), "7b. Game-only dyads: own send by what the partner was seen to send"))
    noise_seen = (dec.sent_comm - dec.sent)[dec.sent > 0].mean()
    out.append(f"\nMean communicated-minus-actual send (the noise a receiver sees): {noise_seen:.2f}; "
               f"return: {(dec.returned_comm - dec.returned)[dec.returned > 0].mean():.2f}.\n")

    # 8. reasoning tokens and prose
    t = calls.groupby(["fam", "arm"]).agg(calls=("content", "count"), share_with_prose=("has_prose", "mean"),
                                          prose_chars=("prose_chars", "mean"), reasoning_tokens_mean=("reasoning_tokens", "mean"),
                                          reasoning_tokens_median=("reasoning_tokens", "median"), output_tokens=("output_tokens", "mean"))
    out.append(md(t, "8. Game calls: visible prose beyond the JSON, and hidden reasoning tokens per call"))

    # 9. keywords in Claude visible justifications, game-only dyads
    c = calls[(calls.fam == "claude") & (calls.order == "game") & (calls.n == 2) & calls.has_prose].copy()
    for k, pat in KEYWORDS.items():
        c[k] = c.content.map(lambda s: bool(re.search(pat, prose_of(s), re.I)))
    t = c.groupby(["arm", "role"])[list(KEYWORDS)].mean().T
    counts = c.groupby(["arm", "role"]).size()
    out.append(md(t, "9. Share of visible justifications containing each theme, Claude game-only dyads (calls with prose: "
                  + ", ".join(f"{a}/{r} {n}" for (a, r), n in counts.items()) + ")"))

    text = "\n".join(out)
    (args.out / "gap_decomposition.md").write_text(text)
    runs.drop(columns=["path"]).to_csv(args.out / "runs.csv", index=False)
    dec.drop(columns=["path"]).to_csv(args.out / "decisions.csv", index=False)
    print(text)
    print(f"\nwrote {args.out}/gap_decomposition.md, runs.csv, decisions.csv", file=sys.stderr)


if __name__ == "__main__":
    main()

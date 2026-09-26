#!/usr/bin/env python3
"""Myth and decision tables for the September linguistic analysis.

One loader shared by every linguistic analysis of the September informed
negative-only runs: the homogeneous controls (negative_only_crossmodel_
reasoning_rerun_20260909) and the mixed-model dyads and populations.

The run list is taken from the validated tables behind the mixed-model figures,
not from a directory glob. The 20260909 folders also hold defector variants in
sibling subfolders; the figure tables list only the no-defector finals
(99 dyads, 135 populations), so reading their `path` column keeps the inclusion
rule identical to Figures 7 and 8.

Outputs (data/analysis/linguistic_20260923/, gitignored):
  myths.csv      one row per myth: run, size, composition, task order, round,
                 author, author family, text, and the myth the author was shown
                 before writing it (from the run's own `myth_exposures` record)
  decisions.csv  one row per agent per round: role, partner, partner family,
                 amount sent / return proportion, and a 0-1 cooperation score
                 (sent / 5 for senders, returned / received for receivers)

Run from the repo root (or pass --data-root to a checkout that holds data/json):
  python3 analyses/linguistic_corpus.py
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RUN_TABLES = {
    2: ROOT / "docs/figures/mixed_model_dyads_20260917/decisions.csv",
    8: ROOT / "docs/figures/mixed_model_populations_20260918/games.csv",
}
OUT = ROOT / "data/analysis/linguistic_20260923"
ENDOWMENT = 5.0
FAMILY_OF = {"claude-sonnet-4.5": "Sonnet", "gpt-5-nano": "GPT", "gemini-3.7-flash": "Gemini"}
FAMILY_ORDER = ["Sonnet", "Gemini", "GPT"]  # the figure labels: Sonnet+GPT, Sonnet+Gemini, Gemini+GPT


def family(model: str) -> str:
    for key, fam in FAMILY_OF.items():
        if key in model:
            return fam
    raise ValueError(f"unknown model {model!r}")


def agent_families(run: dict) -> dict[str, str]:
    meta = run["run_metadata"]
    per_agent = (meta.get("llm_request") or {}).get("agents")
    if per_agent:
        return {a: family(v["model"]) for a, v in per_agent.items()}
    return {a: family(meta["model"]) for a in run["agents"]}


def composition_label(families: dict[str, str]) -> str:
    counts = pd.Series(list(families.values())).value_counts()
    if len(counts) == 1:
        return f"{len(families)} {counts.index[0]}" if len(families) > 2 else f"{counts.index[0]}+{counts.index[0]}"
    if len(families) == 2:
        return "+".join(sorted(families.values(), key=FAMILY_ORDER.index))
    return " + ".join(f"{n} {f}" for f, n in counts.sort_values().items())


def run_list(size: int, data_root: Path) -> list[dict]:
    table = pd.read_csv(RUN_TABLES[size])
    runs = table.drop_duplicates("path")[["path", "task_order", "replicate_id"]]
    runs = runs[runs["task_order"] != "game"]  # game-only runs have no myths
    return [
        {"path": p, "abs_path": data_root / p, "task_order": t, "replicate_id": int(r), "size": size}
        for p, t, r in runs.itertuples(index=False)
    ]


def load(data_root: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    myth_rows, decision_rows = [], []
    for size in (2, 8):
        for spec in run_list(size, data_root):
            run = json.loads(Path(spec["abs_path"]).read_text())
            fams = agent_families(run)
            comp = composition_label(fams)
            mixed = len(set(fams.values())) > 1
            run_id = Path(spec["path"]).stem
            base = {"run_id": run_id, "path": spec["path"], "size": size, "composition": comp, "mixed": mixed,
                    "task_order": spec["task_order"], "replicate_id": spec["replicate_id"]}
            for entry in run["conversation_history"]:
                rnd = int(entry["round"])
                partner = {}
                for p in entry["pairings"]:
                    partner[p["investor"]] = p["trustee"]
                    partner[p["trustee"]] = p["investor"]
                exposures = entry.get("myth_exposures") or {}
                for agent, text in (entry.get("myths") or {}).items():
                    exp = exposures.get(agent) or {}
                    src = exp.get("original_author_id")
                    myth_rows.append({**base, "round": rnd, "agent": agent, "family": fams[agent],
                                      "partner_this_round": partner.get(agent),
                                      "exposed_author": src, "exposed_family": fams.get(src) if src else None,
                                      "exposed_round": exp.get("source_round"),
                                      "text": text, "n_words": len(str(text).split())})
                for d in entry.get("dyads") or []:
                    inv, tru = d["investor"], d["trustee"]
                    sent, received, returned = float(d["sent"]), float(d["received"]), float(d["returned"])
                    ret_prop = returned / received if received > 0 else float("nan")
                    for agent, role, other in ((inv, "investor", tru), (tru, "trustee", inv)):
                        decision_rows.append({
                            **base, "round": rnd, "agent": agent, "family": fams[agent], "role": role,
                            "partner": other, "partner_family": fams[other],
                            "sent": sent, "received": received, "returned": returned,
                            "return_proportion": ret_prop,
                            "coop": sent / ENDOWMENT if role == "investor" else ret_prop,
                        })
    return pd.DataFrame(myth_rows), pd.DataFrame(decision_rows)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-root", type=Path, default=ROOT, help="checkout whose data/json holds the runs")
    args = ap.parse_args()
    myths, decisions = load(args.data_root)
    OUT.mkdir(parents=True, exist_ok=True)
    myths.to_csv(OUT / "myths.csv", index=False)
    decisions.to_csv(OUT / "decisions.csv", index=False)
    print(f"myths: {len(myths)} from {myths.run_id.nunique()} runs -> {OUT / 'myths.csv'}")
    print(myths.groupby(["size", "mixed", "task_order"]).run_id.nunique().to_string())
    print(f"decisions: {len(decisions)} rows -> {OUT / 'decisions.csv'}")
    missing = myths[(myths["round"] > 1) & myths["exposed_author"].isna()]
    print(f"round>1 myths without an exposure record: {len(missing)}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Validation of the myth-moral labels: judge agreement and a blinded human sample.

1. Judge agreement on every September myth: GLM-5.2 (primary) against
   DeepSeek V4 Flash (second judge, a family absent from the runs), with raw
   agreement, Cohen's kappa and the confusion matrix, overall and per author
   family.
2. A blinded sample for human coding: up to 30 myths per GLM label, spread over
   author families and settings, shuffled, with neither judge's label or any run
   information on the sheet. The key sits in a separate file.
3. Scoring (--score): once a coder fills the `human_label` column, precision
   and recall of each judge against the human per label, and Cohen's kappa. A
   label whose GLM precision is below 80% should not carry a headline claim
   (the threshold used in the earlier meme-transmission validation).

Outputs: docs/figures/linguistic_analysis_20260923/moral_labels.csv (both
judges' labels and the one-sentence moral for every myth), and
docs/figures/linguistic_analysis_20260923/validation/
  judge_agreement.csv, judge_confusion.csv
  human_coding_sheet.csv   (give this to the coder; blinded)
  (key: data/analysis/linguistic_20260923/human_coding_key.csv, gitignored)
  CODING_INSTRUCTIONS.md

  python3 analyses/moral_validation.py
  python3 analyses/moral_validation.py --score docs/figures/linguistic_analysis_20260923/validation/human_coding_sheet.csv
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/analysis/linguistic_20260923"
OUT = ROOT / "docs/figures/linguistic_analysis_20260923/validation"
LABELS = ["be generous", "be fair", "be cautious"]
PRIMARY = "moral_labels_z-ai__glm-5.2.csv"
SECOND = "moral_labels_deepseek__deepseek-v4-flash.csv"
KEY = ["run_id", "round", "agent"]
PER_LABEL = 30
# the key stays out of git so a coder with repo access stays blind
KEY_PATH = DATA / "human_coding_key.csv"


def kappa(a: pd.Series, b: pd.Series) -> float:
    from sklearn.metrics import cohen_kappa_score
    m = a.notna() & b.notna()
    return float(cohen_kappa_score(a[m], b[m], labels=LABELS)) if m.sum() else np.nan


def agreement(both: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    groups = [("all myths", both)] + [(f"author {f}", g) for f, g in both.groupby("family")] + \
             [(f"{s}-agent {'mixed' if m else 'homogeneous'}", g) for (s, m), g in both.groupby(["size", "mixed"])]
    for name, g in groups:
        ok = g["label_glm"].notna() & g["label_second"].notna()
        rows.append({"subset": name, "n": int(ok.sum()),
                     "raw_agreement": float((g.loc[ok, "label_glm"] == g.loc[ok, "label_second"]).mean()),
                     "cohen_kappa": kappa(g["label_glm"], g["label_second"]),
                     **{f"glm_share_{l.split()[1]}": float((g.loc[ok, "label_glm"] == l).mean()) for l in LABELS},
                     **{f"second_share_{l.split()[1]}": float((g.loc[ok, "label_second"] == l).mean()) for l in LABELS}})
    confusion = pd.crosstab(both["label_glm"], both["label_second"], rownames=["GLM-5.2"],
                            colnames=["DeepSeek V4 Flash"]).reindex(index=LABELS, columns=LABELS, fill_value=0)
    return pd.DataFrame(rows), confusion


def sample(both: pd.DataFrame, myths: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    pool = both.dropna(subset=["label_glm"]).merge(myths[KEY + ["text"]], on=KEY)
    picks = []
    for lab in LABELS:
        g = pool[pool["label_glm"] == lab]
        if len(g) <= PER_LABEL:
            picks.append(g)
            continue
        # spread over author family x setting, then fill at random
        strata = g.groupby(["family", "size", "mixed"])
        per = max(1, PER_LABEL // strata.ngroups)
        chosen = pd.concat([s.sample(min(per, len(s)), random_state=int(rng.integers(1e9))) for _, s in strata])
        rest = g.drop(chosen.index)
        if len(chosen) < PER_LABEL:
            chosen = pd.concat([chosen, rest.sample(PER_LABEL - len(chosen), random_state=int(rng.integers(1e9)))])
        picks.append(chosen.head(PER_LABEL))
    s = pd.concat(picks).sample(frac=1, random_state=int(rng.integers(1e9))).reset_index(drop=True)
    s.insert(0, "item_id", [f"M{k:03d}" for k in range(1, len(s) + 1)])
    return s


INSTRUCTIONS = """# Coding the moral of a myth

You will read {n} short myths written by AI agents between rounds of a repeated
trust game (a sender gets $5 and may send some of it; the amount is tripled;
the receiver chooses how much to send back). For each myth, write in the
`human_label` column the behavioural rule the myth endorses:

- `be generous`: give or return a lot as a default, whatever the partner did.
- `be fair`: match the partner, rewarding generosity and answering selfishness in kind.
- `be cautious`: protect yourself, start small, and extend trust only after proof.

The full rubric, with examples and tie-breaking rules, is Arabella Sinclair's
`arabella_analyses/data/rubrics/3moral_rubric.txt`. Classify the rule the myth
presents as wise, not the actions of a single character. Always pick one label.
Use `notes` for anything unclear. The answer key is not in the repository.

When done, run:
`python3 analyses/moral_validation.py --score <path to your filled sheet>`
"""


def score(path: Path) -> None:
    filled = pd.read_csv(path)
    key = pd.read_csv(KEY_PATH)
    d = filled[["item_id", "human_label"]].merge(key, on="item_id")
    d["human_label"] = d["human_label"].astype(str).str.strip().str.lower()
    d = d[d["human_label"].isin(LABELS)]
    print(f"{len(d)} coded items")
    for judge in ("label_glm", "label_second"):
        print(f"\n{judge}: agreement {np.mean(d[judge] == d['human_label']):.1%}, "
              f"kappa {kappa(d['human_label'], d[judge]):.2f}")
        for lab in LABELS:
            pred, true = d[judge] == lab, d["human_label"] == lab
            prec = (pred & true).sum() / pred.sum() if pred.sum() else np.nan
            rec = (pred & true).sum() / true.sum() if true.sum() else np.nan
            flag = "  <- below 80% precision: no headline claim on this label" if prec < 0.8 else ""
            print(f"  {lab:12s} precision {prec:.0%} (n={pred.sum()})  recall {rec:.0%} (n={true.sum()}){flag}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--score", type=Path)
    ap.add_argument("--seed", type=int, default=20260923)
    args = ap.parse_args()
    if args.score:
        score(args.score)
        return
    OUT.mkdir(parents=True, exist_ok=True)
    myths = pd.read_csv(DATA / "myths.csv")
    glm = pd.read_csv(DATA / PRIMARY)[KEY + ["size", "mixed", "family", "composition", "task_order", "label"]]
    second = pd.read_csv(DATA / SECOND)[KEY + ["label"]]
    both = glm.rename(columns={"label": "label_glm"}).merge(second.rename(columns={"label": "label_second"}),
                                                            on=KEY, how="left")
    summaries = pd.read_csv(DATA / PRIMARY)[KEY + ["summary"]]
    both.merge(summaries, on=KEY).rename(columns={"label_glm": "label_glm_5_2", "label_second": "label_deepseek_v4_flash",
                                                 "summary": "moral_summary_glm_5_2"}).to_csv(
        OUT.parent / "moral_labels.csv", index=False)  # one row per myth, for coauthors
    agree, confusion = agreement(both)
    agree.to_csv(OUT / "judge_agreement.csv", index=False)
    confusion.to_csv(OUT / "judge_confusion.csv")
    print(agree.round(3).to_string(index=False))
    print(confusion.to_string())

    s = sample(both, myths, np.random.default_rng(args.seed))
    s[["item_id", "text"]].assign(human_label="", notes="").to_csv(OUT / "human_coding_sheet.csv", index=False)
    s.drop(columns=["text"]).to_csv(KEY_PATH, index=False)
    (OUT / "CODING_INSTRUCTIONS.md").write_text(INSTRUCTIONS.format(n=len(s)))
    print(f"\nblinded sheet: {len(s)} myths -> {OUT / 'human_coding_sheet.csv'}")
    print(s.groupby(["label_glm", "family"]).size().unstack(fill_value=0).to_string())


if __name__ == "__main__":
    main()

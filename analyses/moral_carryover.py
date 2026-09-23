#!/usr/bin/env python3
"""Myth morals in the September runs: how they change, spread, and carry into play.

Reads the judge labels from analyses/myth_moral_judge.py (Arabella Sinclair's
3-label rubric and one-sentence moral summary, z-ai/glm-5.2) plus the tables
from analyses/linguistic_corpus.py. Rebuilds every measure from her notebook
(arabella_analyses/src/analysis/analysis_morals_gameplay.ipynb) on the
September data, with two corrections: label trends are shares per label, not
an average of generous=3 / fair=2 / cautious=1; and partner distance uses the
full embedding, not a 2-D PCA projection.

A. Label shares per round, by family and setting.
B. Moral-summary measures (all-mpnet-base-v2 embeddings of the one-sentence
   morals): drift from the agent's round-1 moral, stability versus its
   previous moral, uptake (closeness to the moral of the myth it was shown
   minus closeness to an unseen same-family myth's moral, same comparison
   myths as analyses/linguistic_uptake.py), label uptake (same label as the
   shown myth versus an unseen one), and distance between game partners'
   morals per round.
C. Giving gap (|sent/5 - return proportion|) and behaviour by moral label.
D. Carryover. For each decision, OLS with SE clustered by run:
     coop_t ~ own latest moral label + label of the myth shown most recently
              + own most recent cooperation in the same role
   coop is sent / 5 for senders and return proportion for receivers, fitted
   separately, under run + round fixed effects and (main) agent-within-run +
   round fixed effects, which remove each agent's family and disposition.
   Placebo (8-agent investors): the current co-player's own latest label,
   which the investor never saw, controlling for the co-player's family.
   Reverse check: does cooperation in a game predict the label of the myth
   written right after it?

Outputs: docs/figures/linguistic_analysis_20260923/moral_*.{csv,png}.
No API calls; --labels picks the judge file (default GLM-5.2; pass the DeepSeek
file for the robustness rerun).

  python3 analyses/moral_carryover.py [--labels moral_labels_deepseek__deepseek-v4-flash.csv]
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import warnings

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from analyses._shared import configure_matplotlib  # noqa: E402
from analyses.linguistic_uptake import load_myths, null_candidates  # noqa: E402

DATA = ROOT / "data/analysis/linguistic_20260923"
FIGS = ROOT / "docs/figures/linguistic_analysis_20260923"
LABELS = ["be generous", "be fair", "be cautious"]
LABEL_COLORS = {"be generous": "#1b7837", "be fair": "#b8860b", "be cautious": "#b2182b"}
FAMILIES = ["Sonnet", "Gemini", "GPT"]
KEY = ["run_id", "round", "agent"]


def setting_of(size, mixed) -> str:
    return f"{size}-agent {'mixed' if mixed else 'homogeneous'}"


def load(labels_file: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    myths = load_myths()
    lab = pd.read_csv(DATA / labels_file)
    cols = [c for c in ["label", "summary"] if c in lab.columns]
    myths = myths.merge(lab[KEY + cols], on=KEY, how="left")
    if "summary" not in myths:
        myths["summary"] = np.nan
    myths["setting"] = [setting_of(s, m) for s, m in zip(myths["size"], myths["mixed"])]
    dec = pd.read_csv(DATA / "decisions.csv")
    dec["setting"] = [setting_of(s, m) for s, m in zip(dec["size"], dec["mixed"])]
    return myths, dec


# --------------------------------------------------------------------------- A

def label_shares(myths: pd.DataFrame) -> pd.DataFrame:
    d = myths.dropna(subset=["label"])
    counts = d.groupby(["setting", "family", "task_order", "round", "label"]).size().unstack(fill_value=0)
    counts = counts.reindex(columns=LABELS, fill_value=0)
    shares = counts.div(counts.sum(axis=1), axis=0).add_prefix("share_").reset_index()
    shares["n_myths"] = counts.sum(axis=1).to_numpy()
    return shares


def plot_label_shares(myths: pd.DataFrame) -> None:
    import matplotlib.pyplot as plt
    configure_matplotlib()
    d = myths.dropna(subset=["label"])
    settings = ["2-agent homogeneous", "2-agent mixed", "8-agent homogeneous", "8-agent mixed"]
    fig, axes = plt.subplots(len(FAMILIES), len(settings), figsize=(16, 9.5), sharex=True, sharey=True)
    for r, fam in enumerate(FAMILIES):
        for c, st in enumerate(settings):
            ax = axes[r, c]
            sub = d[(d["family"] == fam) & (d["setting"] == st)]
            if sub.empty:
                ax.axis("off")
                continue
            share = pd.crosstab(sub["round"], sub["label"], normalize="index").reindex(columns=LABELS, fill_value=0)
            bottom = np.zeros(len(share))
            for lab in LABELS:
                ax.bar(share.index, share[lab], bottom=bottom, color=LABEL_COLORS[lab], width=0.85,
                       edgecolor="white", linewidth=1, label=lab)
                bottom += share[lab].to_numpy()
            ax.set_title(f"{fam}, {st} (n={len(sub)})", fontsize=9)
            if c == 0:
                ax.set_ylabel("share of myths")
            if r == len(FAMILIES) - 1:
                ax.set_xlabel("round")
    axes[0, 0].legend(fontsize=8, loc="lower left")
    fig.suptitle("What each myth's moral tells players to do, by round (judge: GLM-5.2, Arabella's 3-label rubric)")
    fig.tight_layout()
    fig.savefig(FIGS / "moral_label_shares.png", dpi=200)
    plt.close(fig)


# --------------------------------------------------------------------------- B

def summary_embeddings(myths: pd.DataFrame) -> np.ndarray:
    cache = DATA / "embeddings_moral_summary_mpnet.npy"
    texts = myths["summary"].fillna("").astype(str).tolist()
    if cache.exists():
        emb = np.load(cache)
        if len(emb) == len(texts):
            return emb
    from sentence_transformers import SentenceTransformer
    emb = SentenceTransformer("all-mpnet-base-v2").encode(texts, batch_size=128, normalize_embeddings=True,
                                                          show_progress_bar=False)
    np.save(cache, emb)
    return emb


def summary_measures(myths: pd.DataFrame, emb: np.ndarray) -> tuple[pd.DataFrame, pd.DataFrame]:
    has = myths["summary"].notna().to_numpy()
    idx = {(r, t, a): i for i, (r, t, a) in enumerate(zip(myths["run_id"], myths["round"], myths["agent"]))}
    rows = []
    for (run, agent), g in myths.groupby(["run_id", "agent"]):
        g = g.sort_values("round")
        first = g.index[0]
        prev = None
        for i in g.index:
            if has[i] and has[first]:
                rows.append({"run_id": run, "agent": agent, "round": myths.at[i, "round"],
                             "setting": myths.at[i, "setting"], "family": myths.at[i, "family"],
                             "task_order": myths.at[i, "task_order"],
                             "drift_from_round1": float(emb[i] @ emb[first]),
                             "stability_vs_previous": float(emb[i] @ emb[prev]) if prev is not None and has[prev] else np.nan})
            prev = i
    per_myth = pd.DataFrame(rows)

    cands = null_candidates(myths)
    up = []
    for i, js in cands.items():
        p, nulls = js[0], [j for j in js[1:] if has[j]]
        if not (has[i] and has[p]) or not nulls:
            continue
        lab_i, lab_p = myths.at[i, "label"], myths.at[p, "label"]
        up.append({"run_id": myths.at[i, "run_id"], "setting": myths.at[i, "setting"],
                   "family": myths.at[i, "family"], "parent_family": myths.at[p, "family"],
                   "round": myths.at[i, "round"],
                   "moral_cos_shown": float(emb[i] @ emb[p]), "moral_cos_unseen": float(np.mean(emb[nulls] @ emb[i])),
                   "same_label_shown": float(lab_i == lab_p) if isinstance(lab_i, str) and isinstance(lab_p, str) else np.nan,
                   "same_label_unseen": np.nanmean([float(lab_i == myths.at[j, "label"]) for j in nulls
                                                    if isinstance(myths.at[j, "label"], str)]) if isinstance(lab_i, str) else np.nan})
    uptake = pd.DataFrame(up)
    uptake["moral_cos_excess"] = uptake["moral_cos_shown"] - uptake["moral_cos_unseen"]
    uptake["same_label_excess"] = uptake["same_label_shown"] - uptake["same_label_unseen"]
    return per_myth, uptake


def partner_distance(myths: pd.DataFrame, dec: pd.DataFrame, emb: np.ndarray) -> pd.DataFrame:
    """1 - cosine between game partners' latest morals before their game."""
    idx = {(r, t, a): i for i, (r, t, a) in enumerate(zip(myths["run_id"], myths["round"], myths["agent"]))}
    has = myths["summary"].notna().to_numpy()
    inv = dec[dec["role"] == "investor"]
    rows = []
    for g in inv.itertuples(index=False):
        r = g.round if g.task_order == "myth_game" else g.round - 1
        i, j = idx.get((g.run_id, r, g.agent)), idx.get((g.run_id, r, g.partner))
        if i is None or j is None or not (has[i] and has[j]):
            continue
        rows.append({"run_id": g.run_id, "setting": g.setting, "round": g.round, "task_order": g.task_order,
                     "pair_type": "same family" if g.family == g.partner_family else "cross family",
                     "moral_distance": 1 - float(emb[i] @ emb[j]),
                     "same_label": float(myths.at[i, "label"] == myths.at[j, "label"])})
    return pd.DataFrame(rows)


def run_summary(df: pd.DataFrame, by: list[str], metrics: list[str]) -> pd.DataFrame:
    per_run = df.groupby(by + ["run_id"])[metrics].mean().reset_index()
    rows = []
    for keys, g in per_run.groupby(by):
        keys = keys if isinstance(keys, tuple) else (keys,)
        rec = {**dict(zip(by, keys)), "n_runs": len(g)}
        for m in metrics:
            vals = g[m].dropna()
            rec[f"{m}_mean"], rec[f"{m}_sd"] = vals.mean(), vals.std(ddof=1)
            if m.endswith("_excess") and len(vals) >= 5 and (vals != 0).any():
                rec[f"{m}_p"] = stats.wilcoxon(vals).pvalue
                rec[f"{m}_runs_positive"] = int((vals > 0).sum())
        rows.append(rec)
    return pd.DataFrame(rows)


def plot_summary_measures(per_myth: pd.DataFrame, dist: pd.DataFrame) -> None:
    import matplotlib.pyplot as plt
    configure_matplotlib()
    settings = ["2-agent homogeneous", "2-agent mixed", "8-agent homogeneous", "8-agent mixed"]
    styles = dict(zip(settings, ["-", "--", "-", "--"]))
    widths = dict(zip(settings, [2.2, 2.2, 1.2, 1.2]))
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.4))
    for ax, (col, title, frame, group) in zip(axes, (
            ("drift_from_round1", "Closeness to the agent's own round-1 moral", per_myth, "family"),
            ("stability_vs_previous", "Closeness to the agent's previous moral", per_myth, "family"),
            ("moral_distance", "Distance between game partners' morals", dist, None))):
        if group:
            for fam in FAMILIES:
                for st in settings:
                    s = frame[(frame["family"] == fam) & (frame["setting"] == st)].groupby("round")[col].mean()
                    if len(s):
                        ax.plot(s.index, s.values, ls=styles[st], lw=widths[st], color=
                                {"Sonnet": "#7570b3", "GPT": "#d95f02", "Gemini": "#1b9e77"}[fam],
                                label=f"{fam}, {st}")
        else:
            for st in settings:
                s = frame[frame["setting"] == st].groupby("round")[col].agg(["mean", "std"])
                ax.plot(s.index, s["mean"], ls=styles[st], lw=widths[st], color="#333333" if "2-" in st else "#999999",
                        label=st)
        ax.set_title(title, fontsize=10)
        ax.set_xlabel("round")
        ax.grid(alpha=0.3)
    axes[0].set_ylabel("cosine similarity of one-sentence morals")
    axes[2].set_ylabel("1 - cosine similarity")
    handles, labels = axes[1].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=6, fontsize=7, frameon=False)
    axes[2].legend(fontsize=7)
    fig.suptitle("How morals settle over the run (lines: mean over myths; thick = 2-agent, thin = 8-agent, dashed = mixed)")
    fig.tight_layout(rect=(0, 0.1, 1, 1))
    fig.savefig(FIGS / "moral_summary_drift_stability_distance.png", dpi=200)
    plt.close(fig)


# --------------------------------------------------------------------------- C + D

def decision_table(myths: pd.DataFrame, dec: pd.DataFrame) -> pd.DataFrame:
    lab = {(r, t, a): l for r, t, a, l in zip(myths["run_id"], myths["round"], myths["agent"], myths["label"])}
    shown = {(r, t, a): (ea, er) for r, t, a, ea, er in
             zip(myths["run_id"], myths["round"], myths["agent"], myths["exposed_author"], myths["exposed_round"])}
    d = dec.sort_values(["run_id", "agent", "round"]).copy()
    own, shown_lab, shown_auth, cop_lab, after_lab = [], [], [], [], []
    for g in d.itertuples(index=False):
        r_before = g.round if g.task_order == "myth_game" else g.round - 1
        r_after = g.round + 1 if g.task_order == "myth_game" else g.round
        own.append(lab.get((g.run_id, r_before, g.agent)))
        ea = shown.get((g.run_id, r_before, g.agent))
        shown_lab.append(lab.get((g.run_id, int(ea[1]), ea[0])) if ea and isinstance(ea[0], str) else None)
        shown_auth.append(ea[0] if ea and isinstance(ea[0], str) else None)
        cop_lab.append(lab.get((g.run_id, r_before, g.partner)))
        after_lab.append(lab.get((g.run_id, r_after, g.agent)))
    d["own_label"], d["shown_label"], d["coplayer_label"], d["label_after"] = own, shown_lab, cop_lab, after_lab
    d["shown_author"] = shown_auth
    d["coop_lag_same_role"] = d.groupby(["run_id", "agent", "role"])["coop"].shift(1)
    d["giving_gap"] = np.nan
    inv = d["role"] == "investor"
    d.loc[inv, "giving_gap"] = (d.loc[inv, "sent"] / 5 - d.loc[inv, "return_proportion"]).abs()
    return d


def carryover_models(d: pd.DataFrame) -> pd.DataFrame:
    """Carryover regressions under two fixed-effect choices.

    fe = "run":   run + round fixed effects (families differ inside a mixed run,
                  so a label can stand in for the author's family).
    fe = "agent": agent-within-run + round fixed effects: does an agent
                  cooperate more in the rounds when its own moral is more
                  generous than usual? This is the carryover question proper.
    The placebo adds the co-player's family, so a co-player label cannot act
    as a family marker."""
    import statsmodels.formula.api as smf
    rows = []
    specs = {
        "own + shown label, own lag": "coop ~ C(own_label, Treatment('be fair')) + C(shown_label, Treatment('be fair')) + coop_lag_same_role",
        "own + shown label, no lag": "coop ~ C(own_label, Treatment('be fair')) + C(shown_label, Treatment('be fair'))",
        "placebo: co-player's unseen label": "coop ~ C(coplayer_label, Treatment('be fair')) + C(own_label, Treatment('be fair')) + coop_lag_same_role + C(partner_family)",
    }
    fes = {"run": " + C(run_id) + C(round)", "agent": " + C(run_agent) + C(round)"}
    d = d.assign(run_agent=d["run_id"] + "|" + d["agent"])
    groups = [(st, g) for st, g in d.groupby("setting")] + [("all settings", d)]
    for fe, fe_terms in fes.items():
        for st, g in groups:
            for role in ("investor", "trustee"):
                base = g[g["role"] == role]
                for name, formula in specs.items():
                    if name.startswith("placebo") and not (role == "investor" and ("8-agent" in st)):
                        continue  # only 8-agent investors choose before seeing anything from an unshown co-player
                    cols = ["coop", "own_label", "run_id", "run_agent", "round", "partner_family"] + \
                           (["shown_label"] if "shown_label" in formula else []) + \
                           (["coplayer_label"] if "coplayer_label" in formula else []) + \
                           (["coop_lag_same_role"] if "lag" in formula else [])
                    sub = base[cols].dropna()
                    if name.startswith("placebo"):
                        # drop cases where the co-player's myth is the one the investor was shown
                        sub = sub[base.loc[sub.index, "partner"] != base.loc[sub.index, "shown_author"]]
                    if sub["run_id"].nunique() < 8:
                        continue
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        try:
                            fit = smf.ols(formula + fe_terms, data=sub).fit(
                                cov_type="cluster", cov_kwds={"groups": pd.factorize(sub["run_id"])[0]})
                        except Exception as err:  # noqa: BLE001 - e.g. a label level absent in a subgroup
                            rows.append({"fe": fe, "setting": st, "role": role, "model": name, "error": str(err)})
                            continue
                    for term in fit.params.index:
                        if "label" not in term and term != "coop_lag_same_role":
                            continue
                        var = term.split(",")[0].replace("C(", "") if "label" in term else term
                        level = term.split("[T.")[-1].rstrip("]") if "[T." in term else ""
                        ci = fit.conf_int().loc[term]
                        rows.append({"fe": fe, "setting": st, "role": role, "model": name, "predictor": var,
                                     "level": level, "coef": fit.params[term], "ci_low": ci[0], "ci_high": ci[1],
                                     "p": fit.pvalues[term], "n_decisions": int(fit.nobs),
                                     "n_runs": sub["run_id"].nunique()})
    return pd.DataFrame(rows)


def reverse_models(d: pd.DataFrame) -> pd.DataFrame:
    """Does a generous game predict a 'be generous' myth right after it?"""
    import statsmodels.formula.api as smf
    rows = []
    for st, g in list(d.groupby("setting")) + [("all settings", d)]:
        for role in ("investor", "trustee"):
            sub = g[(g["role"] == role)][["coop", "label_after", "own_label", "run_id", "round"]].dropna()
            sub = sub.assign(generous_after=(sub["label_after"] == "be generous").astype(float),
                             generous_before=(sub["own_label"] == "be generous").astype(float))
            if sub["run_id"].nunique() < 8:
                continue
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                fit = smf.ols("generous_after ~ coop + generous_before + C(run_id) + C(round)", data=sub).fit(
                    cov_type="cluster", cov_kwds={"groups": pd.factorize(sub["run_id"])[0]})
            ci = fit.conf_int().loc["coop"]
            rows.append({"setting": st, "role": role, "coef_coop_on_generous_after": fit.params["coop"],
                         "ci_low": ci[0], "ci_high": ci[1], "p": fit.pvalues["coop"], "n": int(fit.nobs)})
    return pd.DataFrame(rows)


def plot_carryover(models: pd.DataFrame) -> None:
    import matplotlib.pyplot as plt
    configure_matplotlib()
    m = models[(models["fe"] == "agent") & (models["model"] == "own + shown label, own lag")
               & models["level"].isin(["be generous", "be cautious"])]
    settings = ["2-agent homogeneous", "2-agent mixed", "8-agent homogeneous", "8-agent mixed", "all settings"]
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8), sharey=True)
    for ax, role, xlabel in ((axes[0], "investor", "change in amount sent / 5"),
                             (axes[1], "trustee", "change in return proportion")):
        k = 0
        ticks = []
        for st in settings:
            for pred, name in (("own_label", "own myth"), ("shown_label", "myth shown")):
                for level, color, dy in (("be generous", LABEL_COLORS["be generous"], -0.15),
                                         ("be cautious", LABEL_COLORS["be cautious"], 0.15)):
                    r = m[(m["setting"] == st) & (m["role"] == role) & (m["predictor"] == pred) & (m["level"] == level)]
                    if r.empty:
                        continue
                    r = r.iloc[0]
                    ax.errorbar(r["coef"], k + dy, xerr=[[r["coef"] - r["ci_low"]], [r["ci_high"] - r["coef"]]],
                                fmt="o", color=color, capsize=3,
                                label=f"'{level}' vs 'be fair'" if k == 0 else None)
                ticks.append(f"{st}: {name}")
                k += 1
        ax.axvline(0, color="#666666", lw=1)
        ax.set_xlabel(xlabel + "\n(agent-within-run + round fixed effects, own last move in that role; 95% CI)")
        ax.set_title("Senders" if role == "investor" else "Receivers")
        ax.grid(axis="x", alpha=0.3)
        ax.set_yticks(range(len(ticks)), ticks, fontsize=8)
    axes[0].invert_yaxis()
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=2, fontsize=9, frameon=False)
    fig.suptitle("Does a myth's moral predict the next move beyond the player's own last move?")
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(FIGS / "moral_carryover.png", dpi=200)
    plt.close(fig)


def plot_behaviour_by_label(d: pd.DataFrame) -> None:
    import matplotlib.pyplot as plt
    configure_matplotlib()
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.2))
    panels = (("investor", "coop", "amount sent / 5"), ("trustee", "coop", "return proportion"),
              ("investor", "giving_gap", "giving gap |sent/5 - return proportion|"))
    for ax, (role, col, title) in zip(axes, panels):
        sub = d[(d["role"] == role)].dropna(subset=["own_label", col])
        for lab in LABELS:
            s = sub[sub["own_label"] == lab].groupby("round")[col].mean()
            ax.plot(s.index, s.values, color=LABEL_COLORS[lab], lw=2, marker="o", ms=3, label=f"own myth: {lab}")
        ax.set_title(title, fontsize=10)
        ax.set_xlabel("round")
        ax.grid(alpha=0.3)
    axes[0].legend(fontsize=8)
    fig.suptitle("Behaviour by the moral of the player's latest myth (all September myth runs pooled; descriptive)")
    fig.tight_layout()
    fig.savefig(FIGS / "moral_behaviour_by_label.png", dpi=200)
    plt.close(fig)


# --------------------------------------------------------------------------- main

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--labels", default="moral_labels_z-ai__glm-5.2.csv")
    args = ap.parse_args()
    tag = "" if "glm" in args.labels else "_" + args.labels.replace("moral_labels_", "").replace(".csv", "")
    FIGS.mkdir(parents=True, exist_ok=True)
    myths, dec = load(args.labels)
    print(f"labelled myths: {myths['label'].notna().sum()} / {len(myths)}")
    print(myths.groupby(["setting", "family"])["label"].value_counts(normalize=True).unstack().round(3).to_string())

    label_shares(myths).to_csv(FIGS / f"moral_label_shares{tag}.csv", index=False)
    d = decision_table(myths, dec)
    models = carryover_models(d)
    models.to_csv(FIGS / f"moral_carryover_models{tag}.csv", index=False)
    rev = reverse_models(d)
    rev.to_csv(FIGS / f"moral_reverse_models{tag}.csv", index=False)
    show = ["setting", "role", "model", "predictor", "level", "coef", "ci_low", "ci_high", "p", "n_decisions"]
    key = models[models["predictor"].astype(str).str.contains("label") & (
        (models["setting"] == "all settings") | models["model"].str.startswith("placebo"))]
    print(key[["fe"] + show].round(4).to_string(index=False))
    print(rev.round(4).to_string(index=False))
    if tag:  # robustness rerun: carryover tables only
        return

    plot_label_shares(myths)
    plot_carryover(models)
    plot_behaviour_by_label(d)
    gap = d[d["role"] == "investor"].groupby(["setting", "own_label"])["giving_gap"].agg(["mean", "std", "count"])
    gap.reset_index().to_csv(FIGS / "moral_giving_gap_by_label.csv", index=False)

    if myths["summary"].notna().any():
        emb = summary_embeddings(myths)
        per_myth, uptake = summary_measures(myths, emb)
        dist = partner_distance(myths, dec, emb)
        per_myth.to_csv(DATA / "moral_summary_per_myth.csv", index=False)
        uptake.to_csv(DATA / "moral_uptake_children.csv", index=False)
        dist.to_csv(DATA / "moral_partner_distance.csv", index=False)
        run_summary(per_myth, ["setting", "family"], ["drift_from_round1", "stability_vs_previous"]).to_csv(
            FIGS / "moral_drift_stability.csv", index=False)
        up = run_summary(uptake.assign(exposure=np.where(uptake["family"] == uptake["parent_family"],
                                                         "same family", "other family")),
                         ["setting", "exposure"], ["moral_cos_shown", "moral_cos_unseen", "moral_cos_excess",
                                                   "same_label_shown", "same_label_unseen", "same_label_excess"])
        up.to_csv(FIGS / "moral_uptake.csv", index=False)
        run_summary(dist, ["setting", "pair_type"], ["moral_distance", "same_label"]).to_csv(
            FIGS / "moral_partner_distance.csv", index=False)
        plot_summary_measures(per_myth, dist)
        print(up.round(4).to_string(index=False))


if __name__ == "__main__":
    main()

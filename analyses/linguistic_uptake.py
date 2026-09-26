#!/usr/bin/env python3
"""Do agents reuse the language of the myth they were shown?

Four measures on the September informed negative-only runs (homogeneous
controls plus mixed-model dyads and populations; tables from
analyses/linguistic_corpus.py). Each compares the myth an agent was actually
shown (its `myth_exposures` parent) with a myth it was not shown, so shared
prompts, shared models and population-wide drift cancel out.

1. Word adoption. Among the parent's words the child had never used in its own
   earlier myths, the share the child now uses. Null: the same share for an
   unseen myth by the same family from the previous round (8-agent: another
   agent in the same run; dyads: the same-family agent in another run of the
   same cell).
2. Embedding closeness (all-mpnet-base-v2 cosine) to the parent versus the same
   unseen myths.
3. Cross-family marker uptake (mixed runs only). Markers are words and word
   pairs common in one family's homogeneous myths (>= 5% of myths) and rare in
   the other's (<= 1%, >= 5x ratio). Two tests: (a) specific uptake, whether a
   family-B child starts using a family-A marker more often when its family-A
   parent used that marker than when it did not, against a null that reassigns
   the parent to another unseen family-A myth from the same round (8-agent: same
   run; dyads: same cell); (b) marker rate by round against the family's own
   homogeneous runs.
4. Style drift. A word-level classifier trained on homogeneous myths tells the
   three families apart (accuracy reported from run-grouped cross-validation);
   applied to mixed myths it gives the probability that a family-B myth reads as
   the partner family A, against B's own homogeneous myths at the same round.

Outputs: data/analysis/linguistic_20260923/ (child-level tables, embeddings)
and docs/figures/linguistic_analysis_20260923/ (figures and summary CSVs).
No API calls.

  python3 analyses/linguistic_uptake.py [--perms 1000]
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path
import sys

import numpy as np
import pandas as pd
from scipy import sparse, stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from analyses._shared import cached_embeddings, configure_matplotlib  # noqa: E402

DATA = ROOT / "data/analysis/linguistic_20260923"
FIGS = ROOT / "docs/figures/linguistic_analysis_20260923"
FAMILIES = ["Sonnet", "Gemini", "GPT"]
FAMILY_COLORS = {"Sonnet": "#7570b3", "GPT": "#d95f02", "Gemini": "#1b9e77"}
MIN_WORDS = 20  # one GPT myth in the mixed dyads is an empty response
TOKEN = re.compile(r"[a-z][a-z'-]+")


# --------------------------------------------------------------------------- data

def load_myths() -> pd.DataFrame:
    myths = pd.read_csv(DATA / "myths.csv")
    myths["valid"] = myths["n_words"] >= MIN_WORDS
    myths["text"] = myths["text"].fillna("")
    return myths.reset_index(drop=True)


def content_words(text: str) -> frozenset[str]:
    from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
    return frozenset(w.strip("'-") for w in TOKEN.findall(text.lower())
                     if len(w) >= 3 and w not in ENGLISH_STOP_WORDS)


def embeddings(myths: pd.DataFrame) -> np.ndarray:
    return cached_embeddings(DATA / "embeddings_mpnet.npy", myths["text"].tolist(),
                             batch_size=64, show_progress_bar=True)


def index_of(myths: pd.DataFrame) -> dict[tuple, int]:
    return {(r, t, a): i for i, (r, t, a) in enumerate(zip(myths["run_id"], myths["round"], myths["agent"]))}


def own_history(myths: pd.DataFrame, words: list[frozenset]) -> list[frozenset]:
    """Words each author used in its own myths before the current round."""
    hist: list[frozenset] = [frozenset()] * len(myths)
    for _, grp in myths.groupby(["run_id", "agent"]):
        seen: set[str] = set()
        for i in grp.sort_values("round").index:
            hist[i] = frozenset(seen)
            seen |= words[i]
    return hist


def null_candidates(myths: pd.DataFrame) -> dict[int, list[int]]:
    """For each exposed child: unseen same-family myths from the parent's round."""
    idx = index_of(myths)
    by_run_round = {k: g.index.to_list() for k, g in myths[myths["valid"]].groupby(["run_id", "round"])}
    by_cell_round = {k: g.index.to_list() for k, g in
                     myths[myths["valid"]].groupby(["composition", "task_order", "round"])}
    out: dict[int, list[int]] = {}
    for i, row in myths[(myths["round"] > 1) & myths["valid"]].iterrows():
        p = idx.get((row.run_id, row.exposed_round, row.exposed_author))
        if p is None or not myths.at[p, "valid"]:
            continue
        pfam = myths.at[p, "family"]
        if row["size"] == 8:
            cands = [j for j in by_run_round.get((row.run_id, row.exposed_round), [])
                     if myths.at[j, "agent"] not in (row.agent, row.exposed_author) and myths.at[j, "family"] == pfam]
        else:
            cands = [j for j in by_cell_round.get((row.composition, row.task_order, row.exposed_round), [])
                     if myths.at[j, "run_id"] != row.run_id and myths.at[j, "family"] == pfam
                     and (row.mixed or myths.at[j, "agent"] == row.exposed_author)]
        if cands:
            out[i] = [p] + cands  # first entry is the real parent
    return out


# --------------------------------------------------------------------------- 1 + 2

def exposure_label(row) -> str:
    if not row["mixed"]:
        return "homogeneous"
    return "mixed, same family" if row["family"] == row["parent_family"] else "mixed, other family"


def child_table(myths, words, hist, emb, cands) -> pd.DataFrame:
    rows = []
    for i, js in cands.items():
        p, nulls = js[0], js[1:]
        new = words[i] - hist[i]

        def adoption(j):
            pool = words[j] - hist[i]
            return len(new & pool) / len(pool) if pool else np.nan

        row = myths.loc[i]
        rows.append({
            "run_id": row.run_id, "size": row["size"], "mixed": row.mixed, "composition": row.composition,
            "task_order": row.task_order, "round": row["round"], "agent": row.agent, "family": row.family,
            "parent_family": myths.at[p, "family"],
            "adopt_parent": adoption(p), "adopt_null": np.nanmean([adoption(j) for j in nulls]),
            "cos_parent": float(emb[i] @ emb[p]), "cos_null": float(np.mean(emb[nulls] @ emb[i])),
            "n_null": len(nulls),
        })
    df = pd.DataFrame(rows)
    df["exposure"] = df.apply(exposure_label, axis=1)
    df["adopt_excess"] = df["adopt_parent"] - df["adopt_null"]
    df["cos_excess"] = df["cos_parent"] - df["cos_null"]
    return df


def run_level_summary(children: pd.DataFrame, by: list[str]) -> pd.DataFrame:
    per_run = children.groupby(by + ["run_id"])[
        ["adopt_parent", "adopt_null", "adopt_excess", "cos_parent", "cos_null", "cos_excess"]].mean().reset_index()
    rows = []
    for keys, g in per_run.groupby(by):
        keys = keys if isinstance(keys, tuple) else (keys,)
        rec = dict(zip(by, keys))
        rec["n_runs"] = len(g)
        for m in ["adopt_parent", "adopt_null", "adopt_excess", "cos_parent", "cos_null", "cos_excess"]:
            rec[f"{m}_mean"] = g[m].mean()
            rec[f"{m}_sd"] = g[m].std(ddof=1)
        for m in ["adopt_excess", "cos_excess"]:
            vals = g[m].dropna()
            rec[f"{m}_p"] = stats.wilcoxon(vals).pvalue if len(vals) >= 5 and (vals != 0).any() else np.nan
            rec[f"{m}_runs_positive"] = int((vals > 0).sum())
        rows.append(rec)
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- 3

def marker_matrix(myths: pd.DataFrame):
    from sklearn.feature_extraction.text import CountVectorizer
    vec = CountVectorizer(ngram_range=(1, 2), stop_words="english", binary=True, min_df=5,
                          token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z'-]+\b")
    text = np.where(myths["valid"], myths["text"], "")
    X = vec.fit_transform(text).tocsr().astype(np.int8)
    return X, np.array(vec.get_feature_names_out())


def family_markers(myths, X, vocab, fam_a, fam_b, min_a=0.05, max_b=0.01, ratio=5.0):
    homog = myths["valid"] & ~myths["mixed"]
    Xa = X[(homog & (myths["family"] == fam_a)).to_numpy()]
    Xb = X[(homog & (myths["family"] == fam_b)).to_numpy()]
    df_a = np.asarray(Xa.mean(axis=0)).ravel()
    df_b = np.asarray(Xb.mean(axis=0)).ravel()
    keep = (df_a >= min_a) & (df_b <= max_b) & (df_a >= ratio * np.maximum(df_b, 1.0 / Xb.shape[0]))
    order = np.argsort(-df_a[keep])
    return np.flatnonzero(keep)[order], df_a, df_b


def history_matrix(myths: pd.DataFrame, X) -> sparse.csr_matrix:
    """Row i: every n-gram the author used in its own myths before round i."""
    H = sparse.lil_matrix(X.shape, dtype=np.int8)
    for _, grp in myths.groupby(["run_id", "agent"]):
        acc = None
        for i in grp.sort_values("round").index:
            if acc is not None:
                H[i] = acc
            acc = X[i] if acc is None else ((acc + X[i]) > 0).astype(np.int8)
    return H.tocsr()


def specific_uptake(children_idx, parents, Xc, Hc):
    """P(child starts using m | parent used m) - P(child starts using m | parent did not).

    Xc / Hc: dense boolean marker columns for every myth / its author's history.
    Only (child, marker) cells the child had never used before count."""
    new_ok = ~Hc[children_idx]
    y = Xc[children_idx] & new_ok
    P = Xc[parents]
    e, ne_mask = P & new_ok, new_ok & ~P
    ne, nn = e.sum(), ne_mask.sum()
    if ne == 0 or nn == 0:
        return np.nan, np.nan, np.nan
    p1, p0 = (y & e).sum() / ne, (y & ne_mask).sum() / nn
    return p1 - p0, p1, p0


def marker_tests(myths, X, vocab, H, cands, perms, rng):
    idx = index_of(myths)
    mixed = myths[myths["mixed"] & myths["valid"]]
    pairs = sorted({(b, a) for comp, g in mixed.groupby("run_id") for b in g.family.unique()
                    for a in g.family.unique() if a != b})
    spec_rows, marker_rows, rate_rows = [], [], []
    for fam_b, fam_a in pairs:  # child family B, parent family A
        cols, df_a, df_b = family_markers(myths, X, vocab, fam_a, fam_b)
        for c in cols[:25]:
            marker_rows.append({"marker_family": fam_a, "vs_family": fam_b, "marker": vocab[c],
                                "share_in_marker_family": df_a[c], "share_in_other_family": df_b[c]})
        for size in (2, 8):
            kids = [i for i, js in cands.items()
                    if myths.at[i, "size"] == size and myths.at[i, "mixed"] and myths.at[i, "family"] == fam_b
                    and myths.at[js[0], "family"] == fam_a]
            if len(cols) == 0 or not kids:
                continue
            parents = [cands[i][0] for i in kids]
            Xc = X[:, cols].toarray().astype(bool)
            Hc = H[:, cols].toarray().astype(bool)
            obs, p1, p0 = specific_uptake(kids, parents, Xc, Hc)
            null = np.empty(perms)
            for k in range(perms):
                null[k] = specific_uptake(kids, [rng.choice(cands[i][1:]) for i in kids], Xc, Hc)[0]
            spec_rows.append({"child_family": fam_b, "parent_family": fam_a, "size": size,
                              "n_markers": len(cols), "n_children": len(kids),
                              "p_start_if_parent_used": p1, "p_start_if_parent_did_not": p0,
                              "excess": obs, "null_mean": np.nanmean(null), "null_sd": np.nanstd(null),
                              "p_perm": (np.sum(null >= obs) + 1) / (perms + 1)})
            # marker rate by round: homogeneous B, mixed B shown B, mixed B shown A
            rate = np.asarray(X[:, cols].mean(axis=1)).ravel()
            base = myths["valid"] & (myths["size"] == size) & (myths["family"] == fam_b)
            homog = base & ~myths["mixed"]
            in_pair = base & myths["mixed"] & myths["composition"].str.contains(fam_a)
            groups = {"homogeneous": homog, "mixed, shown same family": in_pair & (myths["exposed_family"] == fam_b),
                      "mixed, shown other family": in_pair & (myths["exposed_family"] == fam_a),
                      "mixed, round 1 (nothing shown)": in_pair & (myths["round"] == 1)}
            for label, mask in groups.items():
                for rnd, vals in pd.Series(rate[mask.to_numpy()], index=myths.loc[mask, "round"]).groupby(level=0):
                    rate_rows.append({"child_family": fam_b, "marker_family": fam_a, "size": size, "group": label,
                                      "round": rnd, "marker_rate_mean": vals.mean(), "marker_rate_sd": vals.std(ddof=1),
                                      "n_myths": len(vals)})
    return pd.DataFrame(spec_rows), pd.DataFrame(marker_rows), pd.DataFrame(rate_rows)


# --------------------------------------------------------------------------- 4

def style_classifier(myths: pd.DataFrame):
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import GroupKFold
    from sklearn.pipeline import make_pipeline

    homog = myths[myths["valid"] & ~myths["mixed"]]
    mixed = myths[myths["valid"] & myths["mixed"]]

    def model():
        return make_pipeline(TfidfVectorizer(ngram_range=(1, 2), min_df=3, sublinear_tf=True),
                             LogisticRegression(max_iter=3000, C=4.0))

    oof = np.zeros((len(homog), len(FAMILIES)))
    for train, test in GroupKFold(n_splits=5).split(homog, groups=homog["run_id"]):
        m = model().fit(homog["text"].iloc[train], homog["family"].iloc[train])
        proba = m.predict_proba(homog["text"].iloc[test])
        oof[test] = proba[:, [list(m.classes_).index(f) for f in FAMILIES]]
    accuracy = float((np.array(FAMILIES)[oof.argmax(1)] == homog["family"].to_numpy()).mean())
    full = model().fit(homog["text"], homog["family"])
    mix_p = full.predict_proba(mixed["text"])[:, [list(full.classes_).index(f) for f in FAMILIES]]
    probs = pd.concat([
        homog[["run_id", "size", "mixed", "composition", "task_order", "round", "agent", "family", "exposed_family"]]
        .assign(**{f"p_{f}": oof[:, k] for k, f in enumerate(FAMILIES)}),
        mixed[["run_id", "size", "mixed", "composition", "task_order", "round", "agent", "family", "exposed_family"]]
        .assign(**{f"p_{f}": mix_p[:, k] for k, f in enumerate(FAMILIES)}),
    ])
    return probs, accuracy


def style_drift(probs: pd.DataFrame) -> pd.DataFrame:
    rows = []
    mixed = probs[probs["mixed"]]
    for (size, comp), g in mixed.groupby(["size", "composition"]):
        fams = sorted(g["family"].unique())
        for fam_b in fams:
            fam_a = [f for f in fams if f != fam_b][0]
            mine = g[g["family"] == fam_b]
            ref = probs[~probs["mixed"] & (probs["size"] == size) & (probs["family"] == fam_b)]
            for label, sub in (("mixed", mine), ("homogeneous", ref)):
                for rnd, vals in sub.groupby("round")[f"p_{fam_a}"]:
                    rows.append({"size": size, "composition": comp, "family": fam_b, "partner_family": fam_a,
                                 "group": label, "round": rnd, "p_reads_as_partner_mean": vals.mean(),
                                 "p_reads_as_partner_sd": vals.std(ddof=1), "n_myths": len(vals)})
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- figures

def plot_excess(summary: pd.DataFrame) -> None:
    import matplotlib.pyplot as plt
    configure_matplotlib()
    order = [(2, "homogeneous"), (2, "mixed, other family"), (8, "homogeneous"),
             (8, "mixed, same family"), (8, "mixed, other family")]
    labels = ["2-agent\nhomogeneous", "2-agent mixed\nshown other\nfamily", "8-agent\nhomogeneous",
              "8-agent mixed\nshown same\nfamily", "8-agent mixed\nshown other\nfamily"]
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.6))
    for ax, metric, title, scale in ((axes[0], "adopt", "New words taken from the myth", 100),
                                     (axes[1], "cos", "Meaning closeness to the myth", 1)):
        for x, (size, exp) in enumerate(order):
            r = summary[(summary["size"] == size) & (summary["exposure"] == exp)]
            if r.empty:
                continue
            r = r.iloc[0]
            for dx, part, color in ((-0.18, "parent", "#444444"), (0.18, "null", "#bbbbbb")):
                ax.bar(x + dx, r[f"{metric}_{part}_mean"] * scale, width=0.34, color=color,
                       yerr=r[f"{metric}_{part}_sd"] * scale, capsize=3, error_kw=dict(lw=1, ecolor="#666666"))
        ax.set_xticks(range(len(order)), labels, fontsize=8)
        ax.set_title(title)
        ax.grid(axis="y", alpha=0.3)
    axes[0].set_ylabel("% of the myth's unused words the agent starts using")
    axes[1].set_ylabel("cosine similarity (all-mpnet-base-v2)")
    from matplotlib.patches import Patch
    axes[1].legend(handles=[Patch(color="#444444", label="myth the agent was shown"),
                            Patch(color="#bbbbbb", label="comparable myth it was not shown")],
                   loc="lower right", fontsize=8)
    lo = min(summary["cos_null_mean"].min(), summary["cos_parent_mean"].min())
    axes[1].set_ylim(max(0, lo - 0.1), 1)
    fig.suptitle("Agents reuse the language of the myth they were shown (bars: mean over runs, whiskers: sd)")
    fig.tight_layout()
    fig.savefig(FIGS / "language_reuse_shown_vs_unseen.png", dpi=200)
    plt.close(fig)


def plot_marker_rates(rates: pd.DataFrame) -> None:
    import matplotlib.pyplot as plt
    configure_matplotlib()
    combos = rates[["size", "child_family", "marker_family"]].drop_duplicates().sort_values(["size", "child_family"])
    n = len(combos)
    cols = 4
    rows_n = int(np.ceil(n / cols))
    fig, axes = plt.subplots(rows_n, cols, figsize=(4 * cols, 3.3 * rows_n), squeeze=False)
    styles = {"homogeneous": ("#999999", "--"), "mixed, shown same family": (None, ":"),
              "mixed, shown other family": (None, "-")}
    for ax, (_, c) in zip(axes.ravel(), combos.iterrows()):
        sub = rates[(rates["size"] == c["size"]) & (rates["child_family"] == c.child_family)
                    & (rates["marker_family"] == c.marker_family)]
        for label, (color, ls) in styles.items():
            s = sub[sub["group"] == label].sort_values("round")
            if label != "homogeneous":
                r1 = sub[sub["group"] == "mixed, round 1 (nothing shown)"]
                s = pd.concat([r1, s]).sort_values("round")
            if s.empty:
                continue
            ax.plot(s["round"], s["marker_rate_mean"] * 100, ls=ls, lw=2,
                    color=color or FAMILY_COLORS[c.marker_family], label=label, marker="o", ms=3)
        ax.set_title(f"{c.child_family} using {c.marker_family} markers ({c['size']}-agent)", fontsize=9)
        ax.set_xlabel("round")
        ax.grid(alpha=0.3)
    for ax in axes.ravel()[n:]:
        ax.axis("off")
    axes[0, 0].set_ylabel("% of the other family's markers present")
    axes[0, 0].legend(fontsize=7)
    fig.suptitle("Does a family pick up the other family's signature words?")
    fig.tight_layout()
    fig.savefig(FIGS / "cross_family_marker_rates.png", dpi=200)
    plt.close(fig)


def plot_style(drift: pd.DataFrame, accuracy: float) -> None:
    import matplotlib.pyplot as plt
    configure_matplotlib()
    combos = drift[["size", "composition", "family"]].drop_duplicates().sort_values(["size", "composition", "family"])
    cols = 4
    rows_n = int(np.ceil(len(combos) / cols))
    fig, axes = plt.subplots(rows_n, cols, figsize=(4 * cols, 3.1 * rows_n), squeeze=False)
    for ax, (_, c) in zip(axes.ravel(), combos.iterrows()):
        sub = drift[(drift["size"] == c["size"]) & (drift["composition"] == c.composition) & (drift["family"] == c.family)]
        partner = sub["partner_family"].iloc[0]
        for label, ls, color in (("homogeneous", "--", "#999999"), ("mixed", "-", FAMILY_COLORS[c.family])):
            s = sub[sub["group"] == label].sort_values("round")
            ax.plot(s["round"], s["p_reads_as_partner_mean"], ls=ls, color=color, lw=2, marker="o", ms=3,
                    label=f"{c.family} {'with ' + partner if label == 'mixed' else 'among its own'}")
        ax.set_ylim(0, 1)
        ax.set_title(f"{c.family} in {c.composition}", fontsize=9)
        ax.set_xlabel("round")
        ax.grid(alpha=0.3)
        ax.legend(fontsize=7, loc="upper left")
        ax.set_ylabel(f"P(reads as {partner})", fontsize=8)
    for ax in axes.ravel()[len(combos):]:
        ax.axis("off")
    fig.suptitle(f"How much each family's myths read like its partner's family "
                 f"(classifier tells the families apart {accuracy:.0%} of the time on held-out runs)")
    fig.tight_layout()
    fig.savefig(FIGS / "style_drift_toward_partner.png", dpi=200)
    plt.close(fig)


# --------------------------------------------------------------------------- main

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--perms", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=20260923)
    args = ap.parse_args()
    rng = np.random.default_rng(args.seed)
    FIGS.mkdir(parents=True, exist_ok=True)

    myths = load_myths()
    print(f"{len(myths)} myths, {int((~myths['valid']).sum())} excluded as empty")
    words = [content_words(t) for t in myths["text"]]
    hist = own_history(myths, words)
    emb = embeddings(myths)
    cands = null_candidates(myths)
    print(f"{len(cands)} exposed myths with at least one unseen comparison myth")

    children = child_table(myths, words, hist, emb, cands)
    children.to_csv(DATA / "uptake_children.csv", index=False)
    main_summary = run_level_summary(children, ["size", "exposure"])
    by_order = run_level_summary(children, ["size", "exposure", "task_order"])
    by_family = run_level_summary(children, ["size", "exposure", "family", "parent_family"])
    main_summary.to_csv(FIGS / "reuse_summary.csv", index=False)
    by_order.to_csv(FIGS / "reuse_by_task_order.csv", index=False)
    by_family.to_csv(FIGS / "reuse_by_family_pair.csv", index=False)
    plot_excess(main_summary)
    show = ["size", "exposure", "n_runs", "adopt_parent_mean", "adopt_null_mean", "adopt_excess_mean",
            "adopt_excess_sd", "adopt_excess_p", "cos_excess_mean", "cos_excess_sd", "cos_excess_p"]
    print(main_summary[show].round(4).to_string(index=False))

    X, vocab = marker_matrix(myths)
    H = history_matrix(myths, X)
    spec, markers, rates = marker_tests(myths, X, vocab, H, cands, args.perms, rng)
    spec.to_csv(FIGS / "marker_specific_uptake.csv", index=False)
    markers.to_csv(FIGS / "family_markers_top25.csv", index=False)
    rates.to_csv(FIGS / "marker_rates_by_round.csv", index=False)
    plot_marker_rates(rates)
    print(spec.round(4).to_string(index=False))

    probs, accuracy = style_classifier(myths)
    probs.to_csv(DATA / "style_probabilities.csv", index=False)
    drift = style_drift(probs)
    drift.to_csv(FIGS / "style_drift_by_round.csv", index=False)
    plot_style(drift, accuracy)
    print(f"family classifier accuracy on held-out homogeneous runs: {accuracy:.3f}")


if __name__ == "__main__":
    main()

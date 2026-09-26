#!/usr/bin/env python3
"""Does myth alignment track cooperation? (September informed negative-only runs)

Successor to analyses/convergence_vs_cooperation.py for the September
homogeneous controls and mixed-model runs. It keeps that script's levels but
reads the shared tables from analyses/linguistic_corpus.py and the myth
embeddings cached by analyses/linguistic_uptake.py, and adds the direction
test: is alignment before a game linked to that game, and is a game linked to
how alike the two players write afterwards?

Pair level (main result). For every game, the similarity of the two players'
latest myths written before it (myth->game: that round's myths; game->myth:
the previous round's) is related to the game's cooperation: amount sent / 5,
return proportion, and Arabella Sinclair's giving gap (|sent / 5 - return
proportion|, 0 = both gave the same share). OLS with run x pair-family and
round fixed effects (a mixed population holds games between different family
pairs in the same run), standard errors clustered by run. "After" repeats this with the two
players' next myths, written after the game.

Run level (context). Per run, mean similarity of playing pairs against mean
cooperation, Spearman across runs, pooled and after centring each composition x
task order cell (pooling mixes model families, which differ on both axes).

Outputs: docs/figures/linguistic_analysis_20260923/alignment_*.{csv,png}.
No API calls.

  python3 analyses/alignment_vs_cooperation.py
"""
from __future__ import annotations

from pathlib import Path
import sys
import warnings

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from analyses._shared import configure_matplotlib  # noqa: E402

DATA = ROOT / "data/analysis/linguistic_20260923"
FIGS = ROOT / "docs/figures/linguistic_analysis_20260923"
OUTCOMES = {"sent_frac": "amount sent / 5", "return_proportion": "return proportion",
            "giving_gap": "giving gap |sent/5 - return proportion|"}
MIN_WORDS = 20


def setting(size: int, mixed: bool, pair_type: str | None = None) -> str:
    base = f"{size}-agent {'mixed' if mixed else 'homogeneous'}"
    return f"{base}, {pair_type}" if mixed and size == 8 and pair_type else base


def games_table() -> pd.DataFrame:
    myths = pd.read_csv(DATA / "myths.csv")
    emb = np.load(DATA / "embeddings_mpnet.npy")
    assert len(emb) == len(myths), "rerun analyses/linguistic_uptake.py to refresh the embedding cache"
    valid = myths["n_words"].to_numpy() >= MIN_WORDS
    idx = {(r, t, a): i for i, (r, t, a) in enumerate(zip(myths["run_id"], myths["round"], myths["agent"]))}

    dec = pd.read_csv(DATA / "decisions.csv")
    inv = dec[dec["role"] == "investor"].rename(columns={"agent": "investor", "partner": "trustee",
                                                         "family": "investor_family",
                                                         "partner_family": "trustee_family"})
    games = inv[["run_id", "size", "mixed", "composition", "task_order", "replicate_id", "round", "investor",
                 "trustee", "investor_family", "trustee_family", "sent", "received", "returned",
                 "return_proportion"]].copy()
    games["sent_frac"] = games["sent"] / 5.0
    games["giving_gap"] = (games["sent_frac"] - games["return_proportion"]).abs()
    games["pair_family"] = ["-".join(sorted(p)) for p in zip(games["investor_family"], games["trustee_family"])]
    games["pair_type"] = np.where(games["investor_family"] == games["trustee_family"], "same family", "cross family")

    def pair_sim(run, rnd, a, b):
        i, j = idx.get((run, rnd, a)), idx.get((run, rnd, b))
        if i is None or j is None or not (valid[i] and valid[j]):
            return np.nan
        return float(emb[i] @ emb[j])

    before, after = [], []
    for g in games.itertuples(index=False):
        # myth->game: round t myths precede game t; game->myth: they follow it
        r_before = g.round if g.task_order == "myth_game" else g.round - 1
        r_after = g.round + 1 if g.task_order == "myth_game" else g.round
        before.append(pair_sim(g.run_id, r_before, g.investor, g.trustee))
        after.append(pair_sim(g.run_id, r_after, g.investor, g.trustee))
    games["sim_before"] = before
    games["sim_after"] = after
    games["setting"] = [setting(s, m, p) for s, m, p in zip(games["size"], games["mixed"], games["pair_type"])]
    return games


def fe_slope(df: pd.DataFrame, y: str, x: str) -> dict:
    """Slope of y on x with run x pair-family and round fixed effects, SE clustered by run."""
    import statsmodels.formula.api as smf
    d = df[[y, x, "run_id", "round", "pair_family"]].dropna()
    if d["run_id"].nunique() < 5 or len(d) < 30:
        return {"n_games": len(d), "n_runs": d["run_id"].nunique()}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        # run x pair-family cells: a mixed population holds GPT-GPT and Sonnet-Sonnet
        # games in the same run; elsewhere this reduces to run fixed effects
        d = d.assign(cell=d["run_id"] + "|" + d["pair_family"])
        fit = smf.ols(f"{y} ~ {x} + C(cell) + C(round)", data=d).fit(
            cov_type="cluster", cov_kwds={"groups": pd.factorize(d["run_id"])[0]})
    # report per 0.1 cosine, roughly the gap between shown and unseen myths
    return {"n_games": len(d), "n_runs": d["run_id"].nunique(), "slope_per_0.1": 0.1 * fit.params[x],
            "ci_low": 0.1 * fit.conf_int().loc[x, 0], "ci_high": 0.1 * fit.conf_int().loc[x, 1],
            "p": fit.pvalues[x], "sd_x_within_run": d.groupby("run_id")[x].transform(lambda v: v - v.mean()).std()}


def pair_level(games: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (st, order), g in list(games.groupby(["setting", "task_order"])) + \
            [((st, "both orders"), g) for st, g in games.groupby("setting")]:
        for direction, x in (("myths before the game", "sim_before"), ("myths after the game", "sim_after")):
            for y in OUTCOMES:
                rows.append({"setting": st, "task_order": order, "direction": direction, "outcome": y,
                             **fe_slope(g, y, x)})
    return pd.DataFrame(rows)


def run_level(games: pd.DataFrame) -> pd.DataFrame:
    """Across runs: pooled Spearman, and Spearman after removing each cell's mean.

    Pooling confounds alignment with model family (families differ in both how
    alike their myths are and how much they cooperate), so the within-cell
    version, which centres each composition x task order, is the one to read."""
    per_run = games.groupby(["size", "mixed", "composition", "task_order", "run_id"]).agg(
        sim=("sim_before", "mean"), sent_frac=("sent_frac", "mean"),
        return_proportion=("return_proportion", "mean"), giving_gap=("giving_gap", "mean")).reset_index()
    rows = []
    for (size, mixed), g in per_run.groupby(["size", "mixed"]):
        cells = g.groupby(["composition", "task_order"])
        for y in OUTCOMES:
            d = g[["sim", y]].dropna()
            rho, p = stats.spearmanr(d["sim"], d[y])
            within = pd.DataFrame({"sim": g["sim"] - cells["sim"].transform("mean"),
                                   y: g[y] - cells[y].transform("mean")}).dropna()
            rho_w, p_w = stats.spearmanr(within["sim"], within[y])
            rows.append({"setting": setting(size, mixed), "outcome": y, "n_runs": len(d),
                         "n_cells": cells.ngroups, "spearman_rho_pooled": rho, "p_pooled": p,
                         "spearman_rho_within_cell": rho_w, "p_within_cell": p_w})
    return pd.DataFrame(rows)


def plot_slopes(pairs: pd.DataFrame) -> None:
    import matplotlib.pyplot as plt
    configure_matplotlib()
    d = pairs[(pairs["task_order"] == "both orders") & pairs["slope_per_0.1"].notna()]
    settings = ["2-agent homogeneous", "2-agent mixed", "8-agent homogeneous",
                "8-agent mixed, same family", "8-agent mixed, cross family"]
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.4), sharey=True)
    for ax, (y, label) in zip(axes, OUTCOMES.items()):
        for k, (direction, color, dy) in enumerate((("myths before the game", "#333333", -0.12),
                                                    ("myths after the game", "#999999", 0.12))):
            for yi, st in enumerate(settings):
                r = d[(d["setting"] == st) & (d["outcome"] == y) & (d["direction"] == direction)]
                if r.empty:
                    continue
                r = r.iloc[0]
                ax.errorbar(r["slope_per_0.1"], yi + dy, xerr=[[r["slope_per_0.1"] - r["ci_low"]],
                                                                [r["ci_high"] - r["slope_per_0.1"]]],
                            fmt="o", color=color, capsize=3, label=direction if yi == 0 else None)
        ax.axvline(0, color="#cc3333", lw=1)
        ax.xaxis.set_major_locator(plt.MaxNLocator(5))
        ax.set_title(label, fontsize=10)
        ax.set_xlabel("change per +0.1 myth similarity\n(run and round fixed effects, 95% CI)")
        ax.grid(axis="x", alpha=0.3)
    axes[0].set_yticks(range(len(settings)), settings)
    axes[0].invert_yaxis()
    axes[0].legend(fontsize=8, loc="lower left")
    fig.suptitle("Do players whose myths are more alike cooperate more with each other?")
    fig.tight_layout()
    fig.savefig(FIGS / "alignment_vs_cooperation.png", dpi=200)
    plt.close(fig)


def main() -> None:
    FIGS.mkdir(parents=True, exist_ok=True)
    games = games_table()
    games.to_csv(DATA / "alignment_games.csv", index=False)
    pairs = pair_level(games)
    runs = run_level(games)
    pairs.to_csv(FIGS / "alignment_pair_level.csv", index=False)
    runs.to_csv(FIGS / "alignment_run_level.csv", index=False)
    plot_slopes(pairs)
    cols = ["setting", "direction", "outcome", "n_games", "n_runs", "slope_per_0.1", "ci_low", "ci_high", "p"]
    print(pairs[pairs["task_order"] == "both orders"][cols].round(4).to_string(index=False))
    print(runs.round(3).to_string(index=False))


if __name__ == "__main__":
    main()

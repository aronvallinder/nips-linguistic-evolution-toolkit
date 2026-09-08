"""Four-panel overview of the meme/norm diffusion analysis.

Visualizes the outputs of the meme-evolution pipeline
(data/analysis/meme_evolution_<date>/):

  A. Which norms are most prevalent (capsule prevalence, mean ± std across runs)
  B. How they spread over rounds (share of capsules carrying each norm per round)
  C. How they travel (transmission rate and mutation rate per route)
  D. Whether they stay static or get updated (variant-to-variant transition
     matrix within the dominant norm)

Usage (from repo root):
    python analyses/plot_meme_evolution.py \
        --input-dir data/analysis/meme_evolution_2026_08_19 \
        --output-dir data/plots/meme_evolution_2026_08_19
"""

import argparse
import os

import numpy as np
import pandas as pd

from _shared import configure_matplotlib

configure_matplotlib()
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

SERIES = ["#2a78d6", "#1baf7a", "#eda100", "#008300", "#4a3aa7"]
GRAY_FILL = "#c3c2b7"

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRIDLINE = "#e1e0d9"
BASELINE = "#c3c2b7"

SEQ_BLUES = LinearSegmentedColormap.from_list(
    "seq_blue", ["#fcfcfb", "#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]
)

PRETTY = {
    "proportional_reciprocity": "Proportional reciprocity",
    "consistency_over_volatility": "Consistency over volatility",
    "sustainable_equilibrium": "Sustainable equilibrium",
    "noise_adaptation": "Noise adaptation",
    "trust_seeding": "Trust seeding",
    "prosperity_through_cooperation": "Prosperity through cooperation",
    "trust_escalation": "Trust escalation",
    "punitive_deterrence": "Punitive deterrence",
    "repair_after_disruption": "Repair after disruption",
}


def style_axis(ax):
    ax.set_facecolor(SURFACE)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(BASELINE)
    ax.tick_params(colors=INK_MUTED, labelsize=9)
    ax.set_axisbelow(True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir",
                        default="data/analysis/meme_evolution_2026_08_19")
    parser.add_argument("--output-dir",
                        default="data/plots/meme_evolution_2026_08_19")
    args = parser.parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    fam = pd.read_csv(os.path.join(args.input_dir, "family_meme_summary.csv"))
    occ = pd.read_csv(os.path.join(args.input_dir, "meme_occurrences.csv"))
    tr = pd.read_csv(os.path.join(args.input_dir, "meme_transmissions.csv"))
    runs = pd.read_csv(os.path.join(args.input_dir, "run_meme_summary.csv"))

    fam = fam.sort_values("capsule_prevalence_mean", ascending=True)
    top5 = list(fam.sort_values("capsule_prevalence_mean",
                                ascending=False)["meme_family"].head(5))
    color_of = {f: SERIES[i] for i, f in enumerate(top5)}

    fig, axes = plt.subplots(2, 2, figsize=(13.5, 9.6))
    fig.patch.set_facecolor(SURFACE)
    (ax_prev, ax_round), (ax_route, ax_mix) = axes
    for ax in axes.flat:
        style_axis(ax)

    # --- A: prevalence ranking -------------------------------------------
    labels = [PRETTY.get(f, f) for f in fam["meme_family"]]
    means = fam["capsule_prevalence_mean"].to_numpy() * 100
    stds = fam["capsule_prevalence_std"].to_numpy() * 100
    colors = [color_of.get(f, GRAY_FILL) for f in fam["meme_family"]]
    y = np.arange(len(fam))
    ax_prev.barh(y, means, height=0.62, color=colors, zorder=3)
    ax_prev.errorbar(means, y, xerr=stds, fmt="none", ecolor=INK_MUTED,
                     elinewidth=1, capsize=2, zorder=4)
    for yi, m, s in zip(y, means, stds):
        ax_prev.annotate(f"{m:.0f}% (±{s:.0f}%)", (m + s + 1.5, yi),
                         va="center", fontsize=8.5, color=INK_SECONDARY)
    ax_prev.set_yticks(y)
    ax_prev.set_yticklabels(labels, fontsize=9, color=INK)
    ax_prev.xaxis.grid(True, color=GRIDLINE, linewidth=0.8, zorder=0)
    ax_prev.set_xlabel("Share of responses carrying the norm (%)",
                       color=INK_SECONDARY, fontsize=9.5)
    ax_prev.set_title("A · Which norms are most prevalent (mean ± std across 60 runs)",
                      color=INK, fontsize=10.5, loc="left")
    ax_prev.set_xlim(0, 100)

    # --- B: prevalence per round -----------------------------------------
    caps_per_round = runs["capsules"].sum() / 10  # equal capsules per round
    for f in top5:
        sub = occ[occ["meme_family"] == f]
        per_round = (sub.groupby("round")["capsule_id"].nunique()
                     .reindex(range(1, 11), fill_value=0) / caps_per_round * 100)
        ax_round.plot(per_round.index, per_round.values, color=color_of[f],
                      linewidth=2, marker="o", markersize=4.5,
                      label=PRETTY[f], zorder=3)
        ax_round.annotate(
            PRETTY[f].split()[0], (10, per_round.values[-1]), xytext=(6, 0),
            textcoords="offset points", va="center", fontsize=8.5,
            color=INK, fontweight="bold",
            bbox=dict(facecolor=SURFACE, edgecolor="none", pad=1.2),
        )
    ax_round.yaxis.grid(True, color=GRIDLINE, linewidth=0.8, zorder=0)
    ax_round.set_xticks(range(1, 11))
    ax_round.set_xlim(0.7, 11.9)
    ax_round.set_xlabel("Round", color=INK_SECONDARY, fontsize=9.5)
    ax_round.set_ylabel("Share of responses (%)", color=INK_SECONDARY,
                        fontsize=9.5)
    ax_round.set_title("B · How norms spread over rounds (all conditions pooled)",
                       color=INK, fontsize=10.5, loc="left")
    ax_round.legend(frameon=True, facecolor=SURFACE, edgecolor="none",
                    framealpha=1, fontsize=8, labelcolor=INK_SECONDARY,
                    loc="upper left")

    # --- C: routes — transmission vs mutation ----------------------------
    route_stats = tr.groupby("route").agg(retained=("retained", "mean")).join(
        tr[tr["retained"] == 1].groupby("route")["variant_shift"].mean()
        .rename("shift"))
    route_stats = route_stats.sort_values("retained", ascending=True)
    y = np.arange(len(route_stats))
    h = 0.34
    ax_route.barh(y + h / 2 + 0.02, route_stats["retained"] * 100, height=h,
                  color="#2a78d6", zorder=3, label="Transmitted to next visible step")
    ax_route.barh(y - h / 2 - 0.02, route_stats["shift"] * 100, height=h,
                  color="#eda100", zorder=3,
                  label="Reformulated when transmitted (variant shift)")
    for yi, (ret, sh) in enumerate(zip(route_stats["retained"],
                                       route_stats["shift"])):
        ax_route.annotate(f"{ret * 100:.0f}%", (ret * 100 + 1, yi + h / 2 + 0.02),
                          va="center", fontsize=8.5, color=INK_SECONDARY)
        ax_route.annotate(f"{sh * 100:.0f}%", (sh * 100 + 1, yi - h / 2 - 0.02),
                          va="center", fontsize=8.5, color=INK_SECONDARY)
    ax_route.set_yticks(y)
    ax_route.set_yticklabels(route_stats.index, fontsize=9, color=INK)
    ax_route.xaxis.grid(True, color=GRIDLINE, linewidth=0.8, zorder=0)
    ax_route.set_xlabel("Rate (%)", color=INK_SECONDARY, fontsize=9.5)
    ax_route.set_title("C · How norms travel — transmission and mutation by route",
                       color=INK, fontsize=10.5, loc="left")
    ax_route.legend(frameon=True, facecolor=SURFACE, edgecolor="none",
                    framealpha=1, fontsize=8, labelcolor=INK_SECONDARY,
                    loc="lower right")
    ax_route.set_xlim(0, 100)

    # --- D: variant mixing inside the dominant norm ----------------------
    dominant = top5[0]
    pr = tr[(tr["meme_family"] == dominant) & (tr["retained"] == 1)]
    variants = [v for v in pr["parent_variant"].value_counts().index
                if v != "generic"][:4]
    mat = pd.crosstab(pr["parent_variant"], pr["child_variant"])
    mat = mat.reindex(index=variants, columns=variants, fill_value=0)
    row_pct = mat.div(mat.sum(axis=1), axis=0) * 100
    im = ax_mix.imshow(row_pct, cmap=SEQ_BLUES, vmin=0, vmax=100)
    ax_mix.set_xticks(range(len(variants)))
    ax_mix.set_yticks(range(len(variants)))
    nice = [v.replace("_", "\n") for v in variants]
    ax_mix.set_xticklabels(nice, fontsize=8.5, color=INK)
    ax_mix.set_yticklabels(nice, fontsize=8.5, color=INK)
    ax_mix.set_xlabel("…to child formulation", color=INK_SECONDARY, fontsize=9.5)
    ax_mix.set_ylabel("From parent formulation…", color=INK_SECONDARY,
                      fontsize=9.5)
    for i in range(len(variants)):
        for j in range(len(variants)):
            val = row_pct.iloc[i, j]
            ax_mix.annotate(f"{val:.0f}%", (j, i), ha="center", va="center",
                            fontsize=9,
                            color="#ffffff" if val > 55 else INK)
    ax_mix.set_title(
        f"D · Does the dominant norm stay static? "
        f"({PRETTY[dominant]}, n={int(mat.to_numpy().sum()):,} transmissions)",
        color=INK, fontsize=10.5, loc="left")
    cbar = fig.colorbar(im, ax=ax_mix, shrink=0.8)
    cbar.set_label("Row share (%)", color=INK_SECONDARY, fontsize=8.5)
    cbar.ax.tick_params(colors=INK_MUTED, labelsize=8)
    cbar.outline.set_visible(False)

    n_recomb = pd.read_csv(
        os.path.join(args.input_dir, "recombination_candidates.csv")).shape[0]
    fig.text(
        0.01, 0.005,
        "Corpus: 60 informed-noise runs (2 & 8 agents × game / game→myth / "
        "myth→game), 5,000 responses, 12,033 norm occurrences, 77,909 "
        f"transmission edges, {n_recomb:,} recombination candidates. "
        "Transmission = norm present in a visible parent response and its "
        "child; measures textual inheritance, not causal influence.",
        fontsize=8, color=INK_MUTED)
    fig.tight_layout(rect=(0, 0.025, 1, 1))

    out = os.path.join(args.output_dir, "meme_evolution_overview.png")
    fig.savefig(out, dpi=200, facecolor=SURFACE, bbox_inches="tight")
    print(f"Saved {out}")

    total_shift = tr[tr["retained"] == 1]["variant_shift"].mean() * 100
    total_ret = tr["retained"].mean() * 100
    print(f"Overall: transmission {total_ret:.1f}%, "
          f"variant shift among transmitted {total_shift:.1f}%, "
          f"recombination candidates {n_recomb}")

    build_by_condition(occ, tr, runs, top5, args.output_dir)


TASK_ORDERS = ["Game only", "Game→Myth", "Myth→Game"]
ORDER_COLORS = {"Game only": "#2a78d6", "Game→Myth": "#1baf7a",
                "Myth→Game": "#eda100"}


def build_by_condition(occ, tr, runs, top5, output_dir):
    """Second figure: panels A, B, D split by task order (agent counts pooled)."""
    for df in (occ, tr, runs):
        df["order"] = df["condition"].str.split("·").str[1].str.strip()

    fig = plt.figure(figsize=(14, 13))
    fig.patch.set_facecolor(SURFACE)
    gs = fig.add_gridspec(3, 12, height_ratios=[1.25, 0.8, 0.95],
                          hspace=0.45, wspace=2.2)

    families = list(occ.groupby("meme_family").size()
                    .sort_values(ascending=True).index)

    # --- A: prevalence per norm, grouped by task order -------------------
    ax_a = fig.add_subplot(gs[0, :7])
    style_axis(ax_a)
    run_caps = runs.set_index("run_id")["capsules"]
    per_run = (occ.groupby(["run_id", "meme_family"])["capsule_id"].nunique()
               .unstack(fill_value=0)
               .reindex(columns=families, fill_value=0)
               .div(run_caps, axis=0)
               .join(runs.set_index("run_id")["order"]))
    y = np.arange(len(families))
    h = 0.24
    for k, order in enumerate(TASK_ORDERS):
        sub = per_run[per_run["order"] == order][families]
        means = sub.mean().to_numpy() * 100
        stds = sub.std().to_numpy() * 100
        off = (k - 1) * (h + 0.03)
        ax_a.barh(y + off, means, height=h, color=ORDER_COLORS[order],
                  zorder=3, label=order)
        ax_a.errorbar(means, y + off, xerr=stds, fmt="none",
                      ecolor=INK_MUTED, elinewidth=0.8, capsize=1.5, zorder=4)
    ax_a.set_yticks(y)
    ax_a.set_yticklabels([PRETTY.get(f, f) for f in families], fontsize=9,
                         color=INK)
    ax_a.invert_yaxis()
    ax_a.xaxis.grid(True, color=GRIDLINE, linewidth=0.8, zorder=0)
    ax_a.set_xlabel("Share of responses carrying the norm (%)",
                    color=INK_SECONDARY, fontsize=9.5)
    ax_a.set_title("A · Norm prevalence by condition (mean ± std across 20 runs each)",
                   color=INK, fontsize=10.5, loc="left")
    ax_a.legend(frameon=True, facecolor=SURFACE, edgecolor="none",
                framealpha=1, fontsize=8.5, labelcolor=INK_SECONDARY,
                loc="upper right")
    ax_a.set_xlim(0, 100)

    # Summary table next to A
    ax_txt = fig.add_subplot(gs[0, 7:])
    ax_txt.axis("off")
    lines = ["Per-condition corpus", ""]
    cond_caps = runs.groupby("order")["capsules"].sum()
    cond_occ = occ.groupby("order").size()
    for order in TASK_ORDERS:
        lines.append(f"{order}: 20 runs, {cond_caps[order]:,} responses, "
                     f"{cond_occ[order]:,} norm occurrences")
    lines += ["", "2-agent and 8-agent runs pooled", "(10 runs each per condition)."]
    ax_txt.text(0, 0.95, "\n".join(lines), va="top", fontsize=9,
                color=INK_SECONDARY, family="sans-serif")

    # --- B: spread over rounds, small multiples per norm -----------------
    top4 = top5[:4]
    caps_per_round = cond_caps / 10
    axes_b = []
    for j, f in enumerate(top4):
        ax = fig.add_subplot(gs[1, j * 3:(j + 1) * 3])
        style_axis(ax)
        axes_b.append(ax)
        for order in TASK_ORDERS:
            sub = occ[(occ["meme_family"] == f) & (occ["order"] == order)]
            pct = (sub.groupby("round")["capsule_id"].nunique()
                   .reindex(range(1, 11), fill_value=0)
                   / caps_per_round[order] * 100)
            ax.plot(pct.index, pct.values, color=ORDER_COLORS[order],
                    linewidth=2, marker="o", markersize=3.5, label=order,
                    zorder=3)
        ax.yaxis.grid(True, color=GRIDLINE, linewidth=0.8, zorder=0)
        ax.set_xticks([1, 4, 7, 10])
        ax.set_ylim(0, 100)
        ax.set_title(PRETTY[f], color=INK, fontsize=9.5, loc="left")
        ax.set_xlabel("Round", color=INK_SECONDARY, fontsize=9)
        if j == 0:
            ax.set_ylabel("Share of responses (%)", color=INK_SECONDARY,
                          fontsize=9)
            ax.legend(frameon=True, facecolor=SURFACE, edgecolor="none",
                      framealpha=1, fontsize=7.5, labelcolor=INK_SECONDARY,
                      loc="lower right")
        else:
            ax.tick_params(labelleft=False)
    axes_b[0].annotate("B · How norms spread over rounds, by condition",
                       xy=(0, 1.22), xycoords="axes fraction", fontsize=10.5,
                       color=INK, fontweight="normal", ha="left")

    # --- D: variant transitions per condition ----------------------------
    dominant = top5[0]
    variants = ["fixed_fraction", "responsive_reward", "general_fairness"]
    nice = [v.replace("_", "\n") for v in variants]
    last_im = None
    for j, order in enumerate(TASK_ORDERS):
        ax = fig.add_subplot(gs[2, j * 4:(j + 1) * 4 - 1])
        style_axis(ax)
        pr = tr[(tr["meme_family"] == dominant) & (tr["retained"] == 1)
                & (tr["order"] == order)]
        mat = (pd.crosstab(pr["parent_variant"], pr["child_variant"])
               .reindex(index=variants, columns=variants, fill_value=0))
        row_pct = mat.div(mat.sum(axis=1).replace(0, np.nan), axis=0) * 100
        last_im = ax.imshow(row_pct, cmap=SEQ_BLUES, vmin=0, vmax=100)
        ax.set_xticks(range(3))
        ax.set_yticks(range(3))
        ax.set_xticklabels(nice, fontsize=8, color=INK)
        ax.set_yticklabels(nice if j == 0 else [], fontsize=8, color=INK)
        for i in range(3):
            for k in range(3):
                val = row_pct.iloc[i, k]
                if not np.isnan(val):
                    ax.annotate(f"{val:.0f}%", (k, i), ha="center",
                                va="center", fontsize=8.5,
                                color="#ffffff" if val > 55 else INK)
        ax.set_title(f"{order} (n={int(mat.to_numpy().sum()):,})",
                     color=INK, fontsize=9.5, loc="left")
        if j == 0:
            ax.set_ylabel("From parent formulation…", color=INK_SECONDARY,
                          fontsize=9)
        ax.set_xlabel("…to child formulation", color=INK_SECONDARY, fontsize=9)
        if j == 0:
            ax.annotate(
                f"D · {PRETTY[dominant]}: formulation transitions per condition",
                xy=(0, 1.28), xycoords="axes fraction", fontsize=10.5,
                color=INK, ha="left")
    cax = fig.add_subplot(gs[2, 11])
    cbar = fig.colorbar(last_im, cax=cax, shrink=0.7)
    cbar.set_label("Row share (%)", color=INK_SECONDARY, fontsize=8.5)
    cbar.ax.tick_params(colors=INK_MUTED, labelsize=8)
    cbar.outline.set_visible(False)

    fig.text(0.01, 0.005,
             "Same corpus as the pooled overview; 2- and 8-agent runs pooled "
             "within each task order. Panel C (routes) is unchanged from the "
             "pooled figure and omitted here.",
             fontsize=8, color=INK_MUTED)

    out = os.path.join(output_dir, "meme_evolution_by_condition.png")
    fig.savefig(out, dpi=200, facecolor=SURFACE, bbox_inches="tight")
    print(f"Saved {out}")


if __name__ == "__main__":
    main()

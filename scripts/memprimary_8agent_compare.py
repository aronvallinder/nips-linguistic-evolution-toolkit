#!/usr/bin/env python3
"""Compare the fixed 8-agent memory-primary runs against the June 8 baseline.

Baseline: sonnet45_8agent_myth_directive_history3_anon_r10_n5 (double memory).
Fixed:    sonnet45_8agent_myth_directive_history3_anon_memprimary_r10_n5.

Outputs (styled after analyses/trajectory_boxplot.py):
- condition_comparison.png: 2x2 boxplots (trust ratio, return ratio, sent,
  cooperation stability), one box per condition
- myth_comparison.png: boxplots of population myth similarity and per-agent
  self-similarity (round r vs r-1)
- trajectories.png: per-round sent / return ratio, thin line per run, bold mean

Usage: python scripts/memprimary_8agent_compare.py [--out DIR]
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))
from analyses._shared import calculate_return_ratios, configure_matplotlib

ENDOWMENT = 5.0

CONDITION_LABELS = {
    "baseline": "Baseline (Double Memory)",
    "fixed": "Memory-Primary (Fixed)",
}
# Same palette family as trajectory_boxplot.py's condition colors (Set2).
CONDITION_COLORS = {
    "baseline": "#66c2a5",
    "fixed": "#fc8d62",
}


def load_runs(condition_dir):
    runs = []
    for path in sorted(Path(condition_dir).rglob("*.json")):
        if path.name.endswith((".results.json", ".checkpoint.json", ".error.json")):
            continue
        with open(path) as f:
            runs.append(json.load(f))
    return runs


def per_round_game(run):
    """Mean sent and return ratio per round across that round's dyads."""
    sent_rounds, rr_rounds = [], []
    for entry in run.get("conversation_history", []):
        dyads = [d for d in entry.get("dyads") or [] if d.get("sent") is not None]
        if not dyads:
            continue
        sent_rounds.append(np.mean([d["sent"] for d in dyads]))
        returned = [d["returned"] for d in dyads if d.get("returned") is not None]
        received = [d["received"] for d in dyads if d.get("returned") is not None]
        ratios = calculate_return_ratios(returned, received)
        observed = ratios[np.isfinite(ratios)]
        rr_rounds.append(float(np.mean(observed)) if observed.size else np.nan)
    return np.array(sent_rounds), np.array(rr_rounds)


def myth_metrics(run, model):
    """Population convergence and per-agent drift from myth embeddings."""
    from sentence_transformers import util

    rounds = []
    for entry in run.get("conversation_history", []):
        myths = entry.get("myths") or {}
        if myths:
            rounds.append((entry["round"], dict(sorted(myths.items()))))
    if not rounds:
        return np.array([]), np.array([])

    agents = list(rounds[0][1])
    texts, index = [], {}
    for r, myths in rounds:
        for a, text in myths.items():
            index[(r, a)] = len(texts)
            texts.append(text)
    emb = model.encode(texts, convert_to_tensor=True, show_progress_bar=False)
    sim = util.cos_sim(emb, emb).cpu().numpy()

    cross = []
    for r, myths in rounds:
        idx = [index[(r, a)] for a in myths]
        pair_vals = [sim[i, j] for k, i in enumerate(idx) for j in idx[k + 1:]]
        cross.append(float(np.mean(pair_vals)))

    drift = []
    for (r_prev, m_prev), (r_cur, m_cur) in zip(rounds, rounds[1:]):
        vals = [
            sim[index[(r_prev, a)], index[(r_cur, a)]]
            for a in agents
            if a in m_prev and a in m_cur
        ]
        drift.append(float(np.mean(vals)))
    return np.array(cross), np.array(drift)


def stack_mean_std(series_list):
    n = min(len(s) for s in series_list)
    arr = np.stack([s[:n] for s in series_list])
    return np.nanmean(arr, axis=0), np.nanstd(arr, axis=0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--baseline", default="data/json/sonnet45_8agent_myth_directive_history3_anon_r10_n5"
    )
    parser.add_argument(
        "--fixed",
        default="data/json/sonnet45_8agent_myth_directive_history3_anon_memprimary_r10_n5",
    )
    parser.add_argument("--out", default="data/plots/memprimary_8agent")
    parser.add_argument("--baseline-label", default=None)
    parser.add_argument("--fixed-label", default=None)
    args = parser.parse_args()
    if args.baseline_label:
        CONDITION_LABELS["baseline"] = args.baseline_label
    if args.fixed_label:
        CONDITION_LABELS["fixed"] = args.fixed_label

    configure_matplotlib()
    import matplotlib.pyplot as plt
    import pandas as pd
    import seaborn as sns
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer("all-mpnet-base-v2")
    conditions = {
        "baseline": load_runs(args.baseline),
        "fixed": load_runs(args.fixed),
    }
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    results = {}
    rows = []
    for cond, runs in conditions.items():
        print(f"{CONDITION_LABELS[cond]}: {len(runs)} runs")
        sents, rrs, crosses, drifts = [], [], [], []
        for run in runs:
            s, r = per_round_game(run)
            c, d = myth_metrics(run, model)
            sents.append(s)
            rrs.append(r)
            crosses.append(c)
            drifts.append(d)
            rows.append({
                "Condition": CONDITION_LABELS[cond],
                "Mean Trust Ratio": float(np.mean(s)) / ENDOWMENT,
                "Mean Return Ratio": float(np.nanmean(r)),
                "Mean Sent": float(np.mean(s)),
                "Cooperation Stability": float(np.nanstd(r)),
                "Population Myth Similarity": float(np.mean(c)),
                "Self Myth Similarity": float(np.mean(d)),
            })
        results[cond] = {"sent": sents, "rr": rrs, "cross": crosses, "drift": drifts}

    df = pd.DataFrame(rows)
    condition_order = [CONDITION_LABELS[c] for c in conditions]

    print("\n=== Run-level means ===")
    for col in df.columns[1:]:
        parts = []
        for label in condition_order:
            v = df[df["Condition"] == label][col]
            parts.append(f"{label}: {v.mean():.3f} (±{v.std(ddof=0):.3f})")
        print(f"{col:28s} " + "  ".join(parts))

    # Set style (same as trajectory_boxplot.py)
    sns.set_style("whitegrid")

    # --- Figure 1: condition comparison boxplots (layout of condition_comparison.png) ---
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Cooperation Patterns: Double Memory vs Memory-Primary',
                 fontsize=16, fontweight='bold')

    ax1 = axes[0, 0]
    sns.boxplot(data=df, x='Condition', y='Mean Trust Ratio',
                order=condition_order, ax=ax1, palette='Set2')
    ax1.set_title('Trust Ratio (Proportion Sent)', fontweight='bold', fontsize=13)
    ax1.set_ylabel('Mean Trust Ratio (0-1)', fontsize=11)
    ax1.set_xlabel('')
    ax1.tick_params(axis='x', rotation=15)
    ax1.set_ylim(0, 1)
    ax1.set_yticks(np.arange(0, 1.1, 0.1))

    ax2 = axes[0, 1]
    sns.boxplot(data=df, x='Condition', y='Mean Return Ratio',
                order=condition_order, ax=ax2, palette='Set2')
    ax2.set_title('Return Ratio (Proportion Returned)', fontweight='bold', fontsize=13)
    ax2.set_ylabel('Mean Return Ratio (0-1)', fontsize=11)
    ax2.set_xlabel('')
    ax2.tick_params(axis='x', rotation=15)
    ax2.set_ylim(0, 1)
    ax2.set_yticks(np.arange(0, 1.1, 0.1))

    ax3 = axes[1, 0]
    sns.boxplot(data=df, x='Condition', y='Mean Sent',
                order=condition_order, ax=ax3, palette='Set2')
    ax3.set_title('Amount Sent by Investors', fontweight='bold', fontsize=13)
    ax3.set_ylabel('Mean Amount Sent', fontsize=11)
    ax3.set_xlabel('Condition', fontsize=11)
    ax3.tick_params(axis='x', rotation=15)
    ax3.set_ylim(bottom=0)

    ax4 = axes[1, 1]
    sns.boxplot(data=df, x='Condition', y='Cooperation Stability',
                order=condition_order, ax=ax4, palette='Set2')
    ax4.set_title('Cooperation Stability (Lower = More Stable)', fontweight='bold', fontsize=13)
    ax4.set_ylabel('Std Dev of Return Ratio', fontsize=11)
    ax4.set_xlabel('Condition', fontsize=11)
    ax4.tick_params(axis='x', rotation=15)
    ax4.set_ylim(bottom=0)

    plt.tight_layout()
    plt.savefig(out_dir / 'condition_comparison.png', dpi=300, bbox_inches='tight')
    print(f"Saved: {out_dir / 'condition_comparison.png'}")
    plt.close()

    # --- Figure 2: myth similarity boxplots (same style, 1x2) ---
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle('Myth Dynamics: Double Memory vs Memory-Primary',
                 fontsize=16, fontweight='bold')

    ax1 = axes[0]
    sns.boxplot(data=df, x='Condition', y='Population Myth Similarity',
                order=condition_order, ax=ax1, palette='Set2')
    ax1.set_title('Population Myth Similarity (All Pairs)', fontweight='bold', fontsize=13)
    ax1.set_ylabel('Mean Pairwise Cosine Similarity', fontsize=11)
    ax1.set_xlabel('Condition', fontsize=11)
    ax1.tick_params(axis='x', rotation=15)
    ax1.set_ylim(0, 1)
    ax1.set_yticks(np.arange(0, 1.1, 0.1))

    ax2 = axes[1]
    sns.boxplot(data=df, x='Condition', y='Self Myth Similarity',
                order=condition_order, ax=ax2, palette='Set2')
    ax2.set_title('Self Myth Similarity (Round r vs r-1)', fontweight='bold', fontsize=13)
    ax2.set_ylabel('Mean Cosine Similarity', fontsize=11)
    ax2.set_xlabel('Condition', fontsize=11)
    ax2.tick_params(axis='x', rotation=15)
    ax2.set_ylim(0, 1)
    ax2.set_yticks(np.arange(0, 1.1, 0.1))

    plt.tight_layout()
    plt.savefig(out_dir / 'myth_comparison.png', dpi=300, bbox_inches='tight')
    print(f"Saved: {out_dir / 'myth_comparison.png'}")
    plt.close()

    # --- Figure 3: per-round trajectories (style of cumulative_balances_by_condition) ---
    fig, axes = plt.subplots(1, 2, figsize=(18, 6))

    for ax, key, title, ylabel in [
        (axes[0], "sent", "Amount Sent per Round", "Mean Amount Sent"),
        (axes[1], "rr", "Return Ratio per Round", "Mean Return Ratio"),
    ]:
        for cond in conditions:
            color = CONDITION_COLORS[cond]
            for s in results[cond][key]:
                ax.plot(np.arange(1, len(s) + 1), s, linewidth=1,
                        color=color, alpha=0.35)
            mean, _ = stack_mean_std(results[cond][key])
            ax.plot(np.arange(1, len(mean) + 1), mean, linewidth=3,
                    label=CONDITION_LABELS[cond], color=color, alpha=0.8)
        ax.set_xlabel('Round', fontsize=13, fontweight='bold')
        ax.set_ylabel(ylabel, fontsize=13, fontweight='bold')
        ax.set_title(title, fontsize=15, fontweight='bold')
        ax.legend(fontsize=11, loc='best')
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_ylim(bottom=0)

    plt.tight_layout()
    plt.savefig(out_dir / 'trajectories.png', dpi=300, bbox_inches='tight')
    print(f"Saved: {out_dir / 'trajectories.png'}")
    plt.close()


if __name__ == "__main__":
    main()

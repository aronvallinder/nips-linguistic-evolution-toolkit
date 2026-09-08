#!/usr/bin/env python3
"""Compare the memory-channel pilot conditions (hybrid vs stateless).

Loads all runs from the two memtest experiment dirs and reports, per condition:
- game behavior: sent and return ratio per round (mean ±std across reps)
- myth dynamics: cross-agent embedding similarity per round (convergence) and
  round-to-round self-similarity per agent (lineage inertia)

Usage:
    python scripts/memtest_compare.py \
        --hybrid data/json/memtest_hybrid_sonnet45_2agent_r10_n5 \
        --stateless data/json/memtest_stateless_sonnet45_2agent_r10_n5 \
        --out data/plots/memtest_memory_channels
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))
from analyses._shared import calculate_return_ratios, configure_matplotlib


def load_runs(condition_dir):
    runs = []
    for path in sorted(Path(condition_dir).rglob("*.json")):
        name = path.name
        if name.endswith((".results.json", ".checkpoint.json", ".error.json")):
            continue
        with open(path) as f:
            runs.append(json.load(f))
    return runs


def per_round_game(run):
    """Return (rounds, sent, return_ratio) arrays for one run."""
    rounds, sent, rr = [], [], []
    for entry in run.get("conversation_history", []):
        if entry.get("sent") is None or entry.get("returned") is None:
            continue
        rounds.append(entry["round"])
        sent.append(entry["sent"])
        received = entry.get("received") or 0
        rr.append(calculate_return_ratios([entry["returned"]], [received])[0])
    return np.array(rounds), np.array(sent, dtype=float), np.array(rr, dtype=float)


def myths_by_round(run):
    """Return {round: {agent_id: myth_text}} for rounds with both myths."""
    out = {}
    for entry in run.get("conversation_history", []):
        myths = entry.get("myths") or {}
        if len(myths) >= 2:
            out[entry["round"]] = myths
    return out


def embed_similarities(runs, model):
    """Per run: cross-agent cosine per round, and per-agent self-similarity
    between consecutive rounds. Returns (cross[rep][round_idx], self_sim[...])."""
    from sentence_transformers import util

    cross_all, self_all = [], []
    for run in runs:
        by_round = myths_by_round(run)
        rounds = sorted(by_round)
        agents = sorted(by_round[rounds[0]]) if rounds else []
        if len(agents) < 2:
            continue
        texts, index = [], {}
        for r in rounds:
            for a in agents:
                index[(r, a)] = len(texts)
                texts.append(by_round[r][a])
        emb = model.encode(texts, convert_to_tensor=True, show_progress_bar=False)
        sim = util.cos_sim(emb, emb).cpu().numpy()

        cross = [sim[index[(r, agents[0])], index[(r, agents[1])]] for r in rounds]
        self_sim = []
        for prev, cur in zip(rounds, rounds[1:]):
            vals = [sim[index[(prev, a)], index[(cur, a)]] for a in agents]
            self_sim.append(float(np.mean(vals)))
        cross_all.append(np.array(cross))
        self_all.append(np.array(self_sim))
    return cross_all, self_all


def final_balance(run):
    """Mean final cumulative balance per agent (last round with balances)."""
    for entry in reversed(run.get("conversation_history", [])):
        balances = entry.get("balances")
        if balances:
            return float(np.mean(list(balances.values())))
    return 0.0


def stack_mean_std(series_list):
    n = min(len(s) for s in series_list)
    arr = np.stack([s[:n] for s in series_list])
    return np.nanmean(arr, axis=0), np.nanstd(arr, axis=0)


def welch(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    a = a[np.isfinite(a)]
    b = b[np.isfinite(b)]
    if len(a) < 2 or len(b) < 2:
        return None, None
    try:
        from scipy import stats

        t, p = stats.ttest_ind(a, b, equal_var=False)
        return float(t), float(p)
    except ImportError:
        return None, None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hybrid", default="data/json/memtest_hybrid_sonnet45_2agent_r10_n5")
    parser.add_argument("--stateless", default="data/json/memtest_stateless_sonnet45_2agent_r10_n5")
    parser.add_argument(
        "--memory-primary", default="data/json/memtest_memoryprimary_sonnet45_2agent_r10_n5"
    )
    parser.add_argument("--out", default="data/plots/memtest_memory_channels")
    args = parser.parse_args()

    configure_matplotlib()
    import matplotlib.pyplot as plt
    from sentence_transformers import SentenceTransformer

    conditions = {
        "hybrid": load_runs(args.hybrid),
        "stateless": load_runs(args.stateless),
        "memory_primary": load_runs(args.memory_primary),
    }
    conditions = {k: v for k, v in conditions.items() if v}
    for name, runs in conditions.items():
        print(f"{name}: {len(runs)} runs")

    model = SentenceTransformer("all-mpnet-base-v2")

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    game = {}
    myth = {}
    summary = {}
    for name, runs in conditions.items():
        sents, rrs = [], []
        for run in runs:
            _, sent, rr = per_round_game(run)
            sents.append(sent)
            rrs.append(rr)
        cross, self_sim = embed_similarities(runs, model)
        game[name] = (sents, rrs)
        myth[name] = (cross, self_sim)
        summary[name] = {
            "mean_sent_per_run": [float(np.mean(s)) for s in sents],
            "mean_return_ratio_per_run": [float(np.nanmean(r)) for r in rrs],
            "mean_cross_sim_per_run": [float(np.mean(c)) for c in cross],
            "mean_self_sim_per_run": [float(np.mean(s)) for s in self_sim],
            "final_balance_per_run": [final_balance(run) for run in runs],
        }

    print("\n=== Run-level means (each n = number of runs) ===")
    metrics = [
        ("mean_sent_per_run", "sent ($/round)"),
        ("mean_return_ratio_per_run", "return ratio"),
        ("mean_cross_sim_per_run", "cross-agent myth sim"),
        ("mean_self_sim_per_run", "self myth sim (r vs r-1)"),
        ("final_balance_per_run", "final balance ($/agent)"),
    ]
    names = list(conditions)
    for key, label in metrics:
        parts = []
        for name in names:
            v = np.array(summary[name][key])
            parts.append(f"{name} {np.nanmean(v):.3f} (±{np.nanstd(v):.3f})")
        print(f"{label:26s} " + "  ".join(parts))
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a = np.array(summary[names[i]][key])
                b = np.array(summary[names[j]][key])
                t, p = welch(a, b)
                if p is not None:
                    print(f"{'':26s}   {names[i]} vs {names[j]}: Welch t={t:.2f} p={p:.3f}")

    panels = [
        ("Sent per round ($)", [(n, stack_mean_std(game[n][0])) for n in conditions]),
        ("Return ratio per round", [(n, stack_mean_std(game[n][1])) for n in conditions]),
        ("Cross-agent myth similarity", [(n, stack_mean_std(myth[n][0])) for n in conditions]),
        ("Self myth similarity (round r vs r-1)", [(n, stack_mean_std(myth[n][1])) for n in conditions]),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    colors = {"hybrid": "tab:blue", "stateless": "tab:orange", "memory_primary": "tab:green"}
    for ax, (title, series) in zip(axes.flat, panels):
        for name, (mean, std) in series:
            x = np.arange(1, len(mean) + 1)
            ax.plot(x, mean, label=name, color=colors[name])
            ax.fill_between(x, mean - std, mean + std, alpha=0.2, color=colors[name])
        ax.set_title(title)
        ax.set_xlabel("Round")
        ax.legend()
    fig.suptitle("Memory-channel pilot (Sonnet 4.5, 2-agent dyads, n=5 per condition)")
    fig.tight_layout()
    fig_path = out_dir / "memtest_comparison.png"
    fig.savefig(fig_path, dpi=150)
    print(f"\nFigure: {fig_path}")

    # Final cumulative balance boxplot (layout of
    # trajectory_boxplot.py::plot_cumulative_balances_boxplot_by_condition)
    import pandas as pd
    import seaborn as sns

    sns.set_style("whitegrid")
    rows = [
        {"Condition": name, "Final Cumulative Balance": v}
        for name in conditions
        for v in summary[name]["final_balance_per_run"]
    ]
    df = pd.DataFrame(rows)
    fig, ax = plt.subplots(figsize=(10, 7))
    sns.boxplot(data=df, x='Condition', y='Final Cumulative Balance',
                order=list(conditions), ax=ax, palette='Set2')
    ax.set_title('Final Cumulative Balances by Condition', fontweight='bold', fontsize=14)
    ax.set_ylabel('Final Cumulative Balance (Average per Agent)', fontsize=12)
    ax.set_xlabel('Condition', fontsize=12)
    ax.tick_params(axis='x', rotation=15)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(bottom=0)
    plt.tight_layout()
    plt.savefig(out_dir / 'cumulative_balance_boxplot_by_condition.png', dpi=300, bbox_inches='tight')
    print(f"Figure: {out_dir / 'cumulative_balance_boxplot_by_condition.png'}")
    plt.close()

    with open(out_dir / "memtest_summary.json", "w") as f:
        json.dump(summary, f, indent=2)


if __name__ == "__main__":
    main()

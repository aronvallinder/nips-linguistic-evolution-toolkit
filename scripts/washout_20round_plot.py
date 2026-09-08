#!/usr/bin/env python3
"""Wash-out test: does the Myth->Game advantage survive 20 rounds?
Left: per-round send (myth_game plateaus; game_myth cold-opens low, climbs, and
overtakes ~round 6). Right: myth_game's cumulative-balance lead shrinks to ~0 by
round 20. The round-10 line marks where the original 'myth_game > game_myth'
headline was measured. 2-agent, corrected code, n=5/arm (preview)."""
import json
from pathlib import Path
import numpy as np

WD = "data/json/noise_experiments/washout_20round"
COL = {"Myth→Game": "#4C72B0", "Game→Myth": "#DD8452"}


def load(s):
    out = []
    for p in Path(f"{WD}/{s}").rglob("*.json"):
        if p.name.endswith((".results.json", ".checkpoint.json", ".error.json")):
            continue
        r = json.load(open(p))
        if len(r["conversation_history"]) == 20:
            out.append(r)
    return out


def sends(r):
    return np.array([np.mean([d["sent"] for d in e.get("dyads", []) if d.get("sent") is not None])
                     for e in r["conversation_history"]])


def cumbal(r):
    return np.array([np.mean(list(e["balances"].values())) if e.get("balances") else np.nan
                     for e in r["conversation_history"]])


def main():
    import argparse
    import matplotlib.pyplot as plt
    import seaborn as sns
    ap = argparse.ArgumentParser()
    ap.add_argument("--prefix", default="noise2i", choices=["noise2i", "noise8i"],
                    help="experiment-set prefix: noise2i (2-agent) or noise8i (8-agent)")
    args = ap.parse_args()
    label = "2-agent" if args.prefix == "noise2i" else "8-agent"
    sns.set_style("whitegrid")
    mg = load(f"{args.prefix}_washout_myth_game")
    gm = load(f"{args.prefix}_washout_game_myth")
    rounds = np.arange(1, 21)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    for runs, name in [(mg, "Myth→Game"), (gm, "Game→Myth")]:
        S = np.vstack([sends(r) for r in runs])
        m, se = np.nanmean(S, 0), np.nanstd(S, 0) / np.sqrt(len(runs))
        ax1.plot(rounds, m, color=COL[name], lw=2.2, label=f"{name} (n={len(runs)})")
        ax1.fill_between(rounds, m - se, m + se, color=COL[name], alpha=0.13)
    ax1.axvline(10, color="grey", ls=":", alpha=0.7)
    ax1.text(10.2, 2.7, "10-round\nheadline", fontsize=8, color="grey")
    ax1.set_title("Per-round mean send", fontweight="bold")
    ax1.set_xlabel("Round"); ax1.set_ylabel("Mean amount sent ($ of $5)")
    ax1.set_ylim(2.5, 5.0); ax1.legend(); ax1.grid(alpha=0.3)

    Cmg = np.nanmean(np.vstack([cumbal(r) for r in mg]), 0)
    Cgm = np.nanmean(np.vstack([cumbal(r) for r in gm]), 0)
    lead = Cmg - Cgm
    ax2.plot(rounds, lead, color="#555", lw=2.4, marker="o", ms=4)
    ax2.axhline(0, color="black", lw=0.8)
    ax2.axvline(10, color="grey", ls=":", alpha=0.7)
    ax2.fill_between(rounds, 0, lead, where=lead >= 0, color=COL["Myth→Game"], alpha=0.18)
    ax2.set_title(f"Myth→Game cumulative lead: {lead[9]:+.1f} at round 10, {lead[19]:+.1f} at round 20",
                  fontweight="bold")
    ax2.set_xlabel("Round"); ax2.set_ylabel("Myth→Game minus Game→Myth\n(cumulative balance/agent, $)")
    ax2.grid(alpha=0.3)

    fig.suptitle(f"Wash-out test ({label}, corrected code, n={len(mg)}/{len(gm)} per arm): does the Myth→Game edge survive 20 rounds?",
                 fontweight="bold", fontsize=13)
    plt.tight_layout()
    out = Path("data/plots/myth_taskorder_trajectories")
    out.mkdir(parents=True, exist_ok=True)
    fp = out / ("washout_20round.png" if args.prefix == "noise2i" else f"washout_20round_{label}.png")
    plt.savefig(fp, dpi=300, bbox_inches="tight")
    print(f"Saved: {fp}")
    print(f"n: myth_game={len(mg)}, game_myth={len(gm)}")
    for rd in (9, 19):
        print(f"round {rd+1}: cumbal myth_game={Cmg[rd]:.1f}, game_myth={Cgm[rd]:.1f}, lead={lead[rd]:+.1f}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Send + return-ratio trajectories, Myth->Game vs Game->Myth, on Aron's
corrected confirmatory data. Shows: the effect is a SEND effect, born at round 1
(game_myth cold-opens at a deterministic $3; myth_game opens ~$4), narrowing but
not closing by round 10; return ratio is flat ~0.5 across everything.

Usage: python scripts/myth_game_vs_game_myth_trajectories.py [--out DIR]
"""
import argparse, json
from pathlib import Path
import numpy as np

CB = ("data/share/corrected_informed_noise_confirmatory_60runs_2026-08-12/data")
CELLS = {
    ("2-agent", "Myth→Game"): "noise2i_memprimary_v2_myth_game",
    ("2-agent", "Game→Myth"): "noise2i_memprimary_v2_game_myth",
    ("8-agent", "Myth→Game"): "noise8i_memprimary_v2_myth_game",
    ("8-agent", "Game→Myth"): "noise8i_memprimary_v2_game_myth",
}
COLORS = {"Myth→Game": "#4C72B0", "Game→Myth": "#DD8452"}
STYLE = {"2-agent": "-", "8-agent": "--"}


def series(run):
    sends, rets = [], []
    for e in run.get("conversation_history", []):
        ds = [x for x in (e.get("dyads") or []) if isinstance(x, dict)]
        s = [x["sent"] for x in ds if x.get("sent") is not None]
        rr = [x["returned"] / x["received"] for x in ds
              if x.get("received") not in (None, 0) and x.get("returned") is not None]
        sends.append(np.mean(s) if s else np.nan)
        rets.append(np.mean(rr) if rr else np.nan)
    return np.array(sends), np.array(rets)


def load(cell):
    runs = [json.load(open(p)) for p in Path(f"{CB}/{cell}").rglob("*.json")
            if not p.name.endswith((".results.json", ".checkpoint.json", ".error.json"))]
    S = np.vstack([series(r)[0] for r in runs])
    R = np.vstack([series(r)[1] for r in runs])
    return S, R


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/plots/myth_taskorder_trajectories")
    args = ap.parse_args()
    import matplotlib.pyplot as plt
    import seaborn as sns
    sns.set_style("whitegrid")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    rounds = np.arange(1, 11)
    for (pop, order), cell in CELLS.items():
        S, R = load(cell)
        m, se = np.nanmean(S, 0), np.nanstd(S, 0) / np.sqrt(S.shape[0])
        ax1.plot(rounds, m, STYLE[pop], color=COLORS[order], lw=2,
                 label=f"{order}, {pop}")
        ax1.fill_between(rounds, m - se, m + se, color=COLORS[order], alpha=0.12)
        rm = np.nanmean(R, 0)
        ax2.plot(rounds, rm, STYLE[pop], color=COLORS[order], lw=2,
                 label=f"{order}, {pop}")
    ax1.set_title("Amount sent per round\n(the effect: send-side, born at round 1)",
                  fontweight="bold")
    ax1.set_xlabel("Round"); ax1.set_ylabel("Mean amount sent ($ of $5)")
    ax1.set_ylim(2.5, 5.0); ax1.legend(fontsize=9); ax1.grid(alpha=0.3)
    ax2.set_title("Return ratio per round\n(inert: ~0.5 across all conditions)",
                  fontweight="bold")
    ax2.set_xlabel("Round"); ax2.set_ylabel("Mean return ratio (returned / received)")
    ax2.set_ylim(0.0, 1.0); ax2.axhline(0.5, color="grey", ls=":", alpha=0.6)
    ax2.legend(fontsize=9); ax2.grid(alpha=0.3)
    fig.suptitle("Myth→Game vs Game→Myth (Aron's corrected confirmatory data, n=10/cell)",
                 fontweight="bold", fontsize=13)
    plt.tight_layout()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    fp = out / "send_and_return_trajectories.png"
    plt.savefig(fp, dpi=300, bbox_inches="tight")
    print(f"Saved: {fp}")


if __name__ == "__main__":
    main()

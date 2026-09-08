#!/usr/bin/env python3
"""Strategy labelling + within-run change-point detection for trust-game runs.

Three levels of output per run:
  1. Role-specific strategy label for each agent
       - investor: high_trust | no_trust | moderate | variable
       - trustee:  generous  | defecting | moderate | variable
  2. Dyadic strategy label (combines both agents' behaviour)
       - always_cooperate | mutual_defect | exploitative_A1 | exploitative_A2
       - tit_for_tat      | grim_trigger | escalating_trust | mixed
  3. Per-agent per-role change points in the action time series
       (mean-shift splitter, no external libraries).

Aggregates across (model × noise × task_order) cells to test whether myth
presence shifts the dyadic-strategy mix or the within-run switch rate.

Purely numerical — no LLM calls, zero API cost.

Example:
    python analyses/strategy_detection.py \
        --input-root data/json/noise_experiments/v2_uniform_distribution_noise \
        --also-scan data/json/baseline \
        --output-dir data/plots/noise_experiments/v2_uniform_distribution_noise/_strategies
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# ----- strategy thresholds ---------------------------------------------------

INV_HIGH = 4.0       # send >= 80% of $5 endowment
INV_LOW = 0.5        # send <= 10%
INV_VAR_STD = 1.5    # std of send series for "variable"

TRU_HIGH = 0.40      # return rate >= 40% (of received)
TRU_LOW = 0.10
TRU_VAR_STD = 0.25   # std of return-rate series for "variable"

# Change-point: split at k, flag switch if |mean_left - mean_right| / pooled_std > SWITCH_Z
SWITCH_Z = 1.5
MIN_RUN = 3          # require at least 3 rounds on each side


# ----- extraction ------------------------------------------------------------

def iter_valid_jsons(root: Path) -> list[Path]:
    return sorted(
        p for p in root.rglob("*.json")
        if ".checkpoint" not in p.name and ".results" not in p.name
    )


def extract_role_series(data: dict) -> dict:
    """Return per-agent investor_sends and trustee_return_rates, in round order."""
    agents = ["Agent_1", "Agent_2"]
    out = {a: {"investor_rounds": [], "investor_sends": [],
               "trustee_rounds": [], "trustee_return_rates": [],
               "trustee_returns": [], "trustee_received": []}
           for a in agents}

    for entry in data.get("conversation_history", []) or []:
        r = entry.get("round")
        roles = entry.get("roles") or {}
        sent = entry.get("sent")
        returned = entry.get("returned")
        received = entry.get("received")
        if sent is None or returned is None:
            continue

        for a in agents:
            role = roles.get(a)
            if role == "investor":
                out[a]["investor_rounds"].append(r)
                out[a]["investor_sends"].append(float(sent))
            elif role == "trustee":
                # Zero received means there was no possible return decision;
                # do not classify that round as trustee defection.
                if received is None or float(received) <= 0:
                    continue
                out[a]["trustee_rounds"].append(r)
                rate = float(returned) / float(received)
                out[a]["trustee_return_rates"].append(rate)
                out[a]["trustee_returns"].append(float(returned))
                out[a]["trustee_received"].append(float(received))

    return out


# ----- labellers -------------------------------------------------------------

def label_investor(sends: list[float]) -> str:
    if not sends:
        return "unknown"
    arr = np.asarray(sends, dtype=float)
    if arr.std() >= INV_VAR_STD:
        return "variable"
    m = arr.mean()
    if m >= INV_HIGH:
        return "high_trust"
    if m <= INV_LOW:
        return "no_trust"
    return "moderate"


def label_trustee(return_rates: list[float]) -> str:
    if not return_rates:
        return "unknown"
    arr = np.asarray(return_rates, dtype=float)
    if arr.std() >= TRU_VAR_STD:
        return "variable"
    m = arr.mean()
    if m >= TRU_HIGH:
        return "generous"
    if m <= TRU_LOW:
        return "defecting"
    return "moderate"


def label_dyad(series: dict) -> str:
    """Combine both agents' behaviour into a dyadic-strategy label."""
    a1, a2 = "Agent_1", "Agent_2"
    inv1 = label_investor(series[a1]["investor_sends"])
    tru1 = label_trustee(series[a1]["trustee_return_rates"])
    inv2 = label_investor(series[a2]["investor_sends"])
    tru2 = label_trustee(series[a2]["trustee_return_rates"])

    # Pure cases
    if inv1 == inv2 == "high_trust" and tru1 == tru2 == "generous":
        return "always_cooperate"
    if inv1 == inv2 == "no_trust" and tru1 == tru2 == "defecting":
        return "mutual_defect"
    # Exploitative: one agent high-trust-investor paired with the other being
    # defecting-trustee while the roles in between are asymmetric.
    if inv1 == "high_trust" and tru2 == "defecting" and tru1 != "defecting":
        return "exploitative_by_A2"
    if inv2 == "high_trust" and tru1 == "defecting" and tru2 != "defecting":
        return "exploitative_by_A1"

    # Reciprocity signatures: correlate send_t with partner's preceding return-rate.
    # Use all investor observations and look at the return-rate the partner gave
    # in the round immediately before (if available).
    def tit_for_tat_score(agent: str, partner: str) -> float:
        sends = series[agent]["investor_sends"]
        s_rounds = series[agent]["investor_rounds"]
        # Partner's return-rates in rounds that the partner was trustee, indexed by round number.
        p_rates = dict(zip(series[partner]["trustee_rounds"], series[partner]["trustee_return_rates"]))
        x, y = [], []
        for s, r in zip(sends, s_rounds):
            prev_rate = None
            for k in sorted(p_rates.keys()):
                if k < r:
                    prev_rate = p_rates[k]
            if prev_rate is not None:
                x.append(prev_rate)
                y.append(s)
        if len(x) < 3:
            return float("nan")
        return float(np.corrcoef(x, y)[0, 1]) if np.std(x) > 0 and np.std(y) > 0 else float("nan")

    tft1 = tit_for_tat_score("Agent_1", "Agent_2")
    tft2 = tit_for_tat_score("Agent_2", "Agent_1")
    if np.nanmean([tft1, tft2]) > 0.6:
        return "tit_for_tat"

    # Grim trigger: at least one dyad member transitions from non-zero to 0-sending
    # after a defection event and stays at 0.
    for a in (a1, a2):
        sends = series[a]["investor_sends"]
        if len(sends) >= 4 and sends[0] > 0.5 and all(s == 0 for s in sends[-2:]) and sends[0] > 1:
            return "grim_trigger"

    # Escalating: monotone increase in a role's send series (slope > 0.3 per round, std > 0.5)
    for a in (a1, a2):
        sends = np.asarray(series[a]["investor_sends"], dtype=float)
        if len(sends) >= 4 and sends.std() >= 0.5:
            rounds = np.asarray(series[a]["investor_rounds"], dtype=float)
            slope = np.polyfit(rounds, sends, 1)[0]
            if slope >= 0.3:
                return "escalating_trust"

    return "mixed"


# ----- change-point detection ------------------------------------------------

def find_change_point(series: list[float]) -> dict | None:
    """Simple mean-shift splitter. Returns best split if any is significant."""
    if len(series) < 2 * MIN_RUN:
        return None
    arr = np.asarray(series, dtype=float)
    n = len(arr)
    best = None
    for k in range(MIN_RUN, n - MIN_RUN + 1):
        left, right = arr[:k], arr[k:]
        var_left = left.var(ddof=0)
        var_right = right.var(ddof=0)
        pooled = np.sqrt(((var_left * len(left)) + (var_right * len(right))) / n)
        pooled = max(pooled, 0.1)
        z = abs(left.mean() - right.mean()) / pooled
        if z >= SWITCH_Z and (best is None or z > best["z"]):
            best = {"split_index": int(k), "z": float(z),
                    "mean_left": float(left.mean()), "mean_right": float(right.mean()),
                    "n_left": len(left), "n_right": len(right)}
    return best


def detect_switches(series: dict) -> list[dict]:
    """Find change-points in both role-series for each agent. Returns a row per
    detected switch."""
    out = []
    for agent in ["Agent_1", "Agent_2"]:
        # Investor sends
        inv_rounds = series[agent]["investor_rounds"]
        inv_sends = series[agent]["investor_sends"]
        if len(inv_sends) >= 2 * MIN_RUN:
            cp = find_change_point(inv_sends)
            if cp:
                out.append({
                    "agent": agent, "role": "investor", "metric": "send",
                    "split_round": inv_rounds[cp["split_index"]] if cp["split_index"] < len(inv_rounds) else inv_rounds[-1],
                    **{k: v for k, v in cp.items() if k != "split_index"},
                })
        # Trustee return rates
        tru_rounds = series[agent]["trustee_rounds"]
        tru_rates = series[agent]["trustee_return_rates"]
        if len(tru_rates) >= 2 * MIN_RUN:
            cp = find_change_point(tru_rates)
            if cp:
                out.append({
                    "agent": agent, "role": "trustee", "metric": "return_rate",
                    "split_round": tru_rounds[cp["split_index"]] if cp["split_index"] < len(tru_rounds) else tru_rounds[-1],
                    **{k: v for k, v in cp.items() if k != "split_index"},
                })
    return out


# ----- orchestration ---------------------------------------------------------

def classify_condition(path: Path, meta: dict) -> dict:
    parts = path.parts
    task_order = None
    experiment = None
    for p in parts:
        if p in {"game", "game_myth", "myth_game", "myth"}:
            task_order = p
        if p.startswith("noise_"):
            experiment = p

    gpn = meta.get("game_params_name") or ""
    if "_informed" in gpn:
        noise_condition = "noise_informed"
    elif gpn and gpn != "default":
        noise_condition = "noise"
    else:
        noise_condition = "no_noise"

    return {
        "model": meta.get("model"),
        "task_order": task_order,
        "experiment": experiment,
        "noise_condition": noise_condition,
        "game_params": gpn,
        "myth_topic": meta.get("myth_topic"),
    }


def analyse_run(path: Path) -> tuple[dict, list[dict]]:
    with open(path) as f:
        data = json.load(f)

    meta = data.get("run_metadata", {}) or {}
    info = classify_condition(path, meta)
    series = extract_role_series(data)

    dyad_row = {
        "path": str(path),
        **info,
        "agent_1_investor_label": label_investor(series["Agent_1"]["investor_sends"]),
        "agent_1_trustee_label":  label_trustee(series["Agent_1"]["trustee_return_rates"]),
        "agent_2_investor_label": label_investor(series["Agent_2"]["investor_sends"]),
        "agent_2_trustee_label":  label_trustee(series["Agent_2"]["trustee_return_rates"]),
        "dyad_strategy": label_dyad(series),
        "n_rounds": max(len(series["Agent_1"]["investor_sends"]) + len(series["Agent_1"]["trustee_return_rates"]),
                         len(series["Agent_2"]["investor_sends"]) + len(series["Agent_2"]["trustee_return_rates"])),
    }

    switches = detect_switches(series)
    switch_rows = [{"path": str(path), **info, **sw} for sw in switches]
    dyad_row["n_switches"] = len(switches)
    dyad_row["has_switch"] = len(switches) > 0

    return dyad_row, switch_rows


def build_dataframes(roots: list[Path]) -> tuple[pd.DataFrame, pd.DataFrame]:
    dyad_rows, switch_rows = [], []
    n_files = 0
    for root in roots:
        if not root.exists():
            print(f"WARNING: path not found: {root}")
            continue
        for p in iter_valid_jsons(root):
            try:
                d, sw = analyse_run(p)
            except Exception as e:  # noqa: BLE001
                print(f"  ! {p}: {type(e).__name__}: {e}")
                continue
            dyad_rows.append(d)
            switch_rows.extend(sw)
            n_files += 1
    print(f"Analysed {n_files} runs.")
    return pd.DataFrame(dyad_rows), pd.DataFrame(switch_rows)


# ----- summary + plots -------------------------------------------------------

def summarise_and_plot(dyad: pd.DataFrame, switches: pd.DataFrame, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    dyad.to_csv(output_dir / "dyad_strategies.csv", index=False)
    switches.to_csv(output_dir / "switches.csv", index=False)

    cells = dyad.dropna(subset=["model", "noise_condition", "task_order"]).copy()
    if cells.empty:
        return

    # Per-cell: strategy distribution + switch rate.
    strat_counts = (
        cells.groupby(["model", "noise_condition", "task_order", "dyad_strategy"])
             .size().unstack("dyad_strategy", fill_value=0)
    )
    strat_counts["total"] = strat_counts.sum(axis=1)
    for c in [x for x in strat_counts.columns if x != "total"]:
        strat_counts[f"{c}_pct"] = (strat_counts[c] / strat_counts["total"] * 100).round(1)
    strat_counts.to_csv(output_dir / "strategy_distribution.csv")
    print(f"Strategy distribution: {output_dir / 'strategy_distribution.csv'}")

    switch_rate = (
        cells.groupby(["model", "noise_condition", "task_order"])["has_switch"]
             .agg(["mean", "count"]).reset_index()
             .rename(columns={"mean": "switch_rate", "count": "n_dyads"})
    )
    switch_rate.to_csv(output_dir / "switch_rate_per_cell.csv", index=False)
    print(f"Switch rates: {output_dir / 'switch_rate_per_cell.csv'}")
    print(switch_rate.to_string(index=False))

    # Plot 1: stacked bar chart of dyadic strategies per (model × noise × task_order).
    strat_long = strat_counts.reset_index()
    all_strats = sorted({c for c in strat_counts.columns
                         if not c.endswith("_pct") and c != "total"})
    pct_cols = [f"{s}_pct" for s in all_strats]

    models = sorted(strat_long["model"].dropna().unique())
    noise_conds = sorted(strat_long["noise_condition"].dropna().unique())
    task_orders = sorted(strat_long["task_order"].dropna().unique())

    fig, axes = plt.subplots(
        len(models), len(noise_conds),
        figsize=(4.5 * len(noise_conds), 3.5 * len(models)),
        squeeze=False, sharey=True,
    )
    palette = plt.cm.tab20.colors
    strat_colors = {s: palette[i % 20] for i, s in enumerate(all_strats)}

    for i, m in enumerate(models):
        for j, nc in enumerate(noise_conds):
            ax = axes[i][j]
            sub = strat_long[(strat_long["model"] == m) & (strat_long["noise_condition"] == nc)]
            if sub.empty:
                ax.set_visible(False)
                continue
            sub = sub.set_index("task_order").reindex([t for t in task_orders if t in sub["task_order"].values])
            bottom = np.zeros(len(sub))
            for s, col in zip(all_strats, pct_cols):
                if col not in sub:
                    continue
                vals = sub[col].fillna(0).values
                ax.bar(sub.index.astype(str), vals, bottom=bottom, color=strat_colors[s], label=s)
                bottom = bottom + vals
            ax.set_title(f"{m} / {nc}", fontsize=9)
            ax.set_ylim(0, 100)
            if j == 0:
                ax.set_ylabel("% of dyads")
            ax.tick_params(axis="x", rotation=30)

    handles, labels = axes[0][0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="center right", fontsize=7, bbox_to_anchor=(1.12, 0.5))
    fig.suptitle("Dyadic strategy distribution per (model × noise × task_order)", fontweight="bold")
    plt.tight_layout()
    out = output_dir / "strategy_distribution.png"
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Plot: {out}")

    # Plot 2: switch rate heatmap
    fig, axes = plt.subplots(1, len(models), figsize=(4.5 * len(models), 3.5), squeeze=False)
    for i, m in enumerate(models):
        ax = axes[0][i]
        sub = switch_rate[switch_rate["model"] == m]
        if sub.empty:
            ax.set_visible(False)
            continue
        pivot = sub.pivot(index="task_order", columns="noise_condition", values="switch_rate")
        pivot = pivot.reindex(index=[t for t in task_orders if t in pivot.index],
                              columns=[n for n in noise_conds if n in pivot.columns])
        im = ax.imshow(pivot.values, cmap="Reds", vmin=0, vmax=1, aspect="auto")
        ax.set_xticks(range(len(pivot.columns)))
        ax.set_xticklabels(pivot.columns, rotation=30, fontsize=8)
        ax.set_yticks(range(len(pivot.index)))
        ax.set_yticklabels(pivot.index, fontsize=8)
        ax.set_title(m, fontsize=10)
        for ii in range(pivot.shape[0]):
            for jj in range(pivot.shape[1]):
                v = pivot.values[ii, jj]
                if not np.isnan(v):
                    ax.text(jj, ii, f"{v:.2f}", ha="center", va="center",
                            color="white" if v > 0.5 else "black", fontsize=9)
    fig.suptitle("Within-run strategy switch rate (fraction of dyads)", fontweight="bold")
    fig.colorbar(im, ax=axes.ravel().tolist(), shrink=0.8)
    out = output_dir / "switch_rate_heatmap.png"
    plt.savefig(out, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Plot: {out}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--input-root", required=True, help="Root directory to scan (recursive).")
    parser.add_argument("--also-scan", action="append", default=[], help="Additional root to scan.")
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    roots = [Path(args.input_root)] + [Path(p) for p in args.also_scan]
    output_dir = Path(args.output_dir)

    dyad, switches = build_dataframes(roots)
    print(f"\nDyads: {len(dyad)}  |  Switches detected: {len(switches)}")
    if dyad.empty:
        return

    summarise_and_plot(dyad, switches, output_dir)


if __name__ == "__main__":
    main()

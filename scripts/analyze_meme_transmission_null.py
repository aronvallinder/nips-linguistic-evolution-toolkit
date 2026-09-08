#!/usr/bin/env python3
"""Exposure-contrast and permutation-null tests for meme-family transmission.

``analyze_meme_evolution.py`` counts a transmission whenever a meme family's
pattern fires in a visible parent capsule and in the child capsule.  Because
every agent is the same base model with the same prompts, that co-occurrence
has a high floor from independent reinvention (Shalizi & Thomas 2011).  This
script asks the question the raw counts cannot answer: do children carry a
family *more often when a visible partner myth carried it* than when one did
not — and does that difference exceed a rewiring null?

Analyses (partner-myth channel only; self-history is reported separately as
retention, not transmission):

1. Exposure contrast, per run: adoption given >=1 exposed partner-myth parent
   minus adoption given partner-myth parents none of which carry the family.
2. Rewiring null (8-agent runs): each child's partner-myth parents are
   replaced by draws, without replacement, from the myths actually written in
   the same run and round by other agents.  Exposure under this null follows
   a hypergeometric law, simulated B times; one-sided p = (b+1)/(B+1) with
   Holm correction across families.  2-agent runs have no within-run rewiring
   (one possible partner), so they only get a cross-run myth-swap flagged as
   a weak sensitivity check.
3. Negative controls on real data: "exposure" to the same author's next-round
   myth (not yet written, so not visible) and to a same-round non-visible
   myth.  A real transmission effect should beat both; a shared-trajectory
   confound predicts all three look alike.
4. Prompt-elicitation audit: family hits in zero-parent capsules and in
   system/task prompts (e.g. ``noise`` is announced by the system prompt, so
   noise_adaptation hits are elicitation, not culture).

Usage:
    python scripts/analyze_meme_transmission_null.py [INPUT_DIR] \
        [--output DIR] [--permutations B] [--seed N]
"""

from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, stdev

import numpy as np

try:
    from scripts.analyze_capsule_genealogies import (
        Capsule,
        attach_parents,
        is_primary_json,
        load_capsules,
    )
    from scripts.analyze_meme_evolution import MEMES
except ModuleNotFoundError:  # Direct execution adds scripts/, not repo root.
    from analyze_capsule_genealogies import (  # type: ignore
        Capsule,
        attach_parents,
        is_primary_json,
        load_capsules,
    )
    from analyze_meme_evolution import MEMES  # type: ignore


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = (
    PROJECT_ROOT
    / "data/share/corrected_informed_noise_confirmatory_60runs_2026-08-12/data"
)
DEFAULT_OUTPUT = PROJECT_ROOT / "data/analysis/meme_transmission_null_2026_08_28"

FAMILIES = [definition.family for definition in MEMES]
FAMILY_PATTERN = {definition.family: definition.family_pattern for definition in MEMES}


@dataclass
class ChildRecord:
    """One child capsule's exposure state for one meme family."""

    run_id: str
    condition: str
    agent_count: int
    agent_id: str
    child_task: str
    round: int
    child_has: bool
    partner_exposed: bool
    n_partner_parents: int
    parent_keys: list[tuple[int, str]]  # (round, author) of partner-myth parents
    self_exposed: bool
    n_self_parents: int
    future_exposed: bool | None
    has_future_control: bool
    sham_exposed: bool | None
    has_sham_control: bool


def family_hits(text: str) -> set[str]:
    return {family for family in FAMILIES if FAMILY_PATTERN[family].search(text or "")}


def system_prompt_text(capsule: Capsule) -> str:
    for message in capsule.messages_sent:
        if message.get("role") == "system":
            return str(message.get("content") or "")
    return ""


def direct_prompt_text(capsule: Capsule) -> str:
    """Final user message with embedded partner myths stripped out."""
    if not capsule.messages_sent or capsule.messages_sent[-1].get("role") != "user":
        return ""
    prompt = str(capsule.messages_sent[-1].get("content") or "")
    for parent, _route in capsule.parents:
        if parent.agent_id != capsule.agent_id and parent.task == "myth":
            prompt = prompt.replace(parent.text, "")
    return prompt


def agent_count_for(condition: str) -> int:
    return 8 if condition.startswith("8-agent") else 2


def build_records(
    capsules_by_run: dict[str, list[Capsule]],
    hits_by_capsule: dict[str, set[str]],
    rng: np.random.Generator,
) -> dict[str, list[ChildRecord]]:
    """Per family, one record per child capsule that has >=1 partner-myth parent."""
    records: dict[str, list[ChildRecord]] = {family: [] for family in FAMILIES}

    for run_id, capsules in capsules_by_run.items():
        myth_by_round_author: dict[tuple[int, str], Capsule] = {}
        for capsule in capsules:
            if capsule.task == "myth":
                # Keep the last myth an agent wrote in a round (rewrites are rare).
                myth_by_round_author[(capsule.round, capsule.agent_id)] = capsule

        for child in capsules:
            partner_parents = [
                parent
                for parent, _route in child.parents
                if parent.agent_id != child.agent_id and parent.task == "myth"
            ]
            self_parents = [
                parent
                for parent, _route in child.parents
                if parent.agent_id == child.agent_id
            ]
            if not partner_parents:
                continue

            parent_keys = [(parent.round, parent.agent_id) for parent in partner_parents]
            visible_ids = {parent.capsule_id for parent in partner_parents}

            # Future control: the same authors' next-round myths, none visible yet.
            future_myths = [
                myth_by_round_author.get((parent.round + 1, parent.agent_id))
                for parent in partner_parents
            ]
            future_myths = [myth for myth in future_myths if myth is not None]

            # Sham control: same-round myths by agents that are neither the child
            # nor a visible parent (only exists in 8-agent runs).
            sham_candidates = [
                myth
                for (myth_round, author), myth in myth_by_round_author.items()
                if myth_round in {parent.round for parent in partner_parents}
                and author != child.agent_id
                and myth.capsule_id not in visible_ids
            ]
            sham_pick = None
            if sham_candidates:
                sham_pick = sham_candidates[int(rng.integers(len(sham_candidates)))]

            child_hits = hits_by_capsule[child.capsule_id]
            for family in FAMILIES:
                records[family].append(
                    ChildRecord(
                        run_id=run_id,
                        condition=child.condition,
                        agent_count=agent_count_for(child.condition),
                        agent_id=child.agent_id,
                        child_task=child.task,
                        round=child.round,
                        child_has=family in child_hits,
                        partner_exposed=any(
                            family in hits_by_capsule[parent.capsule_id]
                            for parent in partner_parents
                        ),
                        n_partner_parents=len(partner_parents),
                        parent_keys=parent_keys,
                        self_exposed=any(
                            family in hits_by_capsule[parent.capsule_id]
                            for parent in self_parents
                        ),
                        n_self_parents=len(self_parents),
                        future_exposed=(
                            any(
                                family in hits_by_capsule[myth.capsule_id]
                                for myth in future_myths
                            )
                            if future_myths
                            else None
                        ),
                        has_future_control=bool(future_myths),
                        sham_exposed=(
                            (family in hits_by_capsule[sham_pick.capsule_id])
                            if sham_pick is not None
                            else None
                        ),
                        has_sham_control=sham_pick is not None,
                    )
                )
    return records


def run_level_contrast(
    records: list[ChildRecord],
    exposed_of: "callable",
) -> tuple[list[float], list[float], list[float]]:
    """Per-run adoption-rate difference: exposed minus unexposed children."""
    by_run: dict[str, list[ChildRecord]] = defaultdict(list)
    for record in records:
        by_run[record.run_id].append(record)

    diffs: list[float] = []
    exposed_rates: list[float] = []
    unexposed_rates: list[float] = []
    for run_records in by_run.values():
        exposed = [r.child_has for r in run_records if exposed_of(r)]
        unexposed = [r.child_has for r in run_records if exposed_of(r) is False]
        if not exposed or not unexposed:
            continue
        exposed_rate = mean(exposed)
        unexposed_rate = mean(unexposed)
        exposed_rates.append(exposed_rate)
        unexposed_rates.append(unexposed_rate)
        diffs.append(exposed_rate - unexposed_rate)
    return diffs, exposed_rates, unexposed_rates


def precompute_null_probabilities(
    capsules_by_run: dict[str, list[Capsule]],
    hits_by_capsule: dict[str, set[str]],
) -> dict[str, dict[tuple[str, str, int, tuple], float]]:
    """For each family: child-key -> P(not exposed) under within-run rewiring.

    Child key = (run_id, child_agent, child_interaction_index, parent_keys).
    Each actual partner-myth parent at round r is replaced by one myth drawn
    without replacement from the same run's round-r myths whose author is not
    the child.  P(none exposed) multiplies across rounds and uses the
    hypergeometric probability within a round.
    """
    probabilities: dict[str, dict] = {family: {} for family in FAMILIES}

    for run_id, capsules in capsules_by_run.items():
        myths_by_round: dict[int, list[Capsule]] = defaultdict(list)
        seen: set[tuple[int, str]] = set()
        for capsule in capsules:
            if capsule.task == "myth":
                key = (capsule.round, capsule.agent_id)
                if key in seen:
                    myths_by_round[capsule.round] = [
                        myth
                        for myth in myths_by_round[capsule.round]
                        if myth.agent_id != capsule.agent_id
                    ]
                seen.add(key)
                myths_by_round[capsule.round].append(capsule)

        for child in capsules:
            partner_parents = [
                parent
                for parent, _route in child.parents
                if parent.agent_id != child.agent_id and parent.task == "myth"
            ]
            if not partner_parents:
                continue
            parents_per_round: dict[int, int] = defaultdict(int)
            for parent in partner_parents:
                parents_per_round[parent.round] += 1

            child_key = (
                run_id,
                child.agent_id,
                child.interaction_index,
                tuple(sorted((p.round, p.agent_id) for p in partner_parents)),
            )
            for family in FAMILIES:
                log_p_none = 0.0
                feasible = True
                for myth_round, k in parents_per_round.items():
                    candidates = [
                        myth
                        for myth in myths_by_round.get(myth_round, [])
                        if myth.agent_id != child.agent_id
                    ]
                    n = len(candidates)
                    m = sum(
                        1
                        for myth in candidates
                        if family in hits_by_capsule[myth.capsule_id]
                    )
                    if k > n:
                        feasible = False
                        break
                    # P(no exposed among k draws without replacement)
                    p_none = 1.0
                    for i in range(k):
                        p_none *= max(0.0, (n - m - i)) / (n - i)
                    if p_none <= 0.0:
                        log_p_none = -math.inf
                        break
                    log_p_none += math.log(p_none)
                if not feasible:
                    continue
                probabilities[family][child_key] = (
                    0.0 if log_p_none == -math.inf else math.exp(log_p_none)
                )
    return probabilities


def permutation_test(
    records: list[ChildRecord],
    p_not_exposed: dict[tuple, float],
    child_keys: list[tuple],
    n_permutations: int,
    rng: np.random.Generator,
) -> tuple[float, float, float, float]:
    """Observed statistic vs simulated rewiring null.

    Statistic: mean over runs of (adoption | exposed) - (adoption | unexposed).
    Returns (observed, null_mean, null_sd, one_sided_p).
    """
    observed_diffs, _, _ = run_level_contrast(records, lambda r: r.partner_exposed)
    if not observed_diffs:
        return math.nan, math.nan, math.nan, math.nan
    observed = mean(observed_diffs)

    run_ids = sorted({record.run_id for record in records})
    run_index = {run_id: i for i, run_id in enumerate(run_ids)}

    usable = [
        (record, p_not_exposed[key])
        for record, key in zip(records, child_keys)
        if key in p_not_exposed
    ]
    if not usable:
        return observed, math.nan, math.nan, math.nan

    child_has = np.array([record.child_has for record, _p in usable], dtype=bool)
    p_exposed = np.array([1.0 - p for _record, p in usable], dtype=float)
    run_of = np.array([run_index[record.run_id] for record, _p in usable], dtype=int)

    null_stats = np.full(n_permutations, np.nan)
    exposure = (
        rng.random((n_permutations, len(usable))) < p_exposed[None, :]
    )
    for b in range(n_permutations):
        diffs = []
        exposed_row = exposure[b]
        for i in range(len(run_ids)):
            mask = run_of == i
            exp_mask = mask & exposed_row
            unexp_mask = mask & ~exposed_row
            if not exp_mask.any() or not unexp_mask.any():
                continue
            diffs.append(
                child_has[exp_mask].mean() - child_has[unexp_mask].mean()
            )
        if diffs:
            null_stats[b] = float(np.mean(diffs))

    valid = null_stats[~np.isnan(null_stats)]
    if valid.size == 0:
        return observed, math.nan, math.nan, math.nan
    exceed = int((valid >= observed).sum())
    p_value = (exceed + 1) / (valid.size + 1)
    return observed, float(valid.mean()), float(valid.std(ddof=1)), p_value


def holm_correction(p_values: dict[str, float]) -> dict[str, float]:
    items = sorted(
        ((family, p) for family, p in p_values.items() if not math.isnan(p)),
        key=lambda item: item[1],
    )
    adjusted: dict[str, float] = {family: math.nan for family in p_values}
    n = len(items)
    running_max = 0.0
    for rank, (family, p) in enumerate(items):
        value = min(1.0, (n - rank) * p)
        running_max = max(running_max, value)
        adjusted[family] = running_max
    return adjusted


def fmt(mean_value: float, sd_value: float, percent: bool = True) -> str:
    if math.isnan(mean_value):
        return "—"
    scale = 100.0 if percent else 1.0
    return f"{mean_value * scale:+.1f} (±{sd_value * scale:.1f})%"


def summarize(values: list[float]) -> tuple[float, float]:
    if not values:
        return math.nan, math.nan
    return mean(values), stdev(values) if len(values) > 1 else 0.0


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_dir", nargs="?", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--permutations", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()

    rng = np.random.default_rng(args.seed)

    run_paths = sorted(
        path for path in args.input_dir.rglob("*.json") if is_primary_json(path)
    )
    if not run_paths:
        raise SystemExit(f"No run JSONs found under {args.input_dir}")

    capsules_by_run: dict[str, list[Capsule]] = {}
    for path in run_paths:
        _data, capsules = load_capsules(path, args.input_dir)
        attach_parents(capsules)
        capsules_by_run[capsules[0].run_id] = capsules

    all_capsules = [c for capsules in capsules_by_run.values() for c in capsules]
    hits_by_capsule = {c.capsule_id: family_hits(c.text) for c in all_capsules}

    # ------------------------------------------------------------------
    # Prompt-elicitation audit
    # ------------------------------------------------------------------
    parent_free = [c for c in all_capsules if not c.parents]
    elicitation_rows = []
    for family in FAMILIES:
        parent_free_hits = sum(
            1 for c in parent_free if family in hits_by_capsule[c.capsule_id]
        )
        system_hits = sum(
            1 for c in all_capsules if FAMILY_PATTERN[family].search(system_prompt_text(c))
        )
        prompt_hits = sum(
            1 for c in all_capsules if FAMILY_PATTERN[family].search(direct_prompt_text(c))
        )
        elicitation_rows.append(
            {
                "meme_family": family,
                "parent_free_capsules": len(parent_free),
                "parent_free_hits": parent_free_hits,
                "parent_free_rate": round(parent_free_hits / len(parent_free), 4)
                if parent_free
                else math.nan,
                "system_prompt_hit_capsules": system_hits,
                "direct_prompt_hit_capsules": prompt_hits,
                "capsules_total": len(all_capsules),
            }
        )
    write_csv(
        args.output / "prompt_elicitation.csv",
        elicitation_rows,
        list(elicitation_rows[0].keys()),
    )

    # ------------------------------------------------------------------
    # Panel + exposure contrasts + negative controls
    # ------------------------------------------------------------------
    records_by_family = build_records(capsules_by_run, hits_by_capsule, rng)
    null_probabilities = precompute_null_probabilities(capsules_by_run, hits_by_capsule)

    contrast_rows = []
    permutation_rows = []
    p_by_family: dict[str, float] = {}

    for family in FAMILIES:
        records = records_by_family[family]
        for group_name, group_records in (
            ("8-agent", [r for r in records if r.agent_count == 8]),
            ("2-agent", [r for r in records if r.agent_count == 2]),
            ("pooled", records),
        ):
            diffs, exposed_rates, unexposed_rates = run_level_contrast(
                group_records, lambda r: r.partner_exposed
            )
            future_diffs, _, _ = run_level_contrast(
                [r for r in group_records if r.has_future_control],
                lambda r: r.future_exposed,
            )
            sham_diffs, _, _ = run_level_contrast(
                [r for r in group_records if r.has_sham_control],
                lambda r: r.sham_exposed,
            )
            self_diffs, _, _ = run_level_contrast(
                [r for r in group_records if r.n_self_parents > 0],
                lambda r: r.self_exposed,
            )
            diff_mean, diff_sd = summarize(diffs)
            exposed_mean, exposed_sd = summarize(exposed_rates)
            unexposed_mean, unexposed_sd = summarize(unexposed_rates)
            future_mean, future_sd = summarize(future_diffs)
            sham_mean, sham_sd = summarize(sham_diffs)
            self_mean, self_sd = summarize(self_diffs)
            contrast_rows.append(
                {
                    "meme_family": family,
                    "group": group_name,
                    "runs_with_both_cells": len(diffs),
                    "adoption_exposed_mean": exposed_mean,
                    "adoption_exposed_sd": exposed_sd,
                    "adoption_unexposed_mean": unexposed_mean,
                    "adoption_unexposed_sd": unexposed_sd,
                    "exposure_diff_mean": diff_mean,
                    "exposure_diff_sd": diff_sd,
                    "future_control_diff_mean": future_mean,
                    "future_control_diff_sd": future_sd,
                    "sham_control_diff_mean": sham_mean,
                    "sham_control_diff_sd": sham_sd,
                    "self_retention_diff_mean": self_mean,
                    "self_retention_diff_sd": self_sd,
                }
            )

        # Permutation null: 8-agent runs only (2-agent has no within-run rewiring).
        eight = [r for r in records if r.agent_count == 8]
        observed, null_mean, null_sd, p_value = permutation_test_positional(
            eight,
            null_probabilities[family],
            capsules_by_run,
            args.permutations,
            rng,
        )
        p_by_family[family] = p_value
        permutation_rows.append(
            {
                "meme_family": family,
                "group": "8-agent",
                "observed_diff": observed,
                "null_mean": null_mean,
                "null_sd": null_sd,
                "p_one_sided": p_value,
            }
        )

    adjusted = holm_correction(p_by_family)
    for row in permutation_rows:
        row["p_holm"] = adjusted[row["meme_family"]]

    write_csv(
        args.output / "exposure_contrast.csv",
        contrast_rows,
        list(contrast_rows[0].keys()),
    )
    write_csv(
        args.output / "permutation_results.csv",
        permutation_rows,
        list(permutation_rows[0].keys()),
    )

    write_report(args, contrast_rows, permutation_rows, elicitation_rows)
    print(f"Wrote {args.output}")


def permutation_test_positional(
    records: list[ChildRecord],
    family_probabilities: dict[tuple, float],
    capsules_by_run: dict[str, list[Capsule]],
    n_permutations: int,
    rng: np.random.Generator,
) -> tuple[float, float, float, float]:
    """Match records to null probabilities via (run, child agent, parent keys)."""
    keyed: dict[tuple, float] = {}
    for (run_id, agent, _index, parent_keys), p in family_probabilities.items():
        keyed[(run_id, agent, parent_keys)] = p

    child_keys = [
        (record.run_id, record.agent_id, tuple(sorted(record.parent_keys)))
        for record in records
    ]
    lookup = {}
    for key in set(child_keys):
        if key in keyed:
            lookup[key] = keyed[key]
    resolved_keys = [key if key in lookup else None for key in child_keys]
    usable_pairs = [
        (record, lookup[key])
        for record, key in zip(records, resolved_keys)
        if key is not None
    ]
    if not usable_pairs:
        observed_diffs, _, _ = run_level_contrast(
            records, lambda r: r.partner_exposed
        )
        observed = mean(observed_diffs) if observed_diffs else math.nan
        return observed, math.nan, math.nan, math.nan

    return permutation_test(
        records,
        {key: lookup[key] for key in lookup},
        resolved_keys,
        n_permutations,
        rng,
    )


def write_report(args, contrast_rows, permutation_rows, elicitation_rows) -> None:
    lines = [
        "# Does meme co-occurrence beat a no-transmission null?",
        "",
        "Partner-myth channel only: a child is *exposed* to a meme family when at",
        "least one partner myth visible in its prompt carries the family pattern.",
        "Self-history is reported as retention, separately, because an agent",
        "re-using its own words is persistence, not transmission.",
        "",
        "## Exposure contrast (run-level mean ± sd, adoption difference in pp)",
        "",
        "| Family | Group | Runs | Adoption exposed | Adoption unexposed | Diff | Future ctrl | Sham ctrl | Self-retention |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in contrast_rows:
        lines.append(
            "| {family} | {group} | {runs} | {exp} | {unexp} | {diff} | {future} | {sham} | {self_} |".format(
                family=row["meme_family"],
                group=row["group"],
                runs=row["runs_with_both_cells"],
                exp=fmt(row["adoption_exposed_mean"], row["adoption_exposed_sd"]),
                unexp=fmt(row["adoption_unexposed_mean"], row["adoption_unexposed_sd"]),
                diff=fmt(row["exposure_diff_mean"], row["exposure_diff_sd"]),
                future=fmt(row["future_control_diff_mean"], row["future_control_diff_sd"]),
                sham=fmt(row["sham_control_diff_mean"], row["sham_control_diff_sd"]),
                self_=fmt(row["self_retention_diff_mean"], row["self_retention_diff_sd"]),
            )
        )
    lines += [
        "",
        "Reading guide: a transmission signal requires Diff > 0, clearly larger",
        "than the future and sham controls. If all three are similar, the",
        "co-occurrence reflects shared trajectories, not copying.",
        "",
        f"## Rewiring null (8-agent runs, B={args.permutations}, seed={args.seed})",
        "",
        "| Family | Observed diff | Null mean | Null sd | p (one-sided) | p (Holm) |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in permutation_rows:
        lines.append(
            "| {family} | {obs} | {nmean} | {nsd} | {p} | {ph} |".format(
                family=row["meme_family"],
                obs="—" if math.isnan(row["observed_diff"]) else f"{row['observed_diff'] * 100:+.1f}pp",
                nmean="—" if math.isnan(row["null_mean"]) else f"{row['null_mean'] * 100:+.1f}pp",
                nsd="—" if math.isnan(row["null_sd"]) else f"{row['null_sd'] * 100:.1f}pp",
                p="—" if math.isnan(row["p_one_sided"]) else f"{row['p_one_sided']:.4f}",
                ph="—" if math.isnan(row.get("p_holm", math.nan)) else f"{row['p_holm']:.4f}",
            )
        )
    lines += [
        "",
        "The null replaces each child's visible partner myths with same-run,",
        "same-round myths by other agents (degree-preserving). 2-agent runs are",
        "excluded: with a single possible partner there is nothing to rewire, so",
        "dyadic transmission claims require an interventional (seeding) design.",
        "",
        "## Prompt elicitation (why some families cannot count as culture)",
        "",
        "| Family | Zero-parent capsules carrying it | System prompt carries it | Direct prompt carries it |",
        "|---|---:|---:|---:|",
    ]
    for row in elicitation_rows:
        lines.append(
            "| {family} | {pf} / {pft} ({rate:.0%}) | {sys} | {direct} |".format(
                family=row["meme_family"],
                pf=row["parent_free_hits"],
                pft=row["parent_free_capsules"],
                rate=row["parent_free_rate"],
                sys=row["system_prompt_hit_capsules"],
                direct=row["direct_prompt_hit_capsules"],
            )
        )
    lines += [
        "",
        "A family carried by the system or task prompt (or common in zero-parent",
        "capsules) is elicited by the experiment itself; its presence in a child",
        "is not evidence of cultural transmission regardless of the contrasts",
        "above.",
        "",
        "## Reproduction",
        "",
        "```bash",
        "python scripts/analyze_meme_transmission_null.py",
        "```",
    ]
    output = args.output / "report.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

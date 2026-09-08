#!/usr/bin/env python3
"""Track idea-level cultural transmission and variation in saved runs.

This extends ``analyze_capsule_genealogies.py`` from literal facts/claims to a
small, predeclared ontology of strategy ideas ("memes").  A meme family is an
idea such as proportional reciprocity or adapting to noisy perceptions.  Each
family has variants, allowing parent -> child edges to be classified as faithful
retention or a surface-level variant shift.

The analysis also identifies candidate *private-belief packets*: a partner myth
and a later game rationale share both an event reference and a numerical claim.
A stricter decoded-discrepancy flag requires explicit language such as "their
myth says ... but I actually ..." plus noise/perception language.

All detection is deterministic.  The ontology is intentionally small and
auditable; it should be treated as a high-precision manipulation check, not a
complete theory of every idea in the corpus.

Usage:
    python scripts/analyze_meme_evolution.py [INPUT_DIR] [--output DIR]
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import mean, stdev

try:
    from scripts.analyze_capsule_genealogies import (
        CONDITION_NAMES,
        DEFAULT_INPUT,
        PROJECT_ROOT,
        TASK_ORDER,
        Capsule,
        attach_parents,
        compact,
        extract_claims,
        is_primary_json,
        load_capsules,
    )
except ModuleNotFoundError:  # Direct execution adds scripts/, not repo root.
    from analyze_capsule_genealogies import (  # type: ignore
        CONDITION_NAMES,
        DEFAULT_INPUT,
        PROJECT_ROOT,
        TASK_ORDER,
        Capsule,
        attach_parents,
        compact,
        extract_claims,
        is_primary_json,
        load_capsules,
    )


DEFAULT_OUTPUT = PROJECT_ROOT / "data/analysis/meme_evolution_2026_08_19"


@dataclass(frozen=True)
class MemeDefinition:
    family: str
    description: str
    family_pattern: re.Pattern[str]
    variants: tuple[tuple[str, re.Pattern[str]], ...]


@dataclass(frozen=True)
class MemeOccurrence:
    family: str
    variant: str
    description: str
    evidence: str


def rx(pattern: str) -> re.Pattern[str]:
    return re.compile(pattern, re.I | re.S)


MEMES = (
    MemeDefinition(
        family="proportional_reciprocity",
        description="Return a fair or proportional share in response to what was received.",
        family_pattern=rx(
            r"\b(?:reciproc\w*|proportional\w*|fair return|return fairly|fairly return|"
            r"honou?r(?:ing|ed)? (?:the |this )?(?:trust|faith|gift|generosity)|"
            r"reward(?:ing|ed)? (?:the |this )?(?:trust|faith|generosity))\b"
        ),
        variants=(
            ("fixed_fraction", rx(r"\b(?:half|percent|percentage|ratio|proportional\w*|50\s*[-–]\s*55)\b|\b(?:fifty|sixty)[- ]\w+ percent\b")),
            ("responsive_reward", rx(r"\b(?:match\w*|reward\w*|respond\w*|honou?r\w*)\b.{0,80}\b(?:trust|faith|generosity|courage|boldness)\b")),
            ("general_fairness", rx(r"\b(?:fair|fairly|fairness|integrity|reciproc\w*)\b")),
        ),
    ),
    MemeDefinition(
        family="sustainable_equilibrium",
        description="Seek a stable level of cooperation that can be maintained over time.",
        family_pattern=rx(r"\b(?:equilibrium|middle path|sustain\w*|balanced? rhythm|stable balance|harmony)\b"),
        variants=(
            ("moderate_middle", rx(r"\b(?:middle path|moderat\w*|sixty percent|60%|cautious balance)\b")),
            ("high_trust", rx(r"\b(?:high trust|bold generosity|generous equilibrium|seventy[- ]five percent|75%|eighty percent|80%)\b")),
            ("generic_balance", rx(r"\b(?:equilibrium|balance|harmony|sustain\w*)\b")),
        ),
    ),
    MemeDefinition(
        family="consistency_over_volatility",
        description="Prefer steady, reliable behavior over large reactive swings.",
        family_pattern=rx(r"\b(?:consisten\w*|stead(?:y|ily)|reliab\w*|dependab\w*|cycle after cycle|wild swings|volatile|volatility)\b"),
        variants=(
            ("anti_volatility", rx(r"\b(?:not|neither|rather than|over)\b.{0,80}\b(?:wild swings|escalat\w*|volatile|maximum risk|fluctuat\w*)\b|\bregardless of (?:their |the )?variations\b")),
            ("steady_repetition", rx(r"\b(?:consisten\w*|stead(?:y|ily)|reliab\w*|dependab\w*|cycle after cycle)\b")),
        ),
    ),
    MemeDefinition(
        family="trust_escalation",
        description="Answer renewed generosity with increased generosity, building an upward spiral.",
        family_pattern=rx(r"\b(?:escalat\w*|positive spiral|renewed (?:courage|boldness|trust)|courage resurges|increasing trust|measured increases?|increase\w* (?:my |the )?(?:send|return|reciprocity))\b"),
        variants=(
            ("measured_escalation", rx(r"\b(?:measured|slight\w*|sustain\w*|not recklessly|not wild)\b.{0,100}\b(?:escalat\w*|increase\w*|renewed)\b|\b(?:escalat\w*|increase\w*|renewed)\b.{0,100}\b(?:measured|slight\w*|sustain\w*|not recklessly|not wild)\b")),
            ("strong_escalation", rx(r"\b(?:escalat\w*|positive spiral|increasing trust|renewed (?:courage|boldness|trust))\b")),
        ),
    ),
    MemeDefinition(
        family="noise_adaptation",
        description="Recognize differing perceptions and use a policy robust to communication noise.",
        family_pattern=rx(r"\b(?:communication noise|noise|distort\w*|percei\w*|perception|appeared different|what (?:was )?actually|exact matching is impossible|based on what (?:you|they|I) receive)\b"),
        variants=(
            ("explicit_discrepancy", rx(r"\b(?:their myth says|they (?:saw|perceived|believed|thought)|but I actually|different from what (?:I|they|was)|appeared to (?:them|me)|what (?:was )?actually)\b")),
            ("robust_policy", rx(r"\b(?:despite|under|with) (?:the )?(?:communication )?noise\b.{0,120}\b(?:consistent|fair|present|received|sustain\w*|exact matching)\b|\b(?:exact matching is impossible|based on what (?:you|they|I) receive|trust the present moment)\b")),
            ("noise_awareness", rx(r"\b(?:communication noise|noise|distort\w*|percei\w*|perception)\b")),
        ),
    ),
    MemeDefinition(
        family="prosperity_through_cooperation",
        description="Mutual generosity creates a larger shared surplus from which both benefit.",
        family_pattern=rx(r"\b(?:mutual (?:benefit|prosperity|abundance)|both (?:profit|prosper|flourish|thrive)|prosperity through|wealth multiplies|abundance through)\b"),
        variants=(
            ("multiplier_abundance", rx(r"\b(?:tripl\w*|multipl\w*)\b.{0,120}\b(?:prosper\w*|abundance|wealth|benefit|flourish|thrive)\b|\b(?:prosper\w*|abundance|wealth|benefit)\b.{0,120}\b(?:tripl\w*|multipl\w*)\b")),
            ("mutual_profit", rx(r"\b(?:mutual (?:benefit|prosperity|abundance)|both (?:profit|prosper|flourish|thrive))\b")),
        ),
    ),
    MemeDefinition(
        family="trust_seeding",
        description="Use an initially generous move to establish or signal trust.",
        family_pattern=rx(r"\b(?:establish\w*|signal\w*|initiat\w*|foundation|start|begin\w*|open\w*)\b.{0,100}\b(?:trust|faith|cooperation|generosity)\b|\b(?:trust|faith|cooperation|generosity)\b.{0,100}\b(?:foundation|from the start|opening move|first move)\b"),
        variants=(
            ("bold_opening", rx(r"\b(?:bold|generous|substantial|high)\b.{0,70}\b(?:opening|start|begin|first|foundation|signal)\b|\b(?:opening|start|begin|first|foundation|signal)\b.{0,70}\b(?:bold|generous|substantial|high)\b")),
            ("general_seed", rx(r"\b(?:establish|signal|initiat|foundation|start|begin|open)\w*\b")),
        ),
    ),
    MemeDefinition(
        family="punitive_deterrence",
        description="Reduce cooperation or impose consequences after betrayal or exploitation.",
        family_pattern=rx(r"\b(?:punish\w*|retaliat\w*|betray\w*|defect\w*|exploit\w*|withhold\w*|withdraw\w* trust|break\w* faith)\b"),
        variants=(
            ("withdrawal", rx(r"\b(?:withhold\w*|withdraw\w*|retreat\w*|reduce\w*|cautio\w*)\b")),
            ("punishment", rx(r"\b(?:punish\w*|retaliat\w*|consequence\w*|betray\w*|defect\w*|exploit\w*)\b")),
        ),
    ),
    MemeDefinition(
        family="repair_after_disruption",
        description="Rebuild cooperation after a rupture rather than treating failure as permanent.",
        family_pattern=rx(r"\b(?:rebuild\w*|restore\w*|repair\w*|regain\w* trust|recover\w* trust|trust can return|second chance)\b"),
        variants=(
            ("gradual_repair", rx(r"\b(?:gradual\w*|step by step|measured|slowly|small)\b.{0,100}\b(?:rebuild|restore|repair|regain|recover)\w*\b|\b(?:rebuild|restore|repair|regain|recover)\w*\b.{0,100}\b(?:gradual\w*|step by step|measured|slowly|small)\b")),
            ("general_repair", rx(r"\b(?:rebuild\w*|restore\w*|repair\w*|regain\w*|recover\w*|second chance)\b")),
        ),
    ),
)


MEME_BY_FAMILY = {definition.family: definition for definition in MEMES}
CONTRAST_RE = rx(
    r"\b(?:their myth says|they (?:saw|perceived|believed|thought)|but I actually|"
    r"different from what (?:I|they|was)|appeared to (?:them|me)|what (?:was )?actually)\b"
)
MYTH_ATTRIBUTION_RE = rx(
    r"\b(?:(?:their|the other|my co-player'?s|my partner'?s)\s+myth|"
    r"myth\s+(?:says|said|mentions|mentioned|describes|described|reveals|revealed|suggests|suggested))\b"
)
DECISION_RE = re.compile(r"[\"'](?P<kind>send|return)[\"']\s*:\s*(?P<value>\d+(?:\.\d+)?)", re.I)


def detect_memes(text: str) -> dict[str, MemeOccurrence]:
    occurrences: dict[str, MemeOccurrence] = {}
    for definition in MEMES:
        match = definition.family_pattern.search(text or "")
        if not match:
            continue
        variant = "generic"
        for variant_name, pattern in definition.variants:
            if pattern.search(text):
                variant = variant_name
                break
        start = max(0, match.start() - 110)
        stop = min(len(text), match.end() + 180)
        occurrences[definition.family] = MemeOccurrence(
            family=definition.family,
            variant=variant,
            description=definition.description,
            evidence=compact(text[start:stop], limit=300),
        )
    return occurrences


def direct_prompt_text(capsule: Capsule) -> str:
    if not capsule.messages_sent or capsule.messages_sent[-1].get("role") != "user":
        return ""
    text = str(capsule.messages_sent[-1].get("content") or "")
    for parent, _route in capsule.parents:
        if parent.agent_id != capsule.agent_id and parent.task == "myth":
            text = text.replace(parent.text, "")
    return text


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def summarize(values: list[float]) -> tuple[float, float]:
    clean = [value for value in values if not math.isnan(value)]
    if not clean:
        return math.nan, math.nan
    return mean(clean), stdev(clean) if len(clean) > 1 else 0.0


def fmt_mean_sd(values: list[float], digits: int = 2, percent: bool = False) -> str:
    avg, sd = summarize(values)
    if math.isnan(avg):
        return "—"
    scale = 100.0 if percent else 1.0
    suffix = "%" if percent else ""
    return f"{avg * scale:.{digits}f} (±{sd * scale:.{digits}f}){suffix}"


def decision_from(text: str) -> tuple[str, float | None]:
    matches = list(DECISION_RE.finditer(text))
    if not matches:
        return "", None
    match = matches[-1]
    return match.group("kind").lower(), float(match.group("value"))


def analyze(input_dir: Path, output_dir: Path) -> dict:
    paths = sorted(path for path in input_dir.rglob("*.json") if is_primary_json(path))
    all_capsules: list[Capsule] = []
    capsules_by_run: dict[str, list[Capsule]] = {}
    for path in paths:
        _data, capsules = load_capsules(path, input_dir)
        attach_parents(capsules)
        all_capsules.extend(capsules)
        capsules_by_run[capsules[0].run_id] = capsules

    memes_by_capsule = {
        capsule.capsule_id: detect_memes(capsule.text) for capsule in all_capsules
    }
    capsule_by_id = {capsule.capsule_id: capsule for capsule in all_capsules}

    occurrence_rows: list[dict] = []
    transmission_rows: list[dict] = []
    recombination_rows: list[dict] = []
    belief_rows: list[dict] = []

    for child in all_capsules:
        child_memes = memes_by_capsule[child.capsule_id]
        parent_memes = {
            parent.capsule_id: memes_by_capsule[parent.capsule_id]
            for parent, _route in child.parents
        }
        parent_families = {
            family for occurrences in parent_memes.values() for family in occurrences
        }
        prompt_families = set(detect_memes(direct_prompt_text(child)))
        source_sets: dict[str, set[str]] = defaultdict(set)
        for parent_id, occurrences in parent_memes.items():
            for family in occurrences:
                source_sets[family].add(parent_id)

        for family, occurrence in child_memes.items():
            inherited = family in parent_families
            prompt_supplied = family in prompt_families
            occurrence_rows.append(
                {
                    "capsule_id": child.capsule_id,
                    "run_id": child.run_id,
                    "condition": child.condition,
                    "agent_id": child.agent_id,
                    "round": child.round,
                    "task": child.task,
                    "meme_family": family,
                    "variant": occurrence.variant,
                    "inherited": int(inherited),
                    "prompt_supplied": int(prompt_supplied),
                    "first_observed_innovation": int(not inherited and not prompt_supplied),
                    "evidence": occurrence.evidence,
                }
            )

        inherited_families = sorted(set(child_memes) & parent_families)
        for index, left in enumerate(inherited_families):
            for right in inherited_families[index + 1 :]:
                if source_sets[left] and source_sets[right] and source_sets[left].isdisjoint(source_sets[right]):
                    recombination_rows.append(
                        {
                            "run_id": child.run_id,
                            "condition": child.condition,
                            "child_capsule_id": child.capsule_id,
                            "agent_id": child.agent_id,
                            "round": child.round,
                            "task": child.task,
                            "meme_a": left,
                            "meme_b": right,
                            "source_capsules_a": "|".join(sorted(source_sets[left])),
                            "source_capsules_b": "|".join(sorted(source_sets[right])),
                        }
                    )

        child_claims = extract_claims(child.text)
        for parent, route in child.parents:
            p_memes = memes_by_capsule[parent.capsule_id]
            for family, parent_occurrence in p_memes.items():
                retained = family in child_memes
                child_variant = child_memes[family].variant if retained else ""
                transmission_rows.append(
                    {
                        "run_id": child.run_id,
                        "condition": child.condition,
                        "route": route,
                        "parent_capsule_id": parent.capsule_id,
                        "child_capsule_id": child.capsule_id,
                        "parent_agent": parent.agent_id,
                        "child_agent": child.agent_id,
                        "parent_round": parent.round,
                        "child_round": child.round,
                        "parent_task": parent.task,
                        "child_task": child.task,
                        "meme_family": family,
                        "parent_variant": parent_occurrence.variant,
                        "child_variant": child_variant,
                        "retained": int(retained),
                        "faithful_variant": int(retained and child_variant == parent_occurrence.variant),
                        "variant_shift": int(retained and child_variant != parent_occurrence.variant),
                    }
                )

            if route != "partner-myth→game":
                continue
            parent_claims = extract_claims(parent.text)
            shared = set(parent_claims) & set(child_claims)
            shared_events = sorted(key for key in shared if key.startswith("event:"))
            shared_numeric = sorted(
                key for key in shared if key.startswith("fact:") or key.startswith("rate:")
            )
            if not shared_events or not shared_numeric:
                continue
            child_noise = child_memes.get("noise_adaptation")
            explicit_contrast = bool(CONTRAST_RE.search(child.text))
            explicit_myth_attribution = bool(MYTH_ATTRIBUTION_RE.search(child.text))
            decoded = bool(
                child_noise
                and child_noise.variant == "explicit_discrepancy"
                and explicit_contrast
                and explicit_myth_attribution
            )
            decision_kind, decision_value = decision_from(child.text)
            belief_rows.append(
                {
                    "run_id": child.run_id,
                    "condition": child.condition,
                    "parent_capsule_id": parent.capsule_id,
                    "child_capsule_id": child.capsule_id,
                    "source_agent": parent.agent_id,
                    "recipient_agent": child.agent_id,
                    "source_round": parent.round,
                    "recipient_round": child.round,
                    "shared_events": "|".join(shared_events),
                    "shared_numeric_claims": "|".join(shared_numeric),
                    "explicit_contrast": int(explicit_contrast),
                    "explicit_myth_attribution": int(explicit_myth_attribution),
                    "decoded_discrepancy": int(decoded),
                    "decision_kind": decision_kind,
                    "decision_value": decision_value if decision_value is not None else "",
                    "source_myth_excerpt": compact(parent.text, 360),
                    "recipient_game_excerpt": compact(child.text, 520),
                }
            )

    # Culture-level family lineages within each run.
    by_run_family: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in occurrence_rows:
        by_run_family[(row["run_id"], row["meme_family"])].append(row)
    lineage_rows: list[dict] = []
    for (run_id, family), rows in by_run_family.items():
        rounds = [int(row["round"]) for row in rows]
        variants = sorted({str(row["variant"]) for row in rows})
        lineage_rows.append(
            {
                "run_id": run_id,
                "condition": rows[0]["condition"],
                "meme_family": family,
                "first_round": min(rounds),
                "last_round": max(rounds),
                "round_span": max(rounds) - min(rounds),
                "carrier_count": len(rows),
                "agent_count": len({str(row["agent_id"]) for row in rows}),
                "game_carriers": sum(row["task"] == "game" for row in rows),
                "myth_carriers": sum(row["task"] == "myth" for row in rows),
                "variant_count": len(variants),
                "variants": "|".join(variants),
                "first_observed_innovations": sum(int(row["first_observed_innovation"]) for row in rows),
            }
        )

    # Per-run summaries keep condition comparisons independent at the run level.
    occurrences_by_run: dict[str, list[dict]] = defaultdict(list)
    transmissions_by_run: dict[str, list[dict]] = defaultdict(list)
    recombinations_by_run: dict[str, list[dict]] = defaultdict(list)
    beliefs_by_run: dict[str, list[dict]] = defaultdict(list)
    for row in occurrence_rows:
        occurrences_by_run[row["run_id"]].append(row)
    for row in transmission_rows:
        transmissions_by_run[row["run_id"]].append(row)
    for row in recombination_rows:
        recombinations_by_run[row["run_id"]].append(row)
    for row in belief_rows:
        beliefs_by_run[row["run_id"]].append(row)

    run_rows: list[dict] = []
    for run_id, capsules in capsules_by_run.items():
        occurrences = occurrences_by_run[run_id]
        transmissions = transmissions_by_run[run_id]
        retained = sum(int(row["retained"]) for row in transmissions)
        inherited_occurrences = sum(int(row["inherited"]) for row in occurrences)
        partner_game = [row for row in transmissions if row["route"] == "partner-myth→game"]
        run_rows.append(
            {
                "run_id": run_id,
                "condition": capsules[0].condition,
                "capsules": len(capsules),
                "meme_occurrences": len(occurrences),
                "memes_per_capsule": len(occurrences) / len(capsules),
                "inherited_occurrence_rate": inherited_occurrences / len(occurrences) if occurrences else 0.0,
                "first_observed_innovation_rate": sum(int(row["first_observed_innovation"]) for row in occurrences) / len(occurrences) if occurrences else 0.0,
                "edge_transmission_rate": retained / len(transmissions) if transmissions else 0.0,
                "variant_shift_rate": sum(int(row["variant_shift"]) for row in transmissions) / retained if retained else 0.0,
                "partner_myth_to_game_rate": sum(int(row["retained"]) for row in partner_game) / len(partner_game) if partner_game else 0.0,
                "recombination_candidates": len(recombinations_by_run[run_id]),
                "recombination_candidates_per_capsule": len(recombinations_by_run[run_id]) / len(capsules),
                "belief_packets": len(beliefs_by_run[run_id]),
                "decoded_discrepancies": sum(int(row["decoded_discrepancy"]) for row in beliefs_by_run[run_id]),
            }
        )

    # Per-run, per-family metrics for mean ± SD reporting.
    run_family_rows: list[dict] = []
    trans_by_run_family: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in transmission_rows:
        trans_by_run_family[(row["run_id"], row["meme_family"])].append(row)
    for run_id, capsules in capsules_by_run.items():
        condition = capsules[0].condition
        run_occurrences = occurrences_by_run[run_id]
        for definition in MEMES:
            family = definition.family
            occurrences = [row for row in run_occurrences if row["meme_family"] == family]
            transmissions = trans_by_run_family[(run_id, family)]
            partner_game = [row for row in transmissions if row["route"] == "partner-myth→game"]
            lineage = next(
                (row for row in lineage_rows if row["run_id"] == run_id and row["meme_family"] == family),
                None,
            )
            run_family_rows.append(
                {
                    "run_id": run_id,
                    "condition": condition,
                    "meme_family": family,
                    "capsule_prevalence": len(occurrences) / len(capsules),
                    "edge_transmission_rate": sum(int(row["retained"]) for row in transmissions) / len(transmissions) if transmissions else math.nan,
                    "partner_myth_to_game_rate": sum(int(row["retained"]) for row in partner_game) / len(partner_game) if partner_game else math.nan,
                    "round_span": int(lineage["round_span"]) if lineage else 0,
                    "variant_count": int(lineage["variant_count"]) if lineage else 0,
                }
            )

    condition_rows: list[dict] = []
    by_condition: dict[str, list[dict]] = defaultdict(list)
    for row in run_rows:
        by_condition[row["condition"]].append(row)
    run_metrics = [
        "memes_per_capsule",
        "inherited_occurrence_rate",
        "first_observed_innovation_rate",
        "edge_transmission_rate",
        "variant_shift_rate",
        "partner_myth_to_game_rate",
        "recombination_candidates",
        "recombination_candidates_per_capsule",
        "belief_packets",
        "decoded_discrepancies",
    ]
    for condition, rows in sorted(by_condition.items(), key=lambda item: TASK_ORDER.get(item[0], 999)):
        summary: dict[str, object] = {"condition": condition, "runs": len(rows)}
        for metric in run_metrics:
            avg, sd = summarize([float(row[metric]) for row in rows])
            summary[f"{metric}_mean"] = avg
            summary[f"{metric}_std"] = sd
        condition_rows.append(summary)

    family_rows: list[dict] = []
    by_family: dict[str, list[dict]] = defaultdict(list)
    for row in run_family_rows:
        by_family[row["meme_family"]].append(row)
    for family, rows in by_family.items():
        definition = MEME_BY_FAMILY[family]
        summary = {"meme_family": family, "description": definition.description, "runs": len(rows)}
        for metric in ("capsule_prevalence", "edge_transmission_rate", "partner_myth_to_game_rate", "round_span", "variant_count"):
            avg, sd = summarize([float(row[metric]) for row in rows])
            summary[f"{metric}_mean"] = avg
            summary[f"{metric}_std"] = sd
        family_rows.append(summary)
    family_rows.sort(key=lambda row: float(row["capsule_prevalence_mean"]), reverse=True)

    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(output_dir / "meme_occurrences.csv", occurrence_rows, list(occurrence_rows[0]))
    write_csv(output_dir / "meme_transmissions.csv", transmission_rows, list(transmission_rows[0]))
    write_csv(output_dir / "meme_lineages.csv", lineage_rows, list(lineage_rows[0]))
    write_csv(output_dir / "recombination_candidates.csv", recombination_rows, list(recombination_rows[0]))
    write_csv(output_dir / "belief_transmission_events.csv", belief_rows, list(belief_rows[0]))
    write_csv(output_dir / "run_meme_summary.csv", run_rows, list(run_rows[0]))
    write_csv(output_dir / "condition_meme_summary.csv", condition_rows, list(condition_rows[0]))
    write_csv(output_dir / "family_meme_summary.csv", family_rows, list(family_rows[0]))

    mutation_counts: dict[tuple[str, str, str, str], int] = defaultdict(int)
    for row in transmission_rows:
        if int(row["variant_shift"]):
            mutation_counts[(row["meme_family"], row["parent_variant"], row["child_variant"], row["route"])] += 1
    mutation_rows = [
        {
            "meme_family": family,
            "parent_variant": parent_variant,
            "child_variant": child_variant,
            "route": route,
            "count": count,
        }
        for (family, parent_variant, child_variant, route), count in sorted(
            mutation_counts.items(), key=lambda item: item[1], reverse=True
        )
    ]
    write_csv(output_dir / "variant_shift_counts.csv", mutation_rows, list(mutation_rows[0]))

    report = [
        "# Meme evolution in the corrected informed-noise runs",
        "",
        f"**Corpus:** {len(run_rows)} runs, {len(all_capsules):,} capsules, "
        f"{len(occurrence_rows):,} meme occurrences, {len(transmission_rows):,} meme exposure edges, "
        f"and {len(belief_rows):,} candidate private-belief packets.",
        "",
        "Here, a meme is a predeclared strategy idea with named variants. Inheritance means that the idea "
        "appeared in a visible parent capsule and in the child capsule. A variant shift means the family "
        "survived but its formulation changed. These are textual evolutionary operations, not evidence of "
        "biological-style selection or behavioral causality.",
        "",
        "## Condition-level dynamics",
        "",
        "| Condition | Runs | Memes/capsule | Inherited occurrences | New-to-visible-lineage | Edge transmission | Variant shifts among retained | Partner myth→game transmission | Recombination candidates/capsule | Belief packets/run | Decoded discrepancies/run |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for condition, rows in sorted(by_condition.items(), key=lambda item: TASK_ORDER.get(item[0], 999)):
        report.append(
            "| "
            + " | ".join(
                [
                    condition,
                    str(len(rows)),
                    fmt_mean_sd([float(row["memes_per_capsule"]) for row in rows]),
                    fmt_mean_sd([float(row["inherited_occurrence_rate"]) for row in rows], percent=True),
                    fmt_mean_sd([float(row["first_observed_innovation_rate"]) for row in rows], percent=True),
                    fmt_mean_sd([float(row["edge_transmission_rate"]) for row in rows], percent=True),
                    fmt_mean_sd([float(row["variant_shift_rate"]) for row in rows], percent=True),
                    fmt_mean_sd([float(row["partner_myth_to_game_rate"]) for row in rows], percent=True),
                    fmt_mean_sd([float(row["recombination_candidates_per_capsule"]) for row in rows]),
                    fmt_mean_sd([float(row["belief_packets"]) for row in rows]),
                    fmt_mean_sd([float(row["decoded_discrepancies"]) for row in rows]),
                ]
            )
            + " |"
        )

    report.extend(
        [
            "",
            "## Meme families",
            "",
            "| Meme | Meaning | Capsule prevalence | Edge transmission | Partner myth→game transmission | Round span | Variants/run |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for family_row in family_rows:
        rows = by_family[family_row["meme_family"]]
        report.append(
            "| "
            + " | ".join(
                [
                    str(family_row["meme_family"]),
                    str(family_row["description"]),
                    fmt_mean_sd([float(row["capsule_prevalence"]) for row in rows], percent=True),
                    fmt_mean_sd([float(row["edge_transmission_rate"]) for row in rows], percent=True),
                    fmt_mean_sd([float(row["partner_myth_to_game_rate"]) for row in rows], percent=True),
                    fmt_mean_sd([float(row["round_span"]) for row in rows]),
                    fmt_mean_sd([float(row["variant_count"]) for row in rows]),
                ]
            )
            + " |"
        )

    decoded_rows = [row for row in belief_rows if int(row["decoded_discrepancy"])]
    report.extend(
        [
            "",
            "## Private-belief transmission",
            "",
            f"The strict detector found **{len(decoded_rows)} decoded discrepancy episodes** among "
            f"**{len(belief_rows)} candidate numerical belief packets**. A candidate requires a partner myth "
            "and later game rationale to share both an event reference and a numerical claim. A decoded "
            "episode additionally requires explicit perception/noise contrast language.",
            "",
            "| Condition | Source→recipient | Rounds | Shared packet | Recipient decision | Source myth | Recipient reasoning |",
            "|---|---|---:|---|---:|---|---|",
        ]
    )
    for row in decoded_rows[:20]:
        source_excerpt = str(row["source_myth_excerpt"]).replace("|", "\\|")
        child_excerpt = str(row["recipient_game_excerpt"]).replace("|", "\\|")
        decision = f"{row['decision_kind']} {row['decision_value']}" if row["decision_kind"] else "—"
        report.append(
            f"| {row['condition']} | {row['source_agent']}→{row['recipient_agent']} | "
            f"{row['source_round']}→{row['recipient_round']} | "
            f"`{row['shared_events']}` + `{row['shared_numeric_claims']}` | {decision} | "
            f"{source_excerpt} | {child_excerpt} |"
        )

    report.extend(
        [
            "",
            "## Most common variant shifts",
            "",
            "| Meme | Parent variant | Child variant | Route | Count |",
            "|---|---|---|---|---:|",
        ]
    )
    for row in mutation_rows[:25]:
        report.append(
            f"| {row['meme_family']} | {row['parent_variant']} | {row['child_variant']} | {row['route']} | {row['count']} |"
        )

    report.extend(
        [
            "",
            "## Limits",
            "",
            "- The ontology is theory-driven and deterministic. It will miss unanticipated ideas and can merge distinct uses of the same strategy language.",
            "- Multiple visible parents often carry the same meme, so an edge establishes possible inheritance rather than unique parentage.",
            "- `First observed innovation` means absent from the recorded visible parents and direct task prompt; it does not mean the pretrained model invented the idea from nothing.",
            "- Variant shifts are textual reformulations. Behavioral selection requires testing whether a meme's presence changes later actions under controlled deletion or transplant.",
            "",
            "## Reproduction",
            "",
            "```bash",
            "python scripts/analyze_meme_evolution.py",
            "```",
            "",
        ]
    )
    (output_dir / "report.md").write_text("\n".join(report), encoding="utf-8")

    summary = {
        "input_dir": str(input_dir),
        "run_count": len(run_rows),
        "capsule_count": len(all_capsules),
        "meme_occurrence_count": len(occurrence_rows),
        "meme_exposure_edge_count": len(transmission_rows),
        "belief_packet_count": len(belief_rows),
        "decoded_discrepancy_count": len(decoded_rows),
        "recombination_candidate_count": len(recombination_rows),
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_dir", nargs="?", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    summary = analyze(args.input_dir.resolve(), args.output.resolve())
    print(
        f"Analyzed {summary['run_count']} runs: {summary['meme_occurrence_count']} meme occurrences, "
        f"{summary['meme_exposure_edge_count']} exposure edges, "
        f"{summary['belief_packet_count']} belief packets, "
        f"{summary['decoded_discrepancy_count']} decoded discrepancies."
    )
    print(f"Report: {args.output.resolve() / 'report.md'}")


if __name__ == "__main__":
    main()

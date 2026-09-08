#!/usr/bin/env python3
"""Trace deterministic claim transmission through saved agent messages.

The analysis treats each visible assistant response as a *capsule*.  For every
capsule it reconstructs which earlier self-responses and partner myths were
actually present in ``messages_sent``.  It then extracts conservative claim
atoms and records which atoms recur across those visible parent -> child edges.

No model calls, embeddings, or fuzzy semantic judges are used.  The supported
claim atoms are:

* event references (``Round 6`` / ``the sixth cycle``)
* round-linked sent, received, and returned quantities when syntax is explicit
* percentages (numeric or written, e.g. ``55%`` / ``fifty-five percent``)
* pre-declared normative frames such as equilibrium, reciprocity, and caution

This makes the output reproducible and auditable, at the cost of missing
paraphrases outside the lexicon.  It establishes textual availability and
retransmission, not causal influence on the model's decision.

Usage:
    python scripts/analyze_capsule_genealogies.py [INPUT_DIR] [--output DIR]
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from statistics import mean, stdev
from typing import Iterable


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = (
    PROJECT_ROOT
    / "data/share/corrected_informed_noise_confirmatory_60runs_2026-08-12/data"
)
DEFAULT_OUTPUT = PROJECT_ROOT / "data/analysis/capsule_genealogies_2026_08_19"


CONDITION_NAMES = {
    "noise2i_memprimary_v2_game": "2-agent · Game only",
    "noise2i_memprimary_v2_game_myth": "2-agent · Game→Myth",
    "noise2i_memprimary_v2_myth_game": "2-agent · Myth→Game",
    "noise8i_memprimary_v2_game": "8-agent · Game only",
    "noise8i_memprimary_v2_game_myth": "8-agent · Game→Myth",
    "noise8i_memprimary_v2_myth_game": "8-agent · Myth→Game",
}

TASK_ORDER = {
    "2-agent · Game only": 0,
    "2-agent · Game→Myth": 1,
    "2-agent · Myth→Game": 2,
    "8-agent · Game only": 3,
    "8-agent · Game→Myth": 4,
    "8-agent · Myth→Game": 5,
}


NORM_PATTERNS = {
    "trust": re.compile(r"\b(?:trust|trusted|trusting|trustworthy|faith)\b", re.I),
    "reciprocity": re.compile(r"\b(?:reciprocity|reciprocal|reciprocate|reciprocated)\b", re.I),
    "fairness": re.compile(r"\b(?:fair|fairly|fairness|integrity|honor|honour)\b", re.I),
    "equilibrium": re.compile(r"\b(?:equilibrium|middle path|balanced? rhythm|harmony)\b", re.I),
    "sustainability": re.compile(r"\b(?:sustain\w*|enduring|endure|lasting|long[- ]term)\b", re.I),
    "escalation": re.compile(r"\b(?:escalat\w*|positive spiral|increasing trust|renewed (?:courage|boldness))\b", re.I),
    "moderation": re.compile(r"\b(?:moderat\w*|cautio\w*|restraint|recalibrat\w*|measured)\b", re.I),
    "noise_awareness": re.compile(r"\b(?:communication noise|noise|distort\w*|imperfect communication|different from what was actually)\b", re.I),
    "prosperity": re.compile(r"\b(?:prosper\w*|mutual abundance|both .* flourish|both .* thrive)\b", re.I),
    "punishment": re.compile(r"\b(?:punish\w*|retaliat\w*|betray\w*|defect\w*|exploit\w*)\b", re.I),
}


ORDINALS = {
    "first": 1,
    "second": 2,
    "third": 3,
    "fourth": 4,
    "fifth": 5,
    "sixth": 6,
    "seventh": 7,
    "eighth": 8,
    "ninth": 9,
    "tenth": 10,
    "eleventh": 11,
    "twelfth": 12,
    "thirteenth": 13,
    "fourteenth": 14,
    "fifteenth": 15,
    "sixteenth": 16,
    "seventeenth": 17,
    "eighteenth": 18,
    "nineteenth": 19,
    "twentieth": 20,
}

ONES = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
}

TENS = {
    "twenty": 20,
    "thirty": 30,
    "forty": 40,
    "fifty": 50,
    "sixty": 60,
    "seventy": 70,
    "eighty": 80,
    "ninety": 90,
}

NUMBER_WORD = "(?:" + "|".join([*ONES, *TENS]) + ")"
FRACTION_WORD = r"(?:a half|one half|three quarters|three-quarters|six tenths|six-tenths)"
NUMBER_EXPR = rf"(?:\$\s*)?\d+(?:\.\d+)?|{NUMBER_WORD}(?:[- ]{NUMBER_WORD})?(?:\s+and\s+{FRACTION_WORD})?"
NUMBER_RE = re.compile(NUMBER_EXPR, re.I)
PERCENT_RE = re.compile(
    rf"(?P<n>\d+(?:\.\d+)?|{NUMBER_WORD}(?:[- ]{NUMBER_WORD})?)\s*(?:%|\bpercent\b)",
    re.I,
)
ROUND_RE = re.compile(r"\bround\s+(\d{1,2})\b", re.I)
ORDINAL_ROUND_RE = re.compile(
    r"\b(" + "|".join(ORDINALS) + r")\s+(?:cycle|round|turning|exchange)\b",
    re.I,
)
OPENING_RE = re.compile(r"\b(?:opened|began|opening exchange|first offering)\b", re.I)

ACTION_PATTERNS = {
    "sent": re.compile(
        rf"\b(?:sent|send|offered|offer|cast|released|release|planted|plant|"
        rf"poured|pour|gave|give|gifted|shared|opened|began)\b[^.;:\n]{{0,45}}?(?P<n>{NUMBER_EXPR})",
        re.I,
    ),
    "returned": re.compile(
        rf"\b(?:returned|return|gave back|sent back|received back)\b[^.;:\n]{{0,35}}?(?P<n>{NUMBER_EXPR})",
        re.I,
    ),
    "received": re.compile(
        rf"\b(?:received|receive)\b(?!\s+back)[^.;:\n]{{0,35}}?(?P<n>{NUMBER_EXPR})",
        re.I,
    ),
}

REVERSED_ACTION_PATTERNS = {
    "sent": re.compile(
        rf"(?P<n>{NUMBER_EXPR})\s+(?:stones?|gems?|orbs?|seeds?|coins?|crystals?|"
        rf"vessels?|pearls?|flames?|embers?|measures?|parts?|stars?|steps?)\s+"
        rf"\b(?:sent|offered|cast|released|planted|poured|given|shared)\b",
        re.I,
    ),
}

SOURCE_SENT_RE = re.compile(
    rf"\b(?:received|receive)[^;:\n]{{0,60}}?\bfrom\s+"
    rf"(?:their\s+|the sender(?:'s)?\s+)?(?P<n>{NUMBER_EXPR})",
    re.I,
)


@dataclass(frozen=True)
class Claim:
    key: str
    kind: str
    label: str
    evidence: str = field(compare=False)
    event_round: int | None = field(default=None, compare=False)
    action: str | None = field(default=None, compare=False)
    value: float | None = field(default=None, compare=False)


@dataclass
class Capsule:
    capsule_id: str
    run_id: str
    condition: str
    agent_id: str
    opponent_id: str | None
    round: int
    task: str
    interaction_index: int
    text: str
    messages_sent: list[dict]
    claims: dict[str, Claim]
    parents: list[tuple["Capsule", str]] = field(default_factory=list)
    direct_claims: dict[str, Claim] = field(default_factory=dict)


def is_primary_json(path: Path) -> bool:
    return (
        path.suffix == ".json"
        and not path.name.endswith(".results.json")
        and not path.name.endswith(".checkpoint.json")
        and not path.name.endswith(".error.json")
    )


def compact(text: str, limit: int = 180) -> str:
    value = re.sub(r"\s+", " ", text).strip()
    return value if len(value) <= limit else value[: limit - 1].rstrip() + "…"


def parse_number(value: str) -> float | None:
    text = value.lower().replace("$", "").strip().replace("-", " ")
    try:
        return float(text)
    except ValueError:
        pass

    if " and " in text:
        whole_text, fraction_text = text.split(" and ", 1)
        whole = parse_number(whole_text)
        fractions = {
            "a half": 0.5,
            "one half": 0.5,
            "three quarters": 0.75,
            "six tenths": 0.6,
        }
        fraction = fractions.get(fraction_text)
        if whole is not None and fraction is not None:
            return whole + fraction

    words = text.split()
    if len(words) == 1:
        if words[0] in ONES:
            return float(ONES[words[0]])
        if words[0] in TENS:
            return float(TENS[words[0]])
    if len(words) == 2 and words[0] in TENS and words[1] in ONES:
        return float(TENS[words[0]] + ONES[words[1]])
    return None


def segment_rounds(text: str) -> list[tuple[int, str]]:
    """Return explicit round-anchored chunks, including mythic ordinal rounds."""
    markers: list[tuple[int, int, int]] = []
    for match in ROUND_RE.finditer(text):
        markers.append((match.start(), match.end(), int(match.group(1))))
    for match in ORDINAL_ROUND_RE.finditer(text):
        markers.append((match.start(), match.end(), ORDINALS[match.group(1).lower()]))
    markers.sort()

    chunks: list[tuple[int, str]] = []
    for index, (start, _end, round_number) in enumerate(markers):
        stop = markers[index + 1][0] if index + 1 < len(markers) else len(text)
        # A ledger line should not absorb all subsequent prose merely because
        # no new marker follows it.  Paragraph/newline boundaries are safer.
        line_end = text.find("\n", start, stop)
        # Ledger-style markers have facts on the same line.  A standalone
        # prompt marker ("Round 10\n\nYou are...") needs the following body.
        if line_end != -1 and text[_end:line_end].strip():
            stop = min(stop, line_end)
        chunks.append((round_number, text[start:stop]))

    # Myths commonly encode round 1 as "opened/began with ...".
    for paragraph in re.split(r"\n\s*\n", text):
        if OPENING_RE.search(paragraph) and not ROUND_RE.search(paragraph) and not ORDINAL_ROUND_RE.search(paragraph):
            chunks.append((1, paragraph))
    return chunks


def action_claims(round_number: int, segment: str) -> list[Claim]:
    claims: list[Claim] = []
    patterns = [(action, pattern) for action, pattern in ACTION_PATTERNS.items()]
    patterns.extend((action, pattern) for action, pattern in REVERSED_ACTION_PATTERNS.items())
    patterns.append(("sent", SOURCE_SENT_RE))
    for action, pattern in patterns:
        for match in pattern.finditer(segment):
            raw_value = match.group("n")
            # Percentages describe a rate, not an amount transferred.
            tail = segment[match.end("n") : match.end("n") + 12]
            if re.match(r"\s*(?:%|percent)\b", tail, re.I):
                continue
            value = parse_number(raw_value)
            if value is None or value < 0 or value > 20:
                continue
            key = f"fact:r{round_number}:{action}:{value:.2f}"
            claims.append(
                Claim(
                    key=key,
                    kind="fact",
                    label=f"round {round_number} {action} {value:g}",
                    evidence=compact(segment),
                    event_round=round_number,
                    action=action,
                    value=value,
                )
            )
    return claims


def extract_claims(text: str) -> dict[str, Claim]:
    claims: dict[str, Claim] = {}
    if not text:
        return claims

    for round_number, segment in segment_rounds(text):
        event = Claim(
            key=f"event:r{round_number}",
            kind="event",
            label=f"round {round_number}",
            evidence=compact(segment),
            event_round=round_number,
        )
        claims.setdefault(event.key, event)
        for claim in action_claims(round_number, segment):
            claims.setdefault(claim.key, claim)

    for match in PERCENT_RE.finditer(text):
        value = parse_number(match.group("n"))
        if value is None or value < 0 or value > 100:
            continue
        start = max(0, match.start() - 80)
        stop = min(len(text), match.end() + 80)
        claim = Claim(
            key=f"rate:{value:.1f}",
            kind="rate",
            label=f"{value:g}%",
            evidence=compact(text[start:stop]),
            value=value,
        )
        claims.setdefault(claim.key, claim)

    for name, pattern in NORM_PATTERNS.items():
        match = pattern.search(text)
        if not match:
            continue
        start = max(0, match.start() - 80)
        stop = min(len(text), match.end() + 80)
        claim = Claim(
            key=f"norm:{name}",
            kind="norm",
            label=name.replace("_", " "),
            evidence=compact(text[start:stop]),
        )
        claims.setdefault(claim.key, claim)
    return claims


def condition_for(path: Path, input_dir: Path, data: dict) -> str:
    relative = path.relative_to(input_dir)
    cell = relative.parts[0]
    if cell in CONDITION_NAMES:
        return CONDITION_NAMES[cell]
    population = f"{len(data.get('agents') or {})}-agent"
    order = data.get("task_order") or []
    order_name = "→".join(task.title() for task in order)
    return f"{population} · {order_name}"


def load_capsules(path: Path, input_dir: Path) -> tuple[dict, list[Capsule]]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)

    condition = condition_for(path, input_dir, data)
    run_id = path.stem
    capsules: list[Capsule] = []
    for agent_id, agent in (data.get("agents") or {}).items():
        for event in agent.get("interaction_history") or []:
            metadata = event.get("metadata") or {}
            response = event.get("response") or {}
            text = str(response.get("content") or "")
            if not text.strip() or event.get("error"):
                continue
            round_number = int(metadata.get("round") or 0)
            task = str(metadata.get("task") or "unknown")
            interaction_index = int(event.get("interaction_index") or 0)
            capsule_id = f"{run_id}:{agent_id}:r{round_number}:{task}:i{interaction_index}"
            capsules.append(
                Capsule(
                    capsule_id=capsule_id,
                    run_id=run_id,
                    condition=condition,
                    agent_id=agent_id,
                    opponent_id=metadata.get("opponent_id"),
                    round=round_number,
                    task=task,
                    interaction_index=interaction_index,
                    text=text,
                    messages_sent=event.get("messages_sent") or [],
                    claims=extract_claims(text),
                )
            )
    return data, capsules


def route_name(parent: Capsule, child: Capsule) -> str:
    if parent.agent_id != child.agent_id:
        return f"partner-{parent.task}→{child.task}"
    if parent.task == "myth" and child.task == "myth":
        return "own-myth→myth"
    return f"{parent.task}→{child.task}"


def attach_parents(capsules: list[Capsule]) -> None:
    by_agent_text: dict[tuple[str, str], list[Capsule]] = defaultdict(list)
    myth_capsules: list[Capsule] = []
    for capsule in capsules:
        by_agent_text[(capsule.agent_id, capsule.text)].append(capsule)
        if capsule.task == "myth":
            myth_capsules.append(capsule)

    for child in capsules:
        parent_by_id: dict[str, tuple[Capsule, str]] = {}
        for message in child.messages_sent:
            content = str(message.get("content") or "")
            if message.get("role") == "assistant":
                candidates = by_agent_text.get((child.agent_id, content), [])
                prior = [candidate for candidate in candidates if candidate.interaction_index < child.interaction_index]
                if prior:
                    parent = max(prior, key=lambda candidate: candidate.interaction_index)
                    parent_by_id[parent.capsule_id] = (parent, route_name(parent, child))
            elif message.get("role") == "user":
                for parent in myth_capsules:
                    if (
                        parent.agent_id != child.agent_id
                        and parent.round <= child.round
                        and len(parent.text) >= 80
                        and parent.text in content
                    ):
                        parent_by_id[parent.capsule_id] = (parent, route_name(parent, child))

        child.parents = sorted(
            parent_by_id.values(),
            key=lambda item: (item[0].round, item[0].interaction_index, item[0].agent_id),
        )

        current_prompt = ""
        if child.messages_sent and child.messages_sent[-1].get("role") == "user":
            current_prompt = str(child.messages_sent[-1].get("content") or "")
        for parent, _route in child.parents:
            if parent.agent_id != child.agent_id and parent.task == "myth":
                current_prompt = current_prompt.replace(parent.text, "")
        child.direct_claims = extract_claims(current_prompt)


def raw_game_prompt_rounds(capsule: Capsule) -> list[int]:
    rounds: list[int] = []
    for message in capsule.messages_sent:
        if message.get("role") != "user":
            continue
        content = str(message.get("content") or "")
        # Actual game prompts start with Round; quoted myth prose can also use
        # the word, but should not determine the raw game-message horizon.
        match = re.match(r"\s*Round\s+(\d{1,2})\b", content, re.I)
        if match:
            rounds.append(int(match.group(1)))
    return rounds


def fact_groups(claims: Iterable[Claim]) -> dict[tuple[int, str], list[Claim]]:
    groups: dict[tuple[int, str], list[Claim]] = defaultdict(list)
    for claim in claims:
        if claim.kind == "fact" and claim.event_round is not None and claim.action:
            groups[(claim.event_round, claim.action)].append(claim)
    return groups


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


def analyze(input_dir: Path, output_dir: Path) -> dict:
    run_paths = sorted(path for path in input_dir.rglob("*.json") if is_primary_json(path))
    all_capsules: list[Capsule] = []
    capsules_by_run: dict[str, list[Capsule]] = {}
    for path in run_paths:
        _data, capsules = load_capsules(path, input_dir)
        attach_parents(capsules)
        all_capsules.extend(capsules)
        capsules_by_run[capsules[0].run_id] = capsules

    capsule_rows: list[dict] = []
    claim_rows: list[dict] = []
    edge_rows: list[dict] = []
    transform_rows: list[dict] = []

    for capsule in all_capsules:
        parent_claim_keys = {
            key
            for parent, _route in capsule.parents
            for key in parent.claims
        }
        inherited = set(capsule.claims) & parent_claim_keys
        supplied = set(capsule.claims) & set(capsule.direct_claims)
        novel = set(capsule.claims) - inherited - supplied
        prompt_rounds = raw_game_prompt_rounds(capsule)
        oldest_raw_round = min(prompt_rounds) if prompt_rounds else None
        event_claims = [claim for claim in capsule.claims.values() if claim.kind == "event"]
        beyond_events = [
            claim
            for claim in event_claims
            if oldest_raw_round is not None
            and claim.event_round is not None
            and claim.event_round < oldest_raw_round
        ]
        beyond_claim_keys = {
            claim.key
            for claim in capsule.claims.values()
            if oldest_raw_round is not None
            and claim.event_round is not None
            and claim.event_round < oldest_raw_round
        }
        kind_counts = {
            kind: sum(claim.kind == kind for claim in capsule.claims.values())
            for kind in ("event", "fact", "rate", "norm")
        }
        inherited_kind_counts = {
            kind: sum(capsule.claims[key].kind == kind for key in inherited)
            for kind in ("event", "fact", "rate", "norm")
        }
        max_event_age = max(
            (capsule.round - claim.event_round for claim in event_claims if claim.event_round is not None),
            default=0,
        )
        capsule_rows.append(
            {
                "capsule_id": capsule.capsule_id,
                "run_id": capsule.run_id,
                "condition": capsule.condition,
                "agent_id": capsule.agent_id,
                "opponent_id": capsule.opponent_id or "",
                "round": capsule.round,
                "task": capsule.task,
                "interaction_index": capsule.interaction_index,
                "visible_parent_count": len(capsule.parents),
                "visible_routes": "|".join(sorted({route for _parent, route in capsule.parents})),
                "claim_count": len(capsule.claims),
                "inherited_claim_count": len(inherited),
                "prompt_supplied_claim_count": len(supplied),
                "novel_claim_count": len(novel),
                "event_claim_count": len(event_claims),
                "beyond_raw_event_count": len(beyond_events),
                "event_inherited_count": inherited_kind_counts["event"],
                "fact_claim_count": kind_counts["fact"],
                "fact_inherited_count": inherited_kind_counts["fact"],
                "rate_claim_count": kind_counts["rate"],
                "rate_inherited_count": inherited_kind_counts["rate"],
                "norm_claim_count": kind_counts["norm"],
                "norm_inherited_count": inherited_kind_counts["norm"],
                "oldest_raw_game_round": oldest_raw_round if oldest_raw_round is not None else "",
                "max_event_age": max_event_age,
                "response_excerpt": compact(capsule.text),
            }
        )
        for claim in capsule.claims.values():
            claim_rows.append(
                {
                    "capsule_id": capsule.capsule_id,
                    "run_id": capsule.run_id,
                    "condition": capsule.condition,
                    "agent_id": capsule.agent_id,
                    "round": capsule.round,
                    "task": capsule.task,
                    "claim_key": claim.key,
                    "claim_kind": claim.kind,
                    "claim_label": claim.label,
                    "event_round": claim.event_round if claim.event_round is not None else "",
                    "event_age": capsule.round - claim.event_round if claim.event_round is not None else "",
                    "action": claim.action or "",
                    "value": claim.value if claim.value is not None else "",
                    "inherited": int(claim.key in inherited),
                    "prompt_supplied": int(claim.key in supplied),
                    "novel": int(claim.key in novel),
                    "beyond_raw_window": int(claim.key in beyond_claim_keys),
                    "evidence": claim.evidence,
                }
            )

        for parent, route in capsule.parents:
            shared = sorted(set(parent.claims) & set(capsule.claims))
            edge_rows.append(
                {
                    "run_id": capsule.run_id,
                    "condition": capsule.condition,
                    "parent_capsule_id": parent.capsule_id,
                    "child_capsule_id": capsule.capsule_id,
                    "route": route,
                    "parent_agent": parent.agent_id,
                    "child_agent": capsule.agent_id,
                    "parent_round": parent.round,
                    "child_round": capsule.round,
                    "parent_task": parent.task,
                    "child_task": capsule.task,
                    "shared_claim_count": len(shared),
                    "shared_claims": "|".join(shared),
                }
            )

            parent_facts = fact_groups(parent.claims.values())
            child_facts = fact_groups(capsule.claims.values())
            for fact_key in sorted(set(parent_facts) & set(child_facts)):
                round_number, action = fact_key
                # Multiple quantities with the same round/action in a paragraph
                # are ambiguous (often two role cycles compressed together).
                # Do not manufacture a mutation by choosing among them.
                if len(parent_facts[fact_key]) != 1 or len(child_facts[fact_key]) != 1:
                    continue
                for child_claim in child_facts[fact_key]:
                    parent_claim = parent_facts[fact_key][0]
                    difference = abs(float(parent_claim.value) - float(child_claim.value))
                    if difference <= 0.005:
                        transform = "exact"
                    elif difference <= 0.15:
                        transform = "near_match"
                    else:
                        transform = "different_quantity_candidate"
                    if (
                        parent.task == "game"
                        and capsule.task == "myth"
                        and "$" in parent_claim.evidence
                        and "$" not in child_claim.evidence
                    ):
                        transform = f"metaphorized_{transform}"
                    transform_rows.append(
                        {
                            "run_id": capsule.run_id,
                            "condition": capsule.condition,
                            "route": route,
                            "parent_capsule_id": parent.capsule_id,
                            "child_capsule_id": capsule.capsule_id,
                            "event_round": round_number,
                            "action": action,
                            "parent_value": parent_claim.value,
                            "child_value": child_claim.value,
                            "absolute_difference": difference,
                            "transformation": transform,
                            "parent_evidence": parent_claim.evidence,
                            "child_evidence": child_claim.evidence,
                        }
                    )

    lineage_rows: list[dict] = []
    by_run_agent_claim: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for row in claim_rows:
        by_run_agent_claim[(row["run_id"], row["agent_id"], row["claim_key"])].append(row)
    for (run_id, agent_id, claim_key), rows in by_run_agent_claim.items():
        ordered = sorted(rows, key=lambda row: (int(row["round"]), row["task"]))
        lineage_rows.append(
            {
                "run_id": run_id,
                "condition": ordered[0]["condition"],
                "agent_id": agent_id,
                "claim_key": claim_key,
                "claim_kind": ordered[0]["claim_kind"],
                "claim_label": ordered[0]["claim_label"],
                "first_round": min(int(row["round"]) for row in ordered),
                "last_round": max(int(row["round"]) for row in ordered),
                "round_span": max(int(row["round"]) for row in ordered) - min(int(row["round"]) for row in ordered),
                "instance_count": len(ordered),
                "task_path": "→".join(row["task"] for row in ordered),
                "crossed_raw_window": max(int(row["beyond_raw_window"]) for row in ordered),
                "first_evidence": ordered[0]["evidence"],
                "last_evidence": ordered[-1]["evidence"],
            }
        )

    run_rows: list[dict] = []
    edge_by_run: dict[str, list[dict]] = defaultdict(list)
    transform_by_run: dict[str, list[dict]] = defaultdict(list)
    for row in edge_rows:
        edge_by_run[row["run_id"]].append(row)
    for row in transform_rows:
        transform_by_run[row["run_id"]].append(row)
    capsule_row_by_run: dict[str, list[dict]] = defaultdict(list)
    for row in capsule_rows:
        capsule_row_by_run[row["run_id"]].append(row)

    for run_id, rows in capsule_row_by_run.items():
        edges = edge_by_run[run_id]
        transforms = transform_by_run[run_id]
        total_claims = sum(int(row["claim_count"]) for row in rows)
        total_events = sum(int(row["event_claim_count"]) for row in rows)
        total_facts = sum(int(row["fact_claim_count"]) for row in rows)
        total_rates = sum(int(row["rate_claim_count"]) for row in rows)
        total_norms = sum(int(row["norm_claim_count"]) for row in rows)
        run_rows.append(
            {
                "run_id": run_id,
                "condition": rows[0]["condition"],
                "capsules": len(rows),
                "claims": total_claims,
                "claims_per_capsule": total_claims / len(rows) if rows else math.nan,
                "inherited_claim_rate": sum(int(row["inherited_claim_count"]) for row in rows) / total_claims if total_claims else math.nan,
                "event_inherited_rate": sum(int(row["event_inherited_count"]) for row in rows) / total_events if total_events else 0.0,
                "fact_inherited_rate": sum(int(row["fact_inherited_count"]) for row in rows) / total_facts if total_facts else 0.0,
                "rate_inherited_rate": sum(int(row["rate_inherited_count"]) for row in rows) / total_rates if total_rates else 0.0,
                "norm_inherited_rate": sum(int(row["norm_inherited_count"]) for row in rows) / total_norms if total_norms else 0.0,
                "novel_claim_rate": sum(int(row["novel_claim_count"]) for row in rows) / total_claims if total_claims else math.nan,
                "event_beyond_raw_rate": sum(int(row["beyond_raw_event_count"]) for row in rows) / total_events if total_events else 0.0,
                "max_event_age": max((int(row["max_event_age"]) for row in rows), default=0),
                "visible_edges": len(edges),
                "shared_edges": sum(int(row["shared_claim_count"]) > 0 for row in edges),
                "shared_edge_rate": sum(int(row["shared_claim_count"]) > 0 for row in edges) / len(edges) if edges else 0.0,
                "cross_agent_transmissions": sum(
                    int(row["shared_claim_count"])
                    for row in edges
                    if row["parent_agent"] != row["child_agent"]
                ),
                "fact_transformations": len(transforms),
                "different_quantity_candidates": sum(
                    row["transformation"].endswith("different_quantity_candidate")
                    for row in transforms
                ),
            }
        )

    condition_rows: list[dict] = []
    by_condition: dict[str, list[dict]] = defaultdict(list)
    for row in run_rows:
        by_condition[row["condition"]].append(row)
    metric_names = [
        "capsules",
        "claims_per_capsule",
        "inherited_claim_rate",
        "event_inherited_rate",
        "fact_inherited_rate",
        "rate_inherited_rate",
        "norm_inherited_rate",
        "novel_claim_rate",
        "event_beyond_raw_rate",
        "max_event_age",
        "shared_edge_rate",
        "cross_agent_transmissions",
        "fact_transformations",
        "different_quantity_candidates",
    ]
    for condition, rows in sorted(by_condition.items(), key=lambda item: TASK_ORDER.get(item[0], 999)):
        summary_row: dict[str, object] = {"condition": condition, "runs": len(rows)}
        for metric in metric_names:
            avg, sd = summarize([float(row[metric]) for row in rows])
            summary_row[f"{metric}_mean"] = avg
            summary_row[f"{metric}_std"] = sd
        condition_rows.append(summary_row)

    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(output_dir / "capsules.csv", capsule_rows, list(capsule_rows[0]))
    write_csv(output_dir / "claim_instances.csv", claim_rows, list(claim_rows[0]))
    write_csv(output_dir / "lineage_edges.csv", edge_rows, list(edge_rows[0]))
    write_csv(output_dir / "fact_transformations.csv", transform_rows, list(transform_rows[0]))
    write_csv(output_dir / "claim_lineages.csv", lineage_rows, list(lineage_rows[0]))
    write_csv(output_dir / "run_summary.csv", run_rows, list(run_rows[0]))
    write_csv(output_dir / "condition_summary.csv", condition_rows, list(condition_rows[0]))

    route_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for row in edge_rows:
        route = row["route"]
        route_counts[route]["visible_edges"] += 1
        if int(row["shared_claim_count"]) > 0:
            route_counts[route]["shared_edges"] += 1
        route_counts[route]["claim_transmissions"] += int(row["shared_claim_count"])
        for claim_key in filter(None, str(row["shared_claims"]).split("|")):
            if claim_key.startswith("event:"):
                route_counts[route]["event_transmissions"] += 1
            elif claim_key.startswith("fact:"):
                route_counts[route]["fact_transmissions"] += 1
            elif claim_key.startswith("rate:"):
                route_counts[route]["rate_transmissions"] += 1
            elif claim_key.startswith("norm:"):
                route_counts[route]["norm_transmissions"] += 1

    transformation_counts: dict[str, int] = defaultdict(int)
    for row in transform_rows:
        transformation_counts[row["transformation"]] += 1

    top_event_lineages = sorted(
        [row for row in lineage_rows if row["claim_kind"] == "event"],
        key=lambda row: (
            int(row["crossed_raw_window"]),
            int(row["round_span"]),
            int(row["instance_count"]),
        ),
        reverse=True,
    )[:10]
    top_fact_lineages = sorted(
        [row for row in lineage_rows if row["claim_kind"] in {"fact", "rate"}],
        key=lambda row: (
            int(row["crossed_raw_window"]),
            int(row["round_span"]),
            int(row["instance_count"]),
        ),
        reverse=True,
    )[:15]

    report_lines = [
        "# Descriptive capsule genealogies",
        "",
        f"**Corpus:** {len(run_rows)} runs, {len(all_capsules):,} assistant-response capsules, "
        f"{len(claim_rows):,} deterministic claim instances, and {len(edge_rows):,} visible capsule edges.",
        "",
        "A capsule is a visible assistant response. A parent edge exists only when the parent's full text "
        "was verifiably present in the child's recorded `messages_sent`. A claim transmission exists when "
        "the same deterministic claim atom occurs in both parent and child. This measures textual inheritance, "
        "not causal influence.",
        "",
        "## Condition-level results",
        "",
        "| Condition | Runs | Capsules/run | Claims/capsule | Events inherited | Facts inherited | Rates inherited | Norms inherited | Event mentions beyond raw window | Max event age |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for condition, rows in sorted(by_condition.items(), key=lambda item: TASK_ORDER.get(item[0], 999)):
        report_lines.append(
            "| "
            + " | ".join(
                [
                    condition,
                    str(len(rows)),
                    fmt_mean_sd([float(row["capsules"]) for row in rows]),
                    fmt_mean_sd([float(row["claims_per_capsule"]) for row in rows]),
                    fmt_mean_sd([float(row["event_inherited_rate"]) for row in rows], percent=True),
                    fmt_mean_sd([float(row["fact_inherited_rate"]) for row in rows], percent=True),
                    fmt_mean_sd([float(row["rate_inherited_rate"]) for row in rows], percent=True),
                    fmt_mean_sd([float(row["norm_inherited_rate"]) for row in rows], percent=True),
                    fmt_mean_sd([float(row["event_beyond_raw_rate"]) for row in rows], percent=True),
                    fmt_mean_sd([float(row["max_event_age"]) for row in rows]),
                ]
            )
            + " |"
        )

    report_lines.extend(
        [
            "",
            "`Event mentions beyond raw window` means that a response mentioned round *r* even though the "
            "oldest literal game prompt still in that call's recorded context came after *r*.",
            "",
            "## Transmission routes",
            "",
            "| Route | Visible edges | Event transmissions | Fact transmissions | Rate transmissions | Norm transmissions |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for route, counts in sorted(route_counts.items()):
        report_lines.append(
            f"| {route} | {counts['visible_edges']} | {counts['event_transmissions']} | "
            f"{counts['fact_transmissions']} | {counts['rate_transmissions']} | {counts['norm_transmissions']} |"
        )

    report_lines.extend(
        [
            "",
            "## Quantitative fact transformations",
            "",
            "These are surface matches between round/action-labelled quantities on visible parent edges. "
            "`Near match` differs by at most $0.15. `Different quantity candidate` is deliberately not called "
            "a mutation: without resolving who acted, it may compare different referents from the same round. "
            "`Metaphorized` means a dollar-valued game claim reappeared without a dollar sign in a myth.",
            "",
            "| Transformation | Count |",
            "|---|---:|",
        ]
    )
    for transformation, count in sorted(transformation_counts.items()):
        report_lines.append(f"| {transformation} | {count} |")

    report_lines.extend(
        [
            "",
            "## Long-lived factual and rate lineages",
            "",
            "| Condition | Agent | Claim | First→last round | Instances | Crossed raw window | First evidence | Last evidence |",
            "|---|---|---|---:|---:|---:|---|---|",
        ]
    )
    for row in top_fact_lineages:
        first_evidence = str(row["first_evidence"]).replace("|", "\\|")
        last_evidence = str(row["last_evidence"]).replace("|", "\\|")
        report_lines.append(
            f"| {row['condition']} | {row['agent_id']} | `{row['claim_key']}` | "
            f"{row['first_round']}→{row['last_round']} | {row['instance_count']} | "
            f"{row['crossed_raw_window']} | {first_evidence} | {last_evidence} |"
        )

    report_lines.extend(
        [
            "",
            "## Long-lived event-reference lineages",
            "",
            "| Condition | Agent | Claim | First→last round | Instances | Crossed raw window | First evidence | Last evidence |",
            "|---|---|---|---:|---:|---:|---|---|",
        ]
    )
    for row in top_event_lineages:
        first_evidence = str(row["first_evidence"]).replace("|", "\\|")
        last_evidence = str(row["last_evidence"]).replace("|", "\\|")
        report_lines.append(
            f"| {row['condition']} | {row['agent_id']} | `{row['claim_key']}` | "
            f"{row['first_round']}→{row['last_round']} | {row['instance_count']} | "
            f"{row['crossed_raw_window']} | {first_evidence} | {last_evidence} |"
        )

    report_lines.extend(
        [
            "",
            "## Interpretation limits",
            "",
            "- Exact `messages_sent` establishes what text was available, but not which parent occurrence the model attended to when several contained the same claim.",
            "- The deterministic extractor favors precision over recall. It misses many genuinely equivalent metaphors and cannot infer unstated causal beliefs.",
            "- A repeated claim in a decision explanation demonstrates uptake in visible text, not that the claim caused the numerical action. That requires deletion/transplant ablations.",
            "- `reasoning: null` is irrelevant here: capsules are the visible `content` strings actually resent to later calls.",
            "",
            "## Reproduction",
            "",
            "```bash",
            "python scripts/analyze_capsule_genealogies.py",
            "```",
            "",
        ]
    )
    (output_dir / "report.md").write_text("\n".join(report_lines), encoding="utf-8")

    summary = {
        "input_dir": str(input_dir),
        "run_count": len(run_rows),
        "capsule_count": len(all_capsules),
        "claim_instance_count": len(claim_rows),
        "visible_edge_count": len(edge_rows),
        "route_counts": route_counts,
        "transformation_counts": transformation_counts,
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
    )
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
        f"Analyzed {summary['run_count']} runs: {summary['capsule_count']} capsules, "
        f"{summary['claim_instance_count']} claim instances, "
        f"{summary['visible_edge_count']} visible parent edges."
    )
    print(f"Report: {args.output.resolve() / 'report.md'}")


if __name__ == "__main__":
    main()

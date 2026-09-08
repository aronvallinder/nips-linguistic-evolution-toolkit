"""Unit tests for the exposure-contrast / rewiring-null analysis."""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from analyze_capsule_genealogies import Capsule  # noqa: E402
from analyze_meme_transmission_null import (  # noqa: E402
    FAMILIES,
    build_records,
    family_hits,
    holm_correction,
    precompute_null_probabilities,
)


def make_capsule(run_id, agent_id, round_number, task, text, index, parents=()):
    capsule = Capsule(
        capsule_id=f"{run_id}:{agent_id}:r{round_number}:{task}:i{index}",
        run_id=run_id,
        condition="8-agent · Myth→Game",
        agent_id=agent_id,
        opponent_id=None,
        round=round_number,
        task=task,
        interaction_index=index,
        text=text,
        messages_sent=[],
        claims={},
    )
    capsule.parents = [(parent, "partner-myth→game") for parent in parents]
    return capsule


RECIPROCITY = "We must honor reciprocity and return a fair share."
NEUTRAL = "The towers stood in silence beneath the moon."


def test_family_hits_detects_reciprocity():
    hits = family_hits(RECIPROCITY)
    assert "proportional_reciprocity" in hits
    assert "repair_after_disruption" not in hits
    assert family_hits(NEUTRAL) == set()


def test_build_records_partner_exposure():
    myth_exposed = make_capsule("run1", "B", 1, "myth", RECIPROCITY, 1)
    myth_neutral = make_capsule("run1", "C", 1, "myth", NEUTRAL, 2)
    child_exposed = make_capsule(
        "run1", "A", 1, "game", RECIPROCITY, 3, parents=[myth_exposed]
    )
    child_unexposed = make_capsule(
        "run1", "D", 1, "game", NEUTRAL, 4, parents=[myth_neutral]
    )
    capsules = [myth_exposed, myth_neutral, child_exposed, child_unexposed]
    hits = {capsule.capsule_id: family_hits(capsule.text) for capsule in capsules}

    records = build_records(
        {"run1": capsules}, hits, np.random.default_rng(0)
    )["proportional_reciprocity"]
    by_agent = {record.agent_id: record for record in records}
    assert by_agent["A"].partner_exposed and by_agent["A"].child_has
    assert not by_agent["D"].partner_exposed and not by_agent["D"].child_has


def test_null_probability_is_hypergeometric():
    # Round 1 has 4 myths by agents other than the child; 2 carry the family.
    myths = [
        make_capsule("run1", author, 1, "myth", text, index)
        for index, (author, text) in enumerate(
            [("B", RECIPROCITY), ("C", RECIPROCITY), ("D", NEUTRAL), ("E", NEUTRAL)]
        )
    ]
    child = make_capsule("run1", "A", 1, "game", NEUTRAL, 10, parents=[myths[0]])
    capsules = myths + [child]
    hits = {capsule.capsule_id: family_hits(capsule.text) for capsule in capsules}

    probabilities = precompute_null_probabilities({"run1": capsules}, hits)
    key = ("run1", "A", 10, ((1, "B"),))
    # One draw from 4 candidates, 2 unexposed -> P(not exposed) = 2/4.
    assert abs(probabilities["proportional_reciprocity"][key] - 0.5) < 1e-12


def test_holm_correction_monotone():
    adjusted = holm_correction({"a": 0.01, "b": 0.04, "c": 0.03})
    assert adjusted["a"] == 0.03
    assert adjusted["b"] >= adjusted["c"] >= adjusted["a"]
    assert all(value <= 1.0 for value in adjusted.values())


def test_families_match_meme_ontology():
    assert len(FAMILIES) == 9

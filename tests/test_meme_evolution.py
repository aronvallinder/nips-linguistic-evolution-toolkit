from scripts.analyze_meme_evolution import (
    CONTRAST_RE,
    MYTH_ATTRIBUTION_RE,
    decision_from,
    detect_memes,
)


def test_detects_equilibrium_and_mutual_prosperity_variants():
    memes = detect_memes(
        "Sixty percent given and fifty-five percent returned creates a "
        "sustainable middle path where both flourish."
    )

    assert memes["sustainable_equilibrium"].variant == "moderate_middle"
    assert memes["prosperity_through_cooperation"].variant == "mutual_profit"


def test_detects_measured_escalation_as_an_idea_variant():
    memes = detect_memes(
        "When courage resurges, reciprocity should respond with measured "
        "increases, not wild swings."
    )

    assert memes["trust_escalation"].variant == "measured_escalation"
    assert memes["consistency_over_volatility"].variant == "anti_volatility"


def test_strict_private_belief_decode_requires_myth_attribution():
    decoded = (
        'Their myth says I sent "nearly four stones" (79%), but I actually '
        "sent $3.25 (65%). This confirms significant communication noise."
    )
    noise_without_myth = (
        "They saw $4 due to communication noise, but I actually sent $3.25."
    )

    assert detect_memes(decoded)["noise_adaptation"].variant == "explicit_discrepancy"
    assert CONTRAST_RE.search(decoded)
    assert MYTH_ATTRIBUTION_RE.search(decoded)
    assert CONTRAST_RE.search(noise_without_myth)
    assert not MYTH_ATTRIBUTION_RE.search(noise_without_myth)


def test_extracts_last_structured_decision():
    assert decision_from('Reasoning... {"send": 3.25}') == ("send", 3.25)
    assert decision_from("No structured decision") == ("", None)

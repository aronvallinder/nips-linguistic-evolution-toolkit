from scripts.analyze_capsule_genealogies import (
    Capsule,
    attach_parents,
    extract_claims,
    parse_number,
    raw_game_prompt_rounds,
)


def make_capsule(
    capsule_id,
    agent_id,
    round_number,
    task,
    interaction_index,
    text,
    messages_sent=None,
):
    return Capsule(
        capsule_id=capsule_id,
        run_id="fixture",
        condition="fixture",
        agent_id=agent_id,
        opponent_id=None,
        round=round_number,
        task=task,
        interaction_index=interaction_index,
        text=text,
        messages_sent=messages_sent or [],
        claims=extract_claims(text),
    )


def test_extracts_explicit_ledger_claims_and_rate():
    claims = extract_claims(
        "**Round 6:** Received $11.88 (from $3.96), returned $6.50 (55%)"
    )

    assert "event:r6" in claims
    assert "fact:r6:received:11.88" in claims
    assert "fact:r6:sent:3.96" in claims
    assert "fact:r6:returned:6.50" in claims
    assert "rate:55.0" in claims


def test_extracts_mythic_round_and_written_quantities():
    claims = extract_claims(
        "The sixth cycle saw renewed boldness: nearly four orbs sent again. "
        "The keeper returned six and a half stones."
    )

    assert "event:r6" in claims
    assert "fact:r6:sent:4.00" in claims
    assert "fact:r6:returned:6.50" in claims
    assert parse_number("fifty-five") == 55.0


def test_reconstructs_self_and_partner_capsule_parents():
    self_game = make_capsule(
        "self-game", "Agent_1", 1, "game", 1, "Round 1: I sent $4 (80%)."
    )
    partner_myth = make_capsule(
        "partner-myth",
        "Agent_2",
        1,
        "myth",
        1,
        "Myth: Trust and reciprocity created a sustainable equilibrium. " * 2,
    )
    child = make_capsule(
        "child",
        "Agent_1",
        2,
        "myth",
        2,
        "Myth: Trust and reciprocity continued after Round 1.",
        [
            {"role": "system", "content": "system"},
            {"role": "assistant", "content": self_game.text},
            {
                "role": "user",
                "content": "Here is the other myth:\n" + partner_myth.text,
            },
        ],
    )

    attach_parents([self_game, partner_myth, child])

    assert {(parent.capsule_id, route) for parent, route in child.parents} == {
        ("self-game", "game→myth"),
        ("partner-myth", "partner-myth→myth"),
    }
    # Embedded partner-myth claims are attributed to the partner capsule, not
    # misclassified as direct claims supplied by the experiment prompt.
    assert "norm:equilibrium" not in child.direct_claims


def test_raw_prompt_horizon_ignores_round_mentions_inside_myth_prompts():
    capsule = make_capsule(
        "child",
        "Agent_1",
        10,
        "game",
        10,
        "response",
        [
            {"role": "user", "content": "A myth about Round 1."},
            {"role": "user", "content": "Round 7\n\nYou are the sender."},
            {"role": "user", "content": "Round 10\n\nYou are the receiver."},
        ],
    )

    assert raw_game_prompt_rounds(capsule) == [7, 10]

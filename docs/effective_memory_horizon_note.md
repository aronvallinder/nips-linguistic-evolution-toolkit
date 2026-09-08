# Methodological note: the 3-round memory horizon is porous

**TL;DR.** The memory-primary design caps each agent's *raw* context at ~3 rounds,
and that cap works — the game prompts an agent receives only ever restate the last
three rounds. But agents **re-summarize the full game history in their own
reasoning every round**, and that reasoning is retained in the 3-round window. So
older rounds survive by being re-copied forward in the agent's own words. The
*effective* memory horizon is much longer than 3 rounds — often the entire game in
2-agent dyads. This is **not** the double-memory bug, and it is not fixable in the
harness; it's emergent model behaviour. It is a real confound for any
memory-horizon claim and should be stated in the paper.

## What we observed

Agents routinely cite specific numbers from far more than 3 rounds ago, and the
numbers are **accurate** (they match the noise-communicated values the agent
actually saw — spot-checked exactly). Example — Agent_1's round-10 game call
(`noise2i_memprimary_v2_myth_game`, rep00): the raw game prompts in its context
cover only rounds 7–10, but its own retained reasoning messages recap rounds 1–9
verbatim ("Round 1: I sent $4 (80%)… Round 5: I sent $3.00… Round 6: Received
$11.88…").

### The mechanism (from `agents[id].interaction_history[*].messages_sent`)

Each game call's context contains:
- `user` **game prompts** — minimal templates that mention only the current/last
  round (the double-memory fix at work: no recap block, each round enters once);
- `assistant` **own-reasoning messages** from the last ~3 rounds — and *these*
  restate the entire history so far.

So at round 10 the agent reads its round-8/9 reasoning, which recaps rounds 1–8,
so it can reconstruct 1–9. It's a rolling self-summary (a telephone chain that,
here, stays accurate).

## How common / how large (corrected confirmatory data, game calls, round ≥5)

| | 2-agent (n=360) | 8-agent (n=1440) |
|---|---|---|
| recap reaches beyond the 3-round window | **72%** | **98%** |
| recap reaches all the way to round 1 | **46%** | 1% |
| mean rounds spanned per recap (nominal = 3) | **5.6** (max 10) | 4.0 (max 9) |

- **2-agent dyads** carry the whole relationship forward — nearly half of late-game
  calls recap back to round 1. Effective memory ≈ the full game.
- **8-agent** agents almost always extend past 3 rounds but rarely to round 1:
  rotating partners mean there is no single relationship to narrate, so the
  self-summary covers ~4 recent own-games.

## Does the self-recap stay accurate? (10 rounds yes, 20 rounds no)

Checking the agents' recap of **their own past sends** (which they knew exactly at
the time, so any error is pure memory drift), against ground truth (tolerance
$0.15):

| recapped round is… | 10-round runs | 20-round runs |
|---|---|---|
| 1 round ago | 99% accurate | 86% |
| 2 rounds ago | 100% | 78% |
| 4 rounds ago | 100% | 69% |
| 6 rounds ago | 100% | 44% |

Overall recap accuracy of own past sends, by setup:

| setup | accuracy |
|---|---|
| 2-agent, 10-round | 99% (faithful at every age, even 9 rounds back) |
| 8-agent, 10-round | 83% (77% at 2 ago, 65% at 3 ago; n small) |
| 2-agent, 20-round | drifts 86% → 44% by 6 rounds back |
| 8-agent, 20-round | pending (runs not complete) |

- **2-agent/10-round: near-perfect** — the carried memory is long *and* faithful,
  so the main (10-round dyad) results rest on accurate effective memory.
- **8-agent is already less faithful at 10 rounds** (83%): an agent's own past
  sends were against *rotating* partners, so tracking "which send in which round"
  across a changing cast is harder. (n=71 — 8-agent agents cite own sends less
  often — so treat as indicative.)
- **Longer horizon frays it further** — 2-agent/20-round drops to ~44% for
  6-rounds-back. Fidelity depends on both horizon and population; ordering ≈
  2-agent/10r > 8-agent/10r ≈ 2-agent/20r > 8-agent/20r (expected).

Implication: long-game (wash-out) dynamics are partly driven by a **degraded /
approximated** summary of history, not a faithful one. The metric can't fully
separate deliberate approximation ("~$4.5") from confabulation, but either way the
stated history diverges from ground truth in long games. (2-agent, n=19 20-round
runs; 8-agent 20-round pending.)

## Why this is NOT the double-memory bug

The double-memory bug was **infrastructure duplicating** each round (in-prompt
recap block + chat memory + reasoning → the same fact 2–3×, inflating the
apparent generosity trend). The fix removed the in-prompt recap; the game prompts
are now minimal, and each round's raw data enters context once. That fix is
verified working here. The present effect is orthogonal: the **model** chooses to
re-summarize, and its (legitimately retained) reasoning carries old rounds forward.
Nothing is duplicated; memory is *extended by self-reference*.

## Why it matters

1. "Agents only remember the last 3 rounds" is **false in effect** — especially in
   2-agent dyads, where they effectively remember the whole game.
2. **Memory-horizon manipulations are confounded**: shrinking `memory_capacity`
   will not shorten what an agent effectively remembers, as long as it keeps
   recapping. Any planned "short vs long memory" comparison needs to account for
   this.
3. It plausibly drives the **escalating cooperation / reciprocity** dynamics (the
   agent tracks the full relationship, not a 3-round slice), and it is a larger
   confound for the 2-agent than the 8-agent condition.

## Options (a design trade-off, not a bug fix)

To actually bound effective memory, retain only the **decision** in chat memory
(the `{send: X}` action, or a one-line stripped justification) instead of the full
verbose reasoning. **Cost:** this breaks the reasoning↔myth co-evolution that
memory-primary was built to preserve (myths would no longer see the agent's
strategic reasoning). So it is a genuine trade-off for the team, not a clean fix.

Minimum recommendation for the paper: **state that the effective memory horizon is
longer than the nominal window** (with these numbers), and avoid claiming a
3-round memory bound. Decide separately whether a bounded-memory arm is worth the
co-evolution cost.

---
*Generated 2026-08-19 from `data/share/corrected_informed_noise_confirmatory_60runs_2026-08-12`.*

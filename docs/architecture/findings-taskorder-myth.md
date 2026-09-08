---
title: Findings — task order, myths, and the cultural ratchet
status: current
updated: 2026-09-08
owner: ivar
---

# Findings: task order and myth-mediated cooperation

The endogenous-myth thread (agents write their own myths between game rounds),
distinct from the seeded-transplant thread in
[findings-cooperation-transplant.md](findings-cooperation-transplant.md).
Canonical numbers come from the corrected v2 confirmatory dataset unless noted.

## Myth→Game > Game-only > Game→Myth — the core, replicated result

Writing myths **before** play raises cooperation; writing them **after** play
does not. Confirmed at n=10/cell over all six corrected cells (2/8 agents ×
game / game→myth / myth→game; 60 runs, strict audit clean): final balance
64.86 / 62.94 / 69.83 per agent in repeated dyads and 59.26 / 60.51 / 66.33 in
8-agent rotating populations. Both 8-agent myth→game contrasts survive Holm
correction; game→myth beats game-only in **neither** regime, and its
population-regime interaction is not detected (diff-in-diff +3.16, p=.218).
_(from researchlog 2026-08-13)_

The ordering is model-general: a corrected GPT-5 Nano replication gives
62.64 / 62.34 / 66.26 (Myth→Game vs Game only +3.63, Holm p=.003).
_(from researchlog 2026-08-21)_ Earlier Sonnet triplets show the same ordering
in plain, uninformed-noise, and informed-noise regimes (trust ratio ~0.84–0.89
myth-first vs ~0.65–0.70 game-first); telling agents about the noise barely
moves anything. _(from researchlog 2026-07-17, 2026-07-22)_ The plain 2026-07-17 triplet has a documented provider-change caveat:
the researchlog records OpenRouter reruns for game and game→myth, and their saved
reasoning-text signatures differ from myth→game. Exact native effort is not
recovered by those signatures. Do not promote no-text records from other
triplets to proof of a direct/non-thinking regime. The
[reassessment](../api-audit-reassessment-2026-09-08.md) lists the bounded evidence;
this caveat does not by itself invalidate within-condition observations.
_(from researchlog 2026-09-08)_

## Mechanism: the cultural ratchet cuts both ways

- **Founding myths seed the opening.** Myth-first populations open generous and
  hit the $5 send ceiling by ~round 4; game-first populations cold-open at
  ~3.0 (structurally identical round-1 context to game-only) and climb slowly.
  The plateau follows the myths, not memory depth: a game-only run with matched
  memory rounds escalates normally. Directive myths written after play codify
  the cautious status quo and anchor it. _(from researchlog 2026-07-20)_
- **Washout is a historical observation with a provenance caveat.** In a 20-round 8-agent washout
  (n=5/arm, directional), per-round sends never converge (myth-first ~4.9 vs
  game-first ~4.4 at round 20) and the cumulative-balance lead grows from
  +11.4/agent at round 10 to +17.9 at round 20. In dyads, sends do converge
  and the lead plateaus (~+6). _(from researchlog 2026-08-19)_
  The 30 checked washout finals contain 23 OpenRouter and seven Anthropic
  top-level labels. Two Anthropic-labelled population myth→game finals contain
  reasoning text in rounds 1–10 but not 11–20. A single run-level label cannot
  establish their full request history; inspect that transition before treating
  the longer-horizon contrast as clean evidence of persistence. This is a
  recorded signature change, not proof of an exact provider switch.
  _(from researchlog 2026-09-08)_
- **Transmission fidelity moderates the effect in both directions.** A lineage
  pointer ("Base it on the myths you wrote earlier this session") raises
  self-myth similarity 0.709→0.839 without collapsing population diversity,
  and amplifies whatever the myths crystallize: myth-first balance rises
  ($66.91→$70.69) while game-first stays anchored ($59.95→$59.00) — a
  fidelity knob on the culture→behavior link, with the decision side
  uninstructed. _(from researchlog 2026-07-23)_

## Textual-evolution evidence (visible inheritance, not yet causal)

Deterministic no-LLM analyses over the 60 corrected runs:

- **Capsule genealogy:** 5,000 capsules, 32,700 verified parent→child edges.
  Exact fact inheritance is far stronger in dyads (43–61%) than 8-agent cells
  (11–15%); in dyadic myth→game, 30% of event references reach beyond the
  literal context window (8-agent: 2.5%). Norm inheritance ~90% in every
  myth-bearing cell. _(from researchlog 2026-08-19)_
- **Meme evolution:** myth-bearing conditions carry more ideas per capsule
  (~2.7 vs ~1.8). Proportional reciprocity dominates (75% capsule prevalence);
  25–31% of retained memes shift variant, mostly between fixed-percentage and
  responsive-reward forms. Two decoded private-belief packets (myth-carried
  noisy perceptions surfacing in a partner's game reasoning) exist but are
  rare. _(from researchlog 2026-08-19)_
- **Meme transmission is mostly base rate.** Against a degree-preserving
  rewiring null with exposure contrasts, the raw ~88% "inheritance" reduces to
  single-digit percentage-point excess; the largest regex families fail a
  future-myth control (a not-yet-visible myth predicts adoption as well as the
  seen one), and `noise_adaptation` is prompt elicitation. Under blinded
  LLM-judge labels (5,000 capsules) no family survives cleanly. Two weak regex
  candidates remain (sustainable_equilibrium, proportional_reciprocity).
  _(from researchlog 2026-08-28)_

Genealogy and meme counts establish visible textual inheritance only, and the
null analysis shows that inheritance is not evidence of transmission; the
seeding/transplant intervention with actions held fixed is the causal test.

## Return behavior: the send/return gap is a denominator artifact

Plots normalize send by the $5 endowment but return by the *tripled* receipt.
In dollars, receivers returned more than was sent in 98.5% of the 1,500
corrected confirmatory dyad-rounds; returned/sent ≈150% everywhere. Receivers
anchor on "return half of the tripled pool" (~50–54% in all cells); myths move
sends, not returns. The old zero-send explanation is retracted.
_(from researchlog 2026-08-20)_

## Superseded claims

- **"60–77% edge transmission" of memes (2026-08-19)** was base rate; honest
  excess over the rewiring null is single-digit pp and no family survives
  under judge labels. _(2026-08-28 supersedes 2026-08-19)_

- **"game_myth vs game is a population-size effect" (2026-08-10)** ran on the
  broken dyad transfer-noise path (post-round-1 receivers saw ~$0) and is
  superseded by the corrected confirmatory result above. _(2026-08-13
  supersedes 2026-08-10)_
- **Noise-buffering by population size** (dyads collapse under noise, 8-agent
  populations don't; 2026-07-17) predates the dyad transfer fix; the corrected
  dataset shows dyads outperforming 8-agent cells on balance. Treat the old
  dyad-collapse numbers as artifact-contaminated.

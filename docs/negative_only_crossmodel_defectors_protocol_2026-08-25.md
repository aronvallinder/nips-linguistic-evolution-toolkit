# Frozen protocol: negative-only cross-model and defection batch

## Purpose

Rerun the population-by-task-order matrix shown on slide 695 of the shared
meeting deck after replacing signed transfer noise, `U(-1,+1)`, with informed
negative-only transfer noise, `U(-1,0)`. Extend the same paired matrix with the
defection treatments requested in the 24 August meeting.

The primary descriptive outcomes are final cumulative balance, proportion
sent, and proportion returned by round. The batch is frozen before outcomes
are observed.

## Matrix

Models:

- Claude Sonnet 4.5 (`anthropic/claude-sonnet-4.5`);
- GPT-5 Nano (`openai/gpt-5-nano`); and
- Gemini 3.7 Flash (`google/gemini-3.7-flash`).

Task orders:

- Game only;
- Game-to-Myth; and
- Myth-to-Game.

Population/treatment arms:

| Population regime | Control | Treatment 1 | Treatment 2 |
|---|---|---|---|
| Two-agent repeated dyad | no forced defection | 25% random defection | 50% random defection |
| Eight-agent rotating population | no fixed defectors | 2 of 8 fixed defectors | 4 of 8 fixed defectors |

There are five paired replicates per model × task order × population ×
treatment cell (`replicate_id` 0–4): 54 cells and 270 runs in total.

## Common protocol

- Ten game rounds, $5 sender endowment, and a 3× transfer multiplier.
- Temperature 0.8 where the direct provider accepts it.
- Transfer noise is sampled independently after both send and return choices,
  then clamped to the feasible interval. Its raw support is `U(-1,0)`, so a
  communicated transfer can never exceed the chosen transfer.
- Agents are informed that communication noise may be present.
- Game-only cells retain three exchanges in memory; two-task cells retain six
  exchanges, preserving approximately three complete task rounds.
- Two-task cells use the existing memory-primary myth prompts and the shared
  myth-to-decision instruction.
- The dyad uses the corrected minimal later-round prompts and a fixed partner.
- The eight-agent population uses balanced anonymous rotation plus the current
  co-player's previous three interactions, matching the rotating-population
  regime represented on slide 695.
- No punishment/deduction stage is enabled.

## Defection interventions

Fixed defectors are hidden mechanical agents. They always send zero and return
zero without a game LLM call, but write myths through the ordinary model path.
The two-defector assignment is nested in the four-defector assignment within a
matched replicate.

Random dyadic defection is a seeded Bernoulli override on each agent game
decision, whether send or return. A selected decision is replaced with zero
without an LLM call and recorded with response source
`random_defection_forced_zero`. The schedule is keyed by replicate seed, round,
agent ID, and role. It is stable across retries and resumes, paired across
models and task orders, and nested so that every 25% event also occurs in the
matched 50% arm. Agents receive no treatment label.

## Pairing and provenance

Noise and pairing use `protocol_seed_base = 202608250` plus the replicate ID.
Random-defection schedules use the same resolved protocol seed. Fixed-defector
assignments use the replicate ID. This pairs exogenous schedules across models,
task orders, and treatment arms without coupling them to provider RNG.

Runs must be launched from a clean committed worktree. Every final JSON records
the code commit, config hash, provider settings, pairing/noise seeds, defector
assignment or random-defection probability, and response source for each game
decision.

Direct-provider settings are:

- Anthropic maximum output: 4096 tokens;
- OpenAI reasoning effort: provider default for this repository (`minimal`);
- Gemini thinking level: `medium`; and
- Gemini request timeout: 300 seconds.

## Integrity gates and plots

The post-run analysis fails closed unless it finds exactly 270 clean,
ten-round runs; five replicates in every cell; the expected model, population,
task-order, and treatment matrix; paired seeds; negative-only noise bounds;
nested fixed-defector assignments; and nested random receiver-defection events.

For every population regime and task order, the analysis plots both:

1. returned amount divided by the amount actually received, conditional on a
   positive receipt; and
2. the rate of zero receipts, which is shown separately rather than silently
   treating `0/0` as a zero return proportion.

Eight-agent figures are produced for all receivers and ordinary receivers
only. Points are means of independent run-level round summaries, with 95%
Student-t intervals across the five replicates. The analysis also exports the
run manifest, receiver-decision table, run-round metrics, and plotted summary
as CSV files.

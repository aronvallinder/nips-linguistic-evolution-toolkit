# Mixed-model eight-agent contagion ladder, 2026-09-18

Does one agent's behaviour spread through a rotating population? Six
compositions under the unchanged September informed negative-only noise
population protocol (balanced rotating pairing, hidden names, co-player history
window 3, no defectors; only the models differ, proved by the launcher's plan
step): 1, 2 or 4 Gemini 3.7 Flash agents among GPT-5 Nano agents, and 1, 2 or 4
GPT-5 Nano agents among Sonnet 4.5 agents. The minority family occupies the
lowest agent ids. Task orders game, game→myth, myth→game; five replicates; 90
runs. Comparators: the 45 September homogeneous populations (8 Sonnet, 8 GPT,
8 Gemini; five replicates per task order). Design authority: project-memory
D010; launcher `scripts/run_mixed_model_populations.py`.

Source finals: `data/json/noise_experiments/mixed_model_populations_20260918/`
(90 validated finals, `completion_receipt.json`; standard-rate cost $104.51:
Anthropic $81.35, OpenAI $14.38, Google $8.77). Regenerate with
`python scripts/analyze_mixed_model_populations.py`.

## Result: resources per agent after ten rounds (max 75), mean (±sd over 5 runs)

Number of minority agents on the left; 0 and 8 are the September homogeneous
populations.

**Gemini among GPT**

| Gemini agents | game | game→myth | myth→game |
|---|---:|---:|---:|
| 0 (8 GPT) | 25.0 (±0.0) | 38.0 (±7.1) | 45.0 (±8.3) |
| 1 | 26.1 (±0.3) | 52.2 (±9.9) | 58.9 (±6.3) |
| 2 | 34.1 (±8.1) | 58.6 (±3.4) | 69.9 (±3.6) |
| 4 | 53.7 (±4.5) | 68.6 (±1.9) | 72.7 (±1.6) |
| 8 (8 Gemini) | 75.0 (±0.0) | 75.0 (±0.0) | 75.0 (±0.0) |

**GPT among Sonnet**

| GPT agents | game | game→myth | myth→game |
|---|---:|---:|---:|
| 0 (8 Sonnet) | 55.2 (±1.0) | 54.1 (±0.9) | 68.7 (±4.4) |
| 1 | 53.5 (±2.7) | 56.2 (±2.5) | 65.1 (±4.4) |
| 2 | 43.7 (±5.8) | 56.6 (±4.0) | 68.5 (±4.5) |
| 4 | 40.0 (±7.7) | 55.6 (±6.7) | 63.5 (±5.9) |
| 8 (8 GPT) | 25.0 (±0.0) | 38.0 (±7.1) | 45.0 (±8.3) |

Per-family splits (minority versus majority agents) are in `ladder_points.csv`
and `ladder.png`; sends by sender family → receiver family and return
proportions by family are in `cell_summary.csv`.

## Reading

- **A lone cooperator does not unlock a GPT population; it gets exploited.**
  One Gemini among seven GPT in game-only play leaves the population at 26.1
  (GPT alone: 25.0). The Gemini agent ends at 20.6, below the GPT agents
  (26.9): it sends $0.88 on average, GPT returns 0.00, and every GPT still
  sends $0. Two Geminis lift the population to 34.1 and four to 53.7, and GPT
  starts sending to Gemini only at four (mean $2.69, versus $0.68 at two and
  $0 at one). Contagion of cooperation is dose-dependent and needs a large
  minority in this protocol.
- **With a myth channel, one Gemini is enough to move a GPT population.**
  1 Gemini + 7 GPT reaches 52.2 (game→myth) and 58.9 (myth→game) against 38.0
  and 45.0 for 8 GPT, and the Gemini agent then out-earns the GPT agents
  (57.2 vs 51.5; 64.9 vs 58.0). GPT sends more to Gemini ($3.5, $4.0) than to
  another GPT ($2.2, $3.0). Text carries the seed where play alone did not.
- **One GPT among Sonnets cooperates; two or more drag the population down.**
  In game-only play a single GPT among seven Sonnets sends $3.21 and the
  population stays at 53.5 (8 Sonnet: 55.2); the GPT agent itself ends at 52.6.
  With two GPTs the population falls to 43.7 and the GPT agents to 37.3 (GPT
  sends $1.29 to Sonnet, $0.56 to GPT); with four, to 40.0. Sonnet's sends to
  GPT fall from $2.08 (one GPT) to $0.88 and $1.38, and Sonnet-to-Sonnet
  sends fall from $3.02 (homogeneous) to $2.92, $2.57, $2.22. Defection spreads
  through a copying majority once the defectors can meet each other.
- **Myth tasks flatten the GPT-among-Sonnet ladder.** With game→myth every
  mixture sits at 55 to 57 (8 Sonnet: 54.1) and with myth→game at 63 to 69
  (8 Sonnet: 68.7); the GPT minority earns as much as or slightly more than the
  Sonnet majority. The zero-lock never forms once myths circulate.
- **Return behaviour barely moves.** Return proportions stay at 0.37 to 0.48
  for Sonnet and Gemini in every composition; GPT returns 0.00 to 0.17 in
  game-only mixtures and 0.34 to 0.46 with a myth task. As in the dyads, the
  composition effects run through sending, not returning.
- **Encounter structure.** The balanced scheduler ignores family, so
  cross-family games are 25%, 41% and 55% of all games for 1, 2 and 4
  minority agents (`encounters.csv`, `cross_family_game_share`). Minority
  agents therefore meet the majority in every round; majority agents meet the
  minority in one to four of their ten games.

## Boundaries and disclosures

- Descriptive, n=5 runs per cell; no inferential test is reported.
- `provenance.json` validates the 90 mixed runs and the 45 September runs as
  two named pools (request-plan shape differs by design, `pool_reason`); within
  each pool every difference is declared field by field, and everything except
  the request-plan shape is checked across pools. Model families are read from
  each run's validated condition. The `implementation` exemption covers only
  `src/` files changed by the per-agent plumbing; `games/` is byte-identical to
  the September run commits.
- Two game-only runs (1 GPT + 7 Sonnet replicate 3, 2 GPT + 6 Sonnet replicate
  2) failed on the first attempt when a Sonnet sender answered with prose
  instead of a JSON decision, twice under the pinned repeat-once retry policy;
  both were resampled from scratch.
- The batch was interrupted twice: an initial 8-worker launch was stopped
  after about 15 minutes to relaunch with 20 workers (eight partial runs
  discarded, no finals or checkpoints existed), and at 48/90 all three
  providers ran out of prepaid credit simultaneously (42 in-flight runs
  discarded and rerun after top-up). Other batches from a separate session
  shared the same provider accounts during this window. Finals therefore
  record several code commits; the code paths are identical across them.
- Recorded cost ($104.51) exceeded the pre-launch estimate ($103 for all 90,
  scaled from homogeneous per-agent usage) because Sonnet agents read and
  reason about GPT myths; the Sonnet-heavy two-task cells came in above the
  homogeneous per-agent cost.
- Mixed runs in the myth conditions transmit myths across families by
  construction; which family's text moved which agent is not separated here.

The ladder split by the minority and majority family's own sending and returning is in
[`../mixed_model_family_split_20260922/`](../mixed_model_family_split_20260922/README.md).

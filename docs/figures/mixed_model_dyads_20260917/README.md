# Mixed-model dyads, 2026-09-17

Two model families share one fixed two-agent trust game under the September
informed negative-only noise protocol. Only the models changed relative to the
September homogeneous dyad controls; the launcher proved every other input equal
before launch (`scripts/run_mixed_model_dyads.py`, plan step). Design authority:
project-memory D010; run plan: `docs/research/mixed_model_run_plan_2026-09-17.md`.

- Compositions: Sonnet 4.5 + GPT-5 Nano, Sonnet 4.5 + Gemini 3.7 Flash, and
  (added 2026-09-18) Gemini 3.7 Flash + GPT-5 Nano.
- Task orders: game, game→myth, myth→game. Ten rounds, endowment $5, multiplier 3.
- Six replicates per cell: the first-named family sends first in replicates
  0/2/4, the other family in 1/3/5 (Agent_1 sends in odd rounds).
- Request profiles: the September 8 native profiles per model (Claude thinking
  8192, GPT reasoning high, Gemini thinking high).
- Comparators: the 45 September homogeneous dyad controls
  (`negative_only_crossmodel_reasoning_rerun_20260909`, five replicates per cell).

Source finals: `data/json/noise_experiments/mixed_model_dyads_20260917/`
(54 validated finals, `completion_receipt.json`; standard-rate cost $14.70:
Anthropic $10.37, OpenAI $1.50, Google $2.82). Regenerate with
`python scripts/analyze_mixed_model_dyads.py`.

## Result: total resources after ten rounds (max 150), mean (±sd over runs)

| Composition | game | game→myth | myth→game |
|---|---:|---:|---:|
| Sonnet + GPT (n=6) | 64.0 (±14.3) | 116.9 (±26.7) | 120.2 (±18.1) |
| GPT + GPT (n=5) | 50.0 (±0.0) | 107.4 (±20.9) | 119.3 (±23.6) |
| Sonnet + Sonnet (n=5) | 100.8 (±8.0) | 111.2 (±9.3) | 115.6 (±16.4) |
| Sonnet + Gemini (n=6) | 140.2 (±6.2) | 146.0 (±1.3) | 148.4 (±1.4) |
| Gemini + GPT (n=6) | 63.3 (±8.2) | 141.3 (±5.9) | 147.2 (±2.9) |
| Gemini + Gemini (n=5) | 150.0 (±0.0) | 150.0 (±0.0) | 150.0 (±0.0) |

## Result: what each family does, by partner (mean over decisions)

Amount sent (of $5) when the family is the sender:

| Family → partner | game | game→myth | myth→game |
|---|---:|---:|---:|
| Sonnet → Sonnet | 2.54 | 3.06 | 3.28 |
| Sonnet → GPT | 1.07 | 3.44 | 3.43 |
| Sonnet → Gemini | 4.12 | 4.60 | 4.84 |
| GPT → GPT | 0.00 | 2.87 | 3.46 |
| GPT → Sonnet | 0.33 | 3.25 | 3.60 |
| GPT → Gemini | 0.17 | 4.13 | 4.72 |
| Gemini → Gemini | 5.00 | 5.00 | 5.00 |
| Gemini → Sonnet | 4.90 | 5.00 | 5.00 |
| Gemini → GPT | 1.17 | 5.00 | 5.00 |

Return proportion when the family is the receiver (undefined when nothing arrived):

| Family ← sender | game | game→myth | myth→game |
|---|---:|---:|---:|
| Sonnet ← Sonnet | 0.38 | 0.43 | 0.48 |
| Sonnet ← GPT | 0.46 (n=2) | 0.44 | 0.47 |
| Sonnet ← Gemini | 0.44 | 0.50 | 0.50 |
| GPT ← GPT | undefined | 0.31 | 0.33 |
| GPT ← Sonnet | 0.03 (n=13) | 0.40 | 0.38 |
| GPT ← Gemini | 0.09 (n=7) | 0.38 | 0.44 |
| Gemini ← Gemini | 0.45 | 0.46 | 0.47 |
| Gemini ← Sonnet | 0.42 | 0.45 | 0.45 |
| Gemini ← GPT | 0.45 (n=1) | 0.44 | 0.45 |

Full tables: `cell_summary.csv`, `family_behaviour.csv`, `round_means.csv`;
per-decision rows in `decisions.csv`. Figures: `resources_boxplots.png` (the figure-2 boxplot grid: resources per agent, six unique pairings drawn once each, homogeneous controls on the top row and mixed pairings on the bottom row; relaid out 2026-09-22 after the earlier 3×3 version repeated the homogeneous panels), `sends_and_returns.png`,
`resources.png`. Each family's own behaviour inside the mixed dyads, against its homogeneous value, is in
[`../mixed_model_family_split_20260922/`](../mixed_model_family_split_20260922/README.md).

## Reading

- **Sonnet follows its partner.** Sonnet sends about $2.5 to another Sonnet,
  about $4.1 to Gemini, and about $1.1 to GPT in the game-only condition. Its
  return proportion barely moves (0.38 to 0.46). The partner's sending, not
  Sonnet's own policy, sets the level.
- **GPT's zero-lock survives a cooperative partner in game-only play.** GPT
  sent $0 in 28 of 30 game-only decisions and returned almost nothing of what
  Sonnet sent (0.03). Sonnet started at $3 and gave up by round 5 to 8. The
  mixed dyad ended at 64 of 150, barely above the GPT+GPT floor of 50.
- **Myth writing breaks the lock in the mixed dyad too.** With a myth task,
  Sonnet+GPT reaches 117 to 120, in the same range as GPT+GPT (107 to 119) and
  Sonnet+Sonnet (111 to 116). GPT returns somewhat more to Sonnet (0.40, 0.38)
  than to another GPT (0.31, 0.33); n is small.
- **Sonnet+Gemini is near the ceiling in every task order** (140 to 148), so
  the myth effect there is at most a few dollars. Gemini keeps sending $5.
- **Gemini is conditional after all (added 2026-09-18).** Against GPT in
  game-only play Gemini sends $5 in rounds 1 and 2, receives nothing back, and
  sends $0 from round 3 on (mean $1.17; GPT sent $0 in 29 of 30 decisions and
  returned 0.09). The pair ends at 63, the same floor as Sonnet+GPT. Gemini's
  unconditional $5 in the homogeneous runs was therefore sustained by
  reciprocation, not fixed. With a myth task Gemini+GPT reaches 141 to 147, and
  GPT sends $4.1 to $4.7 to Gemini against $3.3 to $3.6 to Sonnet and $2.9 to
  $3.5 to another GPT, so GPT is also partner-sensitive once unlocked.
- **First-sender family** did not change these conclusions at n=3 per block;
  per-run values are in `decisions.csv` (`first_sender_family`).

## Boundaries and disclosures

- Descriptive, n=6 per mixed cell (three compositions) and n=5 per homogeneous cell. No inferential
  test is reported.
- `provenance.json` validates the 54 mixed runs and the 45 September runs as
  two named pools: a mixed run records one request plan per agent instead of a
  run-level policy block, so the pools differ in plan shape (`pool_reason`).
  Within each pool every difference is declared field by field; across pools
  everything except the request-plan shape (prompts, protocol, replicate
  identity, implementation) is checked the same way. Every agent plan equals
  the September profile for its model (asserted by the launcher before launch
  and audited per call after). The `implementation` exemption covers only
  `src/` files changed by the per-agent plumbing; `games/` is byte-identical
  between the September commit (893a9713) and the mixed-run commits.
- Model families in the tables are read from each run's validated condition
  (the per-agent plans), never from loose metadata; the validator also
  requires `run_metadata.agent_models` and the saved agent set to match the
  condition.
- One run (`mixed_dyad_game_gpt_sonnet_n3`, replicate 1) failed on the first
  attempt: Sonnet answered a sender prompt with prose analysis instead of a
  JSON decision, twice under the pinned repeat-once retry policy. It was
  resampled from scratch. Four in-flight game-only runs were lost when the
  first batch process was stopped and were resampled from scratch. The last
  five finals therefore record commit `be299fee` instead of `620ce8b3`; the
  code is identical (documentation-only commits in between).
- Mixed runs read the partner's myths, so token use and myth content differ
  from the homogeneous runs by construction. Cost was within the estimate.

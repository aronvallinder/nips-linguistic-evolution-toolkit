# Frozen protocol: GPT-5.5 negative-only completion/behavior gate

## Decision

Before authorizing a full 90-run GPT-5.5 matrix, run one replicate of each
control cell from the frozen 25 August negative-only protocol. The six cells
cross two population regimes (2-agent fixed dyad and 8-agent balanced rotating
population) with three task orders (Game, Game-to-Myth, Myth-to-Game).

## Locked settings

- Model: `openai/gpt-5.5-2026-04-23`.
- OpenAI reasoning effort: `low`, recorded in configuration and run metadata.
- Replicate: `replicate_id = 0` in every cell.
- Noise/pairing seeds: `202608250`, inherited from the frozen protocol.
- Noise: informed uniform negative-only `U(-1, 0)`, applied to communicated
  send and return amounts after the model decision.
- Ten rounds, $5 sender endowment, 3x multiplier, no defection and no
  punishment.
- Prompts, memory capacities, history policy, pairing mode, and myth-to-game
  instruction are identical to the matching August control cell.

## Gate

Proceed to a second replicate only if all six cells produce final full-state
JSON files, no systematic provider/format failure appears, and the model's
cooperation has interpretable headroom rather than an exact floor or ceiling.
Checkpoints, results-only files, logs, and transcripts are not completions.


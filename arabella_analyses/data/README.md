# Coauthor Game/Myth Run Package

Created: 2026-06-08

This package contains curated Sonnet 4.5 trust-game / myth-writing runs for downstream linguistic analysis. The primary source of truth is the JSON file for each run. PDFs are included for human audit/read-through, but the CSV/JSONL tables are the most convenient starting point for analysis.

## What Is Included

- `manifest.csv`: one row per run, with original paths, packaged paths, condition labels, model, temperature, number of agents, number of turns, prompt arm, history settings, noise condition if present, and summary behavior metrics.
- `runs_json/`: primary run JSON files. These include metadata, task order, agent state, game behavior, myths, model responses, and prompt/message payloads where recorded.
- `transcripts_pdf/`: full transcript PDFs for each run.
- `tables/myths.csv` and `tables/myths.jsonl`: one row per myth, with condition/run/round/agent/text.
- `tables/game_rounds.csv` and `tables/game_rounds.jsonl`: one row per dyad per round, including sender/receiver, sent amount, returned amount, return ratio, balances, pairings, and roles.
- `tables/model_responses.csv` and `tables/model_responses.jsonl`: saved model outputs by phase (`myth` or `game`) when present in the run JSON.
- `tables/prompt_messages.csv` and `tables/prompt_messages.jsonl`: prompt/message rows extracted from `conversation_history[].actions` when present.
- `tables/condition_summary.csv`: compact run counts and final-balance summaries by condition.

## Included Run Families

### `2agent_clean_sonnet45`

Two-agent clean Sonnet 4.5 runs, 10 rounds, 5 replicates per condition.

Source root: `data/json/sonnet45_directive_normative_r10_n5`

### `2agent_noisy_sonnet45_negative2_informed`

Two-agent Sonnet 4.5 runs with informed negative-2 noise condition, 10 rounds, 5 replicates per condition.

Source root: `data/json/noise_experiments/sonnet45_directive_normative_r10_n5`

### `8agent_old_prompt_sonnet45`

Eight-agent Sonnet 4.5 runs before self/co-player history prompt change; includes game-only and myth-game directive runs.

Source root: `data/json/sonnet45_8agent_game_directive_r10_n5`

### `8agent_named_history3_sonnet45`

Eight-agent Sonnet 4.5 myth-game directive runs with named agents and own/co-player last 3 games in prompt.

Source root: `data/json/sonnet45_8agent_myth_directive_history3_r10_n5`

### `8agent_anonymous_history3_sonnet45`

Eight-agent Sonnet 4.5 myth-game directive runs with model-facing names suppressed and own/co-player last 3 games in prompt.

Source root: `data/json/sonnet45_8agent_myth_directive_history3_anon_r10_n5`

## Counts

- Primary run JSON files: 50
- Transcript PDFs copied: 50
- Myth rows: 1600
- Game dyad/round rows: 1100
- Model response rows: 3800
- Prompt message rows: 0

## Practical Notes For Analysis

Use `tables/myths.csv` for most linguistic work. Join it to `manifest.csv` on `run_id` if you need hyperparameters or condition metadata.

Use `tables/game_rounds.csv` to align myth language with game behavior. The 8-agent runs have multiple dyads per round, so each round can have several game rows. The 2-agent runs have one game row per round.

For the anonymized 8-agent condition, `show_agent_names` is false in the run metadata and model-facing prompts suppress display names. The raw JSON still keeps internal agent IDs and the `agent_names` mapping for traceability.

The transcript PDFs are intentionally verbose and include full prompt/message context where recorded. They are best for checking what a model saw or said in a specific run; they are not the recommended format for automated text analysis.

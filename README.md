# Linguistic Evolution Toolkit

A configuration-driven framework for behavioral experiments with LLM agents. Pairs of agents play a repeated trust game and co-write myths over many rounds; the analyses measure how their language and cooperation evolve and converge. Built for the experiments behind our NeurIPS 2026 submission on linguistic evolution in LLM dyads.

## Setup

Requires Python 3.11.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt          # framework
pip install -r analyses/requirements.txt # analysis scripts (spaCy, sentence-transformers, ...)

cp .env.example .env                     # then fill in OPENROUTER_API_KEY
```

API keys load from `.env` at the repo root (`src/utils.py` calls `load_dotenv()` at import time). `OPENROUTER_API_KEY` covers most experiments; direct-provider keys (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `TOGETHER_API_KEY`, `GEMINI_API_KEY`) are optional.

## Running experiments

Experiment sets are defined in `config/experiments.yaml` and expand to full factorial designs over models, personas, task orders, and myth topics.

Existing sets predate explicit `llm_settings`. Continuing them requires
`--allow-legacy-settings`, which retains their historical, environment-dependent
requests. For new work, create a new named set with reviewed `llm_settings` and a
separate output location; do not pin an existing set in place over legacy finals
or checkpoints. See the [migration and provenance guide](docs/safeguards-usage.md#3-resume-compare-and-share-deliberately).

```bash
# Inspect an existing set without API calls
python experiments/run_trust_game_batch.py <experiment_set_name> --allow-legacy-settings --dry-run

# Continue an existing set with parallel workers
python experiments/run_trust_game_batch.py <experiment_set_name> --allow-legacy-settings --workers 4

# Inspect a new set after adding reviewed llm_settings
python experiments/run_trust_game_batch.py <new_pinned_set> --dry-run
```

Outputs land in `data/json/<experiment>/<model>/<task_order>/` as full-state `.json`, a `.log` with every prompt and response, and a lightweight `.results.json`. Interrupted runs resume from `.checkpoint.json` files.

## Running analyses

```bash
./scripts/run_all_analyses.sh -all data/json/<experiment>/<file>.json data/plots/<output_dir>

# Or specific analyses (comma-separated):
./scripts/run_all_analyses.sh -a trajectory,cooperativity <input.json> <output_dir>
```

Available analyses: `cooperativity`, `trajectory`, `similarity`, `plot_similarity`, `embedding`, `wordchain`, `ngram`. Further standalone scripts in `analyses/` (phase-specific plots, convergence metrics, judge-based coding) document their usage in their module docstrings.

## Layout

```
config/       experiments.yaml — models, prompts, personas, experiment sets
src/          simulation engine, agents, config parser, API client
games/        trust game implementations (base_game.py defines the interface)
experiments/  batch runners
analyses/     analysis and plotting scripts
scripts/      run_all_analyses.sh + phase-specific run/plot scripts
docs/         architecture docs, design notes
projects/     NeurIPS manuscript, references, paper analysis
tests/        pytest tests
```

`CLAUDE.md` documents the architecture in more depth (prompt template system, checkpointing, personas, adding new games/analyses).

## Data

Raw experiment outputs (`data/json/`, `data/plots/`) are kept out of git — they are multi-GB and reproducible from the configs and runners. The full dataset for the paper will be archived separately (Zenodo link TBD).

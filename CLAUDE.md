# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A configuration-driven framework for running behavioral experiments with multiple LLM models, studying agent interactions through economic games (trust game) and creative tasks (collaborative myth writing). The framework uses YAML-based configuration to enable systematic, reproducible experiments comparing different models, personas, and task sequences.

## Development Commands

### Running Experiments

```bash
# Run specific experiment set (sequential, default)
python experiments/run_trust_game_batch.py <experiment_name>

# Run with parallel workers (faster for large batches)
python experiments/run_trust_game_batch.py <experiment_name> --workers 4

# Test API rate limits to find optimal worker count
python experiments/test_rate_limits.py --max-workers 8

# Run default experiments (pilot + persona_comparison)
python experiments/run_trust_game_batch.py

# Run single experiment (testing)
python experiments/run_trust_game.py
```

### Running Analyses

```bash
# Run all analyses on a simulation output
./scripts/run_all_analyses.sh -all data/json/<experiment>/<file>.json data/plots/<output_dir>

# Run specific analyses (comma-separated)
./scripts/run_all_analyses.sh -a trajectory,cooperativity data/json/<experiment>/<file>.json data/plots/<output_dir>

# Available analyses: cooperativity, trajectory, similarity, plot_similarity, embedding, wordchain, ngram
```

### Python Environment

```bash
# Virtual environment is in .venv (Python 3.11)
source .venv/bin/activate

# Analysis dependencies
pip install -r analyses_clean/requirements.txt
```

## Parallelization

The batch runner (`run_trust_game_batch.py`) supports parallel execution to speed up large experiment batches.

### Parallel Execution

```bash
# Run with 4 parallel workers
python experiments/run_trust_game_batch.py model_comparison --workers 4

# Sequential (backward compatible, default)
python experiments/run_trust_game_batch.py model_comparison --workers 1
```

**How it works**:
- Uses `ProcessPoolExecutor` for true parallelism (no Python GIL limitations)
- Each worker process creates independent API client instance
- Experiments run in isolated processes with no shared state
- Progress shown as experiments complete (not in submission order)
- Individual failures don't crash the entire batch
- Final summary shows success/failure counts and details

**Benefits**:
- 4-8x faster for large batches (depending on worker count and API rate limits)
- Efficient use of API quota (multiple simultaneous requests)
- Better user experience (see progress as experiments finish)

**Considerations**:
- Each worker uses ~500MB-1GB memory (loads full dependencies)
- API costs unchanged (same number of API calls, just faster)
- Must respect API rate limits (see Rate Limit Testing below)
- Disk I/O: multiple simultaneous checkpoint writes

### Rate Limit Testing

Before running large parallel batches, test your API rate limits:

```bash
# Test up to 8 workers
python experiments/test_rate_limits.py --max-workers 8

# Quick test with fewer turns
python experiments/test_rate_limits.py --max-workers 4 --test-turns 2

# Test specific model
python experiments/test_rate_limits.py --model "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"
```

**What it does**:
- Runs minimal experiments (2-3 turns) with increasing worker counts
- Monitors rate limit errors from OpenRouter API
- Provides recommended max worker count
- Tests: 1, 2, 4, 8, 16, 32 workers (up to `--max-workers`)

**Example output**:
```
Workers    Success    RL Errors    Total Time    Avg Time
--------------------------------------------------------------
1          4/4        0            12.3s         3.1s
2          4/4        0            7.1s          1.8s
4          4/4        0            4.2s          1.1s
8          3/4        1            3.8s          0.9s

RECOMMENDATION: Use --workers 4
  (This worker count showed 0 rate limit errors in testing)
```

**Important notes**:
- OpenRouter rate limits vary by model and subscription plan
- Results are specific to your API key and current plan
- Real experiments may behave differently (varying turn counts)
- Existing retry logic in `src/utils.py` helps handle occasional rate limits
- Conservative recommendation: start with 4-8 workers

### Checkpointing with Parallelization

Checkpointing works seamlessly with parallel execution:
- Each experiment maintains independent checkpoint files
- If one experiment crashes, others continue unaffected
- Re-running the batch resumes failed experiments from checkpoints
- Checkpoint files automatically cleaned up on successful completion

## Architecture

### Configuration System (`config/experiments.yaml`)

The entire experimental framework is driven by a single YAML configuration file that defines:

- **Base models**: LLM model identifiers (Llama, GPT-4, Claude, DeepSeek)
- **Prompt templates**: All prompts are configured here (NO hardcoded prompts in code)
  - `trust_game_default`: System prompt explaining game rules
  - `trust_game_round1_investor`: First round investor prompt
  - `trust_game_round1_trustee`: First round trustee prompt
  - `trust_game_later_investor`: Later round investor prompt
  - `trust_game_later_trustee`: Later round trustee prompt
  - `myth_writing_default`: First round myth writing prompt
  - `myth_writing_later_rounds`: Later round myth writing prompt with history
- **Personas**: Behavioral modifiers that alter agent behavior (altruistic, selfish, cautious, risk_taking, neutral)
- **Myth topics**: Predefined topics for myth writing tasks
- **Game parameters**: Default settings (endowment, multiplier, num_turns, temperature, memory_capacity)
- **Experiment sets**: Named experimental conditions that expand to full factorial designs

**Key insight**: `ExperimentConfig.get_experiment_combinations()` generates all parameter combinations from an experiment set definition. Use `"all"` to expand to all available options (e.g., `models: "all"` expands to all defined base models).

**Important**: All prompts must be defined in the config file. If a required prompt is missing, the code will raise an error with the exact prompt name needed.

### Core Flow (src/)

1. **experiment_config.py**: Parses YAML, generates parameter combinations, resolves "all" expansions
2. **simulation.py**: Main orchestration - runs game/myth tasks in specified order, manages checkpointing/resuming, coordinates agents
3. **agents.py**: Simple Agent class with memory capacity (recency bias via message truncation)
4. **myth_writer.py**: Handles myth prompting (first round vs. later rounds with agent's previous myth + other agent's myth)
5. **utils.py**: LLM API calls with retry logic, contains API keys

### Game System (games/)

- **base_game.py**: Abstract Game interface defining required methods
- **trust_game.py**: Sequential trust game with role swapping (investor/trustee), personas modify system prompts
- Games control their own prompt generation, response parsing, state updates, and summary printing

### Execution (experiments/)

- **run_trust_game.py**: Single experiment runner (manual configuration)
- **run_trust_game_batch.py**: Batch runner that loads experiment set from config, generates all combinations, runs each, saves with descriptive filenames
  - Supports parallel execution with `--workers N` flag (default: 1 for sequential)
  - Uses `ProcessPoolExecutor` for process-based parallelism (no GIL limitations)
  - Output pattern: `{experiment_name}_{index:03d}_{model}_{persona}_{task_order}_{myth_topic}.json`
  - Creates `.checkpoint.json` every N turns for crash recovery
  - Creates `.results.json` for lightweight state (no agent message history)
  - Individual experiment failures don't crash entire batch (graceful error handling)

### Task Ordering

Specified in `task_orders` (e.g., `[["game"], ["myth"], ["game", "myth"], ["myth", "game"]]`). The simulation runs tasks sequentially:
- `["game"]`: Only trust game
- `["myth"]`: Only myth writing
- `["game", "myth"]`: Trust game followed by myth writing
- `["myth", "game"]`: Myth writing followed by trust game

This enables studying cross-task influence (does cooperation in game affect creativity in myths?).

### Memory Management

Agents have configurable `memory_capacity` (number of conversation turns to remember). When capacity is exceeded, oldest messages are truncated (keeping system prompt). This creates recency bias where recent interactions have more impact.

### Analysis System (analyses_clean/)

Python scripts that load saved simulation states and generate plots/statistics:
- **cooperativity_analysis.py**: Measures cooperation patterns, mimicry between agents
- **trajectory_plotting.py**: Visualizes investment/return decisions over time
- **trajectory_plotting_rolling.py**: Rolling window analysis
- **myth_similarity.py**: LLM-based similarity scoring between myths
- **myth_similarity_embedding.py**: Embedding-based similarity (sentence-transformers)
- **n_gram_sentence_structure.py**: Linguistic pattern analysis
- **word_chain_evolution.py**: Tracks word usage evolution
- **transaction_flow_plots.py**: Game transaction visualizations

All analyses read from `data/json/` and write to `data/plots/`.

## Key Implementation Details

### Prompt Template System

**All prompts are now configuration-driven** - there are NO hardcoded prompts in the codebase. The system uses Python's `.format()` for variable substitution.

**Trust Game Prompts** require these templates in `config/experiments.yaml`:
- `trust_game_default`: System prompt with `{endowment}` and `{multiplier}` variables
- `trust_game_round1_investor`: First round prompt with `{endowment}` variable
- `trust_game_round1_trustee`: First round prompt with `{sent}`, `{percentage}`, `{received}` variables
- `trust_game_later_investor`: Later round prompt with `{turn}`, `{last_round_sent}`, `{last_round_sent_percentage}`, `{last_round_received}`, `{last_round_returned}`, `{last_round_trustee_payoff}`, `{agent_balance}`, `{endowment}` variables
- `trust_game_later_trustee`: Later round prompt with `{turn}`, `{last_round_sent}`, `{last_round_sent_percentage}`, `{last_round_received}`, `{last_round_returned}`, `{last_round_investor_payoff}`, `{agent_balance}`, `{received}` variables

**Myth Writing Prompts** require:
- `myth_writing_default`: First round prompt with `{myth_topic}` variable
- `myth_writing_later_rounds`: Later round prompt with `{last_myth}` and `{other_agent_myth}` variables

If any required template is missing, the code raises a `ValueError` with the exact prompt name and location in the config file.

### Persona System

Personas modify agent behavior by appending text to the system prompt (see `personas` in config). The `TrustGame` constructor accepts a `personas` dict mapping agent IDs to persona configs. The game's `get_system_prompt()` method appends `persona['system_addition']` to the base prompt.

### Checkpointing & Resuming

- `SimulationData.save_results_only()`: Lightweight save without agent message history (every N turns)
- `SimulationData.save_state()`: Full save including all agent messages (final output)
- `SimulationData.load_state()`: Restores complete simulation state
- `run_simulation()` accepts `resume_from` parameter to continue interrupted experiments

### Response Parsing

Trust game expects JSON responses: `{'send': <amount>, 'reason': <reasoning>}` or `{'return': <amount>, 'reason': <reasoning>}`. The game uses regex to extract these from agent responses (see `trust_game.py`). If parsing fails, defaults are used.

### Myth Topic Handling

When `"myth"` is in task order, the framework iterates over all specified myth topics (or all if `myth_topics: "all"`). Non-myth task orders don't multiply across topics (handled in `experiment_config.py` lines 28-29).

### API Keys

Stored directly in `src/utils.py` (Together_API_KEY and API_KEY for OpenRouter). The LLM client is initialized in `simulation.py` using these keys.

## Common Development Patterns

### Adding a New Experiment Set

1. Edit `config/experiments.yaml` under `experiment_sets:`
2. Define models, templates, personas, task_orders, and game_params
3. Run with `python experiments/run_trust_game_batch.py <new_set_name>`

### Adding a New Model

1. Add to `base_models` in `config/experiments.yaml`
2. Ensure the model string is compatible with your LLM API client

### Adding a New Persona

1. Add to `personas` in `config/experiments.yaml` with description and system_addition
2. No code changes needed - automatically picked up

### Adding a New Game

1. Create class inheriting from `games.base_game.Game`
2. Implement: `get_system_prompt()`, `get_round_1_prompt()`, `get_later_round_prompt()`, `process_turn()`, `print_turn_summary()`, `print_game_summary()`
3. Update experiment runner to instantiate your game

### Adding a New Analysis

1. Create script in `analyses_clean/`
2. Load simulation state from JSON using `SimulationData.load_state()`
3. Access game data via `sim_data.game_data` and conversation history via `sim_data.conversation_history`
4. Add to `scripts/run_all_analyses.sh` in the `run_analysis()` function

## Data Structure

### SimulationData State

```python
{
    "conversation_history": [  # Per-turn records
        {
            "round": 1,
            "actions": {...},  # Game-specific
            "myths": {...},    # If myth task
        }
    ],
    "game_data": {  # Game-specific accumulated state
        "payoffs": {...},
        "cooperation_rate": ...,
        # etc.
    },
    "task_order": ["game", "myth"],
    "run_metadata": {
        "model": "...",
        "temperature": 0.8,
        "myth_topic_id": "...",
        "myth_topic": "..."
    },
    "agents": {  # Agent message histories
        "Agent_1": {
            "messages": [...]
        }
    }
}
```

### Output Locations

- Simulation outputs: `data/json/<experiment_name>/<model>/<task_order>/`
  - `.json` files: Complete experiment data with full conversation history
  - `.log` files: Detailed logs with all prompts and responses sent to/from LLMs
  - `.results.json` files: Lightweight results without agent message history
- Analysis outputs: `data/plots/`
- Notebooks: `notebooks/` (exploratory analysis)

## Important Notes

- All experiments are deterministic given the same configuration and random seed (controlled by temperature)
- The framework supports concurrent experiments (no shared state between runs)
- **Parallelization**: Use `--workers N` for faster batch execution, but test rate limits first with `test_rate_limits.py`
- Each parallel worker uses ~500MB-1GB memory and creates independent API client
- **Directory structure**: Outputs organized as `{experiment}/{model}/{task_order}/` for easy navigation
- **Logging**: Every experiment generates a `.log` file with all prompts and responses for full transparency
- Checkpoint files are deleted on successful completion
- If a filename exists, a suffix (`_2`, `_3`, etc.) is automatically appended
- LLM API calls include retry logic with exponential backoff for rate limiting

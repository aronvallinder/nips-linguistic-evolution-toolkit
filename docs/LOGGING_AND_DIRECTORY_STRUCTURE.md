# Logging and Directory Structure

## Overview

The batch experiment runner now:
1. **Organizes outputs** by `{experiment_name}/{model}/{task_order}/`
2. **Creates detailed log files** with full prompts and responses for every LLM interaction

## New Directory Structure

### Before
```
data/json/
└── experiment_name/
    ├── experiment_name_000_model_persona_task_myth.json
    ├── experiment_name_001_model_persona_task_myth.json
    └── ...
```

### After
```
data/json/
└── experiment_name/
    ├── model1/
    │   ├── task_order1/
    │   │   ├── experiment_name_000_persona_myth.json
    │   │   ├── experiment_name_000_persona_myth.log          ← NEW!
    │   │   └── experiment_name_000_persona_myth.results.json
    │   └── task_order2/
    │       └── ...
    └── model2/
        └── ...
```

### Example with Real Data
```
data/json/
└── 10runs_model_comparison/
    ├── claude-sonnet-4.5/
    │   ├── game/
    │   │   ├── 10runs_model_comparison_000_neutral.json
    │   │   ├── 10runs_model_comparison_000_neutral.log
    │   │   └── 10runs_model_comparison_000_neutral.results.json
    │   ├── myth/
    │   │   └── ...
    │   ├── game_myth/
    │   │   └── ...
    │   └── myth_game/
    │       └── ...
    ├── gpt-5-nano/
    │   ├── game/
    │   │   └── ...
    │   └── ...
    └── gemini-3-flash/
        └── ...
```

## Log File Format

Each `.log` file contains:

### 1. Experiment Header
```
================================================================================
EXPERIMENT LOG
================================================================================
Experiment: 10runs_model_comparison
Index: 000
Model: anthropic/claude-sonnet-4.5
Persona: neutral
Task Order: ['game', 'myth']
Myth Topic ID: anything
Myth Topic: anything
================================================================================
```

### 2. Interaction Entries

For **each** LLM interaction (every prompt/response pair):

```
================================================================================
TIMESTAMP: 2026-02-09 17:07:09
AGENT: Agent_1
MODEL: anthropic/claude-sonnet-4.5
================================================================================

PROMPT:
--------------------------------------------------------------------------------
Round 1: You are the INVESTOR. You have $5. How much do you send? (0-5)

--------------------------------------------------------------------------------

RESPONSE:
--------------------------------------------------------------------------------
Looking at this first round, I need to balance potential gains against risk...
I'll send **$3**:
- This gets tripled to $9 for the trustee
- If they return a fair share (like $4-5), we both gain
- I risk $3 but keep $2 as a safety net
- This tests their trustworthiness for future rounds

{'send': 3}
--------------------------------------------------------------------------------

REASONING:
--------------------------------------------------------------------------------
This is the first round of a trust game where I'm playing as the investor...
[Full reasoning tokens if model provides them - e.g., GPT-5, Claude with reasoning]
--------------------------------------------------------------------------------

USAGE:
--------------------------------------------------------------------------------
Input tokens: 334
Output tokens: 546
Reasoning tokens: 384
--------------------------------------------------------------------------------
```

## What Gets Logged

The log file captures **every** LLM API call, including:

### Trust Game Interactions
- **Round 1 investor prompts** and responses
- **Round 1 trustee prompts** and responses
- **Later round prompts** with game history
- **All decision reasoning** (if model provides it)

### Myth Writing Interactions
- **First round myth prompts** and responses
- **Later round prompts** with previous myths
- **Full myth text** from both agents

### Token Usage
- Input tokens (prompt)
- Output tokens (response)
- Reasoning tokens (if available, e.g., GPT-5 extended reasoning)

## Benefits

### 1. Easier Organization
```bash
# All GPT-5-nano game-only experiments in one place
ls data/json/10runs_model_comparison/gpt-5-nano/game/

# All game-myth experiments across all models
ls data/json/10runs_model_comparison/*/game_myth/
```

### 2. Complete Transparency
- See **exactly** what prompts were sent to each model
- See **exactly** how models responded (including reasoning)
- Debug prompt issues easily
- Analyze model behavior in detail
- Verify experiment correctness

### 3. Research & Analysis
- Compare how different models respond to identical prompts
- Analyze reasoning patterns (for models that provide reasoning)
- Track token usage across experiments
- Study prompt engineering effectiveness

### 4. Reproducibility
- Full record of every interaction
- Can verify exact prompts used
- Can spot any prompt formatting issues
- Complete audit trail

## Example Usage

### Running an Experiment with New Structure

```bash
# Same command as before - logging happens automatically
python experiments/run_trust_game_batch.py 10runs_model_comparison --workers 4
```

### Exploring Results

```bash
# Find all log files for a specific model
find data/json/10runs_model_comparison/claude-sonnet-4.5/ -name "*.log"

# View a specific log file
less data/json/10runs_model_comparison/claude-sonnet-4.5/game_myth/10runs_model_comparison_000_neutral_anything.log

# Search for specific prompts
grep -A 20 "Round 1: You are the INVESTOR" data/json/10runs_model_comparison/*/game/*.log

# Count total LLM interactions in an experiment
grep "TIMESTAMP:" data/json/10runs_model_comparison/gpt-5-nano/game/10runs_model_comparison_000_neutral.log | wc -l
```

### Analyzing Token Usage

```bash
# Extract token usage from log file
grep -A 3 "USAGE:" data/json/10runs_model_comparison/gpt-5-nano/game/10runs_model_comparison_000_neutral.log
```

## File Types

Each experiment generates 3 files:

1. **`.json`** - Complete experiment data (conversation history, game data, agent messages)
   - Size: ~50-100KB
   - Use for: Loading full simulation state, analysis scripts

2. **`.log`** - Full LLM interaction log (all prompts and responses)
   - Size: ~20-50KB
   - Use for: Debugging, prompt analysis, model comparison

3. **`.results.json`** - Lightweight results without agent message history
   - Size: ~20-40KB
   - Use for: Quick results review, progress tracking during long runs

## Implementation Details

### Code Changes

1. **`src/agents.py`**
   - Added `log_file` parameter to `Agent` class
   - Added `_log_interaction()` method to write prompts/responses
   - Every `respond()` call automatically logs

2. **`src/simulation.py`**
   - Added `log_file` parameter to `run_simulation()`
   - Passes log file to agents during creation
   - Handles logging for resumed experiments

3. **`experiments/run_trust_game_batch.py`**
   - Changed directory structure to `{experiment}/{model}/{task_order}/`
   - Creates log file with experiment header
   - Passes log file path to simulation

### Backward Compatibility

- Existing analysis scripts work unchanged (JSON format unchanged)
- Old experiments in flat directory structure still readable
- New experiments automatically use new structure
- No breaking changes to API

## Notes

- Log files are **append-only** - safe for resumed experiments
- Each agent interaction is logged immediately (not buffered)
- Logs include timestamps for debugging timing issues
- Reasoning tokens logged when available (GPT-5, Claude with reasoning)
- UTF-8 encoding supports special characters in myths

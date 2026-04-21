#!/bin/bash
# scripts/run_experiment_batch.sh

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT" || exit 1

# Run specific experiment sets
echo "Running pilot experiments..."
python experiments/run_trust_game_batch.py pilot

echo "Running persona comparison..."
python experiments/run_trust_game_batch.py persona_comparison

# Run analyses for each experiment set
echo "Running analyses on pilot data..."
python analyses_clean/cooperativity_analysis.py --data-dir data/json/pilot/

echo "Running analyses on persona comparison data..."
python analyses_clean/cooperativity_analysis.py --data-dir data/json/persona_comparison/
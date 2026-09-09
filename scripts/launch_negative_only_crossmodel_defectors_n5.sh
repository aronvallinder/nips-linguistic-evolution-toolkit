#!/usr/bin/env bash
set -uo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

if [[ -n "$(git status --porcelain)" ]]; then
  echo "Refusing to launch from a dirty worktree." >&2
  exit 1
fi

LOCK_DIR="/tmp/nlet-negative-only-crossmodel-defectors-n5.lock"
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "Another negative-only batch launcher appears to be active: $LOCK_DIR" >&2
  exit 1
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

export PYENV_VERSION="${PYENV_VERSION:-3.10.14}"
export PYTHONPYCACHEPREFIX="${PYTHONPYCACHEPREFIX:-/tmp/nlet-pycache}"
export MPLCONFIGDIR="${MPLCONFIGDIR:-/tmp/nlet-matplotlib}"
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-/tmp/nlet-cache}"
export PYTHONPATH=.
export LLM_PROVIDER=direct
export ANTHROPIC_MAX_TOKENS="${ANTHROPIC_MAX_TOKENS:-4096}"
export GEMINI_THINKING_LEVEL="${GEMINI_THINKING_LEVEL:-medium}"
export GEMINI_REQUEST_TIMEOUT_SECONDS="${GEMINI_REQUEST_TIMEOUT_SECONDS:-300}"
export TRUST_BATCH_QUIET=1
unset OPENAI_REASONING_EFFORT || true

OUTPUT_SUBDIR="negative_only_crossmodel_defectors_n5_20260825"
LOG_ROOT="${LOG_ROOT:-/tmp/nlet-negative-only-crossmodel-defectors-n5}"
WORKERS="${WORKERS:-3}"
ANALYSIS_OUTPUT="${ANALYSIS_OUTPUT:-docs/figures/$OUTPUT_SUBDIR}"

EXPERIMENTS=(
  negative_only_crossmodel_dyad_game_n5
  negative_only_crossmodel_dyad_game_myth_n5
  negative_only_crossmodel_dyad_myth_game_n5
  negative_only_crossmodel_population_game_n5
  negative_only_crossmodel_population_game_myth_n5
  negative_only_crossmodel_population_myth_game_n5
)

run_python() {
  if [[ -x /opt/homebrew/bin/pyenv ]]; then
    /opt/homebrew/bin/pyenv exec python "$@"
  else
    python3 "$@"
  fi
}

failures=()
echo "Starting negative-only cross-model batch"
echo "Runs: 270 (54 cells x 5 paired replicates)"
echo "Workers: $WORKERS"
echo "Output: data/json/noise_experiments/$OUTPUT_SUBDIR"
echo "Logs: $LOG_ROOT"
echo "Analysis: $ANALYSIS_OUTPUT"

for experiment in "${EXPERIMENTS[@]}"; do
  echo
  run_python scripts/noisy_run_status.py \
    "$experiment" \
    --output-subdir "$OUTPUT_SUBDIR"
  if ! run_python scripts/run_noisy_missing.py \
    "$experiment" \
    --allow-legacy-settings \
    --workers "$WORKERS" \
    --output-subdir "$OUTPUT_SUBDIR" \
    --log-dir "$LOG_ROOT"
  then
    failures+=("$experiment")
  fi
done

if (( ${#failures[@]} > 0 )); then
  echo "The following experiment sets need a resumable retry:" >&2
  printf '  %s\n' "${failures[@]}" >&2
  exit 1
fi

run_python scripts/analyze_negative_only_crossmodel_batch.py \
  --input "data/json/noise_experiments/$OUTPUT_SUBDIR" \
  --output "$ANALYSIS_OUTPUT"

echo "Negative-only batch and return-proportion plots complete."

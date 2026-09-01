#!/usr/bin/env bash
set -uo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

if [[ -n "$(git status --porcelain)" ]]; then
  echo "Refusing to launch from a dirty worktree." >&2
  exit 1
fi

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  echo "OPENAI_API_KEY is not set." >&2
  exit 1
fi

export PYENV_VERSION="${PYENV_VERSION:-3.10.14}"
export PYTHONPYCACHEPREFIX="${PYTHONPYCACHEPREFIX:-/tmp/nlet-pycache}"
export MPLCONFIGDIR="${MPLCONFIGDIR:-/tmp/nlet-matplotlib}"
export XDG_CACHE_HOME="${XDG_CACHE_HOME:-/tmp/nlet-cache}"
export PYTHONPATH=.
export LLM_PROVIDER=direct
export OPENAI_REASONING_EFFORT=low
export TRUST_BATCH_QUIET=1

OUTPUT_SUBDIR="gpt55_negative_only_gate_r1_20260901"
LOG_ROOT="${LOG_ROOT:-/tmp/nlet-gpt55-negative-only-gate-r1-20260901}"
PARALLEL_RUNS="${PARALLEL_RUNS:-3}"

EXPERIMENTS=(
  gpt55_gate_dyad_game_r1
  gpt55_gate_dyad_game_myth_r1
  gpt55_gate_dyad_myth_game_r1
  gpt55_gate_population_game_r1
  gpt55_gate_population_game_myth_r1
  gpt55_gate_population_myth_game_r1
)

run_python() {
  if [[ -x /opt/homebrew/bin/pyenv ]]; then
    /opt/homebrew/bin/pyenv exec python "$@"
  else
    python3 "$@"
  fi
}

run_one() {
  local experiment="$1"
  run_python scripts/run_noisy_missing.py \
    "$experiment" \
    --workers 1 \
    --output-subdir "$OUTPUT_SUBDIR" \
    --log-dir "$LOG_ROOT"
}

failures=()
echo "Starting GPT-5.5 negative-only gate"
echo "Runs: 6 control cells (replicate 0)"
echo "Model: openai/gpt-5.5-2026-04-23"
echo "OpenAI reasoning effort: low"
echo "Parallel runs: $PARALLEL_RUNS"
echo "Output: data/json/noise_experiments/$OUTPUT_SUBDIR"
echo "Logs: $LOG_ROOT"

for ((offset = 0; offset < ${#EXPERIMENTS[@]}; offset += PARALLEL_RUNS)); do
  pids=()
  names=()
  for ((slot = 0; slot < PARALLEL_RUNS; slot += 1)); do
    index=$((offset + slot))
    if ((index >= ${#EXPERIMENTS[@]})); then
      break
    fi
    experiment="${EXPERIMENTS[$index]}"
    run_one "$experiment" &
    pids+=("$!")
    names+=("$experiment")
  done

  for ((slot = 0; slot < ${#pids[@]}; slot += 1)); do
    if ! wait "${pids[$slot]}"; then
      failures+=("${names[$slot]}")
    fi
  done
done

if ((${#failures[@]} > 0)); then
  echo "Gate cells requiring inspection or a resumable retry:" >&2
  printf '  %s\n' "${failures[@]}" >&2
  exit 1
fi

echo "All six launch jobs returned successfully. Verify final full-state JSONs before declaring completion."

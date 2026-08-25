#!/usr/bin/env bash
# PostToolUse hook: auto-push completed runs to the shared HF dataset repo
# whenever a batch runner finishes in this session.
#
# Fires after every Bash call, but only acts when the command ran one of the
# batch runners (run_trust_game_batch.py / run_noisy_batch.py). On a match it
# runs sync_data.sh push (content-deduplicated, so only new runs transfer)
# and logs to .data-sync.log. Wired async so it never blocks the session.
#
# Reads the hook payload as JSON on stdin. Always exits 0 (never blocks a tool).
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG="$PROJECT_ROOT/.data-sync.log"

payload="$(cat)"
tool="$(printf '%s' "$payload" | jq -r '.tool_name // empty')"
[[ "$tool" == "Bash" ]] || exit 0

cmd="$(printf '%s' "$payload" | jq -r '.tool_input.command // empty')"
[[ "$cmd" == *run_trust_game_batch* || "$cmd" == *run_noisy_batch* ]] || exit 0

{
  echo "===== $(date '+%Y-%m-%d %H:%M:%S')  trigger=batch-runner ====="
  "$SCRIPT_DIR/sync_data.sh" push
} >>"$LOG" 2>&1

exit 0

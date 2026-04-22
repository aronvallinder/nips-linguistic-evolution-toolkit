#!/usr/bin/env bash
# Manuscript pipeline guard — called as a PreToolUse hook.
# Receives tool input as JSON on stdin. Checks the file_path field
# against the agent's allowed write patterns.
#
# Usage: ms-guard.sh <role>
#   role — one of: writer, ms-agent, no-ms
#     writer   : may only write *.c_final.md in manuscript/
#     ms-agent : may only write *.a_outline.md in manuscript/
#     no-ms    : may not write anything in manuscript/
#
# Exit codes:
#   0 — allow
#   2 — block (with reason on stdout)

set -euo pipefail

ROLE="${1:-no-ms}"

# Read JSON from stdin
INPUT=$(cat)

# Extract file_path from the tool input
FILE_PATH=$(echo "$INPUT" | python3 -c "
import sys, json
d = json.load(sys.stdin).get('tool_input', {})
print(d.get('file_path', d.get('command', '')))
" 2>/dev/null || echo "")

# If no file path, allow (not a file operation)
[[ -z "$FILE_PATH" ]] && exit 0

# Check if file is in a manuscript directory
if [[ "$FILE_PATH" != *"/manuscript/"* ]]; then
    exit 0
fi

case "$ROLE" in
    writer)
        # Writer: only *.c_final.md
        if [[ "$FILE_PATH" == *.c_final.md ]]; then
            exit 0
        fi
        echo "BLOCKED: ms-writer may only write to *.c_final.md files in manuscript/. Got: $FILE_PATH" >&2
        exit 2
        ;;
    ms-agent)
        # MS agents: only *.a_outline.md
        if [[ "$FILE_PATH" == *.a_outline.md ]]; then
            exit 0
        fi
        echo "BLOCKED: this agent may only write to *.a_outline.md files in manuscript/. Got: $FILE_PATH" >&2
        exit 2
        ;;
    no-ms)
        # Non-MS agents: no manuscript writes at all
        echo "BLOCKED: this agent may not write to manuscript files. Got: $FILE_PATH" >&2
        exit 2
        ;;
esac

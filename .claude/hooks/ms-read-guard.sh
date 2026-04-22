#!/usr/bin/env bash
# Manuscript read guard for ms-writer — only allows reading *.b_draft.md
# in manuscript directories. Blocks all other repo files.
#
# Exit codes:
#   0 — allow
#   2 — block (with reason on stdout)

set -euo pipefail

INPUT=$(cat)

FILE_PATH=$(echo "$INPUT" | python3 -c "
import sys, json
d = json.load(sys.stdin).get('tool_input', {})
print(d.get('file_path', ''))
" 2>/dev/null || echo "")

[[ -z "$FILE_PATH" ]] && exit 0

# Allow reading draft files in manuscript/
if [[ "$FILE_PATH" == *"/manuscript/"* && "$FILE_PATH" == *.b_draft.md ]]; then
    exit 0
fi

# Allow reading the active_project file (needed to resolve slug)
if [[ "$FILE_PATH" == */projects/active_project ]]; then
    exit 0
fi

# Detect repo root (directory containing this script's grandparent .claude/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Block other files in the repo
if [[ "$FILE_PATH" == "$REPO_ROOT"* ]]; then
    echo "BLOCKED: ms-writer may only read *.b_draft.md files in manuscript/. Got: $FILE_PATH" >&2
    exit 2
fi

exit 0

#!/usr/bin/env bash
# Manuscript write warning — reminds agents that only subagents should write
# to manuscript files. Does not block (exit 0), just warns.
#
# Exit codes:
#   0 — always (warning only, no blocking)

set -euo pipefail

INPUT=$(cat)

FILE_PATH=$(echo "$INPUT" | python3 -c "
import sys, json
d = json.load(sys.stdin).get('tool_input', {})
print(d.get('file_path', d.get('path', '')))
" 2>/dev/null || echo "")

[[ -z "$FILE_PATH" ]] && exit 0

# Only warn for manuscript files
if [[ "$FILE_PATH" == *"/manuscript/"* ]]; then
    cat >&2 << 'EOF'
WARNING: You are about to write to a manuscript file.

Only SUBAGENTS with appropriate roles should write to manuscript files:
  - ms-writer → *.c_final.md
  - ms-brainstorm, ms-claim-researcher, ms-literature-researcher,
    ms-paper-extractor → *.a_outline.md

If you are the MAIN AGENT (chatting directly with the user), do NOT proceed.
Instead, delegate this task to the appropriate subagent.

If you are a SUBAGENT with the correct role, proceed — your role-specific
hook will enforce the access rules.
EOF
fi

exit 0

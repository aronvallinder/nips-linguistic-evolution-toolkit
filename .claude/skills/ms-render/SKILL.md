---
name: ms-render
description: Render the manuscript. Merges bibliography and builds PDF/HTML via Quarto. Use when the user asks to render, build, or preview the manuscript.
argument-hint: [--html|--pdf|--all]
---

# Render Manuscript

Merges bibliography from `projects/<slug>/references/bib/*.json` into the active project's manuscript. Reads `projects/active_project` to determine the project slug.

## Usage

```bash
# Default (PDF)
python3 ${CLAUDE_SKILL_DIR}/render.py

# HTML only
python3 ${CLAUDE_SKILL_DIR}/render.py --html

# Both PDF and HTML
python3 ${CLAUDE_SKILL_DIR}/render.py --all

# Merge bibliography only (no render)
python3 ${CLAUDE_SKILL_DIR}/merge_bib.py
```

If `$ARGUMENTS` is provided, pass it through:

```bash
python3 ${CLAUDE_SKILL_DIR}/render.py $ARGUMENTS
```

## Live preview

For live preview (not via this skill): `quarto preview projects/<slug>/manuscript`

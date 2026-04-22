---
name: ms-pdf-extract
description: Extract markdown and bibliography from academic PDFs, and generate relevance notes or exploration leads. Use when the user asks to "extract pdfs", "convert papers", "run pdf extraction", "generate notes", or "explore papers".
argument-hint: "[path|citekey] [--notes] [--notes-only [KEY ...]] [--explore] [--explore-only [KEY ...]]"
---

Run the extraction script. If `$ARGUMENTS` is provided, pass it as arguments:

```bash
poetry run python3 ${CLAUDE_SKILL_DIR}/pdf2md.py $ARGUMENTS
```

## Usage modes

**Extract PDFs (default):**
```bash
poetry run python3 ${CLAUDE_SKILL_DIR}/pdf2md.py [path]          # Extract one PDF or folder
poetry run python3 ${CLAUDE_SKILL_DIR}/pdf2md.py                 # Extract all pending PDFs
poetry run python3 ${CLAUDE_SKILL_DIR}/pdf2md.py --notes [path]  # Extract + generate relevance notes
poetry run python3 ${CLAUDE_SKILL_DIR}/pdf2md.py --explore [path] # Extract + generate note + leads (snowball)
```

**Generate relevance notes only (no PDF extraction):**
```bash
poetry run python3 ${CLAUDE_SKILL_DIR}/pdf2md.py --notes-only obrien2008 green2000  # Specific keys
poetry run python3 ${CLAUDE_SKILL_DIR}/pdf2md.py --notes-only                       # All missing notes
```

**Generate exploration notes + leads only (no PDF extraction):**
```bash
poetry run python3 ${CLAUDE_SKILL_DIR}/pdf2md.py --explore-only smith2024 jones2023  # Specific keys
poetry run python3 ${CLAUDE_SKILL_DIR}/pdf2md.py --explore-only                      # All missing leads
```

**Dry run:**
```bash
poetry run python3 ${CLAUDE_SKILL_DIR}/pdf2md.py --dry-run
```

## Outputs

For each paper:
- **Markdown extraction**: `references/md/<slug>/<key>.md` (Step 1)
- **Bibliography**: `references/bib/<key>.json` (Step 1)
- **Relevance note**: `references/notes/<key>.md` (with `--notes` or `--notes-only`)
- **Exploration note + leads**: `references/notes/<key>.md` + `references/leads/<key>.md` (with `--explore` or `--explore-only`)

The relevance note is a concise summary of why the paper matters to this manuscript, grounded in where it's cited and what claims it supports.

The exploration mode produces both a note and a leads file listing the most promising references to follow up on — designed for snowball literature searches.

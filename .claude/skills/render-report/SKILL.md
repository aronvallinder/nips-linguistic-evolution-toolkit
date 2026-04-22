---
name: render-report
description: Render a QMD analysis report to HTML and/or GitHub Flavored Markdown. Use when the user asks to render, build, or preview an analysis report.
user_invocable: true
argument-hint: <path/to/report.qmd> [--html|--gfm|--all]
---

# Render Analysis Report

Renders a `.qmd` analysis report to HTML and/or GitHub Flavored Markdown
using Quarto via the project's Poetry environment.

## Usage

```bash
bash ${CLAUDE_SKILL_DIR}/render.sh $ARGUMENTS
```

If no path is given, find the most recently modified `.qmd` in
`projects/neurips-2026-mls/analysis/` and render all formats:

```bash
bash ${CLAUDE_SKILL_DIR}/render.sh --all \
  $(ls -t projects/neurips-2026-mls/analysis/*.qmd 2>/dev/null | head -1)
```

## Formats

| Flag     | Output                          |
|----------|---------------------------------|
| `--html` | Styled HTML (Cosmo theme)       |
| `--gfm`  | GitHub Flavored Markdown + PNG  |
| `--all`  | Both HTML and GFM (default)     |

After rendering, open the HTML output:

```bash
open <path-to-output>.html
```

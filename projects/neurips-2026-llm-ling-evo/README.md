# Manuscript: LLM Linguistic Evolution (NeurIPS 2026)

## Folder structure

```
projects/neurips-2026-llm-ling-evo/
  PROJECT.md                # paper summary, status, headline findings
  CLAUDE.md                 # project-local guidance for Claude Code
  README.md                 # this file

  manuscript/               # the Quarto manuscript
    index.qmd               # main document — frontmatter + section includes
    _quarto.yml             # Quarto project config
    neurips.csl             # citation style
    .gitignore              # excludes _manuscript/, references.json
    _0-introduction.{a_outline,b_draft,c_final}.md
    _1-background.{a_outline,b_draft,c_final}.md
    _2-method.{a_outline,b_draft,c_final}.md
    _3-results.{a_outline,b_draft,c_final}.md
    _4-discussion.{a_outline,b_draft,c_final}.md
    _5-appendix.{a_outline,b_draft,c_final}.md
    figures/                # figures referenced in the text
    _manuscript/            # rendered output (generated, gitignored)
    references.json         # merged bibliography (generated, gitignored)

  materials/                # working materials, not part of the paper
    brainstorming/          # ms-brainstorm reports
    literature-research/    # ms-literature-researcher / ms-claim-researcher reports

  data/                     # data files used in the manuscript
  analysis/                 # plot-generating scripts, processed outputs
```

References live **inside the project**:

```
projects/neurips-2026-llm-ling-evo/references/
  bib/                      # one CSL-JSON file per paper (firstauthoryear.json)
  notes/                    # reading notes
  leads/                    # follow-up references worth exploring
  pdfs/                     # downloaded PDFs (firstauthoryear.pdf)
  md/                       # markdown extractions of PDFs (auto-generated)
```

## Three-stage writing pipeline

Each section has three files:

- **`_section.a_outline.md`** — bullet-level scaffolding. One summary sentence per planned paragraph, then bullets with the key arguments, citations, and data points. Written by `ms-*` subagents (brainstorm, claim-researcher, literature-researcher, paper-extractor).
- **`_section.b_draft.md`** — the human-curated draft. **Humans only** — this is the firewall step where you decide what survives from the outline and how to argue it.
- **`_section.c_final.md`** — polished prose. **ms-writer only** writes this. It's what gets rendered into the paper via `{{< include >}}` directives in `index.qmd`.

Only the `.c_final.md` files are pulled into the rendered output.

## Bibliography

References are stored as one CSL-JSON file per paper in `projects/neurips-2026-llm-ling-evo/references/bib/<firstauthoryear>.json`. Before rendering, they're merged into `references.json` inside `manuscript/`.

**Cite** in any section file as `[@authorYYYY]` or `@authorYYYY`. The merge step picks up new references automatically.

**Add a new reference** manually:
1. Create `projects/neurips-2026-llm-ling-evo/references/bib/authorYYYY.json` with CSL-JSON content
2. Cite in any section file
3. Render — the merge step picks it up

**Add references from PDFs**: drop them in `projects/neurips-2026-llm-ling-evo/references/pdfs/` and run:

```bash
poetry run python3 .claude/skills/ms-pdf-extract/pdf2md.py
```

Paths auto-resolve to the active project (set by `projects/active_project`). Renames PDFs to `firstauthoryear.pdf`, extracts markdown to `references/md/`, creates a CSL-JSON stub in `references/bib/`.

## Render

```bash
# Default (PDF)
python3 .claude/skills/ms-render/render.py

# HTML only
python3 .claude/skills/ms-render/render.py --html

# Both
python3 .claude/skills/ms-render/render.py --all

# Merge bibliography only
python3 .claude/skills/ms-render/merge_bib.py
```

**Live preview** (auto-refreshes on save):

```bash
quarto preview projects/neurips-2026-llm-ling-evo/manuscript
```

Output goes to `manuscript/_manuscript/`.

## Available agents and skills

| Agent | What it does |
|-------|--------------|
| `ms-writer` | Turns `.b_draft.md` into polished `.c_final.md` |
| `ms-brainstorm` | Explores a question / strategic decision; saves to `materials/brainstorming/` |
| `ms-claim-researcher` | Investigates whether a specific claim is defensible; saves to `materials/literature-research/` |
| `ms-literature-researcher` | Broader literature search on a topic |
| `ms-paper-extractor` | Reads a PDF → notes + CSL-JSON bib entry + leads |

| Skill | Usage |
|-------|-------|
| `/ms-render` | Merge bibliography and render the manuscript |
| `/ms-pdf-extract [path]` | Extract markdown + bib entries from PDFs |
| `/render-report <path/to/report.qmd>` | Render a QMD analysis report |

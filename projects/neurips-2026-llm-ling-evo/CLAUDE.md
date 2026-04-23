# LLM Linguistic Evolution — Project-local guidance

This file is project-scoped. It applies to work inside `projects/neurips-2026-llm-ling-evo/` and overrides nothing at the repo root (Ivar's `CLAUDE.md` for the toolkit code stays authoritative for `src/`, `games/`, `noise/`, etc.).

## What this project is

A NeurIPS 2026 paper on whether linguistic exchange between LLM agents shapes their cooperation. Two-agent dyads, repeated trust game ± iterated myth-writing, three frontier models, noise conditions.

**Deadline**: early May 2026.

See `PROJECT.md` for the paper summary, `README.md` for the manuscript workflow.

## Manuscript pipeline

Three-tier pipeline with a human firewall between outline and draft:

| Layer | Files | Who writes | Who reads |
|-------|-------|-----------|-----------|
| **Outline** | `*.a_outline.md` | All ms-agents | All agents + humans |
| **Draft** | `*.b_draft.md` | **Humans only** | ms-writer + humans |
| **Manuscript** | `*.c_final.md` | **ms-writer only** | Quarto renderer + humans |

**Access rules** (enforced via PreToolUse hooks in agent frontmatter — `.claude/hooks/ms-guard.sh`):

| Role (`MS_GUARD_ROLE`) | Agents | Manuscript reads | Manuscript writes |
|------------------------|--------|------------------|-------------------|
| `writer` | ms-writer | `*.b_draft.md` only | `*.c_final.md` only |
| `ms-agent` | ms-brainstorm, ms-claim-researcher, ms-literature-researcher, ms-paper-extractor | all | `*.a_outline.md` only |
| `no-ms` | engineer, data-analyst, reviewer, etc. (not currently installed in this fork) | all | none |

**Main agent restriction**: The main/parent agent (the one the user chats with directly) must **not** write to manuscript files. Always delegate manuscript work to the appropriate subagent (`ms-writer`, `ms-brainstorm`, etc.). A global warning hook (`.claude/hooks/ms-warn.sh`, wired in `.claude/settings.json` as a `PreToolUse` matcher on `Edit|Write|StrReplace`) reminds agents of this rule when they attempt to write into a `manuscript/` path; it warns but does not block, since the main agent may still legitimately edit non-manuscript files in the project (configs, READMEs, this CLAUDE.md, etc.).

**Humans** curate outline into draft (the firewall step) and review the final manuscript.

### When to invoke which agent

- **`ms-writer`** — turn a populated `*.b_draft.md` into polished prose at `*.c_final.md`. Reads draft, writes final. Don't invoke until the draft has prose-shaped bullets ready.
- **`ms-brainstorm`** — exploratory thinking about a paper-level question or strategic decision (framing, scope, structural choices). Saves a report to `materials/brainstorming/`. Use when stuck on *what to argue*, not *how to phrase it*.
- **`ms-claim-researcher`** — investigates whether a specific claim is defensible. Finds supporting/challenging literature, downloads open-access PDFs, writes a report to `materials/literature-research/`. Use when a single load-bearing claim needs grounding.
- **`ms-literature-researcher`** — broader literature search on a topic; finds papers, summarises findings, identifies gaps. Use for §2 background coverage.
- **`ms-paper-extractor`** — reads a PDF in `projects/<slug>/references/pdfs/` → produces a notes file in `references/notes/`, a CSL-JSON entry in `references/bib/`, and follow-up leads in `references/leads/`. Use after dropping new PDFs into the references tree.

## Codebase pointers (for analysis / cross-reference)

- **Noise experiment runner**: `noise/run_noisy_batch.py`
- **Noise config (experiment_sets, noise_config presets)**: `noise/experiments_noisy.yaml`
- **Trust game (noise-aware)**: `noise/trust_game_noisy.py`
- **Simulation engine**: `src/simulation.py`
- **Agent class**: `src/agents.py`
- **Myth writer**: `src/myth_writer.py`
- **Saved simulation states**: `data/json/noise_experiments/v2/{experiment}/{model}/{task_order}/{game_params}/<run>.json`
- **Each run also produces**: `<run>.results.json` (lightweight), `<run>.checkpoint.json` (full state + agent message buffers; deleted on success), `<run>.log` (verbatim prompts/responses)

## Active project pointer

This project is the active one as long as `projects/active_project` reads `neurips-2026-llm-ling-evo`. The `ms-render` skill resolves this to find which manuscript to build.

## Bibliography

References are CSL-JSON files in `projects/<slug>/references/bib/<firstauthoryear>.json` (one per paper, project-scoped). They get merged into `references.json` inside `manuscript/` before each render. Cite in section files as `[@authorYYYY]` or `@authorYYYY`. The `ms-paper-extractor` agent populates `references/bib/` from PDFs in `references/pdfs/`.

## Render

```bash
python3 .claude/skills/ms-render/render.py          # PDF (default)
python3 .claude/skills/ms-render/render.py --html    # HTML
python3 .claude/skills/ms-render/render.py --all     # Both
quarto preview projects/neurips-2026-llm-ling-evo/manuscript   # live preview
```

Requires Quarto + a working LaTeX install for PDF.

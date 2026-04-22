# LLM Linguistic Evolution — Project-local guidance

This file is project-scoped. It applies to work inside `projects/neurips-2026-llm-ling-evo/` and overrides nothing at the repo root (Ivar's `CLAUDE.md` for the toolkit code stays authoritative for `src/`, `games/`, `noise/`, etc.).

## What this project is

A NeurIPS 2026 paper on whether linguistic exchange between LLM agents shapes their cooperation. Two-agent dyads, repeated trust game ± iterated myth-writing, three frontier models, noise conditions.

**Deadline**: early May 2026.

See `PROJECT.md` for the paper summary, `README.md` for the manuscript workflow.

## Manuscript pipeline (three-tier, MCE-style)

Section files in `manuscript/` follow the three-stage pattern:

| Layer | Files | Who writes | Who reads |
|-------|-------|-----------|-----------|
| **Outline** | `*.a_outline.md` | ms-* subagents (brainstorm, claim-researcher, literature-researcher, paper-extractor) | All agents + humans |
| **Draft** | `*.b_draft.md` | **Humans only** (the firewall) | ms-writer + humans |
| **Final** | `*.c_final.md` | **ms-writer only** | Quarto renderer + humans |

Access enforced by `.claude/hooks/ms-guard.sh` via the agent frontmatter. The main agent (the one chatting with the user) **must not** write to manuscript files — delegate to the appropriate subagent.

## Scope discipline (anti-bleed)

This paper is **dyadic, single-generation, no selection**. Do not import framing terminology from adjacent projects:

| Term | Where it belongs | Don't use here because |
|------|------------------|------------------------|
| "Norm formation / erosion" | Schmidt RFP, AI Evolution Theory | The paper has no longitudinal norm dynamics |
| "Populations" | MCE, Brinkmann/Perez framing | The paper is dyadic |
| "Generations / selection" | MCE | Single-generation, no fitness function |
| "Prosocial drift" | MCE (Levin framing) | This paper's analogous concept is **strategy consolidation** |
| "Compression and structure" (Kirby prediction) | Long-horizon iterated learning | T = 10 rounds is not the Kirby paradigm |

When in doubt, ask: "is this defensible within the experimental scope of *this* paper?" See user-level `~/.claude/projects/-Users-aron/memory/feedback_project_scoped_framing.md` for the full guard.

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

References are CSL-JSON files in `references/bib/<firstauthoryear>.json` (one per paper, repo-wide). They get merged into `references.json` inside `manuscript/` before each render. Cite in section files as `[@authorYYYY]` or `@authorYYYY`. The `ms-paper-extractor` agent populates `references/bib/` from PDFs in `references/pdfs/`.

## Render

```bash
python3 .claude/skills/ms-render/render.py          # PDF (default)
python3 .claude/skills/ms-render/render.py --html    # HTML
python3 .claude/skills/ms-render/render.py --all     # Both
quarto preview projects/neurips-2026-llm-ling-evo/manuscript   # live preview
```

Requires Quarto + a working LaTeX install for PDF.

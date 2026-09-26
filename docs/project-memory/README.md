# Project memory

This is the repository's durable entry point for research context. It is read
by both Codex and Claude through the repository instruction files.

## Read first

1. Read [CURRENT.md](CURRENT.md) for the current research state and operational
   constraints.
2. Find the relevant record in [decisions/](decisions/). Read the linked
   primary source before relying on a rationale or changing experimental
   semantics.
3. Use the [experiment-design reference](../experiment_design_reference.md)
   for the full chronology and its primary-source appendix.
4. Use [sources/README.md](sources/README.md) to locate meeting evidence and to
   distinguish original transcripts, user-supplied notes, and assistant
   summaries.

## Canonical layers

| Layer | Purpose | Editing rule |
|---|---|---|
| [CURRENT.md](CURRENT.md) | Short, present-tense state and active constraints | Update only when durable state changes |
| [decisions/](decisions/) | One source-linked record per research or experimental decision | Preserve chronology and supersession |
| [sources/](sources/) | Source register and preserved meeting evidence | Never rewrite quotations to fit a conclusion |
| [Design reference](../experiment_design_reference.md) | Full historical reconstruction from slides/comments/code/runs | Add evidence; preserve uncertainty |
| [researchlog.md](../../researchlog.md) | Auditable lasting decisions and completed results | Follow its separate append-only rules |

The old Claude project-memory files under `~/.claude/projects/.../memory/` are
useful recovery sources, but they are assistant-written summaries and are not
the canonical project record. Project-specific knowledge that should survive
across tools belongs here.

## Decision index

- [D001 — History and memory](decisions/001-history-and-memory.md)
- [D002 — Anonymity and local transmission](decisions/002-anonymity-and-local-transmission.md)
- [D003 — Noise semantics](decisions/003-noise-semantics.md)
- [D004 — Model request profiles](decisions/004-model-request-profiles.md)
- [D005 — Hold the proposed 180 runs](decisions/005-hold-180-runs.md)
- [D006 — Pre-August dyad result invalidation](decisions/006-pre-august-dyad-results-invalid.md)
- [D007 — Prompt regimes](decisions/007-prompt-regimes.md)
- [D008 — Myth-transplant isolation](decisions/008-myth-transplant-isolation.md)
- [D009 — Defector treatments](decisions/009-defector-treatments.md)
- [D010 — Mixed-model population sizes](decisions/010-mixed-model-population-sizes.md)
- [D011 — Frontier-model rerun](decisions/011-frontier-model-rerun.md)
- [Decision template](decisions/TEMPLATE.md)

## Automatic maintenance

Agents must follow [WORKFLOW.md](WORKFLOW.md). In brief: read this directory at
session start; update a decision record whenever an explicit decision,
supersession, material semantic implementation, invalidating bug, or completed
result occurs; update `CURRENT.md` if present state changes; and validate the
memory before finishing. Routine coding and speculative discussion create no
memory entry.

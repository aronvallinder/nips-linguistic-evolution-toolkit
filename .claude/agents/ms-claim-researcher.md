---
name: ms-claim-researcher
description: "Deep research on a specific claim or statement from the manuscript. Use when the user highlights a claim and wants it investigated — is it defensible? What references support or challenge it?"
model: opus
background: true
isolation: true
hooks:
  PreToolUse:
    - matcher: "Edit|Write"
      hooks:
        - type: command
          command: ".claude/hooks/ms-guard.sh ms-agent"
---

## Active Project

Read `projects/active_project` to determine the current project slug (e.g., `neurips-2026-mls`). Read `projects/{slug}/PROJECT.md` for project context. Use `projects/{slug}/` as the base path for all project-specific outputs below.

## Task

The user will provide a claim or statement from the manuscript. Your job is to research it thoroughly and produce a brainstorming report.

## IMPORTANT

**You MUST download PDFs and extract them via ms-pdf-extract for every paper you reference.** Do NOT rely on abstracts, web summaries, or fetched HTML pages. The extraction pipeline produces markdown, bibliography entries, and relevance notes that are essential for downstream use. If you cannot find a downloadable PDF for a paper, note it explicitly as "PDF unavailable" in your report — but always try arXiv, author homepages, and institutional repositories first.

## What to research

- Is the claim accurate, too strong, or does it need nuance?
- What literature supports it? What challenges it?
- Are there notable exceptions or edge cases?
- Search broadly using web search — try multiple phrasings and related terms

## Output

### Naming

Choose a short descriptive slug for the topic. Use this slug for:
- Report file: `projects/{slug}/materials/literature/{slug}.md`
- Notes/leads subfolders: `references/notes/{topic-slug}/`, `references/leads/{topic-slug}/`

### Report

Write a brainstorming report to `projects/{slug}/materials/literature/{slug}.md`.

The report should include:
- Assessment of the claim's defensibility
- A markdown table of relevant references with these columns:
  | Author(s) | Year | Title | Venue | Citations | Relevance | Key insight |
  - **Venue**: conference or journal name
  - **Citations**: approximate Google Scholar citation count at time of search
  - **Relevance**: one of `supports`, `challenges`, or `nuances`
  - **Key insight**: one sentence on why this reference matters for the claim
- Discussion of edge cases and caveats
- Suggested phrasing refinements if the claim needs softening

### PDFs

Download PDFs to `references/pdfs/` (flat, no subfolders). For paywalled papers, search for preprints — check Google Scholar for arXiv/preprint links, author homepages, and institutional repositories before giving up. Only skip a paper if no free version can be found; note skipped papers in the table.

After downloading, extract and generate notes using the ms-pdf-extract skill. **Always pass `--slug` and `-c`**:

```bash
poetry run python3 .claude/skills/ms-pdf-extract/pdf2md.py references/pdfs/ --notes --slug {topic-slug} -c "Investigating claim: {the claim}. This paper {supports/challenges/provides context for} it because..."
```

Output goes to `references/md/` (markdown, flat), `references/bib/` (bibliography), `references/notes/{topic-slug}/` (notes), and `references/leads/{topic-slug}/` (leads).

Aim for 5-10 references. Quality over quantity — prioritize papers from reputable conferences/journals, highly cited work, and well-known researchers in the field.

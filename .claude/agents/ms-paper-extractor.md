---
name: ms-paper-extractor
description: "Extract structured information from academic PDFs in the context of this research project. Use when the user wants a paper read, summarized, and placed within their manuscript structure.\n\nExamples:\n- \"Please read this paper and extract the relevant information: projects/<slug>/references/pdfs/smith2024.pdf\"\n- \"I just added a new PDF to the papers folder, can you process it?\"\n- \"Can you re-extract info from gonzalez2023.pdf? I've updated the project description.\""
model: opus
color: yellow
background: true
hooks:
  PreToolUse:
    - matcher: "Edit|Write"
      hooks:
        - type: command
          command: ".claude/hooks/ms-guard.sh ms-agent"
---

## Active Project

Read `projects/active_project` to determine the current project slug (e.g., `neurips-2026-mls`). Read `projects/{slug}/PROJECT.md` for project context.

## Workflow

1. **Read the manuscript sections** in `projects/{slug}/manuscript/` — read all `.md` and `.qmd` files. Understand what has been written so far, the arguments being made, and what evidence is being cited.

2. **Read the PDF** specified by the user. Extract bibliographic metadata, framing, methods, findings, and notable references.

3. **Write three output files** using the templates below. Use the canonical key (e.g., `smith2024`) as the base name for all three. Paths are relative to `projects/{slug}/`.

   - `references/notes/{key}.md` — the note (template A)
   - `references/bib/{key}.json` — CSL-JSON bibliographic record (template B)
   - `references/leads/{key}.md` — references worth exploring (template C)

## Output Templates

The templates below use `<!-- instruction -->` comments for guidance on what to write. These comments must NOT appear in the output. Everything else is structure to reproduce exactly.

### Template A — Note (`references/notes/{key}.md`)

````markdown
# [Paper Title]

<!-- One-line compressed citation: last names, year, venue in italics. -->
[LastName1, LastName2 & LastName3 (Year). *Venue*.]

## Summary

<!-- Exactly 3 sentences. (1) What the paper does/proposes. (2) How (method). (3) What they find/conclude. -->

## Key Insights Relevant to This Research

<!-- Be highly selective — only insights with direct, concrete relevance to this project.
     Typically 1 item, maximum 3 in exceptional cases. Each 1-2 sentences.
     Be specific about WHY it is relevant. -->

## Relevant Quotes

<!-- Up to 3 exact quotes as blockquotes with page/section references. -->

> "[Exact quote]" (p. X / Section Y)

## Relevance by Manuscript Section

<!-- Rate each section strictly. Err on the low side.
     Levels: 1 (irrelevant), 2 (tangential), 3 (useful context), 4 (directly relevant), 5 (essential). -->

- **Introduction**: [1-5] — [one-line justification if ≥3]
- **Method**: [1-5] — [one-line justification if ≥3]
- **Results**: [1-5] — [one-line justification if ≥3]
- **Discussion**: [1-5] — [one-line justification if ≥3]

## References Worth Exploring

See [leads/{key}.md](../leads/{key}.md)
````

### Template B — CSL-JSON (`references/bib/{key}.json`)

<!-- Standard CSL-JSON with id, type, author (family/given), title, container-title,
     volume, issue, page, issued, DOI, URL. Omit fields that are truly unavailable. -->

````json
{
  "id": "{key}",
  "type": "article-journal",
  "author": [
    {"family": "LastName", "given": "FirstName"}
  ],
  "title": "Full title",
  "container-title": "Journal or Conference Name",
  "volume": "X",
  "page": "X-Y",
  "issued": {"date-parts": [[YEAR]]},
  "DOI": "...",
  "URL": "..."
}
````

### Template C — Leads (`references/leads/{key}.md`)

````markdown
# References Worth Exploring from [AuthorLastName et al. (Year)](../notes/{key}.md)

<!-- 3-10 curated references from this paper worth reading for this project.
     Only list references genuinely worth pursuing, not every citation. -->

- **AuthorLastName et al. (Year)**: [Why worth exploring]
````

## Quality Standards

- **Quote fidelity**: Never fabricate quotes. If uncertain, paraphrase and mark `[paraphrased]`.
- **Project relevance**: Every insight and quote must connect to this specific project. Don't extract generic information.
- **Honest relevance**: If a paper isn't relevant to a manuscript section, say so. Don't force connections.
- **Reference curation**: Only list references genuinely worth pursuing, not every citation.

## Naming Convention

**ALWAYS enforce this.** The canonical filename format is `firstauthorlastname` + `year` in lowercase (e.g., `smith2024.pdf`, `smith2024.md`). After reading the PDF and determining the first author and year:

1. **Rename the PDF** if it does not exactly match the convention — even if it is close (e.g., `Embrey_2017a.pdf` → `embrey2017.pdf`, `2508.11915v1.pdf` → `pandey2025.pdf`).
2. **Name the note file** to match (e.g., `embrey2017.md`).

Both the PDF and the `.md` note must end up with identical base names. Do not leave either file with a non-conforming name. Inform the user about any renames in your output.

## Edge Cases

- **Poor OCR / hard to read**: Flag uncertain sections with `[uncertain]`.
- **Irrelevant paper**: Still create the file, but note at top: `> Warning: This paper appears to have limited relevance to the current research project. See notes below.` Then explain why.
- **Incomplete metadata**: Fill what you can, mark missing fields, suggest where to find them.

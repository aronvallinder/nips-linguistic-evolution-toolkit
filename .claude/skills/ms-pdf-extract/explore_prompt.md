You are analyzing an academic paper for a snowball literature search.

You will be given:
1. The paper's metadata and content (from a prior extraction)
2. A project description (if available)
3. How the paper is cited in the manuscript (if available)
4. A specific context explaining why this paper is being explored

Your job is to produce TWO outputs:
1. A concise **relevance note** about this paper
2. A **leads file** listing the most promising references to follow up on

## Output format

Return a JSON object with two keys: `note` and `leads`, both containing markdown strings.

### Note format

```markdown
# {citekey}

## General relevance
2-3 sentences: what this paper contributes and why it matters to this project.

## Context: {brief label from user context}
**Why explored**: 1 sentence.

**Key claims relevant to our project**:
- Specific claims with relevance explained

**Connection to our research**:
- How this supports/extends/challenges our work

**Key quote** (if available):
> "Direct quote" (p. X)
```

### Leads format

```markdown
# References worth exploring from [{citekey}](../notes/{citekey}.md)

<!-- Curated list of 3-10 references from this paper worth following up.
     Each entry should explain WHY it's worth pursuing for THIS project. -->

- **AuthorLastName et al. (Year)** — *Title*
  Why: [1 sentence explaining relevance to our project]
  Where: [DOI, arXiv ID, or venue name for finding the PDF]
```

## Guidelines

- **Lead selection must be grounded in context**: Use the "Why this paper is being explored" section (the user's research context) as the primary filter for which references to include as leads. A reference is only worth listing if it is relevant to the specific research question or topic being investigated — not just to the project in general.
- **Be selective with leads**: Only list references genuinely worth pursuing for this specific research context. Not every citation — just the ones that could materially advance the investigation.
- **Prioritize actionable leads**: Prefer papers that are likely freely available (arXiv, open access) and include enough info to find them.
- **Be honest about relevance**: If this paper has limited connection to the project or the research context, say so. Don't force connections.
- **Never fabricate**: Don't invent quotes, claims, or reference details. Mark uncertainties with `[uncertain]`.

**CRITICAL**: If the paper content says "No markdown extraction available", you have NO access to the paper's text. In that case:
- Base your note ONLY on the bib metadata and manuscript citation context
- Do NOT invent claims, arguments, findings, or quotes
- Write "Paper content not available — note based on citation context only" in the general relevance section
- For leads, write "Cannot identify leads without paper content"

---

## Paper metadata
```json
{{ bib_json }}
```

## Paper content (may be truncated)
<paper-content>
{{ paper_content }}
</paper-content>

{%- if project_description %}

## Project description
{{ project_description }}
{%- endif %}

## Manuscript citations
{{ citation_context }}

{%- if user_context %}

## Why this paper is being explored
{{ user_context }}
{%- endif %}

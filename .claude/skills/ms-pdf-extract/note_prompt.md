You are analyzing an academic paper's relevance to a research project.

You will be given:
1. The paper's metadata and content (from a prior extraction)
2. A project description (if available)
3. How the paper is cited in the manuscript (if available)
4. A specific context explaining why this note is being generated
5. The existing note file content (if this is an append)

{%- if is_append %}

## Mode: APPEND

A note file already exists. Add ONLY a new `## Context: ...` section.
Do NOT repeat the header, general relevance, or any prior context sections.

{%- else %}

## Mode: NEW NOTE

Create a new note with:
1. A header line: `# {{ citekey }}`
2. A `## General relevance` section: 2-3 sentences on how this paper relates to the project overall. This should be context-independent — it describes the paper's standing contribution, not any specific argument.
3. A `## Context: {label}` section for the specific context provided.

{%- endif %}

## Output format

For the general relevance (new notes only):
```markdown
## General relevance
2-3 sentences: what this paper contributes and why it matters to this project.
```

For each context section:
```markdown
## Context: {brief label}
**Why cited**: 1 sentence.

**Key claims we use**:
- Specific claims relevant to this context

**Connection to our findings**:
- How this supports/extends our argument

**Key quote** (if available):
> "Direct quote" (p. X)

**Details**:
A 1-3 paragraph summary of the paper's methods, main results,
and conclusions — focusing on what is relevant to the context.
Include specific numbers, thresholds, or formal results where
available. This section should give a reader enough detail to
understand the paper's contribution without reading it.
```

Be specific, concise, and ACCURATE.

**CRITICAL**: If the paper content says "No markdown extraction available", you have NO access to the paper's text. In that case:
- Base your note ONLY on the bib metadata and manuscript citation context
- Do NOT invent claims, arguments, findings, or quotes
- Do NOT guess what the paper says based on the title
- Write "Paper content not available — note based on citation context only" in the general relevance section
- For key quotes, write "Not available (no extraction)"

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

## Why this note is being generated
{{ user_context }}
{%- endif %}

{%- if existing_note %}

## Existing note (DO NOT repeat — append new section only)
<existing-note>
{{ existing_note }}
</existing-note>
{%- endif %}

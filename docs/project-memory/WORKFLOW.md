# Automatic project-memory workflow

This workflow applies to Codex, Claude, and other repository agents. The human
does not maintain decision records manually.

## At the start of every session

Before making a substantive claim about the research or changing code,
configuration, analysis, prompts, or documentation:

1. Read [README.md](README.md) and [CURRENT.md](CURRENT.md).
2. Search [decisions/](decisions/) for the condition or finding in scope.
3. Read the relevant decision record and its primary evidence. Do not load the
   full 19,000-word design appendix unless the task needs it.

For a tiny non-research change, reading `CURRENT.md` is enough. The operational
hold in `CURRENT.md` always applies.

## Events that require an automatic update

Update project memory during the same session, at the latest before the final
response, when any of these occurs:

- Ivar or the team explicitly makes, changes, rejects, or releases a research
  or experimental decision.
- Code/configuration changes the semantics of a condition: noise, prompt,
  memory/history, identity, task order, seed/replicate identity, model request
  profile, output path, metric, or inclusion rule.
- A bug or provenance finding changes which results can support a claim.
- An experiment or audit completes and establishes a durable result or failure.
- A meeting transcript, authored comment, or other primary source adds or
  changes the rationale for a decision.

Do not create an entry for brainstorming, unaccepted assistant suggestions,
routine refactors, formatting, tests, or intermediate debugging. If a proposal
matters, record it as `proposed` with its author; never turn it into a decision.

## How to update

1. Search for an existing decision before creating a file. Update the existing
   record when it is the same choice; use the next `DNNN` only for a distinct
   choice.
2. Re-read the target immediately before editing so concurrent work is not
   overwritten.
3. Use [decisions/TEMPLATE.md](decisions/TEMPLATE.md). Keep decision status and
   implementation status separate. Label rationale as **explicit**,
   **inferred**, or **unknown**.
4. Link the strongest available source and name its type:
   authored comment/user instruction; original transcript/notes; current slide
   text; code/config/commit; completed final-state manifest; assistant summary.
   An assistant summary is a pointer, never authority for a quotation.
5. Preserve superseded text in the chronology. Add the dated successor and
   narrow its scope; do not silently rewrite history.
6. Update [CURRENT.md](CURRENT.md) only if current state, active constraints,
   supported findings, or unresolved questions changed.
7. Add the decision to [README.md](README.md) and run:

   `python scripts/validate_project_memory.py`

The existing `researchlog.md` has a different purpose and its own trigger
rules. When an event qualifies for both, keep the decision details here and a
short auditable result/decision in the research log; do not paste one into the
other.

## Source handling

- Preserve original wording, speaker/author, absolute date, timestamp if
  available, source type, and a stable link or locator.
- Historical slide text is unavailable unless a revision or quoted anchor was
  recovered. Label current slide text as current.
- Meeting transcripts can be computer-generated and editable. Quote them as
  transcripts and preserve attribution uncertainty.
- Never copy secrets, API keys, or unrelated private conversation into this
  repository.
- When only an old Claude/Codex memory summary exists, label it
  `assistant-written summary` and look for the underlying session, transcript,
  comment, code, or run before treating it as fact.

## End-of-session check

Before claiming work complete, ask internally:

1. Did this session create a durable decision, result, invalidation, or source?
2. If yes, are the relevant decision and `CURRENT.md` updated and validated?
3. If no, leave project memory untouched.

This is event-driven maintenance during every session, not a requirement to
generate a noisy session diary.


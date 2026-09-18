# D006 — Do not use the pre-August-12 dyad collapse as evidence

- Recorded / last verified: 2026-09-15 / 2026-09-15
- Decision status: superseded result interpretation after a confirmed protocol bug.
- Scope: pre-August-12 noisy two-agent results and the resulting population-buffering interpretation; not all dyad results.
- Decision authority: Ivar's August 17 authored comment reports Aron's fix; August 12 research-log repair records the invalidation.
- Implementation status: repair documented; exact file-level boundary remains incomplete, so later filenames alone do not certify validity.

## Decision and rationale

Do not cite the earlier noisy-dyad collapse or the claim that larger population
size buffered it. **Explicit rationale:** the receiver-visible noisy transfer in
the affected dyad path was computed before the sender's later-round decision,
producing false values. Corrected dyads did not reproduce the collapse.

## Evidence

- [August 12/17 chronology](../../experiment_design_reference.md#june-september-decisions-and-corrections), including Ivar's authored [slide 686 comment](../../experiment_design_reference.md#source-slide-686), thread `AAACFueqV_A`.
- [Current audit's excluded findings](../../research/mixed_future_data_audit.md#findings-that-must-not-be-resurrected), item 1.
- [Legacy Claude bug summary](</Users/ivar/.claude/projects/-Users-ivar-Desktop-Research-AI-projects-LLM-evolution-nips-linguistic-evolution-toolkit/memory/project_dyad_transfer_noise_bug.md>) is an assistant-written search aid, not the primary source.

## Chronology and supersession

This bug boundary is separate from March's inconsistent observation-noise
diagnostic and July's duplicate-memory repair. Later corrected results may be
used only when their exact final files, code/configuration, and run metadata are
identified.

## Unresolved / next evidence

Build a file-level manifest before reusing any run near this boundary. A date,
folder name, slide position, or “fixed” heading is insufficient.


# D010 — Test mixed models in dyads and populations

- Recorded / last verified: 2026-09-16 / 2026-09-17
- Decision status: agreed population compositions, task orders and replicate count; exact schedule unresolved.
- Scope: heterogeneous interactions at both population sizes; Sonnet/GPT and Sonnet/Gemini. Execution has not started.
- Decision authority: Ivar, authored instruction in the 2026-09-16 Codex session.
- Implementation status: unimplemented; the current initializer still assigns one model and client to every agent.

## Decision and rationale

The mixed-model experiment must include both fixed two-agent dyads and rotating
eight-agent populations. This supersedes the assistant proposal to run the dyad
comparison first and leave the 4+4 population as a later extension.

Current selected compositions are Sonnet/GPT and Sonnet/Gemini for dyads,
and four Sonnet plus four GPT or four Sonnet plus four Gemini for populations.
Use `game`, `game_myth`, and `myth_game`, with five replicate runs. Homogeneous
simulations are excluded. Existing Sonnet 4.5, GPT-5 Nano and Gemini 3.7 Flash
profiles are the contextual interpretation of the model names.

On September 17 Ivar explicitly selected cross-family-only game pairing.
Each eight-agent encounter must contain one Sonnet and one GPT/Gemini agent,
with partners rotating within the opposite-family group. Same-family game
encounters are excluded. This pairing restriction does not add calls.

The assistant's current minimal interpretation is five total replicates per
composition/task-order cell, yielding 30 dyad plus 30 population runs (60
overall), rather than doubling dyad repetitions for initial sender assignment.
Starting roles must be distributed across those replicates; five cannot split
equally between two starting-role assignments. This run-count interpretation
is distinct from Ivar's explicit rejection of homogeneous compositions.

**Explicit rationale:** game interaction between heterogeneous models from
different families. **Inferred design value:** the two population sizes answer different
questions. Dyads isolate direct cross-model coordination; populations test
whether mixed-model behavior persists across changing partners and locally
transmitted text. Treat that interpretation as inferred until the team states
the intended contrast.

## Evidence

- Primary source, 2026-09-17 authored reply in this Codex conversation: "yes cross-family only. how much would this cost?"
- Primary source: Ivar's authored correction in the 2026-09-16 Codex session: "the mixed model experiment should be for both 2-agent and 8-agent scenarios."
- Subsequent authored instruction in the same session: "if its just number of replicate runs, then just do 5"; for eight agents, "one variant with 4 claude sonnet models and 4 gpt models and one variant with 4 sonnet models and 4 gemini models." Earlier assistant records overinterpreted this as approval of homogeneous dyad controls.
- Composition correction: "the point of mixed model simulation is that it is game interaction between heterogenous models; models from different families; i.e. gpt and claude, claude and gemini". This supersedes the homogeneous dyad entries in earlier assistant matrices.
- Task-order correction in the same session: "what about just game, game_myth and myth_game?" The assistant had incorrectly carried a shared-prose arm from its earlier proposal into the selected design.
- Updated planning description: [mixed-model experiment](../../research/next_cooperation_experiments.md#5-does-shared-culture-bridge-models-with-incompatible-starting-policies).
- Current implementation boundary: [`run_simulation`](../../../src/simulation.py) creates one client and assigns the same model to every agent.

## Chronology and supersession

The September 14 design review proposed a 144-run dyad screen and described a
4+4 population as a later extension. This decision changes the required scope:
both population sizes belong in the mixed-model experiment. It does not revive
the rejected generic 270-run all-pair/task/noise sweep.

The subsequent five-replicate and Sonnet-mixture selection supersedes both the
216-run planning matrix and the assistant's later 48-run pilot suggestion.

Ivar then clarified that the three arms are the existing task orders `game`,
`game_myth` and `myth_game`. Shared prose was an assistant-introduced assumption,
not a user-selected treatment. At that stage the assistant still listed 120 runs.
The subsequent rejection of homogeneous dyads supersedes that matrix and its
claim of full user approval.

## Unresolved / next evidence

Freeze the agent-ID allocation, pairing seeds,
opposite-family partner exposure and role balance,
and request profiles before launch. Use existing task-order prompt protocols.
Any use of existing homogeneous
population controls requires explicit compatibility checks; the selected
population arms alone do not isolate a mixing effect from model composition.
Only final full-state JSONs will count as completed runs.

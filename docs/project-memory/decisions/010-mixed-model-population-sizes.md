# D010 — Test mixed models in dyads and populations

- Recorded / last verified: 2026-09-16 / 2026-09-18
- Decision status: dyad stage agreed and launched (six replicates per cell, first sender alternating by family); eight-agent stage agreed in scope but deferred until the dyad results are seen; exact eight-agent schedule unresolved.
- Scope: heterogeneous interactions at both population sizes; Sonnet/GPT, Sonnet/Gemini and (dyads only, added 2026-09-18) Gemini/GPT. Dyad stage complete; eight-agent execution has not started.
- Decision authority: Ivar, authored instructions in the 2026-09-16 Codex session and the 2026-09-17 Claude session.
- Implementation status: dyads implemented in commit `620ce8b3` (per-agent pinned request plans, `agent_models` sets, launcher `scripts/run_mixed_model_dyads.py`); the eight-agent cross-family pairing mode is not implemented.

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

Later on September 17 Ivar set the dyad replicate count to six per
composition/task-order cell so that each family sends first in three
replicates (Agent_1 sends in odd rounds; Sonnet is Agent_1 in replicates
0/2/4, the other family in 1/3/5), and chose to run the two-agent stage first
and look at its results before the eight-agent stage. The dyad stage is
therefore 2 compositions × 3 task orders × 6 replicates = 36 runs; the
eight-agent stage stays at 2 compositions × 3 task orders × 5 replicates = 30
runs, not yet scheduled. Total planned: 66 runs.

Everything except the models is copied from the September informed-noise
control cells (`negative_only_reasoning_rerun_dyad_*`, base game params, no
forced defectors): prompts, request profiles, noise, memory, seeds, retry
policy. The launcher proves this equality of comparison inputs before any
paid call. Replicate 5 uses protocol seed 202608250 + 5, which no September
run used.

**Explicit rationale:** game interaction between heterogeneous models from
different families. **Inferred design value:** the two population sizes answer different
questions. Dyads isolate direct cross-model coordination; populations test
whether mixed-model behavior persists across changing partners and locally
transmitted text. Treat that interpretation as inferred until the team states
the intended contrast.

## Evidence

- Primary source, 2026-09-17 authored instructions in the Claude session: "make it 6 runs per task order so that agent families can both have 3 replicates" and "Maybe we could just start with the 2-agent version and see what results that give us?"
- Run plan and per-provider budget: [mixed_model_run_plan_2026-09-17.md](../../research/mixed_model_run_plan_2026-09-17.md); implementation commit `620ce8b3`; smoke receipt `data/json/noise_experiments/mixed_model_dyads_20260917/smoke_receipt.json` (2/2 finals, each agent's calls carry its own provider's pinned settings).
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

On September 17 the dyad stage was frozen and launched (36 runs) after the
six-replicate and dyads-first instructions; the earlier "five total
replicates, 60 runs" interpretation is superseded for dyads.

On 2026-09-18 Ivar added a third dyad composition, Gemini/GPT (18 runs,
same protocol), completed the same day. The dyad stage completed 54/54
validated finals on 2026-09-17/18
(`completion_receipt.json`, $14.70). Result summary and disclosures (one
format-failure resample, four interrupted-run resamples):
[results README](../../figures/mixed_model_dyads_20260917/README.md).

## Unresolved / next evidence

Whether to run the eight-agent stage, and in what form, is Ivar's call after
reviewing the dyad results. For the eight-agent stage, freeze the agent-ID
allocation, pairing seeds, opposite-family partner exposure and role balance
before launch; the cross-family pairing mode still has to be implemented in
`games/dyadic_pairing.py`. Use existing task-order prompt protocols.
Any use of existing homogeneous
population controls requires explicit compatibility checks; the selected
population arms alone do not isolate a mixing effect from model composition.
Only final full-state JSONs will count as completed runs.

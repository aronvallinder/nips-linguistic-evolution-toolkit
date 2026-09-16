# D005 — Keep the proposed 180 no-defector runs unlaunched while clarifying design

- Recorded / last verified: 2026-09-15 / 2026-09-16
- Decision status: hold superseded by explicit user approval; approved extension completed.
- Scope: the proposed 180 no-defector runs only. Existing September runs belong to an earlier matrix.
- Decision authority: Ivar's user-provided handoff, preserved in the design reference; no claim that Ed separately approved this hold or matrix.
- Implementation status: 180/180 completed finals; source hashes and conditions revalidated for the September 16 figures. No runs launched during the earlier reconstruction.

## Decision and rationale

Reconstruct and reconcile design decisions before launching the proposal. **Explicit rationale:** give the agent context for why settings are wanted, preserve chronology/bug fixes and uncertainty, and do not launch experiments or change settings during this work. This is an operational constraint, not a new scientific treatment choice or budget approval.

## Evidence

- [Design-reference handoff](../../experiment_design_reference.md): “Ivar reports that the proposed **180 no-defector runs have not launched**.”
- [Unresolved specification](../../experiment_design_reference.md#superseded-choices-and-unresolved-questions), item 8: exact matrix/inherited prompts/required changes not established by the recovered comments.
- [Existing September sample manifest](../../design_evidence/2026-09-15/sampled_runs.json): includes an earlier no-defector run. Its existence is not evidence this proposal launched or was approved.

## Chronology and supersession

The September14 meeting's publication/presentation priority does not itself approve180 runs. The September15 reconstruction retains the user's hold. No later release of this hold is recorded here. A future explicit user instruction and reconciled specification should be recorded as a dated successor/update, preserving this history.

## Unresolved / next evidence

Identify the exact matrix, model profiles, history, identity, prompt linkage, noise, seeds and output provenance before claiming the proposal is specified. Consult [history](001-history-and-memory.md), [anonymity](002-anonymity-and-local-transmission.md), [noise](003-noise-semantics.md) and [request profiles](004-model-request-profiles.md); none supplies launch authorization. Agent record maintenance must not silently choose unresolved settings or release this hold.

## 2026-09-16 successor — approved extension completed

**Primary source: user instructions in this repository conversation (September 15–16).**
After reconciling the design reference, Ivar said to rerun no noise and uninformed
noise while retaining informed noise, then explicitly instructed “run it please”
and requested 20 workers. No defector conditions were authorized. This supersedes
the historical hold above; the earlier unresolved section describes the old state.

The approved matrix is three models × two populations × two new noise conditions
× three task orders × five replicates = 180 runs, preserving September profiles
and per-population memory/history settings. All 180 completed; 90 existing
informed-noise controls supply the third noise condition.

Evidence: [completion receipt](../../../data/json/noise_experiments/figure2_no_defectors_20260915/completion_receipt.json),
[270-source figure manifest](../../figures/figure2_noise_comparison_20260916/provenance.json),
and [run history](../../../researchlog.md). Successful-final standard-rate cost
was $128.18926695, excluding failed attempts. Two Claude runs were resampled after
role-key failures; 24 GPT runs were rerun after exhausted credits and a billing-retry
fix. These caveats must accompany analyses.

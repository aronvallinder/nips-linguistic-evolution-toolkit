---
title: Experiment protocol — memory regime, noise, QA, and data infrastructure
status: current
updated: 2026-09-08
owner: ivar
---

# Experiment protocol

How runs are configured, audited, and stored as of the corrected v2 era.

## Memory regime: memory-primary (canonical)

The June double-memory bug (rounds appearing 2–3× via chat memory + in-prompt
recaps) was fixed by adopting **memory-primary**: both tasks are remembered in
chat memory; duplication is removed on the prompt side (`_minimal` game
templates, myth prompt carries only the co-player myth). Every fact enters
context once. Chosen over *hybrid* (amputates the reasoning→myth pathway) and
*stateless* (homogenizes myths to near-determinism: cross-agent similarity
0.820±0.021 vs 0.719±0.100). Memory-primary is the only design whose
linguistic layer visibly couples to game events — myth drift responds to a
turbulent game while the other channels stay insulated. Game play itself is
channel-invariant. _(from researchlog 2026-07-17)_

Capacity is matched to ~3 completed rounds: `memory_capacity: 3` for game-only,
6 for two-task cells. _(from researchlog 2026-08-12)_ The pre-fix June baseline
inflated the generosity ratchet and suppressed myth drift (self-similarity
0.823 vs 0.688 post-fix); do not compare its myth-stability numbers 1:1 with
post-fix runs. _(from researchlog 2026-07-17)_

## Noise: informed bidirectional is the default condition

Standing directive (2026-07-22): every new experiment runs under informed
bidirectional ±$1 uniform noise on communicated amounts — `inform_agents:
true` auto-appends the notice via `trust_game_noisy.py`. Informed ≈ uninformed
on every metric, with tighter spreads. _(from researchlog 2026-07-22)_

The cross-model defector series (2026-08-25 onward) runs under **negative-only**
noise instead. The two regimes have different dynamics: bidirectional noise
keeps send and return fractions climbing past round 10–15 before they
stabilize; negative-only noise gives flatter curves and a weaker visible
effect. Do not compare cooperation curves across the two regimes without
saying which one a run used. _(from researchlog 2026-09-01)_

**Dyad transfer-noise fix (load-bearing):** communicated-send noise is
generated only for the receiver, *after* the sender's actual transfer exists;
a missing transfer raises instead of silently becoming zero. Every result from
the pre-fix dyad path (post-round-1 receivers saw ~$0) is contaminated — see
superseded claims in [findings-taskorder-myth.md](findings-taskorder-myth.md).
_(from researchlog 2026-08-12)_

## The corrected v2 protocol (confirmatory cells)

- Full 2×3 design (2/8 agents × game / game→myth / myth→game), unified
  sender/receiver prompt builder at both population sizes
  (`prompt_regime: unified`), `history_policy: none` in causal cells (no
  synthetic self/co-player blocks; decisions live only in chat memory), hidden
  names, `pairing_mode: fixed` with accurate system instructions, paired
  pairing/noise seeds. History and prompt-regime values fail closed on unknown
  strings. _(from researchlog 2026-08-12)_
- The standard 8-agent arm deliberately retains rotating partners + a
  three-game co-player block: the contrast is *repeated dyad vs rotating
  population with reputation information*, not a pure agent-count
  manipulation. _(from researchlog 2026-08-12)_
- The game-side line "Take any myths written in this session into account…"
  is appended by one shared finalizer, exactly once, in every current game
  prompt. _(from researchlog 2026-08-12)_
- Retry hardening: an unanswered prompt is removed from private chat memory
  after an exhausted provider call; rejected attempts stay in the audit but
  never contaminate the retry context. _(from researchlog 2026-08-12)_
- Historical provenance is uneven: provider, requested settings, code state and
  stop reasons were not uniformly recorded. Absent fields remain unknown;
  neither current defaults nor absent reasoning text reconstruct an old request.
  Saved zero counters may include adapter defaults. Dataset-specific limits are
  in the [reassessment](../api-audit-reassessment-2026-09-08.md).
  _(from researchlog 2026-09-08)_

## Provider route and sampling settings

Guarded experiments declare all four `llm_settings` fields: `provider`,
provider-native `reasoning`, `temperature` policy, and `max_output_tokens`
policy. Anthropic requires an explicit positive output cap; there is no implicit
4096 cap in the guarded path. See [the usage guide](../safeguards-usage.md) for
the schema, covered entrypoints, structural validation limits and legacy opt-in.

Settings environment variables cannot override the resolved guarded plan.
New guarded runs save `run_metadata.llm_request`, the experiment condition and
per-call requested settings/outcomes. The record describes what was requested,
not a guarantee about vendor internals. Missing usage remains unknown.

Comparisons explicitly name fields that may differ and explain why, including
model and replicate where appropriate; historical comparisons also acknowledge
missing provenance. Covered readers reject undeclared differences and exact
duplicate inputs. Resume checks retain the recorded condition. These safeguards
do not silently change experimental prompts, memory, noise, task order or retries.

The September 4 proposed low-reasoning/two-sentence profile was not adopted by
the restart. The associated format study also changed myth instructions,
self-context and retry policy, so it does not justify making that format a
standard. Future native-setting robustness and format/memory interventions
remain separate scientific decisions. _(from researchlog 2026-09-08)_

## QA: audits with negative controls

- `scripts/audit_v2_protocol.py` — per-cell joint audit: exactly one accepted
  response per agent/round, unrecovered retries fail, forced-action and
  noise-check counts exact. Response validation must check *task type*, not
  just JSON shape — an accepted "myth" that is actually decision JSON slipped
  through until the validator ran at audit time too. _(from researchlog
  2026-08-12, 2026-08-21)_
- `scripts/audit_context_integrity.py` — per-call `messages_sent` audit
  (myth windows verbatim, partner myth quoted, no duplicated facts); standard
  post-batch QA. Validate audits with planted corruptions: the first version
  was blind to drops at the old edge of the window. Audits need negative
  controls too. _(from researchlog 2026-07-23)_

## Data infrastructure

- **Raw runs**: `data/json/` is gitignored; the shared store is the private HF
  dataset `machine-cultural-evolution/nips-linguistic-evolution-runs`
  (`scripts/sync_data.sh push|pull`, per-user namespaces, resumable +
  deduplicated; optional post-batch auto-push hook). Doubles as the citable
  dataset at publication. _(from researchlog 2026-08-25)_
- **Public-facing repo**: `github.com/ivarfresh/linguistic-evolution-toolkit`
  is the clean single-commit export (95 MB); this repo remains the full
  private archive. Re-check anonymity before flipping it public.
  _(from researchlog 2026-07-17)_
- Billing-failed attempts leave `*.checkpoint.json.error.json` snapshots in
  data dirs — loaders must exclude them or n inflates. _(from researchlog
  2026-07-17)_

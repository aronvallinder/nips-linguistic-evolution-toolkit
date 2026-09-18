# D004 — Record explicit model-specific request profiles without rewriting history

- Recorded / last verified: 2026-09-15 / 2026-09-15
- Decision status: later request-profile implementation documented; no new model/profile choice made by this record.
- Scope: September8 cost replay and September9–10 reasoning rerun; not all older runs or the held180 proposal.
- Decision authority: Ed requested cross-model comparisons; exact later profiles evidenced by repository records, not inferred as his verbatim numerical instructions.
- Implementation status: recorded profiles/configuration and a sampled completed Claude final; this record does not certify every provider call.

## Decision and rationale

Keep provider-native reasoning, temperature and output settings explicit per model/run family. **Explicit source direction:** Ed requested latest-prompt Claude/GPT/Gemini comparisons in two/eight agents on July13. **Unknown:** that comment does not select every later model ID or numerical budget. Reasoning labels are not a calibrated scale across vendors, and nominal temperature metadata does not prove what a provider received.

## Evidence

- [Slide677](../../experiment_design_reference.md#source-slide-677), Ed's July13 thread `AAAB_9gqYVs` and replies: comparison direction. Historical model-name comments are not current availability evidence.
- [September8 request reassessment](../../api-audit-reassessment-2026-09-08.md), [researchlog](../../../researchlog.md), “Reasoning pilot measures costs” and “Separate audit evidence from interpretation.” The earlier low-reasoning/two-sentence proposal was not adopted according to this recorded account.
- [Rerun configuration](../../../config/experiments_noisy.yaml), September9 named reasoning-rerun sets: model-specific profiles and preserved scientific matrix.
- [September sampled full-state metadata](../../design_evidence/2026-09-15/sampled_runs.json): Claude request has thinking enabled with budget 8192, `max_tokens: 64000`, and temperature default/omitted; code commit `fd6bdb26f2b0aacda88153217f3d52798d9a776e`, `code_dirty: false`.
- [Older samples](../../design_evidence/2026-09-15/early_sampled_runs.json): nominal temperature 0.8 without full per-call request evidence. [Adapter](../../../src/utils.py) is current implementation, not evidence of an absent historical field.

## Chronology and supersession

The September8 cost replay did not carry new answers forward and is not a behavioral replicate. September9–10 reruns are fresh outputs under explicit profiles. Later profiles do not invalidate or silently reclassify old conditions: provenance must identify what changed. The September8 log records Claude8192 thinking, GPT-high, Gemini-high; it does not establish equivalent effective thinking across those models.

## Unresolved / next evidence

Exact request settings for any proposed new matrix require its own resolved configuration. Missing old settings stay unknown; dates/newness alone cannot certify comparability or publication readiness. This record authorizes no paid calls or experiment launch.

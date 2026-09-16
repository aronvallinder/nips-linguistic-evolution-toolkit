# Current research state

Last verified: 2026-09-16.

## Research question

The broad question is whether narratives created from social experience can
carry information that changes cooperation, including when that information
reaches agents outside the original pair. The current evidence is strongest
for model- and condition-dependent behavioral effects, with promising older
content-transplant evidence. Reliable emergence and persistence of population
culture remains unresolved. See the [design reference](../experiment_design_reference.md)
and [data audit](../research/mixed_future_data_audit.md).

## Current operational state

- The **180 no-defector extension runs completed** after explicit user approval
  and design reconciliation. They add no-noise and uninformed negative-only noise
  at the September profiles; retain the 90 existing informed-noise controls.
  See [D005](decisions/005-hold-180-runs.md) for the superseded hold and approval.
- All 270 full-state sources were hash-checked and condition-validated for
  [the resource and delta figures](../figures/figure2_noise_comparison_20260916/README.md).
  Two Claude runs were resampled after role-key errors; GPT unfinished runs
  were rerun after credits were replenished. Preserve those caveats.
- The targeted informed `U(-2, 0)` dyad bridge completed 20/20 clean finals:
  five paired game-only/myth-first replicates for Claude and Gemini. See the
  [range-2 bridge report](../figures/noise_strength_bridge_20260916/README.md).
- No-defector comparisons are fixed dyads versus rotating populations with
  partner history, not a pure manipulation of agent count.

## Current design understanding

- Ordinary checked eight-agent runs hide display names, retain own game/myth
  exchanges through memory-primary chat context, provide the current
  co-player's three-game history separately, and transmit the previous
  round partner's myth locally. These statements are scoped to the checked
  conditions, not every historical run. See [D001](decisions/001-history-and-memory.md)
  and [D002](decisions/002-anonymity-and-local-transmission.md).
- Negative-only informed communication noise is recorded in the later
  comparison design. Earlier replacement, bidirectional, environmental, and
  communication-noise runs remain distinct conditions. See
  [D003](decisions/003-noise-semantics.md).
- Later runs use explicit model-specific request profiles. These profiles do
  not reveal missing historical API settings or make provider reasoning labels
  equivalent. See [D004](decisions/004-model-request-profiles.md).

## Result boundaries

- The audited September no-defector result is model-dependent: myth-first
  increases ordinary-agent resources for Claude and GPT in the checked setup;
  Gemini is already at the ceiling. With forced defection, differences shrink
  or become uncertain. See the [independently reproduced table](../research/mixed_future_data_audit.md#latest-figures-independently-reproduced).
- In the current dyad protocol, Claude's range-2 informed noise bridge restored
  the difference of medians to +20.0 from +3.5 at range 1; all five range-2
  paired effects were positive. The five-replicate range contrast remains
  exploratory and does not establish a monotonic dose-response. Gemini stayed
  ceiling-locked at 75 throughout.
- Historical myth-transplant results show that different injected texts can
  produce different behavior under an older apparatus. They do not yet prove
  emergent population culture in the current pipeline.
- Do not resurrect interpretations listed in
  [Findings that must not be resurrected](../research/mixed_future_data_audit.md#findings-that-must-not-be-resurrected),
  including the pre-August-12 dyad collapse, the raw 88% meme-inheritance
  claim, or a population-wide cultural collapse caused by defectors.
  The dyad boundary is tracked in [D006](decisions/006-pre-august-dyad-results-invalid.md).
- Descriptive/normative myth prompts and game-side directives are distinct
  interventions ([D007](decisions/007-prompt-regimes.md)); transplant controls
  are a separate causal design ([D008](decisions/008-myth-transplant-isolation.md));
  permanent and random forced defection are distinct stress treatments
  ([D009](decisions/009-defector-treatments.md)).

## Open questions

- Which myth information causes behavioral change, beyond extra text,
  reflection, or explicit strategic advice?
- Does useful information survive transmission to newcomers who never met the
  source agents?
- Which task-order effects survive a comparison where decision-time inputs are
  genuinely different?

Research suggestions are saved separately in
[research_proposals_from_design_review_2026-09-15.md](../research/research_proposals_from_design_review_2026-09-15.md).
They are proposals, not decisions.

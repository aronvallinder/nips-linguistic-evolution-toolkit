# Current research state

Last verified: 2026-09-23.

## Research question

The broad question is whether narratives created from social experience can
carry information that changes cooperation, including when that information
reaches agents outside the original pair. The current evidence is strongest
for model- and condition-dependent behavioral effects, with promising older
content-transplant evidence. Reliable emergence and persistence of population
culture remains unresolved. See the [design reference](../experiment_design_reference.md)
and [data audit](../research/mixed_future_data_audit.md).

## Current operational state

- **Submission target (team meeting 2026-09-22):** AAMAS, abstract 1 October
  2026, full paper 8 October 2026. The mixed-model dyad and eight-agent figures
  lead the paper; frontier results, cooperation round traces and a linguistic
  analysis of the mixed runs follow; noise strength, defector count and a
  possible message-board variant are ablations. Open figure fix: the dyad
  figure duplicates Sonnet/Gemini and must show six unique pairings. A frontier
  mixed-model rerun is proposed, not launched (see
  [D010](decisions/010-mixed-model-population-sizes.md)).
- The **linguistic analysis of the September runs completed** on 2026-09-23
  (156 myth-bearing homogeneous and mixed runs, 8,519 myths; no new runs,
  $8.18 judge labelling). Agents take up words from the myth they are shown,
  across model families too (signature-word uptake beats a permutation null in
  all 10 family × size cells). In populations, moral stances spread only
  within a family (dyad matches are confounded by shared games). Myth
  alignment does not predict cooperation, and with agent-within-run fixed
  effects neither an agent's own moral nor the shown myth's moral predicts its
  next move; generous games are followed by generous myths. The human
  validation of the moral labels is not yet done. See
  [the results README](../figures/linguistic_analysis_20260923/README.md).
- The **frontier-model rerun completed 90/90 validated finals** on 2026-09-18:
  the September no-defector matrix on Claude Opus 5 (adaptive thinking, effort
  high), Gemini 3.1 Pro Preview (thinking high) and GPT-5.6 Sol (effort high),
  five replicates per cell, $142.55. Opus 5 sits 13–19 points above Sonnet 4.5
  in five of six cells (6 points in 8-agent myth→game, where Sonnet was already at 69) and shows game < game→myth < myth→game at both sizes (Sonnet showed it in dyads only); Gemini 3.1
  Pro is ceiling-locked like 3.7 Flash; Sol replaces Nano's game-only zero-lock
  with a partial collapse in 2 of 10 game-only runs that the myth task removes.
  Thinking regime changed with the model (Claude 4.7+ rejects the fixed budget).
  See [D011](decisions/011-frontier-model-rerun.md) and
  [the results README](../figures/frontier_rerun_20260918/README.md).
- The **mixed-model dyad stage completed 54/54 validated finals** on
  2026-09-17/18 (Sonnet/GPT, Sonnet/Gemini and Gemini/GPT; game, game→myth,
  myth→game; six replicates with the first sender alternating by family).
  Every family's sending tracks its partner: Sonnet follows Gemini up and GPT
  down, GPT's game-only zero-lock persists against both partners, and Gemini
  stops sending after its first unreciprocated send against GPT (five of six
  runs; one sends twice; corrected 2026-09-22 from a reading that pooled
  replicate cohorts by global round). A myth task breaks
  the lock in every composition. See
  [the results README](../figures/mixed_model_dyads_20260917/README.md) and
  [D010](decisions/010-mixed-model-population-sizes.md).
- The exact two-agent counterpart to the slide-678 rerun completed 35/35
  validated finals with the same seven donor contexts and pinned Sonnet host
  profile. The qualitative ladder largely persists in one fixed dyad: late
  Sonnet is strongest, filler is near baseline, and low-cooperation myths are
  below baseline. See [D008](decisions/008-myth-transplant-isolation.md).
- The seven-cell slide-678 transplant rerun completed 35/35 validated finals
  using existing donor texts, historical myth-only/negative-$5 apparatus and
  pinned September Sonnet settings. The qualitative seed ladder reappeared;
  late Sonnet reached the ceiling while filler and late GPT stayed near baseline.
  Linguistic analysis still precedes later content deletion; see [D008](decisions/008-myth-transplant-isolation.md).
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
- The mixed-model dyad stage (54 runs) and the eight-agent contagion ladder
  (90 runs, 1/2/4 Gemini among GPT and 1/2/4 GPT among Sonnet, unchanged
  September population protocol) are both complete. In game-only play a lone
  Gemini is exploited by a GPT population and a lone GPT cooperates among
  Sonnets, while two or more GPTs drag Sonnet populations down; contagion of
  cooperation needs four Geminis, or a myth channel, where one Gemini suffices.
  See [the ladder README](../figures/mixed_model_populations_20260918/README.md).
  Task orders are `game`, `game_myth` and `myth_game`; no shared-prose arm. See
  [D010](decisions/010-mixed-model-population-sizes.md).

## Result boundaries

- The pinned-profile slide-678 rerun is descriptive at n=5 donor/run replicates
  per cell. It shows strong context-dependent behavioral differences under the
  historical transplant apparatus, but does not isolate narrative form from
  actionable content or separately estimate donor and run variation.
- The matched dyad rerun is also descriptive at n=5. It shows content-dependent
  differences under the current repeated-seed/no-history apparatus, so the old
  Phase-1 content null is not a general dyad result. It does not isolate which
  historical protocol difference accounts for the reversal.
- The audited September no-defector result is model-dependent: myth-first
  increases ordinary-agent resources for Claude and GPT in the checked setup;
  Gemini is already at the ceiling. With forced defection, differences shrink
  or become uncertain. See the [independently reproduced table](../research/mixed_future_data_audit.md#latest-figures-independently-reproduced).
- In the current dyad protocol, Claude's observed difference of medians was
  +20.0 at range 2 versus +3.5 at range 1; all five range-2 paired effects were
  positive. The pattern is consistent with a noise-strength explanation, but
  the five-replicate direct range contrast is too uncertain to establish one.
  Gemini stayed ceiling-locked at 75 throughout.
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

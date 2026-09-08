---
title: Findings — hidden defectors and costly punishment
status: current
updated: 2026-09-08
owner: aron
---

# Findings: mechanical defectors and the deduction institution

The defector/punishment thread (2026-08-12 → 2026-08-23): hidden mechanical
defectors (`defector_action_policy: forced_zero` — scripted zero sends/returns,
no LLM game calls, myths still LLM-written, treatment label hidden) crossed
with an optional sender-side costly deduction stage (2 points, 1:3
cost-to-target, payoff floor zero).

## Defectors: direct losses, no confirmed cascade

25% hidden defectors impose large mechanical balance losses (−$19 to −$22 per
ordinary agent) but **no confirmed population-wide behavioral or cultural
collapse**: at n=10/cell in both GPT-5 Nano and Gemini Flash-Lite, ordinary
sending (−.013, p=.258) and ordinary-myth cooperation language (p=.300) do not
move. _(from researchlog 2026-08-21)_

**Gemini shows a replicated behavior→culture imprint:** defector *authors*
(forced to defect, writing myths freely) diverge culturally in rounds 2–10 —
−.57 cooperation terms/100 words, +.06 threat terms — absent in round 1 and
absent in GPT. Forced behavior becomes culturally visible in Gemini only.
_(from researchlog 2026-08-21)_

**Circulation transmits tone, not behavior.** Swapping defector-authored myths
for ordinary ones at cultural exposures changes presented cooperation language
but not game behavior; the one-step threat-transmission signal from the screen
(23-vs-5 threat matches) failed independent replication (26 vs 22, p=.624) —
a false positive or seed-contingent pattern. _(from researchlog 2026-08-21)_

## Punishment is model-dependent: GPT spends, Gemini sanctions

- **GPT-5 Nano fails the mechanism.** Deductions are near-universal (90.9% of
  opportunities) and untargeted (defector-minus-ordinary contrast ≈0);
  availability yields no reliable cooperative benefit in a 2×2 with defectors.
  Controlled calibration rejects both wordings: current wording deducts in
  100% of high-return cases; cost-salient wording halves spending but removes
  return sensitivity entirely. GPT treats deduction as a salient action, not a
  calibrated sanction — do not tune prose toward a desired result.
  _(from researchlog 2026-08-21)_
- **Gemini Flash-Lite passes.** Calibration: both points at $0 returns, zero
  at any positive return (cross-model return-slope interaction −1.244,
  p=.0057). Live-noise threshold sits between $.25 and $.50 visible return, so
  a true-zero defector is punished ~69% of the time under ±$1 noise. In
  populations, targeting is decisive and replicated: ~81–86% of
  hidden-defector opportunities punished vs ~2–3% of ordinary receivers, with
  zero deductions after any visibly ≥half return. This is selective response
  to observed defection, not role recognition. _(from researchlog 2026-08-21,
  2026-08-22)_
- **Gemini 3.7 Flash generalizes the sanction, more graded**: full deduction
  at 0–10% returns, partial at 25%, zero at ≥50%; live targeting perfect
  (25/25 defectors, 0/65 ordinary). _(from researchlog 2026-08-23)_

## Punishment's downstream effect: crowding, defector-dependent, version-specific

In Gemini Flash-Lite, making deductions *available* *lowers* ordinary return
ratios — confirmed twice: matched arms −.0491 (Holm p=.0099) and the frozen
new-seed 2×2 −.0455 in defector populations (Holm p=.0121), with the
availability×defector interaction −.0373 (Holm p=.0373) and a near-zero
no-defector simple effect. The effect is absent in round 1 and grows to −.137
by round 10; returns shift toward exactly-half and away from generosity —
punishment anchors the minimally fair rule (motivational crowding-out).
Ordinary myths under the institution gain punishment/threat/betrayal language,
more so with defectors present. _(from researchlog 2026-08-22, 2026-08-23)_

**Not in Gemini 3.7:** the crowding effect does not reproduce (+.0026,
CI [−.0016,+.0069]) — 3.7's rigid "return exactly half of receipt" rule
(280/370 decisions exact to the cent) leaves no motivational room. Selective
punishment generalizes across Gemini versions; crowding does not. Frozen
decision: do not scale the 3.7 population design. _(from researchlog 2026-08-23)_

## Cross-model defector set (Claude / GPT-5 Nano / Gemini 3.7): provisional

The negative-only cross-model defector series (2026-08-25; 2 and 8 agents ×
game / game→myth / myth→game × 0 / 25 / 50% defectors, n=5) showed Gemini 3.7
Flash ceiling-locking without forced defection, GPT-5 Nano beating Claude
Sonnet 4.5 on collective returns in some conditions, and Claude degrading
notably once defectors are added. _(from researchlog 2026-09-01)_

**These are model-plus-settings observations, not an isolated model-only ranking.**
The 270 checked final files record direct Anthropic/OpenAI/Google routes, 90 per
model. Claude's cap of 4096 and Gemini's medium thinking/omitted temperature are
recorded. GPT's exact effort is not: minimal was a code-default inference.
Different visible reply formats also change the context retained by
memory-primary. Those differences motivate robustness checks, not blanket
invalidation or a claim that low reasoning explains the ranking.

The review found no identified silent numeric-default explanation in accepted
slide-set decisions. Missing stop reasons and incomplete attempted-run evidence
prevent a universal no-truncation or clean-data certificate. Historical model
aliases also require dataset-specific interpretation.

The later Claude format-study means reproduce, but its arms also changed myth
instructions/self-context and retries. It does not establish that prose explains
the cross-model gap or the effect of adding defectors. See the
[reassessment and descriptive table](../api-audit-reassessment-2026-09-08.md)
before citing either comparison. _(from researchlog 2026-09-08)_

## Standing design gates

- Baseline Gemini cells (both versions) are **ceiling-limited** — 3.7 sent the
  full $5 in all 360 sender decisions, making task-order/identity contrasts
  uninformative there. Punishment calibrations and defector stress tests are
  the variance-bearing designs for Gemini. _(from researchlog 2026-08-21, 2026-08-23)_
- Model eligibility for population pilots runs through the controlled
  calibration gate (selectivity: low-minus-high separation, zero high-return
  punishment, monotonicity) before any paid population cells.
  _(from researchlog 2026-08-21)_

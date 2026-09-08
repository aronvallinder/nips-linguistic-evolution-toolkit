---
title: Design constraints — what breaks ablations in this framework
status: current
updated: 2026-09-08
owner: ivar
---

# Design constraints

Hard-won rules that determine whether an ablation is a real condition or a
$60 tautology. Check new designs against all of them.

## 1. Statelessness collapses task orders (Option A)

LLM calls are stateless: each API call sees only the messages passed to it.
Under Option A (`remember=False` on discarded calls), task orders that differ
only in "what unrelated API call fired earlier" present **identical**
`messages_sent` to the decision call — they are the same condition sampled
thrice, not three conditions. Empirically confirmed: baseline / s_start / s_end+
all within sd across `["game"]`, `["myth","game"]`, `["game","myth"]`
(~$60 spent confirming). **To make task orders matter, the decision-time call's
input must differ (Option B).** _(from researchlog 2026-06-30)_

## 2. Refusals are a knife-edge conjunction — probe with runtime messages

Sonnet 4.5 can deterministically refuse (`stop_reason="refusal"`, 0 content
blocks) when an unusual-register seed sits in the **assistant slot**:

- Jabberwocky (>~200 words): refused in Phase 5; length-correlated. Same text in
  system/user slot is fine. _(from researchlog 2026-06-30)_
- Gowith seed 4: **0/8 refusal with the game-built prompt wording, 16/16 pass
  with config-template wording differing by a few words**; the original English
  passes everywhere; 4 of 5 gowith siblings pass everywhere. The trigger is a
  conjunction of content × style × exact context. _(from researchlog 2026-07-02)_
- The conjunction replicates **across translators**: seed 4's gowith
  translation is host-refused 4/4 whether Sonnet or Fable wrote it, and Fable
  itself refuses jabberwocky translation of strategy-laden myths (5/5) while
  translating innocent parables (4/5). _(from researchlog 2026-07-03)_

Consequences: (a) probe candidate seeds with the **exact runtime-built messages**
(monkeypatch dump, see `data/phase7/debug_failing_call.json`), never template
reconstructions; (b) retries rescue only *stochastic* refusals —
`src/utils.py::_should_retry_anthropic` retries empty responses since 2026-07-02;
deterministic ones censor the rep (report as refusal-censored, don't force);
(c) the refusal classifier is itself a surface-form-sensitive "reader" —
potentially reportable.

## 3. Ceiling saturation hides effect sizes

S-end+ saturates $600 in every rep, so differences *above* its effect are
invisible under the current game. A harder game (or lower multiplier) is required
before claiming any manipulation "matches" S-end+. _(from researchlog 2026-06-23)_

The same constraint governs model choice: **Gemini Flash-Lite and Gemini 3.7
Flash both play unconditional full-send in the baseline game** (3.7: $5 in all
360 sender decisions; every condition ends at exactly $75/agent). A saturated
null is not a null effect, and more replicates cannot recover variation — a
frozen headroom gate now prohibits adding baseline Gemini replicates. Gemini
needs defectors or a punishment stage to show variance. _(from researchlog
2026-08-21, 2026-08-23)_

Saturation is general, not Gemini-specific: the trust game as configured
drifts to full cooperation for every model, so condition differences live in
the *approach* to the ceiling, not the endpoint. Under bidirectional noise send
and return fractions keep climbing past round 10–15 before stabilizing; under
negative-only noise the curves are flatter and the visible effect weaker.
Per-round cooperation ratios (send fraction, return ratio) are the informative
view; cumulative balance mostly reports when the ceiling was reached.
_(from researchlog 2026-09-01)_

## 4. Silent-zero and duplication bugs corrupt whole result families

Two bug classes each invalidated a published-internally claim before being
caught:

- **Silent fallback to zero**: the dyad later-round noise path cached
  communicated transfers before the send existed, so receivers saw ~$0 for
  nine rounds. Anything downstream of a "missing value → 0" fallback is
  suspect; the fixed path raises instead. _(from researchlog 2026-08-12)_
- **Context duplication**: the double-memory bug put each round into context
  2–3× (memory + recaps), inflating cooperation ratchets and suppressing myth
  drift. _(from researchlog 2026-07-17)_

Consequence: every paid batch is preceded by a smoke run plus the joint
protocol audit, and per-call context audits (with planted-corruption negative
controls) are standard post-batch QA — see
[experiment-protocol.md](experiment-protocol.md). _(from researchlog
2026-07-23, 2026-08-12)_

## 5. Metric denominators can manufacture findings

The long-standing "trustees return less than investors send" pattern was a
chart artifact: send normalized by the $5 endowment, return by the *tripled*
receipt. In dollars, receivers returned more than was sent in 98.5% of
corrected dyad-rounds. Related metric rules now enforced: zero-received rounds
are NaN (no opportunity), not 0% cooperation; endowment is inferred as
payoff + sent − returned; analyses use each run's configured endowment.
_(from researchlog 2026-08-20)_

## 6. Provider route and reasoning settings are part of the condition

Historical environment-driven routing and incomplete request records allowed
the same configured experiment to use different conditions. The cross-model
defector records identify three direct vendor APIs. Older datasets vary in
provenance strength: some have recorded routes or launch settings; others only
have reasoning-text signatures. A missing setting is not recovered by assuming
the current code default, and a saved zero may have been written by an adapter
rather than measured by the provider.

Different models need not have identical native parameters. Comparisons must
describe model-plus-settings conditions and declare known differences; equal
reasoning labels do not establish equal computation. This does not invalidate
all historical results or establish a causal explanation for a model ranking.
The [2026-09-08 reassessment](../api-audit-reassessment-2026-09-08.md) gives
dataset-specific recorded, inferred and unknown fields. Two washout finals also
change reasoning signature halfway despite one top-level provider label; that
comparison needs a per-call/log check, not an assumed route history.

**Current guard:** PR19 pins provider, native reasoning parameters, temperature
policy and output-cap policy before requests, records the plan and outcomes,
and checks declared comparison/resume conditions. Settings environment variables
do not override a guarded request. Coverage and explicit legacy exceptions are
listed in [the safeguards guide](../safeguards-usage.md). The checks cannot
retroactively verify missing historical requests and do not select a research profile.

**Reply format is a condition, not an established mechanism.** Visible response
content is retained in memory-primary and differed across the observed models.
The September 4 format-study means reproduce, but both new arms changed myth
instructions and own-myth repetition; JSON-only also changed retries. These are
exploratory multi-factor comparisons, not isolated prose or memory effects.
No universal two-sentence output standard or low-reasoning regime was selected
by the safeguards restart. _(from researchlog 2026-09-08)_

## 7. Co-occurrence is not transmission

Same-model agents share priors, so a meme appearing in a child after appearing
in a parent is mostly base rate. The Aug-19 "60–77% edge transmission" figure
collapsed to single-digit percentage-point excess over a degree-preserving
rewiring null with exposure contrasts and negative controls; a not-yet-visible
*future* myth "predicted" adoption as well as the seen one. Under blinded
LLM-judge labels no meme family survived cleanly. Transmission claims need a
null model and a future-exposure control; 2-agent dyads have no within-run
rewiring null and need the seeding/transplant intervention instead.
_(from researchlog 2026-08-28)_

## Cheap-screen-first economics

The round-1 behavioral probe (~$1.30/pool) reproduces full-cell orderings and
predicted the gowith cell. Default workflow: probe → fund only interesting cells
($11.50 each). _(from researchlog 2026-07-02)_

The same logic governs the punishment thread: a ~$0.06 controlled calibration
(selectivity gate) decides model eligibility before any population cells, and
frozen escalation rules decide whether confirmations are funded.
_(from researchlog 2026-08-21, 2026-08-23)_

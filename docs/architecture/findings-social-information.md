---
title: Findings — identity, reputation, and social information
status: current
updated: 2026-08-25
owner: aron
---

# Findings: identity, ledgers, and history visibility

What population-level information channels do to cooperation (GPT-5 Nano and
Gemini 3.1 Flash-Lite, Game-only unless noted). All from the 2026-08-21
experiment series.

## Persistent identity helps, not hurts (hypothesis reversed)

The confirmed result contradicts the early screen: persistent stable IDs
**increase** final balance vs round-local pair IDs by +3.71/agent (n=10/arm,
p=.0063, dz=1.12). The effect develops across rounds (round-1 sending is
equal), consistent with relationship-specific trust rather than retaliation.
Persistent IDs also shift returns down (−.0647, redistribution), but sending
drives welfare. The earlier n=5 claim that persistent identity explains the
public-ledger penalty is superseded as an unstable exploratory interpretation.
_(from researchlog 2026-08-21)_

## Public population ledgers do not raise cooperation

A population-wide public ledger (stable pseudonyms + last three rounds of
noisy transfers) *lowered* balance vs private memory (62.04 vs 66.03,
raw p=.026) — and the drop is present in round 1, before any ledger rows
exist. The treatment is a public-monitoring package (stable IDs + anticipated
observability), not a clean history-learning estimate. A stable-ID/no-ledger
control attributes the round-1 drop to the persistent-identity prompt bundle,
not the ledger announcement. Post hoc, the ledger raises return ratios vs
stable IDs (+.158) — possibly norm information without a surplus effect.
_(from researchlog 2026-08-21)_

**Anonymous social information is safe:** an anonymous population record
(transfers visible, pairs relabeled each round) is indistinguishable from
private memory (65.55 vs 66.03) — the cooperation cost comes from persistent
identity, not from information availability. _(from researchlog 2026-08-21)_

Myth→Game under the ledger is directionally positive (+2.26, p=.152) but
unresolved, and ~62% of the gain is round-1 — more consistent with the myth
countering the monitoring frame than with better history processing.
_(from researchlog 2026-08-21)_

## History visibility × task order: no confirmed interaction

The exploratory n=5 result that a current-partner dossier penalizes Game-only
(−3.39/agent) but not Myth→Game (+3.40 interaction — "myth buffers targeted
retaliation") did **not** replicate in the frozen n=10 confirmation:
diff-in-diff +0.50 (p=.655). Effects look roughly additive: the dossier costs
~1.3–1.8 regardless of task order; Myth→Game adds ~1.2–1.7 regardless of
visibility. _(from researchlog 2026-08-21; confirmation supersedes the same-day
screen)_

## Model caveat: Gemini Flash-Lite is uninformative here

Gemini 3.1 Flash-Lite sends the full $5 in every sender decision of the
identity contrast (both arms exactly 1.000 proportion sent), so its identity
test is saturated, not null. Gemini social-information work needs a harder
dilemma or defectors (see
[design-constraints.md](design-constraints.md) §ceiling).
_(from researchlog 2026-08-21)_

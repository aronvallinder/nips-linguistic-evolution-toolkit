# D001 — Retain own history and partner history without duplicate reminders

- Recorded / last verified: 2026-09-15 / 2026-09-15
- Decision status: July memory-primary choice explicitly recorded; August24 history retention conditionally endorsed.
- Scope: ordinary rotating-population game/myth runs. Separate history-visibility controls and injected-myth-only ablations are not superseded.
- Decision authority: Ivar's July decision recorded in researchlog; Ed's August24 remarks attributed by meeting transcript.
- Implementation status: implemented; three bounded June–September final samples inspected, not a census.

## Decision and rationale

Keep game and myth exchanges in private chat memory; remove repeated own-history and own-myth prompt recaps. Keep the current co-player's three-game record in the sampled population condition. **Explicit rationale:** the July log says dropping game responses from memory would remove strategic response context from subsequent myth writing. This preserves the intended cross-task pathway; it does not prove a causal mechanism or access to all private model reasoning.

Ed's June5 request sought more gameplay history, especially the partner's. His August24 conditional position was to retain own-three/partner-three if already implemented. **Unknown:** why three was initially preferred over another length.

## Evidence

- [June 5 source, slide 650](../../experiment_design_reference.md#source-slide-650), Edward Hughes, 2026-06-05T11:30:54Z, thread `AAAB84WHhCk`: proposal, not a numerical selection.
- [June19 source slide660](../../experiment_design_reference.md#source-slide-660), thread `AAAB_5opJy8`: Ed flags two confusing memory mechanisms.
- [July17 researchlog](../../../researchlog.md), “memory-channel pilot,” and [commit9c392fcf](https://github.com/ivarfresh/nips-linguistic-evolution-toolkit/commit/9c392fcf): revised decision/implementation.
- [August24 transcript](https://docs.google.com/document/d/1K_7K443wQhyf86iMJEXySJgHTD_HeYEvTdvgJ1O1y3k/edit), 17:33–18:56: conditional retention; attribution has transcript limitations.
- [Final sample manifest](../../design_evidence/2026-09-15/sampled_runs.json): June self3/co-player3/capacity3; July and September self0/co-player3/capacity6, memory-primary. Full-state paths/hashes are in the manifest.
- [Agent truncation](../../../src/agents.py), [history builder](../../../games/trust_game_noisy.py), [myth template](../../../config/experiments.yaml), [task retention](../../../src/simulation.py).

## Chronology and supersession

June8 expanded history precedes the July17 duplication repair. July changes the channel carrying own history; self-window0 does not mean no own history. August12 no-injected-history isolation cells are separate experiments; the [August21 visibility protocol](../../history_visibility_confirmatory_protocol_2026-08-21.md) explicitly compares them with partner-history cells. June22–23 injected-myth-only agreement applies to a separate ablation.

## Unresolved / next evidence

Capacity counts interaction pairs: six pairs approximate three raw rounds with two tasks. Model-written summaries can preserve older events; see [effective-memory note](../../effective_memory_horizon_note.md), whose numerical findings were not reanalysed here. Reconcile exact prompts/task orders for any future matrix, including [D005's held proposal](005-hold-180-runs.md).

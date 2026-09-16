# D003 — Keep noise choices and accounting changes distinct

- Recorded / last verified: 2026-09-15 / 2026-09-15
- Decision status: August24 negative-only default recorded; earlier replacement/perturbation and accounting changes preserved as distinct historical conditions.
- Scope: negative-only default concerns the August24 comparison design, not retroactive relabeling of all earlier noise experiments.
- Decision authority: August24 slide decision plus transcript attribution to Ed and Aron's agreement; earlier repair request authored by Ed.
- Implementation status: historical environmental examples and a later communication-noise final inspected; current code supports both.

## Decision and rationale

Keep replacement versus additive perturbation, direction/magnitude, informed status, and real versus communicated accounting explicit. **Explicit historical rationale:** bidirectional noise challenged ceiling cooperation; maximum-return replacement tried to break GPT's defection spiral. These were different interventions. Ed's March30 request was to fix inconsistent values and rerun, suggesting stronger downside noise rather than incoherence. **Unknown:** a uniquely justified optimum magnitude or why every later numerical setting was selected.

## Evidence

- [Early design chronology](../../experiment_design_reference.md#early-design-original-questions-and-changes), slides225–227 and [March30 thread on slide405](../../experiment_design_reference.md#source-slide-405), `AAAB2zq_DZs` / Ed reply `AAAB4RifTxk`.
- [April29 commit f6f78bad](https://github.com/ivarfresh/nips-linguistic-evolution-toolkit/commit/f6f78bad052e19610989000deef01527d4e63594), Aron Vallinder: changes observation distortion to environmental transfers/accounts.
- [Early audit](../../design_evidence/2026-09-15/early_code_provenance.md) and [full-state sample paths/hashes](../../design_evidence/2026-09-15/early_sampled_runs.json): v4 bootstrap return decision6 becomes actual9; negative send decision3 becomes actual0. These samples demonstrate environmental effects, not every file's semantics.
- [Slide702](https://docs.google.com/presentation/d/1W0jz81TXkTHMixFNV89lsCsF_2nd9Kjxrue_bsAxEW4/edit#slide=id.g3f8443b4c31_0_0), “decisions (24th August),” and [August24 transcript](https://docs.google.com/document/d/1K_7K443wQhyf86iMJEXySJgHTD_HeYEvTdvgJ1O1y3k/edit),16:20/23:18/34:32: negative-only default and separate defector plans.
- [September final sample](../../design_evidence/2026-09-15/sampled_runs.json): communication semantics, uniform range 1, negative, both transfers, informed. [Current implementation](../../../games/trust_game_noisy.py) separates environmental and communication semantics.

## Chronology and supersession

April29 accounting changes are scientifically material; they do not prove the exact fix intended in every March comment. May discussions sought comparable perturbation rather than model-specific replacement. August24 sets negative-only direction for its design. July double memory and August dyad-transfer repairs are separate boundaries. Old outputs are not migrated into a new treatment by changing current defaults.

## Unresolved / next evidence

The precise intended noise semantics/magnitude for the [180-run proposal](005-hold-180-runs.md) remains to be reconciled. A folder name or stale config comment is insufficient; compare resolved settings, rendered prompts and final metadata. Do not merge bootstrap and negative5 as duplicates.

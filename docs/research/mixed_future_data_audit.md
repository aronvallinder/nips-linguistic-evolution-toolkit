# Repository data audit for the next experiment programme

Date: 2026-09-14. Read-only scientific audit; no simulations or paid requests. New audit outputs only.

## Main conclusion

The latest result is not uniformly small. Myth-first increases ordinary-agent cumulative resources substantially for Claude and GPT in the no-defector condition, but Gemini already achieves the maximum without myths. Forced defection reduces the available surplus mechanically; it is not itself a test of whether cultural information spreads. The most valuable next experiment should identify *what information causes an action change and whether it survives social transmission*, rather than simply add more models to the same ceiling-limited game.

## Inventory coverage and limits

A fresh recursive scan parsed and SHA-256 hashed every `.json` under this checkout, excluding `.git`, `.venv`, and `node_modules`. This includes hidden `data/.hf_stage`, the nested `nlet-hf-data` store, current local outputs, shared-run mirrors, curated shares, analyses, phases, reports, archive and project data. The resulting path inventory is [mixed_future_inventory.csv](mixed_future_inventory.csv); a normalized 132-family inventory with raw-example metadata is [mixed_future_family_inventory.csv](mixed_future_family_inventory.csv). No source files were altered. Reproduction scripts: [inventory scanner](scan_mixed_future_inventory.py) and [latest-figure verifier](verify_mixed_future_latest.py), run from the repository root. Census counts are from the scan before its own output artifacts were written; later scans naturally include additional generated JSON summaries.

- **35,852 JSON paths scanned**; 16,774 final-shaped full-state paths; **6,078 distinct byte hashes** among those finals.
- 979 checkpoint/error/partial snapshot paths excluded from the final category; 18,095 other JSON artifacts (results-only, manifests, judge outputs, derived summaries, frontend dependencies, etc.).
- Four unreadable JSON paths are two malformed Arabella judge-table files and their shared-store copies: `moral_summaries_GLM-5.2.json` and `myths_with_morals_GLM-5.2.json`. Their 50 source run files remain readable.
- A final candidate must have `agents`, `conversation_history`, `game_data`, `task_order`, not have checkpoint/error/partial in its filename, and reach its metadata-declared final round. All 16,774 candidates also had declared `num_turns` and a positive final round; none were underlength by this check.
- **These are file-integrity counts, not 6,078 independent valid replicates.** Byte-distinct copies can share ancestry; smoke runs, deliberately superseded conditions, excluded dirty-code runs, and finals with historical semantic bugs remain in this inventory. Every proposed scientific comparison still needs its exact manifest and condition audit. No historical unknown is silently certified clean.
- CSV/TSV summaries and markdown reports were read selectively for interpretation; every raw JSON was structurally parsed, but not every historical prompt or derived numerical result was independently reanalysed. No remote HF freshness claim is made. Data only available remotely is outside this local census.

| Store | Final-shaped paths | Interpretation |
|---|---:|---|
| `data/json` | 5,351 | Main local raw families, including September reruns |
| `data/.hf_stage/ivarfresh` | 5,058 | Upload staging copies; not extra replications |
| `data/shared_runs/uploaders` | 1,620 | Downloaded shared sets from three uploaders |
| `data/share` | 117 | Curated source bundles, including corrected confirmatory and smoke sets |
| `data/sample` | 2 | Demonstration copies |
| `nlet-hf-data` | 4,576 | Nested data-store checkout; important historical families absent from main output tree |
| `arabella_analyses/data/runs_json` | 50 | Curated source transcripts; duplicated elsewhere |

The preceding September 8 audit covered 4,129 selected paths / 3,661 distinct files from a historical 6,678-row index. The fresh census is broader; do not confuse differing scope with newly completed experiments. See [API reassessment](../api-audit-reassessment-2026-09-08.md).

## Latest figures: independently reproduced

Inputs: [figure run values](../figures/negative_only_crossmodel_reasoning_rerun_20260909_resources_boxplots/run_values.csv), [270-run manifest](../figures/negative_only_crossmodel_reasoning_rerun_20260909/run_manifest.csv), and boxplot `provenance.json`.

Every one of the **270 source-file hashes** matches figure provenance; all finish at round 10. All **405 plotted per-run values** reproduce exactly from final round `balances`, selecting all agents or excluding `defector_agent_ids` as appropriate. The 405 values reuse the population runs for two selections; they are not 405 independent runs.

For the population task-order comparisons, all 45 model × treatment × replicate blocks have matching pairing seed, noise seed, defector seed and defector identities across three task orders. Model sampling remains stochastic; matching protocol seeds is not matching model randomness. Actual noise consumption can still depend on execution path.

Below, each cell is mean (± sample SD) across five independent run outputs. The difference column is the mean (± sample SD) of five seed-paired differences, with an **unadjusted** two-sided t interval (4 df). These exploratory intervals assume an approximately normal distribution of differences, are unstable at n=5, and are not multiplicity-adjusted confirmatory tests. A zero-width ceiling interval does not establish zero effect under other environments.

| Model | Defectors | Game only | Game → Myth | Myth → Game | Paired Myth → Game minus Game (95% t CI) |
|---|---|---|---|---|---|
| claude-sonnet-4.5 | defectors25 | 43.43 (±2.07) | 46.88 (±1.36) | 51.04 (±3.42) | +7.60 (±3.62); [+3.11, +12.09] |
| claude-sonnet-4.5 | defectors50 | 32.20 (±3.73) | 33.48 (±2.59) | 35.34 (±1.58) | +3.14 (±3.90); [-1.71, +7.98] |
| claude-sonnet-4.5 | none | 55.17 (±1.01) | 54.11 (±0.92) | 68.73 (±4.43) | +13.56 (±3.62); [+9.07, +18.05] |
| gemini-3.7-flash | defectors25 | 58.97 (±1.37) | 58.50 (±1.09) | 57.67 (±1.24) | -1.30 (±0.78); [-2.26, -0.34] |
| gemini-3.7-flash | defectors50 | 40.95 (±2.74) | 39.25 (±3.01) | 39.00 (±2.85) | -1.95 (±1.02); [-3.22, -0.68] |
| gemini-3.7-flash | none | 75.00 (±0.00) | 75.00 (±0.00) | 75.00 (±0.00) | +0.00 (±0.00); [+0.00, +0.00] |
| gpt-5-nano | defectors25 | 25.20 (±0.45) | 32.85 (±7.87) | 33.36 (±6.87) | +8.16 (±7.04); [-0.58, +16.90] |
| gpt-5-nano | defectors50 | 25.00 (±0.00) | 25.70 (±1.16) | 30.35 (±6.32) | +5.35 (±6.32); [-2.50, +13.20] |
| gpt-5-nano | none | 25.00 (±0.00) | 37.98 (±7.13) | 45.01 (±8.32) | +20.01 (±8.32); [+9.67, +30.34] |

The practically important contrast is not “myths work versus do not work.” It is **escape from GPT's zero-send state, acceleration of Claude's cooperation, and no headroom in Gemini**. The Claude no-defector myth-first difference is +13.56 resources per agent; GPT's is +20.01. Both are large on this 0–75 scale. In 50%-defector populations, the corresponding estimates shrink and become uncertain; Gemini shows small negative ordinary-agent differences. Nothing here establishes universal cultural benefit.

The Sept10 researchlog reports actual GPT zero decisions with normal completion and substantive reasoning tokens; this is not a parsing default explanation. It also discloses one discarded/resampled Claude role-confusion run, 15 interrupted GPT in-flight runs resampled, and two execution commits surrounding a validator fix. These caveats must travel with the dataset. Read [researchlog](../../researchlog.md), first two dated entries. The high-reasoning setting is recorded for the current run, but a causal reasoning-effort explanation is still untested.

## Historical evidence map: what has already been tried

Counts below are distinct final file bytes for the named family, except grouped phases; they are not pooled analysis Ns. Full family detail and raw samples are in the inventory CSV.

| Family / source | What was actually tested | Evidence and limitation |
|---|---|---|
| `v1`, `v2`, `v2_uniform_distribution_noise`, `v3_deterministic_noise`; `baseline` | Earlier models, myth orders, topics, personas, noise distributions | Large exploratory corpus; changing payoff/noise implementation and old memory contexts prohibit pooling with corrected negative-only runs. |
| `v4_direct_provider` (836); controls (898); A1 partner myth (118); A3 forced reasoning (111); combined (74); targeted/bootstrap/shared-context families | Prompt framing, partner-myth exposure, visible reasoning, noise awareness, shared context, bootstrap/adversarial controls | Much more has already been tried than the latest figure implies. Historical summary reports many null/harmful cells, not a universal myth effect; provider records incomplete, pre-fix semantics apply. |
| `baseline_match_ablation` (126) | Matched baseline / memory-related interventions | Recorded direct-route and low-effort environment fields are stronger than most old v4 metadata, but not complete per-call receipts. |
| `ablation_phase1` (80) | Seed content crossed with memory manipulation | Mechanism initially attributed largely to memory regime; later phases changed the apparatus substantially. |
| Phase2 baseline (45), seeded (60), pilot (3), smoke (1) | High/low-coop source myths, first/last-round seeds, filler; three orders | Some initial task-order and seed-age claims later reversed after reinjection/statelessness correction. |
| Phase3 baseline (5), seeded (13 including Haiku smokes); phase4 baseline (10), seeded (20), smoke (2) | Persistently reinjected myth-only seeds; task-order variants | Stateless discarded tasks can yield the same decision-time messages: not independent task-order treatments. |
| Phase5 seeded (11); phase6 seeded (10); phase7 seeded (4) | Low-coop/filler seeds, cross-writer model transfer, altered grammar | Strongest historical content-intervention arc, but a different memory/noise apparatus and incomplete route provenance. One grammar arm refusal-censored. |
| Phase7 decoder and behavioral probe JSON; Phase8 monitored (5), smoke (1); phase9 seed candidates | Readout versus behavior, monitor penalties, translation/refusal | Probe outputs are not full simulated populations. Silent-monitor null is an induction null; no evidence of hidden cultural coding. |
| `corrected_v2_confirmatory_20260812` (60) | Three task orders × dyad/population, n=10 | Strong corrected endogenous-myth reference, using informed bidirectional ±1 communication noise; do not merge with current negative-only condition. |
| Memory-primary/hybrid/stateless pilots; lineage and washout (30) | Memory design, self-myth continuity, 20-round persistence | Lineage raises textual fidelity; behavioral amplification small-n. Washout mixed route labels and two within-run reasoning-signature transitions prevent clean persistence attribution. |
| Population-ledger extension (3) plus original smoke (2); myth-first ledger (5); anonymous record (5); stable IDs (5); identity confirmation (20) | Public transfer records, pseudonyms, visibility anticipation, anonymity | These are **action ledgers**, not an editable inherited myth board. Initial identity interpretation reversed at n=10. |
| History visibility confirmation (40) | Private/dossier information × task order | Exploratory “myths buffer reputation penalty” interaction failed independent confirmation. |
| Defector crossmodel screen (20) and confirmation (40); circulation screen (10) and confirmation (20) | Hidden scripted defectors; alter which authors' myths circulate | Mechanical resource loss, little evidence of population behavioral cascade. Defector author language can change without changing ordinary behavior; threat-transmission screen failed replication. |
| Punishment screens, calibrations, matched arms and Gemini factorial confirmation (40) | Costly sanctions, selectivity and motivational effects | GPT spent untargetedly; Gemini selectively sanctioned. Flash-Lite crowding replicated but did not generalize to Gemini 3.7. Model-specific eligibility matters. |
| `negative_only_crossmodel_defectors_n5_20260825` (270) | Pre-rerun three-model × regime × order × defection matrix | Recorded unequal model profiles; not intrinsically invalid, but exact GPT effort unrecorded. |
| `fmt_confound_20260904` (10) plus earlier reference | Visible prose / JSON output comparisons | Myth instructions/self-context and retries also changed. Cannot interpret as isolated prose or reasoning-memory effect. |
| `gpt55_rerun_20260909` (12) | Fresh audited gate, two reps/cell | Narrow exact-message replay validation, small n, ceiling-limited cells. Not a substitute for a multi-model mechanism test. |

Supporting current overviews: [task-order findings](../architecture/findings-taskorder-myth.md), [seed findings](../architecture/findings-cooperation-transplant.md), [defector and punishment findings](../architecture/findings-defectors-punishment.md), [identity confirmation](../identity_persistence_confirmation_gpt_n10_overview_2026-08-21.md), [history confirmation](../history_visibility_confirmation_gpt_n10_overview_2026-08-21.md), [API reassessment](../api-audit-reassessment-2026-09-08.md).

## Independently reproduced historical seed outcomes

I reopened the listed local Phase3/5/6/7 finals and summed their final per-agent balances. These values exactly reproduce the reported seed ladder. They describe 8-agent **joint** resources (ceiling 600), not the latest per-agent boxplot scale. All hosts below are archived Sonnet 4.5 labels under the old myth-only/reinjection apparatus.

| Seed condition | Completed runs | Joint resources |
|---|---:|---:|
| Baseline, Phase3 | 5 | 437.40 (±5.50) |
| Filler, Phase5 | 5 | 446.00 (±7.68) |
| First-round myth, Phase3 | 5 | 499.00 (±11.47) |
| High-cooperation final myth, Phase3 | 5 | 600.00 (±0.00) |
| Low-cooperation final myth, Phase5 | 5 | 407.20 (±39.54) |
| Gemini-written final myth, Phase6 | 5 | 549.20 (±45.44) |
| GPT-written final myth, Phase6 | 5 | 446.20 (±13.48) |
| Gowith-translated final myth, Phase7 | 4 | 598.50 (±1.91) |

Raw roots: `data/json/noise_experiments/phase3_baseline`, `phase3_seeded`, `phase5_seeded`, `phase6_seeded`, `phase7_seeded`. The family inventory records representative exact paths. These suggest semantic content can change behavior, but do **not** yet establish emergent population culture under the modern pipeline. They are the strongest justification for a bridging content intervention, with matched concise-strategy controls.

## Findings that must not be resurrected

1. Pre-Aug12 noisy-dyad collapse and the old population-buffering claim: faulty communicated transfers after round 1. Corrected dyads did not exhibit that collapse.
2. Pre-memory-fix outcomes: repeated history appeared multiple times; not interchangeable with memory-primary.
3. Phase2 first-round-seed superiority: later seed reinjection reversed it; task-order moderation collapsed under stateless treatment construction.
4. Raw meme inheritance near 88%: Aug28 rewiring/future-exposure controls reduced it to mostly base rate; blinded judge labels produced no clean surviving family. Similar text is not proof of culture transmitted between agents.
5. Public-ledger penalty “caused by persistent identities”: small-n interpretation contradicted by later positive identity confirmation. `findings-social-information.md` retains both claims and is internally stale; cite the confirmation itself.
6. Reply prose “explains Claude's defector behavior”: the format arms changed multiple causal ingredients. The Sept8 reassessment explicitly withdraws that interpretation.
7. “Forced defectors cause cultural collapse”: confirmation found resource loss without the hypothesized population-wide cascade.
8. “All model profiles were invalid”: the audit explicitly rejects blanket invalidation. Separate model-plus-settings observations from unsupported model-only or reasoning-mechanism claims.

## Implications for the five-experiment shortlist

**Highest evidential value:** a clean content intervention in the current audited pipeline. Freeze histories/actions or branch saved states; compare actual myth against same-information prose/strategy rule, content deletion, irrelevant but length-matched text, and authentic matched donor myths. Then validate the causal contrast during free play. This separates cultural semantics from extra tokens, explicit advice and simply thinking before acting.

**Highest cultural novelty:** a bounded public myth store with controlled persistence and newcomer replacement. The existing apparatus exchanges delayed partner myths, and old public ledgers contain transfer facts rather than inherited editable cultural artifacts. Hold information budget and visibility constant, compare ephemeral/persistent stores, measure survival beyond founders and local adoption after randomized exposure. A board alone adds visibility and memory; it does not prove cultural accumulation.

**Highest headroom value:** select a harder dilemma using a predeclared baseline gate that is independent of myth benefit. More Gemini baseline reps cannot create headroom. A changed payoff schedule, stochastic ecological returns or alternative game must retain a clear social optimum and make exploitation/recovery observable. Do not choose only settings where myths happen to win.

**Mixed-model value:** distinguish live cross-model play from the already-tested cross-writer seed transfer. Heterogeneous play is scientifically useful if tied to a specific question (e.g., can a generous Gemini bootstrap GPT, and does shared culture help beyond the partner's actions?). Include homogeneous endpoints, role-balanced assignments and individual-model earnings; a pooled welfare increase could just reflect Gemini generosity or exploitation.

**Robustness value:** selective confirmations on new protocol seeds and pinned profiles, after discovery. Report all failures and retries, uncertainty over run/lineage rather than turns, welfare plus sending/conditional return/exploitation metrics, and prespecified interactions. Small n=5 boxplots with ceiling/floor atoms cannot support a broad “culture helps cooperation” claim. The strongest eventual story may be a boundary condition or causal mechanism rather than a larger mean bar.

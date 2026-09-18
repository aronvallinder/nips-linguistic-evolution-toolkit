# Slide 678 two-agent counterpart — September 17, 2026

Status: complete. All 35 final-state runs passed request-profile, context,
replicate-identity, and ten-round completion validation. No error snapshots
remain. The completion receipt hashes every included final.

## Frozen design

- Seven inherited-context cells: no text, Wikipedia filler, early Sonnet myth,
  late high-cooperation Sonnet myth, late low-cooperation myth, late Gemini myth,
  and late GPT myth.
- Five donor/run replicates per cell: 35 runs total.
- Two Claude Sonnet 4.5 host agents, ten game-only rounds, one fixed dyad.
- Same exact donor texts as the eight-agent rerun; identical text is supplied to
  both agents and reinjected each round.
- Myth-only chat context with no accumulated game messages or history block.
- Negative-$5 communication noise, hidden names, balanced sender/receiver roles.
- Native `claude-sonnet-4-5-20250929`; thinking enabled with an 8,192-token
  budget, maximum output 64,000 tokens, temperature omitted.

The intentional design change is population structure: two agents in one
repeated dyad instead of eight agents in rotating dyads. The joint-resource
ceiling is $150 rather than $600. Comparisons should therefore report raw joint
resources and percentage of the appropriate ceiling.

## Execution

Plan and outputs:
`data/json/noise_experiments/slide678_dyad_rerun_20260917/`.
The frozen plan contains 35 runs and 700 planned Claude calls. Twenty independent
runs execute concurrently. Preflight estimate: $10, based conservatively on one
quarter of the completed eight-agent call volume and a margin above its recorded
standard-rate cost.

Runner: `scripts/rerun_slide678_dyad.py`. Supervisor:
`scripts/supervise_slide678_dyad.py`. Free checks exercised complete baseline
and seeded dyads for all seven cells; 20 tests across both rerun families passed.
Only complete, condition-validated final JSON files count as results.

This run is not a replication of the historical Phase-1 M1/M2 factorial. It is
a matched counterpart to the new eight-agent plot, designed to test whether the
seed ladder changes with a fixed dyad versus a rotating population while holding
the current transplant apparatus constant.

## Result

| Injected context | Joint resources (mean ±SD) | Percent of $150 ceiling | n |
|---|---:|---:|---:|
| No inherited text | 90.00 (±4.74) | 60.0% | 5 |
| Unrelated Wikipedia filler | 91.40 (±3.80) | 60.9% | 5 |
| Early Sonnet myth | 110.80 (±10.12) | 73.9% | 5 |
| Late high-cooperation Sonnet myth | 140.20 (±13.86) | 93.5% | 5 |
| Late low-cooperation myth | 83.90 (±21.20) | 55.9% | 5 |
| Late high-cooperation Gemini myth | 112.02 (±6.56) | 74.7% | 5 |
| Late high-cooperation GPT myth | 100.36 (±8.53) | 66.9% | 5 |

The qualitative seed ladder largely persists in a fixed dyad. Relative to the
60.0% baseline, late Sonnet rises by 33.5 percentage points of the ceiling;
Gemini by 14.7; early Sonnet by 13.9; GPT by 6.9; filler by 0.9; and the
low-cooperation source falls by 4.1. With n=5 donor/run replicates, these are
descriptive contrasts, not equivalence or significance claims.

Every cell achieves a lower percentage of its ceiling than its eight-agent
counterpart, but the treatment lift relative to each condition's own baseline
is not uniformly weaker. The present dyad result also shows that the historical
Phase-1 content null does not generalize to this matched repeated-seed/no-history
apparatus. It does not by itself identify which historical protocol difference
caused that reversal.

The 35 retained finals record $8.486859 at standard token rates. This excludes
any transport-level retries and is not an invoice total. Figure artifacts are
under `docs/figures/slide678_dyad_rerun_20260917/`.

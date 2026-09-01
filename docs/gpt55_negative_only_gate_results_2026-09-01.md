# GPT-5.5 negative-only gate: pre-meeting result

## Outcome

The staged gate passed. All 12 requested control runs produced final full-state
JSONs: two paired replicates of each population-by-task-order cell. No accepted
run had an interaction error or corrective format retry. Results-only files,
error snapshots, logs, and transcripts were not counted as completions or
analyzed as outcomes.

- Model snapshot: `openai/gpt-5.5-2026-04-23`
- Reasoning effort: `low`
- Final full-state JSONs: 12/12
- Model interactions: 1,000
- Estimated API cost: $15.22
- Protocol: informed negative-only `U(-1, 0)` communication noise, no
  defectors, no punishment

The first attempted launch was blocked by sandbox DNS before a model response.
Its six error snapshots are excluded from analysis; each has a corresponding
successful final state from the network-enabled restart.

## Descriptive behavior (n=2 per cell)

| Population | Task order | Mean send fraction | Replicate range | Mean return / positive receipt | Mean maximum-send rate |
|---|---:|---:|---:|---:|---:|
| 2 agents | Game | 0.525 | 0.500–0.550 | 0.268 | 0.000 |
| 2 agents | Game→Myth | 0.593 | 0.585–0.600 | 0.289 | 0.000 |
| 2 agents | Myth→Game | 0.900 | 0.800–1.000 | 0.443 | 0.500 |
| 8 agents | Game | 0.726 | 0.538–0.915 | 0.348 | 0.400 |
| 8 agents | Game→Myth | 0.760 | 0.615–0.905 | 0.356 | 0.350 |
| 8 agents | Myth→Game | 0.822 | 0.683–0.960 | 0.388 | 0.400 |

GPT-5.5 therefore has usable behavioral headroom overall and is not a
universal defection model. The two-agent Myth→Game cell is notably cooperative
and one replicate reached the exact sending ceiling. The 8-agent cells vary
substantially between the two seeds, so these n=2 summaries do not establish a
stable task-order effect.

## Decision for the 4pm meeting

The technical and behavioral gates support extending GPT-5.5 if the team wants
it in the paper's cross-model claim. A full model matrix contains 90 runs. The
12 completed control runs can remain part of that matrix, leaving 78 runs: 18
additional controls and 60 defection-treatment runs. At the observed token
volume, a conservative planning estimate is at most about $100 additional;
forced-defection cells should cost less because some game calls are skipped.

Do not launch those 78 runs before the team decides that GPT-5.5 is worth the
paper-space, analysis, and deadline cost. If approved, preserve the snapshot,
reasoning effort, protocol, replicate identities, and distinct output paths
used here.

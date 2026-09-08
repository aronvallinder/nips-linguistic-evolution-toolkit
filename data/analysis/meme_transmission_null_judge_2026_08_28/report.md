# Does meme co-occurrence beat a no-transmission null?

Family signal: blinded LLM-judge labels (/Users/ivar/Desktop/Research/AI_projects/LLM_evolution/nips-linguistic-evolution-toolkit/data/analysis/meme_judge_labels_2026_08_28/judge_labels.jsonl). The prompt-elicitation table's system/direct-prompt columns remain regex-based (prompts were not judged).

Partner-myth channel only: a child is *exposed* to a meme family when at
least one partner myth visible in its prompt carries the family pattern.
Self-history is reported as retention, separately, because an agent
re-using its own words is persistence, not transmission.

## Exposure contrast (run-level mean ± sd, adoption difference in pp)

| Family | Group | Runs | Adoption exposed | Adoption unexposed | Diff | Future ctrl | Sham ctrl | Self-retention |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| proportional_reciprocity | 8-agent | 20 | +77.3 (±9.3)% | +67.6 (±18.6)% | +9.7 (±17.9)% | +7.9 (±27.2)% | -0.3 (±9.3)% | -0.2 (±19.3)% |
| proportional_reciprocity | 2-agent | 14 | +52.7 (±19.5)% | +57.5 (±29.8)% | -4.8 (±27.3)% | +7.2 (±38.7)% | — | -23.0 (±37.1)% |
| proportional_reciprocity | pooled | 34 | +67.2 (±18.7)% | +63.5 (±23.9)% | +3.7 (±23.0)% | +7.6 (±32.0)% | -0.3 (±9.3)% | -10.6 (±30.4)% |
| sustainable_equilibrium | 8-agent | 20 | +54.9 (±9.0)% | +45.0 (±14.4)% | +9.9 (±16.4)% | +8.8 (±18.7)% | +2.0 (±7.7)% | +19.1 (±12.8)% |
| sustainable_equilibrium | 2-agent | 18 | +65.6 (±14.9)% | +58.8 (±23.9)% | +6.8 (±30.5)% | +17.7 (±36.5)% | — | +22.7 (±31.0)% |
| sustainable_equilibrium | pooled | 38 | +60.0 (±13.2)% | +51.6 (±20.5)% | +8.4 (±23.8)% | +12.7 (±28.0)% | +2.0 (±7.7)% | +20.6 (±22.1)% |
| consistency_over_volatility | 8-agent | 20 | +44.2 (±13.9)% | +23.9 (±7.8)% | +20.3 (±11.5)% | +18.6 (±18.4)% | +9.9 (±13.0)% | +22.9 (±11.6)% |
| consistency_over_volatility | 2-agent | 20 | +43.7 (±30.2)% | +24.4 (±15.1)% | +19.2 (±27.5)% | +15.1 (±29.0)% | — | +18.7 (±31.6)% |
| consistency_over_volatility | pooled | 40 | +43.9 (±23.2)% | +24.2 (±11.8)% | +19.8 (±20.8)% | +16.8 (±24.0)% | +9.9 (±13.0)% | +20.8 (±23.6)% |
| trust_escalation | 8-agent | 18 | +60.8 (±11.6)% | +60.1 (±18.3)% | +0.7 (±20.2)% | +4.8 (±20.5)% | +1.6 (±7.6)% | +0.1 (±26.2)% |
| trust_escalation | 2-agent | 14 | +73.3 (±23.2)% | +69.2 (±39.2)% | +4.2 (±33.2)% | +4.5 (±27.5)% | — | +4.4 (±32.5)% |
| trust_escalation | pooled | 32 | +66.3 (±18.4)% | +64.1 (±29.1)% | +2.2 (±26.2)% | +4.7 (±22.9)% | +1.6 (±7.6)% | +1.7 (±28.3)% |
| noise_adaptation | 8-agent | 18 | +2.7 (±4.3)% | +1.5 (±1.6)% | +1.2 (±4.8)% | +1.9 (±6.7)% | +0.4 (±4.0)% | +1.9 (±4.4)% |
| noise_adaptation | 2-agent | 9 | +4.2 (±6.4)% | +8.2 (±8.7)% | -4.0 (±8.2)% | -5.3 (±10.0)% | — | +9.2 (±26.5)% |
| noise_adaptation | pooled | 27 | +3.2 (±5.0)% | +3.7 (±5.9)% | -0.5 (±6.5)% | -0.7 (±8.6)% | +0.4 (±4.0)% | +4.9 (±17.3)% |
| prosperity_through_cooperation | 8-agent | 13 | +62.3 (±9.1)% | +60.8 (±35.2)% | +1.6 (±32.8)% | +11.0 (±31.3)% | +0.9 (±14.8)% | +4.7 (±37.7)% |
| prosperity_through_cooperation | 2-agent | 8 | +48.8 (±16.9)% | +49.7 (±38.5)% | -0.9 (±29.1)% | -10.4 (±32.5)% | — | +21.2 (±23.9)% |
| prosperity_through_cooperation | pooled | 21 | +57.2 (±14.0)% | +56.5 (±35.9)% | +0.6 (±30.7)% | +2.2 (±32.8)% | +0.9 (±14.8)% | +9.6 (±34.4)% |
| trust_seeding | 8-agent | 20 | +32.6 (±7.2)% | +33.3 (±8.8)% | -0.7 (±9.0)% | +0.0 (±9.4)% | +1.3 (±8.2)% | -5.3 (±22.9)% |
| trust_seeding | 2-agent | 19 | +10.5 (±8.8)% | +15.3 (±12.4)% | -4.8 (±12.9)% | -3.5 (±18.8)% | — | +4.2 (±14.6)% |
| trust_seeding | pooled | 39 | +21.8 (±13.7)% | +24.5 (±14.0)% | -2.7 (±11.1)% | -1.5 (±14.1)% | +1.3 (±8.2)% | -0.6 (±19.6)% |
| punitive_deterrence | 8-agent | 2 | +0.0 (±0.0)% | +0.8 (±0.0)% | -0.8 (±0.0)% | -0.8 (±0.0)% | -0.7 (±0.0)% | -0.7 (±0.0)% |
| punitive_deterrence | 2-agent | 1 | +7.1 (±0.0)% | +0.0 (±0.0)% | +7.1 (±0.0)% | -3.7 (±0.0)% | — | -4.0 (±0.5)% |
| punitive_deterrence | pooled | 3 | +2.4 (±4.1)% | +0.5 (±0.4)% | +1.9 (±4.6)% | -1.7 (±1.7)% | -0.7 (±0.0)% | -2.4 (±1.9)% |
| repair_after_disruption | 8-agent | 15 | +1.3 (±3.7)% | +2.3 (±2.1)% | -1.0 (±2.4)% | -0.5 (±2.7)% | -0.3 (±4.1)% | +0.8 (±4.7)% |
| repair_after_disruption | 2-agent | 5 | +0.0 (±0.0)% | +9.3 (±10.2)% | -9.3 (±10.2)% | -9.7 (±9.7)% | — | +7.9 (±16.2)% |
| repair_after_disruption | pooled | 20 | +1.0 (±3.2)% | +4.0 (±5.9)% | -3.1 (±6.3)% | -3.4 (±7.1)% | -0.3 (±4.1)% | +2.8 (±9.6)% |

Reading guide: a transmission signal requires Diff > 0, clearly larger
than the future and sham controls. If all three are similar, the
co-occurrence reflects shared trajectories, not copying.

## Rewiring null (8-agent runs, B=10000, seed=7)

| Family | Observed diff | Null mean | Null sd | p (one-sided) | p (Holm) |
|---|---:|---:|---:|---:|---:|
| proportional_reciprocity | +9.7pp | +1.3pp | 3.0pp | 0.0053 | 0.0424 |
| sustainable_equilibrium | +9.9pp | +5.4pp | 2.1pp | 0.0152 | 0.1064 |
| consistency_over_volatility | +20.3pp | +16.3pp | 1.4pp | 0.0026 | 0.0234 |
| trust_escalation | +0.7pp | +5.2pp | 3.8pp | 0.8854 | 1.0000 |
| noise_adaptation | +1.2pp | +0.2pp | 0.7pp | 0.0671 | 0.4026 |
| prosperity_through_cooperation | +1.6pp | +3.4pp | 8.9pp | 0.5707 | 1.0000 |
| trust_seeding | -0.7pp | -2.4pp | 1.8pp | 0.1736 | 0.8679 |
| punitive_deterrence | -0.8pp | -0.8pp | 0.0pp | 0.5230 | 1.0000 |
| repair_after_disruption | -1.0pp | -0.2pp | 1.3pp | 0.7037 | 1.0000 |

The null replaces each child's visible partner myths with same-run,
same-round myths by other agents (degree-preserving). 2-agent runs are
excluded: with a single possible partner there is nothing to rewire, so
dyadic transmission claims require an interventional (seeding) design.

## Prompt elicitation (why some families cannot count as culture)

| Family | Zero-parent capsules carrying it | System prompt carries it | Direct prompt carries it |
|---|---:|---:|---:|
| proportional_reciprocity | 182 / 300 (61%) | 0 | 0 |
| sustainable_equilibrium | 95 / 300 (32%) | 0 | 0 |
| consistency_over_volatility | 21 / 300 (7%) | 0 | 0 |
| trust_escalation | 94 / 300 (31%) | 0 | 0 |
| noise_adaptation | 62 / 300 (21%) | 5000 | 0 |
| prosperity_through_cooperation | 212 / 300 (71%) | 0 | 0 |
| trust_seeding | 143 / 300 (48%) | 0 | 0 |
| punitive_deterrence | 0 / 300 (0%) | 0 | 0 |
| repair_after_disruption | 5 / 300 (2%) | 0 | 0 |

A family carried by the system or task prompt (or common in zero-parent
capsules) is elicited by the experiment itself; its presence in a child
is not evidence of cultural transmission regardless of the contrasts
above.

## Reproduction

```bash
python scripts/analyze_meme_transmission_null.py
```

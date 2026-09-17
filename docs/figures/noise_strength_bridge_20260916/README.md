# Noise-strength bridge

The targeted range-2 bridge completed 20/20 final runs: Claude Sonnet 4.5 and
Gemini 3.7 Flash, each with five game-only and five myth-first dyads. The new
runs preserve the corrected September prompts, memory, model request profiles,
paired protocol seeds and communication-noise semantics. In the recorded
scientific inputs, informed negative-noise strength changes from the existing
`U(-1, 0)` treatment to `U(-2, 0)`. Two implementation hashes also differ:
the already reviewed condition-validator and exhausted-credit handling fixes.
Neither changes prompts, requests, or simulation behavior.

The analysis combines those new finals with the hash-verified no-noise and
informed range-1 controls used in Figure 2. Resources are final actual balances
per agent. The primary plotted quantity is each paired replicate's myth-first
resources minus its game-only resources.

## Result

| Model | Noise | Game median | Myth-first median | Difference of medians | Paired effect, mean (±std) | Pair signs (+ / 0 / −) |
|---|---:|---:|---:|---:|---:|---:|
| Claude | None | 55.0 | 75.0 | +20.0 | 10.00 (±10.00) | 3 / 2 / 0 |
| Claude | `U(-1, 0)` | 51.5 | 55.0 | +3.5 | 7.42 (±11.83) | 3 / 1 / 1 |
| Claude | `U(-2, 0)` | 44.5 | 64.5 | +20.0 | 17.00 (±7.50) | 5 / 0 / 0 |
| Gemini | None | 75.0 | 75.0 | 0.0 | 0.00 (±0.00) | 0 / 5 / 0 |
| Gemini | `U(-1, 0)` | 75.0 | 75.0 | 0.0 | 0.00 (±0.00) | 0 / 5 / 0 |
| Gemini | `U(-2, 0)` | 75.0 | 75.0 | 0.0 | 0.00 (±0.00) | 0 / 5 / 0 |

For Claude, the observed difference of medians was +20.0 at range 2, compared
with +3.5 at range 1, and all five range-2 paired effects were positive. The
exact paired empirical-bootstrap interval for the range-2 mean effect is
[11.70, 23.70]. This pattern is consistent with the proposed noise-strength
explanation: the range-2 game-only baseline was lower while myth-first
cooperation remained higher.

It does not establish a monotonic dose-response. Claude's no-noise difference
of medians is also +20.0, and the paired range-2-minus-range-1 contrast is
9.58 (±17.05), with an exploratory bootstrap interval of [-3.92, 22.31]. With
five replicates per condition, the direct range contrast is too uncertain to
establish that changing the range caused the larger myth effect or to estimate
the response curve precisely. Gemini remains ceiling-locked at 75 in every run,
so this design cannot reveal a Gemini myth effect.

## Provenance

- New-run successful-final cost: **$6.462147** at recorded standard token rates;
  failed-attempt cost was zero because no run failed or retried.
- [Paired-effect plot](paired_myth_effect.png) (`PNG`, `SVG` and `PDF`).
- [Effect summary](effect_summary.csv), [paired replicate values](paired_effects.csv),
  [range contrasts](range_contrasts.csv) and [all run values](run_values.csv).
- [Full recorded conditions, source hashes and output provenance](provenance.json).
- [New-run completion receipt](completion_receipt.json).
- The 20 full-state finals and 60 associated logs/results/transcripts are in the
  [private Hugging Face dataset](https://huggingface.co/datasets/machine-cultural-evolution/nips-linguistic-evolution-runs/tree/69964113834debf90da9f5b9ba5025806abbeab9/uploaders/ivarfresh/data/json/noise_experiments/noise_strength_bridge_20260916)
  at revision `69964113834debf90da9f5b9ba5025806abbeab9`.
- The range-2 finals record execution commit `25a2d26c`; durable tag
  `noise-strength-bridge-execution-20260916` preserves it. Its tree is identical
  to PR commit `8b694c5a` after the branch rebase.

Intervals enumerate all `5^5` paired bootstrap resamples. They are descriptive
with this sample size and are not multiplicity-adjusted.

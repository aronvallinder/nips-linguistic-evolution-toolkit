# Noise-strength bridge

The targeted range-2 bridge completed 20/20 final runs: Claude Sonnet 4.5 and
Gemini 3.7 Flash, each with five game-only and five myth-first dyads. The new
runs preserve the corrected September prompts, memory, model request profiles,
paired protocol seeds and communication-noise semantics. Only informed negative
noise strength changes, from the existing `U(-1, 0)` treatment to `U(-2, 0)`.

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

For Claude, increasing the range from 1 to 2 restored the difference of medians
from +3.5 to +20.0, and all five range-2 paired effects were positive. The exact
paired empirical-bootstrap interval for the range-2 mean effect is
[11.70, 23.70]. This supports the proposed noise-strength explanation: range-2
noise lowers the game-only baseline while myth-first cooperation remains much
higher.

It does not establish a monotonic dose-response. Claude's no-noise difference
of medians is also +20.0, and the paired range-2-minus-range-1 contrast is
9.58 (±17.05), with an exploratory bootstrap interval of [-3.92, 22.31]. With
five replicates per condition, the bridge is evidence that range matters, not a
precise estimate of the response curve. Gemini remains ceiling-locked at 75 in
every run, so this design cannot reveal a Gemini myth effect.

## Provenance

- New-run successful-final cost: **$6.462147** at recorded standard token rates;
  failed-attempt cost was zero because no run failed or retried.
- [Paired-effect plot](paired_myth_effect.png) (`PNG`, `SVG` and `PDF`).
- [Effect summary](effect_summary.csv), [paired replicate values](paired_effects.csv),
  [range contrasts](range_contrasts.csv) and [all run values](run_values.csv).
- [Source hashes and analysis provenance](provenance.json).
- New-run completion receipt:
  `data/json/noise_experiments/noise_strength_bridge_20260916/completion_receipt.json`.

Intervals enumerate all `5^5` paired bootstrap resamples. They are descriptive
with this sample size and are not multiplicity-adjusted.

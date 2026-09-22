# Per-round cooperation for the mixed-model figures, 2026-09-22

Ed's priority (B) after the 2026-09-22 meeting: pull out the per-round
cooperation behind Figures 7 (mixed dyads) and 8 (eight-agent ladder). Those
figures show only where each run ends after ten rounds. These show how it got
there, in the same panel layout.

Two numbers per round, as in `analyses/cooperation_ratio_over_time.py`:

- **Send fraction** = amount sent ÷ $5. 0 = no trust, 1 = sends everything.
- **Return ratio** = amount returned ÷ amount received (the tripled transfer).
  1/3 = the sender just breaks even; 1/2 = the gain is split evenly. Undefined
  in a round where nothing arrived; those rounds are left out, so lines can break.

Each run gets one value per round (in eight-agent runs, pooled over the round's
four games). Lines are the mean over runs; bands are ± 1 sd. n = 5 runs per
homogeneous and ladder panel, 6 per mixed dyad. No new runs, no API calls.
Regenerate with `python analyses/mixed_model_cooperation_per_round.py`.

Figures:

- `fig7_dyads_send_per_round.png`, `fig7_dyads_return_per_round.png`
- `fig8_populations_send_per_round.png`, `fig8_populations_return_per_round.png`

Tables: `per_round_stats.csv` (mean, sd and run counts for every panel, task
order and round) and `run_round_ratios.csv` (one row per run and round).

## Reading

- **Sending is where the conditions separate.** After the first two rounds,
  return ratios sit between about 0.3 and 0.5 almost everywhere. The one exception is GPT in game-only
  play, which returns almost nothing.
- **Game-only mixed dyads with GPT collapse over the rounds.** Sonnet + GPT
  starts near 0.5 and reaches 0 by round 8; Gemini + GPT starts at 0.5 and
  reaches 0 by round 5. With a myth task, the same pairs climb instead
  (Gemini + GPT reaches 1.0 by round 6).
- **In the ladder, myth-first conditions start high.** Myth → Game begins
  at 0.67 to 0.83 send fraction in every mixed population, versus 0.15 to 0.53
  in game-only play. Game → Myth starts low like game-only and climbs over the
  rounds (e.g. 2 Gemini + 6 GPT: 0.30 → 0.95). By round 10 game-only is below
  Myth → Game in every mixed population (2 Gemini + 6 GPT: 0.10 vs 1.00; lone
  GPT among seven Sonnets: 0.70 vs 0.83).
- Descriptive only (n = 5–6). Inputs and their provenance are in
  `../mixed_model_dyads_20260917/` and `../mixed_model_populations_20260918/`.

## Summary tables

### Figure 7 dyads: send fraction at rounds 1, 5 and 10, mean (±sd over runs)

| Composition | Task order | Round 1 | Round 5 | Round 10 |
|---|---|---:|---:|---:|
| Gemini + GPT | game | 0.50 (±0.55) | 0.00 (±0.00) | 0.00 (±0.00) |
| Sonnet + Gemini | game | 0.80 (±0.22) | 0.92 (±0.12) | 0.91 (±0.09) |
| Sonnet + GPT | game | 0.47 (±0.39) | 0.03 (±0.08) | 0.00 (±0.00) |
| Gemini + GPT | game→myth | 0.60 (±0.49) | 0.93 (±0.16) | 1.00 (±0.00) |
| Sonnet + Gemini | game→myth | 0.80 (±0.22) | 0.97 (±0.08) | 1.00 (±0.00) |
| Sonnet + GPT | game→myth | 0.30 (±0.33) | 0.73 (±0.36) | 0.80 (±0.36) |
| Gemini + GPT | myth→game | 0.80 (±0.31) | 1.00 (±0.00) | 1.00 (±0.00) |
| Sonnet + Gemini | myth→game | 0.90 (±0.17) | 1.00 (±0.00) | 1.00 (±0.00) |
| Sonnet + GPT | myth→game | 0.67 (±0.16) | 0.68 (±0.26) | 0.82 (±0.24) |
| Sonnet + Sonnet | game | 0.60 (±0.00) | 0.52 (±0.13) | 0.46 (±0.11) |
| Gemini + Gemini | game | 1.00 (±0.00) | 1.00 (±0.00) | 1.00 (±0.00) |
| GPT + GPT | game | 0.00 (±0.00) | 0.00 (±0.00) | 0.00 (±0.00) |
| Sonnet + Sonnet | game→myth | 0.62 (±0.11) | 0.63 (±0.11) | 0.59 (±0.08) |
| Gemini + Gemini | game→myth | 1.00 (±0.00) | 1.00 (±0.00) | 1.00 (±0.00) |
| GPT + GPT | game→myth | 0.00 (±0.00) | 0.62 (±0.33) | 0.90 (±0.22) |
| Sonnet + Sonnet | myth→game | 0.74 (±0.24) | 0.66 (±0.13) | 0.63 (±0.16) |
| Gemini + Gemini | myth→game | 1.00 (±0.00) | 1.00 (±0.00) | 1.00 (±0.00) |
| GPT + GPT | myth→game | 0.56 (±0.36) | 0.80 (±0.28) | 0.69 (±0.44) |

### Figure 7 dyads: return ratio at rounds 1, 5 and 10, mean (±sd over runs)

| Composition | Task order | Round 1 | Round 5 | Round 10 |
|---|---|---:|---:|---:|
| Gemini + GPT | game | 0.00 (±0.00) | — | — |
| Sonnet + Gemini | game | 0.42 (±0.04) | 0.43 (±0.08) | 0.42 (±0.05) |
| Sonnet + GPT | game | 0.11 (±0.22) | 0.00 | — |
| Gemini + GPT | game→myth | 0.08 (±0.17) | 0.45 (±0.04) | 0.44 (±0.02) |
| Sonnet + Gemini | game→myth | 0.46 (±0.05) | 0.49 (±0.08) | 0.47 (±0.05) |
| Sonnet + GPT | game→myth | 0.10 (±0.18) | 0.45 (±0.25) | 0.44 (±0.22) |
| Gemini + GPT | myth→game | 0.39 (±0.09) | 0.45 (±0.03) | 0.44 (±0.02) |
| Sonnet + Gemini | myth→game | 0.49 (±0.05) | 0.50 (±0.09) | 0.46 (±0.04) |
| Sonnet + GPT | myth→game | 0.39 (±0.13) | 0.44 (±0.15) | 0.45 (±0.07) |
| Sonnet + Sonnet | game | 0.42 (±0.09) | 0.37 (±0.09) | 0.34 (±0.08) |
| Gemini + Gemini | game | 0.45 (±0.04) | 0.44 (±0.02) | 0.44 (±0.02) |
| GPT + GPT | game | — | — | — |
| Sonnet + Sonnet | game→myth | 0.39 (±0.06) | 0.41 (±0.03) | 0.43 (±0.10) |
| Gemini + Gemini | game→myth | 0.45 (±0.03) | 0.46 (±0.03) | 0.45 (±0.03) |
| GPT + GPT | game→myth | — | 0.27 (±0.11) | 0.32 (±0.07) |
| Sonnet + Sonnet | myth→game | 0.48 (±0.09) | 0.49 (±0.07) | 0.47 (±0.15) |
| Gemini + Gemini | myth→game | 0.46 (±0.04) | 0.46 (±0.04) | 0.47 (±0.04) |
| GPT + GPT | myth→game | 0.30 (±0.06) | 0.37 (±0.10) | 0.34 (±0.08) |

### Figure 8 eight-agent ladder: send fraction at rounds 1, 5 and 10, mean (±sd over runs)

| Composition | Task order | Round 1 | Round 5 | Round 10 |
|---|---|---:|---:|---:|
| 1 Gemini  +  7 GPT | game | 0.15 (±0.14) | 0.00 (±0.00) | 0.00 (±0.00) |
| 2 Gemini  +  6 GPT | game | 0.46 (±0.21) | 0.10 (±0.22) | 0.10 (±0.14) |
| 4 Gemini  +  4 GPT | game | 0.53 (±0.31) | 0.74 (±0.24) | 0.60 (±0.22) |
| 1 GPT  +  7 Sonnet | game | 0.51 (±0.08) | 0.48 (±0.05) | 0.70 (±0.03) |
| 2 GPT  +  6 Sonnet | game | 0.44 (±0.13) | 0.34 (±0.17) | 0.38 (±0.13) |
| 4 GPT  +  4 Sonnet | game | 0.33 (±0.17) | 0.39 (±0.33) | 0.48 (±0.17) |
| 1 Gemini  +  7 GPT | game→myth | 0.17 (±0.12) | 0.53 (±0.28) | 0.68 (±0.34) |
| 2 Gemini  +  6 GPT | game→myth | 0.30 (±0.21) | 0.64 (±0.25) | 0.95 (±0.11) |
| 4 Gemini  +  4 GPT | game→myth | 0.50 (±0.31) | 0.92 (±0.10) | 1.00 (±0.00) |
| 1 GPT  +  7 Sonnet | game→myth | 0.52 (±0.09) | 0.62 (±0.08) | 0.67 (±0.06) |
| 2 GPT  +  6 Sonnet | game→myth | 0.45 (±0.15) | 0.59 (±0.14) | 0.72 (±0.13) |
| 4 GPT  +  4 Sonnet | game→myth | 0.33 (±0.16) | 0.59 (±0.20) | 0.86 (±0.14) |
| 1 Gemini  +  7 GPT | myth→game | 0.67 (±0.13) | 0.67 (±0.34) | 0.90 (±0.22) |
| 2 Gemini  +  6 GPT | myth→game | 0.83 (±0.14) | 0.94 (±0.11) | 1.00 (±0.00) |
| 4 Gemini  +  4 GPT | myth→game | 0.80 (±0.10) | 0.99 (±0.02) | 0.99 (±0.02) |
| 1 GPT  +  7 Sonnet | myth→game | 0.76 (±0.14) | 0.79 (±0.10) | 0.83 (±0.07) |
| 2 GPT  +  6 Sonnet | myth→game | 0.74 (±0.10) | 0.89 (±0.10) | 0.90 (±0.12) |
| 4 GPT  +  4 Sonnet | myth→game | 0.78 (±0.03) | 0.78 (±0.08) | 0.78 (±0.14) |
| 8 Sonnet | game | 0.62 (±0.03) | 0.60 (±0.02) | 0.61 (±0.01) |
| 8 Gemini | game | 1.00 (±0.00) | 1.00 (±0.00) | 1.00 (±0.00) |
| 8 GPT | game | 0.00 (±0.00) | 0.00 (±0.00) | 0.00 (±0.00) |
| 8 Sonnet | game→myth | 0.60 (±0.00) | 0.59 (±0.02) | 0.59 (±0.01) |
| 8 Gemini | game→myth | 1.00 (±0.00) | 1.00 (±0.00) | 1.00 (±0.00) |
| 8 GPT | game→myth | 0.00 (±0.00) | 0.27 (±0.19) | 0.30 (±0.45) |
| 8 Sonnet | myth→game | 0.83 (±0.08) | 0.87 (±0.10) | 0.91 (±0.09) |
| 8 Gemini | myth→game | 1.00 (±0.00) | 1.00 (±0.00) | 1.00 (±0.00) |
| 8 GPT | myth→game | 0.56 (±0.10) | 0.46 (±0.30) | 0.20 (±0.33) |

### Figure 8 eight-agent ladder: return ratio at rounds 1, 5 and 10, mean (±sd over runs)

| Composition | Task order | Round 1 | Round 5 | Round 10 |
|---|---|---:|---:|---:|
| 1 Gemini  +  7 GPT | game | 0.00 (±0.00) | — | — |
| 2 Gemini  +  6 GPT | game | 0.15 (±0.17) | 0.41 | 0.44 (±0.06) |
| 4 Gemini  +  4 GPT | game | 0.17 (±0.06) | 0.32 (±0.13) | 0.32 (±0.19) |
| 1 GPT  +  7 Sonnet | game | 0.32 (±0.06) | 0.38 (±0.02) | 0.41 (±0.03) |
| 2 GPT  +  6 Sonnet | game | 0.27 (±0.09) | 0.34 (±0.03) | 0.36 (±0.06) |
| 4 GPT  +  4 Sonnet | game | 0.16 (±0.18) | 0.34 (±0.11) | 0.28 (±0.20) |
| 1 Gemini  +  7 GPT | game→myth | 0.11 (±0.22) | 0.36 (±0.08) | 0.42 (±0.03) |
| 2 Gemini  +  6 GPT | game→myth | 0.00 (±0.00) | 0.39 (±0.04) | 0.41 (±0.03) |
| 4 Gemini  +  4 GPT | game→myth | 0.12 (±0.08) | 0.43 (±0.04) | 0.44 (±0.02) |
| 1 GPT  +  7 Sonnet | game→myth | 0.33 (±0.07) | 0.42 (±0.04) | 0.42 (±0.03) |
| 2 GPT  +  6 Sonnet | game→myth | 0.32 (±0.13) | 0.40 (±0.03) | 0.44 (±0.02) |
| 4 GPT  +  4 Sonnet | game→myth | 0.18 (±0.18) | 0.43 (±0.05) | 0.45 (±0.04) |
| 1 Gemini  +  7 GPT | myth→game | 0.33 (±0.03) | 0.40 (±0.06) | 0.43 (±0.01) |
| 2 Gemini  +  6 GPT | myth→game | 0.37 (±0.07) | 0.43 (±0.02) | 0.44 (±0.02) |
| 4 Gemini  +  4 GPT | myth→game | 0.37 (±0.05) | 0.44 (±0.01) | 0.44 (±0.02) |
| 1 GPT  +  7 Sonnet | myth→game | 0.40 (±0.04) | 0.47 (±0.05) | 0.49 (±0.06) |
| 2 GPT  +  6 Sonnet | myth→game | 0.43 (±0.06) | 0.47 (±0.03) | 0.49 (±0.06) |
| 4 GPT  +  4 Sonnet | myth→game | 0.39 (±0.02) | 0.42 (±0.04) | 0.44 (±0.05) |
| 8 Sonnet | game | 0.36 (±0.03) | 0.39 (±0.03) | 0.39 (±0.02) |
| 8 Gemini | game | 0.44 (±0.02) | 0.45 (±0.01) | 0.44 (±0.02) |
| 8 GPT | game | — | — | — |
| 8 Sonnet | game→myth | 0.38 (±0.02) | 0.40 (±0.02) | 0.41 (±0.03) |
| 8 Gemini | game→myth | 0.43 (±0.02) | 0.45 (±0.01) | 0.44 (±0.02) |
| 8 GPT | game→myth | — | 0.33 (±0.06) | 0.28 (±0.13) |
| 8 Sonnet | myth→game | 0.45 (±0.04) | 0.51 (±0.05) | 0.52 (±0.06) |
| 8 Gemini | myth→game | 0.44 (±0.02) | 0.45 (±0.01) | 0.44 (±0.02) |
| 8 GPT | myth→game | 0.30 (±0.02) | 0.30 (±0.04) | 0.40 (±0.11) |

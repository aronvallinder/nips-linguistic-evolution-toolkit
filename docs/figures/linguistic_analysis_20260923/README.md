# Linguistic analysis of the September runs, 2026-09-23

Edward's priority (A) after the 2026-09-22 meeting: what the agents' myths say,
whether partners take up each other's language, whether that tracks
cooperation, and whether a myth's moral carries into play. Ivar extended it to
the homogeneous runs, so every mixed result has a same-model reference.

**Data.** All myth-bearing runs of the September informed negative-only design,
taken from the validated tables behind Figures 7 and 8 (the 20260909 folders
also hold defector variants; those are excluded by construction):

| Setting | Runs | Myths |
|---|---|---|
| 2-agent homogeneous (Sonnet 4.5, GPT-5 Nano, Gemini 3.7 Flash; game→myth, myth→game; n=5) | 30 | 600 |
| 2-agent mixed (Sonnet+GPT, Sonnet+Gemini, Gemini+GPT; n=6) | 36 | 720 |
| 8-agent homogeneous | 30 | 2,400 |
| 8-agent mixed (1/2/4 GPT among Sonnet; 1/2/4 Gemini among GPT; n=5) | 60 | 4,800 |

One GPT myth is an empty response and is dropped. Which myth each agent saw
before writing comes from each run's own `myth_exposures` record: in dyads the
partner's previous myth, in populations the previous-round co-player's myth.

**Regenerate** (from the repo root; the first two and the last are free):

```
python3 analyses/linguistic_corpus.py            # myth + decision tables
python3 analyses/linguistic_uptake.py            # item 1 (~9 min: embeddings + 1,000 permutations)
python3 analyses/alignment_vs_cooperation.py     # item 2
python3 analyses/myth_moral_judge.py             # item 3 labels (paid; cached)
python3 analyses/myth_moral_judge.py --model deepseek/deepseek-v4-flash --task label
python3 analyses/moral_carryover.py              # item 3 analysis
python3 analyses/moral_validation.py             # item 4
```

Large per-myth tables and embeddings go to `data/analysis/linguistic_20260923/`
(gitignored); judge responses are cached under `data/judge_cache/moral/`.

Every comparison below pits the myth an agent was **shown** against a
comparable myth it was **not shown**: the same family, from the same round
(8-agent: another agent in the same run; dyads: the same-family agent in
another run of the same cell). Shared prompts, shared model habits and drift
over the run hit both sides equally, so the difference is what the exposure
added. Means are over runs, ± sd across runs.

## 1. Partners take up each other's language

`language_reuse_shown_vs_unseen.png`, `reuse_summary.csv`,
`reuse_by_task_order.csv`, `reuse_by_family_pair.csv`.

**Word adoption**: of the words in the shown myth that the agent had never used
before, the share it starts using.

| Setting | Shown myth | Unseen myth | Runs where shown > unseen |
|---|---|---|---|
| 2-agent homogeneous | 16.0% (±4.6) | 6.4% (±1.2) | 30/30 |
| 2-agent mixed | 6.7% (±1.4) | 4.6% (±0.6) | 36/36 |
| 8-agent homogeneous | 13.4% (±2.4) | 8.5% (±1.0) | 29/30 |
| 8-agent mixed, shown own family | 14.1% (±2.1) | 7.7% (±0.7) | 60/60 |
| 8-agent mixed, shown other family | 6.0% (±1.5) | 4.5% (±0.6) | 57/60 |

Meaning (embedding cosine) shows the same ordering: shown minus unseen is
+0.072 (±0.057) in homogeneous dyads, +0.053 (±0.050) in mixed dyads, and
+0.014 to +0.024 in populations (all Wilcoxon p < 0.01 over runs). Both task
orders show it (`reuse_by_task_order.csv`).

Reading: agents copy words from the myth in front of them, 1.3 to 2.5 times
the rate that chance overlap with a comparable myth gives. The excess is largest
between two copies of the same model (+9.6 points in dyads, +6.3 in
populations) and a quarter to a fifth of that across model families (+2.1 and
+1.5 points).

**Cross-family signature words** (`cross_family_marker_rates.png`,
`marker_specific_uptake.csv`, `family_markers_top25.csv`). Each family has
words the other almost never uses (Gemini: *radiant, celestial, sacred,
eternal*; GPT: *gate, road, honesty, harbor, ledger*; Sonnet: *pattern,
consistency, fairly, season*). In every mixed pairing and both sizes, an agent
is more likely to start using a partner-family word when the myth it was shown
contained that word than when it did not. The excess is 1.0–3.6 percentage
points against 0.4–1.5 under a null that swaps in an unseen same-family myth;
p ≤ 0.006 in all 10 family-by-size combinations (1,000 permutations). In
mixed runs the rate of partner-family words climbs over the run, well above the
same family's homogeneous rate. In 8-agent runs it climbs furthest right after
an agent was shown an other-family myth; agents shown a same-family myth rise
less (they still meet the other family in games and indirectly).

Why this matters: the meme test that failed on homogeneous runs (August) could
not separate copying from shared model habits. Here the two models have
different habits, so a Gemini word turning up in a GPT myth, right after GPT
read that word, is transmission, not coincidence.

**Style drift** (`style_drift_toward_partner.png`, `style_drift_by_round.csv`).
A word-level classifier trained on homogeneous myths identifies the author
family of 100% of held-out homogeneous myths. On mixed myths it measures how
far each family moves toward its partner (mean probability of the partner
family, round 10). Families mostly keep their voice: 13 of the 18 family ×
composition cells stay below 0.07. The exceptions are informative:

- **Outnumbered GPT converges on the majority.** GPT scores 0.30 Sonnet-like at
  round 10 when it is 1 of 8 among Sonnets, 0.19 as 2 of 8, 0.04 as 4 of 8
  (0.01 among its own kind). This mirrors the behavioural finding that a lone
  GPT cooperates among Sonnets.
- In dyads, Sonnet moves toward Gemini (0.22) and Gemini toward Sonnet (0.12);
  GPT moves toward Sonnet (0.12).
- A lone Gemini among GPTs barely moves (0.06).

## 2. Alignment does not track cooperation

`alignment_vs_cooperation.png`, `alignment_pair_level.csv`,
`alignment_run_level.csv`. Successor to `analyses/convergence_vs_cooperation.py`
for the September data.

For every game, the similarity of the two players' latest myths before it was
related to the send (amount / 5), the return proportion, and Arabella's
giving gap (|sent/5 − return proportion|), with run and round fixed effects.

- **Within runs, myth similarity before a game does not predict cooperation in
  it.** Every send and return estimate's 95% CI includes zero, in every
  setting.
- The one consistent link runs the other way in homogeneous dyads: after a
  generous game the two players' next myths are more alike (+0.086 send per
  +0.1 similarity, 95% CI 0.031–0.140, p = 0.002). Alignment follows
  cooperation; it does not lead it.
- More alike myths go with a slightly *larger* giving gap in 8-agent
  same-family pairs (homogeneous +0.011 per +0.1 similarity, p = 0.04; mixed
  +0.026, p = 0.0001), i.e. less evenly matched giving, not more.
- **The across-run correlation is a family artefact.** Pooled over runs,
  alignment and cooperation correlate negatively (8-agent homogeneous send
  ρ = −0.72), because GPT writes the most self-similar myths (pair similarity
  0.87 in GPT dyads against 0.69–0.77 elsewhere) and sends the least. After
  centring each composition × task order, send and return correlations vanish
  (send ρ = 0.05 and −0.07 in the two 8-agent settings). Two within-cell
  exceptions: homogeneous dyads whose myths are more alike give more evenly
  (giving gap ρ = −0.50, p = 0.005), and in 8-agent mixed runs more alike
  pairs return slightly less (ρ = −0.27, p = 0.035) (`alignment_run_level.csv`).

Reading: myths converge between partners (item 1), but how alike two players
write says nothing about how they will treat each other in the next game.

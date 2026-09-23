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

One selection follows from this: an 8-agent child is scored only if its run
holds another myth from the parent's family that neither child nor parent
wrote. In the "1 minority + 7 majority" runs, a majority agent shown the lone
minority's myth therefore has no comparison and drops out (half of the
cross-family exposures in those runs). There, the "shown other family" row
measures the minority agent picking up majority words, and the 8-agent marker
test for GPT shown Gemini draws on the 2- and 4-Gemini runs only.

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

The dyad rows compare with a myth from another run, which did not share the
pair's game history; two partners who lived the same rounds could coin the
same words independently. The 8-agent rows (comparison myth from the same run
and round) and the cross-family marker test below do not have that weakness
and carry the claim.

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
same family's homogeneous rate. (That baseline is biased low, because
markers are chosen as words rare in those same homogeneous myths; but round-1
mixed myths, written before anything is shown, sit close to it, e.g. GPT
using Sonnet words in populations 0.64% vs 0.50%, against 2.04% by round 10.
The permutation test does not use this baseline.) In 8-agent runs it climbs furthest right after
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
  (0.01 among its own kind). Per run (rounds 9–10, 10 runs each): 0.26
  (±0.16), range 0.13–0.65, for the lone GPT; 0.16 (±0.12) for two; 0.04
  (±0.03) for four. Every lone-GPT run is above the homogeneous level, so no
  single run carries it. It runs parallel to the behavioural finding that a
  lone GPT cooperates among Sonnets, but item 2 shows that writing alike does
  not predict cooperating, so this is a parallel, not a mechanism.
- In dyads, Sonnet moves toward Gemini (0.22) and Gemini toward Sonnet (0.12);
  GPT moves toward Sonnet (0.12).
- A lone Gemini among GPTs barely moves (0.06).

What the classifier keys on is vocabulary and imagery, not form. Top features:
GPT *gate, bridge, receiver, sender, river, coins, travelers*; Gemini
*fifteen, harvest, radiant, golden, threefold, bounty, celestial*; Sonnet
*pattern, seasons, villages, measures* and more pronouns (*her, my, your*).
Mean length is 192–209 words in every family, and only 6% of Sonnet myths
start with a markdown heading.

## 2. Alignment does not track cooperation

`alignment_vs_cooperation.png`, `alignment_pair_level.csv`,
`alignment_run_level.csv`. Successor to `analyses/convergence_vs_cooperation.py`
for the September data.

For every game, the similarity of the two players' latest myths before it was
related to the send (amount / 5), the return proportion, and Arabella's
giving gap (|sent/5 − return proportion|), with round fixed effects and fixed
effects for each run × pair family (a mixed population holds GPT–GPT and
Sonnet–Sonnet games in the same run).

- **Within runs, myth similarity before a game does not predict cooperation in
  it.** Every send and return estimate's 95% CI includes zero, except one
  marginal case: same-family games inside 8-agent mixed runs (+0.027 send per
  +0.1 similarity, 95% CI 0.003–0.052, p = 0.03). No family shows it on its
  own (GPT, Gemini and Sonnet pairs each null), and it is one of 15
before-the-game tests.
- The one consistent link runs the other way in homogeneous dyads: after a
  generous game the two players' next myths are more alike (+0.086 send per
  +0.1 similarity, 95% CI 0.031–0.140, p = 0.002). Alignment follows
  cooperation; it does not lead it. ("After" myths are built slightly
  differently by task order: in myth→game both players have just read each
  other's myth; in 8-agent game→myth each read its previous co-player's.)
- More alike myths go with a slightly *larger* giving gap in 8-agent
  same-family pairs (homogeneous +0.011 per +0.1 similarity, p = 0.04; mixed
  +0.016, p = 0.03), i.e. less evenly matched giving, not more. Without the
  pair-family term the mixed estimate was +0.026 (p = 0.0001), so most of it
  was which families were playing.
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

## 3. Myth morals: what they say, how they spread, whether they carry into play

Labels: Arabella Sinclair's 3-label rubric (`be generous` / `be fair` /
`be cautious`) and her one-sentence moral prompt, read verbatim from
`arabella_analyses/data/rubrics/`, judged by GLM-5.2 (OpenRouter
`z-ai/glm-5.2`, temperature 0, reasoning off, her system prompt). Check first:
on the 200 June myths she labelled, this setup gives her label 93% of the time.
All 8,519 myths labelled; 8,486 got a summary (33 empty responses). Cost:
$7.23 for GLM-5.2, plus $0.84 for the DeepSeek V4 Flash second judge. Every
myth's labels and moral are in `moral_labels.csv`.

**What the morals say** (`moral_label_shares.png`, `moral_label_shares.csv`).
The families preach differently, and the mix changes that. Both judges show
the same direction for every trend below; the levels differ (DeepSeek calls
more myths generous), so read the percentages as GLM-5.2's:

- Gemini writes `be generous` or `be fair`, almost never `be cautious` (0 of
  1,940). Among GPTs its myths turn from generosity to reciprocity: in 8-agent
  mixed runs, 79% `be generous` in round 1 falls to 30% by round 10 (DeepSeek:
  94% to 51%). Homogeneous Gemini stays between 41% and 70% in every round
  (8-agent round 1 → 10: 65% → 55%; DeepSeek 84% → 85%).
- Sonnet mostly writes `be fair`. With GPTs its `be generous` share falls from
  40% to 15% over the run (DeepSeek: 61% to 21%), while it holds near 35% among
  Sonnets (DeepSeek: 54% to 44%).
- GPT writes `be fair` (79% of its myths) and is the only family with a real
  `be cautious` share (13%, up to 24% late in its own 8-agent runs).

This is the language-side echo of the behavioural result: Gemini stays
generous only while reciprocated, and GPT drags its partners down.

**Drift, stability and partner distance** (`moral_summary_drift_stability_distance.png`,
`moral_drift_stability.csv`, `moral_partner_distance.csv`). Arabella's
embedding measures on the one-sentence morals (full embeddings; her notebook
took cosines on a 2-D PCA projection, which distorts them):

- GPT and Gemini settle after round 2 (closeness to their own round-1 moral
  0.71–0.77 at round 10). Sonnet keeps rewriting its moral (0.58–0.65).
- Game partners' morals are closest in homogeneous dyads (distance 0.235
  ±0.044) and furthest between families in populations (0.286 ±0.032).

**Moral uptake** (`moral_uptake.csv`). An agent's moral moves toward the moral
of the myth it was shown, beyond an unseen myth. Its label matches the shown
myth's label more often: +7.8 points (±10.4) in homogeneous dyads, +12.9
(±15.2) in mixed dyads, +5.0 (±6.1) in homogeneous populations, +4.4 (±8.7)
for same-family exposure in mixed populations. All p < 0.001 over runs.
**Across families in populations there is no moral uptake** (−0.2 points,
p = 0.74), although the words transfer (item 1).

**Carryover into play** (`moral_carryover.png`, `moral_carryover_models.csv`,
`moral_reverse_models.csv`, `moral_behaviour_by_label.png`). For each decision:
the agent's own latest moral and the moral of the myth it was last shown,
controlling for its own last move in that role. Main model: agent-within-run
and round fixed effects, which asks whether an agent cooperates more in the
rounds when its moral is more generous than its usual. The `fe` column in the
CSV also holds the run fixed-effect version.

- **No carryover within an agent.** All settings pooled, a `be generous`
  moral in the agent's own myth changes its send fraction by +0.001 (95% CI
  −0.013 to 0.015) and its return proportion by +0.003 (−0.003 to 0.009). The
  moral of the myth it was shown: −0.009 (−0.029 to 0.011) and +0.002 (−0.004
  to 0.008). With DeepSeek labels, the same: +0.008 and +0.002 for its own,
  −0.010 and +0.001 for the shown myth, all CIs across zero.
- With only run fixed effects, an agent's own `be generous` label does go with
  more cooperation (+0.027 send, +0.011 return). That association comes from the
  mixed settings and disappears once each agent is compared with itself: it
  reflects which agents write generous myths (Gemini, and whoever is doing
  well), not rounds in which a moral changes behaviour.
- **Placebo.** In 8-agent populations, the co-player's own latest label
  predicts the investor's send even though the investor never saw that myth,
  and even controlling for the co-player's family: `be generous` +0.074
  (p < 0.001) in mixed runs with GLM labels. With DeepSeek labels it is +0.025
  (p = 0.21). A co-player's moral reflects how its recent games went, which the
  investor sees in its last three games. So labels carry information about the
  state of play, which is why only the within-agent model can speak to
  carryover.
- **The strong link runs backwards.** A more cooperative game is followed by a
  `be generous` myth: +0.16 in the probability of a generous label per unit of
  send fraction and +0.38 per unit of return proportion (both p < 0.001;
  DeepSeek +0.16 and +0.31). Myths describe the game just played.
- The single odd estimate in the run fixed-effect table (homogeneous-dyad
  receivers shown a `be cautious` myth, −0.13) rests on 19 cautious myths and
  should not be read.

Reading: myths spread words and, within a family, their moral stance. But a
myth's moral does not steer an agent's next decision.
Morals follow play more than they lead it. This fits the August null on norm
transmission and the earlier counter-current finding. A causal test still
needs the seeding design (plant a moral, compare with a placebo).

## 4. Validation

`validation/`. Two parts:

- **Second judge on every myth** (`judge_agreement.csv`, `judge_confusion.csv`):
  GLM-5.2 and DeepSeek V4 Flash agree on 74.6% of myths, Cohen's κ = 0.54
  (moderate). Nearly all disagreement is on the line between `be fair` and
  `be generous`: DeepSeek calls 1,591 of GLM's `be fair` myths generous.
  `be cautious` agrees best. Agreement is lowest on Gemini myths (κ = 0.30),
  which sit on exactly that line, so Gemini's label levels are the least
  certain; the direction of its trend holds under both judges. The carryover
  conclusions do not depend on the judge (item 3).
- **Blinded human sample**: `human_coding_sheet.csv` holds 90 myths (30 per GLM
  label, spread over families and settings, shuffled, no labels or run info),
  with `CODING_INSTRUCTIONS.md`. The key is kept out of git
  (`data/analysis/linguistic_20260923/human_coding_key.csv`) so a coder with
  repo access stays blind. After coding, `python3 analyses/moral_validation.py
  --score <sheet>` reports each judge's precision and recall per label and
  flags any label below 80% precision. **This human pass has not been done
  yet.** Until it is, the label results should be presented as judge-based.

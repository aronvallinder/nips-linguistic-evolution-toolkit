# Mixed-model results split by each family's own behaviour, 2026-09-22

Question (Arabella Sinclair, team meeting 2026-09-22): when two model families
share a trust game, does each keep the behaviour it shows among its own kind,
so the pair's score is just the average of two fixed styles, or does each move
toward its partner? The pooled resource figures for the mixed dyads and the
eight-agent ladder cannot separate these. Here every family's own sending and
returning inside a mixed composition is drawn next to the same family's value
in the homogeneous September controls.

Inputs are the validated per-decision tables of the two mixed-model analyses:
`docs/figures/mixed_model_dyads_20260917/decisions.csv` (54 mixed and 45
homogeneous dyads) and `docs/figures/mixed_model_populations_20260918/games.csv`
(90 ladder and 45 homogeneous eight-agent runs). Provenance for the runs is in
those folders. No new runs and no API calls. Regenerate with
`python analyses/mixed_dyad_family_split.py`.

Figures:

- `2-agent-mixed-model-simulation-split.png`: per mixed pairing and task
  order, each family's per-run mean amount sent (top) and return proportion
  (bottom) as boxes, with a hollow diamond for the same family in its
  homogeneous dyad (mean ± sd).
- `dyad_family_turn_traces_sent.png`, `dyad_family_turn_traces_return.png`:
  the same split over each agent's own turns 1–5 (solid = in the mixed dyad,
  dashed = among its own kind). Each agent sends every other round and the
  first sender alternates across replicates, so the x-axis is the agent's own
  turn, not the global round; plotting by global round would place different
  replicates' first and second turns side by side.
- `mixed-model-simulation-8-agent-split.png` (sending) and
  `population_family_split_return.png`: the eight-agent ladder with the
  minority and the majority family drawn separately against the minority
  count; 0 and 8 are the homogeneous populations.

## How to read the two main figures

**`2-agent-mixed-model-simulation-split.png`.** Each panel is one mixed pairing; the x-axis is the
task order. At each x position there are two filled boxes, one per model in
the pair, coloured by model. A box shows what that model did *inside the mixed
pair*: its mean amount sent per round (top row) or its return proportion
(bottom row), one dot per run. Just outside each box is a hollow diamond in
the same colour. The diamond is what the *same model does among its own kind*
(the homogeneous September dyads, mean ± sd). Compare each box with its own
diamond: if the box sits on the diamond, the model kept its usual behaviour and
the pair's score is just the average of two fixed styles; if the box is away
from the diamond, the partner changed the model's behaviour. Example, top-left
panel, "Game only": Sonnet's diamond is at $2.5 and its box at about $1, so
Sonnet sent much less when paired with GPT; GPT's diamond and box are both at
$0, so GPT did not change. Middle panel, same position: Sonnet's box is at
$4.1 against the same $2.5 diamond, so Sonnet sent more with Gemini. Gemini's
box and diamond both sit at $5. In the bottom row nearly every box sits on its
diamond: return behaviour does not adapt.

**`mixed-model-simulation-8-agent-split.png`.** Each row is one ladder (Gemini agents
added to a GPT group, GPT agents added to a Sonnet group); each column is a
task order. The x-axis is how many agents of the added family are in the group
of eight. The two lines are the two families drawn separately, so the plot
shows what each family sends rather than the group total. The end points are
the pure groups: x = 0 is the majority family on its own and x = 8 is the
minority family on its own, so they are the "among its own kind" reference. A
flat line means the family keeps its behaviour whatever the mix; a sloping line
means it changes with the mix. Example, top-left panel: Gemini's line runs from
$0.9 when it is alone among seven GPTs up to $5 in a pure Gemini group, so
Gemini is pulled down by GPT partners; GPT's line stays at $0 until four
Geminis are present and then reaches $2, so GPT is pulled up only when the
group is half Gemini. With a myth task (middle and right panels) Gemini's line
is flat at $5 and GPT's line rises with every Gemini added.

## Result: amount sent per decision (of $5), dyads, mean (±sd over runs)

Homogeneous n = 5, mixed n = 6. "Alone" = the family's homogeneous dyad.

| Family | Task order | Alone | With Sonnet | With GPT | With Gemini |
|---|---|---:|---:|---:|---:|
| Sonnet | game | 2.54 (±0.40) | — | 1.07 (±0.68) | 4.12 (±0.41) |
| Sonnet | game→myth | 3.06 (±0.46) | — | 3.44 (±1.35) | 4.60 (±0.13) |
| Sonnet | myth→game | 3.28 (±0.82) | — | 3.42 (±0.82) | 4.84 (±0.14) |
| GPT | game | 0.00 (±0.00) | 0.33 (±0.82) | — | 0.17 (±0.41) |
| GPT | game→myth | 2.87 (±1.05) | 3.25 (±1.41) | — | 4.13 (±0.59) |
| GPT | myth→game | 3.46 (±1.18) | 3.60 (±0.99) | — | 4.72 (±0.29) |
| Gemini | game | 5.00 (±0.00) | 4.90 (±0.24) | 1.17 (±0.41) | — |
| Gemini | game→myth | 5.00 (±0.00) | 5.00 (±0.00) | 5.00 (±0.00) | — |
| Gemini | myth→game | 5.00 (±0.00) | 5.00 (±0.00) | 5.00 (±0.00) | — |

Return proportions (returned / received) stay between 0.38 and 0.50 for Sonnet
and between 0.42 and 0.47 for Gemini whatever the partner. GPT returns 0.31 to
0.33 among its own kind and 0.38 to 0.44 to a Sonnet or Gemini partner once a
myth task is present; in game-only play GPT returns almost nothing (0.02 to
0.05) and its homogeneous value is undefined because nothing was ever sent.

## Result: amount sent per decision, eight-agent ladder, mean (±sd over runs)

n = 5 runs per cell. 0 and 8 are the homogeneous September populations.

Gemini among GPT (Gemini count 0 → 1 → 2 → 4 → 8):

| Task order | Gemini sends | GPT sends |
|---|---|---|
| game | — · 0.88 (±0.27) · 1.96 (±1.49) · 3.68 (±0.17) · 5.00 (±0.00) | 0.00 (±0.00) · 0.00 (±0.00) · 0.56 (±0.62) · 2.07 (±0.93) · — |
| game→myth | — · 5.00 (±0.00) · 4.90 (±0.22) · 4.90 (±0.14) · 5.00 (±0.00) | 1.30 (±0.71) · 2.40 (±1.14) · 2.84 (±0.49) · 3.81 (±0.36) · — |
| myth→game | — · 5.00 (±0.00) · 5.00 (±0.00) · 5.00 (±0.00) · 5.00 (±0.00) | 2.00 (±0.83) · 3.16 (±0.72) · 4.32 (±0.47) · 4.54 (±0.31) · — |

GPT among Sonnet (GPT count 0 → 1 → 2 → 4 → 8):

| Task order | GPT sends | Sonnet sends |
|---|---|---|
| game | — · 3.21 (±1.08) · 1.16 (±1.22) · 1.23 (±0.96) · 0.00 (±0.00) | 3.02 (±0.10) · 2.80 (±0.20) · 2.11 (±0.45) · 1.76 (±0.72) · — |
| game→myth | — · 3.34 (±0.84) · 3.24 (±0.82) · 2.93 (±0.88) · 1.30 (±0.71) | 2.91 (±0.09) · 3.09 (±0.18) · 3.14 (±0.33) · 3.20 (±0.52) · — |
| myth→game | — · 4.76 (±0.26) · 4.35 (±0.28) · 3.88 (±0.78) · 2.00 (±0.83) | 4.37 (±0.44) · 3.90 (±0.47) · 4.35 (±0.52) · 3.81 (±0.46) · — |

## Reading

- **The mixed scores are not an average of two fixed styles.** Every family
  moves, but in different ways, so the answer to the meeting question is
  "adaptation", with the shape depending on the family.
- **Sonnet adapts to its partner in both directions.** Its sending goes from
  $2.5 alone to $1.1 against GPT and $4.1 against Gemini in game-only dyads,
  and to $4.6 to $4.8 against Gemini with a myth task. Its return proportion
  hardly moves. In the eight-agent ladder Sonnet's sending falls from $3.0 to
  $1.8 as GPT agents are added in game-only play but stays put with a myth task.
- **GPT is locked in game-only play and adapts upward once unlocked.** In
  game-only dyads it sends about $0 whatever the partner. With a myth task it
  sends more to a Gemini partner ($4.1 to $4.7) than to another GPT ($2.9 to
  $3.5), and its return proportion rises from about 0.32 to about 0.40. In the
  ladder its sending rises with every added Gemini, and with a myth task even a
  single GPT among Sonnets sends $3.3 to $4.8 against $1.3 to $2.0 among GPTs.
  The one game-only exception is the lone GPT among seven Sonnets, which sends
  $3.2 (sd 1.1); two or four GPTs fall back to about $1.2.
- **Gemini is unconditional only while reciprocated.** It sends $5 in every
  composition except game-only play against GPT. There it sends $5 on its
  first turn, gets nothing back, and sends $0 from its second turn on in five
  of six dyads; in the sixth it sends $5 twice before stopping (dyad mean
  $1.2; ladder means $0.9 to $3.7 rising with the Gemini count). Its return
  proportion never changes.
- The turn traces show when this happens: Sonnet's game-only sending against
  GPT falls from $2.8 on its first turn to about $0.6 on its third and $0 by
  its fifth; Gemini's falls to $0.8 on its second turn (the one run that sent
  twice); and GPT's climb against Gemini with a myth task reaches $5 by its
  third (myth→game) or fourth (game→myth) turn. An earlier version of this
  README read these from global-round traces ("Gemini drops at round 3"),
  which mixed replicate cohorts; corrected 2026-09-22.

## Boundaries

- Descriptive: n = 6 per mixed dyad cell, n = 5 per homogeneous and ladder
  cell. No inferential test.
- In a mixed dyad each family sends in alternate rounds, so a round trace
  averages three runs per family per round.
- Return proportions are undefined when nothing was received; those decisions
  are dropped, and the game-only GPT rows in particular rest on few decisions
  (the summary table records the run counts).
- The homogeneous references are the September reasoning-rerun controls; every
  difference between those pools and the mixed runs is declared in the two
  source folders' `provenance.json`.

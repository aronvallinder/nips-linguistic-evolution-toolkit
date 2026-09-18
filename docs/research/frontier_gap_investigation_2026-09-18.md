# Why the frontier models end with more resources than the September models

Date: 2026-09-18. Data: the 90 receipt-audited frontier finals
(`data/json/noise_experiments/frontier_rerun_20260918/`) and the 90 September
no-defector references (`negative_only_crossmodel_reasoning_rerun_20260909`),
the same 180 runs behind `docs/figures/frontier_rerun_20260918/resources_boxplots.png`.
Tables: `docs/figures/frontier_rerun_20260918/gap_decomposition/gap_decomposition.md`,
produced by `scripts/analyze_frontier_gap.py`. Five runs per cell, so everything
below is descriptive.

## Headline

The frontier models finish richer because they send more, and they send more for
three model-specific reasons: Opus 5 opens higher than Sonnet 4.5 and escalates when
a round goes well, where Sonnet holds a self-declared "50% baseline" and drifts down
with the noise; GPT-5.6 Sol opens at 2.5 to 3 and forgives apparent losses, where
GPT-5 Nano opens at 0 and locks there; the two Gemini models are both at the
ceiling. Nothing in the data points to reasoning depth as the cause: the frontier
Claude and GPT models think far less per call than their September predecessors.
The literature agrees that provider post-training and model tier, not capability or
reasoning, predict cooperation in these games.

## 1. The gap is a sending gap, exactly

In this game a dyad's total resources per round are 5 + 2 × sent, so the mean final
balance across agents is 25 + 10 × (mean send per round). That identity holds to
floating-point precision in all 180 runs (table 1). Returns only move money between
the two players of a pair; they cannot raise the population mean. So "why more
resources" is "why more sending", and returns matter only through their effect on
the partner's next send.

Mean send per round (endowment 5), game-only:

| Cell | Opus 5 | Sonnet 4.5 | Gemini 3.1 Pro | Gemini 3.7 Flash | Sol high | GPT-5 Nano |
|---|---|---|---|---|---|---|
| 2 agents | 4.28 (±0.26) | 2.54 (±0.40) | 4.88 (±0.27) | 5.00 (±0.00) | 3.20 (±1.75) | 0.00 (±0.00) |
| 8 agents | 4.34 (±0.18) | 3.02 (±0.10) | 4.97 (±0.06) | 5.00 (±0.00) | 3.81 (±1.50) | 0.00 (±0.00) |

## 2. Claude: Opus 5 leads and escalates; Sonnet 4.5 anchors on half and drifts down

**Opening.** In game-first rounds Opus 5 sends 4 in 27 of 50 round-1 decisions and 3
in the other 23. Sonnet 4.5 sends 3 in 46 of 50 (table 4). One point of the gap is
there from the first move.

**Trajectory.** Sonnet's dyads start at 3.0 and end at 2.3; Opus's start at 4.0 and end
at 4.7 (table 3). The difference is what each model does after a round that went
well. When the investor's last (communicated) payoff was above 5, Opus raises its
next send by 0.35 on average; Sonnet lowers it by 0.06 (table 6c). After a round that
looked like a loss, Opus raises by 0.90, Sonnet by 0.02. Opus treats success as a
reason to send more; Sonnet treats it as a reason to stay put.

**Same input, different output.** Partner behaviour does not explain this. In
game-only dyads, given a partner just seen to send 2 to 3, Sonnet sends 2.70 and Opus
4.25; given 3 to 4, Sonnet sends 3.00 and Opus 4.04 (table 7b). Given a fair
communicated return (45 to 55%), Sonnet sends 2.50 and Opus 4.46 (table 6b). Both
models track the partner's send (own send moves 0.5 to 0.6 per point of partner send
seen), so Sonnet is not unresponsive; its response curve just sits about 1.5 points
lower. The mixed-model dyads show the same thing from the other side: paired with a
Gemini that sends 5 every round, Sonnet sends 4.12; paired with another Sonnet it
sends 2.5. Sonnet-Sonnet pairs are two conditional cooperators matching each other's
cautious opening.

**The noise ratchet.** Negative-only noise makes every send look 0.52 lower than it
was (mean communicated minus actual, table 7 note). A model that matches what it
sees therefore drifts down unless it adds something back. Sonnet sends 0.08 less than
its partner actually sent; Opus sends 0.08 more (table 7). Over ten rounds those
small signs compound into 2.3 versus 4.7.

**Returns.** Opus returns 50% of what it receives on average and gives a fair-or-better
return 48% of the time; Sonnet returns 43% and is fair 21% of the time, and 13% of
its returns leave the investor with less than they sent (table 5). Sonnet's partner
therefore sees weaker reciprocity, which reinforces the low matched equilibrium.

**In their own words.** Sonnet's visible justifications name the policy: 40% of its
investor messages in game-only dyads say "baseline" or "moderate", 32% say "half" or
"50%", and it reads the noise-lowered numbers as "declining trust" (14%). Examples
from round 10: "I'll maintain baseline cooperation by sending $2.50 (50% of my
endowment)"; "Trust levels have been declining overall ... cooperation typically
decreases as there's less future incentive. I'll send $1.50." Opus writes prose in
only 22% of calls, but when it does, 60% of investor messages say "all in", "full
amount" or "maximize", and it attributes shortfalls to the noise: "Last round's
return was a bit under half, but noise could explain it. I'll stay cooperative";
"Trust has been rewarded both ways so far, so I'll go all in" (table 9).

**Not reasoning depth, not output format.** Sonnet used a median 444 hidden thinking
tokens per game call under its 8192 budget; Opus 5 under adaptive thinking used a
median of 0 and a mean of 31 (table 8). Sonnet wrote prose before its JSON in 100% of
calls; Opus answered with bare JSON in 78%. The September format study found that
forbidding visible prose cut Sonnet's sending by about 21 points (researchlog
2026-09-04), so if anything format worked against Opus here. The Opus advantage is a
different prior and a different update rule, not more deliberation.

## 3. GPT: Sol opens above zero and forgives; Nano opens at zero and stays

**Opening.** GPT-5 Nano sends 0 in all 50 game-first round-1 decisions. Sol sends 2.5
(25), 3 (12) or 5 (13). Nano's zero-lock is entirely an opening prior: a model that
matches its partner (Nano's own send tracks the partner's send with slope 0.7 to 0.8
in the two-task orders) and opens at zero against a copy of itself has nothing to
match but zero.

**Forgiveness.** After a communicated return below a third (the investor lost money on
the round as it appeared to them), Sol raises its next send by 0.44; Nano lowers it
by 0.58 (table 6d). Sol also returns more (36 to 40%
versus 31 to 32%) and leaves the investor at a loss in 26% of returns versus 63%.

**Sol's own weakness.** Sol is the most partner-dependent model in the set: its send
moves 1.04 per point of partner send seen, and the run-level correlation between
partner return ratio and mean send is 0.95. In 2 of 10 game-only runs its trustee
returned 15 to 28% for three rounds and the pair collapsed to zero by round 5. Sol's
gain over Nano is a higher opening and forgiveness, not a stable disposition.

## 4. Gemini: both versions at the ceiling

Gemini 3.7 Flash sends 5 in every one of its 1,500 decisions. Gemini 3.1 Pro sends
5 in all but 17 and reaches the ceiling by round 3 everywhere. There is no gap to
explain; the frontier arm is marginally lower, not higher, because of a few round-1
sends of 2 in populations and one dyad replicate that settled at 4 to 4.5.

## 5. What the literature says

The literature agent's report (2023 to 2026, about 35 sources) is summarised here;
I verified the three load-bearing papers on arXiv myself.

- **Provider post-training, not generation, predicts cooperation.** Affonso (2026,
  arXiv:2604.18596; 25 models, 38 games) finds a 48-fold spread in cooperation across
  providers, from 1.5% for GPT-5 Nano to 71.5% for Claude Opus 4.6, with OpenAI
  cooperation falling from 50.3% to 1.5% across four generations while Google's rose
  from 8.3% to 56.8%. Anthropic models cluster at 69 to 72% across four versions and
  sustain 57% cooperation even in a known final round. This independently reproduces
  our Nano zero-lock and Gemini ceiling. Vallinder and Hughes (2024, arXiv:2412.10270)
  found the same provider ordering in the donor game.
- **Tier within a provider matters.** Affonso reports Claude Haiku 4.5 at 39% against
  Sonnet and Opus at 69 to 72%, and GPT-5 Nano 1.5%, Mini 6.3%, GPT-5.4 48%. GovSim
  (Piatti et al., NeurIPS 2024, arXiv:2404.16698) found Claude 3 Opus sustaining the
  commons where Haiku and Sonnet collapsed. Our Opus-over-Sonnet and Sol-over-Nano
  gaps are tier moves as much as generation moves.
- **Reasoning is a headwind, except for Claude.** Li and Shirado (EMNLP 2025,
  arXiv:2502.17720) find reasoning models "consistently reduce cooperation and norm
  enforcement"; the agent reports the Claude 3.7 Sonnet pair as the exception (100%
  versus 96% with extended thinking). Xie et al. (NeurIPS 2024, arXiv:2402.04559)
  found chain-of-thought moved GPT-4's trust-game send by $0.02. Consistent with our
  data, where the models that think least (Opus, Sol) send most.
- **Forgiveness under noise separates families.** Akata et al. (Nature Human Behaviour
  2025) showed GPT-4 never cooperates again after one defection unless told the
  partner "sometimes makes mistakes"; Pal et al. (2026, arXiv:2601.09849) classify
  Claude Sonnet 4 as a "Forgiver" and GPT-4o as GRIM. Our informed-noise notice is the
  direct analogue, and Opus's "noise could explain it" is the forgiving reading.
- **Fixed partners unlock frontier cooperation.** CoopEval (Tewolde et al., ICML 2026,
  arXiv:2604.15267) finds recent models "consistently defect in single-shot social
  dilemmas" and that repetition-induced cooperation "deteriorates drastically when
  co-players vary". Frontier cooperativeness is conditional cooperation, which is why
  it shows in our fixed dyads and small populations with partner history.
- **Human baseline.** Johnson and Mislin's 2011 meta-analysis puts humans at about
  50% sent and 37% of the tripled amount returned. Sonnet 4.5 (51% sent, 43%
  returned) is roughly human; Opus 5 (86% sent, 50% returned) and Gemini are well
  above; Nano is below any human study.

## 6. What this does and does not establish

- The gap is a sending gap and, for Claude, a disposition gap: Opus sends more than
  Sonnet at the same partner input. That is measured, not inferred.
- Whether the disposition comes from tier (Opus versus Sonnet) or generation
  (5 versus 4.5) is not separable in this design. Affonso's Haiku gap suggests tier.
- Thinking regime changed with the model (D011). The data argue against reasoning as
  the driver, but a thinking-off Sonnet 4.5 versus Opus 5 pair would settle it.
- Five replicates per cell. Sol's 2-of-10 collapse rate is not a rate.

## 7. Cheap discriminating tests

1. Opus 5 and Sonnet 4.5 with thinking off, 2-agent game-only, n=10. If the gap
   survives, reasoning is out.
2. Add Claude Haiku 4.5 and GPT-5 Mini in the same cells. A Haiku gap of the size
   Affonso reports would reframe the finding as tier, not generation.
3. A scripted trustee returning exactly 50%, with our noise. Removes partner tracking
   and gives each model's own forgiveness curve, the quantity that separates Sonnet
   from Opus above.
4. Sonnet 4.5 with a system line that reframes the baseline ("sending the full amount
   is the cooperative default"). If Sonnet's 50% anchor is a prompt-level prior, this
   moves it; if it is post-training, it will not.

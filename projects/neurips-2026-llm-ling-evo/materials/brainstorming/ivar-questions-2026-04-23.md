# Questions for Ivar — 2026-04-23

Open `[CHECK]` markers across the manuscript that need Ivar's input before the §4 / §5 prose can be locked. Ordered roughly by how much they unblock other writing.

Suggested format for the message: paste sections as-is into Slack/email. Each numbered item is one yes-or-short-data question.

---

## Hi Ivar — quick batch of questions to unblock the writeup

I've drafted §1 and put §3/§4/§5 outlines in the new `nips-linguistic-evolution-toolkit` fork at [`projects/neurips-2026-llm-ling-evo/`](https://github.com/aronvallinder/nips-linguistic-evolution-toolkit/tree/main/projects/neurips-2026-llm-ling-evo). Bib is built (34 entries, all citations resolve), Quarto rendering works.

A few open items I need from you to lock the methods/results sections. Most are yes/no or one-number; the variance question is the load-bearing one.

### Methodological (quick confirmations)

1. **Judge model for LLM-as-judge myth similarity** — is it `meta-llama/Llama-3.3-70B-Instruct` via Together, or has it changed?
2. **Bootstrap CI procedure** — what's the standard you've been using on cell-level estimates? Number of resamples + percentile vs BCa?
3. **Final N per cell** — 10 across the board, 15 for the GPT-5-Nano negative-noise cell as the YAML suggests, or has it shifted?
4. **Asymmetric naming** — did any of the headline runs we'll report use a non-default `other_player_names` (Prometheus/Orpheus etc.), or do they all use `default`?

### Results — locked numbers needed

5. **Cross-model no-noise baselines** — locked mean cumulative reward (and across-seed dispersion) for Gemini-3.1-Pro, Claude Sonnet 4.5, and GPT-5-Nano? Specifically: does Sonnet 4.5's no-noise baseline still sit at ~82-85 like 3.5 Sonnet did in the March pilots, or has it shifted?
6. **Bidirectional ±$1 noise** — locked Claude and Gemini cumulative-reward deltas from the no-noise baseline?
7. **Negative-only ≤$5 noise** — locked Gemini and Claude numbers? Two follow-ups: do dyads recover after the apparent betrayal, or collapse to permanent defection? Does the *_informed* variant moderate the effect?
8. **Bootstrap noise on GPT-5-Nano** — final rescue magnitude? Is the "suggestive Myth→Game effect (0.41 with high variance)" from March still present, or did it wash out?

### Headline framing — the load-bearing question

9. **Across-seed variance:** in the (model × noise × task-order) cells, does the **variance across seeds drop in myth-present conditions vs game-only**? I leaned heavily on the strategy-consolidation framing in §1.2 / §1.5 / §5.2. If the variance signal is absent or weak, that framing needs to come out of the intro before submission.
10. **Order asymmetry** — does the mean myth effect differ between `game→myth` and `myth→game`? (Tests whether information flow direction matters.)

### Linguistic findings

11. **Lag-1 cross-agent cooperativity correlation** — does the Claude $r \approx 0.72$ from the pilot replicate across seeds, or was it a one-off case study? If just one or two dyads, that's still worth a small subsection but framed as such.
12. **Neologism observations** — are the "kyrexladilokrater"-style coinages still present in the final runs? Approximate count of dyads showing emergent vocabulary that propagates >2 rounds?
13. **Between-agent convergence** — does the embedding-cosine convergence pattern hold for all three models, or only some?

### Methods detail

14. **POS-pattern innovation rate** — sentence-level innovation rate is mechanically near-saturated (most sentences are unique). What's the right aggregation we're treating as the convergence vs innovation measure? I treated structural convergence and innovation as separate constructs in §3.5 and §4.4 with a methodological caveat — let me know if there's a better resolution.

---

That's it. Even partial answers to 5-9 unblock the bulk of the §4 prose; (9) on its own decides the §1 / §5 framing.

Cheers

# LLM Linguistic Evolution: Language and Cooperation in LLM Dyads

**Target**: NeurIPS 2026 (deadline early May 2026)
**Status**: Manuscript in progress; outlines for §1/§2/§4/§5, drafted prose for §3
**Lead author**: Aron Vallinder
**Collaborators**: Ivar Frisch (experiments + analysis), Edward Hughes, Mario Giulianelli, Alexandra Pafford, Arabella Sinclair

## Summary

Two LLM agents play a role-swapping repeated **trust game** (Berg, Dickhaut & McCabe 1995), optionally paired with an iterated **myth-writing** task. We test whether the linguistic exchange between agents shapes their cooperation, and how cooperation in turn shapes the linguistic content.

Three frontier models (`claude-sonnet-4.5`, `gemini-3.1-pro-preview`, `gpt-5-nano`) are crossed with four task orders ({game, myth, game→myth, myth→game}) and six noise conditions designed to break ceiling/floor lock-in (bidirectional ±$1, negative-only ≤$5, bootstrap-max-return — each in informed and uninformed variants). Behavioural measures (cumulative reward, send/return rates, across-seed variance) are paired with a battery of linguistic measures (cooperativity lexicon, LIWC pronoun ratios, sentence-embedding similarity, LLM-as-judge similarity, POS-sequence n-grams, keyword-chain neologism tracking).

## Core question

When LLM dyads talk while they cooperate, is the language *load-bearing* — does it shape the cooperation — or epiphenomenal?

## Headline findings (preliminary, all `[CHECK]`)

1. **Cross-model cooperation profiles are large and persistent.** Gemini ceilings near Pareto-optimal play; Claude sits in a middle regime; GPT-5-Nano collapses to mutual defection without intervention. The model effect dominates everything else in the design.
2. **Myth-writing has a small effect on mean cumulative reward** but a clearer effect on across-seed variance — consistent with a **strategy-consolidation** interpretation rather than a cooperation-lift one.
3. **Bidirectional channel noise** is necessary to give locked-in models room to move; without it the design has no behavioural headroom for myth effects to surface.
4. Linguistically, dyads show measurable **convergence** on word-level (cooperativity lexicon, we/I ratio) and structural (POS n-gram) measures, with occasional **emergent neologisms** that recur into the agents' game-reasoning text.

## Scope

Trust game only (not donor or public goods game). Two-agent dyads only (no population dynamics, no generational selection). Single base model per dyad. Neutral persona. Single myth topic (`anything`) for the noise experiments. T = 10 rounds. N = 10 seeds per cell (15 for the GPT-5-Nano negative-noise cell).

## Codebase

The experiment toolkit lives at the root of this repo (forked from `ivarfresh/nips-linguistic-evolution-toolkit`). Noise-experiment runner: `noise/run_noisy_batch.py`. Config: `noise/experiments_noisy.yaml`. Saved simulation states: `data/json/noise_experiments/v2/{experiment}/{model}/{task_order}/{game_params}/`.

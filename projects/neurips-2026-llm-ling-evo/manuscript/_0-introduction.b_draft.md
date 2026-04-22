# 1. Introduction

*Stage: draft (b). Format per `README.md`: one topic sentence per paragraph followed by bullets with the content for that paragraph. Target length ~1 page (~800 words). Citations in canonical `[@key]` form. `[CHECK]` markers flag claims that depend on §4 results not yet locked. Once curated, hand to `ms-writer` for prose-ification into `_0-introduction.c_final.md`.*

## 1.1 Hook — the language between LLM agents is mostly unmeasured

**¶1.** LLM agents are increasingly deployed in settings where they interact repeatedly with each other through natural language, but the literature has rarely treated that language as a first-class analytical object.

- Sketch the deployment landscape with concrete examples: assistants negotiating on behalf of users, agentic-society simulations, model-vs-model evaluation harnesses.
- Cite the canonical multi-agent LLM testbeds: [@park2023; @vezhnevets2023; @zhou2024; @abdelnabi2023].
- Frame the rest of the paragraph around the empirical fact that two-agent LLM dyads now exist at scale; what they say to each other is data we generate by the millions of tokens.

**¶2.** Existing LLM-as-agent work measures behaviour in fine detail but treats the inter-agent natural-language exchange as either instrumental scaffolding or as background noise.

- The dependent variables in nearly all this work are numeric: cooperation rates, donation amounts, payoffs.
- Cite the wave of recent papers that fit this pattern: [@akata2023; @leng2023; @fontana2024; @lore2024].
- One-sentence diagnosis: the agents are talking, but the talk is not the analysis.

**¶3.** This paper asks the substantive question that this analytical asymmetry brackets: when LLM dyads talk while they cooperate, is what they say *load-bearing* — does it shape the cooperation — or epiphenomenal?

- Single-sentence statement of the central question. Should land hard.
- No citations. The question is the paper's job, not the literature's.

## 1.2 Premise — in humans, cooperation runs on shared narrative

**¶4.** In human groups, cooperation is shaped not only by material payoffs but by shared narratives — myths, norms, stories — that act as compact, transmissible, adaptable coordination devices.

- The empirical anchor is hunter-gatherer storytelling, where storytelling correlates with and plausibly supports cooperation: [@smith2017].
- The theoretical anchor is the cultural-evolution view of the social niche: shared narratives stabilise reciprocity by aligning expectations across parties [@boyd2011].
- Position this as the broader frame the LLM literature should be aware of: machine culture is not just an artefact-transmission story but a cooperation-stabilisation story [@brinkmann2023].

**¶5.** If LLM dyads occupy the same kind of social niche where humans use narrative for coordination, the same channel — what the agents tell each other — should be a candidate causal lever in their cooperation, not a side effect to bracket out.

- This is the analogical bet that motivates the experimental probe.
- Be explicit that "narrative" doesn't have to mean "lift in mean cooperation." In humans, shared narratives often act by reducing variance — making cooperation more *predictable* — rather than raising the average. We adopt this lens up front so §5.1's "weakly load-bearing in a specific way" finding doesn't read as a bait-and-switch.
- (No new cites here; lifts and reuses the §1.2 anchors above.)

## 1.3 Gap — three relevant literatures, none in conversation with the others

**¶6.** Three literatures together cover the components of our question, but none of them combines all of them.

- LLM-cooperation-game work measures behaviour but does not pair it with controlled linguistic interaction [@akata2023; @leng2023; @vallinder2024; @piatti2024].
- LLM cultural-evolution work tracks artefact transmission across chains and generations but typically without a payoff-coupled task running underneath [@perez2024; @acerbi2023].
- Iterated-learning experiments give us the language-evolution methodology, but in trivial referential games and with humans, not LLMs [@kirby2008; @tamariz2016; @raviv2019].
- The closest existing system is CICERO [@bakhtin2022], which bundles language and game into a single end-to-end agent — designed to win Diplomacy, not to *isolate* the causal contribution of language. The intersection — *iterated linguistic transmission inside a repeated economic game with LLM agents* — is where this paper sits.

## 1.4 Approach — one paradigm, three knobs

**¶7.** Two same-base-model LLM agents play a role-swapping repeated Trust Game, optionally paired with an iterated myth-writing task in the form of a transmission chain inside a single dyad.

- Trust game from [@berg1995], with role-swapping every round so cumulative scores reflect both roles.
- Myth-writing chain modelled on [@kirby2008] iterated learning, executed in the LLM-agent style of [@frisch2024].
- One sentence on why myth specifically (vs free chat or strategy verbalisation): myths are short, narrative, value-laden, and explicitly transmissible — a clean experimental probe for what content a partner takes from the previous turn. Forward-link to §3.3.

**¶8.** We cross three factors that probe the paper's question from independent directions: task order, noise on the action channel, and base model.

- Task order ∈ {game, myth, game→myth, myth→game}: isolates within-task baselines and tests cross-task influence in both directions.
- Noise condition ∈ {none, bidirectional ±$1, negative-only ≤$5, bootstrap-max-return}, each in informed and uninformed variants. The noise mechanisms are not the substantive variable; they are the methodological lever that breaks ceiling/floor lock-in (§3.4 explains).
- Models: `claude-sonnet-4.5`, `gemini-3.1-pro-preview`, `gpt-5-nano`. Picked to span a sociality spectrum that, as it turns out, is the dominant axis of variation in the design.

**¶9.** Behavioural measurement is paired with a battery of linguistic measures targeting both content and form, each tied to a specific failure mode of dyadic coordination.

- Behavioural: cumulative reward, send/return rates, across-seed variance.
- Linguistic content: cooperativity lexicon, LIWC pronoun ratios (we/I), keyword-chain neologism tracking.
- Linguistic form: sentence-embedding cosine, LLM-as-judge similarity, POS-sequence n-grams.
- The two-axis structure (content × form) lets us detect convergence (myths becoming more alike) and drift / innovation (myths departing from baseline together) as separate phenomena.

## 1.5 Contribution and findings preview

**¶10.** *Methodological:* a controlled paradigm and open toolkit for crossing iterated linguistic interaction with repeated economic games, agnostic to the specific game.

- Toolkit at [github.com/aronvallinder/nips-linguistic-evolution-toolkit](https://github.com/aronvallinder/nips-linguistic-evolution-toolkit) (forked from `ivarfresh/nips-linguistic-evolution-toolkit`).
- Single config-driven engine, canonical per-run JSON, three-stage manuscript pipeline. Forward-link to §3.7–§3.8.

**¶11.** *Empirical:* three findings, in decreasing order of robustness. **All three need final-result confirmation against §4 before submission — placeholders below `[CHECK]`.**

- (i) Cross-model cooperation profiles are robust and large: Gemini ceilings near Pareto-optimal play; Claude sits in the middle; GPT-5-Nano collapses to mutual defection without intervention. The model effect dominates everything else in the design — comparable in magnitude to persona manipulations reported elsewhere [@fontana2024; @serapio2023]. `[CHECK]`
- (ii) Myth-writing produces a small and inconsistent effect on mean cumulative reward but a more consistent effect on across-seed variance — consistent with a *strategy-consolidation* interpretation rather than a cooperation-lift interpretation. The variance signature is the more substantive finding. `[CHECK — depends on Ivar's variance analysis]`
- (iii) Bidirectional channel noise is necessary to give locked-in models room to move; without it, the design has no behavioural headroom and any cross-task or framing manipulation is mechanically invisible. The noise condition is a methodological precondition for finding (ii), not an independent finding.
- A fourth, more descriptive observation: dyads show measurable linguistic convergence on both word-level (cooperativity lexicon, we/I ratio) and structural (POS n-gram) measures, with occasional emergent neologisms (e.g., the "kyrexladilokrater"-style coinages observed in pilot runs) that recur into game-reasoning text. `[CHECK]`

**¶12.** *Theoretical:* the paper relates these findings to two literatures — the cultural-evolution literature on shared-narrative coordination, and the iterated-learning paradigm — but with calibrated claims about the scope.

- We adopt the iterated-learning paradigm as a *methodological* template (round-by-round transmission with adaptation pressure) rather than as a predictive theory. Our 10-round, 2-agent, single-generation design does not test the long-horizon Kirby-style predictions of compression and structural emergence; we say so explicitly.
- The contribution to the cultural-evolution literature is empirical: a controlled measurement of how strong the language → cooperation channel is when the experimental design isn't structured to maximise it.

## 1.6 Roadmap

**¶13.** §2 positions the paper at the intersection of three literatures (LLM agents in cooperation games, machine culture and iterated learning, narrative-and-cooperation in humans). §3 specifies the paradigm, conditions, and measures. §4 reports the findings, organised by measure family. §5 discusses what we found, what we didn't, what the strategy-consolidation framing implies for follow-up work, and the limitations of the design.

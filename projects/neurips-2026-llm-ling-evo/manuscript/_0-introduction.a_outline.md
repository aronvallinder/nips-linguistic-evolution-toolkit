# 1. Introduction

*Outline — bullet-level scaffolding. Each bullet ≈ one paragraph in the final draft. `[@authorYYYY]` markers correspond to entries in `references/bib/`; `[CHECK]` flags claims that depend on results not yet finalised.*

**1.1 Hook — LLM agents talk to each other, and we mostly ignore what they say.**

- Frame the rapid expansion of multi-agent LLM deployments (assistants negotiating on behalf of users, agentic-society sims, model-vs-model evaluation) — a setting where pairs of LLMs interact repeatedly via natural language. `[CITE: Park et al. 2023; Vezhnevets et al. 2023 (Concordia); Zhou et al. 2024 (SOTOPIA); Abdelnabi et al. 2023]`
- Note the analytical asymmetry in the existing literature: behavioural outcomes (donations, cooperation rates, payoffs) are the dependent variable; the natural-language exchange between agents is treated either as instrumental scaffolding or as background. `[CITE: Akata et al. 2023; Leng & Yuan 2023; Fontana et al. 2024; Lorè & Heydari 2024]`
- Pose the substantive question: when LLM dyads talk while they cooperate, is what they say *load-bearing* — does it shape the cooperation — or epiphenomenal?

**1.2 Premise — in humans, cooperation runs on shared narrative, not just payoffs.**

- Sketch the cultural-evolution view: norms, myths, and shared stories are coordination devices — compact, transmissible, and adaptable units that align expectations and stabilise cooperation in the absence of explicit contracts. `[CITE: Smith et al. 2017 (Nat Commun, hunter-gatherer storytelling); Boyd, Richerson & Henrich 2011; Brinkmann et al. 2023 (Nat Hum Behav, "Machine Culture")]`
- Make the analogical bet explicit: if LLMs increasingly occupy the social niche where humans rely on narrative for coordination, the same channel — *what they tell each other* — should be a candidate causal lever in their cooperation, not just a side effect. (One-sentence framing of the paper's central thesis.)
- Flag the *strategy-consolidation* angle (this paper's variant of a broader "narrative reduces variance more than mean" pattern): one role for myth-writing in a dyad may be to lock in a shared frame and reduce across-seed variance, rather than to lift mean cooperation. We adopt this lens for interpreting null-on-the-mean / signal-on-the-variance results. `[CHECK — confirm framing once Ivar's variance results are finalised]`

**1.3 Gap — three relevant literatures, none of which talks to the others.**

- LLM-cooperation-game work measures behaviour but does not pair it with controlled linguistic interaction. `[CITE: Akata et al. 2023; Leng & Yuan 2023; Vallinder & Hughes 2024; Piatti et al. 2024 (GovSim)]`
- LLM cultural-evolution work tracks artefact transmission across chains/generations but typically without a payoff-coupled task running underneath. `[CITE: Perez et al. 2024; Acerbi & Stubbersfield 2023]`
- Iterated-learning experiments give us the language-evolution methodology, but in trivial referential games and with humans, not LLMs. `[CITE: Kirby et al. 2008, 2015; Tamariz & Kirby 2016; Raviv et al. 2019]`
- CICERO bundles language and game but as a single end-to-end agent, not as a controlled manipulation isolating language's role. `[CITE: Bakhtin et al. / Meta CICERO 2022]`
- The intersection — *iterated linguistic transmission inside a repeated economic game with LLM agents* — is where this paper sits.

**1.4 Approach — one paradigm, three knobs.**

- Two same-base-model LLM agents play a role-swapping repeated Trust Game `[CITE: Berg, Dickhaut & McCabe 1995]`, optionally paired with an iterated myth-writing task in the spirit of `[CITE: Kirby et al. 2008]` and `[CITE: Frisch & Giulianelli 2024]`.
- Crossed factors: task order ({game, myth, game→myth, myth→game}), noise on the action channel ({none, bidirectional ±$1, negative-only $\le$5, bootstrap-max-return}, each in informed and uninformed variants), and model (`claude-sonnet-4.5`, `gemini-3.1-pro-preview`, `gpt-5-nano`).
- Behavioural measures (cumulative reward, send/return rates, across-seed variance) plus a battery of linguistic measures targeting both *content* (cooperativity lexicon, LIWC pronoun ratios, keyword-chain neologism tracking) and *form* (sentence-embedding cosine, LLM-as-judge similarity, POS-sequence n-grams). The linguistic measures are designed to detect both *convergence* (myths becoming more alike) and *drift / innovation* (myths departing from baseline together).
- Headline implementation point: a single config-driven simulation engine that produces a canonical per-run JSON, so each cell of the design is independently re-analysable. (Forward-pointer to §3.7–3.8.)

**1.5 Contribution and findings preview.**

- *Methodological:* a controlled paradigm and open toolkit `[CITE: github.com/aronvallinder/nips-linguistic-evolution-toolkit (fork of ivarfresh/nips-linguistic-evolution-toolkit)]` for crossing iterated linguistic interaction with repeated economic games, agnostic to the specific game.
- *Empirical (preview, all `[CHECK]`):*
    - Cross-model cooperation profiles are robust and large: Gemini ceilings near Pareto-optimal play; Claude sits in the middle; GPT-5-Nano collapses to mutual defection without a noise-bootstrap. `[CITE: own results]`
    - Myth-writing produces detectable but small effects on cumulative reward — too small to be the headline. The clearer signal is in *strategy consolidation* (across-seed variance reduction) rather than mean lift.
    - Bidirectional channel noise is necessary to give locked-in models room to move; without it, the design has no headroom and myth effects are mechanically invisible.
    - Linguistically, dyads show measurable convergence on both word-level (cooperativity lexicon, we/I ratio) and structural (POS n-gram) measures, with occasional emergent neologisms (e.g., the "kyrexladilokrater"-style coinages) that recur into game-reasoning text. `[CITE: own pilot]`
- *Theoretical:* relate findings to the cultural-evolution literature on shared-narrative coordination, and to the iterated-learning paradigm as a *methodological* template (round-by-round transmission with adaptation pressure) — without claiming our short-horizon dyadic setup tests the long-horizon Kirby-style predictions of compression and structure emergence.

**1.6 Roadmap.** One sentence pointing to §2 (background), §3 (methods), §4 (results), §5 (discussion).

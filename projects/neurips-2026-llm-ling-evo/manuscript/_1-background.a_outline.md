# 2. Background

*Outline — four subsections. Each is a self-contained paragraph or two in the final draft. The intent is to position the paper at the intersection of three literatures rather than to survey any one of them exhaustively.*

## 2.1 LLM agents in cooperation games

- The wave of "LLMs as economic / game-theoretic subjects" work over 2023–2025: setup, scope, and recurring findings. [@horton2023; @aher2023; @akata2023; @lore2024; @fontana2024; @leng2023]
- Key recurring observations to position against: (i) LLMs cooperate above the human baseline in single-shot prisoner's dilemmas and trust games but show distinctive failure modes in coordination tasks; (ii) cooperation is highly model-dependent and prompt-sensitive; (iii) framing manipulations (persona, social context) move behaviour reliably. [@akata2023; @fontana2024; @serapio2023]
- Population-level / sustained-cooperation work: Vallinder & Hughes's donor-game-with-selection paradigm [@vallinder2024], Piatti et al.'s commons game [@piatti2024], and the Diplomacy / CICERO line as the high-water mark for natural-language-mediated cooperation in AI [@bakhtin2022].
- The shared limitation we lean on: in nearly all of this work, the dependent variable is numeric (donation amount, cooperation rate, payoff). What the agents *say* to each other is either absent (no chat channel) or present but un-analysed. Our paper's contribution starts here — making the linguistic exchange a first-class measurement target.

## 2.2 Cultural evolution and iterated learning in artificial agents

- The "machine culture" agenda: LLM populations as systems where transmission, drift, and selection apply to artefacts that humans recognise as cultural. [@brinkmann2023; @perez2024]
- Direct precedents: transmission-chain experiments with LLMs reproduce human content biases [@acerbi2023]; populations of LLMs exhibit cultural-evolution-like dynamics over generations [@perez2024]; Vallinder & Hughes show cultural evolution of *cooperation* itself in donor-game populations [@vallinder2024].
- The human-experimental analogue: iterated-learning paradigms have shown that cumulative cultural transmission, under a learnability bottleneck, produces compositional structure and compression — not just convergence. [@kirby2008; @kirby2015; @tamariz2016; @raviv2019]
- Adjacent prior art in RL emergent communication: agents trained in coordination games invent communication systems whose properties depend on population size, channel structure, and grounding. Two takeaways we use: (i) language doesn't emerge "naturally" without the right pressures [@kottur2017]; (ii) population-scale dynamics produce qualitatively different convergence regimes [@lazaridou2020; @chaabouni2022; @galke2022].
- Positioning of *this* paper against §2.2: the LLM substrate gives us natural language for free, so the question is no longer *whether* communication emerges but whether — and through which features — it carries causal weight on cooperation. We adopt the iterated-learning paradigm's *form* (round-by-round transmission with adaptation pressure) but apply it inside a payoff-bearing game.

## 2.3 Narrative, myth, and cooperation in humans

- The empirical anchor: storytelling correlates with — and plausibly supports — cooperation in small-scale human societies. [@smith2017]
- The theoretical anchor: cultural-evolution accounts treat shared narratives as compressed carriers of behavioural prescriptions — coordination devices that align expectations and stabilise reciprocity, observable to all parties and adaptable across iterations. [@boyd2011] [TODO_CITE: Henrich 2016 (book) — optional]
- Why "myth" specifically (rather than e.g. dialogue or strategy verbalisation): myths are short, narrative, value-laden, and explicitly transmissible — they compress a moral stance into a unit a partner can recognise, internalise, and rewrite. This makes them an unusually clean experimental probe for the *content* a partner takes from your previous turn. (Forward-link this to the prompt design in §3.3.)
- Caveat to flag explicitly: the human evidence is correlational and small-N; we are not claiming LLMs reproduce the same mechanism, only that the human regularity motivates the experimental probe.

## 2.4 Measuring linguistic convergence and drift

- Three families of measures we draw on, with the canonical citations and their known limitations:
    - *Lexical / dictionary-based.* Cooperativity word lists, LIWC pronoun categories (notably the *we/I* ratio as a proxy for group-identity framing). [@tausczik2010] [TODO_CITE: Boyd et al. 2022 (LIWC-22) if used] Limitations: no negation handling, no stemming, dictionary coverage gaps — flag these in §3.5 not here.
    - *Distributional / embedding-based.* Sentence-embedding cosine similarity for cross-myth comparison; LLM-as-judge for thematic and structural similarity at higher abstraction levels. [@reimers2019] [TODO_CITE: ?LLM-as-judge methods reference]
    - *Structural / sequence-based.* POS-sequence n-grams and per-sentence innovation rates as a probe for syntactic drift / structural convergence. [@kutuzov2018; @tahmasebi2021]
- Closest methodological precedent in the LLM-agent literature: Frisch & Giulianelli's work on iterated LLM interaction provides our direct template for how to extract and compare interaction-level linguistic outputs. [@frisch2024]
- One unresolved measurement question to pre-register in the discussion: at the sentence level, POS-pattern innovation rate is mechanically near-saturated (most sentences are unique); we therefore treat structural convergence and innovation as two separate constructs measured with different aggregations. (Forward-link to the open question raised in the project notes about whether high innovation rate is meaningful or an artefact of sentence length.) `[CHECK — discuss with Ivar before locking the measure]`

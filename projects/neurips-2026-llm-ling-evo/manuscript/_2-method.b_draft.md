# 3. Methods

*Drafted prose. Length-pass version: ~1.1K words in body. Parameters flagged `[CHECK]` need final confirmation against Ivar's analyses.*

## 3.1 Overview

Two LLM agents interact over repeated rounds of a **Trust (Investment) Game** [@berg1995], optionally paired with a **myth-writing task**. Each experimental run fixes a (model, persona, task-order, noise-condition) tuple and produces a canonical simulation-state JSON logging every agent turn, action, payoff, and generated text. All experiments are configuration-driven via a single YAML file, so each condition corresponds to a named `experiment_set` and is reproducible from the saved state.

## 3.2 Game

We use a role-swapping repeated Trust Game with endowment $E = \$5$ and multiplier $m = 3$. Each round $t \in \{1, \dots, T\}$ has two sequential moves: the **investor** chooses $s_t \in [0, E]$ to send to the **trustee**, who receives $m \cdot s_t$ and chooses $r_t \in [0, m \cdot s_t]$ to return. Per-round payoffs are $\pi^{I}_t = E - s_t + r_t$ and $\pi^{T}_t = m s_t - r_t$, computed from the agents' actual choices. **Roles alternate every round** so cumulative balances $B^{I}_T$, $B^{T}_T$ reflect behaviour in both roles.

Agents receive the game rules in a system prompt (both roles, payoff formulas, response schema) drawn from a single YAML template. On round 1 the investor sees only the rules; from round 2 each agent is shown the previous round's $s$ and $r$, derived percentages, its own per-round payoff, and its own *perceived* cumulative balance — perceived because under noise (§3.4) the figure shown is the *communicated* balance, accumulated from values reported turn by turn, which can drift from the ground-truth balance used for analysis. Memory truncation in the agent's message buffer (`memory_capacity = 3`) gives a memory-1 observability of game state. Responses are regex-extracted from a `{'send': <amount>}` or `{'return': <amount>}` JSON payload; malformed responses abort the run rather than being silently coerced. Default run length in the noise-condition experiments is $T = 10$.

## 3.3 Myth-writing task

In myth conditions each round contains a creative-writing turn in which each agent writes a 200-word myth. The round-1 prompt is minimal: `Write a myth about {myth_topic}. Write 200 words.`, with `myth_topic` configurable per run from a fixed inventory — `anything` (unconstrained), `the rise and spread of moralizing supernatural agents`, and `a trickster who exploits others and the price that follows`; all noise-condition runs reported here use `anything`, so the myth content is endogenously chosen rather than thematically primed. From round 2 onward, the prompt includes both the agent's own previous myth and the partner's previous myth, with the instruction to "use your previous myth as inspiration, but adapt it in your own way." This yields an **iterated-learning-style transmission chain** [@kirby2008] inside the dyad.

The game and myth tasks share an agent's message buffer but interact only through it: the trust-game prompts (§3.2) do not directly inject the partner's myth as game context. Cross-task influence on game play therefore flows through (i) the agent's own previously-written myth, which sits in its context window when it next plays the game, and (ii) the partner's previous myth, which the agent has seen quoted inside its *own* round-$\geq\!2$ myth-writing prompt.

## 3.4 Experimental conditions

Conditions cross task order, noise on the inter-agent action channel, persona, and base model. A guiding principle for the noise designs is **asymmetric perspective**: each agent sees ground-truth information about its *own* actions but potentially noised information about the *other* agent's reported choices. Payoff bookkeeping uses actual amounts; only the inter-agent signal is corrupted. The simulation maintains parallel ledgers of actual and communicated balances, which diverge over noisy rounds.

**Task order** $\in \{\text{game},\ \text{myth},\ \text{game} \to \text{myth},\ \text{myth} \to \text{game}\}$. The first two are baselines isolating each task; the ordered conditions test cross-task influence in both directions.

**Noise condition** comprises six configured presets pairing three mechanisms with informed / uninformed variants:

- *No-noise.* Communicated amounts equal actual amounts. Baseline.
- *Bidirectional uniform $\pm\$1$.* The values of *sent* shown to the trustee and *returned* shown to the investor each receive an additive perturbation drawn independently from $\mathcal{U}(-1, +1)$ (clamped to the action's valid range). Designed to perturb ceiling- or floor-locked dyads without changing expected payoffs.
- *Negative-only $\le \$5$.* The perturbation is drawn from $\mathcal{U}(-5, 0)$ — the partner appears systematically *less* generous than they were. Targets ceiling-locked models by introducing apparent betrayal.
- *Bootstrap.* The trustee's reported return is replaced with its maximum every round, manufacturing apparent reciprocation. Targets floor-locked models.

In each *_informed* variant a single sentence is appended to the system prompt flagging the noise.

**Persona** $\in \{\text{neutral, altruistic, selfish}\}$, injected as a one-sentence addition to the system prompt. All noise-condition runs reported here use *neutral*.

**Model.** Agents in a dyad share a base model: Anthropic `claude-sonnet-4.5`, Google `gemini-3.1-pro-preview`, and OpenAI `gpt-5-nano`, chosen to span an apparent sociality spectrum. Earlier non-noise pilots covering Llama-3.1-8B-Instruct, GPT-4o, Claude Haiku, and DeepSeek-V3 are reported in Appendix B. A separate framing manipulation (`other_player_names`, swapping the partner's role label for a mythological name) is implemented but not used in the headline runs reported here `[CHECK]`.

Each cell is run with $N = 10$ independent seeds (15 for the GPT-5-Nano negative-noise cell); all runs use temperature $0.8$, `memory_capacity = 3`, and identical prompt templates from a single YAML config.

## 3.5 Measures

**Behavioural.** Per-round $s_t$, $r_t$, role-specific payoffs, and cumulative balances. Summary statistics: mean send rate, mean return rate, cumulative reward by role, and across-seed variance. Condition contrasts are computed as **differences of medians** across seeds, to avoid averaging over qualitatively different trajectories (lock-in vs. oscillation) that share the same mean.

**Linguistic.** For each myth we compute six families of measures: (i) **cooperativity word counts** from a hand-curated lexicon (dictionary-based, no negation handling, no stemming); (ii) **LIWC pronoun ratios** — the *we/I* ratio $W / (I + 1)$ and the we-proportion $W / (I + W + Y + T)$, as coarse proxies for group-identity framing [@tausczik2010]; (iii) **pairwise myth similarity** via sentence-embedding cosine using `all-mpnet-base-v2` [@reimers2019] and LLM-as-judge on five dimensions averaged (Llama-3.3-70B via Together API `[CHECK]`); (iv) **structural / n-gram measures** — POS-sequence n-gram distributions, per-sentence innovation rate, and distributional entropy via spaCy; (v) **keyword chain evolution** — per-round top-$k$ keyword extraction tracking emergent vocabulary and neologisms; (vi) **lag correlation** — Pearson $r$ between Agent A's cooperativity score at round $t$ and Agent B's at round $t+1$, indexing mimicry. Similarity measures (iii) are applied both within-agent across rounds (drift) and between-agent within a round (convergence).

## 3.6 Statistical inference

Within each (model × noise × task-order) cell we compare game-only, myth→game, and game→myth task orderings on (i) cumulative reward and (ii) linguistic convergence. Our pre-specified primary contrast is the **median delta in cumulative reward between myth-present and game-only conditions**, computed within each noise condition. We also report variance across seeds as a second-order outcome, since one hypothesis for the role of myth is *strategy consolidation* (lower across-seed variance) rather than *cooperation lift* (higher mean). Non-parametric bootstrap confidence intervals are reported on cell-level estimates `[CHECK — confirm bootstrap procedure with Ivar]`.

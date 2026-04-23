# 3. Methods

## 3.1 Overview

Two LLM agents interact over repeated rounds of a **Trust (Investment) Game** [@berg1995], optionally paired with a **myth-writing task**. Each experimental run fixes a (model, task-order, noise-condition) tuple. Three further axes — persona, myth topic, and a partner-naming framing — are implemented in the framework but held fixed for the runs reported here.

The headline question is whether adding the myth-writing task changes the *level* of cooperation in the trust game (a **cooperation-lift** hypothesis) or its *across-seed variance* (a **strategy-consolidation** hypothesis). Both predictions are tested against the same primary contrast (§3.5), but on different moments of the cell-level distribution.

## 3.2 Game

We use a role-swapping repeated Trust Game with endowment $E = \$5$ and multiplier $m = 3$. Each round $t \in \{1, \dots, T\}$ has two sequential moves: the **investor** chooses $s_t \in [0, E]$ to send to the **trustee**, who receives $m \cdot s_t$ and chooses $r_t \in [0, m \cdot s_t]$ to return. Per-round payoffs are $\pi^{I}_t = E - s_t + r_t$ and $\pi^{T}_t = m s_t - r_t$, computed from the agents' actual choices. **Roles alternate every round**, so cumulative balances $B^{I}_T$ and $B^{T}_T$ reflect behaviour in both roles.

Agents receive the game rules in a system prompt covering both roles and the payoff formulas. On round 1 the investor sees only the rules; from round 2 each agent is shown the previous round's $s$ and $r$, derived percentages, its own per-round payoff, and its own *perceived* cumulative balance. The balance is perceived because under noise (§3.4) the figure shown is the *communicated* balance, accumulated from values reported turn by turn, which can drift from the ground-truth balance used for analysis. Each agent's memory horizon is three exchanges: the previous three rounds in game-only conditions, or roughly the previous 1.5 rounds when game and myth alternate. Malformed responses abort the run rather than being silently coerced. Default run length in the noise-condition experiments is $T = 10$.

## 3.3 Myth-writing task

In myth conditions each round contains a creative-writing turn in which each agent writes a 200-word myth. The round-1 prompt is minimal — "Write a myth about [topic]. Write 200 words." — with the topic drawn from a fixed inventory: *anything* (unconstrained), *the rise and spread of moralizing supernatural agents*, and *a trickster who exploits others and the price that follows*. All noise-condition runs reported here use *anything*, so myth content is endogenously chosen rather than thematically primed. From round 2 onward, the prompt includes both the agent's own previous myth and the partner's previous myth, with the instruction to "use your previous myth as inspiration, but adapt it in your own way." This yields an **iterated-learning-style transmission chain** [@kirby2008] inside the dyad.

**Cross-task coupling.** The game and myth tasks share an agent's message buffer but interact only through it: the trust-game prompts (§3.2) do not directly inject the partner's myth as game context. Cross-task influence on game play therefore flows through two routes: (i) the agent's own previously-written myth, which sits in its context window when it next plays the game, and (ii) the partner's previous myth, which the agent has seen quoted inside its *own* round-$\geq\!2$ myth-writing prompt.

## 3.4 Experimental conditions

Conditions cross task order, noise on the inter-agent action channel, and base model. We introduce noise because the no-noise game tends to lock at ceiling or floor in frontier models, leaving no behavioural headroom for cross-task effects to surface; targeted perturbations create that headroom (rationale developed in §4.2). A guiding principle for the noise designs is **asymmetric perspective**: each agent sees ground-truth information about its *own* actions but potentially noised information about the *other* agent's reported choices. Payoff bookkeeping uses actual amounts; only the inter-agent signal is corrupted, and the simulation maintains parallel ledgers of actual and communicated balances that diverge over noisy rounds. Actions are real-valued in $[0, E]$ and noise perturbations are drawn from continuous uniform distributions; communicated amounts are rounded to two decimal places for display, while ground-truth bookkeeping uses unrounded values.

**Task order** $\in \{\text{game},\ \text{myth},\ \text{game} \to \text{myth},\ \text{myth} \to \text{game}\}$. Game-only and myth-only are single-task baselines; the ordered conditions test cross-task influence in both directions. Myth-only contributes only to the linguistic measures, since it has no game data; the behavioural primary contrast (§3.5) uses the three game-containing cells.

**Noise condition** comprises three mechanisms, each in informed and uninformed variants, plus a no-noise baseline:

- *No-noise.* Communicated amounts equal actual amounts. Baseline.
- *Bidirectional uniform $\pm\$1$.* The values of *sent* shown to the trustee and *returned* shown to the investor each receive an additive perturbation drawn independently from $\mathcal{U}(-1, +1)$ (clamped to the action's valid range). Designed to perturb ceiling- or floor-locked dyads without changing expected payoffs.
- *Negative-only $\le \$5$.* The perturbation is drawn from $\mathcal{U}(-5, 0)$, so the partner appears systematically *less* generous than they were. Targets ceiling-locked models by introducing apparent betrayal.
- *Bootstrap.* The trustee's reported return is replaced with its maximum every round, manufacturing apparent reciprocation. Targets floor-locked models.

In informed variants a single sentence is appended to the system prompt flagging the noise. `[CHECK — enumerate the full preset set explicitly: the no-noise baseline plus each of the three mechanisms above paired with its informed and uninformed variant.]`

**Model.** Agents in a dyad share a base model: Anthropic `claude-sonnet-4.5`, Google `gemini-3.1-pro-preview`, and OpenAI `gpt-5-nano`, chosen to span an apparent sociality spectrum [@fontana2024; @serapio2023; @leng2023]. Earlier non-noise pilots covering Llama-3.1-8B-Instruct, GPT-4o, Claude Haiku, and DeepSeek-V3 are reported in Appendix B.

Each cell is run with $N = 10$ independent seeds (15 for the GPT-5-Nano negative-noise cell `[CHECK — confirm and justify the seed-count exception]`) at temperature $0.8$. A separate framing manipulation, swapping the partner's role label for a mythological name, is implemented but not used in the headline runs reported here `[CHECK]`.

## 3.5 Measures

**Behavioural.** Per-round $s_t$, $r_t$, role-specific payoffs, and cumulative balances. Summary statistics: mean send rate, mean return rate, cumulative reward by role, and across-seed variance. Condition contrasts are computed as **differences of medians** across seeds, to avoid averaging over qualitatively different trajectories (lock-in vs. oscillation) that share the same mean.

**Linguistic.** For each myth we compute six families of measures:

- **Cooperativity word counts** from a hand-curated lexicon (dictionary-based, no negation handling, no stemming).
- **LIWC pronoun ratios** — the *we/I* ratio $W / (I + 1)$ and the we-proportion $W / (I + W + Y + T)$, as coarse proxies for group-identity framing [@tausczik2010].
- **Pairwise myth similarity** via sentence-embedding cosine using `all-mpnet-base-v2` [@reimers2019] and LLM-as-judge on five dimensions averaged (Llama-3.3-70B `[CHECK]`); applied both within-agent across rounds (drift) and between-agent within a round (convergence).
- **Structural / n-gram measures** — POS-sequence n-gram distributions, per-sentence innovation rate, and distributional entropy.
- **Keyword chain evolution** — per-round top-$k$ keyword extraction tracking emergent vocabulary and neologisms.
- **Lag correlation** — Pearson $r$ between Agent A's per-round myth cooperativity score at round $t$ and Agent B's at round $t+1$, computed across the $T-1$ paired observations within a dyad and aggregated by model; indexes mimicry within the myth chain.

Our pre-specified primary contrast is the **median delta in cumulative reward between myth-present and game-only conditions**, computed within each (model × noise) cell, with across-seed variance reported as a second-order outcome; the *strategy consolidation* hypothesis predicts variance reduction without a mean shift. Cell-level estimates are reported with non-parametric bootstrap confidence intervals `[CHECK — confirm bootstrap procedure with Ivar]`.

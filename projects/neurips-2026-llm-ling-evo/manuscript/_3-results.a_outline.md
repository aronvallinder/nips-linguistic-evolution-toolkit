# 4. Results

*Outline — five subsections mirroring §3.5's measure structure. Each cell-level number cited below is a placeholder grounded in the project's interim findings (MEMORY.md, meeting notes); replace with the locked analysis JSONs before prose-ification. `[CHECK]` flags estimates that need confirmation against Ivar's final cell-level statistics.*

## 4.1 Cross-model behavioural baselines (no-noise)

- *Headline:* the three frontier models occupy qualitatively different regimes in the no-noise repeated trust game, and these regimes are stable across seeds. This single fact dominates the design and motivates everything that follows.
- *What to show:*
    - Mean cumulative reward per agent across $T = 10$ rounds, broken down by model, with across-seed dispersion. `[CHECK — pull final numbers from data/json/noise_experiments/v2/.../default/]`
    - Per-round trajectories of $s_t$ and $r_t$ (one panel per model), so the lock-in patterns are visible.
- *Expected pattern (per project notes):*
    - `gemini-3.1-pro-preview`: ceiling-locked near Pareto-optimal cooperation; trustees rapidly learn to return close to the maximum, investors send near $E$. Across-seed variance low.
    - `claude-sonnet-4.5`: middle regime; high cooperation but not ceiling. `[CHECK — confirm Sonnet 4.5 baseline ≈ same as 3.5 Sonnet's ~82–85 cumulative observed in March pilots]`
    - `gpt-5-nano`: floor-locked at mutual defection; cumulative reward at or near the no-trade outcome of $E \cdot T$ per agent.
- *Interpretation paragraph:* model-level "cooperation profile" is large and persistent — comparable in magnitude to the persona manipulations reported elsewhere. Cite the cross-model variation literature for context. [@fontana2024; @serapio2023; @leng2023]
- *Why this matters for the rest of the paper:* both ceiling-locking (Gemini, Claude) and floor-locking (Nano) leave the game with no behavioural headroom for any other manipulation — including myth — to surface. §4.2 addresses this directly.

## 4.2 Effect of noise on the cooperation profile

- *Headline:* targeted noise injections create the headroom that the no-noise design lacks. The noise mechanisms aren't the substantive finding; they're the methodological lever that lets the substantive findings exist.
- *What to show, per noise mechanism:*
    - **Bidirectional ±$1 (`noisy_bidirectional`).** Cumulative-reward deltas vs no-noise baseline, by model. Expected: ceiling-locked models drop into the moderate-cooperation regime (project notes: Claude ~82–85 → ~62–65 with bidirectional ±$1; Gemini ceiling barely budged because ±$1 is small relative to its ~$5 endowment) `[CHECK]`. Across-seed variance increases.
    - **Negative-only $\le 5$ (`noisy_negative_5`).** Stronger downward pressure on perceived partner generosity. Expected: meaningful cooperation drop in both Gemini and Claude. Two questions: (i) does the dyad recover (apparent betrayal forgiven) or collapse (permanent defection); (ii) does informedness moderate this. `[CHECK — pending the noise_negative_mem3 results for gemini_3_1_pro and claude_sonnet_45]`
    - **Bootstrap (`noisy_bootstrap_cooperation`).** Specifically targets GPT-5-Nano's floor-lock by reporting full-reciprocation. Expected: investors sustain higher sending; some level of cooperation visible where no-noise produced none. Magnitude of the rescue effect TBD `[CHECK — noise_bootstrap_mem3 results]`.
- *Informed vs uninformed contrast:* across all three mechanisms, do agents told the channel is noisy ("can you filter out the noise?") behave differently from uninformed agents in the same noise regime? Two reasonable predictions: (i) informed agents discount perceived signals and the noise effect is weaker; (ii) informed agents add the noise warning to their reasoning but behaviour is unchanged. Worth reporting both possibilities and the data.
- *Interpretation paragraph:* under no-noise, the games are "solved" by the models in a model-specific way — there's no behavioural latitude for any cross-task or framing manipulation. Noise is the price of admission for this experimental design, not an intrinsically interesting variable. Forward-link to the discussion (§5.5 limitations: noise as artifice).

## 4.3 Effect of myth-writing on game behaviour (the headline question)

- *Headline (preliminary):* across (model × noise) cells, adding the myth-writing task produces a small and inconsistent effect on *mean* cumulative reward, but a more consistent effect on *across-seed variance*. The clearer story is strategy consolidation, not cooperation lift.
- *Primary contrast:* median cumulative-reward delta between (`game-only`) and each of (`game→myth`, `myth→game`), within each (model × noise) cell. Non-parametric bootstrap CIs (§3.5).
- *Secondary contrast:* across-seed variance delta on the same cells — the *consolidation* test.
- *What to expect, by cell (per project notes):*
    - **Claude × bidirectional ±$1:** the cleanest test. Claude has headroom under this noise condition. Mean myth effect ~2–4 cumulative-reward points, likely not significant on its own `[CHECK]`. Variance reduction: yet to report `[CHECK]`.
    - **Gemini × negative-only $\le 5$:** test of whether myth content can pull a model out of an apparent-betrayal collapse. Direction of effect predicted ambiguously by the consolidation hypothesis; report whichever way it goes. `[CHECK]`
    - **GPT-5-Nano × bootstrap:** Mar 30 result mentioned a "suggestive Myth→Game effect with bootstrap noise (0.41) but high variance" — worth following up. `[CHECK]`
    - **Cells where mean and variance disagree** (if any): explicitly flag — these are the strongest evidence for the consolidation hypothesis over the lift hypothesis.
- *Order effect:* compare `game→myth` vs `myth→game` directly. Asymmetry would suggest the *information flow direction* matters (game → myth lets the myth absorb game state; myth → game lets game decisions condition on myth content). Project's prior intuition is that myth → game is the more interesting cross-task channel, but the data should decide.
- *Interpretation paragraph:* if we land on "weak on mean, clearer on variance", the §5 framing centres on consolidation as the primary effect. If the data lift the mean, that's a happier headline and §5 narrows accordingly. Pre-register the analysis path before peeking — note in the discussion which prediction was made before vs after the cell-level results.

## 4.4 Linguistic dynamics in the myth chain

- *Headline:* over a 10-round myth chain inside a dyad, myths show measurable convergence between agents and measurable drift within an agent. Some chains produce emergent neologisms that recur into the agents' game-reasoning text — a striking but small-sample observation.
- *What to show:*
    - **Between-agent convergence.** Pairwise sentence-embedding cosine similarity between Agent_1 and Agent_2 myths within each round, plotted over rounds. Expected: similarity rises across rounds (convergence); slope and final level vary by model. `[CHECK]`
    - **Within-agent drift.** Same metric applied to consecutive myths from the same agent. Expected: lower than between-agent at each round (own myths are more self-similar than the partner's), but increasing distance across early-vs-late rounds (drift).
    - **LLM-as-judge similarity** (Llama-3.3-70B `[CHECK]`) on the five dimensions (thematic / character / narrative / symbolic / conceptual). Cross-validate the embedding-based convergence picture. Where embedding cosine and LLM-judge disagree, that disagreement is itself informative.
    - **Cooperativity-lexicon counts** and **we/I ratio** per round, per agent. Expected: rise across rounds, especially in the chains where the dyad converges behaviourally.
    - **POS-sequence n-gram structure.** Sentence-level innovation rate is mechanically near-saturated (§2.4 flag) — report the *aggregate* convergence in POS n-gram distributions across agents instead, treating innovation rate as a separate descriptive measure with its own caveat.
    - **Keyword chain evolution.** Per-round top-$k$ keyword tracking. Highlight chains where novel vocabulary appears and propagates — including the "kyrexladilokrater"-style coinages from pilot runs. Number of distinct neologisms per chain, and propagation depth (how many rounds a coined term persists). `[CHECK]`
- *Striking observation to surface:* in the pilot, made-up words generated in myths reappeared in the agents' *game-reasoning* text, suggesting the linguistic content was being absorbed into the agent's broader representation rather than treated as an isolated artefact. Worth a small dedicated paragraph; treat as descriptive, not statistical, evidence given the small number of cases.
- *Interpretation paragraph:* whatever the game-side findings, the linguistic side shows that the myth-writing chain *is* doing work — myths are not random samples drawn IID from the model. The question is whether that linguistic work has any causal back-effect on the game (which is §4.5).

## 4.5 Coupling between game behaviour and myth content

- *Headline:* the strongest evidence for cross-task coupling lives in within-dyad correlations between cooperation language and game cooperation, with one Claude case showing a striking lag-1 correlation; broader picture is mixed.
- *What to show:*
    - **Lag-1 cross-agent correlation.** Pearson $r$ between Agent_A's cooperativity-word score at round $t$ and Agent_B's at round $t+1$, computed per dyad and aggregated by model. Pilot reported $r \approx 0.72$ for one Claude dyad and near-zero for others `[CHECK — confirm replication across seeds]`.
    - **Within-agent same-round correlation.** Cooperativity-word score in agent's myth at round $t$ vs the same agent's $s_t$ or $r_t$. Tests whether the myth content tracks own behaviour (game→myth signal) or precedes it (myth→game signal — would require comparing across task orders).
    - **Direction-of-effect test using task order.** Compare `game→myth` vs `myth→game` cells: does the game-language correlation differ depending on which task comes first within a round?
    - **The Claude lag-correlation case study.** If one or two Claude dyads show $r \approx 0.7$ while the rest don't, characterise *what those dyads did differently* — myth content, behavioural trajectory, model-side reasoning text. Treat as a hypothesis-generating case study, not a statistical claim.
- *Interpretation paragraph:* the linguistic-behavioural coupling is real but weak in aggregate, and concentrated in particular dyads. This is consistent with §4.3's consolidation finding — myth content is doing some work in keeping a dyad on its trajectory, but not enough to systematically shift the trajectory's mean.

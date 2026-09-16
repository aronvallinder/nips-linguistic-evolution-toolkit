# Independent experimental-design review: what to run next

Date: 2026-09-14. Scope: code, configuration, latest figure values, and prior experiment reports. This is a design review, not a new experiment or an exhaustive raw-data audit. The accompanying team literature review supplies external positioning. No paid calls were made. All proposed counts below are design suggestions, not powered sample-size guarantees or runnable configurations.

## Main judgment

The latest plot is not evidence that nothing interesting happens. It contains three different regimes: GPT starts at a no-investment floor and myths unlock investment; Claude has a substantial myth-first lift; Gemini starts at the maximum and cannot improve. The more important weakness is causal interpretation: we do not yet know how much is self-generated strategic reflection, immediate priming, shared cultural transmission, or persistent collective memory. Running more model combinations before separating those mechanisms risks producing another descriptive matrix.

The five ranked priorities are: (1) causal content/transmission versus reflection; (2) persistent collective memory with turnover; (3) a calibrated new dilemma and transfer test; (4) heterogeneous populations with homogeneous matched controls; (5) adaptation after a shock, including strategic rather than immutable adversaries. Ranking emphasizes what would change our scientific conclusions, not which manipulation might make the biggest positive bar.

## Verified diagnosis of the current outcome

Latest population ordinary-agent values, calculated from `docs/figures/negative_only_crossmodel_reasoning_rerun_20260909_resources_boxplots/run_values.csv`, sample standard deviation (n=5 independent runs per cell):

| Model / forced defectors | Game only | Game → Myth | Myth → Game |
|---|---:|---:|---:|
| GPT-5 Nano / none | 25.00 (±0.00) | 37.98 (±7.13) | 45.01 (±8.32) |
| Claude Sonnet 4.5 / none | 55.18 (±1.01) | 54.11 (±0.92) | 68.73 (±4.43) |
| Gemini 3.7 Flash / none | 75.00 (±0.00) | 75.00 (±0.00) | 75.00 (±0.00) |
| GPT-5 Nano / 2 of 8 | 25.20 (±0.45) | 32.85 (±7.87) | 33.36 (±6.87) |
| Claude Sonnet 4.5 / 2 of 8 | 43.43 (±2.07) | 46.88 (±1.36) | 51.04 (±3.42) |
| Gemini 3.7 Flash / 2 of 8 | 58.97 (±1.37) | 58.50 (±1.09) | 57.67 (±1.24) |

A ~20-resource GPT increase is large relative to its baseline, and Claude gains ~13.56 resources without forced defectors. The absent Gemini gain is an upper-bound constraint. These are descriptive estimates, not confirmatory tests selected independently of the observations.

### Cumulative resources exactly cancel returns at the whole-population level

The implemented actual payoffs are, for endowment E, multiplier m, actual send s, actual return r:

- sender: E − s + r;
- receiver: ms − r;
- dyad total: E + (m − 1)s.

This follows directly from `games/trust_game_noisy.py:974` and `games/trust_game_noisy.py:1000`. With no punishment, whole-population cumulative resources are exactly an affine function of cumulative sending; return generosity cancels. With E=5, m=3, 10 rounds, and one dyad per two agents each round, mean cumulative resources range from 25 to 75. A population can therefore maximize this outcome while receivers return nothing. Reciprocity can influence *later* sends, but is absent from the contemporaneous welfare formula.

Ordinary-agent-only resources are different: returns cancel within ordinary–ordinary pairs but do not cancel when a pair crosses the ordinary/defector boundary. Greater sending to an immutable zero-return receiver can improve all-agent welfare while making an ordinary sender poorer. Thus the ordinary-only figure is valuable but still mixes productive coordination, exposure to exploitation, and transfer distribution. It should be accompanied by encounter-specific returns and earnings.

For scripted forced-zero senders, compute the feasible welfare ceiling from the realized schedule: sum E for forced sender slots and mE for free sender slots, then divide by N agents. At exactly balanced forced-sender shares d the 10-round bound is 75−50d, giving 62.5 at 25% and 50 at 50%. Use actual slots, not the nominal ratio, for the reported bound. There is no analogous simple 75−50d bound for ordinary-only welfare because role/exposure composition matters.

Forced actions bypass the LLM (`games/dyadic_pairing.py:209` onward); myths cannot persuade these actors to return money. The randomized dyad manipulation is keyed per agent/role/round (`games/dyadic_pairing.py:185`), whereas the population manipulation fixes identities. They are different interventions, not interchangeable 25% conditions.

### The current protocol already contains a cultural channel, but not a durable public archive

`src/myth_writer.py:146` onward takes the agent's own previous myth and its previous-round paired opponent's myth. The later prompt uses the partner myth, while own earlier outputs remain in private chat. `src/simulation.py:945` retains myth responses in memory-primary. `src/agents.py:86` bounds memory in user/assistant exchanges, not tokens. The September protocol gives two-task cells six exchanges and game-only three, roughly matching game-round horizon but not text amount, latency, reflection, or recency.

The active myth instructions explicitly say to describe how the game should be played, and the game asks agents to take myths into account (stored protocol in the figure provenance; `config/experiments_noisy.yaml:5124` onward selects directive prompts). This is instructed strategic storytelling. That can be scientifically valuable, but does not establish spontaneous institution formation.

Myth-first has its own fresh myth before the first game; at round one it cannot yet have received an evolved partner myth. A round-one advantage can establish priming/reflection, not inter-agent transmission. Later social influence needs its own intervention.

The existing `myth_injection_mode: own/shuffled/filler` is a legacy prompt substitution path. The code explicitly says current corrected templates lack the relevant placeholder (`games/trust_game_noisy.py:258`). Simply toggling that configuration is not a valid new causal ablation without verifying exact request differences.

### Prior results narrow what is worth trying

- Historical transplant experiments already show that seeds carrying explicit strategies can alter play, including suppression, and that filler often does not. They also show cross-model writer/reader asymmetry. They do not establish that narrative beats equal-information plain instructions. See `docs/architecture/findings-cooperation-transplant.md` and `docs/memory_transplant_ablation_design.md`.
- Co-occurrence-based meme transmission largely failed rewiring/future-exposure controls. Shared model priors are a serious alternative explanation. See `docs/architecture/findings-taskorder-myth.md` and `scripts/analyze_meme_transmission_null.py`.
- A public ledger of past actions has already been studied, with weak or adverse welfare effects and framing/identity confounds. This is not the same as a persistent authored myth board. The early identity explanation was reversed in confirmation; do not reuse the exploratory claim that stable identity causes the ledger penalty as a settled result. See `docs/architecture/findings-social-information.md`, `docs/identity_persistence_confirmation_gpt_n10_overview_2026-08-21.md`, and the ledger overview files.
- Swapping defector-authored myths changed exposure tone without confirmed behavioral contagion. A small apparent lexical cascade failed independent confirmation. See `docs/defector_myth_circulation_gemini_confirmation_n10_overview_2026-08-21.md`.
- Longer-horizon washout work exists; some files have within-run reasoning-signature concerns. A clean persistence experiment is useful, but should not be presented as the first longer run. See `docs/architecture/findings-taskorder-myth.md` and `docs/api-audit-reassessment-2026-09-08.md`.

## 1. Separate cultural transmission from self-generated strategy and immediate priming

**Question:** Does encountering other agents' evolving stories cause behavior beyond writing an equally long private strategy note or reading the same strategy in plain language?

**Why first:** This decides what the current finding *is*. A persistent board and mixed population become much more interpretable after this. It targets the gap between the strong historic seed intervention and the weak endogenous transmission evidence.

**Stage A: fixed-context causal probes.** Select 20 prespecified early/middle game states per model from a donor dataset, stratifying by positive/zero receipts and prior cooperation. Freeze the whole recipient game history. Randomly assign one of five text payloads: original donor myth; faithful prose strategy summary with the same behavioral content; myth with strategic prescription removed but story/length retained; unrelated equal-length myth; no extra text. Use two recipient models (GPT and Claude initially), two independent draws per state and payload: 20 × 5 × 2 × 2 = 400 decision calls. Donor texts must be independently sampled, never chosen for the size of their recipient effect. Validate rewritten payloads for retained numbers/policy, and blind the labeling step. Reading comprehension is a manipulation check, not proof of behavioral transfer. Keep the donor and recipient model the same for the first content test, then cross models as an explicit factor; use equal-information plain instructions as the load-bearing control. Fictional author/model labels must not vary with payload. The study-wide game prompt should refer neutrally to the written material in every text arm, rather than retaining a myth-specific directive only in one arm; record that framing change as a new protocol.

**Stage B: free-play validation.** Five arms: game-only; private prose reflection; private myth; exchanged myth; exchanged prose reflection. Match task position, word budget, game history, call count among the four text arms, and naming/observability language. Use one text phase before play per round to eliminate order as a second factor. Start with 2 models × 5 arms × 8 seeds = 80 8-agent/10-round screen runs. Filler/no-text comparison already exists in Stage A, so do not multiply every control into every stage.

**Primary contrast:** exchanged myth minus private myth; second contrast exchanged myth minus exchanged prose. Report a third contrast of private myth minus private prose as a narrative-format effect. The game-only anchor is not a matched compute control.

**Predictions and falsification:** If exchange matters after the initial round and randomized donor policy changes recipient action with the recipient's game history fixed, social transmission has causal support. If prose and myth behave alike, claim natural-language strategy/memory rather than myth-specific advantage. If only private text helps, the result is a self-reflection/priming effect. If deleting strategic clauses removes transfer, that supports strategic content, not mere cooperative vocabulary.

**Guard:** Replacing only the latest visible myth is insufficient if its content survives in earlier recipient chat. Use a clean branching point before first exposure or replace all descendant exposure consistently. Record the full exposure graph. For free play, endogenous action feedback is part of the treatment effect, not held fixed; do not call it the direct transmission effect.

**Implementation:** Explicit cultural exposure policy in `MythWriter`, separate from legacy game injection, with per-call message-difference tests; donor IDs/hashes in metadata. Existing seed injection supports a starting point but its assistant-slot convention can affect refusals and attribution. Present transferred artifacts as external messages unless self-authorship is itself the randomized factor.

## 2. Persistent bounded myth board crossed with agent turnover

**Question:** Can socially accumulated text preserve useful policy after the agents who learned it are gone?

**Why second:** This is the strongest route toward a genuine cultural-memory claim. The current population has private retained conversations and recent partner text; it does not require knowledge to survive replacement of its carriers. Merely expanding context for the same agents does not distinguish cultural inheritance from better individual recall.

**Design:** Eight agents, 30 rounds, 3 communication conditions × 2 turnover conditions. Communication: current delayed partner myth; bounded public myth board; bounded public prose strategy board. Turnover: no replacement versus replace half the agents after rounds 10 and 20 using a prespecified schedule. New agents get fresh IDs, empty private history and normal game rules; board access follows their assigned condition. Existing agents keep their own permitted memory. Balance identities/roles and keep public-observability framing constant. Measure earnings in the same way for replacement slots; record individual birth/death events separately.

**Board mechanics:** One fixed-length candidate per agent per round; 800–1,000-word total budget as a proposed starting point, with deterministic retention and retrieval in the first test. Snapshot at start of round; publish new material only after all agents finish that round, so thread completion order cannot create exposure differences. Specify author visibility, timestamps, replacement rule, read budget, and edit permissions. The board must have the same budget whether myths or plain prose are used. Do not begin with a central model curator, voting, tools, and unrestricted archive simultaneously.

**Screen:** 3 channels × 2 turnover states × 2 models × 8 independent societies = 96 runs, 30 rounds each. Treat this as a substantial follow-on cost, not a cheap tweak to existing plots. A smaller engineering pilot should test only message integrity, replacement resets, and archival bounds.

**Primary estimand:** channel × turnover interaction in resources during the first 3–5 rounds after replacement, plus retention of a previously learned contingent policy by naive agents. Compare myth and prose boards. Add a frozen-old-board or no-inheritance control in confirmation if the screen suggests inheritance; that distinguishes useful updating from persistent instructions.

**Falsification:** If the board helps only without turnover, it is a memory/coordination aid, with no evidence of intergenerational retention. If prose matches myth, shared artifacts matter but narrative is not necessary. If a static founding instruction matches an evolving board, the mechanism is inherited policy rather than cumulative improvement. If successive generations improve only because histories grow, it is an information-volume effect; cap archive size throughout.

**More ambitious follow-on:** Distinct local environments with differing optimal contingent rules, cross-fostering naive agents between cultural archives, and held-out action tests. That makes transmission distinguishable from shared pretrained priors. Cumulative culture needs improvement across independent lineages under an equal final information budget, not just survival of a slogan. Prior shared-store mixed-model culture work identified by the literature teammate makes the causal turnover, content-control and behavioral generalization contrasts essential; the existence of a shared board is not itself a novelty claim.

**Implementation:** New board state, snapshots, artifact versions, exposure graph, birth/death/resume semantics, per-agent resets. Existing `history_policy: population_ledger` supplies action records, not this artifact store. Do not reuse its label for the new treatment.

## 3. Calibrate a real dilemma with behavioral headroom, then test transfer

**Question:** Does the text channel help agents solve a contingent coordination problem beyond the trust game's full-send/half-return default?

**Why third:** More repetitions of Gemini's 75-resource baseline cannot detect improvement. Changing the game can make the test informative, but blindly scanning games for a positive myth effect is outcome selection.

**Candidate environment:** An 8-agent repeated public-goods game with contribution endowment 5 and group multiplier strictly between 1 and N (proposed initial calibration values 1.5 and 2). Personal payoff is E−c_i + m/N × sum(c_j). Contributions increase group welfare while imposing a personal cost for fixed others' contributions. Add a prespecified threshold or common-pool replenishment state only in the next experiment, not all at once. A threshold game is useful specifically for testing coordination on a viable joint target; a replenishing commons tests restraint and long-term stewardship. They answer different questions.

**Calibration:** Before comparing myth arms, test comprehension and selfish/cooperative payoff calculations under identical neutral task framing, and run baseline policies across a small prespecified multiplier grid. Choose difficulty using headroom, comprehension, and reliable variation, never based on whether myth wins. All zero/all maximum regimes are described, not selectively hidden. Stop if all candidate settings saturate or fail comprehension; report that the benchmark does not support the hypothesis under these models.

**Screen:** Two games (current trust game anchor plus one calibrated new game) × 3 conditions (game-only, prose-before-game, myth-before-game) × 2 models × 8 seeds = 96 runs. The new game should use simultaneous decisions and delayed feedback to prevent ordering leakage. Preserve ten rounds initially; length can be a separate sensitivity.

**Primary estimand:** myth versus matched prose within each game, with game-normalized resource efficiency and individual payoffs. Do not compare raw resource dollars across payoff functions. Reserve at least one unseen parameterization or environment for confirmation. A parameterization used to select the intervention is development data.

**Transfer follow-on:** Evolve archives in the donor game, freeze them, and expose fresh recipients in the held-out game to original archive, game-specific plain policy, and irrelevant archive controls. Test whether narratives carry an abstract contingent norm rather than copying an inappropriate numeric recipe. A failure of numeric transfer can itself be informative.

**Implementation:** The repository has `games/trust_game.py`, `games/trust_game_noisy.py`, a pairing mixin and `BaseGame`; no inspected public-goods implementation. Simultaneous group decisions and group-level state require a new game and corresponding simulation dispatch, not a YAML alias. The noisy trust-game class does not expose the clean class's varying-multiplier schedule in the same way; verify the selected path before proposing a simple config switch.

## 4. Mixed-model populations as a test of coordination across different priors

**Question:** Does a shared textual convention help heterogeneous agents coordinate, and who receives the gains?

**Why fourth:** Worth doing, especially given GPT's zero-investment baseline and Gemini's full-investment default, but heterogeneity alone mostly produces a descriptive model tournament. The strong design is a composition × communication interaction, controlling for the homogeneous models' behavior.

**First test:** GPT/GPT, Gemini/Gemini, GPT/Gemini dyads; game-only versus exchanged myth, with a matched prose arm if experiment 1 shows prose is competitive. Balance which model starts as sender, but retain model identity throughout each agent's life and both tasks. Report outcomes by model and role. Use the no-forced-defection regime first to avoid confusing heterogeneity with a second source of asymmetry.

**Screen count:** 3 compositions × 3 channels × 2 starting-role assignments × 8 seeds = 144 dyad runs. In homogeneous arms, role reversal is still a seed/schedule block rather than a scientifically distinct model composition. For an economical first screen, use two channels for 96 runs, then confirm against prose if an interaction appears. Do not start with all three model pairs × 3 noise settings × 3 task orders.

**Primary contrast:** communication benefit in mixed dyads minus the corresponding benefit in homogeneous controls. Do not interpret improvement over GPT/GPT alone as a heterogeneity benefit: replacing one zero-sending player by an unconditional sender changes the baseline mechanically. A stronger later population design holds composition at 4+4 and randomizes cultural connections independently of game pairings, so cross-model exchange itself is identified.

**Falsification:** If the mixed result equals what homogeneous action policies predict, there is no coordination mechanism beyond composition. If only one model's resources rise while the other's fall, call it redistribution/exploitation rather than mutual benefit. If prose matches myth, again the claim is language-based coordination, not narrative-specific culture.

**Metrics:** per-model sender contribution, return fraction conditional on opportunity, realized earnings, ordinary/non-forced earnings, between-model inequality, and model-by-model exposure influence. Counterbalance which model writes or receives an initial convention. Reader/writer transfer and agents of different models playing together are distinct designs; historical transplant work does not answer this one.

**Implementation:** `src/simulation.py:476` constructs every agent with the same model/client/temperature. Although `Agent` stores its own model/client, the runner, condition schema, metadata checks, and resume path need explicit per-agent request plans and assignments. Keep provider-native profiles pinned (`config/experiments_noisy.yaml:33`), rather than pretending equal reasoning labels equal compute. A raw per-agent model list is insufficient provenance.

## 5. Resilience, repair and adaptation under changed incentives

**Question:** Do narratives encode flexible norms that survive mistakes and adapt to genuine betrayal, or do they lock agents into a brittle recipe?

**Why fifth:** A cooperation lift in a stationary easy game is less diagnostic than selective forgiveness, recovery and appropriate policy revision. Prior fidelity and seed results suggest myths can amplify helpful and harmful conventions. A negative result is therefore theoretically valuable.

**Design:** Eight agents, 30 rounds, three text conditions (none/private matched prose/shared myth). Ten warm-up rounds, a five-round perturbation, fifteen recovery rounds. Start with a known exogenous implementation-error schedule applied identically across channels and a clean no-shock control. Keep communication noise distinct from actual action errors. Existing negative communication noise changes observations, while a forced-action shock changes realized actions; these cannot be silently substituted.

**Screen count:** 3 channels × 2 shock states × 2 models × 8 seeds = 96 runs. Pair complete exogenous schedules at the society level. If the board experiment is successful, use its winning archive mechanism and freeze it; do not optimize persistence on the same shock outcomes.

**Primary outcomes:** cumulative resource loss relative to paired no-shock runs; time to return to pre-shock contribution band; over-retaliation to ordinary agents; exploitation losses; revision latency in text and actions. Use a prespecified recovery window rather than defining recovery after seeing trajectories.

**Follow-on adversary:** Replace forced-zero types with a transparent contingent scripted policy, such as cooperate initially and exploit after a threshold, or an explicitly incentive-driven LLM opponent. An immutable zero-return agent can measure harm resistance but cannot measure norm conversion or deterrence. Keep strategic adversaries and random accidents in separate arms so appropriate discrimination is measurable. If adding partner choice, exclusion or punishment, make each a separate institution: prior punishment results show capability and welfare effects need not move together.

**Falsification:** A stable myth that prevents adjustment to changed payoffs is maladaptive cultural persistence. Fast recovery with identical prose is a general memory/coordination result. More aggregate earnings accompanied by sustained exploitation of ordinary senders is not robust prosociality.

**Implementation:** Predeclared shock schedules keyed by seed/round/action, private versus announced shock variants only if hypothesized, saved actual/communicated action separation, and longer-run provenance checks. Do not infer a within-run learning mechanism from different request settings before and after the shock.

## Robustness plan applying to all five

1. **Independent societies are the sample unit.** Five runs are five replicates, not forty independent agents or hundreds of independent rounds. Use society-level paired differences or hierarchical models with society clustering. Donor-text/lineage effects need independent donor sampling and a corresponding random effect or cluster; repeated recipient draws do not create new cultural lineages.
2. **Preregister a small set of contrasts and a meaningful threshold.** Example proposed threshold for the current ten-round trust task: 5 resource units per agent (10% of the 50-unit attainable range), plus a stricter narrative-specific comparison against prose. Choose before confirmation; it is a scientific relevance threshold, not a universal power prescription.
3. **Screen then independently confirm.** Pilot eight seeds/cell is for feasibility and variance. Freeze the successful or diagnostic contrasts, then estimate confirmation sample size from paired-difference variance and the smallest meaningful effect. The rough normal approximation n≈(1.96+0.84)^2 σ_d²/δ² can guide planning, with simulation/bootstrap for clustered bounded outcomes. Do not automatically call n=20 powered; do not recycle the screen as independent confirmation.
4. **Distinguish lack of evidence from equivalence.** A saturated null or wide interval is not proof narratives do nothing. Use confidence intervals relative to the prespecified meaningful interval. Correct the confirmatory family of comparisons, rather than cherry-picking one model/defector panel.
5. **Measure the mechanism.** Keep resources primary for continuity, but also sender fraction, conditional return, zero-receipt probability, sender loss after trust, payoff inequality, and type-specific encounters. The return denominator is actual received resources for economic behavior and communicated receipt for perceived generosity; show both if interpreting intentions. No opportunity means undefined, not zero cooperation.
6. **Freeze exact prompts, histories, naming, seeds, request plans and output policy.** Compare model-plus-settings conditions explicitly. A matched round horizon is not a matched token budget or matched cognitive task. Audit real message arrays and register condition hashes.
7. **Register all attempted runs.** Final full-state JSON proves completion; checkpoints/error snapshots do not. Report failed/resampled runs and reasons. The latest batch's known Claude role-confusion resample and lost in-flight GPT runs are not magically erased by a clean final matrix (`researchlog.md:14`). Do not condition the scientific sample on whether a model found a regime easy to format.
8. **Costs before launch.** These count proposals intentionally avoid invented dollar estimates. The old batch receipt (~$168 for its 270 mixed-size runs) is not a price quote for 30-round public boards. Measure exact new-context cost with a tiny authorized pilot, then print resolved model, N, workers, projected total and margin before a paid batch. No new simulation is authorized by this review alone; the user asked for configuration before running.

## Suggested interpretation to communicate now

The strongest honest current story is that the same storytelling protocol interacts with three distinct starting policies: it can unlock investment, accelerate an intermediate cooperative regime, or have no headroom to improve an already saturated one. The next scientific win is to establish *when shared artifacts causally preserve and adapt useful behavioral rules*, including cases in which they fail or entrench a bad rule. That would be more convincing than forcing every model to show the same positive boxplot.

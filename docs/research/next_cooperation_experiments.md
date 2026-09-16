# What to test next in cultural cooperation

The strongest next step is to establish whether shared stories preserve useful cooperative knowledge, beyond the effects of instructions, private reflection, and additional memory. The latest results already contain sizeable effects for two models. What they lack is a clean explanation of those effects and evidence that the resulting behavior is transferable, resilient, and socially inherited.

The recommended order is: **identify the causal mechanism; test cultural inheritance through a shared archive; challenge cooperation with mistakes and exploitation; test transfer to a different dilemma; then test whether culture bridges mixed-model populations.** This order favors experiments whose positive and negative results would both sharpen the scientific claim. It does not optimize the chance of finding a larger favorable bar.

This report concerns the local repository as inspected on 14 September 2026 and literature available at that date. Proposed experiments have not been implemented or launched. Their designs and sample counts are proposals, not approved configurations or power guarantees.

## 1. What the existing evidence actually says

### The latest result is heterogeneous, not uniformly weak

All 270 latest source hashes were checked, and all 405 plotted run/group observations were reproduced from final round balances. The population observations are reused in all-agent and ordinary-agent views; they do not constitute additional replications. Population task-order comparisons share recorded protocol seeds and defector identities within all 45 model–defection–replicate blocks. Sampling of model responses remains stochastic. [Local audit](mixed_future_data_audit.md)

For the ordinary-agent population figure, the following are **seed-paired Myth → Game minus Game-only differences**, expressed as mean (± sample standard deviation) across five paired runs:

| Model | No forced defectors | 2 of 8 defectors | 4 of 8 defectors |
|---|---:|---:|---:|
| GPT-5 Nano | +20.01 (±8.32) | +8.16 (±7.04) | +5.35 (±6.32) |
| Claude Sonnet 4.5 | +13.56 (±3.62) | +7.60 (±3.62) | +3.14 (±3.90) |
| Gemini 3.7 Flash | 0.00 (±0.00) | −1.30 (±0.78) | −1.95 (±1.02) |

These are descriptive estimates from an inspected dataset, not preregistered confirmation. At n=5, uncertain and bounded distributions deserve particular caution. The supporting audit gives exploratory, unadjusted paired intervals; it does not convert the panels into nine independent confirmatory discoveries. [Reproduced differences](mixed_future_latest_differences.csv)

The interpretation differs by model. GPT's game-only population remains at the zero-send resource floor, and myth-first moves it upward. Claude starts in an intermediate regime and gains substantially from myth-first. Gemini obtains the maximum without forced defectors in every task order, leaving no room for an improvement on this endpoint. Under forced defection, the gains diminish and ordinary-agent Gemini resources decline slightly. That is potentially a useful boundary condition rather than an inconvenient panel to discard.

The latest log also discloses a discarded and resampled Claude role-confusion run and interrupted GPT runs that were resampled. Historical records include changing request metadata and some within-run reasoning-signature concerns. Those issues qualify particular comparisons; they do not invalidate every result or establish that reasoning effort caused the observed differences. [Run history](../../researchlog.md), [API reassessment](../api-audit-reassessment-2026-09-08.md)

### Resources, reciprocity, and protection are different outcomes

The actual payoff code gives a sender `E − s + r` and a receiver `m × s − r`. Their joint payoff is therefore:

\[
W = E + (m-1)s.
\]

Returns cancel. Without punishment, total resources across all agents measure productive sending exactly; they do not independently measure equitable reciprocation. Under the default endowment 5, multiplier 3 and ten rounds, all-agent average cumulative resources range from 25 to 75. Full sending can maximize this score even if receivers return nothing. Reciprocity can affect future sending, but its immediate distributional effect is invisible in the total. [Payoff implementation](../../games/trust_game_noisy.py:1000)

Ordinary-only resources are more sensitive to exploitation, because transfers across the ordinary/defector boundary no longer cancel. However, they combine several mechanisms: how many ordinary senders meet forced-zero receivers, how much they send, how ordinary receivers return, and how the pairing schedule allocates opportunities. Analyze ordinary–ordinary and ordinary–defector encounters separately before attributing the whole difference to culture.

Fixed forced-zero agents cannot be persuaded to cooperate: their actions are imposed by the program. They test resistance to a persistent exploiter, not successful conversion or deterrence. Random dyadic forced actions and fixed population defector identities are also different treatments. Preserve those distinctions. [Action overrides](../../games/dyadic_pairing.py:185)

### The current setup supplies strategic storytelling, but does not require inheritance

The active instructions explicitly connect myths to how the game should be played. Agents retain private context and receive the previous partner's myth. In myth-first, an agent writes its first myth before its first game decision, when no socially evolved partner myth yet exists. An opening-round improvement can therefore be private reflection or priming; it cannot by itself demonstrate transmission between agents. [Myth exposure](../../src/myth_writer.py:146), [rerun configuration](../../config/experiments_noisy.yaml:5149)

There is a genuine social text channel, but no requirement that useful knowledge survive replacement of the agents who acquired it. There is no inherited, bounded public myth archive in the current rerun. This makes a cultural-memory experiment worthwhile, while also explaining why simply extending the same agents' private context would not establish cultural inheritance.

### What a comprehensive local scan covers—and does not cover

The census parsed and hashed **35,852 JSON paths**, including current raw outputs, shared mirrors, hidden upload staging, the nested `nlet-hf-data` store, phases, project data, and archived outputs. It classified **132 experimental families** and found **16,774 final-shaped full-state paths representing 6,078 distinct byte hashes**. Copies, superseded conditions, smoke tests and historically compromised runs remain among those file hashes: this is not a count of independent scientifically valid replicates. Checkpoints and error snapshots were excluded from final candidates. Four malformed derived judge-table files were identified; their raw source runs remain readable.

The full census is structural and provenance-oriented. Every historical prompt and every derived analysis was not independently reanalysed. Representative raw metadata from each family, prior audits, configuration, and targeted numerical reproductions support the historical synthesis. Remote-only data are outside the local scan. These limits are important to the meaning of “all data.” [Full path inventory](mixed_future_inventory.csv), [family inventory](mixed_future_family_inventory.csv), [audit and reproduction scripts](mixed_future_data_audit.md)

The prior work materially changes the shortlist:

| Existing experimental arc | What it contributes | What remains open |
|---|---|---|
| Corrected task-order and memory studies | Myth-first effects depend on model and memory apparatus | Shared transmission versus private reflection and directive text |
| Seed transplants, filler, low-cooperation seeds, altered grammar | Content can change behavior substantially in the historical apparatus | Does equal-information plain advice work just as well in the current pipeline? |
| Cross-model myth writers and recipients | Writer/reader asymmetry has already been explored | Live mixed-model coordination is a separate question |
| Action ledgers, stable identities, history visibility | More social information was not uniformly beneficial; some early interpretations reversed | A bounded inherited archive of authored policies differs from a transaction ledger |
| Defectors, myth circulation, sanctions | Exploitation and institutions matter; some small-screen effects failed confirmation | Adaptive rules, error recovery, and protection rather than unconditional generosity |
| Text lineage, meme mining, washout | Textual persistence and longer runs have already been investigated | Causal lineage transmission surviving exposure controls and clean replacement |

The historical seed ladder was independently reproduced: high-cooperation final seeds produced much higher resources than baseline, filler, or low-cooperation seeds. Those runs used different memory/noise arrangements and cannot be pooled with September data. They justify a bridge experiment, not an assertion that modern endogenous cultural diffusion has already been proved. The audit also identifies withdrawn or failed claims—including raw meme inheritance, identity-based explanations, and isolated prose-effect interpretations—that should not be revived. [Historical results and reversals](mixed_future_data_audit.md)

## 2. How the literature changes the opportunity

Several attractive experiments are already established at a broad level. Akata and colleagues studied cross-model play, multiple games, scripted opponents and extra social reasoning. Vallinder and Hughes studied strategy inheritance across generations. A June 2026 preprint by Jones and Hauert even gives stateless mixed-model agents shared decaying text storage and reports myth-like artifacts. The opportunity is therefore a **controlled behavioral mechanism**, not the existence of mixed play or persistent narrative. [1–3]

The literature also supplies an important warning about explanatory labels. GovSim investigated language-mediated sustainable resource use, while a subsequent replication reports that explicit numerical guidance accounts for much of a purported universalization benefit. The replication's indexed primary abstract was accessible, but its full PDF could not be inspected; it motivates a control, not a detailed unverified replication claim. Equal-information advice is a necessary comparator here. [4–5]

A separate line of theory and experiments distinguishes generosity from cooperation that resists exploitation. Recent LLM invasion tests, classical indirect reciprocity, and institutional research all motivate measuring discrimination, recovery and the distribution of benefits. They do not imply that adding punishment, reputation, or public discussion must help every model. [6–9]

The referenced OpenAI/Hugging Face incident does involve asynchronous board-mediated coordination according to primary reports. It is a relevant example of external state supporting coordination, but it is observational and involved harmful conduct. It is not evidence that a board causes beneficial cultural cooperation. [10–11]

The full literature supplement contains 22 primary sources, with publication status and access limits. Recent preprints are treated as nearby precedents, not settled conclusions. Human cultural-learning and governance work supplies hypotheses and design logic; it does not validate these LLM populations as human social models. [Literature supplement](future_experiments_literature_review.md)

## 3. Five experiments, ranked

| Rank | Experiment | Main uncertainty resolved | Why this position |
|---:|---|---|---|
| 1 | Separate shared myth, private reflection, and matched plain advice | What causes the current effect? | Highest diagnostic value and builds directly on existing positive evidence |
| 2 | Shared archive with genuine agent replacement | Does useful knowledge survive its original carriers? | Strongest route toward a cultural-memory contribution, with a clear erasure test |
| 3 | Mistakes, exploitation, and recovery | Is the resulting cooperation selective and resilient? | Uses the current game to answer the weakness exposed by the defector panels |
| 4 | Transfer across incentives and into a different dilemma | Is the learned policy adaptable beyond this payoff table? | Strong generalization test, but needs calibration and a new environment |
| 5 | Culture in mixed-model populations | Does shared text overcome incompatible model policies? | Useful, but generic cross-play is already established and is easy to misinterpret |

### 1. What is doing the work: a shared myth, a strategy, or thinking first?

**Question.** Does reading another agent's myth change behavior beyond private writing, and does narrative form add anything beyond the same strategy in ordinary prose?

**Recommended starting design.** Use the current eight-agent game, ten rounds, negative-only communication noise, no forced defectors, and pinned GPT/Claude profiles. This is a deliberate bridge to the two models with behavioral headroom, not a claim that Gemini is irrelevant. Retain Gemini as a later boundary-condition check in a non-saturated challenge. Compare five arms: game-only; private prose reflection; private myth; exchanged prose; exchanged myth. Place the text phase before play in every text arm.

Among the four text arms, match the number of calls, allowed length, game-history horizon, presentation slot, and explicit instruction to consider the material. Do not compare a directive myth with an intentionally content-free prose control. Independently generated myths and prose can develop different policies: this free-play comparison estimates the effect of the whole writing/exchange protocol, not narrative form alone. The fixed-history probes below isolate form using matched policy content; an additional prespecified yoked-content free-play study would be needed to isolate form during extended interaction. Social versus private exposure is the intended information difference. The game-only arm remains an anchor, not a compute-matched control.

**Add a small fixed-history intervention before free play.** Select twenty prespecified game states per recipient model, stratified by stage and opportunity, and independently chosen source texts. At a clean point before exposure, compare original myth, matched strategy prose, policy-removed narrative, unrelated matched-length text, and no extra text. Two recipient draws per state give 400 decision calls across two models. Rewriting or validating source texts may require additional calls and must be counted separately. Do not choose donor texts for the effect they produce in the recipients.

This branching experiment holds the recipient's prior game history fixed. It estimates an immediate effect of content rather than the full feedback loop. The free-play experiment then asks whether that intervention matters for cumulative resources when actions and subsequent experiences can diverge. Both are necessary; neither should be described as answering the other's question.

**Primary contrasts.** Exchanged myth versus private myth identifies the value of social exposure under the matched protocol. In free play, exchanged myth versus exchanged prose compares social-writing protocols; private myth versus private prose compares private-writing protocols. Neither alone isolates form because generated policy content can differ. In the fixed-history probes, matched narrative/prose payloads test form while holding policy content fixed. Deleting the operative rule tests whether concrete policy content is essential. Use negative-control sources and randomized exposure, not vocabulary overlap alone.

**Interpretation.** If prose matches myth, the contribution is transferable natural-language policy, not a unique myth advantage. If only private writing helps, the mechanism is reflection or priming. If socially supplied content changes a recipient's contingent choices with prior history fixed, that is stronger evidence of transmission. A myth advantage that emerges only after delay, corruption, or replacement is more interesting than immediate rhetorical preference.

**Screen and implementation.** Two models × five arms × eight new seeds gives 80 full population runs, plus the 400 decision probes. Eight seeds are for screening, not a guaranteed adequately powered confirmation. The existing legacy myth-injection switches can be inert with the active templates; implement an explicit exposure policy and inspect actual outgoing messages. Record donor hashes and all exposures, and prevent earlier copies of removed text from remaining in private history. [Design review](future_experiment_design_review.md), [content precedent and controls: 4–5]

**Why first.** Every subsequent experiment becomes easier to interpret once this identifies what the transmitted object needs to contain. It can yield a strong paper-relevant conclusion even if the answer is that stories are not special.

### 2. Can a shared cultural archive teach a completely new generation?

**Question.** Does useful cooperative know-how survive replacement of experienced agents, and does an evolving archive improve on a fixed founding instruction?

**Recommended design.** Use eight-agent societies over thirty rounds. Cross archive content (myth or plain strategy), persistence (retained archive or reset archive), and population continuity (same agents or scheduled replacement). With two models and eight independent societies per cell, the core 2 × 2 × 2 design comprises 128 runs. Replacement can remove half the agents after round ten and everyone after round twenty. New agents receive normal game rules and permitted archive content, but no predecessor's private chat or hidden summary.

The persistence comparison should retain public visibility and authorship conventions in both arms. A simple “partner myth versus public board” contrast changes audience, quantity, persistence and common knowledge at once. It is useful descriptively but insufficient to identify memory persistence.

**Concrete starting archive mechanics.** Propose eight entries of at most one hundred words each, one scheduled author update per round, and deterministic oldest-entry replacement. Every arm follows the same writing schedule. All agents read a snapshot fixed before the round; writes become visible only next round. The reset arm erases all archive entries after rounds ten and twenty, after the final write and before replacement or the next read, in both the continuous-population and replacement conditions. The retained arm's read budget is capped, with actual exposure lengths logged. Reset necessarily removes useful information—the intended intervention—but equal-length irrelevant padding can check whether an effect is merely context length. A later matched-current-content comparator can separate age of information from total amount read.

These values are starting engineering choices, not empirically optimal settings. Fix them before outcome collection. Do not initially combine a board with model-selected winners, upvotes, sanctions and unlimited storage. Each adds a separate mechanism and selection bias.

**Primary outcomes.** Measure the first three to five decisions of newcomers, their subsequent resources, and whether they execute a locally learned conditional policy in prespecified test situations. Compare the turnover penalty between retained and erased archives and between narrative and prose. Keep cumulative per-slot resources for continuity, but separately report newcomer cohort outcomes; inherited wealth must not be mistaken for inherited competence.

**What would establish more than memory.** An archive-erasure intervention that removes newcomer competence supports inheritance through text. Persistence across complete turnover rules out founder-only private learning. Better behavior from later-generation archives, evaluated in identical fresh recipients against an early frozen archive at equal budget, supports cumulative improvement. A different learned rule in each of two local environments, followed by cross-fostering, helps rule out a shared pretrained default.

The frozen-archive and matched-fresh-recipient evaluations are required before claiming cumulative culture, even if omitted from the initial engineering screen. Temporal persistence of recurring names or stories is not enough. If a static instruction works equally well, report inherited useful policy rather than collective innovation.

**Why second.** This directly tests the cultural-memory intuition and offers the most ambitious potential result. The novelty is constrained: prior work already combines shared text stores and heterogeneous agents, and the project's intellectual predecessors already study generations. The stronger contribution is causal retention of payoff-relevant, adaptable knowledge under bounded resources, with plain-policy and erasure controls. [2–3, 12–13]

### 3. Do the learned norms protect cooperators and recover from mistakes?

**Question.** Does the text channel create flexible cooperation, or merely persuade agents to send more—including to exploiters?

**Recommended design.** Keep the current trust game so that a new environment does not become a simultaneous explanation. Use thirty rounds: ten baseline, five perturbation, fifteen recovery. Compare game-only, shared plain strategy, and shared myth, using the mechanism established in experiment 1. Begin with paired no-shock versus temporary action-error schedules; separate those from the existing communication noise.

Two models × three channels × two shock states × eight seeds gives 96 screen runs. Exogenous event schedules should be identical across arms. Use uniform sampling of recipient roles, not a single chosen agent whose network position happens to matter. A scripted cooperate-then-exploit opponent is a separate follow-on challenge; it should not be pooled with accidental action corruption.

**Primary outcomes.** Retain cumulative resources but add ordinary-agent earnings, money lost after trusting exploiters, exploiter advantage, conditional sending and return behavior, retaliation against ordinary partners, and recovery time relative to paired no-shock runs. Prespecify the recovery window and tolerance. Compare actual rather than only communicated transfers when calculating economic consequences.

**Crucial distinction.** Ordinary agents may benefit from refusing an exploiter even while whole-population production falls. Conversely, a larger total resource score can conceal worse outcomes for cooperative senders. The experiment should reward context-sensitive action, not score every refusal as failed cooperation.

**What would be exciting.** Transmitted rules allow fast recovery after a mistake but suppress repeated exploitation; successors can apply those distinctions to unfamiliar histories. That is a much stronger behavioral claim than an unconditional increase in sending. A harmful result is equally informative if myths entrench indiscriminate trust, retaliatory spirals, or obsolete prescriptions.

**Why third.** The defector panels make this an immediate interpretive need, and the existing game provides a comparatively economical implementation path. It also aligns with invasion-resistance and indirect-reciprocity literature without assuming their binary-game definitions apply unchanged to this noisy continuous game. Do not add partner choice, exclusion and punishment simultaneously; the repository already shows that sanctions can have model-specific costs. [6–9]

### 4. Can a learned culture adapt to a new payoff structure and a different dilemma?

**Question.** Is the transmitted object an adaptable relational rule, or a recipe tied to “send five and return half”?

**Recommended sequence.** First change the trust-game endowment so that a copied absolute amount becomes inappropriate—for example, a lower endowment makes a literal send-five rule infeasible. A multiplier change alone may leave full sending and proportional returns sensible; use it as an adaptation test only if the particular inherited policy is analytically shown to need revision. Then test one structurally different environment, preferably a renewable common-resource game in which excessive extraction reduces future collective resources. This reverses the superficial action heuristic: success may require restraint rather than giving more. Public goods is a reasonable simpler alternative, but do not run both merely to increase the chance of a favorable result.

Before testing narrative benefit, use a small prespecified parameter grid to verify payoff comprehension, feasible cooperation, and baseline behavioral headroom. Select a setting on these criteria alone. Preserve and report saturated and failed-comprehension cells. Never select the environment by which one gives the largest myth lift.

**Transfer comparison.** Create source archives without access to the held-out environment. Fresh recipients receive a frozen original myth archive, an equivalent plain-policy archive, unrelated matched-length text, or a newly generated in-environment strategy as an adaptation benchmark. Hold information and evaluation horizon fixed as far as the treatment permits. Game descriptions that share an identical payoff equation are framing variants, not evidence of structural transfer.

**Primary outcomes.** Measure resource sustainability, collapse risk, long-run individual payoffs and feasible efficiency. Raw dollar totals across different payoff systems are not comparable. Evaluate whether the transferred rule changes appropriately when incentives change, not merely whether agents repeat its moral vocabulary.

**Screen size.** Two held-out targets (changed trust parameters and one new dilemma) × four transfer conditions × two source/recipient model profiles × eight independent donor lineages gives 128 evaluations. Use eight independent donor lineages per source model, sixteen total, and reuse each donor across its target/condition block for paired evaluation. The no-transfer and newly generated strategy controls belong to the same evaluation blocks even though they do not consume the donor archive. Cluster inference by donor block; the 128 evaluations are not 128 independent cultural origins. Additional recipient repetitions within a donor lineage are nested and increase the call count without creating new independent cultural origins. Donor generation and calibration have separate budgets. If the archive experiment has not produced a usable transfer object, defer this stage rather than quietly redefining “culture” after observing the target outcomes.

**Why fourth.** This offers stronger generalization than more models in the same game, but requires new code, calibration, and a credible donor artifact. GovSim and social-norm research already cover resource governance; the distinctive question is adaptation of socially acquired knowledge, including failure through cultural rigidity. [4, 14–15]

### 5. Does shared culture bridge models with incompatible starting policies?

**Question.** Can a shared myth or policy enable mutually beneficial coordination between models that otherwise behave differently?

**Recommended first comparison.** GPT/GPT, Gemini/Gemini and GPT/Gemini dyads; game-only, shared prose and shared myth; balanced initial sender assignments; no forced defectors. Eight seeds per composition–channel–assignment block gives 144 dyad runs. Homogeneous role reversals are schedule blocks, not additional model compositions. Start with this one contrast before adding every pair and noise level.

The current homogeneous baselines make GPT/Gemini a diagnostic candidate, but do not establish how either will behave in cross-play. Keep model identity constant within each agent across game and writing tasks, keep names neutral, and initially omit brand labels. Naming a partner “GPT” is a separate prompt manipulation from actually using GPT.

**Primary contrast.** Estimate the communication benefit in the mixed pair relative to its benefit in each homogeneous pair. A composition-weighted average is a useful descriptive reference, not an interaction-free theorem for a strategic game. Inspect per-model earnings and policies and, where practical, compare against scripted policies reconstructed from homogeneous behavior.

An improvement over GPT/GPT alone is insufficient: replacing a zero sender with a generous sender can raise production mechanically. Evidence of bridging requires changed contingent behavior beyond that replacement and should not simply enrich one model at the other's expense. A later 4+4 population can randomize text connections separately from game encounters to test which cross-model exposures matter.

**Implementation.** The current initializer gives all agents the same model and client. Per-agent model/request plans must be represented in execution, saved conditions, resumes, and per-call provenance. Merely changing the model string on an agent is insufficient. [Initialization](../../src/simulation.py:476)

**Why fifth.** Mixed models remain worth doing, but the literature and existing cross-writer work make a generic tournament less informative than the first four experiments. The earlier proposed 270-run all-pair/task/noise sweep is not the preferred starting point after this review: it spends many runs on descriptive coverage before the mechanism is identified. [1, 16]

## 4. What would make the evidence substantially more robust

### Confirm mechanisms, not selected winners

Use the present dataset for discovery. Before new confirmation, freeze a small set of primary contrasts, a smallest meaningful effect, and a treatment-independent environment-selection rule. For the current ten-round trust task, five resources per agent is a possible practical threshold—ten percent of the attainable 50-resource range—but it is a proposal to justify, not an externally established standard. A narrative-specific effect against prose may warrant a separate threshold.

Screening at eight societies per cell provides feasibility and variance information. Select confirmation size from uncertainty in paired differences and the scientific threshold, preferably through simulation for bounded/clustered data. Do not describe n=20 as automatically powered. Use fresh protocol seeds and independent donor lineages for confirmation; do not reuse the same selected best myth as if it were multiple independent cultural discoveries.

A null with a narrow interval within the meaningful-effect bounds can support practical equivalence. A wide interval, saturated outcome, or n=5 panel generally cannot. Register the family of confirmatory comparisons and report its multiplicity handling. The analysis unit is the independently initialized society or lineage, not an agent or a round.

### Preserve the distinctions that previous audits showed can disappear

Freeze model-plus-request profiles, exact prompt versions, memory policy, actual message arrays, artifact exposures, role assignments, exogenous event schedules, retry policy and output locations. Pair seeds for the intended environment randomness while acknowledging that model sampling is not paired by that mechanism. Report planned and realized profiles separately if any mismatch occurs; do not treat equal “high” labels across vendors as equal computation.

A targeted within-model profile sensitivity is useful once a mechanism is established, especially for the GPT zero-send opening. Change one request-policy dimension at a time, retain exactly the same prompts, and report both profiles rather than selecting the one with the largest effect. This is a robustness check within the programme, not a reason to replace the whole historical record.

Count every attempted simulation, including format failures, interruptions, retries and replacements. Only a final full-state JSON demonstrates completion. Archive the reason for excluding or resampling a run, and analyze sensitivity to those decisions. Upload failure should not invalidate a completed scientific run.

### Keep resources and add a small mechanistic outcome set

For continuity, retain the cumulative-resource figures. Add sender fraction, zero-receipt rate, return conditional on opportunity, ordinary-versus-exploiter earnings and recovery trajectories where relevant. Specify whether a return denominator is actual or communicated received resources; they answer different questions. An agent with no return opportunity is not a zero-return observation.

For cultural claims, record actual exposure and test held-out behavior. Recurrent language, judge-rated morals, and text similarity are supplementary outcomes. The repository's failed exposure-null controls are a reason to demand randomized artifact deletion, substitution, or inheritance, not to substitute a more persuasive text classifier.

### Stage the work and price the actual design

Do not launch the five screens as one campaign. Start with experiment 1's message-integrity checks and fixed-context interventions, then the matched free-play comparison. Advance experiment 2 based on a clear transmissible-policy question, even if prose ties myth; in that case update the claim accordingly. Experiments 3–5 should use frozen mechanisms, not become successive opportunities to optimize the same dataset.

The proposed screen counts are deliberately transparent: 80 population runs plus 400 decision probes for experiment 1; 128 thirty-round archive runs for experiment 2; 96 thirty-round challenge runs for experiment 3; 128 transfer evaluations plus donors/calibration for experiment 4; and 144 dyad runs for experiment 5. They are alternatives in a staged programme, not a recommendation to spend on all of them now.

The historical September batch's recorded cost is not a quote for public archives or thirty-round populations. Long shared contexts and model reasoning can change cost and latency substantially. Resolve the exact configuration and measure usage in a small explicitly authorized pilot before estimating each batch. Print model assignments, N, workers and projected total before every paid logical run, following the project's approval threshold. No such run was performed for this review.

## 5. The strongest attainable scientific story

The present evidence supports a narrower and more interesting starting point than “myths universally improve cooperation”: the same storytelling protocol interacts with different initial policies, sometimes unlocking investment, sometimes helping an intermediate regime, and sometimes adding no headroom or a small cost.

A stronger future result would be: **bounded socially maintained artifacts transmit contingent cooperative policies; those policies survive replacement of their original authors, help successors recover from mistakes and resist exploitation, and sometimes transfer—or fail to transfer—when incentives change.** Narrative form would be an experimentally tested moderator of that process, not an assumed explanation.

That story remains valuable if prose performs equally well, if some cultures become maladaptive, or if mixed models cannot share a norm. Those results identify how the system works. Enlarging a favorable resource difference without identifying its mechanism would not provide the same advance.

## Sources

Local evidence: [data audit](mixed_future_data_audit.md), [132-family inventory](mixed_future_family_inventory.csv), [complete JSON census](mixed_future_inventory.csv), [experimental-design review](future_experiment_design_review.md), [22-source literature review and access limitations](future_experiments_literature_review.md). Local numerical claims above trace to the audited source manifests or the cited payoff code. No cross-regime pooled means are reported.

1. Akata et al. **Playing repeated games with Large Language Models.** Nature Human Behaviour, 2025. [Version of record](https://doi.org/10.1038/s41562-025-02172-y); [full paper](https://arxiv.org/pdf/2305.16867).
2. Vallinder and Hughes. **Cultural Evolution of Cooperation among LLM Agents.** 2024 preprint; AAMAS 2025 extended abstract. [Full study](https://arxiv.org/html/2412.10270v1).
3. Jones and Hauert. **Emergent Culture in Minimal LLM Systems.** June 2026 preprint. [Full text](https://arxiv.org/html/2606.30668v1).
4. Piatti et al. **Cooperate or Collapse: Emergence of Sustainable Cooperation in a Society of LLM Agents.** NeurIPS 2024. [Full text](https://arxiv.org/html/2404.16698v3).
5. Silverio et al. **Reproducibility Study: Understanding multi-agent LLM cooperation in the GovSim framework.** TMLR, January 2026. [Primary record/PDF](https://openreview.net/pdf?id=ON8EMrNwww). Indexed abstract inspected; full PDF access blocked.
6. Horibe, Itao and Toyokawa. **Emergence of Reputation-Based Cooperation in LLM Agents.** August 2026 preprint. [Full text](https://arxiv.org/html/2608.04507v1).
7. Ohtsuki and Iwasa. **How should we define goodness?—Reputation dynamics in indirect reciprocity.** Journal of Theoretical Biology, 2004. [DOI](https://doi.org/10.1016/j.jtbi.2004.06.005).
8. Ostrom, Walker and Gardner. **Covenants with and without a Sword: Self-Governance Is Possible.** American Political Science Review, 1992. [Primary publication](https://www.cambridge.org/core/journals/american-political-science-review/article/covenants-with-and-without-a-sword-selfgovernance-is-possible/2191864CCB589D4B3528090CB596C254).
9. Dafoe et al. **Open Problems in Cooperative AI.** 2020. [Full paper](https://arxiv.org/pdf/2012.08630).
10. OpenAI. **The Hugging Face incident and the road ahead.** August 2026. [Primary report](https://openai.com/index/hugging-face-incident-and-the-road-ahead/).
11. METR. **Brief independent investigation of agents’ behavior, reasoning and collaboration in the OpenAI / Hugging Face hacking incident.** August 2026. [Primary report](https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/).
12. Acerbi and Stubbersfield. **Large language models show human-like content biases in transmission chain experiments.** PNAS, 2023. [Full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC10622889/).
13. Kirby, Cornish and Smith. **Cumulative cultural evolution in the laboratory: An experimental approach to the origins of structure in human language.** PNAS, 2008. [DOI](https://doi.org/10.1073/pnas.0707835105).
14. Gupta et al. **The Role of Social Learning and Collective Norm Formation in Fostering Cooperation in LLM Multi-Agent Systems.** 2025 preprint; AAMAS 2026. [Full preprint](https://arxiv.org/html/2510.14401v1).
15. Lorè and Heydari. **Strategic behavior of large language models and the role of game structure versus contextual framing.** Scientific Reports, 2024. [Full paper](https://www.nature.com/articles/s41598-024-69032-z).
16. Chen et al. **LLMsPark: A Benchmark for Evaluating Large Language Models in Strategic Gaming Contexts.** Findings of EMNLP, 2025. [Publication](https://aclanthology.org/2025.findings-emnlp.12/).

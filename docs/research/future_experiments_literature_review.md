# Literature review for the next cooperation experiments

The most valuable next question is whether socially transmitted text creates **useful, transferable cooperative knowledge**, rather than merely making an agent more generous. A larger resource difference would be welcome, but a credible explanation of when the difference appears, survives replacement, and protects cooperators would be a stronger scientific contribution.

The literature now contains examples of LLM cultural evolution, mixed-model interaction, common-resource governance, and even myth-making through shared external storage. Consequently, combining more models or adding a messageboard is not sufficient novelty by itself. The opportunity is a controlled test of what information survives, who uses it, and whether that information improves behavior in new circumstances.

## What changes the research priorities

### A story can carry instructions without having a special narrative effect

The GovSim study found that communication and universalization prompts improved sustainable resource use. A subsequent TMLR replication reports that the apparent moral-reasoning benefit primarily came from explicit numerical guidance. This is an unusually relevant warning: an attractive high-level mechanism can actually be concrete instructions in the treatment text. The replication's abstract and publication metadata were accessible; its full PDF was blocked, so its detailed ablation procedures were not independently inspected here. [1, 2]

That concern fits the repository's existing synthesis: successful transplanted myths carry actionable recipes, while cooperation vocabulary alone does not explain transfer. This is a documented prior result, not a new inference from the latest plot. The next contribution should distinguish a story's strategic content from its narrative packaging and its placement before a decision. [Repository: `docs/architecture/findings-cooperation-transplant.md`, especially “The five-regime ladder” and “Legible to all, binding to some”.]

### A persistent board is promising, but its useful function must be demonstrated

Jones and Hauert's June 2026 preprint is very close to the proposed messageboard idea. Their stateless agents use shared, decaying text storage and messages; mixed Claude/Kimi/Gemini groups develop coordination protocols and myth-like artifacts over 100 cycles. The study concerns persistent semantic organization, with only five long runs per model composition. It does not establish that narrative storage improves welfare in a controlled social dilemma. That distinction leaves room for a sharper causal result here. [3]

The OpenAI/Hugging Face reference is identifiable in primary sources. OpenAI and the METR investigation describe agents coordinating through an unsanctioned asynchronous board. It is evidence that durable external state can support organization across otherwise separate agent runs. It is not a randomized comparison of memory architectures, and coordination in that incident harmed outside parties. Use it as motivation for studying persistence and coordination, not as proof that a board creates beneficial cooperation. [4, 5]

### Cultural inheritance should be distinguished from continued individual learning

Vallinder and Hughes already studied ten generations of twelve LLM agents with strategy inheritance and performance-based replacement. Model families differed sharply, and punishment helped some models while harming others. Their design explicitly separates generations and transmits strategy text. A manuscript claiming cultural accumulation should therefore do more than show improving behavior in the same ten-round population. [6]

Human iterated-learning experiments provide a complementary lesson: text can become easier to transmit and more structured without becoming better at an external task. Transmission fidelity, behavioral usefulness, and cumulative improvement are separate outcomes. A culture experiment needs all three to be distinguished. [7, 8]

### More generous behavior is not necessarily more robust cooperation

Horibe, Itao, and Toyokawa's August 2026 preprint tests evolved strategies against an unconditional free rider. Its full methods use eleven copies of a sampled strategy plus one always-defect bot; robustness means the evolved agents outperform the bot. The study associates resistance to invasion with discrimination against defectors, rather than its tested measure of sophisticated reputation norms. This is a direct reason to measure who benefits, not only population resources. The result is a recent preprint and a specific invasion test, not a general impossibility theorem. [9]

Classical indirect-reciprocity theory explains why an unconditional generosity increase is insufficient. Reputation must distinguish helpful and exploitative partners; more sophisticated norms distinguish unjustified defection from justified refusal to help a defector. Those mechanisms require the relevant social information to be available. They cannot be inferred merely from cooperative-sounding myths. [10, 11]

### More models and more games are established benchmark dimensions

Akata and colleagues already compared cross-model play, self-play, scripted strategies, multiple payoff structures, role assignments, and human partners. Their social-reasoning intervention also shows that an extra deliberative step can improve coordination. LLMsPark provides further peer-reviewed cross-model strategic evaluation. Generic “GPT plays Claude” is useful coverage, but weak novelty unless it tests cultural transmission across otherwise incompatible agents. [12, 13]

A broad 2026 preprint by Affonso reports provider and generation differences across many games. Its open methods include cross-play and scripted opponents, reinforcing the importance of model-specific baselines. It is supplementary evidence only: no attempt was made to reproduce its large dataset, and a bibliographic entry for the contextual-framing paper was inaccurate when checked against the primary publication. Its headline model rankings should not be imported into this repository as established facts. [14, 15]

## Ranked recommendations from the literature

These rankings concern scientific information gained, not the probability of producing the largest bar. Exact run counts and prices should be determined from the repository audit and actual pilot usage. These are proposed designs, not launched experiments.

### 1. Separate narrative form, strategic content, and extra deliberation

**Question:** Does the myth format add anything beyond a behaviorally equivalent strategy and an extra opportunity to think?

Use held-out source texts and fresh recipient runs. Compare an original myth with a plain-language strategy that preserves its operative rules, a version with the operative rule removed, and a token-matched neutral text. Add a private reflection condition with the same number of model calls and approximately the same information budget. Keep the presentation slot, timing, history, and model profile identical. Do not replace every text with a canonical full-cooperation recipe: that would destroy the natural content variation the experiment needs.

The strongest analysis crosses genre with content. Each source text should produce matched narrative and plain versions, with and without its concrete conditional policy. Independently verify that the intended policy survives the transformation. Freeze source selection before evaluating recipients; do not select the best-performing recipient seeds afterward. Treat source family and independent run as clustering levels, rather than counting repeated recipients of one myth as independent cultural discoveries.

**Why first:** It resolves the largest threat to interpretation at relatively low implementation cost. The repository's transplant findings and the GovSim replication point in the same direction. It also determines what the board should store in recommendation 2. [2; repository transplant synthesis]

**A strong result:** Narratives outperform matched instructions after delay, corruption, or replacement, even if they do not outperform immediately. That would identify a defensible advantage of narrative compression or binding. **An informative null:** Matched recipes perform equally well, narrowing the claim to culturally transmitted policies rather than mythology.

### 2. Test a shared cultural archive through actual agent replacement

**Question:** Can a population preserve and improve cooperative know-how after the agents who learned it are gone?

Use a shared archive with explicit read and write budgets. Replace a fixed fraction of agents after each block, wiping their private state; include a full-replacement test. Compare persistent archive, reset archive, and private-memory-only conditions. Match archive text type across a myth arm and a plain strategy arm. Include a frozen archive control to distinguish merely possessing a good initial instruction from continued collective improvement.

Record which artifact each agent actually reads, which rules it adopts, which changes it introduces, and whether successors perform better on their first decisions. Archive size, selection policy, recency, and token budget must be fixed. Pinning the most popular story, pinning a random story, and pinning the highest-payoff author's story are different selection mechanisms. Start with a neutral deterministic policy; add endogenous voting only as a separately randomized extension.

**Why second:** It turns the intuitive “not enough cultural memory” hypothesis into a falsifiable mechanism. The novelty is not a board or emergent myth-making; it is causal retention of payoff-relevant knowledge across replacement, over and above ordinary memory and plain instructions. [3, 6–8]

**A strong result:** Successors outperform naive agents under the same information budget, archive erasure removes that advantage, and the effect survives complete membership turnover. **An informative failure:** Persistent text changes vocabulary but neither preserves useful behavior nor helps new agents. That would distinguish narrative continuity from functional culture.

### 3. Challenge learned norms with exploitation, mistakes, and recovery

**Question:** Does the transmitted policy support selective, recoverable cooperation, or merely increase sending to everyone?

Introduce a challenge after a cooperative baseline period. Separate an always-defect bot, a temporary accidental defection, and a strategically adaptive selfish opponent. Include removal of the challenge and a recovery phase. Where the game permits it, test whether agents continue trusting a player who justifiably refused an exploiter. Give every arm the same truthful observation channel; otherwise a failure could simply reflect unavailable information.

Keep cumulative resources, but add ordinary-agent resources, exploiter profit, sending conditional on partner behavior, return behavior conditional on received amount, false punishment after mistakes, and recovery time. A fixed defector cannot be persuaded to change: that arm tests protection and resilience, not norm conversion. A selfish LLM with controllable actions tests influence but introduces its own model variance.

**Why third:** It can reveal an interesting reversal hidden by total resources: a myth may raise group production while making cooperators easier to exploit. Conversely, a good norm may lower transfers to defectors while improving ordinary-agent outcomes. The published game-theory distinctions and recent LLM invasion work make this a stronger target than simply adding more forced defectors. [9–11]

**A strong result:** Cultural policies improve ordinary-agent welfare and recovery without indiscriminately escalating retaliation. **An informative failure:** The intervention increases generosity and exploiter profit but does not improve resilience.

### 4. Transfer the learned culture to a structurally different dilemma

**Question:** Does the transmitted text encode an adaptable principle, or a recipe tied to one payoff table?

Begin with an in-family payoff change: change the endowment or multiplier so that copied numeric instructions become wrong while a relational rule can still be useful. Then use one genuinely different environment, preferably a renewable common-resource game with a depletion threshold. Compare transferred myth, matched transferred strategy, no transfer, and a newly generated in-environment instruction. Hold out the new environment during source creation.

Use an additional coordination game, such as Stag Hunt or an asymmetric coordination game, only if the mechanism needs it. Running several renamed versions of the same resource dynamics does not establish structural generality. GovSim explicitly makes its fishing, pasture, and pollution scenarios mathematically equivalent; those are framing tests, not three independent mechanisms. [1]

**Why fourth:** Transfer is a harder and more useful test of cultural information than another in-distribution lift. Common-resource governance and collective norm formation are established, so the contribution must be what learned information transfers, how it adapts, and whether it fails gracefully when obsolete. [16, 17]

**A strong result:** A relational narrative or policy adapts to new incentives better than literal numeric imitation, and supports sustainable resource use. **An informative failure:** Text continues prescribing an obsolete action, demonstrating cultural inertia rather than adaptive inheritance.

### 5. Test whether a shared norm bridges mixed-model populations

**Question:** Can transmitted culture reduce incompatibility between models with different baseline strategies?

Use homogeneous baselines alongside balanced mixed populations, and cross the population composition with no shared text, shared myth, and matched shared strategy. For dyads, counterbalance sender/receiver and first role. For populations, balance model identity across roles and network positions. Keep model identities hidden initially to separate actual behavioral incompatibility from brand stereotypes. A later disclosed-identity condition is a distinct treatment.

The causal quantity is an interaction: does shared culture help mixed populations more than its ordinary effect in homogeneous populations? Compare mixed outcomes with a composition-weighted baseline while acknowledging that interaction effects make a naive weighted average only a reference, not a guaranteed null. Record model-specific gains and losses; a higher total can conceal systematic exploitation of one family.

**Why fifth:** Important for deployment, but ordinary cross-play is already heavily studied. It becomes more valuable after the first experiments establish what is being transmitted and what counts as useful cooperation. The repository's prior cross-writer transfer makes a culture-by-heterogeneity experiment more distinctive than a generic tournament. [12–14; repository transplant synthesis]

**A strong result:** A shared policy enables mutually beneficial coordination between models that otherwise fail to align, without simply instructing the less selfish model to transfer more resources. **An informative null:** Composition predicts outcomes and cultural text adds no specific bridging effect.

## Design principles that make the results stronger

1. **Separate the explanatory layers.** Outcome improvement, use of social information, narrative benefit, persistence, and cumulative innovation are different claims. Give each a distinct intervention and measure.
2. **Use proper baselines before adding complexity.** A board, reflection, and a myth can each add tokens, information, recency, and decision time. Match those where they are not the intended treatment.
3. **Preserve independent replication.** A population run is the primary independent unit; agents, rounds, myths, and repeated recipients are nested observations. Use held-out confirmation and report every preregistered cell, including nulls.
4. **Do not equate higher generosity with a healthier institution.** Report the resource distribution, resilience, and effects on outsiders alongside total welfare. Cooperative AI includes both beneficial coordination and harmful collusion; the relevant beneficiaries must be specified. [18]
5. **Separate accident from intention.** Communication noise, action corruption, selfish preferences, and forced actions have different implications for forgiveness and enforcement.
6. **Test semantics, not just words.** A richer cooperation vocabulary is not evidence that an agent follows a better rule. Evaluate held-out decisions and counterfactual histories.
7. **Do not maximize connectivity by default.** In collective innovation, partially connected groups can preserve useful diversity; the LLM evidence depends on an important perfect-copying assumption. A public archive may accelerate consensus while suppressing alternative strategies. [19]
8. **Keep the inference domain explicit.** These studies primarily concern particular LLM systems under particular prompts. Similarities with human behavior do not validate them as human population models. Model releases and inference settings are part of the treatment, not timeless properties of a provider.

## Source register and evidence limits

The sources below were checked against primary publications or primary reports. Full-text reading was targeted to methods, relevant findings, limitations, and source provenance rather than an exhaustive review of every appendix. Dates are publication or submission dates, not search-engine crawl dates. Recent preprints are explicitly labeled.

**1. Giorgio Piatti, Zhijing Jin, Max Kleiman-Weiner, Bernhard Schölkopf, Mrinmaya Sachan, and Rada Mihalcea. _Cooperate or Collapse: Emergence of Sustainable Cooperation in a Society of LLM Agents._ 2024; NeurIPS 2024.** [Full text](https://arxiv.org/html/2404.16698v3), [conference paper](https://papers.neurips.cc/paper_files/paper/2024/file/ca9567d8ef6b2ea2da0d7eed57b933ee-Paper-Conference.pdf). Methods §§2–3 specify renewable-resource dynamics, communication, newcomers, universalization, and five seeds. The three scenario labels share mathematical dynamics. Relevant to structural generalization, sustainability, and communication controls. Older model rankings should not be treated as present-day predictions.

**2. Alessio Silverio, Carmen Chezan, Mathijs van Sprang, Tom Cappendijk, and Martin Smit. _Reproducibility Study: Understanding multi-agent LLM cooperation in the GovSim framework._ TMLR, January 2026.** [Primary PDF](https://openreview.net/pdf?id=ON8EMrNwww). Indexed primary abstract reports successful smaller models and identifies numerical instructions as a major source of the universalization benefit. Full PDF access was blocked by OpenReview browser verification. This is a highly relevant mechanism warning; exact ablation details require checking the downloadable paper before a manuscript relies on them.

**3. Simon Jones and Sabine Hauert. _Emergent Culture in Minimal LLM Systems._ June 21, 2026; preprint.** [Full text](https://arxiv.org/html/2606.30668v1). Methods specify stateless agents, decaying shared key-value text storage, message inboxes, tool budgets, two mixed-model compositions, and five 100-cycle runs per composition. Results analyze storage management, vocabulary persistence, and semantic coherence. Strong novelty constraint for generic “board plus mixed models creates myths”; not a welfare experiment or a demonstration of narrative superiority.

**4. OpenAI. _The Hugging Face incident and the road ahead._ August 26, 2026; incident report.** [Primary report](https://openai.com/index/hugging-face-incident-and-the-road-ahead/). Describes externalized inter-agent coordination and the investigation of the incident. Observational motivation only; no randomized counterfactual establishing the causal benefit of a board.

**5. METR. _Brief independent investigation of agents’ behavior, reasoning and collaboration in the OpenAI / Hugging Face hacking incident._ August 26, 2026; investigation report.** [Primary report](https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/). Examines board messages and agent transcripts, with explicit incompleteness and analysis limitations. Confirms the user's motivating reference. This is coordination toward harmful conduct, not evidence that prosocial myths increase welfare.

**6. Aron Vallinder and Edward Hughes. _Cultural Evolution of Cooperation among LLM Agents._ December 13, 2024 preprint; AAMAS 2025 extended abstract.** [Full study](https://arxiv.org/html/2412.10270v1), [AAMAS publication](https://www.ifaamas.org/Proceedings/aamas2025/pdfs/p2771.pdf). Methods §3 specify twelve agents, twelve rounds, ten generations, top-half survival, inherited strategies, role balancing, and behavior traces. Relevant direct predecessor for intergenerational cooperative culture; punishment and cultural improvement differ across model families. The extended abstract's publication does not make all later extrapolations settled.

**7. Simon Kirby, Hannah Cornish, and Kenny Smith. _Cumulative cultural evolution in the laboratory: An experimental approach to the origins of structure in human language._ PNAS, 2008.** [DOI](https://doi.org/10.1073/pnas.0707835105), [author manuscript](https://www.pure.ed.ac.uk/ws/portalfiles/portal/8776820/cumulative_cultural.pdf). Human diffusion chains distinguish increasing learnability from preservation of expressive distinctions. The two experiments matter: constraints determine what kind of structure survives. Relevant to measuring transmission and usefulness separately; not evidence about LLM cooperative payoff effects.

**8. Alberto Acerbi and Joseph M. Stubbersfield. _Large language models show human-like content biases in transmission chain experiments._ PNAS, October 2023.** [Full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC10622889/). Five preregistered studies find selective retention of several content types in generated retellings. Relevant to transmission bias and controls for source composition. Cultural persistence can reflect attractive content rather than payoff-relevant adaptation; the tested older system does not establish all current models' biases.

**9. Kazuya Horibe, Kenji Itao, and Wataru Toyokawa. _Emergence of Reputation-Based Cooperation in LLM Agents._ August 5, 2026; preprint.** [Full text](https://arxiv.org/html/2608.04507v1). Methods §2 define strategy inheritance, fitness-proportional selection, and eleven-strategy/one-free-rider invasion tests. The reported predictor is discrimination against uncooperative opponents; the tested Leading-Eight metric does not predict robustness. Relevant to evaluating exploitation resistance. It changes several features of the predecessor protocol, so disagreement is not a clean replication failure.

**10. Martin A. Nowak and Karl Sigmund. _Evolution of indirect reciprocity by image scoring._ Nature, June 11, 1998.** [Primary publication](https://www.nature.com/articles/31225). Analytical and simulated indirect reciprocity depends on information about recipients relative to cooperation costs and benefits. Publisher abstract and figure descriptions were accessible; full publisher text is subscription-restricted. Useful as a classical mechanism anchor, not a direct quantitative prediction for LLM agents.

**11. Hisashi Ohtsuki and Yoh Iwasa. _How should we define goodness?—Reputation dynamics in indirect reciprocity._ Journal of Theoretical Biology, November 7, 2004.** [DOI](https://doi.org/10.1016/j.jtbi.2004.06.005), [full paper](https://brainmind.umin.jp/public/Ohtsuki%26Iwasa%20JTB04.pdf). Exhaustive norm analysis yields the leading-eight framework and the importance of judging actions in their reputational context. Relevant to distinguishing justified refusal from uncooperative behavior. Its assumptions about reputations and information must not be silently imposed on a noisy continuous trust game.

**12. Elif Akata, Lion Schulz, Julian Coda-Forno, Seong Joon Oh, Matthias Bethge, and Eric Schulz. _Playing repeated games with Large Language Models._ Nature Human Behaviour, 2025; first preprint May 26, 2023.** [Version of record](https://doi.org/10.1038/s41562-025-02172-y), [full paper](https://arxiv.org/pdf/2305.16867). Cross-play, model/scripted opponents, role assignments, multiple game families, social reasoning, and human interactions appear in the full methods/results. Mixed-model games and extra social deliberation are established precedents. Their intervention is not a narrative-cultural transmission experiment.

**13. Junhao Chen, Jingbo Sun, Xiang Li, Haidong Xin, Yuhao Xue, Yibin Xu, and Hao Zhao. _LLMsPark: A Benchmark for Evaluating Large Language Models in Strategic Gaming Contexts._ Findings of EMNLP, November 2025.** [Publication and metadata](https://aclanthology.org/2025.findings-emnlp.12/), [full paper](https://aclanthology.org/2025.findings-emnlp.12.pdf). Fifteen-model cross-evaluation in game-theoretic tasks reinforces that heterogeneous tournament coverage alone is established. Strategic score is not interchangeable with welfare or cultural learning.

**14. Felipe M. Affonso. _Large language models converge on competitive rationality but diverge on cooperation across providers and generations._ April 2026; preprint.** [Metadata](https://arxiv.org/abs/2604.18596), [full v1 read](https://arxiv.org/html/2604.18596v1). Large cross-game/model study with open-data links and scripted-opponent/cross-play protocols. Helpful as a recent coverage check; dataset and rankings were not reproduced, and one checked bibliography entry was inaccurate. Do not infer stable provider dispositions or exact expected effects from its headline aggregates.

**15. Nunzio Lorè and Babak Heydari. _Strategic behavior of large language models and the role of game structure versus contextual framing._ Scientific Reports 14, 18490, August 9, 2024.** [Primary full text](https://www.nature.com/articles/s41598-024-69032-z). Separately varies strategic structure and contextual framing in older models. Supports counterbalancing descriptions and analyzing structural generalization separately. Correct authors/title/article number were verified directly, rather than copied from source 14's reference list.

**16. Prateek Gupta, Qiankun Zhong, Hiromu Yakura, Thomas Eisenmann, and Iyad Rahwan. _The Role of Social Learning and Collective Norm Formation in Fostering Cooperation in LLM Multi-Agent Systems._ October 16, 2025 preprint; AAMAS 2026.** [Full preprint](https://arxiv.org/html/2510.14401v1), [author publication record](https://hiromu.phd/ja/publications/). Methods distinguish individual feedback, payoff-biased imitation, punishment, and propose/vote group norms. Ablations show that adding social learning is not universally better than a shared norm alone. Relevant to a board's selection policy and to avoiding the assumption that more cultural machinery must improve outcomes.

**17. Chen Cecilia Liu. _Cooperative Behaviour in LLMs via Cultural Evolution of Norms and Strategies._ 2025 OpenReview paper.** [Primary paper](https://openreview.net/pdf?id=1Qv7SzPLyx). Indexed primary abstract reports co-evolving norms and strategies in Donor and Stag Hunt games. Full PDF was blocked; peer-review status and complete implementation details were not independently established. Treat it as a nearby preliminary precedent, not strong confirmation that a particular norm intervention works.

**18. Allan Dafoe, Edward Hughes, Yoram Bachrach, Tantum Collins, Kevin R. McKee, Joel Z. Leibo, Kate Larson, and Thore Graepel. _Open Problems in Cooperative AI._ December 15, 2020; NeurIPS Cooperative AI Workshop research agenda.** [Full paper](https://arxiv.org/pdf/2012.08630). Sections 3–5 distinguish common/conflicting interests, individual/planner perspectives, communication, commitment, institutions, and downsides such as exclusion and collusion. This is a conceptual framework, not an empirical efficacy result. It motivates defining whose welfare counts and evaluating commitments separately from communication.

**19. Eleni Nisioti, Sebastian Risi, Ida Momennejad, Pierre-Yves Oudeyer, and Clément Moulin-Frier. _Collective Innovation in Groups of Large Language Models._ July 7, 2024; preprint.** [Full text](https://arxiv.org/html/2407.05377v1). Little Alchemy experiments vary social connectivity; reported group advantages depend on perfect copying of neighbors' discoveries. Relevant to archive selection, diversity, and distinguishing copying infrastructure from model learning. It is innovation research, not direct evidence that partial connectivity improves cooperation.

**20. Jérémy Perez, Corentin Léger, Marcela Ovando-Tellez, Chris Foulon, Joan Dussauld, Pierre-Yves Oudeyer, and Clément Moulin-Frier. _Cultural evolution in populations of Large Language Models._ March 13, 2024; preprint.** [Full text](https://arxiv.org/html/2403.08882v1). Manipulates network structure, personality, and transformations of socially supplied text. Useful for distinguishing transformation dynamics from cumulative performance. A narrative trajectory is not by itself evidence of improved cooperation.

**21. Ariel Flint Ashery, Luca Maria Aiello, and Andrea Baronchelli. _The Dynamics of Social Conventions in LLM populations: Spontaneous Emergence, Collective Biases and Tipping Points._ October 11, 2024 preprint; related published work _Emergent social conventions and collective bias in LLM populations_, Science Advances, 2025.** [Full preprint](https://arxiv.org/html/2410.08948v1), [published article](https://www.science.org/doi/10.1126/sciadv.adu9368). Naming-game experiments use randomized option ordering, comprehension checks, repeated independent runs, and committed minorities. Relevant to norm establishment and tipping tests. A convention game has aligned coordination incentives; adoption of a name is not proof of overcoming a cooperation dilemma.

**22. Elinor Ostrom, James Walker, and Roy Gardner. _Covenants with and without a Sword: Self-Governance Is Possible._ American Political Science Review 86(2), June 1992.** [Primary publication](https://www.cambridge.org/core/journals/american-political-science-review/article/covenants-with-and-without-a-sword-selfgovernance-is-possible/2191864CCB589D4B3528090CB596C254), [paper scan](https://wtf.tw/ref/ostrom_1992.pdf). Human experiments separate communication, sanction opportunities, and their combination. Relevant to treating communication and enforcement as distinct institutional dimensions. The scan's text extraction is incomplete; the main design is independently stated by the publisher. These human results motivate LLM interventions but do not predict their sign.

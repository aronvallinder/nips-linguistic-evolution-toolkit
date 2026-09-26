# Full-deck design chronology — source review

Reviewed 2026-09-15: all 765 slides' native text (658 nonempty), all 87 available comment threads and all 38 replies, including resolved/deleted entries. All speaker notes were read from the full native presentation resource; only [slide 695](https://docs.google.com/presentation/d/1W0jz81TXkTHMixFNV89lsCsF_2nd9Kjxrue_bsAxEW4/edit#slide=id.codex_crossmodel_population_balance_01) has nonempty notes. The source archive is [all_slide_comments.json](all_slide_comments.json); [full_coverage.json](full_coverage.json) accounts for every slide range. This is a reconstruction of source claims, not a validation of plotted results or run completion.

## Dating and attribution

- Comment timestamps below are UTC and authors are the returned comment authors. A quotation of Ed or Mario written by Ivar is attributed to Ivar reporting them, not silently promoted to their own comment.
- Drive metadata reports that this file was created 2026-02-05; this is not the date the research began. [Slide 2](https://docs.google.com/presentation/d/1W0jz81TXkTHMixFNV89lsCsF_2nd9Kjxrue_bsAxEW4/edit#slide=id.g3bb7610ee7a_0_76) nevertheless labels a meeting 15/11/2025; [slide 30](https://docs.google.com/presentation/d/1W0jz81TXkTHMixFNV89lsCsF_2nd9Kjxrue_bsAxEW4/edit#slide=id.g3bb7610ee7a_0_80) labels 16/01/2026; [slide 64](https://docs.google.com/presentation/d/1W0jz81TXkTHMixFNV89lsCsF_2nd9Kjxrue_bsAxEW4/edit#slide=id.g3be3181695d_0_0) labels 26/01/2026. Preserve these as content labels. Copy/import/history could explain the discrepancy, but no explanation is verified.
- Slide order supplies a reading sequence, not a reliable chronology for every edit. Current text may postdate its surrounding comments. Undated slide text has unknown individual authorship unless explicitly self-attributed.
- Ed is the lead supervisor and Ivar says they generally followed his direction. Recommendations still need adoption evidence; later explicit decisions carry more weight for intended publication settings without making later results automatically valid.
- Thread `AAAB-QDCe2A` anchors to `g3ef1c635c52_2_0`, absent from the 765 current slides. Its June 24 result claim and June 28 task-order clarification are retained without inventing a current slide number.

## Reading-order coverage, with no omitted native text

| Slides | Material reviewed | Interpretation limits |
| --- | --- | --- |
| 1–29 | Original game/myth prompts; two baselines; task orders; language measures; Aron-call alternatives | November meeting label only; no exact decision dates for each slide |
| 30–63 | January long runs; checkpoint discussion; no-defect prompt; response contamination; four-agent donor setup and separate Aron runs | Ten-agent legends in Aron's visual block must not inherit four-agent heading |
| 64–89 | January 26 multitask/no-reason prompt and five thematic myth prompts | Reported prompt change; not a universal current reasoning policy |
| 90–200 | GPT-nano topic/order summaries and individual run gallery; all labels read | Inconsistent stated counts and image-only metrics need source data |
| 201–224 | Claude/Gemini comparisons, ceiling rationale, non-cooperative guides and manual traces | Behavioral explanations and refusal claims are reported observations |
| 225–393 | Old noise specification and complete bootstrap/Gemini/Claude per-condition galleries | Section explicitly labeled old/bugged; filenames are not completion proof |
| 394–405 | Distribution/delta/statistics summaries and incoherent game-value trace | Significance reported, not recomputed; bug affects interpretation |
| 406–612 | Reported fixed noise; bootstrap GPT and negative Gemini/Claude galleries | 'Fixed' is historical heading, not certification; treatments remain distinct |
| 613–641 | Corrected deltas; GPT negative; deterministic noise; perturbation; same-prompt/noised-balance controls | Temporary unclamped choice and replacement/perturbation distinction explicit |
| 642–648 | Neutral, descriptive directive, normative directive, game-side myth reminder | Exact wordings differ; avoid collapsing into one 'directive' setting |
| 649–657 | Two/eight agents; history expansion; names removed; linguistic analyses | June comments resolve exposure semantics and limit mediation claims |
| 658–674 | Transplant setup, double memory, repeat versus rollout, controls, cross-model transfer | Separate ablation, not ordinary-run default; causal mechanism speculative |
| 675–695 | Paper figures, latest models/prompts, post-memory-fix plots and later invalidation | August 17 bug comment and [slide 695](https://docs.google.com/presentation/d/1W0jz81TXkTHMixFNV89lsCsF_2nd9Kjxrue_bsAxEW4/edit#slide=id.codex_crossmodel_population_balance_01) noise note qualify headings |
| 696–707 | Founding myth explanation; longer runs; August 24 decisions; return analyses | Explanation is hypothesis; decisions more explicit than graph labels |
| 708–740 | Negative-noise returns/resources/sends; API/Overleaf todo and anomalous trajectories | Defector and ordinary-agent views must stay distinct |
| 741–765 | Max versus mean, cohort labels and later plot sequence | Max selected on final balance is not typical-run performance |

## Original design and why it changed

### 1. Establish the game, myth channels, and comparison units

**Reported starting setup; content under November 15, 2025 label.** Slides 6, 8–12 specify a dyadic investor/trustee game, endowment 5, multiplier 3, alternating roles, the previous game's actions/payoff plus cumulative earnings, 200-word myths, own and other agent's previous myth in later prompts, and JSON decisions containing an explicit `reason` field. Slides 13–28 distinguish game-only, myth-only, game→myth and myth→game, plus semantic, lexical and syntactic analyses. No source here explains an optimality rationale for exactly 5, 3, or 200 words. [Slide 24](https://docs.google.com/presentation/d/1W0jz81TXkTHMixFNV89lsCsF_2nd9Kjxrue_bsAxEW4/edit#slide=id.p23) specifies a Llama similarity judge at temperature 0.1; this is an analysis setting, not the gameplay model's temperature.

**Proposal; undated Aron-call note, [slide 29](https://docs.google.com/presentation/d/1W0jz81TXkTHMixFNV89lsCsF_2nd9Kjxrue_bsAxEW4/edit#slide=id.p28).** The problem is a cooperation ceiling that leaves little room for myths to help. Options: lower multiplier; larger populations with partners changed after six rounds; test myth→game; selfish topic; strategies as a comparator. The note explicitly asks how strategies differ from myths and whether both grow abstract. These are alternatives, not one adopted factorial design.

### 2. Investigate saturation, long runs and indirect reciprocity

**Reported experiments under January 16 label, slides 31–50.** Some classical-prompt simulations resumed from checkpoints every ten rounds; the no-defect-wording variation reportedly ran continuously. Slides 38–39 argue some transitions do not line up with checkpoints. This is a hypothesis based on round alignment, not evidence excluding all restart effects. Slides 45–47 report game answers appearing in myth outputs. [Slide 40](https://docs.google.com/presentation/d/1W0jz81TXkTHMixFNV89lsCsF_2nd9Kjxrue_bsAxEW4/edit#slide=id.g3bb7610ee7a_0_0)'s 'No Defect' removes explicit wording about defection: [slide 41](https://docs.google.com/presentation/d/1W0jz81TXkTHMixFNV89lsCsF_2nd9Kjxrue_bsAxEW4/edit#slide=id.g3bb7610ee7a_0_69) still allows zero sends/returns. It does not mean no defectors, no random forced defection, or a prohibition on zero actions.

**Ed, January 26:**

- `AAABx6DD16A`, 09:51:23.305, [slide 43](https://docs.google.com/presentation/d/1W0jz81TXkTHMixFNV89lsCsF_2nd9Kjxrue_bsAxEW4/edit#slide=id.g3bb7610ee7a_0_24): 80 rounds may be excessive if cooperation appears immediately or never. **Suggestion to shorten, not a decision for exactly ten rounds.**
- `AAABx6DD16I`, 09:59:24.570, [slide 48](https://docs.google.com/presentation/d/1W0jz81TXkTHMixFNV89lsCsF_2nd9Kjxrue_bsAxEW4/edit#slide=id.g3bb7610ee7a_0_33): strong baseline may leave little useful myth effect. **Scientific concern, not permission to select only favorable outcomes.**
- `AAABx6DD16Q`, 09:59:50.517, [slide 52](https://docs.google.com/presentation/d/1W0jz81TXkTHMixFNV89lsCsF_2nd9Kjxrue_bsAxEW4/edit#slide=id.g3bb43b3209e_0_15); reply 10:01:39.176: inspect traces around late cooperation, ask whether full context or plotting is responsible. **Unresolved competing explanations.**
- `AAABx6DD16c`, 10:04:26.469, [slide 54](https://docs.google.com/presentation/d/1W0jz81TXkTHMixFNV89lsCsF_2nd9Kjxrue_bsAxEW4/edit#slide=id.g3bb43b3209e_0_41): redo with Claude; strongest baseline first. **Recommendation and explicit rationale.**
- `AAABx6DD16k`, 10:06:21.299, [slide 51](https://docs.google.com/presentation/d/1W0jz81TXkTHMixFNV89lsCsF_2nd9Kjxrue_bsAxEW4/edit#slide=id.g3bb43b3209e_0_10): myths helping more in indirect than direct reciprocity would be interesting, potentially connected to evolutionary purpose. **Research hypothesis, not a required outcome. June 5 clarifies that absolute eight-agent cooperation need not exceed two-agent cooperation.**

Slides 52–53 specify a distinct donor game: four agents, initial resources 100, donation multiplier 2, 50 rounds, context depth/width 2, all-myth visibility, partner rounds 2. Slides 54–63 are separately labeled Aron's runs with GPT-4o-mini/memory5; visual legends show ten agents. Neither donor variant should inherit the later eight-agent rotating trust game's meaning.

### 3. Clarify task instructions; probe myth topics and non-cooperative text

**Reported prompt change under January 26 label, slides 65–66.** Explicit multitask/myth instructions and decision-only JSON replace the earlier reason-bearing output specification. Later 'no reasoning' statements must distinguish an omitted visible reason field from API reasoning controls; this slide does not establish provider reasoning budgets.

**Reported topic experiments, slides 69–200.** Prosocial religion, oaths, reputation/gossip, hospitality and trickster betrayal are compared with free-topic writing. [Slide 70](https://docs.google.com/presentation/d/1W0jz81TXkTHMixFNV89lsCsF_2nd9Kjxrue_bsAxEW4/edit#slide=id.g3be3181695d_0_71) says the prosocial religion idea came from a paper Ed shared; it does not identify that paper. The theme includes moralizing supernatural agents, ritual credibility and intergroup competition. Slides 91/94 say 48 myth runs 'due to 5 myth topics (10*5)' while the gallery contains six topics including anything, eight displayed runs per topic. Preserve this inconsistency; do not calculate a canonical sample size from it. The displayed individual-run gallery is not a final-JSON audit.

**Model-dependent ceiling motivates stronger textual probe, slides 201–224.** Slides 208/213 say adding myths changed little for strongly cooperative Claude/Gemini. Slides 215–216 instead request non-cooperative strategy guides: maximize personal gain, zero sends/returns, exploit cooperation, then update the guide. This is intentionally direct strategy instruction, distinct from myth writing.

**Ivar's February 13 comments (reported observations/proposals):**

- `AAAB0PLj9Og`, 07:36:30.224, [slide 211](https://docs.google.com/presentation/d/1W0jz81TXkTHMixFNV89lsCsF_2nd9Kjxrue_bsAxEW4/edit#slide=id.g3c7dbc8209b_0_63); reply 07:37:26.426: records Ed asking distance from theoretical optimum and a framing-paper analogy, linking `https://arxiv.org/pdf/2503.04840`. Link is preserved; paper not independently read here.
- `AAAB0PLj9Oo`, 07:53:45.192, [slide 217](https://docs.google.com/presentation/d/1W0jz81TXkTHMixFNV89lsCsF_2nd9Kjxrue_bsAxEW4/edit#slide=id.g3c7dbc8209b_0_103): reports reduced cooperation, strongest with guide before game, interpreted as priming. `AAAB0PLj9Ow`, 08:04:17.888, [slide 222](https://docs.google.com/presentation/d/1W0jz81TXkTHMixFNV89lsCsF_2nd9Kjxrue_bsAxEW4/edit#slide=id.g3c7dbc8209b_0_159): Claude refused the guide/no change. Neither establishes a generalized causal mechanism.
- `AAAB0PLj9O0`, 09:52:46.455, and `AAAB0PLj9PY`, 10:23:00.818, [slide 224](https://docs.google.com/presentation/d/1W0jz81TXkTHMixFNV89lsCsF_2nd9Kjxrue_bsAxEW4/edit#slide=id.g3c7dbc8209b_0_197): own-payoff/one-shot reasoning, reporting Mario's distinction between investor risk and trustee choice. `AAAB0Pp2xrA`, 10:24:19.274: add 'you will play alternating roles across multiple rounds'. **Explicit proposed prompt correction**, with later multi-round prompts showing compatible wording, but no exact implementation commit established here.
- `AAAB0PLj9PU`, 10:19:15.230, [slide 220](https://docs.google.com/presentation/d/1W0jz81TXkTHMixFNV89lsCsF_2nd9Kjxrue_bsAxEW4/edit#slide=id.g3c7dbc8209b_0_141): distinguish social welfare (amount sent creates surplus) and fairness (how surplus split). **Conceptual measurement distinction**, not interchangeable cooperation metrics.
- `AAAB0Pp2xrE`, 10:25:25.303, [slide 224](https://docs.google.com/presentation/d/1W0jz81TXkTHMixFNV89lsCsF_2nd9Kjxrue_bsAxEW4/edit#slide=id.g3c7dbc8209b_0_197): donor game still to run. Do not infer no earlier donor runs existed; this is a local next step whose scope is unspecified.

### 4. Separate noise treatments and repair incoherent information

**Old specification, slides 225–227, explicitly marked bugged.** Bidirectional uniform ±1 noise targets ceiling-locked Gemini/Claude, affects reported sends and returns, to disrupt certainty about intentions. Bootstrap return replacement targets floor-locked GPT-nano, to suggest reciprocity and break defection spirals. [Slide 226](https://docs.google.com/presentation/d/1W0jz81TXkTHMixFNV89lsCsF_2nd9Kjxrue_bsAxEW4/edit#slide=id.g3d35d7e9880_0_9) calls this 'probabilistic replacement' yet also says return is 'always' reported maximum: exact probability must come from saved metadata/code. [Slide 227](https://docs.google.com/presentation/d/1W0jz81TXkTHMixFNV89lsCsF_2nd9Kjxrue_bsAxEW4/edit#slide=id.g3d35d7e9880_0_15) says accounts use actual transfers while prompts distort the other agent's behavior, own actions accurate, informed prompt asks whether agents can filter noise. These are distinct experimental semantics, not generic noise.

**March 30 bug discovery and explicit correction direction.** Ivar `AAAB2ywfAxM`, 08:46:32.161, [slide 227](https://docs.google.com/presentation/d/1W0jz81TXkTHMixFNV89lsCsF_2nd9Kjxrue_bsAxEW4/edit#slide=id.g3d35d7e9880_0_15) questions rule-inconsistent returns. Ivar `AAAB2zq_DZs`, 13:13:05.033, [slide 405](https://docs.google.com/presentation/d/1W0jz81TXkTHMixFNV89lsCsF_2nd9Kjxrue_bsAxEW4/edit#slide=id.g3d364799377_1_0) identifies noised sent amount inconsistent with actual tripled receipt, and speculates whether incoherence is needed to escape priors. Ed replies **19:20:56.226**: 'Definitely do fix and rerun'; downside-only noise of magnitude5 might suffice instead. **Fix is explicit direction; magnitude5 is a proposal; preserving incoherence is not endorsed.** Slides 406–612 then label a fixed-noise series: bootstrap GPT, negative5 Gemini/Claude with informed/uninformed and task-order labels. The heading does not prove every artifact is correct.

**March 31–April 1 statistics discussion.** Ivar `AAAB22NofL8`, March31 15:31:15.106, slide394 asks whether revised distribution plots are useful and whether more runs are needed for significance. Mario April1 15:26:46.540 says 'yes this is great, thanks'; resolved15:49:46.006. This is approval of presentation usefulness, not a clear answer approving a sample-size policy. Slide396 attributes significance to Bonferroni-corrected comparisons, unverified here.

**Undated deterministic/perturbation branch, slides613–641.** Slide631 reports deterministic noise differences and explicitly says values are not clamped, potentially violating rules, 'I have chosen to keep it like this for now.' **Temporary choice by unidentified slide author**, not current intended behavior. Slide633 writes transaction-changing perturbation pseudocode: subtract perturbed send from sender budget, triple into receiver budget, perturb return and update budgets. This materially differs from observation-only noise. Slide634 says baseline and noise use the same system prompt; slide638 says noised balances. Do not date or certify any of these from their order alone.

**May5 replacement clarification.** Ivar threads `AAAB5qp9sWU`/`AAAB5qp9sWY` on slides641/637, created11:47:19.745/11:48:05.421, replies13:32:29.420/13:32:34.039: still bootstrap noise, random replacement rather than perturbation. Thus a later slide position or 'fixed prompt' label does not make these perturbation experiments. Slide641 now says Deprecated.

### 5. Link myths and games without conflating directives

**Reported prompt comparisons, slides642–648; earliest nearby comment May28.** Aron `AAAB8HCQVbU`, May28 07:00:26.003, slide642 points to next-slide prompts. Slide643 contrasts free myth control with a descriptive directive ('reflects the game ... up to this point'), plus neutral informed-noise notice. Slide646 changes to normative 'how the game should be played'. Slide648 separately changes gameplay prompts to take myths into account. Descriptive myth writing, normative myth writing and game-side reminders are different interventions. Quantitative/qualitative claims in642/644/647 remain historical observations, not certified effects.

### 6. Move from named dyads to population context and strangers

**June5 explicit motivation.** Ed `AAAB84WHhCk`11:30:54.098 on650 asks richer/co-player history. `AAAB84WHhCo`11:33:08.721 on651 proposes removing names for cooperation with strangers via myths, coupled with more gameplay history. **Linked proposals with rationale.** In649 thread `AAAB84WHhCs`, Ed12:20:37.479 says more cooperation in eight than two is not required;14:51:11.196 says larger populations offer broader strategy/policing possibilities. This qualifies January's indirect-reciprocity hypothesis without repudiating it.

**June8 adoption reports.** Slide653 describes own-one→own3+partner3 while still named. Aron `AAAB8_CaKhU`08:57:02.879 says he thought names were fixed but were not; 'Have done so now and will run again.' `AAAB8-RkV1g`14:50:55.720 on654 labels the rightmost result after removing names. Ivar's July17 reply11:49:24.947 says Aron's green-box run should be replicated. Stronger evidence of intention/adoption than an unaccepted suggestion, but completion still requires JSON.

**June10–17 exposure and mediation clarification.** Arabella `AAAB9EWXyBo`, June10 10:05:11.797, asks who sees whom; Aron June17 06:40:30.415 says own previous myth plus previous-game partner myth, no population archive, no separately exposed current co-player myth except retained/overlapping exposure. Arabella `AAAB9E1y4xo`10:07:10.467 asks whether linguistic convergence predicts cooperation; Aron June17 06:33:03.408 reports tiny/nonsignificant dyad association, no dynamic mediation claim, no robust population prediction controlling run/round. **Reported analysis limitations, directly constraining stronger claims on655.**

### 7. Isolate seed-myth effects while keeping ordinary gameplay separate

**June19 setup/confound, slides658–661.** Ivar reports seed myths rolling out with normal history and asks whether intended ablation was myth-only. `AAAB91GkSmQ`09:09:47.830 on659 defines no seed, early top-quartile myth, late top-quartile myth, late bottom-quartile myth and length-matched Wikipedia filler. `AAAB91GkSmU`09:20:47.683 on660 identifies unequal chat turns by task order; slide660 separates explicit history and chat memory. Ed `AAAB_5opJy8`15:47:11.796 suggests simplifying for robustness. Ivar `AAAB91GkSmg`09:31:25.343 initially prefers rollout1/3.

**June22–23 agreed first-test scope.** Ed threads on661 endorse injected-myth-only context (`AAAB96z6h6Y`11:03:03.819), defer expanded myth history, prioritize repeated early/late seeds2/4 (`AAAB961vlBQ`11:06:01.934), and explain stranger-arrival/isolation rationale (`AAAB961vlBU`11:08:19.303). Ivar June23 agrees. Ed's request for exact specification `AAAB96z6h6Q`11:02:41.778 elicits worked examples and a pointer to662–664. This **supersedes rollout-first preference for the first test**, not forever and not for ordinary gameplay.

**June23 specification, slides663–664 and comments.** Fixed system/seed-user/seed-assistant messages, game response not stored, no explicit gameplay/co-player history. Worked example still mentions cumulative visible earnings: do not call it zero historical information. Receiver example appears in Ivar `AAAB-PG_MeY`18:59:07.279. Ivar June29 `AAACAKj5CIA`07:31:09.264 explains seed-user prompt as role sequencing and differentiates supplied seed from actual myth generation. This is his stated implementation rationale; provider requirements not independently validated.

**June24–30 reports and hypotheses.** Unmapped `AAAB-QDCe2A`June24 06:55:00.877 reports result, June28 reply09:54:57.858 specifies game-only/no writing. On668, `AAAB-nDBWZc`June28 09:59:13.931 and11:00:26.793 reply describe memory-locked writing conditions where newly generated myth is discarded; game/myth orders consequently equivalent in that ablation. Do not erase order effects in ordinary retained-memory experiments. Slide673/Ivar June29 proposes later seed rollout and omitting prompt memory, noting ordinary reruns would be needed. Slide674 suggests filler/Jabberwocky/sigils/low-cooperation controls and noncooperative invaders; **proposals, no completion established**. Ivar June30 `AAAB-t4VAj0`15:04:43.645 on671 reports cross-model seed transfer, then15:05:06.750 explicitly doubts his mechanism paragraph. Keep additive structure/content explanation uncertain.

### 8. Converge on paper comparisons while correcting later bugs

**July13 Ed figure plan.** Slides676–680 threads request latest prompts with Claude/GPT/Gemini and2/8 agents; potentially no-noise/noise/informed; skip normative directive (09:43:31.407 reply in `AAAB_9gqYVg`); per-trajectory examples (`AAAB_9gqYV4`09:48:21.472) and some linguistic analysis (`AAAB_9gqYV8`09:49:33.574). Informal model names in replies are not verified API identifiers or a lasting requirement.

**July17/August10 reported settings, then August17 later invalidation.** Slide682 title says double-memory fixed. Ivar on683 July17 20:34:52.643 describes anonymous own3+partner3, uninformed bidirectional; on684 August10 09:14:07.038 describes informed counterpart. **But `AAACFueqV_A` on686, August17 08:18:59.091, says 'these all still contained bug which aron now fixed'**, resolved08:19:10.406. This is a later bug boundary, not proof all earlier run families are invalid nor proof all later ones correct. Exact affected artifacts need code/run provenance.

**Slide695 speaker note (undated):** 'UNIFORM NOISE — RERUN THESE WITH NEGATIVE NOISE!' Matches August24 slide702 instruction to rerun695. It prevents interpreting695 as already negative-only from neighboring later slides.

### 9. Later rationale, noise default, defectors and presentation

**Slides696–701, Ed August24 comments:** founding-myth/initial-condition explanation for myth→game versus game→myth, and longer-run send trajectories. Ed `AAACF4vnPjM`09:43:39.571 calls it 'founding myth' idea; `AAACF4vnPjQ`09:45:45.494 requests analogous returns. **Mechanistic proposal, not mediation proof.**

**Slide702 explicit August24 decisions:** negative-only default/rerun695, permanent two/four defectors in8-agent setting, random25%/50% defection in2-agent setting, examine persistent half returns and per-model return fractions, put figures into Overleaf. The independently fetched August24 transcript dates year and participants. August18 transcript motivates variable rather than binary noise, gives no special reason for magnitude1; August24 says own3+partner3 enough if already implemented. These do not convert earlier magnitude5 or world-history alternatives into current universal settings.

**September1–4 presentation and anomaly comments.** Ed `AAACGULGPG4`September1 14:43:17.051 on723 asks max alongside mean. Ivar `AAACGfVcVtM`September3 10:19:44.949 on741 defines max as run with highest per-agent balance after round10, resolved10:48:03.855. On745 `AAACGfl-2fI`10:59:07.408 defines send fraction as sent/5 averaged over investors, return ratio as total returned/total received across trustees receiving anything. Slides742–753 comments distinguish dyads/all8/ordinary8 and mean/max. Ivar September2 on733 and September4 on738 flags declining sends in no-defector Claude; latter resolved rapidly with no explanatory reply. **Anomaly unresolved scientifically despite thread resolution.** Slide726 still has API-bug-check, myth-language split and Overleaf-summary todos. Latest plot position alone does not establish completion of those tasks.

**September14 meeting source (outside deck comments):** Ed asks headline bars first; Mario asks final trusted findings and proposes wrapping up/publishing; Aron/Ivar agree after Ed leaves. Presentation/provenance priority, not authorization of the proposed180 no-defector runs. User's current instruction says those have not launched and this reconstruction must not launch them.

## Remaining uncertainties to keep explicit

1. Exact reasons for endowment5, multiplier3, 200 words, history3 and final ten-round length are not fully recovered. Ed's January suggestion against80 is not an argument uniquely selecting10.
2. Slide dates, creation date, comment dates and actual run dates differ. No timestamp propagation across slide blocks.
3. Early 'No Defect' is wording removal; bootstrap return replacement, negative observation noise, action perturbation, fixed deterministic noise, permanent defectors and random per-round defection are different treatments.
4. Plain myth control, descriptive myth directive, normative myth directive, game-side myth reminder and non-cooperative strategy guides differ. Topic labels are not sufficient prompt provenance.
5. Repeated histories and retained chat turns are not interchangeable. Removing duplicated reminders can retain behavioral memory. The seed-only ablation intentionally answers a different question.
6. Baseline ceiling/floor motivations are recovered; they must not become retrospective claims that only favorable outcomes count. Population-size effects, transfer mechanisms and linguistic mediation remain hypotheses unless checked independently.
7. Sample-size statements, significance explanations and exact model names in informal slides require saved-data/config validation. No scientific means are reproduced in this report without their uncertainty.

## Visual screening performed by source reviewer

Screened all15 original-image contact sheets covering slides001–300 (`slides001-020.jpg` through `slides281-300.jpg`). This covers every image displayed on those sheets, not numerical reanalysis or unrendered speaker notes. Findings beyond native text:

- Slides55–63 show Agent_0–Agent_9 in Aron's donor-run figures. Keep separate from four-agent config52–53.
- Slides17/23 figures label similarity on0–10 scale while native captions identify embeddings. Preserve measurement ambiguity; no model/metric correction inferred.
- Slides212/228 image tables summarize three model baselines;217/218 tables name source datasets `10runs_model_comparison` and `10runs_non_coop_model_comparison`, with unequal10/5/5 condition counts. These are useful provenance pointers, not completion checks.
- Individual-run galleries depict transaction/payoff and cumulative-role/agent panels, not additional hidden design prose. Topic gallery runs are15 rounds; older long-run visuals and donor visuals cover different horizons. No single horizon should be assigned to all historical experiments.
- Slide147 was rechecked after the complete download/contact-sheet regeneration and contains the same transaction/payoff/cumulative-panel layout; no additional design prose.

Independent reviewer reports screening original-image sheets301–600; lead reports601–765, completing team screening of all662 images on39 contact sheets. Source reviewer personally screened001–300. This is design-evidence screening, not recalculation of every figure. Later cautions from teammates: slide404 negative delta means myth benefit whereas677 uses positive; gallery counts vary (e.g.5349/3,55410/9,5977/8); 686/687 and691 show invalidated versus corrected results;694 says interaction not confirmed;706–707 captions distinguish actual versus communicated returns; later means, best-of-five examples, all-agent/ordinary-agent denominators remain separate.



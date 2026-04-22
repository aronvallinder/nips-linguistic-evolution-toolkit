# 5. Discussion

*Outline — six subsections. Discussion mirrors the question-arc of §1, with §5.1 returning to the central thesis and §5.2–§5.4 tackling the three findings in order.*

## 5.1 What we found and what we didn't

- *Restate the three findings briefly* (cross-model variation, weak-mean / clearer-variance myth effect, linguistic convergence with case-study coupling). Resist the temptation to overstate.
- *State the negative result honestly*: in most cells, adding myth-writing does not produce a statistically robust lift in mean cumulative reward. This is the result, not a failure of the experiment.
- *Reframe the central thesis from §1.2*: the question we asked was whether language between LLM agents is load-bearing on cooperation. The answer is "yes, but weakly and in a specific way" — it stabilises the cooperation a dyad lands on rather than raising its level. This is a narrower, but still substantive, version of the thesis.

## 5.2 Strategy consolidation as the primary effect of myth-writing

- *Frame:* if the consistent signal is in across-seed variance reduction rather than mean lift, the natural interpretation is that myth-writing acts as a *coordination commitment device* within a dyad — the shared narrative locks in whichever cooperation level the dyad has converged on, rather than pulling the level upward. `[CHECK — only if §4.3 actually shows variance reduction]`
- *Why this is interesting in its own right:* in human groups, narrative devices often act this way — they don't necessarily make people more cooperative on average, they make cooperation more *predictable* and reduce backsliding. Cite the human evidence we already have in §2.3. `[CITE: Smith et al. 2017 (Nat Commun); Boyd, Richerson & Henrich 2011]`
- *Mechanism speculation* (clearly labelled as such): possible mechanisms include (i) the myth gives the agent a self-consistent narrative to anchor its own behaviour to across rounds; (ii) the partner's myth provides a stable model of the partner that resists volatile updating from noisy game signals; (iii) the round-on-round myth evolution functions like a slow-moving prior that absorbs short-horizon variance.
- *Disclaim*: with $T = 10$ and $N = 10$ per cell, we can't distinguish these mechanisms; we can only point at the variance-reduction signature.

## 5.3 Cross-model variation as model-personality, not noise

- *Frame:* the cross-model differences are larger than any of our experimental manipulations. Defend this as a substantive finding rather than a confound to control out.
- *Position against existing work:* cross-model variation in social-game behaviour is a recurring finding `[CITE: Fontana et al. 2024 (Llama2 forgiving / Llama3 exploitative); Leng & Yuan 2023; Serapio-García et al. 2023]`. Our contribution is to show that the variation persists *under matched experimental conditions* (same prompts, same seeds, same noise mechanism) and *under conditions designed to break ceiling/floor lock-in*.
- *Speculation, carefully bounded:* differences are most plausibly attributed to RLHF / Constitutional AI training mixes (`[CITE: Bai et al. 2022 (Constitutional AI)]`) rather than to scale or capability per se. We cannot test this directly; flag as a hypothesis for cross-model studies that have access to base / RLHF / instruction-tuned variants of the same model family.
- *Methodological recommendation:* future LLM-game work should report all findings with model-stratified statistics; pooling across frontier models hides the dominant effect.

## 5.4 Cross-task influence: language is in the loop, but quietly

- *Methodological honesty:* the design choice (§3.3) of *not* injecting the partner's myth into the game prompt limits how strongly language can causally influence game play. The partner's myth reaches the game-reasoning model only via the agent's own previous myth-writing prompt — a thin and easily overshadowed channel.
- *Two possible readings:*
    - (i) The weak myth → game effect tells us "language is unimportant to LLM cooperation" — the strong reading.
    - (ii) The weak effect tells us "the channel through which language could influence cooperation was deliberately constrained, and even so, some signal leaks through" — the design-constrained reading.
- *Our position:* (ii) is more defensible. A more aggressive manipulation — explicit partner-myth injection into the game prompt — is the natural follow-up and is a better test of the strong-language hypothesis. Forward-link to §5.6.
- *What we did learn:* even through the constrained channel, dyads show measurable linguistic convergence (§4.4) and at least one case of strong lag-1 cross-agent correlation in cooperativity language (§4.5). Language is doing *some* work, even when the experimental design isn't structured to maximise its causal weight.

## 5.5 Limitations

- *Short horizon.* $T = 10$ rounds is short relative to typical iterated-learning paradigms. Some predicted dynamics (compression, structural emergence) require many more iterations and probably generational replacement; we explicitly do not test those. (Cross-link to the §1.5 disclaimer.)
- *Two-agent dyad.* No population dynamics, no partner-switching, no opportunity for reputation effects or assortment. The dyad is the minimal interesting unit, not the natural unit.
- *Single base model per dyad.* Cross-model dyads (e.g. Claude × Gemini) are not tested; the cross-model variation result therefore tells us about same-model behaviour only.
- *Single persona, single myth topic.* All noise experiments use neutral persona and the unconstrained `anything` topic. Persona × myth-content interactions are infrastructure-ready (§3.4) but unmeasured here.
- *Noise as artifice.* The bootstrap and negative-only noise mechanisms are designed to manufacture headroom; they don't correspond to any naturally-occurring noise process. Findings under those conditions are about LLM responses to a specific intervention, not about LLM cooperation in some neutral baseline.
- *Linguistic measures.* Dictionary-based cooperativity counts have no negation handling and no stemming. LIWC categories are blunt. LLM-as-judge similarity is reproducible but not validated against gold-standard human judgement on this kind of text.
- *No human baseline.* We compare LLM dyads to other LLM dyads, not to human pairs in the same trust-game protocol. Some claims (e.g. about model-personality magnitudes) would benefit from human anchors.
- *Channel design constrains conclusions.* See §5.4: the partner's myth is not directly injected into the game prompt, which deliberately weakens the cross-task channel.

## 5.6 Future directions

- *Direct partner-myth injection into the game prompt.* The single most informative follow-up: rerun the design with the partner's most recent myth quoted in the trust-game prompt, and compare. Strongest test of the language → cooperation hypothesis.
- *Longer horizons + generational replacement.* Move from 10 rounds in a 2-agent dyad to an N-agent population with selection across generations — i.e. the Vallinder & Hughes paradigm — and measure whether the consolidation signal compounds into level shifts over time. `[CITE: Vallinder & Hughes 2024]` (Out of scope for this paper; flagged for the population follow-up.)
- *Cross-model dyads.* Holding the experimental design fixed, vary which models are paired. Tests whether one model's "cooperation profile" can pull another's, and whether linguistic convergence happens between models with different baselines.
- *Persona × myth interaction.* The infrastructure is ready (§3.4 lists three personas; §3.3 lists three myth topics). One factorial pass would test whether myth content interacts with persona to produce cooperation effects neither produces alone.
- *Alternative games with more headroom.* Trust game is locked-in for two of three models even without the noise interventions. Public goods games and multi-agent commons games (`[CITE: Piatti et al. 2024 (GovSim)]`) may have more behavioural latitude.
- *Pre-registered confirmatory replication of the consolidation finding.* Because the variance-reduction interpretation emerged partly from inspection of cell-level results, a clean confirmatory study with pre-registered cells, $N$, and analysis path would substantially strengthen the claim.

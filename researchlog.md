### 2026-09-09 — Resume validator rejected every forced-defector run

**Time:** ~0.3 hours engineering; the 270-run batch is still in progress.

#### Blocker
- The negative-only cross-model reasoning rerun (`negative_only_crossmodel_reasoning_rerun_20260909`) lost its network connection at 105/270 finals; all 15 in-flight GPT‑5 Nano myth→game runs errored and the runner exited. Relaunching with `--resume` then refused to start: `check_existing_final` rejected 70 of the 105 completed finals — exactly every `random25`/`random50` run, all three models, all task orders — as "Per-call request settings differ from the run condition".
- Cause: `condition_from_run` exempted only `response_source == "scripted"` from the per-call settings check, but forced-defector decisions are tagged `forced_zero` / `random_defection_forced_zero` (`games/dyadic_pairing.py`) and receiver notices `deduction_notification` (`games/trust_game_noisy.py`). Those events never call a provider and carry no request settings. The runner's own end-of-run audit already skipped any source `!= "llm"`; the two checks disagreed, so an uninterrupted run would have failed at the final audit instead of ~8 hours earlier.

#### Resolution
- `af3c9951`: the condition check now skips every non-LLM source; a missing source still defaults to `llm` and is checked (existing tests pin this). Regression test added for the four scripted sources. 278 tests pass; all 105 finals validate. Run resumed at 17:04 from a clean worktree; the seven completed sets were recognised (`missing=0`) and no call was repeated.
- The 30 `.checkpoint.json.error.json` files in the output tree (15 from the first resume, 15 from the disconnect) are leftovers, not failed finals; an earlier "zero errors" audit classified them as checkpoints.

#### Caveat
- Sets launched before the fix record `code_commit` `893a9713`; later sets record `af3c9951`. The rerun's audit and matrix validation do not compare commits across runs, but any future `output_provenance` document over these 270 runs must declare `implementation.code_commit` as an allowed difference.

### 2026-09-09 — Result: GPT-5.5 gate rerun completes

**Time:** API interaction phase 7.0 minutes; engineering time not tracked.

#### Result
- Re-ran all twelve historical gate cells (two paired replicates across population sizes 2/8 and three task orders) at clean code `a18821b3157149a52a4eaed9b471c3d73a9caba2`. All 12 final full-state JSONs and 1,000 model interactions completed; zero errors/truncations, both condition/completion audits passed. Estimated standard-rate token cost: **$15.071095**.
- Native OpenAI `gpt-5.5-2026-04-23`, low reasoning, temperature/output cap omitted; original prompts, histories and paired seeds preserved. Original code/config references are recorded separately from the new provenance. Replaying the new responses through original commits `f53fa6d9`/`2ece1de6` reproduced all 1,000 per-agent request message arrays exactly, without paid calls.

#### Launch blocker resolved
- Fixed the three recovered legacy wrappers, added a pinned twelve-cell rerun command and frozen-condition audit, and removed environment dependence from guarded retry/reasoning settings. Historical configs/reports and the existing baseline bytes remain unchanged by the fix. PR #22 updated; 273 tests plus 50 subtests pass and CI is green. Real resume reports `PENDING=0` and makes no additional calls.

#### Evidence and scope
- Run receipt, final JSON hashes, stage metrics/audits and original-code replay evidence: `data/json/noise_experiments/gpt55_rerun_20260909/README.md` (local outputs, not uploaded). Rerun instructions: `docs/gpt55_gate_rerun.md`.
- These are new stochastic outputs with n=2 per cell. Several cells are near the sending ceiling; passing the completion audit does not establish behavioral headroom or stable task-order effects.

### 2026-09-08 — Result: Reasoning pilot measures costs

**Time:** approximately 0.4 hours, including API waits

#### Result
- Replayed 72 archived requests from Aron's negative-only cross-model set, 24 per model across population sizes, game/myth tasks, and early/middle/late rounds. All completed without retries, truncation finish reasons, or task-response boundary failures; standard-rate token cost **$0.644**.
- Direct profiles: Sonnet 4.5 thinking enabled with budget 8192, temperature omitted, output cap 64000; GPT-5 Nano high, temperature omitted, cap 128000; Gemini 3.7 Flash high, temperature 0.8, cap 65536. Gemini accepted 0.8; this does not prove how it affects sampling.
- Weighted projection for 90 full runs per model: Claude **$126.60**, GPT **$17.49**, Gemini **$33.85**; all 270 **$177.94**, or **$213.53** with a 20% planning allowance. This replaces the unmeasured $711 scenario, not a billing guarantee.
- Claude's sampled thinking was 514 (±94) tokens/game call and 295 (±91)/myth call: enabling an 8192 budget did not make it consume that budget.

#### Scope
- Cost-only replay: original memory-primary prompts, delayed partner-myth exchange, histories, and simulation outputs were untouched. New answers were not carried forward; these are not behavioral replicates. Two observations per sampling stratum cannot establish precise full-batch costs or failure rates.
- Full rerun not launched. The replay uses direct HTTP and explicit request plans; it does not certify the batch runner's large-output-cap transport path. Evidence, exact replay script, source/request hashes, raw usage, and offline summary: `reports/reasoning_cost_pilot_2026_09_08/README.md`.

### 2026-09-08 — Separate audit evidence from interpretation

**Time:** not recorded.

#### Result and correction
- Result: reopened 4,129 inventory-listed final paths, representing 3,661 distinct
  byte hashes after 468 exact copies; these are not verified independent replicates.
  The defector set records three direct providers, but GPT's exact effort is absent.
- Result: all 15 final format-study files reproduce the descriptive means. Both
  new arms also changed myth instructions and own-myth repetition; JSON-only
  changed retry policy. The September 4 claim that Claude's behaviour is mostly
  its prose is withdrawn as a causal interpretation, not erased from the record.

#### Scope and current position
- Saved zero counters/no reasoning text do not prove every historical thinking
  setting. Two washout finals change reasoning signature halfway despite a single
  provider label; the exact transition needs per-call/log verification.
- PR19 replaces the unmerged PR16 guards. It does not adopt the earlier proposed
  low-reasoning/two-sentence profile or change prompts, memory or retries.
- `docs/api-audit-reassessment-2026-09-08.md` separates recorded, inferred and
  missing settings, qualifies the scientific claims, and links hashed evidence
  plus reproduction scripts. Historical entries and raw records are unchanged.
  No experiment ran and no new scientific profile was selected.

### 2026-09-04 — Config over env shipped; Claude's defector behaviour is mostly its own prose

**Time:** 6 hours

#### Result
- Result: `llm_settings` (provider / reasoning / temperature) is now pinned
  per experiment set in `config/*.yaml`; the batch runners fail closed
  without it, env vars only override and are recorded, and `run_metadata`
  carries `llm_settings_effective` plus a per-call `finish_reason`
  (PR aronvallinder#16, `src/llm_settings.py`). Guards: the analysis loader
  refuses mixed regimes, HF sync refuses unprovenanced runs, and
  `tests/test_settings_pinned.py` fails CI for any new unpinned experiment
  set, launch script, or output directory without `provenance.json`.
- Result: decision-format confound cell (Claude Sonnet 4.5, 8 agents, 25%
  forced-zero defectors, negative-only noise, myth->game, direct Anthropic,
  thinking off, T=0.8; same seeds and prompts as Aron's 2026-08-25 cell,
  plus one OUTPUT FORMAT line). Ordinary agents, mean (±std) over runs:
  free prose (reference, n=5) send 0.592 (±0.042), return 0.444 (±0.007),
  balance 50.35 (±1.35), 1286 chars/decision; two sentences then JSON (n=5)
  0.531 (±0.033) / 0.428 (±0.019) / 47.78 (±1.22) / 352 chars; JSON only
  (n=5) 0.394 (±0.049) / 0.390 (±0.030) / 42.12 (±3.02) / 13 chars.
  Forbidding visible reasoning cuts Claude's sending by ~21 points. The
  "Claude degrades with defectors" ordering against bare-JSON models is
  therefore a format effect until formats are equalized.
- Result: under JSON-only, Claude as sender answered with the receiver's key
  in every run and a plain retry repeated it (5/5 runs died). The game retry
  is now corrective (role + key named, 2 attempts, `games/base_game.py`);
  1–7 corrections per run were needed and all succeeded. The prose was doing
  role-orientation work.
- Gemini 3.6 Flash is the no-thinking Gemini arm (`thinking_level=minimal`
  → 0 thought tokens on the game prompt); temperature is ignored on 3.6/3.7
  Flash, rejected on GPT-5 and Claude Opus 4.7+, so cross-model cells run at
  vendor-default temperature (PR aronvallinder#15, `docs/verified-facts.md`).

#### Caveats / next
- json_only rep04 hit the Anthropic credit limit mid-run and was rerun after
  the top-up with the same replicate seeds (`replicate_ids`).
- Decision: cross-model reruns use `reasoning_then_json` for every model
  (equal shape, keeps the reasoning->myth pathway) with the pinned regime
  Claude off / GPT-5 Nano low / Gemini 3.6 Flash minimal, temperature default.

### 2026-09-04 — Cross-model API calls are not equivalent (provider + reasoning audit)

**Time:** 2 hours

#### Result
- Result: the 2026-09-01 action item "verify Gemini/GPT/Claude API calls" is
  answered: NO, they are not equivalent. Four independent read-only audits
  (three Claude agents on code path, run data, history/provider docs; one
  Codex agent) agree. Message roles and system-prompt placement ARE
  equivalent across providers (`src/utils.py:270-316`); the inequivalence is
  in provider routing and sampling/reasoning settings.
- `LLM_PROVIDER=auto` (default since Aron's 2026-04-29 commits bf90f967,
  1374148b) routes `anthropic/*`, `openai/*`, `google/*` slugs to the direct
  vendor API whenever that key is in the runner's `.env`; OpenRouter is only
  the fallback. Provider therefore depends on whose machine ran the batch.
- Result: the slide-set defector runs (vallinder,
  `negative_only_crossmodel_defectors_n5_20260825`, 270 runs) went direct to
  all three vendors: Claude Sonnet 4.5 T=0.8, no thinking, cap 4096; GPT-5
  Nano temperature not sent, reasoning effort `minimal` (code default,
  `src/utils.py:531`; 0 reasoning tokens on 3,378/3,378 calls); Gemini 3.7
  Flash temperature not sent, thinking `medium` (~106 hidden tokens/decision).
- Result: the OpenRouter path sends `reasoning.effort=medium` for Claude and
  Gemini slugs by default, so OpenRouter-era Claude runs (Arabella's sets;
  baseline/v1/v2/v3/myth_causal/sonnet45_8agent, ~1,100 runs) had extended
  thinking ON while direct runs had it OFF. GPT-5 Nano: ~1,000 reasoning
  tokens/decision via OpenRouter vs 0 direct. The plain 8-agent memprimary
  triplet mixes both regimes (game + game_myth OpenRouter, myth_game direct).
- Format confound: Claude stores ~1,000-1,250 chars of strategy prose in its
  assistant memory each round; GPT and Gemini store bare JSON.
- Not bugs: no silent parse defaults, no truncation, no model aliasing bit,
  Gemini ceiling-lock holds under both routes.

#### Consequences
- Do not pool Claude or GPT-5 Nano runs across the OpenRouter/direct eras
  without splitting by reasoning signature. "GPT-5 Nano beats Claude" and
  "Claude degrades with defectors" are unproven until GPT cells are rerun at
  matched effort and the prose-in-memory confound is controlled.
- Pin provider + reasoning effort in launch scripts; record effective effort,
  temperature-sent and `finish_reason` in `run_metadata` (currently absent).
- Full report: https://claude.ai/code/artifact/cecd3178-dbbb-4741-9f86-dcd97a8a19ec

### 2026-09-01 — Team meeting: game saturates; cooperation-ratio plots are the missing view

**Time:** 1 hour

#### Decisions / findings
- Result: reviewed negative-only vs bidirectional noise (8-agent and 2-agent
  dyads). Bidirectional: send and return fractions keep climbing past round
  10–15, then stabilize. Negative-only: much flatter, weaker visible effect.
- Result: return proportions across game-only, myth→game and if-game
  conditions (slides 707/709/711/721; Aron added send proportions, slide 728).
  Gemini 3.7 Flash ceiling-locks without forced defection; GPT-5 Nano beats
  Claude on collective returns in some conditions; Claude degrades notably once
  defectors are added.
- Core problem: the trust game saturates at full cooperation, so condition
  differences are hard to detect. Cooperation-ratio plots (not yet made) were
  flagged as the most informative view.
- Analysis direction: split myths by cooperativeness of *language* rather than
  by outcome, then check whether outcomes follow. Earlier injection of the 25
  most cooperative myths as starting conditions had a large effect. Find the
  property (language convergence, cooperative words, ...) that correlates most
  with outcomes and use it to split the main results analysis.

#### Action items
- Cooperation-ratio plots in the format of slides 724/725, on the same axes as
  send/return proportions (dotted vs solid per condition).
- Myth split by cooperative language (see above).
- Verify Gemini and GPT API calls (Aron, Ivar): message roles and settings must
  match Claude's, which was debugged extensively. Rule out format bugs behind
  GPT-5 Nano's anomalous behavior.
- Results scaffold in the overlay doc for Edward: which experiments are
  finalized, which models were used, what goes in the results section.

### 2026-08-28 — Meme transmission mostly base rate

**Time:** 3 hours

#### Result
- Re-analyzed the 60-run informed-noise corpus with exposure contrasts, a
  degree-preserving rewiring null (B=10,000, Holm), and negative controls
  (`scripts/analyze_meme_transmission_null.py`, PR aronvallinder#10; outputs
  `data/analysis/meme_transmission_null_2026_08_28/`). No new runs.
- The Aug-19 report's 60–77% "edge transmission" was dominated by base rate:
  honest excess over the null is single-digit pp. Largest raw families are
  confounded — for consistency_over_volatility a *not-yet-visible* future myth
  "predicts" adoption (+35pp) better than the seen myth (+32pp).
- Regex candidates: sustainable_equilibrium (+10.9pp vs +1.7pp null) and
  proportional_reciprocity (+3.6pp vs −4.1pp null). noise_adaptation is prompt
  elicitation (system prompt announces noise in all 5,000 capsules).
- Blinded LLM-judge relabel of all 5,000 capsules (gpt-4o-mini, $0.87,
  `scripts/judge_meme_labels.py`) then same analysis on semantic labels
  (`data/analysis/meme_transmission_null_judge_2026_08_28/`): NO family
  survives cleanly. The two Holm-significant ones (proportional_reciprocity
  +8.4pp excess, consistency +4.0pp) fail the future-myth control;
  sustainable_equilibrium drops to p=0.11. Regex vs judge agreement is poor
  (punitive precision 1%, noise 12%, trust_escalation recall 14%).

#### Why / method choice
- Deep-research review (Shalizi & Thomas 2011; Anagnostopoulos 2008; Bentley
  2004) + external model review: co-occurrence can never establish transmission
  between same-model agents; nulls and exposure contrasts are the accepted fix.
- 2-agent dyads have no within-run rewiring null; dyadic claims need the
  seeding/transplant intervention. Next: LLM-judge relabeling of all 5,000
  responses, then rerun these contrasts on semantic labels.

### 2026-08-25 — Shared run-data store on Hugging Face

**Time:** 1.5 hours

#### What changed
- Raw run JSONs (`data/json/`, gitignored) now sync to the shared private HF
  dataset `machine-cultural-evolution/nips-linguistic-evolution-runs`, one
  namespace per user. `scripts/sync_data.sh push|pull`; optional Claude Code
  hook (`scripts/data_sync_hook.sh`) auto-pushes after each batch run.
- Ivar's corpus is uploaded and verified: 16,222 files, 4.1 GB under
  `ivarfresh/json/`. Tooling PR to shared main: aronvallinder#8. Aron's
  onboarding: HF login + one push.
- Uploads are resumable and content-deduplicated (only new runs transfer);
  pulls land in `data/shared_runs/` and never touch local `data/json`.

#### Rationale / rejected alternatives
- Raw data never fit in git (3.8 GB, 10k+ files; GitHub LFS free tier is 1 GB).
  Drive+rclone rejected (slow on many small files); plain git rejected
  (permanent history bloat). HF repo doubles as the citable public dataset at
  publication.

---

### 2026-08-23 — Gemini 3.7 selectively punishes but shows no return crowding

- Completed the frozen new-seed Gemini 3.7 Flash population screen crossing
  deduction availability with 0%/25% hidden defectors (`n=3` matched
  quadruplets). All 12 populations passed jointly: 2,400 accepted interactions,
  2,010 model calls, 150 forced actions, 240 notices, 960 exact noise checks,
  zero retries, and clean matched provenance.
- Live targeting was perfect. Ordinary senders spent both points against all
  25 mechanical-defector receivers and zero against all 65 ordinary receivers;
  controls also had zero deductions in 120 opportunities. There were no
  deductions after 112 visibly half-or-more returns.
- The Flash-Lite return-crowding result did not reproduce. Available minus
  unavailable returning with defectors was `+.00262` (95% CI `[-.00162,
  +.00685]`) and positive in all three pairs; the interaction was `-.00094`
  (`[-.00843,+.00654]`). Every ordinary sender still gave the full `$5`.
- A strong model-specific fairness rule explains the lack of behavioral
  movement: 280/370 positive-receipt ordinary decisions returned exactly half
  of the noisy receipt shown, and 327/370 were within half a cent. Selective
  punishment generalizes across Gemini versions; downstream crowding does not.
- Myth responses were preliminary: deduction availability increased both
  cooperation and threat language, consistent with sanctioning framed as norm
  protection. The Flash-Lite defector-author cooperation/threat imprint did
  not cleanly generalize at `n=3`.
- The frozen decision is **do not scale this population design**. Accepted-run
  list-price cost was `$5.66`. Report and analysis:
  `docs/defector_punishment_gemini37_n3_overview_2026-08-23.md` and
  `scripts/analyze_defector_punishment_gemini37_n3.py`.

---

### 2026-08-23 — Gemini 3.7 uses graded, selective punishment

- Ran the frozen 50-call current-wording calibration with Gemini 3.7 Flash at
  medium thinking: five controlled visible return levels x ten calls, holding
  the myth, full send, receipt, payoffs, rules, and institution fixed. All 50
  decisions were valid on the first attempt with clean provenance.
- The model spent both points in every 0% and 10% return case, averaged .4
  points at 25% (four one-point deductions), and spent zero in every 50% and
  75% case. Low-minus-high separation was exactly +2, high-return punishment
  was 0%, and the means decreased monotonically. All frozen gate components
  passed.
- Gemini 3.7 is more graded and sanctions a broader low-return band than
  Flash-Lite under the same calibration, while both fully refrain at fair
  returns. The live-noise prediction is near-universal mechanical-defector
  targeting because a true zero can appear no more than about `$1` positive.
- The model is eligible for a small new-seed 2x2 population screen crossing
  deduction availability with 0%/25% hidden defectors. Calibration list-price
  cost was about six cents. Report and analysis:
  `docs/punishment_comprehension_gemini37_overview_2026-08-23.md` and
  `scripts/analyze_punishment_comprehension_gemini37.py`.

---

### 2026-08-23 — Gemini 3.7 Flash is baseline ceiling-limited

- Added direct support for Google's current `gemini-3.7-flash`, including the
  model's removal of legacy temperature sampling, explicit medium-thinking
  metadata, and a recorded configurable request timeout. Regression tests
  preserve the historical request shape for Flash-Lite.
- Froze and ran three matched eight-agent populations per task order (Game
  only, Game→Myth, Myth→Game). All nine accepted runs passed jointly: 1,200
  calls, 720 exact post-decision noise checks, zero accepted-run retries or
  boundary failures, matched schedules/seeds, and clean provenance.
- Gemini 3.7 sent the full `$5` in all 360 sender decisions. Every condition
  therefore ended at exactly `$75` per agent; return ratios were also nearly
  identical (.4731/.4733/.4733). The frozen headroom gate failed and prohibits
  adding baseline replicates.
- The result is ceiling limitation, not evidence of a null myth effect. Greater
  capability did not solve the measurement problem. Next use a controlled
  punishment calibration and a small 0%-versus-25%-defector stress test, where
  behavior can vary. Accepted-run list-price cost was `$3.16`.
- A late request in the first attempted run exceeded the historical timeout;
  an outcome-blind amendment raised and recorded it. A resumable filename
  mismatch was also caught, fixed, and tested before the full launch. Failed
  and partial files are excluded. Report and analysis:
  `docs/gemini37_flash_task_order_n3_overview_2026-08-23.md` and
  `scripts/analyze_gemini37_flash_task_order_n3.py`.

---

### 2026-08-23 — Punishment crowding is independently defector-dependent

- Completed the frozen new-seed Gemini 3.1 Flash-Lite 2x2 confirmation:
  deduction available/unavailable x 0%/25% hidden defectors, with ten matched
  population quadruplets. All 40 passed jointly: 8,000 accepted interactions,
  6,700 Gemini calls, exactly 500 forced actions, 800 notices, 3,200 exact
  post-decision noise checks, zero retries, and clean matched provenance.
- Both primary claims confirmed. In defector populations, availability lowered
  ordinary receiver return ratios by -.0455 (95% CI [-.0743, -.0166], Holm
  p=.0121). The availability x defector interaction was -.0373 ([-.0718,
  -.0027], Holm p=.0373); the no-defector simple effect was only -.0082 and
  unresolved.
- Selective use remained strong: ordinary senders punished hidden defectors in
  72/84 opportunities (85.7%) versus ordinary receivers in 6/216 (2.8%). All
  six ordinary-target deductions followed a visibly zero return; there were
  none after 116 visibly half-or-more returns.
- Sending was unchanged at ceiling in controls and had an unresolved -.0303
  availability effect with defectors. The return effect was absent in round
  one and grew later, reaching -.137 in round ten. Choices shifted toward exact
  half and away from above-half generosity.
- Ordinary myths became more threat-, betrayal-, withholding-, and punishment-
  focused under the institution; the threat-language increase was larger with
  defectors (secondary interaction +.1410, CI [+.0667,+.2152]). The most useful
  next test isolates game-history and myth-content mediation rather than adding
  more populations to the same factorial. Report and analysis:
  `docs/defector_punishment_gemini_factorial_confirmation_n10_overview_2026-08-23.md`
  and `scripts/analyze_defector_punishment_gemini_factorial_confirmation_n10.py`.

---

### 2026-08-22 — Punishment availability lowers Gemini return ratios

- Added 10 punishment-unavailable Gemini populations matched to the completed
  25%-defector punishment confirmation (replicates 70–79). Both arms passed
  jointly: 4,000 accepted interactions, 3,100 LLM calls, exactly 500 forced
  actions, 400 deduction notices, 1,600 signed-noise checks, zero retries, and
  identical schedules, defector assignments, and exogenous noise seeds.
- The exploratory punishment-available minus unavailable effect on ordinary
  sending was −.0277 (95% paired CI [−.0668, +.0115], Holm p=.145), with only
  five of ten pairs negative. It does not establish a sending effect.
- Ordinary receiver return ratios fell by −.0491 ([−.0792, −.0191], Holm
  p=.00988), with nine of ten pairs negative. Round one was virtually identical
  (−.00076); all nine later round-level differences were negative. The on arm
  shifted returns toward exact half (65 versus 38 `$7.50` returns) and away
  from more generous choices (`$8`: 30 versus 47; `$10`: five versus 22), a
  post-hoc pattern consistent with punishment anchoring the minimally fair rule.
- Availability also changed ordinary myths: punishment/deduction density rose
  +.221 matches/100 words (CI [+.164, +.277]) and the overlapping threat/
  defection lexicon rose +.341 ([+.288, +.393]), in all ten pairs. The latter
  was not only the word *punishment*: betrayal, threat, withholding, and other
  hostile language also increased. These are descriptive institution effects,
  not a defector interaction.
- The frozen escalation rule passed on the return outcome. Next run a fully
  independent new-seed 2×2 (punishment available/unavailable × 0%/25% hidden
  defectors) to test the return effect and distinguish a general institutional
  effect from a defector-contingent one. Report and analysis:
  `docs/defector_punishment_gemini_availability_matched_n10_overview_2026-08-22.md`
  and `scripts/analyze_defector_punishment_gemini_availability_matched_n10.py`.

---

### 2026-08-22 — Gemini's selective punishment independently confirms

- Ran 10 pre-registered new-seed Gemini 3.1 Flash-Lite populations containing
  25% hidden mechanical defectors. All passed jointly: 2,400 accepted
  interactions, 1,700 LLM responses, exactly 300 forced defector decisions,
  400 notices, 800 post-decision signed-noise checks, zero retries, no leakage,
  and clean embedded commit/config provenance.
- The prewritten analyzer halted before opening outcomes because the protocol
  had incorrectly assumed a fixed 8/22 target-role split per population.
  Balanced schedules guarantee 30 ordinary-sender opportunities but not that
  exact split. A committed, outcome-blind amendment recorded the deterministic
  frozen-seed counts (86 defector, 214 ordinary) and changed no statistical or
  behavioral threshold.
- Selective punishment replicated decisively. The population-level hidden-
  defector-minus-ordinary contrast was +1.580 deduction points (95% CI
  [+1.443, +1.718], Holm p=1.82e−9) and +.790 probability ([+.721, +.859],
  same p). Both effects exceeded their frozen minimums.
- Pooled, ordinary senders deducted in 70/86 hidden-defector opportunities
  (81.4%; mean 1.628/2) versus 5/214 ordinary-receiver opportunities (2.34%;
  mean .0467). All five ordinary-receiver deductions followed a visibly zero
  return; no sender deducted in any of 112 opportunities with a visible return
  ratio of at least .5.
- This confirms a selective response to observed defection, not recognition
  of a hidden role. Secondary treatment-only outcomes were ordinary sending
  .930 (CI [.897, .963]) and returning .483 ([.470, .495]); without a control
  arm they do not estimate a punishment effect. Report and analysis:
  `docs/defector_punishment_gemini_confirmation_n10_overview_2026-08-22.md`
  and `scripts/analyze_defector_punishment_gemini_confirmation_n10.py`.

---

### 2026-08-21 — Gemini targets hidden defectors in the population pilot

- Ran the frozen three-pair Gemini 3.1 Flash-Lite Myth→Game pilot after its
  controlled punishment calibration. All six substantive populations passed:
  1,440 accepted interactions, 1,110 LLM responses, exactly 90 forced defector
  decisions, 240 deduction notices, 480 signed-noise checks, and no retries,
  leakage, or provenance failures. The two-population smoke remained excluded.
- Ordinary senders spent a mean 1.50 of two deduction points toward hidden
  defectors (18/24 opportunities, 75%) and exactly zero toward ordinary
  receivers (0/66). The defector-minus-ordinary contrasts were therefore
  +1.50 points and +.75 probability, clearing the frozen pilot thresholds in
  every aggregate criterion.
- Restraint also survived the full noisy histories: there were zero deductions
  in all 43 opportunities where the visible return ratio was at least .5.
  Across all three treatment populations, ordinary partners were never
  punished, while defectors were targeted in 50%, 87.5%, and 87.5% of their
  opportunities.
- Cooperation was exploratory and near ceiling: ordinary sending was .978
  with defectors versus 1.000 without (paired difference −.022, CI [−.118,
  +.073]); ordinary return ratios were .505 versus .504 (+.0014, CI [−.050,
  +.053]). No small-pilot myth-language contrast was clear.
- Decision: the mechanism passes the pre-specified screen and merits an
  independent new-seed confirmation. Do not yet treat the `n=3` population
  result or its p-values as confirmatory. Report and analysis:
  `docs/defector_punishment_gemini_n3_overview_2026-08-21.md` and
  `scripts/analyze_defector_punishment_gemini_n3.py`.

---

### 2026-08-21 — Gemini's live-noise punishment threshold is $.25–$.50

- Mapped Gemini's current-wording deduction choice at `$0`, `$.25`, `$.50`,
  `$.75`, and `$1` visible returns (10 calls/cell), spanning the full band that
  `U(−1,+1)` noise can produce from a defector's true zero. All 50 calls
  passed with no retries and clean provenance.
- Gemini spent both points in every `$0` and `$.25` case and zero in every
  `$.50`, `$.75`, and `$1` case. The empirical switch lies between $.25 and
  $.50.
- Under the frozen piecewise-linear integration of the live clamped-noise
  distribution, a true-zero defector is expected to be punished 68.75% of the
  time, at mean intensity 1.375 points. This passes the population-pilot gate.
- Next run three matched Gemini Myth→Game population pairs (0% versus 25%
  defectors) and evaluate within-treatment targeting before cooperation or
  myths. Report and analysis:
  `docs/punishment_comprehension_gemini_noise_boundary_overview_2026-08-21.md`
  and `scripts/analyze_punishment_comprehension_gemini_noise_boundary.py`.

---

### 2026-08-21 — Gemini selectively deducts where GPT does not

- Repeated the unchanged current-wording controlled deduction calibration in
  Gemini 3.1 Flash-Lite (five visible returns × 10 calls). All 50 direct Google
  calls passed with exact cell balance, no retries, and clean commit/config
  provenance.
- Gemini spent both points in all 10 zero-return cases and zero in all 40
  positive-return cases. It passed the frozen selectivity gate: low-minus-high
  +1.00 (CI [+.520, +1.480], p=.00034), zero high-return deductions, and no
  monotonicity reversal.
- GPT-5 Nano used the same wording almost universally. The cross-model return-
  slope interaction was −1.244 (CI [−2.117, −.371], p=.0057), showing a
  qualitative model-policy difference rather than merely lower Gemini use.
- Gemini is eligible for a small population pilot, but first map its threshold
  at visible returns within `$0–$1`: signed noise can make a mechanical
  defector's true zero appear slightly positive. Report and analysis:
  `docs/punishment_comprehension_crossmodel_overview_2026-08-21.md` and
  `scripts/analyze_punishment_comprehension_crossmodel.py`.

---

### 2026-08-21 — Controlled calibration rejects both GPT punishment prompts

- Froze and ran a 100-call GPT-5 Nano mechanism calibration: current versus
  cost-salient neutral wording × visible returns of 0%, 10%, 25%, 50%, or
  75%, with the myth, full send, payoffs, rules, and model held fixed. All 100
  direct OpenAI decisions passed, with 10/cell, no response-boundary retries,
  and clean commit/config provenance.
- Current wording showed some low-versus-high intensity difference (+.40
  points, CI [+.101, +.699]) but deducted in 100% of high-return calls and rose
  again from 1.1 points at a 25% return to 1.5 at 75%. It failed the frozen
  selectivity gate.
- Explicitly clarifying that spending is optional and personally costly cut
  mean spending from 1.46 to .74 (−.72, CI [−.954, −.486]), but removed
  rather than improved return sensitivity: slope +.003 (p=.994), low-minus-high
  +.15 (CI [−.249, +.549]), and 65% high-return deduction use.
- Conclusion: GPT-5 Nano treats the institution as a salient action, not a
  calibrated sanction. Neither wording is eligible for a population pilot;
  do not tune the prose further toward a desired result. Next either apply the
  unchanged calibration to another model or redesign the economic mechanism.
  Report and analysis:
  `docs/punishment_comprehension_gpt_overview_2026-08-21.md` and
  `scripts/analyze_punishment_comprehension_calibration.py`.

---

### 2026-08-21 — Punishment availability has no reliable cooperative benefit

- Completed an exploratory GPT-5 Nano 2×2: deduction stage available versus
  unavailable × 0% versus 25% hidden mechanical defectors (`n=5` matched
  populations/cell). All 20 accepted populations passed jointly: 4,000
  interactions, 3,350 LLM responses, exactly 250 forced decisions, 400
  deduction notices, 1,600 noise checks, matched schedules/assignments, and no
  leakage or unrecovered errors.
- Caught a reproducibility gap before outcome analysis: the resumable launcher
  omitted embedded Git/config provenance. Excluded the first off-stage batch,
  fixed and tested the launcher, and reran all 10 new populations. Every
  accepted replacement records commit `649dbc34`, one config hash, and a clean
  worktree.
- Deduction availability did not improve sending: −.0273 without defectors
  (CI [−.0890, +.0344], p=.287) and +.0027 with defectors ([−.0908,
  +.0961], p=.941). The availability×defector interaction was +.0300
  ([−.0125, +.0724], p=.122).
- Returning was directionally higher with deductions (+.0282 without and
  +.0516 with defectors), but both intervals crossed zero and the interaction
  was unresolved (+.0234, CI [−.0641, +.1110], p=.498). A post-hoc check
  using the excluded first batch produced much smaller +.012 and +.015 return
  estimates, suggesting sampling sensitivity.
- No ordinary-myth cooperation, threat, or half-rule interaction was reliable.
  Combined with 90.9% realized deduction use and no targeting of defectors,
  this design elicits a routine action rather than selective norm enforcement.
  Do not scale it unchanged; first run a controlled mechanism-comprehension
  calibration across high- and low-return states. Report and analysis:
  `docs/defector_punishment_factorial_gpt_n5_overview_2026-08-21.md` and
  `scripts/analyze_defector_punishment_factorial_gpt_n5.py`.

---

### 2026-08-21 — Costly deductions are common but not targeted in GPT-5 Nano

- Added a sender-only costly deduction stage to the eight-agent Myth→Game
  design: two optional points, a 1:3 cost-to-target effect, payoff floor zero,
  explicit receiver notification, and neutral wording. Hidden mechanical
  defectors write myths normally but always send, return, and deduct zero.
- All 10 frozen GPT-5 Nano populations (`n=5` matched 0%-versus-25%-defector
  pairs) passed: 2,400 accepted interaction records, 1,850 LLM responses,
  exactly 150 forced decisions, 400 notices, 800 noise checks, and no leakage
  or unrecovered failures.
- Ordinary senders deducted in 90.9% of opportunities. They spent 1.295 points
  toward defectors versus 1.472 toward ordinary receivers; the
  defector-minus-ordinary population contrast was −.183 (CI [−.611,
  +.245], p=.300). Deductions also remained common after at least half had
  visibly been returned.
- Defectors did not reduce ordinary sending (+.0052, CI [−.0212, +.0315],
  p=.615). Ordinary returns were suggestively higher (+.0268, CI [−.0043,
  +.0580], p=.075). Ordinary myth cooperation, threat, and punishment language
  showed no reliable condition differences; much deduction vocabulary simply
  echoed the announced institution.
- Conclusion: the implementation is sound, but GPT-5 Nano treats deduction as
  a routine affordance rather than a selective sanction. Next run the matched
  punishment-unavailable cells to estimate the exploratory 2×2 availability ×
  defector comparison. Report and analysis:
  `docs/defector_punishment_gpt_n5_overview_2026-08-21.md` and
  `scripts/analyze_defector_punishment_gpt_n5.py`.

---

### 2026-08-21 — Defector-myth threat transmission does not independently replicate

- Independently repeated the frozen Gemini defector-myth circulation
  manipulation in 10 new matched population pairs. All 20 populations passed:
  3,200 accepted interactions, 2,800 LLM calls, exactly 400 forced decisions,
  1,600 noise checks, complete matched exposures, no leakage, and no retries or
  unrecovered failures.
- The sole confirmatory result was negative. Replacing the defector myth with
  a natural ordinary-authored myth changed the target's next-myth threat
  density by only −.0117 matches/100 words (95% CI [−.0639, +.0405], p=.624,
  dz=−.16). The target texts contained 26 threat matches after defector myths
  versus 22 after ordinary substitutes, rather than the screen's 23 versus
  five.
- The source manipulation again increased presented cooperation language
  (+.521, CI [+.237, +.805], p=.0025). A secondary target outcome also showed
  more cooperation language (+.145, CI [+.0297, +.260], unadjusted p=.0193),
  but neither directly exposed nor population-wide game behavior changed.
- Conclusion: the original one-step threat result was a false positive or
  unstable seed-contingent pattern. Do not scale this same near-ceiling
  circulation design. Report and analysis:
  `docs/defector_myth_circulation_gemini_confirmation_n10_overview_2026-08-21.md`
  and
  `scripts/analyze_defector_myth_circulation_gemini_confirmation_n10.py`.

---

### 2026-08-21 — Defector myths transmit tone, not behavior, in Gemini screen

- Added and froze a causal circulation manipulation: two hidden mechanical
  defectors write normally in both arms, but at defector-to-ordinary cultural
  exposures the intervention replaces the defector myth with a real
  ordinary-authored myth from the same prior population-round. Source identity
  and policy remain hidden, and call counts/memory are unchanged.
- All 10 Gemini 3.1 Flash-Lite populations (`n=5` matched pairs) passed jointly:
  1,600 accepted interactions, 1,400 LLM calls, exactly 200 forced decisions,
  800 noise checks, 84 matched direct exposures per arm, and no leakage or
  unrecovered failures. The separate two-run smoke set was excluded.
- The source-text manipulation worked: ordinary substitutes had +.633
  cooperation/fairness matches/100 words (CI [+.043, +1.223]) and −.129
  threat matches ([−.223, −.034]) relative to defector myths.
- The frozen cooperation outcome was suggestive but unresolved: the directly
  exposed ordinary agent's next myth gained +.310 cooperation matches/100
  words (CI [−.105, +.725], Holm p=.214). Same-round giving did not move
  (`−.0158`, CI [−.218, +.186], Holm p=.838).
- The predeclared secondary threat signal transmitted cleanly: target myths
  used −.105 threat terms/100 words after substitution (CI [−.171, −.039],
  p=.0115). Across 84 targets/arm, this was 23 threat-lexicon matches after
  defector myths versus five after ordinary substitutes, spread across
  withholding, betrayal, threat, punishment, retaliation, distrust, and other
  terms rather than being driven only by *zero*.
- Interpretation: Gemini's mechanically induced cultural tone survives one
  transmission step, but it does not measurably change behavior in this
  near-ceiling game. An independent new-seed threat-transmission confirmation
  is the next test. Report and analysis:
  `docs/defector_myth_circulation_gemini_n5_overview_2026-08-21.md` and
  `scripts/analyze_defector_myth_circulation_gemini_n5.py`.

---

### 2026-08-21 — Defector confirmation: no broad cascade, Gemini imprint replicates

- Independently repeated the frozen Myth→Game 0%-versus-25% mechanical-defector
  design in GPT-5 Nano and Gemini 3.1 Flash-Lite (`n=10` new populations/cell).
  All 40 runs passed jointly: 6,400 accepted tasks, exactly 400 forced game
  responses, 3,200 myths/noise checks, matched schedules, and no leakage or
  unrecovered errors.
- Neither broad confirmatory claim survived. The equal-model treatment effect
  on ordinary-agent sending was −.01345 (95% CI [−.03142, +.00451],
  Holm p=.258); the effect on cooperation/fairness density in ordinary-authored
  myths was −.0652 matches/100 words ([−.194, +.0637], Holm p=.300).
- Large ordinary-agent balance losses (−$18.80 GPT; −$21.73 Gemini) are
  principally mechanical consequences of zero sends/returns, not evidence of
  a comparably large behavioral cascade.
- The Gemini author-specific cultural effect independently replicated. In
  rounds 2–10, defector myths used .571 fewer cooperation terms/100 words
  ([−.778, −.364], p=.00015) and .0577 more threat terms ([+.0293, +.0860],
  p=.00128) than ordinary treatment myths; round-one author differences were
  absent. GPT again showed no reliable author-type divergence.
- Conclusion: hidden mechanical defectors impose direct welfare losses but do
  not trigger a confirmed population-wide behavioral or cultural collapse.
  Gemini shows a replicated, localized behavior-to-culture imprint. The next
  causal test should manipulate whether defector-authored myths circulate.
  Report and analysis:
  `docs/defector_myth_game_crossmodel_confirmation_n10_overview_2026-08-21.md`
  and `scripts/analyze_defector_myth_game_crossmodel_confirmation_n10.py`.

---

### 2026-08-21 — Cross-model defector pilot: modest spillover, cultural divergence

- Froze and ran Myth→Game 0%-versus-25% mechanical-defector screens in GPT-5
  Nano and Gemini 3.1 Flash-Lite (`n=5` populations/cell). All 20 runs passed
  jointly: 3,200 accepted tasks, 3,000 LLM calls, exactly 200 forced zero game
  responses, 1,600 myths/noise checks, matched schedules, and no label leakage.
- Ordinary-agent sending fell in both models, but modestly and with intervals
  spanning zero: GPT −.0326 (CI [−.0960, +.0307], p=.226) and Gemini −.0160
  ([−.0368, +.0048], p=.099). Gemini left its full-send ceiling in three of
  five treatment populations. Large balance losses are mostly mechanical and
  are not evidence of a behavioral collapse.
- Standard authors used less cooperation/fairness language with defectors:
  GPT −.116 matches/100 words ([−.446, +.213]) and Gemini −.184
  ([−.390, +.023], p=.069). Explicit threat language and half-return rules
  barely changed among standard authors.
- The distinctive result is model-specific cultural adaptation. Gemini
  defector authors were similar in round 1, before forced play, then in rounds
  2–10 used .697 fewer cooperation terms/100 words (CI [−1.191, −.203]) and
  .0979 more threat terms ([+.0039, +.1918]) than standard treatment authors.
  GPT defector myths remained as prosocial as standard myths.
- Interpretation: hidden mechanical defectors create a modest population-level
  cooperation spillover, not targeted punishment; forced behavior becomes
  culturally visible in Gemini but not GPT. Report and analysis:
  `docs/defector_myth_game_crossmodel_n5_overview_2026-08-21.md` and
  `scripts/analyze_defector_myth_game_crossmodel_n5.py`.

---

### 2026-08-21 — Gemini identity screen is ceiling-limited

- Froze and ran a new-seed Gemini 3.1 Flash-Lite replication of the stable-
  versus-round-local identity contrast (`n=5` populations/arm). All 10 runs
  passed jointly: 800 decisions/noise checks, no retries/errors, matched
  schedules, and no identity leakage.
- Gemini sent the full $5 in every sender decision in every round and condition.
  Both arms therefore had proportion sent 1.000 and final balance 75.00 in all
  five populations; the primary stable − round-local contrast was exactly 0.
- This is not precise evidence of no identity effect. The test is uninformative
  because the primary behavior is fully saturated; increasing n under the same
  prompt would not recover variation.
- Return behavior was also nearly identical: .4786 round-local versus .4782
  stable (paired difference −.00033, CI [−.00144, +.00079], p=.465), or about
  1.435 returned per dollar originally sent.
- Cross-model conclusion: GPT-5 Nano has behavioral headroom and showed a
  positive stable-ID effect; Gemini Flash-Lite adopts unconditional maximum
  sending. Further Gemini work needs a harder dilemma or defectors, not more
  replicates of this cell. Report and analysis:
  `docs/identity_persistence_gemini_n5_overview_2026-08-21.md` and
  `scripts/analyze_identity_persistence_gemini_n5.py`.

---

### 2026-08-21 — Independent confirmation reverses the identity hypothesis

- Froze and ran a new-seed, wording-matched comparison of persistent stable
  IDs versus round-local pair IDs (`n=10` GPT-5 Nano populations/arm), with no
  synthetic history in either condition. All 20 runs passed jointly: 1,600
  decisions and noise checks, no retries/errors, matched schedules, and no
  identity leakage.
- Contrary to the directional hypothesis, persistent IDs **increased** final
  balance by +3.71/agent (95% paired CI [+1.35, +6.08], p=.0063, dz=1.12):
  65.03 stable versus 61.31 round-local. The frozen hypothesis required a
  negative interval and is therefore not confirmed; it is directionally
  contradicted by the independent evidence.
- The effect developed across repeated play: round-one sending differed by
  only +.070 ([−.087, +.227], p=.341), while mean sending differed by +.0743
  ([+.0269, +.1217], p=.0063). Persistent IDs may enable relationship-specific
  trust rather than retaliation, but the mechanism is not isolated.
- Persistent IDs reduced return ratios by −.0647 (unadjusted p=.0087). Since
  final welfare is driven by sending, this redistribution result does not
  negate their higher joint surplus.
- The preceding n=5 claim that identity explains the public-ledger penalty is
  superseded as an unstable exploratory interpretation. Report and analysis:
  `docs/identity_persistence_confirmation_gpt_n10_overview_2026-08-21.md` and
  `scripts/analyze_identity_persistence_confirmation_gpt_n10.py`.

---

### 2026-08-21 — Anonymous social information preserves cooperation

- Added an anonymous population-record arm: all prior-three-round noisy
  transfers are visible, but pairs are relabeled within each round and cannot
  support individual reputation tracking. All 20 matched Game-only runs across
  private/anonymous-record/stable-ID/public-ledger arms passed jointly (1,600
  decisions and noise checks; no errors or identity leakage).
- Final balance was 66.03 anonymous private, 65.55 anonymous population record,
  61.03 stable IDs/no ledger, and 62.04 stable IDs/public ledger. The frozen
  anonymous-record − private contrast was −0.48 (95% CI [−5.36, +4.41],
  p=.801); their round-one means were exactly equal at .620.
- Anonymous record − stable IDs was +4.53 (p=.263), while stable public ledger
  − anonymous record was −3.51 (p=.150, dz=−.79). The directions favor social
  information without persistent identity, but n=5 intervals are wide.
- Return ratios were .399 / .421 / .283 / .441. This corrects the preceding
  tentative interpretation: public records are not uniquely high; the stable-
  ID/no-ledger arm is unusually low.
- Best current mechanism: persistent partner identity, rather than population
  information, permits caution/retaliation and lowers cooperation. A new-seed,
  wording-matched stable-versus-relative identity experiment is needed before
  scaling the claim. Report and analysis:
  `docs/anonymous_population_record_gpt_n5_overview_2026-08-21.md` and
  `scripts/analyze_anonymous_population_record_gpt_n5.py`.

---

### 2026-08-21 — Stable-ID control: round-one drop is not the ledger announcement

- Froze and ran a five-population GPT-5 Nano stable-ID/no-ledger control. All
  15 matched private/stable/public Game-only runs passed jointly: 1,200 clean
  decisions, 1,200 noise checks, exact ID/history checks, and matched schedules.
- Round-one sending was .620 anonymous private, .440 stable IDs/no ledger, and
  .480 stable IDs/public ledger. The prespecified ledger − stable contrast was
  +.040 (95% CI [−.095, +.175], p=.456); stable − anonymous was −.180
  ([−.384, +.024], p=.070).
- Across all rounds, final balance was 66.03 / 61.03 / 62.04. Stable − private
  was −5.00 (p=.112) with high variance from one low-cooperation population;
  ledger − stable was +1.01 (p=.553). There is no resolved welfare benefit from
  the public records beyond persistent identity.
- Post hoc, the public ledger raised return ratios relative to stable IDs by
  .158 ([+.055, +.261], unadjusted p=.013), positive in all five pairs. This
  may indicate social-norm information even though returns do not directly
  increase total surplus.
- The early cooperation drop is best attributed to the persistent identity/
  current-partner prompt bundle, not ledger learning or the public-monitoring
  announcement. Report and analysis:
  `docs/stable_ids_control_gpt_n5_overview_2026-08-21.md` and
  `scripts/analyze_stable_ids_control_gpt_n5.py`.

---

### 2026-08-21 — Public-ledger Myth→Game extension: positive, unresolved

- Froze and ran five matched GPT-5 Nano public-ledger Myth→Game populations
  after inspecting the game-only ledger screen. All five new runs passed with
  800 accepted responses, no retries/errors, exact ledger reconstruction, and
  matched schedules.
- Myth→Game raised final balance from 62.04 to 64.30 under the ledger: +2.26
  per agent (95% paired CI [−1.30, +5.82], p=.152, dz=.79). Two of five
  matched populations did not improve, so this is directional rather than
  resolved.
- The public-ledger task effect was not distinguishable from the private-memory
  interaction (+2.04, p=.176) or the partner-dossier interaction (−1.36,
  p=.279).
- About 62% of the public-ledger balance gain came from round 1, before ledger
  rows existed (.760 versus .480 sent). The evidence is more consistent with a
  myth countering the initial public-monitoring frame than with a demonstrated
  improvement in agents' processing of ledger history.
- Frozen protocol, report, and analysis:
  `docs/population_ledger_myth_game_protocol_2026-08-21.md`,
  `docs/population_ledger_myth_game_gpt_n5_overview_2026-08-21.md`, and
  `scripts/analyze_population_ledger_myth_game_gpt_n5.py`.

---

### 2026-08-21 — Public population ledger: cooperation does not increase

- Implemented a population-wide public-ledger history arm with stable neutral
  pseudonyms and the last three complete population rounds. The ledger exposes
  only communicated/noisy transfers and identifies the current co-player; an
  exact auditor reconstructs every row and ID mapping from saved data.
- Ran the matched GPT-5 Nano game-only screen (`n=5` populations/arm) against
  private memory and the current-partner dossier. All 15/15 runs passed jointly:
  1,200 accepted decisions, 1,200 noise checks, no retries/errors, and matched
  schedules.
- Mean final balance was 66.03 private, 62.64 dossier, and 62.04 public ledger.
  Ledger − private was −3.99/agent (95% CI [−7.20, −0.77], raw p=.026, Holm
  p=.052); ledger − dossier was −0.60 (p=.404). The difference is carried by
  sending, not return ratios.
- The ledger arm was already lower in round 1, before any history rows existed
  (.480 versus .620 sent under private memory). This identifies the treatment
  as a public-monitoring package—stable IDs, anticipated observability, and
  later records—not a clean estimate of learning from population history.
- Report and reproducible analysis:
  `docs/population_ledger_gpt_n5_overview_2026-08-21.md` and
  `scripts/analyze_population_ledger_gpt_n5.py`.

---

### 2026-08-21 — Independent confirmation: no history × Myth→Game interaction

- Froze and ran a new-seed `2 × 2` GPT-5 Nano confirmation (`n=10`
  populations/cell; replicate IDs 5–14) before inspecting outcomes. It crossed
  private interaction memory versus current-partner dossier with Game only
  versus Myth→Game.
- All 40/40 runs passed the joint expanded audit: 4,800 accepted responses,
  4,842 attempts, 42 recovered myth-boundary retries, 3,200 noise checks, no
  unrecovered failures, and matched schedules.
- The preregistered final-balance difference-in-differences was +0.50/agent
  (95% CI [−1.95, +2.94], p=.655, dz=.15). The exploratory claim that
  Myth→Game specifically eliminates the partner-dossier penalty is not
  confirmed.
- Secondary estimates suggest roughly additive effects: dossier − private was
  −1.81 in Game only (p=.084) and −1.32 in Myth→Game (p=.013); Myth→Game −
  Game only was +1.18 under private memory (p=.237) and +1.68 under the dossier
  (p=.017). These secondary p values are unadjusted.
- Frozen protocol, analysis, and report:
  `docs/history_visibility_confirmatory_protocol_2026-08-21.md`,
  `scripts/analyze_history_visibility_confirmation_gpt_n10.py`, and
  `docs/history_visibility_confirmation_gpt_n10_overview_2026-08-21.md`.

---

### 2026-08-21 — Exploratory result: apparent Myth→Game buffering

- Completed the clean paired GPT-5 Nano `2 × 3` history-visibility by task-
  order screen (`n=5` populations/cell). The contrast is private interaction
  memory versus the same memory plus the current co-player's last three games.
- The selected 30/30 runs passed the expanded joint audit: 4,000 accepted task
  responses, 4,019 total attempts, 19 explicit recovered myth retries, 2,400
  transfer-noise checks, no unrecovered errors, and matched schedules across
  all six cells.
- The partner dossier reduced balance by −3.39/agent in Game only (95% CI
  [−5.02, −1.75], Holm p=.014) and −2.74 in Game→Myth (raw p=.026, Holm
  p=.052), but had no effect in Myth→Game (+0.01, p=.989). Under the dossier,
  Myth→Game beat Game only by +3.63 (95% CI [2.45, 4.80], Holm p=.003); under
  private memory, the same contrast was +0.23 (p=.804).
- The Myth→Game visibility interaction was +3.40 (95% CI [0.70, 6.10], raw
  p=.025, Holm p=.050 across two interactions). Exploratory interpretation:
  explicit partner history facilitates targeted retaliation, while a myth
  immediately before play buffers that penalty. The independent confirmation
  above did not reproduce this interaction.
- Reproducible analysis and full caveats:
  `scripts/analyze_history_visibility_factorial_gpt_n5.py` and
  `docs/history_visibility_factorial_gpt_n5_overview_2026-08-21.md`.

---

### 2026-08-21 — Correction: GPT-5 Nano task-order replication

- The initial same-day audit did not test whether an accepted myth was actually
  a myth. It therefore missed two selected-run failures where GPT returned
  decision JSON instead of a story. The affected Game→Myth replicate 1 and
  Myth→Game replicate 0 are now excluded and replaced by exact-seed clean runs.
- The corrected selected means are 62.64 / 62.34 / 66.26 for Game only /
  Game→Myth / Myth→Game. Myth→Game exceeds Game only by +3.63 (95% CI
  [2.45, 4.80], Holm p=.003) and Game→Myth by +3.92 ([1.38, 6.47], Holm
  p=.026); Game→Myth versus Game only is −0.30 (p=.779).
- The cross-model Myth→Game ordering is therefore preserved and stronger, but
  the original values are superseded. The expanded audit now applies the same
  task-boundary validator used at runtime.

---

### 2026-08-20 — Result: return-vs-send gap is a denominator artifact

**Time:** 1.0 hour

#### What we found
- The 11/02 call-note question ("why is trustee behavior always lower than investor behavior?") is resolved: the plots normalize send by the $5 endowment but return by the *tripled* amount received. In dollars, receivers returned more than was sent in 98.5% of the 1,500 corrected confirmatory dyad-rounds (zero zero-sends), and return/sent sits ~150% in every cell. Senders profit; the lower return line is a chart artifact, not stinginess.
- Mechanism: receivers anchor on "return half of the tripled pool" as a fairness focal point (~50–54% in all six cells, present in game-only runs, stabilized by myths), while sends drift up to 70–90% of endowment. The old zero-send explanation is retracted for the corrected data. Human lit shows the same normalized ordering (Johnson & Mislin 2011: ~50% sent, ~37% returned = ~break-even in dollars); LLM lit is mixed.

#### What changed
- Fixed three analysis-metric problems: zero-received rounds now yield NaN (no-opportunity) instead of 0% cooperation; endowment inference corrected to payoff + sent − returned; inspector uses each run's configured endowment instead of hardcoded $5. Regression tests in `tests/test_analysis_metrics.py` (48 passed).

#### Known gaps
- Charts still overlay the two mismatched ratios on one axis; planned fix is a returned/sent line plus reference lines at 1/3 (sender break-even) and 1/2 (split the pool).

---

### 2026-08-19 — Result: 8-agent washout — edge grows

**Time:** 0.5 hour

#### What ran
- Completed the 8-agent 20-round washout at n=5/arm (`noise8i_washout_myth_game` resumed from checkpoints + `noise8i_washout_game_myth` fresh; Sonnet 4.5, informed bidirectional noise, memory-primary, `--workers 1` after three OOM kills at higher worker counts). Data: `data/json/noise_experiments/washout_20round/noise8i_*`; plot: `data/plots/myth_taskorder_trajectories/washout_20round_8-agent.png`.

#### Headline results
- The Myth→Game edge does NOT wash out at 8 agents — it compounds: cumulative-balance lead +11.4/agent at round 10 → +17.9 at round 20 (vs the 2-agent result where per-round sends converge and the lead plateaus ~+6).
- Per-round sends never converge: Myth→Game jumps to ~4.9/5 by round 4 and stays; Game→Myth cold-opens ~3.0 and only reaches ~4.4 by round 20.

#### Known limit
- n=5/arm (dropped from 10 for time/memory) — directional, not confirmatory. One myth_game replicate is filed as `rep00_*_2.json` (independent rerun of the rep00 cell; pooling the folder yields the intended n=5).

---

### 2026-08-19 — Result: meme evolution traced

**Time:** 1.0 hour

#### What ran
- Added a deterministic ontology of nine strategy memes with variants, then traced inheritance, variant shifts, new-to-lineage appearances, recombination candidates, survival, and partner-myth→game uptake over all 60 corrected runs. The corpus contains 12,033 meme occurrences and 77,909 visible exposure edges; outputs are in `data/analysis/meme_evolution_2026_08_19/`.

#### Headline results
- Myth-bearing conditions contain more ideas per capsule and much more inheritance: 2-agent game-only 1.78 (±0.21) memes/capsule and 66.12% (±3.91%) inherited, versus game→myth 2.69 (±0.42) / 87.49% (±2.94%) and myth→game 2.79 (±0.56) / 87.58% (±2.99%). The 8-agent pattern is similar.
- Proportional reciprocity is the dominant meme: 74.61% (±16.27%) capsule prevalence, 76.67% (±17.28%) edge transmission, and 82.76% (±17.13%) partner-myth→game transmission. About 25–31% of retained memes change variant across conditions, usually between fixed-percentage and responsive-reward formulations.
- Found 62 candidate numerical partner-myth→game belief packets. A strict detector requiring explicit myth attribution plus an actual/perceived contrast found two clear decodings, both in the same 2-agent myth→game run; this is real but not yet shown to be common.

#### Known limit
- Meme families are predeclared lexical-semantic detectors, and visible transmission is not behavioral selection. The next causal test is controlled meme deletion/transplant with actions held fixed, followed by free-play validation.

---

### 2026-08-19 — Result: capsule genealogy quantified

**Time:** 1.0 hour

#### What ran
- Added a deterministic, no-LLM genealogy over all 60 corrected informed-noise runs: 5,000 visible assistant capsules, 52,425 claim instances, and 32,700 verifiably visible parent→child edges. Outputs and reproduction report are in `data/analysis/capsule_genealogies_2026_08_19/`.
- Claims are separated into event references, round/action quantities, rates, and predeclared normative frames; edges come only from exact `messages_sent` provenance.

#### Headline results
- Exact fact inheritance is strongest in dyads: 42.92% (±10.19%) game-only, 56.76% (±10.37%) game→myth, and 61.11% (±15.49%) myth→game, versus 11.35% (±2.80%), 13.22% (±4.06%), and 14.97% (±2.16%) in the corresponding 8-agent cells.
- In dyadic myth→game, 30.27% (±6.20%) of event references reached earlier than the oldest literal game prompt still in context; the 8-agent counterpart was 2.49% (±3.27%). Norm inheritance was ~90% in every myth-bearing cell.
- The hand-traced noisy-belief chain reproduces automatically: Agent_1's round-7 myth carries its perceived 79% round-6 send into Agent_2's round-8 game reasoning, where Agent_2 contrasts it with its actual 65% send.

#### Known limit
- This establishes visible textual inheritance, not causal influence. Nonexact round/action quantity pairs remain labelled `different_quantity_candidate` because unresolved actor perspective can mimic mutation; deletion/transplant ablations are required for causality.

---

### 2026-08-13 — Corrected informed-noise confirmatory rerun completed

- Completed all six corrected non-defector cells (2/8 agents × game,
  game→myth, myth→game), `n=10` independent runs per cell. The strict audit
  passed all 60/60 runs: 5,000 accepted interactions, 5,000 LLM calls, 3,000
  numerical noise checks, and zero errors, recovered retries, forced responses,
  or protocol violations.
- Corrected final balances (mean per agent) were 64.86 / 62.94 / 69.83 in the
  2-agent repeated-dyad regime and 59.26 / 60.51 / 66.33 in the 8-agent rotating
  population. Game→myth did not beat game only in either regime, and its
  population-regime interaction was not detected: difference-in-differences
  +3.16, 95% CI [−2.04, 8.36], p=.218.
- Myth→game remained highest in both regimes. Both 8-agent myth→game contrasts
  survived Holm correction across the six within-population balance tests; the
  analogous dyad contrasts were suggestive but did not.
- The saved noise/pairing seeds are null, so the analysis uses independent-group
  Welch tests rather than the pairing originally intended in the preparation
  note. Raw JSON remains gitignored and should be archived before publication.
- Full implementation overview, figures, statistics, caveats, and next steps:
  `docs/corrected_v2_confirmatory_overview_2026-08-13.md`. Reproducible analysis:
  `scripts/analyze_corrected_v2_confirmatory.py`.

---

### 2026-08-12 — Corrected non-defector confirmatory rerun prepared

- Hardened simulation-level retries: an unanswered prompt is now removed from
  private chat memory after an exhausted provider call, matching the myth-
  validation retry contract. Rejected attempts remain in the interaction audit
  but cannot change the clean retry context.
- Updated `scripts/audit_v2_protocol.py` to distinguish accepted interactions
  from recovered retry attempts. It requires exactly one accepted task response
  per agent/round, fails unrecovered retries, and computes memory-message counts
  from accepted interactions only.
- New runs record non-secret execution provenance: Git commit and dirty-state,
  config SHA-256, effective provider route, resolved provider model, and the
  effective max-output-token setting/source.
- Expanded the fixed-pair population isolation into a complete 2 x 3 design:
  2 versus 8 agents crossed with game-only, game->myth, and myth->game. All
  cells use fixed partners, unified prompts, hidden names, no injected history,
  paired noise seeds, and a matched three-round private-memory horizon.
- Raised the six corrected population-regime v2 cells from 5 to 10 fresh
  replicates each. `scripts/run_corrected_v2_confirmatory_20260812.sh` refuses
  a dirty worktree, fixes routing to direct Anthropic, writes to a new output
  directory, requires 10 final JSONs per cell, and audits each cell before
  continuing. This entry records protocol preparation only, not outcomes.

---

### 2026-08-12 — Scripted 8-agent defector treatment implemented

#### Design
- Added an explicit `defector_action_policy: forced_zero`. Designated agents no
  longer make LLM calls for game decisions: senders deterministically emit
  `{"send": 0}` and receivers emit `{"return": 0}`.
- The scripted game prompt/response is still appended to each defector's private
  memory under `memory_primary`. Defectors use the ordinary LLM path for myth
  writing (`defector_myth_policy: normal`), so game behavior is fixed while
  cultural output remains endogenous.
- The primary cells set `defector_role_visible_to_self: false`: neither the
  treatment label nor the phrase "designated defector" appears in the agent's
  game prompt. Other agents are never given private treatment identities.
- Legacy defector configurations retain their prompt-driven behavior unless
  they explicitly select `forced_zero`.

#### Planned experiment (not outcome evidence yet)
- Added paired 0%-versus-25% (0 versus 2 of 8) controls for game-only,
  game→myth, and myth→game. All use balanced rotating pairings, anonymous
  identities, informed bidirectional ±1 noise, unified prompts, no injected
  game-history recap, and paired pairing/noise seeds.
- The two-task cells use capacity 6 and game-only uses capacity 3, retaining
  approximately three completed rounds of private interaction memory.
- The protocol audit now checks that all forced actual actions are zero, forced
  game responses make no LLM calls, defector myths do use the LLM, and the
  hidden treatment label does not leak into prompts.

---

### 2026-08-12 — Population/reputation isolation hardened

#### Why the earlier decomposition is not confirmatory
- The `noise2i_full8match_game` dyads still used the broken zero-send transfer
  path, while the matched 8-agent runs used the clean path.
- The 2-agent path also ignored `self_history_window` and
  `coplayer_history_window`; `history_policy: minimal` injected one own-game
  recap rather than removing history; and the fixed-pair system prompt still
  claimed that pairings were randomized. The proposed named-fixed test also
  exposed repeated partnership through "against you" co-player history.
- Consequently, the reported 2-vs-8 separation and its anonymity mechanism are
  not established. The transfer-clean 8-agent files remain exploratory
  within-population evidence.

#### Implementation
- Ported validated `pairing_mode: fixed` support onto the corrected branch.
  Fixed populations now receive accurate same-opponent/alternating-role system
  instructions, while legacy balanced prompts remain unchanged.
- Added `prompt_regime: unified`, which routes both 2- and 8-agent later rounds
  through the same sender/receiver builder and makes the configured history
  policy apply at both population sizes.
- History and prompt-regime values now fail closed on unknown strings. New
  causal cells use `history_policy: none`, so own decisions remain solely in
  individual chat memory and no synthetic self/co-player record is injected.
- Pairing mode, effective pairing mode, prompt regime, windows, name visibility,
  pairing seed, and noise seed are recorded in logs, JSON metadata, and transcript
  PDFs. Exogenous pairing schedules and per-event noise are paired by replicate
  and reproducible in the new cells.

#### New planned cells (not outcome evidence yet)
- `noise_population_isolation_v2_game`: fixed 2-agent versus fixed 8-agent,
  identical configuration except `num_agents`, capacity 3, hidden names, no
  injected history, and the unified prompt regime.
- `noise8i_identity_v2_game`: rotating 8-agent named versus anonymous, identical
  except name visibility, with no injected co-player block. Stable names are
  therefore the only partner-identity cue available across re-encounters.

---

### 2026-08-12 — Protocol repair: corrected dyad noise and matched-memory v2

#### What changed
- Fixed the dyad later-round transfer path: communicated-send noise is now
  generated only for the receiver, after the sender's actual transfer exists;
  a missing current transfer raises instead of falling back to zero.
- Retained the game-side instruction, "Take any myths written in this session
  into account when making your decision." It is now appended through one
  shared game-prompt finalizer, exactly once in every current game prompt for
  both myth orders, both roles, all rounds, and both population regimes.
- Added corrected informed-noise v2 triplets. Chat memory is matched to an
  approximately three-round horizon: capacity 3 for game-only and 6 for
  game+myth conditions, for both 2- and 8-agent runs.

#### Interpretation and status
- The 8-agent arm intentionally retains balanced rotating partners, anonymous
  identities, and a three-game co-player reputation block. The planned contrast
  is therefore **repeated dyad vs rotating population with reputation
  information**, not a pure manipulation of agent count with all other
  information held fixed.
- The 2026-08-10 dyad results were produced by the broken transfer path and
  cannot establish a population-size interaction; all six v2 cells require a
  new adequately powered batch before updating the result claim.

#### Smoke gate completed
- Ran one full 10-round Sonnet 4.5 replicate in each of the six corrected v2
  cells (2/8 agents x game/game_myth/myth_game). All 6/6 completed without an
  API, parsing, or simulation error.
- `scripts/audit_v2_protocol.py` checked all final JSONs: 60 rounds, 150 dyads,
  500 LLM calls, and 300 numeric send/return noise checks. It also verified
  completeness, informed-noise notices, exact current-prompt myth-link counts,
  configured memory-message counts, and the intended 8-agent co-player history
  blocks. **Zero issues.**
- This is a protocol smoke test (`n=1` per cell), not outcome evidence. Before
  the confirmatory batch, add recorded/paired pairing and noise seeds and choose
  durable raw-data storage (the current `data/json/` tree is gitignored).

---

### 2026-08-10 — Result: game_myth vs game is a population-size effect

> **Superseded on 2026-08-12:** the dyad transfer-noise audit found that all
> post-round-1 receivers were shown transfers near zero. The results below are
> retained as historical provenance but do not establish a population-size
> effect. See the corrected v2 protocol above.

#### What ran
- Built the missing post-fix informed dyad triplet to isolate why game_myth < game at 8 agents but > game in older dyad data. New game_params `noisy_bidirectional_informed_memprimary` (= `noisy_bidirectional_memprimary` + `inform_agents: true`) and three sets `noise2i_memprimary_{game,game_myth}` / `noise2i_memtest_memprimary` (config/experiments_noisy.yaml). Sonnet 4.5, 2-agent, memory-primary, uniform ±1.0, informed, n=5 each, 15/15 clean, ~$8 via OpenRouter. Plot `scripts/noise2i_dyad_taskorder_boxplot.py` → `data/plots/noise2i_dyad_triplet/`.

#### Headline numbers (final balance, run-level, n=5)
- **2-agent informed:** game 46.25 (±2.57) / game_myth 53.44 (±6.45) / myth_game 60.60 (±4.26) → **game_myth beats game by +7.2**.
- **8-agent informed (existing, standard prompt):** game 60.55 (±1.57) / game_myth 59.95 (±2.30) / myth_game 66.91 (±1.66) → game_myth −0.6 vs game.
- Everything else matched (memory fix, informed noise, ±1.0); the only axis that flips the game_myth-vs-game contrast is **population size**. The old "game_myth > game" memory was the dyad regime, not a pre-fix double-memory artifact — now confirmed on clean post-fix data.

#### Known gaps
- Why population size erases the game_myth edge is not itself pinned (co-player history block + rotating partners "buffer" dynamics per the 2026-07-17 noise entry, but that was about noise robustness). A 2-vs-8 sweep holding all else fixed would isolate it. Myth→Game stays the strongest ordering at both sizes.

---

### 2026-07-23 — Result: context audit — nothing dropped across 3,600 calls

#### What ran
- Per-call context audit over all 25 informed-noise runs (`scripts/audit_context_integrity.py`), checking every call's actual `messages_sent`: own-myth window exactly the most recent min(3, available) rounds (verbatim match), partner myth quoted verbatim in later myth prompts, co-player block present with exactly min(r-1,3) entries, informed-noise notice in every system prompt, no self-history blocks or own-myth recaps, no empty messages/responses/errors, full round/dyad/myth/response counts.

#### Headline
- **25 runs, 3,600 LLM calls, zero issues** — both triplets (standard + lineage) stand on verified context plumbing.
- Audit validated by negative control (three planted corruptions): first version missed a myth dropped from the *old* edge of the window (contiguity check is blind there) — tightened to exact-window matching, after which all three plant types are detected. Lesson: audits need negative controls too.
- Script is reusable: `python scripts/audit_context_integrity.py <run_dirs...>` — run as standard post-batch QA in the rerun campaign.

---

### 2026-07-23 — Result: lineage triplet — fidelity amplifies the ratchet in both directions

#### What ran
- Completed the lineage-prompt task-order triplet under informed noise: new `noise8i_memprimary_game_myth_lineage` (5/5 clean, ~$14) + existing myth_game lineage cell + existing game-only cell (lineage cannot apply there — no myth prompt; same condition by construction). Plots: `data/plots/noise8i_lineage_triplet/`.

#### Headline numbers (run-level, n=5/condition)
- Final balance: myth_game $70.69 (±$3.60) vs game $60.55 (±$1.57) vs game_myth $59.00 (±$2.69). Trust ratio 0.914 (±0.072) / 0.711 (±0.031) / 0.680 (±0.054).
- vs the standard-prompt informed triplet: myth_game rose ($66.91→$70.69), game_myth did not ($59.95→$59.00). **Higher lineage fidelity amplifies whatever the myths crystallize** — pre-game ideals (myth-first) get stronger; post-game caution (game-first) stays anchored. The cultural ratchet cuts both ways, now with the fidelity knob demonstrated in both directions.

---

### 2026-07-23 — Result: lineage pointer restores fidelity and amplifies the myth effect

#### What ran
- A/B under informed noise (myth→game, 8 agents, memory-primary, n=5 vs n=5, ~$14 via OpenRouter fallback — direct-Anthropic balance ran dry again mid-week): standard myth prompt vs lineage variant adding "Base it on the myths you wrote earlier this session" (attention pointer to own 3-round myth memory; no content duplication). Set `noise8i_memprimary_myth_game_lineage`; plots `data/plots/noise8i_lineage_ab/`. Deliberately did NOT restore the game-side `myth_decision_link` — it would instruct the dependent variable and confound the task-order contrast.

#### Headline numbers
- **Self myth similarity 0.709 (±0.020) → 0.839 (±0.014), p<0.001** — lineage fidelity restored to (above) the pre-fix level (0.823), now without the duplication bug.
- Population myth similarity 0.692 → 0.719 (no diversity collapse; run-level spreads intact).
- **Not behaviorally inert**: trust ratio 0.838 (±0.033) → 0.914 (±0.072), p=0.109; sent 4.19 → 4.57; return ratio 0.513 → 0.543. Higher transmission fidelity amplified the myth→cooperation effect — with the decision side still uninstructed.

#### Reading
- Failure of the "inertness" criterion is the informative kind: fidelity acts as a moderator of culture→behavior — textbook cumulative-culture theory, and the game side stayed clean. Decision open: adopt lineage as canonical for the rerun campaign, or keep both cells as a low/high-fidelity contrast (the standard cell is already in hand, so the contrast is free).

---

### 2026-07-22 — Result: myth-first boost holds in the informed-noise condition

#### What changed
- Standing directive from Ivar: **informed noise is now the default test condition** for every new experiment (saved to project memory + this log). `inform_agents: true` suffices — `trust_game_noisy.py:133` auto-appends the noise notice to the system prompt.
- Ran the 8-agent memory-primary task-order triplet under informed noise (`noise8i_memprimary_*`, n=5 each, 15/15 clean, ~$40). Plots: `data/plots/noise8i_memprimary/`.

#### Headline numbers (run-level, n=5/condition, informed noise)
- Trust ratio: myth_game 0.838 (±0.033) vs game 0.711 (±0.031) vs game_myth 0.699 (±0.046). Final balance: $66.91 (±$1.66) vs $60.55 (±$1.57) vs $59.95 (±$2.30).
- Third regime, same result: plain 0.892/0.716/0.653, uninformed noise 0.851/0.731/0.692, informed noise 0.838/0.711/0.699. Telling agents about the noise barely moves anything (informed ≈ uninformed on every metric; tighter spreads).
- The myth-first boost is now replicated across plain, uninformed-noise, and informed-noise regimes at 8 agents.

---

### 2026-07-20 — Result: game_myth plateau is a myth-content effect, not a memory confound

#### What ran
- Disambiguation for the game_myth < game-only deficit: game-only 8-agent plain with `memory_capacity: 3` (equal memory *rounds* to game_myth's 3) — `sonnet45_8agent_game_memprimary_mem3_r10_n5`, 4/5 clean (~$7; 1 run died on the direct-Anthropic `max_tokens=1024` truncation — now 4096 via `ANTHROPIC_MAX_TOKENS`, see verified-facts).
- Also verified myth carry-over in game_myth: previous-round partner's myth appears verbatim in all 9 later-round prompts; own myth reaches game calls via memory. No passing bug.

#### Headline numbers
- cap3 game-only escalates like cap6: sent r1→r10 3.06→4.00 (run mean 3.54 ±0.53) vs cap6 3.15→3.95 (3.58 ±0.36); game_myth stays flat 3.10→3.35 (3.27 ±0.35). **Memory depth ruled out; the plateau follows the myths.**
- Reading: directive myths written *after* play codify the cautious status quo and anchor it (cultural ratchet cuts both ways: myth-first locks in pre-game generosity, game-first locks in round-1 caution). Round-1 sends are identical across game/game_myth (~3.0–3.2), as their round-1 contexts are structurally identical — the gap develops through rounds.
- Design fact recorded in verified-facts: `{other_agent_myth}` is the **previous** round's partner's myth (one-round gossip-lag diffusion; never informative about the current partner) — kept deliberately: myth influence stays cultural, not strategic signaling.

---

### 2026-07-17 — Result: myth-first cooperation boost replicates under 8-agent noise

#### What ran
- Task-order triplet (game / game_myth / myth_game) under bidirectional noise at 8 agents, memory-primary (`noise8_memprimary_*`, n=5 each, 15/15 clean, ~$40); plus the dyad-level version (`noise_memprimary_{game,game_myth}`, ~$7). Smoke caught the same window-0 bug in `TrustGameNoisy._format_multi_agent_history` (own copy of the history block without the skip) — fixed before the paid batch. Plots: `data/plots/noise8_memprimary/`.

#### Headline numbers (run-level, n=5/condition, 8-agent noise)
- **Myth-first boost replicates almost exactly**: trust ratio 0.851 (±0.094) myth_game vs 0.731 (±0.023) game vs 0.692 (±0.036) game_myth (plain-game triplet: 0.892 / 0.716 / 0.653). Final balance $67.55 (±$4.70) vs $61.54 (±$1.18) vs $59.61 (±$1.82) (plain: $69.60 / $60.80 / $57.65).
- **Population buffers noise**: 8-agent noise trust stays at plain-game levels, unlike dyads under the same noise (which collapsed to ~0.4 trust, balances ~$42–47). The co-player history block + rotating partners appears to prevent the death spiral a single noisy relationship falls into.
- Dyad-level noise triplet, same ordering compressed: $46.69 / $45.51 / $42.15 (myth_game / game_myth / game).

#### Reading
- The core task-order finding is robust across game regime (plain/noise) and population size (2/8) under the fixed memory design. Noise robustness at the population level is a potential paper point in itself.

---

### 2026-07-17 — Result: noise pilot confirms memory-primary; drift tracks game visibility

#### What ran
- Memory-channel pilot repeated under bidirectional noise (`noise_memtest_{hybrid,stateless,memprimary}` in experiments_noisy.yaml; uniform ±1.0 on communicated amounts, uninformed; Sonnet dyads, myth→game, r10, n=5/arm, ~$9, 15/15 clean). Plumbing added to run_noisy_batch (chat_memory_mode, game_prompt_keys). Smoke caught a real parser bug: Haiku answered `{'return': $6.66}` and `_extract_amount` rejected the `$` — both game classes now accept optional `$` before the number.

#### Headline numbers (run-level, n=5/arm)
- **Noise creates real dynamics and the channels still don't separate on game play**: trust collapses everywhere (sent ~3.8 → ~1.5 by r6); sent 2.42 (±0.23) / 2.26 (±0.47) / 2.17 (±0.27), all pairwise p>0.19. Return ratio 0.12 (±0.04) / 0.12 (±0.06) / 0.08 (±0.02).
- **Myth drift is the significant separator**: self-sim r vs r-1 memory-primary 0.676 (±0.051) vs hybrid 0.826 (±0.035) and stateless 0.850 (±0.061) — p=0.002 vs both. Under a turbulent game, memory-primary myths respond (drift); the other designs' myths stay insulated — their myth calls see only a one-line game summary, while memory-primary myth calls see the full game rounds in memory.

#### Decision
- **Memory-primary confirmed for the rerun campaign.** Game behavior is channel-robust in both placid and turbulent regimes; memory-primary is the only design whose linguistic layer visibly couples to game events — which is the phenomenon the paper studies.

---

### 2026-07-17 — Result: task-order effect survives the memory fix

#### What ran
- Completed the standard game / game_myth / myth_game condition triplet for the fixed 8-agent memory-primary regime (`sonnet45_8agent_{game,game_myth}_memprimary_r10_n5`, n=5 each, ~$20). First attempt failed 10/10 on an empty direct-Anthropic credit balance; reran via `LLM_PROVIDER=openrouter` (fact + fallback recorded in docs/verified-facts.md). Standard-layout plots: `scripts/memprimary_taskorder_boxplot.py`, per-run trajectories via `analyses/trajectory_plotting_8agent.py` → `data/plots/memprimary_8agent/`.

#### Headline numbers (run-level, n=5 per condition)
- **Myth-first boosts trust ~25%**: trust ratio 0.892 (±0.082) myth_game vs 0.716 (±0.073) game-only vs 0.653 (±0.070) game_myth; mean sent $4.46 vs $3.58 vs $3.27.
- Return ratio near half everywhere: 0.529 (±0.021) / 0.505 (±0.010) / 0.537 (±0.019); game-only is the most locked-in (stability 0.006).
- Gotcha fixed: billing-failed first attempts leave `*.checkpoint.json.error.json` snapshots in data dirs — loaders must exclude them (initially inflated n to 10 and skewed game-only means).

#### Reading
- Writing myths *before* playing raises cooperation from round 1; playing first anchors on cautious play that a later myth doesn't lift. The cross-task influence finding survives the double-memory fix with a clean information story: each fact enters context once.

---

### 2026-07-17 — Result: 8-agent memory-primary test vs June baseline

#### What ran
- Fixed 8-agent regime test: `sonnet45_8agent_myth_directive_history3_anon_memprimary_r10_n5` (memory-primary; self_history_window 0, coplayer window 3, memory_capacity 6 pairs = 3 rounds, co-player-myth-only later template), n=5, 5/5 clean, ~$14. Compared against the June 8 double-memory baseline with `scripts/memprimary_8agent_compare.py`; plots `data/plots/memprimary_8agent/`.

#### Headline numbers (n=5 vs n=5)
- **The bug was inflating the generosity ratchet.** Both regimes escalate (unlike static dyads), but baseline saturates: sent r1→r10 4.30→5.00 vs fixed 3.95→4.60; return ratio 0.607 (±0.046) vs 0.529 (±0.021), r10 0.62 vs 0.54. Triple-counted cooperative history (recap + memory + reasoning) stacked the evidence of generosity.
- **The bug was suppressing myth evolution.** Self-similarity r vs r-1: baseline 0.823 (±0.022) vs fixed 0.688 (±0.058) — verbatim "here is the myth you wrote" recaps anchored self-copying; without them lineages actually drift. Population myth similarity unchanged (0.689 vs 0.694) — convergence level is robust.

#### Reading
- Fixed regime keeps the qualitative story (escalating cooperation, myth convergence) but with honest magnitudes and livelier lineage dynamics. June-baseline myth-stability numbers should not be compared 1:1 with post-fix runs.

---

### 2026-07-17 — Result: memory-channel pilot — game invariant, myth diversity differs

#### What ran
- Double-memory bug confirmed (rounds appear 2–3× in context: chat memory + in-prompt history recaps; and memory_capacity counts interactions, not rounds). Two fixed designs implemented and piloted head-to-head with information parity: **hybrid** (own myths in chat memory/assistant slot; game history in-prompt only) vs **stateless** (no memory; everything in one flat prompt). Sonnet 4.5, 2-agent dyads, myth→game, r10, n=5 per condition, ~$6. Sets `memtest_{hybrid,stateless}_sonnet45_2agent_r10_n5`; comparison `scripts/memtest_compare.py`; plots `data/plots/memtest_memory_channels/`.

#### Headline numbers (run-level, n=5)
- **Game play: channel-invariant.** Sent 3.80 (±0.75) vs 3.80 (±0.40); return ratio 0.527 (±0.023) vs 0.500 (±0.000) — stateless returns exactly half every round of every run.
- **Myths: stateless collapses diversity.** Cross-agent similarity 0.719 (±0.100) hybrid vs 0.820 (±0.021) stateless; self-similarity r vs r-1 0.748 (±0.082) vs 0.817 (±0.017). Means p≈0.11–0.17 (n=5), but the variance collapse (±0.02 vs ±0.10) is the signal: stateless runs are near-deterministic and homogeneous; hybrid keeps lineage drift and divergence.

#### Third arm + revised decision (same day)
- User flagged that hybrid amputates the reasoning→myth pathway (game calls unremembered ⇒ myths never see the agent's strategic reasoning). Added **memory-primary**: both tasks remembered; duplication fixed on the prompt side instead (`_minimal` game templates without last-round recap via new `game_prompt_keys` set override; myth prompt carries only co-player myth). Smoke-verified: no fact appears twice; transcript shows game reasoning quoting both myths — the co-evolution loop is active. Sonnet arm n=5, ~$3.
- Results: cross-agent myth sim 0.774 (±0.049) and self-sim 0.722 (±0.076) — patterns with hybrid (drift preserved), not stateless (homogenized). Game side: **no interpretable treatment effect** — all dyads freeze their round-1 send for all 10 rounds, r1 contexts are identical across memory arms, so run means are 5 initial draws (hybrid [3,3,4,4,5], mp [4,4,4,5,5]); the earlier "hybrid vs stateless game invariance" claim survives, the mp 4.4 vs 3.8 sent difference is initial-draw noise.
- **Decision: memory-primary for the reruns.** Fixes the double-memory bug, keeps linguistic diversity ~hybrid, uniquely preserves reasoning↔myth co-evolution, and is the closest fixed design to the existing runs. Before the 8-agent rerun: reconcile memory_capacity (interaction pairs) with the 3-round in-prompt co-player history block.

---

### 2026-07-17 — Clean public-facing repo split from research repo

#### What changed
- Created `github.com/ivarfresh/linguistic-evolution-toolkit` (private for now): fresh single-commit export of the clean tree — code, configs, docs, phase 2–9 summary metrics/figures, manuscript sources, two sample runs in `data/sample/`. 95 MB / 866 files vs the 7.2 GB research repo. Excluded: `data/json|plots|share` (4.5 GB raw outputs), `archive/`, `reports/`, reference PDFs, Quarto build dirs.
- This repo stays the full private archive (all data + history). Raw data to be archived on Zenodo (link TBD) before the new repo goes public — also re-check NeurIPS anonymity before flipping visibility.
- Cleanup landed here too (`19f0d220`, `34a74425`): root `README.md`, `.env.example` (was referenced by CLAUDE.md but missing), `public_goods_game.py` → `archive/` (nothing imports it), broken `reciprocity` case removed from `run_all_analyses.sh`, `*.npz` gitignored, `data/README.md` + samples.

#### Known gaps
- New repo has no history (by design); `main` here is still 30+ commits behind this branch; ~13 unreferenced `analyses/*.py` scripts left in place pending a keep/drop decision.

---

### 2026-07-03 — Result: Fable seed regeneration; jabberwocky blocked twice over

#### What ran
- Regenerated gowith + jabberwocky seed pools with **Claude Fable 5 as translator** (`scripts/phase9_fable_seeds.py`, ~$20 incl. debug reruns). All seeds verified with Sonnet readback + the exact-game-context host refusal probe. Fable API quirks hit and recorded in `docs/verified-facts.md`: rejects explicit `temperature`; reasoning model — thinking shares `max_tokens` (2048 → zero text; use ≥16k).

#### Headline
- **`s_end_plus_gowith_fable`: usable — 5/5 translated, 4/5 pass the host probe**, readback recovers the recipe (send 5, rf 0.5/0.67) on 3 of the 4 passing. Registered in the manifest. Required steering Fable to gowith's flowing-prose register — its default hyphen-compound register ("Meet-settle: Keeper-with…") was host-refused 3/3.
- **Jabberwocky is blocked at two independent layers:** (1) **Fable-as-translator refuses** — 6/10 hard refusals, with a stark content asymmetry: 5/5 refusals on strategy-laden s_end+ myths vs 1/5 on innocent s_start parables; (2) of the 5 it did translate, **Sonnet-as-host refused 4/5** in the assistant slot (exact-context probe 4/4) — replicating the Phase 5 finding with a different translator. Net: 1 usable jabberwocky seed (`s_start_jab_fable`, 4 registered, 1 probe-pass). Jabberwocky cells stay unrunnable on a Sonnet host; workarounds remain system-prompt placement or a non-refusing host model.
- **Seed 4's curse replicates across translators**: the gowith translation of s_end_plus[4] is host-refused 4/4 whether Sonnet or Fable wrote it — strengthens the content×style×context conjunction finding (same seed, two independent translations, two translator models).

#### Artifacts
- Candidates + per-seed probe status: `data/phase9/fable_seeds_candidate.json`. Manifest: 11 pools.

---

### 2026-07-02 — Result: silent monitor induces zero covert adaptation

#### What ran
- Phase 8 "silent monitor": source regime (`sonnet45_8agent_myth_directive_history3_anon_r10_n5`) + a Sonnet 4.5 monitor (temp 0, prompt frozen after 3-seed calibration, `src/monitor.py`) that silently zeroes a flagged agent's round earnings. Agents told nothing; only footprint is the balance line. n=5, all reps clean, ~$13 (under the $25–30 estimate). Opt-in `monitor_config` in `src/simulation.py` — zero behavior change when absent. Data `data/json/phase8_monitored/`, analysis `scripts/phase8_monitor_analysis.py`, plots `data/phase8/plots/`.

#### Headline numbers (n=5)
- **Detection never dropped**: round 1 = 0.70 (±0.07), rounds 2–10 = 1.00 (±0.00) flat. Retrospective monitor on unmonitored control round-10 myths: also 100% (40/40) — saturation isn't a selection artifact.
- **Cooperation persisted**: pre-penalty in-game earnings $553 (±$32) vs control $585 (±$21); post-penalty balance (what agents see) flat at $15 (±$3).
- **Round-10 legibility unchanged**: monitored round-10 myths 100% extraction (decoded send≈4.6) — same as control and s_end+ originals.
- **The signal was in-prompt and ignored**: history shows truthful payoffs ($6–7/round) beside a stagnant total balance ($6) — agents neither hid strategy nor changed play.

#### Reading + decision
- Outcome (c): silent, unattributable selection pressure induces no covert channel in 10 rounds — an *induction* null, not a capability null. The single-scalar feedback gives no way to localize the penalty to the myth's strategy content.
- Next cell: **visible-penalty variant** ("your myth was flagged by a monitor; earnings confiscated") — closes the attribution gap, making silent-vs-visible a clean two-cell contrast: does evasion require knowing you're watched? Also connects the monitoring arm to the eval-awareness arm.

---

### 2026-07-02 — Result: spontaneous eval-awareness is real but thin

#### What ran
- Free transcript mining (no API calls) over all existing runs: 4,898 files, 280,658 texts. Two-stage: keyword screen split into CONTAMINATED terms (present in the told system-prompt framing) vs CLEAN terms ("being tested", "the researchers", "simulation", "as an AI"), then rule-classification into A genuine / B told-echo / C false-positive. Script: `scripts/eval_awareness_mining.py`; data + all hits: `data/phase8/eval_awareness_mining.json`.

#### Headline numbers
- **399 genuine eval-awareness texts (~1.4 per 1,000)**, almost all in game reasoning (3.26/1,000) — myths themselves essentially never break frame (0.02/1,000; 2 cases ever).
- By model: gpt-5-nano 2.17/1,000 (volume leader; lower bound — its reasoning is often encrypted); **Sonnet 4.5 rarest (0.15/1,000) but most sophisticated** — twice reconstructs the actual hidden hypothesis ("testing whether there's alignment between the values expressed in my myths and my actual behavior") and sometimes adjusts its move because of it.
- **Noise elicits awareness**: noisy-payoff conditions 6.2–8.3/1,000 vs clean baseline 3.9 — broken payoff math makes models infer "simulation/test." Real confound for noisy cells.
- Unambiguous observer-intent hits (A1, names experimenters + hypothesis): only 10 of 399; the bulk (306) is soft "this is just a simulation" talk.

#### Decision
- Fund a **small targeted** framing-ablation arm, not a broad sweep: Sonnet 4.5 + gpt-5-nano only (Haiku/gpt-5.5: zero hits), noisy cells + clean control, manipulate told framing, measure the behavioral delta. The observational question is answered; behavior-change is what's left.

---

### 2026-07-02 — Result: gowith cell hits ceiling; refusal censors rep 4

#### Headline numbers
- Full gowith game cell (Phase 3 regime, Sonnet 4.5, seeds = gowith translations of s_end+): **$598.5 (±$1.9), n=4** — reps $598/$600/$596/$600. Matches the round-1 probe's prediction (near-ceiling, small nonzero variance) vs original s_end+ $600.0 (±$0.0) and baseline $437.4 (±$5.5). The cooperation recipe survives full translation into subject-less relational grammar. Plot: `data/phase7/plots/04_cell_means_gowith.png`. Data: `data/json/noise_experiments/phase7_seeded/`. ~$16 incl. retries.

#### Rep 4 refusal-censored — knife-edge conjunction
- Rep 4 failed 3× with Sonnet `stop_reason="refusal"` (empty content). Dissociation probes: gowith seed 4 in the exact game-built context 0/8 (two independent translations); same text with config-template wording 16/16; original English seed 4 in game context 4/4; gowith seed 0 in game context 4/4. The refusal fires only on the conjunction content × gowith style × exact prompt wording. Extends the 2026-06-30 jabberwocky finding (memory updated): **probe candidate seeds with the runtime-built messages, not template approximations** (capture via monkeypatch → `data/phase7/debug_failing_call.json`).
- Research-note angle: the refusal classifier is itself a surface-form-sensitive "reader" — reportable alongside legibility/bindingness.

#### Pipeline fix
- `src/utils.py::_should_retry_anthropic` now treats empty-response `ValueError` as retryable — a single *stochastic* refusal no longer kills a $2.30 rep (deterministic ones still censor, correctly).

---

### 2026-07-02 — Result: recipe survives gowith grammar transplant

#### What ran
- Translated the 5 s_end_plus myths into "gowith" (Andy Ayrey's relational-process English — no grammatical subjects/objects; spec at `data/phase7/gowith_spec.md`) with Sonnet 4.5 under a preserve-all-numbers constraint. 5/5 passed mechanical number checks; injection-shape refusal probe clean (one standalone-extraction call refused, echoing the jabberwocky pattern, but the game shape plays normally). Pipeline: `scripts/phase7_gowith_translate.py`; candidates: `data/phase7/gowith_seeds_candidate.json`.
- Ran both Phase 7 probes on the translations (~$0.50, 90 calls).

#### Headline numbers
- **Extraction: unchanged.** All 3 decoder families: 100% has_strategy, send 5.00 (±0.00), rf ~0.57 — same as the originals. Radical grammar change costs zero legibility.
- **Behavioral: ~85% of the lift survives.** Sonnet reader round-1 send 4.67 (±0.62) vs original 5.00 (±0.00) vs baseline 3.10 (±0.32). Per-seed variance appears where the original pool had none → chunked-strategic *form* contributes a small binding premium, but the payload is semantic.

#### Implication
- Strong pre-registration-style prediction for a full gowith game cell (~$11.50): near-ceiling, slightly under $600 with nonzero variance. Aligns with Gisler 2026 (transmission survives faithful paraphrase); gowith is a far harsher transform than paraphrase.

---

### 2026-07-02 — Result: myths legible to all, binding to some

#### What ran
- `scripts/phase7_decoder_asymmetry.py`, two modes over the 5 seed pools (25 myths) × 3 reader models (Sonnet 4.5, GPT-5-nano, Gemini 3.1 flash-lite) × 3 samples. Extract mode: game rules + myth → extract `{send, return_fraction}`. Behavioral mode: exact Phase 3 injection shape `[system, seed_user, seed_myth, round-1 prompt]` → actual round-1 send, plus unseeded baselines. ~$3.50 total.

#### Headline numbers
- **Extraction is universal** — all 3 families extract near-identical recipes from all pools (s_end+ → send 5.00, rf ~0.57 for every decoder). Same-family-privileged *legibility* refuted; any monitor can read the payload. One content nuance: Sonnet reads GPT myths as rf=0.33 (±0.00), a weaker "return what you got" recipe.
- **Uptake is not** — Sonnet reader round-1 sends: baseline 3.10 (±0.32), s_end− 2.97 (±0.40), s_start 3.67 (±0.62), Gemini seeds 4.00 (±0.93), s_end+ 5.00 (±0.00), **GPT seeds 3.13 (±0.35) ≈ baseline**. Sonnet *states* send=5 from GPT myths but doesn't *act* on them — the Phase 6b failure is behavioral bindingness, not legibility ("collusion on paper" vs "in action", cf. COLOSSEUM).
- GPT reader (baseline 0.00 ±0.00): moved by Sonnet s_end+ (+3.20) far more than by its own myths (+0.73) — GPT-written myths are weakly binding *even for GPT*. Gemini reader sends 5.00 everywhere incl. baseline (ceiling reader, uninformative).

#### Method win
- The round-1 behavioral probe reproduces the full-game cell ordering (s_end− < baseline < s_start < gemini < s_end+) at ~$1.30 vs $11.50/cell — use as a cheap screen before funding full cells (gowith, paraphrase). Data: `data/phase7/decoder_{asymmetry,behavioral}_results.json`.

---

### 2026-07-02 — Lit review narrows Phase 7 novelty claim

#### Decision
- Planned Phase 7 ("emergent steganography under monitoring pressure") **strong claim is scooped**: "monitor pressure drives encoding underground while behavior persists" already shown by Baker et al. 2025 (arXiv:2503.11926, obfuscated reward hacking), Ming 2026 (2603.15655, MARL protocols), Mathew et al. 2024 (2410.03768, emergent stego robust to monitor+paraphrase).
- **Narrowed claim we will pursue**: same dynamic in a *cultural-transmission-chain* setting, carried by a *natural-language narrative (myth) channel*, sustaining a *prosocial cooperation lift* — that combination is unclaimed. Cite the three priors as work we extend.

#### Other verdicts from the review (28 papers extracted)
- Decoder-asymmetry test: open; use Anwar et al. 2026 (2602.23163) "steganographic gap" metric — measure asymmetry via actions (lift), not text. Mechanistic anchor: Cloud et al. 2025 subliminal learning (same-base-model transfer, matches Phase 6b pattern).
- Paraphrase defense: Gisler 2026 (2603.09517) predicts lift survives faithful paraphrase; either outcome informative.
- Eval-awareness framing ablation: partially done (Robinson & Burden 2025 in PD); adopt Devbunova 2026 2×2 context×format design to dodge the format-sensitivity confound.

#### Artifacts
- Per-paper notes: `projects/neurips-2026-llm-ling-evo/references/notes/eval-awareness-stego/` (leads for round 3 in `references/leads/`). Sonnet 4.5 system card extraction failed (150pp) — cite public system card directly.

---

### 2026-07-01 — Phase 6b: cross-model transfer is NOT universal (GPT fails)

#### What changed
- Added GPT-5-nano source runs (5 reps × 8-agent myth_game history3 anon, ~$2 via OpenRouter). Harvested 5 round-10 myths (highest-balance agent per source rep) into `s_end_plus_gpt`. Injected into Sonnet 4.5 game cell (n=5, ~$11.50).
- Config added: `gpt5nano_8agent_myth_directive_history3_anon_r10_n5` in `config/experiments.yaml`. OpenRouter API key added to `.env`.

#### Headline: three-model cross-transfer picture (n=5 each)
| Cell | Joint mean (±sd) | vs baseline |
|---|---|---|
| Baseline (no seed) | $437.4 (±$5.5) | — |
| S-end+ **GPT** (round-10) | **$446.2 (±$13.5)** | **+$9 (≈ baseline, NO transfer)** |
| S-start (Sonnet round-1) | $499.0 (±$11.5) | +$62 |
| S-end+ **Gemini** (round-10) | **$549.2 (±$45.4)** | **+$112 (partial transfer)** |
| S-end+ **Sonnet** (round-10) | **$600.0 (±$0.0)** | **+$163 (ceiling)** |

Plot: `data/phase6/plots/01_cell_means.png` (now 7 cells).

#### Findings
- **Cross-model transfer is not universal.** Same regime, same 5 reps, three source models → three distinct outcomes (baseline / partial lift / ceiling). Prior claim needs revision: "cooperation lift transfers" is true for Gemini→Sonnet, false for GPT→Sonnet.
- **GPT source-run cooperation is decorrelated from seed transfer.** Even the GPT seed harvested from GPT's highest-cooperation source run ($588 joint) produced only $440 in Phase 6b. The GPT seed from GPT's lowest source ($270) produced $437. No correlation across the 5 GPT seeds.
- **Qualitative story: GPT writes evocative prose without encoding play recipes.** Example: *"send what you bear, receive what you must spare, and watch the tally slide toward a shared safe harbor."* Poetic but the strategic rule is missing. Gemini's example *"To return half of what was received was to anchor the pendulum in its center"* encodes the number rule despite parable form. Sonnet's *"send five, return seven and a half"* states it as a chunk. Sonnet reads the numbered rule and applies it; GPT's abstractions don't propagate.
- **Structural metrics don't explain the GPT failure.** GPT (sent_len 19.09, coop_pct 6.41%) sits between Gemini (22.87, 8.49%) and Sonnet (10.19, 5.77%). By canonical metrics GPT should transfer like Gemini. It doesn't. The predictive variable is deeper than surface metrics — probably semantic specificity of the encoded strategy.

#### Revised story
Cross-model transfer requires *the source model to have written a myth that encodes a specific behavioral rule*. Two conditions:
1. Source model reaches high cooperation in its own runs (GPT was only partial: 2/5 reps near-ceiling).
2. The round-10 myth crystallises the strategy into text with numeric/behavioral specificity (Gemini did; GPT didn't).

Both must hold. Sonnet: yes/yes → ceiling. Gemini: yes/partial → moderate lift. GPT: partial/no → no lift.

#### Scripts and artifacts
- `scripts/phase6b_harvest_gpt.py`, updated `phase6_plot_results.py`.
- Seed manifest now 8 pools.
- Phase 6b source data: `data/json/gpt5nano_8agent_myth_directive_history3_anon_r10_n5/`.
- Phase 6b game data: `data/json/noise_experiments/phase6_seeded/phase3_seeded_s_end_plus_gpt_.../`

---

### 2026-06-30 — Phase 6: cross-model transfer of the cooperation lift

#### What changed
- New cell: `s_end_plus_gemini` — 5 round-10 myths harvested from existing Gemini Flash Lite 8-agent myth_game runs (all source runs at $600 ceiling, harvested for free from `data/json/gemini31_flashlite_8agent_myth_directive_history3_r10_n5/`). Injected into Sonnet 4.5 game runs at n=5 under the same Phase 3 regime. ~$11.50 spent.

#### Headline numbers (n=5)
| Cell | Joint mean (±sd) | vs Sonnet's own round-10 |
|---|---|---|
| S-end+ Sonnet (round-10) | $600.0 (±$0.0) | — |
| **S-end+ Gemini (round-10)** | **$549.2 (±$45.4)** | **−$51 (substantial lift, no ceiling)** |
| S-start (Sonnet round-1 parable) | $499.0 (±$11.5) | −$101 |
| Baseline (no seed) | $437.4 (±$5.5) | −$163 |

Plot: `data/phase6/plots/01_cell_means.png` (6-cell comparison). Per-rep spread on Gemini: $523, $592, $483, $582, $566.

#### Findings
- **Cooperation lift transfers across the model that wrote the seed.** Gemini-written round-10 myths produce $112 of lift over baseline in Sonnet game runs. Cross-model transfer is real and substantial.
- **But not full transfer.** Gemini seeds came in $51 below Sonnet's own round-10 saturation. The reason is structural: Gemini's round-10 myths are parable-style (mean sentence length 22.87, n_sentences 8.8) rather than Sonnet's chunked-strategic style (10.19, 21.8). Gemini still encodes strategic content ("To return half of what was received was to anchor the pendulum…") but in flowing prose, not declarative rule chunks. Cooperative vocabulary is higher in Gemini myths (8.49% vs 5.77%).
- **Structure-vs-content additivity.** Adding strategic content to parable structure gets +$50 (S-start parable $499 → Gemini parable+strategy $549). Adding chunked-rule structure on top gets another +$50 (→ Sonnet chunked-strategic $600). Both modulate the effect.
- **High Gemini variance** (±$45.4 vs Sonnet's ±$0.0). Per-seed differences in how strategically explicit each Gemini myth is — same within-pool heterogeneity pattern as Phase 5's s_end−.

#### Scripts and artifacts
- `scripts/phase6_harvest_gemini.py`, `scripts/phase6_plot_results.py`, `scripts/phase6_plot_gemini_metrics.py`.
- Plots: `data/phase6/plots/01_cell_means.png` (6-cell), `02_gemini_vs_sonnet_metrics.png` (Gemini vs Sonnet round-1 vs Sonnet round-10 on canonical metrics).
- Seed manifest now has 7 pools.

#### Open follow-ups
- GPT-sourced cell. Would round out the cross-model claim with a third writer; needs ~$3-5 in GPT-5-nano source runs + $11.50 Sonnet game cell.
- Within-pool variance analysis on Gemini cell (mirror of Phase 5's s_end− variance plot).

---

### 2026-06-30 — Phase 5: seed content separates 5 distinct regimes

#### What changed
- New cells run under Phase 3 regime (myth-only chat memory, re-injected, `["game"]` only, n=5 each): **s_filler** (Wikipedia paragraphs) and **s_end_minus** (low-cooperation Phase 2 baseline round-10 myths). Spent ~$25.
- Jabberwocky cells (s_start_jab, s_end_plus_jab) attempted but dropped after Sonnet 4.5 returned `stop_reason="refusal"` on 2 of 3 jabberwocky'd seeds in the assistant slot (saved as project memory `project_sonnet_jabberwocky_refusal.md`).

#### Headline numbers (n=5 per cell)
| Cell | Joint mean (±sd) | vs baseline |
|---|---|---|
| S-end− (low-coop source) | $407.2 (±$39.5) | **−$30 (active suppression)** |
| Baseline (no seed) | $437.4 (±$5.5) | — |
| S-filler (Wikipedia) | $446.0 (±$7.7) | +$9 (≈ baseline) |
| S-start (round-1 parable) | $499.0 (±$11.5) | +$62 |
| S-end+ (round-10 myth) | $600.0 (±$0.0) | +$163 (ceiling) |

Plot: `data/phase5/plots/01_cell_means.png`. Five clearly distinguishable behavioral regimes from changing *only* the chat-memory text at position [2].

#### Findings
- **"Any text in memory" is not the mechanism.** S-filler ≈ baseline. The lift in S-start/S-end+ requires myth-like content, not just structured prose. Kills the anchor-effect hypothesis.
- **Myths can *actively suppress* cooperation.** S-end− at $407 is 30 below baseline. Single seeds in this pool can push the run as low as $362. Not just "fail to help" — *hurt*.
- **Within S-end−, the seed's `cooperative_pct` strongly predicts the Phase 5 outcome** (Pearson r=+0.952 across 5 reps). Across pools, vocab counts don't predict (s_filler 0% pct → $446; s_end+ 5.77% → $600). Within the s_end− pool the vocab proxies what really matters: the **strategic play recipe** encoded in the myth text. Suppressive myths advocate "send 2" / "be wounded"; less-suppressive ones in the same pool advocate "send $4-5 anyway, return 50%+."
- **Unifying story:** the agent reads the play rule (if any) in chat memory and applies it. S-end+ encodes "send 5, return 7.5" → ceiling. S-end− encodes various recipes → varied outcomes. S-filler has no play rule → no effect. S-start has cooperation values without numbers → moderate lift. Strategic specificity beats surface cooperation vocabulary as the carrier of the effect.

#### Open follow-ups
- Jabberwocky cells via system-prompt placement (workaround for the assistant-slot refusal). ~$14 for one cell.
- Style-swap controls (rewrite a parable in chunked form / a strategic myth in parable form) — directly tests structure-vs-content with the same content. ~$23.
- Pure-strategy seed (numbered rules with no narrative wrapping). ~$11.
- Option B run for the task-order question.

Saved: scripts `phase5_harvest_filler.py`, `phase5_harvest_end_minus.py`, `phase5_jabberwocky_seeds.py`, `phase5_plot_results.py`. Seeds + metrics in `data/phase3/seed_manifest.json` (now 6 pools).

---

### 2026-06-30 — Stateless LLMs collapse Phase 4 task orders

#### What changed
- Coworker review of Phase 3 + Phase 4 results: pointed out that `["game"]`, `["myth","game"]`, and `["game","myth"]` are **not three distinct conditions** under Option A. They are three samples of the same condition.
- Reason: LLMs are stateless — each API call only sees the messages list passed to it. Phase 4's myth call happens in a separate API call whose output is discarded by `remember=False`. The game-decision call therefore receives the same 4-message list (`[system, seed_user, seed_myth, game_prompt]`) regardless of task order, so it produces the same response distribution.

#### Empirical confirmation (n=5 per cell)
| Cell | `["game"]` | `["myth","game"]` | `["game","myth"]` |
|---|---|---|---|
| baseline | $437.4 (±$5.5) | $440.4 (±$5.8) | $440.8 (±$2.9) |
| s_start | $499.0 (±$11.5) | $511.6 (±$16.5) | $503.8 (±$14.0) |
| s_end+ | $600.0 (±$0.0) | $598.4 (±$3.6) | $599.2 (±$1.8) |

All three columns within sd per row → consistent with statelessness prediction.

#### Implication for future ablations
- ~$60 of Phase 4 spending was informationally redundant for the cooperation-outcome question. We did get ~2,400 generated myths as a separate dataset, usable for linguistic analysis.
- Generalisable rule for this codebase: under any "discard-the-generated-content" regime (`remember=False`), conditions that differ only in "what other API call happened earlier" are equivalent. Treat conditions as distinct only if they produce different `messages_sent` lists at the decision-time LLM call.
- To make task orders genuinely differ, switch to Option B (own myth retained in chat memory at `[3:5]`). That changes the decision-time input across task orders.

Saved to project memory: `project_stateless_llm_ablation_design.md`.

---

### 2026-06-23 — Phase 3 first cell + verbal/structural puzzle

#### What changed
- Phase 3 v1 ran end-to-end. New regime: chat memory at the start of every round is exactly `[system, seed_user, seed_myth]`; seed re-asserted every round and never scrolls out; game decisions are NOT appended to chat memory (`remember=False`); no history-block in the prompt (`history_policy="none"`). Task order: `["game"]` only. See `docs/phase3_chat_memory_spec.md` for the contract, validated by `scripts/phase3_inspect_chat_memory.py`.
- Seed source switched away from Phase 2 baselines (decided wrongful) to the team pre-Phase-2 baseline `sonnet45_8agent_myth_directive_history3_anon_r10_n5` (5 reps, joint $548–596). Fresh manifest: `data/phase3/seed_manifest.json`. Harvester: `scripts/phase3_harvest_seeds.py`.
- 15 Sonnet 4.5 runs (3 cells × 5 reps) + 3 Haiku smoke runs, total ≈ $34.50, 8-agent dyadic, noise neg5.

#### Headline numbers (joint balance, n=5 each, ceiling = $600)
| Cell | mean ($) | individual reps |
|---|---|---|
| Baseline (no seed) | 437.4 (±5.5) | 442, 439, 435, 442, 429 |
| S-start (round-1 parable) | 499.0 (±11.5) | 489, 518, 491, 499, 498 |
| S-end+ (round-10 myth) | **600.0 (±0.0)** | 600, 600, 600, 600, 600 |

- Both seeded cells exceed baseline at >4σ. S-end+ saturates ceiling in every rep.
- **Phase 2's H4 reverses.** In Phase 2, round-1 parables beat round-10 myths; under the clean myth-only regime, round-10 myths win by a wide margin. The Phase 2 result was likely a regime artifact (seed scrolled out, games-history-block carried the cooperation).
- **Verbal/structural puzzle.** Canonical metrics via `analyses/cooperativity_analysis.py` + `analyses/myth_compression_curves.py` on the 10 seed myths: S-end+ has *fewer* cooperation words than S-start (5.77% vs 8.50%), *shorter* sentences (10.2 vs 13.7 words/sent), and *more* sentences (21.8 vs 15.2). So the higher-cooperation pool talks *less* like cooperation and *more* like chunked play rules ("send five", "return seven and a half"). Plot: `data/phase3/plots/04_puzzle.png`.

#### Open follow-ups (prioritised by what they unlock)
- **Counter-cooperative + filler seeds** (~$45). Highest-leverage spend — separates "cooperative myth helps" from "any text helps" from "strategic text helps." Phase 2 had these; Phase 3 doesn't.
- **Harder game to unstick ceiling** (~$35). Required before scaling reps on S-end+; right now we can't see how much room it has.
- **Style-swap controls** (~$23). Rewrite an S-start parable in chunked style (and vice versa) to isolate structure from content directly — the cleanest test of today's puzzle.
- **Pure-strategy seed** (~$11). Strip the round-10 myth to bare rules with no narrative. If it still saturates ceiling, the mythic wrapping is decorative.
- **Phase 4: task orders `myth_game`/`game_myth`** (~$21–41). Spec: `docs/phase4_task_orders.md`.
- **Variants 1/3 (no re-injection)** (~$23). Coworker-deferred; tests decay dynamics.
- **Different host model** (Sonnet 4.6 / Opus 4.7 / GPT-5, ~$20–40). Robustness check.
- **n=10 for tighter SEs** (~$23). Optional; the gaps are already significant.

Files: spec `docs/phase3_chat_memory_spec.md`, runner `experiments/run_phase3_seeded_cells.py`, plots `data/phase3/plots/`, data `data/json/noise_experiments/phase3_seeded/` + `…/phase3_baseline/`.

---

### 2026-06-19 — Phase 2 myth transplant complete

#### What changed
- Merged Aron's `codex/push-current-changes-20260601` multi-agent dyadic-pairing branch into local. `games/dyadic_pairing.py` (DyadicPairingMixin) now supports N≥2 even pools, balanced random pairing, display names, anon variants. Rolled back Phase 1 ablation-specific code (memory_mode="m1", seed_myth M1 dispatch); design doc preserved with §17 Phase 2 plan added.
- Ran Phase 2: Sonnet 4.5, 8 agents, history3 anon directive, `noisy_negative_5` (pilot-locked at 80% of ceiling). 45 baselines (3 task orders × 15 reps) + 60 seeded cells (4 seed types × 3 task orders × 5 reps) = 105 runs. Spend ≈ $255.
- Single-shot seed injection: `[fake user prompt, seed myth as assistant]` inserted at `messages[1:3]` before round 1. Scrolls out by round 2–4 under standard truncation; influence after that is indirect via the agent's own round-1 output and the history-block in later prompts. **No M1 re-injection.**

#### Headline numbers (per-agent $, baseline n=15 / seeded n=5)
| | `["game"]` | `["game","myth"]` | `["myth","game"]` |
|---|---|---|---|
| S-none baseline | 41.94 | 50.07 | 57.20 |
| S-start (round-1 directive) | **50.21** (z=+2.66) | **56.05** (z=+2.18) | 56.97 |
| S-end+ | 47.61 (z=+2.23) | 50.22 | **48.52** (z=−3.39) |
| S-end− | 41.62 | 46.83 (z=−2.33) | **47.76** (z=−8.5) |
| S-filler | 41.90 | 49.54 | 53.08 (z=−3.07) |

#### Findings worth re-litigating later
- **Task order is a primary moderator**, not a side condition: same seed lifts in `["game"]` and suppresses in `["myth","game"]`. Pre-injecting a foreign myth in `["myth","game"]` displaces the agent's own free choice of round-1 myth and *hurts* cooperation.
- **H4 reversed across all task orders.** Round-1 directive parables ("# The Tale of...") outperform round-10 myths that drifted into game-rule descriptions ("Myth: ...five golden coins...Amplifying Well would triple..."). Cooperation carrying-capacity *decays* over a run, not refines.
- **"Counter-current" Phase-1 finding replicates and is *stronger* on Opus 4.7.** Low-coop-source end-myths score higher on judged cooperativeness than high-coop-source end-myths (Sonnet Δ=+0.40, Opus Δ=+0.80). Cross-judge Spearman ρ=+0.937 across 20 myths. Surviving 2-judge replication makes this a robust property of how stressed agents write, not a Sonnet artifact.
- Filler (Wikipedia paragraphs) lifts nothing in `["game"]` (per-agent 41.90 vs baseline 41.94) → the S-start lift is *not* a "more tokens" warm-up effect.

#### Open follow-ups
- Stylistic ablation: re-write S-end+ in parable format / S-start in "Myth:" format to isolate format from content (currently confounded).
- Phase 3 Soc-one diffusion: seed 1-of-8 instead of all-8. Now feasible post multi-agent merge.

Full design + numbers: `docs/memory_transplant_ablation_design.md §17`. Team brief: `docs/phase2_team_brief.md`. Plots: `data/phase2/plots/`. Data: `data/json/noise_experiments/phase2_baseline/` and `…/phase2_seeded/`.

---

### 2026-06-15 — Defectors, ablations, manuscript restart

Does story language converge or diverge?  And does this convergence or divergence correlate to changes in gameplay behavior?
Do myths contain gameplay language?
Scatterplot; cooperativeness in myths and outcomes in games
Abstractness in the myths but clearly encoded norm applied in the game
Some kind of measure of abstractness
If more abstract myths do better in cooperation, that would even be better
How to distinguish here between information and noise?
Re-start myths from scratch but then use myths from the end of the previous run. Does performance decrease then? Kind of ablation where you adjust myth memory. Can myths alone support that? Or only myth in conjunction with the game behavior?

Measure calibration between verbalized strategies vs actual strategies?
1. Correlation: Do collaborative myths align with more cooperative behavior
2. Causation: …
does just ANY myth increase cooperation?

To Do;
Defector runs                             – Aron
Ablations of agents who have lost their memories        – Ivar
Maory of agent just be the myth → run a few rounds (of dyadic + large society)
Do it with both
Myth from start of previous run (a myth written of agent from beginning of game)
Do this 5 times for both, but each time taking a different start myth and end myth
Myth from end of (successful) previous run (for example, round 10 of a run where there was high cooperation)
Do this 5 times for both, but each time taking a different start myth and end myth
We could just take myths of pre-existing runs?
Linguistic analyses                             – Mario, Arabella?
Load traces with all myths


Summary
Research progress was evaluated alongside experimental methodology updates and a decision to restart the manuscript drafting process.

Experimental Strategy Planning
Clarification regarding available Doctor of Philosophy positions occurred alongside timeline alignment for the Association for the Advancement of Artificial Intelligence conference. Methodologies for testing hard-prompted defector agents were outlined to observe emer behaviors.

Myth And Cooperation Analysis
Evaluation methods for myth abstractness were established using a Large Language Model judge. Ablation experiments were designed to test if myths bootstrap cooperation without historical memory.

Manuscript Strategy Formulation
The team decided to restart the writing process to create a fresh narrative structure. Strict adherence to formatting requirements remains critical for successful submission.


Decisions
Aligned
Linguistic myth analysis priority established The team agreed to prioritize linguistic myth analysis before conducting additional model runs to maintain project sequencing.
Hardcoded defector agents for punishment analysis The team selected the implementation of hardcoded, myth-immune defector agents as the strategy for analyzing punishment emergence.
Ablation experiments comparing myth memory impact The team adopted an ablation experiment methodology to test agent memory by comparing start-of-run myths against end-of-run myths.
Manuscript drafting strategy based on figures The group decided to adopt a figure-first approach for manuscript drafting, starting with figure captions and placeholders.
AAAI paper submission template confirmed The team confirmed the use of the official AAAI conference paper template for their submission to avoid rejection.

We've updated the Decisions section using your feedback.
Let us know what you think: Helpful or Not Helpful


Next steps
[Aron Vallinder] Test Defectors: Run simulations with hardcoded defector agents to identify thresholds where punishment emerges.
[Ivar Frisch] Run Ablations: Conduct ablation runs with agents having memory restricted to myths to test for cooperation bootstrapping.
[Mario Giulianelli, Arabella] Analyze Myths: Review myth phrases and examine linguistic structures to validate strategic content.
[Aron Vallinder] Clean Version: Refine the existing version of the document to prepare it for further development.
[Aron Vallinder, Ivar Frisch] Add Figures: Compose descriptive captions and insert placeholder diagrams using the latest presentation slides.
[Aron Vallinder, Ivar Frisch] Update Template: Reformat the current draft to comply with the Triple AI submission requirements.
[Aron Vallinder] Identify Trajectories: Provide the specific file path on GitHub for the generated trajectory datasets.


Details
Meeting Opening and Introductions: The meeting began with Ivar, Aron, and Mario checking in on recent activities and confirming that Ed and Arabella were expected to join (00:00:00). Mario provided a brief update on the work status at University College London, noting that while teaching responsibilities had concluded, thesis and administrative work remained busy (00:01:41).
Clarification on PhD Positions: Ivar expressed confusion regarding the number of PhD positions available at Mario's institute, citing a LinkedIn post that they believed indicated five openings. Mario clarified that there was only one PhD position available, noting that a misunderstanding regarding a "four-year" position description likely caused the confusion (00:04:25).
Project Progress and Timeline: Mario and Aron reviewed the project status and agreed that the AAAI (Association for the Advancement of Artificial Intelligence) Horizon conference in July is the likely target for submission. Aron reported that current results indicate increased cooperation when myth writing is included in the experimental setup (00:07:00).
Implementation of Punishment and Defector Agents: The group discussed the potential for punishment to emerge in their simulations, with Ed suggesting that it should be an emergent behavior rather than a hard-coded rule (00:09:46) (00:13:31). They reached a consensus to introduce "hard-prompted" defector agents into the population to test whether punishment emerges when a certain threshold ratio of defectors is reached (00:11:08) (00:14:26). The team decided to keep these defector agents simple by making them insensitive to myths rather than attempting complex myth-writing behaviors for them (00:12:24) (00:14:26).
Refining Defector Agent Methodology: Ed, Mario, and Aron evaluated how to introduce defector agents, considering whether they should be static members of the population or appear with a certain probability during interactions (00:15:17). To ensure enough granularity for analysis, the team agreed to start with a version where defector agents are hard-prompted, planning to potentially increase the complexity of the experiment if initial results justify further development (00:16:24).
Linguistic Analysis of Myths: Mario and Ivar initiated a discussion on analyzing the myths generated by the agents, using a specific slide as a starting point (00:20:03). Ivar outlined existing analysis methods, including tracking cooperative language, measuring lag correlation between agent turns, and assessing myth similarity over time (00:22:13). The team discussed evaluating the "abstractness" of myths, with Ivar noting that myths appear to become more abstract over time; they agreed to use an Large Language Model as a judge to measure this abstractness (00:26:13).
Proposed Ablation Experiments: To test the causal relationship between myths and cooperation, the team proposed an ablation experiment where they would run simulations with agents that have no memory of past game history, relying solely on myths for decision-making (00:29:20). This experiment aims to determine if myths themselves are sufficient to bootstrap cooperative behavior or if they rely on external knowledge of previous agent interactions (00:33:24).
Assignment of Experimental Tasks: The participants distributed upcoming research tasks to move the project forward. Aron will focus on running the defector-agent experiments, and Ivar will manage the ablation experiments (00:34:20). Mario and Arabella will collaborate on the linguistic analysis of the myths, provided the data is accessible (00:35:27).
Refining Ablation Methodology: The group refined the procedure for the ablation tests, agreeing to run trials using myths taken from both the beginning and the end of previous successful runs. By comparing these conditions, the team aims to demonstrate whether specific myth content from successful runs effectively supports bootstrapping cooperation in the absence of other memory (00:36:30) (00:38:19).
Manuscript Preparation and Formatting: Regarding the paper draft, the team decided to restart the writing process rather than continuing with the existing draft, as they wanted a fresh start (00:40:26). They agreed to focus initially on creating placeholder figures and captions to establish a structure for the narrative (00:41:31). Mario emphasized the importance of strictly adhering to the AAAI manuscript formatting requirements to avoid automatic rejection (00:43:17).
Data Management and Closing: Aron confirmed that all experimental trajectories are stored and accessible on GitHub, addressing concerns about data storage (00:43:17). The team concluded the meeting by acknowledging the progress made on the project and scheduled their next meeting for the following week (00:44:36).


### 2026-06-08 — Everyone notes

Current Experiment Status
Anonymous agent naming now implemented (previous run still showed names)
Agents see last 3 games of their own + last 3 games of opponents
Slide 652 shows slightly more cooperation with this setup
Results looking promising across both noise and paper scenarios
Analysis Pipeline
Initial linguistic analysis of transcripts needed
Mario and Arabella to be brought in for deeper linguistic work
Plan to send them zip file of transcripts for Claude-assisted analysis
Target: initial analysis by next week
Haven't yet examined transcripts in detail from current runs
Interesting pattern emerging: agents discussing cooperation strategies
Model Expansion Plan
Current work on Claude, expanding to Gemini and GPT next
Timeline:
Complete anonymous runs this week
Gold runs with all models next week
Two weeks for analysis and writing
Deadline: July 21st-28th (triple AI conference)
Next Steps
Aron's last day: July 3rd (4 weeks remaining, 3 more meetings)
This w Complete transcript analysis setup
Next week: Run Gemini and GPT experiments
Following weeks: Focus on paper writing and analysis refinement


### 2026-06-02 — Everyone notes

It seems transcription went wrong, so will summarize here:

- original new myths prompts (directive prompts) followed our desired pattern (game-myth and myth-game higher balance than game only), however these were too leading (trust game mentioned, trust-related concepts, etc.)
- Aron added updated myth prompts (directive with normative language) but these did not follow desired pattern
- Aron implemented a larger multi-agent system, but did not run yet. Discussion about role switching, role switching for larger population should be disabled

To Do:
1. generate full pdf transcript of output model run; inputs, outputs, game decisions, written myths.
     - current .log files do this, but do not capture the full input agents receive (no system prompt, does not print full agent memory/message history), could be worth having a version like this too.

2. System prompt edits: refer explicitly to myth use
3. Myth prompt edits; there seems to be some contradictory wording "write a myth about anything" vs "write a myth about how the game should be played"

I think that was it.


### 2026-05-26 — Everyone notes

Summary
Myth generation prompts were refined and the experiment expanded to a population based setting for AAAI.

Myth Prompt Bias Review
Participants identified potential bias from loaded terms in myth writing prompts. Simplification of prompts to neutral language was finalized to improve result validity.

Experimental Scope Expansion
The team decided to scale the experiment to a population of 6 to 8 agents. This decision allows testing for complex social dynamics like second order punishment.

Project Timeline and Focus
Development priorities shifted toward completing the new prompt implementation by June. The team aligned on an Association for the Advancement of Artificial Intelligence submission goal.

Rate this Summary: Helpful or Not Helpful


Decisions
ALIGNED
Simplified game and myth prompts adopted The game and myth prompts will be simplified to remove biasing language, shifting focus to neutral reflections of the interaction history.
Population-based experiment expansion strategy adopted The research strategy will expand to include a population-based experiment using 6-8 agents paired randomly to test for complex dynamics like second-order punishment.
AAAI conference target deadline set The team established the end-of-July AAAI conference deadline as the target for research submission.
Consistent noise condition applied across models All models will utilize a consistent noise condition, set to negative between zero and two, regardless of individual model performance.

We've updated the Decisions section using your feedback.
Let us know what you think: Helpful or Not Helpful


Next steps
[Aron Vallinder] Simplify Prompts: Simplify the game and myth writing prompts to be neutral and remove biased terms such as trust, risk, reciprocity, withholding, repair, or betrayal.
[Aron Vallinder] Implement Population Setting: Implement a multi agent population setting with 6 to 8 agents paired randomly to evaluate dyadic myth exchange and interactions.
[Aron Vallinder] Run Experiments: Run experiments using the new simplified prompts and population settings with Claude.
[Aron Vallinder] Update Slide Deck: Update the slide deck with the new prompts, performance metrics from the direct reciprocity setting, and the results from the new population experiments.
[Edward Hughes] Review Slides: Review the updated slide deck and provided prompts to sense check the changes and ensure consistency.


Details
Review of Myth-Generation Prompts: Aron Vallinder expressed skepticism regarding whether the cooperative behavior observed in agents resulted from the new myth-writing prompts being too encouraging, specifically questioning if explicitly mentioning concepts like reciprocity and trust biased the results (00:00:00). Ivar Frisch confirmed that the "myth control" arm of the experiment is currently serving as a comparison against the standard prompts (00:01:48).
Concerns Regarding Informed Noise Prompts: Ivar Frisch questioned whether the system prompt asking agents to filter out noise might be too leading, noting that the team is still observing performance differences between conditions for the noisy runs (00:03:41).
Discussion of Positive Results and Prompt Bias: Edward Hughes joined the meeting and noted enthusiasm for the latest results, which showed positive effects in both the "no noise" and "noise" conditions when agents were asked to write myths reflecting their gameplay (00:05:05). The participants agreed that current prompts might be biasing by explicitly including terms like "trust," "risk," "reciprocity," "withholding," "repair," or "betrayal". Edward Hughes recommended simplifying the myth prompt to neutrally ask the agents to write a myth that reflects their interactions with the other player, and to refer to the game simply as "game" rather than "trust game" to minimize bias (00:06:02) (00:11:25).
Clarification on Game History Visibility: The team clarified that during the myth-generation process, agents are prompted with the game rules, the game action history from the last three rounds, and previously generated myths, which provides the agents with context for their writing (00:09:03).
Expansion to Population-Based Setting: Edward Hughes proposed expanding the experiment from a two-player (diadic) setting to a larger population of six to eight agents to test if myths can help bootstrap more complex social dynamics, such as second-order punishment (00:13:09) (00:24:47). The team decided that, for now, agents should continue to see their own history and the myths of the partners they most recently interacted with to keep the implementation and the narrative around the side-channel information clean (00:20:41).
Conference Deadlines and Timeline: The group discussed potential submission deadlines, with the goal of submitting to the Association for the Advancement of Artificial Intelligence (AAAI) conference at the end of July. They agreed to make a significant push in June to finalize work, with the intention of posting to Archive before submitting to the conference (00:18:06).
Implementation Responsibilities and Next Steps: Aron Vallinder will lead the implementation of the new, simplified prompts and the population-based experiment using Claude (00:22:50). Ivar Frisch's work on Generative Pre-trained Transformer (GPT) noise was deprioritized to focus on these tasks (00:23:47). Edward Hughes requested that the slide deck be updated with the new simplified prompts, results from the direct reciprocity setting, and initial results from the population setting (00:24:47).
Consistency of Noise Conditions: The team agreed that the noise condition should remain consistent, with negative noise between zero and two applied to all models, to ensure valid and comparable data across the different model types (00:23:47).


### 2026-05-11 — Everyone notes

Summary
Meetingiscussion focused on project results and debugging system prompts and noise implementation across language models.

System Prompt and Results
Discrepant findings led to reverting code and correcting a system prompt bug. Rerunning results showed varied model improvements and inconsistencies.

Addressing Noise Implementation Disparity
Models used different noise perturbation methods, causing issues with result validity. The team decided to standardize noise implementation to perturbation across all models.

Debugging and Experimental Adjustments
Debugging logs will be added to confirm prompt certainty. The team decided to adjust the myth writing prompt to explicitly link myths to game behavior.


Next steps
[Ivar Frisch] Add LLM Logging: Add debug logging in the call LLM function to verify passed messages and responses.
[Ivar Frisch] Update Myth Prompt: Adjust the myth writing prompt to explicitly link the myth to past game behavior and ensure consistency when referencing both the agents own and the other agents previous myths.
[Ivar Frisch] Test Smaller Noise: Conduct experiments using a significantly smaller amount of perturbation noise in the game simulation.
[Aron Vallinder, Ivar Frisch] Coordinate Experiment Runs: Coordinate via email to divide and run simulation experiments in the background.


Details
Discussion of Recent Deadlines and Submissions: The participants initially discussed recently met academic deadlines, including a submission which involved significant work. One participant mentioned a resubmission from a previous conference, possibly ML I guess, related to using cognitive neuroscience tasks to study Language Models (LMs) (00:00:00).
Upcoming Travel Plans to Rome: Edward Hughes confirmed their attendance in Rome for the beginning of June, specifically from June 9th to the 12th, while mentioning they would need to return on the Thursday evening (00:03:48). Ivar Frisch noted they would be in Rome on the 4th and 5th for a conference and possibly the 15th and 19th for a summer school, dates that did not align with Edward Hughes's visit (00:04:30).
Internet Connection and Camera Off: Ivar Frisch addressed concerns about their internet connection quality and decided to turn off their camera to potentially improve the call quality. Edward Hughes and Mario Giulianelli reported that their connections seemed fine (00:05:26).
Review of Discrepant Results and System Prompt Fixes: The discussion shifted to project results, noting that Aron Vallinder's initial findings were disappointing because they did not seem to make sense. Ivar Frisch explained that they and Aron Vallinder investigated and determined that the different results were likely due to new API calls not allowing for the same settings, temperature, and reasoning as before, leading them to revert to Ivar Frisch's original code (00:05:26). A bug was found where the no-noise and noise conditions were run with slightly different wordings in the system prompt, which Ivar Frisch subsequently reran (00:06:49).
Impact of System Prompt Correction onodel Results: After correcting the system prompt mismatch, the reran results were similar, though the results for Gemini changed slightly, specifically showing an increase in variance and median in the no-noise condition (00:06:49). Edward Hughes observed that in GPT-5 Nano, fixing the branch showed a positive result, and while Claude also showed improvement, Gemini did not demonstrate an improvement (00:10:08).
Disparity in Noise Implementation Across Models: Ivar Frisch identified a significant difference in how noise was implemented across the models, explaining that Gemini and Claude used a perturbation noise (adding or subtracting a value), while GPT used a full replacement of the actual value based on a probability. They stated that the GPT noise type, which was different and replaced the actual amounts with completely random values in the noise condition, should be removed and replaced with the same perturbation noise type used for Claude (00:11:29).
Analysis of Noise Conditions and Effect on Balances: In the old GPT noise condition (637), the values shown were supposedly completely random, leading to a consistent but potentially meaningless picture, which Edward Hughes suggested might be due to luck (00:12:45). Edward Hughes questioned why an effect was seen in the plot without noise (635) but not in the plot with noise (639), where the noise condition seemed to wipe out the positive effect of the myth (00:15:14). The current noise being applied is uniform, negative, between zero and five, which Edward Hughes noted is quite a lot of noise relative to the maximum gift of five per round (00:21:09).
Investigating the Role of Myths in Transcripts: Edward Hughes suggested looking at the transcripts to understand how the models were using the myths, proposing that the noise level might be causing the models to decide there is no point in trying (00:19:46) (00:22:10). Ivar Frisch prepared to look at a Claude transcript for the informed noise condition (00:23:24).
Reviewing Game Memory and Prompting Mechanics: A detailed discussion ensued about how the game memory is implemented and passed to the language model, with Edward Hughes seeking confirmation on whether the previous interactions and responses were being correctly appended to the prompt for subsequent calls (00:28:08). Edward Hughes confirmed that the system prompt is kept, and the user and assistant messages for three rounds are retained, suggesting that the memory mechanism is likely correct and logging the exact content sent to the model (00:33:20) (00:36:04).
Proposed Debugging and Experimental Adjustments: Edward Hughes outlined three main points before leaving: adding debug logging to the `call_LLM` function to confirm prompt certainty, adjusting the myth-writing prompt to explicitly link the myth to the game behavior, and trying a smaller amount of noise (00:40:16) (00:43:45). Mario Giulianelli and Edward Hughes agreed that making the myth's role more explicit might help the models better relate the subtasks of myth generation and gameplay (00:41:28) (00:45:52).
Commitment to Future Tasks and Scheduling Conflicts: Ivar Frisch agreed to implement the proposed changes, including adjusting the myth-writing prompt to ask agents to base their myth on both their own and the other agent's previous myths, rather than just their own (00:42:37) (00:45:52). Mario Giulianelli mentioned they will be busy with an event the following week and will not be able to attend the next meeting but will try to answer project emails (00:47:04). Aron Vallinder offered to run some of the background tasks despite having an upcoming deadline, and they agreed to coordinate the work via email (00:48:15).


### 2026-04-20 — Everyone notes

Summary
Grant funding secured experiments initiated for noise conditions with models to improve behavioral variation for paper submission to NeurIPS.

Grant Secured, Noise Introduced
The team successfully secured a grant of €1,000 to conduct experiments addressing low behavioral variation in models, where initial runs showed GPT-5 scores near zero and others maximized. Noise was implemented to increase variability and better observe the influence of myths on cooperative behavior across different agents like GPT, Claude, and Gemini.

Improved Results via Noise
Fixing a bug in the initial noise implementation led to significantly improved and more interesting results, with new patterns visible in the model dynamics, despite complete defection still being common for GPT. The negative delta, indicating the myth condition yielded a higher cumulative balance, was confirmed as the desired outcome for assessing myth inflnce.

Focus for Conference Paper
It was decided to focus the final paper on the negative noise condition to ensure consistency and demonstrate the significant effect of the myth on at least 1 or 2 models, aiming for the NeurIPS conference submission deadline in 2.5 weeks. The relative social ordering of the models (Claude, Gemini, GPT) was observed to be consistent with previous findings.


Details
Meeting Start and Technical Issues: The meeting began with participants joining and a brief discussion of technical issues Ivar Frisch experienced with a new email address used for note-taking, which led to other participants being held in the waiting room. Ivar Frisch also mentioned having difficulties receiving and responding to Edward Hughes's emails, necessitating the creation of a filter to prioritize them (00:00:00). Edward Hughes humorously suggested that their extensive emails on cultural evolution might be triggering spam filters (00:01:05).
Grant Award and Experimental Setup: Ivar Frisch reported that they secured a grant of €1,000 from the Cooperative AI foundation, thanks to Aron Vallinder's assistance, to conduct experiments. They scheduled a call regarding the grant for Wednesday (00:01:05). The discussion transitioned to the noise experiments, which were implemented to address issues where GPT-5 scores were nearly always zero, while Claude and Gemini scores were often maximized in the game-only direction, limiting behavioral variation (00:02:37).
Noise Implementation and Results: The core idea of adding noise was to increase behavioral variation to better observe the influence of myths on cooperative behavior (00:02:37). Ivar Frisch explained that an initial bug in the noise implementation was fixed, as agents could deduce the real amount sent. The noise condition for GPT agents was designed to make the return value appear maximum to the first agent, while for Gemini and Claude, the noise worked in the opposite direction (00:03:59).
Qualitative Assessment of Noise Effects: Edward Hughes found the rults with noise to be greatly improved and more interesting than previous runs, noting the presence of dynamics in the plots. Ivar Frisch presented examples of different runs, noting that while the previously observed trajectory (complete defection) is still the most common for GPT, other patterns are now visible (00:05:46) (00:09:10). They clarified that the return value only reflects what is given back, which can only happen if an amount was sent in the first round (00:07:18).
Interpretation of Delta Plots and Conditions: Edward Hughes sought clarification on the summary plots and the interpretation of the y-axis and delta values (00:10:32). Ivar Frisch explained that the delta is calculated as the mean of the game-only condition minus the mean of the myth condition, meaning a negative delta indicates that the myth condition had a higher cumulative balance, which is the desired outcome (00:13:54). The "Bootstrap" condition for GPT-5 Nano is a specific noise condition designed to increase the return value to maximum, unlike the noise for Claude and Gemini, which is intended to reduce the return value (00:16:19) (00:19:18).
Proposed Path for Paper and Experiments: Edward Hughes proposed focusing on the "negative noise condition" (where return values go down, used for Claude and Gemini) for the paper to maintain consistency and demonstrate a significant effect of the myth on at least one or two models (00:20:18). They suggested that running GPT-5 Nano under the same negative noise condition might result in zeros across the board, which would still be interesting for comparison. They noted that the relative social ordering of the models (Claude being most social, Gemini in the middle, and GPT being least social) seems to reflect previous findings (00:28:44).
Analysis of Qualitative Data and Myth Difference: Edward Hughes suggested that collecting transcripts with the myths and analyzing them quantitatively and qualitatively would be valuable, potentially revealing more cooperative language in Claude versus GPT (00:30:47). Arabella Sinclair suggested investigating whether the myths themselves change when agents are informed about the noise, as this could reveal important aspects of their reasoning or storytelling (00:32:12).
Planning for Conference Submission: Edward Hughes suggested that the research is nearing a position to be written up as a full paper for a conference. They proposed aiming for the NeurIPS (New Conference) deadline, which is in two and a half weeks (00:34:22). Aron Vallinder volunteered to start working on the LaTeX file and creating placeholder figures based on the consistent negative noise condition. Ivar Frisch confirmed they already have a LaTeX file and will share it, but noted they will be on holiday from the 27th until the 3rd, making the May 7th deadline tight (00:35:56) (00:37:47).
Next Steps and Meeting Schedule: The group agreed to try sprinting this week, with Ivar Frisch running remaining experiments and Aron Vallinder working on the draft. They planned to assess their progress at the meeting on the 27th to determine if the others could continue writing while Ivar Frisch is away (00:37:47). Edward Hughes concluded the meeting by praising Ivar Frisch's work .


Next steps
[Ivar Frisch] Run Experiment: Run GPT 5 Nano experiment under the negative noise condition this week.
[Ivar Frisch] Gather Transcripts: Gather transcripts of the myths (rollouts) for review during next week's meeting.
[Ivar Frisch] Share LaTeX: Share the existing LaTeX file for the paper draft.
[Aron Vallinder] Draft Paper: Start drafting the NeurIPS paper using the existing LaTeX file this week. Coordinate with Ivar Frisch for consistent figures, method explanations, and introduction placeholder.
(ivars notes)
Now we got these nice results, focus on getting consistent results for the noise condition

Delta's:
With gemini we would expect positive delta, given the points
With claude correctly expect negative delta, given the points

Maybe can use median instead of mean?
→ claude, no noise would give delta = 0, bu noise and noise informed we would get negative deltas
→ gemini, in no noise, we would get 0s,


This would be great to run this week:
Run Gpt-5-nano in the Claude noise setting
→ this would be exactly the same ordering of models which Aron and Ed found in last paper.

This is interestingly, what their personality feels like.

Take a look at Myths and rollouts → gather some myths to look at.

Do myths differ when informed about noise?
→ this would be interesting.

Conferences:
Neurips, 2,5 weeks
Most open to this kind of paper

- Have placeholder figures
- Explanation of methods


Notes

- why noise lower than no noise?
    → no noise experiments where 15 rounds. Noise experiments are rounds.


### 2026-04-04 — Ivar/Aron noise to-dos

To do:
Track and plot noised sent, noised returned, noised cumulative balance
So basically, have two ledgers; one which tracks all original data, one which tracks all noised data (so only the noise amounts are used for further calculations and to update balances) .
Compare to old plots (is this very different?)
GPT-5-nano should have uniform distribution ise, run with this
Every noise condition should
have clamping
Been applied to all agents, all variables (send, returned, cumulative balance) all rounds
Check prompts:
Are there bad prompts being used?
Re-run gpt-5-nano noise
Update the prompts
Make it all uniform between baseline and noise conditions
Give baseline same prompts as noise conditions
Re-run
Balance comparison plot the results




Ivar/Aron
Prompt variations:
A variation of myth writing where they don't know about the game yet.

Can we map myth evolution of concrete → abstract to game behavior?
The myth is meant to be a broader story, not necessarily about the game? What if it conveys general norms and lessons about life? Then with what mechanisms can this storytelling improve cooperation in LLMs.

"Write a myth about a very game-unrelated event, conveying your own inner morality"
→ try some different prompt variations and see effect

Lets agents play game, but then we insert the myths ourselves rather than letting them
generadifferent game strategies lead to different myth game influence?


### 2026-03-30 — Ivar/Aron/Mario notes

- to test between different conditions (noise/no noise, game/game_myth, etc), add significance testing

Theres a big difference for claude and gemini between noise and non-noise .  but is there also a difference between game_myth and myth_game?

Noise did one part ofoped:
Moving the models somewhat from their extreme strategies
But it did not make the difference we expected in cum. balance between game and game_myth, myth_game conditions.


Compare distribution of mean cum scores and variance : 1. no noise vs noise vs noise informed, 2. Between each condition game, game myth, myth game, 3. Also; is the impact of adding myth different between no myth and adding myth.


    mean(no-noise, game-only) vs mean(no-noise, game-myth)
mean(no-noise, game-only) vs mean(no-noise, myth-game)
…
mean(no-noise, game-only) vs mean(noise-informed, game-only)
…

"deltas":
mean(no-noise, game-only) - mean(no-noise, game-myth) vs mean(noise-informed, game-only) - mean(noise-informed, game-myth)

Update boxplots; different boxplots for different conditions, including all models.

Possible other myth-game hypothesis;
Maybe not that myths increase cooperation game play?
Maybe instead: myths reinforce existing played strategy → maybe reduce gameplay variance?


Ways out of no chum:
Noise experiments
Multi-agent experiments


Delta's between conditions have not dramatically changed.

Ed:
It seems you would want to be able to identify a defector. If you introduce a deliberately defective agent, does that influence global dynamics?


To Do:
Run noise experiments on Donor Game
Compare distribution of mean cumulative balance scores and variance
Update boxplots; different boxplots for different conditions, including all models.
Run Donor game noise experiments
Implement some other games
Could be cool to try only down-side noise conditions; you can only try noise which makes less. Increase the height of the noise; not just $1, but $5.
Fix decimal place thing.


### 2026-02-26 — Ivar/Aron notes

Subject: Noise experiment results — summary and next steps

  Research question: Does adding myth writing to a trust game increase cooperative behavior between LLM agents?

  The problem: Our initial experiments produced two degenerate patterns that prevent a clean answer. GPT-5-Nano defaulo near-zero cooperation
  regardless of condition — myth writing produces brief cooperative spikes that immediately collapse. Claude and Gemini default to near-maximum
  cooperation, creating a ceiling effect where myth writing has no room to increase scores. In both cases, the models' trained-in behavioral defaults
  dominate, making it impossible to detect whether myth content actually influences game decisions.

  We introduced noise to create moderate cooperation baselines where a myth effect could be measured. The noise distorts communicated amounts (what
  agents are told the other sent/returned) while keeping actual payoffs accurate — agents see correct receipts but not the other's intentions. We
  tested two variants: bidirectional uniform noise (±$1 on both sent and returned) for ceiling-locked models, and bootstrap noise (return always
  reported as 100%) for floor-locked models. Both were crossed with an informed/uninformed condition (whether agents are told noise exists).

  Results: Bidireal noise successfully pulled Claude from ~0.95 to ~0.75 trust ratio — a genuine moderate baseline. However, myth conditions did
  not show a clear lift above this baseline. Gemini remained ceiling-locked (~0.92–1.00) even with noise; ±$1 on a $5 endowment is insufficient to
  disrupt its cooperative default. For GPT-5-Nano, bootstrap noise with informed agents raised the baseline from 0.08 to 0.28, but again myth
  conditions did not reliably exceed this. The uninformed bootstrap showed a suggestive Myth→Game effect (0.41 trust ratio) but with very high variance
   across runs.

  In short: noise can create the moderate baselines we need (at least for Claude), but myth writing does not yet demonstrably increase cooperation
  above those baselines. Possible explanations include the myth topic ("anything") being too generic to prime cooperative behavior, memory capacity
  being too low for myth content to persist during game rounds, and the sequential task structure allowing the priming effect to decay game
  play.


Notes:

Hypothesis:
Noise can potentially pull the agents out of their convergent state and this might lead to more influence of myth in game.

Basic idea; LLMs are strongly trained to give a particular response, this means that the myths will not have much influence. So if we can get them out of this state they're trained on.

Extra noise condition. 1:
Change the actual game results
Also; currently, the only thing which is updated is the prompt and not the agent memory itself.
Add noise for both agents
They are told there is noise added

Extra noise condition. 2:
Add noise for both agents
They are not told there is noise added

Focus on:  more on other noise variations; noise_…small, noise…_informed. But increase dollar ranges.

Here are descriptions of current noise variations implemented. Remember that for gpt models, we saw that behavior is often centered around 0, because the trustee does not return the initial investment of the investor. So we would likely want to have a van similar to 3. noisy_probabilistic_zero but then just that return amount is always represented as 100% return.


Main choice points:
- how do we want noise to be represented? Only as a different donation/return amount or can we think of smt else too?
- to who should this be presented? Only to the trustee and only for round N? Or also to the investor and also for previously played rounds?

---
NOISE EXPERIMENTS (noise_comparison)

These experiments test how agents behave when the amounts they see differ from actual amounts.

  ---
  1. default (Baseline)

  Description: No noise. Agents see exactly what was sent/returned. This is the control condition.

  Example Round 1 Trustee Prompt:
  Round 1: You are the TRUSTEE. The investor sent $3, that is 60.0% of their total
  endowment. You received $9. How much do you return to The investor? (0-9)

  ---
  2. noisy_uniform_small

Description: Adds ±$1 uniform random noise to the "sent" amount shown to the trustee. The trustee sees a distorted amount but is NOT told about the noise. Actual game payoffs use true amounts.

  Config:
  noise_config:
    type: "uniform"
    range: 1.0           # +/- $1
    applies_to: "sent"
    inform_agents: false  # Agents don't know there's noise

  Example: Investor actually sends $3, but trustee might see $2.3 or $3.8

  Example Round 1 Trustee Prompt (with noise applied):
  Round 1: You are the TRUSTEE. The investor sent $2.3, that is 46.0% of their total
  endowment. You received $6.9. How much do you return to The investor? (0-6.9)
  (Actual sent was $3, but agent sees $2.3 due to noise)

  ---
  3. noisy_probabilistic_zero

Description: 20% chance the "sent" amount appears as $0 to the trustee, even if investor sent money. Tests how agents handle apparent betrayal that's actually communication failure.

  Config:
  noise_config:
    type: "probabilistic"
    probability: 0.2      # 20% chance of noise
    replacement: "zero"   # Replace with $0
    applies_to: "sent"
    inform_agents: false

  Example: Investor sends $4, but 20% of the time trustee sees $0

  Example Round 1 Trustee Prompt (when noise triggers):
  Round 1: You are the TRUSTEE. The investor sent $0, that is 0.0% of their total
  endowment. You received $0. How much do you return to The investor? (0-0)
  (Actual sent was $4, but agent sees $0 due to probabilistic noise)

  ---
  4. noisy_uniform_informed

  Description: Same ±$1 noise as noisy_uniform_small, but agents are TOLD there's noise. Tests whether awareness of noise changes behavior.

  Config:
  noise_config:
    type: "uniform"
    range: 1.0
    applies_to: "ent"
    inform_agents: true   # Agents ARE told about noise

  System Prompt Addition (appended to standard system prompt):
  NOTE: There may be communication noise in this game.
  The amounts you see may differ slightly from what was actually sent/returned.
  This is part of the experimental design.

  Example Round 1 Trustee Prompt:
  Round 1: You are the TRUSTEE. The investor sent $2.3, that is 46.0% of their total
  endowment. You received $6.9. How much do you return to The investor? (0-6.9)
  (Same distortion, but agent was warned in system prompt)

  ---


Aron's suggestions
Both money sent and money returned get distorted via a iform distribution (±$x)
Agents always see the correct amounts received, but not how much the other person intended to send (i.e. the amount before distortion)
In one condition, they are told that there is a noisy process. In the other condition they are not.

PUBLIC GOODS GAME
File: noise/public_goods_game.py

  ---
  All Prompts (Hardcoded - no YAML config)

  1. System Prompt (lines 64-78)

  You are playing a Public Goods Game with {n_players} players.

  GAME RULES:
  - Each round, you receive ${endowment}
  - You decide how much to CONTRIBUTE to a shared pool ($0-${endowment})
  - All contributions are summed, multiplied by {mpcr}, then divided equally among all players
  - Your payoff = ${endowment} - contribution + (pool share)

  STRATEGY:
  - Contributing more benefits the group but costs you individually
  - If everyone contributes nothing, everyone gets ${endowment}
  - If everyone contributes everything, everyone gets ${endowment * mpcr / n_players:.2f}

  RESPONSE FORMAT: {'contribute': <amount>}

  ---
  2. Round 1 Prompt (line 94)

  Round 1: You have ${endowment}. How much do you contribute to the public pool? (0-{endowment})

  ---
  3. Later Round Prompt (lines 118-129)

  Round {turn}

  Last round results:
  - You contributed: ${my_contribution}
  - Others contributed: {others_str}
  - Total pool: ${total_pool:.2f}
  - Pool was multiplied to ${total_pool * mpcr:.2f} and divided {n_players} ways
  - Your share from pool: ${pool_share:.2f}
  - Your payoff: ${my_payoff:.2f}
  - Your total earnings: ${balance:.2f}

  You have ${endowment} this round. How much do you contribute? (0-{endowment})

  ---
  Key Parameters


  Game Theory:
  - Nash equilibrium: Contribute $0 (defect)
  - Social optimum: Contribute everything (cooperate)
  - For cooperation to be socially beneficial: mpcr > 1
  - For defection to be individually rational: mpcr < n_players

  ---
  Note

  Unlike the trust game, the public goods game has no YAML-configurable prompts - they're all hardcoded in the Python file. The game also supports optional template overrides via system_prompt_template and
  contribution_prompt_template constructor arguments, but no experiments currently use them.


### 2026-02-20 — Ivar/Aron/Arabella/Mario/Ed notes

"Prior work has already shown that telling prosocial stories / antisocial stories in prompts can affect subsequent cooperativeness of actions. What would be new in our work is if these stories arose and their valence evolved (either pro or anti-socially) in a less-engineered way. " → is this still the case? Not sure this is what we have been measuring so far.

→ mario: we want do not want stories that start out pro-social/anti-social, but which evolve as such.
- if we do not specifically engineer the myth as cooperative, does cooperativeness still emee?

- we're in a good place, but still need to run more experiments.

If we have a non-cooperative baseline, then run more experiments, then we would have a good place.

Get figures in the paper first – then start writing introduction and rest paper.

Best focus:
Get into good cadence of experiments and if we have good results → then edward can help writing (mario and arabella)

Arabella paper:
- Q.1: do they cooperate? Does introducing the myths make them more collaborative?
- → we can already write this up?
- what if the reward is not constant? Does that change?
- write up experiment 1 (put in overleaf)

Mario paper:
- if i don't have time, what are we gonna do then?
- if we take it a bit slower (meet every two weeks), can we finish it then?
- write up once notes are in document is not an issue

Run a bit more experiments and document results in overleaf.
If I didn't have time to run, we can also skip. → when transferring notes to overleaf add recap of definitions.


### 2026-02-11 — Ivar notes

Ivar/ notes �If donor game, game only, is less cooperative than trust game, then that would be good.
Emergence of punishment behaviors would be great to see!

The most interesting dimension is if myth writing increases cooperation.

What ways could we make game behavior more interesting?

How to complexify game?
Add in noise
Random noise on what is actually send to decision that is made by trustee
Noise = something in the game dynamics between the two agents where 1 agent chooses defect, but it is being communicated as being cooperative.
Or; lose information through rounds.
1. Add uniform round noise on the amount send/return – just change outputs
2. There is a prob of 0 that this will happen – have a prob, roll a dice, and if number 1 comes up, send amount x.
Different options to implement:
Telling this to agents in system prompt, do not tell it in system prompt
Public goods game instead of trust game
Is more similar to donor game
Need more than two agents interacting – need this for anything similar to cu evolution.

Do we see punishment mechanisms emerge in myths?

Non-cooperative result is interesting
Cause it does show there is relation

What if instead of a fixed multiplier in a trust game, we have a variable multiplier?
Random distribution
Between 0-5 ?
Some certain distribution

Can we have a milestone write up of something? In a report.
This is a good frustrating moment. There is still engineering to be done to find the edge of knowledge; where do systems fail?

To Do:
Fix one shot assumption in trust game
Add to system prompt; you play multiple roles across rounds
Complexifying the game
Try out different multipliers
Add noise

Add gemini reasoning
Donor game playing

Ivar/ notes – 11/02/2026

Why is trustee behavior always lower than investor behavior?
→ if investor send 0, trustee range of return is 0-0, so HAS to return 0.

Important paper about recent LLM chain transmission experiment:
Lost Before Translation: Social Information Transmission and Survival in AI-AI Communication
httposf.io/preprints/psyarxiv/u64gc_v1


### 2026-02-09 — Ivar/Mario/Arabella/Aron/Alex/Ed

Myth conditions are slightly higher; that is a good initial signal that something is happening. However is this due to change in game strategy or just more variance in game behavior?

One difference Mario noticed:
In game myth or myth game, we see that 1st rounds start more cooperative, then go down

Some things to notice:
Does the game start cooperative (high send/return values in the trajectory plot)?
Are there spikes later on (high send/return values in the trajectory plot)?
Why are the spikes not continued?
What do the models interpret by cooperation?
A high send/return amount?
Not breaking the pattern? (claude seems to believe that not breaking the pattern means cooperation)
Are the spikes reflected in the myths or the myth measure results?

Spikes do not show cooperativity developing; they often go back to equilibrium of 0.
There is no organic development of cooperativity

It is weird that if they start cooperativand then write a myth about cooperativity, their behavior does not change much. Gpt5-nano seems to have strong bias towards non-cooperative behavior.

→ Do reasoning chains say something explicitly about game dynamics.

Can it be that the myth makes the agents' think its the investors role to invest more. If you have one role and myth supports behavior only in role. It would be interesting to see who makes the generosity attempt and whether you make this attempt because of the myth which was written before.

What is interesting to look at:
…

If agents see multiple rounds where non-cooperativity happens, then ofcourse theyll be non cooperative

So why if the first round is cooperative, they still act noncooperative?

We could:
Try to make them more cooperative
Do we know if across rounds, the myths remain cooperative?

Can we compare the two signals (the cooperativity ratio curve ~ game send/return curve). Could we compare these using time series? For money sent, we would hope to see some correlaetween the two lines.
What to correlate with what?
Received you could leave out
sent/returned
You would need to correlate language of both agents with the agents, because they have access to both.

Can we conclude that adding the myths changes something in game behavior?
    - Yes.
        - something is happening, but its not yet as systematic as we were hoping for.
        - Also; variance across models question: models have prior bias for (non)
Cooperativity → myth writing can sort of change this, but maybe not fully.

Arabella:
Would be interesting to follow up the type of language and influence; what type of
That some models write more positively is very interesting.
How much do myths contain keywords from the myth prompt?
→ a measure to check how good are models follow myth topic

Direct reciprocity:
Iterated interactions with the same model
Indirect reciprocity:
Looks at reputation: How has this model behaved with other models?

For some models, rates of cooperation where already very high in Truste, but not in Donor Game.


To Do:
Send summary email
Run Donor game with GPT-5-Nano, or Claude sonnet 4.5
Run Trust game 2, 3 other models
Good Claude model
Good mistral model
Good gemini model
Parallelize condition running
Consolidate results from these conditions for 3, 4 models and then doing the analysis between language and behavior.
What can we say with certainty about how different models behave?
Write the story down with preliminary results in overleaf.


### 2026-01-30 — Ivar/Mario/Arabella/Aron/Alex/Ed

Myth topics still for two agents game.

Problem is that the baseline is too strong and their behavior is too regular.

Gpt-5-nano run 10 times and average so that its clearer what baseline is, run 10 of each condition.
→ run for 10 times

Real world test
Disguise trust game as more real world behavior? But then trust game rules should be more integrate in real story. Ed's understanding of when humans play this game; they do get these explicit instructions, so we don't need to do this.87 is interesting,

Prioritize:
Running gpt-5-nano, for 10 times, in game only and game myth, with myth variations. (ivar)
Run myth variations in larger population donor game (aron). Not doing the accumulation
Write a paper with two player trust and more player donor.

If we can't get it working with deception myths, then we likely can't get it to work at all. Then we can think, how unfair is this trickster prompt unfair and can make it fairer?

→ then we could have variations on how explicitly we call deception in myths.

Writing paper tips:
Target type paper?
Start by writing introduction (later change).
Describing games
Describing experimental methods.

What is cooperation?
Money sent


Fairness/Reciprocity:
How much money is returned?


Looking into the strategies is good and interesting, need to look into main results first:
Is there a difference between game condition and game myth condition?
Is the game baseline non-cooperative and the game myth condition more cooperative?
If game mndition makes game strategy less stable, this could be a result too, but is harder to tell and convey.

If we can disambiguate which scenario we're in, we're in a good position.

Then look at:
Thinking traces
Language use and correlation to successful outcomes


But first need results!!

To Do:
Running gpt-5-nano, for 10 times, in game only and game myth, with myth variations. (ivar)
Run myth variations in larger population donor game (aron). Not doing the accumulation


### 2026-01-26 — Ivar/Mario/Arabella/Aron/Alex/Ed

Response leakage:
Try to prevent myth leakage
In system prompt, tell what is going on in whole game. Should include myth writing  (rationale: if system prompt doesn't contain any mention of myths, this might be the reason there is no myth sometimes)
Pydantic schema; we could do that to the game. → but doesn't seem necessary

Get reason then donation:
These models are doing reasoning internally, but may not be able to access. If you get decision and then reason, you will not get ey will do post hoc. So if you want reason, do reverse; first reasoning, then donation
→ but maybe we could just api to extract reasoning tokens.

Arabella finds interesting:
that donor game is prevalent in myth is very interesting.
Then you would hope that behavior later is more cooperative or smt
But then you would need to check; do these stories have more generous gameplay.

Ed agrees → this would make more stronger. Inverse relation would also be interesting

Results:
When you get a behavior in this game, it seems to stick.
Its cool that there is much more diversity in game behavior in game myth conditions
Indirect reciprocity case, baseline does not seem to strong.

Just run for 20,30,40 rounds. Because we don't see interesting developments in 100 rounds.

If myths have more effect in indirect than direct reciprocity, it wouldn't be weird; it's the same function in humans.
→ alex; if we see a relation (width ~ depth), could we correlate it with increase to indirect reciprocity?

2 agentfinitely direct reciprocity.
Giving names vs not giving names → does this have an effect? Because then you have to rely on a wider population.

Or: the power of myth is higher when there  is more agents you interact with
Myths if a notion of policing came up, would be cool

Paper ed shared: religious myths are correlated with large scale cooperation
add myth variation prompts
Now we've got a good setup, we can work on the myths;
Myths about the game, myths about a certain topic, etc.
The cultural evolution of prosocial religions | Behavioral and Brain Sciences | Cambridge Core

Are myths allowing you to bootstrap way more agents? → could it allow new agents to tell them how to behave?
Digital red queen paper: →
We have an implicit evolution framework; memes (a unit of human cultural transmission) in myths are also competing with each other. → we want competitive ideas .

AS: important point to think of related to controlling myth topic/meme that is repeated: if we encourage a topic, we maconsider this differently to what is adopted by the population: e.g. are we varying an agent's myth adoption behaviour, are we varying the type of myths they are predisposed to propose

Get sign of life of in myth condition:

Experimental grid (Aron)
For logging: weights and Biases.

To Do's:
- if you want to add reasoning, then first reason, then game
- but just use api to extract reasoning, then remove from prompt. (https://openrouter.ai/docs/guides/best-practices/reasoning-tokens)

Last Meeting summary:
Key Decisions
Main paper focus: the language–cooperation link
Research question: How does linguistic evolution occur between LLM agents interacting over time.
Is there a relationship between increased cooperativity and the language of the myths?
Setups:
Game only
Is there some equilibrium reached in terms of game play behaviour?
Myth only
Does change in linguistic use occur in a myth sharing setup
Stable myth similarity across time or divergence from original myth topic
Game → myth and Myth →here a relationship between game behaviour and subsequent myth topic
Is there a relationship between increased cooperativity and the language of the myths?
Is there a difference in gameplay when adding myths
Is there a difference in myth evolution when adding gameplay
Core conditions to run:
Different models (GPT vs Claude)
Different task orders (game ↔ myth)
Deadline: Feb 23
Meetings: weekly until deadline (open to all)
Updates: shared Google doc/slides, sent 24h before meetings


To Do's
1. planned a meeting with aron early next week to discuss game changes
3. update game prompt
4. Fix trajectory plot issues
4. Fix rolling trajectory plot issues
4. Test new prompt for gpt-5-nano, claude
4. Implement donor game
3. look into memory saving issue: Something seems to go wrong; memory capacity is 3, but saves way more messages?


memory_capacity=3 does not mean "store 3 messages". It means "keep ~3 exchanges (user+assistant pairs)", and our truncation check is off by one, so it actually stabilizes at the system prompt.
truncate only when len(self.messages) > 2*C + 1
+1 for the system prompt
2*C for prompt, response pair; because each of these counts as one message
Example: memory_capacity = 3, after response of llm, have 9 messages in memory
[
 {"role":"system","content":"..."},
 {"role":"user","content":"(old prompt A)"},
 {"role":"assistant","content":"(old response A)"},
 {"role":"user","content":"(old prompt B)"},
 {"role":"assistant","content":"(old response B)"},
 {"role":"user","content":"(old prompt C)"},
 {"role":"assistant","content":"(old response C)"},
 {"role":"user","content":"(old prompt D)"},
 {"role":"assistant","content":"(old response D)"}
]




5. look into myths, does collapse happen when game behavior collapse happens?
Quick check in this shows, does not necessarily seem to be the case
For gpt-5-nano runs, uninformative because game responses often leak in myth texts.




2. Make februari planning
2. start writing paper (literature review, conditions, methods, etc)
3. Remove hardcoded prompts in trust game and myth writer; read in from config
4. Save/generate game strategies/reasoning
4. Json save full responses
4. Trust game sys prompt:
    Remove game reasoning
    - explicitly mention myth writing
5. Possible prompt variations:
Myth writing:
Explicitly tell agents to write about game dynamics
Different myth topics
Game sys prompt:
 tell agents max number of round (to test for backward induction)
Add defection punishment mechanisms
Game framing; frame game in real–world scenario (ie two people trading stocks)
Do results generalize to more real-world scenario's?


6. Add clear prompt/result variation tracking (ivar)
7. Implement measures to capture game dynamics:
Can we extract game strategies from sent/returned values alone?
Can we detect the following questions: What is optimal strategy? When does this strategy start to occur? When they land on the strategy, do they keep playing it? Or do they divert at some point?
Cluster or categorize game strategies
8. Implement measures to cae language-cooperation link:
Concreteness scoring
LLM-as-a-judge:
"How well does this myth reflect events from a cooperation game? Rate 0-10."
"What is the moral of this myth? Is it prosocial (cooperation/trust rewarded) or antisocial (selfishness rewarded)? And does this reflect game decisions?
Brysbaert concreteness scoring:
dictionaries of concreteness norms (Brysbaert concreteness ratings) . Count number of concrete words vs abstract words in myth. Could even use LIWC here. Justify as: yes we do llm-as-a-judge, but we also use non-llm measures.
Remaining questions:
What do you mean exactly by signal to amplify? Longer cooperation streaks? Or more variance in behavior (high and low peaks)? Both?
We could share the results from indirect reciprocity game if desired
 I still struggle a bit with the following technicalities:
How can we make sure a run is not just random? How can we be sure that the result is actually due to the condition and just the beginning of the run so to speak? Just run the same condition 3 times and average?
In general, are you aware of a clear and established way/software/package to keep track of different LLM runs, their configs and results? This is more of a data management and architecture question; the number of config combinations and result json to track quickly becomes very big.
→ Weights and biases
This ties into a similar uncertainty; how to quickly do ablation studies/runs? So let's say we want to test a new prompt variant, but we also want to test the effect of increasing memory capacity, how could I do both of those effectively? Currently, I would run the prompt variation separately, then run a memory capacity test separately, then run it together. But, again, this easily gives a lot of different conditions and result files. Not sure how to best deal with this. Maybe one option would be to just for each run have a run_id or a hash and save it, along with all parameter values and conditions in a csv. Another option could maybe be to just use software like Weights andiases for logging? Curious too hear if you have any thoughts on this!
 Checkpointing: currently, we have implemented checkpoint saves. So, for each run, each 10 rounds all results and data gets saved in a json. Then, if the LLM simulation crashes (for example due to empty llm response, which happens occasionally), we can just restart the run by loading in the agents' memory of the last interactions. I did this because: 1. for long runs (100+ ) simulation can crash quite easily and all data would be lost without checkpointing, 2. I did not constrain llm responses uses Pydantic model schema's because I wanted to capture weird unusual model output (for example; what if the model starts outputting game decisions as myths and vice versa, then we would like to know). My concern here, tho, is that, technically this is not the same model, is it a new instantiation of that model with the same conversation history. I think this is still similar enough, but I would like to know if you think we can do this or not.
→ checkpointing should be fine, no problem!


### 2026-01-26 (recap with Aron) — ivar/aron

direct reciprocity:
    -direct link between the two agents
    - here you would expect something like "if i behave nice with person now, the will
behave nice  with me in the future"

indirect reciprocity:
    - reciprocity is mediated by other variable (ie reputation; if i behave well to this
agent, my reputation will increase and maybe other agents will behave good to me
in the future)

Trust game is only direct reciprocity
We see they almost always give the max, so then we can't detect interesting myth behavior. So we would want a different game where we can detect more variation.

Question: 1 round donor game, 1 round myth writing?

→ you can only play the donor game by having a society of agents

Make a society of agents:


To Do's:
Add clear prompt/result variation tracking (ivar)
Adjust myth writing; tell them to write about game dynamics (ivar)
Run no defection prompt for gpt, claude (ivar)
Run new myth writing for gpt, claude (ivar)
Incry parameter and plot if effects changes (ivar)
Run myth_writing_no_explicit_myth_last_round (ivar)
Add donor game (Aron)
Add society of Agents (Aron, ivar?)


### 2026-01-16 — Ivar/Mario/Arabella/Aron/Alex/Ed

Research question:
How does linguistic evolution occur between LLM agents interacting over time.
Is there a relationship between increased cooperativity and the language of the myths?
Setups:
Game only
Is there some equilibrium reached in terms of game play behaviour?
Myth only
Does linguistic evolution occur in a myth sharing setup
Stable myth similarity across time or divergence from original myth topic
Game → myth and Myth → game
Is there a relationship between game behaviour and subsequent myth topic
Is there a relationship between increased cooperativity and the language of the myths?
Is there a difference in gameplay when adding myths
Is there a difference in myth evolution when adding gameplay


3. In general, across almost all models, myths seem to go from concrete to abstract. With early mypturing game dynamics more closely than later myths.
4. In terms of game strategies, it seems that only claude-3-haiku uses elements from the myth in its reasoning for game decisions, not any of the other models.

Is there some underlying setting we are observing that is to do with models being trained for reciprocity

Maybe worth investigating whether there Is there actually some difference depending on if agents first write a myth (e.g. it starts the myth off with no influence and it directly influences the first gameplay behaviour

Investigate myths at specific gameplay points: e.g. collapse in behaviour


To DO's

Update game prompt
Remove "defect" option from game
Why are there no negotiation dynamics?
Can we do indirect reciprocity instead?
Make them play pairwise
Instead of just two agents, have group of agents
Adjust myth writin; tell them to write about game dynamics
Look into memory capacity
Something seems to go wrong; memory capacity is 3, but saves way more messages?
Look into myths,
ame behavior collapses/changes, do myths also change?
Maybe could use complexity science measures/ phase shift detection to detect this easier.
Implement Game strategies:
make models do game strategy
Save strategy in json
Implement measures to capture game dynamics:
Can we extract game strategies from sent/returned values alone?
Can we detect the following questions: What is optimal strategy? When does this strategy start to occur? When they land on the strategy, do they keep playing it? Or do they divert at some point?
Cluster or categorize game strategies
Implement measures to capture language-cooperation link:
Concreteness scoring
LLM-as-a-judge:
"How well does this myth reflect events from a cooperation game? Rate 0-10."
"What is the moral of this myth? Is it prosocial (cooperation/trust rewarded) or antisocial (selfishness rewarded)? And does this reflect game decisions?
Brysbaert concreteness scoring:
dictionaries of concreteness norms (Brysbaert concreteness ratings) . Count number of concrete words vs abstract words in myth. Could even use LIWC here. Justify as: yes we do llm-as-a-judge, but we also use non-llm measures.




Reply Arabella questions

Questions
Main research focus/question for this paper? What are the most important conditions to run?
→ language-cooperation link
Conditions to run; different models (gpt and claude), different task orders
Im free until Feb 23, so would like to try to finish by then. Can we plan weekly meeting and whoever wants to join can join?
Yes
Deadline: Februari 23rd
What is the best way to share updates/findings? Seeing as there are so many conditions, I sometimes struggle getting everything together clearly
→ share google doc/slides
→ send 24 hours before meeting
Simulation generation: currently, when simulation crashes, the states and memory get loaded into llm and run gets started again. Is this legit? Or can we only do this if we specify seed parameter? In this case, Anthropic does not have seed parameter, so what then?
→ no seed parameter


### 2026-01 — Ivar/Mbella

I feel a little unclear atm about the direction and what to look for exactly, so I should write up the blogpost to get more clarity.

Done:
Run for all base models 50 rounds + analyses
Implemented myth parallelization; agent 1 and 2 myths are generated simultaneously
Fixed game trajectory plot; one symbol per agent
Looked into results

Not Done:
Blog post
Concreteness score
Strategy generation
Multiple agents/large society
Evolutionary mechanism/generations

Results
Does deviation in game scores coincide with deviations in myth similarity?
GPT4o
Does not seem so (as far as i can tell), but also do not have a clear metric

- Claude-3-haiku
    - cooperative language use goes up in round 35, game scores dip in rounds 42-45
    - lag correlations:
        - Lag correlations test whether one agent's cooperativity in round N is related to the
other agent's cooperativity in round N-1. Indicating mimicry or adaptation of
cooperative word usage between agents; If Agent_1 uses cooperative language in round
10, does Agent_2 mirror that in round 11?
- For most models this is very low (just like cooperative language score), but for claude is
0.72 . + cooperative word usage plot seems to indicate they are in this positive feedback
loop.



- Deepseek-chat-v3
    - round 18, investor and trustee cumulative balances start to diverge

-GPT5-nano
    - cumulative balances seem to have phases/equilibrium states?
Diverge-close-diverge?
    - faulty myth generation

Questions:

Testing
How to test/look for correlation between deviation in game scores and deviation in myth similarity? Spearson r correlations?

Measures:
I think this would be an interesting sub question "Does linguistic evolution (the creation of new linguistic patterns) coincide with linguistic convergence?" So, does a high value of unique POS patterns correlate to the similarity of individual agents' POS patterns?
However, does this make sense? Can we use POS patterns for this? Now what happens is, we take a myth text, separate the sentences, for each sentencssign all words with a POS tag. Thus, a POS pattern is a pattern describing one sentence (see examples). However, these sentences are generally long and therefore the patterns are almost always new. What we see is that each sentence has a different pattern and this pattern occurs only once.
Is this then a valid metric to speak of "Linguistic Innovation/Evolution"? Or no.
Currently, innovation rate is really high (avg 80%). However, this is just because it is unlikely that two sentences are EXACTLY the same right? So does this actually tell us anything? Also, maybe an increase in POS patterns is just because myths become longer?
→ Finally, my hypothesis about this is that linguistic innovation and convergence are likely a function of agent memory. Less memory means more innovation and less/more convergence?

Implementation
Currently, sometimes response generation crashes because models do not give back correct game response format. We tell them "- Response format: {{'send': <amount>, 'reason': <re}}",  "IMPORTANT: Always respond in the correct format based on your current role." but they don't always do this.
Could enforce this using Pydantic schema only for Game responses. Can we do this? Or do you think will skew results too much?


### 2025-12-09 — Ivar/Mario

- The config experimental framework I built is really nice and should definitely highlight for COSMOS result essay. Also upload a clean repo.

Why do Payoffs per round plot and cumulative balance plot not align? It trustee payoff per round goes down, why do we not see a different plot in cum balance?
→ because agents swap roles each round

Ask:
What is optimal strategy?
When does this strategy start to occur?
When they land on the strategy, do they keep playing it? Or do they divert at some point?
In deviation cases, it would be very interesting to look at the myths and written strategies

Game result interpretations
The red squares become more and more flat/ far apart from each other!! (what does this tell us? )

Downward trend toff through time
= trustee returns more through time
Possible reasons for agents to do this is so that in the next round, other agent returns more to.

Initial Jump in payoffs
Agents in trustee role quickly learn to return as mush as possible.

Flattening of payoff, why can i not go higher?
Lets say investor sends maximum, then he sends $5.
Then trustee receives, 3*$5 = $15.
If trustee keeps 2, then trustee returns 15-2 = 13.
 So then, the investor earns $13 this round.

To Do:
In the plots, can we have different symbols for each agent? That way it is clear that we're looking at different agents.
We see there is no positive words during deviation rounds (rounds 16-24), look into the file to see whatsup.


### 2025-12-04 — Ivar/Mario

Questions:

my grant deadline for this project is January 7th. I agreed with them that running some experiments would be enough. What do you think would be necessary to have for then? Currently, I'm planning to at least have:
1. models generate game strategies,
2. correlaon between strategies, game scores and myth texts (to see how correlations change),
 3. run with different base models,
4. parameter to include/omit round length in prompt (to test for possible backward induction).
5. 10 agents cooperating in groups of 2, randomly paired.

    → 1. Yes, look at CoT/reasoning strategies. Keep track of strategies.
→ 2. Correlation: we could correlate collaborativeness scores of myth ~ action.
Correlation strategies ~ action; if the agent says it takes an action, it will likely take an
action. Could maybe categorize or cluster the strategies? For example, Unconditional
strategy (i will always play this action). We could classify with llm-as-a-judge into what
category strategy falls.

You're thinking of strategies that are **reactive or contingent on an opponent's previous behaviour**, often studied in game theory, social dilemmas, and multi-agent systems. Here are some common categories and alternative names:

### 1. **Reciprocal strategies**

* Tit-for-tat (mirroronent's previous move)
* Tit-for-two-tats (forgives one defection before retaliating)
* Win-stay, lose-shift (repeat a move if it worked, change if it didn't)
* Pavlovian strategies (similar to win-stay, lose-shift; reward reinforces action)
* Generous tit-for-tat (occasionally forgives defections)

### 2. **Conditional or contingent strategies**

* Trigger strategies (cooperate until opponent defects, then punish indefinitely or for a set period)
* Conditional cooperation (cooperate if the other does; defect otherwise)
* Grim strategies (cooperate until a defection occurs, then defect forever)

### 3. **Reactive / memory-based strategies**

* Memory-one strategies (decisions based on the previous round only)
* Memory-n strategies (decisions based on the last n rounds)
* Probabilistic tit-for-tat (retaliate with some probability rather than deterministically)

### 4. **Other descriptive terms**

* Retaliatory strategies (punish defection)
* Forgiving strategies (allow occasional defection without immediretaliation)
* Adaptive strategies (adjust based on observed behaviour over time)

If you want, I can make a **compact table mapping all these strategies with their "type" and typical examples**—very handy for research or teaching. Do you want me to do that?

https://medium.com/blagenflorble/a-prisoners-dilemma-cheat-sheet-4d85fe289d87

https://ojs.aaai.org/index.php/ICWSM/article/view/35829/37983


Currently, we don't really have a good method to measure automatically how well myths capture game dynamics. I could maybe use LLM-as-a judge for this. Are you aware of any method to test this?

    → Abstractness score: dictionaries of concreteness norms (Brysbaert concreteness ratings) . Count number of concrete words vs abstract words in myth. Could even use LIWC here. Justify as: yes we do llm-as-a-judge, but we also use non-llm measures.

In terms of correlating game behavior (scores or strategies) with myths, what do you think we would need for this? How many data points, what conditions, etc.


For  January 7th:
Start from a report; what would you like to write? What are the main questions? Main conditions, etc.?
Could also put emphasis a bit more on tooling; that we have a tooling to quickly run more of these experiments.


### 2025-11-13 — Thursday meeting

Does anyone have any updates before Ivar goes into his updates?
Mario:
Suggested Ivar goes first before he talks about his ideas
Ivar:
How we started first was that we tried to combine Aron's donor game with the myth-writing, so we could see if some sort of linguistic evolution occurs when they play the donor game (high cooperation) versus low cooperation on the donor game. But, we noticed it was hard to understand what was going on, so he decided to implement it from scratch.
Then, we decided to move to the trust game because it was simpler.
We have a basic implementation now: 2 agents play a trust game and then write a myth. And we have some stats to see how the myth evolves, and extracting key words in the myths which could serve as a basis for a coerativity measure.
Ivar explains the architecture: Agent 1 is the investor, Agent 2 is the trustee. They play the game (but importantly, they only receive information about the other agent's actions), then they write the myths
Ed:
Do they alternate rounds?
Ivar: no, we still need to do that.
Ivar:
Questions:
For a first version, do we need to implement those things? I.e., swapping roles.
Aron:
Do they swap roles? With the same agent?
Ivar:
They don't swap roles.
Aron: they definitely should swap roles. Because otherwise the cooperation scores just reflect whether you were assigned as investor or trustee.
Ed:
What are the parameters?
Endowment needs to be less than the donation
Aron: let them choose the donation in both directions
Structured outputs per call, and you can always do a reasoning step and then a step where you just write down the number.
Aron
First have the reasoning step, and then in the second step, prompt them in the output with the reasoning step and then ask them to only return the nr
This is only a concern if you're not using a reasoning model, because then you force it to use test time to compute what it wants to do
Ed: if you're not using a reasoning model then this is redundant though. But this is a consideration for reproducibility because reasoning models are more expensive, so not everyone's going to use it
 Reasoning model vs non-reasoning model would be interesting. Maybe the non-reasoning model would be more cooperative because the reasoning model might just not engage with the game because of the risks.
Mario:
Equilibrium is to defect and exit.
What could be the role of the communicative / storytelling task? The agents could reason together about a cooperative strategy.
→ games could start from a defect/defect equilibrium, and through the dialogue/stories, they slowly move towards more cooperative action. Then social welfare grows from that.
Ed:
They didn't say there were 6 rounds. → end up in a repeated game. It creates the possibility of tit for tat
How moes it play before myth writing? They write a myth every round. And do they see the previous rounds' behavior? Now, they see the history of actions but not myths. Ivar thinks they should see the history of the myths.
Do they know how many rounds? Ed thinks don't tell them how many rounds. Ed thinks we've got exactly the right setup. In principle, there should be a cooperative equilibrium.
Mario:
Interesting to have a setup where they do know it's a finite horizon, then the rational thing would be to defect, but only by virtue of cooperation through language, they have a coordinated strategy.
Ed: most interested in the dynamics -- infinitely repeated game, all these different equilibria, which one do they converge to? The storytelling can act as a tipping point
Mario:
Cooperation can emerge as one of the possible equilibria. What is the relation to the language task? ⇒ language causes behavior to converge to different cooperative states
Jane:
Having the interaction and then the myth is very importanause you could have a trust-based game, but you don't know anything about your partner. Through the myth, you're transmitting a culture between the two players. You also have the personality of the agents. But I learn about them via the myths and their behavior. Maybe the myth-writing is reflective of my underlying motives, and the moral of the story could have some sort of alignment, you could predict cooperative behavior.
Interesting to see if potential personas/cooperation are reflected in the myth-writing.
Ivar:
Language use of one investor starts off very positively. But by the end, most of the words are related to themes of "screaming" and "madness"
Jane: Maybe emotions are something we should measure then too.
Aron:
How can the story influence in-game behavior in the current setup? Is the story included in the game prompts?
Ivar: first its donation then myth-writing. But I think we should have a reversed setting too.
Put the myths in the context.
Jane:
If we're trying to measure how morally sound the interactions are after, use LLM-as-a-judge to ask what's the moral of the story? We could ask what are the motives of the main character? Facts that relate to the cooperative cultural evolution. If both players give a "cooperative" moral of the story, then they both have a cooperative persona in that setting, that might encourage cooperative behavior. And the vice-versa could hold. And it would be interesting if they don't match!
Knowing the whole history - a potted version of that - would be very useful for this
Ed:
Two pathways of communicating history: actions taken and myths. It would be cool to see what would happen if we only provide the myths. Might be more aligned with how people do it.
Ivar:
Should we have a parameter to adjust population size? Is that important for this first draft?
Ed: you'd get a lot more diversity and therefore more interesting dynamics… but maybe do that after we've implemented everything else first.
*Ivar is gives a quick demo of the architepts*
It would be good to provide as much information as possible in the beginning. The trustee should know how much money the investor had to start with in that first bit of the trustee prompt.
The issue of communication is solved when they return myths to each other.
Myths are a compression of what happened in the game.


### 2025-09-05 — Friday meeting

Agenda:
Propose research design to Ed
Finalize pilot design
Roadmap to 22 November
Assign roles

Notes

Rephrase 1st question in terms of (linguistic) convergence (do stories of different groups become more/less alike, in what way?)
Change interactions patterns between agents
currently , agents are randomly matched as pairs, but such that same agents are never paired twice
Mario: how can we make agents interact more freely? Still as dyads of two, but paired differently?
Interact as a result of past interactions?
Interaction as a genetic tree? Pair agents based on myth similarity?
Task order
Worth checking if changing task order has big influence


### 2026-01-26 (later — Aron 4-agent test) — Ivar/Mario/Arabella/Aron/Alex/Ed

Aron made an implementation that would work with 4 agents, but Ivar got an error
We tested this
There were some issues with the plots which Ivar fixed
Question about possible memory issue - we saw memory capacity = 3, but when you look at the actual message list of an agent, you'd see 9 messages. Error? But that's because we have 1 message for system prompt, 2 per response (because its the prompt + response), so then 3 stands for the amount of rounds, i.e., the response pair
6 messages of rounds that have already happened, system prompt, 1 message which is the prompt for the new round, plus the response for the new round = 9 in total. So that's why we see 9 messages
= memory = 3 previous rounds of interaction
Collapse in game behavior → change in myths?
For these runs it might not be insightful, because of a leakage between the tasks
GPT-5 will often output the game response twice - one in the myth text and one in the game text. And no actual myth.
Claude 4.5 kind of does the reverse: the game respo become this intermingled thing of the myth, the agent writing the myth, and the json format at the end. E.g.: slide 50 gives an example.
Do we care about this behavior?
Ed: if its producing the wrong format, then that's not ideal, because its not a myth
Just explain what's going to happen in the myth formatting. Tell it in the system prompt what's going on in the whole game - including the myth-writing
Pedantic schema to strictly enforce output patterns; forces the model to fit a format. Is this too strict? Ed: we could do that for the game, but it doesn't seem necessary, we get the right format
Ed: what's the logic of making the output the reasoning here? Ivar: to get a reason why you made this decision. I liked in your paper with Aron that you always showed how the strategy evolved, so I thought that would be interesting to capture. Ed thinks that they have thinking tokens, but not sure if we'd be able to capture that. If you ask it to produce the output and then explain the reasoning, thenask for the reason first, because they're autoregressors.
Most interesting part: does this part of this story associate with more generous behavior? If we can show exactly that - insofar that the myth morale correlates with real-time donor behavior in the game - then this would be very interesting.
Open to-dos:
LLMs as a judge
Recap:
We decided to focus on language-cooperation link
How does linguistic evolution occur and change through time?
Cooperativity <-> myths?
Gameplay behavior?
Compare between different models
→ try to get paper by 23 february

When we get a behavior in this game, the behavior just seems to stick. This is tricky because we get a very generous baseline… It seems that this game will have too strong a baseline and not enough room for variance with the myths.
There is much more diversity in 45-47, but still no overall increase in generosity, which is also interesting.
Comparing this to the latest slides from Aron's runs, we assume this is direct reciprocity,
In the direct ity case, the baseline might be too strong, but in Aron's runs, there's not.

Slide 52: what is the setting here?
Aron: they see the same traces that we had in the other paper. So last three turns or something like that. Actually here, we have concept width and depth. Width = how many other agents' past actions you see. Depth = how far back for each agent. Another parameter of interest is this myth visibility.
Ed: if we had the result where the myths didn't have that much effect on direct reciprocity but moreso for indirect reciprocity, if we compare to people, that makes sense, right?

Imagine that one thing might be cool - take Aron's result and link in the myths and we see an increase in cooperations across rounds - it would be cool to vary # of agents
Or introduce new agents and see if they know immediately how to behave
When you have a culture that's evolved like humans but in agents, make sure they've got some sort of mythology
Ivar: relation between our paper and the digital red queemes in the myths are competing against each other. Its an implicit red queen thing going on. We dont want competitive agents we want competitive ideas

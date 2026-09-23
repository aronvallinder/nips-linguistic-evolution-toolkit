# D011 — Rerun the September matrix on current frontier models with reasoning on

- Recorded / last verified: 2026-09-18 / 2026-09-23
- Decision status: agreed and executed (Opus 5, Gemini 3.1 Pro Preview, GPT-5.6 Sol at effort high); Sol at effort none skipped after its smoke run; GPT-5.6 Luna rejected as a non-frontier tier. Opus 5.5 checked on replicates 0–2 (2026-09-23); replacing Opus 5 with Opus 5.5 as the frontier Claude model is proposed (assistant), leaning yes (Ivar), not yet decided.
- Scope: the September no-defector matrix (2 and 8 agents × game / game→myth / myth→game × replicates 0–4, informed negative-only noise) on one flagship per provider. Excludes defector conditions, mixed-model runs, and any reasoning-off arm.
- Decision authority: Ed's request in the 2026-08-18 team meeting (transcript: results stop being believed once the model is three or four months old); Ivar's authored instructions in the 2026-09-18 Claude session ("run full Opus 5, Gemini and sol High. Skip sol none"; reasoning kept on after the assistant's assessment).
- Implementation status: sampled completed finals, 90/90 launcher-audited (`data/json/noise_experiments/frontier_rerun_20260918/main_reasoning_on_receipt.json`); config `config/frontier_rerun_20260918.yaml` (generated), launcher `scripts/run_frontier_rerun.py`, branch `run/frontier-rerun-20260918`.

## Decision and rationale

Run each provider's current flagship on the unchanged September protocol, with the
provider's reasoning on, so the task-order results can be shown on models readers
consider current. **Explicit** (Ivar, 2026-09-18): frontier capability is the goal,
which excludes Luna (OpenAI's nano tier) and Sonnet 5; Sol-none is dropped from the
matrix. **Explicit** (Ivar, accepting the assistant's assessment): reasoning stays on
because the frontier claim is about the deployed system, the September references had
reasoning on, the September format study showed visible reasoning moves Claude
sending by about 21 points, and Opus 5 with thinking disabled writes reasoning into the
visible answer. **Inferred** (assistant, accepted by launch): Batch API and prompt
caching were reviewed by three agents and rejected as not worth their engineering
at the corrected cost (about $150 total).

Request profiles: Opus 5 adaptive thinking with `output_config.effort: high`,
temperature omitted, cap 64000; Gemini 3.1 Pro `thinkingLevel: high`, temperature 0.8,
cap 65536; Sol `reasoning_effort: high`, temperature omitted, cap 128000. Opus 5
rejects `budget_tokens`, so the thinking regime changes together with the model; this
is a recorded protocol difference, not a pure model swap (see D004).

## Evidence

- Primary source: Ivar's instructions in the 2026-09-18 Claude session (user
  instruction); Ed's 2026-08-18 meeting transcript (computer-generated transcript,
  attribution as recorded).
- Prices and API constraints read on 2026-09-18 from platform.claude.com (pricing;
  4.7+ tokenizer note), developers.openai.com (gpt-5.6-sol, gpt-5.6-luna model pages),
  ai.google.dev (thinking levels; 3.1 Pro cannot disable thinking).
- Implementation: commits on `run/frontier-rerun-20260918` (config generator,
  launcher, analysis); condition audit asserts every non-model input equals the
  September combination and every call's request settings equal the pinned plan.
- Runs: 90 finals with sha256 in `main_reasoning_on_receipt.json`; two quarantined
  Gemini finals with `reason.json` under `quarantine/` (transient connection drops,
  resampled under the same seeds); credit interruptions on all three providers,
  rerun after top-ups. Results and disclosures:
  `docs/figures/frontier_rerun_20260918/README.md`.

## Chronology and supersession

- 2026-08-18: Ed asks for a rerun on current models (transcript).
- 2026-09-17: Codex cost table (pasted by Ivar) prices Opus 5 at $2/$10; superseded by
  the verified $5/$25 on 2026-09-18.
- 2026-09-18: plan doc `docs/research/frontier_model_run_plan_2026-09-18.md`; first
  cost table overstated 5–7× (recursive usage aggregation), corrected against the
  receipt method; three-agent review of Batch API, caching, model choice; smoke (4
  arms), 18-run pilot, 90-run main stage; Sol-none skipped.
- 2026-09-23: Ivar asks whether to use Opus 5.5 instead of Opus 5 and requests a test
  run ("do smoke and pilot for now", then "just do 3 replicates per cell"). An `opus55`
  arm with the Opus 5 request profile (effort pinned high) was added; 18/18 audited
  finals, $31.79 (`reps3_opus55_receipt.json`). All six cell means within 2 points of
  Opus 5 on the same seeds; same task-order ordering; wider spread in the 2-agent game
  (61/75/73). Opus 5.5 uses 3–9× more thinking tokens per call at the same effort, so
  the thinking regime differs again. Ivar leaned towards switching ("probably yes");
  the switch itself is **proposed**, pending his confirmation. Results:
  `docs/figures/frontier_rerun_20260918/README.md` (Opus 5.5 check).
- Does not supersede D004 (September profiles remain the September regime) or D010.

## Unresolved / next evidence

- Five replicates per cell: descriptive only. Sol's game-only collapse (2 of 10 runs)
  needs more replicates before any rate is claimed.
- Whether Sol's behavior differs at effort none (the zero-lock question flagged in the
  September researchlog) is untested beyond one smoke run.
- Fable 5.1 and GPT-6 Astra were priced but not run.

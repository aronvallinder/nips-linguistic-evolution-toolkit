# Frontier-model rerun plan (for explicit go) — 2026-09-18

Status: proposed, not approved, not implemented, no paid calls made.
Origin: Ed's 18 August request to rerun on current frontier models ("once the model is
three or four months old people stop believing your results"). Supersedes the earlier
Opus 5 + GPT-5.6 Luna draft of the same day: Luna is OpenAI's nano tier and does not
meet the frontier-capability goal, and the earlier cost table was inflated 5–7× by a
faulty token aggregation (corrected below, §5).

## 1. Models and request profiles

Three provider flagships, reasoning ON to match the September regime, plus one cheap
reasoning-OFF contrast arm on the OpenAI model.

| Arm | Repo slug (`base_models` key) | Provider id | Reasoning | Temperature | Output cap | Prices in/out per MTok |
|---|---|---|---|---|---|---|
| A | `anthropic/claude-opus-5` (`claude_opus_5`, NEW) | `claude-opus-5` | `thinking: {type: adaptive}`, `output_config: {effort: high}` | default (omitted; Opus 5 rejects it) | 64000 | $5 / $25 |
| B | `google/gemini-3.1-pro-preview` (`gemini_3_1_pro`, exists) | `gemini-3.1-pro-preview` | `thinkingConfig: {thinkingLevel: high}` | 0.8 (as September Gemini) | 65536 | $2 / $12 |
| C | `openai/gpt-5.6-sol` (`gpt56_sol`, NEW) | `gpt-5.6-sol` | `reasoning_effort: high` | default (omitted) | 128000 | $4 / $20 |
| C0 | same as C | `gpt-5.6-sol` | `reasoning_effort: none` | default | 128000 | $4 / $20 |

Verified today on official pages: Opus 5 price and the 4.7+ tokenizer note
(platform.claude.com pricing); Sol id, price and effort values none/low/medium/high/xhigh/max
(developers.openai.com model page); Gemini 3.1 Pro thinkingLevel low/medium/high, default high,
cannot be disabled (ai.google.dev thinking page). Not verified: Gemini 3.1 Pro's maximum
output cap; 65536 is carried over from the 3.7 Flash profile and the smoke run checks it.

Why these reasoning settings:
- Opus 5 rejects `budget_tokens` (400), so the September fixed 8192 budget cannot be
  reproduced. Adaptive thinking at effort `high` is the documented default. Fable 5.1 was
  not chosen: exactly 2× the Opus 5 cost and thinking cannot be disabled either.
- `high` on Sol and Gemini Pro matches the September GPT/Gemini labels. Labels are not a
  cross-vendor scale (D004).
- Reasoning is NOT turned off on the main arms. Repo evidence: forbidding visible
  reasoning cut Claude's sending by about 21 points (researchlog 2026-09-04); the
  September reference runs all had reasoning on; Opus 5 with thinking disabled tends to
  write reasoning into the visible answer instead. Arm C0 exists because the GPT round-1
  zero-lock appeared under high reasoning and the researchlog flags "specific to the
  high-reasoning profile" as unverified. It costs about $30 and answers that question.
- `src/llm_settings.py` validates all four profiles as written. `resolve_request_plan`
  strips the vendor prefix, so `claude-opus-5` and `gpt-5.6-sol` need no alias entry;
  `gemini-3.1-pro-preview` already has one in `src/utils.py`.

## 2. Matrix

Per arm, the exact September no-defector matrix:

| Size | Task orders | Replicates (ids) | Runs |
|---|---|---|---|
| 2 agents, fixed partner | game, game→myth, myth→game | 5 (0–4) | 15 |
| 8 agents, balanced rotating pairing | game, game→myth, myth→game | 5 (0–4) | 15 |
| Total per arm | | | 30 |

Four arms → 120 runs. Everything except the model and its profile is copied from the
`negative_only_reasoning_rerun_*` sets in `config/experiments_noisy.yaml`, restricted to
the no-defector game params (`noisy2_/noisy8_crossmodel_negative_game_r3`,
`_negative_twotask_r3`).

## 3. Game parameters and prompts (unchanged)

Endowment $5, multiplier 3, 10 rounds, neutral persona, memory-primary chat context
(capacity 3 game-only, 6 two-task), uniform negative-only noise range 1.0 on sent and
returned amounts, agents informed via the system-prompt notice, paired protocol seeds
base 202608250, game retry policy repeat-same-prompt-once, myth topic "anything".
Dyads: fixed partner, roles alternate, Agent_1 sends in round 1. 8 agents: names hidden,
co-player history window 3, own window 0, previous-round partner's myth transmitted.
Prompt keys: `trust_game_default` system prompt, `trust_game_round1_*`,
`trust_game_later_*_minimal`, myth arm `memtest_memory_primary`
(`myth_writing_default_game_directive` / `myth_writing_later_rounds_directive_memory_primary`).
No prompt names a model.

## 4. Sequence and gates

| Stage | What | Est. cost (mid) | Purpose |
|---|---|---|---|
| 0 Smoke | one 2-agent game run per arm (4 runs) | about $1 | request bodies accepted (adaptive thinking + effort; Sol effort none/high; Gemini Pro cap), JSON parsing, refusal path |
| 1 Pilot | one 8-agent myth→game run for A, B, C (3 runs) | Opus $7, Gemini $5, Sol $12–35 | pin the three unknowns: Opus tokenizer + thinking volume, Sol reasoning volume, Gemini Pro thinking volume |
| 2 Main | 30 runs each for A, B, C0; C after pilot confirms cost | see §5 | the result |

Stage 2 launches only after the pilot's measured per-run cost is re-projected and, if the
projection differs materially from §5, re-approved. Stages 0–1 together stay under $50.

## 5. Cost (standard rates, no batch or cache discount)

Basis: receipt-method token means of the 90 September no-defector finals
(`agents[*].interaction_history[*].response.usage`, LLM-sourced calls only). Cross-check:
Sonnet 4.5's 30 runs cost $47.14 on this basis, the same Anthropic figure the 17 September
mixed-model plan derived. Anthropic mid adds +30% tokens (4.7+ tokenizer); high doubles
output on top. OpenAI low/mid/high = Nano output tokens × 0.5 / 1 / 1.5. Gemini Pro uses
the 3.7 Flash token profile as-is (single figure, likely a floor). Sol effort none is
priced as input plus visible-text output only.

| Arm | 30-run matrix, low / **mid** / high | 8-agent cells only (15 runs) |
|---|---|---|
| A Opus 5 | $79 / **$102** / $155 | $63 / $82 / $124 |
| B Gemini 3.1 Pro | **$36** | $28 |
| C Sol, effort high | $163 / **$306** / $448 | $131 / $244 / $358 |
| C0 Sol, effort none | about **$30** | about $25 |
| Smoke + pilot | about **$30–50** | |
| **Total** | **about $350 low / $525 mid / $720 high** | |

Per provider (mid): Anthropic about $110, Google about $45, OpenAI about $370. The total
crosses the $200 approval threshold, so this document is the thing to say "go" to.
OpenAI credits ran dry on 2026-09-15; top up before Stage 0.

Levers reviewed and rejected (three-agent review, reports in the session scratchpad):
Batch API halves the Anthropic bill (about $51 saved) but needs a 600–800 line batch
coordinator and 6–33 h unattended wall clock; prompt caching saves 4–7% because the
sliding memory window leaves only the system prompt as a stable prefix and the 2-agent
system prompt is below the 512-token cacheable minimum. Neither changes the condition;
neither is worth it at this scale.

## 6. Implementation required before Stage 0 (not yet done)

- `config/experiments_noisy.yaml`: `base_models` entries `claude_opus_5`, `gpt56_sol`;
  `llm_profiles` anchors `september18_opus5`, `september18_gemini31pro`,
  `september18_sol_high`, `september18_sol_none`; 24 sets (6 shapes × 4 arms) copied from
  `negative_only_reasoning_rerun_*` with only the no-defector game params.
- Frozen launcher `scripts/run_frontier_rerun.py` in the style of
  `scripts/run_figure2_extension.py`: dry-run default, `--execute`, `--stage smoke|pilot|main`,
  resumable finals only, condition audit asserting every non-model input equals the
  September combination, `EXPECTED_POLICIES` for the four arms, rates
  anthropic (5, 25) / openai (4, 20) / google (2, 12), completion receipt. Output under
  `data/json/noise_experiments/frontier_rerun_20260918/<arm>/`.
- No fallback model on Opus 5 (a server-side fallback would silently change the
  condition). A refusal surfaces as an empty response, is retried by
  `_should_retry_anthropic`, and otherwise fails the run for resampling.
- Launcher Python has `anthropic` 0.75.0 and `openai` 1.37.1; all profiles travel through
  `extra_body` / `generationConfig`, so no SDK upgrade is required.
- Analysis: extend `scripts/analyze_negative_only_crossmodel_batch.py` (or its successor)
  to read the new arm directories; record the thinking-regime change in the results README.

## 7. Caveats

- Not a pure model swap: Claude 4.7+ models reject the fixed thinking budget, so "model"
  and "thinking regime" change together for arm A (D004). Record it.
- Gemini 3.1 Pro is a preview model from an older generation than the current Flash; it
  is still Google's only Pro on the API.
- Sol at effort high may generate about 1M output tokens per 8-agent two-task run; GPT-5
  Nano at high was the September critical path (about 3 h per two-task set at 3 workers).
- The 90-run mixed-model population ladder started 2026-09-18 12:37 on the same
  Anthropic and OpenAI keys; launching concurrently shares rate limits.

# Provider code-path audit (read-only)

Repo: `/Users/ivar/Desktop/Research/AI_projects/LLM_evolution/nips-linguistic-evolution-toolkit`, branch `main`, audited 2026-09-04. All line numbers refer to the working tree at that time.

## Headline

**The PI's belief is wrong in part.** Message format (roles, system prompt, seeds) is equivalent across providers. Routing, reasoning/thinking, temperature and max-tokens are NOT identical, and the same model slug has been run under two different regimes (direct vendor API vs OpenRouter) whose settings differ.

Provider routing is decided per machine by which keys sit in `.env`, not by the experiment config. Under the default `LLM_PROVIDER=auto` a slug goes direct to its vendor when the vendor key exists and otherwise falls back to OpenRouter (`src/utils.py:208-215`).

- On this machine (Ivar) only `ANTHROPIC_API_KEY` and `OPENROUTER_API_KEY` are set (key names checked in `.env`, values not read), plus `ANTHROPIC_MAX_TOKENS=4096`. So Claude runs direct-Anthropic; GPT and Gemini go through OpenRouter. `docs/verified-facts.md:11` confirms this routing.
- Aron's Gemini 3.7 Flash figure metadata (`docs/figures/punishment_comprehension_gemini37_20260823/metadata.json`) shows `llm_provider: google`, `llm_provider_mode: direct`, `thinking_level: medium` from `GEMINI_THINKING_LEVEL`, `temperature_sent: false`, `request_timeout_seconds: 300`. So Aron routes Gemini direct with a thinking level set. Aron also authored the direct OpenAI/Anthropic/Gemini routing (commits bf90f967, 1374148b, 83654c20, all 2026-04-29), which suggests direct keys on that machine, but that is inference, not verified.
- Provenance fields (`llm_provider`, `provider_model`, ...) were only added to `run_metadata` on 2026-08-25 (commit 38fa31aa). Of 5526 saved run files under `data/json`, 5495 have no provider fields at all.

## 1. Provider selection (`src/utils.py`)

- Mode source and precedence: `provider` argument > env `LLM_PROVIDER` (re-read at call time via `_env`) > module constant `LLM_PROVIDER` > `"auto"` (`:27`, `:178`). Valid modes: auto, direct, openrouter, openai, anthropic, google, gemini (`:31`).
- Slug to vendor: `openai/` -> openai, `anthropic/` -> anthropic, `google/` -> google, anything else -> openrouter (`:68-75`).
- Forced modes (`:187-194`): `openrouter`, `openai`, `anthropic`, `google`/`gemini` create that client regardless of slug.
- `direct` (`:196-206`): vendor client by slug; other slugs raise.
- `auto` (`:208-215`): `openai/*` + `OPENAI_API_KEY` -> direct OpenAI; `anthropic/*` + `ANTHROPIC_API_KEY` -> direct Anthropic; `google/*` + (`GEMINI_API_KEY` or `GOOGLE_API_KEY` or `GOOGLE_GENERATIVE_AI_API_KEY`, `:254`) -> direct Gemini; else `OPENROUTER_API_KEY` -> OpenRouter; else raise (`:217-222`).
- Client is created once per `run_simulation` call (`src/simulation.py:379`), so each batch worker process resolves the provider independently from its own environment.
- Gemini "client" is a dict of api_key + base URL; calls use raw `urllib` against `generativelanguage.googleapis.com/v1beta` (`:30`, `:257-261`, `:637-654`).

## 2. Model-id aliasing

- OpenRouter: slug passed unchanged (`:86-87`).
- Direct providers, in order: env override `LLM_DIRECT_MODEL_<SLUG_UPPERCASED>` (`:78-80`, `:89-91`) > `DIRECT_MODEL_ALIASES` (`:33-50`, `:93-94`) > strip `<provider>/` prefix (`:96-98`).
- Aliases that change the model relative to the slug:
  - `google/gemini-3-pro-preview` -> `gemini-3.1-pro-preview` (`:48`, added 2026-04-29 in commit 1374148b). Direct runs under the 3-pro slug hit 3.1 Pro; OpenRouter runs hit the real 3-pro-preview. `config/experiments.yaml:955` notes the original endpoint is deprecated and reruns moved to 3.1.
  - `anthropic/claude-3.5-sonnet` -> `claude-3-5-sonnet-latest` (`:36`), a floating id.
  - The rest pin dated snapshots (e.g. `anthropic/claude-sonnet-4.5` -> `claude-sonnet-4-5-20250929`, `:39`).
- `run_metadata.provider_model` records the resolved id (`:107`) only for runs after 2026-08-25.

## 3. Message transformation per provider

Input to all paths is the same list built in `src/agents.py:161-170`: `messages[0]` is the system prompt (`src/simulation.py:420`), optional seed user/assistant pair at `[1:3]` (`:426-431`), then alternating user/assistant. Truncation keeps `messages[0]` plus the last `2*memory_capacity` messages (`agents.py:82-87`), which preserves alternation. A rejected or failed prompt is rolled back (`agents.py:89-96`), so no dangling user turn is left.

- OpenAI-compatible (OpenRouter and direct OpenAI), `_chat_messages` (`:270-277`): keeps `role` in {system, user, assistant} with non-None content; strips the extra `reasoning` and `usage` keys stored in memory (`agents.py:211-216`). System stays a `system` role message. No merging, renaming or dropping.
- Direct Anthropic, `_anthropic_messages` (`:280-294`): all `system` messages joined with a blank line into the `system` parameter (`:559-560`); user/assistant passed as-is. No merging of consecutive same-role turns (none occur, see above).
- Direct Gemini, `_gemini_messages` (`:297-316`): system -> `system_instruction`; `assistant` renamed to `model`; content wrapped as `parts[{text}]`. Empty contents list raises (`:620-621`).
- Assistant-slot content (seed myths, prior decisions) is sent verbatim on all three paths. Nothing else is dropped.

Conclusion for this item: format is equivalent. No evidence of a role or system-prompt bug.

## 4. Sampling and generation parameters

No path sets `top_p`, `seed`, `stop`, or `n` (grep of `src/utils.py`). `temperature` comes from the config (0.8 in `run_metadata`).

| Route | Temperature | Max output tokens | Reasoning / thinking |
|---|---|---|---|
| OpenRouter, non-`openai/` non-`meta-llama/` slugs (Claude, Gemini, DeepSeek, Grok...) | 0.8 sent (`:377`; `_supports_custom_temperature` returns True for provider != openai, `:518-520`) | none unless `OPENROUTER_MAX_TOKENS` (`:382-383`) | `extra_body.reasoning.effort` = `OPENROUTER_REASONING_EFFORT` if set, else the `call_llm` default `"medium"` (`:319`, `:388-406`). `agents.py:174` never overrides it. Values none/false/0/off disable (`:393-394`). |
| OpenRouter, `openai/gpt-5-nano` (and `meta-llama/*`) | 0.8 sent (`:377`) | same | **no reasoning param at all** (`:396-401`), so the vendor default applies. |
| Direct OpenAI, `gpt-5*` | **omitted** (`:521-523`, comment: GPT-5 Chat Completions accepts only the default) | none | `reasoning_effort` = `OPENAI_REASONING_EFFORT` or **`"minimal"`** (`:379-380`, `:526-531`). |
| Direct Anthropic | 0.8 sent except `claude-opus-4-7*`/`4-8*` (`:534-538`, `:557-558`) | `ANTHROPIC_MAX_TOKENS` or **1024** (`:547`); this `.env` sets 4096 | **no thinking parameter ever** (`:552-560`); `reasoning` always `None` (`:577`). |
| Direct Gemini | 0.8 sent except `gemini-3.7-flash` (`:624`, `:689-695`) | none (`:626-629`) | `thinkingConfig.thinkingLevel` only if `GEMINI_THINKING_LEVEL` set (`:633-635`); `reasoning` always `None` (`:663`); `thoughtsTokenCount` recorded as `reasoning_tokens` (`:744`). Request timeout 120 s default, `GEMINI_REQUEST_TIMEOUT_SECONDS` override (`:698-712`). |

Note the exact-string check for 3.7 Flash (`:695`): an `LLM_DIRECT_MODEL_*` override to another id would bypass it.

## 5. Response parsing

Per provider, in `call_llm`:

- OpenAI-compatible (`:408-479`): empty `choices` or empty `content` -> `ValueError("Empty response from LLM")` (`:410-411`). That `ValueError` is not matched by the retry clauses; it falls to the generic `except Exception` and re-raises immediately (`:511-513`). `finish_reason` is never inspected. Reasoning extracted from `msg.reasoning`, `reasoning_details`, `model_extra`, else a placeholder string built from reasoning token counts (`:413-455`).
- Direct Anthropic (`:562-579`): text blocks joined (`:593-601`); empty -> `ValueError`, which IS retried in-loop as a stochastic refusal (`:604-613`). `stop_reason` never inspected, so a `max_tokens` truncation passes through as content.
- Direct Gemini (`:656-665`): text parts joined (`:715-722`); empty (incl. safety blocks) -> `ValueError` with finishReason (`:658`). Not caught by the Gemini except clauses (`:667-677`), so no in-loop retry.

Trust-game decision path:

- Validator `games/base_game.py:30-53` (not overridden in `trust_game.py` or `trust_game_noisy.py`): requires non-empty content and a quoted role key (`'send'`/`"send"` or `return`) followed by a number. Failure -> `InvalidGameResponseError`.
- On validator failure `agents.py:194-207` rolls back the pending prompt and records the rejected payload with an `error` field in `interaction_history`. `simulation.py:668-680` retries the same prompt once, then the exception propagates; the batch runner records the run as failed (`experiments/run_trust_game_batch.py:209-212`). **No default amount is ever substituted.** The same one-retry pattern applies to the post-game deduction stage (`simulation.py:754-765`).
- Extraction `games/trust_game.py:539-551` uses `re.search` and returns the FIRST `'send': N` / `"send": N` match. `games/trust_game_noisy.py:1440-1467` is the same (`matches[0]`) plus an alternate-key fallback (`:1453-1466`) that is unreachable in the game path because the validator already guarantees the expected key.
- Bounds: `_bounded_amount` clamps silently to `[0, endowment]` for sends and `[0, received]` for returns (`trust_game.py:534-537`, noisy `:1436-1438`). The noisy game records a `clamped` flag (`:1020-1049`); the plain game does not.
- Regex mismatch: validator allows whitespace before the colon (`base_game.py:46-49`); extractor requires the colon right after the closing quote (`trust_game.py:547`). A reply like `"send" : 5` passes validation and then raises uncaught in `process_intermediate_response` (`trust_game.py:394`), killing the run.

Myth path:

- `validate_myth_response` (`src/myth_writer.py:50-75`) rejects empty content, decision-only content, or content matching >= 2 game-prompt markers. `simulation.py:876-905` retries up to 2 times with a corrective suffix (`myth_writer.py:115-131`). Myth text is otherwise stored raw. Same for every provider.

## 6. Retry logic

| Route | In `call_llm` (3 attempts, backoff 2^n + jitter) | SDK-internal retries | Simulation-level |
|---|---|---|---|
| OpenAI-compatible | 429, connection error, HTTP >= 500 (`:481-509`); 4xx raise immediately (`:508-509`); empty content not retried | openai 1.37.1 `DEFAULT_MAX_RETRIES=2`, 600 s read timeout (verified from installed package) | game 1 retry (`simulation.py:668-680`), deduction 1 (`:754-765`), myth 2 (`:880-905`) |
| Direct Anthropic | RateLimitError, APIConnectionError, APITimeoutError, >= 500, empty response (`:582-613`) | anthropic 0.75.0 `DEFAULT_MAX_RETRIES=2`, 600 s | same |
| Direct Gemini | HTTP 408/409/429/>= 500, URLError, TimeoutError (`:667-684`, `:748-749`); empty not retried | none (raw urllib), 120 s default timeout | same |

## 7. What `run_metadata` records

`llm_runtime_metadata` (`src/utils.py:102-166`), merged in `src/simulation.py:440-461`, since commit 38fa31aa (2026-08-25):

- All routes: `llm_provider`, `provider_model`, `llm_provider_mode`, `max_output_tokens`, `max_output_tokens_source`.
- Gemini only: `thinking_level`, `thinking_level_source`, `temperature_sent`, `request_timeout_seconds`, `request_timeout_source`.
- NOT recorded: whether the OpenRouter `reasoning.effort` was sent and at what value; the direct-OpenAI `reasoning_effort`; whether temperature was sent on non-Gemini routes; `OPENROUTER_MAX_TOKENS` is recorded only as `max_output_tokens`.
- Per-response `reasoning` and `usage` (`input_tokens`, `output_tokens`, `reasoning_tokens`) are stored in `conversation_history.*_responses` and in each agent's `interaction_history` (`agents.py:55-80`, `simulation.py:684-691`). These are the only provenance signal for pre-2026-08-25 runs.

Observed signatures across saved runs (first LLM response per run; month = file mtime, which may be the HF sync date rather than the run date):

| Model slug | Reasoning text or tokens present | Neither present | Provider fields present |
|---|---|---|---|
| anthropic/claude-sonnet-4.5 | 645 | 726 | 31 (24 openrouter, 7 anthropic direct) |
| openai/gpt-5-nano | 659 | 2264 | 0 |
| google/gemini-3.1-pro-preview | 218 with text, 271 tokens-only | 0 | 0 |
| google/gemini-3-pro-preview | 110 | 0 | 0 |
| openai/gpt-5.5 | 92 | 17 | 0 |

Reading: the only code path that yields no reasoning text and zero reasoning tokens for Claude is direct Anthropic (`:577`, `:572`); for GPT-5 Nano it is direct OpenAI at `minimal` (or a vendor returning zero reasoning tokens, which I cannot rule out). Gemini "tokens-only" matches the direct path (`:663`, `:744`); "text" matches OpenRouter with effort medium.

## Ranked asymmetries that could plausibly produce cross-model behavioural differences

1. **Reasoning regime differs by route, and both regimes exist in the data for every model.**
   Claude via OpenRouter gets extended thinking at effort medium (`utils.py:396-406`); Claude direct gets none (`:552-560`). GPT-5 Nano direct runs at `minimal` (`:531`); via OpenRouter it runs at the vendor default with no param (`:396-401`). Gemini via OpenRouter gets effort medium; direct gets `GEMINI_THINKING_LEVEL` or the vendor default (`:633-635`). The signature table above shows the split within each model.
   Test: split runs by reasoning signature (reasoning text or `reasoning_tokens > 0` vs neither) and compare send/return ratios within model. Going forward, set `OPENROUTER_REASONING_EFFORT` and `OPENAI_REASONING_EFFORT` explicitly and add them to `llm_runtime_metadata`.

2. **GPT-5 Nano never runs at temperature 0.8; Gemini 3.7 Flash direct does not either.**
   Direct OpenAI omits it (`:521-523`). OpenRouter sends it (`:377`) although the code's own comment says the GPT-5 family rejects a non-default temperature; those runs completed, so OpenRouter presumably drops it (unverifiable from the repo). Gemini 3.7 Flash direct omits it (`:695`). `run_metadata.temperature = 0.8` is misleading for both.
   Test: one OpenRouter request for gpt-5-nano with temperature 0.8 vs 1.0 and inspect the generation record on the OpenRouter dashboard; or compare decision variance across replicates between GPT-5 Nano and Claude.

3. **Output cap only on direct Claude, and truncation is never detected.**
   1024 default, 4096 in this `.env` (`:547`); unbounded on OpenRouter, direct OpenAI, Gemini. No path reads `finish_reason`/`stop_reason`, so a truncated reply surfaces as a validator failure and kills the run (`docs/verified-facts.md:9` records two runs killed this way). Survivorship follows: if long deliberation correlates with a behavioural state (e.g. weighing defection), the surviving Claude runs are a biased sample.
   Test: count failed runs per model per batch (batch summaries, leftover `.checkpoint.json`); count `interaction_history` entries with an `error` field per model (`agents.py:200-207`).

4. **Parse failure is loud, not silent, but selection still differs by model.**
   The one game retry plus run death (`simulation.py:668-680`, batch `:209-212`) means a model with a higher malformed-JSON rate loses more runs. Combined with item 3 this is the real "parse-failure default" channel: not a substituted value, but a filtered sample. The HF sync excludes failed/partial runs (`CLAUDE.md`, "Sharing completed runs").
   Test: per-model validator-rejection counts from `interaction_history`; compare partial-checkpoint decisions of failed runs with completed ones.

5. **First-match extraction.**
   The parsed decision is the first `'send': N` in the content, not the final JSON (`trust_game.py:548`, noisy `:1451`). A model that narrates alternatives in prose before its answer gets the wrong number recorded.
   Test: for each response, count distinct values matching the role key; report the per-model share with more than one value and whether the first differs from the last.

6. **Silent clamping.**
   Out-of-range amounts are clipped without error (`trust_game.py:534-537`, noisy `:1436-1438`). A trustee returning more than received, or a negative send, is clamped. Only the noisy game records `clamped` (`:1020-1049`).
   Test: per-model `clamped` counts in noisy runs; for plain runs, regex the raw content and compare with the recorded amount.

7. **Gemini 3 Pro alias.**
   Direct runs under `google/gemini-3-pro-preview` call `gemini-3.1-pro-preview` (`:48`); OpenRouter runs call the real 3-pro slug. The 110 saved runs under that slug predate provenance fields.
   Test: check `provider_model` in any post-2026-08-25 run; for older runs treat the model identity as unknown.

8. **Empty-response handling differs.**
   Direct Anthropic retries empty content up to 3 times in-loop (`:604-613`); OpenAI-compatible (`:410-411` -> `:511-513`) and Gemini (`:656-658`, outside `:667-677`) re-raise at once. Each then gets one simulation-level retry. Affects failure rates, not the decision values.
   Test: count "Empty response" errors per model in `.log` files and `interaction_history`.

9. **Retry depth and timeouts.**
   OpenAI and Anthropic SDKs add 2 silent retries under the manual loop (verified: `DEFAULT_MAX_RETRIES=2` in openai 1.37.1 and anthropic 0.75.0); Gemini uses raw urllib with no SDK layer and a 120 s default timeout (`:698-701`) against 600 s for the SDKs. Long Gemini thinking is more likely to time out; Aron's env raises it to 300 s. Minor.
   Test: count Gemini timeout retries in logs.

10. **Validator/extractor regex mismatch.**
    `"send" : 5` passes `base_game.py:46-49` and then crashes uncaught at `trust_game.py:394`. Rare; the run dies rather than misparses.
    Test: grep response contents for `"(send|return)"\s+:` per model.

Not an asymmetry: message roles, system-prompt placement, seed injection and memory truncation are identical across providers (`utils.py:270-316`, `agents.py:82-87`, `simulation.py:420-431`). The monitor (`src/monitor.py:79-85`) and the judge scripts use the same `call_llm` and inherit the same routing.

## Unverifiable from the repo

- OpenAI's default reasoning effort for gpt-5-nano when no `reasoning` param is sent via OpenRouter.
- Whether OpenRouter drops or forwards `temperature` for GPT-5 models.
- How OpenRouter maps `effort: medium` to an Anthropic thinking budget, and whether it forces temperature 1.0 when thinking is on.
- Gemini's vendor-default thinking level and max output tokens; OpenRouter's default max tokens.
- Which provider Aron's machine uses for Claude and GPT (no metadata before 2026-08-25; key presence on that machine not visible here).
- File mtimes used for the per-month split may be Hugging Face sync dates, not run dates.
- Whether zero reasoning tokens for GPT-5 Nano proves the direct `minimal` path or a vendor reporting quirk.

## Stale doc line (left untouched, read-only brief)

`docs/verified-facts.md:9` cites `src/utils.py:478` for the 1024 default; it is now at line 547.

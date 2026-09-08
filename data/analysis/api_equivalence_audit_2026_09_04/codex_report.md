# Independent API-equivalence audit

## Headline

**No—only partially for early runs.** Before 2026-04-29 the simulator hard-wired every model through OpenRouter, but even then it enabled medium OpenRouter reasoning for Claude/Gemini slugs while excluding `openai/*`. Current `auto` mode instead prefers direct OpenAI, Anthropic, or Google whenever the matching key exists. The August cross-model runs explicitly record three direct providers with different temperature, token, and thinking settings. [src/utils.py:169–222](src/utils.py:169) [src/utils.py:388–406](src/utils.py:388)

The initial application-level role list is shared, but the wire payloads and the histories subsequently shown to each model are not equivalent.

## Findings, ordered by likely explanatory importance

1. **The relevant GPT/Claude/Gemini runs used different providers and inference settings.**

   The six `negative_only_crossmodel_*_n5` experiment sets contain 90 completed full-state files per model. Their metadata records direct Anthropic, direct OpenAI, and direct Google—not OpenRouter:

   | Model | Recorded provider/model | Temperature | Output limit | Reasoning/thinking |
   |---|---|---|---|---|
   | Claude Sonnet 4.5 | Anthropic / `claude-sonnet-4-5-20250929`; 89 files say mode `direct`, one says `auto` but still resolved to Anthropic | `0.8` | `4096` from `ANTHROPIC_MAX_TOKENS` | Setting not recorded; usage reports zero reasoning tokens |
   | GPT-5 Nano | OpenAI / `gpt-5-nano`; mode `direct` | Metadata says `0.8`, but does not record whether it was sent | Provider default | Setting not recorded; usage reports zero reasoning tokens |
   | Gemini 3.7 Flash | Google / `gemini-3.7-flash`; mode `direct` | Metadata explicitly says `temperature_sent: false` | Provider default | `thinking_level: medium` |

   Evidence: [Claude metadata:9267–9290](data/shared_runs/uploaders/vallinder/data/json/noise_experiments/negative_only_crossmodel_defectors_n5_20260825/negative_only_crossmodel_population_game_myth_n5/claude-sonnet-4.5/game_myth/noisy8_crossmodel_negative_defectors25_twotask_r3/negative_only_crossmodel_population_game_myth_n5_005_neutral_rep00_memtest_memory_primary_anything.json:9267), [GPT metadata:9267–9290](data/shared_runs/uploaders/vallinder/data/json/noise_experiments/negative_only_crossmodel_defectors_n5_20260825/negative_only_crossmodel_population_game_myth_n5/gpt-5-nano/game_myth/noisy8_crossmodel_negative_defectors25_twotask_r3/negative_only_crossmodel_population_game_myth_n5_022_neutral_rep02_memtest_memory_primary_anything.json:9267), [Gemini metadata:9267–9295](data/shared_runs/uploaders/vallinder/data/json/noise_experiments/negative_only_crossmodel_defectors_n5_20260825/negative_only_crossmodel_population_game_myth_n5/gemini-3.7-flash/game_myth/noisy8_crossmodel_negative_defectors25_twotask_r3/negative_only_crossmodel_population_game_myth_n5_038_neutral_rep03_memtest_memory_primary_anything.json:9267), [Claude `auto` outlier:1934–1952](data/shared_runs/uploaders/vallinder/data/json/noise_experiments/negative_only_crossmodel_defectors_n5_20260825/negative_only_crossmodel_dyad_game_n5/claude-sonnet-4.5/game/noisy2_crossmodel_negative_random50_game_r3/negative_only_crossmodel_dyad_game_n5_012_neutral_rep02.json:1934).

   The logs reinforce the reasoning asymmetry: 5,564 of 6,378 Gemini usage records had non-zero thought tokens, with a maximum of 6,717; all 6,471 GPT and 6,396 Claude usage records reported zero. Examples: [Gemini:73](data/shared_runs/uploaders/vallinder/data/json/noise_experiments/negative_only_crossmodel_defectors_n5_20260825/negative_only_crossmodel_population_myth_game_n5/gemini-3.7-flash/myth_game/noisy8_crossmodel_negative_defectors50_twotask_r3/negative_only_crossmodel_population_myth_game_n5_043_neutral_rep03_memtest_memory_primary_anything.log:73), [GPT:73](data/shared_runs/uploaders/vallinder/data/json/noise_experiments/negative_only_crossmodel_defectors_n5_20260825/negative_only_crossmodel_population_myth_game_n5/gpt-5-nano/myth_game/noisy8_crossmodel_negative_defectors50_twotask_r3/negative_only_crossmodel_population_myth_game_n5_025_neutral_rep00_memtest_memory_primary_anything.log:73), [Claude:77](data/shared_runs/uploaders/vallinder/data/json/noise_experiments/negative_only_crossmodel_defectors_n5_20260825/negative_only_crossmodel_population_myth_game_n5/claude-sonnet-4.5/myth_game/noisy8_crossmodel_negative_defectors50_twotask_r3/negative_only_crossmodel_population_myth_game_n5_012_neutral_rep02_memtest_memory_primary_anything.log:77).

2. **Claude’s response format creates a systematic chat-memory confound.**

   In the August comparison, 3,301 of 4,500 accepted Claude game responses contained explanatory prose around the decision. All 4,500 GPT and all 4,500 Gemini accepted game responses were decision-only JSON or fenced JSON. A typical Claude response contains several paragraphs of strategic reasoning followed by `{"send": 3}`. [Claude response:144](data/shared_runs/uploaders/vallinder/data/json/noise_experiments/negative_only_crossmodel_defectors_n5_20260825/negative_only_crossmodel_dyad_game_myth_n5/claude-sonnet-4.5/game_myth/noisy2_crossmodel_negative_random25_twotask_r3/negative_only_crossmodel_dyad_game_myth_n5_005_neutral_rep00_memtest_memory_primary_anything.json:144)

   This happens because validation only searches for a quoted `send` or `return` key anywhere in the response; it does not require the response to be JSON-only. [games/base_game.py:30–53](games/base_game.py:30) The entire accepted response—not the extracted number—is then appended as the next assistant message. [src/agents.py:209–216](src/agents.py:209)

   These runs use `chat_memory_mode: memory_primary`, under which game responses remain in memory. [Claude run:2385](data/shared_runs/uploaders/vallinder/data/json/noise_experiments/negative_only_crossmodel_defectors_n5_20260825/negative_only_crossmodel_dyad_game_myth_n5/claude-sonnet-4.5/game_myth/noisy2_crossmodel_negative_random25_twotask_r3/negative_only_crossmodel_dyad_game_myth_n5_005_neutral_rep00_memtest_memory_primary_anything.json:2385) [src/simulation.py:634–638](src/simulation.py:634)

   Therefore Claude repeatedly sees its prior strategic rationales, while GPT and Gemini mainly see their prior numeric decisions. That is a concrete format-driven treatment difference. The repo does not isolate its causal effect on collective returns.

3. **There is model-dependent format failure and resampling, but no silent default.**

   In the August cross-model logs:

   | Signal | Claude | GPT-5 Nano | Gemini 3.7 |
   |---|---:|---:|---:|
   | Invalid game decisions | 17 events in 14 logs; all were missing/malformed sender decisions | 0 | 0 |
   | Invalid myth responses | 0 | 93 events in 39 logs; all first correction attempts succeeded | 0 |
   | Transport-level game retry | 0 observed | 0 observed | 3 `RemoteDisconnected` events |
   | Provider-internal retry | 0 observed | 0 observed | 2: one connection retry, one HTTP 503 |
   | Final actions clamped | 0 / 4,500 | 0 / 4,500 | 0 / 4,500 |

   Examples: [Claude invalid sender:819](data/shared_runs/uploaders/vallinder/data/json/noise_experiments/negative_only_crossmodel_defectors_n5_20260825/negative_only_crossmodel_dyad_game_n5/claude-sonnet-4.5/game/noisy2_crossmodel_negative_random25_game_r3/negative_only_crossmodel_dyad_game_n5_005_neutral_rep00.log:819), [GPT myth rejection:2172](data/shared_runs/uploaders/vallinder/data/json/noise_experiments/negative_only_crossmodel_defectors_n5_20260825/negative_only_crossmodel_population_myth_game_n5/gpt-5-nano/myth_game/noisy8_crossmodel_negative_defectors50_twotask_r3/negative_only_crossmodel_population_myth_game_n5_025_neutral_rep00_memtest_memory_primary_anything.log:2172), [Gemini disconnect:575](data/shared_runs/uploaders/vallinder/data/json/noise_experiments/negative_only_crossmodel_defectors_n5_20260825/negative_only_crossmodel_dyad_game_n5/gemini-3.7-flash/game/noisy2_crossmodel_negative_random25_game_r3/negative_only_crossmodel_dyad_game_n5_037_neutral_rep02.log:575), [Gemini 503:259](data/shared_runs/uploaders/vallinder/data/json/noise_experiments/negative_only_crossmodel_defectors_n5_20260825/negative_only_crossmodel_dyad_myth_game_n5/gemini-3.7-flash/myth_game/noisy2_crossmodel_negative_random50_twotask_r3/negative_only_crossmodel_dyad_myth_game_n5_042_neutral_rep02_memtest_memory_primary_anything.log:259).

   Rejected responses are recorded for audit but removed from chat memory before retry. [src/agents.py:190–207](src/agents.py:190) A game response is retried once with the same prompt; a myth is retried up to twice with an explicit correction suffix. [src/simulation.py:658–679](src/simulation.py:658) [src/simulation.py:870–906](src/simulation.py:870) The correction suffix is itself part of GPT’s accepted interaction history. [src/myth_writer.py:115–129](src/myth_writer.py:115)

   No game response is parsed with `json.loads`; both trust-game implementations use a numeric regular expression and raise on failure. [games/trust_game.py:539–551](games/trust_game.py:539) [games/trust_game_noisy.py:1440–1467](games/trust_game_noisy.py:1440) Out-of-range numbers are clamped, not defaulted to zero. [games/trust_game_noisy.py:1435–1438](games/trust_game_noisy.py:1435)

   If the retry also fails, the simulation raises and writes results/error state rather than manufacturing an action. [src/simulation.py:992–998](src/simulation.py:992)

4. **The recent Gemini ceiling-lock is not accompanied by a numeric-format failure.**

   All 4,500 accepted Gemini actions contained exactly one expected key; none was clamped, empty, or retried for parsing. The same was true of accepted GPT actions. Claude’s accepted actions also each contained exactly one expected key despite the surrounding prose. The action extractor therefore did not select an earlier tentative value in this series. The extractor always uses the first expected-key match. [games/trust_game_noisy.py:1446–1450](games/trust_game_noisy.py:1446)

   This rules out silent parse defaults and multiple-decision extraction as the direct cause of Gemini 3.7’s ceiling-locking in these files. It does not rule out the provider, temperature, or medium-thinking differences above.

5. **There is no positive evidence of token truncation in the relevant logs, but the logs cannot conclusively rule it out.**

   The largest recorded output was 677 tokens for Claude, 375 for GPT, and 267 for Gemini; no Claude output reached its 4,096-token cap. The August logs contained no empty-content or reasoning-only markers.

   However, `finish_reason`, Anthropic `stop_reason`, and Gemini `finishReason` are discarded from successful responses. The logger retains only content, reasoning text, and usage. [src/utils.py:475–479](src/utils.py:475) [src/utils.py:575–579](src/utils.py:575) [src/utils.py:660–665](src/utils.py:660) [src/agents.py:37–50](src/agents.py:37)

   Across all 6,698 GPT/Gemini/Claude log artifacts in the two requested trees, I found four Claude empty-response errors, one older Gemini Flash-Lite empty-response error, and zero GPT empties. Examples: [Claude empty:34](data/json/noise_experiments/phase5_seeded/phase3_seeded_s_end_plus_jab_phase3_8agent_anon_neg5_myth_only/claude-sonnet-4.5/game/default/phase3_seeded_s_end_plus_jab_000_neutral_rep00_myth_game_directive_anything.log:34), [Gemini Flash-Lite empty:9156](data/json/gemini31_flashlite_8agent_myth_directive_history3_r10_n5/gemini-3.1-flash-lite/myth_game/gemini31_flashlite_8agent_myth_directive_history3_r10_n5_001_neutral_rep01_myth_game_directive_anything.log:9156).

## End-to-end request trace

The config maps friendly keys to OpenRouter-style slugs such as `openai/gpt-5-nano`, `anthropic/claude-sonnet-4.5`, and `google/gemini-3.7-flash`. [config/experiments.yaml:8–27](config/experiments.yaml:8) `ExperimentConfig` resolves the selected key to that slug, and the runners normally supply temperature `0.8`. [src/experiment_config.py:105–107](src/experiment_config.py:105) [experiments/run_noisy_batch.py:525–535](experiments/run_noisy_batch.py:525)

`run_simulation` creates one client from the slug, records partial runtime metadata, builds a system message, and shares the client across agents. [src/simulation.py:379–380](src/simulation.py:379) [src/simulation.py:408–434](src/simulation.py:408)

### Routing modes

- `openrouter`, `openai`, `anthropic`, and `google`/`gemini` force that provider without validating that it matches the slug. [src/utils.py:187–194](src/utils.py:187)
- `direct` selects OpenAI, Anthropic, or Google from the slug prefix and rejects unsupported prefixes. [src/utils.py:196–206](src/utils.py:196)
- `auto` prefers the matching direct key, then falls back to OpenRouter. [src/utils.py:208–221](src/utils.py:208)

OpenRouter leaves the slug unchanged. Direct routing first checks `LLM_DIRECT_MODEL_<NORMALIZED_SLUG>`, then `DIRECT_MODEL_ALIASES`, then strips the selected provider prefix. [src/utils.py:78–99](src/utils.py:78) Notably, direct `google/gemini-3-pro-preview` is aliased to `gemini-3.1-pro-preview`; the two labels are not the same direct model. [src/utils.py:45–50](src/utils.py:45)

### Current provider payloads

| Provider | System and roles | Temperature | Max output | Reasoning/thinking | Successful parse | Retry |
|---|---|---|---|---|---|---|
| OpenRouter | Keeps `system`, `user`, `assistant`; drops every field except `role` and `content`; no role merging | Sent | `max_tokens` only if `OPENROUTER_MAX_TOKENS` was present at module import | Environment override or call default `medium`; omitted for `openai/*` and `meta-llama/*` | Requires first choice’s content; then extracts optional reasoning fields | Rate limit, connection, and 5xx only |
| Direct OpenAI | Same role sanitization | Omitted for `gpt-5*`; sent otherwise | Never set | `OPENAI_REASONING_EFFORT`, default `minimal`, for GPT-5 | Same OpenAI-compatible parser | Same as OpenRouter |
| Direct Anthropic | Joins all system messages with blank lines into top-level `system`; keeps unmerged `user`/`assistant` messages | Sent except Opus 4.7/4.8 | `ANTHROPIC_MAX_TOKENS`, default `1024` | None configured | Joins all text blocks; discards non-text blocks | Rate limit, connection, timeout, 5xx, and empty text |
| Direct Google | Joins system messages into `system_instruction`; renames `assistant` to `model`; wraps text in `parts`; no role merging | Omitted only for `gemini-3.7-flash` | Never set | Optional `GEMINI_THINKING_LEVEL` under `thinkingConfig` | Joins text from every part of every candidate; returns reasoning as `None`, but records thought-token usage | HTTP 408/409/429/5xx and URL/timeout; an empty result is not caught by the provider retry loop |

Evidence: [role adapters, src/utils.py:270–316](src/utils.py:270), [OpenAI/OpenRouter request, src/utils.py:362–408](src/utils.py:362), [OpenAI temperature/reasoning, src/utils.py:518–531](src/utils.py:518), [Anthropic request, src/utils.py:541–613](src/utils.py:541), [Gemini request, src/utils.py:616–686](src/utils.py:616).

`OPENROUTER_MAX_TOKENS` and `OPENROUTER_REASONING_EFFORT` are read once at import, whereas the direct-provider reasoning/thinking/token helpers reread their environment variables at request time. [src/utils.py:20–27](src/utils.py:20) [src/utils.py:530–531](src/utils.py:530) [src/utils.py:547–548](src/utils.py:547) [src/utils.py:633–635](src/utils.py:633)

## Saved-run provider coverage

I found 13,681 JSON artifacts in the requested trees; two non-run summary tables were malformed JSON. Of 6,678 completed plain full-state files, only 300 contain the standardized provider fields:

| Experiment set | Completed files | Recorded provider/settings |
|---|---:|---|
| Six August `negative_only_crossmodel_*_n5` sets | 270: 15 per set and model | Direct Anthropic/OpenAI/Google as detailed above |
| `noise2i_washout_game_myth` | 10 file versions | Claude through OpenRouter; temperature `0.8`, provider-default max |
| `noise2i_washout_myth_game` | 10 file versions | Claude through OpenRouter; temperature `0.8`, provider-default max |
| `noise8i_washout_game_myth` | 5 | Direct Anthropic selected by `auto`; temperature `0.8`, max `4096` |
| `noise8i_washout_myth_game` | 5 | Mixed: three OpenRouter, two direct Anthropic |
| All other completed full-state files | 6,378 | No standardized `llm_provider`, `provider_model`, `llm_provider_mode`, max-token, or reasoning metadata |

Washout evidence: [OpenRouter run:4344–4361](data/json/noise_experiments/washout_20round/noise2i_washout_game_myth/claude-sonnet-4.5/game_myth/noisy_bidirectional_informed_memprimary_twotask_r3_r20/noise2i_washout_game_myth_000_neutral_rep00_memtest_memory_primary_anything.json:4344), [direct Anthropic run:17214–17237](data/json/noise_experiments/washout_20round/noise8i_washout_game_myth/claude-sonnet-4.5/game_myth/noisy8_bidirectional_informed_memprimary_twotask_r3_r20/noise8i_washout_game_myth_000_neutral_rep00_memtest_memory_primary_anything.json:17214), [older metadata gap:734–739](data/json/baseline/gpt-5-nano/game/myth_topics_gpt5_stable_000_gpt-5-nano_neutral_game_6.json:734).

The baseline-match ablation is a partial exception: its copied artifacts record `provider_env: direct` and `openai_reasoning_effort_env: low`, but lack the standardized resolved-provider fields. [old_prompt_old_runner_15:750–767](data/json/baseline_match_ablation/direct/old_prompt_old_runner_15/gpt-5-nano/game/default/old_prompt_old_runner_15_001_neutral.json:750)

## Git history and run-date boundary

`git blame` attributes direct OpenAI/Anthropic routing to Aron Vallinder in commit `bf90f96797d95da5ec0c60a7bf28824bfa35781b`, dated 2026-04-29 10:56:31 CEST. [src/utils.py:169–222](src/utils.py:169) Direct Gemini routing followed in Aron Vallinder’s `1374148baac5ab26f170fc3d04b737e00211e23e`, dated 2026-04-29 22:42:22 CEST. [src/utils.py:30–50](src/utils.py:30)

Immediately before `bf90f967`, `src/simulation.py:125–129` required `OPENROUTER_API_KEY` and constructed an OpenAI client with `base_url=https://openrouter.ai/api/v1`; therefore runs dated 2026-02-10, 03-19, 03-31, 04-21, 04-22, 04-23, and 04-25 necessarily predate direct routing. Representative timestamps: [02-10:15](data/shared_runs/uploaders/ivarfresh/data/json/baseline/gemini-3-pro-preview/game_myth/trickster_myth_topic/10runs_model_comparison_011_neutral_trickster_betrayal_and_price_8.log:15), [03-19:17](data/json/noise_experiments/v1/noise_bidirectional_mem3/gemini-3-pro-preview/game_myth/noisy_bidirectional_informed/noise_bidirectional_mem3_030_neutral_anything.log:17), [03-31:17](data/json/noise_experiments/v2_uniform_distribution_noise/noise_negative_mem3/gemini-3.1-pro-preview/game_myth/noisy_negative_5_informed/noise_negative_mem3_034_neutral_anything.log:17), [04-21:17](data/json/noise_experiments/v2_uniform_distribution_noise/noise_negative_mem3_gpt5_nano/gpt-5-nano/game/noisy_negative_5_informed/noise_negative_mem3_gpt5_nano_021_neutral.log:17), [04-22:17](data/json/noise_experiments/v3_deterministic_noise/noise_deterministic_max_mem3_gpt5_nano/gpt-5-nano/game_myth/noisy_deterministic_max/noise_deterministic_max_mem3_gpt5_nano_036_neutral_anything.log:17), [04-23:17](data/json/noise_experiments/v2_uniform_distribution_noise/noise_negative_mem3_gpt5_nano/gpt-5-nano/game_myth/noisy_negative_5_informed/noise_negative_mem3_gpt5_nano_029_neutral_anything.log:17), [04-25:15](data/shared_runs/uploaders/ivarfresh/data/json/baseline/gpt-5-nano/game/baseline_topup_n5_game_012_neutral.log:15).

Even those all-OpenRouter runs were not parameter-identical: the historical caller added medium reasoning to non-OpenAI/non-Llama slugs but excluded `openai/*` (`bf90f967^:src/utils.py:45–53`).

The first direct GPT pilot started at 11:19:59, after the 11:16 GPT-temperature fix but before the 12:13 minimal-reasoning commit; seven pilot logs started in that interval. [pilot log:17](data/json/noise_experiments/v4_direct_provider_pilot/noise_pilot/gpt-5-nano/game/noisy_bidirectional/noise_pilot_000_neutral.log:17) Current blame attributes temperature omission to `b42d84c2` and minimal reasoning to `83654c208`. [src/utils.py:518–531](src/utils.py:518)

## What could not be verified

- The August files record code commit `58d15e…`, but that object is absent from the local Git object database. I could therefore verify provider/settings metadata and logs, but not reconstruct that exact historical source revision. [GPT metadata:9291–9295](data/shared_runs/uploaders/vallinder/data/json/noise_experiments/negative_only_crossmodel_defectors_n5_20260825/negative_only_crossmodel_population_game_myth_n5/gpt-5-nano/game_myth/noisy8_crossmodel_negative_defectors25_twotask_r3/negative_only_crossmodel_population_game_myth_n5_022_neutral_rep02_memtest_memory_primary_anything.json:9291)
- Saved `messages_sent` are copied before provider transformation, so they are not literal HTTP payloads. [src/agents.py:163–174](src/agents.py:163)
- Successful raw responses and stop/finish reasons are not retained, so `finish_reason=length` cannot be conclusively ruled out.
- For post-2026-04-29 run sets lacking standardized provider metadata, directory names such as `v4_direct_provider` are suggestive but are not sufficient proof of the actual resolved provider.

**Bottom line:** the numeric parser did not silently default or clamp the recent cross-model actions, and Gemini 3.7 shows no associated parse failures. But provider/settings equivalence is decisively false, and Claude’s verbose decisions create a large, persistent message-history difference that should be controlled before treating the behavioral gap as purely model-level.

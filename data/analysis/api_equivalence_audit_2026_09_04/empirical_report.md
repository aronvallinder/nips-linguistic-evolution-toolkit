# API-equivalence audit: what the real runs actually used

Audit date: 2026-09-04. Read-only; nothing in the repo was modified.
Repo: `/Users/ivar/Desktop/Research/AI_projects/LLM_evolution/nips-linguistic-evolution-toolkit`

## Headline

**No.** The cross-model defector set Aron used for the meeting slides did not go through OpenRouter at all. Claude Sonnet 4.5, GPT-5 Nano and Gemini 3.7 Flash each went to their own vendor API directly, with different temperature, reasoning and max-token settings. The older runs (before 2026-08-25) mostly did go through OpenRouter, but with extended thinking switched on for Claude and Gemini and medium reasoning for GPT-5 Nano, so the OpenRouter era and the direct era are not comparable to each other either.

## Files produced

All under `data/analysis/api_equivalence_audit_2026_09_04/`:

| File | Content |
|---|---|
| `inventory.py`, `diagnostics.py` | Helper scripts that produced everything below |
| `runs_inventory.csv` | One row per run JSON (6,678 runs): every `run_metadata` provider field plus per-run diagnostics |
| `runs_inventory_inferred.csv` | Same plus an `inferred_provider` column for runs that predate the metadata code |
| `grouped_by_uploader_expset_model.csv` | Full (uploader, experiment set, model) table, 176 groups |
| `game_responses.csv` | 175,750 individual LLM game decisions: tokens, content length, JSON presence, amount, reasoning kind |
| `interaction_errors.csv` | Every retry recorded in agents' `interaction_history` (114 total) |
| `diag_by_model_provider.csv` | Diagnostics per model x inferred provider, all runs |
| `diag_defector_set.csv` | Diagnostics per model x population size, defector set only |
| `orphan_checkpoints.txt` | 4 checkpoint files with no completed JSON (excluded) |

## 1. What the metadata can and cannot tell us

Provider fields (`llm_provider`, `provider_model`, `llm_provider_mode`, `max_output_tokens`, `max_output_tokens_source`, `thinking_level`, `thinking_level_source`, `temperature_sent`) are written by `llm_runtime_metadata()` in `src/utils.py:102-167` and merged into `run_metadata` in `src/simulation.py:440-465`. That function landed in commit 38fa31aa on 2026-08-25. Direct-provider routing itself is older: commits bf90f967 (OpenAI/Anthropic) and 1374148b (Gemini), both 2026-04-29. So any run after 2026-04-29 could have gone direct, but only runs after 2026-08-25 say so.

Run counts:

| Source | Run JSONs | With provider fields | Experiment sets |
|---|---|---|---|
| `data/json/` (local) | 5,058 | 30 (washout_20round) | 90 |
| `data/shared_runs/uploaders/ivarfresh` | 1,300 | 0 | 52 (mirror of local sets) |
| `data/shared_runs/uploaders/arabella` | 50 | 0 | 5 |
| `data/shared_runs/uploaders/vallinder` | 270 | 270 | 1 (the defector set) |
| Total | 6,678 | 300 | |

Two files under `arabella/data/tables/` failed to parse as JSON (`moral_summaries_GLM-5.2.json`, `myths_with_morals_GLM-5.2.json`); they are analysis tables, not runs. `.checkpoint.json` and `.results.json` duplicates were skipped.

### Inferring the provider for the 6,378 runs without fields

The stored `reasoning` field is diagnostic:

- The direct Anthropic path (`src/utils.py::_call_anthropic`) and the direct Gemini path (`_call_gemini`) always return `"reasoning": None`.
- The OpenRouter path (`_call_openai_compatible`) sends `extra_body.reasoning.effort = "medium"` by default for every model slug not starting with `openai/` or `meta-llama/` (`src/utils.py:386-406`), and stores whatever reasoning text the provider returns. For `openai/` slugs it sends nothing, but OpenRouter still returns GPT-5 reasoning summaries, which the code stores.
- When only a reasoning-token count is available (no text), the code stores the string `"[N reasoning tokens used, but content encrypted by provider]"`. This happens on both the OpenRouter and the direct OpenAI path, so it is not diagnostic by itself.

Rules used:

| Model family | Reasoning text present | No reasoning text |
|---|---|---|
| Claude | OpenRouter with extended thinking on (certain) | Ambiguous: direct Anthropic, or OpenRouter with `OPENROUTER_REASONING_EFFORT=none` |
| Gemini | OpenRouter with thinking (certain) | Direct Gemini if `usage.reasoning_tokens > 0` (`thoughtsTokenCount`), else ambiguous |
| GPT-5 Nano | OpenRouter (certain; direct OpenAI Chat Completions never returns reasoning text) | Direct OpenAI with minimal effort if reasoning tokens = 0, else ambiguous |

Nothing else helps. The `.log` header records `Model: openai/gpt-5-nano`, the repo slug, not the provider. No `finish_reason` or `stop_reason` is stored anywhere. No response model id is stored.

## 2. Grouped inventory

Condensed to the groups that matter. Full 176-row table in `grouped_by_uploader_expset_model.csv`.

### 2a. Runs with provider fields (300 runs)

| Uploader / set | Model | Runs | Provider, provider_model (source) | Mode | Reasoning | Temp sent | Max out tokens |
|---|---|---|---|---|---|---|---|
| vallinder / noise_experiments/negative_only_crossmodel_defectors_n5_20260825 | anthropic/claude-sonnet-4.5 | 90 | anthropic, `claude-sonnet-4-5-20250929` (metadata) | direct (89), auto (1) | none; 0 reasoning tokens on 3,378/3,378 calls | 0.8 | 4096 (`ANTHROPIC_MAX_TOKENS`) |
| same | openai/gpt-5-nano | 90 | openai, `gpt-5-nano` (metadata) | direct | reasoning_tokens = 0 on 3,378/3,378 calls; effort setting not recorded | not sent (code omits for gpt-5*, `src/utils.py:494-499`) | provider default |
| same | google/gemini-3.7-flash | 90 | google, `gemini-3.7-flash` (metadata) | direct | thinking_level = medium (`GEMINI_THINKING_LEVEL`); mean 106 thought tokens, max 1,504; 83.5% of calls > 0 | not sent (`temperature_sent: false`, `src/utils.py:601-608`) | provider default |
| local / noise_experiments/washout_20round | anthropic/claude-sonnet-4.5 | 30 | 7 anthropic direct (8-agent, commit 5546f56e) + 23 openrouter (20 two-agent, 3 eight-agent, commit 9a972c36) (metadata) | auto / openrouter | OpenRouter runs: thinking text on 100% of calls | 0.8 | 4096 / unset |

All 270 defector-set runs share `config_sha256 52091a5b...` and, except one, `code_commit 58d15e24...`. The one `auto`-mode run (`negative_only_crossmodel_dyad_game_n5_012_neutral_rep02.json`, commit c97f59ee) still resolved to direct Anthropic with the same settings. Populations: 45 two-agent runs and 45 eight-agent runs per model, across game / game_myth / myth_game and defector ratios 0 / 0.25 / 0.5.

### 2b. Runs without provider fields (6,378 runs), by inferred provider

| Uploader / sets | Model | Runs | Inferred provider | Reasoning regime | Temp requested | Max out tokens |
|---|---|---|---|---|---|---|
| arabella / 2agent_clean_sonnet45, 2agent_noisy_sonnet45_negative2_informed, 8agent_anonymous_history3_sonnet45, 8agent_named_history3_sonnet45, 8agent_old_prompt_sonnet45 | claude-sonnet-4.5 | 50 | OpenRouter (thinking text on 100% of calls) | extended thinking, effort medium | 0.8 | unset |
| ivarfresh + local / baseline, myth_topics, myth_causal_confirm_*_r10*, myth_causal_neutral_directive_*, myth_causal_normative_{clamped,clean,newprompt,clamped_maxtok4096}_*, noise_experiments/{v1, v2_uniform_distribution_noise, v3_deterministic_noise, neutral_2026_05_27, neutral_2026_05_28, myth_causal_negative*_claude_*, sonnet45_directive_normative_r10_n5}, sonnet45_8agent_game_directive_r10_n5, sonnet45_8agent_game_memprimary_r10_n5, sonnet45_8agent_game_myth_memprimary_r10_n5, sonnet45_8agent_myth_directive_history3{,_anon}_r10_n5, sonnet45_directive_normative_r10_n5, prompt_tests | claude-sonnet-4.5 | ~1,050 (25,260 game calls) | OpenRouter (thinking text on 100% of calls) | extended thinking, effort medium; mean 718 output tokens incl. thinking, max 5,853 | 0.8 | unset |
| ivarfresh + local / ablation_phase1, memtest_{hybrid,memoryprimary,stateless}_*, myth_causal_confirm_claude_fixed_prompt, _topup, myth_causal_screen_claude, myth_prompt_variants_*, noise_experiments/phase2_{baseline,pilot,seeded,smoke}, phase3_{baseline,seeded}, phase4_{baseline,seeded,smoke}, phase5–7_seeded, v4_direct_provider, v4_direct_provider_{baseline,neutral}, phase8_monitored, phase8_smoke, sonnet45_8agent_game_memprimary_mem3_r10_n5, sonnet45_8agent_memprimary_smoke, sonnet45_8agent_myth_directive_history3_anon_memprimary_r10_n5 | claude-sonnet-4.5, claude-haiku-4.5 | ~1,065 (45,292 game calls) | Ambiguous (no reasoning text, 0 reasoning tokens). Likely direct Anthropic: this machine's `.env` has an Anthropic key and no OpenAI/Gemini keys, and `docs/verified-facts.md:11` says auto mode routes `anthropic/*` direct | none | 0.8 | 1024 default before 2026-07-20, 4096 after (`docs/verified-facts.md:9`); not recorded per run |
| ivarfresh + local / baseline, myth_topics, noise_experiments/{v1, v2_uniform_distribution_noise, v3_deterministic_noise}, gpt5nano_8agent_myth_directive_history3_anon_r10_n5, prompt_tests | gpt-5-nano | ~775 (18,764 game calls) | OpenRouter (reasoning summaries on 91% of calls, encrypted-count on 7%) | median 1,024 reasoning tokens per decision (OpenAI default effort) | 0.8 requested; whether OpenRouter passed it is unknown | unset |
| local / baseline_match_ablation, noise_experiments/v4_direct_provider_pilot | gpt-5-nano | 132 (6,060 calls) | Ambiguous (encrypted-count only, reasoning tokens > 0 on 98%) | reasoning on, ~260–1,700 tokens | | |
| local / noise_experiments/v4_direct_provider, v4_direct_provider_{A1A3_combined, A1_adversarial_bootstrap, A1_no_noise, A1_partner_myth, A1_targeted_bootstrap, A3_forced_reasoning, baseline, controls, controls_smoke, neutral, pilot_minimal, prompt_variants, shared_context, shared_context_pilot, targeted_bootstrap, targeted_gpt5nano, targeted_k1_gpt5nano, targeted_k2_gpt5nano, targeted_neutral_gpt5nano}, v4_smoke_test | gpt-5-nano | ~2,200 (44,120 calls) | Direct OpenAI (per `docs/v4_next_runs.md`, `scripts/run_overnight_2026-05-03*.sh`: `LLM_PROVIDER=direct`); reasoning tokens = 0 on 100% of calls | minimal (0 reasoning tokens). Note `run_overnight_2026-05-03_missing.sh:65` set `OPENAI_REASONING_EFFORT=low`, yet the data show 0 reasoning tokens throughout | not sent | provider default |
| local / noise_experiments/v4_direct_provider, v4_direct_provider_gpt5_5_probe | gpt-5.5 | 109 | Ambiguous (encrypted-count on 35% of calls) | reasoning on part of the time | not sent | provider default |
| ivarfresh + local / baseline, noise_experiments/v1 | gemini-3-pro-preview | 106 (5,240 calls) | OpenRouter (thought text on 82%, encrypted-count on 18%) | ~200 thought tokens mean | 0.8 | unset |
| ivarfresh + local / baseline, noise_experiments/{v2_uniform_distribution_noise, v3_deterministic_noise} | gemini-3.1-pro-preview | 224 (6,320 calls) | OpenRouter (thought text on 96%) | 186 thought tokens mean | 0.8 | unset |
| local / noise_experiments/v4_direct_provider | gemini-3.1-pro-preview | 270 (5,400 calls) | Direct Gemini (no text, `thoughtsTokenCount` > 0 on 100%) | 357 thought tokens mean, max 6,179; no `GEMINI_THINKING_LEVEL` recorded | 0.8 | provider default |
| ivarfresh + local / gemini31_flashlite_*, myth_causal_normative_clamped_gemini31_flashlite_r10_n5, noise_experiments/{v2, gemini31_flashlite_8agent_noise_r10_smoke} | gemini-3.1-flash-lite | ~160 (4,540 calls) | OpenRouter (thought text on 42%, encrypted-count on 58%); 1–2 runs in the clamped set look direct | ~250 thought tokens mean | 0.8 | unset |

### 2c. Conditions that mix providers

Within one experiment set and model:

| Set | Model | Split | Evidence |
|---|---|---|---|
| noise_experiments/washout_20round | claude-sonnet-4.5 | 8-agent: 7 direct Anthropic (no thinking, cap 4096) vs 3 OpenRouter (thinking on, no cap); 2-agent: all 20 OpenRouter | metadata |
| noise_experiments/v2 | claude-sonnet-4.5 | 20 of 80 runs with thinking text, 60 without | reasoning field |
| myth_causal_normative_clamped_gemini31_flashlite_r10_n5 | gemini-3.1-flash-lite | 18–19 OpenRouter, 1–2 direct | reasoning field |

Across sets that are compared with each other:

| Comparison | Regime A | Regime B | Corroboration |
|---|---|---|---|
| 8-agent memory-primary triplet | `sonnet45_8agent_game_memprimary_r10_n5`, `sonnet45_8agent_game_myth_memprimary_r10_n5`: OpenRouter, thinking on | `sonnet45_8agent_game_memprimary_mem3_r10_n5`: direct, no thinking | `researchlog.md:1085` ("reran via LLM_PROVIDER=openrouter"), `researchlog.md:1043` (direct, `ANTHROPIC_MAX_TOKENS`) |
| GPT-5 Nano across eras | baseline / v1 / v2_uniform / v3 / myth_topics: OpenRouter, ~1,000 reasoning tokens per call | v4_direct_provider* and defector set: direct, 0 reasoning tokens | reasoning field, `docs/v4_next_runs.md` |
| Claude across eras | Arabella's sets and Ivar's baseline / v1 / v2_uniform / v3 / myth_causal / sonnet45_8agent sets: OpenRouter, thinking on | defector set, v4, phase2–7, memtest: direct, no thinking | reasoning field, metadata |

## 3. Response-quality diagnostics

### 3a. Defector set (the slide data), LLM calls only

Forced defector moves (`response_source: "scripted"`) are excluded. Each model: 90 runs, 3,378 LLM game decisions, 3,000 myth calls.

| Metric | Claude Sonnet 4.5 (direct Anthropic) | GPT-5 Nano (direct OpenAI) | Gemini 3.7 Flash (direct Google) |
|---|---|---|---|
| Mean visible content length, chars (2-agent / 8-agent) | 1,001 / 1,249 | 13 / 13 | 23 / 26 |
| Mean output tokens (max) | 282 / 361 (677) | 15.8 (20) | 11.4 / 12.7 (18) |
| Mean hidden reasoning tokens (max) | 0 (0) | 0 (0) | 106 (1,504); 83.5% of calls > 0 |
| Responses that are bare JSON (start with `{` or a code fence) | 11.5% / 0% | 100% | 100% |
| Empty content | 0 | 0 | 0 |
| Output at max-token cap | 0 of 3,378 (cap 4,096) | n/a, no cap | n/a, no cap |
| Decision rejected by validator and retried (`InvalidGameResponseError`) | 18 (0.53%) in 15 runs | 0 | 0 |
| Myth rejected by validator and retried (`InvalidMythResponseError`) | 0 | 93 (3.1%) in 39 runs | 0 |
| Transport errors retried | 0 | 0 | 3 `RemoteDisconnected` in 3 runs |
| Sends at the maximum ($5), 2-agent / 8-agent | 5.7% / 3.7% | 22.8% / 21.3% | 78.7% / 84.4% |
| Returns of $0, 2-agent / 8-agent | 27.5% / 23.0% | 30.1% / 25.3% | 41.4% / 22.7% |
| Myth length, mean output tokens (max) | 293 (555) | 273 (375) | 234 (267) + 214 thought tokens |

Claude's 18 rejections: 16 were long strategic analyses (300–470 output tokens, well under the cap) that never emitted the JSON line; 2 were role confusion, the sender answered `{"return": 0}`. GPT-5 Nano's 93 rejections all carry the message "Myth response is a game decision rather than a story" (`src/myth_writer.py:60-63`): asked for a myth in a two-task run, it answered with a game JSON. Every rejection was followed by a successful retry (the run completed), and the rejected text is not in the agent's memory (`src/agents.py:190-205` rolls the prompt back).

### 3b. All runs, by model and inferred provider

| Model | Inferred provider | Calls | Runs | Chars mean | Out tokens mean (p95) | Reasoning tokens mean (max) | Reasoning text % | JSON key present % | Bare JSON % | Send=$5 % | Return=$0 % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| claude-sonnet-4.5 | OpenRouter (reasoning text) | 25,260 | 1,052 | 788 | 718 (1,366) | 384 (2,667), often reported as 0 | 100 | 100 | 5.0 | 14.2 | 22.3 |
| claude-sonnet-4.5 | OpenRouter (metadata, washout) | 1,280 | 23 | 1,162 | 925 (1,554) | 0 reported | 100 | 100 | 0 | 57.8 | 0 |
| claude-sonnet-4.5 | direct Anthropic (metadata) | 4,498 | 97 | 1,293 | 395 (631) | 0 | 0 | 100 | 1.7 | 12.7 | 18.0 |
| claude-sonnet-4.5 | ambiguous (no thinking) | 44,260 | 1,040 | 1,009 | 289 (470) | 0 | 0 | 100 | 4.0 | 15.5 | 35.3 |
| claude-haiku-4.5 | ambiguous (no thinking) | 1,032 | 25 | 739 | 178 (337) | 0 | 0 | 100 | 20.3 | 44.4 | 15.5 |
| gpt-5-nano | OpenRouter (reasoning text) | 18,764 | 773 | 13 | 1,127 (2,416) | 1,028 (6,144) | 91 | 100 | 100 | 13.4 | 83.1 |
| gpt-5-nano | ambiguous (encrypted count) | 6,060 | 258 | 13 | 304 (655) | 287 (4,992) | 0 | 100 | 100 | 20.6 | 16.3 |
| gpt-5-nano | direct OpenAI (metadata) | 3,378 | 90 | 13 | 15.8 (17) | 0 | 0 | 100 | 100 | 21.6 | 26.3 |
| gpt-5-nano | direct OpenAI, minimal (inferred) | 44,120 | 2,206 | 40 | 21 (75) | 0 | 0 | 99.88 | 91.6 | 53.4 | 19.0 |
| gpt-5.5 | ambiguous | 2,180 | 109 | 13 | 28 (94) | 16 (219) | 0 | 100 | 100 | 98.2 | 0.8 |
| gemini-3-pro-preview | OpenRouter (reasoning text) | 5,240 | 212 | 129 | 231 (633) | 197 (4,965) | 82 | 100 | 89.3 | 96.6 | 0 |
| gemini-3.1-pro-preview | OpenRouter (reasoning text) | 6,320 | 270 | 24 | 198 (367) | 186 (986) | 96 | 100 | 100 | 40.1 | 52.5 |
| gemini-3.1-pro-preview | direct Gemini (inferred) | 5,400 | 270 | 26 | 12 (14) | 357 (6,179) | 0 | 100 | 99.9 | 51.6 | 31.7 |
| gemini-3.1-flash-lite | OpenRouter (reasoning text) | 4,540 | 161 | 55 | 271 (549) | 256 (1,595) | 42 | 100 | 96.9 | 76.0 | 40.0 |
| gemini-3.7-flash | direct Google (metadata) | 3,378 | 90 | 25 | 12 (14) | 106 (1,504) | 0 | 100 | 100 | 83.3 | 26.5 |

Notes on this table:
- The Send=$5 and Return=$0 columns pool very different conditions (noise types, defector ratios, prompts) and are shown only to check that format artefacts are not driving them; do not read them as behavioural results.
- For OpenRouter-era Claude the `usage.reasoning_tokens` count is usually 0 even though thinking text is present, so thinking cost is folded into `output_tokens` (mean 718 vs 289–395 without thinking).

### 3c. Silent parse defaults

The current parser (`games/trust_game_noisy.py:1440`, `games/trust_game.py:539`) raises `ValueError` when the key is missing; the validator in `games/base_game.py:30-53` (added 2026-08-25) catches this before the response enters memory, and `src/simulation.py:668-680` retries once. A second failure kills the run, so completed runs cannot contain a silent default from this path.

One historical default exists: commit 5ddd2cbe (2026-04-29, "Handle zero-pot trustee return omissions") caught the `ValueError` and recorded return = 0 when the trustee had received $0. In the data, 54 GPT-5 Nano trustee responses across 44 runs in the v4_direct_provider* sets are literally `{}` and were recorded as return 0. All 54 have sent = 0 and received = 0 (verified from `conversation_history`). Benign: there was nothing to return. No other game response in 175,750 lacks the required key.

### 3d. Truncation

No `finish_reason` is stored. Inferred from token counts:
- Direct Anthropic runs with metadata (defector set, washout): max output 677 and 2,148 tokens respectively, cap 4,096. Zero cap hits.
- Direct-era Claude runs without metadata: max output 946 tokens. None at the old 1,024 default. Runs that hit it died before writing a JSON (`docs/verified-facts.md:9`, 2 runs killed 2026-07-17/20).
- OpenRouter-era Claude: no cap set; individual responses up to 5,853 tokens (thinking included), no evidence of truncation.
- GPT-5 Nano and Gemini: no cap set on either path.

## 4. Ranked findings that could explain cross-model behavioural differences

1. **Three different APIs and three different sampling regimes in the slide set.** Claude ran at temperature 0.8 with no thinking and a 4,096-token cap. GPT-5 Nano ran at the vendor default temperature (the code drops the parameter for gpt-5 models, `src/utils.py:494-499`) with reasoning effort at the code default "minimal" (`src/utils.py:502-503`; the value is not recorded in metadata, but 0 reasoning tokens on 3,378 of 3,378 calls is consistent with it). Gemini 3.7 Flash ran at vendor default temperature with thinking level "medium" and no cap (`temperature_sent: false`; env pattern in `scripts/launch_gemini37_flash_task_order_n3.sh:7-8`). Evidence: `run_metadata` in every JSON under `data/shared_runs/uploaders/vallinder/data/json/noise_experiments/negative_only_crossmodel_defectors_n5_20260825/`.

2. **Claude deliberates out loud and re-reads its own deliberation; the other two do not.** Claude's decisions average 1,000–1,250 characters of visible strategic analysis that stays in its chat memory for later rounds (memory-primary mode keeps the assistant content, `src/agents.py:207-212`). GPT-5 Nano emits 13 characters of bare JSON with zero reasoning. Gemini emits bare JSON after ~100 hidden thought tokens that are not stored. Under the 3-round memory window the three models therefore play with categorically different amounts of self-generated context. "Claude degrades with defectors" and "GPT-5 Nano beats Claude on collective returns" could be this rather than the models' dispositions.

3. **GPT-5 Nano's regime flipped between eras.** Via OpenRouter (baseline, v1, v2_uniform, v3, myth_topics; ~775 runs) it used a median 1,024 reasoning tokens per decision and returned reasoning summaries. Via direct OpenAI (v4_direct_provider*, defector set; ~2,300 runs) it used 0. Any comparison of GPT-5 Nano across those sets compares a reasoning model with a non-reasoning one. Evidence: `game_responses.csv`, column `rtok`, grouped by `expset`.

4. **Claude's regime also flipped.** All OpenRouter-era Claude runs (Arabella's five sets, Ivar's baseline / v1 / v2_uniform / v3 / myth_causal / sonnet45_8agent sets; ~1,100 runs) had extended thinking on, because the OpenRouter path sends `reasoning.effort = "medium"` by default (`src/utils.py:386-406`). Direct-Anthropic runs (defector set, v4, phase2–7, memtest, the mem3 set) had none. Within `washout_20round` and `noise_experiments/v2` both regimes sit inside the same condition (section 2c).

5. **GPT-5 Nano confuses the two tasks in two-task runs.** 93 of 3,000 myth calls (39 of 90 runs) in the defector set returned a game decision instead of a story and were retried. Claude and Gemini had zero. The validator that catches this was added 2026-08-25 (`src/myth_writer.py:50`), so older GPT-5 Nano game_myth / myth_game runs (baseline, v1, v2_uniform, v3, v4_direct_provider) may contain unflagged game JSON stored as "myths". Evidence: `interaction_errors.csv`.

6. **Gemini's ceiling-lock is not a provider artefact.** Gemini 3.7 Flash sends the maximum on 79–84% of decisions via direct Google in the defector set; gemini-3-pro-preview sent the maximum on 96.6% of decisions via OpenRouter in baseline / v1; gemini-3.1-pro-preview sent the maximum on 40% (OpenRouter) and 52% (direct). It maxes out under both routes, with and without visible thinking.

7. **Model aliasing did not bite.** `DIRECT_MODEL_ALIASES` in `src/utils.py:34-52` maps `google/gemini-3-pro-preview` to `gemini-3.1-pro-preview` on the direct path, but all 212 runs with that slug carry OpenRouter reasoning text, so none were rerouted. What backend model OpenRouter actually served for that slug is unverifiable (no response model id is stored). For every metadata-bearing run, `provider_model` is the expected native id (`claude-sonnet-4-5-20250929`, `gpt-5-nano`, `gemini-3.7-flash`).

8. **No truncation and no empty responses in completed runs** (section 3d). Empty content raises and retries on every path (`src/utils.py:409`, `:527`, `:579`), so it cannot reach a JSON.

9. **Message-role plumbing is identical across the three vendors in the defector set.** All 1,350 agents have `system` as message 0 and only `user` / `assistant` thereafter; agent `model` matches `run_metadata.model` in every run. The direct paths translate roles (`_anthropic_messages`, `_gemini_messages`, `src/utils.py:270-317`); whether the translated payloads are semantically equivalent is a code-path question outside this data audit.

## 5. Unverifiable

- **The exact code that produced the defector set.** `code_commit` 58d15e24 (269 runs) and c97f59ee (1 run) exist on neither `origin` nor `upstream` after `git fetch --all`; `config_path` is `/private/tmp/nips-negative-noise-20260825/config/experiments_noisy.yaml` on Aron's machine. Only `config_sha256` is recorded.
- **`OPENAI_REASONING_EFFORT`** for any direct OpenAI run; not written to metadata. Inferred "minimal" from reasoning_tokens = 0.
- **Provider of the ~1,065 Claude runs with no reasoning text** (phase2–7, memtest, ablation_phase1, mem3 set, v4 Claude). Direct Anthropic is likely (this machine's `.env` holds an Anthropic key and no OpenAI / Gemini keys; `docs/verified-facts.md:11`), but no run field proves it, and `OPENROUTER_REASONING_EFFORT=none` on OpenRouter would look identical.
- **Whether OpenRouter honoured temperature 0.8 for gpt-5-nano** in the OpenRouter era. OpenAI rejects non-default temperature for gpt-5 directly; OpenRouter's handling is not logged.
- **`finish_reason` / `stop_reason`** for any call; never stored.
- **Which backend OpenRouter served** for any slug; no response model id is stored.

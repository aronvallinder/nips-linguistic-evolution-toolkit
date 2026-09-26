# Early code/run provenance (bounded read-only audit, 2026-09-15)

## Scope and limits

Read the full slide-source snapshot from slide 1 onward, selected current code/config, dated git commits and six final full-state JSONs. No experiments or settings changes; this report documents read-only checks. Run timestamps and code hashes are absent from these older finals; file paths and content hashes identify evidence but do not prove its date or exact plotted slide. The earliest available repository commit is `8c9199b818b5f08f9a9177b4043e6280315a1400` (2026-04-21T23:37:40+02:00 initial source import). Therefore this history cannot timestamp implementation of November–March slide proposals.

## Design arc supported by code and saved states

### Early trust game, prompts and comparators

Slides 3/6–12 describe Llama70B, $5 endowment, tripling transfers, role-specific JSON with a reason field, own last-game recap, and own/partner prior myths. Slides 13/16/20/28 explicitly separate game-only, myth-only, game→myth and myth→game. Current [config/experiments.yaml:339-344](../../../config/experiments.yaml) still has all four task orders in an old pilot set, but current values are NOT evidence of exact original runs. The commented Llama70B mapping at [config/experiments.yaml:3](../../../config/experiments.yaml) is archival text, not an active model or proof of availability. I did not locate/validate an exact full-state final for the initial Llama slide sequence or January Haiku/GPT4o examples.

Slide 41's “No Defect” removes the verbal option-to-defect reminder; it does not remove the numerical ability to send/return zero. This differs from later mechanical defector manipulations and should not be called the modern no-defector treatment.

Slide65 says updated system prompt/no explicit reasoning/explicit myth writing. Sample old_baseline records exactly that broad transition: system introduces a multi-task experiment and myth writing, role labels still INVESTOR/TRUSTEE, action JSON lacks an explicit reason field. The final contains 15 complete rounds and two agents. This supports implementation existence, not identification with a specific slide or proof why it changed. Current [config/experiments.yaml:35](../../../config/experiments.yaml) instead says iterated game and SENDER/RECEIVER, so later vocabulary should not be projected onto this early state.

Personas are explicit alternative configuration choices ([config/experiments.yaml:282-300](../../../config/experiments.yaml)): neutral adds nothing; altruistic/selfish/cautious/risk_taking append behavioral instructions. These definitions do not establish use in the displayed runs. Sample filenames say neutral and sampled system prompts have no added persona sentence, but early metadata does not record a separate persona ID.

### Other games remain separate branches

Slides51–53 explicitly describe a four-agent donor setup, initial_resources100, donation_multiplier2, context_depth2/context_width2, myth_visibility all, myth_partner_rounds2. Slide54 reports gpt4o-mini/memory5, and parent inspected slides55–63 showing ten-agent long-horizon donation charts. Do not conflate these with eight-agent rotating trust dyads. [archive/games/public_goods_game.py:1-14](../../../archive/games/public_goods_game.py) defines a different pooled-contribution game with fixed per-round endowment and equal pool sharing. Its existence does not prove it generated those donor/compounding-balance figures. Exact archived donor implementation/final provenance remains unverified; neither abandonment rationale nor trust-game superiority is established by code.

### Noise intent, implementation and changed semantics

Slide226 explicitly gives two DIFFERENT goals: perturb transfers by ±1 for ceiling-locked models, and force apparently full returns for GPT's defection spiral. Current [config/experiments_noisy.yaml:1930](../../../config/experiments_noisy.yaml) defines bootstrap as probabilistic replacement probability1, replacement max, returned only; :1789 defines negative5 as uniform range5, direction negative, both transfers. [games/trust_game_noisy.py:300-334](../../../games/trust_game_noisy.py) implements those distinct transformations. The stale comment above negative5 says $3, while executable range is5; report actual config and do not silently adopt the comment.

Old sample bootstrap_v1 has separate sent/received/returned_communicated fields and memory10. bootstrap_v4 has memory3 and separate decisions/real ledger amounts: in round1 receiver DECIDES6 but ledger RETURNED9 (all9 available). Negative_v4's sender DECIDES3 but ledger SENT0, received0. This verifies an environmental-transfer implementation in these v4 outputs. It does not establish the semantics of every file in the same folder.

Commit `f6f78bad052e19610989000deef01527d4e63594` by Aron Vallinder, 2026-04-29T09:52:47+02:00, explicitly changes “distort communicated amounts” to “environmental perturbations on actual transferred amounts,” changes the informed prompt accordingly, and separates decision from ledger. This is a scientifically material condition change, not merely a cosmetic correction.

Current code supports BOTH environmental and communication semantics: [games/trust_game_noisy.py:53](../../../games/trust_game_noisy.py) default communication; :96-105 validates; :968-998 switches ledger behavior; :1000-1003 computes real and visible payoffs. Therefore calling all noisy runs a single treatment—or applying today's default to v4 old finals—is incorrect. Current [tests/test_noise_semantics_compatibility.py:45](../../../tests/test_noise_semantics_compatibility.py) and :92 cover environmental accounting and distinct prompts (read only, not rerun here).

Slides225 and 227 identify the old bug-bearing condition; March30 Ed comment asks to fix and rerun, while proposing downside noise up to5. This source request should be linked separately from the April29 implementation evidence. Neither commit alone proves it was the precise fix intended on March30, nor does the old slide prove later environmental noise was finally preferred for publication. May11 backfilled notes (researchlog.md:1825-1835) report a further decision to standardize perturbation rather than model-specific replacement and try smaller noise; direct meeting transcript should outrank the backfill for exact wording.

### System prompt mismatch and diagnostic arms

Exact sampled strings differ: old_baseline says “different roles across rounds”; bootstrap_v1/v4, negative_v4 and baseline_v4 say “different roles across multiple rounds.” baseline_match sample uses an explicit iterated trust game, says roles swap each round, and gives Agent1/Agent2 alternating examples. [scripts/run_baseline_match_ablation.py:1-11](../../../scripts/run_baseline_match_ablation.py) defines separate old/new-prompt, old/noisy-runner and 15/10-round diagnostics; the final records its prompt_source, runner kind, provider environment and low reasoning environment.

The sample v4 no-noise and v4 noise system prompts are equal; this establishes matched system wording for these specific sampled no-noise/ uninformed-noise runs. It does NOT prove every baseline matched every noise arm, or isolate causal outcome differences. researchlog.md:1825 reports a mismatch discovered and rerun by May11; no precisely timestamped code fix was identified here. Present this as a reported fix plus sampled matched strings, not a verified global repair date.

Today's [config/experiments.yaml:35](../../../config/experiments.yaml) and [config/experiments_noisy.yaml:212](../../../config/experiments_noisy.yaml) still have different base wording (explicit iterated game/current-role instruction versus “play a game”/different roles). This is a current config difference, not proof a particular modern experiment suffers the old bug: inspect resolved prompts for that experiment before concluding.

### Temperature/memory provenance

All six sampled finals record temperature0.8. That is a SAVED nominal value, not verified exact paid API payload. They lack per-call interaction history, provider route (except baseline-match environment fields), and code_commit. [src/utils.py:587-600](../../../src/utils.py) currently omits custom temperature for GPT5-family direct calls and has a legacy reasoning fallback; April29 commits b42d84c2/83654c20 introduced direct GPT5 temperature handling/minimal reasoning. Do not conclude GPT actually sampled at0.8 or equate “low/minimal/high” across vendors from these old metadata fields.

Memory differs even in early noise experiments: bootstrap_v1 capacity10 versus bootstrap_v4 capacity3, old_baseline capacity3. Capacity counts interaction pairs, not rounds (current [src/agents.py:83-88](../../../src/agents.py)). Consequently one-task and two-task conditions with equal capacity need not have equal raw-round horizons. The later July double-memory decision is separately documented by the previous audit.

## Final sample ledger

Each artifact below has top-level agents and conversation_history and a completed round count matching num_turns. None is a checkpoint/results-only/error artifact. This is structural completion evidence, not a new full scientific/protocol validation. Exact slide association and execution dates remain unknown unless explicitly stated.

### old_baseline

- File: `data/json/baseline/claude-sonnet-4.5/game/10runs_model_comparison_000_neutral.json`
- SHA-256: `9932f25a823e6a1696d73c83be1db0dae1dbc455b79ae6756954c33d10b27193`
- Model: `anthropic/claude-sonnet-4.5`; rounds 15; agents 2; tasks `['game']`; nominal temperature 0.8; memory 3.
- Noise config: `null`.

### bootstrap_v1

- File: `data/json/noise_experiments/v1/noise_bootstrap/gpt-5-nano/game/noisy_bootstrap_cooperation/noise_bootstrap_000_neutral.json`
- SHA-256: `5810367966e9600f66e6bf8a7f4a7f26682e03c726c7aa5aa8c5e37d6bf5d767`
- Model: `openai/gpt-5-nano`; rounds 10; agents 2; tasks `['game']`; nominal temperature 0.8; memory 10.
- Noise config: `{"type": "probabilistic", "probability": 1.0, "replacement": "max", "applies_to": "returned", "inform_agents": false}`.

### bootstrap_v4

- File: `data/json/noise_experiments/v4_direct_provider/noise_bootstrap_mem3/gpt-5-nano/game/noisy_bootstrap_cooperation/noise_bootstrap_mem3_000_neutral.json`
- SHA-256: `60910f776d980d0dd389fa05a6d0dbf93533066f678ec89145b250a566939a03`
- Model: `openai/gpt-5-nano`; rounds 10; agents 2; tasks `['game']`; nominal temperature 0.8; memory 3.
- Noise config: `{"type": "probabilistic", "probability": 1.0, "replacement": "max", "applies_to": "returned", "inform_agents": false}`.

### negative_v4

- File: `data/json/noise_experiments/v4_direct_provider/noise_negative_mem3_claude_sonnet_45/claude-sonnet-4.5/game/noisy_negative_5/noise_negative_mem3_claude_sonnet_45_000_neutral.json`
- SHA-256: `45b109c0c1a3648e7e792ba79402c5e520735f92695a033db060ea404d5281b5`
- Model: `anthropic/claude-sonnet-4.5`; rounds 10; agents 2; tasks `['game']`; nominal temperature 0.8; memory 3.
- Noise config: `{"type": "uniform", "range": 5.0, "direction": "negative", "applies_to": "both", "inform_agents": false}`.

### baseline_v4

- File: `data/json/noise_experiments/v4_direct_provider_baseline/baseline_v4_mem3_direct/gpt-5-nano/game/default/baseline_v4_mem3_direct_000_neutral.json`
- SHA-256: `a220d5e084e7152be0d3c5fe3837e3f05e5f84cb88c4ff80dea48e065f89d90e`
- Model: `openai/gpt-5-nano`; rounds 10; agents 2; tasks `['game']`; nominal temperature 0.8; memory 3.
- Noise config: `null`.

### match_old

- File: `data/json/baseline_match_ablation/direct/old_prompt_noisy_runner_10/gpt-5-nano/game_myth/default/old_prompt_noisy_runner_10_000_neutral_anything.json`
- SHA-256: `19c0b43d546621521331f48331e665f4398be85456d08d8f447dd066619bdb85`
- Model: `openai/gpt-5-nano`; rounds 10; agents 2; tasks `['game', 'myth']`; nominal temperature 0.8; memory 3.
- Noise config: `null`.

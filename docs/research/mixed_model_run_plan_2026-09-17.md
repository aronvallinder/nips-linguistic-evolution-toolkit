# Mixed-model run plan (for explicit go) — 2026-09-17

Status: proposed settings, not yet approved, not yet implemented, no paid calls.
Design authority: D010 (`docs/project-memory/decisions/010-mixed-model-population-sizes.md`).
Every setting below is copied from the September protocol in
`config/experiments_noisy.yaml` (sets `negative_only_reasoning_rerun_*`) unless
marked **NEW**.

## 1. Matrix — 66 runs

| Size | Composition | Task orders | Replicates | Runs |
|---|---|---|---|---|
| 2 agents | 1 Sonnet 4.5 + 1 GPT-5 Nano | game, game_myth, myth_game | 6 (3 Sonnet-first, 3 GPT-first) | 18 |
| 2 agents | 1 Sonnet 4.5 + 1 Gemini 3.7 Flash | game, game_myth, myth_game | 6 (3 Sonnet-first, 3 Gemini-first) | 18 |
| 8 agents | 4 Sonnet 4.5 + 4 GPT-5 Nano | game, game_myth, myth_game | 5 | 15 |
| 8 agents | 4 Sonnet 4.5 + 4 Gemini 3.7 Flash | game, game_myth, myth_game | 5 | 15 |

No homogeneous runs, no forced defectors, no random defection.

## 2. Models and request profiles (direct provider APIs, D004 "september8" profiles)

| Repo slug | Sent to provider | Provider | Reasoning | Temperature | Output cap |
|---|---|---|---|---|---|
| `anthropic/claude-sonnet-4.5` | `claude-sonnet-4-5-20250929` | Anthropic | thinking enabled, budget 8192 | provider default (omitted) | 64000 |
| `openai/gpt-5-nano` | `gpt-5-nano` | OpenAI | reasoning_effort high | provider default (omitted) | 128000 |
| `google/gemini-3.7-flash` | `gemini-3.7-flash` | Google | thinkingLevel high | 0.8 | 65536 |

Source: `llm_profiles` anchors `september8_claude/gpt/gemini` in
`config/experiments_noisy.yaml`; slug→ID map `DIRECT_MODEL_ALIASES` in `src/utils.py`.
Keys needed in `.env`: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`.
OpenRouter is not used.

## 3. Game parameters

Copied from `noisy2_crossmodel_negative_game_r3` / `_twotask_r3` (dyads) and
`noisy8_crossmodel_negative_game_r3` / `_twotask_r3` (populations).

| Parameter | 2 agents | 8 agents |
|---|---|---|
| endowment / multiplier | $5 / 3× | $5 / 3× |
| rounds (`num_turns`) | 10 | 10 |
| memory_capacity, game-only | 3 | 3 |
| memory_capacity, two-task | 6 | 6 |
| chat_memory_mode | memory_primary | memory_primary |
| noise | uniform, range 1.0, negative only, applies to sent and returned, agents informed | same |
| pairing_mode | fixed (same partner all run; roles alternate each round; Agent_1 sends in odd rounds) | **NEW** cross_family (each round every Sonnet is paired with one opposite-family agent; roles balanced over 10 rounds) |
| history_policy | n/a | self_and_coplayer, self window 0, co-player window 3 |
| show_agent_names | n/a (names "The sender"/"the receiver") | false |
| paired_protocol_seeds / protocol_seed_base | true / 202608250 | true / 202608250 |
| persona | neutral | neutral |
| game retry policy | repeat_same_prompt_once | repeat_same_prompt_once |
| myth topic | anything | anything |

`temperature: 0.8` in these blocks is overridden by the per-model profile above
(Claude and GPT send no temperature; Gemini sends 0.8).

## 4. Prompts (unchanged template keys)

- system: `trust_game_default` (+ informed-noise notice appended by
  `games/trust_game_noisy.py`, + population block from `games/dyadic_pairing.py`)
- round 1: `trust_game_round1_investor`, `trust_game_round1_trustee`
- later rounds: `trust_game_later_investor_minimal`, `trust_game_later_trustee_minimal`
- myth arm `memtest_memory_primary`: first `myth_writing_default_game_directive`,
  later `myth_writing_later_rounds_directive_memory_primary` (200-word myth that
  reflects how the game should be played; later rounds see the previous-round
  partner's myth)
- No prompt names any model brand. Agents are not told their partner's model.

## 5. Decisions still needed from Ivar (marked NEW)

1. **Dyad first sender (decided 2026-09-17).** Agent_1 sends in round 1. Six
   replicates per dyad cell: Sonnet is Agent_1 in replicates 0, 2, 4; the other
   family is Agent_1 in replicates 1, 3, 5. Replicate 5 uses protocol seed
   202608250 + 5, which no September run used.
2. **Cross-family pairing at 8 agents.** Proposal: 10-round schedule where each
   Sonnet meets each opposite-family agent at least twice, and every agent sends
   5 times and receives 5 times. Same-family games never occur. Myth transmission
   stays "previous-round partner's myth", so all myth exposure is cross-family too.
3. **Smoke first.** One dyad run per composition (2 runs, under $2) before the
   batch, to check the mixed transport path and JSON parsing.

## 6. What differs from the September informed-noise control runs

The reference is the 90 control runs of `negative_only_crossmodel_reasoning_rerun_20260909`
(sets `negative_only_reasoning_rerun_*`, game-params `*_negative_game_r3` /
`*_negative_twotask_r3`, no forced defectors). The mixed plan copies their
prompts, profiles, noise, memory, history, seeds and retry policy. Exactly four
things change:

1. Models: two families per run instead of one.
2. 8-agent pairing: cross-family only, instead of the balanced random schedule
   that also allowed same-family games. This is a protocol change, not only a
   model change.
3. Dyad replicates: 6 instead of 5, with the first sender alternating by family.
4. Code commit: per-agent models need new code, so the recorded commit differs
   from 893a9713/af3c9951. Prompts and request bodies must be shown unchanged by
   the launcher's condition audit.

The 180-run figure-2 extension (no noise, uninformed noise) is not the reference;
the mixed plan uses informed noise only.

## 7. Implementation required before launch (not yet done)

- `src/simulation.py` creates one client and one model for all agents
  (`create_llm_client` once, then `Agent(agent_id, model, ...)` in a loop).
  Needs per-agent model, client and request plan, preserved across resume.
- `games/dyadic_pairing.py` only has `balanced` and `fixed` pairing modes;
  add `cross_family` with role balancing.
- Record each agent's model in `run_metadata` and each call's provider in usage;
  extend `src/experiment_condition.py` validation, which assumes one model per run.
- New config sets plus a frozen launcher in the style of
  `scripts/run_figure2_extension.py` (dry-run default, `--execute`, resumable,
  completion receipt with standard-rate cost).

## 8. Cost (standard rates, from recorded usage of the September informed-noise runs)

Per-agent cost in the homogeneous September runs, times the number of agents of
each family in the mixed run, times the replicate count (6 dyad, 5 population). Rates: Sonnet $3/$15,
GPT-5 Nano $0.05/$0.40, Gemini 3.7 Flash $0.75/$3.75 per million input/output tokens.

| Cell | Anthropic | OpenAI | Google | Cell total |
|---|---:|---:|---:|---:|
| 2 agents, Sonnet+GPT, game (6 runs) | 0.66 | 0.04 | | 0.70 |
| 2 agents, Sonnet+GPT, game_myth (6) | 2.42 | 0.34 | | 2.76 |
| 2 agents, Sonnet+GPT, myth_game (6) | 2.37 | 0.34 | | 2.72 |
| 2 agents, Sonnet+Gemini, game (6) | 0.66 | | 0.10 | 0.76 |
| 2 agents, Sonnet+Gemini, game_myth (6) | 2.42 | | 0.67 | 3.09 |
| 2 agents, Sonnet+Gemini, myth_game (6) | 2.37 | | 0.70 | 3.07 |
| 8 agents, 4 Sonnet+4 GPT, game (5) | 2.37 | 0.14 | | 2.51 |
| 8 agents, 4 Sonnet+4 GPT, game_myth (5) | 8.17 | 1.11 | | 9.28 |
| 8 agents, 4 Sonnet+4 GPT, myth_game (5) | 8.48 | 1.13 | | 9.61 |
| 8 agents, 4 Sonnet+4 Gemini, game (5) | 2.37 | | 0.39 | 2.76 |
| 8 agents, 4 Sonnet+4 Gemini, game_myth (5) | 8.17 | | 2.12 | 10.29 |
| 8 agents, 4 Sonnet+4 Gemini, myth_game (5) | 8.48 | | 2.18 | 10.67 |
| **Total (66 runs)** | **48.96** | **3.10** | **6.16** | **58.22** |
| With 20% allowance | 58.75 | 3.72 | 7.39 | 69.86 |
| **Credit to hold per account** | **$65** | **$5** | **$10** | **$80** |

Caveats: mixed runs change what each model reads (Sonnet reads GPT/Gemini myths),
so token counts will shift; Sonnet input tokens dominate the bill. OpenAI credits
ran out mid-batch on 2026-09-15 at 36/60 runs, so top up before launch.
Wall-clock: GPT-5 Nano at high reasoning was the critical path in September
(~3 h per two-task set at 3 workers).

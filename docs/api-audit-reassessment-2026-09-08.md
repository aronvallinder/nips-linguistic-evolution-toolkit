# API audit reassessment — 2026-09-08

Two independent reviews checked the saved settings and scientific interpretation.
No experiment ran and no historical data changed. The corrected write-up is in PR20,
which supersedes closed PR17; the safeguards are already merged through PR19.

## Bottom line

The original audit correctly identified unequal recorded routes/settings and insufficient historical provenance. It overstates how confidently missing fields and saved reasoning signatures establish exact thinking modes. The checked ablation families are not demonstrated invalid: most simply cannot support a full retrospective reconstruction of every request setting.

**The format-study means reproduce, but the causal prose explanation is withdrawn:**
myth instructions/self-context and retry behavior also changed. See the format section below.

The strongest directly documented mixed-provider example is the washout family. The cross-model defector family explicitly records three direct APIs. Comparing reasonable, disclosed model-specific profiles is not intrinsically a bug, and the same reasoning label does not establish matched computation across vendors.

## Scope and method

- Input: `data/analysis/api_equivalence_audit_2026_09_04/runs_inventory_inferred.csv`, a historical path index rather than ground truth for inferred settings.
- Opened every one of 4,129 selected inventory-listed paths. All are present and have the final full-state fields `agents`, `conversation_history`, `game_data`, `task_order`, and `run_metadata`.
- SHA-256 over original file bytes leaves 3,661 distinct files after 468 exact-copy paths are removed. Most copies are local/shared mirrors. **These are distinct-file counts, not a claim of independent replicates.** Different bytes can still share experimental ancestry, partial histories, or replicate identity.
- Selected families: phase1; hybrid/memory-primary/stateless memtests including smokes; phase2–8; mem3; four fixed-prompt causal-confirmation variants; baseline-match; main v4 and its follow-ups; cross-model defectors; washout; and the three plain memory-primary task-order sets.
- This does not cover all 6,678 inventory rows, newly created files outside the historical index, all failed attempts, or all experimental families in the repository.
- Counts below use distinct original bytes. The [machine-readable appendix](../reports/api_audit_reassessment_2026_09_08/settings.json) contains allowlisted metadata counts and hashed source examples. No credentials, complete environment, prompts, or response text are exported in this settings appendix; the separate format appendix includes prompt/error examples.
- The extractor distinguishes an absent numeric field from zero. However, historical adapters already transformed missing vendor values into zero, and Anthropic's adapter hard-coded zero. A saved zero is therefore **not always a raw vendor measurement**.

## Small settings table

All rows record the repository model slug and `temperature: 0.8`. The latter is a configuration/request value, not proof that the adapter transmitted it or the provider applied it. Model names below are literal archived labels, not a claim about current availability.

| Dataset/model | Distinct final files | What is directly recorded | What remains inferred or unknown |
|---|---:|---|---|
| Cross-model defectors: Claude Sonnet 4.5 | 90 | Provider `anthropic`; resolved request ID `claude-sonnet-4-5-20250929`; cap 4096; mode direct in 89 and auto in one | No recorded thinking setting or temperature-sent flag. Historical adapter supports a temperature-0.8/no-thinking-parameter interpretation, not an archived raw request. |
| Cross-model defectors: GPT-5 Nano | 90 | Provider `openai`; resolved request ID `gpt-5-nano`; cap null with `provider_default` source; all 3,378 accepted game records contain normalized reasoning count 0 | Reasoning effort is unrecorded. `minimal` is a code default, not proven per-run. Historical code omits temperature, but metadata's 0.8 is not an effective-temperature measurement. |
| Cross-model defectors: Gemini 3.7 Flash | 90 | Provider `google`; resolved request ID `gemini-3.7-flash`; thinking `medium` from `GEMINI_THINKING_LEVEL`; `temperature_sent: false`; cap null/provider-default | Actual provider-default sampling and cap are unknown. 2,819/3,378 accepted game records have positive normalized reasoning counts. |
| Phase1 ablation: Sonnet 4.5 | 80 (160 paths) | Slug, configured temperature, ablation cell/seed fields; no saved reasoning text in 1,600 accepted game records | Provider, resolved ID, thinking parameter, transmitted temperature and output cap are absent. No-text does not prove thinking-off or direct Anthropic. |
| Memory-regime pilot: Sonnet 4.5 | 5 per hybrid/memory-primary/stateless arm; 15 total | Configured temperature and memory regime; no saved game/myth reasoning text | Same missing route/effort/cap fields. Three separate Haiku smoke files are additional, not members of the Sonnet arms. |
| Phase2–8 families | 190 total, including 6 Haiku files | Slug, configured temperature and per-family protocol fields; no accepted game response stores reasoning text | No provider/effort/cap metadata. Observed signatures agree, but “the whole thread is internally consistent” is too strong for unrecorded settings and differing intended protocols. |
| Fixed-prompt confirmation: base / top-up | 15 / 15 | Configured temperature; no saved reasoning text in 240 / 240 accepted game records | Provider/native effort/cap unknown. |
| Fixed-prompt confirmation: r10 / r10-directive-retry | 20 / 10 | Configured temperature; saved reasoning text in all 400 / 200 accepted game records | Strong signature difference from base/top-up, compatible with OpenRouter in historical code; exact route and native effort are not directly recorded. These also have deliberate protocol differences, so this is not an isolated provider experiment. |
| Baseline-match ablation: GPT-5 Nano | 126 (252 paths) | `provider_env: direct`, `openai_reasoning_effort_env: low` in every file; 2,915/2,970 accepted game records have positive reasoning-token counts | These are explicit recorded environment choices, not resolved-ID or raw-request receipts. Transmitted temperature, endpoint, model override and cap are not directly recorded. |
| Main v4 family | Sonnet 180; GPT-5 Nano 307; Gemini 3.1 Pro 270; GPT-5.5 79 | Slug and configured temperature. Gemini has positive reasoning counts in 5,400/5,400 accepted game records; Nano has saved zero in 6,140/6,140 | No route/effort/cap metadata. Launch scripts corroborate an intended direct route, not the exact history of each file. Nano `minimal` must not be filled in from zero counts. |
| v4 follow-ups | Sonnet 98; Nano 1,904; GPT-5.5 30 | Same limited metadata. Nano's 6 pilot files contribute 120 accepted game records with positive reasoning; the remaining 37,960 game records have saved zero | Exact route/effort per file unknown. Some historical launchers explicitly specify low, so neither folder name nor a zero count reconstructs effort reliably. |
| Plain memory-primary task-order triplet | 5 game; 5 game→myth; 5 myth→game | First two sets have saved reasoning text in every accepted game record; myth→game has none. Researchlog records an OpenRouter rerun for the first two | Exact native effort/caps unknown. Cross-leg pooling needs a historical-route caveat, not a categorical claim that task order has no effect. |
| Game-only mem3 follow-up | 4 finals | No saved reasoning text; configured temperature; researchlog records 4/5 completions and an output-cap failure | Not five completed replicates despite the name. Historical cap/route details are partly narrative; final-file-only inspection cannot rule out selection from failed attempts. |
| Washout, Sonnet 4.5 | 30 | Top-level provider 23 OpenRouter / 7 Anthropic. Resolved request ID and cap distinguish routes; Anthropic-labelled cap 4096, OpenRouter-labelled cap null | Two Anthropic-labelled 8-agent myth→game finals have reasoning text in rounds 1–10 and none in 11–20. Top-level provider must not be assumed to describe every call; confirm transition using logs/per-call records before causal interpretation. |

## Verified signature details, not new behavioral findings

### Defector set

All 270 files have `code_dirty: false`. Their recorded code identifiers are `58d15e2418a2533e6a12f752e3037035fcc202a5` (269 files) and `c97f59ee4aef157645e4175880ac8767f9215297` (one Claude file). Those exact objects are not readable in this checkout, so code-at-run reproduction remains incomplete. Reachable historical commit `38fa31aa` shows the relevant adapter policies but is not silently substituted for the recorded commits.

There are 3,378 accepted LLM game records and 3,000 accepted myth records per model, plus 1,122 scripted game decisions excluded per model. All accepted LLM records in the selected scope lack `finish_reason`. Absence of cap hits or parsing failures in completed outputs does not prove that truncation never happened or that failed attempts caused no selection.

### Washout records that mix signatures within a final

Both have 160 accepted game records: 80 with reasoning text in rounds 1–10, 80 without in11–20. Both are top-level `llm_provider: anthropic`.

1. `data/json/noise_experiments/washout_20round/noise8i_washout_myth_game/claude-sonnet-4.5/myth_game/noisy8_bidirectional_informed_memprimary_twotask_r3_r20/noise8i_washout_myth_game_001_neutral_rep01_memtest_memory_primary_anything.json` — SHA256 `682efc514f3667e78a40bcd2183bcfd9d79ce3f9024ddee4caba53d89ff5abf5`.
2. `data/json/noise_experiments/washout_20round/noise8i_washout_myth_game/claude-sonnet-4.5/myth_game/noisy8_bidirectional_informed_memprimary_twotask_r3_r20/noise8i_washout_myth_game_000_neutral_rep00_memtest_memory_primary_anything_2.json` — SHA256 `501020b49adc626acaff791507ae7ff20da1c00309b4a51604be6c4b73f27678`.

This is an observed logging/signature discrepancy. It is compatible with resuming under another route, but it is not itself a recovered exact request history. The other five Anthropic-labelled washout files lack saved reasoning text throughout.

### Phase2–8 file denominator

Distinct files: phase2 baseline 45, seeded 60, pilot 3, smoke 1; phase3 baseline 5, seeded 13 (10 Sonnet + 3 Haiku); phase4 baseline 10, seeded 20, smoke 2 Haiku; phase5 seeded 11; phase6 seeded 10; phase7 seeded 4; phase8 monitored 5, smoke 1 Haiku. Total 190. These counts are inventories, not an analysis population to pool.

## Source-level limits that change the original audit's wording

Historical source inspection used `git show 38fa31aa:src/utils.py | nl -ba`, not the current safeguard implementation. Other source line references in this section refer to shared main `a1ed13af` before the new researchlog entry:

- Lines 102–166: run metadata records resolved routing and selected policy fields, but not an entire actual request or returned model identity.
- Lines 377–380,518–531: direct GPT-family temperature omitted; effort selected from `OPENAI_REASONING_EFFORT` or fallback `minimal`. A missing recorded environment value prevents deciding which branch applied.
- Lines 388–405: OpenRouter reasoning effort comes from environment/default except excluded model families. Stored reasoning text does not recover the override or provider mapping.
- Lines 457–472: OpenAI-compatible reasoning-token extraction starts at zero, so some missing provider fields can become saved zero.
- Lines 547–578: Anthropic cap comes from environment or 1024; no thinking parameter is sent; reasoning returned as None and token count hard-coded 0. A later machine `.env` setting is not evidence of an earlier run's cap.
- Lines 737–744: Gemini missing thought count normalizes to 0.
- `scripts/audit_api_provenance_inventory.py:71` and `:79` add another missing→zero conversion. The new scratch extractor does not repeat it, but cannot undo values normalized before saving.
- `scripts/run_baseline_match_ablation.py:237`–`:249` confirms baseline-match intentionally records `provider_env` and `openai_reasoning_effort_env`; the old inventory omitted those columns.
- `scripts/run_overnight_2026-05-03_missing.sh:65` explicitly requests direct/low, whereas neighboring overnight scripts omit the effort variable. These show intent/default dependence, not proof of every run's settings.
- `researchlog.md:1084` records four successful mem3 runs and one cap-related failure. `researchlog.md:1126` records the plain game/game→myth OpenRouter rerun. Preserve these historical entries rather than rewriting them.

## Scientific claims: what changes

| Earlier claim | Corrected interpretation |
|---|---|
| Different provider settings invalidate the research. | The outcomes describe model-plus-settings conditions. Hidden changes limit particular comparisons; they do not establish that all historical results are invalid. |
| GPT's anomalous result is explained by minimal reasoning. | Minimal was a code-default inference, not recorded effort for the defector set. The proposed explanation is untested. |
| No reasoning text or zero counters means thinking was off. | Some historical adapters discarded reasoning or wrote default/synthetic zeros. Missing fields and transformed counters cannot establish native thinking settings or compute. |
| Equal effort labels make models comparable. | Report reasonable, explicit native settings. Labels are not calibrated computation budgets; within-model robustness checks answer a different question from model-only rankings. |
| No role-format bug means identical prompts and wire requests. | The inspected adapters preserve intended user/assistant order and provider-native system placement. Saved `messages_sent` precede adaptation; this is not proof of universal equivalence across versions. |
| No parsing defaults, truncation, or aliasing occurred anywhere. | The completed slide-set review found no identified silent numeric-default explanation. Older exceptions exist; absent stop reasons, missing responses/failed attempts, and historical alias mappings prevent universal negatives. |
| A credit outage automatically changes provider. | Legacy `auto` chooses by key availability. The documented July switch was an explicit rerun/provider override; a credit failure itself does not prove automatic fallback. |
| The small Gemini probe proves ignored temperature and a universal no-thinking arm. | Request acceptance and variable outputs at temperature zero do not establish that a parameter is ignored. A few reported zero thought counters do not establish an off guarantee. Raw probe records were not independently recovered in this review. |
| The restart selected low reasoning and two-sentence replies for all models. | It did not. PR19 changes safeguards, not model selection, prompt format, memory, or retries. |

The original [Codex report](../data/analysis/api_equivalence_audit_2026_09_04/codex_report.md)
already qualified truncation and message equivalence; the
[empirical report](../data/analysis/api_equivalence_audit_2026_09_04/empirical_report.md)
identified default-dependent effort and older empty trustee objects converted to zero
when receipts were zero. The consolidated claims were stronger than this underlying evidence.
Original reports and CSVs remain historical artifacts, not a substitute for these qualifications.

## Format study: reproducible descriptive differences, not an isolated prose effect

All 15 final full-state files were reopened: five per arm, ten rounds per run,
six ordinary agents and 60 accepted ordinary-agent game decisions per run.
The table averages **run-level summaries**; SD is sample SD across five runs,
not variability across 300 supposedly independent decisions.

| Historical arm | Final runs | Send fraction | Return ratio | Final balance | Reply characters |
|---|---:|---:|---:|---:|---:|
| Free prose + game-directed myths | 5 | 0.592 (±0.042) | 0.444 (±0.007) | 50.35 (±1.35) | 1286 (±17) |
| Two sentences then JSON + generic myths | 5 | 0.531 (±0.033) | 0.428 (±0.019) | 47.78 (±1.22) | 352 (±6) |
| JSON only + generic myths + corrective retries | 5 | 0.394 (±0.049) | 0.390 (±0.030) | 42.12 (±3.02) | 13 (±1) |

The first-to-third sending gap is **19.77 percentage points, descriptively**.
It is not an estimate of the effect of removing prose.

### What else changed

- **Myth instructions and self-context:** the reference uses
  `myth_writing_default_game_directive` and
  `myth_writing_later_rounds_directive_memory_primary`. Both new arms use
  `myth_writing_default` and `myth_writing_later_rounds`. Saved prompts confirm
  removal of explicit game-directed instructions and additional repetition of the
  agent's own prior myth. These are substantive differences, not renamed keys.
- **Retry policy:** the reference used a plain retry. Commit `e27003a0` introduced
  up to two corrective retries naming role and decision key. Completed reference
  files contain two rejected game attempts total; the two-sentence files have none;
  JSON-only files have 21 corrections/rejections total, 1–7 per run.
  One required a second correction. “Prose provides role orientation” remains a hypothesis.
- **Code provenance:** reference files name the unavailable `58d15e24` object;
  two-sentence files name `be3eae6b` with a dirty worktree. JSON replicates 0–3
  name clean `e27003a0`; replicate 4 names dirty `f6ddd121`.
  A dirty-state flag does not recover the exact source.
- **Thinking evidence:** all three arms record direct Anthropic, the same resolved
  model ID, configured temperature 0.8 and cap 4096. Only the new arms record
  `llm_settings_effective`; the reference's exact thinking request is less documented.
- **Attempt selection:** four initial JSON-only error snapshots were located, not
  all five claimed original failures. The historical note reports a credit-failed
  replicate-4 attempt and fresh rerun; the final file confirms its seeds, not the
  full interrupted history. Error snapshots are not included as completed runs.

Recorded replicate IDs 0–4, pairing/noise seeds 202608250–202608254 and defector
seeds 0–4 match across the three arms. Matching these seeds does not repair the
other changes or establish identical vendor sampling draws.

[Per-run evidence](../reports/api_audit_reassessment_2026_09_08/format.json)
contains relative paths, byte hashes, selected metadata, metrics, and prompt/error
examples. The same caveats were already noted in archived commit `0237659e`;
they had not reached PR17's living write-up. The historical researchlog entry is
preserved with a new corrective entry above it.

### What the study does and does not support

Visible assistant prose is retained in memory-primary; provider-hidden reasoning
and logging metadata are different things. The study motivates checking response
format and reliability. It does **not** isolate the retained-memory mechanism,
prove why model rankings differ, or identify a format-by-defector interaction
from a single 25%-defector condition.

A clean future format comparison would keep directed myth templates, memory,
source revision, retry policy and all other declared conditions fixed, changing
only the format instruction. A memory-retention mechanism needs its own explicit
intervention. These are proposed designs, not changes adopted or runs launched here.

## Current position and next manual check

- Keep the safeguards: they prevent future silent changes but cannot reconstruct
  historical missing values. See [their usage guide](safeguards-usage.md).
- Preserve historical findings at the scope their documented conditions support.
  Do not substitute either blanket invalidation or blanket reassurance for evidence.
- Inspect the two washout files at the round-10/11 boundary and the exact inputs
  of any figure that uses them before interpreting that comparison.
- Choose reasonable native settings with Ed and Aron, then verify a few real calls
  and consider the smallest informative within-model robustness comparison.
  Keep format/memory interventions separate. No new profile is selected here.
- Ed's expectation that reasonable higher reasoning may leave findings intact
  remains an expectation, not a completed robustness result.

## Reproduce and inspect

The [review evidence directory](../reports/api_audit_reassessment_2026_09_08/README.md)
contains the input hashes, allowlisted summaries and standard-library extraction
scripts. The scripts read existing files only; they do not invoke model APIs,
change conditions, sync data or overwrite the historical audit outputs.
Raw runs are still needed from the existing data store to independently rerun them.

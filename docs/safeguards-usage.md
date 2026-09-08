# Safeguards: use and human review

**Purpose: the same declared experiment must send the same requested settings
on another person's machine.** Different models may deliberately use different
settings. These checks do not make native reasoning levels equivalent.

This replacement implements the four promises in [the scope](safeguards-restart.md).
It changes no experimental configurations, game prompts, memory rules, noise,
seeds, task order, or game/myth retry behavior. No canonical model profile is
selected and no paid experiment is part of validation.

## 1. Configuration is the source of requested settings

Each guarded experiment set needs all four `llm_settings` fields. A
**synthetic test example, not a recommended research profile**, is:

```yaml
llm_settings:
  provider: direct
  reasoning:
    reasoning_effort: low
  temperature: default
  max_output_tokens: 128
```

This example uses the OpenAI request shape. A set spanning different vendors
must be split into explicit per-provider sets; there is no automatic reasoning
translation. The configuration checker can validate named `comparison_sets`
across those sets, with written reasons for their differences.


| Field               | Accepted policy and guard                                                                                                                                                 |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `provider`          | `direct`, `openai`, `anthropic`, `google`, or `openrouter`. Never `auto`; missing credentials fail rather than choosing another provider.                                 |
| `reasoning`         | An explicit native request object, as listed below. Missing/unknown keys fail locally. No hidden mapping from a shared label to a vendor budget.                          |
| `temperature`       | `default` omits the parameter; a finite number is sent explicitly. Locally validated range is 0–2, or 0–1 for Anthropic. Model-specific support still needs verification. |
| `max_output_tokens` | Positive integer or `default` to omit. Anthropic requires a positive value: there is **no implicit 4096 cap** in the guarded path.                                        |


Native reasoning objects accepted by `src/llm_settings.py`:

- OpenAI: `reasoning_effort` (`none`, `minimal`, `low`, `medium`, `high`, `xhigh`, `max`).
- Anthropic: `thinking.type` (`disabled`, `enabled`, `adaptive`); `enabled`
also requires positive `budget_tokens`, strictly below the output cap.
Optional `output_config.effort`: `low`, `medium`, `high`, `max`.
- Google: `thinkingConfig` with exactly `thinkingLevel` (`minimal`, `low`,
`medium`, `high`) or integer `thinkingBudget` ≥ −1.
- OpenRouter: `reasoning` with exactly `enabled` (boolean), `effort`
(`none`, `minimal`, `low`, `medium`, `high`, `xhigh`), or positive `max_tokens`.

These are **structurally accepted requests, not a model capability catalogue**.
An endpoint may reject a level or combination for a particular model. Numeric
temperature is not dropped based on the old audit's unproven behavioral inference.

The cap becomes `max_completion_tokens` for OpenAI, `max_tokens` for
Anthropic/OpenRouter, and `maxOutputTokens` for Google. These native caps do
not necessarily count the same kinds of tokens. `default` means omitted,
not a known effective number. Provider defaults can change.

Guarded requests ignore legacy environment settings for provider, native model
override, reasoning, temperature, and cap. There are no environment overrides
for those experimental settings; edit and review the config instead. Credentials
remain in the environment. Canonical endpoints are explicit. Transport settings,
including Gemini timeout and existing SDK retry behavior, are not experiment
parameters in this version.

No general pass-through for tools, structured-output schemas, stop sequences,
top-p/top-k, penalties, logit bias, model RNG seeds, or arbitrary API fields is
added. Their support would need a separate reviewed change. Experiment seeds
are recorded as protocol inputs; they are not provider sampling seeds.

## 2. Inspect without spending money

All three guarded entrypoints accept `--dry-run`. It prints resolved request
plans and run/worker counts, then exits before workers, API clients, or uploads:

```sh
python3 experiments/run_noisy_batch.py YOUR_SET --config config/experiments_noisy.yaml --dry-run
python3 experiments/run_trust_game_batch.py YOUR_SET --dry-run
python3 scripts/run_noisy_missing.py YOUR_SET --config config/experiments_noisy.yaml --dry-run
```

Replace `YOUR_SET` with a reviewed pinned set. Existing sets remain unchanged
and unpinned: a normal launch now fails unless migrated or explicitly given
`--allow-legacy-settings`. That escape hatch retains historical behavior and
does **not** supply modern provenance. It is forbidden in new CI-checked launchers.

Each modern final JSON records `run_metadata.llm_request` and a hashed
`experiment_condition`. Each logical model call records `usage.request_settings`,
`finish_reason`, `outcome`, available token counts, and available response model/ID.
Unknown token usage is `null`, distinct from a reported zero. Failed calls keep a
sanitized error record. Existing internal transport retries are not separately
recorded as individual HTTP attempts.

The stop reason identifies truncation/refusal where reported; it does not force
rejection of an otherwise parseable decision or equalize output format. Existing
parsers and behavioral retry rules are unchanged. Tests verify serialized request
bodies; they do not prove that a remote vendor honors a parameter internally.
OpenRouter receives `require_parameters: true`, but its underlying backend is
not pinned or independently verified. A returned model ID is evidence, not proof
that a vendor has kept model weights unchanged.

## 3. Resume, compare, and share deliberately

Guarded resume compares the saved condition before any API call. Provider,
reasoning, cap, prompt, memory, noise, task order, seeds, and run identity changes
are not silently accepted. Source-file hashes in `src/` and `games/` make this
conservative: even a nonbehavioral source edit can require a new run rather than
resuming an old checkpoint. The missing-run launcher requires final full-state
JSON and matching recorded configuration inputs before treating a file as done;
it is not a guarantee that old completed outputs came from today's source revision.
For shuffled-myth controls, planning hashes the actual loaded pool and compares
it with the completed run's pool hash. Workers also reject a pool changed since
planning before starting a simulation.

**Migration:** keep existing unpinned sets and their outputs under their historical
identity. Continue them only with `--allow-legacy-settings`. Create a new named
set with reviewed `llm_settings` and a separate output location for pinned work
(also change any copied `output_dir` override). Do not add pinned settings in place
over legacy outputs: a legacy final cannot satisfy a pinned missing-run check,
and a legacy checkpoint cannot resume as a pinned run. The legacy flag does not
disable validation on a set that already has `llm_settings`. Preserve old outputs
as historical evidence; the new pinned condition must start its own runs.

`analyses/_shared.py::load_simulation_runs` compares conditions across all input
models. Only named differences with written reasons are allowed. For example,
an otherwise identical replication comparison can use this JSON spec:

```json
{"replicate": "Independent replicates of the same treatment"}
```

Different models require explicitly naming the differing model/provider/native
parameter fields as appropriate; there is no blanket `allow_mixed_settings`.
Legacy input also needs `--legacy-reason` (or Python `legacy_reason`), remains
labelled incomplete/unknown, and cannot bypass invalid modern records.
Legacy comparisons retain recorded temperature sent-ness and setting sources.
Missing OpenAI effort remains unknown: a passing exploratory comparison does not
establish matched effort.

The cooperation-ratio and resources-max plot CLIs accept `--comparison-spec`
and `--legacy-reason`. They check the selected runs before creating output
directories. They write `provenance.json` with input hashes, recorded conditions,
declared/observed differences, and output hashes. Other analysis writers can use:

```sh
python3 scripts/write_provenance.py OUTPUT_DIR FINAL_RUN.json --comparison-spec comparison.json
```

HF automatic sync defaults to completed full-state runs with valid modern
provenance, plus their corresponding sidecars. To also back up historical runs,
explicitly set `HF_DATASET_ALLOW_LEGACY_PROVENANCE=1` alongside the usual upload
settings. Manual historical backfill accepts `--allow-legacy-provenance`.
Both exceptions accept missing legacy provenance, never broken modern records
or partial runs. Upload failures do not invalidate successful scientific completion.

**Remaining legacy entrypoints:** direct simulation callers
`experiments/run_trust_game.py`, `experiments/run_ablation.py`,
`experiments/run_phase2_seeded_cells.py`, `experiments/run_phase3_seeded_cells.py`,
`experiments/test_rate_limits.py`, and `scripts/run_baseline_match_ablation.py`.
Low-level `call_llm` users (judges, seed scorers, translation scripts, monitors)
and readers still using `load_simulation_data` are not automatically guarded.
Guarded simulations with the optional strategy monitor fail explicitly until
its separate model request is pinned. No silent monitor fallback is added.

## 4. GitHub checks and the human merge gate

`scripts/check_safeguards.py` validates new/changed experiment definitions in
`config/*.yaml`, direct `scripts/launch_*` wrappers, declared config comparisons,
and tracked output groups under `data/analysis`, `docs/figures`, and `data/plots`.
Output-manifest enforcement is scoped to those directories; it is not repository-wide.
In particular, `reports/` is outside this automatic gate. Audit/replay reports there
retain their own evidence and reproduction scripts and require review; they are not
certified by the plot-provenance check. Other writers can opt in by placing output
groups in a checked directory and writing a compatible `provenance.json`.
Unchanged historical definitions/artifacts are grandfathered by the checksummed
fixture, not relabelled as verified. Do not regenerate that baseline to make a
new failure disappear. Checks cannot authenticate uncommitted input data or stop
an author deliberately editing both a guard and its tests.

New launchers must contain only a shebang/comments, `set -euo pipefail`, and
`exec python3 GUARDED_RUNNER SET` with full option names and literal values.
Complex launch orchestration requires review, not a regex-based assertion of safety.
Changed output groups need a valid manifest matching all their tracked files.

The `pytest` job in `.github/workflows/tests.yml` runs the full `tests/` directory
and then explicitly runs `python scripts/check_safeguards.py`. The safeguard gate
therefore remains in that job even if its repository-check unit test is refactored.
**A passing workflow becomes a merge requirement only through branch rules.**
This account has push, not admin/maintain, access (checked 2026-09-07).
Aron/a repo admin must require `pytest` and at least one independent approval
on `main`, dismiss stale approvals after changes, and review who may bypass those rules. No claim is made that these repository settings have been enabled.

Before merge, Ivar and an independent reviewer follow this short walkthrough:

1. Inspect the synthetic test's config in `tests/test_llm_request_plan.py` and
  the native request plan in `src/llm_settings.py`. Confirm no research profiles changed.
2. Run the free SDK-body tests: `python3 -m pytest tests/test_llm_request_plan.py -q`.
  Compare the captured JSON body to the saved request record for each provider.
3. Run `python3 -m pytest tests/test_safeguards_smoke.py -q`. This uses a real
  local HTTP server, the installed OpenAI SDK, the simulator, and saved files;
   it sends no request to a paid vendor. Identical resume succeeds; changed
   conditions fail before HTTP.
4. Run `python3 -m pytest tests/test_experiment_condition.py tests/test_safeguards_ci.py -q`.
  Inspect one intentional rejection and one explicitly allowed comparison.
5. Confirm CI and the actual required-check/review rules, then approve the PR.

Keep subsequent scientific decisions separate: manually verify a small set of
real calls under team-chosen profiles before rerunning any research comparison.

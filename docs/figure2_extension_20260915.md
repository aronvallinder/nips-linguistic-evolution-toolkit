# Figure 2 no-defector extension — 2026-09-15

Approved scope: 180 new runs; preserve the 90 September informed-noise controls.
Three native-provider profiles (Sonnet 4.5 thinking 8192, GPT-5 Nano high,
Gemini 3.7 Flash high), 2/8 agents, game/game→myth/myth→game, five
replicates, ten rounds. New treatments: noise disabled and uninformed
uniform negative-only communication noise of range 1 on both actions.
No fixed defectors, random forced-zero actions, punishment, or uploads.

`config/figure2_no_defectors_20260915.yaml` freezes the original source YAML
with only its control game-parameter variants and new experiment names.
The launcher compares every resolved input against the original September
configuration and permits only the noise_config difference. An offline check
also matched comparison_inputs against all 90 existing control finals.

Run `python scripts/run_figure2_extension.py` for an offline validation.
Use `--workers 20 --execute` for execution. The global pool interleaves
providers and task orders. Existing final JSONs are validated before reuse;
checkpoints are never completion evidence. Incomplete jobs retry at one
worker, up to ten passes; any existing final that fails validation stops the
batch. Repeated jobs are fresh samples and must be disclosed in reporting.

Estimated standard-rate spend $129.86; planning allowance rounds to $160.
New profiles and data scope require a new decision. Output is
`data/json/noise_experiments/figure2_no_defectors_20260915/`; the final
completion_receipt.json lists verified full-state hashes and usage costs.
The 20-worker setting affects concurrency only, not scientific inputs.

The population condition intentionally retains partner-history information;
it is not a pure manipulation of agent count. Preserve this distinction in
Figure 2. Median myth-minus-game resource differences will match the original
plot's statistic; comparison must remain within model, population and noise.

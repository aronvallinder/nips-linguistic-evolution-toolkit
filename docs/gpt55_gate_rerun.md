# Rerunning Aron's GPT-5.5 gate

From a clean checkout containing PR #22 and its rerun fixes:

```bash
python3 scripts/rerun_gpt55_gate.py --output-subdir gpt55_rerun_20260909
python3 scripts/rerun_gpt55_gate.py --output-subdir gpt55_rerun_20260909 --workers 3 --execute
```

The first command checks all twelve resolved conditions without API calls or
output writes. The second runs them and audits each six-cell stage. It needs
`OPENAI_API_KEY`; the existing client loads the repository `.env`. Existing output
folders are refused unless `--resume` is provided. Resume verifies completed
finals and skips them; incomplete cells reuse their matching checkpoints.
Reports are written under the new output folder's `reports/r1` and `reports/r2`.
There are no automatic uploads.

These are the original two paired replicates of the six population/task-order
cells: 12 runs, 10 rounds each, 1,000 expected model interactions before retries.
The original YAML and historical outputs remain unchanged. The separate
`config/gpt55_gate_rerun.yaml` preserves every expanded historical input and pins
native OpenAI requests to `gpt-5.5-2026-04-23`, low reasoning, with temperature
and the output cap omitted as in the historical adapter. It explicitly uses
`repeat_same_prompt_once`, the original launcher's default retry policy. The
historical launcher's retry environment was not fully recorded, so this cannot
prove byte-identical retry behavior on a rejected response. Successful outputs
and behavioral results are stochastic and need not match the old runs.

New finals record their actual current code/config hashes, the original code and
config references, and the full request/protocol condition. The audit compares
every request, protocol and replicate field against frozen condition hashes,
not merely agreement among the new runs. Legacy originals are accepted only
with their original stage-specific commit and config SHA-256:

- r1: `f53fa6d9fcde5bd10528054423914b03db8881fc`, config `86f5fff912effffc406352cc05c66f7c38f36725bc72c055073b50ad32c4d137`.
- r2: `2ece1de681e5c99243df9de181cfce43ee94cd5e`, config `d204c480b334a5973ec6145abb9d3a6c077430b80e3d2c0d86a373dc892a53ea`.

The historical cost was $15.22 for twelve runs. A $30 planning estimate allows
roughly twice that token volume, at the September 9, 2026 standard rates of
[$5 input / $30 output per million tokens](https://developers.openai.com/api/docs/models/gpt-5.5).
This is an estimate, not a spend cap; check current prices before later runs.

A passing `completion_passed` audit establishes completion and checked
conditions. `behavioral_headroom: requires_review` deliberately leaves the
scientific judgement to inspection of the distributions. It makes no claim of
headroom merely because parsing succeeded.

The three recovered historical shell launchers now explicitly acknowledge
legacy settings. The safeguard checker accepts only this exact one-line change
to their frozen bytes; its baseline is unchanged. Use the new pinned entrypoint
above for fresh GPT-5.5 runs.

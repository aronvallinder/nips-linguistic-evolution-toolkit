# Reasoning-cost pilot — 2026-09-08

This is a cost-only replay of archived requests, **not new behavioral runs**.
Original simulations, prompts, memory policies, and results are unchanged.
All 72 selected requests completed, without HTTP/transport errors, retries,
empty answers, truncation finish reasons, or task-response boundary failures.
The standard-rate token cost is **$0.64398115**. All received request hashes
reconstruct from the archived messages and declared policies.

## Results

| Model | Pilot calls | Pilot cost, USD | Projected cost for its 90 full runs, USD |
|---|---:|---:|---:|
| Claude Sonnet 4.5 | 24 | 0.458151 | 126.60 |
| GPT-5 Nano | 24 | 0.065937 | 17.49 |
| Gemini 3.7 Flash | 24 | 0.119893 | 33.85 |
| Total | 72 | 0.643981 | 177.94 |

The full 270-run projection plus a 20% allowance is **$213.53**, reasonably
rounded to a **$215 planning budget**, not a spending guarantee. The earlier
$711 scenario assumed 4,000 thinking tokens per call for every model; the
observed Claude usage is much lower. The full batch has not been launched.

Thinking tokens per sampled call, mean (± sample standard deviation):

| Model | Game | Myth |
|---|---:|---:|
| Claude Sonnet 4.5 | 514 (±94) | 295 (±91) |
| GPT-5 Nano | 4,635 (±3,205) | 8,331 (±2,033) |
| Gemini 3.7 Flash | 356 (±279) | 1,255 (±459) |

Each model/task has 12 observations, except the Gemini game thinking counter:
11 are reported and one is missing. These are balanced replay-sample means,
not population-weighted means or estimates of behavioral effects.
Sonnet used 159–703 thinking tokens per request despite its 8,192 budget;
the budget is not an amount automatically consumed. GPT's high setting used
more tokens but remains inexpensive at its lower token rate.

See `summary.json` for unrounded results and verification counts.

## Profiles

| Model | Direct API | Reasoning sent | Temperature sent | Total output cap |
|---|---|---|---|---:|
| Claude Sonnet 4.5 | Anthropic | `thinking: {type: enabled, budget_tokens: 8192}` | Omitted | 64,000 |
| GPT-5 Nano | OpenAI | `reasoning_effort: high` | Omitted | 128,000 |
| Gemini 3.7 Flash | Google | `thinkingConfig: {thinkingLevel: high}` | 0.8 | 65,536 |

These are deliberately model-specific settings, not equivalent amounts of
computation. The total output caps are ceilings, not assumed consumption.
Gemini accepting 0.8 establishes request compatibility, not its causal effect
on sampling. GPT's request alias resolves to the documented
`gpt-5-nano-2025-08-07` snapshot; both IDs are retained in each call record.

## Sampling and execution

- Source: the 270 final full-state JSONs in
  `data/shared_runs/uploaders/vallinder/data/json/noise_experiments/negative_only_crossmodel_defectors_n5_20260825/`.
- 24 saved contexts per model: 2 population sizes × 2 tasks × 3 periods × 2
  contexts. Periods are rounds 1–3, 4–7, and 8–10. Within each game stratum,
  one sender and one receiver are sampled; myth strata have one game→myth
  and one myth→game context. The sampling seed is 20260908.
- Only accepted original LLM calls are eligible. Scripted forced-zero
  decisions, checkpoints, results-only JSONs, and rejected attempts are excluded.
- Exactly the archived role/content messages are resent, including their
  rolling memory. New answers do not replace old history or influence later
  pilot requests. This preserves context for measurement but does not simulate
  the trajectories that high reasoning might produce.
- Requests use the repository's explicit request-policy resolver and message
  adapters, then direct HTTP with a 1,200-second timeout. The older SDK's
  non-streaming large-output-limit check is not used. This pilot therefore
  does **not** establish that the batch runner works end to end with these caps.
- Three model workers; each model's requests are sequential. A transient HTTP
  error permits at most one retry; unknown transport outcomes stop that model.
  No provider fallback, response correction, or scientific-data upload occurs.

## Cost calculation

Current standard input/output USD rates per million tokens:

| Model | Input | Output, including thinking |
|---|---:|---:|
| Claude Sonnet 4.5 | 3.00 | 15.00 |
| GPT-5 Nano | 0.05 | 0.40 |
| Gemini 3.7 Flash | 0.75 | 3.75 |

Sources: [Anthropic pricing](https://platform.claude.com/docs/en/about-claude/pricing),
[OpenAI model/pricing](https://developers.openai.com/api/docs/models/gpt-5-nano),
[Google pricing](https://ai.google.dev/gemini-api/docs/pricing#gemini-3.7-flash).

Anthropic and OpenAI output totals already include thinking; do not add it
twice. Google's output total here is candidates plus thoughts, verified against
the provider's total-token count. One Gemini response omits the thoughts field;
the missing field stays null, and its total equals input plus candidate tokens.

Costs use recorded token counts at standard rates, not billing-dashboard
invoices. Cached input is not discounted in these estimates; Anthropic cache
read/write counts are checked to be zero. No Batch or Flex discount is assumed.

For each model, the 90-run projection sums each stratum's original number of
calls multiplied by its two pilot calls' mean cost. There are 6,378 accepted
original LLM calls per model. A separate 20% allowance is a planning contingency,
**not a confidence interval or guaranteed spending ceiling**.

The sample is small and deliberately balanced by role/task order within each
stratum. Changed future histories, retries, failures, and output lengths can
change the full-run bill. These projections are not evidence about cooperation
or a causal effect of reasoning.

## Evidence and reproduction

- `manifest.json`: policies, rates, sampling design, population counts, source
  locations and hashes, message hashes, and exact replay-script hash.
- `calls.jsonl`: actual request parameters/hash, raw usage metadata, returned
  model/response ID, finish reason, visible answer, and cost for each attempt.
  No credentials or thinking text are stored.
- `run_pilot.py`: replay script with the repository root now derived from its
  location, so it works in another checkout. The byte-identical script used for
  paid calls is preserved at [commit 47f83e7b](https://github.com/aronvallinder/nips-linguistic-evolution-toolkit/blob/47f83e7b41d7dea0bb430fe6f8e0c381680d2bd2/reports/reasoning_cost_pilot_2026_09_08/run_pilot.py).
  `manifest.json` retains that original script's hash; the portability fix does
  not rewrite the historical execution record.
- `summarize.py`: offline validation and weighted projection. It validates
  policy/source identity, returned models, token arithmetic, and task-response
  boundaries. Missing reasoning counters are not silently replaced by zero.

From a checkout containing the archived source runs, recompute the summary
without spending money:

```bash
python3 reports/reasoning_cost_pilot_2026_09_08/summarize.py
```

The replay script defaults to a free dry-run. Its `--execute` flag makes paid
calls for unfinished selections only and refuses changed policies or sources.

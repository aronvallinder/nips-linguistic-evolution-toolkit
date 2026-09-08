# Safeguards restart: the review contract

**Status: scope approved in merged PR 18; implementation under review.**
The replacement starts from shared main `5e00733a`. See
[the usage and walkthrough guide](safeguards-usage.md) for the implemented
boundaries and remaining merge gates. This is not a new experimental regime.

## Problem and boundaries

The same experiment must not silently change when another person runs it.
Different models may use different, deliberately chosen settings: equal
reasoning labels do not establish equal computation across vendors.

Preserve existing data, prompt templates, memory, noise, task order, seeds,
and retry behavior. No new experiments, canonical model profiles, automatic
research conclusions, or Watcher installation belong in this PR. Legacy
data remain readable; missing historical settings remain unknown.

## Four promises and their acceptance checks

| Promise | Evidence required before merge |
|---|---|
| **No silent machine-dependent settings.** New guarded runs resolve model, provider, reasoning, temperature policy, and output-cap policy before calling an API. Credentials do not choose the experiment. Overrides must be explicit and recorded. | Change environment keys and legacy knobs: the request stays the same, or startup fails clearly. Missing pinned credentials cannot trigger another provider. Missing settings fail before a paid call. |
| **The record matches the request.** Save the resolved request settings and each call's outcome, stop reason, and available usage. An omitted parameter means vendor default; missing usage is unknown, not zero. | Capture actual HTTP request bodies through the installed SDKs/local transports and compare them with saved metadata. Test omitted fields, output caps, failures, truncation status, and missing usage. No credentials in records. |
| **No silent condition mixing.** Resume preserves the recorded run identity. Comparisons declare which fields may differ, including model or replicate when intended. | Changing provider, reasoning, cap, prompts, memory/noise/task order, retry policy, or run identity triggers the appropriate resume/comparison rejection. A declared difference is accepted. Legacy comparisons require explicit acknowledgement, not guessed settings. |
| **Future changes cannot quietly bypass the checks.** Cover launchers, guarded readers, uploads, and new/changed output provenance in GitHub checks. | Deliberately remove pinning, introduce an undeclared difference, or omit provenance: CI fails. Verify required-check/review repository rules separately; a running workflow alone is not a merge gate. |

Covered entrypoints: both batch runners, the missing-run launcher, simulation
resume, the shared multi-run reader, the cooperation-ratio and resources-max
plots, and completed-run HF sync. Enumerate any remaining legacy entrypoints;
do not claim every ad-hoc script is guarded. Upload rejection must not turn a
completed scientific run into a failed run; incomplete artifacts stay excluded.

## Manual walkthrough: before coding, then before merge

Follow one example through this path:

1. **Configuration to runner:** `experiments/run_noisy_batch.py` expands the set.
2. **Runner to request:** `src/simulation.py` creates the client; `src/utils.py`
   selects the provider and builds the API request.
3. **Request to saved record:** compare the captured payload with run metadata
   and per-call outcomes, distinguishing requested values from unknown defaults.
4. **Saved record to analysis:** show an allowed comparison, then deliberately
   change one undeclared field and demonstrate rejection before output is written.

Before implementation, Ivar reviews these promises and the unchanged-condition
boundary. If the scope needs to expand, stop and explain why. Before merge,
require the acceptance checks, independent review, and Ivar's walkthrough.
Do not select paid smoke-run models or budgets without a resolved preflight.

## Where the old work lives

- PR 16 is superseded by this restart; its original branch is retained.
- PR 17 remains a separate draft. Its format-effect interpretation needs correction.
- Local archive: `archive/llm-safeguards-2026-09-07`, commit `0237659e`.
  It preserves the unfinished code and separate researchlog updates. It is
  unreviewed reference material, not code to merge wholesale or a cloud backup.
- Reuse only changes justified by the four promises. Experimental configurations,
  behavioral interventions, and scientific write-ups stay out of this replacement.

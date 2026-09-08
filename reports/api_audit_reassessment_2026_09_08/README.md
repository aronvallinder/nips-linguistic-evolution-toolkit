# API audit reassessment evidence — 2026-09-08

Read the [human-readable reassessment](../../docs/api-audit-reassessment-2026-09-08.md)
first. This directory contains retrospective review evidence, not new experiment
results or a new model-capability catalogue.

## Files

- `settings.json`: allowlisted aggregates for 4,129 historical inventory paths,
  3,661 distinct byte hashes after removing 468 exact-copy paths; representative
  source paths/hashes and two within-file washout signature profiles.
- `source-files.json`: every selected source path grouped by original byte hash.
  Distinct hashes do not establish independent replicates.
- `format.json`: 15 final format-study files with paths/hashes, selected metadata,
  per-run descriptive metrics, first myth instructions and error/correction examples.
  Whole later myths are not exported; their sampled prompt hashes are retained.
- `scan_inventory.py`, `summarize_inventory.py`, `summarize_format.py`:
  standard-library extraction helpers. Only existing local files are read;
  no vendor calls, credential reads, data downloads or uploads.

The selection is fixed by `TARGET_PARTS` in `scan_inventory.py` applied to
the historical inventory's `expset` column. Its inferred-provider column is
**not** used as evidence. Full-state fields, byte hashes, and saved round counts
are checked. The scan records missing/invalid paths and round-count mismatches;
all three lists were empty for this review. It is not a census of all attempted
experiments, all repository data, or files created after the historical inventory.

## Reproduce without overwriting the evidence

From the repository root, with the existing raw data available:

```bash
review=reports/api_audit_reassessment_2026_09_08
scratch=$(mktemp -d)
python3 "$review/scan_inventory.py" --repo-root "$PWD" --output "$scratch/scan.json"
python3 "$review/summarize_inventory.py" --repo-root "$PWD" --scan "$scratch/scan.json" --output "$scratch/settings.json" --sources-output "$scratch/source-files.json"
python3 "$review/summarize_format.py" --repo-root "$PWD" --output "$scratch/format.json"
diff -u "$review/settings.json" "$scratch/settings.json"
diff -u "$review/source-files.json" "$scratch/source-files.json"
diff -u "$review/format.json" "$scratch/format.json"
```

An isolated checkout can use `--repo-root /path/to/checkout-with-raw-data`;
do not copy credentials or change its experimental configuration. Missing data
must remain a reproduction limitation, not be filled with inferred values.

## Metric and evidence boundaries

Format outcomes use true dyad amounts, ordinary agents only, send/endowment
(the archived cells have a verified endowment of 5), positive-receipt return
ratios, final ordinary-agent balances, and accepted decision-response lengths.
Reported means and sample SDs aggregate the five run summaries in each arm.
Rejected attempts and error snapshots are not additional replicates. The arms
also differ in myth/self-context and retry policy, so these are descriptive,
not isolated treatment-effect estimates.

Numeric usage counters are values saved by the historical adapters. Missing
fields are kept separate from zero by this extraction, but it cannot undo
synthetic/default zeros already written by older adapters. Resolved request-model
IDs are not receipts of the model actually returned by the vendor. Top-level
run labels may fail to describe a resumed run's entire call history.

The original September 4 reports, CSVs and raw experiments are unchanged.

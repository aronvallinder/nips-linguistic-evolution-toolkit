# Repository guidance

This repository runs configuration-driven behavioral experiments with LLM agents. Preserve reproducibility, compatibility, and the distinction between experimental conditions when changing code or configuration.

## Code Review Rules

### Experimental semantics and provenance

- Flag changes that silently alter a condition's noise semantics, prompt regime, task order, history policy, seed, replicate identity, or output path. A deliberate change must remain explicit in configuration and be recorded in run metadata so old and new outputs cannot be mistaken for the same treatment.

### Completed-run boundary

- Treat only the final full-state JSON as proof that a run completed. Checkpoints, error snapshots, results-only JSON, logs, and transcripts must never make an incomplete run appear complete or be shared without their corresponding final JSON. Backup or upload failures must not invalidate a successfully completed scientific run.

### Backward compatibility

- Preserve legacy configuration keys, prompt-template behavior, and saved-data readers unless the change includes an explicit migration path and regression coverage. Never write credentials, access tokens, or secret-bearing environment contents to repository files, experiment artifacts, or logs.

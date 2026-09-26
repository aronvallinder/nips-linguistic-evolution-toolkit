"""Provenance manifest for analyses that re-aggregate the mixed-model tables.

scripts/check_safeguards.py requires every docs/figures/ folder to carry a
provenance.json whose outputs map equals the folder's tracked files. The
figures here are built from the validated decisions.csv (dyads) and games.csv
(eight-agent ladder); this records the same run finals, allowed differences
and pools that the scripts producing those tables use.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.experiment_condition import output_provenance  # noqa: E402
from scripts import analyze_mixed_model_dyads as dyads  # noqa: E402
from scripts import analyze_mixed_model_populations as populations  # noqa: E402

POOL_REASON = (
    "Mixed runs (dyads and eight-agent ladder) record one request plan per agent under llm.agents instead of a "
    "run-level llm.policy/llm.parameters block; every agent plan equals the September profile of its model "
    "(launcher plan step and per-call audit), so the mixed and September pools differ only in plan shape."
)


def write_provenance(output: Path, table_paths: set[str]) -> None:
    """Write output/provenance.json. `table_paths` are the ROOT-relative run paths read from the input tables."""
    dyad_mixed, dyad_september = dyads.final_paths()
    population_mixed, population_september = populations.final_paths()
    mixed = dyad_mixed + population_mixed
    september = dyad_september + population_september
    listed = {str(p.relative_to(ROOT)) for p in mixed + september}
    if listed != table_paths:
        raise SystemExit(f"Input tables and run finals disagree: {len(listed ^ table_paths)} paths differ")
    allowed = {**dyads.ALLOWED, **populations.ALLOWED}
    outputs = sorted(p for p in output.iterdir() if p.is_file() and p.name != "provenance.json" and not p.name.startswith("."))
    document = output_provenance(mixed + september, outputs, allowed, output_root=output,
                                 pools={"mixed": mixed, "september": september}, pool_reason=POOL_REASON)
    (output / "provenance.json").write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")

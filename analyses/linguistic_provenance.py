#!/usr/bin/env python3
"""Write provenance.json for docs/figures/linguistic_analysis_20260923/.

scripts/check_safeguards.py requires every docs/figures/ folder to carry a
provenance.json whose outputs map equals the folder's tracked files (including
the validation/ subfolder). The linguistic analysis reads only the
myth-bearing runs of the validated mixed-model tables (game-only runs have no
myths), so this records exactly those 156 run finals, with the allowed
differences and pools that analyses/_mixed_model_provenance.py uses for the
full tables.

Run last, after every analysis that writes into the folder:
  python3 analyses/linguistic_provenance.py
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
from analyses._mixed_model_provenance import POOL_REASON  # noqa: E402
from analyses.linguistic_corpus import run_list  # noqa: E402

OUTPUT = ROOT / "docs/figures/linguistic_analysis_20260923"


def main() -> None:
    used = {spec["path"] for size in (2, 8) for spec in run_list(size, ROOT)}
    dyad_mixed, dyad_september = dyads.final_paths()
    population_mixed, population_september = populations.final_paths()

    def keep(paths):
        return [p for p in paths if str(p.relative_to(ROOT)) in used]

    mixed = keep(dyad_mixed + population_mixed)
    september = keep(dyad_september + population_september)
    listed = {str(p.relative_to(ROOT)) for p in mixed + september}
    if listed != used:
        raise SystemExit(f"Myth runs and run finals disagree: {len(listed ^ used)} paths differ")
    # record where the finals really live (a worktree may reach them through a symlink)
    mixed, september = [p.resolve() for p in mixed], [p.resolve() for p in september]
    allowed = {**dyads.ALLOWED, **populations.ALLOWED}
    outputs = sorted(p for p in OUTPUT.rglob("*")
                     if p.is_file() and p.name != "provenance.json" and not p.name.startswith("."))
    document = output_provenance(mixed + september, outputs, allowed, output_root=OUTPUT,
                                 pools={"mixed": mixed, "september": september}, pool_reason=POOL_REASON)
    (OUTPUT / "provenance.json").write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(f"provenance: {len(mixed + september)} runs, {len(outputs)} outputs -> {OUTPUT / 'provenance.json'}")


if __name__ == "__main__":
    main()

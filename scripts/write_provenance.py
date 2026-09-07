"""Write a checked input/condition manifest for an analysis output directory."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from analyses._shared import write_output_provenance


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("runs", nargs="+")
    parser.add_argument("--comparison-spec", type=Path)
    parser.add_argument("--legacy-reason")
    args = parser.parse_args()
    allowed = json.loads(args.comparison_spec.read_text()) if args.comparison_spec else {}
    write_output_provenance(args.output, args.runs, allowed_differences=allowed, legacy_reason=args.legacy_reason)


if __name__ == "__main__":
    main()

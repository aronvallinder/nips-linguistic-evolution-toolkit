"""Merge CSL-JSON files from the active project's references/bib into references.json."""

import json

from paths import manuscript_quarto_dir, references_bib_dir


def merge():
    bib_dir = references_bib_dir()
    output = manuscript_quarto_dir() / "references.json"
    records = []
    for bib_file in sorted(bib_dir.glob("*.json")):
        try:
            data = json.loads(bib_file.read_text(encoding="utf-8"))
            if isinstance(data, list):
                records.extend(data)
            else:
                records.append(data)
        except json.JSONDecodeError as e:
            print(f"Warning: skipping {bib_file.name}: {e}")

    output.write_text(
        json.dumps(records, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Merged {len(records)} records -> {output}")


if __name__ == "__main__":
    merge()

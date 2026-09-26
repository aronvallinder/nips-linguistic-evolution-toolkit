#!/usr/bin/env python3
"""Validate the small, repo-native project-memory index.

This checks structure and local links. It cannot decide whether a scientific
claim is true; agents must still follow the source hierarchy in WORKFLOW.md.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MEMORY = ROOT / "docs" / "project-memory"
DECISIONS = MEMORY / "decisions"
REQUIRED_FILES = (
    MEMORY / "README.md",
    MEMORY / "CURRENT.md",
    MEMORY / "WORKFLOW.md",
    MEMORY / "sources" / "README.md",
    DECISIONS / "TEMPLATE.md",
)
REQUIRED_DECISION_FIELDS = (
    "Recorded / last verified:",
    "Decision status:",
    "Scope:",
    "Decision authority:",
    "Implementation status:",
    "## Decision and rationale",
    "## Evidence",
    "## Chronology and supersession",
    "## Unresolved / next evidence",
)
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^# (D\d{3}) — ", re.MULTILINE)


def local_link_target(source: Path, raw_target: str) -> Path | None:
    target = raw_target.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    target = target.split("#", 1)[0]
    if not target or "://" in target or target.startswith("/"):
        return None
    return (source.parent / target).resolve()


def main() -> int:
    errors: list[str] = []

    for path in REQUIRED_FILES:
        if not path.is_file():
            errors.append(f"missing required file: {path.relative_to(ROOT)}")

    decision_paths = sorted(DECISIONS.glob("[0-9][0-9][0-9]-*.md"))
    if not decision_paths:
        errors.append("no numbered decision records found")

    seen_ids: set[str] = set()
    index_text = (MEMORY / "README.md").read_text() if (MEMORY / "README.md").is_file() else ""
    for path in decision_paths:
        text = path.read_text()
        heading = HEADING_RE.search(text)
        if not heading:
            errors.append(f"{path.relative_to(ROOT)}: missing DNNN title")
            continue
        decision_id = heading.group(1)
        if decision_id in seen_ids:
            errors.append(f"duplicate decision id: {decision_id}")
        seen_ids.add(decision_id)
        if path.name[:3] != decision_id[1:]:
            errors.append(f"{path.relative_to(ROOT)}: filename/id mismatch")
        for field in REQUIRED_DECISION_FIELDS:
            if field not in text:
                errors.append(f"{path.relative_to(ROOT)}: missing {field}")
        if path.name not in index_text:
            errors.append(f"{path.relative_to(ROOT)}: absent from project-memory index")

    markdown_paths = [path for path in MEMORY.rglob("*.md")]
    for path in markdown_paths:
        for raw_target in LINK_RE.findall(path.read_text()):
            target = local_link_target(path, raw_target)
            if target is not None and not target.exists():
                errors.append(
                    f"{path.relative_to(ROOT)}: broken local link {raw_target}"
                )

    if errors:
        print("Project-memory validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "Project-memory validation passed: "
        f"{len(decision_paths)} decisions, {len(markdown_paths)} Markdown files."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())


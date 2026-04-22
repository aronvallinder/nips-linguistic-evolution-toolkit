"""Resolve repository root, active project slug, and manuscript paths."""

from pathlib import Path

_SKILL_DIR = Path(__file__).resolve().parent


def repo_root() -> Path:
    """Return repository root (directory that contains ``.claude/``)."""
    return _SKILL_DIR.parent.parent.parent


def active_project_slug() -> str:
    """Read the active project slug from ``projects/active_project``."""
    root = repo_root()
    pointer = root / "projects" / "active_project"
    if not pointer.is_file():
        rel = pointer.relative_to(root)
        raise FileNotFoundError(
            f"Missing {rel}; set the slug (e.g. neurips-2026-mls)."
        )
    text = pointer.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError("projects/active_project is empty")
    return text


def manuscript_quarto_dir() -> Path:
    """Quarto project dir: ``projects/<slug>/manuscript``."""
    slug = active_project_slug()
    return repo_root() / "projects" / slug / "manuscript"


def references_bib_dir() -> Path:
    """CSL-JSON shards: ``references/bib`` (repo-wide)."""
    return repo_root() / "references" / "bib"

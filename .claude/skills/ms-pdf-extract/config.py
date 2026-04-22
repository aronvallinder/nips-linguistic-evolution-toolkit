"""Shared configuration and paths for the ms-pdf-extract skill."""

import os
from pathlib import Path

import yaml

SKILL_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SKILL_DIR.parent.parent.parent
REFS_DIR = PROJECT_DIR / "references"
PDF_DIR = REFS_DIR / "pdfs"
MD_DIR = REFS_DIR / "md"
BIB_DIR = REFS_DIR / "bib"
NOTES_DIR = REFS_DIR / "notes"

CONFIG = yaml.safe_load((SKILL_DIR / "config.yml").read_text())
_local_cfg = SKILL_DIR / "config.local.yml"
if _local_cfg.exists():
    CONFIG.update(yaml.safe_load(_local_cfg.read_text()) or {})
MODEL = CONFIG["model"]
PROMPT = (SKILL_DIR / "prompt.md").read_text().strip()
NOTE_TEMPLATE = (SKILL_DIR / "note_prompt.md").read_text().strip()
EXPLORE_TEMPLATE = (SKILL_DIR / "explore_prompt.md").read_text().strip()
LEADS_DIR = REFS_DIR / "leads"
# No global MANUSCRIPT_DIR — project-specific, passed by agents


def load_env():
    """Load .env file from project root if API keys not already set."""
    env_file = PROJECT_DIR / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

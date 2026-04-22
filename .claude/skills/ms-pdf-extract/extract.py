"""PDF extraction: send PDFs to an LLM and get structured markdown + bibliography."""

import json
import os
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.messages import BinaryContent

from config import BIB_DIR, MD_DIR, MODEL, PDF_DIR, PROMPT


# --- Pydantic models ---


class Author(BaseModel):
    family: str
    given: str


class Issued(BaseModel):
    date_parts: list[list[int]] = Field(alias="date-parts")
    model_config = {"populate_by_name": True}


class BibRecord(BaseModel):
    type: str = Field(description="CSL type, e.g. article-journal, paper-conference, book")
    author: list[Author]
    title: str
    container_title: str | None = Field(None, alias="container-title")
    volume: str | None = None
    issue: str | None = None
    page: str | None = None
    issued: Issued | None = None
    DOI: str | None = None
    URL: str | None = None
    model_config = {"populate_by_name": True}


class PaperExtraction(BaseModel):
    key: str = Field(description="Reference key: firstauthorlastname + year, lowercase")
    bib: BibRecord
    markdown: str = Field(description="Full PDF content as markdown")


# --- Agent (lazy init) ---

_agent: Agent[None, PaperExtraction] | None = None


def _get_agent() -> Agent[None, PaperExtraction]:
    global _agent
    if _agent is None:
        _agent = Agent(MODEL, output_type=PaperExtraction, system_prompt=PROMPT)
    return _agent


# --- Core functions ---


def resolve_key(key: str, title: str) -> str:
    """Resolve key conflicts by appending a-z suffix if needed."""
    bib_path = BIB_DIR / f"{key}.json"
    if not bib_path.exists():
        return key

    existing = json.loads(bib_path.read_text())
    if existing.get("title", "").lower().strip() == title.lower().strip():
        return key

    for suffix in "abcdefghijklmnopqrstuvwxyz":
        candidate = f"{key}{suffix}"
        candidate_path = BIB_DIR / f"{candidate}.json"
        if not candidate_path.exists():
            return candidate
        existing = json.loads(candidate_path.read_text())
        if existing.get("title", "").lower().strip() == title.lower().strip():
            return candidate

    raise ValueError(f"Too many papers with key {key}")


def _find_existing_md(key: str) -> Path | None:
    """Find an existing markdown file for a given key across all slug dirs."""
    for md in MD_DIR.rglob(f"{key}.md"):
        if not md.is_symlink():
            return md
    return None


def find_pending(scan_dir: Path) -> list[Path]:
    """Find PDFs that don't have a corresponding .md file."""
    pending = []
    for pdf in sorted(scan_dir.rglob("*.pdf")):
        md_path = MD_DIR / f"{pdf.stem}.md"
        if not md_path.exists():
            pending.append(pdf)
    return pending


async def process(pdf_path: Path) -> tuple[str, Path, Path, Path, bool, str | None]:
    """Extract a single PDF. Returns (key, pdf_path, md_path, bib_path, is_duplicate, renamed_from)."""
    orig_name = pdf_path.name

    # Async LLM call
    result = await _get_agent().run(
        [
            BinaryContent(data=pdf_path.read_bytes(), media_type="application/pdf"),
            "Extract from this PDF.",
        ]
    )
    extraction = result.output
    key = extraction.key
    bib_dict = extraction.bib.model_dump(by_alias=True, exclude_none=True)

    key = resolve_key(key, bib_dict.get("title", ""))
    bib_dict["id"] = key

    BIB_DIR.mkdir(parents=True, exist_ok=True)
    bib_path = BIB_DIR / f"{key}.json"
    md_path = MD_DIR / f"{key}.md"
    md_path.parent.mkdir(parents=True, exist_ok=True)

    is_duplicate = bib_path.exists()

    if is_duplicate:
        existing_md = _find_existing_md(key)
        if existing_md and not md_path.exists():
            rel_target = os.path.relpath(existing_md, md_path.parent)
            md_path.symlink_to(rel_target)
        elif not existing_md and not md_path.exists():
            md_path.write_text(extraction.markdown)
    else:
        bib_path.write_text(json.dumps(bib_dict, indent=2, ensure_ascii=False) + "\n")
        md_path.write_text(extraction.markdown)

    renamed_from = None
    new_pdf_path = pdf_path.parent / f"{key}.pdf"
    if new_pdf_path != pdf_path and not new_pdf_path.exists():
        pdf_path.rename(new_pdf_path)
        renamed_from = orig_name

    return key, pdf_path, md_path, bib_path, is_duplicate, renamed_from

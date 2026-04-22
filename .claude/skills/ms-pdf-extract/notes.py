"""Note generation: create relevance notes and exploration notes for extracted papers."""


import subprocess
from pathlib import Path

from jinja2 import Environment
from pydantic import BaseModel, Field
from pydantic_ai import Agent

from config import (
    BIB_DIR,
    EXPLORE_TEMPLATE,
    LEADS_DIR,
    MD_DIR,
    MODEL,
    NOTE_TEMPLATE,
    NOTES_DIR,
    PDF_DIR,
    PROJECT_DIR,
)
from extract import process


class RelevanceNote(BaseModel):
    markdown: str = Field(description="The full relevance note as markdown following the template")


class ExplorationResult(BaseModel):
    note: str = Field(description="Relevance note as markdown")
    leads: str = Field(description="Leads file as markdown listing references worth exploring")


# --- Agent (lazy init) ---

_note_agent: Agent[None, RelevanceNote] | None = None
_explore_agent: Agent[None, ExplorationResult] | None = None


def _get_note_agent() -> Agent[None, RelevanceNote]:
    global _note_agent
    if _note_agent is None:
        _note_agent = Agent(MODEL, output_type=RelevanceNote)
    return _note_agent


def _get_explore_agent() -> Agent[None, ExplorationResult]:
    global _explore_agent
    if _explore_agent is None:
        _explore_agent = Agent(MODEL, output_type=ExplorationResult)
    return _explore_agent


# --- Helper functions ---


def _render_note_prompt(template=None, **kwargs) -> str:
    """Render a prompt template with Jinja2. Uses NOTE_TEMPLATE by default."""
    env = Environment(keep_trailing_newline=True)
    tmpl = env.from_string(template or NOTE_TEMPLATE)
    return tmpl.render(**kwargs)


def _grep_manuscript(key: str) -> str:
    """Find all lines in any project manuscript that cite this key."""
    projects_dir = PROJECT_DIR / "projects"
    if not projects_dir.exists():
        return f"No citations of @{key} found (no projects/ dir)."
    result = subprocess.run(
        [
            "grep", "-rn", "--include=*.md",
            "--include=*.qmd", f"@{key}",
            str(projects_dir),
        ],
        capture_output=True, text=True, timeout=10,
    )
    return (
        result.stdout.strip()
        or f"No citations of @{key} found in manuscripts."
    )


def _load_project_description() -> str:
    """Load project description from the active project's PROJECT.md."""
    pointer = PROJECT_DIR / "projects" / "active_project"
    if pointer.exists():
        slug = pointer.read_text().strip()
        path = PROJECT_DIR / "projects" / slug / "PROJECT.md"
        if path.exists():
            return path.read_text().strip()
    # Fallback: root PROJECT.md
    path = PROJECT_DIR / "PROJECT.md"
    if not path.exists():
        return ""
    return path.read_text().strip()


async def _get_paper_content(key: str) -> str:
    """Load paper content, extracting from PDF if needed (async)."""
    for md in MD_DIR.rglob(f"{key}.md"):
        content = md.read_text()
        return content[:3000] + ("\n...[truncated]" if len(content) > 3000 else "")

    # No extraction -- try to find and extract the PDF
    pdf_candidates = list(PDF_DIR.rglob(f"{key}.pdf"))
    if pdf_candidates:
        print(f"  No markdown for {key}, extracting from {pdf_candidates[0].name}...")
        _, _, md_path, _, _, _ = await process(pdf_candidates[0])
        content = md_path.read_text()
        return content[:3000] + ("\n...[truncated]" if len(content) > 3000 else "")

    raise FileNotFoundError(
        f"No markdown extraction and no PDF found for '{key}'. "
        f"Add a PDF to {PDF_DIR.relative_to(PROJECT_DIR)} and try again."
    )


async def generate_note(
    key: str, context: str = "", slug: str = ""
) -> Path:
    """Generate (or append to) a relevance note for a paper."""
    if not slug:
        raise ValueError(
            "--slug is required for note generation"
        )
    out_dir = NOTES_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    note_path = out_dir / f"{key}.md"

    existing_note = ""
    is_append = note_path.exists()
    if is_append:
        existing_note = note_path.read_text().strip()

    bib_path = BIB_DIR / f"{key}.json"
    if not bib_path.exists():
        raise FileNotFoundError(
            f"No bib entry for '{key}'. Create {bib_path.relative_to(PROJECT_DIR)} first "
            f"(e.g., extract the PDF or add manually)."
        )
    bib_json = bib_path.read_text()

    paper_content = await _get_paper_content(key)

    prompt = _render_note_prompt(
        citekey=key,
        is_append=is_append,
        bib_json=bib_json,
        paper_content=paper_content,
        project_description=_load_project_description(),
        citation_context=_grep_manuscript(key),
        user_context=context,
        existing_note=existing_note,
    )

    # Async LLM call
    result = await _get_note_agent().run(prompt)

    if is_append:
        with open(note_path, "a") as f:
            f.write("\n\n" + result.output.markdown.strip() + "\n")
    else:
        note_path.write_text(result.output.markdown.strip() + "\n")

    return note_path


async def generate_exploration(
    key: str, context: str = "", slug: str = ""
) -> tuple[Path, Path]:
    """Generate an exploration note + leads file.

    Returns (note_path, leads_path).
    """
    if not slug:
        raise ValueError(
            "--slug is required for exploration"
        )
    notes_out = NOTES_DIR / slug
    leads_out = LEADS_DIR / slug
    notes_out.mkdir(parents=True, exist_ok=True)
    leads_out.mkdir(parents=True, exist_ok=True)

    note_path = notes_out / f"{key}.md"
    leads_path = leads_out / f"{key}.md"

    bib_path = BIB_DIR / f"{key}.json"
    if not bib_path.exists():
        raise FileNotFoundError(
            f"No bib entry for '{key}'. Create {bib_path.relative_to(PROJECT_DIR)} first "
            f"(e.g., extract the PDF or add manually)."
        )
    bib_json = bib_path.read_text()

    paper_content = await _get_paper_content(key)

    prompt = _render_note_prompt(
        template=EXPLORE_TEMPLATE,
        citekey=key,
        is_append=False,
        bib_json=bib_json,
        paper_content=paper_content,
        project_description=_load_project_description(),
        citation_context=_grep_manuscript(key),
        user_context=context,
        existing_note="",
    )

    result = await _get_explore_agent().run(prompt)

    # Write note (append if exists)
    if note_path.exists():
        with open(note_path, "a") as f:
            f.write("\n\n" + result.output.note.strip() + "\n")
    else:
        note_path.write_text(result.output.note.strip() + "\n")

    # Write leads (overwrite — leads are regenerated each time)
    leads_path.write_text(result.output.leads.strip() + "\n")

    return note_path, leads_path

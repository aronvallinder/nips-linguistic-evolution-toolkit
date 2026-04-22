"""Tests for ms-pdf-extract skill — focused on critical edge cases that could fail silently.

Tests the refactored modules: config.py, extract.py, notes.py.
All LLM calls are mocked. Each test is independent via tmp_path.
"""

import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Ensure skill directory is importable
SKILL_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SKILL_DIR))


# ---------------------------------------------------------------------------
# Fixture: redirect all path constants to tmp_path
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def isolated_dirs(tmp_path, monkeypatch):
    """Redirect all directory constants in config, extract, and notes to tmp_path."""
    layout = {
        "PROJECT_DIR": tmp_path,
        "REFS_DIR": tmp_path / "refs",
        "PDF_DIR": tmp_path / "refs" / "pdfs",
        "MD_DIR": tmp_path / "refs" / "md",
        "BIB_DIR": tmp_path / "refs" / "bib",
        "NOTES_DIR": tmp_path / "refs" / "notes",
        "MANUSCRIPT_DIR": tmp_path / "manuscript",
    }
    for v in layout.values():
        v.mkdir(parents=True, exist_ok=True)

    import config
    import extract
    import notes

    for mod in (config, extract, notes):
        for k, v in layout.items():
            if hasattr(mod, k):
                monkeypatch.setattr(mod, k, v)

    return layout


# ---------------------------------------------------------------------------
# 1. Note generation guards
# ---------------------------------------------------------------------------

class TestNoteGenerationGuards:

    @pytest.mark.asyncio
    async def test_no_bib_entry_raises(self, isolated_dirs):
        """generate_note must raise FileNotFoundError when bib is missing."""
        from notes import generate_note
        with pytest.raises(FileNotFoundError, match="No bib entry"):
            await generate_note("nonexistent2024")

    @pytest.mark.asyncio
    async def test_no_markdown_and_no_pdf_raises(self, isolated_dirs):
        """With bib but no markdown AND no PDF, should raise FileNotFoundError."""
        from notes import generate_note
        bib = isolated_dirs["BIB_DIR"] / "smith2024.json"
        bib.write_text(json.dumps({"id": "smith2024", "title": "Test Paper"}))

        with pytest.raises(FileNotFoundError, match="No markdown extraction and no PDF"):
            await generate_note("smith2024")

    @pytest.mark.asyncio
    async def test_no_markdown_but_pdf_triggers_extraction(self, isolated_dirs):
        """If bib + PDF exist but no markdown, should call process() to extract."""
        from notes import generate_note

        d = isolated_dirs
        bib = d["BIB_DIR"] / "jones2024.json"
        bib.write_text(json.dumps({"id": "jones2024", "title": "A Paper"}))

        pdf = d["PDF_DIR"] / "jones2024.pdf"
        pdf.write_bytes(b"%PDF-fake")

        md_path = d["MD_DIR"] / "jones2024.md"

        async def fake_process(path):
            md_path.write_text("Extracted content here")
            return ("jones2024", path, md_path, bib, False, None)

        mock_note_result = MagicMock()
        mock_note_result.output.markdown = "# jones2024\n## General relevance\nRelevant."

        mock_agent = MagicMock()
        mock_agent.run = AsyncMock(return_value=mock_note_result)

        with patch("notes.process", side_effect=fake_process) as mock_proc, \
             patch("notes._get_note_agent", return_value=mock_agent), \
             patch("notes._grep_manuscript", return_value="No citations found"), \
             patch("notes._load_project_description", return_value=""):
            result = await generate_note("jones2024")
            mock_proc.assert_called_once_with(pdf)
            assert result.exists()


# ---------------------------------------------------------------------------
# 2. Append mode correctness
# ---------------------------------------------------------------------------

class TestAppendMode:

    def _setup_bib_and_md(self, dirs, key="lee2023"):
        bib = dirs["BIB_DIR"] / f"{key}.json"
        bib.write_text(json.dumps({"id": key, "title": "Test"}))
        md = dirs["MD_DIR"] / f"{key}.md"
        md.write_text("Paper content for testing.")
        return bib, md

    def _mock_note_agent(self, markdown_output):
        mock_result = MagicMock()
        mock_result.output.markdown = markdown_output
        mock_agent = MagicMock()
        mock_agent.run = AsyncMock(return_value=mock_result)
        return mock_agent

    @pytest.mark.asyncio
    async def test_first_run_creates_new_file(self, isolated_dirs):
        """First run should create the note file (write, not append)."""
        from notes import generate_note
        self._setup_bib_and_md(isolated_dirs)

        agent = self._mock_note_agent("# lee2023\n## General relevance\nGood paper.")

        with patch("notes._get_note_agent", return_value=agent), \
             patch("notes._grep_manuscript", return_value="No citations found"), \
             patch("notes._load_project_description", return_value=""):
            note = await generate_note("lee2023", context="first context")

        content = note.read_text()
        assert content.startswith("# lee2023")
        assert "General relevance" in content

    @pytest.mark.asyncio
    async def test_second_run_appends_does_not_overwrite(self, isolated_dirs):
        """Second run should append, preserving original content."""
        from notes import generate_note
        self._setup_bib_and_md(isolated_dirs)

        note_path = isolated_dirs["NOTES_DIR"] / "lee2023.md"
        original = "# lee2023\n## General relevance\nOriginal content.\n"
        note_path.write_text(original)

        agent = self._mock_note_agent("## Context: new angle\nNew section.")

        with patch("notes._get_note_agent", return_value=agent), \
             patch("notes._grep_manuscript", return_value="No citations found"), \
             patch("notes._load_project_description", return_value=""):
            await generate_note("lee2023", context="second context")

        content = note_path.read_text()
        assert "Original content." in content
        assert "new angle" in content
        assert content.count("# lee2023") == 1  # header not duplicated

    @pytest.mark.asyncio
    async def test_append_passes_is_append_flag_to_template(self, isolated_dirs):
        """When note exists, the rendered prompt should contain APPEND mode."""
        from notes import generate_note
        self._setup_bib_and_md(isolated_dirs)

        note_path = isolated_dirs["NOTES_DIR"] / "lee2023.md"
        note_path.write_text("# lee2023\nExisting.\n")

        prompts_captured = []
        mock_result = MagicMock()
        mock_result.output.markdown = "## Context: x\nStuff."
        mock_agent = MagicMock()

        async def capture_run(prompt, *a, **kw):
            prompts_captured.append(prompt)
            return mock_result

        mock_agent.run = capture_run

        with patch("notes._get_note_agent", return_value=mock_agent), \
             patch("notes._grep_manuscript", return_value="No citations found"), \
             patch("notes._load_project_description", return_value=""):
            await generate_note("lee2023")

        assert len(prompts_captured) == 1
        assert "APPEND" in prompts_captured[0]


# ---------------------------------------------------------------------------
# 3. Template rendering
# ---------------------------------------------------------------------------

class TestTemplateRendering:

    def _render(self, **overrides):
        from notes import _render_note_prompt
        defaults = dict(
            citekey="test2024",
            is_append=False,
            bib_json='{"id": "test2024"}',
            paper_content="Some content.",
            project_description="A project about X.",
            citation_context="manuscript.md:10: [@test2024]",
            user_context="Testing relevance",
            existing_note="",
        )
        defaults.update(overrides)
        return _render_note_prompt(**defaults)

    def test_all_fields_populated(self):
        """All Jinja2-controlled sections should render when fields are provided."""
        result = self._render()
        # Conditional sections should be present
        assert "Project description" in result
        assert "Why this note is being generated" in result
        assert "NEW NOTE" in result

    def test_no_project_description_omits_section(self):
        result = self._render(project_description="")
        assert "Project description" not in result

    def test_no_user_context_omits_section(self):
        result = self._render(user_context="")
        assert "Why this note is being generated" not in result

    def test_no_citation_context_still_renders(self):
        """citation_context is not conditional — it always renders."""
        result = self._render(citation_context="No citations of @test2024 found in manuscript.")
        # The Manuscript citations header is always present
        assert "Manuscript citations" in result

    def test_append_mode_renders_append_instructions(self):
        result = self._render(is_append=True, existing_note="# test2024\nOld stuff.")
        assert "APPEND" in result
        assert "Existing note" in result  # the existing_note section header renders
        assert "NEW NOTE" not in result

    def test_new_mode_renders_new_instructions(self):
        result = self._render(is_append=False)
        assert "NEW NOTE" in result
        assert "APPEND" not in result

    def test_existing_note_omitted_when_empty(self):
        """When existing_note is empty, the existing note section should not render."""
        result = self._render(is_append=False, existing_note="")
        assert "Existing note (DO NOT repeat" not in result


# ---------------------------------------------------------------------------
# 4. Key resolution
# ---------------------------------------------------------------------------

class TestKeyResolution:

    def test_new_key_used_as_is(self, isolated_dirs):
        from extract import resolve_key
        assert resolve_key("novel2024", "A Novel Paper") == "novel2024"

    def test_existing_key_same_title_returns_same(self, isolated_dirs):
        from extract import resolve_key
        bib = isolated_dirs["BIB_DIR"] / "smith2024.json"
        bib.write_text(json.dumps({"title": "Same Title"}))
        assert resolve_key("smith2024", "Same Title") == "smith2024"

    def test_existing_key_same_title_case_insensitive(self, isolated_dirs):
        from extract import resolve_key
        bib = isolated_dirs["BIB_DIR"] / "smith2024.json"
        bib.write_text(json.dumps({"title": "Same Title"}))
        assert resolve_key("smith2024", "  same title  ") == "smith2024"

    def test_existing_key_different_title_gets_suffix(self, isolated_dirs):
        from extract import resolve_key
        bib = isolated_dirs["BIB_DIR"] / "smith2024.json"
        bib.write_text(json.dumps({"title": "First Paper"}))
        assert resolve_key("smith2024", "Different Paper") == "smith2024a"

    def test_multiple_conflicts_increment_suffix(self, isolated_dirs):
        from extract import resolve_key
        for name, title in [("smith2024", "Paper A"), ("smith2024a", "Paper B")]:
            (isolated_dirs["BIB_DIR"] / f"{name}.json").write_text(json.dumps({"title": title}))
        assert resolve_key("smith2024", "Paper C") == "smith2024b"


# ---------------------------------------------------------------------------
# 5. Manuscript grepping
# ---------------------------------------------------------------------------

class TestGrepManuscript:

    def test_key_found_returns_matching_lines(self, isolated_dirs):
        from notes import _grep_manuscript
        ms = isolated_dirs["MANUSCRIPT_DIR"] / "intro.md"
        ms.write_text("As shown by [@chen2023], this is important.\n")
        result = _grep_manuscript("chen2023")
        assert "chen2023" in result
        assert "important" in result

    def test_key_not_found_returns_message(self, isolated_dirs):
        from notes import _grep_manuscript
        ms = isolated_dirs["MANUSCRIPT_DIR"] / "intro.md"
        ms.write_text("Nothing relevant here.\n")
        result = _grep_manuscript("missing2024")
        assert "No citations" in result

    def test_key_with_special_chars_does_not_crash(self, isolated_dirs):
        """grep receives @key — apostrophes etc. should not crash."""
        from notes import _grep_manuscript
        ms = isolated_dirs["MANUSCRIPT_DIR"] / "intro.md"
        ms.write_text("Some text.\n")
        result = _grep_manuscript("o'brien2024")
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# 6. Project description loading
# ---------------------------------------------------------------------------

class TestProjectDescription:

    def test_project_md_exists(self, isolated_dirs):
        from notes import _load_project_description
        pm = isolated_dirs["PROJECT_DIR"] / "PROJECT.md"
        pm.write_text("This project studies X.")
        assert "studies X" in _load_project_description()

    def test_missing_project_md_raises(self, isolated_dirs):
        from notes import _load_project_description
        with pytest.raises(FileNotFoundError, match="PROJECT.md not found"):
            _load_project_description()

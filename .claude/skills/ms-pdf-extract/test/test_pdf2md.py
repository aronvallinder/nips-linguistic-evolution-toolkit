"""Tests for the pdf2md extraction tool.

Uses a 2-page fixture PDF (arxiv:2302.12854, "The Micro-Paper" by Elavsky 2023).
Runs a real Gemini API call — requires GOOGLE_API_KEY.
"""

import json
import os
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pdf2md

FIXTURE = Path(__file__).resolve().parent / "fixture.pdf"
TEST_DIR = Path(__file__).resolve().parent / "tmp"


def setup():
    """Create a temporary directory structure mirroring the real layout."""
    if TEST_DIR.exists():
        shutil.rmtree(TEST_DIR)
    pdfs = TEST_DIR / "pdfs" / "test-slug"
    pdfs.mkdir(parents=True)
    shutil.copy(FIXTURE, pdfs / "test-paper.pdf")
    return TEST_DIR


def teardown():
    if TEST_DIR.exists():
        shutil.rmtree(TEST_DIR)


def test_extract_pdf():
    """Test that Gemini returns valid structured output."""
    result = pdf2md.extract_pdf(FIXTURE)

    # Should be a PaperExtraction model
    key = result.key
    assert key == key.lower(), f"Key should be lowercase: {key}"
    assert " " not in key, f"Key should not contain spaces: {key}"
    assert any(c.isdigit() for c in key), f"Key should contain a year: {key}"
    assert any(c.isalpha() for c in key), f"Key should contain letters: {key}"

    assert len(result.bib.author) >= 1, "Should have at least one author"
    assert "micro" in result.bib.title.lower(), f"Title should mention 'micro': {result.bib.title}"

    assert len(result.markdown) > 500, f"Markdown too short: {len(result.markdown)} chars"
    assert "micro" in result.markdown.lower(), "Markdown should mention 'micro-paper'"

    print(f"  key: {key}")
    print(f"  title: {result.bib.title}")
    print(f"  authors: {len(result.bib.author)}")
    print(f"  markdown: {len(result.markdown)} chars")


def test_full_pipeline():
    """Test the full pipeline: extract, write files, rename PDF."""
    tmp = setup()

    orig_pdf_dir = pdf2md.PDF_DIR
    orig_md_dir = pdf2md.MD_DIR
    orig_bib_dir = pdf2md.BIB_DIR
    pdf2md.PDF_DIR = tmp / "pdfs"
    pdf2md.MD_DIR = tmp / "md"
    pdf2md.BIB_DIR = tmp / "bib"

    try:
        pdf_path = tmp / "pdfs" / "test-slug" / "test-paper.pdf"
        key, new_pdf, md_path, bib_path, is_dup, _ = pdf2md.process(pdf_path)

        assert bib_path.exists(), f"Bib file not created: {bib_path}"
        assert md_path.exists(), f"Markdown file not created: {md_path}"
        assert new_pdf.exists(), f"PDF not found at new path: {new_pdf}"
        assert new_pdf.name == f"{key}.pdf", f"PDF not renamed: {new_pdf.name}"
        assert not (tmp / "pdfs" / "test-slug" / "test-paper.pdf").exists(), "Old PDF still exists"

        bib = json.loads(bib_path.read_text())
        assert bib["id"] == key, f"Bib id mismatch: {bib['id']} != {key}"
        assert "test-slug" in str(md_path), f"Markdown not in slug dir: {md_path}"
        assert not is_dup, "Should not be a duplicate on first run"

        print(f"  key: {key}")
        print(f"  pdf: {new_pdf.relative_to(tmp)}")
        print(f"  md: {md_path.relative_to(tmp)}")
        print(f"  bib: {bib_path.relative_to(tmp)}")

    finally:
        pdf2md.PDF_DIR = orig_pdf_dir
        pdf2md.MD_DIR = orig_md_dir
        pdf2md.BIB_DIR = orig_bib_dir


def test_duplicate_detection():
    """Test that duplicate papers get symlinked instead of re-extracted."""
    tmp = setup()

    slug2 = tmp / "pdfs" / "other-slug"
    slug2.mkdir(parents=True)
    shutil.copy(FIXTURE, slug2 / "same-paper.pdf")

    orig_pdf_dir = pdf2md.PDF_DIR
    orig_md_dir = pdf2md.MD_DIR
    orig_bib_dir = pdf2md.BIB_DIR
    pdf2md.PDF_DIR = tmp / "pdfs"
    pdf2md.MD_DIR = tmp / "md"
    pdf2md.BIB_DIR = tmp / "bib"

    try:
        pdf1 = tmp / "pdfs" / "test-slug" / "test-paper.pdf"
        key1, _, md1, _, dup1, _ = pdf2md.process(pdf1)
        assert not dup1, "First extraction should not be duplicate"
        assert md1.exists() and not md1.is_symlink(), "First md should be a real file"

        pdf2 = tmp / "pdfs" / "other-slug" / "same-paper.pdf"
        key2, _, md2, _, dup2, _ = pdf2md.process(pdf2)
        assert dup2, "Second extraction should be detected as duplicate"
        assert key2 == key1, f"Keys should match: {key1} vs {key2}"
        assert md2.is_symlink(), f"Second md should be a symlink: {md2}"

        print(f"  key: {key1}")
        print(f"  md1 (real): {md1.relative_to(tmp)}")
        print(f"  md2 (symlink): {md2.relative_to(tmp)} -> {os.readlink(md2)}")

    finally:
        pdf2md.PDF_DIR = orig_pdf_dir
        pdf2md.MD_DIR = orig_md_dir
        pdf2md.BIB_DIR = orig_bib_dir
        teardown()


def main():
    pdf2md._load_env()
    if not os.environ.get("GOOGLE_API_KEY"):
        print("SKIP: GOOGLE_API_KEY not set")
        return

    tests = [
        ("extract_pdf", test_extract_pdf),
        ("full_pipeline", test_full_pipeline),
        ("duplicate_detection", test_duplicate_detection),
    ]

    passed = 0
    failed = 0
    for name, fn in tests:
        print(f"\n--- {name} ---")
        try:
            fn()
            print("PASS")
            passed += 1
        except Exception as e:
            print(f"FAIL: {e}")
            failed += 1
        finally:
            teardown()

    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()

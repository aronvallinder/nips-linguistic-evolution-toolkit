"""Extract markdown and bibliography from PDFs using pydantic-ai.

CLI entry point. Delegates to extract.py (PDF extraction) and notes.py (note generation).
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Ensure the skill directory is importable
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import BIB_DIR, CONFIG, LEADS_DIR, NOTES_DIR, PDF_DIR, REFS_DIR, load_env
from extract import find_pending, process
from notes import generate_exploration, generate_note


# --- Async batch helpers ---


async def _run_with_semaphore(sem: asyncio.Semaphore, coro):
    """Run a coroutine with a semaphore for concurrency limiting."""
    async with sem:
        return await coro


async def extract_batch(pending: list[Path], max_jobs: int) -> tuple[list[str], list[tuple[str, str]]]:
    """Extract a batch of PDFs concurrently. Returns (extracted_keys, renames)."""
    sem = asyncio.Semaphore(max_jobs)
    extracted_keys: list[str] = []
    renames: list[tuple[str, str]] = []

    async def _do_one(pdf: Path) -> str:
        try:
            key, _, _, _, dup, renamed = await _run_with_semaphore(sem, process(pdf))
            extracted_keys.append(key)
            if renamed:
                renames.append((renamed, f"{key}.pdf"))
            label = f"{key} (duplicate)" if dup else key
            return f"{pdf.relative_to(PDF_DIR)} -> {label}"
        except Exception as e:
            return f"{pdf.relative_to(PDF_DIR)} FAILED: {e}"

    tasks = [_do_one(pdf) for pdf in pending]
    results = await asyncio.gather(*tasks)
    for i, msg in enumerate(results, 1):
        print(f"[{i}/{len(pending)}] {msg}")

    return extracted_keys, renames


async def generate_notes_batch(
    keys: list[str], context: str, slug: str, max_jobs: int
):
    """Generate notes for multiple keys concurrently."""
    sem = asyncio.Semaphore(max_jobs)
    slug_dir = NOTES_DIR / slug

    async def _do_one(key: str) -> str:
        note_path = slug_dir / f"{key}.md"
        if note_path.exists() and not context:
            return f"{key} (note exists, skipping)"
        try:
            path = await _run_with_semaphore(
                sem,
                generate_note(key, context=context, slug=slug),
            )
            return f"{key} -> {path.relative_to(REFS_DIR)}"
        except Exception as e:
            return f"{key} FAILED: {e}"

    tasks = [_do_one(key) for key in keys]
    results = await asyncio.gather(*tasks)
    for i, msg in enumerate(results, 1):
        print(f"[{i}/{len(keys)}] {msg}")


async def explore_batch(
    keys: list[str], context: str, slug: str, max_jobs: int
):
    """Generate exploration notes + leads for multiple keys."""
    sem = asyncio.Semaphore(max_jobs)

    async def _do_one(key: str) -> str:
        try:
            note_path, leads_path = await _run_with_semaphore(
                sem,
                generate_exploration(
                    key, context=context, slug=slug
                ),
            )
            return f"{key} -> {note_path.relative_to(REFS_DIR)}, {leads_path.relative_to(REFS_DIR)}"
        except Exception as e:
            return f"{key} FAILED: {e}"

    tasks = [_do_one(key) for key in keys]
    results = await asyncio.gather(*tasks)
    for i, msg in enumerate(results, 1):
        print(f"[{i}/{len(keys)}] {msg}")


# --- Subcommand handlers ---


async def cmd_notes_only(
    keys: list[str], context: str, slug: str, max_jobs: int
):
    """Handle --notes-only mode."""
    slug_dir = NOTES_DIR / slug
    if not keys:
        keys = [
            p.stem for p in sorted(BIB_DIR.glob("*.json"))
            if not (slug_dir / f"{p.stem}.md").exists()
        ]
        if not keys:
            print("All bib entries already have notes.")
            return
        print(
            f"Generating notes for {len(keys)} papers "
            f"missing notes in {slug}/..."
        )

    await generate_notes_batch(keys, context, slug, max_jobs)


async def cmd_explore_only(
    keys: list[str], context: str, slug: str, max_jobs: int
):
    """Handle --explore-only mode."""
    leads_slug_dir = LEADS_DIR / slug
    if not keys:
        keys = [
            p.stem for p in sorted(BIB_DIR.glob("*.json"))
            if not (leads_slug_dir / f"{p.stem}.md").exists()
        ]
        if not keys:
            print("All bib entries already have leads.")
            return
        print(
            f"Generating exploration notes for "
            f"{len(keys)} papers in {slug}/..."
        )

    await explore_batch(keys, context, slug, max_jobs)


async def cmd_extract(args):
    """Handle standard extraction mode (with optional --notes)."""
    scan_dir = PDF_DIR
    extracted_keys: list[str] = []

    # Handle single-file target
    if args.path:
        target = Path(args.path)
        if not target.is_absolute():
            candidate = PDF_DIR / target
            if candidate.exists():
                target = candidate
        target = target.resolve()

        if target.is_file():
            key, _, md, bib, dup, renamed = await process(target)
            label = f"{key} (duplicate, symlinked)" if dup else key
            print(f"Done: {label} -> {md.relative_to(REFS_DIR)}, {bib.relative_to(REFS_DIR)}")
            if renamed:
                print(f"Renamed: {renamed} -> {key}.pdf")
            extracted_keys.append(key)
        elif target.is_dir():
            scan_dir = target
        else:
            print(f"Not found: {target}")
            return

    # Batch extraction for pending PDFs
    if not extracted_keys:
        pending = find_pending(scan_dir)
        if not pending:
            print("All PDFs already extracted.")
            if not args.notes:
                return
        elif args.dry_run:
            print(f"{len(pending)} pending PDFs:")
            for p in pending:
                print(f"  {p.relative_to(PDF_DIR)}")
            return
        else:
            extracted_keys, renames = await extract_batch(pending, args.jobs)
            if renames:
                print(f"\nRenamed {len(renames)} PDFs:")
                for old, new in sorted(renames):
                    print(f"  {old} -> {new}")

    # Generate notes/exploration if requested
    slug = args.slug
    if args.explore and extracted_keys:
        print(f"\nGenerating exploration notes + leads for {len(extracted_keys)} papers...")
        await explore_batch(extracted_keys, args.context, slug, args.jobs)
    elif args.explore and not extracted_keys:
        leads_slug_dir = LEADS_DIR / slug
        keys = [
            p.stem for p in sorted(BIB_DIR.glob("*.json"))
            if not (leads_slug_dir / f"{p.stem}.md").exists()
        ]
        if keys:
            print(f"Generating exploration notes for {len(keys)} papers...")
            await explore_batch(keys, args.context, slug, args.jobs)
    elif args.notes and extracted_keys:
        print(f"\nGenerating relevance notes for {len(extracted_keys)} papers...")
        await generate_notes_batch(extracted_keys, args.context, slug, args.jobs)
    elif args.notes and not extracted_keys:
        slug_dir = NOTES_DIR / slug
        keys = [
            p.stem for p in sorted(BIB_DIR.glob("*.json"))
            if not (slug_dir / f"{p.stem}.md").exists()
        ]
        if keys:
            print(f"Generating notes for {len(keys)} papers...")
            await generate_notes_batch(keys, args.context, slug, args.jobs)


# --- CLI ---


async def async_main():
    parser = argparse.ArgumentParser(
        description="Extract markdown and bibliography from PDFs, generate relevance notes"
    )
    parser.add_argument("path", nargs="?", help="PDF file, subfolder, or citekey (default: all pending)")
    parser.add_argument("--dry-run", action="store_true", help="List pending without converting")
    parser.add_argument("--notes", action="store_true", help="Also generate relevance notes after extraction")
    parser.add_argument("--notes-only", nargs="*", metavar="KEY",
                        help="Only generate notes for given citekeys (no PDF extraction)")
    parser.add_argument("--explore", action="store_true",
                        help="Generate exploration notes + leads after extraction (for snowball search)")
    parser.add_argument("--explore-only", nargs="*", metavar="KEY",
                        help="Only generate exploration notes + leads (no PDF extraction)")
    parser.add_argument("--slug", "-s", type=str, default="",
                        help="Research topic slug (required for --notes/--explore); notes and leads go to notes/{slug}/ and leads/{slug}/")
    parser.add_argument("--context", "-c", type=str, default="",
                        help="Context for note generation (why this paper matters)")
    parser.add_argument(
        "-j", "--jobs", type=int, default=CONFIG.get("parallel_jobs", 4),
        help=f"Parallel jobs (default: {CONFIG.get('parallel_jobs', 4)})",
    )
    args = parser.parse_args()

    load_env()

    needs_slug = (
        args.explore
        or args.notes
        or args.explore_only is not None
        or args.notes_only is not None
    )
    if needs_slug and not args.slug:
        parser.error(
            "--slug is required when using "
            "--notes/--explore/--notes-only/--explore-only"
        )

    if args.explore_only is not None:
        keys = args.explore_only
        if not keys and args.path:
            keys = [args.path]
        await cmd_explore_only(
            keys, args.context, args.slug, args.jobs
        )
    elif args.notes_only is not None:
        keys = args.notes_only
        if not keys and args.path:
            keys = [args.path]
        await cmd_notes_only(
            keys, args.context, args.slug, args.jobs
        )
    else:
        await cmd_extract(args)


def main():
    asyncio.run(async_main())


if __name__ == "__main__":
    main()

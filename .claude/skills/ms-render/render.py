"""Merge bibliography and render manuscript via Quarto."""

import argparse
import subprocess
import sys

from paths import manuscript_quarto_dir


def main():
    parser = argparse.ArgumentParser(description="Render manuscript")
    parser.add_argument("--html", action="store_true", help="Render HTML")
    parser.add_argument(
        "--pdf", action="store_true", help="Render PDF (default)"
    )
    parser.add_argument(
        "--all", action="store_true", help="Render both PDF and HTML"
    )
    args = parser.parse_args()

    # Merge bibliography first
    from merge_bib import merge

    merge()

    quarto_dir = manuscript_quarto_dir()

    # Determine format
    formats = []
    if args.all:
        formats = ["pdf", "html"]
    elif args.html:
        formats = ["html"]
    else:
        formats = ["pdf"]

    for fmt in formats:
        cmd = ["quarto", "render", str(quarto_dir), "--to", fmt]
        print(f"Running: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd)
        except FileNotFoundError as exc:
            message = (
                "Quarto is required as a global executable and must be "
                "available on PATH (for example: brew install --cask "
                f"quarto). Original error: {exc}"
            )
            raise RuntimeError(message) from exc
        if result.returncode != 0:
            sys.exit(result.returncode)


if __name__ == "__main__":
    main()

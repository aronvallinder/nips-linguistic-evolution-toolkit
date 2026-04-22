#!/usr/bin/env bash
# render.sh — render a QMD analysis report to HTML and/or GFM
#
# Usage:
#   render.sh [--html|--gfm|--all] <path-to-qmd>
#
# Examples:
#   render.sh projects/neurips-2026-mls/analysis/5groups_20gen_report.qmd
#   render.sh --html projects/neurips-2026-mls/analysis/5groups_20gen_report.qmd
#   render.sh --gfm  projects/neurips-2026-mls/analysis/5groups_20gen_report.qmd

set -euo pipefail

FORMAT="all"
QMD=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --html) FORMAT="html"; shift ;;
        --gfm)  FORMAT="gfm";  shift ;;
        --all)  FORMAT="all";  shift ;;
        -*)     echo "Unknown flag: $1" >&2; exit 1 ;;
        *)      QMD="$1"; shift ;;
    esac
done

if [[ -z "$QMD" ]]; then
    echo "Error: no QMD file specified." >&2
    echo "Usage: render.sh [--html|--gfm|--all] <path-to-qmd>" >&2
    exit 1
fi

QMD_ABS=$(realpath "$QMD")
QMD_DIR=$(dirname "$QMD_ABS")
QMD_FILE=$(basename "$QMD_ABS")

# Project root: walk up to find pyproject.toml (Poetry project)
PROJECT_ROOT="$QMD_DIR"
while [[ "$PROJECT_ROOT" != "/" ]]; do
    [[ -f "$PROJECT_ROOT/pyproject.toml" ]] && break
    PROJECT_ROOT=$(dirname "$PROJECT_ROOT")
done

if [[ ! -f "$PROJECT_ROOT/pyproject.toml" ]]; then
    echo "Error: could not find pyproject.toml from $QMD_DIR" >&2
    exit 1
fi

echo "Report : $QMD_FILE"
echo "Dir    : $QMD_DIR"
echo "Root   : $PROJECT_ROOT"
echo "Format : $FORMAT"
echo ""

cd "$QMD_DIR"

render_format() {
    local fmt="$1"
    echo "--- Rendering $fmt ---"
    # Run from QMD dir so relative paths (CSVs, figures) resolve correctly.
    # Poetry finds pyproject.toml by searching upward from the current dir.
    poetry run quarto render "$QMD_FILE" --to "$fmt"
}

case "$FORMAT" in
    html) render_format html ;;
    gfm)  render_format gfm  ;;
    all)
        render_format html
        render_format gfm
        ;;
esac

echo ""
echo "Done. Output in: $QMD_DIR"

#!/usr/bin/env bash
# Refresh the public data-inspector site (GitHub Pages).
#
#   Live URL:  https://ivarfresh.github.io/linguistic-evolution-inspector/
#   Source:    data/plots/inspector/{inspector.html, run_plots/, runs/, agg_plots/, negnoise_plots/}
#   Repo:      github.com/ivarfresh/linguistic-evolution-inspector
#
# Copies the local inspector into the Pages repo (inspector.html -> index.html
# so the URL is the repo root), commits, and pushes. GitHub rebuilds the site
# in ~1 minute. Re-run any time you regenerate the inspector or plots.
#
# Usage:  ./scripts/refresh_inspector_site.sh
set -euo pipefail

REPO_URL="https://github.com/ivarfresh/linguistic-evolution-inspector.git"
PAGES_URL="https://ivarfresh.github.io/linguistic-evolution-inspector/"

# Resolve repo root from this script's location so it runs from anywhere.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SRC="$PROJECT_ROOT/data/plots/inspector"
CLONE_DIR="$PROJECT_ROOT/.inspector-site"   # persistent local clone (gitignored)

# --- sanity checks ---------------------------------------------------------
if [[ ! -f "$SRC/inspector.html" ]]; then
  echo "ERROR: $SRC/inspector.html not found." >&2
  exit 1
fi
if [[ ! -d "$SRC/run_plots" ]]; then
  echo "ERROR: $SRC/run_plots/ not found." >&2
  exit 1
fi

# --- clone or update the Pages repo ---------------------------------------
if [[ -d "$CLONE_DIR/.git" ]]; then
  echo "Updating existing clone at $CLONE_DIR ..."
  git -C "$CLONE_DIR" fetch -q origin
  git -C "$CLONE_DIR" reset -q --hard origin/main
else
  echo "Cloning $REPO_URL ..."
  rm -rf "$CLONE_DIR"
  git clone -q "$REPO_URL" "$CLONE_DIR"
fi

# --- sync files ------------------------------------------------------------
echo "Syncing inspector.html -> index.html and asset dirs ..."
touch "$CLONE_DIR/.nojekyll"   # serve _underscore paths verbatim (skip Jekyll)
cp "$SRC/inspector.html" "$CLONE_DIR/index.html"
for d in run_plots runs agg_plots; do
  [[ -d "$SRC/$d" ]] || continue
  rm -rf "${CLONE_DIR:?}/$d"
  cp -R "$SRC/$d" "$CLONE_DIR/$d"
done

# Standalone negnoise inspector (built by scripts/build_negnoise_inspector.py)
# publishes under /negnoise/ on the same Pages site.
NEG_SRC="$PROJECT_ROOT/data/plots/inspector_negnoise"
if [[ -f "$NEG_SRC/inspector.html" ]]; then
  echo "Syncing negnoise inspector -> negnoise/ ..."
  rm -rf "${CLONE_DIR:?}/negnoise"
  mkdir -p "$CLONE_DIR/negnoise"
  cp "$NEG_SRC/inspector.html" "$CLONE_DIR/negnoise/index.html"
  for d in runs run_plots agg_plots; do
    [[ -d "$NEG_SRC/$d" ]] && cp -R "$NEG_SRC/$d" "$CLONE_DIR/negnoise/$d"
  done
fi

# --- commit & push (no-op if nothing changed) ------------------------------
cd "$CLONE_DIR"
git add -A
if git diff --cached --quiet; then
  echo "No changes — site already up to date."
  echo "Live: $PAGES_URL"
  exit 0
fi

STAMP="$(date '+%Y-%m-%d %H:%M:%S')"
N_PLOTS="$(ls run_plots | wc -l | tr -d ' ')"
git commit -q -m "Refresh inspector site ($STAMP, ${N_PLOTS} plots)"
git push -q origin main

echo "Pushed. GitHub Pages rebuilds in ~1 min."
echo "Live: $PAGES_URL"

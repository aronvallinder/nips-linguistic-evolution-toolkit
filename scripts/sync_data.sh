#!/usr/bin/env bash
# Sync completed simulation runs with the shared HF dataset repo.
#
#   Repo:  https://huggingface.co/datasets/machine-cultural-evolution/nips-linguistic-evolution-runs
#   Usage: ./scripts/sync_data.sh push          # upload local data/json under <ns>/json/
#          ./scripts/sync_data.sh pull          # download everyone's runs to data/shared_runs/
#          ./scripts/sync_data.sh status        # who has uploaded what + last commit
#          ./scripts/sync_data.sh push mylabel  # override the namespace
#
# Each machine pushes under its own namespace (default: HF username), so
# runs from different people never collide. Pulling fetches the whole repo
# into data/shared_runs/<ns>/json/... — local data/json is never touched.
#
# Requires: `hf auth login` once (free account, write token).
# Uploads are content-deduplicated (xet), so re-pushing after a new batch
# only transfers the new runs.
set -euo pipefail

REPO="machine-cultural-evolution/nips-linguistic-evolution-runs"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CMD="${1:-}"
NS="${2:-$(python3 -c 'from huggingface_hub import whoami; print(whoami()["name"])')}"

case "$CMD" in
  push)
    # upload-large-folder is resumable (batched commits) but always uploads to
    # the repo root, so stage the namespace layout first. On APFS the copy is
    # a clonefile (instant, no extra disk); elsewhere rsync does incremental.
    STAGE="$PROJECT_ROOT/data/.hf_stage"
    mkdir -p "$STAGE"
    rm -rf "$STAGE/$NS"
    mkdir -p "$STAGE/$NS"
    if ! cp -Rpc "$PROJECT_ROOT/data/json" "$STAGE/$NS/json" 2>/dev/null; then
      rsync -a --delete "$PROJECT_ROOT/data/json/" "$STAGE/$NS/json/"
    fi
    echo "Pushing data/json -> $REPO:$NS/json ..."
    hf upload-large-folder "$REPO" "$STAGE" --repo-type dataset
    echo "Done."
    ;;
  status)
    python3 - "$REPO" <<'PY'
import sys, collections
from huggingface_hub import HfApi
repo = sys.argv[1]
api = HfApi()
files = api.list_repo_files(repo, repo_type="dataset")
by_ns = collections.Counter(f.split("/")[0] for f in files if "/" in f)
print(f"{repo}:")
for ns, n in sorted(by_ns.items()):
    print(f"  {ns}/  ({n} files)")
c = api.list_repo_commits(repo, repo_type="dataset")[0]
print(f"last commit: {c.title} · {c.created_at:%Y-%m-%d %H:%M} · {', '.join(c.authors)}")
PY
    ;;
  pull)
    echo "Pulling $REPO -> data/shared_runs/ ..."
    hf download "$REPO" --repo-type dataset \
      --local-dir "$PROJECT_ROOT/data/shared_runs"
    echo "Done. Runs are under data/shared_runs/<namespace>/json/."
    ;;
  *)
    echo "Usage: $0 push|pull [namespace]" >&2
    exit 1
    ;;
esac

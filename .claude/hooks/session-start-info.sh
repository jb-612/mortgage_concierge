#!/usr/bin/env bash
set -euo pipefail

# SessionStart hook — display contextual information
# Always exits 0 (informational only)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "=== Mortgage Concierge Session ==="

# Current branch
BRANCH=$(git -C "$PROJECT_DIR" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
echo "Branch: $BRANCH"

# Active workitems
if [ -d "$PROJECT_DIR/.workitems" ]; then
  WI_COUNT=0
  echo ""
  echo "Active Workitems:"
  for wi_dir in "$PROJECT_DIR/.workitems"/*/; do
    if [ -d "$wi_dir" ]; then
      WI_NAME=$(basename "$wi_dir")
      echo "  - $WI_NAME"
      WI_COUNT=$((WI_COUNT + 1))
    fi
  done
  if [ "$WI_COUNT" -eq 0 ]; then
    echo "  (none)"
  fi
else
  echo "No .workitems/ directory. Use /feature-spec to start."
fi

# Eval sets
EVAL_DIR="$PROJECT_DIR/tests/eval/data"
if [ -d "$EVAL_DIR" ]; then
  EVALSETS=$(find "$EVAL_DIR" -maxdepth 1 -name "*.evalset.json" 2>/dev/null || true)
  if [ -n "$EVALSETS" ]; then
    echo ""
    echo "Eval sets:"
    while IFS= read -r f; do
      [ -n "$f" ] && echo "  - $(basename "$f")"
    done <<< "$EVALSETS"
  fi
fi

echo "================================="
exit 0

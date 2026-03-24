#!/usr/bin/env bash
set -euo pipefail

# Stop hook — advisory audit of modified packages vs workitems
# Always exits 0 (advisory only, never blocks)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_DIR"

# Get modified Python files in mortgage_concierge/
MODIFIED_FILES=$(git diff --name-only HEAD -- 'mortgage_concierge/' 2>/dev/null | grep '\.py$' || true)

if [ -z "$MODIFIED_FILES" ]; then
  exit 0
fi

if [ ! -d "$PROJECT_DIR/.workitems" ]; then
  echo "[Audit] Changes detected in mortgage_concierge/ but no .workitems/ directory found." >&2
  echo "[Audit] Consider creating workitems with /feature-spec for better traceability." >&2
  exit 0
fi

# Collect unmatched packages
UNMATCHED=()
while IFS= read -r file; do
  INNER="${file#mortgage_concierge/}"
  if [[ "$INNER" == */* ]]; then
    PKG=$(echo "$INNER" | cut -d'/' -f1)
  else
    PKG="root"
  fi

  FOUND=false
  for doc in "$PROJECT_DIR/.workitems"/*/*.md; do
    if [ -f "$doc" ] && grep -qi "$PKG" "$doc" 2>/dev/null; then
      FOUND=true
      break
    fi
  done

  if [ "$FOUND" = false ]; then
    UNMATCHED+=("$PKG")
  fi
done <<< "$MODIFIED_FILES"

if [ ${#UNMATCHED[@]} -gt 0 ]; then
  UNIQUE=$(printf '%s\n' "${UNMATCHED[@]}" | sort -u)
  echo "" >&2
  echo "[Audit Warning] Modified packages without matching workitems:" >&2
  while IFS= read -r pkg; do
    echo "  - $pkg" >&2
  done <<< "$UNIQUE"
  echo "[Audit] Consider creating workitems with /feature-spec." >&2
fi

exit 0

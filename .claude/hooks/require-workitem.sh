#!/usr/bin/env bash
set -euo pipefail

# PreToolUse hook for Edit|Write — block production code edits without workitem
# Exit 0 = allow, Exit 2 = block

INPUT=$(cat)

FILE_PATH=$(echo "$INPUT" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(data.get('tool_input', {}).get('file_path', ''))
" 2>/dev/null || echo "")

if [ -z "$FILE_PATH" ]; then
  exit 0
fi

# Only check Python files
if [[ "$FILE_PATH" != *.py ]]; then
  exit 0
fi

# Derive project root
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

REL_PATH="${FILE_PATH#$PROJECT_DIR/}"

# Only enforce for production code in mortgage_concierge/
if [[ "$REL_PATH" != mortgage_concierge/* ]]; then
  exit 0
fi

# Skip test files
FILENAME=$(basename "$FILE_PATH")
if [[ "$FILENAME" == test_* ]] || [[ "$FILENAME" == *_test.py ]]; then
  exit 0
fi

# Check if .workitems/ exists — graceful for initial setup
WORKITEMS_DIR="$PROJECT_DIR/.workitems"
if [ ! -d "$WORKITEMS_DIR" ]; then
  exit 0
fi

# Extract package segment from path
INNER_PATH="${REL_PATH#mortgage_concierge/}"
if [[ "$INNER_PATH" == */* ]]; then
  PACKAGE_SEGMENT=$(echo "$INNER_PATH" | cut -d'/' -f1)
else
  PACKAGE_SEGMENT="root"
fi

# Search for matching workitem
FOUND=false
for wi_dir in "$WORKITEMS_DIR"/*/; do
  if [ ! -d "$wi_dir" ]; then
    continue
  fi
  for doc in "${wi_dir}"*.md; do
    if [ -f "$doc" ] && grep -qi "$PACKAGE_SEGMENT" "$doc" 2>/dev/null; then
      FOUND=true
      break 2
    fi
  done
done

if ! $FOUND; then
  echo "BLOCKED: No workitem found referencing package '$PACKAGE_SEGMENT'." >&2
  echo "Create a workitem with /feature-spec or add '$PACKAGE_SEGMENT' to an existing workitem." >&2
  exit 2
fi

exit 0

#!/bin/bash
# block-md-creation.sh
# PreToolUse hook on Write tool — .md files only.
# Warns when .md files are created outside standard workspace locations.
# INFORMATIONAL ONLY — does not block (exit 0 always).
#
# Standard .md locations in this workspace:
#   outputs/research/**   — all skill outputs
#   .claude/skills/**     — SKILL.md, LESSONS.md, DEPRECATED.md
#   context/              — living context files
#   automation/           — automation docs
#   outputs/research/handoffs/  — handoff files
#   Root level: CLAUDE.md, ARCHITECTURE.md, WORKFLOW.md, README.md

TMPFILE=$(mktemp /tmp/claude-hook-XXXXXX.json)
trap "rm -f $TMPFILE" EXIT
cat > "$TMPFILE"

FILE_PATH=$(python3 -c "
import json, sys
try:
    with open(sys.argv[1]) as f:
        d = json.load(f)
    print(d.get('tool_input', {}).get('file_path', ''))
except Exception:
    pass
" "$TMPFILE" 2>/dev/null)

# Only care about .md files
[ -z "$FILE_PATH" ] && exit 0
echo "$FILE_PATH" | grep -qE '\.md$' || exit 0

# Check against allowed location patterns
ALLOWED_PATTERNS=(
    "outputs/research/"
    ".claude/skills/"
    "context/"
    "automation/"
    "handoffs/"
    "CLAUDE.md"
    "ARCHITECTURE.md"
    "WORKFLOW.md"
    "README.md"
    "DEPRECATED.md"
    "ACTION-PLAN"
    "SERVER-OPS"
)

for pattern in "${ALLOWED_PATTERNS[@]}"; do
    if echo "$FILE_PATH" | grep -qF "$pattern"; then
        exit 0  # Allowed location — pass silently
    fi
done

# Out-of-standard location — warn but always allow
BASENAME=$(basename "$FILE_PATH")
echo "" >&2
echo "⚠️  FILE LOCATION: Creating '$BASENAME' at a non-standard path." >&2
echo "   Path: $FILE_PATH" >&2
echo "   Standard .md locations: outputs/research/, .claude/skills/, context/, automation/" >&2
echo "   If intentional, proceed. Otherwise reconsider the path before writing." >&2

exit 0  # Always allow — warning only, never blocks

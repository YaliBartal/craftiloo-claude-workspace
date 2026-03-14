#!/bin/bash
# bash-safety.sh
# PreToolUse hook on Bash tool.
# Blocks catastrophically dangerous commands before they execute.
#
# Calibrated for Craftiloo workspace: allows git rm, rm -f on specific paths,
# git reset HEAD (soft), etc. Only blocks commands that are irreversible or
# would destroy the workspace, credentials, or shared git history.

TMPFILE=$(mktemp /tmp/claude-hook-XXXXXX.json)
trap "rm -f $TMPFILE" EXIT
cat > "$TMPFILE"

CMD=$(python3 -c "
import json, sys
try:
    with open(sys.argv[1]) as f:
        d = json.load(f)
    print(d.get('tool_input', {}).get('command', ''))
except Exception:
    pass
" "$TMPFILE" 2>/dev/null)

[ -z "$CMD" ] && exit 0

BLOCKED=""

# ── CATASTROPHIC BLOCKS ──────────────────────────────────────────────────────

# Root filesystem deletion
if echo "$CMD" | grep -qE 'rm\s+-[a-zA-Z]*r[a-zA-Z]*f?\s+/\s*$|rm\s+-[a-zA-Z]*r[a-zA-Z]*f?\s+/\s+'; then
    BLOCKED="rm targeting root filesystem — would delete entire system"
fi

# Wildcard deletion with no specific path
if [ -z "$BLOCKED" ] && echo "$CMD" | grep -qE 'rm\s+-[a-zA-Z]*r[a-zA-Z]*\s+\*\s*$'; then
    BLOCKED="rm -rf * with no path — confirm working directory before running"
fi

# Delete entire workspace
if [ -z "$BLOCKED" ] && echo "$CMD" | grep -qE 'rm\s+-[a-zA-Z]*r[a-zA-Z]*\s+/home/yali/workspace\s*$'; then
    BLOCKED="rm targeting entire workspace directory"
fi

# Force push to protected branches only (allow to feature/worktree branches)
if [ -z "$BLOCKED" ] && echo "$CMD" | grep -qE 'git\s+push\s+(--force|-f)\s+(origin\s+)?(master|main)\b'; then
    BLOCKED="force push to master/main — rewrites shared branch history irreversibly"
fi

# Hard reset WITH a ref (loses uncommitted work — git reset --hard alone is less dangerous)
if [ -z "$BLOCKED" ] && echo "$CMD" | grep -qE 'git\s+reset\s+--hard\s+(HEAD~|origin/|[a-f0-9]{7})'; then
    BLOCKED="git reset --hard to a commit ref — destroys all uncommitted changes"
fi

# Overwriting .env file
if [ -z "$BLOCKED" ] && echo "$CMD" | grep -qE '1?>\s*\.env\b|1?>\s*/home/yali/workspace/\.env\b|tee\s+.*\.env\b'; then
    BLOCKED="overwriting .env — destroys all 71 API credentials"
fi

# Reading .env via shell read commands
if [ -z "$BLOCKED" ] && echo "$CMD" | grep -qE '(cat|less|more|head|tail|bat|strings)\s+.*\.env\b'; then
    BLOCKED="reading .env directly — use 'echo \$VAR_NAME' to check individual values"
fi

# ── OUTPUT ───────────────────────────────────────────────────────────────────

if [ -n "$BLOCKED" ]; then
    echo "" >&2
    echo "⚠️  SAFETY BLOCK: Command not executed." >&2
    echo "   Reason: $BLOCKED" >&2
    echo "   State your intent and request explicit user approval before retrying." >&2
    exit 2
fi

exit 0

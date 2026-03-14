#!/bin/bash
# secret-scanner.sh
# PreToolUse hook on Write and Edit tools.
# Scans content being written for actual API credential VALUE patterns.
# Blocks (exit 2) if real credential values detected — not just variable names.
#
# Protects against: 71 API keys in .env accidentally leaking into git-pushed output files.
# Does NOT fire on: variable names like "ADS_API_CLIENT_ID", only on actual token values.

TMPFILE=$(mktemp /tmp/claude-hook-XXXXXX.json)
trap "rm -f $TMPFILE" EXIT
cat > "$TMPFILE"

# Extract content being written
# Write tool uses 'content' field; Edit tool uses 'new_string' field
CONTENT=$(python3 -c "
import json, sys
try:
    with open(sys.argv[1]) as f:
        d = json.load(f)
    inp = d.get('tool_input', {})
    val = inp.get('content', '') or inp.get('new_string', '') or ''
    print(val[:50000])  # Cap at 50KB for performance
except Exception:
    pass
" "$TMPFILE" 2>/dev/null)

[ -z "$CONTENT" ] && exit 0

FOUND=""

# Amazon LWA access/refresh tokens (Atza| prefix + long base64)
if echo "$CONTENT" | grep -qE 'Atza\|[A-Za-z0-9+/=_-]{30,}'; then
    FOUND="Amazon LWA token (Atza|...)"
fi

# Amazon OAuth application client IDs
if [ -z "$FOUND" ] && echo "$CONTENT" | grep -qE 'amzn1\.application-oa2-client\.[a-z0-9]{20,}'; then
    FOUND="Amazon OAuth client ID (amzn1.application-oa2-client....)"
fi

# Slack bot tokens
if [ -z "$FOUND" ] && echo "$CONTENT" | grep -qE 'xoxb-[0-9]{10,}-[0-9]{10,}-[A-Za-z0-9]{20,}'; then
    FOUND="Slack bot token (xoxb-)"
fi

# Slack user tokens
if [ -z "$FOUND" ] && echo "$CONTENT" | grep -qE 'xoxp-[0-9]{10,}-[0-9]{10,}-[A-Za-z0-9]{20,}'; then
    FOUND="Slack user token (xoxp-)"
fi

# GitHub personal access tokens (classic)
if [ -z "$FOUND" ] && echo "$CONTENT" | grep -qE 'ghp_[A-Za-z0-9]{36}'; then
    FOUND="GitHub classic PAT (ghp_...)"
fi

# GitHub fine-grained tokens
if [ -z "$FOUND" ] && echo "$CONTENT" | grep -qE 'github_pat_[A-Za-z0-9_]{82}'; then
    FOUND="GitHub fine-grained token (github_pat_...)"
fi

# AWS access keys
if [ -z "$FOUND" ] && echo "$CONTENT" | grep -qE 'AKIA[0-9A-Z]{16}'; then
    FOUND="AWS access key (AKIA...)"
fi

# Notion integration tokens
if [ -z "$FOUND" ] && echo "$CONTENT" | grep -qE 'secret_[A-Za-z0-9]{40,}'; then
    FOUND="Notion integration token (secret_...)"
fi

if [ -n "$FOUND" ]; then
    echo "" >&2
    echo "⚠️  SECRET SCANNER BLOCKED" >&2
    echo "   Detected: $FOUND" >&2
    echo "   This is an actual credential value — not just a variable name." >&2
    echo "   Remove it before writing. If documenting API formats, use placeholders:" >&2
    echo "   e.g. 'xoxb-XXXXX-XXXXX-XXXX' instead of the real token." >&2
    exit 2
fi

exit 0

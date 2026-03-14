#!/bin/bash
# block-env-read.sh
# PreToolUse hook on Read tool.
# Blocks direct reading of .env and other credential files.
#
# Why: .env contains 71 API keys. skill-runner.py's load_env() already loads all values
# into os.environ before Claude runs. There is no legitimate reason to read .env directly.
# Reading it would dump all 71 credentials into the context window in one tool call.

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

[ -z "$FILE_PATH" ] && exit 0

# Block reading credential and secret files
if echo "$FILE_PATH" | grep -qE '(^|/)\.env$|(^|/)\.env\.(local|prod|dev|staging|test)$|\.key$|\.pem$|credentials\.json$|secrets\.json$'; then
    BASENAME=$(basename "$FILE_PATH")
    echo "" >&2
    echo "🔒 BLOCKED: Direct reading of '$BASENAME' is not permitted." >&2
    echo "   All .env credentials are pre-loaded into environment variables by skill-runner.py." >&2
    echo "   To check a specific variable:  Bash(\"echo \$VARIABLE_NAME\")" >&2
    echo "   To list vars by prefix:        Bash(\"env | grep ADS_API_\")" >&2
    echo "   Never read the raw .env file — it dumps all 71 credentials to context." >&2
    exit 2
fi

exit 0

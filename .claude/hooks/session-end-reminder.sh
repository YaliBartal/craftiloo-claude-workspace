#!/bin/bash
# session-end-reminder.sh
# Stop hook — fires when Claude finishes responding.
# Checks if skill outputs were written but LESSONS.md / run-log were not updated.
# Reminder only — enforces post-run housekeeping discipline.
#
# Most useful in interactive sessions where the user can see the reminder.
# In automated runs (claude -p), output goes into the skill-runner.py log.

WORKSPACE="/home/yali/workspace"

# Get current git status
GIT_STATUS=$(git -C "$WORKSPACE" status --short 2>/dev/null || echo "")

# Nothing changed — reading/planning session, nothing to remind about
[ -z "$GIT_STATUS" ] && exit 0

# Check if any outputs/ files were modified (key indicator that a skill ran)
HAS_OUTPUTS=$(echo "$GIT_STATUS" | grep "outputs/" | head -1)

# No outputs written — not a skill run (browsing, planning, etc.) — skip
[ -z "$HAS_OUTPUTS" ] && exit 0

# Check if post-run housekeeping files were updated
HAS_LESSONS=$(echo "$GIT_STATUS" | grep "LESSONS\.md" | head -1)
HAS_RUNLOG=$(echo "$GIT_STATUS" | grep "run-logs/" | head -1)

# Both present — properly wrapped up — silent pass
if [ -n "$HAS_LESSONS" ] && [ -n "$HAS_RUNLOG" ]; then
    exit 0
fi

# At least one is missing — print reminder
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  📝 SESSION END — Post-run housekeeping incomplete             ║"
echo "╠════════════════════════════════════════════════════════════════╣"

if [ -z "$HAS_LESSONS" ]; then
    echo "║  ✗  LESSONS.md  — not updated this session                    ║"
else
    echo "║  ✓  LESSONS.md  — updated ✓                                   ║"
fi

if [ -z "$HAS_RUNLOG" ]; then
    echo "║  ✗  Run log     — not written to run-logs/ this session        ║"
else
    echo "║  ✓  Run log     — written ✓                                    ║"
fi

echo "╠════════════════════════════════════════════════════════════════╣"
echo "║  Run /wrap-up to complete both before ending this session.     ║"
echo "╚════════════════════════════════════════════════════════════════╝"

exit 0

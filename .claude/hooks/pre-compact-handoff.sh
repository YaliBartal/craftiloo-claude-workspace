#!/bin/bash
# pre-compact-handoff.sh
# PreCompact hook — fires before auto-compaction.
# Creates a structured handoff file and instructs Claude to populate it
# with current task state BEFORE context is compressed.
#
# Why: Auto-compaction at 95% fires mid-task (e.g., turn 60 of 80 in weekly-ppc).
# After compaction, Claude loses all the detailed analysis from the first 60 turns.
# This hook creates the preservation infrastructure and prompts Claude to use it.

TMPFILE=$(mktemp /tmp/claude-hook-XXXXXX.json)
trap "rm -f $TMPFILE" EXIT
cat > "$TMPFILE"

# Capture transcript path for raw recovery fallback
TRANSCRIPT=$(python3 -c "
import json, sys
try:
    with open(sys.argv[1]) as f:
        d = json.load(f)
    print(d.get('transcript_path', 'unknown'))
except Exception:
    print('unknown')
" "$TMPFILE" 2>/dev/null || echo "unknown")

HANDOFF_DIR="/home/yali/workspace/outputs/research/handoffs"
mkdir -p "$HANDOFF_DIR" 2>/dev/null

TIMESTAMP=$(date +%Y-%m-%d-%H%M)
HANDOFF_FILE="${HANDOFF_DIR}/${TIMESTAMP}-pre-compact-auto.md"

# Write the handoff file shell — Claude populates the content sections
{
    echo "---"
    echo "type: pre-compact-auto"
    echo "created: ${TIMESTAMP}"
    echo "transcript_path: ${TRANSCRIPT}"
    echo "status: NEEDS_POPULATION"
    echo "---"
    echo ""
    echo "## Current Task"
    echo "<!-- What skill or workflow is running — be specific -->"
    echo ""
    echo "## Current Phase"
    echo "<!-- data-fetch / analysis / output-writing + what's completed within this phase -->"
    echo ""
    echo "## Data on Disk"
    echo "<!-- Every file written this session — full absolute paths, one per bullet -->"
    echo "-"
    echo ""
    echo "## Key Findings So Far"
    echo "<!-- Specific numbers, portfolio states, decisions, conclusions found so far -->"
    echo ""
    echo "## Pending Work"
    echo "<!-- What still needs to happen after compaction resumes, in order -->"
    echo "1."
    echo ""
    echo "## Resume Instructions"
    echo "1. Re-read this file completely"
    echo "2. Load context files: [list which ones are needed]"
    echo "3. Read data files from disk: [list the paths from 'Data on Disk' above]"
    echo "4. First action: [exact next step to continue the task]"
    echo ""
    echo "## Active Workarounds / Errors"
    echo "<!-- API rate limits hit, errors encountered, workarounds applied this session -->"
} > "$HANDOFF_FILE"

# Output to Claude's context — clear, urgent instruction
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  📦 PRE-COMPACT HOOK — Context compaction about to fire        ║"
echo "╠════════════════════════════════════════════════════════════════╣"
echo "║  Handoff file created. YOU MUST populate it BEFORE proceeding: ║"
echo "║  $HANDOFF_FILE"
echo "╠════════════════════════════════════════════════════════════════╣"
echo "║  Use the Write tool RIGHT NOW to add:                          ║"
echo "║    • Current task + phase                                      ║"
echo "║    • All file paths written this session                       ║"
echo "║    • Key findings and critical numbers                         ║"
echo "║    • Pending work and exact resume instructions                ║"
echo "║  After populating → compaction will compress context.          ║"
echo "║  After compaction → re-read this file to continue.             ║"
echo "╚════════════════════════════════════════════════════════════════╝"

exit 0

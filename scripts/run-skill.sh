#!/bin/bash
set -euo pipefail

# --- Configuration ---
WORKSPACE="/home/yali/workspace"
LOG_DIR="/var/log/claude"
SKILL_NAME="$1"
TIMESTAMP=$(date +%Y-%m-%d-%H%M)
LOG_FILE="${LOG_DIR}/${SKILL_NAME}-${TIMESTAMP}.log"

# --- Start ---
echo "=== ${SKILL_NAME} started at $(date) ===" >> "$LOG_FILE"

cd "$WORKSPACE"

# Load environment variables (OAuth token, API keys, etc.)
set -a
source .env
set +a

# Pull latest code from GitHub
git pull --ff-only origin master >> "$LOG_FILE" 2>&1 || true

# Run Claude Code headless
claude -p "Run the ${SKILL_NAME} skill. Follow the SKILL.md instructions exactly. Read LESSONS.md first. Update LESSONS.md when done." \
  --allowedTools "Read,Write,Edit,Glob,Grep,Bash(python3*),Bash(pip3*),Bash(git*),Bash(ls*),Bash(cat*),Bash(mkdir*),Bash(date*),mcp__amazon-ads-api__*,mcp__amazon-sp-api__*,mcp__sellerboard__*,mcp__slack__*,mcp__datadive__*,mcp__notion__*,mcp__apify__*,mcp__asana__*" \
  --max-turns 50 \
  --output-format text \
  >> "$LOG_FILE" 2>&1

EXIT_CODE=$?

# Commit any new output files to GitHub
if [ -n "$(git status --porcelain outputs/ 2>/dev/null)" ]; then
  git add outputs/
  git commit -m "auto: ${SKILL_NAME} $(date +%Y-%m-%d)" >> "$LOG_FILE" 2>&1
  git push origin master >> "$LOG_FILE" 2>&1 || true
fi

echo "=== ${SKILL_NAME} finished at $(date) with exit code ${EXIT_CODE} ===" >> "$LOG_FILE"

exit $EXIT_CODE

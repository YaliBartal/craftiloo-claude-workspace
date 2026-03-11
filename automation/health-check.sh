#!/bin/bash
# health-check.sh — Daily server health ping to Slack
# Install via cron: 0 5 * * * /home/yali/workspace/automation/health-check.sh
# (5:00 UTC = 7:00 AM IST — fires before any skill runs)
#
# If this message stops arriving in #claude-alerts, the server is down.

set -euo pipefail

# Source credentials
source /home/yali/workspace/.env

# Gather metrics
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}')
MEMORY_PCT=$(free -m | awk 'NR==2 {printf "%.0f%%", $3/$2*100}')
MEMORY_USED=$(free -m | awk 'NR==2 {print $3}')
MEMORY_TOTAL=$(free -m | awk 'NR==2 {print $2}')
UPTIME_STR=$(uptime -p)
LOAD=$(cat /proc/loadavg | awk '{print $1, $2, $3}')
LOG_COUNT=$(find /var/log/claude -name "*.json" -mtime -1 2>/dev/null | wc -l)
DOCKER_STATUS=$(docker ps --format "{{.Names}}: {{.Status}}" 2>/dev/null | tr '\n' ' ' || echo "Docker not running")

# Check if Claude CLI is accessible
CLAUDE_VERSION=$(claude --version 2>/dev/null || echo "NOT FOUND")

# Build message
MESSAGE=":white_check_mark: *Server Health* — $(date +%Y-%m-%d %H:%M)

:computer: *System*
• Uptime: ${UPTIME_STR}
• Load: ${LOAD}
• Disk: ${DISK_USAGE}
• Memory: ${MEMORY_PCT} (${MEMORY_USED}/${MEMORY_TOTAL} MB)

:whale: *Docker*
• ${DOCKER_STATUS}

:robot_face: *Claude*
• Version: ${CLAUDE_VERSION}
• Runs last 24h: ${LOG_COUNT} log files"

# Post to Slack
curl -s -X POST \
  -H "Authorization: Bearer ${SLACK_WORKSPACE_1_BOT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg channel "#claude-alerts" --arg text "$MESSAGE" '{channel: $channel, text: $text}')" \
  https://slack.com/api/chat.postMessage > /dev/null 2>&1

exit 0

#!/bin/bash
# health-check.sh — Daily server health ping to Slack + Healthchecks.io dead man's switch
# Installed via cron: 0 5 * * * /home/yali/workspace/automation/health-check.sh
# (5:00 UTC = 7:00 AM IST winter / 8:00 AM IST summer)
#
# If the Slack message stops arriving in #claude-alerts, the server is down.
# If the Healthchecks.io ping stops arriving, something is wrong with the server or this script.
#
# HEALTHCHECKS_URL: set in .env as HC_HEALTH_CHECK_URL=https://hc-ping.com/YOUR-UUID-HERE
# Create check at https://healthchecks.io — period 24h, grace 2h.

# Source credentials (no set -e — we want the Slack post to succeed even if metrics fail)
source /home/yali/workspace/.env 2>/dev/null || true

# Gather metrics with fallbacks — each command is safe to fail individually
DISK_USAGE=$(df -h / 2>/dev/null | awk 'NR==2 {print $5}' || echo "unknown")
MEMORY_PCT=$(free -m 2>/dev/null | awk 'NR==2 {printf "%.0f%%", $3/$2*100}' || echo "unknown")
MEMORY_USED=$(free -m 2>/dev/null | awk 'NR==2 {print $3}' || echo "?")
MEMORY_TOTAL=$(free -m 2>/dev/null | awk 'NR==2 {print $2}' || echo "?")
UPTIME_STR=$(uptime -p 2>/dev/null || echo "unknown")
LOAD=$(awk '{print $1, $2, $3}' /proc/loadavg 2>/dev/null || echo "unknown")
LOG_COUNT=$(find /var/log/claude -name "*.json" -mtime -1 2>/dev/null | wc -l || echo "0")
DOCKER_STATUS=$(docker ps --format "{{.Names}}: {{.Status}}" 2>/dev/null | tr '\n' ' ' || echo "Docker unreachable")
CLAUDE_VERSION=$(claude --version 2>/dev/null || echo "NOT FOUND")

# Count recent failures from structured logs
FAILURE_COUNT=$(find /var/log/claude -name "*.json" -mtime -1 2>/dev/null \
  -exec python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(1 if d.get('exit_code',0)!=0 else 0)" {} \; 2>/dev/null \
  | paste -sd+ | bc 2>/dev/null || echo "?")

# Disk warning flag
DISK_NUM=$(df / 2>/dev/null | awk 'NR==2 {print int($5)}' || echo "0")
DISK_WARN=""
if [ "$DISK_NUM" -gt 80 ] 2>/dev/null; then
  DISK_WARN="
:warning: *Disk above 80%* — clean up /var/log or outputs/"
fi

# Build Slack message
MESSAGE=":white_check_mark: *Server Health* — $(date '+%Y-%m-%d %H:%M')

:computer: *System*
• Uptime: ${UPTIME_STR}
• Load: ${LOAD}
• Disk: ${DISK_USAGE}
• Memory: ${MEMORY_PCT} (${MEMORY_USED}/${MEMORY_TOTAL} MB)${DISK_WARN}

:whale: *Docker*
• ${DOCKER_STATUS}

:robot_face: *Claude*
• Version: ${CLAUDE_VERSION}
• Runs last 24h: ${LOG_COUNT} log files | Failures: ${FAILURE_COUNT}"

# Post to Slack
if [ -n "${SLACK_WORKSPACE_1_BOT_TOKEN:-}" ]; then
  curl -s -X POST \
    -H "Authorization: Bearer ${SLACK_WORKSPACE_1_BOT_TOKEN}" \
    -H "Content-Type: application/json" \
    -d "$(jq -n --arg channel "#claude-alerts" --arg text "$MESSAGE" \
         '{channel: $channel, text: $text}' 2>/dev/null || \
         echo "{\"channel\":\"#claude-alerts\",\"text\":\"Server health ping (jq unavailable)\"}")" \
    https://slack.com/api/chat.postMessage > /dev/null 2>&1
fi

# Ping Healthchecks.io dead man's switch — ONLY if URL is configured
# To activate: add HC_HEALTH_CHECK_URL=https://hc-ping.com/YOUR-UUID to .env
if [ -n "${HC_HEALTH_CHECK_URL:-}" ]; then
  curl -fsS -m 10 --retry 3 "${HC_HEALTH_CHECK_URL}" > /dev/null 2>&1 || true
fi

exit 0

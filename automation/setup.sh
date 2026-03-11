#!/bin/bash
# setup.sh — One-time setup for the Craftiloo automation system.
# Run as: sudo bash ~/workspace/automation/setup.sh
#
# What this does:
#   1. Creates the log directory with correct ownership
#   2. Installs logrotate config for log cleanup
#   3. Installs the pyyaml Python dependency
#   4. Sets up the daily health check cron job
#   5. Verifies Claude Code CLI and Python are available

set -euo pipefail

WORKSPACE="/home/yali/workspace"
USER="yali"

echo ""
echo "=== Craftiloo Automation Setup ==="
echo ""

# 1. Log directory
echo "[1/5] Creating log directory..."
mkdir -p /var/log/claude
chown ${USER}:${USER} /var/log/claude
echo "  ✓ /var/log/claude (owned by ${USER})"

# 2. Logrotate
echo "[2/5] Installing logrotate config..."
cp ${WORKSPACE}/automation/logrotate.d/claude-skills /etc/logrotate.d/claude-skills
chmod 644 /etc/logrotate.d/claude-skills
echo "  ✓ /etc/logrotate.d/claude-skills"

# 3. Python dependencies
echo "[3/5] Installing Python dependencies..."
pip3 install pyyaml 2>/dev/null || pip install pyyaml 2>/dev/null || {
    echo "  ⚠ Could not install pyyaml. Install manually: pip3 install pyyaml"
}
echo "  ✓ pyyaml installed"

# 4. Health check cron
echo "[4/5] Setting up health check cron..."
# Install jq if not present (needed by health-check.sh)
which jq > /dev/null 2>&1 || {
    echo "  Installing jq..."
    apt-get install -y jq > /dev/null 2>&1
}
chmod +x ${WORKSPACE}/automation/health-check.sh
# Add to user's crontab (dedup: remove existing line first, then add)
CRON_LINE="0 5 * * * ${WORKSPACE}/automation/health-check.sh"
(crontab -u ${USER} -l 2>/dev/null | grep -v "health-check.sh"; echo "${CRON_LINE}") | crontab -u ${USER} -
echo "  ✓ Health check scheduled at 5:00 UTC daily (7:00 AM IST)"

# 5. Verification
echo "[5/5] Verifying tools..."

echo -n "  Python: "
python3 --version 2>/dev/null || echo "NOT FOUND"

echo -n "  Claude: "
su - ${USER} -c "claude --version" 2>/dev/null || echo "NOT FOUND (check PATH)"

echo -n "  Git: "
git --version 2>/dev/null || echo "NOT FOUND"

echo -n "  Docker: "
docker --version 2>/dev/null || echo "NOT FOUND"

echo -n "  jq: "
jq --version 2>/dev/null || echo "NOT FOUND"

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "  1. Test dry run:    python3 ${WORKSPACE}/automation/skill-runner.py ppc-daily-health --dry-run"
echo "  2. Test real run:   python3 ${WORKSPACE}/automation/skill-runner.py ppc-daily-health --verbose"
echo "  3. Import n8n workflows from: ${WORKSPACE}/automation/n8n-workflows/"
echo "  4. Set SLACK_WORKSPACE_1_BOT_TOKEN in n8n Settings > Variables"
echo ""

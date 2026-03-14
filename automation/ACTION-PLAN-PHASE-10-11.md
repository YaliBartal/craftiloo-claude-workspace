# Phase 10-11 Action Plan: Server Ops, Monitoring, Backup & Security

> **Created:** 2026-03-12
> **Target:** GMKtec NucBox M8 (Ubuntu 24.04) at 10.0.0.22
> **Approach:** 5 implementation phases, smallest-to-largest blast radius. Each phase ends with a verification checkpoint before moving on.
> **Estimated total time:** 3-4 hours hands-on (spread across 1-2 sessions)

---

## Context & Assumptions

- The workspace is replicated on 3 machines (this laptop, server, manager's laptop) via git. The .env file and all code exist in multiple places — there's no single-point-of-failure for source files.
- n8n is **already on PostgreSQL** (not SQLite). The Phase 10-11 doc's suggestion to "switch to PostgreSQL" is already done.
- `skill-api.py` runs as a systemd user service on port 5680.
- Two daily skills are live (daily-market-intel, ppc-daily-health). Weekly/monthly skills are staged in config.yaml but not yet activated in n8n.
- The server is behind a home NAT. No ports are forwarded to the internet.
- Israel timezone (Asia/Jerusalem), DST switches late March and late October.

---

## Phase A: Network Foundation (15 min)

**Goal:** Make sure the server's IP never drifts, and you can reach it from anywhere.

Everything else depends on stable addressing. Do this first.

### A1. Router DHCP Reservation

1. Get the server's MAC address:
   ```bash
   ip link show | grep -A1 "enp\|eth0" | grep ether
   ```
2. Log into router admin (probably `10.0.0.1` or `192.168.1.1`)
3. Find DHCP settings → Address Reservation / Static Lease
4. Reserve `10.0.0.22` for the NucBox's MAC address
5. **Verify:** Reboot the server (`sudo reboot`). After it comes back, confirm it's still at `10.0.0.22` with `ip addr`

### A2. Netplan Static IP (belt-and-suspenders)

1. Check current netplan config:
   ```bash
   ls /etc/netplan/
   cat /etc/netplan/*.yaml
   ```
2. Edit (backup first):
   ```bash
   sudo cp /etc/netplan/*.yaml /etc/netplan/backup.yaml
   sudo nano /etc/netplan/01-netcfg.yaml
   ```
3. Set static IP:
   ```yaml
   network:
     version: 2
     renderer: networkd
     ethernets:
       enp1s0:   # ← replace with your actual interface name
         dhcp4: false
         addresses:
           - 10.0.0.22/24
         routes:
           - to: default
             via: 10.0.0.1   # ← replace with your router's IP
         nameservers:
           addresses: [1.1.1.1, 8.8.8.8]
   ```
4. **Test safely** (auto-reverts after 120s if you don't confirm):
   ```bash
   sudo netplan try
   ```
5. If it works:
   ```bash
   sudo netplan apply
   ```

### A3. mDNS / Avahi (access by hostname)

1. Install (may already be present):
   ```bash
   sudo apt install -y avahi-daemon
   sudo systemctl enable --now avahi-daemon
   ```
2. **Verify from your laptop:**
   ```bash
   ping nucbox.local     # or whatever the hostname is
   ssh yali@nucbox.local
   ```
3. The hostname used is whatever `hostnamectl` shows. If it's something generic, set it:
   ```bash
   sudo hostnamectl set-hostname nucbox
   ```

### A4. Tailscale

1. Install:
   ```bash
   curl -fsSL https://tailscale.com/install.sh | sh
   sudo tailscale up
   ```
2. Open the auth URL it prints → log in with your Tailscale account (free personal plan)
3. Note the Tailscale IP:
   ```bash
   tailscale ip -4
   ```
4. **Disable key expiry** (important for servers): Go to https://login.tailscale.com/admin/machines → find the NucBox → three dots → "Disable key expiry"
5. Install Tailscale on your Windows laptop too (download from tailscale.com)
6. **Verify:**
   ```bash
   # From your laptop, using Tailscale IP
   ssh yali@100.x.x.x
   curl http://100.x.x.x:5678   # n8n UI
   curl http://100.x.x.x:5680/health   # skill-api
   ```

### Phase A Checkpoint

| Test | Expected |
|------|----------|
| `ip addr` on server shows 10.0.0.22 | ✅ |
| `ping nucbox.local` from laptop (same network) | ✅ |
| `ssh yali@100.x.x.x` from laptop via Tailscale | ✅ |
| `curl http://100.x.x.x:5680/health` via Tailscale | ✅ JSON response |

---

## Phase B: Security Hardening (15 min)

**Goal:** Lock down the server. Do this immediately after Tailscale because Tailscale gives you a fallback access path if you accidentally lock yourself out of SSH.

### B1. UFW Firewall

```bash
# Allow SSH first (CRITICAL — do this before enabling UFW)
sudo ufw allow OpenSSH

# Allow local network access to services
sudo ufw allow from 10.0.0.0/24 to any port 5678 proto tcp   # n8n UI
sudo ufw allow from 10.0.0.0/24 to any port 5680 proto tcp   # skill-api

# Tailscale traffic is automatically allowed (it uses its own interface)
# But explicitly allow it to be safe:
sudo ufw allow in on tailscale0

# Enable
sudo ufw enable

# Verify
sudo ufw status verbose
```

**What this does:** Only SSH, n8n, and skill-api are reachable from local network. Everything else is blocked. Tailscale traffic is allowed on its own interface. Nothing is exposed to the internet (NAT already handles this, but defense in depth).

### B2. fail2ban

```bash
sudo apt install -y fail2ban
sudo systemctl enable --now fail2ban
```

Default config bans IPs after 5 failed SSH attempts for 10 minutes. Good enough for a home server.

**Verify:**
```bash
sudo fail2ban-client status sshd
```

### B3. Unattended Security Upgrades

```bash
# Should already be installed on Ubuntu 24.04 Server, but verify:
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

Select "Yes" when prompted. This auto-installs security patches only (not full version upgrades).

**Verify:**
```bash
cat /etc/apt/apt.conf.d/20auto-upgrades
# Should show: APT::Periodic::Unattended-Upgrade "1";
```

### B4. SSH Hardening

1. Confirm you can SSH via key (not just password). If you don't have a key set up yet:
   ```bash
   # From your laptop (Windows PowerShell):
   ssh-keygen -t ed25519
   type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh yali@10.0.0.22 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
   ```
2. Test key-based login works:
   ```bash
   ssh yali@10.0.0.22   # should NOT ask for password
   ```
3. **Only after confirming key login works**, disable password auth:
   ```bash
   sudo nano /etc/ssh/sshd_config
   ```
   Set:
   ```
   PasswordAuthentication no
   PubkeyAuthentication yes
   PermitRootLogin no
   ```
   Restart:
   ```bash
   sudo systemctl restart ssh
   ```
4. **Verify:** Open a NEW terminal and try `ssh yali@10.0.0.22`. It should work with your key. If it doesn't, you can still access via Tailscale or physical console to fix it.

### Phase B Checkpoint

| Test | Expected |
|------|----------|
| `sudo ufw status` shows SSH, 5678, 5680 allowed | ✅ |
| `sudo fail2ban-client status sshd` shows jail active | ✅ |
| SSH via key works, password login rejected | ✅ |
| `unattended-upgrades` enabled | ✅ |
| n8n still accessible at http://10.0.0.22:5678 | ✅ |
| skill-api still accessible at http://10.0.0.22:5680/health | ✅ |

---

## Phase C: Monitoring & Alerting (30-45 min)

**Goal:** Know when things break before you notice they're broken.

### C1. Docker Restart Policies

Verify all containers will survive a reboot:

```bash
# Check current restart policies
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"
docker inspect --format '{{.Name}}: {{.HostConfig.RestartPolicy.Name}}' $(docker ps -q)
```

If any container shows `no` instead of `always` or `unless-stopped`:
```bash
docker update --restart unless-stopped <container_name>
```

**Test:** `sudo reboot` — after it comes back, `docker ps` should show all containers running.

### C2. Portainer (Docker Web UI)

```bash
docker volume create portainer_data

docker run -d \
  -p 9443:9443 \
  --name portainer \
  --restart=always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data \
  portainer/portainer-ce:lts
```

- Access: `https://10.0.0.22:9443` (or `https://100.x.x.x:9443` via Tailscale)
- First visit: create admin password (12+ chars)
- Select "Local" environment → Connect
- Add UFW rule: `sudo ufw allow from 10.0.0.0/24 to any port 9443 proto tcp`
- Also allow on Tailscale: `sudo ufw allow in on tailscale0 to any port 9443 proto tcp`

### C3. Healthchecks.io (External Dead Man's Switch)

This is the most important monitoring piece. If the server dies, Healthchecks.io notices and alerts you.

1. **Sign up** at https://healthchecks.io (free tier: 20 checks)
2. **Create checks** for each critical job:

   | Check Name | Period | Grace |
   |------------|--------|-------|
   | nucbox-health-check | 24 hours | 1 hour |
   | nucbox-daily-market-intel | 24 hours | 2 hours |
   | nucbox-ppc-daily-health | 24 hours | 2 hours |

3. **Integrate with health-check.sh** — add a ping at the end:
   ```bash
   # At the end of health-check.sh, after the Slack post:
   curl -fsS -m 10 --retry 3 https://hc-ping.com/YOUR-UUID-HERE > /dev/null 2>&1
   ```

4. **Integrate with skill-runner.py** — add a `healthcheck_url` field to config.yaml:
   ```yaml
   defaults:
     # ... existing fields ...

   skills:
     daily-market-intel:
       healthcheck_url: "https://hc-ping.com/UUID-FOR-MARKET-INTEL"
       # ... rest of config ...

     ppc-daily-health:
       healthcheck_url: "https://hc-ping.com/UUID-FOR-PPC-HEALTH"
       # ... rest of config ...
   ```

   Then modify `skill-runner.py` to ping the URL on success:
   ```python
   # After successful run, before return:
   hc_url = skill_config.get("healthcheck_url")
   if hc_url and exit_code == 0:
       subprocess.run(["curl", "-fsS", "-m", "10", "--retry", "3", hc_url],
                       capture_output=True, timeout=20)
   ```

5. **Set up alerts in Healthchecks.io:**
   - Add your email as a notification channel
   - Optionally add Slack webhook (Settings → Integrations → Slack)
   - Optionally add Pushover or ntfy for phone push notifications

**Verify:** Wait for the next scheduled run. Check Healthchecks.io dashboard shows a green ping.

### C4. Watchtower (Docker Auto-Update Monitor)

Start in **monitor-only mode** — it notifies you about available updates but doesn't apply them:

```bash
docker run -d \
  --name watchtower \
  --restart=always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  containrrr/watchtower \
  --monitor-only \
  --schedule "0 0 3 * * 0" \
  --cleanup \
  --notifications slack \
  --notification-slack-hook-url "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
```

If you don't have a Slack incoming webhook, skip the notification flags for now and just check Watchtower logs:
```bash
docker logs watchtower
```

**Note:** Keep `--monitor-only` until you've done at least 2-3 manual n8n updates successfully. Then you can remove it if you want auto-updates.

### C5. Netdata (System Metrics Dashboard)

```bash
wget -O /tmp/netdata-kickstart.sh https://get.netdata.cloud/kickstart.sh
sh /tmp/netdata-kickstart.sh --dont-wait
```

- Access: `http://10.0.0.22:19999` (or via Tailscale)
- Add UFW rule: `sudo ufw allow from 10.0.0.0/24 to any port 19999 proto tcp`
- Also allow on Tailscale: `sudo ufw allow in on tailscale0 to any port 19999 proto tcp`

**Configure disk alert** (important — skill outputs grow daily):
```bash
sudo nano /etc/netdata/health.d/custom-disk.conf
```
```
alarm: disk_space_warning
on: disk.space
lookup: min -1m unaligned of avail
units: GiB
every: 1m
warn: $this < 10
crit: $this < 5
info: Available disk space
```
```bash
sudo systemctl restart netdata
```

**Optional: Netdata Cloud** — create a free account at app.netdata.cloud to view metrics remotely without Tailscale. Netdata agent connects outbound (no port forwarding needed).

### C6. Dozzle (Docker Log Viewer) — Optional, Low Priority

```bash
docker run -d \
  -p 9999:8080 \
  --name dozzle \
  --restart=always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  amir20/dozzle:latest
```

Access: `http://10.0.0.22:9999`. Useful for tailing n8n container logs in a browser instead of `docker logs -f`.

### Phase C Checkpoint

| Test | Expected |
|------|----------|
| Portainer shows all containers at https://10.0.0.22:9443 | ✅ |
| Healthchecks.io shows green for health-check | ✅ (after next 7AM run) |
| `docker ps` shows watchtower running | ✅ |
| Netdata dashboard at http://10.0.0.22:19999 shows CPU/RAM/disk | ✅ |
| `sudo reboot` → all containers come back automatically | ✅ |
| Containers accessible via Tailscale IP | ✅ |

---

## Phase D: Backup & Recovery (45-60 min)

**Goal:** Protect what git doesn't cover — n8n database, n8n credentials/encryption key, Docker volumes, server config.

### What actually needs backing up (revised)

The workspace code, .env, and skill outputs are already in git across 3 machines. What's **only on the server** and **not in git**:

| Item | Why it matters | How bad if lost |
|------|---------------|-----------------|
| **n8n Docker volume** | All workflows, credentials (encrypted), execution history | HIGH — rebuilding workflows from JSON backups works but credentials need re-entering |
| **PostgreSQL data** | n8n's database (workflows, executions, settings) | HIGH — same as above |
| **n8n encryption key** | Decrypts stored credentials | CRITICAL — without it, credential backups are useless |
| **Server config** | Netplan, UFW rules, SSH config, systemd services, logrotate | LOW — can recreate from setup.sh + this action plan, but annoying |
| **Crontab** | Health check schedule | LOW — one line, easy to recreate |
| **Tailscale state** | VPN identity | LOW — can re-auth, but means new Tailscale IP |

### D1. Install Restic

```bash
sudo apt install -y restic
```

### D2. Set Up Backblaze B2 (Cloud Backup Target)

1. Create account at https://www.backblaze.com/b2 (first 10GB free)
2. Create a bucket:
   - Name: `craftiloo-nucbox-backup` (must be globally unique, adjust if taken)
   - Private, no encryption at rest (restic handles encryption), no lifecycle rules
3. Create an application key:
   - Key name: `nucbox-restic`
   - Bucket: restrict to the bucket you just created
   - Capabilities: all (read, write, list, delete)
   - Note the `keyID` and `applicationKey` — you'll need both

### D3. Initialize Restic Repository

```bash
# Set credentials (add to ~/.bashrc for persistence)
export B2_ACCOUNT_ID="your-key-id"
export B2_ACCOUNT_KEY="your-application-key"
export RESTIC_REPOSITORY="b2:craftiloo-nucbox-backup:/"
export RESTIC_PASSWORD="generate-a-strong-passphrase-here"

# Initialize the repository (one-time)
restic init
```

**CRITICAL:** Save `RESTIC_PASSWORD` somewhere outside the server (password manager, printed paper, manager's machine). Without it, backups are unrecoverable.

### D4. Create Backup Script

Create `/home/yali/workspace/automation/backup.sh`:

```bash
#!/bin/bash
# backup.sh — Daily automated backup to Backblaze B2 via restic
# Covers: n8n database, Docker volumes, server config
# The workspace code/outputs are already in git across 3 machines.
#
# Install: add to crontab — 0 1 * * * /home/yali/workspace/automation/backup.sh
# (1:00 AM IST, before any skill runs)

set -euo pipefail

LOG_FILE="/var/log/claude/backup-$(date +%Y-%m-%d).log"
BACKUP_STAGING="/tmp/nucbox-backup-staging"

# Restic credentials
export B2_ACCOUNT_ID="your-key-id"
export B2_ACCOUNT_KEY="your-application-key"
export RESTIC_REPOSITORY="b2:craftiloo-nucbox-backup:/"
export RESTIC_PASSWORD="your-restic-password"

log() { echo "[$(date '+%H:%M:%S')] $1" | tee -a "$LOG_FILE"; }

log "=== Backup started ==="

# Clean staging area
rm -rf "$BACKUP_STAGING"
mkdir -p "$BACKUP_STAGING"

# 1. Dump n8n PostgreSQL database
log "Dumping n8n PostgreSQL..."
docker exec n8n-postgres pg_dump -U n8n n8n | gzip > "$BACKUP_STAGING/n8n-db-dump.sql.gz"
log "  Done ($(du -h "$BACKUP_STAGING/n8n-db-dump.sql.gz" | cut -f1))"

# 2. Export n8n workflows via API (human-readable JSON backup)
log "Exporting n8n workflows..."
curl -s http://localhost:5678/api/v1/workflows \
  -H "X-N8N-API-KEY: ${N8N_API_KEY:-}" \
  > "$BACKUP_STAGING/n8n-workflows-export.json" 2>/dev/null || \
  log "  WARNING: n8n API export failed (API key not set?). DB dump is the primary backup."

# 3. Capture n8n encryption key (CRITICAL — needed to decrypt credentials in DB)
log "Backing up n8n encryption key..."
docker exec n8n-app printenv N8N_ENCRYPTION_KEY > "$BACKUP_STAGING/n8n-encryption-key.txt" 2>/dev/null || \
  log "  WARNING: Could not read encryption key from container env"

# 4. Capture server config
log "Backing up server config..."
mkdir -p "$BACKUP_STAGING/server-config"
cp /etc/netplan/*.yaml "$BACKUP_STAGING/server-config/" 2>/dev/null || true
sudo ufw status verbose > "$BACKUP_STAGING/server-config/ufw-rules.txt" 2>/dev/null || true
cp /etc/ssh/sshd_config "$BACKUP_STAGING/server-config/" 2>/dev/null || true
crontab -l > "$BACKUP_STAGING/server-config/crontab.txt" 2>/dev/null || true
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}" > "$BACKUP_STAGING/server-config/docker-containers.txt"
dpkg --get-selections > "$BACKUP_STAGING/server-config/installed-packages.txt"
systemctl --user cat skill-api > "$BACKUP_STAGING/server-config/skill-api-service.txt" 2>/dev/null || true

# 5. Copy systemd user services
cp -r ~/.config/systemd/user/ "$BACKUP_STAGING/server-config/systemd-user/" 2>/dev/null || true

# 6. Run restic backup
log "Running restic backup..."
restic backup \
  "$BACKUP_STAGING" \
  --tag "daily" \
  --tag "$(date +%Y-%m-%d)" \
  2>&1 | tee -a "$LOG_FILE"

# 7. Prune old backups (keep 7 daily, 4 weekly, 3 monthly)
log "Pruning old snapshots..."
restic forget \
  --keep-daily 7 \
  --keep-weekly 4 \
  --keep-monthly 3 \
  --prune \
  2>&1 | tee -a "$LOG_FILE"

# 8. Clean up staging
rm -rf "$BACKUP_STAGING"

# 9. Ping Healthchecks.io
if [ -n "${BACKUP_HC_URL:-}" ]; then
  curl -fsS -m 10 --retry 3 "$BACKUP_HC_URL" > /dev/null 2>&1
fi

log "=== Backup complete ==="

# 10. Post to Slack on failure only (success is silent)
# The Healthchecks.io dead man's switch handles "backup didn't run" alerts.
# This catches "backup ran but errored":
# (The set -e at the top means we only reach here on success)
```

```bash
chmod +x /home/yali/workspace/automation/backup.sh
```

### D5. Add Restic Credentials to .bashrc

```bash
cat >> ~/.bashrc << 'EOF'

# Restic backup credentials
export B2_ACCOUNT_ID="your-key-id"
export B2_ACCOUNT_KEY="your-application-key"
export RESTIC_REPOSITORY="b2:craftiloo-nucbox-backup:/"
export RESTIC_PASSWORD="your-restic-password"
EOF
```

### D6. Schedule Backup Cron

```bash
crontab -e
```

Add:
```
# Daily backup at 1:00 AM IST (before any skill runs)
0 23 * * * /home/yali/workspace/automation/backup.sh >> /var/log/claude/backup-cron.log 2>&1
```

(Note: 23:00 UTC = 1:00 AM IST during winter, adjust for DST)

### D7. Create Healthchecks.io Check for Backup

1. Create a new check: `nucbox-backup`, period 24 hours, grace 2 hours
2. Set the `BACKUP_HC_URL` in the backup script to the ping URL

### D8. Test the Backup

```bash
# Run manually
/home/yali/workspace/automation/backup.sh

# Verify snapshots exist
restic snapshots

# Test restore to temp dir
mkdir /tmp/restore-test
restic restore latest --target /tmp/restore-test
ls -la /tmp/restore-test/tmp/nucbox-backup-staging/
# Should see: n8n-db-dump.sql.gz, server-config/, etc.
rm -rf /tmp/restore-test
```

### D9. Document Recovery Procedures

Add to the bottom of the backup script or create a `RECOVERY.md`:

| Scenario | Steps |
|----------|-------|
| **n8n database corrupted** | 1. `restic restore latest --target /tmp/restore` 2. `gunzip /tmp/restore/.../n8n-db-dump.sql.gz` 3. `docker exec -i n8n-postgres psql -U n8n n8n < /tmp/restore/.../n8n-db-dump.sql` 4. Restart n8n: `docker restart n8n-app` |
| **n8n credentials lost** | Restore DB dump (above) + set `N8N_ENCRYPTION_KEY` from backup to the same value in docker-compose |
| **Server hardware failure** | 1. New Ubuntu 24.04 install 2. Clone workspace from git 3. Run `setup.sh` 4. Install Docker, n8n, skill-api 5. `restic restore latest` → restore n8n DB + config 6. Install Tailscale (`tailscale up` with new auth) |
| **Accidentally broke Ubuntu** | Boot USB → reinstall → same as hardware failure recovery |

### Phase D Checkpoint

| Test | Expected |
|------|----------|
| `restic snapshots` shows at least 1 snapshot | ✅ |
| Snapshot contains n8n-db-dump.sql.gz | ✅ |
| Healthchecks.io backup check is green | ✅ (after first cron run) |
| Test restore produces valid files | ✅ |
| Restic password is saved somewhere OFF the server | ✅ |

---

## Phase E: Quality of Life & Polish (20-30 min)

**Goal:** Nice-to-haves that improve daily experience but aren't critical.

### E1. Push Notifications for Critical Alerts

Pick ONE of these (ntfy is free and self-hostable, Pushover is $5 one-time):

**Option A: ntfy.sh (free)**
```bash
# No server install needed — use the public ntfy.sh server
# Subscribe on your phone: install ntfy app → subscribe to "craftiloo-nucbox" topic

# Test:
curl -d "Server backup failed!" ntfy.sh/craftiloo-nucbox-alerts

# Add to health-check.sh for critical alerts:
# If disk > 90%:
DISK_NUM=$(df / | awk 'NR==2 {print int($5)}')
if [ "$DISK_NUM" -gt 90 ]; then
  curl -d "CRITICAL: NucBox disk at ${DISK_NUM}%!" -H "Priority: urgent" ntfy.sh/craftiloo-nucbox-alerts
fi
```

**Option B: Pushover ($5 one-time)**
- Buy at https://pushover.net, create an application
- API is a simple curl POST
- Better notification UX on iOS/Android than ntfy

### E2. Enhance health-check.sh

Add these checks to the existing health-check.sh:

```bash
# After existing metrics gathering, add:

# Disk space warning
DISK_NUM=$(df / | awk 'NR==2 {print int($5)}')
DISK_WARNING=""
if [ "$DISK_NUM" -gt 80 ]; then
  DISK_WARNING="\n:warning: *Disk usage above 80%!* Clean up /var/log or outputs/"
fi

# Check if skill-api is responding
SKILL_API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5680/health 2>/dev/null || echo "DOWN")
if [ "$SKILL_API_STATUS" != "200" ]; then
  SKILL_API_MSG=":red_circle: skill-api is DOWN"
else
  SKILL_API_MSG=":white_check_mark: skill-api responding"
fi

# Check if n8n is responding
N8N_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5678/healthz 2>/dev/null || echo "DOWN")
if [ "$N8N_STATUS" != "200" ]; then
  N8N_MSG=":red_circle: n8n is DOWN"
else
  N8N_MSG=":white_check_mark: n8n responding"
fi

# Check last backup
LAST_BACKUP=$(ls -t /var/log/claude/backup-*.log 2>/dev/null | head -1)
if [ -n "$LAST_BACKUP" ]; then
  BACKUP_MSG="Last backup: $(basename $LAST_BACKUP .log | sed 's/backup-//')"
else
  BACKUP_MSG=":warning: No backup logs found"
fi
```

Then add these to the Slack message body.

### E3. SSH Config on Your Laptop

Create/edit `C:\Users\YourName\.ssh\config` (Windows) or `~/.ssh/config` (Mac/Linux):

```
Host nucbox
    HostName 10.0.0.22
    User yali

Host nucbox-ts
    HostName 100.x.x.x
    User yali
```

Now: `ssh nucbox` from home, `ssh nucbox-ts` from anywhere.

### E4. UPS (When You Buy One)

- **Recommended:** APC Back-UPS BE600M1 (~$55-70). Gives 30-60 min runtime for the mini PC.
- After purchase:
  ```bash
  sudo apt install -y nut nut-client nut-server
  ```
- Configure NUT per the Phase 10-11 doc section 11F
- Add a Healthchecks.io check for "server rebooted unexpectedly" by pinging on boot:
  ```bash
  # Add to crontab:
  @reboot curl -fsS -m 10 https://hc-ping.com/REBOOT-UUID
  ```

### Phase E Checkpoint

| Test | Expected |
|------|----------|
| Push notification received on phone (test) | ✅ |
| `ssh nucbox` works from laptop on home network | ✅ |
| `ssh nucbox-ts` works from laptop via Tailscale | ✅ |
| health-check.sh Slack message includes service status | ✅ |

---

## Implementation Schedule (Suggested)

| Session | What | Time |
|---------|------|------|
| **Session 1** | Phase A (networking) + Phase B (security) | ~30 min |
| **Session 2** | Phase C (monitoring) | ~45 min |
| **Session 3** | Phase D (backup) | ~60 min |
| **Session 4** | Phase E (polish) — can be done anytime | ~20 min |

You can do sessions 1+2 in one sitting (75 min). Session 3 requires the Backblaze B2 signup which might be a natural break point.

---

## What NOT to Do (Yet)

| Item | Why skip for now |
|------|-----------------|
| **Prometheus + Grafana** | Overkill for one server. Netdata covers everything. |
| **SOPS/age secrets encryption** | .env is on 3 machines in git-ignored files. Not the biggest risk right now. Revisit if you add team members. |
| **HashiCorp Vault** | Way overkill. |
| **Cloudflare Tunnel** | Tailscale is simpler and sufficient. Only consider if you need to expose webhooks publicly. |
| **n8n PostgreSQL switch** | Already done. |
| **Uptime Kuma** | Healthchecks.io + Netdata cover the same ground without running another container. Add later if you want a status page. |
| **Custom log dashboard** | n8n execution history + Dozzle + JSON logs are enough. |

---

## Files Modified By This Plan

| File | Change |
|------|--------|
| `automation/health-check.sh` | Add Healthchecks.io ping + enhanced checks (Phase C3, E2) |
| `automation/config.yaml` | Add `healthcheck_url` per skill (Phase C3) |
| `automation/skill-runner.py` | Add Healthchecks.io ping on success (Phase C3) |
| `automation/backup.sh` | **NEW** — daily backup script (Phase D4) |
| `automation/AUTOMATION-PLAN.md` | Update "What's Active" section after each phase |

---

## Post-Implementation: Ongoing Maintenance

| Task | Frequency | How |
|------|-----------|-----|
| Check Healthchecks.io dashboard | Glance daily | Should be all green |
| Review Netdata alerts | When notified | Fix disk/memory issues |
| Test backup restore | Monthly | `restic restore latest --target /tmp/test` |
| Update n8n | When Watchtower notifies | Check release notes → `docker compose pull && up -d` |
| Review fail2ban bans | Monthly | `sudo fail2ban-client status sshd` |
| Rotate Restic password | Yearly | Update in .bashrc + backup script + password manager |
| Check Tailscale status | After router changes | `tailscale status` |

# Phase 10 & 11: Server Operations, Monitoring, Backup & Security

> **Purpose:** Reference document for setting up the full operational layer on the GMKtec NucBox M8 (Ubuntu 24.04). This covers everything beyond "skills run" — making sure we **know when things break, can access the server from anywhere, keep it secure, and can recover from disasters.**
>
> **How to use:** Send this to the server's Claude session to create an action plan. Not a step-by-step guide — it's a landscape of tools and approaches, prioritized.

---

## Current State (what's already done)

- n8n running in Docker (scheduler + UI at http://10.0.0.22:5678)
- `skill-runner.py` + `config.yaml` handling all skill execution
- `health-check.sh` posting daily metrics to Slack #claude-alerts
- `logrotate` configured for `/var/log/claude/` (weekly rotation, 12 weeks)
- Git auto-pull/commit/push after each skill run
- Basic cron for health check

### What's missing

- No way to access the server remotely (outside home network)
- No alerting if a scheduled skill silently stops running
- No Docker container auto-restart or update policy
- No backup of n8n database, configs, or workspace
- No security hardening (SSH, firewall, auto-updates)
- No disk/memory alerting (only passive daily report)
- No centralized view of all skill run history and health
- No recovery plan if the server dies or Ubuntu breaks

---

## Phase 10: Monitoring, Alerting & Remote Access

### 10A: Remote Access (Priority: HIGH)

Without this, you can only manage the server while on your home network.

#### Tailscale (recommended)
- **What:** WireGuard-based mesh VPN. Creates a permanent IP (100.x.x.x) for the server accessible from anywhere — laptop, phone, coffee shop
- **Why it fits:** Zero config networking, no port forwarding, no dynamic DNS. Free for personal use (up to 100 devices)
- **What it enables:**
  - SSH from anywhere: `ssh yali@100.x.x.x`
  - n8n UI from anywhere: `http://100.x.x.x:5678`
  - Portainer from anywhere: `http://100.x.x.x:9000`
- **Install:** `curl -fsSL https://tailscale.com/install.sh | sh && sudo tailscale up`
- **Also install on:** Your Windows laptop (Tailscale app) and phone (iOS/Android app)
- **Bonus: Tailscale SSH** — replaces traditional SSH keys, uses Tailscale identity. Even simpler.
- **Bonus: Tailscale Funnel** — if you ever need to expose a service publicly (webhook receiver, etc.)

#### Alternative: Cloudflare Tunnel (Zero Trust)
- Free, no port forwarding needed
- Better if you want to expose n8n behind auth on a real domain (e.g., `n8n.craftiloo.dev`)
- More complex setup than Tailscale but more powerful for web-facing services
- `cloudflared tunnel` daemon runs on server, tunnels traffic through Cloudflare

#### Alternative: WireGuard (manual)
- Tailscale is built on this. Only use raw WireGuard if you want full control and don't mind manual key management.

---

### 10B: Docker Management (Priority: HIGH)

n8n runs in Docker. Other monitoring tools will too. Need proper container lifecycle management.

#### Portainer CE (recommended)
- **What:** Web-based Docker management UI
- **Why:** Visual container health, logs, restart, resource usage — without memorizing Docker CLI commands
- **What it shows:**
  - All running containers with status, uptime, resource usage
  - Container logs (live tail)
  - One-click restart/stop/remove
  - Docker Compose stack management
  - Volume and network inspection
- **Install:** Single Docker command:
  ```
  docker volume create portainer_data
  docker run -d -p 9000:9000 --name portainer --restart=always \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v portainer_data:/data portainer/portainer-ce:latest
  ```
- **Access:** `http://10.0.0.22:9000` (or via Tailscale IP)

#### Watchtower (recommended)
- **What:** Automatically updates Docker containers when new images are published
- **Why:** n8n publishes updates frequently. Watchtower keeps it current without manual intervention
- **Config options:**
  - Schedule checks (e.g., weekly on Sunday 3 AM)
  - Notify via Slack/email when updates are applied
  - Monitor-only mode (notify but don't auto-update) — good for production caution
  - Label-based: only auto-update containers you explicitly tag
- **Install:**
  ```
  docker run -d --name watchtower --restart=always \
    -v /var/run/docker.sock:/var/run/docker.sock \
    containrrr/watchtower --schedule "0 0 3 * * 0" --cleanup
  ```
- **Risk:** Auto-updating n8n could break workflows if there's a breaking change. Consider monitor-only mode initially, or pin n8n to a specific version and update manually after checking release notes.

#### Docker restart policies
- Ensure all containers have `--restart=always` or `--restart=unless-stopped`
- This means n8n comes back after server reboot, power outage, or Docker daemon restart
- Verify: `docker inspect n8n --format '{{.HostConfig.RestartPolicy.Name}}'`

---

### 10C: Uptime & Dead-Man-Switch Monitoring (Priority: HIGH)

The health-check.sh script tells you the server is alive. But what if health-check.sh itself stops running?

#### Healthchecks.io (recommended)
- **What:** Dead man's switch / cron job monitor. You create a check, it gives you a unique ping URL. If the URL isn't pinged within the expected interval, it alerts you.
- **Free tier:** 20 checks, unlimited team members
- **How to use:**
  - Create a check per critical job: "health-check", "daily-market-intel", "ppc-daily-health"
  - Add a `curl` ping at the end of each successful run
  - Healthchecks.io alerts (email/Slack/push) if a ping is missed
  - Supports "start" + "success/fail" ping pattern for duration tracking
- **Integration with skill-runner.py:** Add a `healthcheck_url` field per skill in config.yaml. Runner pings on success.
- **Integration with health-check.sh:** Add `curl -fsS -m 10 --retry 5 https://hc-ping.com/{uuid}` at the end
- **Dashboard:** Web UI shows all checks with status, last ping time, uptime %

#### Alternative: Uptime Kuma (self-hosted)
- **What:** Self-hosted monitoring dashboard (like a personal StatusPage)
- **Why consider:** No external dependency, runs on the same server, beautiful UI
- **Monitors:**
  - HTTP endpoints (n8n UI, Portainer)
  - TCP ports (SSH)
  - Docker containers (via Docker socket)
  - Ping (server itself from external — but needs an external checker for that)
  - Push-based (like Healthchecks.io dead man's switch)
- **Notifications:** Slack, email, Telegram, Discord, Pushover, many more
- **Install:** `docker run -d -p 3001:3001 --restart=always --name uptime-kuma -v uptime-kuma:/app/data louislam/uptime-kuma:1`
- **Limitation:** It's ON the server — if the server dies, Uptime Kuma dies too. Pair with Healthchecks.io for external monitoring of the server itself.

#### Recommended combo
- **Healthchecks.io** (external) — monitors that the server is alive and skills are running
- **Uptime Kuma** (self-hosted) — monitors n8n, Docker, internal services, provides a dashboard

---

### 10D: System Metrics & Resource Monitoring (Priority: MEDIUM)

The health-check.sh gives a daily snapshot. For real-time visibility:

#### Netdata (recommended for simplicity)
- **What:** Real-time system monitoring with web dashboard. Zero config.
- **What it shows out of the box:**
  - CPU, RAM, disk I/O, network, per-process resource usage
  - Docker container metrics (CPU/RAM per container)
  - Disk space trending (predict when you'll run out)
  - Alerts when thresholds are crossed (disk > 80%, RAM > 90%, etc.)
- **Install:** One-liner: `wget -O /tmp/netdata-kickstart.sh https://get.netdata.cloud/kickstart.sh && sh /tmp/netdata-kickstart.sh`
- **Access:** `http://10.0.0.22:19999`
- **Cloud option:** Free Netdata Cloud account syncs metrics for remote viewing even without Tailscale
- **Alerts:** Built-in disk/memory/CPU alerts. Can route to Slack.

#### Alternative: Prometheus + Grafana
- Industry standard, extremely powerful, but overkill for a single mini PC
- Only consider if you want custom dashboards or plan to monitor multiple servers
- Setup is significantly more complex (Prometheus scraping, Grafana datasource config, dashboard building)

#### Alternative: Glances
- Terminal-based system monitor (like htop on steroids)
- `pip install glances` → run `glances` over SSH
- Has a web mode: `glances -w` → `http://10.0.0.22:61208`
- Lightweight, no Docker needed, good for quick SSH checks

#### Key metrics to alert on
| Metric | Warning | Critical | Why |
|--------|---------|----------|-----|
| Disk usage | > 75% | > 90% | Skill outputs + logs grow daily |
| RAM usage | > 80% | > 95% | Claude CLI + n8n + MCP servers compete for RAM |
| CPU sustained | > 80% for 10min | > 95% for 5min | Skill stuck in loop |
| Swap usage | Any | > 50% | Mini PC has limited RAM, swap = slowness |
| Docker container down | — | n8n not running | Skills won't trigger |
| Load average | > 4 (on 4-core) | > 8 | System overloaded |

---

### 10E: Log Aggregation & Skill Run History (Priority: MEDIUM)

Currently logs are JSON files in `/var/log/claude/`. Searchable via `jq` but not visual.

#### Dozzle (recommended — lightweight)
- **What:** Real-time Docker log viewer in the browser
- **Why:** See n8n logs, skill output, container errors — all in one UI
- **Install:** `docker run -d -p 9999:8080 --restart=always --name dozzle -v /var/run/docker.sock:/var/run/docker.sock amir20/dozzle:latest`
- **Access:** `http://10.0.0.22:9999`
- **Limitation:** Only shows Docker container logs, not the skill-runner JSON logs

#### n8n's built-in execution history
- n8n already stores execution history (success/fail, duration, input/output per node)
- Access: n8n UI → Executions tab
- Configure retention: n8n environment variable `EXECUTIONS_DATA_MAX_AGE=168` (hours to keep)
- This is already your primary skill run history — leverage it

#### Custom log dashboard (future consideration)
- A simple script that reads `/var/log/claude/*.json` and generates an HTML dashboard
- Shows: last run per skill, success/fail trend, duration trend, error patterns
- Could be served by a tiny Python HTTP server or Caddy
- Low priority — n8n execution history covers most of this

---

### 10F: Notification Routing & Escalation (Priority: MEDIUM)

Currently: health-check.sh posts to #claude-alerts. Skill failures post to #claude-alerts via n8n.

#### Enhance with severity tiers

| Severity | Channel | When |
|----------|---------|------|
| Info | #claude-alerts | Daily health check, successful skill completions (optional) |
| Warning | #claude-alerts | Skill failed but will retry, disk > 75%, high memory |
| Critical | #claude-alerts + **Push notification** | Server unreachable, n8n down, multiple consecutive skill failures |

#### Push notifications for critical alerts
- **Pushover** ($5 one-time, iOS/Android) — simple API, `curl` one-liner to push to phone
- **ntfy.sh** (free, self-hostable) — pub/sub push notifications, phone app subscribes to topics
- **Telegram bot** (free) — create bot via @BotFather, send messages via API
- Any of these ensure you see critical alerts even if you're not checking Slack

---

## Phase 11: Backup & Disaster Recovery

### 11A: What Needs Backing Up

| Item | Location | Size | Changes | Criticality |
|------|----------|------|---------|-------------|
| **n8n database** | Docker volume (`n8n_data`) | ~5-50 MB | Every workflow edit/execution | HIGH — all workflows, credentials, history |
| **n8n workflows (JSON exports)** | `automation/n8n-workflows/` | ~50 KB | Rarely | MEDIUM — already in git |
| **.env file** | `/home/yali/workspace/.env` | ~5 KB | Rarely | CRITICAL — 71 API keys, tokens, secrets |
| **config.yaml** | `automation/config.yaml` | ~3 KB | Occasionally | LOW — already in git |
| **Skill outputs** | `outputs/` | ~500 MB+ growing | Daily | MEDIUM — in git, but git is on this server |
| **Crontab** | `crontab -l` | ~1 KB | Rarely | LOW — easy to recreate |
| **Docker compose / run commands** | Not yet formalized | ~1 KB | Rarely | MEDIUM — document how containers were started |
| **SSH keys & Tailscale state** | `~/.ssh/`, `/var/lib/tailscale/` | ~10 KB | Rarely | MEDIUM — can regenerate but annoying |
| **Server packages & config** | `/etc/` (logrotate, etc.) | Varies | Rarely | LOW — setup.sh can recreate |

### 11B: Backup Tools

#### Restic (recommended)
- **What:** Fast, encrypted, deduplicated backup program
- **Why:** Incremental backups (only changed blocks), encryption at rest, multiple backend targets
- **Backends:** Local disk, SFTP, S3, Backblaze B2, Google Cloud Storage, rclone (anything rclone supports)
- **Key features:**
  - Snapshots — each backup is a point-in-time snapshot, browsable
  - Deduplication — only stores changed data, very space-efficient
  - Encryption — all data encrypted with a password before leaving the machine
  - Prune policies — keep last 7 daily, 4 weekly, 6 monthly snapshots automatically
  - Verify — `restic check` validates backup integrity
- **Install:** `sudo apt install restic`
- **Fits well because:** Workspace is mostly text/JSON files that change incrementally

#### Alternative: BorgBackup
- Similar to restic (dedup, encryption, snapshots)
- Slightly more mature, slightly less user-friendly
- Requires a borg server on the remote end (or BorgBase service)
- Choose borg if you already know it, otherwise restic is simpler

#### Alternative: Simple rsync + tar
- `rsync` to mirror workspace to external drive or remote server
- `tar` the n8n Docker volume periodically
- No dedup, no encryption, no snapshot management — but dead simple
- Fine as a starting point if restic feels like overkill

### 11C: Where to Back Up To

**Rule: Backups must be OFF this machine.** A backup on the same disk as the data protects against nothing.

| Target | Cost | Pros | Cons |
|--------|------|------|------|
| **Backblaze B2** | ~$0.005/GB/mo (~$0.05/mo for 10GB) | Cheap, S3-compatible, restic native support | Requires account setup |
| **Google Drive** (via rclone) | Free (15GB) | Already have Google account | rclone config needed, not ideal for automated backups |
| **External USB drive** | $0 (if you have one) | Simple, fast, no internet needed | Not offsite — fire/theft loses both |
| **Another computer on LAN** | $0 | Fast, local | Still not offsite |
| **GitHub (git push)** | $0 | Already doing this for workspace | .env and n8n DB are NOT in git (correctly) — doesn't cover everything |
| **Hetzner Storage Box** | €3.50/mo (1TB) | EU-based, SFTP/rsync/restic native, reliable | Monthly cost |

**Recommended:** Backblaze B2 for cloud backup (pennies/month) + external USB drive for local fast-recovery copy.

### 11D: Backup Strategy

#### Automated backup script
A single script that:
1. Exports n8n workflows via n8n API (`GET /api/v1/workflows`) → JSON files
2. Dumps n8n Docker volume (`docker cp` or `docker exec` + sqlite3 `.backup`)
3. Copies `.env` file
4. Captures `crontab -l` and `docker ps` output
5. Captures list of installed packages (`dpkg --get-selections`)
6. Runs `restic backup` on the whole workspace + the above exports
7. Runs `restic forget --prune` with retention policy
8. Pings Healthchecks.io on success
9. Alerts Slack on failure

#### Schedule
| Backup | Frequency | What | Retention |
|--------|-----------|------|-----------|
| Full workspace + n8n DB | Daily 3:00 AM | Everything in 11A | 7 daily, 4 weekly, 3 monthly |
| .env file | After every change (manual) | Just the secrets file | Keep all versions |
| n8n workflow export | Daily (part of backup script) | All workflows as JSON | Part of workspace backup |

#### Restore testing
- **Monthly:** Pick a random backup, restore to a temp directory, verify files are intact
- `restic restore latest --target /tmp/restore-test/ && diff -rq /tmp/restore-test/workspace ~/workspace`
- Automate this as a monthly cron that posts result to Slack

### 11E: Disaster Recovery Plan

| Scenario | Recovery |
|----------|----------|
| **Skill outputs corrupted** | `git checkout` or `restic restore` specific files |
| **n8n database corrupted** | Restore n8n Docker volume from backup, reimport workflows from JSON |
| **.env deleted/corrupted** | Restore from backup (this is the most critical file to protect) |
| **Docker breaks** | Reinstall Docker, `docker run` commands recreate containers, restore n8n volume |
| **Ubuntu breaks** | Fresh Ubuntu install, run setup.sh, restore workspace + .env + n8n from backup |
| **Mini PC hardware failure** | Buy replacement, fresh Ubuntu, restore everything from Backblaze B2 |
| **Power outage** | UPS keeps server alive for 15-30 min. Docker restart policies bring containers back after hard shutdown. |

### 11F: UPS (Uninterruptible Power Supply)

- **What:** Battery backup that keeps the server running during power outages
- **Why:** Prevents hard shutdowns mid-skill-run, avoids file corruption, avoids n8n database corruption
- **Size needed:** Mini PC draws ~15-30W. A 600VA UPS gives 30-60 minutes of runtime.
- **Software:** `apcupsd` or `nut` (Network UPS Tools) — auto-shutdown when battery gets low
- **Cost:** $40-80 for a basic unit
- **Priority:** MEDIUM — Israel's power grid is stable, but one bad shutdown can corrupt the n8n SQLite database

---

## Phase 10+: Additional Tools Worth Considering

### Security Hardening (Priority: HIGH)

#### UFW (Uncomplicated Firewall)
- **Already on Ubuntu**, just needs enabling
- Allow only: SSH (22), n8n (5678), Portainer (9000), monitoring ports
- Block everything else
- `sudo ufw default deny incoming && sudo ufw allow ssh && sudo ufw allow 5678 && sudo ufw enable`
- If using Tailscale: only allow Tailscale interface for non-SSH ports (even more secure)

#### fail2ban
- **What:** Bans IPs that fail SSH login repeatedly
- **Why:** If SSH is exposed (even via Tailscale), brute force protection is cheap insurance
- **Install:** `sudo apt install fail2ban`
- Default config bans after 5 failed attempts for 10 minutes — good enough

#### Unattended Upgrades
- **What:** Auto-installs Ubuntu security patches
- **Why:** Server runs 24/7, can't rely on manual `apt upgrade`
- **Install:** `sudo apt install unattended-upgrades && sudo dpkg-reconfigure unattended-upgrades`
- Configure to only auto-install security updates, not full upgrades (avoids breaking changes)
- Optional: email/Slack notification when updates are applied

#### SSH hardening
- Disable password auth (use key-only): `PasswordAuthentication no` in `/etc/ssh/sshd_config`
- Change SSH port from 22 to something non-standard (reduces noise, not security)
- If using Tailscale SSH, can disable traditional SSH entirely

### Secrets Management (Priority: MEDIUM)

Currently: all 71 secrets in a `.env` file on disk. Works but risky (one `cat` away from exposure).

#### Age / SOPS (recommended for your scale)
- **SOPS** (by Mozilla): Encrypts YAML/JSON/ENV files, decrypts at runtime
- **age** is the encryption backend (simpler than GPG)
- Workflow: `.env` stored encrypted in git, decrypted on the server via age key
- Solves: "what if someone gets access to the repo or server filesystem"
- Lightweight, no external service

#### Alternative: HashiCorp Vault
- Overkill for a single server, but industry standard for secrets management
- Only consider if you expand to multiple servers or team members

#### Alternative: Bitwarden CLI
- If you already use Bitwarden, its CLI can fetch secrets programmatically
- `bw get notes "craftiloo-env"` → pipe to .env file

### n8n Quality of Life (Priority: MEDIUM)

#### n8n Credentials Store
- n8n has its own credential management (Settings → Credentials)
- Store the Slack bot token there instead of in workflow JSON
- Other skills' API keys could be stored here too if n8n ever calls APIs directly

#### n8n Community Nodes
- Check if there are community nodes for services you use
- e.g., Slack node (built-in), HTTP Request node (for any API)
- Could simplify failure alerting workflows

#### n8n Database: Switch to PostgreSQL
- Default n8n uses SQLite — fine for small scale but can corrupt on hard shutdown
- PostgreSQL is more resilient and supports concurrent access
- Docker Compose makes this easy — add a postgres container, set `DB_TYPE=postgresdb` in n8n env
- Consider this if you experience any SQLite corruption issues

### Process Management (Priority: LOW)

#### systemd service for non-Docker processes
- If any process runs outside Docker (e.g., a future webhook listener, the backup script daemon)
- Create a systemd unit file → auto-start on boot, auto-restart on crash, journalctl logging
- Not needed now since n8n handles scheduling and Docker handles container lifecycle

### Static Local IP (Priority: HIGH)

The server is currently at `10.0.0.22`. If the router reassigns this IP (power outage, DHCP lease expiry, router reboot), everything breaks — n8n URLs, SSH aliases, any hardcoded references. Two approaches, use both for belt-and-suspenders:

#### Approach 1: Router-side DHCP reservation (recommended first step)
- **What:** Tell the router "always give this MAC address the same IP"
- **How:** Router admin panel (usually `192.168.1.1` or `10.0.0.1`) → DHCP / LAN settings → Address Reservation / Static Lease
- **You need:** The NucBox's MAC address — get it with `ip link show` on the server (look for the `ether` line on the main interface, usually `enp*` or `eth0`)
- **Why this first:** No server-side changes, survives Ubuntu reinstalls, works even if Netplan config breaks
- **Limitation:** Tied to this specific router. If you change routers, redo the reservation.

#### Approach 2: Server-side static IP via Netplan (Ubuntu 24.04)
- **What:** Configure the server itself to always use `10.0.0.22`, regardless of what the router offers
- **How:** Ubuntu 24.04 uses Netplan for network configuration
- **Config file:** `/etc/netplan/01-netcfg.yaml` or similar (check with `ls /etc/netplan/`)
- **What to set:**
  - Static IP: `10.0.0.22/24`
  - Gateway: your router's IP (e.g., `10.0.0.1`)
  - DNS: router IP or public DNS (`8.8.8.8`, `1.1.1.1`)
- **Apply:** `sudo netplan apply` (instant, no reboot needed)
- **Why this too:** Even if the router doesn't support DHCP reservations, or someone resets the router, the server keeps its IP
- **Risk:** If you change your network subnet or router IP, the server loses connectivity. Need physical access (monitor + keyboard) to fix.
- **Mitigation:** Tailscale provides a *separate* stable IP (100.x.x.x) that works regardless of local network changes — so even if the local static IP breaks, you can still reach the server via Tailscale

#### Approach 3: mDNS / Avahi (access by hostname)
- **What:** Access the server as `nucbox.local` instead of `10.0.0.22` — works even if the IP changes
- **How:** `sudo apt install avahi-daemon` (may already be installed)
- **Then:** `ssh yali@nucbox.local`, `http://nucbox.local:5678` for n8n
- **Why:** Hostname stays the same regardless of IP changes
- **Limitation:** Only works on the local network, doesn't help with remote access (Tailscale handles that)
- **Good for:** All your local bookmarks and SSH aliases survive IP changes

#### What to reference where
| Context | Use this address | Why |
|---------|-----------------|-----|
| SSH from home | `nucbox.local` or `10.0.0.22` | Local network, fast |
| SSH from anywhere | Tailscale IP (`100.x.x.x`) | Works through any network |
| n8n UI from home | `http://nucbox.local:5678` | Hostname survives IP changes |
| n8n UI remote | `http://100.x.x.x:5678` | Via Tailscale |
| Scripts/configs on server | `localhost` or `127.0.0.1` | Never reference external IP from the server itself |
| health-check.sh, skill-runner.py | No IP needed | Everything is local |

#### Recommended combo
1. **Router DHCP reservation** — 2 minutes, prevents the problem at the source
2. **Netplan static IP** — 5 minutes, server-side guarantee
3. **Avahi/mDNS** — 1 minute, `nucbox.local` is easier to remember than an IP
4. **Tailscale** — already in Phase 10A, gives a permanent remote IP that never changes

All four together = IP never drifts, and even if local networking breaks completely, Tailscale still works.

### DNS (Priority: LOW)
- If using Cloudflare Tunnel: point a subdomain to the tunnel
- If using Tailscale: MagicDNS gives you `nucbox.tail12345.ts.net` automatically

---

## Recommended Implementation Order

| Priority | Item | Time | Depends On |
|----------|------|------|------------|
| 1 | **Static IP** (router DHCP reservation + Netplan + Avahi) | 10 min | Router admin access |
| 2 | **Tailscale** | 10 min | Nothing |
| 3 | **UFW firewall** | 5 min | Nothing |
| 4 | **fail2ban** | 5 min | Nothing |
| 5 | **Unattended upgrades** | 5 min | Nothing |
| 6 | **Portainer** | 5 min | Docker |
| 7 | **Docker restart policies** (verify all containers) | 5 min | Docker |
| 8 | **Healthchecks.io** (external monitoring) | 15 min | Account signup |
| 9 | **Backup script + Backblaze B2** | 30 min | Restic install, B2 account |
| 10 | **Backup cron schedule** | 5 min | Backup script |
| 11 | **Watchtower** (monitor-only mode first) | 5 min | Docker |
| 12 | **Uptime Kuma** | 10 min | Docker |
| 13 | **Netdata** or **Glances** | 10 min | Nothing |
| 14 | **Dozzle** (Docker log viewer) | 5 min | Docker |
| 15 | **Push notifications** (ntfy or Pushover) | 15 min | Nothing |
| 16 | **UPS** | Physical purchase + 10 min setup | Hardware |
| 17 | **SOPS/age** (secrets encryption) | 30 min | When comfortable |

**Total estimated setup time:** ~2-3 hours for items 1-13 (the essentials)

---

## What This Gives You When Done

```
┌─────────────────────────────────────────────────────────┐
│                   YOUR PHONE / LAPTOP                    │
│                                                          │
│  Tailscale VPN ──→ Access from anywhere                 │
│  Slack ──────────→ Skill results + alerts               │
│  Pushover/ntfy ──→ Critical alerts (push notification)  │
│  Healthchecks.io → "Is the server alive?" dashboard     │
└─────────────────────┬───────────────────────────────────┘
                      │ Tailscale tunnel
┌─────────────────────▼───────────────────────────────────┐
│              NUCBOX M8 (10.0.0.22 / 100.x.x.x)         │
│                                                          │
│  ┌─────────┐ ┌───────────┐ ┌──────────┐ ┌───────────┐  │
│  │  n8n    │ │ Portainer │ │  Uptime  │ │  Netdata  │  │
│  │  :5678  │ │   :9000   │ │  Kuma    │ │  :19999   │  │
│  │scheduler│ │ Docker UI │ │  :3001   │ │  metrics  │  │
│  └────┬────┘ └───────────┘ └──────────┘ └───────────┘  │
│       │                                                  │
│  ┌────▼──────────────────────────────┐  ┌────────────┐  │
│  │ skill-runner.py → claude -p       │  │ Watchtower │  │
│  │ 14 scheduled skills               │  │ auto-update│  │
│  │ JSON logs → /var/log/claude/      │  └────────────┘  │
│  └───────────────────────────────────┘                   │
│                                                          │
│  Security: UFW + fail2ban + unattended-upgrades          │
│  Backup: restic → Backblaze B2 (daily, encrypted)       │
│  UPS: 30-60 min battery backup                           │
└─────────────────────────────────────────────────────────┘
```

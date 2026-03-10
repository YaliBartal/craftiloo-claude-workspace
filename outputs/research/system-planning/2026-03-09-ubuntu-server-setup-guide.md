# Ubuntu Server + Docker + n8n + Claude Code CLI: Complete Beginner Guide

> Researched 2026-03-09 from official docs, DigitalOcean, Reddit r/selfhosted, r/homelab, and community guides.

---

## Table of Contents

1. [Ubuntu Server 24.04 LTS Installation](#1-ubuntu-server-2404-lts-installation)
2. [First-Time Server Setup](#2-first-time-server-setup)
3. [Static IP Configuration (Netplan)](#3-static-ip-configuration-netplan)
4. [Docker Engine Installation](#4-docker-engine-installation)
5. [Docker Compose](#5-docker-compose)
6. [n8n Docker Compose with PostgreSQL](#6-n8n-docker-compose-with-postgresql)
7. [Node.js 20 LTS Installation](#7-nodejs-20-lts-installation)
8. [Claude Code CLI Installation](#8-claude-code-cli-installation)
9. [Cron Job Setup](#9-cron-job-setup)
10. [Tailscale Installation](#10-tailscale-installation)
11. [Portainer Installation](#11-portainer-installation)
12. [SSH from Windows 11](#12-ssh-from-windows-11)
13. [UPS Recommendation + NUT Setup](#13-ups-recommendation--nut-setup)
14. [Backup Strategy](#14-backup-strategy)
15. [Common Beginner Mistakes](#15-common-beginner-mistakes)

---

## 1. Ubuntu Server 24.04 LTS Installation

### Download & Boot Media

1. Download ISO from https://ubuntu.com/download/server
2. On Windows, use **Rufus** (https://rufus.ie) to flash the ISO to a USB drive
3. Insert USB into mini PC, enter BIOS (usually F2, F12, DEL, or ESC during boot)
4. Set USB as first boot device, save and restart

### Installation Screen-by-Screen

| Screen | What to choose | Notes |
|--------|---------------|-------|
| **Language** | English | Or your preference |
| **Keyboard** | Auto-detected or pick yours | Default is fine for US |
| **Installation type** | "Ubuntu Server" (NOT minimized) | Minimized strips out tools you'll need. Full server base is better for beginners. The other options (MAAS) are for data centers -- ignore them |
| **Network** | Leave as DHCP for now | We'll set static IP after install. Installer auto-detects via DHCP |
| **Proxy** | Leave blank | Unless you're behind a corporate proxy |
| **Mirror** | Accept the suggested mirror | It auto-selects the closest one |
| **Storage** | "Use an entire disk" | **Check "Set up this disk as an LVM group"** -- see below |
| **Storage confirmation** | Review and confirm | The installer shows the partition layout before writing |
| **Profile** | Enter your name, server hostname, username, password | This user gets sudo automatically |
| **SSH** | **CHECK "Install OpenSSH server"** | This is essential for remote access. You can also import keys from GitHub here |
| **Featured snaps** | Skip all | Install Docker properly later, not via snap |
| **Wait for install** | Let it finish, then "Reboot Now" | Remove USB when prompted |

### Should You Use LVM?

**Yes, check the LVM box.** Here's why:

- LVM lets you **resize partitions later** without reinstalling
- The Ubuntu installer with LVM only uses ~50% of your disk by default (you can extend later)
- Without LVM, if you need more space for `/var` (where Docker stores data), you're stuck
- Extending an LVM volume later: `sudo lvextend -l +100%FREE /dev/ubuntu-vg/ubuntu-lv && sudo resize2fs /dev/ubuntu-vg/ubuntu-lv`

**One gotcha:** The installer may only allocate half your disk to the root LV. After install, run this to use all available space:

```bash
sudo lvextend -l +100%FREE /dev/ubuntu-vg/ubuntu-lv
sudo resize2fs /dev/ubuntu-vg/ubuntu-lv
```

### Should You Use Minimized?

**No.** The minimized image strips out `man` pages, `nano`, `less`, and other tools you'll want as a beginner. It's meant for automated cloud VMs, not hands-on servers.

---

## 2. First-Time Server Setup

Run these commands in order after your first login.

### Update everything

```bash
sudo apt update && sudo apt upgrade -y
```

### Set timezone

```bash
# See current timezone
timedatectl

# Set to your timezone (example: US Eastern)
sudo timedatectl set-timezone America/New_York

# Verify
timedatectl
```

Find your timezone string: `timedatectl list-timezones | grep America`

### Enable automatic security updates

Ubuntu 24.04 Server has `unattended-upgrades` installed by default. Verify:

```bash
sudo dpkg -l | grep unattended-upgrades
```

If not installed:

```bash
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

Optional: enable automatic reboot for kernel updates. Edit `/etc/apt/apt.conf.d/50unattended-upgrades`:

```
Unattended-Upgrade::Automatic-Reboot "true";
Unattended-Upgrade::Automatic-Reboot-Time "04:00";
```

Logs go to: `/var/log/unattended-upgrades/unattended-upgrades.log`

### Configure UFW Firewall

```bash
# Allow SSH FIRST (critical -- do this before enabling!)
sudo ufw allow OpenSSH

# Allow other services you'll use
sudo ufw allow 5678/tcp    # n8n
sudo ufw allow 9443/tcp    # Portainer

# Enable the firewall
sudo ufw enable

# Check status
sudo ufw status verbose
```

**CRITICAL:** Always allow SSH **before** enabling UFW. Otherwise you lock yourself out.

### Install useful tools

```bash
sudo apt install -y curl wget git htop nano net-tools
```

### Set a static hostname (if you didn't during install)

```bash
sudo hostnamectl set-hostname my-server
```

---

## 3. Static IP Configuration (Netplan)

### Find your current IP and interface name

```bash
# Shows interface names and current IPs
ip addr

# Shows your default gateway (router IP)
ip route | grep default
```

Typical output: `default via 192.168.1.1 dev enp1s0` -- here `enp1s0` is your interface and `192.168.1.1` is your gateway.

### Edit the netplan config

```bash
sudo nano /etc/netplan/50-cloud-init.yaml
```

Replace contents with (adjust values for your network):

```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    enp1s0:
      dhcp4: false
      dhcp6: false
      addresses:
        - 192.168.1.100/24
      routes:
        - to: default
          via: 192.168.1.1
      nameservers:
        addresses: [1.1.1.1, 8.8.8.8]
```

### Key values to customize

| Field | What to put | How to find it |
|-------|------------|----------------|
| `enp1s0` | Your interface name | `ip addr` -- look for the one with an IP |
| `192.168.1.100/24` | Your desired static IP + subnet | Pick an IP outside your router's DHCP range |
| `192.168.1.1` | Your router/gateway IP | `ip route \| grep default` |
| `1.1.1.1, 8.8.8.8` | DNS servers | Cloudflare + Google, or use your router's IP |

### Apply (safely)

```bash
# TEST first -- reverts after 120 seconds if you don't confirm
sudo netplan try

# If test works, apply permanently
sudo netplan apply

# Verify
ip addr show enp1s0
```

### Common Netplan YAML Mistakes

| Mistake | Fix |
|---------|-----|
| Using TABS instead of spaces | **Always use spaces** (2 or 4 per indent level) |
| Wrong indentation depth | Each nested level must be indented consistently |
| Using old `gateway4:` syntax | Use `routes: - to: default via: x.x.x.x` instead (gateway4 is deprecated) |
| Forgetting `/24` after IP | Always include CIDR notation: `192.168.1.100/24` |
| Typo in interface name | Copy-paste from `ip addr` output |

### Also: Reserve the IP in your router

Log into your router admin page and **reserve** the static IP you chose (usually under DHCP settings > Address Reservation). This prevents your router from assigning that IP to another device.

---

## 4. Docker Engine Installation

**Use the official apt repository method -- NOT Docker Desktop, NOT snap.**

### Step 1: Remove conflicting packages

```bash
# Remove old or conflicting Docker packages
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do
  sudo apt-get remove -y $pkg 2>/dev/null
done
```

### Step 2: Set up Docker's apt repository

```bash
# Install prerequisites
sudo apt-get update
sudo apt-get install -y ca-certificates curl

# Add Docker's official GPG key
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the Docker repository
sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Signed-By: /etc/apt/keyrings/docker.asc
EOF

sudo apt-get update
```

### Step 3: Install Docker Engine

```bash
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### Step 4: Post-install -- run Docker without sudo

```bash
# Create docker group (may already exist)
sudo groupadd docker 2>/dev/null

# Add your user to it
sudo usermod -aG docker $USER

# Activate the new group (or log out and back in)
newgrp docker
```

**Security note:** The docker group grants root-equivalent access. Only add trusted users.

### Step 5: Verify

```bash
docker run hello-world
```

### Step 6: Configure Docker log rotation (IMPORTANT)

Without this, Docker logs grow forever and fill your disk.

```bash
sudo nano /etc/docker/daemon.json
```

Add:

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "5"
  }
}
```

Restart Docker:

```bash
sudo systemctl restart docker
```

**Note:** This only applies to containers created AFTER the change. Existing containers keep their old logging settings.

### Common Mistakes

| Mistake | Fix |
|---------|-----|
| Installing Docker via `snap` | Snap Docker is outdated and has socket issues. Use apt repo method above |
| Using `sudo` with every Docker command | Add yourself to docker group (Step 4) |
| Forgetting log rotation | Logs fill disk silently. Configure `daemon.json` (Step 6) |
| Not starting Docker on boot | It's enabled by default with apt install, but verify: `sudo systemctl enable docker` |

---

## 5. Docker Compose

### Is it bundled?

**Yes.** When you installed `docker-compose-plugin` in Step 3 above, Docker Compose v2 was included. It's now a Docker CLI plugin, not a standalone binary.

### Verify

```bash
docker compose version
```

You should see something like: `Docker Compose version v2.x.x`

### Old vs New syntax

| Old (standalone) | New (plugin) |
|-----------------|--------------|
| `docker-compose up -d` | `docker compose up -d` |
| `docker-compose down` | `docker compose down` |
| `docker-compose logs` | `docker compose logs` |

**Use the new syntax** (no hyphen). The old `docker-compose` standalone binary is deprecated.

---

## 6. n8n Docker Compose with PostgreSQL

### Why PostgreSQL over SQLite?

- SQLite is fine for testing, but **corrupts under concurrent writes**
- PostgreSQL handles multiple workflows running simultaneously
- PostgreSQL is what n8n recommends for production

### Create the project directory

```bash
mkdir -p ~/n8n-docker && cd ~/n8n-docker
```

### Create `.env` file

```bash
nano .env
```

```env
# ---------- Postgres ----------
POSTGRES_USER=n8n
POSTGRES_PASSWORD=CHANGE_ME_TO_SOMETHING_STRONG
POSTGRES_DB=n8n

# ---------- n8n Database Connection ----------
DB_TYPE=postgresdb
DB_POSTGRESDB_HOST=postgres
DB_POSTGRESDB_PORT=5432
DB_POSTGRESDB_DATABASE=n8n
DB_POSTGRESDB_USER=n8n
DB_POSTGRESDB_PASSWORD=CHANGE_ME_TO_SOMETHING_STRONG
DB_POSTGRESDB_SCHEMA=public

# ---------- n8n Instance ----------
N8N_HOST=0.0.0.0
N8N_PORT=5678
N8N_PROTOCOL=http
WEBHOOK_URL=http://YOUR_SERVER_IP:5678

# ---------- Security ----------
N8N_ENCRYPTION_KEY=GENERATE_A_RANDOM_64_CHAR_STRING
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=CHANGE_ME_STRONG_PASSWORD

# ---------- Timezone ----------
GENERIC_TIMEZONE=America/New_York
TZ=America/New_York

# ---------- Telemetry ----------
N8N_DIAGNOSTICS_ENABLED=false
```

**Generate a random encryption key:**

```bash
openssl rand -hex 32
```

### Create `docker-compose.yml`

```bash
nano docker-compose.yml
```

```yaml
version: "3.8"

services:
  postgres:
    image: postgres:16-alpine
    container_name: n8n-postgres
    restart: unless-stopped
    env_file:
      - .env
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 10

  n8n:
    image: n8nio/n8n:latest
    container_name: n8n-app
    restart: unless-stopped
    env_file:
      - .env
    environment:
      - DB_TYPE=${DB_TYPE}
      - DB_POSTGRESDB_HOST=${DB_POSTGRESDB_HOST}
      - DB_POSTGRESDB_PORT=${DB_POSTGRESDB_PORT}
      - DB_POSTGRESDB_DATABASE=${DB_POSTGRESDB_DATABASE}
      - DB_POSTGRESDB_USER=${DB_POSTGRESDB_USER}
      - DB_POSTGRESDB_PASSWORD=${DB_POSTGRESDB_PASSWORD}
      - DB_POSTGRESDB_SCHEMA=${DB_POSTGRESDB_SCHEMA}
      - N8N_HOST=${N8N_HOST}
      - N8N_PORT=${N8N_PORT}
      - N8N_PROTOCOL=${N8N_PROTOCOL}
      - WEBHOOK_URL=${WEBHOOK_URL}
      - GENERIC_TIMEZONE=${GENERIC_TIMEZONE}
      - TZ=${TZ}
      - N8N_DIAGNOSTICS_ENABLED=${N8N_DIAGNOSTICS_ENABLED}
      - N8N_ENCRYPTION_KEY=${N8N_ENCRYPTION_KEY}
      - N8N_BASIC_AUTH_ACTIVE=${N8N_BASIC_AUTH_ACTIVE}
      - N8N_BASIC_AUTH_USER=${N8N_BASIC_AUTH_USER}
      - N8N_BASIC_AUTH_PASSWORD=${N8N_BASIC_AUTH_PASSWORD}
    ports:
      - "5678:5678"
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - n8n_data:/home/node/.n8n
    healthcheck:
      test: ["CMD-SHELL", "wget -qO- http://localhost:5678/healthz || exit 1"]
      interval: 15s
      timeout: 5s
      retries: 20

volumes:
  n8n_data:
  postgres_data:
```

### Start it up

```bash
docker compose up -d
```

### Access n8n

Open browser: `http://YOUR_SERVER_IP:5678`

### Critical notes

| Topic | Detail |
|-------|--------|
| **Encryption key** | Set `N8N_ENCRYPTION_KEY` BEFORE first run. Changing it later makes stored credentials unrecoverable |
| **DB_TYPE value** | Must be `postgresdb` (not `postgres` -- that causes connection failures) |
| **Volume backup** | Back up both `n8n_data` and `postgres_data` volumes. The n8n_data volume contains the encryption key |
| **Updates** | `docker compose pull && docker compose up -d` to update. Always back up first |
| **Reverse proxy** | For production/internet access, put Nginx or Caddy in front with HTTPS. Don't expose port 5678 directly to the internet |

---

## 7. Node.js 20 LTS Installation

### Which method?

| Method | Version available | Recommended? |
|--------|------------------|-------------|
| `apt install nodejs` (default Ubuntu repo) | Node 18.x | No -- too old, EOL April 2025 |
| **NodeSource repository** | Node 20.x LTS (exact version) | **Yes** |
| NVM (Node Version Manager) | Any version | Good for development, overkill for servers |

### Install via NodeSource (recommended)

```bash
# Add NodeSource repository for Node.js 20
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -

# Install Node.js (includes npm)
sudo apt-get install -y nodejs

# Verify
node --version   # Should show v20.x.x
npm --version    # Should show 10.x.x
```

### Set up npm for global installs without sudo

```bash
mkdir -p ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

This is important for Claude Code CLI installation next.

---

## 8. Claude Code CLI Installation

### Install

```bash
# Make sure npm global dir is set up (see Node.js section above)
npm install -g @anthropic-ai/claude-code
```

**Do NOT use `sudo npm install -g`** -- this causes permission issues and security risks.

### Set up API key

For headless/server use, set the API key as an environment variable (skips browser OAuth):

```bash
# Add to .bashrc for persistence
echo 'export ANTHROPIC_API_KEY="sk-ant-your-key-here"' >> ~/.bashrc
source ~/.bashrc
```

Claude Code detects `ANTHROPIC_API_KEY` automatically and skips the browser OAuth flow.

### Run headless with `-p` flag

The `-p` (or `--print`) flag runs Claude Code non-interactively -- it processes the request and exits:

```bash
# Simple question
claude -p "What does the auth module do?"

# With tool permissions
claude -p "Run the test suite and fix any failures" \
  --allowedTools "Bash,Read,Edit"

# JSON output (for scripts/automation)
claude -p "Summarize this project" --output-format json

# Streaming JSON
claude -p "Explain this code" --output-format stream-json
```

### Allow tools for unattended use

Use `--allowedTools` to pre-approve tools without prompting:

```bash
# Allow reading, editing, and specific bash commands
claude -p "Review and fix bugs" \
  --allowedTools "Read,Edit,Grep,Glob,Bash(git diff *),Bash(git log *),Bash(git status *),Bash(git commit *)"
```

**Permission syntax:**
- `Bash` -- allows ALL bash commands (dangerous for unattended)
- `Bash(git diff *)` -- only allows commands starting with `git diff` (the space before `*` matters)
- `Read,Edit` -- allows file read and edit
- `Write` -- allows creating new files

### Continue conversations

```bash
# First run
claude -p "Start reviewing this codebase"

# Continue where you left off
claude -p "Now focus on database queries" --continue

# Or capture session ID for specific resumption
session_id=$(claude -p "Start review" --output-format json | jq -r '.session_id')
claude -p "Continue" --resume "$session_id"
```

### Custom system prompt

```bash
claude -p "Review this code" \
  --append-system-prompt "You are a security engineer. Focus on vulnerabilities."
```

### Example: Cron job with Claude Code

```bash
# In crontab, a daily code review at 6 AM
0 6 * * * cd /home/user/my-project && /home/user/.npm-global/bin/claude -p "Run daily health check on this project" --allowedTools "Read,Grep,Glob" --output-format json >> /var/log/claude-daily.log 2>&1
```

---

## 9. Cron Job Setup

### Edit your crontab

```bash
crontab -e
```

First time: it asks which editor. Choose `nano` (option 1) for beginners.

### Cron syntax

```
 *  *  *  *  *   command
 |  |  |  |  |
 |  |  |  |  +-- Day of week (0-7, Sun=0 or 7)
 |  |  |  +----- Month (1-12)
 |  |  +-------- Day of month (1-31)
 |  +----------- Hour (0-23)
 +-------------- Minute (0-59)
```

### Common patterns

| Schedule | Cron expression |
|----------|----------------|
| Every day at 6 AM | `0 6 * * *` |
| Every hour | `0 * * * *` |
| Every 15 minutes | `*/15 * * * *` |
| Monday at 9 AM | `0 9 * * 1` |
| First of month at midnight | `0 0 1 * *` |
| Weekdays at 8:30 AM | `30 8 * * 1-5` |

### Always log output

```bash
# Redirect both stdout and stderr to a log file
0 6 * * * /path/to/command >> /var/log/my-job.log 2>&1
```

Without this, cron tries to email output (which probably isn't configured).

### Use full paths

Cron doesn't load your `.bashrc` or PATH. Always use absolute paths:

```bash
# BAD
0 6 * * * claude -p "check"

# GOOD
0 6 * * * /home/user/.npm-global/bin/claude -p "check"
```

Or set PATH at the top of your crontab:

```bash
PATH=/home/user/.npm-global/bin:/usr/local/bin:/usr/bin:/bin
ANTHROPIC_API_KEY=sk-ant-your-key-here

0 6 * * * cd /home/user/project && claude -p "daily check" --allowedTools "Read,Grep" >> /var/log/claude.log 2>&1
```

### Common timezone mistakes

| Mistake | Fix |
|---------|-----|
| Assuming cron uses your local time | Cron uses the **system timezone**. Check with `timedatectl` |
| Not restarting cron after timezone change | `sudo systemctl restart cron` after changing timezone |
| DST confusion | Cron has no DST support. Jobs near 2 AM can skip or double-fire during DST transitions. Avoid scheduling at 2 AM |
| Forgetting to set env vars | Cron runs in a minimal environment. Set PATH and API keys in crontab |

### Verify your cron jobs are running

```bash
# List your cron jobs
crontab -l

# Check cron logs
grep CRON /var/log/syslog | tail -20
```

---

## 10. Tailscale Installation

Tailscale creates a private network (VPN mesh) between your devices. Access your server from anywhere without exposing ports to the internet.

### One-liner install

```bash
curl -fsSL https://tailscale.com/install.sh | sh
```

Or the manual method:

```bash
# Add Tailscale repository
curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/noble.noarmor.gpg | sudo tee /usr/share/keyrings/tailscale-archive-keyring.gpg >/dev/null
curl -fsSL https://pkgs.tailscale.com/stable/ubuntu/noble.tailscale-keyring.list | sudo tee /etc/apt/sources.list.d/tailscale.list

# Install
sudo apt-get update && sudo apt-get install -y tailscale
```

### Connect to your network

```bash
sudo tailscale up
```

This prints a URL. Open it in a browser to authenticate with your Tailscale account (free for personal use, up to 100 devices).

### Verify

```bash
# Your Tailscale IP
tailscale ip -4

# All connected devices
tailscale status
```

### Disable key expiry (important for servers)

By default, Tailscale keys expire after 180 days. For a server, disable this:

1. Go to https://login.tailscale.com/admin/machines
2. Click the three dots next to your server
3. Select "Disable key expiry"

### Connect from Windows 11

1. Install Tailscale on your Windows PC: https://tailscale.com/download/windows
2. Sign in with the same account
3. SSH using the Tailscale IP: `ssh user@100.x.x.x`

### Useful: Access n8n and Portainer via Tailscale

With Tailscale, you don't need to expose ports 5678 or 9443 to your home network. Access them via Tailscale IP only:

- n8n: `http://100.x.x.x:5678`
- Portainer: `https://100.x.x.x:9443`

---

## 11. Portainer Installation

Portainer gives you a web UI to manage Docker containers, images, volumes, and networks.

### Create volume and run

```bash
# Create persistent volume
docker volume create portainer_data

# Run Portainer CE
docker run -d \
  -p 8000:8000 \
  -p 9443:9443 \
  --name portainer \
  --restart=always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data \
  portainer/portainer-ce:lts
```

### Access the web UI

Open browser: `https://YOUR_SERVER_IP:9443`

- Uses a self-signed SSL certificate (browser will warn -- click "Advanced" > "Accept")
- First visit: create an admin password (must be 12+ characters)
- Select "Local" environment > "Connect"

### What you can do in Portainer

- View all running containers, their logs, and resource usage
- Start/stop/restart containers
- View Docker volumes and networks
- Deploy new containers or stacks (docker-compose) from the UI
- Check container health and auto-restart status

---

## 12. SSH from Windows 11

Windows 11 has a built-in OpenSSH client. No need to install PuTTY.

### Basic connection

Open **Windows Terminal** (or PowerShell) and type:

```powershell
ssh username@192.168.1.100
```

Replace `username` with your Ubuntu username and the IP with your server's IP (or Tailscale IP).

### Set up SSH key authentication (recommended)

**On your Windows 11 PC:**

```powershell
# Generate a key pair (Ed25519 is most secure)
ssh-keygen -t ed25519

# Press Enter for default file location (~/.ssh/id_ed25519)
# Set a passphrase or leave empty
```

**Copy the public key to your server:**

```powershell
# From Windows PowerShell
type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh username@192.168.1.100 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

**Set permissions on the server:**

```bash
# SSH into the server, then:
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

### Disable password authentication (security hardening)

After confirming key-based login works:

```bash
sudo nano /etc/ssh/sshd_config
```

Change these lines:

```
PasswordAuthentication no
PubkeyAuthentication yes
PermitRootLogin no
```

Restart SSH:

```bash
sudo systemctl restart ssh
```

### SSH config file for convenience

On your Windows PC, create/edit `C:\Users\YourName\.ssh\config`:

```
Host myserver
    HostName 192.168.1.100
    User username
    IdentityFile ~/.ssh/id_ed25519

Host myserver-ts
    HostName 100.x.x.x
    User username
    IdentityFile ~/.ssh/id_ed25519
```

Now just type: `ssh myserver` or `ssh myserver-ts`

---

## 13. UPS Recommendation + NUT Setup

### Recommended Budget UPS Models

| Model | Capacity | Price range | Best for |
|-------|----------|-------------|----------|
| **APC Back-UPS BE600M1** | 600VA / 330W | ~$55-70 | Single mini PC + router |
| **CyberPower EC650LCD** | 650VA / 390W | ~$60-75 | Single mini PC + router |
| **APC Back-UPS BX1000M** | 1000VA / 600W | ~$100-120 | Mini PC + NAS + router |
| **CyberPower CP1500PFCLCD** | 1500VA / 1000W | ~$180-220 | Multiple devices, pure sine wave |

**For a single mini PC (draws 20-50W):** The APC BE600M1 or CyberPower EC650LCD gives you 15-30 minutes of runtime -- enough for a graceful shutdown.

**Must-have feature:** USB port for NUT communication. All models above have USB.

### Install NUT (Network UPS Tools)

```bash
sudo apt update
sudo apt install -y nut nut-client nut-server
```

### Detect your UPS

Plug in the UPS via USB, then:

```bash
# Find the USB device
lsusb

# Scan for NUT-compatible devices
sudo nut-scanner -U
```

Note the `vendorid` and `productid` from the output.

### Configure NUT

**1. `/etc/nut/nut.conf`** -- Set mode:

```
MODE=standalone
```

(Use `standalone` for single server. Use `netserver` if other machines need to monitor this UPS too.)

**2. `/etc/nut/ups.conf`** -- Define the UPS:

```
pollinterval = 5
maxretry = 3

[myups]
    driver = usbhid-ups
    port = auto
    desc = "APC Back-UPS"
```

**3. `/etc/nut/upsd.users`** -- Create a monitor user:

```
[upsmon]
    password = YourSecurePassword
    upsmon master
```

**4. `/etc/nut/upsmon.conf`** -- Set up monitoring:

```
MONITOR myups@localhost 1 upsmon YourSecurePassword master
SHUTDOWNCMD "/sbin/shutdown -h +0"
MINSUPPLIES 1
POLLFREQ 5
POLLFREQALERT 5
HOSTSYNC 15
DEADTIME 15
FINALDELAY 5
```

### Start and enable services

```bash
sudo systemctl enable nut-server
sudo systemctl enable nut-monitor
sudo systemctl start nut-server
sudo systemctl start nut-monitor
```

### Verify UPS communication

```bash
# Check UPS status
upsc myups@localhost

# Key values to look for:
# battery.charge: 100
# ups.status: OL (Online = on mains power)
# ups.status: OB (On Battery = power outage)
```

### What happens during a power outage

1. Power goes out -> UPS switches to battery -> NUT detects `OB` (on battery)
2. Battery gets low -> UPS reports `LB` (low battery)
3. NUT sees `OB LB` -> triggers `SHUTDOWNCMD`
4. Server shuts down gracefully
5. Power comes back -> server boots (set "restore on AC power loss" in BIOS)

---

## 14. Backup Strategy

### What needs backing up

| What | Location | Priority |
|------|----------|----------|
| **n8n workflows + credentials** | `n8n_data` Docker volume | Critical |
| **n8n database** | `postgres_data` Docker volume | Critical |
| **Docker compose files + .env** | `~/n8n-docker/` | Critical |
| **Claude Code workspace** | Your project directory | High |
| **System configuration** | `/etc/` (netplan, NUT, ssh, UFW) | High |
| **Crontab** | `crontab -l` output | Medium |
| **Home directory** | `/home/username/` | Medium |

### Method 1: Cron + rsync to external drive

```bash
# Mount external USB drive (find it first with lsblk)
sudo mkdir -p /mnt/backup
sudo mount /dev/sdb1 /mnt/backup

# Add to /etc/fstab for auto-mount on boot:
# UUID=your-drive-uuid /mnt/backup ext4 defaults,nofail 0 2
```

Create a backup script at `~/backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/mnt/backup/$(hostname)/$(date +%Y-%m-%d)"
mkdir -p "$BACKUP_DIR"

# Docker volumes
docker run --rm -v n8n-docker_n8n_data:/data -v "$BACKUP_DIR":/backup alpine \
  tar czf /backup/n8n-data.tar.gz -C /data .

docker run --rm -v n8n-docker_postgres_data:/data -v "$BACKUP_DIR":/backup alpine \
  tar czf /backup/postgres-data.tar.gz -C /data .

# PostgreSQL proper dump (more reliable than volume tar)
docker exec n8n-postgres pg_dump -U n8n n8n | gzip > "$BACKUP_DIR/n8n-db-dump.sql.gz"

# Config files
rsync -a ~/n8n-docker/ "$BACKUP_DIR/n8n-config/"
rsync -a /etc/netplan/ "$BACKUP_DIR/etc-netplan/"
rsync -a /etc/nut/ "$BACKUP_DIR/etc-nut/"
crontab -l > "$BACKUP_DIR/crontab.txt"

# Trim backups older than 30 days
find /mnt/backup/$(hostname)/ -maxdepth 1 -type d -mtime +30 -exec rm -rf {} \;

echo "Backup completed: $BACKUP_DIR"
```

```bash
chmod +x ~/backup.sh
```

Add to crontab (daily at 3 AM):

```bash
0 3 * * * /home/username/backup.sh >> /var/log/backup.log 2>&1
```

### Method 2: Timeshift for system snapshots

```bash
sudo apt install timeshift
```

Timeshift backs up system files (OS, configs, installed packages) -- NOT personal data or Docker volumes. Use it alongside rsync, not instead of it.

```bash
# Create a snapshot
sudo timeshift --create --comments "Before big change"

# List snapshots
sudo timeshift --list

# Restore (emergency)
sudo timeshift --restore
```

### Method 3: Offsite backup with rclone (optional)

```bash
sudo apt install rclone
rclone config  # Set up a remote (Google Drive, Backblaze B2, etc.)

# Sync backups offsite
rclone sync /mnt/backup remote:server-backups
```

### 3-2-1 Rule

- **3** copies of your data
- **2** different storage types (local disk + external drive, or local + cloud)
- **1** offsite copy

---

## 15. Common Beginner Mistakes

### Security Mistakes

| Mistake | Impact | Fix |
|---------|--------|-----|
| **Leaving SSH password auth enabled** | Brute force attacks (they start within hours) | Use key-only auth, disable passwords in sshd_config |
| **Not enabling UFW** | All ports exposed to network | `sudo ufw enable` after allowing SSH |
| **Forgetting to disable root SSH login** | Root is the #1 target | `PermitRootLogin no` in sshd_config |
| **Exposing services to the internet without HTTPS** | Credentials sent in plain text | Use reverse proxy + Let's Encrypt, or Tailscale |
| **Running everything as root** | One exploit = total compromise | Use your regular user + sudo |
| **Not installing fail2ban** | Hundreds of brute force attempts/day | `sudo apt install fail2ban` (works out of the box) |

### Maintenance Mistakes

| Mistake | Impact | Fix |
|---------|--------|-----|
| **Skipping unattended-upgrades** | Known vulnerabilities remain unpatched | Enabled by default on Ubuntu Server, but verify |
| **No Docker log rotation** | Disk fills up silently, services crash | Configure `daemon.json` (see Docker section) |
| **No system monitoring** | You don't know when things break | Install Uptime Kuma (Docker container) or at minimum check `htop` and `df -h` regularly |
| **Not checking disk space** | Full disk = corrupted databases, failed containers | Set up a cron alert: `df -h / \| awk 'NR==2{if($5+0>80) print "DISK WARNING: " $5 " used"}'` |
| **Not backing up** | Hardware dies, you lose everything | Follow backup strategy above |
| **Forgetting to set timezone** | Cron jobs run at wrong time, logs confusing | `timedatectl set-timezone your/timezone` |

### Docker-Specific Mistakes

| Mistake | Impact | Fix |
|---------|--------|-----|
| **Using `:latest` tag without pinning** | Unexpected breaking changes on `docker compose pull` | Use specific versions for databases: `postgres:16-alpine` |
| **Not using `restart: unless-stopped`** | Containers don't come back after reboot | Add to every production container |
| **Storing secrets in docker-compose.yml** | Secrets in version control | Use `.env` files + `.gitignore` |
| **Not backing up Docker volumes** | Losing all application data | Regular volume backups (see backup section) |

### Network Mistakes

| Mistake | Impact | Fix |
|---------|--------|-----|
| **Not reserving the static IP in your router** | Another device gets assigned your IP | Add DHCP reservation in router settings |
| **Opening too many ports in UFW** | Larger attack surface | Only open what you need. Use Tailscale for remote access |
| **Forgetting to allow SSH before enabling UFW** | Locked out of your own server | Always `ufw allow OpenSSH` FIRST |

### Mindset Mistakes (from r/selfhosted and r/homelab)

1. **Starting too big.** Get ONE thing working perfectly before adding the next. Don't try to set up 10 services on day one.
2. **Not documenting what you did.** You'll forget how you set things up. Keep a text file of every command you ran.
3. **Self-hosting email.** Don't. The deliverability requirements (DKIM, SPF, DMARC, IP reputation) are a nightmare. Use a paid email service.
4. **Comparing your setup to others.** Reddit homelabs with 42U racks are not the goal. A mini PC running 3 containers is a perfectly valid setup.
5. **Not having a recovery plan.** Know how to reinstall from scratch. Test your backups. Have your docker-compose files and .env backed up somewhere you can access without the server.

---

## Quick Reference: Order of Operations

After Ubuntu Server install, do everything in this order:

```
1.  sudo apt update && sudo apt upgrade -y
2.  Set timezone
3.  Verify unattended-upgrades is active
4.  Set static IP (netplan)
5.  Harden SSH (keys, disable passwords, disable root)
6.  Enable UFW (allow SSH first!)
7.  Install fail2ban
8.  Install Docker Engine (apt method)
9.  Configure Docker log rotation
10. Add user to docker group
11. Install Portainer
12. Set up n8n + PostgreSQL (docker compose)
13. Install Node.js 20 (NodeSource)
14. Install Claude Code CLI
15. Install Tailscale
16. Set up NUT for UPS
17. Create backup script + cron job
18. Set up cron jobs for Claude Code automation
19. Extend LVM to use full disk (if needed)
20. Reboot and verify everything comes back up
```

---

## Sources

### Ubuntu Server Installation
- [Official Ubuntu Server Install Tutorial](https://ubuntu.com/tutorials/install-ubuntu-server)
- [LinuxTechi: How to Install Ubuntu Server 24.04](https://www.linuxtechi.com/how-to-install-ubuntu-server/)
- [OneUpTime: Install Ubuntu Server 24.04 Step by Step](https://oneuptime.com/blog/post/2026-03-02-install-ubuntu-server-24-04-lts-step-by-step/view)

### Security & Hardening
- [Frank's Blog: Hardening Ubuntu Server 24.04](https://frankschmidt-bruecken.com/en/blog/ubuntu-server-hardening/)
- [DigitalOcean: UFW Firewall Setup](https://www.digitalocean.com/community/tutorials/how-to-set-up-a-firewall-with-ufw-on-ubuntu)
- [MassiveGRID: Ubuntu VPS Security Hardening](https://massivegrid.com/blog/ubuntu-vps-security-hardening-guide/)
- [DigitalOcean: Security Best Practices](https://www.digitalocean.com/security/security-best-practices-guide-droplet)

### Static IP / Netplan
- [Mendhak: Static IP on Ubuntu 24.04 with Netplan](https://code.mendhak.com/ubuntu-2404-set-static-ip-address-using-netplan/)
- [LinuxConfig: Static IP via Command Line](https://linuxconfig.org/setting-a-static-ip-address-in-ubuntu-24-04-via-the-command-line)
- [OneUpTime: Netplan YAML Configuration](https://oneuptime.com/blog/post/2026-03-02-netplan-yaml-static-ip-configuration-ubuntu/view)

### Docker
- [Official Docker Install on Ubuntu](https://docs.docker.com/engine/install/ubuntu/)
- [Docker Post-Install Steps](https://docs.docker.com/engine/install/linux-postinstall/)
- [Docker Log Rotation (daemon.json)](https://docs.docker.com/engine/logging/drivers/json-file/)
- [SigNoz: Docker Log Rotation Guide](https://signoz.io/blog/docker-log-rotation/)

### n8n
- [Official n8n Docker Docs](https://docs.n8n.io/hosting/installation/docker/)
- [n8n-hosting GitHub (PostgreSQL compose)](https://github.com/n8n-io/n8n-hosting/blob/main/docker-compose/withPostgres/README.md)
- [n8nlogic: Docker + Postgres Setup](https://n8nlogic.com/blog/n8n-docker-postgres-setup)
- [DigitalOcean: n8n Setup Guide](https://www.digitalocean.com/community/tutorials/how-to-setup-n8n)

### Node.js
- [Linuxize: Install Node.js on Ubuntu 24.04](https://linuxize.com/post/how-to-install-node-js-on-ubuntu-24-04/)
- [NodeSource Setup Script](https://deb.nodesource.com/setup_20.x)

### Claude Code CLI
- [Official Claude Code Headless Docs](https://code.claude.com/docs/en/headless)
- [Claude Code npm Package](https://www.npmjs.com/package/@anthropic-ai/claude-code)
- [Claude Code API Key Management](https://support.claude.com/en/articles/12304248-managing-api-key-environment-variables-in-claude-code)
- [SSD Nodes: Install Claude Code on Ubuntu](https://www.ssdnodes.com/blog/install-claude-code-on-ubuntu-linux/)

### Cron
- [Contabo: Crontab Syntax Guide 2026](https://contabo.com/blog/contrab-syntax-on-linux-guide-for-2026/)
- [Cronitor: Complete Cron Jobs Guide 2026](https://cronitor.io/guides/cron-jobs)
- [DEV: Handling Timezone Issues in Cron Jobs](https://dev.to/cronmonitor/handling-timezone-issues-in-cron-jobs-2025-guide-52ii)

### Tailscale
- [Official Tailscale Linux Install](https://tailscale.com/docs/install/linux)
- [Tailscale Quickstart](https://tailscale.com/kb/1017/install)
- [Tailscale Server Setup](https://tailscale.com/docs/how-to/set-up-servers)

### Portainer
- [Official Portainer CE Install (Docker Linux)](https://docs.portainer.io/start/install-ce/server/docker/linux)
- [HowToGeek: Getting Started with Portainer](https://www.howtogeek.com/devops/how-to-get-started-with-portainer-a-web-ui-for-docker/)

### SSH
- [Microsoft: SSH Key Management on Windows](https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh_keymanagement)
- [GeekRewind: SSH Key Auth with Windows 11](https://geekrewind.com/how-to-set-up-ssh-key-login-with-windows-11/)
- [Ubuntu: SSH Keygen on Windows](https://ubuntu.com/tutorials/ssh-keygen-on-windows)

### UPS / NUT
- [Techno Tim: NUT Server Ultimate Guide](https://technotim.com/posts/NUT-server-guide/)
- [Network UPS Tools Official](https://networkupstools.org/)
- [Jeff Geerling: NUT on Pi](https://www.jeffgeerling.com/blog/2025/nut-on-my-pi-so-my-servers-dont-die/)
- [OneUpTime: NUT on Ubuntu](https://oneuptime.com/blog/post/2026-03-02-how-to-configure-ups-monitoring-with-nut-on-ubuntu/view)

### Backups
- [CubeBackup: rsync + crontab Backups](https://www.cubebackup.com/blog/automatic-backup-linux-using-rsync-crontab/)
- [LinuxTechLab: Timeshift Guide](https://linuxtechlab.com/backup-ubuntu-systems-using-timeshift/)
- [TecAdmin: Backup and Restore Ubuntu](https://tecadmin.net/backup-and-restore-ubuntu-system/)

### Common Mistakes
- [HowToGeek: 5 Homelab Mistakes](https://www.howtogeek.com/homelab-mistakes-almost-ruined-self-hosting-dreams/)
- [hoop.dev: 11 Common SSH Security Mistakes](https://hoop.dev/blog/the-11-most-common-ssh-security-mistakes-and-how-to-fix-them/)
- [Dan Levy: Docker Security Tips for Self-Hosting](https://danlevy.net/docker-security-tips-for-self-hosting/)
- [Ubuntu: Automatic Updates Docs](https://documentation.ubuntu.com/server/how-to/software/automatic-updates/)

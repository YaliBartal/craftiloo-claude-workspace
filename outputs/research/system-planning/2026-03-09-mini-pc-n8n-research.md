# Mini PC + n8n Self-Hosting Research

**Date:** 2026-03-09
**Purpose:** Practical research on running n8n and Docker on mini PCs for home automation

---

## 1. n8n on Mini PCs -- What People Are Using

### Official Requirements vs Reality

| Tier | CPU | RAM | Storage | Use Case |
|------|-----|-----|---------|----------|
| **Official minimum** | 1 vCPU | 1 GB | 10 GB | Will crash under any real load |
| **Testing/hobby** | 2 cores | 2-4 GB | 20 GB | Simple workflows, learning |
| **Production (recommended)** | 4 cores | 8 GB | 50 GB SSD | Business-critical automations |
| **Heavy/AI workflows** | 4+ cores | 16 GB | 100 GB NVMe | AI agents, large context windows |

### What the Community Actually Runs

From n8n community forums and Reddit:

- **Intel N100/N150 with 16 GB RAM** -- most recommended budget option (~$120-180)
- **Intel Core i5 7th gen, 8 GB RAM** -- works fine for basic workflows
- **Used Dell Optiplex Micro / Intel NUC** -- popular eBay finds ($80-150)
- **Beelink S12 Pro (N100)** -- frequently cited as the go-to budget pick
- **ZBOX / MinisForum** -- users report good experience

### Critical: AI Workflows Are RAM-Hungry

When an AI agent "thinks," it passes massive context windows between nodes serialized as JSON. A simple chat history can consume **200 MB of RAM per execution**. If you plan to run AI agent workflows through n8n, 16 GB RAM is the minimum.

### Production Stack (What You Actually Need)

A real n8n deployment runs **3-5 containers minimum:**

| Container | RAM Usage | Purpose |
|-----------|-----------|---------|
| n8n main | 500 MB - 2 GB | Workflow engine |
| PostgreSQL | 200-500 MB | Database (required for production) |
| Redis | 50-100 MB | Queue mode for reliability |
| n8n worker(s) | 500 MB - 1 GB each | Parallel execution |
| Traefik/Caddy | 50-100 MB | Reverse proxy + SSL |

**Total baseline: ~1.5 - 4 GB RAM** for the n8n stack alone, leaving headroom on a 8-16 GB system.

---

## 2. Docker Engine vs Docker Desktop -- RAM Usage

### The Key Difference

| | Docker Desktop | Docker Engine (native) |
|---|---|---|
| **Idle RAM** | 3-4 GB | ~50-100 MB (daemon only) |
| **Architecture** | Runs a Linux VM (even on Linux) | Native Linux containers |
| **GUI** | Yes (Electron app) | No (CLI only, use Portainer for GUI) |
| **Best for** | Windows/Mac development | Linux servers, production |

**Bottom line: On a Linux mini PC, never install Docker Desktop.** Install Docker Engine directly. The overhead difference is massive -- 3+ GB of RAM saved.

### Alternative: Podman

- 100% Docker-compatible (same commands)
- Daemonless (no background process eating RAM)
- Rootless by default (better security)
- Slightly faster startup

### Minimum Specs for 3-5 Containers

| RAM | Feasibility |
|-----|------------|
| **4 GB** | Possible but tight. n8n + PostgreSQL + Redis fills it. No headroom. |
| **8 GB** | Comfortable for 3-5 containers. Recommended minimum. |
| **16 GB** | Run 10+ containers easily. Room for AI workflows. Future-proof. |
| **32 GB** | Overkill for n8n, but great if also running Proxmox VMs. |

---

## 3. OS Choice: Ubuntu Server vs Proxmox vs Others

### Option A: Ubuntu Server (Bare Metal) -- RECOMMENDED FOR YOUR USE CASE

**Pros:**
- Simplest path: install OS, install Docker, run containers
- Minimal overhead -- no hypervisor layer eating resources
- Huge community, best documentation, most tutorials target Ubuntu
- Native Linux tools (Btrfs snapshots, cron, systemd) just work
- Ansible/Terraform automation integrates naturally
- More up-to-date kernel and container runtimes than Proxmox

**Cons:**
- No built-in VM management (don't need it for n8n)
- No web GUI for OS management (use Cockpit if wanted)
- Backup/restore requires manual setup

**Best for:** Single-purpose automation server. Your use case.

### Option B: Proxmox VE

**Pros:**
- Web GUI for VM/container management
- LXC containers share host kernel (very low overhead)
- Easy backup/snapshot/restore of entire environments
- Can run 100+ Docker containers across multiple LXCs
- Great for learning virtualization

**Cons:**
- Adds complexity you don't need for just n8n
- Proxmox itself consumes 1-2 GB RAM
- Overkill for a single-purpose automation box
- Subscription nag (free tier works but reminds you)

**Best for:** Multi-purpose homelab running diverse services.

### Option C: Debian (Minimal)

**Pros:**
- Even lighter than Ubuntu
- Rock-solid stability
- What Proxmox is built on

**Cons:**
- Slightly less beginner-friendly
- Some packages older than Ubuntu

### Recommendation

**For a dedicated n8n automation box: Ubuntu Server 24.04 LTS, bare metal.** No Proxmox overhead, maximum resources for containers, easiest path from zero to running.

---

## 4. Power Consumption -- Real-World Numbers

### Intel N100 (6W TDP) -- The Budget King

| State | Watts (at wall) | Annual Cost (US $0.12/kWh) |
|-------|-----------------|---------------------------|
| **Idle (headless)** | 6-8W | $6-8/yr |
| **Light load (Docker + n8n)** | 9-12W | $9-13/yr |
| **Full load** | 20-27W | $21-28/yr |

Real measurements: Beelink S12 Pro idles at 6-8W headless, 9-11W with mixed workloads.

### AMD Ryzen 5500U (15W TDP)

| State | Watts | Annual Cost |
|-------|-------|-------------|
| **Idle** | 7-10W | $7-11/yr |
| **Light load** | 12-18W | $13-19/yr |
| **Full load** | 25-35W | $26-37/yr |

### AMD Ryzen 7 (28W+ TDP)

| State | Watts | Annual Cost |
|-------|-------|-------------|
| **Idle** | 12-18W | $13-19/yr |
| **Light load** | 20-30W | $21-32/yr |
| **Full load** | 45-65W | $47-68/yr |

### Context: What This Means for You

Running an N100 mini PC 24/7 for n8n automation costs about **$1/month in electricity**. Even the beefier Ryzen options are under $3/month. Compare this to a VPS at $5-20/month.

Every watt of idle power = ~$1/year (US rates). An N100 at 8W idle = $8/year. A Ryzen 7 at 15W idle = $15/year. The difference is negligible.

---

## 5. Noise Levels -- Fanless vs Quiet vs Noticeable

### Truly Silent (Fanless, 0 dB)

| Model | Processor | RAM | Price Range |
|-------|-----------|-----|-------------|
| **MeLE Quieter 4C** | N100 | 8-16 GB | $150-200 |
| **MINIX Z100-0dB** | N100 | 8-16 GB | $180-220 |
| **CWWK fanless N100** | N100 | configurable | $120-180 |
| Various fanless N100 units | N100 | varies | $100-200 |

User report: "Never wakes the household with fans spinning up, even during remote management tasks."

**Caveat:** Fanless relies on passive cooling via the case. Works fine for N100's 6W TDP. Not viable for Ryzen 7 processors.

### Quiet (Fan rarely spins, <25 dB)

| Model | Processor | Notes |
|-------|-----------|-------|
| **Beelink S12 Pro** | N100 | Fan exists but rarely activates at idle |
| **Beelink EQ12** | N100 | Similar; fan kicks in under sustained load |
| Intel NUC (various) | i3/i5 | Quiet but audible under load |

### Noticeable (Fan always on, 25-35 dB)

- Most Ryzen 5/7 mini PCs have always-on fans
- Higher TDP processors generate more heat
- BIOS fan curve tuning can help but won't eliminate noise

### Recommendation

**For a closet/shelf automation server: Any N100 fanless unit.** Zero noise, zero maintenance, plenty of power for n8n + Docker.

---

## 6. Reliability -- Brand Reports

### Beelink

| Aspect | Rating | Details |
|--------|--------|---------|
| **Build quality** | Good | Generally solid construction, decent QC |
| **Warranty** | 3 years | Covers manufacturing defects |
| **Support** | Mixed | Responds to claims, but can be slow; may ask you to run tests before RMA |
| **Known issues** | Thermal paste degradation (temps rise 20C after months), some random reboot reports |
| **Buy from** | Amazon preferred (easier returns than direct) |

### MinisForum

| Aspect | Rating | Details |
|--------|--------|---------|
| **Build quality** | Good-Excellent | Higher-end models well-built, better variety |
| **Warranty** | Standard | But known to reject claims and ask customer to pay shipping to China |
| **Support** | Poor-Mixed | Reports of ignored support emails, warranty pushback |
| **Known issues** | Some thermal issues on certain models requiring re-spins |
| **Buy from** | Amazon (warranty protection via Amazon) |

### GMKtec

| Aspect | Rating | Details |
|--------|--------|---------|
| **Build quality** | Budget | Competitive hardware at low prices |
| **Warranty** | Standard on paper | |
| **Support** | Poor | Ignored support emails, minimal post-sale support |
| **Known issues** | Questionable engineering on some models |
| **Buy from** | Only if comfortable self-troubleshooting; Amazon for return safety |

### GEEKOM

| Aspect | Rating | Details |
|--------|--------|---------|
| **Build quality** | Excellent | Consistently ranked most reliable in 2025-2026 reviews |
| **Support** | Good | Better than Chinese competitors |
| **Price** | Higher | Premium for reliability |

### Practical Advice

1. **Buy from Amazon** -- regardless of brand, Amazon's return policy protects you
2. **Budget brands are fine for non-critical use** -- n8n automation can tolerate occasional reboots
3. **Beelink is the sweet spot** -- best balance of price, quality, and support
4. **Re-apply thermal paste** after 6-12 months if you notice temp creep
5. **Keep a spare** -- at $120 for an N100, buying two is cheaper than downtime

### Spyware Concern

Chinese mini PCs (all brands above) have been flagged for potential spyware. Mitigation: **Wipe Windows, install Ubuntu Server fresh.** This eliminates any pre-installed software concerns entirely.

---

## 7. Setup Difficulty -- Beginner Assessment

### Honest Difficulty Rating

| Task | Difficulty | Time | Notes |
|------|-----------|------|-------|
| Install Ubuntu Server from USB | Easy | 20 min | Guided installer, just follow prompts |
| Install Docker Engine | Easy | 10 min | 5 commands from official docs |
| Run n8n with docker-compose | Easy | 15 min | Copy a YAML file, run one command |
| Set up PostgreSQL for n8n | Medium | 30 min | Requires understanding env variables |
| Configure SSL/HTTPS | Medium-Hard | 1-2 hrs | Needs domain + DNS + reverse proxy |
| Set up webhooks (public access) | Hard | 1-2 hrs | Requires Tailscale Funnel or Cloudflare Tunnel |
| Queue mode (Redis + workers) | Medium | 30 min | Extra containers in docker-compose |
| Automated backups | Medium | 30 min | Cron + pg_dump script |

### Total Time Estimate

- **Basic setup (n8n running locally):** 1-2 hours
- **Production-ready (PostgreSQL + SSL + backups):** 4-6 hours
- **Full stack (+ webhooks + monitoring + queue mode):** 1-2 days

### Best Tutorials & Guides

1. **DigitalOcean's n8n guide** -- step-by-step, production-quality
2. **n8n official Docker Compose docs** -- the canonical reference
3. **Onidel blog** -- "Install n8n on Ubuntu with Docker" -- beginner-focused
4. **XDA Developers** -- "I built a silent home server using an Intel N100 mini PC"
5. **Latenode's n8n system requirements guide** -- comprehensive hardware + software analysis

### The 97% Stat

The 2024 r/selfhosted survey showed **97% of respondents use containers**. Docker has become the standard. Modern tools like Portainer (GUI for Docker) and NGINX Proxy Manager (point-and-click SSL) have turned sysadmin into point-and-click tasks.

### Realistic Assessment for a Linux Beginner

- **Day 1:** Ubuntu installed, Docker running, n8n accessible on local network
- **Week 1:** Comfortable with docker-compose, PostgreSQL configured
- **Month 1:** SSL, backups, and remote access sorted out
- **Ongoing:** Occasional updates (`docker compose pull && docker compose up -d`)

The n8n community warns that self-hosting requires "advanced technical expertise" and errors can cause data loss. This is **legally cautious language**. In practice, thousands of non-sysadmins run n8n on home hardware. The Docker Compose approach isolates everything -- if something breaks, delete the container and recreate it.

---

## 8. Remote Management -- How People Access Headless Mini PCs

### Tier 1: SSH (Everyone Uses This)

- Built into Ubuntu Server
- Access from any terminal: `ssh user@mini-pc-ip`
- Works on local network immediately, no setup needed
- **Verdict:** Must-have baseline. Zero overhead.

### Tier 2: Tailscale (The Game-Changer)

| Feature | Details |
|---------|---------|
| **What it does** | Creates a private VPN mesh between your devices |
| **Setup** | Install on mini PC + phone/laptop. Done. |
| **Access** | SSH, web UIs, everything -- from anywhere in the world |
| **Cost** | Free for personal use (up to 100 devices) |
| **Overhead** | Negligible (~20 MB RAM) |
| **Security** | WireGuard-based, no open ports needed |

Community consensus: **Tailscale is the single most recommended tool for remote access** in r/selfhosted. It eliminates port forwarding, dynamic DNS, and VPN server setup.

For webhooks: **Tailscale Funnel** can expose specific services to the internet without opening router ports.

### Tier 3: Portainer (Docker GUI)

- Web-based Docker management at `http://mini-pc:9443`
- View containers, logs, resource usage
- Start/stop/restart containers with a click
- Deploy new stacks from templates
- **Verdict:** Highly recommended. First container you should install.

### Tier 4: Cockpit (System GUI)

- Web-based Linux server management at `http://mini-pc:9090`
- Monitor CPU, RAM, disk, network
- Manage storage, users, services
- View system logs
- Terminal in the browser
- **Verdict:** Nice-to-have for beginners who want a dashboard. Install with `apt install cockpit`.

### Recommended Stack (Simplest to Most Complete)

| Level | Tools | For Who |
|-------|-------|---------|
| **Minimal** | SSH + Tailscale | Comfortable with terminal |
| **Comfortable** | SSH + Tailscale + Portainer | Want a Docker GUI |
| **Full dashboard** | SSH + Tailscale + Portainer + Cockpit | Want system monitoring too |

---

## Summary: Recommended Setup for Your Use Case

### Hardware

| Component | Recommendation | Cost |
|-----------|---------------|------|
| **Mini PC** | Beelink S12 Pro or EQ12 (N100, 16 GB RAM, 500 GB SSD) | $150-180 |
| **Backup unit** | Same model (optional, for peace of mind) | $150-180 |

### Software Stack

| Layer | Choice | Why |
|-------|--------|-----|
| **OS** | Ubuntu Server 24.04 LTS | Simplest, most documented, no overhead |
| **Container runtime** | Docker Engine (NOT Desktop) | Native, lightweight |
| **n8n** | Docker Compose with PostgreSQL + Redis | Production-ready |
| **Remote access** | Tailscale + SSH | Access from anywhere, zero config |
| **Docker GUI** | Portainer | Visual container management |
| **Reverse proxy** | Caddy or Traefik | Auto-SSL if exposing to internet |

### Power & Noise

- **8-12W** at the wall while running your full stack
- **$1/month** electricity
- **Silent** (fanless N100) or **inaudible** (fan rarely spins)

### Key Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Hardware failure | Buy from Amazon (easy returns). Consider a spare. |
| Power outage | UPS ($40-60) if uptime is critical |
| ISP issues for webhooks | Use Tailscale Funnel or Cloudflare Tunnel |
| Data loss | Automated PostgreSQL backups to cloud storage |
| Security | Fresh Ubuntu install (no Windows spyware risk), Tailscale (no open ports) |
| Mini PC thermal degradation | Re-paste after 6-12 months; monitor temps |

### vs. Staying on GitHub Actions

| Factor | GitHub Actions | Mini PC |
|--------|---------------|---------|
| **Monthly cost** | Free (2000 min) or $4+ | ~$1 electricity |
| **Upfront cost** | $0 | $150-180 |
| **Webhooks** | Native | Requires tunnel setup |
| **Always-on** | Yes (cloud) | Yes (if power stays on) |
| **n8n GUI** | Not available | Full visual workflow builder |
| **Complexity** | YAML workflows | Docker Compose + Linux basics |
| **Worker interaction** | Limited | Full Slack bot / approval flows possible |

---

## Sources

- [n8n Community: Mini PC config for n8n](https://community.n8n.io/t/mini-pc-config-for-n8n/99337)
- [n8n Community: Hardware For Self Hosting](https://community.n8n.io/t/hardware-for-self-hosting/30647)
- [n8n Community: Self-Host Hardware Requirements](https://community.n8n.io/t/self-host-hardware-requirements/12843)
- [Latenode: N8N System Requirements 2025](https://latenode.com/blog/low-code-no-code-platforms/n8n-setup-workflows-self-hosting-templates/n8n-system-requirements-2025-complete-hardware-specs-real-world-resource-analysis)
- [ThinkPeak: n8n Self-Hosted Requirements 2026](https://thinkpeak.ai/n8n-self-hosted-requirements-2026/)
- [XDA: 5 reasons I prefer Ubuntu Linux instead of Proxmox](https://www.xda-developers.com/reasons-prefer-ubuntu-linux-proxmox-home-server/)
- [XDA: I built a silent home server using an Intel N100 mini PC](https://www.xda-developers.com/built-silent-home-server-using-intel-n100-mini-pc/)
- [XDA: 9 Docker containers that run 24/7 on my $100 mini PC](https://www.xda-developers.com/docker-containers-that-run-247-on-my-100-mini-pc/)
- [XDA: If you're running Docker on bare metal, Proxmox LXC containers are lighter](https://www.xda-developers.com/if-youre-running-docker-on-bare-metal-proxmox-lxc-containers-are-lighter-and-easier-to-manage/)
- [Hobbyist's Hideaway: N100 & N150 Mini PC Power Consumption Guide](https://bishalkshah.com.np/blog/low-power-homelab-n100-mini-pc)
- [Jeff Geerling: Is an Intel N100 a better value than a Raspberry Pi?](https://www.jeffgeerling.com/blog/2025/intel-n100-better-value-raspberry-pi/)
- [Overclockers UK: Minisforum, Gmktec, Beelink reliability thread](https://forums.overclockers.co.uk/threads/minisforum-gmktec-beelink.19002413/)
- [Level1Techs: MINISFORUM and other mini PCs reliability question](https://forum.level1techs.com/t/minisforum-and-other-mini-pcs-reliability-question/212247)
- [PC Build Advisor: Best Mini PC Manufacturers Reviewed](https://www.pcbuildadvisor.com/what-are-the-best-mini-pc-manufacturers-minisforum-beelink-geekom-gmktec-aoostar-acemagic-trigkey-reviewed/)
- [Beelink Trustpilot Reviews](https://www.trustpilot.com/review/www.bee-link.com)
- [DigitalOcean: How to Set Up n8n](https://www.digitalocean.com/community/tutorials/how-to-setup-n8n)
- [n8n Docs: Docker Compose Setup](https://docs.n8n.io/hosting/installation/server-setups/docker-compose/)
- [Toolsana: Production n8n Docker Compose with PostgreSQL & Redis](https://toolsana.com/blog/n8n-docker-compose-production-postgresql-redis/)
- [Future Tech Stack: Docker Desktop Alternatives 2025](https://futuretechstack.io/posts/docker-desktop-alternatives-2025/)
- [Docker Forums: Docker Desktop Idle Memory Usage](https://forums.docker.com/t/docker-desktop-idle-memory-usage/138540)
- [XDA: Tailscale guide for self-hosted services](https://www.xda-developers.com/tailscale-guide/)
- [Tailscale: How to self-host with Proxmox](https://tailscale.com/blog/guide-self-hosting-proxmox)
- [Fullmetalbrackets: Home server with Tailscale](https://fullmetalbrackets.com/blog/how-i-setup-home-server/)
- [SimpleHomelab: Best Home Server OS + Proxmox VM vs LXC](https://www.simplehomelab.com/udms-03-best-home-server-os/)
- [efundies: Unraid vs Proxmox vs Ubuntu Comparative Analysis](https://efundies.com/unraid-vs-proxmox-vs-ubuntu/)
- [Virtualization Howto: Docker Performance Tweaks on Low-Power Hardware](https://www.virtualizationhowto.com/2025/05/top-docker-performance-tweaks-on-low-power-hardware/)
- [n8n Community: Running n8n on a homeserver](https://community.n8n.io/t/running-n8n-on-a-homeserver/50492)

# Craftiloo Automation — n8n on GMKtec NucBox

**Status:** Daily skills live since 2026-03-12. Weekly/monthly skills staged, not yet activated.

---

## Architecture

```
n8n (Docker, host network, UI at http://10.0.0.22:5678)
  │
  │  cron triggers (Asia/Jerusalem timezone)
  │  HTTP Request nodes
  ▼
skill-api.py (port 5680, systemd service on host)
  │
  │  validates skill name, acquires lock
  ▼
skill-runner.py (config, locking, logging, git ops)
  │
  │  executes headless Claude Code
  ▼
claude -p "Run the <skill> skill"
  │
  │  calls MCP tools (Amazon Ads, SP-API, Slack, etc.)
  ▼
Output files → git commit + push → Slack notification
```

**Hardware:** GMKtec NucBox M8 (Ubuntu 24.04) at 10.0.0.22
**Orchestrator:** n8n (Docker, `network_mode: host`) — visual workflow UI + cron scheduling
**API bridge:** `automation/skill-api.py` — HTTP server on host, port 5680. n8n calls this instead of running commands directly (Docker can't access host python3/claude).
**Runner:** `automation/skill-runner.py` — Python, handles config, locks, logging, git
**Model:** claude-sonnet-4-6 (all automated runs)
**Cost:** $0 infrastructure. ~$30-40/mo Claude API tokens.

### Why the skill-api bridge?

n8n runs inside Docker (Alpine Linux) — no python3, no claude CLI. The n8n executeCommand node runs inside the container. The skill-api.py runs as a systemd service on the host and exposes 3 endpoints:

| Endpoint | Method | Purpose |
|---|---|---|
| `/run` | POST | Run a skill. Body: `{"skill": "daily-market-intel", "flags": "--dry-run"}` |
| `/pull` | POST | Git pull the workspace. Used by git-sync workflow. |
| `/health` | GET | Health check. Returns uptime and status. |

Security: only listens on `0.0.0.0:5680` (local network only, NucBox is behind NAT). Skill names are whitelisted. Flags are whitelisted. Command injection is not possible.

---

## What's Active Now (2026-03-13 — Full New Architecture Live)

### n8n Workflows

| Workflow | Status | ID | Purpose |
|---|---|---|---|
| **Craftiloo Skill Scheduler** | ACTIVE | `PmTbyvW67XpVEv8b` | Master scheduler — all 9 schedules |
| **Monday PPC Pipeline** | ACTIVE | `yUafv7HE3fSAgliu` | Sub-workflow: 5 AUTONOMOUS data skills |
| **Git Auto-Sync** | ACTIVE | `zHHmmLqDVqWLSaeg` | Polls git every 2 min, auto-pulls new code |
| Friday PPC Chain | INACTIVE | `vYM5hKbUd6p7GAQf` | **DEPRECATED** (old 3-skill chain, replaced by Fri 12PM inline) |

### Full Weekly Schedule

| Day | Time (IST) | Skill / Workflow | Mode | Timeout |
|---|---|---|---|---|
| **Every day** | 8:00 AM | daily-market-intel | Full | 25 min |
| **Every day** | 8:30 AM | ppc-daily-health | Full | 20 min |
| **Monday** | 9:00 AM | weekly-ppc-analysis | Full | 30 min |
| **Monday** | 10:30 AM | Monday Pipeline (sub-workflow) | AUTONOMOUS × 5 | ~2 hrs total |
| | ↳ 10:30 | ppc-tacos-optimizer | AUTONOMOUS | 25 min |
| | ↳ 11:00 | ppc-portfolio-summary | AUTONOMOUS | 25 min |
| | ↳ 11:30 | keyword-rank-optimizer | AUTONOMOUS | 25 min |
| | ↳ 12:00 | ppc-bid-recommender | AUTONOMOUS | 25 min |
| | ↳ 12:30 | ppc-search-term-harvester | AUTONOMOUS | 25 min |
| **Tuesday** | 12:00 PM | ppc-agent-autonomous-tuesday | Deep-dive, report only | 55 min |
| **Thursday** | 9:00 AM | competitor-price-serp-tracker | Full | 35 min |
| **Friday** | 12:00 PM | ppc-agent-autonomous-friday | Validation only | 40 min |
| **Sunday** | 9:00 AM | brand-analytics-weekly | Full | 30 min |
| **1st of month** | 10:00 AM | ppc-monthly-review | Full | 35 min |

### Two-Day PPC Autonomous Workflow

```
Monday 10:30 AM → 5 skills each save -autonomous-*.json files (no API writes)
                  ├── ppc-tacos-optimizer → tacos-optimizer/{date}-autonomous-analysis.json
                  ├── ppc-portfolio-summary → portfolio-summaries/{date}-autonomous-summary.json
                  ├── keyword-rank-optimizer → rank-optimizer/{date}-autonomous-analysis.json
                  ├── ppc-bid-recommender → bids/{date}-autonomous-recommendations.json
                  └── ppc-search-term-harvester → search-terms/{date}-autonomous-harvest.json

Tuesday 12:00 PM → ppc-agent reads all Monday files, cross-references, synthesizes
                   └── Outputs: sessions/{date}-tuesday-brief.md + sessions/{date}-tuesday-actions.json
                               + Notion page + Slack summary to #claude-ppc-updates

User reviews brief → approves action items → applies interactively

Friday 12:00 PM → ppc-agent validates applied actions (before/after comparison)
                  └── Updates: sessions/{date}-tuesday-actions.json validation fields
                              + Friday brief with WORKED/PARTIAL/FAILED verdicts
```

### Services

| Service | How It Runs | Port | Purpose |
|---|---|---|---|
| n8n | Docker (`docker compose`, host network) | 5678 | Workflow orchestration |
| PostgreSQL | Docker (bridge network) | 5432 (localhost) | n8n database |
| skill-api | systemd user service | 5680 | Bridge between n8n and host |
| health-check | cron (7:00 AM daily) | — | Server health ping to Slack |

---

## How It Works

### Per-Skill Execution Flow

1. n8n cron fires → HTTP POST to `http://127.0.0.1:5680/run` with `{"skill": "<name>"}`
2. skill-api validates the skill name, acquires a thread lock
3. skill-api calls `skill-runner.py <skill-name>` as a subprocess
4. Runner loads config from `config.yaml`
5. Acquires file lock (`/tmp/claude-skill.lock`) — prevents concurrent runs
6. `git pull` to get latest code
7. Runs `claude -p "<prompt>"` with configured model, max turns, timeout
8. Claude executes the skill, calls APIs, writes output files
9. Runner commits outputs to git and pushes
10. Returns exit code + JSON result to skill-api → back to n8n
11. n8n checks exit code → routes to "Done" or "Slack failure alert"

### Git Auto-Sync Flow

1. n8n fires every 2 minutes → HTTP POST to `http://127.0.0.1:5680/pull`
2. skill-api runs `git pull --ff-only` on the workspace
3. If output is "Already up to date." → no action
4. If new code was pulled → posts notification to `#claude-alerts`

This means: push from your laptop → server has the code within 2 minutes.

### Exit Codes

| Code | Meaning |
|---|---|
| 0 | Success |
| 1 | Skill execution failed |
| 2 | Timeout |
| 3 | Git error |
| 4 | Configuration error |
| 5 | Lock conflict (another skill running) |

### Failure Handling

- Any non-zero exit code → Slack alert posted to `#claude-alerts`
- The skill's own Slack notification (e.g., to #claude-morning-brief) only happens on success (Claude posts it as part of the skill)
- No automatic retry — failed daily skills run again next day

---

## Key Files

| File | Purpose |
|---|---|
| `automation/config.yaml` | Central config — skill prompts, timeouts, turns, channels |
| `automation/skill-api.py` | HTTP API bridge between n8n (Docker) and host |
| `automation/skill-api.service` | Systemd service definition for skill-api |
| `automation/skill-runner.py` | Production runner — locking, logging, git, Claude execution |
| `automation/n8n-workflows/master-scheduler-full.json` | **Authoritative master scheduler** (all 9 schedules, live in n8n as `PmTbyvW67XpVEv8b`) |
| `automation/n8n-workflows/monday-pipeline-chain.json` | Monday 5-skill AUTONOMOUS pipeline (live in n8n as `yUafv7HE3fSAgliu`) |
| `automation/n8n-workflows/git-sync.json` | Git auto-sync workflow |
| `automation/n8n-workflows/master-scheduler.json` | SUPERSEDED — old daily-only scheduler, kept for reference |
| `automation/n8n-workflows/tuesday-chain.json` | DEPRECATED — old Tuesday executeCommand chain (replaced by monday-pipeline-chain) |
| `automation/n8n-workflows/friday-chain.json` | DEPRECATED — old Friday executeCommand chain (replaced by Fri 12PM inline in master) |
| `automation/health-check.sh` | Daily 7:00 AM server health ping to Slack |
| `automation/setup.sh` | One-time server setup (logs, cron, deps) |
| `/home/yali/n8n/docker-compose.yml` | Docker Compose for n8n + postgres |

---

## Health Monitoring

**Daily health check** runs at 7:00 AM IST (before any skills):
- Posts to `#claude-alerts`: system uptime, CPU, disk, memory, Docker status, Claude CLI version, run count
- If this message stops arriving, the server is down

**Logs:** `/var/log/claude/<skill>-YYYY-MM-DD-HH-MM-SS.json` (structured JSON, rotated weekly)

**skill-api status:** `systemctl --user status skill-api`

---

## Testing

### 1. Health Check (instant)

```bash
curl http://localhost:5680/health
```

### 2. Dry Run via API (no Claude, no git)

```bash
curl -s -X POST http://localhost:5680/run \
  -H "Content-Type: application/json" \
  -d '{"skill": "daily-market-intel", "flags": "--dry-run"}' | python3 -m json.tool
```

### 3. Verbose Run via API (real Claude, no git)

```bash
curl -s -X POST http://localhost:5680/run \
  -H "Content-Type: application/json" \
  -d '{"skill": "daily-market-intel", "flags": "--verbose --no-git"}' | python3 -m json.tool
```

### 4. Full Run via API (identical to what n8n does)

```bash
curl -s -X POST http://localhost:5680/run \
  -H "Content-Type: application/json" \
  -d '{"skill": "daily-market-intel"}' | python3 -m json.tool
```

### 5. Git Pull Test

```bash
curl -s -X POST http://localhost:5680/pull | python3 -m json.tool
```

### 6. n8n UI Test

Open `http://10.0.0.22:5678` → open workflow → click **"Test workflow"** to trigger all nodes manually.

---

## Adding a New Skill

1. Add a block to `config.yaml` under `skills:`
2. Add the skill name to `ALLOWED_SKILLS` in `skill-api.py`
3. Restart skill-api: `systemctl --user restart skill-api`
4. Add a trigger + HTTP Request + IF node row in the n8n workflow
5. Test: dry-run → verbose → full run → n8n trigger

---

## Activation Roadmap

| Phase | When | What |
|---|---|---|
| **Phase 1 (now)** | Mar 12+ | Daily market intel + PPC health + git auto-sync |
| **Phase 2** | After 3+ clean daily runs | Monday weekly PPC + Thursday competitors + Sunday BA |
| **Phase 3** | After Phase 2 stable | Tuesday chain (5 PPC skills) + Friday chain (3 PPC skills) |
| **Phase 4** | After Phase 3 stable | Monthly review (1st of month) |

---

## Docker Setup

**Location:** `/home/yali/n8n/docker-compose.yml`

Key config:
- n8n uses `network_mode: host` — shares the host's network stack, can reach skill-api on `127.0.0.1:5680`
- PostgreSQL exposed on `127.0.0.1:5432` (localhost only)
- n8n data persisted in Docker volume `n8n_data`
- Workspace mounted at `/workspace` (for file access if needed)

**Restart n8n:** `cd ~/n8n && docker compose up -d`
**Restart skill-api:** `systemctl --user restart skill-api`

---

## Previous System (Removed)

GitHub Actions workflows were created as Phase 1 but never reached production. All `.github/workflows/` files were deleted on 2026-03-11. The n8n approach is superior for this use case:
- Persistent filesystem (no cold starts, MCP servers always warm)
- No secrets mirroring (uses local `.env` directly)
- Native Israel timezone support
- Visual debugging in n8n UI
- $0 infrastructure cost

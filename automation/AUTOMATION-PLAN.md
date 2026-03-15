# Craftiloo Automation — n8n on GMKtec NucBox

**Last updated:** 2026-03-14
**Status:** Fully live. All skills active. Ghost chains deactivated.

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
  │  validates skill name, acquires thread lock
  ▼
skill-runner.py (config, file lock, logging, git ops)
  │
  │  executes headless Claude Code
  ▼
claude -p "<prompt>" --allowedTools ...
  │
  │  calls MCP tools (Amazon Ads, SP-API, Slack, etc.)
  ▼
Output files → git commit + push → Slack notification
```

**Hardware:** GMKtec NucBox M8 (Ubuntu 24.04) at 10.0.0.22
**Orchestrator:** n8n (Docker, `network_mode: host`) — cron scheduling + failure routing
**API bridge:** `automation/skill-api.py` — HTTP server on host, port 5680. n8n calls this because Docker containers can't access the host's python3/claude CLI.
**Runner:** `automation/skill-runner.py` — config loading, file locking, structured logging, git
**Model:** claude-sonnet-4-6 (all automated runs)
**Cost:** $0 infrastructure. ~$100–115/mo Claude API tokens.

### Why the skill-api bridge?

n8n runs inside Docker (Alpine Linux) — no python3, no claude CLI. `skill-api.py` runs as a systemd user service on the host and exposes:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/run` | POST | Run a skill. Body: `{"skill": "daily-market-intel"}` |
| `/pull` | POST | Git pull the workspace (used by git-sync workflow) |
| `/health` | GET | Basic health check — uptime + runner path |
| `/syshealth` | GET | Full system metrics — disk, memory, load, n8n, postgres, lock |

Security: skill names and flags are whitelisted. Command injection is not possible.

---

## Active n8n Workflows

| Workflow ID | Name | Status | Purpose |
|-------------|------|--------|---------|
| `PmTbyvW67XpVEv8b` | **Craftiloo Skill Scheduler** | ACTIVE | Master — all 13 triggers inline |
| `zHHmmLqDVqWLSaeg` | **Git Auto-Sync** | ACTIVE | Polls git every 2 min, auto-pulls new code |
| `bUKwPWxKnIunhKqJ` | **Server Health** | ACTIVE | Daily /syshealth check |
| `yUafv7HE3fSAgliu` | Tuesday PPC Chain | **INACTIVE** | Deprecated — old non-AUTONOMOUS chain |
| `8ometmla4UroHBuX` | Friday PPC Chain | **INACTIVE** | Deprecated — old non-AUTONOMOUS chain |

**Authoritative workflow file:** `automation/n8n-workflows/master-scheduler-current.json`

---

## Full Weekly Schedule

| Day | Time (IST) | Skill | Mode | Timeout |
|-----|------------|-------|------|---------|
| **Every day** | 7:00 AM | health-check.sh (cron) | — | — |
| **Every day** | 8:00 AM | daily-market-intel | Full | 25 min |
| **Every day** | 8:30 AM | ppc-daily-health | Full | 20 min |
| **Sunday** | 10:00 AM | weekly-ppc-analysis | Full | 50 min |
| **Wednesday** | 2:00 PM | brand-analytics-weekly | Full | 50 min |
| **Monday** | 10:00 AM | ppc-tacos-optimizer | AUTONOMOUS — even ISO weeks only | 25 min |
| **Monday** | 10:35 AM | ppc-portfolio-summary | AUTONOMOUS — every week | 25 min |
| **Monday** | 11:10 AM | keyword-rank-optimizer | AUTONOMOUS — odd ISO weeks only | 25 min |
| **Monday** | 11:45 AM | ppc-bid-recommender | AUTONOMOUS — every week | 25 min |
| **Monday** | 12:20 PM | ppc-search-term-harvester | AUTONOMOUS — every week | 25 min |
| **Tuesday** | 12:00 PM | ppc-agent-autonomous-tuesday | Deep-dive synthesis, report only | 55 min |
| **Thursday** | 9:00 AM | competitor-price-serp-tracker | Full | 35 min |
| **Friday** | 12:00 PM | ppc-agent-autonomous-friday | Validates PREVIOUS week's Tuesday actions | 40 min |
| **1st of month** | 10:00 AM | ppc-monthly-review | Full | 35 min |

### Monday Bi-Weekly Alternation

```
Odd ISO weeks  (11, 13, 15…):  keyword-rank-optimizer runs | tacos SKIPS
Even ISO weeks (12, 14, 16…):  ppc-tacos-optimizer runs   | keyword-rank SKIPS
```

Every Monday always runs: portfolio-summary + bid-recommender + search-term-harvester.

### Three-Layer PPC Autonomous Cycle

```
SUNDAY 10:00 AM
  weekly-ppc-analysis
  → Pulls 4 raw reports (campaigns 30d, search terms 14d, keywords, placements 7d)
  → Saves snapshots to outputs/research/ppc-weekly/snapshots/YYYY-MM-DD/

MONDAY pipeline (data collection — 3 or 4 skills depending on week)
  Each skill saves an -autonomous-*.json file, then exits. No user interaction.
  ├── ppc-portfolio-summary   → portfolio-summaries/YYYY-MM-DD-autonomous-summary.json
  ├── ppc-bid-recommender     → bids/YYYY-MM-DD-autonomous-recommendations.json
  ├── ppc-search-term-harvester → search-terms/YYYY-MM-DD-autonomous-harvest.json
  ├── ppc-tacos-optimizer (even weeks) → tacos-optimizer/YYYY-MM-DD-autonomous-analysis.json
  └── keyword-rank-optimizer (odd weeks) → rank-optimizer/YYYY-MM-DD-autonomous-analysis.json

TUESDAY 12:00 PM (synthesis session)
  ppc-agent reads Sunday's weekly-ppc snapshot + all Monday pipeline files
  → Cross-references, synthesizes, generates action items
  → Outputs: sessions/YYYY-MM-DD-tuesday-brief.md
             sessions/YYYY-MM-DD-tuesday-actions.json
             Notion page + Slack summary

User reviews brief → applies action items interactively

FRIDAY 12:00 PM (validation session)
  ppc-agent finds LAST WEEK's Tuesday actions.json (~10 days of post-application data)
  → Compares before/after metrics
  → Scores each action: WORKED / PARTIAL / INCONCLUSIVE / FAILED
  → Outputs: sessions/YYYY-MM-DD-friday-brief.md + validation verdicts
```

---

## Services

| Service | How It Runs | Port | Purpose |
|---------|-------------|------|---------|
| n8n | Docker (`docker compose`, host network) | 5678 | Workflow orchestration |
| PostgreSQL | Docker (bridge network) | 5432 (localhost) | n8n database |
| skill-api | systemd user service | 5680 | Bridge between n8n and host |
| health-check | cron (`0 5 * * *` UTC = 7AM IST) | — | Daily server ping to Slack |

---

## Per-Skill Execution Flow

1. n8n cron fires → HTTP POST to `http://127.0.0.1:5680/run` with `{"skill": "<name>"}`
2. skill-api validates skill name (ALLOWED_SKILLS whitelist), acquires thread lock
3. skill-api calls `skill-runner.py <skill-name>` as a subprocess
4. Runner loads config from `config.yaml`, merges defaults + skill overrides
5. Acquires file lock (`/tmp/claude-skill.lock`) — prevents concurrent runs
6. `git pull --ff-only origin master` to get latest code
7. Runs `claude -p "<prompt>"` with configured model, max turns, timeout
8. Claude executes the skill, calls MCP tools, writes output files
9. Runner commits outputs to git and pushes (only on success)
10. Returns JSON result to skill-api → HTTP response to n8n
11. n8n checks `exitCode == 0` → routes to Done or Slack failure alert

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Skill execution failed |
| 2 | Timeout |
| 3 | Git error |
| 4 | Configuration error |
| 5 | Lock conflict (another skill running) |

### Failure Handling

- Non-zero exit code → Slack alert to `#claude-alerts`
- Skill's own Slack notification (to skill-specific channel) only happens on success
- No automatic retry — failed daily skills run again next day

---

## Git Auto-Sync Flow

1. n8n fires every 2 minutes → HTTP POST to `http://127.0.0.1:5680/pull`
2. skill-api runs `git pull --ff-only` on the workspace
3. New commits pulled → posts notification to `#claude-alerts`

Push from any machine → server has the code within 2 minutes.

---

## Key Files

| File | Purpose |
|------|---------|
| `automation/config.yaml` | Central config — all skill schedules, prompts, timeouts, channels |
| `automation/skill-api.py` | HTTP API bridge between n8n (Docker) and host |
| `automation/skill-api.service` | Systemd service definition |
| `automation/skill-runner.py` | Production runner — locking, logging, git, Claude execution |
| `automation/health-check.sh` | Daily 7:00 AM server health ping to Slack |
| `automation/setup.sh` | One-time server setup (logs, cron, deps) |
| `automation/n8n-workflows/master-scheduler-current.json` | Live n8n workflow export (53 nodes, `PmTbyvW67XpVEv8b`) |
| `automation/n8n-workflows/git-sync.json` | Git auto-sync workflow |
| `automation/n8n-workflows/server-health.json` | Server health workflow |
| `automation/n8n-workflows/archive/` | Deprecated workflow JSONs (old chains, old scheduler) |
| `/home/yali/n8n/docker-compose.yml` | Docker Compose for n8n + postgres |

---

## Health Monitoring

**Daily health check** runs at 7:00 AM IST (before any skills):
- Posts to `#claude-alerts`: uptime, CPU load, disk, memory, Docker container status, Claude CLI version, run count
- Covers: n8n status, PostgreSQL status, skill-api lock file staleness, recent failure count

**Logs:** `/var/log/claude/<skill>-YYYY-MM-DD-HHMM.json` — structured JSON, rotated weekly, 12 weeks retention

**skill-api status:** `systemctl --user status skill-api`

---

## Testing

### 1. Health check (instant)
```bash
curl http://localhost:5680/health
curl http://localhost:5680/syshealth
```

### 2. Dry run (no Claude, no git)
```bash
curl -s -X POST http://localhost:5680/run \
  -H "Content-Type: application/json" \
  -d '{"skill": "daily-market-intel", "flags": "--dry-run"}' | python3 -m json.tool
```

### 3. Full run (identical to what n8n does)
```bash
curl -s -X POST http://localhost:5680/run \
  -H "Content-Type: application/json" \
  -d '{"skill": "daily-market-intel"}' | python3 -m json.tool
```

### 4. n8n UI test
Open `http://10.0.0.22:5678` → open workflow → click **"Test workflow"**

---

## Adding a New Skill

1. Add a block to `config.yaml` under `skills:`
2. Add the skill name to `ALLOWED_SKILLS` in `skill-api.py`
3. Restart skill-api: `systemctl --user restart skill-api`
4. Add trigger + HTTP Request + IF node row in the Craftiloo Skill Scheduler n8n workflow
5. Test: dry-run → verbose → full run → n8n trigger

---

## Docker Setup

**Location:** `/home/yali/n8n/docker-compose.yml`

- n8n uses `network_mode: host` — shares the host network stack, reaches skill-api on `127.0.0.1:5680`
- PostgreSQL on `127.0.0.1:5432` (localhost only)
- n8n data persisted in Docker volume `n8n_data`

**Restart n8n:** `cd ~/n8n && docker compose up -d`
**Restart skill-api:** `systemctl --user restart skill-api`

---

## Previous Architecture (Removed)

- **GitHub Actions** — created March 2026 but never reached production. Deleted 2026-03-11. n8n approach is superior: persistent filesystem, no cold starts, Israel timezone support, $0 infrastructure.
- **Tuesday PPC Chain** (`yUafv7HE3fSAgliu`) — ran 5 skills non-autonomously on Tuesdays. Replaced by the Monday pipeline + Tuesday synthesis architecture. Deactivated 2026-03-14.
- **Friday PPC Chain** (`8ometmla4UroHBuX`) — ran 3 skills non-autonomously on Fridays. Replaced by Friday validation agent. Deactivated 2026-03-14.

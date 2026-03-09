# Craftiloo Automation Plan — Phase 1: GitHub Actions + Claude Scheduling

**Approach:** Start with zero infrastructure (no VPS, no n8n). Use GitHub Actions for 24/7 scheduled skills and Claude Desktop scheduled tasks for work-hours monitoring. Add VPS + n8n later only if worker Slack interaction becomes a clear need.

---

## 1. How It Works (No VPS, No n8n)

```
┌──────────────────────────────────────────────────────┐
│                  GITHUB ACTIONS                       │
│  Runs 24/7 on GitHub's servers (free)                │
│  YAML workflow files in .github/workflows/            │
│                                                       │
│  6:00 AM → daily-market-intel                        │
│  6:30 AM → ppc-daily-health                          │
│  Mon 8AM → weekly-ppc-analysis                       │
│  Tue 8AM → ppc-tacos-optimizer                       │
│  ...etc                                              │
└───────────────────┬──────────────────────────────────┘
                    ↓ each skill run posts results via MCP
┌──────────────┐  ┌──────────────┐  ┌──────────────────┐
│    SLACK     │  │   NOTION     │  │  OUTPUT FILES    │
│ #market-intel│  │ Report DBs   │  │ committed to repo│
│ #ppc-updates │  │ (browsable)  │  │ (version history)│
└──────────────┘  └──────────────┘  └──────────────────┘
```

**Your computer is off. You're asleep. Skills still run.**

GitHub Actions runs Claude Code on Ubuntu servers. Each workflow:
1. Checks out this repo
2. Installs Python + MCP server dependencies
3. Runs Claude Code with a skill prompt
4. Claude executes the skill, calls MCP tools (Slack, Notion, APIs)
5. Commits output files back to the repo
6. Posts results to Slack + Notion via notification-hub

**Cost: $0 infrastructure.** Free tier = 2,000 minutes/month. Your daily + weekly skills use ~300 min/month total.

---

## 2. All 26 Skills — Automation Map

### Fully Automatable (schedule and forget)

| Skill | Schedule | What It Does | Tokens | Time |
|---|---|---|---|---|
| **daily-market-intel** | Daily 6:00 AM | BSR/rank tracking, competitor snapshots, alerts | ~80K | 8-10 min |
| **ppc-daily-health** | Daily 6:30 AM | Traffic-light status per portfolio, anomaly detection | <30K | <3 min |
| **weekly-ppc-analysis** | Mon 8:00 AM | 4 Ads API reports, WoW comparison, 30-day trajectories | <80K | 5-7 min |
| **ppc-portfolio-summary** | Tue+Fri 9:00 AM | Portfolio health classification, structure audit | <40K | <4 min |
| **ppc-tacos-optimizer** | Tue 8:00 AM | TACoS scorecard, profit reality, organic momentum | <60K | <5 min |
| **keyword-rank-optimizer** | Tue 9:30 AM | PPC spend vs organic rank cross-reference | <65K | <6 min |
| **competitor-price-serp-tracker** | Thu 8:00 AM | Competitor prices/BSR/reviews + SERP positions | <80K | ~10 min |
| **ppc-monthly-review** | Last day of month | Strategic review, trends, stage transitions | <100K | <10 min |

**8 skills, fully headless, zero human input needed.**

### Semi-Automatable (analysis runs automatically, execution needs approval)

| Skill | Schedule | Analysis | Execution | Approval Pattern |
|---|---|---|---|---|
| **ppc-bid-recommender** | Tue+Fri 10:00 AM | Generates bid change table | Applies bid changes via API | Report to Slack → user approves locally |
| **ppc-search-term-harvester** | Tue+Fri 10:30 AM | Classifies NEGATE/PROMOTE/DISCOVER | Adds negatives, promotes terms | Report to Slack → user approves locally |
| **ppc-campaign-creator** | After harvester | Proposes up to 5 campaigns | Creates in PAUSED state | Report to Slack → user enables |
| **negative-keyword-generator** | Monthly per portfolio | Generates proactive negative list | Applies via API | Report to Slack → user approves locally |
| **listing-optimizer** | Monthly | Portfolio scan, scores all listings | Pushes rewrites to live listing | Scan auto, rewrites need approval |
| **ppc-agent** (orchestrator) | Daily 9:30 AM | Routes to appropriate sub-skill based on cadence | Delegates execution | Orchestration is headless |

**Approval pattern:** GitHub Actions runs the skill in **report-only mode** → posts recommendations to Slack → you review on your phone → approve by running the execution step locally in Claude Code (or configure auto-execute with guardrails).

### Manual Only (need human input to start)

| Skill | Why Manual | When Used |
|---|---|---|
| **listing-creator** | Needs product specs, positioning decisions | New product launch |
| **image-planner** | Needs product info, strategic direction | New product launch |
| **product-listing-development** | Orchestrates listing + image (collaborative) | New product launch |
| **customer-review-analyzer** | Needs ASIN selection, scope questions | On-demand research |
| **niche-category-analysis** | Needs niche keyword, scoping questions | Exploring new markets |
| **ppc-portfolio-action-plan** | Needs portfolio name, approval per action | Deep dive when portfolio needs work |
| **daily-prep** | Asks about your to-do list | Morning briefing |
| **automation-discovery-interview** | 30-40 min interactive interview | Quarterly review |
| **skill-creator** | Needs skill specification | Building new skills |
| **mcp-builder** | Needs API credentials and service info | Connecting new services |

### Utility

| Skill | Role |
|---|---|
| **notification-hub** | Called by other skills to post Slack summaries. Not scheduled directly. |

---

## 3. The Daily Workflow

### What happens automatically (you're asleep)

```
6:00 AM  ─── daily-market-intel ──→ Slack #market-intel + Notion "Market Intel" DB
6:30 AM  ─── ppc-daily-health ────→ Slack #ppc-updates + Notion "PPC Health" DB
```

### What happens on specific days (you're asleep)

```
MONDAY
  8:00 AM  ─── weekly-ppc-analysis ────→ Slack #ppc-updates + Notion "PPC Weekly" DB

TUESDAY
  8:00 AM  ─── ppc-tacos-optimizer ────→ Slack #ppc-updates
  9:00 AM  ─── ppc-portfolio-summary ──→ Slack #ppc-updates
  9:30 AM  ─── keyword-rank-optimizer ─→ Slack #ppc-updates
  10:00 AM ─── ppc-bid-recommender ────→ Slack #ppc-updates (REPORT ONLY)
  10:30 AM ─── ppc-search-term-harvester → Slack #ppc-updates (REPORT ONLY)

THURSDAY
  8:00 AM  ─── competitor-price-serp-tracker → Slack #competitor-watch

FRIDAY
  9:00 AM  ─── ppc-portfolio-summary ──→ Slack #ppc-updates
  10:00 AM ─── ppc-bid-recommender ────→ Slack #ppc-updates (REPORT ONLY)
  10:30 AM ─── ppc-search-term-harvester → Slack #ppc-updates (REPORT ONLY)

MONTH-END
  10:00 AM ─── ppc-monthly-review ─────→ Slack #ppc-updates + Notion "PPC Monthly" DB
```

### What you do when you arrive at work

1. Open Slack → morning reports are already there
2. Review any bid/negative recommendations from Tue/Fri runs
3. If recommendations look good → open Claude Code locally → approve and execute
4. Run any manual skills you need (listing work, deep dives, etc.)

### How approval works (no VPS needed)

```
GitHub Actions runs ppc-bid-recommender at 10:00 AM Tuesday
  → Generates bid change recommendations
  → Posts summary to Slack: "12 bid changes recommended, est. -$3.50/day spend"
  → Saves detailed recommendations to outputs/research/ppc-agent/pending/

You see the Slack message at 10:30 AM
  → Open Claude Code on your laptop
  → "Apply the pending bid changes from this morning's run"
  → Claude reads the pending file, executes via Ads API
  → Updates portfolio trackers
```

OR: Configure the skill to auto-execute with guardrails (max 25% bid change, max $50 spend change, weekend freeze). Then it runs fully headless on the schedule.

---

## 4. GitHub Actions Setup

### What goes in the repo

```
.github/
└── workflows/
    ├── daily-market-intel.yml      # Daily 6:00 AM UTC
    ├── daily-ppc-health.yml        # Daily 6:30 AM UTC
    ├── weekly-ppc-analysis.yml     # Monday 8:00 AM UTC
    ├── tuesday-ppc-suite.yml       # Tuesday: tacos + portfolio + rank + bids + harvest
    ├── thursday-competitors.yml    # Thursday 8:00 AM UTC
    ├── friday-ppc-suite.yml        # Friday: portfolio + bids + harvest
    └── monthly-ppc-review.yml      # Last day of month
```

### Example workflow file

```yaml
name: Daily Market Intel
on:
  schedule:
    - cron: '0 6 * * *'    # 6:00 AM UTC daily
  workflow_dispatch:         # Manual "Run" button in GitHub UI

jobs:
  run-market-intel:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install MCP dependencies
        run: pip install httpx mcp fastmcp

      - uses: anthropics/claude-code@v1
        with:
          prompt: |
            Run the daily-market-intel skill.
            After completing, use the notification-hub to post results
            to Slack #claude-morning-brief.
            Upload the full report to Notion "Market Intel" database.
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          APIFY_API_TOKEN: ${{ secrets.APIFY_API_TOKEN }}
          DATADIVE_API_KEY: ${{ secrets.DATADIVE_API_KEY }}
          SP_API_CLIENT_ID: ${{ secrets.SP_API_CLIENT_ID }}
          SP_API_CLIENT_SECRET: ${{ secrets.SP_API_CLIENT_SECRET }}
          SP_API_REFRESH_TOKEN: ${{ secrets.SP_API_REFRESH_TOKEN }}
          SP_API_SELLER_ID: ${{ secrets.SP_API_SELLER_ID }}
          SP_API_MARKETPLACE_US: ${{ secrets.SP_API_MARKETPLACE_US }}
          SELLERBOARD_SALES_DETAILED_7D: ${{ secrets.SELLERBOARD_SALES_DETAILED_7D }}
          SLACK_WORKSPACE_1_BOT_TOKEN: ${{ secrets.SLACK_WORKSPACE_1_BOT_TOKEN }}
          SLACK_WORKSPACE_1_TEAM_ID: ${{ secrets.SLACK_WORKSPACE_1_TEAM_ID }}
          NOTION_API_KEY: ${{ secrets.NOTION_API_KEY }}

      - name: Commit outputs
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add outputs/ || true
          git diff --staged --quiet || git commit -m "Daily market intel $(date +%Y-%m-%d)"
          git push || true
```

### GitHub Secrets to configure

All 71 env vars from your `.env` file need to be added as GitHub repository secrets:
- Settings → Secrets and variables → Actions → New repository secret
- One-time setup, ~15 minutes
- More secure than .env on a VPS (encrypted, never exposed in logs)

### Free tier math

| Skill | Runs/Month | Minutes/Run | Total Min |
|---|---|---|---|
| daily-market-intel | 30 | 10 | 300 |
| ppc-daily-health | 30 | 3 | 90 |
| weekly-ppc-analysis | 4 | 7 | 28 |
| ppc-portfolio-summary | 8 | 4 | 32 |
| ppc-tacos-optimizer | 4 | 5 | 20 |
| keyword-rank-optimizer | 4 | 6 | 24 |
| competitor-price-serp-tracker | 4 | 10 | 40 |
| ppc-bid-recommender | 8 | 5 | 40 |
| ppc-search-term-harvester | 8 | 8 | 64 |
| ppc-monthly-review | 1 | 10 | 10 |
| **Total** | | | **~648 min** |

Free tier: 2,000 min/month. You're using ~650. **Plenty of headroom** for growth or manual triggers.

---

## 5. Claude Desktop Scheduled Tasks (For Work Hours)

While GitHub Actions handles 24/7 automation, Claude Desktop's native scheduling handles "while you're working" tasks:

| Task | Frequency | What It Does |
|---|---|---|
| PPC agent check-in | Hourly during work | Quick scan of portfolio state, surface anything urgent |
| Approval file check | Every 30 min | Check if pending bid/negative recommendations need attention |

**Setup:** In Claude Desktop app → Schedule → + New task → set frequency and prompt.

**Limitations to know:**
- Computer must be on and app running
- Recurring tasks expire after 3 days (need to recreate)
- Max 50 tasks
- Not for 24/7 automation — that's GitHub Actions' job

**Best used for:** monitoring and reminders during your workday, not as the primary automation engine.

---

## 6. Output Delivery

### Slack (automated notifications)

Every skill run posts to Slack via the notification-hub skill:

| Channel | Content | Frequency |
|---|---|---|
| `#claude-morning-brief` | Market intel summary + stock alerts | Daily |
| `#claude-ppc-updates` | PPC health, bid recs, search terms, weekly analysis | Daily/Weekly |
| `#claude-competitor-watch` | Price/BSR/SERP changes | Weekly |
| `#claude-alerts` | Anomalies, OOS warnings, budget alerts | As detected |

### Notion (browsable reports hub)

Each skill uploads full reports to Notion databases:

| Notion Database | Skill Source | Key Columns |
|---|---|---|
| Market Intel Reports | daily-market-intel | Date, BSR summary, alerts, top movers |
| PPC Weekly Reports | weekly-ppc-analysis | Week, TACoS, ACoS, campaigns, trajectories |
| PPC Health Log | ppc-daily-health | Date, portfolio statuses, anomalies |
| PPC Changes Log | ppc-bid-recommender + harvester | Date, changes, before/after, reasoning |
| Competitor Tracker | competitor-price-serp-tracker | Date, price changes, BSR shifts, SERP moves |
| Listing Audits | listing-optimizer | Date, ASIN, score, recommendations |

### Git (version-controlled outputs)

GitHub Actions commits output files back to the repo after each run. This gives you:
- Full history of every report generated
- Ability to compare any two dates
- Snapshots available for monthly review skill to aggregate

---

## 7. PPC Agent — Already Built, Just Needs Scheduling

The PPC agent and all its sub-skills are already connected and working. The Amazon Ads API MCP server is already registered in `.mcp.json` with all 29 tools operational.

**What's already there:**
- `ppc-agent` orchestrator → routes to 10 sub-skills based on cadence tracking
- `ppc-bid-recommender` → generates and can auto-apply bid changes
- `ppc-search-term-harvester` → classifies and can auto-negate/promote terms
- `ppc-campaign-creator` → proposes campaigns, creates in PAUSED state
- `ppc-portfolio-action-plan` → deep dive with per-action execution
- Full state tracking in `outputs/research/ppc-agent/state/` (agent-state.json + per-portfolio JSONs)

**What this plan adds:** Scheduling these skills to run automatically via GitHub Actions, with the approval pattern for execution-capable skills.

**Safety guardrails already in the skills:**
- Portfolio trackers log every change
- Change caps per run
- LESSONS.md tracks known issues and repeat errors
- Dedup protection (won't re-apply actions already taken)

---

## 8. Billing

### You're already on API billing

Your `.env` has `ANTHROPIC_API_KEY`. Every Claude Code session is billed per token. GitHub Actions uses the same key — no new plan needed.

| Plan | What It Is | Relevant? |
|---|---|---|
| Claude.ai Pro ($20/mo) | Browser chat | No — can't run headlessly |
| Claude.ai Max ($100/mo) | Browser + Claude Code interactive | No — can't authenticate on GitHub runner |
| API key (what you have) | Pay per token, programmatic use | **Yes — this is what GitHub Actions uses** |

### Monthly cost estimate

| Item | Cost |
|---|---|
| GitHub Actions | $0 (free tier) |
| Claude API — daily skills (market intel + PPC health × 30 days) | ~$15–20/mo |
| Claude API — weekly skills (PPC analysis + tacos + portfolio + rank + bids + harvest × 4-8) | ~$10–15/mo |
| Claude API — monthly skills | ~$2/mo |
| Claude API — competitor tracker (4×/month) | ~$3/mo |
| **Total new monthly cost** | **~$30–40/mo** |

This is just the API cost. No VPS, no n8n, no infrastructure fees.

**Set a budget cap** in Anthropic console → Billing → Usage limits. Start at $100/month.

---

## 9. Risks and Downsides

### GitHub Actions limitations
- **UTC timezone only** for cron — adjust schedules accordingly (UTC offset from your timezone)
- **Ephemeral runners** — no persistent filesystem between runs (outputs committed to git)
- **No real-time Slack interaction** — workers can't trigger skills from Slack (that needs VPS + n8n later)
- **Workflow_dispatch** for manual triggers — but requires GitHub access, not Slack-friendly
- **Rate limits** — GitHub cron can be delayed by up to 15 minutes during peak times

### Headless Claude Code
- Skills that ask "should I proceed?" will hang — need to run in report-only mode
- Partial failures produce no output — need error handling in workflows
- Each run is stateless — reads context from files, no memory of previous session

### Silent failures
If a skill fails, it produces no Slack message. Add failure notifications to each workflow:
```yaml
- name: Alert on failure
  if: failure()
  run: curl -X POST "$SLACK_WEBHOOK" -d '{"text":"⚠️ daily-market-intel FAILED"}'
```

### Cost unpredictability
A workflow that retries on failure could run up costs. Mitigation:
- Set `timeout-minutes` on every job
- Anthropic budget cap
- Monitor GitHub Actions usage in Settings → Billing

### Git repo growth
Output files committed each day will grow the repo. ~5-10MB/day = ~150-300MB/month. Manageable for months, but consider periodic cleanup or moving historical outputs to a separate branch.

---

## 10. Build Order

### Week 1: Prove the pipeline
1. Add `.github/workflows/daily-market-intel.yml` to the repo
2. Add all API credentials as GitHub Secrets (~15 min)
3. Test with `workflow_dispatch` (manual trigger) — verify end-to-end:
   - Claude Code runs on GitHub runner ✓
   - MCP servers install and work ✓
   - Skill executes successfully ✓
   - Posts to Slack ✓
   - Commits output to repo ✓
4. Enable the cron schedule — let it run for 3 days to verify reliability

### Week 2: Daily automation
5. Add `daily-ppc-health.yml` — second daily skill
6. Add failure alerting to both workflows
7. Verify output files are committing correctly

### Week 3: Weekly PPC suite
8. Add `weekly-ppc-analysis.yml` (Monday)
9. Add `tuesday-ppc-suite.yml` (tacos + portfolio + rank optimizer)
10. Add `friday-ppc-suite.yml` (portfolio + bid recommender + harvester in report mode)

### Week 4: Polish
11. Add `thursday-competitors.yml`
12. Add `monthly-ppc-review.yml`
13. Set up Notion databases for output hub
14. Add Notion upload steps to each workflow
15. Configure bid-recommender and harvester auto-execute guardrails (if comfortable)

### Later (when needed)
- VPS + n8n for worker Slack interaction
- Claude.ai Projects for worker conversations
- Daily email digest
- Asana task triggers

---

## 11. What Changes in This Repo

### New: `.github/workflows/` (7 YAML files)
```
.github/workflows/
├── daily-market-intel.yml
├── daily-ppc-health.yml
├── weekly-ppc-analysis.yml
├── tuesday-ppc-suite.yml
├── thursday-competitors.yml
├── friday-ppc-suite.yml
└── monthly-ppc-review.yml
```

### New: `automation/scripts/` (helper scripts for GitHub runners)
```
automation/
├── scripts/
│   ├── install-deps.sh       # pip install all MCP dependencies
│   └── setup-env.sh          # Any runner-specific env configuration
└── README.md
```

### Existing files — no changes needed
- `.claude/skills/` — all skills stay as-is
- `mcp-servers/` — all MCP servers stay as-is
- `.mcp.json` — already has all servers registered
- `context/` — context files stay as-is
- `outputs/` — will grow with automated commits

---

## 12. When to Add VPS + n8n (Phase 2)

You don't need it now. Add it when:
- Workers need to trigger skills from Slack (dynamic @claude mode)
- You want real-time responses (GitHub Actions has ~30s startup overhead)
- You need complex conditional routing (if X then run Y)
- Email digest becomes a priority
- Worker team grows beyond 3-5 people

**Phase 2 adds:**
- Hetzner VPS ($8-12/mo) running n8n
- Slack command router (`#team-claude` → n8n → Claude Code)
- Daily email digest via n8n Email node
- GitHub Actions continues handling scheduled skills (VPS handles only interactive)

---

## Critical Files

| File | Why It Matters |
|---|---|
| [.claude/skills/daily-market-intel/SKILL.md](.claude/skills/daily-market-intel/SKILL.md) | First skill to automate — fully headless |
| [.claude/skills/ppc-agent/SKILL.md](.claude/skills/ppc-agent/SKILL.md) | Orchestrator — routes all PPC sub-skills |
| [.claude/skills/notification-hub/SKILL.md](.claude/skills/notification-hub/SKILL.md) | Posts results to Slack after each run |
| [mcp-servers/amazon-ads-api/server.py](mcp-servers/amazon-ads-api/server.py) | Already connected, 29 tools for PPC automation |
| [mcp-servers/slack/server.py](mcp-servers/slack/server.py) | Posts to 5 Slack channels |
| [.mcp.json](.mcp.json) | All 8 MCP servers already registered |
| [.env](.env) | All 71 credentials — mirror to GitHub Secrets |
| [outputs/research/ppc-agent/state/agent-state.json](outputs/research/ppc-agent/state/agent-state.json) | PPC agent state — tracks cadence, pending actions |
| [context/business.md](context/business.md) | Business context loaded by all skills |

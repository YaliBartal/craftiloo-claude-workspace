# Config.yaml + n8n Workflow Changes — Detailed Plan

**Created:** 2026-03-13
**Purpose:** Transition from the current Tuesday/Friday skill chains to the autonomous three-layer architecture.

---

## What Changes

### Current Schedule (being replaced)

```
DAILY:
  8:00  daily-market-intel
  8:30  ppc-daily-health

MONDAY:
  9:00  weekly-ppc-analysis

TUESDAY (chain of 5):
  9:00  ppc-tacos-optimizer
  9:30  ppc-portfolio-summary
  10:00 keyword-rank-optimizer
  10:30 ppc-bid-recommender
  11:00 ppc-search-term-harvester

FRIDAY (chain of 3):
  9:00  ppc-portfolio-summary
  10:00 ppc-bid-recommender
  10:30 ppc-search-term-harvester

THURSDAY:
  9:00  competitor-price-serp-tracker

SUNDAY:
  9:00  brand-analytics-weekly

MONTHLY:
  10:00 ppc-monthly-review
```

### New Schedule

```
DAILY (unchanged):
  8:00  daily-market-intel
  8:30  ppc-daily-health

MONDAY (data pipeline — replaces Tuesday chain):
  9:00  weekly-ppc-analysis                       ← existing, unchanged
  9:45  ppc-portfolio-summary AUTONOMOUS          ← NEW prompt
  10:15 ppc-search-term-harvester AUTONOMOUS      ← NEW prompt
  10:45 ppc-bid-recommender AUTONOMOUS            ← NEW prompt
  11:15 keyword-rank-optimizer AUTONOMOUS          ← NEW prompt (weekly, not biweekly*)
  11:45 ppc-tacos-optimizer AUTONOMOUS             ← NEW prompt (weekly, not biweekly*)

TUESDAY (agent session — NEW):
  9:00  ppc-agent AUTONOMOUS Tuesday              ← NEW skill entry

THURSDAY (unchanged):
  9:00  competitor-price-serp-tracker

FRIDAY (agent session — replaces Friday chain):
  9:00  ppc-agent AUTONOMOUS Friday               ← NEW skill entry

SUNDAY (unchanged):
  9:00  brand-analytics-weekly

MONTHLY (agent session — replaces standalone monthly):
  10:00 ppc-agent AUTONOMOUS Monthly              ← replaces ppc-monthly-review
```

*Originally planned as biweekly. Running weekly is simpler (no alternation logic needed) and costs ~$2-3/month extra. The agent has fresh data every week. Can switch to biweekly later if cost matters.

### What goes away
- Tuesday chain workflow (5 skills chained) → replaced by Monday pipeline
- Friday chain workflow (3 skills chained) → replaced by Friday agent
- Individual non-AUTONOMOUS skill entries for: ppc-tacos-optimizer, ppc-portfolio-summary, keyword-rank-optimizer, ppc-bid-recommender, ppc-search-term-harvester at their current schedules
- Standalone ppc-monthly-review → replaced by monthly agent session

### What stays unchanged
- daily-market-intel (8:00 daily)
- ppc-daily-health (8:30 daily)
- weekly-ppc-analysis (9:00 Monday)
- competitor-price-serp-tracker (9:00 Thursday)
- brand-analytics-weekly (9:00 Sunday)

---

## New config.yaml

```yaml
# Craftiloo Skill Runner Configuration
# Central config for all automated skill runs on the mini PC.

defaults:
  workspace: /home/yali/workspace
  log_dir: /var/log/claude
  model: claude-sonnet-4-6
  max_turns: 30
  timeout_minutes: 25
  git_pull: true
  git_commit: true
  git_push: true
  git_add_paths:
    - outputs/
    - .claude/skills/
  commit_prefix: "auto"
  env_file: /home/yali/workspace/.env
  lockfile: /tmp/claude-skill.lock
  min_gap_minutes: 2
  allowed_tools:
    - "Read"
    - "Write"
    - "Edit"
    - "Glob"
    - "Grep"
    - "Bash(python3*)"
    - "Bash(pip3*)"
    - "Bash(git*)"
    - "Bash(ls*)"
    - "Bash(cat*)"
    - "Bash(mkdir*)"
    - "Bash(date*)"
    - "Bash(cd*)"
    - "Bash(cp*)"
    - "Bash(head*)"
    - "Bash(tail*)"
    - "Bash(wc*)"
    - "Bash(sort*)"
    - "Bash(curl*)"
    - "mcp__amazon-ads-api__*"
    - "mcp__amazon-sp-api__*"
    - "mcp__sellerboard__*"
    - "mcp__slack__*"
    - "mcp__datadive__*"
    - "mcp__notion__*"
    - "mcp__apify__*"
    - "mcp__asana__*"
  prompt_suffix: |
    After completing the skill, use the notification-hub skill to post
    the results summary to Slack.
    If the notification-hub fails, that's OK — do not retry notifications.
    EFFICIENCY RULES:
    - Keep Slack messages under 2000 chars.
    - Do NOT post to #claude-alerts. The automation handles failure alerts.
    - Target: complete in the fewest turns possible.

# ---------------------------------------------------------------------------
# Skill definitions
# ---------------------------------------------------------------------------

skills:

  # === DAILY (every day) ===

  daily-market-intel:
    timeout_minutes: 25
    max_turns: 30
    slack_channel: "#claude-morning-brief"
    schedule: "Daily 8:00 AM IST"

  ppc-daily-health:
    timeout_minutes: 20
    max_turns: 25
    prompt: |
      Run the ppc-daily-health skill.
      EFFICIENCY RULES:
      - Do NOT update individual portfolio tracker JSON files. Only update agent-state.json.
    slack_channel: "#claude-ppc-updates"
    schedule: "Daily 8:30 AM IST"

  # === MONDAY (data pipeline for autonomous agent) ===

  weekly-ppc-analysis:
    timeout_minutes: 30
    max_turns: 80
    slack_channel: "#claude-ppc-updates"
    schedule: "Monday 9:00 AM IST"

  ppc-portfolio-summary-auto:
    timeout_minutes: 20
    max_turns: 30
    prompt: |
      Run the ppc-portfolio-summary skill in AUTONOMOUS mode.
      Run on ALL 17 portfolios. Save structured output.
      Do NOT post to Slack. Do NOT present findings to user.
      Save all output files and update LESSONS.md, then exit.
    prompt_suffix: ""
    slack_channel: "#claude-ppc-updates"
    schedule: "Monday 9:45 AM IST"

  ppc-search-term-harvester-auto:
    timeout_minutes: 25
    max_turns: 35
    prompt: |
      Run the ppc-search-term-harvester skill in AUTONOMOUS mode.
      Run on ALL portfolios at FULL depth. Save structured output.
      STOP before Step 8 — do NOT apply any negations or promotions.
      Do NOT post to Slack. Save all output files and update LESSONS.md, then exit.
    prompt_suffix: ""
    slack_channel: "#claude-ppc-updates"
    schedule: "Monday 10:15 AM IST"

  ppc-bid-recommender-auto:
    timeout_minutes: 20
    max_turns: 30
    prompt: |
      Run the ppc-bid-recommender skill in AUTONOMOUS mode.
      Run on ALL campaigns, ALL portfolios. Save structured output.
      STOP before Step 7 — do NOT apply any bid changes.
      Do NOT post to Slack. Save all output files and update LESSONS.md, then exit.
    prompt_suffix: ""
    slack_channel: "#claude-ppc-updates"
    schedule: "Monday 10:45 AM IST"

  keyword-rank-optimizer-auto:
    timeout_minutes: 25
    max_turns: 35
    prompt: |
      Run the keyword-rank-optimizer skill in AUTONOMOUS mode.
      Run account-wide on ALL portfolios. Save structured output.
      STOP before Step 11 — do NOT present routing options.
      Skip Brand Analytics enrichment.
      Do NOT post to Slack. Save all output files and update LESSONS.md, then exit.
    prompt_suffix: ""
    slack_channel: "#claude-ppc-updates"
    schedule: "Monday 11:15 AM IST"

  ppc-tacos-optimizer-auto:
    timeout_minutes: 20
    max_turns: 30
    prompt: |
      Run the ppc-tacos-optimizer skill in AUTONOMOUS mode.
      Run on ALL portfolios. Save structured output.
      Do NOT post to Slack. Save all output files and update LESSONS.md, then exit.
    prompt_suffix: ""
    slack_channel: "#claude-ppc-updates"
    schedule: "Monday 11:45 AM IST"

  # === TUESDAY (autonomous agent session) ===

  ppc-agent-tuesday:
    timeout_minutes: 55
    max_turns: 50
    prompt: |
      Read .claude/skills/ppc-agent/SKILL.md and run in AUTONOMOUS Tuesday mode.
      REPORT ONLY — no API writes, ever.
      Read all Monday pipeline outputs. Do NOT re-run sub-skills.
      Validate previous changes. Cross-reference findings across skills.
      Produce full brief + action items JSON.
      Save to disk FIRST, then push to Notion.
      Post SHORT Slack notification to #claude-ppc-updates with Notion link.
    prompt_suffix: ""
    slack_channel: "#claude-ppc-updates"
    schedule: "Tuesday 9:00 AM IST"

  # === THURSDAY ===

  competitor-price-serp-tracker:
    timeout_minutes: 35
    max_turns: 40
    slack_channel: "#claude-competitor-watch"
    schedule: "Thursday 9:00 AM IST"

  # === FRIDAY (autonomous agent session) ===

  ppc-agent-friday:
    timeout_minutes: 40
    max_turns: 35
    prompt: |
      Read .claude/skills/ppc-agent/SKILL.md and run in AUTONOMOUS Friday mode.
      REPORT ONLY — no API writes, ever.
      Read daily health outputs since Tuesday.
      Validate any actions applied mid-week.
      Check for new anomalies. Produce shorter brief + action items JSON.
      Save to disk FIRST, then push to Notion.
      Post SHORT Slack notification to #claude-ppc-updates.
    prompt_suffix: ""
    slack_channel: "#claude-ppc-updates"
    schedule: "Friday 9:00 AM IST"

  # === SUNDAY ===

  brand-analytics-weekly:
    timeout_minutes: 30
    max_turns: 40
    slack_channel: "#claude-product-updates"
    schedule: "Sunday 9:00 AM IST"

  # === MONTHLY (1st of month) ===

  ppc-agent-monthly:
    timeout_minutes: 70
    max_turns: 60
    prompt: |
      Read .claude/skills/ppc-agent/SKILL.md and run in AUTONOMOUS Monthly mode.
      REPORT ONLY — no API writes, ever.
      Pull fresh 30d data for month-over-month comparison.
      Full month strategic review: budget reallocation, stage transitions.
      Produce comprehensive brief + action items JSON.
      Save to disk FIRST, then push to Notion.
      Post Slack notification to #claude-ppc-updates.
    prompt_suffix: ""
    git_add_paths:
      - outputs/
      - context/business.md
      - .claude/skills/
    slack_channel: "#claude-ppc-updates"
    schedule: "1st of month 10:00 AM IST"

  # === LEGACY (kept for interactive/fallback use, NOT scheduled) ===
  # These are the original non-AUTONOMOUS versions.
  # They can still be invoked manually: python3 skill-runner.py ppc-bid-recommender
  # They are NOT in any n8n schedule.

  ppc-bid-recommender:
    timeout_minutes: 25
    max_turns: 30
    prompt: |
      Run the ppc-bid-recommender skill in REPORT ONLY mode.
      Do NOT apply any bid changes. Generate recommendations only.
    slack_channel: "#claude-ppc-updates"
    # NO schedule — manual/interactive only

  ppc-search-term-harvester:
    timeout_minutes: 25
    max_turns: 30
    prompt: |
      Run the ppc-search-term-harvester skill in REPORT ONLY mode.
      Do NOT apply any negations or promotions. Generate recommendations only.
    slack_channel: "#claude-ppc-updates"
    # NO schedule — manual/interactive only

  ppc-portfolio-summary:
    timeout_minutes: 25
    max_turns: 30
    slack_channel: "#claude-ppc-updates"
    # NO schedule — manual/interactive only

  keyword-rank-optimizer:
    timeout_minutes: 25
    max_turns: 30
    slack_channel: "#claude-ppc-updates"
    # NO schedule — manual/interactive only

  ppc-tacos-optimizer:
    timeout_minutes: 25
    max_turns: 30
    slack_channel: "#claude-ppc-updates"
    # NO schedule — manual/interactive only

  ppc-monthly-review:
    timeout_minutes: 35
    max_turns: 50
    slack_channel: "#claude-ppc-updates"
    # NO schedule — replaced by ppc-agent-monthly
```

---

## n8n Workflow Changes

### Current Workflows → New Workflows

| Current | Action | New |
|---------|--------|-----|
| `master-scheduler.json` | **MODIFY** — update triggers and targets | See below |
| `tuesday-chain.json` | **REPLACE** with `monday-pipeline.json` | 5 sequential AUTONOMOUS skills |
| `friday-chain.json` | **REPLACE** with single agent call | Inline in master-scheduler |
| `git-sync.json` | **KEEP** unchanged | — |

### New Master Scheduler

The master scheduler triggers everything via HTTP POST to `skill-api.py` at port 5680.

```
Triggers:

Daily 5:30 UTC (8:00 IST):    POST /run {"skill": "daily-market-intel"}
Daily 6:00 UTC (8:30 IST):    POST /run {"skill": "ppc-daily-health"}
Monday 6:30 UTC (9:00 IST):   POST /run {"skill": "weekly-ppc-analysis"}
Monday 7:15 UTC (9:45 IST):   Execute monday-pipeline workflow (chains 5 skills)
Tuesday 6:30 UTC (9:00 IST):  POST /run {"skill": "ppc-agent-tuesday"}
Thursday 6:30 UTC (9:00 IST): POST /run {"skill": "competitor-price-serp-tracker"}
Friday 6:30 UTC (9:00 IST):   POST /run {"skill": "ppc-agent-friday"}
Sunday 6:30 UTC (9:00 IST):   POST /run {"skill": "brand-analytics-weekly"}
1st of month 7:30 UTC (10:00 IST): POST /run {"skill": "ppc-agent-monthly"}
```

Note: UTC offsets assume IST = UTC+2:30 (Israel Standard Time is actually UTC+2, daylight saving UTC+3). Verify the current offset and adjust. n8n's timezone setting should handle this if set to `Asia/Jerusalem`.

### New Monday Pipeline Workflow (`monday-pipeline.json`)

Replaces `tuesday-chain.json`. Sequential chain of 5 AUTONOMOUS skills.

```
Structure:
  Trigger (executeWorkflowTrigger — called from master-scheduler Monday 9:45 IST)
  ↓
  1. Execute: skill-runner.py ppc-portfolio-summary-auto (timeout: 1200s)
  ↓ Check exit code → alert on failure → continue either way
  ↓ Wait 2 min (gap between skills)
  ↓
  2. Execute: skill-runner.py ppc-search-term-harvester-auto (timeout: 1500s)
  ↓ Check exit code → alert on failure → continue
  ↓ Wait 2 min
  ↓
  3. Execute: skill-runner.py ppc-bid-recommender-auto (timeout: 1200s)
  ↓ Check exit code → alert on failure → continue
  ↓ Wait 2 min
  ↓
  4. Execute: skill-runner.py keyword-rank-optimizer-auto (timeout: 1500s)
  ↓ Check exit code → alert on failure → continue
  ↓ Wait 2 min
  ↓
  5. Execute: skill-runner.py ppc-tacos-optimizer-auto (timeout: 1200s)
  ↓ Check exit code → alert on failure
  ↓
  Final: POST to Slack summary
    "Monday pipeline complete. {N}/5 skills succeeded. Failures: {list}"
```

Each step follows the same pattern as the current tuesday-chain.json:
- `executeCommand` node → `if` exit code check → `alert` Slack on failure → `wait` 2min → next skill
- On failure: alert to #claude-alerts but CONTINUE to next skill (failure isolation)

### Tuesday/Friday Agent Sessions

These are simple single-skill calls in the master scheduler (no chain needed):

```
Tuesday 9:00 IST:
  POST http://127.0.0.1:5680/run
  {"skill": "ppc-agent-tuesday"}
  timeout: 3600000 (60 min)

  → On success: done (agent posts its own Slack notification)
  → On failure: POST to #claude-alerts: "PPC Agent Tuesday session FAILED"
```

```
Friday 9:00 IST:
  POST http://127.0.0.1:5680/run
  {"skill": "ppc-agent-friday"}
  timeout: 2400000 (40 min)

  → On success: done
  → On failure: POST to #claude-alerts: "PPC Agent Friday session FAILED"
```

### Monthly Agent Session

```
1st of month 10:00 IST:
  POST http://127.0.0.1:5680/run
  {"skill": "ppc-agent-monthly"}
  timeout: 4200000 (70 min)

  → On success: done
  → On failure: POST to #claude-alerts: "PPC Agent Monthly session FAILED"
```

---

## skill-api.py Update

The new skill names need to be recognized by `skill-api.py`. Currently it reads from config.yaml, so the new entries should auto-register if the API reads the skill list dynamically. If it uses a hardcoded allowlist, add:

```
ppc-portfolio-summary-auto
ppc-search-term-harvester-auto
ppc-bid-recommender-auto
keyword-rank-optimizer-auto
ppc-tacos-optimizer-auto
ppc-agent-tuesday
ppc-agent-friday
ppc-agent-monthly
```

---

## Monitoring

### Built into n8n (failure alerts)

Every skill call in n8n already checks exit codes and posts to #claude-alerts on failure. This is unchanged.

### Additional monitoring (nice to have, implement later)

| Check | When | How | Alert |
|-------|------|-----|-------|
| Monday pipeline completion | Monday 12:30 IST | n8n cron → check if all 5 autonomous JSONs exist for today's date | If <5 files: "Monday pipeline incomplete — {N}/5 skills ran" |
| Tuesday brief exists | Tuesday 10:30 IST | n8n cron → check if `sessions/{date}-tuesday-brief.md` exists | If missing: "Tuesday agent session may have failed" |
| Friday brief exists | Friday 10:30 IST | Same check for friday brief | If missing: "Friday agent session may have failed" |

These are implemented as simple n8n Schedule Trigger → Execute Command (`ls outputs/research/ppc-agent/sessions/*-tuesday-brief.md`) → If check → Slack alert.

---

## Rollout Plan

### Phase 1: Monday Pipeline First (Week 1)

1. Update config.yaml with the new entries
2. Create monday-pipeline.json n8n workflow
3. **Disable** the old tuesday-chain.json and friday-chain.json in n8n (don't delete — keep as fallback)
4. **Activate** the Monday pipeline
5. Verify Monday outputs exist Tuesday morning
6. Tuesday/Friday: run agent sessions MANUALLY (not automated yet)

### Phase 2: Automate Tuesday (Week 2)

7. Add ppc-agent-tuesday trigger to master-scheduler
8. Verify Tuesday brief quality
9. Test "apply items" workflow interactively
10. Friday: still manual

### Phase 3: Automate Everything (Week 3)

11. Add ppc-agent-friday trigger
12. Add ppc-agent-monthly trigger
13. Remove old tuesday-chain.json and friday-chain.json from n8n
14. Full autonomous cycle running

### Fallback

If anything breaks badly, the old non-AUTONOMOUS skill entries are still in config.yaml (marked as no-schedule). You can re-enable the old chains in n8n by reactivating the disabled workflows. Data keeps flowing through daily health regardless.

---

## DST Handling

Israel observes daylight saving time (IDT = UTC+3 in summer, IST = UTC+2 in winter). The transition dates vary yearly.

**Recommendation:** Set n8n's timezone to `Asia/Jerusalem`. Use cron expressions in local time. n8n handles the UTC conversion automatically. Do NOT hardcode UTC offsets in cron expressions.

If n8n timezone is already set correctly (check Settings → General → Timezone), no changes needed. All cron expressions use IST/IDT-relative times.

---

## Cost Estimate (Weekly)

| Component | Sessions/Week | Est. Tokens | Est. Cost |
|-----------|--------------|-------------|-----------|
| Daily health × 7 | 7 | ~105K | ~$3.50 |
| Daily market intel × 7 | 7 | ~140K | ~$4.50 |
| Weekly PPC analysis | 1 | ~80K | ~$3.00 |
| Monday pipeline (5 skills) | 5 | ~175K | ~$6.00 |
| Tuesday agent session | 1 | ~100K | ~$3.50 |
| Friday agent session | 1 | ~65K | ~$2.50 |
| Competitor tracker | 1 | ~50K | ~$2.00 |
| Brand analytics weekly | 1 | ~40K | ~$1.50 |
| **Weekly total** | **24** | **~755K** | **~$26.50** |
| **Monthly total** | | | **~$115** |

(Add ~$4 for monthly agent session. Interactive "apply items" sessions add ~$3-5/month depending on frequency.)

This compares to the current cost of ~$80-90/month, so the autonomous system adds roughly $25-30/month in exchange for significantly deeper analysis and the validation loop.

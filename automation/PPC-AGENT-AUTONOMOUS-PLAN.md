# PPC Agent Autonomous — Architecture & Implementation Plan

**Created:** 2026-03-13
**Goal:** Replace scheduled skill chains with an intelligent PPC agent that does real analysis, validates its own work, and produces data-backed briefs. Must be bulletproof enough to run without human PPC oversight.

---

## Architecture: Three-Layer Design

### Why Not a Single Session

A single 55-65 minute agent session that runs sub-skills sequentially will fail because:
1. **Context window bloat** — by sub-skill #4, earlier data is compressed/lost
2. **Time pressure causes shortcuts** — healthy portfolios get skipped
3. **Portfolio bias is structural** — agent focuses on RED portfolios, neglects GREEN
4. **Single point of failure** — crash at minute 40 = lost session

### The Three Layers

**Layer 1: Monday Data Pipeline (standalone skills, no agent intelligence)**

Mechanical, exhaustive data collection. Runs on ALL portfolios with equal depth. Each skill runs independently — if one fails, others continue.

```
Mon 7:30   weekly-ppc-analysis
           → Pulls 4 raw reports (campaigns 30d, search terms 14d, keywords, placements 7d)
           → Saves to outputs/research/ppc-weekly/snapshots/YYYY-MM-DD/

Mon 8:30   ppc-portfolio-summary — ALL 17 portfolios
           → Saves: portfolio-summaries/YYYY-MM-DD-autonomous-summary.json

Mon 9:30   ppc-search-term-harvester — ALL portfolios, FULL depth
           → Saves: search-terms/YYYY-MM-DD-autonomous-harvest.json

Mon 10:30  ppc-bid-recommender — ALL campaigns, ALL portfolios
           → Saves: bids/YYYY-MM-DD-autonomous-recommendations.json

Mon 11:30  (biweekly, odd weeks) keyword-rank-optimizer
           → Saves: rank-optimizer/YYYY-MM-DD-autonomous-analysis.json

Mon 11:30  (biweekly, even weeks) ppc-tacos-optimizer
           → Saves: tacos/YYYY-MM-DD-autonomous-analysis.json
```

**Layer 2: Tuesday Agent Session (reads data, thinks, outputs)**

The agent doesn't run sub-skills. It reads Monday's structured output and does the work that requires intelligence: validation, cross-referencing, synthesis, action item generation.

Session structure (~35-45 min):
1. Load all Monday outputs + daily health since last session + agent state
2. Validate previous changes (targeted fresh data pull for changed campaigns only)
3. Cross-reference findings across skills
4. Per-portfolio checklist assessment
5. Generate action items with evidence
6. Save brief to disk FIRST, then push to Notion
7. Post Slack notification
8. Update agent state

**Layer 3: Friday Validation + Check Session**

Lighter session (~25-30 min):
1. Load daily health since Tuesday + Tuesday's action items
2. Validate any actions applied mid-week
3. Anomaly scan — anything change significantly?
4. Shorter Notion brief
5. Update agent state

**Monthly Strategic Review (1st of month, ~60 min):**
- Full month comparison (current vs previous)
- Budget reallocation recommendations
- Stage transition assessments
- Quarterly trend analysis

---

## Key Design Decisions

### Coverage Guarantee
Monday pipeline treats all 17 portfolios equally. No portfolio gets skipped because "everything looks healthy." The agent decides depth of ANALYSIS, not depth of DATA COLLECTION.

### Disk-First Output
Every session saves to disk before pushing to Notion. If Notion fails, data isn't lost.

```
outputs/research/ppc-agent/sessions/
  YYYY-MM-DD-tuesday-brief.md        ← human-readable
  YYYY-MM-DD-tuesday-actions.json    ← machine-readable
  YYYY-MM-DD-friday-brief.md
  YYYY-MM-DD-friday-actions.json
```

### Machine-Readable Action Items
Every action item is saved as structured JSON alongside the human-readable brief. When user says "apply items 1 and 3," the agent reads the JSON — no markdown re-parsing.

### Failure Isolation
Each Monday skill runs independently. If bid recommender crashes, search term harvester still ran. Tuesday's agent notes which data is missing and works with what it has.

### Validation Loop
The single most valuable feature. For every action taken, the agent pulls fresh data 7+ days later and compares before vs after. This is what turns reports into learning.

---

## Agent State Schema

`outputs/research/ppc-agent/state/agent-state.json` additions:

```json
{
  "cadence_tracker": {
    "portfolio_summary": {"last_run": "2026-03-10", "next_due": "2026-03-17"},
    "search_term_harvester": {"last_run": "2026-03-10", "next_due": "2026-03-17"},
    "bid_recommender": {"last_run": "2026-03-10", "next_due": "2026-03-17"},
    "keyword_rank_optimizer": {"last_run": "2026-03-03", "next_due": "2026-03-17"},
    "tacos_optimizer": {"last_run": "2026-03-10", "next_due": "2026-03-24"}
  },
  "rotation_tracker": {
    "last_deep_scan": {
      "cross-stitch": "2026-03-10",
      "embroidery": "2026-03-07"
    },
    "scan_queue": ["knitting", "latch-hook", "sewing"],
    "max_days_between_scans": 14
  },
  "action_registry": [
    {
      "id": "ACT-2026-03-10-001",
      "created": "2026-03-10",
      "session": "2026-03-10-tuesday",
      "portfolio": "sewing",
      "type": "NEGATE_SEARCH_TERM",
      "description": "Negate 'sewing kit for adults'",
      "campaign_id": "123456",
      "status": "pending_approval",
      "evidence_file": "search-terms/2026-03-10-autonomous-harvest.json",
      "applied_date": null,
      "validated_date": null,
      "validation_result": null
    }
  ],
  "validation_queue": [
    {
      "action_id": "ACT-2026-03-03-002",
      "applied_date": "2026-03-05",
      "earliest_validation": "2026-03-12",
      "status": "ready_for_validation"
    }
  ],
  "session_log": [
    {
      "date": "2026-03-10",
      "type": "tuesday",
      "duration_min": 38,
      "skills_read": ["portfolio-summary", "search-term-harvester", "bid-recommender"],
      "action_items_created": 4,
      "validations_completed": 2,
      "notion_page_id": "abc123",
      "brief_file": "sessions/2026-03-10-tuesday-brief.md"
    }
  ]
}
```

## Action Items JSON Schema

```json
{
  "session_date": "2026-03-10",
  "session_type": "tuesday",
  "actions": [
    {
      "id": "ACT-2026-03-10-001",
      "priority": "P2",
      "type": "NEGATE_SEARCH_TERM",
      "portfolio": "sewing",
      "portfolio_id": "12345",
      "campaign_id": "67890",
      "campaign_name": "Sewing Kit - SPM MK Broad TOS",
      "description": "Negate 'sewing kit for adults'",
      "params": {
        "keyword_text": "sewing kit for adults",
        "match_type": "NEGATIVE_EXACT"
      },
      "evidence": {
        "period": "30d",
        "weeks": [
          {"week": "Feb 10-16", "impressions": 340, "clicks": 12, "spend": 8.40, "orders": 0}
        ],
        "total_spend": 28.00,
        "total_orders": 0
      },
      "expected_impact": "Save ~$7/week",
      "risk": "low",
      "confidence": "high",
      "status": "pending_approval"
    }
  ]
}
```

---

## Data Evidence Standards

| Recommendation Type | Minimum Evidence Required |
|---------------------|--------------------------|
| Negate search term | 30 days, 4-week breakdown, $0 or <2% CVR across full window |
| Reduce bid | 30 days performance + rank data + target CPC calculation |
| Increase bid | Rank trend (dropping) + impression share loss + budget utilization |
| Pause keyword | 30 days zero conversions + minimum 200 impressions |
| Pause campaign | 30 days performance + comparison to portfolio average |
| Budget change | 14 days utilization trend + impression share data |

---

## Per-Portfolio Checklist (Agent's Analytical Framework)

For each portfolio during synthesis:
1. **Budget utilization** — any campaign >80% or <10%?
2. **ACoS trend** — improving, stable, or worsening vs 2 weeks ago?
3. **Search term quality** — ratio of relevant vs irrelevant terms
4. **Rank trajectory** — any hero keyword declining?
5. **Organic share** — is PPC dependency increasing or decreasing?
6. **Campaign structure** — any new imbalances since last scan?
7. **Pending actions** — anything queued from previous sessions?
8. **Competitor signals** — new ASINs appearing in search terms?

---

## Graduated Autonomy Path

| Phase | When | Agent Does |
|-------|------|-----------|
| Phase 1 (now) | Weeks 1-8 | Analyze + recommend. Full evidence. Human approves. |
| Phase 2 | After 8+ weeks validated good judgment | Auto-execute LOW-RISK: negate obviously irrelevant terms (30d proof), reduce bids on ACoS >3x target. Posts what it did. |
| Phase 3 | After Phase 2 validated | Manages routine PPC. Human sets strategy. Agent handles tactical. |

Phase 2 unlocks when validation_history shows >80% WORKED rate over 8+ weeks.

---

## Monitoring & Alerting

- If no Slack notification within 90 min of scheduled session start → alert #claude-alerts
- If session brief file doesn't exist on disk → alert
- If session ran but 0 action items AND 0 validations → warning
- Monday pipeline: if any skill fails, alert immediately (next skills still run)

---

## Notion Structure

Parent page: "PPC Agent Sessions"
- Each session = child page with properties: Date, Type, Health Summary, Action Count
- Page content follows the brief template (executive summary → dashboard → validations → action items → reasoning log)

---

## Implementation Timeline & Progress

| Day | What | Status |
|-----|------|--------|
| 1 | Add AUTONOMOUS mode to all 5 data collection skills | DONE (Mar 13) |
| 2 | Expand agent-state.json schema + action items JSON + sessions folder | DONE (Mar 13) |
| 3-4 | Write PPC Agent AUTONOMOUS mode (Tuesday + Friday + Monthly) | DONE (Mar 13) |
| 5 | Structural validation (all paths, schemas, routing) | DONE (Mar 13) — all checks passed |
| 6 | Config.yaml + n8n plan (see CONFIG-AND-N8N-PLAN.md) | PLANNED (Mar 13) — awaiting approval |
| 7 | Go-live: automated Monday + manual Tue/Fri (week 1) | TODO |
| 8 | Go-live: automated Tue/Fri (week 2-3) | TODO |

### What Was Built (Day 1-2)

**5 skills modified** with AUTONOMOUS mode sections:
- `ppc-portfolio-summary/SKILL.md` — autonomous summary JSON output
- `ppc-search-term-harvester/SKILL.md` — stops before approval gate, saves harvest JSON
- `ppc-bid-recommender/SKILL.md` — stops before approval gate, saves recs JSON
- `keyword-rank-optimizer/SKILL.md` — always account-wide, saves analysis JSON
- `ppc-tacos-optimizer/SKILL.md` — saves analysis JSON

**Agent state expanded:**
- Added `autonomous` object with cadence_tracker, rotation_tracker, session_log
- Trim rules: 20 sessions max, 60 days for action registry

**Sessions infrastructure created:**
- `outputs/research/ppc-agent/sessions/` folder with README.md
- `outputs/research/ppc-agent/sessions/action-schema.json` — full schema reference
- `outputs/research/ppc-agent/sessions/archive/` subfolder for trimmed history

---

## Config.yaml

```yaml
# Monday Data Pipeline
monday-data-pipeline:
  - skill: ppc-portfolio-summary
    time: "08:30"
    timeout_minutes: 25
    prompt: "AUTONOMOUS mode. ALL 17 portfolios. Save structured output."
  - skill: ppc-search-term-harvester
    time: "09:30"
    timeout_minutes: 30
    prompt: "AUTONOMOUS mode. ALL portfolios, FULL depth. Save structured output."
  - skill: ppc-bid-recommender
    time: "10:30"
    timeout_minutes: 25
    prompt: "AUTONOMOUS mode. ALL campaigns, ALL portfolios. Save structured output."
  - skill: keyword-rank-optimizer
    time: "11:30"
    frequency: biweekly-odd
    timeout_minutes: 20
    prompt: "AUTONOMOUS mode. Full analysis. Save structured output."
  - skill: ppc-tacos-optimizer
    time: "11:30"
    frequency: biweekly-even
    timeout_minutes: 20
    prompt: "AUTONOMOUS mode. Full analysis. Save structured output."

# Agent Sessions
ppc-agent-tuesday:
  time: "Tuesday 09:00"
  timeout_minutes: 55
  max_turns: 50
  prompt: |
    AUTONOMOUS mode — Tuesday full session.
    REPORT ONLY — no API writes.
    Read all Monday pipeline outputs. Do NOT re-run sub-skills.
    Validate previous changes. Cross-reference findings.
    Produce Notion brief + action items JSON.
    Save to disk FIRST, then push to Notion.
    Post short Slack notification.

ppc-agent-friday:
  time: "Friday 09:00"
  timeout_minutes: 40
  max_turns: 35
  prompt: |
    AUTONOMOUS mode — Friday check session.
    REPORT ONLY — no API writes.
    Read daily health outputs since Tuesday.
    Validate any actions applied mid-week.
    Produce shorter Notion brief.

ppc-agent-monthly:
  time: "1st of month 10:00"
  timeout_minutes: 70
  max_turns: 60
  prompt: |
    AUTONOMOUS mode — Monthly strategic review.
    REPORT ONLY — no API writes.
    Full month comparison. Budget reallocation recs.
    Stage transition assessments.
```

---

## Open Questions

1. **Notion location** — New top-level page "PPC Agent Sessions" or under existing parent?
2. **Action approval method** — Interactive sessions ("apply items 1 and 3") vs Notion database with Status toggles?
3. **Monthly review** — Autonomous draft + interactive discussion, or fully autonomous?
4. **DST handling** — Israel DST vs server timezone. n8n cron needs to account for this.

---
name: ppc-agent
description: PPC Agent v2 — active orchestrator that assesses context, chains skills intelligently, and proposes session plans
triggers:
  - ppc
  - ppc check
  - ppc agent
  - ppc morning
  - daily ppc
  - ppc health
  - adjust bids
  - bid review
  - portfolio check
  - harvest search terms
  - monthly ppc
  - deal prep
  - post deal
  - rank optimizer
  - rank vs spend
  - create campaigns
  - tacos check
  - profit check
  - deep dive
  - portfolio action plan
  - portfolio review
  - review all
  - audit mode
output_location: outputs/research/ppc-agent/
---

# PPC Agent v2

**USE WHEN** user says anything PPC-related: "ppc", "ppc check", "ppc morning", "adjust bids", "portfolio check", "harvest search terms", "monthly ppc", "ppc catch-up", "portfolio review", "audit mode", or similar.

---

## What This Is

The PPC Agent is an **active orchestrator** — it assesses what needs to happen based on cadence, portfolio health, and pending work, then builds a session plan, chains skills intelligently, and tracks everything.

**v2 changes from v1:**
- **Smart Catch-Up** as default entry point (not passive cadence table)
- **Skill Chaining** — skills auto-trigger follow-up skills based on findings
- **Audit Mode** — permanent toggle for analysis-only runs (no API mutations)
- **Portfolio Review Mode** — urgency-scored pick-list + per-portfolio deep dive sequence
- **Portfolio Action Plan as anchor skill** — the go-to for any deep problem
- **Revenue-Weighted Rotation** — ALL portfolios get regular optimization scans (Tier 1 weekly, Tier 2 biweekly, Tier 3 monthly)
- **Optimization Scan Protocol** — 5-7 min focused checkup for healthy portfolios (budget, trends, search terms, rank momentum)
- **Session tracking** — prevents duplicate work, enables context recovery
- **Action Validator** — validates prior changes against fresh API data (WORKED/PARTIAL/NEUTRAL/FAILED)
- **Campaign Lifecycle Tracker** — tracks new campaigns through AWAITING_ENABLE → RAMPING → EARLY → ESTABLISHED → GRADUATED
- **Stale Action Hygiene** — auto-expires old pending actions and reviews, prevents unbounded growth
- **Competitive Response Integration** — surfaces competitor alerts into PPC decisions (price drops, new entrants, BSR shifts)
- **Budget Intelligence Layer** — cross-campaign and cross-portfolio budget awareness during scans and reviews
- **Pattern Learning Engine** — derives actionable insights from accumulated validation data (4+ weeks)

---

## Step 0: Read Lessons (MANDATORY)

**FIRST STEP — NO EXCEPTIONS:**

1. Read `.claude/skills/ppc-agent/LESSONS.md`
2. Check **Known Issues** — plan around these
3. Check **Repeat Errors** — if you encounter one, tell user: _"Repeat issue (xN): [description]"_
4. Apply all past lessons to this run

---

## Step 1: Load State + Determine Mode

1. Read `outputs/research/ppc-agent/state/agent-state.json`
2. Check `audit_mode` flag — display badge: **`[AUDIT MODE]`** or **`[LIVE MODE]`**
3. Check `session` object:
   - If exists and age < 24 hours: "Found in-progress session from {time}. Skills done: {list}. Remaining: {list}. Resume?"
   - If exists and age > 24 hours: auto-clear stale session, start fresh
   - If null: fresh session

**If agent-state.json doesn't exist:** Create it with all null dates (first-time setup).

### State File Structure

```json
{
  "audit_mode": false,
  "session": null,
  "last_daily_health": null,
  "last_search_harvest": null,
  "last_bid_review": null,
  "last_portfolio_summary": null,
  "last_weekly_analysis": null,
  "last_monthly_review": null,
  "last_rank_optimizer": null,
  "last_tacos_optimizer": null,
  "last_negative_generation": {},
  "revenue_tiers_updated": null,
  "campaign_watchlist": [
    {
      "campaign_id": "123456",
      "campaign_name": "SK example keyword",
      "portfolio": "portfolio-slug",
      "type": "SP",
      "match_type": "exact",
      "created_date": "2026-03-10",
      "created_by": "ppc-campaign-creator",
      "phase": "AWAITING_ENABLE",
      "phase_entered": "2026-03-10",
      "daily_budget": 15.00,
      "initial_bid": 0.75,
      "notes": "From STH PROMOTE signal"
    }
  ],
  "expired_actions": [],
  "portfolio_index": {
    "{slug}": {
      "revenue_tier": 1,
      "review_cadence_days": 7,
      "last_optimization_scan": null,
      "monthly_revenue": 3200,
      "last_validation": null,
      "validation_history": [],
      "last_listing_change": null,
      "listing_stage": null,
      "...": "other existing fields"
    }
  },
  "all_pending_actions": [ ... ],
  "upcoming_reviews": [ ... ],
  "pending_summary": {
    "total": 38, "p1": 4, "p2": 11, "p3": 16, "p4": 7,
    "aging_5d": 8, "oldest_p1_days": 8,
    "portfolios_with_p1": ["portfolio-a", "portfolio-b"],
    "last_computed": "2026-03-10"
  },
  "review_summary": {
    "total_tracked": 29, "in_global_state": 24,
    "overdue": 4, "due_today": 4, "due_this_week": 16,
    "future_in_trackers_only": 5, "last_computed": "2026-03-10"
  }
}
```

### Session Object Structure (when active)

```json
{
  "started": "ISO timestamp",
  "skills_run": [{"skill": "name", "completed": "ISO", "result": "success|partial|failed"}],
  "data_fetched": [{"type": "campaign_report", "date": "...", "path": "..."}],
  "findings": [{"skill": "...", "finding": "...", "triggers": ["skill-name"]}],
  "queued_actions": [{"skill": "...", "reason": "...", "approved": null}],
  "chain_depth": 0
}
```

### Surfaced Data (maintained by every sub-skill)

| Field | What it surfaces | Updated by |
|-------|-----------------|------------|
| `portfolio_index.{slug}.acos` | Latest ACoS from tracker | Daily health, portfolio summary, deep dive |
| `portfolio_index.{slug}.tacos` | Latest TACoS | TACoS optimizer |
| `portfolio_index.{slug}.tacos_target` | Portfolio TACoS goal | TACoS optimizer |
| `portfolio_index.{slug}.tacos_grade` | TACoS grade (A-F) | TACoS optimizer |
| `portfolio_index.{slug}.trend` | From tracker's improvement_assessment | Deep dive, significant metric shifts |
| `portfolio_index.{slug}.top_action` | Highest-priority pending action | Any skill that adds/completes actions |
| `portfolio_index.{slug}.health_status` | Traffic light | Daily health, deep dive |
| `portfolio_index.{slug}.revenue_tier` | 1/2/3 (high/mid/low) | Revenue tier setup (from Seller Board) |
| `portfolio_index.{slug}.review_cadence_days` | 7/14/30 | Based on revenue tier |
| `portfolio_index.{slug}.last_optimization_scan` | Date of last scan | Optimization scan |
| `portfolio_index.{slug}.monthly_revenue` | Revenue from Seller Board | Revenue tier setup |
| `portfolio_index.{slug}.last_listing_change` | Date of most recent listing push | Listing Manager (after push) |
| `portfolio_index.{slug}.listing_stage` | null / "awaiting-ab" / "measuring-impact" | Listing Manager, Listing AB Analyzer |
| `portfolio_index.{slug}.last_validation` | Date of last action validation | Action Validator (3d) |
| `portfolio_index.{slug}.validation_history` | Array of validation scorecards | Action Validator (3d) |
| `campaign_watchlist` | New campaigns being tracked through lifecycle | Campaign Creator, deep dive, manual |
| `expired_actions` | Archive of stale actions removed by hygiene | Stale Action Hygiene (3f) |
| `competitive_flags` | Active competitor alerts by portfolio | Competitor Price SERP Tracker |
| `all_pending_actions` | Active pending actions P1-P4 (completed auto-cleaned by Step 3f) | Any skill that adds/completes actions |
| `upcoming_reviews` | Near-term reviews only (date <= today + 7 days). Future reviews live in portfolio tracker `scheduled_reviews` | Deep dive, bid recommender, harvester |
| `pending_summary` | Quick counts: total, by priority, aging, portfolios with P1 | Step 8a (recomputed after every skill run) |
| `review_summary` | Quick counts: total tracked, overdue, due today/this week | Step 8a (recomputed after every skill run) |

### Portfolio Tracker System

Each portfolio has a tracker at `outputs/research/ppc-agent/state/{slug}.json` containing:
- **goals** — ACoS/CVR targets, rank targets, strategic notes
- **baseline** — write-once snapshot from before agent changes
- **latest_metrics** — most recent snapshot + delta vs baseline
- **metric_history** — time-series for trend tracking (max 30 entries)
- **change_log** — every API change made
- **pending_actions** — queued work with priority and due dates
- **scheduled_reviews** — upcoming re-check dates
- **skills_run** — log of skill executions
- **improvement_assessment** — is this portfolio improving?

---

## Step 2: Classify User Intent

Check user intent in this order:

| User says | Entry mode | Go to |
|-----------|------------|-------|
| Prompt contains "AUTONOMOUS" | **Autonomous Session** | Step 10 |
| "audit mode on/off" / "live mode" | **Toggle Audit Mode** | Step 7 |
| "portfolio review" / "full review" / "review all" | **Portfolio Review** | Step 6 |
| Specific skill trigger (see routing table below) | **Direct Route** | Step 5 |
| "apply items {N} from {day}" / "apply actions from Tuesday" | **Apply Session Actions** | Step 11 |
| "ppc" / "ppc agent" / "ppc check" / "ppc catch-up" / anything ambiguous | **Smart Catch-Up** (DEFAULT) | Step 3 |

---

## Step 3: Smart Catch-Up (DEFAULT Entry Point)

This is the heart of the agent. Every ambiguous PPC invocation runs this.

### 3a. Calculate Overdue Skills

For each skill, compute `days_since = today - last_run`. Compare against cadence:

| Skill | Cadence | Overdue if | Priority | Type |
|-------|---------|-----------|----------|------|
| Daily Health | Daily | >1 day | P1 | READ-ONLY |
| Search Term Harvest | 2-3 days | >3 days | P2 | HYBRID |
| Bid Review | 2-3 days | >3 days | P2 | ACTION |
| Portfolio Summary | 2-3 days | >3 days | P3 | READ-ONLY |
| Weekly Analysis | Weekly | >7 days | P4 | READ-ONLY |
| Keyword Rank Optimizer | Weekly (after weekly) | >7 days | P4 | READ-ONLY |
| TACoS Optimizer | Weekly (after weekly) | >7 days | P4 | READ-ONLY |
| Negative Keyword Gen | Per-portfolio first + quarterly | Never or >90d | P5 | HYBRID |
| Campaign Creator | On demand | Pending PROMOTE/REDIRECT exist | P5 | ACTION |
| Monthly Review | Monthly | Month boundary crossed | P3 (elevated 1st of month) | READ-ONLY |

### 3b. Scan Portfolio Flags

From `portfolio_index`, collect:
- **RED** portfolios (urgent)
- Portfolios with **P1 pending actions**
- Portfolios with **`next_review` <= today** (scheduled reviews due)
- Portfolios with **`last_deep_dive` = null** (never analyzed)
- Portfolios with **no negative gen ever** (check `last_negative_generation` dict)

### 3c. Scan Pending Actions

Use `pending_summary` for quick counts (P1/P2/P3/P4 totals, aging count, portfolios with P1). Only scan the full `all_pending_actions` array if you need to identify specific actions for display or hygiene (Step 3f).

### 3d. Validate Due Reviews (Action Validator)

**Purpose:** Before making new changes, check if previous changes actually worked. This closes the feedback loop — without it, the agent optimizes blind.

**When this runs:** Every Smart Catch-Up. Scan `upcoming_reviews` for entries where `date <= today`. Use `review_summary` for quick counts. Note: `upcoming_reviews` only contains near-term items (date <= today + 7 days). Future reviews live exclusively in portfolio tracker `scheduled_reviews` and get promoted to global state as they come within the 7-day window (Step 8a).

**For each due review:**

1. **Locate the source changes** — read the portfolio tracker's `change_log` entries matching the review's `source` field
2. **Pull fresh campaign data** for each changed campaign:
   - `list_sp_campaigns` filtered by campaign ID → current state, budget, bidding
   - If recent campaign report exists (<3 days old), use cached data
   - Otherwise, `create_ads_report` (sp_campaigns, LAST_7_DAYS) → filter by campaign IDs
3. **Compare before vs after** for each change:

| Change Type | "Before" (from change_log `old`) | "After" (from fresh data) | Success Criteria |
|-------------|----------------------------------|---------------------------|-----------------|
| BID_DECREASE / TOS reduction | Old ACoS / old TOS-IS% | New ACoS / new TOS-IS% | ACoS improved AND rank didn't drop >3 positions |
| NEGATE_SEARCH_TERM | Spend on negated term (from old data) | $0 on that term (verify via search term report) | Spend eliminated, no false positive |
| CAMPAIGN_CREATE | null (didn't exist) | Impressions, clicks, orders, ACoS | Getting impressions? If ENABLED >7d: any orders? |
| BUDGET_DECREASE | Old budget utilization | New utilization + ACoS | ACoS improved, didn't starve campaign |
| BUDGET_INCREASE | Old budget, was constrained | New spend, new orders | More orders without ACoS blowout |
| KEYWORD_PAUSE | Was spending with poor ACoS | $0 spend on keyword | Spend eliminated, overall portfolio ACoS improved |
| CAMPAIGN_PAUSE | Was bleeding | $0 spend | Confirmed waste stopped |

4. **Classify each change outcome:**
   - **WORKED** — metric improved in intended direction
   - **PARTIAL** — some improvement but less than expected, or side effects
   - **NEUTRAL** — no significant change (<5% delta)
   - **FAILED** — metric worsened or change had negative side effects
   - **INSUFFICIENT_DATA** — too early to tell (<100 impressions or <7 days)

5. **Produce validation scorecard:** Table with `| # | Change | Before | After {N}d | Verdict | Next Step |`, followed by summary counts (WORKED/PARTIAL/NEUTRAL/FAILED) and aggregate ACoS impact.

6. **Act on results:**
   - **WORKED** → log pattern to portfolio tracker `validation_history` + LESSONS.md if novel
   - **PARTIAL** → keep monitoring, schedule follow-up in 7 more days
   - **NEUTRAL** → close review, note "no significant impact"
   - **FAILED** → auto-queue corrective action as P2 pending action: "Revert {change} — validation showed {outcome}"
   - **INSUFFICIENT_DATA** → extend review by 7 days, add new `upcoming_review` entry

7. **Update portfolio tracker:**
   - `validation_history` → append: `{"date": "today", "source": "{review source}", "score": "4/7 WORKED", "details": [{change, verdict, impact}]}`
   - `improvement_assessment` → update based on validation trend

**Priority in session plan:** Validations appear BEFORE new work — must validate old changes before making new ones. If no due reviews exist, skip silently.

### 3e. Scan Campaign Watchlist (Campaign Lifecycle)

**Purpose:** Track new campaigns from creation through graduation. Prevents "create and forget."

**When this runs:** Every Smart Catch-Up. Read `campaign_watchlist` from agent-state.json.

**For each watched campaign:**

1. **Check current status** via `list_sp_campaigns` (filter by campaign ID):
   - Is it still PAUSED? ENABLED? How long since creation?
2. **Classify lifecycle phase:**

| Phase | Criteria | What to check | Alert if |
|-------|----------|---------------|----------|
| **AWAITING_ENABLE** | Created PAUSED, still PAUSED | Days since creation | PAUSED >3 days → flag for user |
| **RAMPING** | ENABLED, age 1-7 days | Impressions, clicks | 0 impressions after 3 days → "not serving" |
| **EARLY** | ENABLED, age 8-14 days | Orders, ACoS | >100 clicks + 0 orders → "failing to convert" |
| **ESTABLISHED** | ENABLED, age 15-30 days | ACoS vs target, rank | ACoS >2x target → "underperforming" |
| **GRADUATED** | ENABLED, age >30 days, ACoS within target | Stable performance | Remove from watchlist → normal tracking |

3. **Update watchlist entry:**
   - `current_state` → from API
   - `last_checked` → today
   - `ramp_phase` → current phase
   - `metrics_7d` → `{impressions, clicks, orders, spend, acos}` from campaign data
   - `alerts` → any new alerts

4. **Graduation:** When a campaign reaches 30+ days ENABLED with ACoS within 1.5x of portfolio target, remove from watchlist. Log in portfolio tracker: `{"skill": "campaign-graduated", "date": "today", "campaign": "...", "final_acos": "...", "orders_30d": N}`

**Watchlist alerts in session plan:** Table with `| # | Campaign | Portfolio | Phase | Age | Alert |`. Skip section silently if watchlist is empty.

### 3f. Clean Stale Items (Action Hygiene)

**Purpose:** Prevent the pending action queue and review list from growing unbounded with stale, irrelevant items. Keeps signal-to-noise ratio high.

**When this runs:** Every Smart Catch-Up. Scan `all_pending_actions` and `upcoming_reviews`.

**Staleness rules for pending actions:**

| Priority | Stale after | Action |
|----------|------------|--------|
| P1 | >7 days, not completed | **Re-validate:** pull fresh campaign data for the specific action. If issue still exists → keep + escalate. If issue resolved → auto-expire. |
| P2 | >14 days, not completed | **Re-validate:** same check. Still valid → keep. Resolved → expire. |
| P3 | >21 days, not completed | **Auto-expire:** move to `expired_actions` with reason "Data likely stale after 21d — re-assess if still needed" |
| P4 | >30 days, not completed | **Auto-expire:** same. |
| Any | `status: completed` | **Clean:** remove from `all_pending_actions` (already preserved in portfolio tracker change_log) |

**Re-validation for P1/P2 actions:** Identify campaign → pull current metrics → if issue persists: keep + re-date + escalate. If resolved (ACoS improved, campaign paused): auto-expire with reason. If can't identify: expire.

**Staleness rules for upcoming_reviews:** >5 days past due → escalate to Due Validations (3d). >14 days past due → auto-expire ("data too stale"). Completed → remove.

**After cleanup, report in session plan:** Bullet list summarizing: re-validated P1/P2 counts, expired P3/P4 counts, cleaned completed counts, escalated/expired review counts.

**Move expired items to `expired_actions`** in agent-state.json with fields: `id`, `original_action`, `portfolio`, `priority`, `created`, `expired`, `reason`. **Cap at 50 entries** (oldest auto-removed).

### 3g. Check Month Boundary

If `last_monthly_review` is null OR the month of `last_monthly_review` < current month - 1, flag Monthly Review.

On the 1st-3rd of any month, elevate Monthly Review to top of session plan with note: "Month boundary crossed — monthly review recommended before other work."

### 3h. Check Portfolio Rotation

**Every portfolio deserves regular attention, not just broken ones.** Use revenue-weighted rotation to ensure healthy portfolios get systematic optimization.

**Revenue Tiers and Cadences:**

| Tier | Revenue Range | Review Cadence | Portfolios |
|------|--------------|----------------|------------|
| **Tier 1** (High) | >$2,000/mo | Every 7 days | Top ~5 by revenue |
| **Tier 2** (Mid) | $500-$2,000/mo | Every 14 days | Middle ~8 by revenue |
| **Tier 3** (Low) | <$500/mo | Every 30 days | Bottom ~5 by revenue |

**First-time tier setup:** If `revenue_tiers_updated` is null or >30 days old, pull 30d revenue from Seller Board (`get_sales_detailed_report`, save full CSV) → sort portfolios by PPC+organic revenue → assign tiers → store `monthly_revenue`, `revenue_tier`, `review_cadence_days` per portfolio in `portfolio_index` → set `revenue_tiers_updated` to today.

**Rotation check:** For each portfolio, compute `days_since_scan = today - last_optimization_scan`. If `days_since_scan >= review_cadence_days`, the portfolio is **due for optimization scan**.

Collect all due portfolios, sorted by:
1. Revenue tier (Tier 1 first)
2. Days overdue (most overdue first)
3. Health status (GREEN last — they're stable but still need attention)

### 3i. Build Session Plan

Present a prioritized plan combining all findings. Use `pending_summary` and `review_summary` for quick counts.

**Session plan sections (in order, skip if empty):**

1. **Due Validations** (from 3d) — `| # | Portfolio | Source | Changes | Est. time |`
2. **Campaign Watchlist Alerts** (from 3e) — `| # | Campaign | Portfolio | Phase | Age | Alert |`
3. **Housekeeping** (from 3f) — bullet list of cleanup actions taken
4. **Overdue Skills** (from 3a) — `| # | Skill | Last run | Days overdue | Est. time | Type |`
5. **Flagged Portfolios** (from 3b) — `| # | Portfolio | Health | ACoS | Trend | Deep Dive | Pending | Top Concern |`
6. **Rotation Queue** (from 3h) — `| # | Portfolio | Tier | Health | Last Scan | Days Overdue | Revenue |`
7. **Pending Work** — P1 count + review count from summaries
8. **Recommended Session** — numbered sequence with time estimates + `Approve all / Pick items / Modify?`

**Session priority order:** Validations first → Overdue skills → Flagged portfolios → Rotation scans. Fill remaining time with optimization scans (2-4 per session).

### 3j. Execute Approved Plan

Run each approved item sequentially:
1. Create session object in agent-state.json (if not resuming)
2. For each skill in the plan:
   a. Route to the sub-skill (Step 5 routing)
   b. For rotation portfolios: run **Optimization Scan Protocol** (Step 3k) instead of full PAP
   c. After completion: run **Step 4 (Skill Chaining Protocol)**
   d. Update session object with skill result + findings
3. After all planned items: run Step 9 (Session Wrap-Up)

### 3k. Optimization Scan Protocol (5-7 min per portfolio)

**Purpose:** Systematic review of healthy/stable portfolios to find scaling opportunities, efficiency gains, and emerging issues BEFORE they become problems. This is NOT a deep dive — it's a focused checkup.

**When to use:** For rotation-queue portfolios (GREEN/YELLOW, not flagged as urgent). If the scan reveals a serious problem, escalate to full PAP.

**Scan Checklist (in order):**

| # | Check | Data Source | Looking For | Time |
|---|-------|------------|-------------|------|
| 1 | **Budget utilization** | `get_sp_campaign_budget_usage` for top campaigns | Utilization >85% = starved (scale up). <40% = over-allocated (redistribute). | 1 min |
| 2 | **ACoS trend** | Portfolio tracker `metric_history` (last 3-4 entries) | Drift >5pp from target = early warning. Improving = opportunity to scale. | 1 min |
| 3 | **Search term quick-scan** | Most recent search term report (if <5d old) or quick `create_ads_report` (sp_search_terms, LAST_7_DAYS) | High-spend zero-conversion terms (>$15, 0 orders). New converting terms not yet in exact campaigns. | 2 min |
| 4 | **Rank momentum** | DataDive `get_rank_radar_data` (if rank radar exists for this portfolio) | Rank gains to protect (increase bids). Rank drops to investigate. Keywords approaching page 1. | 1 min |
| 5 | **Organic share trend** | Portfolio tracker `tacos` + `tacos_grade` history | Organic growing (TACoS improving) = can reduce PPC reliance. TACoS worsening = investigate listing/rank. | 30 sec |
| 6 | **Pending action check** | Portfolio tracker `pending_actions` | Stale actions >7 days old. Completed actions not marked done. | 30 sec |
| 7 | **Campaign watchlist** | `campaign_watchlist` entries for this portfolio | New campaigns stuck in AWAITING_ENABLE. RAMPING campaigns with zero impressions. EARLY campaigns underperforming expectations. | 30 sec |
| 8 | **Competitor context** | `competitive_flags` in agent-state.json + portfolio tracker `competitor_alerts` | Competitor price drops >10%. New competitors on page 1. Competitor BSR gains. | 30 sec |

**Scan Output:** Header line with tier/revenue/health/last-scan, then `| Check | Status | Finding |` table (one row per checklist item, status = OK/WATCH/ACTION), followed by numbered recommendations and next scan date.

**Escalation triggers (scan → full PAP):**
- ACoS >15pp above target
- Budget utilization >95% on >50% of campaigns
- Hero keyword dropped 5+ positions
- CVR dropped below 5%
- Any metric with "declining" trend for 3+ consecutive data points

**After scan:** Update portfolio tracker:
- `last_optimization_scan` → today
- `pending_actions` → add any new recommendations
- `scheduled_reviews` → add next scan date
- `skills_run` → append `{"skill": "optimization-scan", "date": "today", "result": "ok/watch/escalate"}`

### 3l. Budget Intelligence (when data available)

**Purpose:** Cross-campaign and cross-portfolio budget awareness. Prevents local optimization that misses global inefficiency.

**When this runs:** During Optimization Scan (check #1 already covers per-campaign budget), Portfolio Summary, and Portfolio Action Plan. NOT a standalone step — it enhances existing skills.

**Budget checks to integrate:**

| Check | Where it runs | What to flag |
|-------|--------------|--------------|
| Portfolio total utilization | Portfolio Summary, PAP | Total daily budget vs actual spend. If <50% across portfolio → over-allocated |
| Budget-starved campaigns | Optimization Scan (#1), Daily Health | >90% utilization + impression share loss → recommend increase |
| Budget-idle campaigns | Optimization Scan (#1), PAP | <30% utilization for 14+ days → recommend decrease or pause |
| Cross-portfolio imbalance | Monthly Review | Portfolio A under-spending while Portfolio B starved → recommend reallocation |
| Monthly spend forecast | Monthly Review | Current daily run rate × remaining days. Alert if >120% of historical monthly average |

**Budget data sources:**
- `get_sp_campaign_budget_usage` — per-campaign utilization (most accurate)
- Campaign report `spend` vs `budget` — daily spend efficiency
- Seller Board `get_ppc_marketing_report` — account-level PPC spend

**No new state fields required** — budget data is ephemeral (pulled fresh each run, not stored). Findings surface through existing pending_actions and scan recommendations.

---

## Step 4: Skill Chaining Protocol (runs after EVERY sub-skill)

After every sub-skill completes, evaluate these chaining triggers BEFORE proceeding to the next planned item.

### Chain Constraints
- **Max chain depth: 3** (prevent infinite loops)
- **Never re-run a skill already completed this session** (check `session.skills_run`)
- **Respect audit mode** — queued action skills become "recommendations" in audit mode
- **Inform user of auto-chains:** "Daily Health found 2 RED portfolios. Auto-running Portfolio Action Plan for deeper context."

### Skill Classification

| Skill | Type | Auto-chain? | Audit mode behavior |
|-------|------|-------------|-------------------|
| Daily Health | READ-ONLY | Yes | No change |
| Portfolio Summary | READ-ONLY | Yes | No change |
| Weekly Analysis | READ-ONLY | Yes | No change |
| Keyword Rank Optimizer | READ-ONLY | Yes | No change |
| TACoS Optimizer | READ-ONLY | Yes | No change |
| Monthly Review | READ-ONLY | Yes | No change |
| Search Term Harvest | HYBRID | Analysis auto, actions pause | Skip negation step |
| Bid Recommender | ACTION | No, always pause | Skip application step |
| Campaign Creator | ACTION | No, always pause | Skip creation step |
| Portfolio Action Plan | HYBRID | Analysis auto, actions pause | Skip execution step |
| Negative Keyword Gen | HYBRID | Analysis auto, actions pause | Skip application step |

### Auto-Chain Rules (read-only / analysis — no approval needed)

These run automatically. Just inform the user:

| After this skill... | If this condition is true... | Auto-run... |
|---------------------|------------------------------|-------------|
| Daily Health | RED portfolio found | **Portfolio Action Plan** for each RED portfolio (anchor skill — the go-to deep dive for any red flag) |
| Daily Health | YELLOW with P1 pending actions | **Portfolio Summary** for context |
| Weekly Analysis | Rank Optimizer >7d or never run | **Keyword Rank Optimizer** (uses fresh weekly targeting data) |
| Weekly Analysis | TACoS Optimizer >7d or never run | **TACoS Optimizer** (uses fresh weekly data + Seller Board) |
| TACoS Optimizer | LOSS-MAKING portfolios found (TACoS grade D/F) | **Portfolio Action Plan** (deep problems need the anchor skill) |
| Portfolio Summary | ACoS >50% or CVR <5% on any portfolio | **Portfolio Action Plan** (deep problems need deep analysis) |
| Competitor Tracker | competitor_alerts found for any portfolio | **Daily Health** with competitive context (or **Bid Recommender** for PROTECT alerts) |

### Queue Rules (action skills — approval required)

These get queued and presented to the user:

| After this skill... | If this condition is true... | Queue... |
|---------------------|------------------------------|----------|
| Search Term Harvest | PROMOTE candidates found | **Campaign Creator** (present candidates, ask user) |
| Rank Optimizer | PROTECT alerts (rank dropping) | **Bid Recommender** (pass PROTECT keywords) |
| Portfolio Action Plan | No negatives ever generated for this portfolio | **Negative Keyword Gen** (proactive seeding) |
| Campaign Creator | New campaigns created | **Negative Keyword Gen** (seed new campaigns with negatives) |
| Portfolio Summary | Structure gaps found (missing campaign types) | **Campaign Creator** (present gaps) |
| Rank Optimizer | WASTING MONEY keywords with conversion waste (conv_click_ratio <0.5) AND `last_listing_change` is null or >14 days ago | **Listing Manager** (suggest: "Listing issue suspected for {ASIN} — conversion waste on {N} keywords. Run listing-manager to audit.") |
| Portfolio Action Plan | CVR dropped >25% over 2+ weeks with stable bids/spend AND `last_listing_change` is null or >14 days ago | **Listing Manager** (suggest: "CVR drop not explained by PPC changes — listing issue suspected for {ASIN}. Run listing-manager to audit.") |

### Queue Presentation

For queued action skills: state the finding + condition, name the suggested next skill, then ask Y/N (live mode) or note "adding to recommendations" (audit mode).

### Portfolio Action Plan as Anchor Skill

**PAP is the most powerful analysis skill.** It pulls all data sources, does campaign-by-campaign analysis, and produces impact-ranked action plans. Whenever a portfolio has a genuine problem (RED health, loss-making, high ACoS, structural issues), PAP should be the automatic response — not just a surface-level summary.

PAP auto-chains from:
- Daily Health → RED portfolio
- TACoS Optimizer → LOSS-MAKING portfolio
- Portfolio Summary → ACoS >50% or CVR <5%

### Competitive Response Rules

When `competitive_flags` in agent-state.json has active alerts for a portfolio:

| Competitor Signal | PPC Response | Urgency |
|-------------------|-------------|---------|
| Price drop >10% on competing ASIN | Flag in Daily Health → consider defensive bid increase on hero KWs | P2 |
| New competitor on page 1 for hero keyword | Flag in Rank Optimizer → recommend TOS boost | P2 |
| Competitor BSR improving rapidly | Flag in TACoS Optimizer → evaluate compete vs pivot | P3 |
| Competitor out-of-stock | Opportunity → consider temporary bid increase to capture share | P2 |

**Data source:** `competitive_flags` in agent-state.json (populated by competitor-price-serp-tracker skill, weekly cadence). If `last_competitor_tracker` is >14 days old, note "competitive data stale" but don't block other work.

---

## Step 5: Direct Route (for specific skill triggers)

### Status Bar (show before every route)

Always show a 3-line status bar before routing:
```
**[{AUDIT MODE / LIVE MODE}]** | Overdue: {N} skills | RED portfolios: {N} | Pending P1: {N}
```

### Routing Table

| User says | Route to | Skill location |
|-----------|----------|----------------|
| "ppc morning" / "daily ppc" / "ppc health" | **Daily PPC Health Check** | `.claude/skills/ppc-daily-health/SKILL.md` |
| "adjust bids" / "bid recommendations" / "bid review" | **Bid Adjustment Recommender** | `.claude/skills/ppc-bid-recommender/SKILL.md` |
| "portfolio check" / "portfolio health" / "portfolio flags" | **Portfolio Performance Summary** | `.claude/skills/ppc-portfolio-summary/SKILL.md` |
| "harvest search terms" / "negate and promote" / "search term review" | **Search Term Harvester** | `.claude/skills/ppc-search-term-harvester/SKILL.md` |
| "monthly ppc" / "monthly review" / "ppc month" | **Monthly PPC Review** | `.claude/skills/ppc-monthly-review/SKILL.md` |
| "weekly ppc" / "ppc analysis" / "weekly review" | **Weekly PPC Analysis** (standalone) | `.claude/skills/weekly-ppc-analysis/SKILL.md` |
| "negative keywords" / "generate negatives" | **Negative Keyword Generator** (standalone) | `.claude/skills/negative-keyword-generator/SKILL.md` |
| "rank optimizer" / "rank vs spend" / "keyword rank analysis" / "ppc rank check" | **Keyword Rank Optimizer** | `.claude/skills/keyword-rank-optimizer/SKILL.md` |
| "create campaigns" / "campaign creator" / "build campaigns" / "new campaigns" | **PPC Campaign Creator** | `.claude/skills/ppc-campaign-creator/SKILL.md` |
| "portfolio deep dive" / "deep dive {name}" / "portfolio action plan" / "fix {portfolio}" / "work on {portfolio}" | **Portfolio Action Plan** | `.claude/skills/ppc-portfolio-action-plan/SKILL.md` |
| "deal prep" / "deal ppc" / "prep for deal" | **Deal Coordination** (Bid Recommender — deal mode) | `.claude/skills/ppc-bid-recommender/SKILL.md` |
| "tacos check" / "tacos optimizer" / "profit check" / "tacos scorecard" / "profit reality" | **TACoS & Profit Optimizer** | `.claude/skills/ppc-tacos-optimizer/SKILL.md` |
| "ppc trends" / "ppc dashboard" / "trend check" / "trajectory" / "time series" / "30 day trend" | **Weekly PPC Analysis** (includes trajectories) | `.claude/skills/weekly-ppc-analysis/SKILL.md` |
| "post deal" / "deal ended" / "deal cleanup" | **Deal Cleanup** (Bid Recommender — post-deal mode) | `.claude/skills/ppc-bid-recommender/SKILL.md` |

### How to Route

1. **Read the target skill's LESSONS.md** first (mandatory)
2. **Read the target skill's SKILL.md** for instructions
3. **If audit mode is ON**, inject the audit mode instruction (see Step 7)
4. **Follow those instructions** step by step
5. **After completion:** Run Step 4 (Skill Chaining Protocol)
6. **After completion:** Update state (Step 8)
7. **After completion:** Update LESSONS.md (Step 9)

### Passing Shared Data

When routing, check if upstream data exists to avoid redundant API calls:

| Sub-skill needs | Check for | Pass if found |
|----------------|-----------|---------------|
| Seller Board data | `outputs/research/market-intel/snapshots/{today}*.json` | File path |
| Campaign report | `outputs/research/ppc-weekly/snapshots/{recent}/campaign-report.json` | If <3 days old |
| Search term report | `outputs/research/ppc-weekly/snapshots/{recent}/search-term-report.json` | If <3 days old |
| Applied negatives | `outputs/research/negative-keywords/data/*-applied-*.json` | For dedup check |
| Weekly summary | `outputs/research/ppc-weekly/snapshots/{recent}/summary.json` | For downstream skills |
| Targeting report | `outputs/research/ppc-weekly/snapshots/{recent}/targeting-report.json` | For rank optimizer |
| Rank radar snapshot | `outputs/research/ppc-agent/rank-optimizer/snapshots/{recent}/rank-radar-snapshot.json` | For bid recommender |
| Rank-spend matrix | `outputs/research/ppc-agent/rank-optimizer/snapshots/{recent}/rank-spend-matrix.json` | For bid recommender |
| TACoS snapshot | `outputs/research/ppc-agent/tacos-optimizer/snapshots/{recent}/*-tacos-snapshot.json` | For monthly review |
| Trajectory data | `outputs/research/ppc-weekly/snapshots/*/summary.json` (history) | For monthly review |

**Key principle:** Never re-fetch data that a recent skill run already has on disk.

---

## Step 6: Portfolio Review Mode

Triggered by: "portfolio review", "full review", "review all portfolios"

### 6a. Score All Portfolios

Compute a composite urgency score (0-100) for each portfolio using data in `portfolio_index`:

| Factor | Weight | Scoring |
|--------|--------|---------|
| Health status | 25 | RED=25, YELLOW=15, GREEN=0, null=20 |
| ACoS vs target | 20 | (acos - target) / target * 20, capped at 20 |
| Days since deep dive | 15 | min(days_since / 30 * 15, 15). Never=15 |
| Pending P1 count | 15 | min(p1_count * 5, 15) |
| Trend | 10 | declining=10, unknown=8, stable=3, improving=0, restructuring=5 |
| TACoS grade | 10 | F=10, D=8, C=5, B=2, A=0, null=6 |
| Scheduled review overdue | 5 | next_review < today? 5 : 0 |

### 6b. Present Ranked Pick-List

```
## Portfolio Review — Ranked by Urgency [{AUDIT MODE / LIVE MODE}]

| # | Portfolio | Urgency | Health | ACoS | TACoS | Trend | Last Dive | Pending | Top Concern |
|---|-----------|---------|--------|------|-------|-------|-----------|---------|-------------|
| 1 | 4 Flowers | 85/100 | RED | — | D | unknown | never | 2 P1 | No deep dive, listing audit due |
| 2 | Needlepoint | 72/100 | RED | 57% | B | stable | today | 7 | CVR 5%, listing needed |
| 3 | Princess Lacing | 65/100 | RED | 62% | — | restruct | 4d | 4 | Launch, identity drift |
| ... |

**Pick portfolios:** "1, 2, 3" or "top 5" or "all RED" or "all"
```

### 6c. Per-Portfolio Analysis Sequence

For each picked portfolio, run this sequence. **Portfolio Action Plan is the anchor skill:**

1. **Portfolio Summary** (4 min) — structure audit, quick metrics context
2. **Keyword Rank Optimizer** (6 min, if rank radar exists for this portfolio) — rank vs spend context
3. **TACoS check** (5 min, if not already run this session) — profit reality context
4. **Portfolio Action Plan** (12 min) — **THE ANCHOR SKILL** — pulls ALL context from steps 1-3 + its own campaign-by-campaign analysis. Produces the impact-ranked action plan.

In audit mode: PAP produces full brief with actions labeled "RECOMMENDED (not applied — audit mode)".
In live mode: PAP pauses for approval before executing.

**Cap: 3-5 portfolios per session.** If user picked more, offer: "Completed {N} portfolios. Continue with {remaining} in next session?"

Run Step 4 (chaining) after each skill within the sequence.

### 6d. Executive Summary

After all picked portfolios are reviewed, produce a summary with: Portfolio Scorecards table (`| Portfolio | Health | ACoS | Key Recommendation | Est. Impact |`), Cross-Portfolio Patterns (common issues), Aggregate Opportunity (total waste, action count, time estimate), and prioritized Next Steps.

---

## Step 7: Toggle Audit Mode

- **"audit mode on" / "audit mode"** → set `audit_mode: true` in agent-state.json
- **"audit mode off" / "live mode"** → set `audit_mode: false`

Confirm: "**Audit mode {ON/OFF}.** All skills will {produce analysis briefs only / operate normally with approval gates}."

### Audit Mode Injection

When audit mode is ON, inject this instruction when routing to ANY sub-skill:

```
[AUDIT MODE ACTIVE]
Skip all API mutation steps. Produce the full analysis brief with all recommendations,
but label each action as "RECOMMENDED (not applied — audit mode)".
Do NOT call: update_sp_campaigns, manage_sp_keywords, manage_sp_negative_keywords,
create_sp_campaigns, create_sp_ad_groups, manage_sp_product_ads, manage_sp_targets,
manage_sp_negative_targets, update_sp_ad_groups, create_sp_campaign_negative_keywords,
update_sb_campaigns, update_sd_campaigns, manage_portfolios.
```

### Audit Mode + Chaining

- Auto-chains still work (analysis skills run normally)
- Queue-chains become recommendations: "Would normally trigger Campaign Creator. In audit mode, adding to recommendations brief."
- All briefs get `[AUDIT MODE — Analysis Only]` header

---

## Step 8: State Update (after every sub-skill run)

**CRITICAL — DO NOT SKIP.** After ANY sub-skill completes, update both agent-state.json and affected portfolio trackers BEFORE presenting results.

### 8a. Update `agent-state.json`

1. **Update timestamp** for the skill that just ran
2. **Add/remove pending actions** from `all_pending_actions` (remove completed items immediately)
3. **Add/remove scheduled reviews** from `upcoming_reviews` — only add reviews where date <= today + 7 days. Future reviews go exclusively in portfolio tracker `scheduled_reviews`
4. **Promote near-term reviews:** Scan portfolio tracker `scheduled_reviews` for any with date <= today + 7 days not already in `upcoming_reviews` — add them
5. **Recompute `pending_summary`:** total, p1-p4 counts, aging_5d count, oldest_p1_days, portfolios_with_p1, last_computed
6. **Recompute `review_summary`:** total_tracked, in_global_state, overdue, due_today, due_this_week, future_in_trackers_only, last_computed

### 8b. Update `portfolio_index` per portfolio touched

1. `last_updated` → today
2. `health_status` → from sub-skill output
3. `trend` → from tracker's improvement_assessment
4. `acos` → from tracker's latest_metrics
5. `pending_count` → count of pending actions in tracker
6. `top_action` → "[{priority}] {description}" of highest-priority action
7. `next_review` → earliest pending review date
8. `last_deep_dive` → if Portfolio Action Plan was run
9. `last_optimization_scan` → if optimization scan was run

### 8c. Update Portfolio Tracker Files

For each affected portfolio at `outputs/research/ppc-agent/state/{slug}.json`:

1. `skills_run` → append: `{"skill": "{name}", "date": "{today}", "result": "success/partial/failed"}`
2. `change_log` → append any API changes (bid, negative, campaign)
3. `pending_actions` → add new, mark completed
4. `latest_metrics` → update if fresh metrics produced
5. `metric_history` → append if metrics updated (max 30)
6. `scheduled_reviews` → add re-check dates
7. `improvement_assessment` → update if enough history

### 8d. Update Session Object

If session is active, update:
- `skills_run` → append completed skill
- `data_fetched` → append any new data files
- `findings` → append key findings with trigger suggestions
- `chain_depth` → track for chain limit enforcement

### 8e. Post Slack Notification (MANDATORY)

**Every sub-skill completion MUST post to Slack.** This is how upper management tracks PPC activity.

**DO NOT read notification-hub SKILL.md.** You already have the sub-skill results in context. Compose the message directly.

**Channel routing:**
- **Most PPC skills** → workspace `craft`, channel `claude-ppc-updates`
- **Daily health** → workspace `craft`, channel `claude-morning-brief`
- **Threshold breaches** → ALSO post to `claude-alerts` (in addition to the primary channel)

**Message format rules:**
- Max 2000 chars (truncate with "... _(see full report in outputs/)_" if longer)
- Use Slack markdown: `*bold*` for headers, bullets for lists, `\n` for line breaks
- Status emojis: :large_green_circle: :large_yellow_circle: :red_circle: :white_check_mark: :warning: :dart: :bar_chart: :ear_of_rice: :clipboard: :new: :calendar:
- Lead with skill name + portfolio/date, then key metrics, then actions taken/recommended
- No tables — they render poorly in Slack

**Message structure (adapt per skill):**
```
:{emoji}: *{Skill Name}* — {Portfolio or Date}

*Key metrics:* {2-3 most important numbers}

*Actions:*
- {What was done or recommended}
- {What was done or recommended}

{If applied:} :white_check_mark: Applied via API
{If pending:} Awaiting approval
```

**Alert escalation — also post to `claude-alerts` if:**
- Any RED portfolio status
- ACoS > 50% (Scaling stage) or > 80% (Launch stage)
- Revenue drop > 30% WoW
- Hero keyword rank drop > 5 positions

Alert format: `:warning: *ALERT* — {Skill}\n{One-line description}\n{Recommended action}`

**Error handling:**
- Slack MCP unavailable → skip, log "Slack notification skipped — MCP unavailable" in LESSONS.md
- Channel doesn't exist → log warning, don't fail the skill
- **NEVER let a notification failure cause the parent skill to fail**

**DO NOT SKIP THIS STEP.** If you completed a sub-skill and didn't post to Slack, the run is incomplete.

---

## Step 9: Session Wrap-Up (after all skills complete)

When all planned skills are done:

### 9a. Present Session Summary

Include: Skills Run table (`| # | Skill | Result | Key Finding |`), Chained Actions bullet list, State Changes summary (trackers updated, pending action counts), and Next Session Priorities (top 3).

### 9b. Clear Session Object

Set `session: null` in agent-state.json.

### 9c. Verify Slack Notifications Were Posted

Before closing the session, verify that Step 8e ran for every sub-skill. If any were missed (e.g., due to errors or oversight), post them now. This is the final safety net — management relies on `#claude-ppc-updates` for visibility.

### 9d. Update LESSONS.md

Add a run log entry at the TOP of the Run Log section with: date, mode, skills run, result, what happened, chains triggered, issues, lessons learned, token estimate. Include "Slack: {N}/{N} notifications posted" in the entry. Update Known Issues / Repeat Errors / Resolved Issues as needed.

---

## Global PPC Operating Rules

**These rules apply to ALL PPC sub-skills and must NEVER be violated:**

1. **Never pause a campaign based on a single week of zero conversions.** Always check minimum 30 days (ideally 60) before recommending pause. Only pause for sustained poor performance.

2. **Never use round/organized bid amounts.** No clean -30%, -50%. Use irregular amounts: -31%, -48%, -52%, -27%. Avoid predictable bid patterns.

3. **Never negate a search term based on a single week of zero conversions.** Minimum 30-day window required. Only negate for sustained zero conversions AND clearly irrelevant.

4. **Always update portfolio tracker JSON files after any API change.** Update `change_log`, `pending_actions`, `scheduled_reviews`, `skills_run` immediately after API calls succeed, BEFORE presenting results.

5. **Always post Slack notifications after every sub-skill completes (Step 8e).** Use the notification-hub recipe for the skill. Post to `#claude-ppc-updates` (or `#claude-morning-brief` for daily health). Escalate threshold breaches to `#claude-alerts`. Never skip this — management tracks PPC activity via these channels.

6. **Check for `bsr_goal` in portfolio tracker before making efficiency-based cuts.** Some portfolios have a primary goal of achieving/maintaining #1 Best Seller rank. When `bsr_goal` exists, prioritize sales velocity over ACoS efficiency. Allow ACoS to run above target if it sustains the sales volume needed to close the BSR gap. Currently applies to: **Cross Stitch Backpack Charms** (~1,000 BSR behind #1).

**Enforce these rules when routing to any sub-skill.** Flag violations before presenting to user.

---

## Integrating Never-Run Skills

These skills are built but have never been used. The agent must actively trigger them:

| Skill | When to trigger | How |
|-------|----------------|-----|
| **Keyword Rank Optimizer** | Auto-chain after Weekly Analysis (weekly cadence) | Uses fresh weekly targeting data + DataDive rank radar |
| **Negative Keyword Generator** | After first PAP per portfolio + quarterly refresh | Check `last_negative_generation[{slug}]` — null = first run needed |
| **Monthly Review** | First PPC invocation after month boundary | Reads 4 weekly snapshots + Brand Analytics monthly. Also runs Pattern Learning analysis if data thresholds met. |

### Checking for Never-Run Skills

In Smart Catch-Up (Step 3a), always flag:
- `last_rank_optimizer: null` → "Keyword Rank Optimizer has NEVER been run"
- `last_monthly_review: null` → "Monthly Review has NEVER been run"
- Any portfolio missing from `last_negative_generation` → "Negative Keyword Gen never run for {portfolio}"

---

## Pattern Learning (requires 4+ weeks of validation data)

**Purpose:** After accumulating validation_history across portfolios, detect patterns in what types of changes work and what fails. This turns accumulated data into actionable intelligence.

**When to run:** During Monthly Review, OR on-demand when user asks "what's working?"

**Minimum data thresholds:** Do NOT run pattern analysis unless:
- At least 30 validated changes exist across all `validation_history` arrays
- At least 3 portfolios have validation data
- Validation data spans at least 21 days

### Pattern Analysis Checks

| Analysis | Data Source | Output |
|----------|-----------|--------|
| **Success rate by change type** | All `validation_history` entries | "TOS reductions: 80% WORKED. Bid decreases >30%: 20% WORKED. Negations: 95% WORKED." |
| **Portfolio response profiles** | Per-portfolio validation_history | "Needlepoint responds well to TOS cuts but poorly to bid reductions" |
| **Optimal change magnitude** | change_log before/after values + validation outcomes | "TOS reductions of 30-50% work best. Reductions >60% tend to FAIL (starve campaigns)" |

### How to use patterns

- **Feed into Bid Recommender:** If pattern shows TOS cuts >50% fail, cap recommendations at -48%
- **Feed into PAP:** Include portfolio response profile in analysis context
- **Surface in Monthly Review:** "Top 3 insights from last month's changes"

**Store patterns in:** LESSONS.md (account-wide insights) + portfolio tracker `improvement_assessment` (per-portfolio patterns). Do NOT create new state fields — patterns are derived, not stored.

---

## SOP Reference

### Portfolio Stages

| Phase | ACoS Target | Primary KPI | Bid Flexibility |
|-------|------------|-------------|-----------------|
| **Launch** | Flexible (up to 60%+) | Rank velocity | High |
| **Scaling** | 28-32% | ACoS + Rank retention | Medium |
| **General** | N/A | Account-wide utility | Varies |

### Red Flag Thresholds

| Metric | Red Flag | Action |
|--------|----------|--------|
| ACoS >50% (Scaling) | Bleeding spend | Route to PAP (anchor skill) |
| CVR <5% | Listing or targeting issue | Flag — may need listing review |
| Hero keyword drops 5+ positions | Competitor attack | Route to Bid Recommender |
| 50+ clicks, 0 orders on keyword | Dead weight | Route to Search Term Harvester |
| Budget utilization >95% | Starved campaign | Flag in Daily Health |
| BSR declining despite spend | Market saturation | Flag for strategic review |

---

## Step 10: Autonomous Session Mode

**Triggered when:** Prompt contains "AUTONOMOUS" (from automation runner, not interactive use).

**This is a fundamentally different operating mode.** The agent does NOT run sub-skills. It reads pre-computed data from the Monday pipeline and does the work that requires intelligence: validation, cross-referencing, synthesis, and action item generation.

**Core rule: REPORT ONLY — no API writes, ever.** Action items are saved to disk for the user to approve and apply interactively via Step 11.

---

### 10a. Detect Session Type

| Prompt contains | Session type | Scope | Time budget |
|----------------|-------------|-------|-------------|
| "Tuesday" or weekday is Tuesday | **Tuesday full session** | Full analysis + validation + action items | ~40 min |
| "Friday" or weekday is Friday | **Friday check session** | Validation + anomaly scan + rotation | ~25 min |
| "Monthly" or "1st of month" | **Monthly strategic review** | Full month comparison + budget reallocation | ~55 min |

Default to Tuesday if ambiguous.

---

### 10b. Tuesday Full Session

#### Phase 1: Load (5 min)

**Load ALL of these in parallel. Do NOT pull fresh API data — read what the Monday pipeline saved.**

| # | File | Purpose | Required? |
|---|------|---------|-----------|
| 1 | `outputs/research/ppc-agent/state/agent-state.json` | State, cadence, rotation, pending actions | Yes |
| 2 | Most recent `outputs/research/ppc-agent/portfolio-summaries/*-autonomous-summary.json` | Monday's portfolio health scan | Yes |
| 3 | Most recent `outputs/research/ppc-agent/search-terms/*-autonomous-harvest.json` | Monday's search term findings | Yes |
| 4 | Most recent `outputs/research/ppc-agent/bids/*-autonomous-recommendations.json` | Monday's bid recommendations | Yes |
| 5 | Most recent `outputs/research/ppc-agent/rank-optimizer/*-autonomous-analysis.json` | Biweekly rank-spend analysis | If exists and <14d old |
| 6 | Most recent `outputs/research/ppc-agent/tacos-optimizer/*-autonomous-analysis.json` | Biweekly TACoS scorecard | If exists and <14d old |
| 7 | `outputs/research/ppc-agent/daily-health/*-health-snapshot.json` (last 5 days) | Daily health trends since last session | Yes |
| 8 | Most recent `outputs/research/ppc-agent/sessions/*-actions.json` | Previous session's action items (for validation) | If exists |
| 9 | `context/business.md` | Portfolio stages, targets | Yes |
| 10 | `outputs/research/ppc-agent/sessions/action-schema.json` | Schema reference for output | Yes |

**If a Monday output is missing:** Note it in the brief (`"Portfolio summary unavailable this week — pipeline may have failed"`). Continue with available data. Never re-run the skill — that's the Monday pipeline's job.

**Staleness check:** If the most recent Monday output is >3 days old, note: "Monday pipeline data is {N} days old — findings may not reflect current state."

#### Phase 2: Validate Previous Changes (10 min)

**This is the most valuable part of the system. Skip nothing.**

1. **Find the previous session's action items** — read the most recent `*-actions.json` from the sessions folder
2. **For each action with `status: "applied"`** (meaning the user approved and executed it since last session):
   - **Pull targeted fresh data** — ONLY for the specific campaign(s) affected. Use `list_sp_campaigns` filtered by campaign ID + most recent daily health data. This is the ONE place where the autonomous session makes API calls.
   - **Compare before vs after** using the `evidence.metrics` from the original action item as "before" and fresh data as "after"
   - **Classify the outcome:**

| Verdict | Criteria |
|---------|---------|
| **WORKED** | Primary metric improved in intended direction by >10% |
| **PARTIAL** | Some improvement (<10%) or improvement with side effects (e.g., ACoS improved but rank dropped) |
| **FAILED** | Primary metric worsened or no change after 7+ days |
| **INCONCLUSIVE** | <7 days since application OR <100 impressions — too early to tell |

3. **Produce validation scorecard** — one row per validated action
4. **Act on results:**
   - WORKED → log pattern (what type of change, what portfolio, what magnitude → what result)
   - FAILED → auto-create a P2 corrective action item: "Revert {change} — validation showed {outcome}"
   - INCONCLUSIVE → carry forward to Friday session

**If no previous session exists or no actions were applied:** Skip Phase 2, note "No previous actions to validate — first session or no approvals since last session."

#### Phase 3: Synthesize & Cross-Reference (15-20 min)

**This is where the agent thinks. Read Monday's structured output and connect the dots.**

##### 3A. Per-Portfolio Assessment (8-point checklist)

For EVERY portfolio (all 17), produce a brief assessment using Monday's data. This guarantees full coverage.

**The 8-Point Checklist:**

| # | Check | Data Source | What to note |
|---|-------|------------|-------------|
| 1 | **Budget utilization** | Bid recommender autonomous output → `on_hold` entries with budget notes | Any campaign >80% or <10% utilization |
| 2 | **ACoS trend** | Portfolio summary → `vs_weekly` + daily health trend over 5 days | Improving, stable, or worsening. Flag if worsening >5pp |
| 3 | **Search term quality** | Search term harvest → per-portfolio `negate_candidates` count + `estimated_weekly_savings` | How much waste was found. Flag if >$20/week waste |
| 4 | **Rank trajectory** | Rank optimizer → per-portfolio `rank_alerts` | Any hero keyword declining. Flag drops >5 positions |
| 5 | **Organic share** | TACoS optimizer → `organic_ratio_30d` + `organic_momentum_class` | Is PPC dependency increasing? Flag if momentum is "Eroding" |
| 6 | **Campaign structure balance** | Portfolio summary → `campaign_types` + bid recommender → per-portfolio recommendation count | Anything lopsided? Many bids flagged = structural issue |
| 7 | **Pending actions** | Agent-state → `all_pending_actions` filtered by portfolio | Stale P1/P2 items. Overdue reviews. |
| 8 | **Competitor signals** | Agent-state → `competitive_flags` | Active alerts for this portfolio |

**Output:** 2-3 sentences per portfolio summarizing the 8 checks. Don't write a novel — flag what matters, skip what's fine.

##### 3B. Cross-Reference Patterns

**Look for these specific patterns across skill outputs. These are the connections individual skills can't see.**

| Pattern | How to detect | What it means |
|---------|--------------|---------------|
| **Same campaign flagged by 2+ skills** | Search term harvest has negation candidates from Campaign X AND bid recommender recommends bid decrease on Campaign X | The campaign has multiple problems — combine into one action item, not two |
| **Rank drop correlates with recent bid change** | Rank optimizer shows keyword declining AND previous session's action items include a bid decrease on that keyword's campaign | The bid cut may have caused the rank drop. Flag as "Possible bid-rank correlation" — recommend reverting or monitoring |
| **Healthy ACoS but eroding organic** | Portfolio summary shows GREEN AND TACoS optimizer shows `organic_momentum_class: "Eroding"` | Portfolio looks fine by ACoS but is becoming PPC-dependent. Flag: "Hidden risk — organic share declining" |
| **Search term waste concentrated in one campaign** | Search term harvest has 5+ negation candidates from the same campaign | That campaign's targeting is broken. Recommend structural review, not just individual negations |
| **Bid recommendations all in same direction** | Bid recommender has 3+ decreases and 0 increases for a portfolio | Portfolio is systematically over-bidding. Note the pattern. |
| **Promote candidate matches rank opportunity** | Search term harvest has a PROMOTE candidate AND rank optimizer shows that keyword as REDIRECT | Strong signal — the keyword converts AND we don't have dedicated targeting. Elevate to P1 action. |
| **Budget-starved + efficient** | Bid recommender flags campaign as efficient (low ACoS) AND daily health shows that campaign as GREEN | Easy win — increase budget on a proven campaign. Elevate priority. |

##### 3C. Generate Action Items

From the combined analysis, produce action items using the schema at `outputs/research/ppc-agent/sessions/action-schema.json`.

**Rules for action item generation:**

| Recommendation type | Minimum evidence required |
|---------------------|--------------------------|
| Negate search term | 30 days data, zero conversions AND clearly irrelevant to product |
| Reduce bid / TOS | 30 days performance + rank data + target CPC calculation |
| Increase bid / TOS | Rank trend dropping + impression share data |
| Pause keyword | 30 days zero conversions + minimum 200 impressions |
| Pause campaign | 30 days sustained poor performance + comparison to portfolio average |
| Budget change | 14 days utilization trend |
| Campaign creation | Converting search term (PROMOTE) or REDIRECT keyword with SV >1,000 |

**De-duplicate:** Check each proposed action against `all_pending_actions` in agent-state. If an equivalent action already exists, don't create a duplicate — instead, note "Reconfirmed: {existing action ID} — still valid per fresh data."

**Priority assignment:**
- **P1:** Score ≥70 OR emergency flag (rank drop >10, ACoS >3x target)
- **P2:** Score 45-69, has 30d evidence
- **P3:** Score 25-44
- **P4:** Score <25 or insufficient evidence — monitor only, no API action

**Never use round bid amounts.** Every bid recommendation must use irregular values ($0.73 not $0.70, -31% not -30%).

#### Phase 4: Output (8-10 min)

##### 4A. Save brief to disk (FIRST — before Notion)

Save to: `outputs/research/ppc-agent/sessions/{YYYY-MM-DD}-tuesday-brief.md`

**Brief structure:**

```markdown
# PPC Agent Session — {YYYY-MM-DD} (Tuesday Full)

**Duration:** {X} min | **Monday data from:** {date}
**Portfolios assessed:** 17/17 | **Action items:** {N} new | **Validations:** {N}

---

## Executive Summary
{3-5 sentences. Lead with the single most important finding. Include overall account health.}

## Validations (Previous Changes)
{Validation scorecards from Phase 2. Table: | # | Action | Applied | Before | After | Verdict |}
{Summary: N WORKED, N PARTIAL, N FAILED, N INCONCLUSIVE}

## Portfolio Health Dashboard
{All 17 portfolios — one row each}
| Portfolio | Stage | Health | ACoS | TACoS | Trend | Organic | Top Finding | Actions |
{GREEN rows at the bottom, RED/YELLOW at top}

## Cross-Portfolio Patterns
{Patterns detected in Phase 3, 3B}

## Portfolio Assessments
{Per-portfolio 2-3 sentence summaries from Phase 3, 3A. Group by health: RED first, then YELLOW, then GREEN.}

## Action Items — {N} Total
{Grouped by priority: P1, P2, P3, P4}

### P1 — Critical ({N} items)
| # | ID | Type | Portfolio | Description | Evidence | Expected Impact |

### P2 — Optimization ({N} items)
| # | ID | Type | Portfolio | Description | Evidence | Expected Impact |

### P3 — Maintenance ({N} items)
{Same format}

### P4 — Monitor ({N} items)
{Description-only list, no API actions}

## Skills Data Quality
| Skill | Status | Data Date | Notes |
{Which Monday outputs were available, which were missing}

## Agent Reasoning Log
{What the agent looked at, what it decided, what it skipped and why}
```

##### 4B. Save action items JSON

Save to: `outputs/research/ppc-agent/sessions/{YYYY-MM-DD}-tuesday-actions.json`

Follow the schema at `outputs/research/ppc-agent/sessions/action-schema.json` exactly. Include the `validations` array from Phase 2 and the `actions` array from Phase 3.

##### 4C. Push to Notion

Create a child page under "PPC Agent Sessions" in Notion using the brief content. If Notion fails, log the error and continue — the disk brief is the source of truth.

##### 4D. Post Slack notification

Post to workspace `craft`, channel `claude-ppc-updates`:

```
:robot_face: *PPC Agent Session* — Tuesday {date}

*Health:* {N} :large_green_circle: {N} :large_yellow_circle: {N} :red_circle:
*Actions:* {N} new ({N} P1, {N} P2, {N} P3)
*Validations:* {N} checked — {N} :white_check_mark: {N} :warning: {N} :x:
*Top concern:* {one-line description}

:page_facing_up: Full brief: {Notion link or "saved to disk"}
```

##### 4E. Update agent state

1. Update `autonomous.cadence_tracker` — set `last_run` for each skill whose Monday output was read
2. Update `autonomous.rotation_tracker.last_optimization_scan` for portfolios that got full checklist assessment
3. Append to `autonomous.session_log`:
   ```json
   {
     "date": "YYYY-MM-DD",
     "type": "tuesday",
     "duration_min": 0,
     "monday_data_read": ["portfolio-summary", "search-term-harvester", "bid-recommender"],
     "portfolios_assessed": 17,
     "action_items_created": 0,
     "validations_completed": 0,
     "validation_results": {"worked": 0, "partial": 0, "failed": 0, "inconclusive": 0},
     "cross_patterns_found": 0,
     "notion_page_id": null,
     "brief_file": "sessions/YYYY-MM-DD-tuesday-brief.md"
   }
   ```
4. **Trim session_log** — if >20 entries, move oldest to `outputs/research/ppc-agent/sessions/archive/`

##### 4F. Update LESSONS.md

Write run log entry to `.claude/skills/ppc-agent/LESSONS.md` as normal (Step 9d format).

---

### 10c. Friday Check Session

**Lighter version of Tuesday. Focus on validation and anomaly detection.**

#### Phase 1: Load (3 min)

Load:
- Agent-state.json
- Daily health outputs since Tuesday (3-4 files)
- Tuesday's session actions JSON (for validation check)
- Most recent Tuesday brief (for context on what was found)

#### Phase 2: Validate (10 min)

Same validation logic as Tuesday Phase 2. Focus on:
- Actions applied since Tuesday
- Tuesday's INCONCLUSIVE items — do they have enough data now?

#### Phase 3: Quick Scan (8 min)

- Read daily health snapshots — any new RED/YELLOW since Tuesday?
- Check agent-state `all_pending_actions` — any P1 items >5 days old?
- Check `upcoming_reviews` — any overdue?
- If Tuesday found patterns, check: did anything change? (read relevant daily health for those portfolios)

**Do NOT re-read Monday pipeline outputs.** Friday works from daily health + Tuesday's findings only. Monday's data is 5 days old by Friday — too stale for fresh analysis. If something urgent appears in daily health, flag it for next Monday's pipeline.

#### Phase 4: Output (5 min)

Same process as Tuesday but shorter brief:
- Save to `{YYYY-MM-DD}-friday-brief.md` and `{YYYY-MM-DD}-friday-actions.json`
- Push to Notion (shorter page)
- Post Slack notification
- Update agent state + session log

---

### 10d. Monthly Strategic Review

**Deeper than Tuesday. The ONE session per month that pulls its own data for month-over-month comparison.**

#### What's different from Tuesday:

1. **Pulls fresh 30d data** — `create_ads_report(sp_campaigns, LAST_30_DAYS)` for current month + reads previous month's weekly snapshots for comparison
2. **Pulls Seller Board 30d** — `get_sales_detailed_report()` for revenue and profit reality
3. **Additional analysis sections:**
   - Month-over-month comparison (spend, sales, ACoS, orders, TACoS across all portfolios)
   - Budget reallocation recommendations across portfolios (shift spend from over-performing to under-invested)
   - Stage transition assessments (should any portfolio move Launch → Scaling or Scaling → General?)
   - Quarterly trend if 3+ months of session data exists
   - Pattern Learning analysis if validation data thresholds are met (see Pattern Learning section above)
4. **Longer brief** with strategic recommendations, not just tactical action items

#### Output:

- Save to `{YYYY-MM-DD}-monthly-brief.md` and `{YYYY-MM-DD}-monthly-actions.json`
- Monthly actions tend to be strategic: budget reallocation, stage transitions, portfolio restructuring
- Push to Notion
- Post Slack notification (slightly more detailed than weekly)

---

### 10e. Housekeeping (runs at end of every autonomous session)

1. **Trim action items** — any action in `all_pending_actions` older than 60 days → archive to `outputs/research/ppc-agent/state/action-archive-{YYYY}.json`
2. **Trim upcoming_reviews** — any review >14 days overdue → auto-expire with reason
3. **Trim session_log** — keep last 20, archive older
4. **Recompute `pending_summary` and `review_summary`** in agent-state
5. **Check cadence tracker** — set `next_due` dates based on today + frequency

---

## Step 11: Apply Session Actions (Interactive)

**Triggered when user says:** "apply items 1 and 3 from Tuesday", "apply actions from last session", "execute action ACT-2026-03-10-001"

This is an INTERACTIVE mode — the user is present and approving.

### 11a. Find the session

1. Parse the user's request for a date or day reference ("Tuesday" = most recent Tuesday, "last session" = most recent actions JSON)
2. Load the matching `*-actions.json` from `outputs/research/ppc-agent/sessions/`
3. If not found: "No session actions found for {date}. Available sessions: {list recent files}"

### 11b. Parse which actions to apply

- "all P1" → filter actions where priority = "P1"
- "items 1, 3, 5" → match by item number from the brief
- "apply all" → all actions
- Specific ID: "ACT-2026-03-10-001" → match by ID

### 11c. Present confirmation

For each action to be applied, show:
```
### Item {N}: {type} — {description}
**Portfolio:** {name} | **Campaign:** {campaign_name}
**Current:** {current_value} → **Proposed:** {proposed_value}
**Evidence:** {summary from evidence field}
**Risk:** {risk level}

Apply? (yes / skip / modify)
```

### 11d. Execute approved actions

Follow the same API call patterns as the Portfolio Action Plan (Step 6 execution). For each action:
1. Make the API call
2. Log result (success/failed)
3. Update the actions JSON: set `status: "applied"`, `applied_date: today`, `applied_by: "interactive"`
4. Update portfolio tracker `change_log`
5. Add to `upcoming_reviews` with validation date = today + 7 days

### 11e. Report results

```
## Execution Complete

| # | Action | Status | Details |
|---|--------|--------|---------|
| 1 | ... | SUCCESS | ... |

**Next:** These changes will be validated in the Friday/Tuesday session.
```

---

## Error Handling

| Issue | Response |
|-------|----------|
| `agent-state.json` missing | Create with all null dates |
| Sub-skill's SKILL.md missing | Tell user: "Skill {name} not created yet." |
| Sub-skill fails mid-run | Log failure, update LESSONS.md, inform user |
| Chain depth reaches 3 | Stop chaining, note in session summary |
| Context window running out | Save session object, suggest "continue next session" |
| Upstream data stale (>7 days) | Warn user, suggest running upstream skill first |
| Reports stuck PENDING | Use cached data, note in findings |
| Monday pipeline output missing | Note in brief, continue with available data. Never re-run skills. |
| Notion push fails | Log error, continue. Disk brief is source of truth. |
| Slack notification fails | Log error, continue. Never let notification failure break the session. |
| No previous session to validate | Skip Phase 2, note "First session — no validation history yet" |
| Action items JSON schema mismatch | Fall back to best-effort parsing, log warning |

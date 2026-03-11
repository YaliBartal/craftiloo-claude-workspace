---
name: ppc-portfolio-action-plan
description: Single-portfolio deep dive with impact-ranked action plan generation and execution
triggers:
  - portfolio deep dive
  - deep dive
  - portfolio action plan
  - fix portfolio
  - work on portfolio
output_location: outputs/research/ppc-agent/deep-dives/
---

# PPC Portfolio Action Plan

**USE WHEN** user says: "portfolio deep dive", "deep dive {portfolio}", "portfolio action plan", "fix {portfolio}", "work on {portfolio}"

**Also routed from PPC Agent** when user requests a portfolio-specific deep dive with actions.

---

## BEFORE YOU START -- Read Lessons

**MANDATORY FIRST STEP:** Read `LESSONS.md` in this skill's folder before doing anything else.

1. Read `.claude/skills/ppc-portfolio-action-plan/LESSONS.md`
2. Check **Known Issues** -- plan around these
3. Check **Repeat Errors** -- if you encounter one during this run, tell the user immediately: _"Repeat issue (xN): [description]"_
4. Apply all past lessons to this run

**Do NOT skip this step.**

---

## What This Does

A **mini-orchestrator** that takes a single portfolio through a complete cycle:

1. **Deep Dive Analysis** -- comprehensive portfolio assessment (campaigns, keywords, search terms, ranks, placement health, structure audit, profitability)
2. **Action Plan Generation** -- impact-ranked list of every improvement action available (bids, budgets, campaigns, negatives, pauses, enables, targets)
3. **User Approval** -- granular approve/reject/modify per action item, choose execution mode
4. **Execution** -- applies approved actions via Amazon Ads API directly
5. **Output & Logging** -- saves brief, snapshot, and action log

**Think of it as:** Portfolio Summary gives you the "what's wrong." This skill gives you "what's wrong + here's exactly how to fix it + let me do it for you."

---

## Organization & Efficiency Standards

### File Organization
```
outputs/research/ppc-agent/deep-dives/
  briefs/          # Deep dive + action plan briefs (user reads first)
  snapshots/       # Machine-readable portfolio state JSON
  action-logs/     # What was proposed, approved, executed, results
  README.md        # Folder guide
```

### Naming Conventions
- **Brief:** `YYYY-MM-DD-{portfolio-slug}-brief.md`
- **Snapshot:** `YYYY-MM-DD-{portfolio-slug}-snapshot.json`
- **Action log:** `YYYY-MM-DD-{portfolio-slug}-action-log.json`

### Efficiency Targets
- <120K tokens total (analysis + presentation + execution)
- <15 minutes execution (deep dive ~5-7 min, execution ~5-8 min)
- 3 output files per run (brief, snapshot, action log)

---

## Step 1: Identify Portfolio + Load Tracker

Ask the user which portfolio to analyze, or extract the portfolio name from their request.

**If ambiguous:** List all portfolios from `context/business.md` and let the user pick.

**Gather from `context/business.md`:**
- Portfolio stage (Launch / Scaling / General)
- ACoS target for that stage
- Hero ASIN(s) in portfolio
- ASIN-to-portfolio mapping

**Load the portfolio tracker** at `outputs/research/ppc-agent/state/{portfolio-slug}.json`:
- **If tracker exists:** Read it — this is your primary context. It contains goals, baseline, all previous changes, pending actions, scheduled reviews, and improvement history.
- **If tracker doesn't exist:** Create it with the skeleton structure (see ppc-agent SKILL.md for schema). Set `portfolio.stage` and `goals` from `context/business.md`.

**From the tracker, gather:**
- `goals` — ACoS/CVR targets, rank targets, strategic notes
- `baseline` — previous metrics (if set)
- `latest_metrics` — most recent snapshot
- `change_log` — what was already changed (avoid re-recommending)
- `pending_actions` — queued work from previous runs
- `scheduled_reviews` — upcoming re-checks
- `skills_run` — when this portfolio was last analyzed by this skill
- `improvement_assessment` — is the portfolio improving?

**Also read `agent-state.json`** for global context:
- `portfolio_index.{portfolio-slug}` — quick health status
- `global_pending_actions` — any cross-portfolio items

**If last action plan was <7 days ago** (check `skills_run` for last `ppc-portfolio-action-plan` entry): Warn user: "This portfolio was analyzed {N} days ago on {date}. Changes need time to show results. Run anyway?"

---

## Step 2: Deep Dive -- Data Collection

Pull data in 3 batches. Maximize parallel calls. Minimize redundant fetches.

### Batch 1: Context Files (parallel, no API calls)

Read ALL of these in parallel:

| File | Purpose | Required? |
|------|---------|-----------|
| `context/business.md` | Stage, targets, hero ASINs | Yes |
| `context/search-terms.md` | Protected terms for negation safety | Yes |
| `outputs/research/ppc-agent/state/agent-state.json` | Pending actions, last runs | Yes |
| Most recent `outputs/research/ppc-weekly/snapshots/*/summary.json` | Weekly baseline for WoW comparison | If <7d old |
| Most recent `outputs/research/ppc-agent/portfolio-summaries/*-portfolio-snapshot.json` | Previous portfolio summary | If exists |
| Most recent `outputs/research/ppc-agent/bids/*-bid-changes-applied.json` | Recent bid changes (avoid re-recommending) | If <7d old |
| Most recent `outputs/research/ppc-agent/search-terms/*-applied-actions.json` | Recent negatives (dedup) | If <14d old |
| Most recent `outputs/research/ppc-agent/rank-optimizer/snapshots/*/rank-spend-matrix.json` | Previous rank classifications | If exists |
| Most recent `outputs/research/negative-keywords/briefs/{portfolio-slug}*.md` | Proactive negative list (for campaign seeding) | If exists |

### Batch 2: API Calls (parallel where possible)

| # | Tool | Parameters | Purpose |
|---|------|-----------|---------|
| 2a | `list_portfolios` | `marketplace="US"` | Get portfolio ID + name mapping |
| 2b | `list_sp_campaigns` | `portfolio_id="{id}", state="ENABLED", marketplace="US"` | All enabled campaigns |
| 2c | `list_sp_campaigns` | `portfolio_id="{id}", state="PAUSED", marketplace="US"` | Paused campaigns (recovery candidates) |
| 2d | `create_ads_report` | `report_type="sp_campaigns", date_range="LAST_30_DAYS", marketplace="US"` | 30-day campaign performance |
| 2e | `create_ads_report` | `report_type="sp_search_terms", date_range="LAST_14_DAYS", marketplace="US"` | 14-day search term data |
| 2f | `create_ads_report` | `report_type="sp_placements", date_range="LAST_7_DAYS", marketplace="US"` | 7-day placement health |

**Important:** Split campaign list into ENABLED + PAUSED separately. Never use `state="ALL"` (returns 200+ archived campaigns first).

**Report polling:** After creating reports (2d, 2e, 2f), poll with `get_ads_report_status` every 15-20 seconds, max 2 minutes. If stuck in PENDING after 2 min, fall back to weekly snapshot data with staleness note.

**Re-check old report IDs:** Before creating new reports, check `agent-state.json` and recent action logs for report IDs from previous sessions (within 24h). Amazon reports stuck in PENDING often resolve after ~1 hour. Call `get_ads_report_status` on old IDs first — if COMPLETED, download directly and skip creating new reports. This saves API calls and avoids redundant report creation.

**30d data is MANDATORY for action planning.** If 30d campaign report is unavailable (PENDING or failed), DO NOT generate P1/P2 bid or TOS recommendations. Structural analysis alone is misleading — a 900% TOS campaign with zero spend is cleanup, not emergency. A 311% TOS campaign at 13.3% ACoS is a star performer. Without 30d data, limit action plan to P4 observations only and note: "Action plan deferred — 30d campaign data required for reliable recommendations."

### Batch 3: Dependent Calls (after Batch 2 resolves)

| # | Tool | Parameters | Purpose |
|---|------|-----------|---------|
| 3a | `list_sp_keywords` | `campaign_id="{id}", marketplace="US"` (per campaign) | All keywords with bids + match types |
| 3b | `list_sp_targets` | `campaign_id="{id}", marketplace="US"` (PT campaigns only) | Product/category targets |
| 3c | `list_sp_campaign_negative_keywords` | `campaign_id="{id}", marketplace="US"` (per campaign) | Existing negatives for dedup |
| 3d | `list_sp_product_ads` | `campaign_id="{id}", marketplace="US"` (per campaign) | ASINs + SKUs advertised |
| 3e | `get_rank_radar_data` | `rank_radar_id="{id}", start_date="{28d_ago}", end_date="{today}"` | 28-day rank history |
| 3f | `get_niche_keywords` | `niche_id="{id}", page_size=200` | Full keyword universe for gap analysis |
| 3g | `get_sales_detailed_7d_report` | (none) | Per-ASIN sales/profit/organic ratio |
| 3h | `get_sp_campaign_budget_usage` | `campaign_ids="{ids}", marketplace="US"` | Budget utilization classification |
| 3i-k | `download_ads_report` | `report_id="{2d/2e/2f}"` | Download the 3 reports |

**Rank radar identification:** Match portfolio's hero ASIN to a rank radar from `list_rank_radars()`. If no radar exists, skip rank analysis and note in brief.

**Search term filtering:** The search term report contains ALL account search terms. After download, filter to only campaigns in this portfolio by campaign ID.

**Token optimization:** If search term data is large (>300 rows for this portfolio), save to file and analyze in summary form. Don't dump raw data into conversation context.

---

## Step 3: Deep Dive -- Analysis & Brief

Build the brief following this exact section structure (proven in the March 2 Fuse Beads deep dive):

### Brief Structure

```markdown
# {Portfolio Name} -- Portfolio Action Plan
**Date:** {YYYY-MM-DD}
**Stage:** {Launch/Scaling/General} | **ACoS Target:** {X}% | **Red Flag:** >{Y}%
**Last Action Plan:** {date or "First run"}

---

## Executive Summary
{3-5 key findings. Lead with the single most important issue. Include health score out of 10.}

## ASINs in This Portfolio
| ASIN | Product | Role | 7d Sales | 7d Profit | Organic Ratio |
{hero, secondary, organic-only classification}

## 30-Day Performance Overview
| Metric | Value | Target | Status |
{Spend, Sales, ACoS, Orders, CVR, CPC, ROAS, Budget Utilization}
{Include WoW comparison if weekly snapshot available}

## Campaign-by-Campaign Breakdown
{Ranked by 30-day spend, highest first}
| # | Campaign | Type | 30d Spend | 30d Sales | ACoS | Orders | CVR | CPC | TOS% | Status |
{Status flags: BLEEDING / ABOVE TARGET / EFFICIENT / STAR / DORMANT / PAUSED}

## Portfolio Structure Health Score

**This section evaluates how well-structured the portfolio is — not just performance, but architecture.**

### Campaign Type Inventory
| Type | Required | Found | Status | 30d Spend | % of Portfolio |
|------|----------|-------|--------|-----------|----------------|
| Auto | 1 | {n} | OK / MISSING / EXCESS | $ | % |
| MK Broad | 1 | {n} | OK / MISSING / EXCESS | $ | % |
| SK (single keyword exact) | ~3+ (top KWs) | {n} | OK / LOW / EXCESS | $ | % |
| MK (root phrase) | ~2+ | {n} | OK / LOW | $ | % |
| PT (product targeting) | 1 | {n} | OK / MISSING | $ | % |
| Shield | 1 (if applicable) | {n} | OK / MISSING / N/A | $ | % |
| Low-bid Discovery | 1-2 | {n} | OK / MISSING | $ | % |

### Spend Distribution Assessment
| Metric | Value | Benchmark | Status |
|--------|-------|-----------|--------|
| MK Broad % of total spend | % | <30% ideal, >40% = cannibalization risk | OK / WARNING / CRITICAL |
| Auto % of total spend | % | <20% ideal, >35% = too much auto reliance | OK / WARNING / CRITICAL |
| SK % of total spend | % | >40% ideal (precise targeting) | OK / LOW / CRITICAL |
| Top 1 campaign % of spend | % | <35% ideal, >50% = over-concentration | OK / WARNING / CRITICAL |
| Single-keyword campaigns | {n} SK + {n} MK roots | More = better precision | COUNT |

**Healthy spend profile:** SK campaigns should capture the largest share of spend (40%+), followed by MK broad (15-30%), auto (10-20%), MK roots (10-15%), PT (5-10%). If auto+broad exceeds 50%, the portfolio is leaking — too much goes to uncontrolled matching.

### Campaign Gap Analysis
| Expected Campaign | Keyword / Target | Search Volume | Exists? | Action |
|-------------------|-----------------|---------------|---------|--------|
| SK {top keyword 1} | {keyword} | {SV} | YES / NO | — / CREATE |
| SK {top keyword 2} | {keyword} | {SV} | YES / NO | — / CREATE |
| SK {top keyword 3} | {keyword} | {SV} | YES / NO | — / CREATE |
| MK {root 1} | {root} | {combined SV} | YES / NO | — / CREATE |
| PT competitor | {ASINs} | — | YES / NO | — / CREATE |

{Cross-reference DataDive niche keywords (top 10 by SV) against existing SK campaigns. Every keyword with SV >3,000 that ranks top 20 should have a dedicated SK campaign.}

### Structure Health Grade

Score each dimension (0-10), then combine:

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| **Campaign type completeness** (all types present) | /10 | 25% | |
| **Spend distribution balance** (SK-dominant, not broad-heavy) | /10 | 25% | |
| **Keyword coverage** (top SV keywords have SK campaigns) | /10 | 25% | |
| **Single-targeting precision** (# of single-KW campaigns vs portfolio size) | /10 | 15% | |
| **Negative keyword hygiene** (campaigns have negatives, no cannibalization) | /10 | 10% | |
| **TOTAL** | | 100% | **/10** |

**Grading:**
- **9-10:** Excellent structure — focus on performance optimization only
- **7-8:** Good structure — minor gaps to fill
- **5-6:** Needs work — missing campaign types or poor spend distribution
- **3-4:** Structural problems — broad/auto dominating, key campaigns missing
- **1-2:** Rebuild needed — portfolio architecture is fundamentally wrong

**This grade feeds into the overall Health Score** alongside performance metrics. A portfolio can have good ACoS but terrible structure (e.g., all spend going through a single broad campaign with no SK isolation).

## TOS Strategy Audit
| Campaign | TOS% | Effective TOS Bid | TOS ACoS | ROS ACoS | PP ACoS | PP% | ROS% | Health |
{Health classifications: TOS_DOMINANT, TOS_EFFICIENT_ROS_BLEEDING, TOS_BLEEDING, ALL_EFFICIENT, ALL_BLEEDING, INSUFFICIENT_DATA}

## PP/ROS Placement Modifier Decision Framework

**CRITICAL: Adding PP/ROS modifiers is NOT a default recommendation.** Each campaign must be evaluated individually using placement data. Do NOT blanket-recommend "add PP +X% and ROS +Y% to all campaigns missing them."

### Required Data Before Any PP/ROS Recommendation

You MUST have at least ONE of these before recommending PP/ROS changes:
1. **Placement report data** (sp_placements) — shows per-placement ACoS, spend, sales, orders
2. **30d search term data with placement context** — shows which placements are converting
3. **Budget utilization data** — shows if campaign is spend-constrained

**If placement data is unavailable:** Do NOT recommend PP/ROS changes. Instead, flag as P4 Monitor: "Collect placement data before adjusting PP/ROS."

### Decision Matrix: When to ADD PP/ROS Modifiers (currently at 0%)

| Condition | Add PP/ROS? | Rationale |
|-----------|-------------|-----------|
| Campaign has TOS modifier, base bid is competitive (≥70% of Amazon rec), and is spending normally | **NO** | Base bid alone is winning non-TOS auctions. Adding modifiers would overpay. |
| Campaign has TOS modifier, base bid is low (<70% of Amazon rec), campaign is NOT spending, AND the campaign has proven TOS conversion data (ACoS ≤ target) | **MAYBE** | Low base bid may explain under-spending. But first check: is MK broad cannibalizing? Is there a structural issue? PP/ROS is only the fix if the campaign is truly being outbid on non-TOS. |
| Campaign is dormant (near-zero spend over 30d) with no other structural explanation | **INVESTIGATE FIRST** | Check for: paused ad groups, zero keywords, MK broad stealing traffic, irrelevant targeting. PP/ROS won't fix a structurally broken campaign. |
| Campaign is budget-capped (≥80% utilization) | **NO** | Adding PP/ROS increases reach but campaign can't afford more impressions. Fix budget first, then reassess. |
| New campaign (created this session) | **YES (conservative)** | Start with PP +10%, ROS +10% to test non-TOS performance. Revisit after 14d of data. |
| Portfolio stage is LAUNCH and campaign targets hero keywords | **YES (moderate)** | Launch needs maximum visibility. PP +15-25%, ROS +15-25% to drive impressions across all placements. |
| Placement data shows non-TOS placements are MORE efficient than TOS | **YES** | Lean into what's working. Set PP/ROS modifiers to shift spend toward efficient placements. |

### Decision Matrix: When to INCREASE Existing PP/ROS Modifiers

| Condition | Increase? | How Much |
|-----------|-----------|----------|
| PP/ROS placement ACoS is ≤80% of target AND campaign is NOT budget-capped | **YES** | +5-10pp incremental. Never more than +15pp in one change. |
| Campaign is performing well overall but non-TOS share is <30% of spend | **MAYBE** | Only if TOS is saturated (high impression share) and non-TOS is efficient. |
| Non-TOS ACoS is worse than TOS ACoS | **NO** | The current modifiers may already be too high. |

### Decision Matrix: When to DECREASE or REMOVE PP/ROS Modifiers

| Condition | Action | Rationale |
|-----------|--------|-----------|
| PP or ROS placement ACoS is >1.5x target | **Decrease by 10-20pp** | Non-TOS is bleeding. Reduce exposure. |
| PP or ROS placement ACoS is >2x target with significant spend | **Remove (set to 0%)** | Non-TOS is a waste channel for this campaign. |
| Campaign is overspending (ACoS above target) and non-TOS is the primary waste source | **Decrease or remove** | "Other on-Amazon" has no modifier — lowering default bid is the only lever. PP can be directly reduced. |

### PP/ROS Modifier Ranges by Context

| Context | PP Range | ROS Range | Notes |
|---------|----------|-----------|-------|
| Launch (hero keywords) | +15-25% | +15-25% | Maximum visibility |
| Scaling (proven converters) | +10-20% | +10-20% | Only if placement data supports |
| Mature (organic rank #1-3) | +0-10% | +0-10% | Organic handles most non-TOS traffic |
| New campaign (testing) | +10% | +10% | Conservative start, adjust after 14d |
| Dormant rescue (confirmed bid issue) | +10-15% | +10-15% | Only after ruling out structural issues |

### What PP/ROS Modifiers Do NOT Fix

- MK Broad cannibalizing SK campaigns → Fix with negatives, not modifiers
- Paused ad groups → Re-enable the ad group
- Zero keywords in campaign → Add keywords
- Low base bid on all placements → Raise base bid (affects ALL placements including TOS)
- "Other on-Amazon" waste → No modifier exists for this. Lower the default bid instead.

### Presentation Requirement for PP/ROS Actions

When proposing a PP/ROS change, the action item MUST include:
1. **Current modifiers:** TOS %, PP %, ROS % (or "none")
2. **Placement performance:** Per-placement ACoS/spend/orders if available, or "no placement data"
3. **Why this campaign specifically:** What evidence supports this change vs leaving as-is
4. **Alternative considered:** What else could explain the under-spending (if that's the motivation)

**Example of a GOOD PP/ROS recommendation:**
> "Add PP +15%, ROS +15% to SK latch hook kit. **Evidence:** Placement data shows TOS at 28% ACoS (35% target), PP at 31% ACoS, but PP gets only 8% of spend despite 40% of impressions. Base bid $0.34 is below Amazon rec $0.52 for non-TOS. Campaign is NOT budget-capped (23% utilization). No MK broad cannibalization detected."

**Example of a BAD PP/ROS recommendation (DO NOT DO THIS):**
> "Add PP +13%, ROS +18% to 7 campaigns missing modifiers. These campaigns are under-spending."

## Keyword Strategy Analysis
**Roots covered:** {list root words present across campaigns}
**Match type coverage:**
| Root | Auto | Broad | Exact (SK) | MK | Gap? |
**Missing roots:** {keywords with high search volume in niche but no campaign coverage}
**Total keywords:** {count} across {count} campaigns

## Rank Radar Analysis
{28-day trending table. Only include if rank radar data available.}
| Keyword | SV | Rank Now | 7d Ago | 14d Ago | 28d Ago | Trend | Alert |
{Trend: IMPROVING / STABLE / DECLINING / CRITICAL}
{Alert: flag drops of 5+ positions}

## Search Term Analysis
### Top Converters (14d)
| Search Term | Campaign | Clicks | Orders | ACoS | CVR | Action Opportunity |
{Top 10 by orders}

### Zero-Order Waste (14d)
| Search Term | Campaign | Clicks | Spend | CPC | Relevance | Recommendation |
{Top 10 by spend with 0 orders -- only if 30d+ data supports negation}

### Cannibalization Check
{Search terms appearing in 3+ campaigns within this portfolio}

## Product Targeting Analysis
| Target ASIN | Campaign | 30d Spend | Sales | ACoS | Bid | Status |
{Only if PT campaigns exist}

## Seller Board Context
| Metric | Value |
| 7d Revenue (total) | $ |
| 7d PPC Sales | $ |
| 7d Organic Sales | $ |
| Organic Ratio | % |
| Real ACoS (TACoS) | % |
| Margin | % |
| Sessions | |

## MK Broad Cannibalization Audit
**Standard check — run on EVERY portfolio that has a MK Broad campaign.**

| Metric | Value |
|--------|-------|
| MK Broad 30d Spend | $ |
| MK Broad % of Portfolio Spend | % |
| MK Broad ACoS | % |
| MK Broad Orders | |
| Overlapping SK Keywords | {list terms that appear in both MK broad search terms AND SK campaign targets} |

**Cannibalization signal:** If MK Broad is >30% of portfolio spend AND its search terms overlap with active SK campaigns, it's cannibalizing. The broad match is competing with its own exact-match SK campaigns, driving up CPCs for both.

**Action when detected:**
- `BID_DECREASE` on MK Broad TOS (reduce dominance)
- `BUDGET_DECREASE` on MK Broad (cap its share)
- Cross-check: are the SK campaigns getting enough impressions? If not, the broad is stealing them.

**This pattern is systemic.** Fairy Family MK Broad was 41% of spend at 46.2% ACoS, competing with SK campaigns on "kids sewing kit" and "kids sewing kits age 5-8". Check every portfolio for this.

## Structural Issues Summary
{Numbered list of root causes found across all sections above. Not just symptoms -- explain WHY each issue exists and its downstream impact.}
```

**Save the brief:** `outputs/research/ppc-agent/deep-dives/briefs/{YYYY-MM-DD}-{portfolio-slug}-brief.md`

**Save the snapshot:** `outputs/research/ppc-agent/deep-dives/snapshots/{YYYY-MM-DD}-{portfolio-slug}-snapshot.json`

Snapshot JSON structure:
```json
{
  "date": "YYYY-MM-DD",
  "portfolio": "{name}",
  "portfolio_id": "{id}",
  "stage": "{stage}",
  "acos_target": 30,
  "health_score": "6/10",
  "metrics_30d": {
    "spend": 0, "sales": 0, "acos": 0, "orders": 0,
    "cvr": 0, "cpc": 0, "roas": 0
  },
  "campaigns": [
    {
      "name": "", "campaign_id": "", "type": "SK",
      "state": "ENABLED", "spend_30d": 0, "sales_30d": 0,
      "acos": 0, "orders": 0, "cvr": 0, "cpc": 0,
      "tos_modifier": 0, "budget": 0, "budget_utilization": "",
      "status": "EFFICIENT"
    }
  ],
  "structure_audit": {
    "auto": 1, "broad": 0, "sk": 3, "mk": 2, "pt": 1,
    "missing": ["broad"], "complete": false,
    "spend_distribution": {
      "sk_pct": 0, "mk_broad_pct": 0, "auto_pct": 0,
      "mk_root_pct": 0, "pt_pct": 0, "other_pct": 0
    },
    "single_targeting_campaigns": 0,
    "structure_health_grade": "6/10",
    "structure_health_breakdown": {
      "type_completeness": 0, "spend_balance": 0,
      "keyword_coverage": 0, "targeting_precision": 0,
      "negative_hygiene": 0
    }
  },
  "rank_data": {
    "keywords_tracked": 0,
    "improving": 0, "stable": 0, "declining": 0, "critical": 0
  },
  "search_term_summary": {
    "total_terms": 0, "top_converters": 0,
    "zero_order_waste_spend": 0, "cannibalized_terms": 0
  },
  "seller_board": {
    "organic_ratio": 0, "tacos": 0, "margin": 0
  }
}
```

---

## Step 4: Generate Action Items

Analyze every section of the brief and generate ALL applicable actions. Cover every action type.

### Action Categories

| Category | Description | API Tool | Reversibility |
|----------|------------|----------|---------------|
| `BID_DECREASE` | Lower TOS modifier or default bid | `update_sp_campaigns` / `update_sp_ad_groups` | Easy |
| `BID_INCREASE` | Raise TOS modifier for rank defense or scaling | `update_sp_campaigns` | Easy |
| `BUDGET_INCREASE` | Increase daily budget (starved/scaling campaigns) | `update_sp_campaigns` | Easy |
| `BUDGET_DECREASE` | Reduce daily budget (bleeding campaigns) | `update_sp_campaigns` | Easy |
| `KEYWORD_PAUSE` | Pause bleeding keywords (requires 30d+ data) | `manage_sp_keywords(action="update")` | Easy |
| `KEYWORD_ADD` | Add keywords to existing campaigns | `manage_sp_keywords(action="create")` | Easy |
| `NEGATE_SEARCH_TERM` | Add negative exact to campaign (requires 30d+ data for zero-order) | `create_sp_campaign_negative_keywords` | Medium |
| `CAMPAIGN_CREATE` | Create new campaign (SK/MK/Auto/Broad/PT) | Full 5-step pipeline | Medium |
| `CAMPAIGN_PAUSE` | Pause a bleeding campaign (requires 30d+ data) | `update_sp_campaigns` | Easy |
| `CAMPAIGN_ENABLE` | Re-enable a paused campaign | `update_sp_campaigns` | Easy |
| `TARGET_ADD` | Add ASIN/category targets to PT campaigns | `manage_sp_targets(action="create")` | Easy |
| `CAMPAIGN_CONSOLIDATE` | Merge overlapping campaigns | Manual flag only -- no API | N/A |
| `CAMPAIGN_ARCHIVE` | Archive dormant/dead campaigns (30d+ idle) | `update_sp_campaigns` | Hard |

### Where Each Category Comes From

| Brief Section | Potential Actions |
|--------------|-------------------|
| Campaign Breakdown (bleeding campaigns) | `BID_DECREASE`, `BUDGET_DECREASE`, `CAMPAIGN_PAUSE` |
| Campaign Breakdown (star performers) | `BUDGET_INCREASE`, `BID_INCREASE` |
| Portfolio Structure Health (gaps) | `CAMPAIGN_CREATE` |
| Portfolio Structure Health (spend imbalance) | `BID_DECREASE` / `BUDGET_DECREASE` (on over-dominant campaigns) |
| TOS Strategy Audit (TOS bleeding) | `BID_DECREASE` (TOS modifier) |
| TOS Strategy Audit (efficient but low TOS) | `BID_INCREASE` (TOS modifier) |
| PP/ROS Decision Framework (under-spending, placement data supports) | `BID_INCREASE` (PP/ROS modifier) — only after ruling out structural causes |
| PP/ROS Decision Framework (non-TOS bleeding) | `BID_DECREASE` (PP/ROS modifier) or remove |
| Keyword Strategy (gaps) | `KEYWORD_ADD`, `CAMPAIGN_CREATE` (MK) |
| Rank Radar (declining keywords) | `BID_INCREASE` (rank defense) |
| Search Terms (zero-order waste) | `NEGATE_SEARCH_TERM` |
| Search Terms (top converters without SK) | `CAMPAIGN_CREATE` (SK EXACT) |
| Search Terms (cannibalization) | `NEGATE_SEARCH_TERM` (in lower-priority campaign) |
| MK Broad Cannibalization Audit | `BID_DECREASE` (TOS), `BUDGET_DECREASE` (cap share), flag SK impression starvation |
| Product Targeting (bleeding targets) | `BID_DECREASE` on target bid, or remove |
| Seller Board (low organic ratio) | Flag -- may need listing work, not PPC fix |
| Paused Campaigns | `CAMPAIGN_ENABLE` (if conditions allow) |
| Budget Utilization (starved) | `BUDGET_INCREASE` |
| Dormant campaigns | `CAMPAIGN_ARCHIVE` |

### Impact Scoring (0-100)

Score each action item:

| Factor | Weight | Scoring |
|--------|--------|---------|
| **Financial impact** | 35 pts | Est. weekly $ impact: >$50/wk = 35, $25-50 = 25, $10-25 = 15, <$10 = 8 |
| **Rank impact** | 25 pts | Hero keyword defense = 25, rank opportunity = 18, secondary keyword = 12, no rank signal = 5 |
| **Urgency** | 20 pts | Bleeding/emergency = 20, above-target = 14, optimization = 8, cleanup = 4 |
| **Confidence** | 15 pts | 30d+ data = 15, 14d data = 10, 7d data = 7, inferred/estimated = 4 |
| **Reversibility** | 5 pts | Bid/budget change = 5, keyword pause = 4, campaign pause = 3, negate = 2, archive = 1 |

### Priority Grouping

| Priority | Criteria | Action |
|----------|----------|--------|
| **P1 -- Critical** | Score >= 70 OR any emergency flag | Execute ASAP |
| **P2 -- Optimization** | Score 45-69 | Execute if time allows |
| **P3 -- Maintenance** | Score 25-44 | Queue for next run |
| **P4 -- Monitor** | Score < 25 or insufficient data | No API action, observation only |

### Presentation Format

Append the action plan to the brief:

```markdown
---

## Action Plan -- {N} Items (Impact-Ranked)

### P1 -- Critical ({count} items, est. ${X}/week impact)

| # | Score | Category | Action | Campaign | 30d Evidence | Current | Proposed | Est. Weekly Impact |
|---|-------|----------|--------|----------|-------------|---------|----------|--------------------|
| 1 | 87 | BID_DECREASE | Lower TOS modifier | SK fuse beads TOS | $420 spend, $198 sales, 46% ACoS, 9 orders, 6.2% CVR | TOS 895% | TOS 347% | -$21/wk waste |
| 2 | 82 | BUDGET_INCREASE | Increase budget | SK fairy sewing kit | $24 spend, $181 sales, 13.3% ACoS, 8 orders, 29.6% CVR | $20/d | $31/d | +$5-10/wk profitable spend |

**30d Evidence column is MANDATORY for P1/P2.** Every bid/TOS/budget recommendation must show the campaign's 30d spend, sales, ACoS, orders, and CVR. The user needs this data to make an informed decision.

**P1 rationale:** {1-2 sentences on why these are critical}

### P2 -- Optimization ({count} items, est. ${X}/week impact)

| # | Score | Category | Action | Campaign | 30d Evidence | Current | Proposed | Est. Weekly Impact |
{same format}

### P3 -- Maintenance ({count} items)

| # | Score | Category | Action | Campaign | Current | Proposed | Est. Weekly Impact | Confidence |
{same format}

### P4 -- Monitor Only ({count} items)
{Description-only list, no API actions}
- {keyword/campaign} -- {what to watch for} -- {re-evaluate in N days}

### Dependencies
{List any actions that depend on other actions}
- Item {X} depends on Item {Y}: "{description}"
```

### 30d Data Gate (MANDATORY)

**Every BID_DECREASE, BID_INCREASE, BUDGET_DECREASE, or TOS recommendation MUST include 30d per-campaign evidence:**
- 30d Spend, 30d Sales, 30d ACoS, 30d Orders, 30d CVR
- Without this data, the action CANNOT be ranked P1 or P2 — downgrade to P4 Monitor

**Why this is non-negotiable:** In the Fairy Family run (2026-03-03), structural analysis alone produced 3 wrong P1 items out of 5. Two 900% TOS campaigns appeared as emergencies but had $0 spend (completely dead). The best performer at 311% TOS and 13.3% ACoS was flagged for TOS reduction — the user correctly identified this as wrong.

### Top Performer Protection Rule

**Never recommend lowering TOS or bid on a campaign with ACoS below 20% (Scaling) or below the portfolio's ACoS target (any stage).** These campaigns are working — the correct action is usually `BUDGET_INCREASE` to let them spend more, not bid reduction. If the TOS looks high, check the effective ACoS first. A 311% TOS at 13.3% ACoS is a star performer, not an over-bidder.

### Global PPC Rules Check

Before presenting, verify EVERY action against the 3 global rules + 2 portfolio-specific rules:

1. **No pause on single-week zero conversions.** Any `KEYWORD_PAUSE` or `CAMPAIGN_PAUSE` must show 30d+ data backing. If only 7d data available, downgrade to P4 Monitor.
2. **No round bid amounts.** Every bid value must be irregular: $0.73 not $0.70, -31% not -30%, TOS 347% not 350%.
3. **No negation on single-week zero conversions.** Any `NEGATE_SEARCH_TERM` must show 30d+ sustained zero conversions or clear irrelevance. If only 14d data, add confidence caveat.
4. **No bid/TOS recommendations without 30d data.** Every P1/P2 action item must cite 30d per-campaign metrics. If only weekly/7d data available, downgrade to P3/P4.
5. **No TOS/bid reduction on campaigns below ACoS target.** If ACoS < target, recommend BUDGET_INCREASE instead of BID_DECREASE. Flag to user with data.

Adjust any proposed values to comply. Flag to user if you had to modify a recommendation.

---

## Step 5: User Approval

Present the full brief + action plan, then show:

```markdown
---

## Your Call

**{N} actions identified across {count} priorities.**

| Option | Description |
|--------|-------------|
| **Approve all P1** | Execute {count} critical items now |
| **Approve P1 + P2** | Execute {count} critical + optimization items |
| **Approve specific** | "approve 1, 3, 5" (by item number) |
| **Modify** | "change item 2 TOS to 400%" (I'll adjust and confirm) |
| **Save brief only** | No API changes -- save analysis for reference |

**Execution mode:**
| Mode | Description |
|------|-------------|
| **Step-by-step** (default) | I confirm each action before executing, show result, then ask about next |
| **Auto-execute** | I run all approved items in sequence, report results at the end |

What would you like to do?
```

**Do NOT execute anything without explicit user approval.**

### Handling Modifications

If user says "change item 2 TOS to 400%":
1. Update the proposed value
2. Recalculate estimated impact
3. Confirm: "Updated Item 2: TOS 895% -> 400% (was 350%). Est. impact adjusted to -$18/wk. Proceed?"
4. Log modification in action log: `"user_modification": "TOS 350% -> 400%"`

### Handling Rejections

If user says "skip 3, 5":
1. Mark those items as `SKIPPED` in internal tracking
2. Check if any other items depend on them -- if so, note: "Item {X} depends on skipped Item {Y} -- also skipping {X}."
3. Confirm the final execution list

---

## Step 6: Execution

### Execution Order (dependencies matter)

Execute in this strict sequence:

1. **CAMPAIGN_ENABLE** -- Re-enable paused campaigns first (must exist before other actions can target them)
2. **CAMPAIGN_CREATE** -- New campaigns (must exist before keywords/targets/negatives can be added)
3. **BUDGET_INCREASE / BUDGET_DECREASE** -- Set budget limits before bid changes
4. **BID_DECREASE / BID_INCREASE (TOS modifiers)** -- Placement-level bid adjustments
5. **BID_DECREASE / BID_INCREASE (default bids)** -- Ad group-level bid adjustments
6. **KEYWORD_PAUSE** -- Pause bleeding keywords
7. **KEYWORD_ADD** -- Add new keywords to existing campaigns
8. **NEGATE_SEARCH_TERM** -- Add negative keywords (including cross-campaign negatives for promoted terms)
9. **TARGET_ADD** -- Add ASIN/category targets
10. **CAMPAIGN_PAUSE / CAMPAIGN_ARCHIVE** -- Destructive actions last

### API Call Patterns

**BID_DECREASE / BID_INCREASE (TOS modifier only):**
```
update_sp_campaigns(
  campaigns=[{
    "campaignId": "{id}",
    "dynamicBidding": {
      "strategy": "LEGACY_FOR_SALES",
      "placementBidding": [
        {"placement": "PLACEMENT_TOP", "percentage": {new_tos_pct}}
      ]
    }
  }],
  marketplace="US"
)
```

**BID_INCREASE / BID_DECREASE (PP/ROS modifiers — requires decision framework approval):**
```
update_sp_campaigns(
  campaigns=[{
    "campaignId": "{id}",
    "dynamicBidding": {
      "strategy": "LEGACY_FOR_SALES",
      "placementBidding": [
        {"placement": "PLACEMENT_TOP", "percentage": {tos_pct}},
        {"placement": "PLACEMENT_PRODUCT_PAGE", "percentage": {pp_pct}},
        {"placement": "PLACEMENT_REST_OF_SEARCH", "percentage": {ros_pct}}
      ]
    }
  }],
  marketplace="US"
)
```

**BID_DECREASE / BID_INCREASE (default bid):**
```
update_sp_ad_groups(
  ad_groups=[{"adGroupId": "{id}", "defaultBid": {new_bid}}],
  marketplace="US"
)
```

**BUDGET_INCREASE / BUDGET_DECREASE:**
```
update_sp_campaigns(
  campaigns=[{"campaignId": "{id}", "budget": {"budget": {amount}, "budgetType": "DAILY"}}],
  marketplace="US"
)
```

**KEYWORD_PAUSE:**
```
manage_sp_keywords(
  action="update",
  keywords=[{"keywordId": "{id}", "state": "PAUSED"}],
  marketplace="US"
)
```

**KEYWORD_ADD:**
```
manage_sp_keywords(
  action="create",
  keywords=[{
    "campaignId": "{id}", "adGroupId": "{id}",
    "keywordText": "{keyword}", "matchType": "{EXACT/BROAD}",
    "bid": {bid_amount}, "state": "ENABLED"
  }],
  marketplace="US"
)
```

**NEGATE_SEARCH_TERM:**
```
create_sp_campaign_negative_keywords(
  keywords=[{
    "campaignId": "{id}", "keywordText": "{term}",
    "matchType": "NEGATIVE_EXACT", "state": "ENABLED"
  }],
  marketplace="US"
)
```
Batch max 100 per call.

**CAMPAIGN_CREATE (full pipeline -- follow Campaign Creator Steps 7a-7e):**

### Campaign Creation Approval Card (MANDATORY)

**Before executing ANY campaign creation, present this card to the user and wait for explicit approval. Do NOT create the campaign until the user says yes.**

```markdown
---

## New Campaign Proposal

### Why This Campaign?
{2-3 sentences explaining the strategic rationale. What gap does it fill? What evidence supports it?}

| | |
|---|---|
| **Evidence** | {e.g., "Search term 'lacing cards' converts at 13.7% ACoS, 18.5% CVR across 14 orders in Auto/MK broad. No dedicated SK exists."} |
| **Source signal** | {PROMOTE from search terms / Rank defense / Structure gap / Keyword opportunity} |

---

### Campaign Settings

| Setting | Value | Rationale |
|---------|-------|-----------|
| **Name** | `{SOP name}` | {naming convention} |
| **Type** | SK Exact / MK Broad / Auto / PT | {why this match type} |
| **Portfolio** | {portfolio name} ({portfolio_id}) | |
| **Targeting** | MANUAL / AUTO | |
| **State** | PAUSED (user enables) | |
| **Daily Budget** | ${amount} | {stage default or custom — explain if custom} |
| **Bidding Strategy** | LEGACY_FOR_SALES | Fixed bids + down only |
| **Start Date** | {YYYY-MM-DD} | |

### Placement Modifiers

| Placement | Modifier | Rationale |
|-----------|----------|-----------|
| **TOS** | {X}% | {source: PROMOTE 47% / rank defense 63% / gap fill 41% / new KW 33%} |
| **Product Page** | {X}% | {from PP/ROS defaults table — explain why this level} |
| **Rest of Search** | {X}% | {from PP/ROS defaults table — explain why this level} |

### Ad Group

| Setting | Value |
|---------|-------|
| **Name** | `{campaign_name} - Ad Group` |
| **Default Bid** | ${bid} |
| **Bid source** | {how bid was calculated: Amazon rec, CPC from search term data, manual} |

### Product Ads

| ASIN | SKU | Product | Role |
|------|-----|---------|------|
| {ASIN} | {SKU} | {product name} | Hero / Secondary |

### Keywords (manual campaigns only)

| Keyword | Match Type | Bid | Search Volume | Current Rank | Evidence |
|---------|-----------|-----|---------------|-------------|----------|
| {keyword} | EXACT / BROAD | ${bid} | {SV} | #{rank} or "unranked" | {where this KW was validated — search terms, niche keywords, rank radar} |

### Negative Keywords (seeded)

| Source | Count | Examples |
|--------|-------|---------|
| Proactive negative list | {N} | {top 3-5 examples} |
| Cross-campaign isolation | {N} | {terms negated to prevent cannibalization — list all} |
| **Total negatives** | {N} | |

### Risk Assessment

| Risk | Level | Mitigation |
|------|-------|-----------|
| Cannibalization with existing campaigns | LOW / MED / HIGH | {what negatives/isolation is in place} |
| Budget impact on portfolio | LOW / MED / HIGH | {total portfolio budget before/after} |
| Keyword overlap with other portfolios | LOW / MED / HIGH | {any cross-portfolio concerns} |

---

**Create this campaign?** (yes / modify / skip)
```

**Rules:**
- Every field must be filled — no "TBD" or "N/A" unless truly not applicable (e.g., keywords for Auto campaigns)
- If multiple campaigns are being created in one session, present each card separately
- User modifications to any field must be confirmed before proceeding
- If user modifies bid/budget/TOS, recalculate effective bids and update the card before creating

Step A -- Create campaign:
```
create_sp_campaigns(
  campaigns=[{
    "name": "{SOP naming convention}",
    "portfolioId": "{portfolio_id}",
    "targetingType": "MANUAL" (or "AUTO"),
    "state": "PAUSED",
    "dynamicBidding": {
      "strategy": "LEGACY_FOR_SALES",
      "placementBidding": [{"placement": "PLACEMENT_TOP", "percentage": {tos_pct}}]
    },
    "budget": {"budget": {amount}, "budgetType": "DAILY"},
    "startDate": "{YYYY-MM-DD}"
  }],
  marketplace="US"
)
```
Extract `campaignId` from response.

Step B -- Create ad group:
```
create_sp_ad_groups(
  ad_groups=[{
    "campaignId": "{new_campaign_id}",
    "name": "{campaign_name} - Ad Group",
    "defaultBid": {bid},
    "state": "ENABLED"
  }],
  marketplace="US"
)
```
Extract `adGroupId`.

Step C -- Create product ads:
```
manage_sp_product_ads(
  action="create",
  product_ads=[{
    "campaignId": "{id}", "adGroupId": "{id}",
    "asin": "{ASIN}", "sku": "{SKU}", "state": "ENABLED"
  }],
  marketplace="US"
)
```
**SKU required.** Get from `list_sp_product_ads` on existing campaigns in this portfolio. If unavailable, use `get_my_listings` from SP-API.

Step D -- Create keywords (manual campaigns only):
```
manage_sp_keywords(
  action="create",
  keywords=[{
    "campaignId": "{id}", "adGroupId": "{id}",
    "keywordText": "{keyword}", "matchType": "{EXACT/BROAD}",
    "bid": {bid}, "state": "ENABLED"
  }],
  marketplace="US"
)
```

Step E -- Seed negative keywords:
Load from proactive negative list (`outputs/research/negative-keywords/briefs/{portfolio-slug}*.md`).
Apply as campaign-level `NEGATIVE_PHRASE`.

**Campaign naming conventions (SOP):**
| Type | Pattern | Example |
|------|---------|---------|
| SK exact | `{product} - SPM SK {keyword} TOS` | `Fuse Beads - SPM SK perler beads bulk TOS` |
| MK broad | `{product} - SPM MK {root} TOS` | `Fuse Beads - SPM MK fuse beads TOS` |
| Broad | `{product} - SPM MK Broad TOS` | `Fuse Beads - SPM MK Broad TOS` |
| Auto | `{product} - SPA Auto` | `Fuse Beads - SPA Auto` |
| PT | `{product} - manual - product targeting` | `Fuse Beads - manual - product targeting` |

**Budget defaults by stage:**
| Stage | SK/MK | Broad/Auto | PT |
|-------|-------|------------|-----|
| Launch | $15/day | $15/day | $10/day |
| Scaling | $10/day | $10/day | $8/day |
| General | $8/day | $8/day | $5/day |

**TOS modifier defaults by source:**
| Source | Starting TOS % |
|--------|----------------|
| From search term PROMOTE | 47% |
| Rank defense (declining keyword) | 63% |
| Structure gap fill | 41% |
| New keyword opportunity | 33% |

**PP/ROS modifier defaults for new campaigns (see PP/ROS Decision Framework for existing campaigns):**
| Stage | PP % | ROS % | Notes |
|-------|------|-------|-------|
| Launch (hero keywords) | 15% | 15% | Maximum visibility across placements |
| Scaling (proven converters) | 10% | 10% | Conservative start, adjust after 14d with placement data |
| General/new keyword | 10% | 10% | Conservative start, adjust after 14d with placement data |
| Discovery/testing | 0% | 0% | Let TOS drive initial data before expanding |

**All campaigns created in PAUSED state.** User enables manually.

**CAMPAIGN_PAUSE / CAMPAIGN_ENABLE / CAMPAIGN_ARCHIVE:**
```
update_sp_campaigns(
  campaigns=[{"campaignId": "{id}", "state": "{PAUSED/ENABLED/ARCHIVED}"}],
  marketplace="US"
)
```

**TARGET_ADD:**
```
manage_sp_targets(
  action="create",
  targets=[{
    "campaignId": "{id}", "adGroupId": "{id}",
    "expressionType": "MANUAL",
    "expression": [{"type": "ASIN_SAME_AS", "value": "{ASIN}"}],
    "bid": {bid}, "state": "ENABLED"
  }],
  marketplace="US"
)
```

### Batching

Where possible, batch multiple changes of the same type into a single API call:
- Multiple budget changes -> one `update_sp_campaigns` call with array
- Multiple bid changes on same campaign -> combine into one call
- Multiple negatives -> batch up to 100 per `create_sp_campaign_negative_keywords` call

### Dependency Handling

- If action A depends on action B (e.g., "negate keyword in source" depends on "create SK campaign"), and B was rejected or failed, **skip A** and note: "Skipped Item {A}: depends on rejected/failed Item {B}"
- If a campaign creation partially succeeds (campaign created but ad group failed), log the campaign ID for manual cleanup, mark as PARTIAL

### Error Handling

| Situation | Response |
|-----------|----------|
| API call fails (400/403) | Log failure, mark action FAILED, continue to next independent action, skip dependents |
| API call fails (429/500) | Wait 5s, retry once. If still fails, mark FAILED |
| Campaign creation partial (campaign OK, ad group fail) | Log campaign ID, mark PARTIAL, note for manual cleanup |
| SKU not found for product ad | Try `get_my_listings` from SP-API. If fails, create campaign without product ad, flag: "Campaign {name} needs product ad added manually" |
| Batch size exceeded | Auto-split into batches of 100 (negatives) or 10 (campaigns) |

### Step-by-Step Mode UX

Before each action:
```markdown
### Executing Item {N} of {total}: {CATEGORY} (Score: {score})

**Action:** {description}
**Campaign:** {name} (ID: {id})
**Current:** {current_value}
**Proposed:** {proposed_value}
**API call:** {tool_name} -> {key parameter}

**Proceed?** (yes / skip / modify / stop)
```

After each action:
```markdown
**Result:** SUCCESS / FAILED / PARTIAL
- {What changed, with before/after values}

**Next:** Item {N+1} of {total}: {category}...
```

### Auto-Execute Mode UX

Run all approved items in sequence. Present a final summary:
```markdown
## Execution Complete

| # | Action | Status | Details |
|---|--------|--------|---------|
| 1 | BID_DECREASE: SK fuse beads TOS 895%->347% | SUCCESS | TOS modifier updated |
| 2 | CAMPAIGN_CREATE: SK perler beads bulk | SUCCESS | Campaign ID: 123456, PAUSED |
| 3 | NEGATE_SEARCH_TERM: "kids craft set" in Auto | FAILED | API error: 429 rate limit |

**Summary:** {success}/{total} actions completed. {failed} failed. {skipped} skipped.
**Estimated weekly impact:** ${X} savings / ${Y} additional spend
```

---

## Step 7: Save Outputs + Update Portfolio Tracker

### 7a. Update Portfolio Tracker

Update the portfolio's tracker file at `outputs/research/ppc-agent/state/{portfolio-slug}.json`:

1. **`baseline`** — If `null` (first deep dive for this portfolio), set it now from the 30d metrics:
   ```json
   "baseline": {
     "date": "YYYY-MM-DD",
     "acos": 0, "spend_30d": 0, "sales_30d": 0, "orders_30d": 0,
     "cvr": 0, "cpc": 0, "roas": 0, "rank_top10": 0, "rank_top50": 0
   }
   ```
   **Baseline is write-once.** Never overwrite an existing baseline.

2. **`latest_metrics`** — Update with fresh data from this deep dive:
   ```json
   "latest_metrics": {
     "date": "YYYY-MM-DD",
     "acos": 0, "spend_30d": 0, "sales_30d": 0, "orders_30d": 0,
     "cvr": 0, "cpc": 0, "roas": 0, "rank_top10": 0, "rank_top50": 0,
     "health_score": "6/10",
     "delta_vs_baseline": { "acos": -2.1, "orders_30d": +5 }
   }
   ```

3. **`metric_history`** — Append new entry (max 90 entries, trim oldest if exceeded)

4. **`change_log`** — Append entry for every executed action:
   ```json
   {
     "date": "YYYY-MM-DD",
     "source": "ppc-portfolio-action-plan",
     "summary": "{N} actions executed",
     "changes": [
       {"category": "BID_DECREASE", "campaign": "{name}", "old": "TOS 895%", "new": "TOS 347%", "status": "success"}
     ]
   }
   ```

5. **`pending_actions`** — Mark completed items, add new P3/P4 items for future attention

6. **`scheduled_reviews`** — Add re-check date (typically 7 days after deep dive)

7. **`skills_run`** — Append: `{"skill": "ppc-portfolio-action-plan", "date": "YYYY-MM-DD", "result": "success/partial/failed", "key_metrics": {"health_score": "6/10", "actions_executed": N, "actions_proposed": N}}`

8. **`improvement_assessment`** — Update if baseline exists:
   - Compare `latest_metrics` vs `baseline` using weights: ACoS (35%), rank_top10 (25%), CVR (20%), orders (20%)
   - Direction: `improving` (>5% better), `stable` (within 5%), `declining` (>5% worse)
   - Confidence: `high` (14+ days history), `medium` (7-13 days), `low` (<7 days)

9. **`goals`** — Update `rank_targets`, `strategic_notes` if the deep dive revealed new targets

10. **`portfolio`** — Fill in `hero_asins`, `hero_keywords`, `niche_id`, `rank_radar_id`, `campaigns_enabled`, `campaigns_paused` if they were null

### 7b. Action Log (JSON)

Save to `outputs/research/ppc-agent/deep-dives/action-logs/{YYYY-MM-DD}-{portfolio-slug}-action-log.json`:

```json
{
  "date": "YYYY-MM-DD",
  "portfolio": "{name}",
  "portfolio_id": "{id}",
  "stage": "{stage}",
  "execution_mode": "step_by_step / auto_execute",
  "analysis_summary": {
    "campaigns_analyzed": 0,
    "keywords_analyzed": 0,
    "search_terms_analyzed": 0,
    "rank_keywords_tracked": 0,
    "health_score": "6/10"
  },
  "actions": [
    {
      "item_number": 1,
      "impact_score": 87,
      "priority": "P1",
      "category": "BID_DECREASE",
      "description": "Lower SK fuse beads TOS modifier",
      "campaign_id": "",
      "campaign_name": "",
      "current_value": {},
      "proposed_value": {},
      "estimated_weekly_impact": 0,
      "data_confidence": "30d",
      "depends_on": null,
      "user_decision": "approved / rejected / modified",
      "user_modification": null,
      "execution_status": "success / failed / partial / skipped",
      "api_call": "",
      "api_response": "",
      "executed_at": ""
    }
  ],
  "summary": {
    "total_actions": 0,
    "approved": 0,
    "rejected": 0,
    "skipped_dependency": 0,
    "executed_success": 0,
    "executed_partial": 0,
    "executed_failed": 0,
    "estimated_weekly_impact": 0,
    "actual_api_calls": 0
  }
}
```

### 7c. Update Agent State

Update `outputs/research/ppc-agent/state/agent-state.json`:

1. **Update `portfolio_index.{portfolio-slug}`:**
   - `last_deep_dive`: today's date
   - `last_updated`: today's date
   - `health_status`: from deep dive assessment (GREEN/YELLOW/RED)
   - `pending_count`: count of pending actions in the portfolio tracker
   - `next_review`: from scheduled_reviews in the portfolio tracker
2. **Mark completed** any `global_pending_actions` related to this portfolio that were addressed
3. **Add new** `global_pending_actions` only for cross-portfolio items (portfolio-specific items go in the tracker)

---

## Step 8: Present Results to User

After execution (or after saving brief-only):

```markdown
## Portfolio Action Plan Complete

**Portfolio:** {name} | **Date:** {date}
**Health Score:** {X}/10

### Results
- **Actions proposed:** {N}
- **Approved:** {N} | **Executed:** {N} success, {N} failed, {N} skipped
- **Estimated weekly impact:** ${X}

---

### Action Items Summary (P1 / P2 / P3)

**MANDATORY: Always include this section.** The user should never have to ask "what are the action items?" — they're right here with full context.

#### P1 — Critical (execute ASAP)

For each P1 item, include ALL of these:

| # | Category | Action | Campaign | Score |
|---|----------|--------|----------|-------|
| {n} | {BID_DECREASE / BUDGET_INCREASE / etc.} | {what was done or needs doing} | {campaign name} | {impact score} |

**Per-item detail (REQUIRED for every P1):**

> **Item {N}: {Action title}**
> - **What:** {1-sentence description of the change}
> - **Why:** {Strategic rationale — what problem does this solve? What evidence supports it?}
> - **Data:** {30d spend, sales, ACoS, orders, CVR for the affected campaign}
> - **Before → After:** {specific values changed, e.g., TOS 895% → 347%, budget $20/d → $31/d}
> - **Expected impact:** {estimated $/week savings or additional profitable spend}
> - **Status:** {EXECUTED / APPROVED-PENDING / DEFERRED / FAILED — with detail if failed}

#### P2 — Optimization (execute if time allows)

Same per-item format as P1. Include data backing for every recommendation.

> **Item {N}: {Action title}**
> - **What / Why / Data / Before → After / Expected impact / Status**

#### P3 — Maintenance (queued for next run)

For P3 items, a shorter format is acceptable but still include the "why":

| # | Category | Action | Campaign | Why | When |
|---|----------|--------|----------|-----|------|
| {n} | {category} | {description} | {campaign} | {1-sentence rationale + key data point} | {suggested timing: "next deep dive", "7-day re-check", "after P1 results settle"} |

#### P4 — Monitor Only (no action, observation)

- {keyword/campaign} — {what to watch for} — {re-evaluate in N days}

---

### Pending Actions Carried Forward

{List any P2/P3/P4 items that were NOT executed this session, with their priority and suggested timing. These get written to the portfolio tracker's `pending_actions` field.}

| # | Priority | Action | Suggested Timing | Notes |
|---|----------|--------|-----------------|-------|
| {n} | P2/P3 | {description} | {date or trigger condition} | {any context needed for the future run} |

---

### Files Saved
- Brief: `outputs/research/ppc-agent/deep-dives/briefs/{filename}`
- Snapshot: `outputs/research/ppc-agent/deep-dives/snapshots/{filename}`
- Action Log: `outputs/research/ppc-agent/deep-dives/action-logs/{filename}`

### Next Steps
- {Recommended follow-up: e.g., "Re-check in 7 days", "Run bid review in 3 days", "Monitor rank on {keyword}"}
- {Any failed actions that need manual attention}

### Lessons Update
{Brief note on what was logged to LESSONS.md}
```

---

## Edge Cases

### Portfolio has no campaigns
- Skip campaign/keyword/search term analysis
- Note: "This portfolio has 0 enabled campaigns."
- Generate `CAMPAIGN_CREATE` actions only: Auto + Broad + SK for top 3 keywords from DataDive niche keywords
- These score as P1 (structure gap = high urgency)

### No rank radar data available
- Skip Rank Radar Analysis section entirely
- Note: "No DataDive rank radar found for this portfolio's hero ASIN. Rank-based actions (PROTECT, rank defense) cannot be generated."
- Redistribute rank scoring weight (25 pts) proportionally to financial impact + urgency
- Recommend: "Consider adding a Rank Radar for ASIN {X} in DataDive for future runs"

### API failure mid-execution
- Log failure, continue to next independent action, skip dependents
- At end, present summary with failed items highlighted
- Offer: "Retry failed actions? (yes / skip)"

### Large portfolio (>15 campaigns)
- Warn: "This portfolio has {N} campaigns. Full analysis may approach token limits."
- Proceed normally but save intermediate data to files rather than holding in context
- If token limits approached, save brief and action plan, offer: "Analysis complete. Run execution in a follow-up session?"

### All campaigns paused
- Means portfolio was intentionally frozen (OOS, seasonal, etc.)
- Check `context/business.md` for notes on why
- Present current state, check if re-enable conditions are met
- Generate `CAMPAIGN_ENABLE` actions with conservative bid levels

### Recent action plan exists (<7 days)
- Warn user about the gap
- If user proceeds, focus on: what changed since last run, any failed actions from last run, new issues
- Load previous action log for comparison

---

## Step 9: Slack Notification

**Skip this step.** The PPC Agent orchestrator handles Slack notifications via Step 8e after every sub-skill completes.

---

## AFTER EVERY RUN -- Update Lessons (MANDATORY)

**Before presenting final results, update `.claude/skills/ppc-portfolio-action-plan/LESSONS.md`.**

### 1. Write a Run Log Entry

Add a new entry at the **TOP** of the Run Log section:

```
### Run: YYYY-MM-DD -- {Portfolio Name}
**Goals:**
- [ ] Deep dive analysis
- [ ] Action plan generation
- [ ] Execution of approved items

**Result:** Success / Partial / Failed

**What happened:**
- (Data collection: which APIs succeeded/failed)
- (Action items: how many proposed, approved, executed)
- (Any surprises or unexpected findings)

**What didn't work:**
- (API issues, data gaps, token budget concerns)

**Is this a repeat error?** Yes/No -- if yes, which one?

**Lesson learned:**
- (What to do differently next time)

**Tokens/cost:** ~XX K tokens
```

### 2. Update Issue Tracking

| Situation | Action |
|-----------|--------|
| New problem | Add to **Known Issues** |
| Known Issue happened again | Move to **Repeat Errors**, increment count, **tell the user** |
| Fixed a Known Issue | Move to **Resolved Issues** |

### 3. Tell the User

End your output with a **Lessons Update** note.

**Do NOT skip this. The system only improves if every run is logged honestly.**

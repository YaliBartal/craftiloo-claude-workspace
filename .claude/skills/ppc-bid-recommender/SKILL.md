---
name: ppc-bid-recommender
description: SOP-based bid adjustment recommendations with rank-aware decisions and programmatic application
triggers:
  - adjust bids
  - bid recommendations
  - bid review
  - bid adjustments
  - deal prep
  - deal ppc
  - prep for deal
  - post deal
  - deal ended
  - deal cleanup
output_location: outputs/research/ppc-agent/bids/
---

# Bid Adjustment Recommender

**USE WHEN** routed from the PPC Agent via: "adjust bids", "bid recommendations", "bid review"

**This skill is invoked through the PPC Agent orchestrator, not directly.**

---

## BEFORE YOU START — Read Lessons

**MANDATORY FIRST STEP:** Read `LESSONS.md` in this skill's folder before doing anything else.

1. Read `.claude/skills/ppc-bid-recommender/LESSONS.md`
2. Check **Known Issues** — plan around these
3. Check **Repeat Errors** — if you encounter one during this run, tell the user immediately: _"Repeat issue (xN): [description]"_
4. Apply all past lessons to this run

**Do NOT skip this step.**

---

## What This Does

Codifies the PPC SOP's bid adjustment decision matrix into an automated recommendation engine. Reads campaign performance data, cross-references rank movement, applies stage-specific thresholds, and produces a concrete bid change table for user approval.

**Cadence:** Every 2-3 days
**Time saved:** ~4-5 hrs/week (biggest single win from automation audit)
**Token budget:** <60K tokens, <5 minutes

---

## Efficiency Standards

- **<60K tokens** per run
- **<5 minutes** execution time
- **Reads existing data first** — only fetches fresh data if snapshots are >3 days old
- **No Apify calls** — pure Ads API + DataDive + context files

---

## Process

### Step 1: Load Data Sources

Load in parallel:

| File | Purpose | Freshness Rule |
|------|---------|----------------|
| `context/business.md` | Portfolio stages + ACoS targets | Always current |
| Most recent `outputs/research/ppc-weekly/snapshots/*/campaign-report.json` | Campaign performance data | Use if <3 days old |
| Most recent `outputs/research/ppc-weekly/snapshots/*/targeting-report.json` | Keyword/target performance | Use if <3 days old |
| Most recent `outputs/research/ppc-weekly/snapshots/*/summary.json` | Weekly baseline metrics | Use if <7 days old |
| `outputs/research/ppc-agent/daily/*-health-snapshot.json` | Recent daily health checks | Last 3 days |
| `outputs/research/ppc-agent/bids/*-bid-changes-applied.json` | Previous bid changes | For tracking what we already changed |
| `outputs/research/ppc-agent/agent-state.json` | Last bid review date | |

**If campaign data is >3 days old or doesn't exist:** Pull fresh reports:
```
create_ads_report(report_type="sp_campaigns", date_range="LAST_7_DAYS", marketplace="US")
```
```
create_ads_report(report_type="sp_placements", date_range="LAST_7_DAYS", marketplace="US")
```
Poll and download as in Weekly PPC Analysis.

### Step 1b: Load Placement Performance Data

The SOP requires TOS (Top of Search) specific bid decisions. Load placement-level data:

| File | Purpose |
|------|---------|
| Most recent `outputs/research/ppc-weekly/snapshots/*/placement-report.json` | TOS vs Rest of Search vs Product Pages ACoS |

If the weekly snapshot has placement data, use it. If not, pull via `sp_placements` report (see above).

For each campaign, extract:
- **TOS ACoS** — cost / sales for `PLACEMENT_TOP` rows
- **Rest of Search ACoS** — cost / sales for `PLACEMENT_REST_OF_SEARCH`
- **Product Pages ACoS** — cost / sales for `PLACEMENT_PRODUCT_PAGE`

This data informs whether TOS bid modifiers should increase, decrease, or hold.

### Step 2: Load Rank Data

Check for recent DataDive rank data:

1. **First check:** Most recent weekly snapshot — does it have rank radar data?
2. **If <3 days old:** Use it
3. **If >3 days old or missing:** Fetch fresh:
   ```
   list_rank_radars()
   ```
   Then for each relevant radar (matching our active portfolios):
   ```
   get_rank_radar_data(radar_id="{id}")
   ```
   Extract per-keyword: `organicRank`, `impressionRank`, 7-day movement

### Step 3: Load Budget Utilization

```
get_sp_campaign_budget_usage(
    campaign_ids="{comma-separated top 30 campaign IDs}",
    marketplace="US"
)
```

Classify each campaign:
- **Starved:** >90% budget used, spending consistently to cap
- **Healthy:** 50-90% budget used
- **Underutilized:** <50% budget used
- **Wasteful:** High spend + poor ACoS

### Step 4: Apply SOP Bid Adjustment Matrix

For each active campaign with meaningful spend (>$5 in the period), apply the decision matrix:

#### The SOP Decision Matrix

| ACoS | CVR | Rank Trend | Stage | Action | Bid Change |
|------|-----|------------|-------|--------|------------|
| <20% | >12% | Stable/Rising | Any | **Scale** — increase budget + TOS bid | TOS +20-30% |
| <25% | >10% | Stable | Scaling | **Harvest** — lower TOS bid slightly | TOS -10-15% |
| <25% | >10% | Declining | Any | **Maintain** — rank dropping despite good performance | Hold, investigate listing |
| 25-35% | >10% | Rising | Any | **On track** — no change | Hold |
| 25-35% | >10% | Stable | Scaling | **Target zone** — minor optimization | Hold |
| 25-35% | 6-10% | Any | Any | **Monitor** — acceptable but not strong | Hold |
| 35-50% | >10% | Rising | Launch | **Acceptable** — launch phase, rank gaining | Hold, monitor weekly |
| 35-50% | >10% | Stable | Scaling | **Concerning** — cut TOS bid | TOS -15-20% |
| 35-50% | <6% | Any | Any | **Listing issue** — CVR too low for any bid level | Pause keyword, flag listing |
| >50% | Any | Rising | Launch | **Evaluate** — burning money but gaining rank | Reduce -10%, reassess in 3 days |
| >50% | Any | Stable/Declining | Scaling | **Bleeding** — immediate action | Decrease -30-50% or pause |
| >50% | Any | Stable/Declining | Launch | **Reassess** — spending without rank movement | Decrease -20-30% |
| >100% | Any | Any | Any | **Emergency** — pause unless strategic ranking play | Pause |

#### Additional Rules

| Scenario | Action |
|----------|--------|
| 50+ clicks, 0 orders | **Pause keyword** — dead weight |
| Hero keyword drops 5+ positions | **Increase TOS +25%** or create dedicated SK campaign |
| Ranked top 5 organically | **Reduce paid dependency** — lower bid -15-20% |
| Budget starved + ACoS <30% | **Increase budget** — campaign is efficient but capped |
| Budget starved + ACoS >40% | **Do NOT increase budget** — it would waste more money |
| Competitor launches deal on our hero keyword | **Increase TOS +20%** — defend position temporarily |
| Campaign idle (LOW BID) for >14 days | **Flag for cleanup** — pause or increase bid to re-enter |

#### Deal Coordination Mode (SOP Section 14)

When routed from PPC Agent with "deal prep" or "deal ppc":

**Pre-Deal (1-2 days before deal starts):**

| Action | How | Why |
|--------|-----|-----|
| Increase budgets 2-3x for deal portfolios | `update_sp_campaigns` → `budget` | Deals spike traffic; avoid budget cap before day ends |
| Increase TOS placement modifier +30-50% | `update_sp_campaigns` → `dynamicBidding.placementBidding` | Win TOS during high-converting deal traffic |
| Enable any paused broad/auto campaigns | `update_sp_campaigns` → `state: "ENABLED"` | Capture incremental deal-related search terms |
| Record pre-deal baseline | Save current bids/budgets to `{YYYY-MM-DD}-pre-deal-baseline.json` | For restoring after the deal ends |

**Ask the user:** Which portfolios are running deals? What deal dates? (Lightning Deal, 7-Day Deal, Prime Day, etc.)

When routed with "post deal" or "deal ended":

**Post-Deal (within 48 hours of deal ending):**

| Action | How | Why |
|--------|-----|-----|
| Restore budgets to pre-deal baseline | Read `*-pre-deal-baseline.json`, apply via `update_sp_campaigns` | Prevent overspend at normal conversion rates |
| Restore TOS modifiers to baseline | Read baseline, apply via `update_sp_campaigns` | TOS premium no longer justified at normal traffic |
| Re-pause campaigns that were enabled for the deal | Read baseline, apply via `update_sp_campaigns` | Clean up temporary enablements |
| Assess deal performance | Compare deal-period spend/orders vs baseline period | Was the deal profitable after ad spend? |

**Do NOT auto-restore without user approval.** Present the baseline vs current values and let the user confirm.

#### Stage-Specific Thresholds

| Portfolio Stage | ACoS Target | ACoS Red Flag | CVR Minimum |
|----------------|-------------|---------------|-------------|
| **Launch** | Flexible (up to 60%) | >80% | 5% |
| **Scaling** | 28-32% | >50% | 8% |
| **General** (Catch All / Shield) | 30-40% | >60% | N/A |

### Step 5: Generate Bid Recommendations

For campaigns where changes are recommended, fetch Amazon's bid suggestions:

```
get_sp_bid_recommendations(
    campaign_id="{campaign_id}",
    ad_group_id="{ad_group_id}",
    keywords=[{"keyword": "{keyword}", "matchType": "{type}"}],
    marketplace="US"
)
```

Use Amazon's recommendation as a **reference point**, not as the final bid. The SOP decision matrix takes priority:
- If Amazon suggests higher than our SOP says: note it but follow SOP
- If Amazon suggests lower: consider it as supporting evidence for a decrease
- If Amazon and SOP agree: high confidence change

### Step 6: Present Recommendations

**Format:**

```markdown
# Bid Adjustment Recommendations — {YYYY-MM-DD}

**Data period:** {date range}
**Campaigns analyzed:** {N}
**Campaigns with recommended changes:** {N}
**Campaigns on hold (no change):** {N}

---

## Priority 1 — Immediate Action

### Bleeding Campaigns (ACoS >50%, Scaling stage)

| Campaign | Portfolio | ACoS | CVR | Spend | Orders | Rank Trend | Current Bid | Recommended | Change | Reason |
|----------|-----------|------|-----|-------|--------|------------|-------------|-------------|--------|--------|
| {name} | {portfolio} | X% | X% | ${X} | {N} | {trend} | ${X} | ${X} | -X% | {SOP rule applied} |

### Dead Weight (50+ clicks, 0 orders)

| Campaign | Keyword/Target | Clicks | Spend | Action |
|----------|---------------|--------|-------|--------|
| {name} | {keyword} | {N} | ${X} | Pause |

### Hero Keyword Defense (rank dropped 5+)

| Keyword | Previous Rank | Current Rank | Campaign | Current TOS Bid | Recommended | Change |
|---------|--------------|-------------|----------|-----------------|-------------|--------|
| {kw} | #{N} | #{N} | {campaign} | ${X} | ${X} | +25% |

## Priority 2 — Optimization

### Scale Winners (ACoS <20%, CVR >12%)

| Campaign | Portfolio | ACoS | CVR | Current Bid | Recommended | Change | Budget Note |
|----------|-----------|------|-----|-------------|-------------|--------|-------------|
| {name} | {portfolio} | X% | X% | ${X} | ${X} | +X% | {starved/healthy} |

### Reduce Organic Dependency (ranked top 5)

| Campaign | Keyword | Organic Rank | ACoS | Current Bid | Recommended | Change |
|----------|---------|-------------|------|-------------|-------------|--------|
| {name} | {kw} | #{N} | X% | ${X} | ${X} | -15% |

### Budget Adjustments

| Campaign | Current Budget | Usage | ACoS | Recommendation |
|----------|---------------|-------|------|----------------|
| {name} | ${X} | X% | X% | Increase to ${X} / Decrease to ${X} |

## Priority 3 — Monitor Only

### Launch Phase (high ACoS acceptable)

| Campaign | Portfolio | ACoS | Rank Trend | Note |
|----------|-----------|------|------------|------|
| {name} | {portfolio} | X% | {rising} | On track — rank gaining. Review in weekly analysis. |

### On Hold (no change needed)

| Campaign | Portfolio | ACoS | CVR | Status |
|----------|-----------|------|-----|--------|
| {name} | {portfolio} | X% | X% | Target zone |

## Dormant Campaigns ({count})

| Campaign | Status | Days Idle | Recommendation |
|----------|--------|-----------|----------------|
| {name} | LOW BID | {N} | Pause or increase bid to ${X} |

## Summary

| Action Type | Count | Est. Weekly Spend Impact |
|-------------|-------|------------------------|
| Bid decreases | {N} | -${X}/week |
| Bid increases | {N} | +${X}/week |
| Pauses | {N} | -${X}/week |
| Budget changes | {N} | +/-${X}/week |
| **Net estimated impact** | — | **${X}/week** |
```

### Step 7: User Approval Gate

Present the recommendations and ask:

**"Review the recommendations above. Options:**
1. **Approve all P1 changes** — I'll apply bid changes via the API
2. **Approve specific changes** — tell me which campaign numbers to apply
3. **Modify recommendations** — adjust any bids before applying
4. **Save for reference only** — don't apply anything"

**Do NOT apply any changes without explicit user approval.**

### Step 8: Apply Approved Changes

After user approval:

#### For bid changes:

1. **TOS placement modifier changes (SOP: bid increases applied on TOS only):**
   ```
   update_sp_campaigns(
       campaigns=[
           {
               "campaignId": "{id}",
               "dynamicBidding": {
                   "strategy": "LEGACY_FOR_SALES",
                   "placementBidding": [
                       {"placement": "PLACEMENT_TOP", "percentage": {new_tos_percentage}}
                   ]
               }
           }
       ],
       marketplace="US"
   )
   ```
   The `percentage` is the modifier on top of the base bid (e.g., 50 = +50% on TOS).
   When the matrix says "TOS +20%", increase the `percentage` by 20 points.
   When it says "TOS -15%", decrease the `percentage` by 15 points (min 0).

2. **Campaign-level budget changes:**
   ```
   update_sp_campaigns(
       campaigns=[
           {"campaignId": "{id}", "budget": {"budget": {new_amount}, "budgetType": "DAILY"}}
       ],
       marketplace="US"
   )
   ```

3. **Ad group-level base bid changes (use only for overall bid decreases or pausing):**
   ```
   update_sp_ad_groups(
       ad_groups=[
           {"adGroupId": "{id}", "defaultBid": {new_bid}}
       ],
       marketplace="US"
   )
   ```
   **Note:** Per SOP, bid *increases* go through TOS placement modifiers (item 1 above).
   Use `defaultBid` decreases only when reducing overall spend, not for ranking plays.

4. **Keyword-level pauses:**
   ```
   manage_sp_keywords(
       action="update",
       keywords=[
           {"keywordId": "{id}", "state": "PAUSED"}
       ],
       marketplace="US"
   )
   ```

5. **Report results:** Success/failure per change.

### Step 9: Save Outputs

**Brief:**
`outputs/research/ppc-agent/bids/{YYYY-MM-DD}-bid-recommendations.md`

**Applied changes log:**
`outputs/research/ppc-agent/bids/{YYYY-MM-DD}-bid-changes-applied.json`

```json
{
  "date": "YYYY-MM-DD",
  "data_period": "LAST_7_DAYS",
  "campaigns_analyzed": 0,
  "changes_applied": [
    {
      "campaign_name": "...",
      "campaign_id": "...",
      "change_type": "bid_decrease",
      "previous_value": 0,
      "new_value": 0,
      "reason": "ACoS 52% in Scaling portfolio, SOP: decrease -30%",
      "status": "success"
    }
  ],
  "changes_skipped": [],
  "changes_failed": [],
  "paused_keywords": [],
  "budget_changes": [],
  "net_weekly_impact_estimate": 0
}
```

---

## Error Handling

| Issue | Response |
|-------|----------|
| No weekly snapshot exists | Pull fresh campaign report (adds ~3 min) |
| Weekly snapshot >7 days old | Warn user, pull fresh report |
| DataDive rank data unavailable | Skip rank-aware decisions, note in output: "Rank data unavailable — decisions based on ACoS/CVR only" |
| `get_sp_bid_recommendations` fails | Use SOP percentages only (still reliable without Amazon's suggestions) |
| Campaign not found during application | Re-fetch campaign list, try matching by name |
| Portfolio stage missing from `context/business.md` | Default to "Scaling" thresholds (more conservative) |
| Budget usage API returns error | Skip budget classification, note in output |
| Previous bid changes log missing | First run — no previous change tracking |

---

## AFTER EVERY RUN — Update Lessons (MANDATORY)

**Before presenting final results, update `.claude/skills/ppc-bid-recommender/LESSONS.md`.**

### 1. Write a Run Log Entry

Add a new entry at the **TOP** of the Run Log section:

```
### Run: YYYY-MM-DD
**Result:** Success / Partial / Failed

**Campaigns analyzed:** {N}
**Changes recommended:** {N} (bid decreases: {N}, increases: {N}, pauses: {N}, budget: {N})
**Changes applied:** {N}
**Net weekly impact estimate:** ${X}

**What happened:**
- (What went according to plan)

**What didn't work:**
- (Any issues)

**Lesson learned:**
- (What to do differently)

**Tokens/cost:** ~XX K tokens
```

### 2. Update Issue Tracking

| Situation | Action |
|-----------|--------|
| New problem | Add to **Known Issues** |
| Known Issue happened again | Move to **Repeat Errors**, increment count, **tell the user** |
| Fixed a Known Issue | Move to **Resolved Issues** |

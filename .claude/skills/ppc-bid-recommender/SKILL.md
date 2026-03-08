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

## TOS-First Bidding Philosophy

**This is how we manage bids. All bid decisions must follow this framework.**

### Core Principles

1. **TOS (Top of Search) is the primary conversion channel.** Most orders come from TOS. It consistently has the best ACoS and CVR across placements.

2. **The TOS modifier is how we control TOS visibility — not the default bid.** When we want more visibility on TOS, we increase the TOS modifier percentage. The default bid is NOT the lever for this.

3. **The default bid controls ROS (Rest of Search) and PP (Product Pages) exposure.** These placements use the base bid directly. Lowering the default bid shrinks ROS/PP traffic without affecting TOS (because the TOS modifier compensates).

4. **New campaigns start TOS-heavy** — high TOS modifier from day one, with a conservative default bid. This means most initial traffic goes to the highest-converting placement while limiting exposure on lower-converting placements.

5. **Bid increases = TOS modifier increases.** When we want to scale, defend rank, or increase visibility — the TOS modifier goes up.

6. **Bid decreases depend on WHERE the problem is:**
   - TOS is efficient but ROS/PP are wasting money → **lower default bid** (TOS stays stable via modifier, ROS/PP shrink)
   - TOS is bleeding → **lower TOS modifier**
   - Everything is bleeding → **not a bid problem** — flag for listing/targeting review

7. **ROS/PP modifiers are a rare, tertiary lever.** Only used when TOS is underperforming but ROS or PP are converting well — which is uncommon but valid.

### New Campaign Defaults

| Parameter | Default | Rationale |
|---|---|---|
| TOS modifier | Start high | TOS converts best. Start aggressive, let data adjust. |
| Default bid | Start conservative | Low base limits ROS/PP bleed. TOS modifier handles competitiveness. |
| Bidding strategy | LEGACY_FOR_SALES | Down-only dynamic. Prevents Amazon auto-escalating bids. |
| ROS/PP modifier | Unset (0%) | Let default bid handle naturally. |

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

### Step 1: Load Data Sources + Portfolio Trackers

Load in parallel:

| File | Purpose | Freshness Rule |
|------|---------|----------------|
| `context/business.md` | Portfolio stages + ACoS targets | Always current |
| `outputs/research/ppc-agent/state/*.json` | **Portfolio trackers** — goals, pending bid actions, recent change_log (avoid re-recommending), baseline for context | Always read |
| Most recent `outputs/research/ppc-weekly/snapshots/*/campaign-report.json` | Campaign performance data | Use if <3 days old |
| Most recent `outputs/research/ppc-weekly/snapshots/*/targeting-report.json` | Keyword/target performance | Use if <3 days old |
| Most recent `outputs/research/ppc-weekly/snapshots/*/summary.json` | Weekly baseline metrics | Use if <7 days old |
| `outputs/research/ppc-agent/daily-health/*-health-snapshot.json` | Recent daily health checks | Last 3 days |
| `outputs/research/ppc-agent/bids/*-bid-changes-applied.json` | Previous bid changes | For tracking what we already changed |
| `outputs/research/ppc-agent/state/agent-state.json` | Last bid review date, portfolio_index | |

**From portfolio trackers, use:**
- `change_log` — avoid re-recommending changes already made in the last 7 days
- `pending_actions` with category containing "BID" — these are queued bid actions from previous skills
- `goals.acos_target` — use portfolio-specific targets instead of stage defaults when available
- `baseline` + `latest_metrics` — for trend context (is this portfolio improving or declining?)

**If campaign data is >3 days old or doesn't exist:** Pull fresh reports:
```
create_ads_report(report_type="sp_campaigns", date_range="LAST_7_DAYS", marketplace="US")
```
```
create_ads_report(report_type="sp_placements", date_range="LAST_7_DAYS", marketplace="US")
```
Poll and download as in Weekly PPC Analysis.

### Step 1b: Load Placement Performance Data + Current TOS Modifiers

The TOS-First Bidding Philosophy requires per-placement performance AND current modifier percentages. Load both:

| Source | Data | How |
|--------|------|-----|
| Weekly snapshot `placement-report.json` | Per-campaign per-placement ACoS, CVR, spend, orders | Read file |
| Weekly snapshot `summary.json` → `placement.per_campaign_health` | Pre-classified placement health per campaign | Read file |
| `list_sp_campaigns(state="ENABLED", marketplace="US")` | Current TOS/ROS/PP modifier percentages via `placementBidding` | API call |

If the weekly snapshot has placement data (<3 days old), use it. If not, pull fresh via `sp_placements` report (see Step 1).

**Always pull current TOS modifiers fresh** via `list_sp_campaigns` — these can change between weekly runs.

For each campaign, extract:
- **Per-placement metrics:** TOS ACoS, ROS ACoS, PP ACoS, spend share, order share, CVR
- **Current modifiers:** TOS %, ROS %, PP % from `placementBidding` array
- **Placement health classification** (from weekly snapshot, or classify fresh using Step 4b)

This data feeds into Step 4b (Placement Health Classification) to determine which lever to pull.

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

**CRITICAL RULES (apply to ALL rows below):**
1. **Never pause a campaign based on a single week of zero conversions.** Always check minimum 30 days (ideally 60 days) of data before recommending a pause. A campaign with zero orders in one week might just be in a rough patch.
2. **Never use round/organized bid amounts.** When applying percentage changes, never use clean numbers like -30%, -50%, +20%. Always use slightly irregular amounts like -31%, -48%, +22%, -27%. This avoids predictable bid patterns in Amazon's auction dynamics.
3. **Never negate a search term based on a single week of zero conversions.** Always check a minimum 30-day window of data before recommending a search term for negation. A search term with zero orders in one week might convert in other weeks. Only recommend negating if the search term shows sustained zero conversions AND is clearly irrelevant to the product over the full 30-day window.

| ACoS | CVR | Rank Trend | Stage | Action | Bid Change |
|------|-----|------------|-------|--------|------------|
| <20% | >12% | Stable/Rising | Any | **Scale** — increase budget + TOS bid | TOS +22-31% |
| <25% | >10% | Stable | Scaling | **Harvest** — lower TOS bid slightly | TOS -11-16% |
| <25% | >10% | Declining | Any | **Maintain** — rank dropping despite good performance | Hold, investigate listing |
| 25-35% | >10% | Rising | Any | **On track** — no change | Hold |
| 25-35% | >10% | Stable | Scaling | **Target zone** — minor optimization | Hold |
| 25-35% | 6-10% | Any | Any | **Monitor** — acceptable but not strong | Hold |
| 35-50% | >10% | Rising | Launch | **Acceptable** — launch phase, rank gaining | Hold, monitor weekly |
| 35-50% | >10% | Stable | Scaling | **Concerning** — cut TOS bid | TOS -16-22% |
| 35-50% | <6% | Any | Any | **Listing issue** — CVR too low for any bid level | Pause keyword (only after 30+ days of data), flag listing |
| >50% | Any | Rising | Launch | **Evaluate** — burning money but gaining rank | Reduce -11%, reassess in 3 days |
| >50% | Any | Stable/Declining | Scaling | **Bleeding** — immediate action | Decrease -31-48% (verify 30+ days before pause) |
| >50% | Any | Stable/Declining | Launch | **Reassess** — spending without rank movement | Decrease -22-31% |
| >100% | Any | Any | Any | **Emergency** — pause only after verifying 30+ days of sustained >100% ACoS | Pause (confirm long-term data) |

#### Additional Rules

| Scenario | Action |
|----------|--------|
| 50+ clicks, 0 orders (over 30-60 day window) | **Pause keyword** — dead weight. **Never based on a single week.** |
| Hero keyword drops 5+ positions | **Increase TOS +26%** or create dedicated SK campaign |
| Ranked top 5 organically | **Reduce paid dependency** — lower bid -16-22% |
| Budget starved + ACoS <30% | **Increase budget** — campaign is efficient but capped |
| Budget starved + ACoS >40% | **Do NOT increase budget** — it would waste more money |
| Competitor launches deal on our hero keyword | **Increase TOS +22%** — defend position temporarily |
| Campaign idle (LOW BID) for >14 days | **Flag for cleanup** — pause or increase bid to re-enter |
| Campaign with 0 orders in a single week | **Do NOT pause.** Check 30-60 day performance first. May just be a rough patch. |

### Step 4b: Placement Health Classification

**For every campaign with meaningful spend, classify its placement health before deciding which lever to pull.**

The SOP Decision Matrix above determines **how much** to change. This step determines **which lever** to pull (TOS modifier vs default bid vs ROS/PP modifier).

#### Input Data Per Campaign

Pull from the `sp_placements` report (or weekly snapshot) and `list_sp_campaigns`:

- **Per-placement ACoS, CVR, spend share, order share** — from `sp_placements` report
- **Current TOS/ROS/PP modifier percentages** — from `list_sp_campaigns` → `placementBidding`

#### Placement Health Categories

| Classification | What It Means | Which Lever |
|---|---|---|
| **TOS DOMINANT** | TOS is efficient (below stage target ACoS) and drives most orders | Scale via TOS modifier. Never lower default bid. |
| **TOS EFFICIENT / ROS-PP BLEEDING** | TOS ACoS is below target, but ROS and/or PP ACoS are significantly above target | Lower default bid to shrink ROS/PP. Keep or increase TOS modifier. |
| **TOS BLEEDING / ROS-PP EFFICIENT** | TOS ACoS is significantly above target, but ROS and/or PP are below target | Lower TOS modifier. Optionally add ROS/PP modifiers. |
| **ALL EFFICIENT** | All three placements are within stage target ACoS | Hold or scale budget. If scaling: increase TOS modifier. |
| **ALL BLEEDING** | All three placements are above stage target ACoS | **Not a bid problem.** Flag for listing/targeting review. Do not adjust bids. |
| **INSUFFICIENT DATA** | Not enough clicks or spend on one or more placements to classify | Hold and revisit next run. |

**How to classify:** Compare each placement's ACoS and CVR against the portfolio's stage target. The **relative performance between placements** determines the classification, not absolute numbers. What matters is which placements are working and which are not.

#### Applying the Classification

For each campaign:

1. Read current TOS modifier % from `list_sp_campaigns` → `placementBidding`
2. Read placement performance from `sp_placements` report (or weekly snapshot `placement.per_campaign_health`)
3. Classify using the table above
4. Combine with SOP matrix recommendation:

| SOP Matrix Says | Placement Health Says | Final Action |
|---|---|---|
| **Scale** | TOS DOMINANT or ALL EFFICIENT | Increase TOS modifier |
| **Scale** | TOS BLEEDING | Do not scale TOS. Investigate why TOS is underperforming. |
| **Concerning / Bleeding** | TOS EFFICIENT / ROS-PP BLEEDING | Lower default bid (not TOS modifier — TOS is working) |
| **Concerning / Bleeding** | TOS BLEEDING / ROS-PP EFFICIENT | Lower TOS modifier |
| **Concerning / Bleeding** | ALL BLEEDING | Do not adjust bids. Flag listing/targeting issue. |
| **Harvest** | TOS DOMINANT | Reduce TOS modifier to capture profit |
| Any | INSUFFICIENT DATA | Hold — not enough placement data to act on |

#### Lever Selection Summary

**TOS modifier (primary lever) — use for:**
- Scaling efficient campaigns UP
- Defending hero keyword rank (rank drops)
- Deal prep (increase for high-converting deal traffic)
- New campaign setup (start high)

**Default bid decrease (secondary lever) — use for:**
- ROS/PP bleeding while TOS is efficient (lower default bid shrinks ROS/PP; TOS modifier keeps TOS stable)
- Overall spend reduction needed across all placements
- Campaign-wide profitability emergency (default bid is the "pull everything back" lever)

**ROS/PP modifier increase (rare, tertiary lever) — use for:**
- TOS bleeding but ROS/PP converting well (uncommon)
- Product Pages driving strong CVR on specific ASINs

---

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

## Placement Health Summary

| Campaign | Portfolio | TOS ACoS | ROS ACoS | PP ACoS | TOS Spend% | Current TOS% | Health | Lever |
|----------|-----------|----------|----------|---------|------------|--------------|--------|-------|
| {name} | {portfolio} | X% | X% | X% | X% | X% | {classification} | TOS modifier / Default bid / Hold |

**Health Distribution:** {N} TOS Dominant, {N} TOS Eff/ROS Bleed, {N} TOS Bleeding, {N} All Efficient, {N} All Bleeding, {N} Insufficient Data

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

3. **Default bid changes (use per TOS-First Philosophy — see Step 4b for when):**
   ```
   update_sp_ad_groups(
       ad_groups=[
           {"adGroupId": "{id}", "defaultBid": {new_bid}}
       ],
       marketplace="US"
   )
   ```
   **Per TOS-First Philosophy, default bid changes are the SECONDARY lever:**
   - **Lower default bid** when placement health = TOS EFFICIENT / ROS-PP BLEEDING (shrinks ROS/PP while TOS modifier maintains TOS)
   - **Lower default bid** for campaign-wide spend emergencies
   - **Never increase default bid to scale** — use TOS modifier increase instead
   - Always log the `placement_health` classification that justified this lever choice

4. **ROS/PP placement modifier changes (rare — see Step 4b lever selection):**
   ```
   update_sp_campaigns(
       campaigns=[
           {
               "campaignId": "{id}",
               "dynamicBidding": {
                   "strategy": "LEGACY_FOR_SALES",
                   "placementBidding": [
                       {"placement": "PLACEMENT_REST_OF_SEARCH", "percentage": {new_ros_percentage}},
                       {"placement": "PLACEMENT_PRODUCT_PAGE", "percentage": {new_pp_percentage}}
                   ]
               }
           }
       ],
       marketplace="US"
   )
   ```
   Only used when TOS is bleeding but ROS/PP are converting well (TOS BLEEDING / ROS-PP EFFICIENT classification).

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

### Step 9: Save Outputs + Update Portfolio Trackers

**Brief:**
`outputs/research/ppc-agent/bids/{YYYY-MM-DD}-bid-recommendations.md`

**Applied changes log:**
`outputs/research/ppc-agent/bids/{YYYY-MM-DD}-bid-changes-applied.json`

**Portfolio tracker updates** — for each portfolio with applied changes, update its tracker at `outputs/research/ppc-agent/state/{slug}.json`:

1. **`change_log`** — append entry:
   ```json
   {
     "date": "YYYY-MM-DD",
     "source": "ppc-bid-recommender",
     "summary": "{N} bid changes applied",
     "changes": [
       {"category": "BID_DECREASE", "campaign": "{name}", "old": "TOS 50%", "new": "TOS 33%", "status": "success"}
     ]
   }
   ```
2. **`pending_actions`** — mark completed any bid-related pending actions that were addressed; add new P3/P4 items
3. **`skills_run`** — append: `{"skill": "ppc-bid-recommender", "date": "YYYY-MM-DD", "result": "success", "key_metrics": {"changes_applied": N, "net_weekly_impact": "$X"}}`

**`agent-state.json` update:**
- Update `portfolio_index.{slug}.last_updated` for each affected portfolio
- Update `portfolio_index.{slug}.pending_count` from tracker

```json
{
  "date": "YYYY-MM-DD",
  "data_period": "LAST_7_DAYS",
  "campaigns_analyzed": 0,
  "changes_applied": [
    {
      "campaign_name": "...",
      "campaign_id": "...",
      "change_type": "tos_modifier_increase",
      "lever": "tos_modifier",
      "placement_health": "TOS_DOMINANT",
      "tos_acos": 0,
      "ros_acos": 0,
      "pp_acos": 0,
      "previous_tos_modifier": 0,
      "new_tos_modifier": 0,
      "previous_default_bid": 0,
      "new_default_bid": 0,
      "reason": "TOS DOMINANT — scaling efficient campaign via TOS modifier",
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

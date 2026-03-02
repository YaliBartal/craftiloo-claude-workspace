---
name: ppc-search-term-harvester
description: Reactive search term harvesting — classifies terms as NEGATE/PROMOTE/DISCOVER from performance data every 2-3 days
triggers:
  - harvest search terms
  - negate and promote
  - search term review
  - search term harvest
output_location: outputs/research/ppc-agent/search-terms/
---

# Search Term Harvester

**USE WHEN** routed from the PPC Agent via: "harvest search terms", "negate and promote", "search term review"

**This skill is invoked through the PPC Agent orchestrator, not directly.**

---

## BEFORE YOU START — Read Lessons

**MANDATORY FIRST STEP:** Read `LESSONS.md` in this skill's folder before doing anything else.

1. Read `.claude/skills/ppc-search-term-harvester/LESSONS.md`
2. Check **Known Issues** — plan around these
3. Check **Repeat Errors** — if you encounter one during this run, tell the user immediately: _"Repeat issue (xN): [description]"_
4. Apply all past lessons to this run

**Do NOT skip this step.**

---

## What This Does

Pulls the search term report from the Amazon Ads API and classifies every term into one of three actions: **NEGATE** (stop spending), **PROMOTE** (create dedicated campaign), or **DISCOVER** (monitor). Then applies approved changes via the API.

**Cadence:** Every 2-3 days
**Time saved:** Part of the ~4-5 hrs/week bid management cluster
**Token budget:** <60K tokens, <8 minutes (includes report generation wait)

**Distinction from Negative Keyword Generator:**
- **This skill** = reactive, performance-data-based, runs every 2-3 days on the full account
- **Negative Keyword Generator** = proactive, product-knowledge-based, run once per portfolio

---

## Operating Rules

1. **Never pause a campaign based on a single week of zero conversions.** Always check a longer timeframe (minimum 30 days, ideally 60 days) before recommending a pause. A campaign with zero orders in one week might just be in a rough patch. Only recommend pausing if the campaign shows sustained poor performance over the longer timeframe.
2. **Never use round/organized bid amounts.** When lowering or placing bids, never use clean percentages like -30%, -50%. Always use slightly irregular amounts like -31%, -48%, -52%, -27%. This avoids predictable bid patterns and helps stand out in Amazon's auction dynamics.
3. **Never negate a search term based on a single week of zero conversions.** Always check a minimum 30-day window of data before recommending a search term for negation. A search term with zero orders in one week might convert in other weeks. Only recommend negating if the search term shows sustained zero conversions AND is clearly irrelevant to the product over the full 30-day window.

---

## Efficiency Standards

- **<60K tokens** per run
- **<8 minutes** execution time (report generation takes 1-3 min)
- **No Apify calls** — pure Ads API + context files
- **Save search term report to file** — it's 3,000-5,000+ rows

---

## Process

### Step 1: Load Context

Load in parallel:

| File | Purpose |
|------|---------|
| `context/business.md` | Portfolio stages + ACoS targets |
| `context/search-terms.md` | **PROTECTED terms — never negate these** |
| `outputs/research/negative-keywords/data/*-applied-*.json` | Previously applied negatives (dedup) |
| `outputs/research/ppc-agent/agent-state.json` | Last harvest date |
| Most recent `outputs/research/ppc-weekly/snapshots/*/summary.json` | Weekly baseline for context |

### Step 2: Pull Search Term Report

**Date range:** Last 14 days (gives enough data volume without going stale)

```
create_ads_report(
    report_type="sp_search_terms",
    date_range="LAST_14_DAYS",
    marketplace="US"
)
```

Poll for completion:
```
get_ads_report_status(report_id="{reportId}", marketplace="US")
```
Wait for `COMPLETED`. Poll every 30 seconds, max 10 times.

Download to file (report is too large for inline):
```
download_ads_report(
    report_id="{reportId}",
    marketplace="US",
    save_to_file="outputs/research/ppc-agent/search-terms/{YYYY-MM-DD}-search-term-report.json"
)
```

### Step 3: Load Portfolio Mapping

```
list_portfolios(marketplace="US")
```

Build portfolio-to-campaign mapping so every search term can be attributed to a portfolio.

### Step 4: Classify Search Terms

For each search term in the report, apply these SOP-based classification rules:

#### NEGATE — Stop spending on these terms

| Condition | Priority | Match Type |
|-----------|----------|------------|
| `spend >= $10` AND `purchases7d == 0` | **P1** | NEGATIVE_EXACT |
| `clicks >= 20` AND `purchases7d == 0` | **P1** | NEGATIVE_EXACT |
| ACoS > 100% AND `clicks >= 3` | **P1** | NEGATIVE_EXACT |
| `spend >= $5` AND `purchases7d == 0` AND `CTR < 0.3%` | **P1** | NEGATIVE_EXACT |
| `spend >= $5` AND `purchases7d == 0` AND `CTR >= 0.3%` | **P2** (review) | NEGATIVE_EXACT |
| ACoS > 3x portfolio target AND `clicks >= 5` | **P2** | NEGATIVE_EXACT |

#### PROMOTE — Create dedicated exact campaign

| Condition | Priority | Action |
|-----------|----------|--------|
| `purchases7d >= 3` AND ACoS < 40% AND buying intent | **P1** | Create SK campaign |
| `purchases7d >= 2` AND ACoS < 30% | **P2** | Consider SK campaign |
| Converting term NOT already in any exact match campaign | **P1** | Keyword gap |

**Buying intent indicators:** Specific product terms (not generic), long-tail (3+ words), contains product type + modifier

#### DISCOVER — Monitor, don't act yet

| Condition | Action |
|-----------|--------|
| `purchases7d == 1` AND ACoS < 50% | Watch — may become PROMOTE with more data |
| New term not seen in previous harvests | Log for awareness |
| Converting term already in exact campaign | No action — system working correctly |

### Step 5: Safety Cross-Reference

**Before presenting the list, apply safety checks:**

1. **Protected terms check:** Cross-reference every NEGATE candidate against `context/search-terms.md`. If a term appears there, **remove it from NEGATE** and flag: "Protected term — tracked keyword for {category}."

2. **Rank check (if DataDive data available):** If the most recent weekly snapshot has rank data, check if we rank organically for any NEGATE candidate. If we rank top 30 organically, **flag as [REVIEW]** instead of auto-negating.

3. **Dedup against applied negatives:** Check `outputs/research/negative-keywords/data/*-applied-*.json` for already-applied negatives. Skip any terms that have been negated previously.

4. **Product title check:** Do not negate terms that contain words from our own product titles.

5. **Cross-portfolio check:** Flag if a NEGATE term is a valuable keyword for a DIFFERENT portfolio (cannibalization signal).

### Step 6: Identify Target Campaigns for Negatives

For each NEGATE term, identify which campaign(s) it appeared in:

- If it appeared in an **Auto campaign** — apply negative at campaign level
- If it appeared in a **Broad campaign** — apply negative at campaign level
- If it appeared in an **Exact campaign** — do NOT negate (it was explicitly targeted)
- If it appeared across **multiple campaigns** — apply at the portfolio's broadest campaign level

### Step 7: Present Action List

**Format:**

```markdown
# Search Term Harvest — {YYYY-MM-DD}

**Report period:** Last 14 days
**Total search terms analyzed:** {N}
**Terms with spend:** {N}

---

## P1 NEGATE — Immediate Action ({count} terms, ${total_spend} wasted)

| # | Search Term | Spend | Clicks | Orders | ACoS | Campaign | Action |
|---|------------|-------|--------|--------|------|----------|--------|
| 1 | {term} | ${X} | {N} | 0 | --- | {campaign name} | Negate EXACT in {campaign} |

**Estimated weekly savings:** ${X} (based on 14-day spend / 2)

## P2 NEGATE — Review Recommended ({count} terms)

| # | Search Term | Spend | Clicks | Orders | ACoS | Campaign | Concern |
|---|------------|-------|--------|--------|------|----------|---------|
| 1 | {term} | ${X} | {N} | 0 | --- | {campaign} | {why it's P2 not P1} |

## PROMOTE — Campaign Creation Candidates ({count} terms)

| # | Search Term | Orders | Spend | ACoS | CVR | Source Campaign | Recommended Bid |
|---|------------|--------|-------|------|-----|----------------|----------------|
| 1 | {term} | {N} | ${X} | X% | X% | {auto/broad} | ${X} (from bid rec) |

**Action:** Create SK (Single Keyword) exact campaigns for these terms. Add as negative in source campaign to isolate traffic.

## DISCOVER — Watch List ({count} terms)

| # | Search Term | Orders | Spend | ACoS | Note |
|---|------------|--------|-------|------|------|
| 1 | {term} | 1 | ${X} | X% | First conversion — monitor |

## Safety Check Results

| Check | Status |
|-------|--------|
| Protected terms (search-terms.md) | {N} terms checked, {N} removed from NEGATE |
| Previously applied negatives | {N} duplicates skipped |
| Product title terms | {N} terms preserved |
| Cross-portfolio flags | {N} terms flagged |

## Summary

| Action | Count | Spend Involved |
|--------|-------|----------------|
| P1 NEGATE | {N} | ${X} |
| P2 NEGATE | {N} | ${X} |
| PROMOTE | {N} | ${X} |
| DISCOVER | {N} | ${X} |
| **Total waste identified** | — | **${X}/14 days** |
| **Estimated weekly savings** | — | **${X}/week** |
```

### Step 8: User Approval Gate

Present the action list and ask:

**"Review the lists above. You can:**
1. **Approve all P1 negatives** — I'll apply them via the API
2. **Review P2 negatives** — tell me which to approve/skip
3. **Approve PROMOTE terms** — I'll fetch bid recommendations and prepare campaign creation
4. **Modify any list** — add/remove terms before applying
5. **Skip application** — just save the analysis for reference"

**Do NOT apply any changes without explicit user approval.**

### Step 9: Apply Approved Changes

After user approval:

#### For NEGATE terms:

1. **Dedup check:** List existing negatives for each target campaign
   ```
   list_sp_campaign_negative_keywords(campaign_id="{id}", marketplace="US")
   ```

2. **Apply campaign-level negatives (preferred):**
   ```
   create_sp_campaign_negative_keywords(
       keywords=[
           {"campaignId": "{id}", "keywordText": "{term}", "matchType": "NEGATIVE_EXACT", "state": "ENABLED"}
       ],
       marketplace="US"
   )
   ```

3. **Batch size:** Max 100 keywords per API call. Split into batches if needed.

4. **Report results:** Success count, failure count, skipped duplicates.

#### For PROMOTE terms:

1. **Fetch bid recommendations:**
   ```
   get_sp_bid_recommendations(
       campaign_id="{source_campaign_id}",
       ad_group_id="{source_ad_group_id}",
       keywords=[{"keyword": "{term}", "matchType": "EXACT"}],
       marketplace="US"
   )
   ```

2. **Present campaign creation plan** — the user creates campaigns manually (too strategic for automation). Provide:
   - Recommended campaign name (per SOP naming convention)
   - Keyword + match type
   - Suggested starting bid
   - Suggested daily budget
   - Note: "Add '{term}' as negative EXACT in {source campaign} after creating the SK campaign"

### Step 10: Save Outputs

**Brief:**
`outputs/research/ppc-agent/search-terms/{YYYY-MM-DD}-search-term-harvest.md`

**Applied actions log:**
`outputs/research/ppc-agent/search-terms/{YYYY-MM-DD}-applied-actions.json`

```json
{
  "date": "YYYY-MM-DD",
  "report_period": "LAST_14_DAYS",
  "total_terms_analyzed": 0,
  "negatives_applied": [
    {"term": "...", "match_type": "NEGATIVE_EXACT", "campaign_id": "...", "campaign_name": "...", "status": "success"}
  ],
  "negatives_skipped_duplicate": [],
  "negatives_failed": [],
  "promote_candidates": [
    {"term": "...", "orders": 0, "acos": 0, "recommended_bid": 0, "source_campaign": "..."}
  ],
  "discover_watch_list": [],
  "estimated_weekly_savings": 0
}
```

---

## Error Handling

| Issue | Response |
|-------|----------|
| Report creation fails | Retry once. If still fails, check API credentials and tell user |
| Report still pending after 5 minutes | Save report ID, tell user to retry later |
| `context/search-terms.md` missing | WARN: "Cannot verify protected terms. Flagging ALL negatives for review." |
| No previous negative application logs | First run — no dedup needed, note this |
| API throttled during application | Wait 5 seconds, retry. If persistent, save remaining for next run |
| Partial application failure | Report what succeeded, provide copy-paste for failures |
| list_portfolios truncated at 50 | Known issue — note some campaigns may be unmapped |

---

## AFTER EVERY RUN — Update Lessons (MANDATORY)

**Before presenting final results, update `.claude/skills/ppc-search-term-harvester/LESSONS.md`.**

### 1. Write a Run Log Entry

Add a new entry at the **TOP** of the Run Log section:

```
### Run: YYYY-MM-DD
**Result:** Success / Partial / Failed

**Terms analyzed:** {N}
**P1 negatives identified:** {N} (${X} spend)
**P2 negatives identified:** {N}
**Promote candidates:** {N}
**Applied:** {N negatives} / {N total}
**Estimated weekly savings:** ${X}

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

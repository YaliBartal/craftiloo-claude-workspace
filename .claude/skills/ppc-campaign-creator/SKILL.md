# PPC Campaign Creator

> Proposes and creates PPC campaigns from upstream skill signals — PROMOTE terms, REDIRECT keywords, structure gaps.

---

## What This Does

Reads pending campaign-creation signals from three upstream sources (Search Term Harvester PROMOTE, Rank Optimizer REDIRECT/PROTECT, Portfolio Summary structure gaps) plus agent-state pending actions. Builds full campaign specifications, deduplicates against existing campaigns, presents a detailed proposal for user approval, and executes approved campaigns via the Amazon Ads API.

- **Cadence:** On demand (triggered by pending actions from other skills, or user request)
- **Invoked through:** PPC Agent orchestrator
- **Token budget:** <70K tokens, <10 minutes
- **Safety cap:** Max 5 campaigns per run
- **Output:** `outputs/research/ppc-agent/campaign-creator/`

---

## Operating Rules

1. **Never pause on a single week of zero conversions** — minimum 30 days, ideally 60 days
2. **Never use round bid amounts** — always irregular (e.g., $0.73, $0.41, not $0.70, $0.40)
3. **Never negate a search term based on a single week** — minimum 30-day window
4. **All campaigns created in PAUSED state** — user must manually enable after reviewing in Seller Central
5. **Never create a campaign without at least one product ad (ASIN)** — campaigns without ASINs will never serve
6. **Max 5 campaigns per run** — prevents overwhelming review and reduces API error risk
7. **TOS-only placement bids** — only set `PLACEMENT_TOP` modifier at creation. No Product Pages, no Rest of Search modifiers. Those get added later by the Bid Recommender based on performance data.
8. **Full-detail proposals** — every campaign card must show: name, ASIN, product name, TOS%, base bid (with math), budget, type, keywords/targets, negatives count, source rationale, and priority score

---

## Process

### Step 0: Read LESSONS.md (mandatory)

Read `.claude/skills/ppc-campaign-creator/LESSONS.md`. Check Known Issues, Repeat Errors. Apply all past lessons. If a Repeat Error exists, tell the user immediately with occurrence count.

---

### Step 1: Gather Inputs

Load in parallel:

| File | Purpose | Required |
|------|---------|----------|
| `context/business.md` | Portfolio stages, hero ASINs, ACoS targets | Always |
| `outputs/research/ppc-agent/state/agent-state.json` | Pending actions requesting campaign creation | Always |
| Most recent `outputs/research/ppc-agent/search-terms/*-search-term-harvest.md` | PROMOTE candidates | If exists |
| Most recent `outputs/research/ppc-agent/rank-optimizer/snapshots/*/rank-spend-matrix.json` | REDIRECT/PROTECT keywords | If exists |
| Most recent `outputs/research/ppc-agent/rank-optimizer/briefs/*-rank-optimizer.md` | REDIRECT/PROTECT briefs | If exists |
| Most recent `outputs/research/ppc-agent/portfolio-summaries/*-portfolio-snapshot.json` | Structure gaps per portfolio | If exists |
| Most recent `outputs/research/negative-keywords/briefs/*-negatives-*.md` | Proactive negative lists for seeding | For negative seeding |

**If no input files exist from any source:** Tell the user "No campaign creation signals found. Run Search Term Harvester, Rank Optimizer, or Portfolio Summary first to generate candidates."

---

### Step 2: Extract Candidates

Parse each source into a unified candidate list.

#### From Search Term Harvester (PROMOTE)

Extract each PROMOTE row:
- `keyword_text`, `orders`, `spend`, `acos`, `cvr`, `source_campaign`, `source_campaign_id`, `buying_intent`
- Campaign type: **SK (Single Keyword)** exact match
- Also extract the source campaign ID for negative insertion after creation

#### From Rank Optimizer (REDIRECT)

Extract keywords where `classification == "REDIRECT"`:
- Fields: `keyword`, `search_volume`, `relevance_score`, `priority_tier`, `organic_rank_current`
- Campaign type:
  - Tier 1 (high volume, >3000 SV): **SK exact**
  - Tier 2-3 (lower volume): **MK broad** grouped by root keyword

#### From Rank Optimizer (PROTECT)

Extract keywords where `rank_change_7d <= -5`:
- Campaign type: **SK exact** with higher TOS modifier (rank defense)
- Only create dedicated SK if keyword does NOT already have its own SK campaign

#### From Portfolio Summary (Structure Gaps)

Extract portfolios where `structure_complete == false`:
- Read `missing_types` array
- Campaign type: whatever is missing (Auto, Broad, MK, PT)
  - **Auto:** `targetingType: AUTO`, no keywords needed
  - **Broad:** needs main portfolio keywords in BROAD match
  - **PT:** needs competitor ASINs from `context/business.md`

#### From Agent-State Pending Actions

Filter `pending_actions` where description contains: "create", "add Broad", "add Auto", "new campaign", "dedicated SK"
- Parse the action description to extract keyword / campaign type

---

### Step 3: Priority Score & Rank

When more than 5 candidates exist, score and rank.

**Scoring formula (0-100):**

| Factor | Weight | Scoring |
|--------|--------|---------|
| **Source reliability** | 30 pts | PROMOTE (proven converter): 30, PROTECT (rank emergency): 28, Structure gap (SOP compliance): 20, REDIRECT (opportunity): 15, Agent-state (unverified): 10 |
| **Revenue potential** | 25 pts | PROMOTE: `orders × (1 - acos/100) × 25` (normalized). Others: `search_volume / max_sv × 25` |
| **Urgency** | 20 pts | PROTECT: 20, PROMOTE: 15, Structure gap: 12, REDIRECT: 8 |
| **Portfolio stage fit** | 15 pts | Launch + any gap: 15, Scaling + structure gap: 12, Scaling + keyword: 10, General: 5 |
| **Data confidence** | 10 pts | PROMOTE 3+ orders: 10, PROTECT 28d rank data: 8, Structure gap: 6, REDIRECT with rank data: 5, Agent-state text-only: 3 |

Sort descending. Take top 5 (safety cap). Present the full ranked list noting which are above and below the cap.

**Experimental slot:** Reserve 1 of 5 slots for an experiment when candidates exist:
- REDIRECT keyword (Tier 2, organic rank 30-50)
- Match type variation: if creating SK exact, also propose a broad variant
- Competitor ASIN targeting: if competitors identified for the portfolio

---

### Step 4: Build Full Campaign Specs

For each candidate (up to 5), generate all fields:

#### A. Campaign Name (SOP naming convention)

| Type | Pattern | Example |
|------|---------|---------|
| SK exact | `{product} - SPM SK {keyword} TOS` | `Cross Stitch Hero - SPM SK cross stitch kits TOS` |
| MK broad | `{product} - SPM MK {root} TOS` | `Fuse Beads - SPM MK fuse beads TOS` |
| Broad discovery | `{product} - SPM MK Broad TOS` | `Fairy Family - SPM MK Broad TOS` |
| Auto | `{product} - SPA Auto` | `4 Flowers Embroidery - SPA Auto` |
| PT | `{product} - manual - product targeting` | `Cat & Hat Knitting - manual - product targeting` |

#### B. Budget (stage-based defaults)

| Stage | SK/MK | Broad/Auto | PT |
|-------|-------|------------|-----|
| Launch | $15/day | $15/day | $10/day |
| Scaling | $10/day | $10/day | $8/day |
| General | $8/day | $8/day | $5/day |

#### C. Default Bid

1. Fetch Amazon recommendation via `get_sp_bid_recommendations` (use existing campaign + ad group in same portfolio)
2. If recommendation available: use `medBid` as reference, adjust:
   - PROMOTE (proven converter): `medBid × 1.07`
   - PROTECT (rank defense): `medBid × 1.13`
   - REDIRECT (new keyword): `medBid × 0.87`
   - Structure gap (Auto/Broad): `medBid × 0.93`
3. If recommendation unavailable: use portfolio average CPC from portfolio-snapshot.json, adjusted by same factors
4. **Always round to 2 decimals with irregular cents** (e.g., $0.73, $0.41, $0.58 — never $0.70, $0.40, $0.50)

#### D. TOS Modifier (PLACEMENT_TOP only)

| Source | Starting TOS % |
|--------|----------------|
| PROMOTE | 47% |
| PROTECT | 63% |
| REDIRECT | 33% |
| Structure gap | 41% |

**PP/ROS modifiers at creation follow the defaults table in the Portfolio Action Plan skill's PP/ROS Decision Framework:**
| Stage | PP % | ROS % | Notes |
|-------|------|-------|-------|
| Launch (hero keywords) | 15% | 15% | Maximum visibility |
| Scaling (proven converters) | 10% | 10% | Conservative start |
| General/new keyword | 10% | 10% | Conservative start |
| Discovery/testing | 0% | 0% | TOS-only until placement data exists |

#### E. Keywords / Targets

- **SK exact:** single keyword, match type `EXACT`
- **MK broad:** 3-8 related keywords, match type `BROAD`
- **Broad discovery:** top 5-8 portfolio keywords from DataDive/search-terms.md, match type `BROAD`
- **Auto:** no keywords (automatic targeting)
- **PT:** competitor ASINs from `context/business.md`

#### F. Product ASINs

Pull from the portfolio's existing campaigns:
1. `list_sp_campaigns(portfolio_id="{portfolioId}", state="ENABLED")` → get campaign IDs
2. `list_sp_product_ads(campaign_id="{first_campaign_id}")` → get ASINs
3. Use the same ASINs for the new campaign

#### G. Negative Seeds

Load proactive negatives from Negative Keyword Generator output:
1. Find matching brief in `outputs/research/negative-keywords/briefs/{portfolio-slug}-negatives-*.md`
2. Extract PHRASE negatives (Wrong Craft Types, Wrong Product Types, Wrong Age Groups, Wrong Intent)
3. Apply as campaign-level `NEGATIVE_PHRASE` negatives
4. For SK exact from PROMOTE: also add the keyword as `NEGATIVE_EXACT` in the source campaign

#### H. Bidding Strategy

All campaigns: `LEGACY_FOR_SALES` (down-only dynamic bidding per SOP)

#### I. Campaign State

All campaigns: `PAUSED`

---

### Step 5: Dedup Check

Before presenting proposals, verify no duplicates exist:

```
list_sp_campaigns(portfolio_id="{portfolioId}", state="ALL", marketplace="US")
```

For each proposed campaign:
1. Check if a campaign with the same name already exists (case-insensitive)
2. For SK campaigns: check if the keyword already has a dedicated SK campaign in the portfolio
3. For Auto/Broad/PT: check if that type already exists in the portfolio

If duplicate found: remove from proposal, note: "Skipped: {campaign name} — already exists ({existing name})"

---

### Step 6: Present Proposal

**Format — one full-detail card per campaign:**

```markdown
# Campaign Creation Proposal — {YYYY-MM-DD}

**Total candidates found:** {N} | **Proposed:** {N} (cap: 5) | **Skipped (dedup):** {N} | **Deferred:** {N}

---

### Campaign 1 of {N} — ✅ PROMOTE Source (Score: 87/100)

| Field | Value |
|-------|-------|
| **Campaign Name** | `{full campaign name}` |
| **Type** | SK Single Keyword — EXACT match |
| **Portfolio** | {portfolio name} ({stage} stage) |
| **Product** | {product name} |
| **ASIN(s)** | {ASIN(s)} |
| **Keyword** | `{keyword}` |
| **Match Type** | EXACT |
| **Base Bid** | ${bid} (Amazon rec: ${rec} med, ×{factor} for {reason}) |
| **TOS Modifier** | {pct}% |
| **PP Modifier** | {pct}% ({rationale — stage default or "0% — discovery/testing"}) |
| **ROS Modifier** | {pct}% ({rationale — stage default or "0% — discovery/testing"}) |
| **Daily Budget** | ${budget} ({stage} default) |
| **Bidding Strategy** | LEGACY_FOR_SALES (down-only dynamic) |
| **State** | PAUSED (you enable manually after review) |
| **Negatives to Seed** | {N} PHRASE from proactive list ({list name}) |
| **Post-Creation** | Add "{keyword}" as NEG_EXACT in source: `{source campaign name}` (ID: {id}) |

**Why this campaign:**
> {2-3 sentence rationale explaining data and reasoning}

---
{repeat for each campaign}

### 🧪 Experiment Slot (optional)

{Same card format for the experiment campaign with risk assessment}

---

**Your call:**
1. **Approve all {N}** — creates all in PAUSED state
2. **Approve specific** — "approve 1, 3" (by number)
3. **Modify** — "change campaign 2 budget to $8" (I'll adjust before creating)
4. **Include experiment** — approve main campaigns + the experiment
5. **Save brief only** — no API calls, just save the proposal for reference
```

**Do NOT create any campaigns without explicit user approval.**

---

### Step 7: Execute Approved Campaigns

For each approved campaign, execute in strict sequence (each step depends on previous):

#### 7a. Create Campaign

```
create_sp_campaigns(campaigns='[{
    "name": "{campaign_name}",
    "targetingType": "{MANUAL or AUTO}",
    "budget": {"budget": {amount}, "budgetType": "DAILY"},
    "startDate": "{today YYYYMMDD}",
    "state": "PAUSED",
    "portfolioId": "{portfolioId}",
    "dynamicBidding": {
        "strategy": "LEGACY_FOR_SALES",
        "placementBidding": [
            {"placement": "PLACEMENT_TOP", "percentage": {tos_pct}}
        ]
    }
}]', marketplace="US")
```

Extract `campaignId` from response. Include `PLACEMENT_PRODUCT_PAGE` and `PLACEMENT_REST_OF_SEARCH` entries in `placementBidding` if the PP/ROS defaults table specifies non-zero values for this campaign's stage/context.

#### 7b. Create Ad Group

```
create_sp_ad_groups(ad_groups='[{
    "name": "{campaign_name} - Main",
    "campaignId": "{campaignId}",
    "defaultBid": {bid_amount},
    "state": "ENABLED"
}]', marketplace="US")
```

Extract `adGroupId` from response.

#### 7c. Create Product Ads (ASINs)

```
manage_sp_product_ads(action="create", product_ads='[
    {"campaignId": "{campaignId}", "adGroupId": "{adGroupId}", "asin": "{ASIN}", "state": "ENABLED"}
]', marketplace="US")
```

For multiple ASINs, include one object per ASIN in the array.

#### 7d. Create Keywords or Targets (skip for Auto)

**For SK/MK keyword campaigns:**
```
manage_sp_keywords(action="create", keywords='[
    {"campaignId": "{campaignId}", "adGroupId": "{adGroupId}",
     "keywordText": "{keyword}", "matchType": "{EXACT/BROAD}",
     "bid": {bid_amount}, "state": "ENABLED"}
]', marketplace="US")
```

**For PT product targeting:**
```
manage_sp_targets(action="create", targets='[
    {"campaignId": "{campaignId}", "adGroupId": "{adGroupId}",
     "expression": [{"type": "asinSameAs", "value": "{competitor_ASIN}"}],
     "expressionType": "manual", "bid": {bid_amount}, "state": "ENABLED"}
]', marketplace="US")
```

#### 7e. Seed Negative Keywords

```
create_sp_campaign_negative_keywords(keywords='[
    {"campaignId": "{campaignId}", "keywordText": "{term}",
     "matchType": "NEGATIVE_PHRASE", "state": "ENABLED"}
]', marketplace="US")
```

Batch size: max 100 per API call. Split into multiple calls if needed.

#### Error Handling

| Step | If it fails... |
|------|---------------|
| 7a Campaign | Skip this campaign entirely, log failure, continue to next |
| 7b Ad Group | Log failure — campaign exists but is incomplete, note for manual cleanup |
| 7c Product Ads | **Critical** — campaign won't serve. Flag prominently. |
| 7d Keywords/Targets | For Manual: needs manual fix. For Auto: not applicable. |
| 7e Negatives | Non-critical — campaign works but without negative protection. Log. |

**Between campaigns:** Proceed to next even if one fails. Log all results.

---

### Step 8: Post-Creation Actions

#### 8a. Source Campaign Negative Insertion (PROMOTE only)

For each PROMOTE-sourced campaign, add the promoted keyword as `NEGATIVE_EXACT` in the source Auto/Broad campaign to isolate traffic:

```
create_sp_campaign_negative_keywords(keywords='[
    {"campaignId": "{source_campaign_id}", "keywordText": "{keyword}",
     "matchType": "NEGATIVE_EXACT", "state": "ENABLED"}
]', marketplace="US")
```

#### 8b. Update Agent-State

In `outputs/research/ppc-agent/state/agent-state.json`:
- Mark completed `pending_actions` as `"status": "completed"` with date
- Add entry to `applied_changes`:
```json
{
    "date": "YYYY-MM-DD",
    "action": "Created {N} campaigns via Campaign Creator",
    "campaigns_created": [
        {"name": "...", "campaignId": "...", "type": "SK", "keyword": "...", "portfolio": "...", "source": "PROMOTE", "status": "success"}
    ],
    "campaigns_failed": [],
    "negatives_inserted_in_source": [],
    "experiment_campaigns": []
}
```
- Set `"last_campaign_creator": "YYYY-MM-DD"`

#### 8c. Save Outputs

**Brief:** `outputs/research/ppc-agent/campaign-creator/{YYYY-MM-DD}-campaigns-created.md`

**Machine-readable log:** `outputs/research/ppc-agent/campaign-creator/{YYYY-MM-DD}-creation-log.json`

```json
{
    "date": "YYYY-MM-DD",
    "candidates_found": 0,
    "proposed": 0,
    "approved": 0,
    "created_success": 0,
    "created_failed": 0,
    "dedup_skipped": 0,
    "deferred": 0,
    "campaigns": [
        {
            "name": "...",
            "campaign_id": "...",
            "ad_group_id": "...",
            "type": "SK",
            "portfolio": "...",
            "portfolio_id": "...",
            "product_name": "...",
            "asin": "...",
            "keyword": "...",
            "match_type": "EXACT",
            "bid": 0.73,
            "tos_modifier": 47,
            "budget": 10.0,
            "asins": ["B0B1927HCG"],
            "negatives_seeded": 29,
            "source": "PROMOTE",
            "source_campaign_id": "...",
            "source_negative_inserted": true,
            "experiment": false,
            "priority_score": 87,
            "status": "success",
            "api_responses": {
                "campaign": "success",
                "ad_group": "success",
                "product_ads": "success",
                "keywords": "success",
                "negatives": "success"
            }
        }
    ],
    "experiments": [],
    "deferred_candidates": []
}
```

---

### Step 9: Post Notifications

Read `.claude/skills/notification-hub/SKILL.md` → "Recipe: ppc-campaign-creator".
Follow those instructions to post a summary to Slack.
If Slack MCP is unavailable, skip and note in run log.

---

### Step 10: Update LESSONS.md (mandatory)

Log entry format:

```markdown
### Run: YYYY-MM-DD
**Result:** Success / Partial / Failed

**Candidates found:** {N} ({N} PROMOTE, {N} REDIRECT, {N} PROTECT, {N} structure gap, {N} agent-state)
**Proposed:** {N}
**Approved:** {N}
**Created successfully:** {N}
**Failed:** {N}
**Source negatives inserted:** {N}
**Negatives seeded:** {N} across {N} campaigns

**What happened:**
- ...

**What didn't work:**
- ...

**Lesson learned:**
- ...

**Tokens/cost:** ~XX K tokens
```

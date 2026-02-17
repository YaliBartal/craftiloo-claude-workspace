# Search Term Analysis

**USE WHEN** user says: "search term analysis", "analyze search terms", "search term report", "negate terms", "find negatives", "keyword mining", "search term review", "ST analysis", "check search terms"

---

## What This Does

Analyzes Seller Central search term reports to generate three prioritized action lists:

1. **Negate** — Irrelevant or wasteful terms to add as negative keywords
2. **Promote** — High-performing terms to graduate to exact/phrase campaigns
3. **Discover** — New keyword opportunities worth testing

Saves 1-2 hours per week of manual search term combing.

---

## Organization & Efficiency Standards

### File Organization

```
outputs/research/search-term-analysis/
├── input/         # DROP SEARCH TERM CSVs HERE — skill auto-detects
├── briefs/        # Analysis reports (what user reads)
├── data/          # Archived search term exports
└── README.md      # Folder guide
```

### Naming Conventions

| File Type | Format | Example |
|-----------|--------|---------|
| Analysis reports | `{portfolio-slug}-search-terms-YYYY-MM-DD.md` | `cross-girl-search-terms-2026-02-17.md` |
| Multi-portfolio | `account-search-terms-YYYY-MM-DD.md` | `account-search-terms-2026-02-17.md` |
| Archived data | `{portfolio-slug}-st-export-YYYY-MM-DD.csv` | `cross-girl-st-export-2026-02-17.csv` |

### Efficiency Targets

- **< 80K tokens** per analysis
- **< 5 minutes** execution time
- **No paid API calls** — works entirely from user-provided data

### Forbidden Practices

- Do NOT auto-negate branded competitor terms without flagging — user may want to keep targeting competitors
- Do NOT recommend specific bid amounts — recommend direction (raise/lower) and magnitude
- Do NOT negate terms with fewer than 3 impressions — not enough data to judge
- Do NOT combine data from different date ranges in one analysis
- Do NOT skip low-impression terms — they may reveal targeting issues

---

## Input

### Auto-Detection (Preferred)

**The skill automatically checks `outputs/research/search-term-analysis/input/` for CSV files.**

When the skill starts:
1. Glob for `outputs/research/search-term-analysis/input/*.csv`
2. If **one CSV found** → use it automatically, tell the user which file was detected
3. If **multiple CSVs found** → list them and ask: analyze individually or combined?
4. If **no CSVs found** → ask the user to either:
   - Drop a Seller Central search term report CSV into the `input/` folder and re-run
   - Provide a file path directly
   - Paste the data

### How to Export from Seller Central

Tell user if they ask:
1. Go to **Advertising → Campaign Manager**
2. Click **Measurement & Reporting → Search Term Report** (or Sponsored Products → Search Terms tab)
3. Set date range: **Last 7 days, exclude last 2 days** (per PPC SOP)
4. Filter by portfolio (optional — or export all)
5. Download as CSV
6. Drop into `outputs/research/search-term-analysis/input/`

### Data Requirements

**Expected columns** (from Seller Central search term export):
- Campaign Name
- Ad Group Name
- Targeting (the keyword/ASIN being targeted)
- Match Type (broad, phrase, exact, or targeting expression)
- Customer Search Term (what the shopper actually typed)
- Impressions, Clicks, CTR
- Spend, CPC
- Orders (7-day), Sales (7-day)
- ACoS, ROAS (if available — can calculate from spend/sales)

---

## Process

### Step 1: Find & Load Data

1. **Auto-detect:** Glob for `outputs/research/search-term-analysis/input/*.csv`
   - If 1 file found → read it, tell user: "Found: {filename} — analyzing now."
   - If multiple files → list them, ask user which to analyze (or all)
   - If no files → check if user provided a path or pasted data. If neither, tell them: "Drop your Seller Central search term report CSV into `outputs/research/search-term-analysis/input/` and run again."
2. If user provided a **file path**, read that file directly
3. Read the CSV file contents

### Step 2: Parse & Contextualize

1. Parse the search term data from the CSV
2. Identify which **portfolio(s)** and **campaign(s)** are represented
3. Cross-reference campaign names against known campaign types from PPC review:
   - Auto, Broad, SK, MK, PAT, TOS, Video, SD, Shield, Catch-all
4. Note the **match type** for each row — this affects recommendations:
   - Broad match terms → candidates for phrase/exact promotion
   - Auto-discovered terms → candidates for manual campaign migration
   - Exact match terms → already targeted, focus on bid optimization

### Step 3: Calculate Search Term Metrics

For EACH unique search term, calculate:

| Metric | Formula |
|--------|---------|
| **Total Impressions** | Sum across all campaigns targeting this term |
| **Total Clicks** | Sum across all campaigns |
| **Total Spend** | Sum across all campaigns |
| **Total Orders** | Sum across all campaigns |
| **Total Sales** | Sum across all campaigns |
| **CTR** | Total Clicks / Total Impressions |
| **CVR** | Total Orders / Total Clicks |
| **ACoS** | Total Spend / Total Sales (if sales > 0) |
| **CPC** | Total Spend / Total Clicks |

### Step 4: Classify Each Search Term

Apply this decision matrix to classify every search term:

#### Category 1: NEGATE (Add as negative keyword)

| Condition | Priority | Reasoning |
|-----------|----------|-----------|
| **$10+ spend, 0 orders** | P1 — Negate immediately | Bleeding money with zero return |
| **$5-10 spend, 0 orders, CTR < 0.3%** | P1 — Negate immediately | Low relevance + wasted spend |
| **$5-10 spend, 0 orders, CTR > 0.3%** | P2 — Negate soon | Getting clicks but not converting |
| **ACoS > 100%, 3+ clicks** | P1 — Negate immediately | Spending more than earning |
| **ACoS > 70%, 5+ clicks** | P2 — Negate or reduce | Very unprofitable |
| **Clearly irrelevant term** | P1 — Negate immediately | Wrong product/audience entirely |

**Irrelevance signals** (auto-flag for negation):
- Adult/inappropriate terms appearing on kids products
- Wrong product category entirely (e.g., "sewing machine" on a sewing kit)
- Wrong age group (e.g., "adult" terms on kids products, unless the product targets adults)
- Wrong craft type (e.g., "crochet hook" on an embroidery kit)
- Competitor brand names WITH high ACoS (they're searching for a specific competitor and not converting)
- Single-letter or gibberish terms

#### Category 2: PROMOTE (Graduate to exact/phrase campaigns)

| Condition | Priority | Action |
|-----------|----------|--------|
| **3+ orders, ACoS < portfolio target, from Auto campaign** | P1 — Promote now | Add as exact match in manual campaign |
| **3+ orders, ACoS < portfolio target, from Broad campaign** | P1 — Promote now | Add as phrase or exact match |
| **2 orders, ACoS < 30%, CVR > 15%** | P2 — Watch & promote | Strong signal, needs more data |
| **5+ orders, ACoS 30-40%** | P2 — Promote with lower bid | Converting but expensive — control via exact |
| **High CVR (>15%) + reasonable ACoS from broad/auto** | P2 — Promote | Move to tighter match type for control |

**Promotion logic:**
- From **Auto** → Add to **Broad or Exact** manual campaign
- From **Broad** → Add to **Phrase or Exact** campaign
- From **Phrase** → Add to **Exact** campaign
- When promoting, also add as **negative exact** in the source campaign to prevent cannibalization

#### Category 3: DISCOVER (New keyword opportunities)

| Condition | Signal |
|-----------|--------|
| **Converting term NOT in any manual campaign** | New keyword to test |
| **Term with high impressions + decent CTR but from Auto only** | Market demand exists, worth testing manually |
| **Variant/misspelling of known high-performer** | Add as separate exact target |
| **Seasonal/trending term appearing for first time** | Time-sensitive opportunity |
| **Long-tail term with strong CVR** | Low competition opportunity |

Cross-reference against `context/search-terms.md` to check if discovered terms are already tracked.

### Step 5: Relevance Check Against Business Context

For each term flagged for negation, verify against business context:
- Check `context/business.md` for product categories — don't negate terms that ARE relevant to the catalog
- Check `context/search-terms.md` for tracked keywords — don't negate known high-value terms
- Flag competitor brand names (Kraftlab, Fanzbo, Krafun, etc.) separately — these need human decision

### Step 6: Generate Report

Output the full analysis as a structured markdown report. Follow the exact output format below.

---

## Output Format

```markdown
# Search Term Analysis: {Portfolio/Campaign Name}

**Date:** {YYYY-MM-DD}
**Data Window:** {date range from the export}
**Source:** {Campaign type(s) — Auto / Broad / All}
**Total Search Terms Analyzed:** {X}

---

## Summary Dashboard

| Metric | Value |
|--------|-------|
| Total unique search terms | X |
| Total spend on analyzed terms | $X |
| Total sales from analyzed terms | $X |
| Overall ACoS | X% |
| Terms with 0 orders | X (X% of total) |
| Spend on 0-order terms | $X (X% of total spend) |
| Terms recommended for negation | X |
| Terms recommended for promotion | X |
| New keyword opportunities | X |
| **Estimated weekly savings from negations** | **$X** |

---

## P1 — NEGATE IMMEDIATELY

These terms are wasting budget with zero or terrible return. Add as negative keywords today.

| # | Search Term | Source Campaign | Match Type | Impressions | Clicks | Spend | Orders | ACoS | Reason |
|---|-------------|----------------|------------|-------------|--------|-------|--------|------|--------|
| 1 | {term} | {campaign} | {broad/auto} | X | X | $X | 0 | — | {reason} |

**Negation instructions:**
- Add as **negative exact** in the source campaign
- If the term is broadly irrelevant (e.g., "sewing machine"), add as **negative phrase** at the campaign or portfolio level

**Total spend recoverable:** $X/week

---

## P2 — NEGATE SOON (Review First)

These terms show poor performance but may need a second look before negating.

| # | Search Term | Source Campaign | Match Type | Impressions | Clicks | Spend | Orders | ACoS | Reason |
|---|-------------|----------------|------------|-------------|--------|-------|--------|------|--------|
| 1 | {term} | {campaign} | {type} | X | X | $X | X | X% | {reason} |

**Note:** Review these terms — some may be worth keeping at lower bids rather than negating.

---

## P1 — PROMOTE NOW

These terms are converting well and should be graduated to tighter match types for better control and efficiency.

| # | Search Term | Source Campaign | Current Match | Orders | Sales | ACoS | CVR | Recommended Action |
|---|-------------|----------------|---------------|--------|-------|------|-----|--------------------|
| 1 | {term} | {campaign} | {auto/broad} | X | $X | X% | X% | {Add to [campaign type] as [match type]} |

**Promotion checklist:**
- [ ] Add term as exact/phrase in target campaign
- [ ] Add as negative exact in source campaign (prevent cannibalization)
- [ ] Set initial bid at current CPC or slightly below
- [ ] Monitor for 1 week after promotion

---

## P2 — WATCH & PROMOTE LATER

Strong signals but need more data before promoting.

| # | Search Term | Source Campaign | Current Match | Orders | Sales | ACoS | CVR | Why Watching |
|---|-------------|----------------|---------------|--------|-------|------|-----|--------------|
| 1 | {term} | {campaign} | {type} | X | $X | X% | X% | {reason} |

---

## NEW KEYWORD OPPORTUNITIES

Terms discovered through auto/broad campaigns that aren't currently targeted manually.

| # | Search Term | Where Found | Impressions | Clicks | Orders | ACoS | Opportunity |
|---|-------------|-------------|-------------|--------|--------|------|-------------|
| 1 | {term} | {campaign} | X | X | X | X% | {why it's interesting} |

**Cross-reference with tracked keywords:** {Note which are already in context/search-terms.md and which are new}

---

## COMPETITOR BRAND TERMS (Human Decision Required)

These are competitor brand name searches appearing in your campaigns. Decide whether to keep targeting or negate.

| # | Search Term | Spend | Orders | ACoS | Recommendation |
|---|-------------|-------|--------|------|----------------|
| 1 | {competitor term} | $X | X | X% | {Keep if profitable / Negate if wasteful} |

---

## Campaign-Level Insights

### {Campaign Name} — Search Term Health

| Metric | Value |
|--------|-------|
| Total search terms | X |
| Profitable terms (ACoS < target) | X (X%) |
| Unprofitable terms (ACoS > target) | X (X%) |
| Zero-order terms | X (X%) |
| Spend on zero-order terms | $X |
| Top converting term | {term} (X% CVR) |
| Most expensive zero-order term | {term} ($X spent) |

[Repeat for each campaign in the data]

---

## Action Summary

### Do Today (5 minutes)
- [ ] Negate {X} P1 terms (saves ~$X/week)
- [ ] Promote {X} P1 terms to exact campaigns

### Do This Week (15 minutes)
- [ ] Review {X} P2 negation candidates
- [ ] Set up {X} new keyword tests from discoveries
- [ ] Review competitor brand term decisions

### Track Next Week
- [ ] Monitor {X} promoted terms for performance
- [ ] Re-run analysis with fresh data to validate negations

---

## Appendix: All Search Terms by Spend

<details>
<summary>Click to expand full search term table (sorted by spend, highest first)</summary>

| Search Term | Campaign | Impressions | Clicks | Spend | Orders | Sales | ACoS | CVR | Classification |
|-------------|----------|-------------|--------|-------|--------|-------|------|-----|----------------|
| {term} | {campaign} | X | X | $X | X | $X | X% | X% | {Negate/Promote/Keep/Watch} |

</details>
```

---

## Output Location

1. Save the report to: `outputs/research/search-term-analysis/briefs/{portfolio-slug}-search-terms-YYYY-MM-DD.md`
2. **Copy** the input CSV to: `outputs/research/search-term-analysis/data/{portfolio-slug}-st-export-YYYY-MM-DD.csv`
3. **Delete** the original CSV from `outputs/research/search-term-analysis/input/` to keep clean for next run

---

## Multi-Portfolio Mode

When user provides search term reports for **multiple portfolios** (or an account-wide export):

1. If a single CSV contains multiple portfolios → group by portfolio name, analyze each separately
2. If multiple CSVs → analyze each, then generate a combined summary
3. Combined summary goes to: `outputs/research/search-term-analysis/briefs/account-search-terms-YYYY-MM-DD.md`

The combined summary should include:
- **Cross-portfolio negation list** — terms that are wasteful everywhere
- **Cross-portfolio winners** — terms converting well across multiple products
- **Portfolio-specific recommendations** — brief per portfolio

---

## Integration with PPC Review

This skill complements the PPC Portfolio Review skill:

- **PPC Review** identifies campaigns that need search term analysis (P2 action: "check search terms")
- **This skill** does the deep dive into those search terms
- When PPC Review flags "investigate search terms for Campaign X", run this skill on that campaign's search term export

**Shared decision framework:**
- Uses the same ACoS targets by portfolio stage (Launch/Growth/Optimization/Maintenance)
- Uses the same campaign type classifications
- References the same portfolio stage thresholds from PPC Review

| Portfolio Stage | ACoS Target for Negation Threshold | Promotion ACoS Threshold |
|-----------------|-------------------------------------|--------------------------|
| Launch | Negate at ACoS > 80% (flexible) | Promote at ACoS < 50% |
| Growth | Negate at ACoS > 60% | Promote at ACoS < 35% |
| Optimization | Negate at ACoS > 50% | Promote at ACoS < 30% |
| Maintenance | Negate at ACoS > 50% | Promote at ACoS < 30% |
| Catch-all | Negate at ACoS > 40% | Promote at ACoS < 25% |

---

## Execution Checklist

Before delivering the report, verify:

- [ ] All search terms are classified (Negate / Promote / Discover / Keep / Watch)
- [ ] Terms are sorted by spend within each category (highest spend first)
- [ ] P1 negation terms all have clear reasoning
- [ ] Promotion candidates include specific instructions (which campaign, which match type)
- [ ] Competitor brand terms are separated for human decision (not auto-negated)
- [ ] Business context cross-reference is done (no relevant terms accidentally flagged)
- [ ] Estimated savings are calculated from P1 negation spend
- [ ] Campaign-level insights are included for each campaign in the data
- [ ] Action summary has concrete, time-boxed steps
- [ ] Report is saved to correct output location
- [ ] Input CSV is archived to data/ folder

---

## Error Handling

| Issue | Response |
|-------|----------|
| CSV has unexpected columns | Map available columns to expected ones. Flag missing data. |
| No "Customer Search Term" column | Cannot analyze — ask user to re-export with search terms included |
| Very few search terms (< 10) | Warn that data is too thin for reliable decisions. Suggest longer date range. |
| All terms have 0 orders | Portfolio may have conversion issues beyond search terms. Flag for PPC review. |
| Mixed portfolios in one CSV | Group by portfolio, ask user if they want combined or separate analysis |
| Data appears to include last 2 days | Warn about unreliable attribution data per PPC SOP |
| Search term matches the targeting keyword exactly | Skip classification — this is expected behavior, not a discovery |

---
name: listing-optimizer
description: Scores existing Craftiloo listings against competitors on title/bullets/description optimization, cross-references with rank and sales data, and produces specific rewrite recommendations
triggers:
  - listing audit
  - audit listing
  - listing optimizer
  - optimize listing
  - listing score
  - listing health
  - how is my listing
  - listing check
  - portfolio scan
  - listing scan
output_location: outputs/research/listing-optimizer/
---

# Listing Optimizer / Audit

**USE WHEN** user says: "listing audit", "audit listing", "listing optimizer", "optimize listing", "listing score", "listing health", "how is my listing", "listing check", "portfolio scan", "listing scan"

---

## ⚠️ BEFORE YOU START — Read Lessons

**MANDATORY FIRST STEP:** Read `LESSONS.md` in this skill's folder before doing anything else.

1. Read `.claude/skills/listing-optimizer/LESSONS.md`
2. Check **Known Issues** — plan around these
3. Check **Repeat Errors** — if you encounter one during this run, tell the user immediately: _"⚠️ Repeat issue (×N): [description]"_
4. Apply all past lessons to this run

**Do NOT skip this step.**

---

## What This Does

Scores existing Craftiloo listings against competitors and produces actionable rewrite recommendations. Two modes:

1. **Single Product Audit** — Deep audit of one Craftiloo ASIN: Ranking Juice scores vs top 5 competitors, keyword gap analysis, root word coverage, rank trend analysis, CVR comparison, and AI Copywriter alternatives across all 4 modes
2. **Portfolio Scan** — Quick scan across ALL 13 hero products: optimization scores vs niche averages, flagging underperformers, prioritizing fixes by (optimization gap x revenue), and top 3 quick wins per product

**Core insight:** "Your listing is weak HERE, and you are losing rank HERE — and these two things are correlated."

**Complements:**
- **Listing Creator** — This skill audits existing listings; Listing Creator generates from scratch
- **Customer Review Analyzer** — Review language feeds rewrite recommendations
- **Weekly PPC Analysis** — CVR data validates listing weaknesses identified here
- **Daily Market Intel** — Sales velocity context for prioritization

---

## Organization & Efficiency Standards

### File Organization

```
outputs/research/listing-optimizer/
├── briefs/                 # Audit reports (what user reads)
├── rewrites/               # AI Copywriter output + rewrite suggestions
│   └── YYYY-MM-DD/         # Date-stamped rewrite batches
├── snapshots/              # Historical scores for trend tracking
│   └── {slug}-snapshot-YYYY-MM-DD.json
└── README.md               # Folder guide
```

### Naming Conventions (STRICT)

| File Type | Format | Example |
|-----------|--------|---------|
| **Single audit report** | `{product-slug}-listing-audit-YYYY-MM-DD.md` | `fairy-sewing-listing-audit-2026-02-23.md` |
| **Portfolio scan report** | `portfolio-scan-YYYY-MM-DD.md` | `portfolio-scan-2026-02-23.md` |
| **AI Copywriter output** | `{product-slug}-rewrites-YYYY-MM-DD.md` | `fairy-sewing-rewrites-2026-02-23.md` |
| **Snapshot** | `{slug}-snapshot-YYYY-MM-DD.json` | `fairy-sewing-snapshot-2026-02-23.json` |
| **Portfolio snapshot** | `portfolio-snapshot-YYYY-MM-DD.json` | `portfolio-snapshot-2026-02-23.json` |

### Efficiency Targets

- **< 80K tokens** per single audit
- **< 60K tokens** per portfolio scan (lighter per-product analysis)
- **< 10 minutes** execution time (single audit)
- **< 8 minutes** execution time (portfolio scan)
- **No Apify cost** for portfolio scan (DataDive + Seller Board only)
- **< $0.10 Apify cost** for single audit (competitor listings only — our listing comes from Amazon SP-API for free)
- **DataDive AI Copywriter:** runs only in Single Audit mode, all 4 modes

### Forbidden Practices

- ❌ Do NOT scrape competitor listings in Portfolio Scan mode — use DataDive Ranking Juice scores only
- ❌ Do NOT run AI Copywriter in Portfolio Scan mode — too expensive across 13 products
- ❌ Do NOT recommend removing high-volume keywords without checking Rank Radar data first
- ❌ Do NOT treat Ranking Juice scores below 50 as automatically "bad" — compare against the niche average
- ❌ Do NOT skip the CVR/sales cross-reference — scores without performance context are misleading
- ❌ Do NOT recommend keyword stuffing — readability and conversion matter more than cramming keywords
- ❌ Do NOT consume DataDive tokens (`create_niche_dive`) — use only existing niches and radars

---

## Input

### Required

1. **Mode selection** — Ask user: "Single Product Audit or Portfolio Scan?"
2. **Product selection (Single Audit only):** Which product? (name, ASIN, or category from hero-products.md)

### Auto-Loaded

3. **Context files:**
   - `context/hero-products.md` — 13 hero product ASINs with specs and key selling points
   - `context/competitors.md` — 72 competitor ASINs by category with market share context
   - `context/products.md` — Full product catalog with kit contents and specs
   - `context/business.md` — Brand info, PPC portfolio stages, competitor names
   - `context/search-terms.md` — Tracked keywords by category with search volume and relevance

### How to Start

When skill triggers:
1. Ask: **"Single Product Audit or Portfolio Scan?"**
   - **Single Audit:** "Which product? (name or ASIN)" — then confirm the product, its niche, and top 5 competitors
   - **Portfolio Scan:** No further input needed — scans all 13 hero products automatically
2. Confirm estimated cost and data sources before proceeding:
   - **Single Audit:** "This will use DataDive (free), Amazon SP-API (free), Seller Board (free), and Apify (~$0.08 for competitor listing scraping). Proceed?"
   - **Portfolio Scan:** "This uses DataDive, Amazon SP-API, and Seller Board only (no Apify cost). Proceed?"

---

## Process

### Step 1: Load Context & Identify Products

1. Load `context/hero-products.md` — get all 13 hero product ASINs and specs
2. Load `context/competitors.md` — get competitor ASINs per category with market share
3. Load `context/products.md` — get detailed kit contents (for listing content verification)
4. Load `context/business.md` — get PPC portfolio stages, target audience, brand context
5. Load `context/search-terms.md` — get tracked keywords with search volume and relevance scores

**Build product list based on mode:**

| Mode | Our Products | Competitors | DataDive Niches |
|------|-------------|-------------|-----------------|
| **Single Audit** | 1 (selected product) | Top 5 from `competitors.md` for that category | 1 niche (matching category) |
| **Portfolio Scan** | All 13 hero products | Niche averages only (no individual competitor detail) | All relevant niches (up to 8) |

6. **Match each hero product to its DataDive niche:**

Call `list_niches(page_size=50)` to get all active niches. Match each hero product ASIN to its niche using the niche label and hero keyword. Known mappings:

| Hero Product | ASIN | DataDive Niche ID | Niche Label |
|-------------|------|-------------------|-------------|
| Cross Stitch Girls | B08DDJCQKF | b4Nisjv3xy | Cross Stitch Kits for Kids |
| 10 Embroidery Kit | B09X55KL2C | Er21lin0KC | Beginners Embroidery Kit for Kids |
| 4 Embroidery Flowers | B0DC69M3YD | gfot2FZUBU | Embroidery Stitch Practice Kit |
| Fairy Sewing Kit | B09WQSBZY7 | RmbSD3OH6t | Sewing Kit for Kids |
| Dessert Sewing Kit | B096MYBLS1 | RmbSD3OH6t | Sewing Kit for Kids |
| Latch Hook Pencil Cases | B08FYH13CL | VqBgB5QQ07 | Latch Hook Kit for Kids |
| Latch Hook Rainbow Heart | B0F8R652FX | VqBgB5QQ07 | Latch Hook Kit for Kids |
| Knitting Cat & Hat | B0F8DG32H5 | O6b4XATpTj | Loom Knitting |
| 48 Mini Fuse Beads | B09THLVFZK | AY4AlnSj9g | Mini Perler Beads |
| 10mm Big Fuse Beads | B07D6D95NG | (resolve from list_niches) | Biggie Beads / Fuse Beads |
| Princess Lacing Card | B0FQC7YFX6 | Aw4EQhG6bP | Lacing Cards for Kids |
| Needlepoint Cat Wallet | B09HVSLBS6 | (resolve from list_niches) | Needlepoint |
| Felt Unicorn Cross Stitch | B0F6YTG1CH | b4Nisjv3xy | Cross Stitch Kits for Kids |

7. If any hero product has no matching niche, note it and skip DataDive-specific analysis for that product

### Step 2: Load Previous Snapshot (for Trend Comparison)

1. **Single Audit:** Glob for `outputs/research/listing-optimizer/snapshots/{product-slug}-snapshot-*.json`
2. **Portfolio Scan:** Glob for `outputs/research/listing-optimizer/snapshots/portfolio-snapshot-*.json`
3. If snapshots exist:
   - Load the **most recent** snapshot
   - Note the date and how many days ago
   - Store previous data for comparison in Step 10
4. If no snapshots:
   - Note this is the first run (no trend comparison available)
   - First run establishes the baseline

### Step 3: Fetch DataDive Ranking Juice Scores

**PURPOSE:** Get per-ASIN listing optimization scores (title, bullets, description) for our products AND their competitors.

**MCP Tool:** `get_niche_ranking_juices(niche_id, page_size=50)`

**For each relevant niche (1 for Single Audit, up to 8 for Portfolio Scan):**

| Field | What It Contains | Used For |
|-------|------------------|----------|
| `asin` | Product ASIN | Match to our hero / competitor |
| Title optimization score | Title keyword coverage (0-100) | Title quality assessment |
| Bullets optimization score | Bullet keyword coverage (0-100) | Bullet quality assessment |
| Description optimization score | Description keyword coverage (0-100) | Description quality assessment |
| Overall score | Combined optimization (0-100) | Composite listing quality |

**Extract and organize:**
- Our hero product score for title, bullets, description
- Top 5 competitor scores (for Single Audit)
- Niche average scores (for both modes)
- Niche max scores (benchmark — who has the best listing?)
- Delta: our score minus niche average for each dimension

**Fallback if API fails:** Note "Ranking Juice data unavailable — listing quality scores cannot be calculated. Proceeding with keyword and rank analysis only." Do NOT block the analysis.

### Step 4: Fetch DataDive Master Keyword List (Single Audit Only)

**PURPOSE:** Get the full keyword universe with search volumes, relevancy, and per-ASIN organic rank positions.

**MCP Tool:** `get_niche_keywords(niche_id, page_size=200)`

| Field | What It Contains | Used For |
|-------|------------------|----------|
| `keyword` | Search term | Keyword gap analysis |
| `searchVolume` | Monthly search volume | Prioritizing gaps by impact |
| `relevancy` | Core / Related / Outlier | Filtering to important keywords |
| Organic rank columns | Per-ASIN organic rank positions | Who ranks for what |

**Extract:**
- All **Core** and **Related** keywords (skip Outliers)
- Our hero product's organic rank per keyword
- Top 5 competitors' organic ranks per keyword
- Keywords where we rank 11-20 (almost page 1 = quick wins)
- Keywords where competitors rank top 10 but we do not (keyword gaps)
- Keywords we rank top 5 that competitors do not (our unique strengths)

**For Portfolio Scan:** SKIP this step. Use Ranking Juice scores as proxy.

**Fallback if API fails:** Note "Master Keyword List unavailable — keyword gap analysis skipped." Continue with other data.

### Step 5: Fetch DataDive Keyword Roots (Single Audit Only)

**PURPOSE:** Identify which root word clusters are missing from our listing copy.

**MCP Tool:** `get_niche_roots(niche_id, page_size=100)`

| Field | What It Contains | Used For |
|-------|------------------|----------|
| `root` | Root word (e.g., "stitch", "kit", "beginner") | Root coverage analysis |
| `frequency` | How many keywords contain this root | Root importance |
| `broadSearchVolume` | Aggregate search volume for keywords with this root | Prioritizing by impact |

**Extract:**
- All roots sorted by broadSearchVolume (highest first)
- For each root: check if it appears in our listing (title, bullets, description)
- Flag roots missing from our listing but with high broadSearchVolume
- Compare our root coverage against the top 3 competitors

**For Portfolio Scan:** SKIP this step.

**Fallback if API fails:** Note "Keyword roots unavailable — root coverage analysis skipped." Continue with other data.

### Step 6: Fetch DataDive Rank Radar Data (Rank Trends)

**PURPOSE:** Identify keywords where our ranking is declining — these correlate with listing weakness and need urgent attention.

**How to fetch:**

1. Call `list_rank_radars(page_size=50)` to get all active Rank Radars
2. Match Rank Radars to the hero product(s) being audited using the `asin` field
3. **Single Audit:** For the matched Rank Radar, fetch 30-day keyword rankings:
   - `get_rank_radar_data(rank_radar_id, start_date={30 days ago}, end_date={today})`
   - Dates in YYYY-MM-DD format
4. **Portfolio Scan:** Only use the summary data from `list_rank_radars()` (top10KW, top50KW counts). Skip per-keyword daily data to save tokens.

| Field | What It Contains | Used For |
|-------|------------------|----------|
| `keyword` | Search term tracked | Matching to MKL keywords |
| `searchVolume` | Monthly search volume | Impact weighting |
| Daily `organicRank` | Daily organic position | Trend analysis |
| Daily `impressionRank` | Daily sponsored position | PPC context |

**Calculate for each keyword (Single Audit):**
- **7-day trend:** Compare last 7 days avg vs previous 7 days avg
- **30-day trend:** Compare last 7 days avg vs first 7 days of 30-day window
- **Direction:** Improving (rank going down) / Stable (< 3 position change) / Declining (rank going up)

**Key outputs:**
- Keywords declining in rank (7-day + 30-day) — "listing is failing here"
- Keywords in positions 11-20 (almost page 1) — "quick wins if listing improves"
- Keywords improving — "listing is working here, do not change"

**Fallback if API fails:** Note "Rank Radar data unavailable — rank trend analysis skipped." Continue with optimization scores.

### Step 7: Fetch Sales & Conversion Data

**PURPOSE:** Get actual CVR, sessions, organic/PPC sales split to correlate listing quality with conversion performance.

**Two data sources — Amazon SP-API is primary, Seller Board is secondary:**

#### 7a: Amazon SP-API Sales & Traffic Report (Primary — most accurate CVR)

**Why primary:** Amazon's `GET_SALES_AND_TRAFFIC_REPORT` provides the most accurate session and conversion data directly from Amazon, without third-party estimation.

**How to fetch (3-step async flow):**
1. Call `create_report(report_type="GET_SALES_AND_TRAFFIC_REPORT", marketplace="US", days_back=30)`
   - Returns a `reportId`
2. Poll `get_report_status(report_id={reportId})` every 30 seconds until status is `DONE`
   - Typical time: 30-90 seconds
   - If status is `FATAL` or `CANCELLED`, fall through to Seller Board (Step 7b)
   - Max 5 polls (2.5 minutes) — if still not DONE, fall through to Seller Board
3. Call `get_report_document(document_id={documentId from status response})`
   - Returns CSV/TSV with per-ASIN daily data

| Field | What It Contains | Used For |
|-------|------------------|----------|
| ASIN | Product ASIN | Matching |
| Sessions | Listing page views (Amazon-verified) | Traffic volume |
| Unit Session Percentage | Conversion rate (Amazon-verified) | CVR comparison — most reliable source |
| Page Views | Total page views including variations | Traffic context |
| Units Ordered | Total units | Sales velocity |
| Ordered Product Sales | Revenue $ | Revenue context |

#### 7b: Seller Board Sales Detailed (Secondary — profit & PPC split)

**MCP Tool:** `get_sales_detailed_report()`

**Always fetch this regardless of SP-API success** — Seller Board provides data that Amazon SP-API does not:

| Field | What It Contains | Used For |
|-------|------------------|----------|
| Organic sales column | Organic sales $ | Organic vs PPC split (SP-API doesn't separate these) |
| PPC sales column | PPC sales $ | PPC dependency calculation |
| Net Profit column | Net profit $ | Profitability context |
| Margin column | Profit margin % | Health indicator |
| COGS column | Cost of goods | Margin validation |

#### How to merge the two sources:

| Metric | Primary Source | Fallback Source |
|--------|--------------|----------------|
| **CVR (Unit Session %)** | Amazon SP-API | Seller Board |
| **Sessions** | Amazon SP-API | Seller Board |
| **Organic vs PPC sales split** | Seller Board (only source) | — |
| **Net Profit / Margin** | Seller Board (only source) | — |
| **Revenue** | Amazon SP-API | Seller Board |
| **Units** | Amazon SP-API | Seller Board |

**For Single Audit — extract for our product and compare to portfolio averages:**
- CVR — is our listing converting well?
- Sessions — are we getting traffic?
- Organic vs PPC sales split — are we PPC dependent?
- Revenue and profit — financial context for prioritization

**For Portfolio Scan — extract for ALL hero products:**
- CVR per product — flag products with below-average CVR
- Revenue per product — for weighting the prioritization formula
- Calculate: **Priority Score = (niche_avg_score - our_score) x monthly_revenue**
- Higher priority score = fix this listing first

**Fallback if both fail:** Note "Sales data unavailable — CVR and revenue context skipped. Prioritization will be based on optimization scores only." Continue without.

### Step 8: Fetch Current Listing Copy

**PURPOSE:** Get the actual current title, bullets, and description text for our product and top competitors.

**Two sources — Amazon SP-API for our listing (free), Apify for competitor listings:**

#### 8a: Our Listing Copy via Amazon SP-API (Free — No Apify Cost)

**How to fetch (3-step async flow):**
1. Call `get_my_listings(marketplace="US")`
   - This initiates a `GET_MERCHANT_LISTINGS_ALL_DATA` report
   - Returns a `reportId`
2. Poll `get_report_status(report_id={reportId})` every 30 seconds until status is `DONE`
   - Typical time: 30-90 seconds
   - Max 5 polls (2.5 minutes)
3. Call `get_report_document(document_id={documentId from status response})`
   - Returns TSV with ALL Craftiloo listings

**Note:** If the Sales & Traffic report (Step 7a) is still processing, you can initiate this report request in parallel — Amazon allows multiple concurrent report requests.

| Field | What It Contains | Used For |
|-------|------------------|----------|
| `item-name` | Full product title | Title keyword analysis |
| `item-description` | Product description text | Description analysis |
| `bullet-point-1` through `bullet-point-5` | Individual bullet points | Bullet content analysis |
| `price` | Current price | Competitive context |
| `quantity` | Available inventory | Stock context |
| `asin1` | ASIN identifier | Matching to target product |

**Extract for the target product:**
- Full title text + character count
- All 5 bullet points
- Description text
- Price

**For Portfolio Scan:** Also fetch this report — it covers ALL products in one call. Use the listing copy to do basic keyword presence checks against Ranking Juice data (which keywords from the niche are in/not in the title). This is free and adds value to the scan.

**Fallback if SP-API report fails:** Fall through to Apify for our ASIN (add it to the competitor batch in Step 8b).

#### 8b: Competitor Listing Copy via Apify (Single Audit Only)

**Apify Actor:** `junglee/amazon-product-scraper`

```json
{
  "asins": ["{competitor-1}", "{competitor-2}", "{competitor-3}", "{competitor-4}", "{competitor-5}"],
  "amazon_domain": "www.amazon.com"
}
```

**Batching rules:**
- 5 competitor ASINs per call (our product handled by SP-API above)
- If SP-API failed for our listing, add our ASIN here (6 total)
- Use async mode
- Timeout after 3 minutes — use whatever data collected

| Field | What It Contains | Used For |
|-------|------------------|----------|
| `title` | Full product title | Title keyword comparison |
| `bullets` | Bullet points array | Bullet content comparison |
| `description` | Product description / A+ content text | Description comparison |
| `price` | Current price | Competitive context |
| `stars` | Rating | Social proof context |
| `reviewsCount` | Review count | Social proof context |

**Extract and analyze (combining SP-API + Apify data):**
- Keyword presence in our title vs competitor titles
- Root word coverage in our bullets vs competitor bullets
- Character counts: are we using available space?
- Keyword front-loading: primary keywords near title start?

**For Portfolio Scan:** SKIP Apify entirely. Use SP-API listing data + Ranking Juice scores.

**Fallback if Apify fails:** Note "Competitor listing scraping failed — competitor copy comparison unavailable. Our listing analysis continues using SP-API data + DataDive scores." Continue with our listing data from SP-API.

### Step 9: Run DataDive AI Copywriter (Single Audit Only)

**PURPOSE:** Generate optimized alternative listing copy across all 4 AI modes for comparison and rewrite inspiration.

**MCP Tool:** `run_ai_copywriter(niche_id, mode, product_name, product_description)`

**Run for ALL 4 modes:**

| Mode | What It Generates | Best For |
|------|-------------------|----------|
| `cosmo` | COSMO-optimized copy (Amazon's algorithm) | Best overall ranking signals |
| `ranking-juice` | Copy optimized for Ranking Juice scores | Maximizing optimization scores |
| `nlp` | NLP-optimized copy (natural language) | Human readability + search |
| `cosmo-rufus` | COSMO + Rufus-optimized (AI shopping assistant) | Future-proofing for Rufus |

**Input for each call:**
- `niche_id`: The matched DataDive niche ID from Step 1
- `mode`: One of the 4 modes above
- `product_name`: From `context/hero-products.md`
- `product_description`: Brief description from `context/products.md` (kit contents + key selling points)

**Extract from each mode:**
- Suggested title
- Suggested bullet points
- Suggested description
- Compare each mode's output against our current listing
- Highlight phrases/keywords that appear in AI output but not in our current listing

**For Portfolio Scan:** SKIP this step entirely (too expensive across 13 products).

**Fallback if AI Copywriter fails:** Note which modes failed. Continue with manual rewrite recommendations based on keyword gap analysis.

### Step 10: Correlation Analysis — Connecting Listing Weakness to Rank Decline

**PURPOSE:** This is the core value of the skill — connecting "where the listing is weak" to "where we are losing rank."

**For Single Audit:**

1. **Keyword Gap → Rank Position:** For each Core keyword missing from our listing:
   - What is our organic rank? (from Rank Radar or MKL)
   - What are competitor ranks? (from MKL)
   - Is our rank declining on this keyword? (from Rank Radar trends)
   - **Correlation:** Missing keyword + declining rank = HIGH PRIORITY rewrite

2. **Root Word Gap → Rank Cluster:** For each high-volume root missing from our listing:
   - How many keywords contain this root?
   - What is our average rank across those keywords?
   - Are those keywords trending up or down?
   - **Correlation:** Missing root + poor average rank on root-cluster keywords = ROOT PRIORITY

3. **Ranking Juice Score → CVR:**
   - Our Ranking Juice scores vs CVR (from Seller Board)
   - Competitor Ranking Juice scores vs their estimated sales (from DataDive competitors)
   - **Correlation:** Low Ranking Juice + low CVR = listing quality is hurting conversion

4. **Rank 11-20 Keywords → Quick Wins:**
   - Keywords where we rank 11-20 AND the keyword is Core/Related
   - Check: is this keyword in our title? In our bullets?
   - If NOT in listing → adding it could push us to page 1
   - **Priority by:** searchVolume x (21 - currentRank) — higher = bigger opportunity

**For Portfolio Scan:**
- Simplified: Flag products where Ranking Juice < niche average AND CVR < portfolio average
- These products have both listing quality AND conversion issues — highest priority for Single Audit

### Step 11: Generate Rewrite Recommendations (Single Audit Only)

Based on all data collected, produce specific rewrite suggestions:

**Title Recommendations:**
- Current title with word count and character count
- Specific keywords to ADD (from gap analysis) with search volume
- Specific keywords to MOVE FORWARD (front-loading high-volume terms)
- 2-3 rewritten title options incorporating changes
- Compare against AI Copywriter title suggestions (all 4 modes)

**Bullet Recommendations:**
- For each of 5 bullets: current text, what is missing, suggested rewrite
- Root words to incorporate
- Customer language from `context/search-terms.md`
- Compare against AI Copywriter bullet suggestions

**Description Recommendations:**
- Current description assessment
- Missing keywords/roots to add
- AI Copywriter description alternatives

**Backend Keywords:**
- Keywords NOT in title or bullets that should go in backend
- Compare against `context/search-terms.md` for tracked terms not yet in backend

### Step 12: Save Snapshot

**Single Audit Snapshot** — save to `outputs/research/listing-optimizer/snapshots/{product-slug}-snapshot-YYYY-MM-DD.json`:

```json
{
  "date": "YYYY-MM-DD",
  "mode": "single_audit",
  "product": {
    "name": "{product name}",
    "asin": "{ASIN}",
    "category": "{category}",
    "niche_id": "{DataDive niche ID}"
  },
  "ranking_juice": {
    "our_title_score": 0,
    "our_bullets_score": 0,
    "our_description_score": 0,
    "our_overall_score": 0,
    "niche_avg_title": 0,
    "niche_avg_bullets": 0,
    "niche_avg_description": 0,
    "niche_avg_overall": 0,
    "niche_max_overall": 0,
    "top_5_competitors": [
      {
        "asin": "",
        "title_score": 0,
        "bullets_score": 0,
        "description_score": 0,
        "overall_score": 0
      }
    ]
  },
  "keyword_analysis": {
    "total_core_keywords": 0,
    "core_keywords_ranked_top10": 0,
    "core_keywords_not_ranked": 0,
    "keywords_rank_11_to_20": 0,
    "keywords_declining_7d": 0,
    "keywords_improving_7d": 0,
    "keywords_declining_30d": 0,
    "top_gaps": [
      {
        "keyword": "",
        "search_volume": 0,
        "our_rank": null,
        "best_competitor_rank": 0,
        "in_our_listing": false
      }
    ]
  },
  "root_analysis": {
    "total_high_volume_roots": 0,
    "roots_in_our_listing": 0,
    "roots_missing": 0,
    "missing_roots": [
      {
        "root": "",
        "broad_search_volume": 0,
        "frequency": 0
      }
    ]
  },
  "performance": {
    "cvr": 0.0,
    "sessions": 0,
    "organic_sales": 0.0,
    "ppc_sales": 0.0,
    "revenue": 0.0,
    "profit": 0.0
  },
  "rank_radar": {
    "total_keywords_tracked": 0,
    "top_10_count": 0,
    "top_50_count": 0,
    "declining_7d": [],
    "almost_page_1": []
  },
  "priority_score": 0.0
}
```

**Portfolio Scan Snapshot** — save to `outputs/research/listing-optimizer/snapshots/portfolio-snapshot-YYYY-MM-DD.json`:

```json
{
  "date": "YYYY-MM-DD",
  "mode": "portfolio_scan",
  "products": {
    "{ASIN}": {
      "name": "",
      "category": "",
      "ranking_juice_overall": 0,
      "niche_avg_overall": 0,
      "score_delta": 0,
      "cvr": 0.0,
      "revenue": 0.0,
      "priority_score": 0.0,
      "top10_keywords": 0,
      "top50_keywords": 0,
      "quick_wins": []
    }
  },
  "portfolio_averages": {
    "avg_ranking_juice": 0,
    "avg_cvr": 0.0,
    "total_revenue": 0.0,
    "products_below_avg_score": 0,
    "products_below_avg_cvr": 0
  }
}
```

### Step 13: Generate Report

Output the full analysis as a structured markdown report following the exact Output Format below.

**Single Audit:** Save to `outputs/research/listing-optimizer/briefs/{product-slug}-listing-audit-YYYY-MM-DD.md`
**AI Copywriter output:** Save separately to `outputs/research/listing-optimizer/rewrites/YYYY-MM-DD/{product-slug}-rewrites-YYYY-MM-DD.md`
**Portfolio Scan:** Save to `outputs/research/listing-optimizer/briefs/portfolio-scan-YYYY-MM-DD.md`

### Step 14: Present Summary to User

After saving, present a concise summary:
- Mode run (Single Audit / Portfolio Scan)
- Product(s) analyzed
- Overall optimization health (1 sentence)
- Top 3 most impactful findings
- File location(s)
- Trend note (if previous snapshot existed)
- Recommended next action

---

## Output Format

### Single Product Audit Report Template

```markdown
# Listing Audit: {Product Name} ({ASIN})

**Date:** {YYYY-MM-DD}
**Category:** {Amazon category}
**DataDive Niche:** {niche label}
**Previous Snapshot:** {YYYY-MM-DD} (or "None — first run")
**Data Sources:** DataDive (Ranking Juice, MKL, Roots, Rank Radar), Amazon SP-API (listing copy, sessions/CVR), Seller Board (profit, PPC split), Apify (competitor listings)

---

## Executive Summary

{3-4 sentences: Overall listing health, biggest weakness, most urgent fix, expected impact of fixing it. Be specific — name exact keywords and scores.}

**Listing Health:** {STRONG / GOOD / NEEDS WORK / WEAK / CRITICAL}
**Biggest Gap:** {1 sentence — the single most impactful thing wrong with the listing}
**Quick Win:** {1 sentence — the easiest fix with highest impact}
**Estimated Impact:** {If fixed, estimate rank improvement and revenue impact}

---

## Optimization Scorecard

### Ranking Juice — Our Listing vs Niche

| Dimension | Our Score | Niche Avg | Niche Max | Delta vs Avg | Delta vs Max | Status |
|-----------|----------|-----------|-----------|-------------|-------------|--------|
| **Title** | {X}/100 | {X}/100 | {X}/100 | {+/- X} | {-X} | {Above Avg / Below Avg / Well Below} |
| **Bullets** | {X}/100 | {X}/100 | {X}/100 | {+/- X} | {-X} | {status} |
| **Description** | {X}/100 | {X}/100 | {X}/100 | {+/- X} | {-X} | {status} |
| **Overall** | {X}/100 | {X}/100 | {X}/100 | {+/- X} | {-X} | {status} |

### Ranking Juice — vs Top 5 Competitors

| # | Brand | ASIN | Title | Bullets | Description | Overall | vs Us |
|---|-------|------|-------|---------|-------------|---------|-------|
| 1 | {brand} | {ASIN} | {X} | {X} | {X} | {X} | {+/- X} |
| 2 | {brand} | {ASIN} | {X} | {X} | {X} | {X} | {+/- X} |
| 3 | {brand} | {ASIN} | {X} | {X} | {X} | {X} | {+/- X} |
| 4 | {brand} | {ASIN} | {X} | {X} | {X} | {X} | {+/- X} |
| 5 | {brand} | {ASIN} | {X} | {X} | {X} | {X} | {+/- X} |
| **Us** | **Craftiloo** | **{ASIN}** | **{X}** | **{X}** | **{X}** | **{X}** | — |

**Our Rank in Niche:** #{X} of {Y} products (by overall score)

### Trend (vs Previous Snapshot)

> Only include if previous snapshot exists. If first run: "First audit — no previous data. This snapshot establishes the baseline."

| Dimension | Current | Previous ({date}) | Change | Direction |
|-----------|---------|-------------------|--------|-----------|
| Title Score | {X} | {X} | {+/- X} | {Improving / Stable / Declining} |
| Bullets Score | {X} | {X} | {+/- X} | {direction} |
| Description Score | {X} | {X} | {+/- X} | {direction} |
| Overall Score | {X} | {X} | {+/- X} | {direction} |

---

## Keyword Gap Analysis

### Summary

| Metric | Count | Impact |
|--------|-------|--------|
| Total Core Keywords in Niche | {X} | — |
| Core Keywords We Rank Top 10 | {X} ({X%}) | We own these |
| Core Keywords We Rank 11-20 | {X} | **Quick wins — almost page 1** |
| Core Keywords We Do NOT Rank | {X} ({X%}) | **Gaps to close** |
| Related Keywords Not Ranked | {X} | Secondary opportunities |

### Quick Wins — Keywords Ranked 11-20 (Almost Page 1)

Sorted by search volume (highest impact first).

| # | Keyword | Search Vol | Our Rank | Best Competitor | In Our Title? | In Our Bullets? | 7d Trend | Action |
|---|---------|-----------|----------|----------------|---------------|----------------|----------|--------|
| 1 | {keyword} | {sv} | #{X} | {brand} #{X} | {Yes/No} | {Yes/No} | {trend} | {Add to title / Add to bullet X / Optimize placement} |

### Keyword Gaps — Competitors Rank, We Do Not

Keywords where at least 2 of our top 5 competitors rank top 10, but we do not.

| # | Keyword | Search Vol | Relevancy | Comp 1 Rank | Comp 2 Rank | Comp 3 Rank | In Our Listing? | Action |
|---|---------|-----------|-----------|-------------|-------------|-------------|----------------|--------|
| 1 | {keyword} | {sv} | {Core/Related} | #{X} | #{X} | #{X} | {Yes/No} | {action} |

### Our Keyword Strengths — Keywords We Own

Keywords where we rank top 5 and competitors do not. **Do NOT remove these from the listing.**

| # | Keyword | Search Vol | Our Rank | Best Competitor | Notes |
|---|---------|-----------|----------|----------------|-------|
| 1 | {keyword} | {sv} | #{X} | #{X} ({brand}) | Protect — do not change |

---

## Root Word Coverage Analysis

### Root Coverage Summary

| Metric | Value |
|--------|-------|
| Total High-Volume Roots (>1000 SV) | {X} |
| Roots Present in Our Listing | {X} ({X%}) |
| Roots Missing from Our Listing | {X} ({X%}) |

### Missing Roots (Sorted by Search Volume Impact)

| # | Root Word | Broad Search Vol | Frequency in Keywords | In Competitor Titles? | Priority |
|---|-----------|-----------------|----------------------|-----------------------|----------|
| 1 | {root} | {sv} | {X} keywords | {X/5 competitors} | {HIGH / MEDIUM / LOW} |

### Root Coverage vs Top 3 Competitors

| Root Word | Our Listing | {Comp 1} | {Comp 2} | {Comp 3} | Gap? |
|-----------|------------|----------|----------|----------|------|
| {root} | {Present/Missing} | {P/M} | {P/M} | {P/M} | {We're missing / We all have / Only us} |

---

## Rank Trend Analysis (30-Day)

### Keywords Declining in Rank (Action Needed)

| # | Keyword | Search Vol | Rank 30d Ago | Rank 7d Ago | Rank Now | 30d Change | In Listing? | Correlation |
|---|---------|-----------|-------------|-------------|----------|-----------|-------------|-------------|
| 1 | {keyword} | {sv} | #{X} | #{X} | #{X} | {-X positions} | {Yes/No} | {Missing from listing / Root gap / Competitor improved} |

### Keywords Improving (Protect These)

| # | Keyword | Search Vol | Rank 30d Ago | Rank Now | 30d Change |
|---|---------|-----------|-------------|----------|-----------|
| 1 | {keyword} | {sv} | #{X} | #{X} | {+X positions} |

### Rank Movement Summary

| Metric | Value |
|--------|-------|
| Total Keywords Tracked | {X} |
| Improving (7d) | {X} ({X%}) |
| Stable (7d) | {X} ({X%}) |
| Declining (7d) | {X} ({X%}) |
| Improving (30d) | {X} ({X%}) |
| Declining (30d) | {X} ({X%}) |

---

## Conversion & Sales Context

> If Seller Board data unavailable: "Seller Board data unavailable — conversion context skipped."

| Metric | Our Product | Portfolio Avg | Status |
|--------|------------|--------------|--------|
| CVR (Unit Session %) | {X%} | {X%} | {Above Avg / Below Avg / Well Below} |
| Sessions (last 7d) | {X} | {X} | — |
| Organic Sales (last 7d) | ${X} | ${X} | — |
| PPC Sales (last 7d) | ${X} | ${X} | — |
| PPC Dependency | {X%} of sales from PPC | — | {Healthy / PPC Dependent / Over-Reliant} |
| Net Profit (last 7d) | ${X} | — | — |
| Margin | {X%} | — | — |

**Conversion Assessment:**
{2-3 sentences: Is the listing converting well? Is low CVR correlated with poor Ranking Juice scores? Is high PPC dependency indicating weak organic listing quality?}

---

## Correlation Map — Listing Weakness x Rank Decline

**Core insight:** Where listing weaknesses are CAUSING rank losses.

| # | Listing Weakness | Keyword(s) Affected | Search Vol | Rank Change (30d) | Est. Revenue at Risk | Priority |
|---|-----------------|---------------------|-----------|-------------------|---------------------|----------|
| 1 | {Missing root/keyword from title} | {keyword1}, {keyword2} | {combined SV} | {-X positions avg} | ~${X}/month | **P1** |
| 2 | {Low bullet score — missing {topic}} | {keyword3} | {SV} | {-X positions} | ~${X}/month | **P1** |
| 3 | {Description gap} | {keyword4}, {keyword5} | {combined SV} | {-X positions avg} | ~${X}/month | **P2** |

---

## Rewrite Recommendations

### Title

**Current Title:**
> {exact current title}

**Character Count:** {X} / 200 | **Primary Keyword Position:** word #{X}

**Issues Found:**
- {Missing high-volume keyword: "{keyword}" (SV: {X})}
- {Primary keyword not front-loaded}
- {Character count underutilized — {X} chars remaining}

**Recommended Title Option A:**
> {rewritten title with gaps filled}

**Recommended Title Option B:**
> {alternative rewrite}

**AI Copywriter Titles:**

| Mode | Suggested Title |
|------|----------------|
| COSMO | {title} |
| Ranking Juice | {title} |
| NLP | {title} |
| COSMO-Rufus | {title} |

### Bullets

#### Bullet {X}

**Current:**
> {exact current bullet text}

**Issues:**
- {Missing root word: "{root}" (broadSV: {X})}
- {Keyword opportunity: "{keyword}" not present}

**Recommended Rewrite:**
> {specific rewritten bullet}

**AI Copywriter Alternatives:**

| Mode | Suggested Bullet {X} |
|------|---------------------|
| COSMO | {bullet} |
| Ranking Juice | {bullet} |
| NLP | {bullet} |
| COSMO-Rufus | {bullet} |

[Repeat for each of 5 bullets]

### Description

**Current Assessment:**
- Description score: {X}/100 (niche avg: {X})
- {Issues found}

**Recommended Changes:**
- {Specific additions/rewrites}

### Backend Keywords

**Keywords to ADD to backend (not in title or bullets):**

| # | Keyword | Search Volume | Why |
|---|---------|-------------|-----|
| 1 | {keyword} | {sv} | {High relevance, not in any listing field} |

---

## Consolidated Action List

### P1 — Fix Now (Highest Revenue Impact)

| # | Action | Affected Keywords | Combined SV | Est. Revenue Impact | Effort |
|---|--------|-------------------|-----------|---------------------|--------|
| 1 | {Specific: "Add '{keyword}' to title position 2"} | {keywords} | {SV} | ~${X}/month | {Easy / Medium / Hard} |

### P2 — Fix Soon

| # | Action | Rationale | Effort |
|---|--------|-----------|--------|
| 1 | {action} | {rationale} | {effort} |

### P3 — Monitor / Test

| # | Action | Rationale |
|---|--------|-----------|
| 1 | {action} | {rationale} |

### Do NOT Change (Protected)

- **{Keyword/element}:** Ranks well, driving organic traffic — do not alter
- **{Keyword/element}:** {reason to protect}

---

## Data Notes

- **DataDive Niche:** {niche label} ({niche ID})
- **Ranking Juice ASINs scored:** {X} products
- **Master Keyword List:** {X} Core + {X} Related keywords analyzed
- **Keyword Roots:** {X} roots analyzed
- **Rank Radar:** {X} keywords tracked, 30-day window
- **Amazon SP-API:** Our listing copy via Merchant Listings report; Sessions/CVR via Sales & Traffic report
- **Seller Board:** Profit/PPC split data through {date}
- **Apify:** {X} competitor ASINs scraped for listing copy
- **AI Copywriter:** {X} modes run ({mode list})
- **Snapshot saved:** {filepath}
```

### Portfolio Scan Report Template

```markdown
# Portfolio Listing Scan — {YYYY-MM-DD}

**Products Scanned:** {X} hero products across {Y} categories
**Previous Scan:** {YYYY-MM-DD} (or "None — first run")
**Data Sources:** DataDive (Ranking Juice, Rank Radar summaries), Amazon SP-API (listing copy, sessions/CVR), Seller Board (profit, PPC split)

---

## Executive Summary

{2-3 sentences: Overall portfolio listing health, how many products need attention, which product to fix first and why.}

**Products Strong:** {X} | **Adequate:** {X} | **Weak:** {X} | **Critical:** {X}

---

## Priority Matrix — Which Listing to Fix First

Sorted by Priority Score = (Niche Avg Score - Our Score) x Monthly Revenue.

| Priority | Product | ASIN | Category | Our Score | Niche Avg | Gap | Monthly Revenue | CVR | Priority Score | Status |
|----------|---------|------|----------|----------|-----------|-----|-----------------|-----|----------------|--------|
| 1 | {name} | {ASIN} | {category} | {X}/100 | {X}/100 | {-X} | ${X} | {X%} | {score} | {status} |

**Status thresholds:**
- **CRITICAL:** Score > 15 points below niche avg AND CVR below portfolio avg
- **WEAK:** Score > 10 points below niche avg OR CVR significantly below portfolio avg
- **NEEDS WORK:** Score 5-10 points below niche avg
- **GOOD:** Score within 5 points of niche avg
- **STRONG:** Score above niche avg

---

## Per-Product Summary

### {Product Name} ({ASIN}) — {Status}

| Dimension | Our Score | Niche Avg | Delta | Status |
|-----------|----------|-----------|-------|--------|
| Title | {X} | {X} | {+/- X} | {status} |
| Bullets | {X} | {X} | {+/- X} | {status} |
| Description | {X} | {X} | {+/- X} | {status} |
| Overall | {X} | {X} | {+/- X} | {status} |

**Rank Radar:** {X} keywords top 10 | {X} keywords top 50 | {X} declining
**CVR:** {X%} (portfolio avg: {X%})
**Revenue:** ${X}/month

**Top 3 Quick Wins:**
1. {Specific, actionable recommendation}
2. {Specific, actionable recommendation}
3. {Specific, actionable recommendation}

**Recommended:** {Run Single Audit / No action needed / Minor tweaks only}

---

[Repeat for each hero product, sorted by Priority Score descending]

---

## Portfolio Health Overview

### Optimization Score Distribution

| Range | Count | Products |
|-------|-------|----------|
| 80-100 (Excellent) | {X} | {names} |
| 60-79 (Good) | {X} | {names} |
| 40-59 (Needs Work) | {X} | {names} |
| < 40 (Critical) | {X} | {names} |

### Category Comparison

| Category | Avg Craftiloo Score | Avg Niche Score | Craftiloo vs Niche | Best Competitor Score |
|----------|--------------------|-----------------|--------------------|----------------------|
| {category} | {X} | {X} | {+/- X} | {X} ({brand}) |

### Trend (vs Previous Scan)

> Only include if previous portfolio snapshot exists.

| Product | Current Score | Previous Score | Change | Direction |
|---------|-------------|----------------|--------|-----------|
| {name} | {X} | {X} | {+/- X} | {direction} |

---

## Consolidated Recommendations

### Immediate Actions (Top 5 — This Week)

| # | Product | Action | Expected Impact |
|---|---------|--------|----------------|
| 1 | {name} | {specific action} | {impact} |

### Run Single Audit On (Deep Dives Needed)

| # | Product | Why | Priority |
|---|---------|-----|----------|
| 1 | {name} | {reason} | {HIGH / MEDIUM} |

### Products in Good Shape (No Action Needed)

- **{Product}** — Score above niche avg, CVR healthy, ranks stable

---

## Data Notes

- **DataDive Niches Queried:** {X} niches ({niche labels})
- **Ranking Juice ASINs scored:** {X} per niche avg
- **Rank Radar summaries:** {X} radars checked
- **Amazon SP-API:** Listing copy for all products; Sessions/CVR via Sales & Traffic report
- **Seller Board:** Profit/PPC split data through {date}
- **Snapshot saved:** {filepath}
```

---

## Output Location

| Output | Location |
|--------|----------|
| **Single Audit report** | `outputs/research/listing-optimizer/briefs/{product-slug}-listing-audit-YYYY-MM-DD.md` |
| **Portfolio Scan report** | `outputs/research/listing-optimizer/briefs/portfolio-scan-YYYY-MM-DD.md` |
| **AI Copywriter rewrites** | `outputs/research/listing-optimizer/rewrites/YYYY-MM-DD/{product-slug}-rewrites-YYYY-MM-DD.md` |
| **Single Audit snapshot** | `outputs/research/listing-optimizer/snapshots/{product-slug}-snapshot-YYYY-MM-DD.json` |
| **Portfolio Scan snapshot** | `outputs/research/listing-optimizer/snapshots/portfolio-snapshot-YYYY-MM-DD.json` |

---

## Token Budget Strategy

### Single Product Audit

| Component | Estimated Tokens | Priority |
|-----------|-----------------|----------|
| Context file loading (5 files) | ~12K | Required |
| DataDive Ranking Juice (1 niche) | ~5K | Required |
| DataDive MKL (1 niche, 200 keywords) | ~15K | Required |
| DataDive Roots (1 niche) | ~3K | Required |
| DataDive Rank Radar (1 radar, 30 days) | ~10K | Required |
| Amazon SP-API Sales & Traffic report | ~5K | Required |
| Amazon SP-API Merchant Listings report (our copy) | ~3K | Required |
| Seller Board Sales Detailed (profit/PPC split) | ~4K | Required |
| Apify competitor listing scrape (5 ASINs) | ~7K | Required |
| AI Copywriter (4 modes) | ~10K | Required |
| Analysis + correlation | ~5K | Required |
| Report generation | ~7K | Required |
| **Total estimated** | **~86K** | — |

**If approaching token limit:**
1. Reduce MKL to Core keywords only (skip Related) — saves ~5K
2. Reduce Rank Radar window from 30 days to 7 days — saves ~4K
3. Run only 2 AI Copywriter modes (cosmo + cosmo-rufus) instead of 4 — saves ~5K
4. Skip SP-API Sales & Traffic if Seller Board already loaded — saves ~3K
5. Never cut: Ranking Juice scores, keyword gaps, correlation map, SP-API listing copy, title rewrite recommendations

### Portfolio Scan

| Component | Estimated Tokens | Priority |
|-----------|-----------------|----------|
| Context file loading (5 files) | ~12K | Required |
| DataDive Ranking Juice (up to 8 niches) | ~20K | Required |
| DataDive Rank Radar summaries (list only) | ~3K | Required |
| Amazon SP-API Sales & Traffic report | ~5K | Required |
| Amazon SP-API Merchant Listings report (all products) | ~5K | Required |
| Seller Board Sales Detailed (profit/PPC split) | ~4K | Required |
| Analysis + prioritization | ~8K | Required |
| Report generation (13 products) | ~12K | Required |
| **Total estimated** | **~69K** | — |

**If approaching token limit:**
1. Reduce per-product analysis from full summary to table-only — saves ~5K
2. Show top 3 quick wins only for CRITICAL and WEAK products — saves ~3K

---

## Execution Checklist

### Setup & Context Loading
- [ ] Mode confirmed (Single Audit or Portfolio Scan)
- [ ] Product identified (Single Audit) or all 13 hero products loaded (Portfolio Scan)
- [ ] All 5 context files loaded
- [ ] Each hero product matched to its DataDive niche ID
- [ ] Previous snapshot checked (loaded or noted as first run)
- [ ] Estimated cost confirmed with user

### Data Fetching
- [ ] DataDive Ranking Juice fetched for relevant niches — or failure noted
- [ ] DataDive Master Keyword List fetched (Single Audit) — or failure noted
- [ ] DataDive Keyword Roots fetched (Single Audit) — or failure noted
- [ ] DataDive Rank Radar data fetched (30-day for Single Audit, summaries for Portfolio Scan) — or failure noted
- [ ] Amazon SP-API Sales & Traffic report fetched (sessions, CVR) — or fell back to Seller Board
- [ ] Amazon SP-API Merchant Listings report fetched (our listing copy) — or fell back to Apify
- [ ] Seller Board Sales Detailed fetched (profit, PPC split) — or failure noted
- [ ] Apify competitor listing scrape completed (Single Audit only, 5 ASINs) — or failure noted
- [ ] AI Copywriter run in all 4 modes (Single Audit only) — or failure noted

### Analysis
- [ ] Ranking Juice scores compared: our product vs niche avg vs top 5 competitors
- [ ] Keyword gaps identified: Core keywords we do not rank for that competitors do
- [ ] Quick wins identified: Keywords ranked 11-20 with high search volume
- [ ] Root word coverage analyzed: missing roots flagged by broadSearchVolume
- [ ] Rank trends analyzed: 7-day and 30-day direction per keyword
- [ ] CVR and revenue context applied from Seller Board
- [ ] Correlation map built: listing weaknesses mapped to rank declines
- [ ] Priority score calculated for each product (Portfolio Scan)

### Rewrite Recommendations (Single Audit Only)
- [ ] Title rewrite includes missing high-volume keywords
- [ ] Title options include front-loaded primary keyword
- [ ] Each bullet has specific rewrite with root/keyword additions noted
- [ ] AI Copywriter outputs compared against current listing
- [ ] Backend keyword additions identified
- [ ] "Protected" keywords/elements flagged (do NOT change)

### Output & Housekeeping
- [ ] Report follows exact output template
- [ ] Report saved to correct output location
- [ ] Snapshot JSON saved with all metrics
- [ ] AI Copywriter output saved separately (Single Audit)
- [ ] Summary presented to user
- [ ] Token usage within budget

---

## Error Handling

| Issue | Response |
|-------|----------|
| User does not specify mode | Ask: "Single Product Audit or Portfolio Scan?" with brief explanation of each |
| Product ASIN not in hero-products.md | List the 13 hero products and ask user to select one or add the ASIN to `context/hero-products.md` first |
| No matching DataDive niche for a product | Skip DataDive analysis for that product. Note: "No DataDive niche found for {product}." Continue with Seller Board data. |
| DataDive Ranking Juice API fails | Note: "Ranking Juice data unavailable." Proceed with keyword gap and rank trend analysis only. |
| DataDive MKL API fails | Note: "Master Keyword List unavailable — keyword gap analysis skipped." Proceed with Ranking Juice scores and rank data. |
| DataDive Rank Radar API fails | Note: "Rank Radar data unavailable — trend analysis skipped." Proceed with static optimization scores. |
| DataDive AI Copywriter fails (1+ modes) | Note which modes failed. Proceed with successful modes. If all fail, provide manual rewrite recommendations only. |
| Amazon SP-API Sales & Traffic report fails or times out | Fall back to Seller Board for CVR/sessions data. Note: "SP-API Sales & Traffic unavailable — using Seller Board CVR data." |
| Amazon SP-API Merchant Listings report fails or times out | Add our ASIN to the Apify batch in Step 8b. Note: "SP-API listing data unavailable — scraping our listing via Apify." |
| Amazon SP-API auth token expired | Note: "SP-API authentication failed." Fall through to Seller Board + Apify. Check `SP_API_REFRESH_TOKEN` in `.env`. |
| Amazon SP-API report stuck `IN_PROGRESS` beyond 5 polls | Stop polling. Fall back to Seller Board (for sales) and Apify (for listing copy). Note the timeout. |
| Seller Board report fails | Note: "Seller Board data unavailable — profit/PPC split unavailable." CVR still available from SP-API. Prioritize by optimization scores + SP-API revenue. |
| Both SP-API and Seller Board fail for sales data | Note: "All sales data sources unavailable — CVR and revenue context skipped." Prioritize by optimization scores only. |
| Apify competitor scrape fails (Single Audit) | Note: "Competitor listing copy unavailable." Our listing analysis continues using SP-API data. Rewrite recs will be keyword-focused rather than copy-comparison. |
| Apify timeout (>3 minutes) | Use whatever data was collected. Note which competitor ASINs are missing. |
| Previous snapshot JSON is corrupted | Skip trend comparison. Note: "Previous snapshot unreadable — treating as first run." |
| Token budget tight (approaching 80K) | Priority cuts: 1) Reduce MKL to Core only, 2) Reduce Rank Radar window, 3) Cut AI Copywriter to 2 modes. Never cut: Ranking Juice, keyword gaps, correlation map. |
| Product has no Rank Radar | Skip rank trend analysis. Note: "No Rank Radar found for {ASIN}." |
| Niche has very few competitors (<3) | Note: "Small niche — averages may not be meaningful." Still show scores but flag small sample. |
| Two hero products share same niche | Fetch Ranking Juice once. Show both products' scores from the same niche data. |
| User asks to audit a competitor listing | Refuse: "This skill audits Craftiloo listings only. Use Niche Category Analysis or Customer Review Analyzer for competitor analysis." |

---

## Integration with Other Skills

### Feeds INTO

| This skill provides... | To... | How |
|------------------------|-------|-----|
| Keyword gaps + rewrite recs | **Listing Creator** | Re-run listing creator with gap analysis as input |
| Missing customer language | **Customer Review Analyzer** | Run review analysis to get exact phrases for rewrites |
| Low CVR listings identified | **Weekly PPC Analysis** | Flag listings where high spend + low CVR = listing problem |
| Declining rank keywords | **Daily Market Intel** | Track whether rewrite improved rank |

### Receives FROM

| This skill needs... | From... | How |
|---------------------|---------|-----|
| Review language/vocabulary | **Customer Review Analyzer** | Use praise themes as rewrite inspiration |
| Search term performance | **Weekly PPC Analysis** | High-converting search terms should be in listing |
| Competitor movements | **Daily Market Intel** | New competitor listing quality changes |

### Recommended Workflow Sequences

| Scenario | Sequence |
|----------|----------|
| **Monthly listing health check** | 1. Portfolio Scan → 2. Single Audit on top 2-3 flagged products → 3. Implement rewrites → 4. Track with Daily Market Intel |
| **Listing not converting** | 1. Single Audit → 2. Customer Review Analyzer (customer language) → 3. Rewrite → 4. Monitor CVR in Weekly PPC |
| **Rank dropping on key keywords** | 1. Single Audit → 2. Implement P1 rewrites → 3. Track rank recovery via Daily Market Intel |
| **Post-listing-creator quality check** | 1. Run Listing Creator → 2. Single Audit after 2 weeks live → 3. Refine based on actual rank + CVR data |

---

## ⚠️ AFTER EVERY RUN — Update Lessons (MANDATORY)

**Before presenting final results, update `.claude/skills/listing-optimizer/LESSONS.md`.**

### 1. Write a Run Log Entry

Add a new entry at the **TOP** of the Run Log section:

```
### Run: YYYY-MM-DD
**Goals:**
- [ ] Goal 1
- [ ] Goal 2

**Result:** ✅ Success / ⚠️ Partial / ❌ Failed

**What happened:**
- (What went according to plan)

**What didn't work:**
- (Any issues, with specifics)

**Is this a repeat error?** Yes/No — if yes, which one?

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

End your output with a **Lessons Update** note:
- What you logged
- Any repeat errors encountered
- Suggestions for skill improvement

**Do NOT skip this. The system only improves if every run is logged honestly.**

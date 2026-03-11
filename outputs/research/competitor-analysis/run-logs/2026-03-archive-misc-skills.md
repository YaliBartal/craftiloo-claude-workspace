# Other Skills — Run Log Archive (Feb-March 2026)

> Extracted from LESSONS.md files for niche-category-analysis, customer-review-analyzer, competitor-price-serp-tracker, and mcp-builder skills. Run entries only — Known Issues, Repeat Errors, and Resolved Issues remain in the original files.

---

## Niche Category Analysis

### Run: 2026-02-26
**Goals:**
- [x] Niche analysis for new Barbie/fashion-doll loom knitting kit for kids
- [x] Assess DataDive loom knitting niche (O6b4XATpTj)
- [x] Pull internal Seller Board data for our 3 existing knitting kits
- [x] Competitor pricing via SP-API
- [x] Keyword + roots + ranking juice from DataDive
- [x] Review scraping for top 2 competitors (Hapinest, CFK)

**Result:** Success — full brief generated with CONDITIONAL GO verdict (32/40)

**Data sources used:** DataDive | SP-API | Seller Board | Apify (partial — 8 reviews/ASIN)

**What happened:**
- Found existing "loom knitting" niche in DataDive (O6b4XATpTj) — no token spend needed
- Niche has only 4 competitors tracked: Hapinest, CFK, and 2x CRAFTILOO
- CRAFTILOO holds 41% of measurable niche revenue — already #2 and #3 by revenue
- SP-API revealed significant price gap: Hapinest $16.49 vs our $22.98-$26.98 — major driver of their volume lead
- All 4 competitors score 0 on description (listing gap opportunity)
- Barbie IP warning is critical — cannot use "Barbie" trademark without Mattel license
- Ran all DataDive pulls in parallel (competitors, keywords, ranking juice) — worked well
- Review scraper returned only 8 reviews/ASIN (page-1 cap confirmed again)

**What didn't work:**
- Review scraper page-1 cap hit again — only 8 reviews per ASIN instead of 50
- User never sent competitor list (they referenced it but didn't paste it) — proceeded with DataDive 4-competitor set
- DataDive niche was last researched Jan 7, 2026 — data is 7 weeks old, not current

**Is this a repeat error?** Yes — review scraper 8-review cap is a Known Issue (KI from Feb 23 run... actually this was tracked in customer-review-analyzer LESSONS.md). First time for niche-category-analysis LESSONS.

**Lesson learned:**
- For small niches (4 competitors), DataDive provides a complete picture — no need for SP-API catalog search to find competitors
- When user references a list they didn't send, proceed with what DataDive shows and note the gap in the report
- Run DataDive competitors + keywords + ranking juice all in parallel at the start — saves significant time
- Seller Board data is valuable for internal baseline even when not "already in the niche" technically
- Always flag IP/trademark issues prominently when a product concept uses a brand name (Barbie, Disney, etc.)
- For doll-themed products: the "sizing complaint" (hat too small) becomes a feature for doll accessories — use this insight in positioning

**Tokens/cost:** ~80K tokens, $0 MCP costs, ~$0.02 Apify (3 runs, free tier)

---

### Run: 2026-02-23
**Goals:**
- [x] Run MCP-powered analysis on "quilt kit for kids" niche
- [x] Compare new DataDive/SP-API data with Feb 22 Apify/BSR analysis
- [x] Set up proper output folder structure

**Result:** Partial — niche dive creation failed, used existing overlapping niche instead

**Data sources used:** DataDive | SP-API | Seller Board (none) | Apify (none — reused Feb 22 review data)

**What happened:**
- Successfully pulled DataDive competitor data from "sewing kit for kids new" niche (RmbSD3OH6t) — 10 competitors with Jungle Scout actuals
- Successfully pulled 309 keywords with real search volumes + 305 keyword roots
- Successfully pulled Ranking Juice scores for all 10 competitors
- Successfully pulled SP-API real-time competitive pricing for 10 ASINs
- Comparison revealed BSR tables underestimated market by 2.7x ($105K -> $285K)
- Craftiloo underestimated by 6.7x ($4.4K -> $29.3K/mo)
- Quilt-specific keywords confirmed as negligible (~250/mo) — key strategic insight
- Updated folder structure with README showing historical runs

**What didn't work:**
- `create_niche_dive` returned HTTP 400 for both seed ASINs (B072JH19F8, B09CR5RX65)
- `get_profile` returned 404 — couldn't verify token balance
- Used existing "sewing kit for kids" niche as workaround — good overlap but quilt-specific products (M&D, Made By Me) not in DataDive competitor set
- Keyword file was too large (138K chars, 70K tokens) — had to use subagent to extract
- Roots file was also too large (234K chars) — same workaround

**Is this a repeat error?** No — first run with MCP data.

**Lesson learned:**
- `create_niche_dive` may have account/plan limitations — investigate with DataDive support
- Always check `list_niches` first — existing niches are free and often overlap with target niche
- DataDive keyword/roots responses can be VERY large — use subagents or pagination to handle
- BSR estimation tables are unreliable for mid-tier products (off by 3-7x) — always prefer Jungle Scout actuals
- For "quilt kit for kids" specifically: the keyword data proves this is NOT a separate niche — it's a sub-feature of "sewing kit for kids"
- SP-API pricing is essential for real-time data — DataDive prices can be stale (CRAFTILOO showed $17.98 in DataDive vs $21.98 in SP-API)

**Tokens/cost:** ~60K tokens, $0 Apify cost (reused old review data), $0 MCP costs

---

### Run: 2026-02-22
**Goals:**
- [x] First analysis of "quilt kit for kids" niche
- [x] Identify competitors, pricing, keywords, review themes

**Result:** Success (Apify + BSR method)

**Data sources used:** DataDive (none) | SP-API (none) | Seller Board (none) | Apify

**What happened:**
- Scraped search results, product details, and reviews via Apify
- Identified 15 competitors, analyzed pricing, keywords from titles, reviews from top 5
- Produced CONDITIONAL GO verdict (26/35)
- Key finding: Amazon blends quilt kits and sewing kits in search results

**What didn't work:**
- BSR-to-sales estimation was significantly off (discovered in Feb 23 run)
- Keywords were guessed from title frequency, not actual search volumes
- No listing optimization data

**Lesson learned:**
- BSR tables are directional but should not be trusted for absolute numbers
- Review analysis (Apify) is still the best method for customer voice — MCP services don't replace this
- Apify cost was ~$0.15 — reasonable for review scraping

**Tokens/cost:** ~40K tokens, ~$0.15 Apify

---

## Customer Review Analyzer

### Run: 2026-02-26
**Goals:**
- [x] Scrape 50 reviews each for B0B8W4FK4Q (Hapinest) and B004JIFCXO (Creativity for Kids) — loom knitting kit niche
- [ ] 50 reviews per ASIN (target not met — only 8 per ASIN returned)

**Result:** Partial — scrape succeeded but capped at 8 reviews per ASIN, not 50

**What happened:**
- `junglee/amazon-reviews-scraper` ran successfully (SUCCEEDED, 97.2% rate, free tier)
- Actor returned only 8 reviews per ASIN regardless of `maxReviews: 50` setting
- `totalCategoryReviews: 1` per item confirms actor stops at 1 page (Amazon serves ~8 per page)
- Tried residential proxy — same result: 8 reviews per ASIN
- Tried `epctex/amazon-reviews-scraper` — BLOCKED: requires paid rental after free trial
- Tried `web_wanderer/amazon-reviews-extractor` — returned 0 items (possible auth issue)
- `axesso_data/amazon-reviews-scraper` — same 8 reviews, `maxPages: 5` parameter ignored, stops at page 1
- Total: 16 reviews collected (8 per ASIN), raw data saved to `data/2026-02-26/`
- Product-level rating summaries obtained: Hapinest 4.5/5 (426 ratings), CFK 4.6/5 (3336 ratings)

**What didn't work:**
- `junglee` actor ignores `maxReviews > ~8`: it only scrapes 1 page per product regardless of the setting
- `axesso_data` actor's `maxPages` parameter appears non-functional — only returns page 1
- `epctex` actor requires paid rental — cannot use without subscribing
- `web_wanderer` actor returned 0 results on first attempt (possible anti-bot block or auth requirement)

**Is this a repeat error?** No — first run

**Lesson learned:**
- `junglee/amazon-reviews-scraper` is capped at ~8 reviews per run (1 page). Do NOT rely on it for 50+ reviews. It is useful for a quick spot-check of the most recent reviews only.
- `axesso_data` similarly only returns page 1 despite `maxPages` parameter.
- For 50 reviews, the best available free approach is to run `junglee` with explicit page URL strings: `https://www.amazon.com/product-reviews/{ASIN}?pageNumber=2&sortBy=recent` etc., up to 6 sequential runs per ASIN.
- Alternative: `web_wanderer/amazon-reviews-extractor` — retry with full product review URL format rather than just ASIN. It claims up to 500 reviews in `all_stars` mode.
- Best paid option if budget allows: `axesso_data` at $0.00075/review (50 reviews x 2 ASINs = $0.075 total) — very cheap, 100% success rate.

**Tokens/cost:** ~15K tokens, Apify cost ~$0.01 (6 actor runs, very low compute each)

---

## Competitor Price & SERP Tracker

### Run 1 — 2026-03-08 (BASELINE)
- **Goals:** First run — capture baseline product + SERP data across 11 categories
- **Result:** SUCCESS
- **What worked:**
  - Parallel launch of all 8 Apify runs (3 product + 5 SERP) — all succeeded in ~90 seconds
  - Python processing script approach — avoided context window overflow from 5,052 SERP results
  - Axesso batching: 20-24 keywords per run works well
  - saswave batching: 31-33 ASINs per run works well
- **What didn't:**
  - saswave returns prices with excessive decimal precision (e.g., $10.3231502 instead of $10.32) — need rounding in brief generation
  - Script needed 3 iterations to handle: None titles in SERP data, string prices, string BSR values
  - "Our ASINs found: 0" in product scrape — expected since we only scrape competitors, but brief shows empty "Our Products" table
- **Runtime:** ~5 minutes total (scraping + processing)
- **Apify cost:** 8 runs, ~$3-4 estimated
- **Data collected:** 97 products, 103 keywords, 5,052 SERP results, 286 unknown ASINs in top 10

---

## MCP Builder

### Run: 2026-02-24
**Goals:**
- [x] Build custom Asana MCP server to replace NPM package
- [x] Register 26 tools covering projects, tasks, sections, subtasks, comments, tags, search, dependencies
- [x] Update .mcp.json, CLAUDE.md, folder structure

**Result:** Success

**What happened:**
- Built `mcp-servers/asana/server.py` following existing server pattern (dotenv loader, rate limiter, httpx async client, formatted output)
- Replaced NPM `@roychri/mcp-server-asana` with custom Python server in .mcp.json
- 26 tools in 8 groups: User (3), Teams (1), Projects (3), Sections (3), Tasks (5), Subtasks (2), Comments (2), Tags (3), Search (1), Dependencies (3)
- Auto-pagination helper for list endpoints
- Full CRUD for tasks and projects
- Updated CLAUDE.md with complete tool table and documentation

**What didn't work:**
- Nothing — clean build

**Is this a repeat error?** No

**Lesson learned:**
- The existing server pattern (notion, slack, datadive) is well-established and easy to replicate
- Asana API is straightforward REST with Bearer token auth — no OAuth dance needed for PAT
- Tool count: always verify with `mcp._tool_manager._tools` after building

**Tokens/cost:** ~30K tokens

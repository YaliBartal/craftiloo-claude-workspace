# Lessons Learned — Niche Category Analysis

> **Living document.** Claude MUST read this before every run and write to it after every run.

---

## How to Use This File

### Before Every Run
1. Read this entire file
2. Check **Known Issues** for active problems to avoid
3. Check **Repeat Errors** — if you hit the same issue again, flag it to the user immediately
4. Apply all lessons to your execution plan

### After Every Run
1. Add a new entry under **Run Log** using the template below
2. If something went wrong, add it to **Known Issues**
3. If a Known Issue happened again, move it to **Repeat Errors** and increment the count
4. If you solved a Known Issue, move it to **Resolved Issues**

---

## Run Log

### Run: 2026-02-26
**Goals:**
- [x] Niche analysis for new Barbie/fashion-doll loom knitting kit for kids
- [x] Assess DataDive loom knitting niche (O6b4XATpTj)
- [x] Pull internal Seller Board data for our 3 existing knitting kits
- [x] Competitor pricing via SP-API
- [x] Keyword + roots + ranking juice from DataDive
- [x] Review scraping for top 2 competitors (Hapinest, CFK)

**Result:** ✅ Success — full brief generated with CONDITIONAL GO verdict (32/40)

**Data sources used:** DataDive ✅ | SP-API ✅ | Seller Board ✅ | Apify ✅ (partial — 8 reviews/ASIN)

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

### Run: 2026-02-23
**Goals:**
- [x] Run MCP-powered analysis on "quilt kit for kids" niche
- [x] Compare new DataDive/SP-API data with Feb 22 Apify/BSR analysis
- [x] Set up proper output folder structure

**Result:** ⚠️ Partial — niche dive creation failed, used existing overlapping niche instead

**Data sources used:** DataDive ✅ | SP-API ✅ | Seller Board ❌ | Apify ❌ (reused Feb 22 review data)

**What happened:**
- Successfully pulled DataDive competitor data from "sewing kit for kids new" niche (RmbSD3OH6t) — 10 competitors with Jungle Scout actuals
- Successfully pulled 309 keywords with real search volumes + 305 keyword roots
- Successfully pulled Ranking Juice scores for all 10 competitors
- Successfully pulled SP-API real-time competitive pricing for 10 ASINs
- Comparison revealed BSR tables underestimated market by 2.7x ($105K → $285K)
- Craftiloo underestimated by 6.7x ($4.4K → $29.3K/mo)
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

### Run: 2026-02-22
**Goals:**
- [x] First analysis of "quilt kit for kids" niche
- [x] Identify competitors, pricing, keywords, review themes

**Result:** ✅ Success (Apify + BSR method)

**Data sources used:** DataDive ❌ | SP-API ❌ | Seller Board ❌ | Apify ✅

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

## Known Issues

### 1. DataDive `create_niche_dive` returns HTTP 400
- **First seen:** 2026-02-23
- **Details:** Both B072JH19F8 and B09CR5RX65 as seed ASINs returned 400. `get_profile` also returns 404.
- **Workaround:** Use existing overlapping niches from `list_niches`
- **Impact:** Can't create new DataDive niches — limited to existing 23 niches
- **Action needed:** Check DataDive account status/plan. May need to contact DataDive support or verify API key permissions.

### 4. Review scraper returns only 8 reviews per ASIN (page-1 cap)
- **First seen:** 2026-02-26 (in niche skill context; also seen in customer-review-analyzer)
- **Details:** `junglee/amazon-reviews-scraper` returns page 1 only (~8 reviews) regardless of `maxReviews` setting. `epctex` requires paid rental. `web_wanderer` returns 0.
- **Workaround:** Run junglee multiple times with explicit page numbers (pageNumber=2 through 6 in URL). Cost: ~$0.05 per ASIN for full 50.
- **Impact:** Review analysis is directional only. Patterns from 8 reviews are suggestive, not statistically reliable.
- **Action needed:** Budget $0.10-0.25 per niche for proper review scraping if full review analysis is required.

### 2. DataDive keyword/roots responses exceed context window
- **First seen:** 2026-02-23
- **Details:** Keywords returned 138K chars (70K tokens), roots returned 234K chars. Too large to read directly.
- **Workaround:** Use subagent tasks to extract and summarize key data
- **Impact:** Adds ~80s to execution time per large file
- **Possible fix:** Reduce `page_size` parameter (e.g., 50 instead of 200 for keywords) or add server-side filtering

### 3. DataDive prices may be stale
- **First seen:** 2026-02-23
- **Details:** CRAFTILOO B09WQSBZY7 showed $17.98 in DataDive (updated Feb 8) vs $21.98 in SP-API (real-time Feb 23)
- **Workaround:** Always use SP-API `get_competitive_pricing` for current prices
- **Impact:** Revenue calculations from DataDive may be off if prices changed. DataDive uses price × units, so stale prices affect revenue figures.

---

## Repeat Errors

_None yet._

---

## Resolved Issues

_None yet._

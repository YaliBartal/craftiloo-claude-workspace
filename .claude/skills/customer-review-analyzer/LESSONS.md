# Lessons Learned — Customer Review Analyzer

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
- [x] Scrape 50 reviews each for B0B8W4FK4Q (Hapinest) and B004JIFCXO (Creativity for Kids) — loom knitting kit niche
- [ ] 50 reviews per ASIN (target not met — only 8 per ASIN returned)

**Result:** ⚠️ Partial — scrape succeeded but capped at 8 reviews per ASIN, not 50

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

## Known Issues

### KI-1: junglee/amazon-reviews-scraper hard-capped at ~8 reviews (1 page)
- `maxReviews` parameter is effectively ignored — actor always stops after scraping 1 Amazon reviews page (~8 results)
- Same behavior with and without residential proxy
- `totalCategoryReviews: 1` in output confirms single-page behavior
- **Workaround:** Run actor separately using explicit page URLs: `https://www.amazon.com/product-reviews/{ASIN}?pageNumber=2&sortBy=recent` for pages 2-6 to reach ~50 reviews
- Status: **Active** — do not rely on this actor alone for 50-review targets

### KI-2: axesso_data/amazon-reviews-scraper maxPages parameter non-functional
- Setting `maxPages: 5` returns the same result as `maxPages: 1` — only page 1 is scraped
- Confirmed across two separate runs with different ASINs
- **Workaround:** Same page-by-page approach as KI-1
- Status: **Active**

### KI-3: epctex/amazon-reviews-scraper requires paid rental
- Free trial expired — returns "You must rent a paid Actor" error immediately on run
- Cannot use without subscribing in Apify console
- **Workaround:** Remove from fallback list. Use `junglee` with page URLs or `web_wanderer` instead.
- Status: **Active** — remove from SKILL.md fallback or note rental requirement

### KI-4: web_wanderer/amazon-reviews-extractor returned 0 results on first attempt
- Attempted with ASIN string input and `limit: 5`, `sort: "recent"` — returned 0 items in dataset
- Possible anti-bot block or incorrect input format (may need full product review URL)
- Actor claims 100 reviews per star (500 total) in `all_stars` mode — worth retesting
- **Workaround:** Retry with full Amazon review URL format rather than ASIN string
- Status: **Untested further** — needs retry before dismissing

---

## Repeat Errors

_None yet._

---

## Resolved Issues

_None yet._

# Lessons Learned — Listing Creator

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

### Run: 2026-03-02
**Product:** 4 Embroidery Flowers Kit (B0DC69M3YD / EK17)
**Mode:** Rewrite based on Listing Optimizer audit (not from-scratch)
**Goals:**
- [x] Generate 3 title options with keyword placement rationale
- [x] Generate 5 recommended bullets with alternatives for each
- [x] Generate 2 description options (full + mobile-friendly)
- [x] Generate backend keywords (247/249 bytes)
- [x] Upload to Notion under Product Listing Development
- [ ] Scrape competitor Q&A (product scraper doesn't return Q&A — used competitor bullets + web search instead)

**Result:** ✅ Success

**What worked:**
- Using the listing-optimizer audit report as input saved massive time — no need to redo competitor research, keyword gaps, or rank radar analysis
- Competitor bullet scraping via `saswave~amazon-product-scraper` confirmed all 3 competitor bullet sets
- Keyword placement map ties each keyword to specific title/bullet/backend location with search volume
- Notion upload successful (109 blocks, page ID: 31757318-d05c-816b-9f38-db4da7e7c6e5)
- All measurements in inches per US market rule

**What didn't work:**
1. **Apify product scraper doesn't include Q&A sections** — `saswave~amazon-product-scraper` returns title, bullets, price, BSR but NOT customer questions. Searched for dedicated Q&A scraper (`epctex/amazon-questions-answers-scraper`) but it didn't appear in Apify store search results
2. **Workaround:** Used competitor bullet themes + web search for common embroidery kit questions. Mapped these to bullet answers successfully

**Is this a repeat error?** No — first run

**Lessons learned:**
- When a listing-optimizer audit exists, use it as primary input — saves 50%+ tokens
- `saswave~amazon-product-scraper` does NOT include Q&A data — need a different actor or manual web scraping for customer questions
- Competitor bullets are nearly as useful as Q&A for understanding customer concerns — every competitor's bullets are written to answer the same questions
- Product catalog discrepancy: products.md says "4 threaders" but hero-products.md says "2 needle threaders" — need user to verify

**Tokens/cost:** ~45K tokens, ~$0.04 Apify (3 competitor scrapes)

**Post-run update (2026-03-03):** Listing rewrite was pushed live to Amazon via SP-API `update_listing` tool. Submission ID: a7db9ea7233c4245962c10e5821723a0. Status: ACCEPTED. All 4 fields updated (title Option A, 5 recommended bullets, description Option A, backend keywords 247/249 bytes). SKU on Amazon is `7B-EONH-U3A3` (not EK17 — that's the internal catalog name). Product type: `ART_CRAFT_KIT`.

---

## Known Issues

### 1. Apify product scraper does not include customer Q&A
- **First seen:** 2026-03-02
- **Details:** `saswave~amazon-product-scraper` returns product data but no Q&A. Dedicated scraper `epctex/amazon-questions-answers-scraper` not found in Apify store search.
- **Workaround:** Use competitor bullets + web search to infer top customer questions. Map to bullet answers.
- **TODO:** Search Apify store more thoroughly or try direct URL scraping of Amazon Q&A pages

### 2. Product catalog discrepancy — threader count
- **First seen:** 2026-03-02
- **Details:** `context/products.md` says EK17 has "4 threaders" but `context/hero-products.md` says "2 needle threaders"
- **Impact:** Bullet 1 may have wrong count
- **Fix:** Ask user to verify actual kit contents

---

## Repeat Errors

_None yet._

---

## Resolved Issues

_None yet._

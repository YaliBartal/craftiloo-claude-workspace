# Lessons Learned — Listing Optimizer

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
**Mode:** Single Product Audit
**Product:** 4 Embroidery Flowers Kit (B0DC69M3YD)
**Goals:**
- [x] Full listing audit with Ranking Juice, keyword gaps, rank trends, competitor comparison
- [x] Generate rewrite recommendations for title, bullets, description
- [ ] Run AI Copywriter in all 4 modes (failed)

**Result:** ⚠️ Partial — audit complete, AI Copywriter failed

**What worked:**
- DataDive Ranking Juice, MKL, Roots, Rank Radar all fetched successfully
- Seller Board sales data extracted correctly for Jan + Feb 2026
- Apify competitor scrape got all 5 competitor listings (after actor name fix)
- Amazon SP-API Merchant Listings report fetched (revealed empty bullets/description)
- Comprehensive correlation analysis connecting listing weakness to rank decline
- Snapshot JSON saved for future trend tracking

**What didn't work:**
1. **Apify actor name wrong** — `junglee/amazon-product-scraper` returned 404. Fixed by using `saswave~amazon-product-scraper`
2. **DataDive AI Copywriter failed on ALL 4 modes** — HTTP 400 "Invalid prompt option" even though exact mode names (cosmo, ranking-juice, nlp, cosmo-rufus) were used. Could not resolve. Workaround: manual rewrite recs based on gap analysis
3. **SP-API Sales & Traffic report didn't contain B0DC69M3YD** — report only had 10 parent ASINs; this product's parent wasn't among them. Fell back to Seller Board CVR data
4. **SP-API Merchant Listings report has no bullet-point columns** — GET_MERCHANT_LISTINGS_ALL_DATA format doesn't include bullet fields. Description was just "Embroidery Kit"
5. **DataDive niche mismatch** — niche gfot2FZUBU ("Embroidery Stitch Practice Kit") contains mostly kids' cross stitch products, not adult embroidery. Our actual market competitors (CYANFOUR, Santune, etc.) are NOT in this niche. Ranking Juice scores are valid for optimization %, but MKL rank data compares against wrong competitors

**Is this a repeat error?** No — first run

**Lessons learned:**
- Always use `saswave~amazon-product-scraper` for Apify product scraping, NOT `junglee/amazon-product-scraper`
- AI Copywriter API may have changed — investigate parameter format before next run
- SP-API Sales & Traffic may not include all ASINs — always fetch Seller Board as backup
- SP-API Merchant Listings doesn't include bullet points — need Apify to get our own bullets too
- Niche mismatch is a real issue for products in wrong DataDive niche — flag this to user and consider creating a better-matched niche

**Tokens/cost:** ~95K tokens, ~$0.08 Apify (5 competitor scrapes)

**Post-run update (2026-03-03):** Audit recommendations were implemented. Listing creator generated the rewrite, then all 4 fields (title, bullets, description, backend keywords) were pushed live via SP-API Listings Items API PATCH. Submission ACCEPTED. Key discovery: Amazon SKU is `7B-EONH-U3A3` (not internal catalog name EK17). Product type: `ART_CRAFT_KIT`. SP-API `get_listing` + `update_listing` tools now available for future audits → direct application. Re-audit due 2026-03-10 to measure rank recovery and CVR impact.

---

## Known Issues

### 1. DataDive AI Copywriter returns HTTP 400 on all modes
- **First seen:** 2026-03-02
- **Details:** All 4 modes (cosmo, ranking-juice, nlp, cosmo-rufus) return "Invalid prompt option" despite using exact documented mode names
- **Impact:** No AI-generated rewrite alternatives; must provide manual recommendations
- **Workaround:** Manual rewrite recs based on keyword gap + competitor listing analysis
- **TODO:** Check if API parameters changed — may need `product_name` or `product_description` in different format

### 2. Apify actor `junglee/amazon-product-scraper` no longer exists
- **First seen:** 2026-03-02
- **Details:** Returns 404. Correct actor is `saswave~amazon-product-scraper`
- **Impact:** Delays competitor scraping if wrong actor used first
- **Fix:** Always use `saswave~amazon-product-scraper`

### 3. SP-API Sales & Traffic report may not contain all ASINs
- **First seen:** 2026-03-02
- **Details:** GET_SALES_AND_TRAFFIC_REPORT only returned 10 parent ASINs; B0DC69M3YD's parent was missing
- **Workaround:** Always fetch Seller Board as backup for CVR/sessions data

### 4. SP-API Merchant Listings report has no bullet-point columns
- **First seen:** 2026-03-02
- **Details:** GET_MERCHANT_LISTINGS_ALL_DATA doesn't include bullet-point-1 through bullet-point-5 fields
- **Impact:** Can't get our own bullets from SP-API — need Apify or manual check
- **Workaround:** Add our own ASIN to Apify batch if bullets are needed

### 5. DataDive niche mismatch for 4 Embroidery Flowers (gfot2FZUBU)
- **First seen:** 2026-03-02
- **Details:** Niche "Embroidery Stitch Practice Kit" contains mostly kids' cross stitch products. Our actual adult embroidery competitors (CYANFOUR, Santune, Bradove, ETSPIL) are NOT in this niche
- **Impact:** MKL rank comparisons are against wrong competitors; Ranking Juice % is still valid but competitor context is misleading
- **Recommendation:** Consider creating a new DataDive niche with proper adult embroidery competitors as seed ASIN

---

## Repeat Errors

_None yet._

---

## Resolved Issues

_None yet._

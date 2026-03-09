# Competitor Price & SERP Tracker -- Lessons Learned

## Run Log

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

## Known Issues

### 1. Price precision from saswave scraper
saswave returns prices like $10.3231502 instead of $10.32. Round to 2 decimal places in all outputs.

### 2. Null/string type safety in Apify data
All numeric fields from both scrapers can be null or string type. Must use safe_float/safe_int conversion. Fields affected: price, BSR rank, rating, review count, search position.

### 3. Uncategorized ASINs need mapping
66 uncategorized ASINs were scraped but aren't assigned to any category. Need manual review and categorization.

### 4. Our ASINs not in product scrape
Skill only scrapes competitor + uncategorized ASINs. Our ASINs only appear in SERP results. For our own price/BSR snapshots, use Seller Board data.

---

## Repeat Errors

_None yet._

---

## Resolved Issues

_None yet._

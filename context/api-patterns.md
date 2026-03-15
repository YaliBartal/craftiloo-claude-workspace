# API Patterns & Gotchas

> Shared knowledge extracted from all skill LESSONS.md files. Loaded by skills that call external APIs.
> Last updated: 2026-03-11

---

## Amazon Ads API

- **Auth:** LWA OAuth2 (auto-refreshing). Profile IDs in .env as `ADS_API_PROFILE_US`, `ADS_API_PROFILE_CA`
- **Expression types use SCREAMING_SNAKE_CASE:** `ASIN_SAME_AS`, `MANUAL`, `NEGATIVE_EXACT`, `LEGACY_FOR_SALES`. Never use camelCase (`asinSameAs` → HTTP 400)
- **Campaign `startDate` format:** `YYYY-MM-DD` (ISO). Compact `YYYYMMDD` → HTTP 400
- **Campaign states:** `ENABLED`, `PAUSED`, `PROPOSED` only. No `ARCHIVED` via API — must archive in Seller Central UI
- **Campaign-level negative keywords** require `campaignId` + `state` in EACH keyword object (unlike ad-group negatives)
- **Campaign-level negatives** use `PAUSED` (not `ARCHIVED`) for deactivation
- **Amazon rejects negative keywords >4 words**
- **Product ads need SKU field:** `manage_sp_product_ads` requires `{"asin": "...", "sku": "..."}`, not just ASIN
- **No `portfolioId` in async reports.** Must map campaigns to portfolios via `list_sp_campaigns` by name or portfolioId field
- **`list_sp_campaigns` with `state=ALL`** returns 200 ARCHIVED items first, hiding ENABLED campaigns. Always query `state=ENABLED` explicitly
- **Never scope portfolios by campaign name patterns.** Names like "cross stitch" appear across multiple portfolios. Always verify via `portfolioId` field
- **Reports can be PENDING 5-30 min.** All 4 reports may stuck simultaneously. Don't panic — poll every 30-60s. Workaround: use cached data if <3 days old. Reports often self-resolve within 30 min
- **Report presets:** `sp_campaigns`, `sp_search_terms`, `sp_keywords`, `sp_targets`, `sp_placements`, `sp_purchased_products`
- **sp_placements config:** `groupBy` uses `campaignPlacement`, `columns` must include `placementClassification` for labeled output
- **Placement labels:** "Top of Search on-Amazon", "Detail Page on-Amazon", "Other on-Amazon", "Off Amazon"
- **"Other on-Amazon" placement has no bid modifier.** Only TOS and Product Page modifiers exist. To reduce "Other" waste, lower the DEFAULT BID
- **Bid recommendation API** may return HTTP 429 — use search term CPC data as fallback
- **Calendar-aligned date ranges only.** Never use `LAST_7_DAYS` (rolling window causes WoW drift). Use explicit start/end dates (Mar 1-7, Mar 8-14)
- **⚠️ Placement modifier updates silently fail.** `update_sp_campaigns` returns HTTP 200 for TOS/PP/ROS `placementBidding` changes, but values don't persist. Campaign state (ENABLED/PAUSED) and budget changes DO work. Confirmed on 2026-03-05 (9 Shield All campaigns) and again 2026-03-15. **Mandatory verification:** After ANY placement modifier change, call `list_sp_campaigns` for the modified campaign(s) and compare returned `placementBidding` against requested values. If mismatch: retry once, verify again, log as FAILED if still wrong. See ppc-bid-recommender SKILL.md Step 8 VERIFY for full procedure. Root cause TBD — may need separate API call for placement bidding vs campaign state

## Amazon SP-API

- **Auth:** LWA OAuth2 (auto-refreshing, 1hr expiry). No AWS credentials needed
- **`get_listing(sku)`** is the best way to get our own listing copy — returns title, bullets, description, backend keywords in one call
- **`product_type`:** Use `ART_CRAFT_KIT` when `get_listing` returns `UNKNOWN`. Works for all Craftiloo craft kits
- **SKU mismatch:** Internal catalog SKUs (CS01, CC48, EK17) differ from Amazon SKUs. Always check Seller Board or `get_fba_inventory` for real Amazon SKU
- **`get_fba_inventory` without `asin_filter`** returns individual SKUs. With filter, it aggregates across SKUs and hides names
- **Merchant Listings report** (`GET_MERCHANT_LISTINGS_ALL_DATA`) has no bullet-point columns — use `get_listing(sku)` instead
- **Sales & Traffic report** may not contain all ASINs — always fetch Seller Board as backup for CVR/sessions
- **Brand Analytics weekly = Sun-Sat.** Use `periods_back=2` on Sun/Mon (48h SLA — most recent week may not be ready)
- **SQP requires `asins` param** (space-separated, max 200 chars). All other BA reports don't
- **Search Terms BA report:** 591 MB compressed, ~8.3M rows. Pass `save_path` ending in `.gz` to `get_report_document` — this triggers streaming bytes to disk (no RAM decompression). Then run `filter_search_terms.py` with our ASINs to extract only relevant rows (~86 matches for our 41 active ASINs). JSON structure: flat `dataByDepartmentAndSearchTerm[]` array. **Each row = one (searchTerm, ASIN, rank) triplet**: fields are `searchTerm`, `departmentName`, `searchFrequencyRank`, `clickedAsin`, `clickedItemName`, `clickShareRank` (1/2/3), `clickShare`, `conversionShare`. NOT `clickedAsin1/2/3` — that format does not exist.
- **BA processing times:** market_basket ~45s, sqp/scp/repeat ~60s, search_terms ~5min
- **`update_listing` rejects `UNKNOWN` product_type** — always specify a valid type

## Seller Board

- **CSV output capped at 100 rows by default** (`csv_to_summary max_rows=100`). 30d report has ~2,000 rows. ALWAYS use `save_path` parameter
- **Sanity check:** Craftiloo US does ~$170K/month. If 30d data shows <$10K, it's truncated
- **7d report** (~460 rows) is manageable without `save_path`
- **"Real ACOS" column is TACoS** (total ad spend / total revenue) — no need to compute manually
- **CSV requires BOM handling** and double-quoted headers
- **Tokens may expire** — if 401 errors, regenerate URLs in SB → Settings → Automation → Reports

## Apify

- **Product scraper:** Always use `saswave~amazon-product-scraper` (NOT `junglee/amazon-product-scraper` — 404)
- **saswave prices** have excessive decimal precision (e.g., $10.3231502) — round to 2 decimal places
- **saswave BSR field:** `bestsellerRanks[0].rank` (comma-formatted string, e.g., "29,277"). Strip commas before parsing
- **saswave prices may be in EUR** — ignore price field, use SP-API for accurate pricing
- **Review scrapers capped at ~8 reviews** (1 page). `junglee` and `axesso_data` both ignore `maxReviews`/`maxPages`. Workaround: run with explicit page URLs (`?pageNumber=2&sortBy=recent`)
- **`epctex/amazon-reviews-scraper`** requires paid rental — remove from fallback lists
- **axesso keyword scan input format:** `{"input": [{"keyword": "...", "country": "US"}]}`. Position field: `searchResultPosition` (0-indexed)
- **axesso actor MUST use internal ID `9GmEDf8sr9Jyb6b3X`** — slug format `axesso_data/amazon-search-scraper` or `axesso_data~amazon-search-scraper` returns 404 on both sync and async endpoints. Use `run_actor("9GmEDf8sr9Jyb6b3X", ...)` (confirmed 2026-03-15)
- **All numeric fields from scrapers can be null or string type** — always use safe_float/safe_int conversion

## DataDive

- **`create_niche_dive` may return HTTP 400** — possible account/plan limitation. Use existing niches from `list_niches` instead
- **Keyword/roots responses can be very large** (138K-234K chars). Use subagents or save to file for processing
- **Prices may be stale** — always cross-reference with SP-API `get_competitive_pricing` for current prices
- **AI Copywriter returns HTTP 400 on all 4 modes** (cosmo, ranking-juice, nlp, cosmo-rufus) — "Invalid prompt option". Unresolved as of 2026-03-05. Skip and use manual analysis

## Notion

- **Product Listing Development parent page:** `30557318-d05c-806a-a94f-f5a439d94d10`
- **Use `append_markdown` or `create_page_with_content`** for simplified markdown input

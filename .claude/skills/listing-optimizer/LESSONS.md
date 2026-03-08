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

### Run: 2026-03-06 (f)
**Mode:** Single Product Audit
**Product:** Latch Hook Pencil Cases Kit (B08FYH13CL / M8-07DZ-ZEYX)
**Result:** Success

**Key findings:**
- Ranking Juice: 172,790 / 310,881 (55.6%) - #5 in niche
- Title RJ: 49,246 / 97,104 (50.7%) - #7 of 10 (biggest weakness)
- Title only 98/200 chars (49%) - massive wasted space
- Backend KW only 95/249 bytes (38%) - 154 bytes wasted
- Bullet 5 wasted on returns policy
- Latchkits in title is competitor brand (trademark risk)
- Sewing Set in title is wrong category

**What worked:**
- SP-API listings search by ASIN found SKU M8-07DZ-ZEYX
- All DataDive sources fetched successfully
- Background subagents for large data analysis

**What didn't work:**
- SKU not in sku-asin-mapping.json
- Seller Board save_path param broken
- OneDrive EEXIST (repeat x4)

**Lessons:** When SKU not in mapping, use SP-API identifiers search. B08FYH13CL is oldest product (2020), never optimized.

**Tokens/cost:** ~80K tokens, /usr/bin/bash Apify

---

### Run: 2026-03-06 (e)
**Mode:** Single Product Audit
**Product:** Princess Lacing Card Kit (B0FQC7YFX6 / 6P-KW6N-9F9J)
**Result:** Success

**Key findings:**
- Bullets have ZERO Ranking Juice - no MKL keywords detected in any bullet
- Title missing brand name CRAFTILOO and key roots: sewing (7,130 BSV), toy (4,098), threading (2,267)
- Princess leads title but is not a search term - wastes highest-weight position
- Product ranks for sewing keywords despite sewing not appearing in listing (category cross-indexing)
- Price positioning: $19.98 vs niche avg $11.99 - structural headwind
- Backend keywords largely empty - massive room for expansion

**What worked:**
- DataDive RJ, MKL (150 kw), Roots, Rank Radar all fetched successfully
- Seller Board 7d data provided sales/CVR context
- SP-API get_listing confirmed current listing attributes
- Subagent handled Rank Radar data analysis (178K chars) effectively

**What didn't work:**
- Write tool EEXIST error (OneDrive sync) - used Bash heredoc as workaround

**Is this a repeat error?** Yes - OneDrive EEXIST (x3 across listing-optimizer runs)

**Lessons learned:**
- Launch-stage products often have listings written for humans (benefit copy) but not for Amazon algorithm (keyword indexing)
- A product can rank for keywords not in its listing via category cross-indexing - but adding them explicitly would dramatically boost rank
- Emoji decorators in bullets waste space that should be keyword-indexed text

**Tokens/cost:** ~60K tokens, $0 Apify

---

### Run: 2026-03-06 (d)
**Mode:** Single Product Audit + Listing Creator (combined workflow)
**Product:** 10mm Big Fuse Beads (B07D6D95NG / O9-70DP-C5J6)
**Result:** Success - full audit + 3 title options + 5 bullets + backend KW generated

**Key findings:**
- Ranking Juice: 173,532 / 704,160 (24.6%) - #8 in niche (near bottom)
- Bullets RJ: 3,631 / 29,805 (12.2%) - terrible, biggest weakness
- Backend KW: 105/249 bytes = 58% WASTED (144 bytes empty!)
- Rank Radar: 13/38 top 10 but only branded terms (3,250 SV)
- Declining: fuse beads kit (-35 pos), melting beads (-41 pos)
- Bullet 5 wasted on ORDER WITH CONFIDENCE
- Last in niche: 182 sales/mo, 103 reviews, 4.1 rating (all lowest)

**Issues:** OneDrive EEXIST error writing brief (workaround: Bash cat)

**Lessons:**
- Product with most room for improvement of any audited
- Backend keywords at 42% usage is worst seen - easy win
- Subagent approach for large MKL/Roots/RankRadar files works well

**Tokens/cost:** ~80K tokens, 0 Apify

**Post-run update (2026-03-06):** Listing rewrite pushed to Amazon via SP-API. Submission ID: 54986da36c924c8d9607be42f969e546. Status: ACCEPTED. Title Option A, 5 bullets (user chose educational Bullet 5 over compatibility), backend 248/249 bytes. Portfolio tracker updated.

---

### Run: 2026-03-06 (c)
**Mode:** Single Product Audit + Listing Creator (combined workflow)
**Product:** Cross Stitch Kit - Girls (B08DDJCQKF / CS01 / FH-FMO5-Y9LJ)
**Result:** Success - full audit + 3 title options + 5 bullets + backend KW generated

**Key findings:**
- Ranking Juice: 175,006 / 214,096 (81.7%) - #1 in niche
- Title RJ: 51,246 / 60,633 (84.5%) - 9,387 point gap to optimal
- Bullets RJ: 10,634 / 11,072 (96.0%) - near-perfect
- Rank Radar: 36/38 keywords in top 10, 15/38 at #1
- Title issues: no brand, keyword-stuffed with periods, no age range, missing easy
- Bullet 3 says 2 needles but product has 4 needles + 2 threaders
- Bullet 5 wasted on ORDER WITH CONFIDENCE customer service message
- Backend KW only 183/249 bytes - 66 bytes opportunity
- Sales: ~540/day, 27 units/day, 12-15% CVR, 18-19% ACoS

**Issues:** None - all data sources worked

**Lessons:**
- Amazon SKU FH-FMO5-Y9LJ (not CS01)
- For #1 ranked products, listing changes carry medium risk - include risk assessment
- product_type UNKNOWN returned by get_listing (Known Issue #8)
- Previous audit (2026-02-23) exists - useful for trend comparison
- First hero product audit where ALL data sources worked without failure

**Tokens/cost:** ~70K tokens, 0 Apify

---

### Run: 2026-03-06 (b)
**Mode:** Single Product Audit + Listing Creator (combined workflow)
**Product:** 24K Mini Fuse Beads (B09THLVFZK / CC48)
**Result:** Success — audit complete, listing pushed and ACCEPTED (Submission ID: 2bfbdf753cba40ada513c843bbe295c0)

**Key findings:**
- Ranking Juice: 381,565 / 1,212,066 (31% of optimal)
- Title RJ: 117,349 vs top competitor 291,356
- Rank Radar: 10/18 keywords on Page 1, 163K combined SV
- Declining: fuse beads (#3->#7), perler beads bulk (#33), melting beads (#3->#11)
- Core business problem: wrong-buyer refunds (parents buying for kids, 2.6mm beads too small)
- Solution: 8 anti-refund signals woven across listing (educate > warn)
- Pushed: Title Option A, 5 bullets, backend KW (244/249 bytes). Skipped description (A+ active)
- SKU on Amazon: RV-FA22-4WFQ (not CC48). Product type: ART_CRAFT_KIT

**Issues:** Apify scrape FAILED x2 (repeat). AI Copywriter skipped (repeat x4).

**Lessons:**
- SKU mismatch: CC48 != RV-FA22-4WFQ — always check Seller Board for real SKU
- Refund-prevention through education beats warnings
- A+ content overrides description — always ask about A+ before pushing description
- Apify saswave~amazon-product-scraper unreliable (2 failures)
- Anti-refund: compare sizes, mention pegboard incompatibility, multiple gentle signals > 1 aggressive warning

**Tokens/cost:** ~80K tokens, $0 Apify (failed)

---

### Run: 2026-03-06 (a)
**Mode:** Single Product Audit + Listing Creator (combined workflow)
**Product:** Fairy Sewing Kit (B09WQSBZY7)
**Result:** Success — audit complete, listing pushed and ACCEPTED (Submission ID: ce4555272818413d9801469b2ce64e89)

**Key findings:**
- DataDive Ranking Juice, MKL (309 kw), Roots, Rank Radar (50 kw, 30d) all fetched
- 23/50 tracked keywords declining including kids sewing kit falling off page 1
- Root gaps: ages, 8-12, beginners = 80K+ BSV missing from title
- Title RJ #8 of 10 in niche (13,827 vs avg 34,727) confirmed title as core weakness
- Bullets RJ #1 in niche (22,990) — bullets were strong, kept spirit intact
- Pushed via SP-API: new title (Option A with brand+ages+beginner+stuffed animal), 5 bullets, backend KW (246/249 bytes)
- Skipped description (A+ content active)

**Issues:** Apify scrape returned empty (new issue). AI Copywriter skipped (repeat x3).

**Lessons:** Always ask about A+ before writing description. Count backend KW bytes before submit (249 not 250). Root analysis reveals gaps keyword-level misses. Combined audit+creator workflow is efficient.

**Tokens/cost:** ~90K tokens, /usr/bin/bash Apify

---

### Run: 2026-03-05
**Mode:** Single Product Audit
**Product:** My First Cross Stitch Kit for Kids (B0F6YTG1CH)
**Goals:**
- [x] Full listing audit with keyword gap analysis, root coverage, competitor comparison
- [x] Generate rewrite recommendations for title, bullets, backend keywords
- [ ] Run AI Copywriter in all 4 modes (failed — repeat issue x2)
- [ ] Ranking Juice scoring (N/A — product not tracked in niche)
- [ ] Rank Radar trend analysis (N/A — no radar exists for this ASIN)

**Result:** ⚠️ Partial — audit complete, but limited by DataDive tracking gaps

**What worked:**
- SP-API `get_listing(sku='75-24RO-YAXR')` successfully retrieved full listing copy including title, all 5 bullets, description, and backend keywords — much better than Merchant Listings report
- DataDive MKL fetched 93 keywords with search volumes and competitor ranks
- DataDive Roots fetched and top 30 analyzed by broadSearchVolume
- Apify competitor scrape succeeded for all 5 ASINs (4 competitors + our own) using `saswave~amazon-product-scraper`
- Seller Board extracted B0F6YTG1CH data (2 days only — product is new)
- Word-level keyword coverage analysis revealed 10 missing words affecting 24 keywords
- Critical finding: "embroidery" missing from title entirely
- Snapshot JSON and full audit report saved

**What didn't work:**
1. **DataDive AI Copywriter failed on ALL 4 modes (REPEAT x2)** — HTTP 400 "Invalid prompt option" again
2. **B0F6YTG1CH NOT tracked in DataDive niche b4Nisjv3xy** — no Ranking Juice score, no MKL organic rank positions for our ASIN. Could only analyze keyword universe and competitor ranks, not our own positions
3. **No Rank Radar exists for B0F6YTG1CH** — no rank trend data available
4. **Only 2 days of Seller Board data** — product is newly launched, limited confidence in CVR/sales metrics
5. **Context compaction mid-session** — session ran out of context and had to be continued. Lost some intermediate data and had to re-fetch MKL and Roots

**Is this a repeat error?** Yes — AI Copywriter (×2)

**Lessons learned:**
- `get_listing(sku)` is far superior to Merchant Listings report — use it always for our own listing copy
- New/recently launched products may not be tracked in DataDive niches — check early and flag to user
- Always verify the target ASIN exists in the niche's competitor list before fetching Ranking Juice
- Word-level keyword analysis (checking individual words, not exact phrases) is more accurate for how Amazon A10 indexes
- Newly launched products may have very limited Seller Board data — note the data window in the report
- For products not tracked in DataDive, recommend adding to niche or creating Rank Radar as P2 action

**Tokens/cost:** ~85K tokens, ~$0.05 Apify (5 scrapes)

**Post-run update (2026-03-05):** Audit recommendations implemented same day via listing-creator skill. Listing pushed live via SP-API `update_listing`. Submission ID: 040c70871fad4befb88e67d8b39c034b. Status: ACCEPTED. All 4 fields (title, bullets, description, backend keywords). SKU: `75-24RO-YAXR`. Product type: `ART_CRAFT_KIT` (get_listing returned "UNKNOWN" — known issue, ART_CRAFT_KIT accepted). Word-level coverage estimated to improve from 59% to ~90%. Verification task due 2026-03-06. Re-audit recommended 2026-03-12 to measure rank and CVR impact.

---

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

### 1. ~~DataDive AI Copywriter returns HTTP 400 on all modes~~ → MOVED TO REPEAT ERRORS (×2)

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

### 6. New/recently launched products may not be tracked in DataDive niche
- **First seen:** 2026-03-05
- **Details:** B0F6YTG1CH (My First Cross Stitch Kit) is not in the competitor list for niche b4Nisjv3xy. No Ranking Juice score, no organic rank data in MKL, no Rank Radar.
- **Impact:** Cannot do full Ranking Juice comparison or rank trend analysis. Must rely on word-level keyword coverage analysis.
- **Workaround:** Word-level analysis of keyword presence in listing copy vs MKL keyword universe. Check root word coverage. Still valuable but missing quantitative optimization score.
- **Recommendation:** Before running an audit, verify ASIN is in niche competitor list. If not, recommend user add it to DataDive or create a Rank Radar.

### 7. SP-API `get_listing(sku)` is the best way to get our own listing copy
- **First seen:** 2026-03-05
- **Details:** `get_listing` returns full title, all 5 bullets, description, backend keywords, and product type in a single call. Far better than Merchant Listings report (which lacks bullets) or Apify (which costs money).
- **Impact:** Positive — eliminates need for Apify scrape of our own ASIN
- **Action:** Always use `get_listing(sku)` for our products. Only need Apify for competitors.

### 8. SP-API `get_listing` returns "UNKNOWN" product_type for some ASINs
- **First seen:** 2026-03-05
- **Details:** B0F6YTG1CH returned product_type "UNKNOWN" from `get_listing`. `update_listing` rejects "UNKNOWN" as invalid. Workaround: use `ART_CRAFT_KIT` (accepted for both B0DC69M3YD and B0F6YTG1CH).
- **Impact:** Delays the push — requires a retry with correct product type.
- **Fix:** For Craftiloo craft kits, always try `ART_CRAFT_KIT` as product_type when get_listing returns "UNKNOWN".

### 9. Apify saswave~amazon-product-scraper intermittently fails
- **First seen:** 2026-03-06
- **Details:** Actor returns HTTP 400 run-failed on both attempts. Tried with 5 ASINs, then 3 ASINs. Both failed.
- **Impact:** Cannot scrape competitor bullet points for detailed comparison
- **Workaround:** Proceed with DataDive data (Ranking Juice, MKL, Roots, Rank Radar) + context/competitors.md. These provide sufficient keyword and ranking data for the audit.
- **TODO:** Test alternative Apify actors or check if saswave actor requires updated input format

### 10. Amazon SKU may differ from internal catalog SKU
- **First seen:** 2026-03-06
- **Details:** Internal SKU CC48 does not match Amazon SKU RV-FA22-4WFQ. SP-API get_listing(sku="CC48") returns 404.
- **Impact:** Delays listing fetch — requires checking Seller Board to find real Amazon SKU
- **Fix:** Always check Seller Board report for the actual SKU before calling get_listing

### 5. DataDive niche mismatch for 4 Embroidery Flowers (gfot2FZUBU)
- **First seen:** 2026-03-02
- **Details:** Niche "Embroidery Stitch Practice Kit" contains mostly kids' cross stitch products. Our actual adult embroidery competitors (CYANFOUR, Santune, Bradove, ETSPIL) are NOT in this niche
- **Impact:** MKL rank comparisons are against wrong competitors; Ranking Juice % is still valid but competitor context is misleading
- **Recommendation:** Consider creating a new DataDive niche with proper adult embroidery competitors as seed ASIN

---

## Repeat Errors

### 1. DataDive AI Copywriter returns HTTP 400 on all modes (×2)
- **First seen:** 2026-03-02 | **Last seen:** 2026-03-05
- **Occurrences:** 2
- **Details:** All 4 modes (cosmo, ranking-juice, nlp, cosmo-rufus) return "Invalid prompt option" despite using exact documented mode names and providing product_name + product_description
- **Impact:** No AI-generated rewrite alternatives; must provide manual recommendations
- **Workaround:** Manual rewrite recs based on keyword gap + competitor listing + root coverage analysis
- **Status:** UNRESOLVED — may require DataDive support ticket or API investigation

---

## Resolved Issues

_None yet._

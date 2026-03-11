# Listing Skills — Run Log Archive (March 2026)

> Extracted from LESSONS.md files for listing-optimizer, listing-creator, and listing-manager skills. Run entries only — Known Issues, Repeat Errors, and Resolved Issues remain in the original files.

---

## Listing Optimizer

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

**Result:** Partial — audit complete, but limited by DataDive tracking gaps

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

**Is this a repeat error?** Yes — AI Copywriter (x2)

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

**Result:** Partial — audit complete, AI Copywriter failed

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

**Post-run update (2026-03-03):** Audit recommendations were implemented. Listing creator generated the rewrite, then all 4 fields (title, bullets, description, backend keywords) were pushed live via SP-API Listings Items API PATCH. Submission ACCEPTED. Key discovery: Amazon SKU is `7B-EONH-U3A3` (not internal catalog name EK17). Product type: `ART_CRAFT_KIT`. SP-API `get_listing` + `update_listing` tools now available for future audits -> direct application. Re-audit due 2026-03-10 to measure rank recovery and CVR impact.

---

## Listing Creator

### Run: 2026-03-06 (e)
**Product:** Latch Hook Pencil Cases Kit (B08FYH13CL / M8-07DZ-ZEYX)
**Mode:** Rewrite based on Listing Optimizer audit (same session)
**Goals:**
- [x] Generate 3 title options with keyword placement rationale
- [x] Generate 5 recommended bullets
- [x] Generate optimized backend keywords (249/249 bytes)
- [ ] Upload to Notion (not requested)
- [x] Push to Amazon via SP-API (submission ID: c3e8e77c092e493b824fab5ce0091070, ACCEPTED)

**Result:** Success

**Post-run update (2026-03-06):** Listing pushed live. Title Option A (187 chars), 5 bullets (fixed Bullet 2 duplicate dimensions), backend 249/249 bytes. SKU: M8-07DZ-ZEYX. Product type: ART_CRAFT_KIT. Description skipped (A+ active). Portfolio tracker + agent-state updated.

**What worked:**
- Combined audit+creator in single session - efficient, no duplicate fetching
- All DataDive data (RJ, Roots 35 entries, Rank Radar 53 kw) used
- No Apify needed - DataDive + SP-API sufficient
- Backend expanded from 95 to 249 bytes (+162%)
- Identified Latchkits as competitor brand - removed
- Bullet 5 completely rewritten from returns to brand trust

**What didn't work:**
- OneDrive EEXIST error with Write tool (workaround: Python open())

**Is this a repeat error?** Yes - OneDrive EEXIST (x5)

**Lessons learned:**
- Oldest products (launched 2020) have most room for improvement
- Competitor brand names in titles are a real trademark risk
- Sewing Set for a latch hook product attracts wrong buyers
- 62% backend waste is the worst seen - easy massive win

**Tokens/cost:** ~80K tokens, 0 Apify (shared session with audit)

---

### Run: 2026-03-06 (d)
**Product:** Princess Lacing Card Kit (B0FQC7YFX6 / 6P-KW6N-9F9J)
**Mode:** Rewrite based on Listing Optimizer audit (same session)
**Goals:**
- [x] Generate 3 title options with keyword placement rationale
- [x] Generate 5 recommended bullets with keyword indexing
- [x] Generate optimized backend keywords (247/249 bytes)
- [ ] Upload to Notion (not requested)
- [x] Push to Amazon via SP-API (submission ID: 54986da36c924c8d9607be42f969e546, ACCEPTED)

**Result:** Success

**What worked:**
- Combined audit+creator in single session - very efficient
- All DataDive data (RJ, MKL 150 kw, Roots, Rank Radar) fetched without failures
- No Apify needed - DataDive + context files sufficient
- Identified sewing keyword paradox - product ranks for sewing despite not being in listing
- Three missing high-BSV roots (sewing/toy/threading) now covered across title+bullets+backend

**What didn't work:**
- Write tool EEXIST error (OneDrive sync) - workaround: Bash heredoc, then Python open()
- Bash heredoc also failed due to single quotes in content - Python file writing was final solution

**Is this a repeat error?** Yes - OneDrive EEXIST (x4 across listing-creator runs)

**Lessons learned:**
- For Launch-stage products, keyword indexing is more important than benefit copy in bullets
- Category cross-indexing means Amazon already associates the product with terms not in listing - adding them explicitly amplifies the signal
- Python open() is the most reliable file writing method when OneDrive EEXIST and Bash heredoc both fail
- Price premium ($19.98 vs $11.99 avg) must be justified through perceived value in bullets (gem stickers, counting practice, reusable box)

**Tokens/cost:** ~80K tokens, 0 Apify (shared session with audit)

---

### Run: 2026-03-06 (c)
**Product:** 10mm Big Fuse Beads (B07D6D95NG / O9-70DP-C5J6)
**Mode:** Rewrite based on Listing Optimizer audit (same session)
**Goals:**
- [x] Generate 3 title options with keyword placement rationale
- [x] Generate 5 recommended bullets with alternatives
- [x] Generate optimized backend keywords (~245/249 bytes)
- [ ] Upload to Notion (not requested)
- [ ] Push to Amazon (not requested - user reviewing options first)

**Result:** Success

**What worked:**
- Combined audit+creator in single session - very efficient
- All DataDive data (RJ, MKL 202 kw, Roots, Rank Radar 38 kw) fetched without failures
- No Apify needed - DataDive + context files sufficient
- Subagents parallelized large file analysis (MKL, Roots, Rank Radar) effectively
- Backend keywords expanded from 105 to ~245 bytes (+133%)

**What didn't work:**
- OneDrive EEXIST error with Write tool (workaround: Bash cat)

**Is this a repeat error?** Yes - OneDrive EEXIST (same as Run 2026-03-06 (b))

**Lessons learned:**
- Product has most room for improvement: 42% backend usage, 12% bullets RJ
- Iron beads (4.6K SV) completely missing from listing - easy high-impact add
- Kids missing from title despite ages 4-7 being there (Amazon indexes differently)
- Perler brand terms must go in backend only (trademark) but represent 159K+ broadSV
- Rating 4.1 is structural issue - listing can help but won't solve reviews

**Tokens/cost:** ~80K tokens, 0 Apify (shared session with audit)

**Post-run update (2026-03-06):** Listing rewrite pushed live to Amazon via SP-API update_listing. Submission ID: 54986da36c924c8d9607be42f969e546. Status: ACCEPTED. 3 fields updated (title Option A, 5 bullets with educational Bullet 5, backend keywords 248/249 bytes). SKU: O9-70DP-C5J6. Product type: ART_CRAFT_KIT. User replaced compatibility bullet with educational value bullet (LEARNING THROUGH PLAY). Backend trimmed from 261 to 248 bytes by removing "kindergarten" (covered by "preschool"). Portfolio tracker + agent-state updated.

---

### Run: 2026-03-06 (b)
**Product:** Cross Stitch Kit - Girls (B08DDJCQKF / CS01)
**Mode:** Rewrite based on Listing Optimizer audit (same session)
**Goals:**
- [x] Generate 3 title options with keyword placement rationale
- [x] Generate 5 recommended bullets with alternatives
- [x] Generate optimized backend keywords (246/249 bytes)
- [ ] Upload to Notion (not requested)
- [ ] Push to Amazon (not requested - user reviewing options first)

**Result:** Success

**What worked:**
- Combined audit+creator in single session - very efficient
- All DataDive data (RJ, MKL, Roots, Rank Radar) fetched without failures
- No Apify needed - context files + DataDive provided all keyword/competitor data
- Word-level gap analysis identified 6 missing high-impact words from title
- Risk assessment section added since this is the #1 product

**What didn't work:**
- Write tool EEXIST error when saving briefs (file system issue on OneDrive synced folder)
- Workaround: used Bash cat/touch to create files instead

**Is this a repeat error?** No

**Lessons learned:**
- For #1 ranked hero products, always include a risk assessment section
- OneDrive-synced folders may cause EEXIST errors with Write tool - use Bash as fallback
- Amazon SKU FH-FMO5-Y9LJ confirmed (not CS01)
- This product already had a previous audit (2026-02-23) - cross-reference for trend tracking
- Backend keywords had massive room (183 to 246 bytes = +34% more coverage)

**Tokens/cost:** ~70K tokens, 0 Apify (shared session with audit)

---

### Run: 2026-03-06
**Product:** 24K Mini Fuse Beads (B09THLVFZK / CC48)
**Mode:** Rewrite based on Listing Optimizer audit (same session)
**Goals:**
- [x] Generate 3 title options with anti-refund strategy
- [x] Generate 5 bullets with 8 anti-refund signals
- [x] Generate backend keywords (244/249 bytes)
- [ ] Upload to Notion (skipped — user didn't request)
- [x] Push to Amazon via SP-API

**Result:** Success

**What worked:**
- Combined audit+creator in single session — very efficient, no duplicate data fetching
- Anti-refund strategy: 8 natural signals across listing vs 1 all-caps warning
- "(NOT Standard 5mm)" in title is a pattern interrupt that educates before click
- SP-API push with product_type ART_CRAFT_KIT accepted (get_listing returned UNKNOWN)
- Backend keywords expanded from 182 to 244 bytes (+34%)

**What didn't work:**
1. Apify saswave~amazon-product-scraper failed x2 — no competitor bullet scraping
2. SKU CC48 not found in SP-API — real Amazon SKU is RV-FA22-4WFQ

**Is this a repeat error?** Yes — Apify failure (x2 in listing-optimizer)

**Lessons learned:**
- For products with refund issues, the listing must EDUCATE wrong buyers, not just warn them
- Size comparison (2.6mm vs 5mm = "half the size") is more effective than age warnings
- Mentioning pegboard incompatibility is a practical filter that parents understand
- Always check Seller Board for the actual Amazon SKU — internal SKUs may not match
- A+ content overrides description — always ask before writing/pushing description
- Product type ART_CRAFT_KIT works for shinshin creation fuse beads products too

**Tokens/cost:** ~80K tokens, $0 Apify (failed)

---

### Run: 2026-03-05
**Product:** My First Cross Stitch Kit for Kids (B0F6YTG1CH / UCE01)
**Mode:** Rewrite based on Listing Optimizer audit (same day)
**Goals:**
- [x] Generate 3 title options with keyword placement rationale
- [x] Generate 5 recommended bullets with alternatives for each
- [x] Generate description (full product description)
- [x] Generate backend keywords (201/249 bytes)
- [x] Upload to Notion under Product Listing Development
- [x] Save listing brief to outputs

**Result:** Success

**What worked:**
- Using the same-day listing-optimizer audit as input was extremely efficient — all keyword gaps, root coverage, and competitor data already analyzed
- No Apify cost — all competitor data from the audit run, no duplicate scraping
- Word-level coverage estimated to improve from 59% to ~90% with the new listing
- 10 previously missing words now covered across title, bullets, and backend
- Notion upload successful (63 blocks, page ID: 31a57318-d05c-812e-9b3f-f9ac63604092)
- Full description generated with keyword-rich content and complete kit contents list

**What didn't work:**
- Nothing — clean run. The audit-first approach makes listing creation straightforward.

**Is this a repeat error?** No

**Lessons learned:**
- Same-day audit -> listing creator is the ideal workflow. Audit identifies exactly what's wrong, creator fixes it.
- When product not tracked in DataDive (no Ranking Juice), word-level analysis from audit still provides clear rewrite direction
- Including individual age numbers (6, 7, 8, 9, 10, 11, 12) in bullet 3 helps index for "ages 8-12" type searches where we're missing standalone "8"
- Description should cover ALL keyword roots since Amazon indexes description text too

**Tokens/cost:** ~25K tokens, $0 Apify (used audit data)

**Post-run update (2026-03-05):** Listing rewrite pushed live to Amazon via SP-API `update_listing`. Submission ID: 040c70871fad4befb88e67d8b39c034b. Status: ACCEPTED. All 4 fields updated (title, 5 bullets, description, backend keywords 201/249 bytes). SKU: `75-24RO-YAXR`. Product type: `ART_CRAFT_KIT` (get_listing returned "UNKNOWN" but ART_CRAFT_KIT was accepted — same as EK17). Asana verification task created (due 2026-03-06).

---

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

**Result:** Success

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

## Listing Manager

### Run: 2026-03-10
**Mode:** OPTIMIZE
**Product:** Needlepoint Wallet Kit Cat (B09HVDNFMR)
**Trigger:** User — post-PPC restructure to kids niche, CVR improvement needed
**Result:** Success

**What happened:**
- Audit completed: score 31/100. Critical gap = "beginner" entirely missing from listing (30,618 combined SV)
- Title restructured: "Pre Printed..." -> "Craftiloo Needlepoint Kit for Kids — Beginner..."
- All 5 bullets rewritten (Bullet 5 replaced return policy with gift angle)
- Backend expanded 82->247 bytes (+201%)
- Pushed to Amazon via SP-API: submission ae52f02381cb4aeca1edb75dd12b1c7d ACCEPTED

**What didn't work:**
- Backend keywords first attempt was 260 bytes (11 over limit). Removed "kindergarten" to fit at 247/249.

**Sub-skills called:**
- listing-optimizer: ran (audit data gathering — DataDive RJ, MKL, Roots, Rank Radar + SP-API get_listing)
- listing-creator: ran (rewrite generation — title options, 5 bullets, backend)
- image-planner: skipped — not requested
- listing-ab-analyzer: skipped — scheduled for 2026-03-31

**Is this a repeat error?** No

**Lesson learned:**
- When PPC strategy pivots to a niche (kids), the listing MUST match. Misalignment between PPC targeting and listing keywords causes rank decay.
- "Beginner" was the single highest-ROI word to add — 7 of top 10 SV keywords contain it, and rank trends confirmed: kid-terms improving (word present), beginner-terms declining (word absent).
- User wanted brand name "Craftiloo" at title start — this is a branding decision to apply across portfolio.
- Always count backend bytes before pushing — 249 limit is strict.

**Tokens/cost:** ~60K tokens, 0 Apify

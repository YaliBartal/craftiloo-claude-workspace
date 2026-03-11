---
name: negative-keyword-generator
description: Proactive negative keyword list generator using product knowledge and the Craftiloo catalogue
triggers:
  - generate negatives
  - negative keywords
  - negative keyword list
  - negative keyword generator
  - proactive negatives
  - build negative list
  - negate keywords
output_location: outputs/research/negative-keywords/
---

# Negative Keyword Generator

**USE WHEN** user says: "generate negatives", "negative keywords", "negative keyword list", "proactive negatives", "build negative list", "negate keywords", "negative keyword generator"

---

## ⚠️ BEFORE YOU START — Read Lessons

**MANDATORY FIRST STEP:** Read `LESSONS.md` in this skill's folder before doing anything else.

1. Read `.claude/skills/negative-keyword-generator/LESSONS.md`
2. Check **Known Issues** — plan around these
3. Check **Repeat Errors** — if you encounter one during this run, tell the user immediately: _"⚠️ Repeat issue (×N): [description]"_
4. Apply all past lessons to this run

**Do NOT skip this step.**

---

## What This Does

Generates a comprehensive, proactive negative keyword list for a specific portfolio's broad and auto campaigns. Instead of waiting for wasted spend (reactive), this skill uses **product knowledge** to predict and prevent irrelevant traffic before it happens.

**Core engine:** Analyzes what the product IS and ISN'T, cross-references the 76-product Craftiloo catalogue, and generates categorized negatives by type.

**Complements Weekly PPC Analysis:** That skill finds negatives from performance data (reactive). This skill generates negatives from product knowledge (proactive). Use both for complete coverage.

---

## Organization & Efficiency Standards

### File Organization

```
outputs/research/negative-keywords/
├── briefs/     # Negative keyword review lists + copy-paste output
├── data/       # Archived search term exports (if provided)
└── README.md   # Folder guide
```

### Naming Conventions

| File Type | Format | Example |
|-----------|--------|---------|
| Review briefs | `{portfolio-slug}-negatives-YYYY-MM-DD.md` | `cross-girl-negatives-2026-02-19.md` |
| Data archives | `{portfolio-slug}-st-export-YYYY-MM-DD.xlsx` | `cross-girl-st-export-2026-02-19.xlsx` |

### Efficiency Targets

- **< 80K tokens** per analysis
- **< 8 minutes** execution time (includes API report generation wait time)
- **No additional cost** — Amazon Ads API is free with approval; DataDive API has rate limits but no per-call cost

### Forbidden Practices

- Do NOT negate terms that appear in `context/search-terms.md` as tracked/target keywords
- Do NOT negate the product's own category terms or product title words
- Do NOT skip the review step — ALWAYS present the list for human approval before generating copy-paste output
- Do NOT auto-negate competitor brand names — flag for human decision
- Do NOT negate broad gift terms that could apply to any Craftiloo product (e.g., "craft kit for kids", "arts and crafts")
- **NEVER recommend pausing a campaign based on a single week of zero conversions.** Always check a longer timeframe (minimum 30 days, ideally 60 days) before recommending a pause. A campaign with zero orders in one week might just be in a rough patch.
- **NEVER use round/organized bid amounts** when recommending bid adjustments alongside negatives. Use slightly irregular amounts like -31%, -48%, -52%, -27% instead of clean -30%, -50%. This avoids predictable bid patterns in Amazon's auction dynamics.
- **NEVER negate a search term based on a single week of zero conversions.** Always check a minimum 30-day window of data before recommending a search term for negation. A search term with zero orders in one week might convert in other weeks. Only recommend negating if the search term shows sustained zero conversions AND is clearly irrelevant to the product over the full 30-day window.

---

## Input

### Required
1. **Portfolio/product selection** — Ask user which portfolio or product to generate negatives for
2. **Context files** (loaded automatically):
   - `context/products.md` — Full product catalogue with specs
   - `context/hero-products.md` — Hero products with ASINs
   - `context/business.md` — Brand info, categories, competitors, target audience
   - `context/search-terms.md` — PROTECTED keyword list (MUST NOT negate these)

### Automated (No User Action Needed)
3. **Search term data** — Pulled automatically from the **Amazon Ads API** in Step 0a (no manual CSV export needed)
4. **Campaign mapping** — Pulled automatically from the **Amazon Ads API** in Step 0b.5 (enables programmatic application)

### How to Start

When skill triggers:
1. Ask: **"Which portfolio or product should I generate negatives for?"**
   - If user doesn't know portfolio names, list the 17 active portfolios
2. Load context files
3. Run Step 0a (pull search term data from Ads API — automated)
4. Run Step 0b.5 (identify campaigns in portfolio — automated)
5. Run Step 0b (DataDive keyword data — optional enhancement)

---

## Process

### Step 0a: Pull Search Term Data from Amazon Ads API (Automated)

**PURPOSE:** Replace the manual CSV export with an automated pull from the Amazon Ads API. This gives you the same high-spend zero-order terms and high-ACoS terms that previously required a Seller Central export.

**How to fetch:**

1. **Create the search term report:**
   ```
   create_ads_report(
       report_type="sp_search_terms",
       date_range="LAST_30_DAYS",
       marketplace="US"
   )
   ```
   Save the returned `reportId`.

2. **Poll for completion:**
   ```
   get_ads_report_status(report_id="{reportId}", marketplace="US")
   ```
   Wait for `COMPLETED` status (typically 1-3 minutes). Poll every 30 seconds, max 10 times.

3. **Download to file** (search term reports are large — 3,000-5,000+ rows):
   ```
   download_ads_report(
       report_id="{reportId}",
       marketplace="US",
       save_to_file="outputs/research/negative-keywords/data/{portfolio-slug}-search-terms-{YYYY-MM-DD}.json"
   )
   ```
   This saves the full report to disk and returns a summary with row count + aggregate metrics.

4. **Read the saved file** and extract negative candidates:

   | Condition | Action | Priority |
   |-----------|--------|----------|
   | `cost >= 10` AND `purchases7d == 0` | Negative EXACT candidate | P1 |
   | `cost >= 5` AND `purchases7d == 0` AND `clickThroughRate < 0.003` | Negative EXACT candidate | P1 |
   | `cost >= 5` AND `purchases7d == 0` AND `clickThroughRate >= 0.003` | Negative EXACT candidate | P2 (review) |
   | ACoS > 100% AND `clicks >= 3` | Negative EXACT candidate | P1 |
   | ACoS > 3x portfolio target AND `clicks >= 5` | Negative EXACT candidate | P2 |

5. **Filter to the selected portfolio only:**
   - Match `campaignName` against the user's selected portfolio
   - If portfolio mapping is available (from `list_portfolios()`), filter by `portfolioId` in campaign data

6. **If API fails:** Fall back to the manual approach — ask user to provide a search term CSV/Excel file. Note: "Amazon Ads API unavailable — using manual search term data."

**This replaces the "Optional" search term report input.** The API pull happens automatically unless the API is unavailable.

### Step 0b.5: Identify Active Campaigns for This Portfolio

**PURPOSE:** Map exactly which campaigns belong to the selected portfolio so negatives can be applied to the right campaigns programmatically in Step 8.

1. **Fetch portfolio mapping:**
   ```
   list_portfolios(marketplace="US")
   ```
   Find the portfolioId matching the user's selected portfolio name.

2. **Fetch campaigns in this portfolio:**
   ```
   list_sp_campaigns(state="ENABLED", portfolio_id="{portfolioId}", marketplace="US")
   ```
   This returns all active campaigns in the portfolio with `campaignId`, `name`, `state`, and `budget`.

3. **For each campaign, fetch its ad groups:**
   ```
   list_sp_ad_groups(campaign_id="{campaignId}", state="ENABLED", marketplace="US")
   ```
   Save the `adGroupId` for each ad group — needed for ad-group-level negative application.

4. **Build a campaign map** for use in Step 8:
   ```
   Portfolio: {name} (portfolioId: {id})
   ├── Campaign: {name} (campaignId: {id})
   │   ├── Ad Group: {name} (adGroupId: {id})
   │   └── Ad Group: {name} (adGroupId: {id})
   ├── Campaign: {name} (campaignId: {id})
   │   └── Ad Group: {name} (adGroupId: {id})
   └── ...
   ```

5. **Fetch existing negatives** (for dedup in Step 8):
   ```
   list_sp_negative_keywords(campaign_id="{campaignId}", state="ENABLED", marketplace="US")
   list_sp_campaign_negative_keywords(campaign_id="{campaignId}", marketplace="US")
   ```
   Build a set of existing negative terms per campaign for dedup checking later.

6. **If API fails:** Note which campaigns/ad groups could not be fetched. Programmatic application (Step 8) will be unavailable — fall back to copy-paste output only.

**Show the user the campaign map** so they know exactly which campaigns will receive negatives.

### Step 0b: Fetch DataDive Keyword Data (Optional Enhancement)

**PURPOSE:** Use DataDive's Master Keyword List and Rank Radar to enhance negative keyword generation with search volume and relevancy data.

**API Details:**
- **Base URL:** `https://api.datadive.tools`
- **Auth:** Header `x-api-key` with value from `.env` → `DATADIVE_API_KEY`

**How to use:**

1. **Match the product's category to a DataDive niche:**
   - Call `GET /v1/niches?pageSize=50` to list all niches
   - Find the niche matching this product's category (by `heroKeyword` or `nicheLabel`)

2. **Fetch Master Keyword List:**
   ```
   GET /v1/niches/{nicheId}/keywords
   ```
   Returns per keyword: `keyword`, `searchVolume`, `relevancy`, `asinRanks` (organic), `sponsoredAsinRanks`

3. **Use the data for smarter negation decisions:**

   | DataDive Field | Use for Negation |
   |---------------|-----------------|
   | `relevancy = "Outlier"` | Keywords marked as outliers are low-relevancy — strong negative candidates if high search volume (would drive irrelevant traffic) |
   | `searchVolume` | Prioritize negating high-volume irrelevant terms (more wasted spend potential) |
   | `asinRanks` | If our ASIN ranks well on a keyword, do NOT negate it (even if it seems irrelevant — the market disagrees) |
   | `sponsoredAsinRanks` | If we're advertising on a keyword, flag it for review before negating |

4. **Fetch Keyword Roots (for root-level negation):**
   ```
   GET /v1/niches/{nicheId}/roots
   ```
   Returns root words with `frequency` and `broadSearchVolume`.
   - Roots with LOW frequency + LOW broadSearchVolume in the niche = likely irrelevant → negative phrase candidates
   - Roots with HIGH frequency = core niche terms → NEVER negate

5. **Add a new output section: "DataDive-Informed Negatives"**
   - List keywords from the Master Keyword List with `relevancy = "Outlier"` that are also NOT in our tracked search terms
   - These are keywords DataDive identified as irrelevant to the niche but that may still trigger our broad/auto campaigns

6. **If DataDive fetch fails:** Continue with existing product-knowledge-based approach. Note: "DataDive data unavailable — using product knowledge only."

### Step 0c: Brand Analytics SQP — Search Funnel Validation (Optional Enhancement)

**PURPOSE:** Use Amazon's Search Query Performance data to validate negative candidates with real impression/click/conversion data. SQP shows which search terms actually drive (or fail to drive) conversions for our ASINs — far more reliable than spend-based guessing alone.

**Cost:** $0 (Brand Analytics is free with Brand Registry)
**Time:** ~60 seconds (report creation + download)
**Tool:** `create_brand_analytics_report` (SP-API MCP)

**How to use:**

1. **Get the portfolio's hero ASINs** from `context/sku-asin-mapping.json` (match by portfolio name)

2. **Create the SQP report:**
   ```
   create_brand_analytics_report(
       report_name="sqp",
       period="WEEK",
       periods_back=2,
       marketplace="US",
       asins="B09WQSBZY7 B096MYBLS1"
   )
   ```
   **Note:** Use `periods_back=2` on Sunday/Monday (48h SLA). ASINs are space-separated, max 200 chars.

3. **Poll + download** (same as other BA reports — poll every 15s, max 8 times)

4. **Use the data for smarter negation decisions:**

   | SQP Metric | Use for Negation |
   |------------|-----------------|
   | High impressions + 0 clicks + 0 purchases | **Auto-negate candidate** — Amazon is showing us but shoppers aren't interested. Product/search mismatch. |
   | High impressions + some clicks + 0 purchases | **Strong negate candidate** — shoppers click but don't buy. Wrong audience or product mismatch. |
   | Low impressions + 0 everything | Ignore — too little data to act on |
   | Any purchases > 0 | **NEVER negate** — this term converts, regardless of what the product profile says |

5. **Add SQP-informed negatives to Category 7: "Brand Analytics Negatives"**
   - List search terms from SQP where our ASIN received 50+ impressions but 0 purchases over the reporting period
   - Cross-reference with Category 6 (spend-based negatives) — terms appearing in BOTH are highest confidence
   - Terms in SQP with purchases > 0 that appear in other negative categories → **remove from negatives and flag as [BA PROTECTED]**

6. **If SQP fails:** Continue with existing approach. Note: "Brand Analytics SQP unavailable — using spend data and product knowledge only."

**This step runs after Step 0a (search term pull) and before Step 1 (product intelligence).** The SQP data enriches the negation decisions made in later steps.

### Step 1: Gather Product Intelligence

1. **Identify the product(s)** from user's portfolio selection
2. **Load product details** from `context/products.md`:
   - Product name, SKU, category
   - Kit contents (materials, tools, components)
   - What the product MAKES (keychains, pillows, wallets, figures, etc.)
3. **Load hero product details** from `context/hero-products.md` (if applicable):
   - ASIN, brand on Amazon, key selling points, age range
4. **Load protected terms** from `context/search-terms.md`:
   - All tracked keywords for this product's category
   - All tracked keywords for closely related categories
   - These are NEVER negated
5. **Load business context** from `context/business.md`:
   - Target audience (grandparents/parents buying for kids 6-12)
   - Shinshin Creations targets adults
   - Competitor list
6. **From search term data (Step 0a)**, extract:
   - Terms with $5+ spend and 0 orders → candidate negative exacts
   - Terms with ACoS > 100% → candidate negative exacts
   - These were already identified in Step 0a — carry them forward into Category 6

### Step 2: Build Product Profile

Create this profile and show it to the user:

| Attribute | Value |
|-----------|-------|
| **Product IS** | {craft type}, {kit type}, {what it makes} |
| **Target age** | {age range from hero-products.md or products.md} |
| **Target buyer** | Grandparents/parents (gift purchasers) — or Adults for Shinshin |
| **Target user** | {end user: girls 6-12, adults, etc.} |
| **Category** | {primary craft category} |
| **Materials in kit** | {list key materials from products.md} |
| **Product makes** | {finished items: keychains, pillows, figures, etc.} |
| **Product is NOT** | {list other craft types, other product types} |
| **Brand on Amazon** | CRAFTILOO or shinshin creation |

### Step 3: Generate Categorized Negatives

Apply the negative keyword categories below systematically.

### Step 4: Safety Cross-Reference

Before presenting the list, check every generated term against:

1. **`context/search-terms.md`** — Remove ANY term that appears as a tracked keyword in ANY category (even partial matches — e.g., if "latch hook kits for kids" is tracked, do not negate "latch hook")
2. **Product title/listing words** — Remove terms that appear in the product's own name or description
3. **Own category terms** — NEVER negate the product's primary craft type (e.g., never negate "embroidery" for an embroidery product)
4. **Cross-category check** — Cross stitch and embroidery share significant audience overlap. Do NOT auto-negate one from the other unless user explicitly requests it
5. **Barbie check** — If this IS a Barbie product, preserve all Barbie-related terms. If NOT, consider adding "barbie" as a negative
6. **Shinshin check** — Fuse bead products target ADULTS. Do NOT negate "adult" terms for fuse beads
7. **DataDive rank check** — If DataDive data was fetched (Step 0b), check `asinRanks` for our ASIN on each keyword. If we rank organically on a keyword, do NOT negate it — the market considers it relevant even if it seems off. Flag as [REVIEW] instead.
8. **Brand Analytics conversion check** — If SQP data was fetched (Step 0c), check if any NEGATE candidate has `purchases > 0` in SQP. If so, **remove from negatives** and flag as **[BA PROTECTED]** — Amazon's own data confirms this term converts for our product. This overrides all other signals.

Flag any borderline terms with **[REVIEW]** marker.

### Step 5: Present Review List

Display the full categorized list to the user in the review format (see Output Format section).

**This step is MANDATORY.** Tell the user:
- "Review each category. Remove any terms you want to keep targeting."
- "Add any terms I missed."
- "Change match types if needed (phrase ↔ exact)."

### Step 6: User Reviews & Adjusts

Wait for user feedback. Process their changes:
- Remove terms they flag
- Add terms they suggest
- Adjust match types as requested

### Step 7: Generate Copy-Paste Output

After user approval, generate two clean lists:

1. **Negative Phrase terms** — One per line, no bullets, no formatting. Ready to paste into Seller Central.
2. **Negative Exact terms** — One per line, same format.

Save the full brief (review + copy-paste) to the output location.

---

## Negative Keyword Categories

### Category 1: Wrong Craft Types (Negative PHRASE)

The most impactful category. Negate all craft types that this product is NOT.

**Master Craft-to-Negative Mapping:**

| If product IS... | Negate these as PHRASE |
|------------------|----------------------|
| **Cross Stitch** | crochet, quilting, weaving, macrame, diamond painting, diamond art, paint by number, pottery, clay, slime, tie dye, scrapbook, origami, jewelry making |
| **Embroidery** | crochet, quilting, weaving, macrame, diamond painting, diamond art, paint by number, pottery, clay, slime, tie dye, scrapbook, origami, jewelry making |
| **Sewing (felt kits)** | crochet, quilting, weaving, macrame, diamond painting, diamond art, paint by number, pottery, clay, slime, tie dye, sewing machine, scrapbook, origami, jewelry making |
| **Latch Hook** | crochet, quilting, weaving, macrame, diamond painting, diamond art, paint by number, pottery, clay, slime, tie dye, scrapbook, origami, jewelry making |
| **Needlepoint** | crochet, quilting, weaving, macrame, diamond painting, diamond art, paint by number, pottery, clay, slime, tie dye, scrapbook, origami, jewelry making |
| **Loom Knitting** | crochet hook, quilting, weaving, macrame, diamond painting, diamond art, paint by number, pottery, clay, slime, tie dye, scrapbook, origami, jewelry making |
| **Punch Needle** | crochet, quilting, weaving, macrame, diamond painting, diamond art, paint by number, pottery, clay, slime, tie dye, scrapbook, origami, jewelry making |
| **Lacing Cards** | crochet, knitting, quilting, weaving, macrame, diamond painting, diamond art, paint by number, pottery, clay, slime, tie dye, embroidery, cross stitch, latch hook, scrapbook, origami, jewelry making |
| **Fuse Beads** | crochet, knitting, sewing, embroidery, cross stitch, latch hook, quilting, weaving, macrame, diamond painting, paint by number, pottery, clay, slime, tie dye, needlepoint, scrapbook, origami |

**Within-Craftiloo-family negation rules:**

| If product IS... | Also negate from own sewing family |
|------------------|-----------------------------------|
| Cross Stitch | latch hook, locker hooking, punch needle, loom knitting |
| Embroidery | latch hook, locker hooking, loom knitting |
| Sewing (felt) | latch hook, loom knitting, punch needle |
| Latch Hook | punch needle |
| Loom Knitting | latch hook, punch needle |
| Punch Needle | latch hook, loom knitting |

**IMPORTANT EXCEPTIONS:**
- Cross stitch and embroidery share significant audience overlap → Do NOT auto-negate one from the other
- "Knitting" as a broad term → Only negate for categories that clearly don't involve yarn/knitting (e.g., lacing cards, fuse beads)
- "Sewing" as a broad term → Do NOT negate for cross stitch or embroidery (customers often use "sewing" loosely for all needle crafts)

### Category 2: Wrong Product Types Within Craft (Negative PHRASE)

Negate product formats that share category terms but are completely different products.

| Craft Category | Negate These Product Types |
|----------------|---------------------------|
| **ANY sewing kit** | sewing machine, serger, overlock, rotary cutter, fabric bolt, pattern paper, dress form, mannequin, seam ripper, bobbin, sewing table |
| **ANY embroidery kit** | embroidery machine, machine embroidery, digitizing, embroidery software, stabilizer, embroidery thread cone |
| **ANY cross stitch kit** | counted cross stitch fabric only, aida cloth only, cross stitch frame stand |
| **ANY latch hook kit** | latch hook canvas only, latch hook tool only, rug hooking frame |
| **ANY fuse beads kit** | bead loom, seed beads, jewelry beads, pony beads, letter beads, water beads, orbeez |
| **ANY knitting kit** | knitting needles only, yarn only, knitting machine, circular needles, knitting gauge |
| **ANY lacing cards** | shoe laces, boot laces, shoelace |
| **ANY needlepoint kit** | needlepoint canvas only, tapestry frame, needlepoint stand |

### Category 3: Wrong Age Groups (Negative PHRASE)

| Product Age Range | Negate These |
|-------------------|-------------|
| **Ages 3-5** (lacing cards) | adult, senior, elderly, professional |
| **Ages 5-12** (most Craftiloo kits) | toddler, baby, infant, 18 month |
| **Ages 8+** (complex kits) | toddler, baby, infant, 18 month, preschool, pre-k |
| **Ages 10+** (mini fuse beads) | toddler, baby, infant, preschool, pre-k |
| **Adults** (Shinshin fuse beads 2.6mm) | toddler, baby, infant, preschool |

**IMPORTANT:**
- Do NOT negate "adult" for Shinshin Creations fuse beads — those target adults
- Do NOT negate "adult" for embroidery kits that target teens/adults (e.g., 4 Flowers EK17)
- Do NOT negate "toddler" for lacing cards — those DO target ages 3+, and "toddler sewing" is a tracked keyword
- Always check `context/search-terms.md` — "toddler sewing kits ages 2-4" is a tracked term for lacing cards

### Category 4: Wrong Intent (Negative PHRASE)

These terms indicate the searcher wants something other than a physical product kit:

| Intent Type | Negate Terms |
|-------------|-------------|
| **Digital/free** | free pattern, free download, printable pattern, digital pattern, pdf pattern, ebook, e-book |
| **Education only** | online class, virtual class, workshop registration, course enrollment |
| **Professional/commercial** | wholesale, bulk order, commercial, industrial, professional grade, resale, retail lot |
| **Used/rental** | used, secondhand, second hand, rental |
| **Repair/parts** | replacement parts only, repair kit, spare parts, refill only |

**IMPORTANT:** Do NOT negate these terms broadly:
- "pattern" alone — Craftiloo products ARE patterns/kits
- "tutorial" / "instructions" — Customers expect kits with instructions
- "beginner" / "easy" — These are valuable for Craftiloo
- "free" alone — Only negate "free pattern", "free download", etc.
- "bulk" alone — Fuse bead customers search "fuse beads bulk"

### Category 5: Specific Irrelevant Products (Negative EXACT)

Generate based on specific product analysis. Examples by category:

| If product is... | Consider negating (EXACT) |
|------------------|--------------------------|
| Cross stitch keychain kit | cross stitch wall art, cross stitch sampler, cross stitch bookmark |
| Sewing felt figures | sewing apron, sewing tote bag, sewing organizer |
| Latch hook pillow | latch hook rug, latch hook wall hanging |
| Fuse beads kit | perler bead refill, pegboard only |
| Lacing cards | flash cards, alphabet cards, math cards |

**Always generate these based on the specific product — not generic lists.**

### Category 6: High-Spend Zero-Order Terms (Negative EXACT) — FROM ADS API

**From the search term data pulled in Step 0a** (or manual CSV fallback if API unavailable):

| Condition | Action |
|-----------|--------|
| **$10+ spend, 0 orders** | Negative EXACT (P1 — negate immediately) |
| **$5-10 spend, 0 orders, CTR < 0.3%** | Negative EXACT (P1) |
| **$5-10 spend, 0 orders, CTR > 0.3%** | Negative EXACT (P2 — flag for review) |
| **ACoS > 100%, 3+ clicks** | Negative EXACT (P1) |

### Category 6b: Brand Analytics Negatives (Negative EXACT) — FROM SQP DATA

**From the SQP data pulled in Step 0c** (skip if SQP was unavailable):

| SQP Pattern | Action | Confidence |
|-------------|--------|------------|
| **50+ impressions, 0 purchases** over reporting period | Negative EXACT candidate | **High** if also in Category 6 |
| **100+ impressions, clicks > 0, 0 purchases** | Negative EXACT candidate | **Very High** — shoppers see us, click, but never buy |
| **Any purchases > 0** in SQP data | **REMOVE from all other categories** — BA says this term converts | Override |

**Key advantage:** Category 6 relies on PPC spend data (only shows terms we're PAYING for). SQP shows ALL search terms where our product appeared organically — catching irrelevant terms we didn't even know about.

**Cross-reference rule:** Terms that appear in BOTH Category 6 (high spend, 0 orders) AND Category 6b (high impressions, 0 purchases) are the **highest confidence negatives**. Mark these as **[BA+PPC CONFIRMED]**.

**Override rule:** If SQP shows a term has purchases > 0 but Category 6 flagged it as a negate (maybe orders came organically, not via PPC), **remove it from negatives** and flag as **[BA PROTECTED]** — the product genuinely converts on this term.

### Category 7: Cross-Portfolio Terms (Negative EXACT) — NICE TO HAVE

When analyzing a specific portfolio, identify terms that clearly belong to OTHER Craftiloo portfolios:

| If analyzing... | Consider negating terms for... |
|-----------------|-------------------------------|
| Cross Stitch portfolio | "fairy sewing kit", "latch hook pillow", "fuse beads kit" |
| Sewing portfolio | "cross stitch keychain", "latch hook pencil case", "embroidery hoop kit" |
| Fuse Beads portfolio | "sewing kit for kids", "embroidery kit", "latch hook" |

**Rules for cross-portfolio negatives:**
- Only negate **specific product terms**, not broad category terms
- Always mark with **[REVIEW]** — cannibalization may be acceptable
- Do NOT negate terms that are broadly relevant to multiple products

### Category 8: Color/Attribute Modifiers (Negative PHRASE — CONDITIONAL)

Color and attribute terms that indicate the searcher wants a **specific single-color item**, not a multi-color craft kit. These are from the TitanOS "Never KWs" methodology.

**Master Color Modifier List (70 terms):**

amethyst, ash, beige, black, blue, blush, bronze, brown, caramel, cerulean, charcoal, clear, cobalt, coffee, copper, coral, cream, creme, cyan, ebony, egg shell, eggplant, fuchsia, gold, graphite, gray, green, grey, hazel, hot pink, indigo, iron, ivory, lapis, lavendar, lilac, lime, magenta, maroon, mauve, metallic, mint, navy, nickel, onyx, orange, peach, pearl, periwinkle, pewter, red, rose, rust, sage, sand, sapphire, seafoam, silver, sky, slate, smoke, snow, tan, tawny, teal, turquoise, violet, walnut, white, yellow

**CRITICAL — Apply per-product logic before negating:**

| Product Type | Color Negation Rule |
|-------------|---------------------|
| **Fuse Beads (any)** | **DO NOT negate colors.** Fuse bead kits ARE multi-color products. Customers search "blue fuse beads", "red perler beads" for specific color refills. Also "iron" is a tracked keyword ("iron beads"). |
| **Latch Hook kits** | Negate most colors EXCEPT those in the product design (e.g., if kit makes a rainbow unicorn, keep "pink", "purple", "white") |
| **Cross Stitch kits** | Negate most colors — customers search by design theme, not thread color |
| **Embroidery kits** | Negate most colors — same logic as cross stitch |
| **Sewing kits (felt)** | Negate most colors — customers search by character/theme, not felt color |
| **Lacing Cards** | Negate most colors — product is multi-color by nature |

**Per-product exceptions to always check:**
- "iron" → NEVER negate for fuse beads (tracked keyword: "iron beads")
- "gold", "silver" → May indicate material preference, not just color. Flag as [REVIEW] for jewelry-adjacent categories
- "clear" → May mean transparent/see-through for some products. Flag as [REVIEW]
- Colors that match the product's design theme → DO NOT negate (e.g., "pink" for a pink fairy cross stitch kit)

### Category 9: Competitor Brands (Negative EXACT — HUMAN REVIEW REQUIRED)

Competitor brand names from TitanOS research. These are ALWAYS flagged for human decision, NEVER auto-negated.

**Known Craftiloo Competitors (from TitanOS + business.md):**

| # | Brand | Category Focus |
|---|-------|---------------|
| 1 | Kraftlab | Craft kits |
| 2 | Fanzbo | Craft kits |
| 3 | Krafun | Craft kits |
| 4 | Azerka | Craft kits |
| 5 | KLUTZ | Craft kits |
| 6 | Melissa and Doug | Kids crafts |
| 7 | Creativity for Kids | Kids crafts |
| 8 | Latch Kits | Latch hook |
| 9 | EZCRA | Gem art/sticker |
| 10 | AHCo. | Craft supplies |
| 11 | VGOODALL | Craft supplies |
| 12 | Hapinest | Kids crafts |
| 13 | READAEER | Craft supplies |
| 14 | UCDRMA | Craft supplies |
| 15 | Katech | Craft supplies |
| 16 | BeKnitting | Knitting kits |
| 17 | PREBOX | Craft kits |
| 18 | QXHOL | Craft supplies |
| 19 | Coopay | Craft supplies |
| 20 | Aeelike | Craft supplies |
| 21 | IQKidz | Kids crafts |
| 22 | Olikraft | Craft kits |
| 23 | Frola | Craft supplies |
| 24 | Made By Me | Kids crafts |
| 25 | WONVOC | Craft supplies |
| 26 | FLYOUTH | Craft supplies |
| 27 | novelinks | Craft supplies |
| 28 | AUTHENTIC KNITTING BOARD | Knitting |
| 29 | cureder | Craft supplies |
| 30 | Mira HandCrafts | Yarn/crafts |
| 31 | YGSEPCC | Craft supplies |
| 32 | The Woobles | Crochet kits |
| 33 | SNOUUOSN | Craft supplies |
| 34 | S & E TEACHER'S EDITION | Education crafts |
| 35 | JAPCHET | Craft supplies |
| 36 | Tatahu | Craft supplies |
| 37 | Granny Squirrel | Craft kits |
| 38 | WAYION | Craft supplies |
| 39 | FUNiOi | Kids crafts |
| 40 | Hobbspring | Craft kits |
| 41 | HIERYQHE | Craft supplies |
| 42 | Minatee | Craft supplies |
| 43 | WaldyWop | Craft kits |
| 44 | NBEADS | Beading supplies |
| 45 | WodGod | Craft supplies |
| 46 | PKHOUHYI | Craft supplies |
| 47 | Boye | Knitting/crochet |
| 48 | MAHITOI | Craft supplies |
| 49 | Disracker | Craft supplies |
| 50 | SAYHALO | Craft supplies |
| 51 | Yuhoo | Craft supplies |
| 52 | Thyle | Craft supplies |
| 53 | Andgiv | Craft supplies |
| 54 | BOLDNOVA | Craft supplies |
| 55 | CYCHIRV | Craft supplies |
| 56 | Crochetta | Crochet kits |
| 57 | ULIONTAC | Craft supplies |

**Competitor ASINs (72 known):**

B08YS42GPG, B0CCN877BL, B0B5RBBGC9, B09C1KQG2J, B0CZF266QH, B0B7JF9FW2, B0C2XYP6L3, B07PPD8Q8V, B0CL22LLSY, B08CVSB189, B0DF7Q6P5J, B0BMFV811F, B0D9NSPBSS, B0DG7VK3HX, B0CN8Z1XKM, B0D4V9B9SH, B0D45DCDWJ, B0CND45Y4Z, B08BC56MQ8, B0D5QZ5CZF, B0CB6WDB7S, B09GK6WQQ1, B0CKQZ3BRV, B0D26CVQSH, B08C7SWHY7, B00ZSE93LA, B0CHVF4VFX, B09X55KL2C, B0DP5N76G4, B0D9WH15DW, B0BPJBTXN7, B096Z5MCHJ, B07HBGHS5W, B0CYG4676W, B0CWDZ3Y7T, B0BZP4FRMR, B0DPLZWBZL, B0DHH1QBYN, B0DJRLQDHH, B0DN1ZG6Q7, B001TC0UGC, B0DJFZLJFL, B0CJXQTM35, B096N2Q2YV, B0B8W4FK4Q, B08FYH13CL, B0D9XZGP79, B0C74JCL87, B0DMSQQSPY, B0DFPYD2RW, B0C689CVY4, B0BNH7FLJC, B0DKD2S3JT, B0CZ9MDYQ3, B0CQHL4R7X, B0D9L9XWGV, B00JYGPLUK, B0DKX5G74Q, B0DCHB6CLJ, B0CZDGNM8L, B09Q63J9RV, B0DK2V2D83, B0CKGYD2ZF, B0CHBF4RR3, B0DT72GZXP, B0DS7TGGC2, B08CZQ3ZMY, B08Y1W2JMJ, B0F1MFR5KN, B0DBZHG3KD, B0BNK1HSXL, B09DTHQH3Q

**Rules for competitor brand negation:**
- **NEVER auto-negate** — always present for human review
- Brand-name searches often have decent conversion if your product is competitive
- Only negate competitor brands if search term data shows high spend + zero orders for that brand
- **NEVER negate Perler or Hama** — these are category names for fuse beads, not just brands
- **NEVER negate CRAFTILOO or shinshin creation** — own brands
- Consider negating brands from unrelated categories (e.g., "The Woobles" for fuse beads — they're crochet only)

---

## Output Format

### Review Brief Format

```markdown
# Negative Keyword Review: {Portfolio/Product Name}

**Date:** {YYYY-MM-DD}
**Product:** {Product name} ({SKU})
**Category:** {Primary category}
**Target Age:** {Age range}
**Search Term Report:** {Included / Not included}

---

## Product Profile

| Attribute | Value |
|-----------|-------|
| Product IS | {description} |
| Product is NOT | {what it excludes} |
| Target buyer | {buyer persona} |
| Target user | {end user} |
| Materials in kit | {key materials} |
| Product makes | {finished items} |

---

## Negative PHRASE Candidates

### Wrong Craft Types
> These are entirely different craft categories. Searchers for these will never buy this product.

| # | Term | Why Negate |
|---|------|-----------|
| 1 | crochet | Product is {craft type}, not crochet |
| 2 | ... | ... |

### Wrong Product Types
> These share category words but are completely different products.

| # | Term | Why Negate |
|---|------|-----------|
| 1 | sewing machine | Product is a hand-sewing kit, not a machine |
| 2 | ... | ... |

### Wrong Age Groups
> Searchers looking for different age groups than this product serves.

| # | Term | Why Negate |
|---|------|-----------|
| 1 | toddler | Product is for ages 8+ |
| 2 | ... | ... |

### Wrong Intent
> Searchers looking for digital content, tutorials, or non-product results.

| # | Term | Why Negate |
|---|------|-----------|
| 1 | free pattern | Indicates free content seeker |
| 2 | ... | ... |

---

## Negative EXACT Candidates

### Specific Irrelevant Terms
| # | Term | Why Negate |
|---|------|-----------|
| 1 | {specific term} | {reason} |

### High-Spend Zero-Order Terms (from search term report)
*Only if search term report was provided*

| # | Term | Spend | Clicks | Orders | Why Negate |
|---|------|-------|--------|--------|-----------|
| 1 | {term} | ${X} | X | 0 | Spent ${X} with zero return |

### Cross-Portfolio Terms [REVIEW]
| # | Term | Belongs To | Why Consider |
|---|------|-----------|-------------|
| 1 | {term} | {other portfolio} | Prevents cannibalization |

### DataDive Outlier Keywords (Low Relevancy, High Volume)
> Keywords DataDive flagged as "Outlier" relevancy in the Master Keyword List — likely irrelevant to the niche but may trigger broad/auto campaigns. Prioritized by search volume.
> *Only included if DataDive data was successfully fetched.*

| # | Term | Search Volume | Relevancy | Our Rank | Why Consider Negating |
|---|------|-------------|-----------|----------|----------------------|
| 1 | {keyword} | {sv} | Outlier | {rank or "Not ranked"} | High volume irrelevant term — wasted ad spend risk |

### Color/Attribute Modifiers
> Color terms that indicate searcher wants a specific single-color item.
> **Conditional** — skip this section if product IS multi-color (e.g., fuse beads).

| # | Term | Why Negate |
|---|------|-----------|
| 1 | {color} | Product is multi-design kit, not single-color item |

### Competitor Brand Terms (Human Decision Required)

| # | Brand | Recommendation |
|---|-------|----------------|
| 1 | {brand} | {Keep if converting / Negate if high spend + 0 orders} |

---

## Flagged for Review [BORDERLINE]

| # | Term | Match Type | Concern |
|---|------|-----------|---------|
| 1 | {term} | {phrase/exact} | {why it's borderline} |

---

## Safety Check Results

| Check | Status |
|-------|--------|
| Cross-referenced against search-terms.md | ✅ {X} tracked terms checked |
| Product title terms excluded | ✅ No title terms negated |
| Own category terms preserved | ✅ {category} terms preserved |
| DataDive rank check | ✅ No keywords where we rank organically were negated / ⚠️ DataDive unavailable |
| DataDive outlier keywords included | ✅ {X} outlier terms added / ⚠️ DataDive unavailable |
| Competitor brands flagged separately | ✅ Listed below for your decision |

---

## Competitor Brand Terms (Human Decision Required)

| # | Brand | Recommendation |
|---|-------|----------------|
| 1 | {brand} | {Keep if your product shows for these / Negate if low CVR} |

---

## Summary

| Category | Negative Phrase | Negative Exact | Flagged |
|----------|----------------|----------------|---------|
| Wrong craft types | X | — | X |
| Wrong product types | X | — | X |
| Wrong age groups | X | — | X |
| Wrong intent | X | — | X |
| Specific irrelevant | — | X | X |
| High-spend zero-order | — | X | X |
| Cross-portfolio | — | X | X |
| DataDive outlier keywords | X | X | X |
| Color/attribute modifiers | X | — | X |
| Competitor brands | — | X | X |
| **TOTAL** | **X** | **X** | **X** |

---

**REVIEW THIS LIST.** Tell me:
1. Terms to remove
2. Terms to add
3. Match type changes (phrase ↔ exact)
4. Approve or reject borderline terms

When ready, say **"approved"** or **"generate"** and I'll produce the copy-paste output.
```

### Copy-Paste Output Format (after approval)

After user says "approved" or "generate":

```markdown
---

## COPY-PASTE: Negative Phrase Keywords

Paste into Seller Central → Campaign → Negative Targeting → Add Negative Keywords → Negative Phrase:

{one term per line, no bullets, no formatting, no numbers — raw text ready to paste}

---

## COPY-PASTE: Negative Exact Keywords

Paste into Seller Central → Campaign → Negative Targeting → Add Negative Keywords → Negative Exact:

{one term per line, no bullets, no formatting, no numbers — raw text ready to paste}
```

---

## Output Location

Save the complete brief (review + copy-paste) to:
`outputs/research/negative-keywords/briefs/{portfolio-slug}-negatives-YYYY-MM-DD.md`

If a search term file was provided, archive it to:
`outputs/research/negative-keywords/data/{portfolio-slug}-st-export-YYYY-MM-DD.xlsx`

---

## Step 8: Programmatic Application via Amazon Ads API

**CRITICAL: This entire step requires explicit user confirmation at every stage. NEVER auto-apply.**

After the user has reviewed and approved the negative keyword list (Steps 6-7), offer programmatic application.

### 8a. Present Application Plan

Present a clear summary of what will be applied:

```
## Application Plan

**Portfolio:** {portfolio name}
**Campaigns:** {N campaigns}
**Total negatives to apply:** {count}

### Campaign-Level Negatives (apply to ALL ad groups in campaign)
| Campaign | Negative Term | Match Type |
|----------|--------------|------------|
| ... | ... | NEGATIVE_EXACT / NEGATIVE_PHRASE |

### Ad-Group-Level Negatives (apply to SPECIFIC ad groups only)
| Campaign | Ad Group | Negative Term | Match Type |
|----------|----------|--------------|------------|
| ... | ... | ... | NEGATIVE_EXACT / NEGATIVE_PHRASE |

⚠️ Please confirm: Apply these {N} negatives? (yes/no)
```

**Default behavior:** Apply all negatives at **campaign level** (broader protection). Only use ad-group level if the user specifically requests it or if a negative is only relevant to certain ad groups.

### 8b. Dedup Check

Before applying, check for existing negatives to avoid duplicates:

1. **Campaign-level negatives:** Already fetched in Step 0b.5 via `list_sp_campaign_negative_keywords()`
2. **Ad-group-level negatives:** Already fetched in Step 0b.5 via `list_sp_negative_keywords()`
3. **Compare:** For each proposed negative, check if it already exists (same keyword text + same match type + same campaign/ad group)
4. **Report duplicates:** "Skipping {N} negatives that already exist: {list}"
5. **Only apply net-new negatives**

### 8c. Execute Application

After user confirms:

**For campaign-level negatives:**
```
create_sp_campaign_negative_keywords(
    campaign_id="{campaign_id}",
    keywords=[
        {"keywordText": "{term}", "matchType": "NEGATIVE_EXACT", "state": "ENABLED"},
        {"keywordText": "{term}", "matchType": "NEGATIVE_PHRASE", "state": "ENABLED"},
        ...
    ],
    marketplace="US"
)
```

**For ad-group-level negatives:**
```
manage_sp_negative_keywords(
    action="create",
    keywords=[
        {"campaignId": "{id}", "adGroupId": "{id}", "keywordText": "{term}", "matchType": "NEGATIVE_EXACT", "state": "ENABLED"},
        ...
    ],
    marketplace="US"
)
```

**Batch size:** Send up to 100 keywords per API call. If more than 100, batch into multiple calls.

### 8d. Report Results

After application, present a results summary:

```
## Application Results

✅ Successfully applied: {N} negatives
❌ Failed: {N} negatives
⏭️ Skipped (duplicates): {N} negatives

### Failures (if any)
| Term | Campaign | Error |
|------|----------|-------|
| ... | ... | ... |

### Applied Summary
| Campaign | Campaign-Level Added | Ad-Group-Level Added |
|----------|---------------------|---------------------|
| ... | ... | ... |
```

Save the application audit log to:
`outputs/research/negative-keywords/data/{portfolio-slug}-applied-YYYY-MM-DD.json`

### 8e. Error Handling

| Error | Response |
|-------|----------|
| API returns 400 (bad request) | Check keyword format — remove special chars, validate matchType |
| API returns 429 (throttled) | Wait 5 seconds and retry once. If still failing, save remaining to file for manual application |
| Partial failure (some succeed, some fail) | Report successes, retry failed once, then save remaining to file |
| User declines application | Save the approved list to file for later manual application. Provide copy-paste format as fallback |
| Campaign not found (ID mismatch) | Re-fetch campaign list, try matching by name. If still failing, flag to user |

---

## Execution Checklist

Before delivering the review list, verify:

**Data Gathering (Steps 0a-0b.5):**
- [ ] Search term report pulled from Ads API (30-day, saved to file)
- [ ] Active campaigns identified for this portfolio (campaigns + ad groups + existing negatives)
- [ ] Dedup baseline loaded (existing campaign-level + ad-group-level negatives)

**Negative Generation (Steps 1-5):**
- [ ] Product profile is accurate (correct SKU, category, age range, contents)
- [ ] All negative categories generated (craft types, product types, age, intent, specifics, color modifiers, competitor brands)
- [ ] Every term cross-referenced against `context/search-terms.md` — no protected terms negated
- [ ] Product's own category terms are NOT negated
- [ ] Product title words are NOT negated
- [ ] Barbie terms handled correctly (preserved on Barbie products, consider negating on non-Barbie)
- [ ] Shinshin/fuse beads age targeting correct (adults for mini beads, kids for biggie beads)
- [ ] Color/attribute modifiers evaluated per-product (skipped for multi-color products like fuse beads)
- [ ] Competitor brand terms flagged separately for human decision (not auto-negated)
- [ ] Borderline terms clearly marked with [REVIEW]
- [ ] Match types correct (phrase for categories, exact for specific terms)
- [ ] Safety check results included

**Review & Delivery (Steps 6-7):**
- [ ] Review step presented — NOT skipping to copy-paste
- [ ] After approval, copy-paste lists are clean (one term per line, no formatting)
- [ ] Brief saved to correct output location

**Programmatic Application (Step 8 — only if user opts in):**
- [ ] Application plan presented with full term list, campaigns, and match types
- [ ] User explicitly confirmed application (never auto-apply)
- [ ] Dedup check completed — existing negatives skipped
- [ ] API calls batched (max 100 per call)
- [ ] Results summary presented (success/fail/skip counts)
- [ ] Audit log saved to outputs/research/negative-keywords/data/

---

## Error Handling

| Issue | Response |
|-------|----------|
| User doesn't specify portfolio/product | List all 17 active portfolios and ask them to pick |
| Product not found in context/products.md | Ask for product name/ASIN and work from user description |
| context/search-terms.md missing or empty | WARN: "Cannot verify protected terms. Proceeding with extra caution — flagging more terms for review." |
| Search term file has unexpected format | Map available columns. Flag if missing Customer Search Term or Spend columns. |
| Product spans multiple categories (Barbie) | Identify the PRIMARY craft type of the Barbie product and generate based on that |
| User wants negatives for ALL portfolios | Run one at a time. Suggest starting with highest-spend portfolio. |
| User approves without reviewing | Remind: "The review step catches mistakes. Are you sure you want to skip?" |
| Ads API report creation fails | Fall back to manual: ask user for search term CSV export from Seller Central |
| Ads API report still pending after 5 polls | Save report ID, continue without search term data. User can retry later |
| list_sp_campaigns returns 0 for portfolio | Verify portfolioId is correct. List all portfolios and re-map |
| Programmatic application partially fails | Report successes, provide copy-paste format for failed terms |

---

## Integration with Other Skills

### With Weekly PPC Analysis
- **This skill** generates proactive negatives from product knowledge (use BEFORE launching or after restructuring campaigns)
- **Weekly PPC Analysis** finds reactive negatives from spend data (use WEEKLY on active campaigns)
- **Best workflow:** Run this skill first for baseline negatives → apply → then run Weekly PPC Analysis weekly to catch what product knowledge missed

### Handoff Points

| Scenario | Use This Skill | Next Step |
|----------|---------------|-----------|
| New portfolio launch | Generate baseline negatives | Apply via Step 8, then Weekly PPC after 2 weeks |
| Restructured campaigns | Regenerate negatives | Apply via Step 8, monitor with weekly analysis |
| Weekly PPC flags category-level waste | Run this skill for systematic category negatives | Apply via Step 8 |
| High-spend zero-order discovered | Auto-detected via Ads API search term data | Apply via Step 8 |

---

## Step 9: Slack Notification

**Skip this step.** The PPC Agent orchestrator handles Slack notifications via Step 8e after every sub-skill completes.

---

## ⚠️ AFTER EVERY RUN — Update Lessons (MANDATORY)

**Before presenting final results, update `.claude/skills/negative-keyword-generator/LESSONS.md`.**

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

---
name: listing-manager
description: Reactive listing workbench — orchestrates listing audits, optimizations, new listing creation, image planning, and impact measurement for any product
triggers:
  - listing manager
  - listing workbench
  - optimize listing
  - fix listing
  - listing needs work
  - full listing
  - launch product
  - create listing
  - new listing
  - listing for
output_location: outputs/research/listing-manager/
---

# Listing Manager

**USE WHEN** user says: "listing manager", "optimize listing", "fix listing", "listing needs work", "full listing", "launch product", "create listing", "new listing", "listing for"

**Also called by other skills:** PPC Agent (CVR drops), Keyword Rank Optimizer (conversion waste), Listing AB Analyzer (NEGATIVE/ITERATE verdicts).

---

## BEFORE YOU START — Read Lessons

**MANDATORY FIRST STEP:** Read `LESSONS.md` in this skill's folder before doing anything else.

1. Read `.claude/skills/listing-manager/LESSONS.md`
2. Check **Known Issues** — plan around these
3. Check **Repeat Errors** — if you encounter one during this run, tell the user immediately: _"Repeat issue (xN): [description]"_
4. Apply all past lessons to this run

**Do NOT skip this step.**

---

## Design Philosophy

**This is a reactive workbench, not a proactive scanner.**

- It **never** scans products on a schedule
- It **never** runs portfolio-wide audits unprompted
- It **never** triggers itself
- It gets called when: (1) the user asks, or (2) another skill flags a product

In a well-optimized catalog, this skill rarely runs. That's the goal.

---

## What This Does

Single entry point for ALL listing work. Determines what a product needs and chains the right sub-skills together:

| Product State | Flow |
|--------------|------|
| **New product** (no listing exists) | Research → listing-creator → image-planner → Notion → optional SP-API push |
| **Existing product** (needs optimization) | listing-optimizer audit → score → listing-creator with audit context → push → schedule AB check |
| **Post-change measurement** | Routes to listing-ab-analyzer |
| **Iteration after negative AB result** | Re-audit with AB context → targeted rewrite |

**Cadence:** On-demand only
**Token budget:** Varies by mode (see sub-skill budgets)

---

## Efficiency Standards

- **New product full run:** <150K tokens, <$0.30 API cost, <20 min
- **Existing product optimization:** <120K tokens, <$0.20 API cost, <15 min
- **Impact check (route to AB analyzer):** <35K tokens, <5 min
- **Shared research saves ~50%** when running listing-creator + image-planner together

---

## Entry Points

This skill is triggered from different sources. Each provides different context:

| Trigger Source | What It Passes | Example |
|---------------|---------------|---------|
| **User direct** | Product name, ASIN, or SKU | "Optimize the cross stitch listing" |
| **User (new product)** | Product specs or SKU | "Create listing for new latch hook kit" |
| **PPC Agent** | ASIN + reason + metrics | "B08DDJCQKF — CVR dropped 40% over 3 weeks" |
| **Keyword Rank Optimizer** | ASIN + classification details | "B08DDJCQKF — WASTING MONEY due to conversion waste (conv_click_ratio <0.5)" |
| **Listing AB Analyzer** | ASIN + verdict + findings | "B09X55KL2C — NEGATIVE verdict, CTR dropped after title change" |
| **User (check results)** | Product name + "did it work?" | "Did that listing change work for cross stitch?" |

---

## Process

### Step 0: Identify the Product

1. Read `context/sku-asin-mapping.json` — resolve whatever the user/caller provides (name, ASIN, or SKU) to a full product record
2. Read `outputs/research/listing-manager/state/listing-tracker.json` — check history for this product
3. Read `context/business.md` — get portfolio stage and product context

**If product not found:** Ask user to clarify. Do not guess.

### Step 1: Classify — What Does This Product Need?

Based on the trigger source and product state, classify into one of five modes:

| Mode | Conditions | Next Step |
|------|-----------|-----------|
| **NEW_PRODUCT** | No listing exists, or user explicitly says "create listing" / "new listing" / "launch product" | → Step 2a |
| **OPTIMIZE** | Product has a listing, user says "optimize" / "fix", or upstream skill flagged it | → Step 2b |
| **CHECK_RESULTS** | User asks "did that change work?" or AB analyzer is due | → Step 2c |
| **ITERATE** | AB analyzer returned NEGATIVE or ITERATE verdict | → Step 2d |
| **IMAGE_ONLY** | User specifically asks for image plan only | → Step 2e |

**Ambiguous cases:** If unclear, ask: "This product already has a listing. Do you want to (1) optimize the existing listing, (2) create a completely new listing from scratch, or (3) check if the last listing change worked?"

### Step 2a: NEW_PRODUCT Flow

Full listing creation + image planning with shared research.

**This absorbs the logic from the deprecated product-listing-development skill.**

#### Gather Inputs (ONCE)

- [ ] Product SKU or name — which product from the catalog?
- [ ] Target niche keywords — what do customers search for?
- [ ] Target age range — what age is this product for?
- [ ] Competitor ASINs (optional — will discover if not provided)
- [ ] Key differentiators — what makes this product different?

**STOP and ask user if niche keywords are missing.** These drive the entire strategy.

#### Shared Research (Run ONCE, used by both listing + images)

Run all research once. Both listing-creator and image-planner consume the same data.

1. **Check context files first** (ALWAYS before any scraping):
   - `context/competitors.md` — competitor ASINs by category
   - `context/search-terms.md` — keywords with volume by category
   - `context/hero-products.md` — our ASIN + key selling points
   - `context/products.md` — exact specs, contents, measurements

2. **Competitor analysis** (only scrape what's NOT in context files):
   - Apify product scraper for titles, bullets, prices, BSR, ratings, reviews
   - Extract image patterns (main image style, lifestyle vs white background, infographic usage)
   - Extract review themes (praise language, complaint language, emotional triggers)

3. **Q&A scraping** from top 3-5 competitor listings:
   - Categorize by theme: contents, age/skill, safety, quality, completion, instructions, gift, size
   - Sort by vote count / helpfulness

4. **Keyword research:**
   - Primary keywords (3-5) — highest search volume, must be in title
   - Secondary keywords (5-10) — medium volume, title or bullets
   - Long-tail keywords (10-20) — backend keywords

5. **Brand Analytics validation** (if existing ASINs in same category):
   - SQP report for conversion data per keyword
   - Search Terms report for click share intelligence
   - Cross-reference keyword list against BA data

**Save shared research to:** `outputs/research/listing-manager/new-products/{product-slug}/research/`

#### Generate Listing

Delegate to **listing-creator** logic (read `.claude/skills/listing-creator/SKILL.md`):
- Pass all shared research as input (competitors, keywords, Q&A, BA validation)
- listing-creator skips its own research phases (already done)
- Generates: title, 5 bullets, backend keywords
- Save to: `outputs/research/listing-manager/new-products/{product-slug}/listing/`

#### Generate Image Plan

Delegate to **image-planner** logic (read `.claude/skills/image-planner/SKILL.md`):
- Pass shared research (competitor images, review themes, Q&A insights)
- image-planner skips its own research phases (already done)
- Generates: main image strategy, 6-7 image plan with rationale
- Save to: `outputs/research/listing-manager/new-products/{product-slug}/image-plan/`

#### Upload to Notion

Single Notion page with both sections:

1. Search for existing page using `find_or_create_page`
2. **Parent page:** "Product Listing Development" (ID: `30557318-d05c-806a-a94f-f5a439d94d10`)
3. Append listing section (see listing-creator SKILL.md for Notion format)
4. Append image plan section (see image-planner SKILL.md for Notion format)
5. Set properties: Title, SKU, Status=Draft, Date, Has Listing=true, Has Image Plan=true

#### Optional: Push to Amazon

If user approves:
```
update_listing(seller_id, sku, marketplace_id, body)
```
- Push title, bullets, description, backend keywords via SP-API
- Log the push to listing-tracker.json

#### Update Tracker

Log to `listing-tracker.json`:
- Set `listing_created` date
- Add entry to `changes[]` with type "initial_creation"
- Set `current_score` to null (no audit yet)
- Set `next_action` to "Monitor performance for 3-4 weeks, then audit"

### Step 2b: OPTIMIZE Flow

Audit existing listing, then optionally rewrite and push.

#### Run Listing Optimizer

Delegate to **listing-optimizer** (read `.claude/skills/listing-optimizer/SKILL.md`):
- Deep audit mode (single product)
- Gets: ranking juice scores, keyword gaps, root word coverage, rank trends, CVR comparison
- Generates: optimization score, specific weaknesses, AI copywriter alternatives

**Present audit results to user:**
```
## Listing Audit: {Product Name}

**Optimization Score:** {X}/100
**Weakest Component:** {title/bullets/description/backend}
**Key Gaps:** {top 3 keyword gaps}
**Rank Trend:** {improving/stable/declining} on {N} tracked keywords

### Recommendation
{What specifically needs to change and why}

**Options:**
1. Generate optimized rewrite (I'll use the audit findings to create a targeted rewrite)
2. Save audit for reference only
3. Skip this product
```

#### If User Says "Rewrite" / "Fix It" / "Generate"

Delegate to **listing-creator** WITH `audit_context`:

The audit_context includes:
- `keyword_gaps` — exact words missing from title/bullets
- `ranking_juice_scores` — which components are weakest (title, bullets, description)
- `root_coverage` — which broad search roots are missing
- `rank_trends` — which keywords are rising/falling (from DataDive Rank Radar)
- `competitor_strengths` — what top competitors do better specifically
- `ai_copywriter_alternatives` — DataDive's generated options (all 4 modes)
- `current_listing` — the current title, bullets, backend keywords (from SP-API `get_listing`)

listing-creator uses this context to write a targeted rewrite, not a generic from-scratch listing. See **listing-creator Phase 0b** for how it consumes this.

Save rewrite to: `outputs/research/listing-manager/optimizations/{product-slug}/{YYYY-MM-DD}/`

#### Present Rewrite for Approval

Show the user:
- Current vs proposed title (side by side)
- Current vs proposed bullets (side by side)
- Current vs proposed backend keywords
- What changed and why (tied to audit findings)

#### Optional: Push to Amazon

If user approves the rewrite:
```
update_listing(seller_id, sku, marketplace_id, body)
```

#### Schedule AB Analysis

After push:
- Calculate 3 weeks from push date
- Set `ab_scheduled` in tracker
- Tell user: "I'll remind you to check the impact in 3 weeks ({date}). Run 'listing AB for {product name}' then."

#### Update Tracker

Log to `listing-tracker.json`:
- Add audit to `audits[]`
- If pushed: add to `changes[]` with type, before/after summary
- Update `current_score` from audit
- Update `next_action` to "AB analysis due {date}" or "Audit complete — no changes made"

#### Update PPC Portfolio Tracker (if push was made)

After a successful listing push, update `outputs/research/ppc-agent/state/{portfolio-slug}.json` and `agent-state.json` portfolio_index:
- `last_listing_change` → push date (today)
- `listing_stage` → "awaiting-ab"

This prevents the PPC agent from suggesting listing audits for products that were just optimized (14-day cooldown in Step 4 queue rules).

### Step 2c: CHECK_RESULTS Flow

Route to listing-ab-analyzer.

1. Read listing-tracker.json — find the most recent change for this product
2. Validate timing (must be 7+ days since change)
3. Delegate to **listing-ab-analyzer** (read `.claude/skills/listing-ab-analyzer/SKILL.md`)
4. AB analyzer updates the tracker with its verdict

### Step 2d: ITERATE Flow

Re-optimization after a negative AB result.

1. Load from listing-tracker.json:
   - The previous change details (what was modified)
   - The AB analysis verdict and findings
   - The original audit that prompted the change

2. Run listing-optimizer again (fresh audit post-change)

3. Compare:
   - Pre-change audit vs post-change audit
   - Which metrics got worse? Which improved?
   - What did the AB analyzer flag specifically?

4. Present to user:
   ```
   ## Iteration Analysis: {Product Name}

   **Previous change:** {what was changed} on {date}
   **AB Verdict:** {NEGATIVE/ITERATE}
   **What went wrong:** {specific findings from AB analyzer}

   **Current audit vs pre-change audit:**
   | Component | Pre-Change Score | Current Score | Delta |
   |-----------|-----------------|---------------|-------|
   | Title     | {X}             | {X}           | {+/-} |
   | Bullets   | {X}             | {X}           | {+/-} |

   **Options:**
   1. Revert to previous version (I have the old listing from the tracker)
   2. Generate a new iteration (using both the original audit + AB findings)
   3. Leave as-is and monitor
   ```

5. If user chooses iteration:
   - Pass both original audit context AND AB findings to listing-creator
   - The creator gets: what worked, what didn't, and what to try differently
   - This is the tightest feedback loop: audit → change → measure → learn → iterate

### Step 2e: IMAGE_ONLY Flow

1. Check if shared research exists for this product (from a previous NEW_PRODUCT run)
2. If yes: reuse research, delegate to image-planner
3. If no: run competitor image analysis only (no full research), delegate to image-planner
4. Upload to Notion (append to existing product page if it exists)

---

## State Tracker

**File:** `outputs/research/listing-manager/state/listing-tracker.json`

### Schema

```json
{
  "last_updated": "YYYY-MM-DD",
  "products": {
    "B08DDJCQKF": {
      "name": "Product Name",
      "sku": "SKU-CODE",
      "portfolio": "portfolio-slug",
      "status": "active",
      "listing_created": "YYYY-MM-DD",
      "audits": [
        {
          "date": "YYYY-MM-DD",
          "score": 62,
          "weakest": "title",
          "trigger": "ppc-agent: CVR drop",
          "brief_path": "outputs/research/listing-manager/optimizations/{slug}/{date}/audit.md"
        }
      ],
      "changes": [
        {
          "date": "YYYY-MM-DD",
          "type": "title + bullets rewrite",
          "trigger": "audit score 62 — user approved",
          "pushed_to_amazon": true,
          "ab_scheduled": "YYYY-MM-DD",
          "ab_status": "pending",
          "ab_verdict": null,
          "before_summary": "Old title: ...",
          "after_summary": "New title: ..."
        }
      ],
      "current_score": 62,
      "next_action": "AB analysis due YYYY-MM-DD"
    }
  }
}
```

### Tracker Rules

- **Every audit** → append to product's `audits[]`
- **Every listing change** → append to product's `changes[]` with before/after summary
- **AB verdict arrives** → update the relevant `changes[]` entry's `ab_status` and `ab_verdict`
- **`current_score`** = most recent audit score (null if never audited)
- **`next_action`** = human-readable next step
- **Update `last_updated`** on every write
- **Update IMMEDIATELY** after API calls succeed, before presenting results

---

## Output Organization

```
outputs/research/listing-manager/
├── state/
│   └── listing-tracker.json           # Product state tracker
├── new-products/
│   └── {product-slug}/
│       ├── research/                   # Shared competitor/keyword/Q&A data
│       │   ├── competitors-YYYY-MM-DD.md
│       │   ├── keywords-YYYY-MM-DD.json
│       │   ├── qa-YYYY-MM-DD.md
│       │   └── ba-validation-YYYY-MM-DD.md
│       ├── listing/                    # listing-creator output
│       │   └── {product-slug}-listing-YYYY-MM-DD.md
│       └── image-plan/                 # image-planner output
│           └── {product-slug}-image-plan-YYYY-MM-DD.md
└── optimizations/
    └── {product-slug}/
        └── {YYYY-MM-DD}/
            ├── audit.md                # listing-optimizer output
            ├── rewrite.md              # listing-creator output (with audit context)
            └── snapshot.json           # Machine-readable state
```

---

## Sub-Skill Delegation Rules

### When delegating to listing-creator:

1. Read `.claude/skills/listing-creator/SKILL.md`
2. Read `.claude/skills/listing-creator/LESSONS.md`
3. If `audit_context` is available (OPTIMIZE/ITERATE modes):
   - Pass audit_context so creator uses Phase 0b
   - Creator skips Phase 3 (keyword research) and Phase 3b (BA validation) — already done by optimizer
   - Creator still runs Phase 4-6 (Q&A, bullet mapping, generation)
4. If shared research is available (NEW_PRODUCT mode):
   - Pass research data so creator skips its own research phases
5. Save output to listing-manager's folder structure (not listing-creator's)

### When delegating to listing-optimizer:

1. Read `.claude/skills/listing-optimizer/SKILL.md`
2. Read `.claude/skills/listing-optimizer/LESSONS.md`
3. Always use deep audit mode (single product)
4. Save output to listing-manager's folder structure

### When delegating to image-planner:

1. Read `.claude/skills/image-planner/SKILL.md`
2. Read `.claude/skills/image-planner/LESSONS.md`
3. Pass shared research if available
4. Save output to listing-manager's folder structure

### When delegating to listing-ab-analyzer:

1. Read `.claude/skills/listing-ab-analyzer/SKILL.md`
2. Read `.claude/skills/listing-ab-analyzer/LESSONS.md`
3. Pass ASIN + change date from listing-tracker.json
4. AB analyzer updates the tracker directly

---

## What This Skill Does NOT Do

- Does NOT scan products on a schedule
- Does NOT run portfolio-wide audits proactively
- Does NOT trigger itself — always called by user or another skill
- Does NOT decide WHAT to optimize — the caller tells it which product and why
- Does NOT apply bid changes (that's PPC agent territory)
- Does NOT compete with listing-optimizer or listing-creator — it orchestrates them

---

## Error Handling

| Issue | Response |
|-------|----------|
| Product not found in sku-asin-mapping | Ask user to clarify product name/ASIN |
| listing-tracker.json doesn't exist | Create it with empty `products` object |
| Sub-skill fails (optimizer/creator/AB) | Log failure in tracker, tell user which step failed and why |
| User says "optimize" but product has never been audited | Run audit first (can't optimize what you haven't measured) |
| User says "check results" but no changes logged | "No listing changes found in the tracker for this product. When was the change made?" |
| AB analysis requested but change is <7 days old | "Too early — need at least 1 full week. Re-run after {date}." |
| Notion upload fails | Save locally, tell user. Notion is nice-to-have, not blocking. |
| SP-API push fails | Save rewrite locally, tell user to push manually. Log in tracker as `pushed_to_amazon: false`. |

---

## Post Notifications

Read `.claude/skills/notification-hub/SKILL.md` for notification recipes.

**Channel:** `#claude-product-updates`

**Format varies by mode:**

NEW_PRODUCT:
```
*New Listing Created* — {Product Name}
- Listing: {title preview}
- Image plan: {N} images planned
- Uploaded to Notion: {Yes/No}
- Pushed to Amazon: {Yes/No}
```

OPTIMIZE:
```
*Listing Optimized* — {Product Name}
- Audit score: {X}/100
- Changes: {what was changed}
- Pushed to Amazon: {Yes/No}
- AB check scheduled: {date}
```

If Slack MCP is unavailable, skip and note in run log.

---

## AFTER EVERY RUN — Update Lessons (MANDATORY)

**Before presenting final results, update `.claude/skills/listing-manager/LESSONS.md`.**

### 1. Write a Run Log Entry

Add a new entry at the **TOP** of the Run Log section:

```
### Run: YYYY-MM-DD
**Mode:** NEW_PRODUCT / OPTIMIZE / CHECK_RESULTS / ITERATE / IMAGE_ONLY
**Product:** {name} ({ASIN})
**Trigger:** {user / ppc-agent / keyword-rank-optimizer / listing-ab-analyzer}
**Result:** Success / Partial / Failed

**What happened:**
- (What went according to plan)

**What didn't work:**
- (Any issues, with specifics)

**Sub-skills called:**
- listing-optimizer: {ran / skipped} — {outcome}
- listing-creator: {ran / skipped} — {outcome}
- image-planner: {ran / skipped} — {outcome}
- listing-ab-analyzer: {ran / skipped} — {outcome}

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

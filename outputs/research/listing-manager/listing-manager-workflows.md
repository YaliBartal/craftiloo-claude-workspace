# Listing Manager — Workflow Charts

---

## 1. Master Orchestration Flow

How listing-manager receives a request and routes it.

```
                         ┌─────────────────────┐
                         │   LISTING MANAGER    │
                         │   (Entry Point)      │
                         └──────────┬───────────┘
                                    │
                         ┌──────────▼───────────┐
                         │  Step 0: Identify     │
                         │  - sku-asin-mapping   │
                         │  - listing-tracker    │
                         │  - business.md        │
                         └──────────┬───────────┘
                                    │
                         ┌──────────▼───────────┐
                         │  Step 1: Classify     │
                         │  What does this       │
                         │  product need?        │
                         └──────────┬───────────┘
                                    │
            ┌───────────┬───────────┼───────────┬──────────┐
            ▼           ▼           ▼           ▼          ▼
     ┌────────────┐┌──────────┐┌──────────┐┌──────────┐┌────────┐
     │ NEW_PRODUCT││ OPTIMIZE ││ CHECK_   ││ ITERATE  ││ IMAGE_ │
     │            ││          ││ RESULTS  ││          ││ ONLY   │
     └─────┬──────┘└────┬─────┘└────┬─────┘└────┬─────┘└───┬────┘
           │            │           │           │          │
           ▼            ▼           ▼           ▼          ▼
     ┌────────────┐┌──────────┐┌──────────┐┌──────────┐┌────────┐
     │ Shared     ││ listing- ││ listing- ││ Re-audit ││ image- │
     │ Research   ││ optimizer││ ab-      ││ + AB     ││ planner│
     │ ────────── ││ (audit)  ││ analyzer ││ context  ││        │
     │ listing-   ││ ──────── ││          ││ ──────── ││        │
     │ creator    ││ listing- ││          ││ listing- ││        │
     │ +          ││ creator  ││          ││ creator  ││        │
     │ image-     ││ (rewrite)││          ││ (iterate)││        │
     │ planner    ││          ││          ││          ││        │
     └─────┬──────┘└────┬─────┘└────┬─────┘└────┬─────┘└───┬────┘
           │            │           │           │          │
           ▼            ▼           ▼           ▼          ▼
     ┌─────────────────────────────────────────────────────────┐
     │              UPDATE LISTING TRACKER                     │
     │   - Log audit/change/verdict                            │
     │   - Set next_action                                     │
     │   - Schedule AB check (if pushed)                       │
     └────────────────────────┬────────────────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │   Notify Slack     │
                    │   #claude-product  │
                    │   -updates         │
                    └───────────────────┘
```

---

## 2. Upstream Trigger Map

How other skills feed products into listing-manager (all suggestions, never auto-triggers).

```
┌──────────────────────────────────────────────────────────────────────┐
│                        UPSTREAM TRIGGERS                             │
│                  (Skills that SUGGEST listing-manager)                │
└──────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────┐     ┌─────────────────────┐
  │   PPC AGENT         │     │   KEYWORD RANK       │
  │   (Portfolio        │     │   OPTIMIZER           │
  │    Action Plan)     │     │                       │
  │                     │     │  Finds WASTING MONEY  │
  │  CVR dropped >25%   │     │  keywords with        │
  │  over 2+ weeks      │     │  conv_click_ratio     │
  │  with stable bids   │     │  < 0.5 (conversion    │
  │                     │     │  waste = listing       │
  │  "CVR drop not      │     │  problem)             │
  │   explained by PPC  │     │                       │
  │   changes"          │     │  "N keywords show     │
  │                     │     │   conversion waste"   │
  └────────┬────────────┘     └──────────┬────────────┘
           │                             │
           │    ┌────────────────────┐    │
           │    │  USER (direct)     │    │
           │    │                    │    │
           │    │  "Optimize the     │    │
           │    │   cross stitch     │    │
           │    │   listing"         │    │
           │    │                    │    │
           │    │  "Create listing   │    │
           │    │   for new product" │    │
           │    │                    │    │
           │    │  "Did that listing │    │
           │    │   change work?"    │    │
           │    └─────────┬──────────┘    │
           │              │               │
           ▼              ▼               ▼
  ┌────────────────────────────────────────────────┐
  │              LISTING MANAGER                    │
  │                                                 │
  │   Receives: ASIN + reason + metrics             │
  │   Classifies into mode                          │
  │   Routes to sub-skills                          │
  └────────────────────────┬───────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
  │  listing-    │ │  listing-    │ │  listing-    │
  │  optimizer   │ │  creator     │ │  ab-analyzer │
  └──────────────┘ └──────────────┘ └──────┬───────┘
                                           │
                                           │ NEGATIVE / ITERATE
                                           │ verdict
                                           ▼
                                  ┌──────────────────┐
                                  │  Suggests back    │
                                  │  to LISTING       │
                                  │  MANAGER           │
                                  │  (ITERATE mode)   │
                                  └──────────────────┘
```

---

## 3. Existing Product Lifecycle (OPTIMIZE → MEASURE → ITERATE)

The full feedback loop for an existing product.

```
                    ┌─────────────────┐
                    │  Trigger:       │
                    │  "Optimize X"   │
                    │  or upstream    │
                    │  skill flags X  │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  LISTING        │
                    │  OPTIMIZER      │
                    │  (Deep Audit)   │
                    │                 │
                    │  • Ranking Juice│
                    │  • Keyword gaps │
                    │  • Root coverage│
                    │  • Rank trends  │
                    │  • CVR compare  │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Present Audit  │
                    │  Score: 62/100  │
                    │  Weakest: Title │
                    │                 │
                    │  ┌────────────┐ │
                    │  │ User Opts: │ │
                    │  │ 1. Rewrite │ │
                    │  │ 2. Save    │──────────► STOP (audit saved)
                    │  │ 3. Skip    │ │
                    │  └─────┬──────┘ │
                    └────────┼────────┘
                             │ (User picks "Rewrite")
                             │
                    ┌────────▼────────┐
                    │  LISTING        │
                    │  CREATOR        │
                    │  (with audit_   │
                    │   context)      │
                    │                 │
                    │  Phase 0b:      │
                    │  • Uses keyword │
                    │    gaps         │
                    │  • Uses ranking │
                    │    juice scores │
                    │  • Uses current │
                    │    listing      │
                    │  Skips Phase 3  │
                    │  Skips Phase 3b │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Present Side   │
                    │  by Side:       │
                    │                 │
                    │  OLD title      │
                    │  vs NEW title   │
                    │                 │
                    │  OLD bullets    │
                    │  vs NEW bullets │
                    │                 │
                    │  ┌────────────┐ │
                    │  │ Approve?   │ │
                    │  │ Y / N      │ │
                    │  └─────┬──────┘ │
                    └────────┼────────┘
                             │ (User approves)
                             │
                    ┌────────▼────────┐
                    │  PUSH TO        │
                    │  AMAZON         │
                    │  (SP-API        │
                    │   update_       │
                    │   listing)      │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  UPDATE         │
                    │  TRACKER        │
                    │                 │
                    │  • Log change   │
                    │  • Set ab_      │
                    │    scheduled    │
                    │    = +3 weeks   │
                    │  • Notify Slack │
                    └────────┬────────┘
                             │
                             │  ~~~ 3 weeks pass ~~~
                             │
                    ┌────────▼────────┐
                    │  User asks:     │
                    │  "Did that      │
                    │   change work?" │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  LISTING AB     │
                    │  ANALYZER       │
                    │                 │
                    │  • SCP funnel   │
                    │  • SQP keywords │
                    │  • PPC correl.  │
                    │  • Confounders  │
                    │  • Revenue $    │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
     ┌──────────────┐ ┌───────────┐ ┌──────────────┐
     │  POSITIVE    │ │  NEUTRAL  │ │  NEGATIVE /  │
     │              │ │           │ │  ITERATE     │
     │  KEEP the    │ │  KEEP     │ │              │
     │  change.     │ │  No harm. │ │  Consider    │
     │  Done.       │ │  Done.    │ │  reverting   │
     │              │ │           │ │  or iterating│
     └──────────────┘ └───────────┘ └──────┬───────┘
                                           │
                                           │ (User picks "Iterate")
                                           │
                                  ┌────────▼────────┐
                                  │  ITERATE MODE   │
                                  │                 │
                                  │  Load:          │
                                  │  • Original     │
                                  │    audit        │
                                  │  • AB findings  │
                                  │  • What went    │
                                  │    wrong        │
                                  │                 │
                                  │  Re-run         │
                                  │  OPTIMIZER      │
                                  │  (fresh audit)  │
                                  │                 │
                                  │  Compare pre vs │
                                  │  post change    │
                                  └────────┬────────┘
                                           │
                                  ┌────────▼────────┐
                                  │  LISTING        │
                                  │  CREATOR        │
                                  │  (with BOTH     │
                                  │   audit_context │
                                  │   + ab_findings)│
                                  │                 │
                                  │  Knows what     │
                                  │  worked AND     │
                                  │  what didn't    │
                                  └────────┬────────┘
                                           │
                                           │ (Push → Track → Wait 3 weeks → Measure again)
                                           │
                                  ┌────────▼────────┐
                                  │  CYCLE REPEATS  │
                                  │  until POSITIVE │
                                  │  or user stops  │
                                  └─────────────────┘
```

---

## 4. New Product Flow (NEW_PRODUCT Mode)

Creating a listing + image plan from scratch with shared research.

```
                    ┌─────────────────┐
                    │  "Create listing │
                    │   for new        │
                    │   product X"     │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  GATHER INPUTS  │
                    │                 │
                    │  • Product SKU  │
                    │  • Niche        │
                    │    keywords     │
                    │  • Target age   │
                    │  • Competitor   │
                    │    ASINs (opt)  │
                    │  • Differen-    │
                    │    tiators      │
                    └────────┬────────┘
                             │
                    ┌────────▼─────────────────────────────────┐
                    │          SHARED RESEARCH                  │
                    │          (Run ONCE — costs ~50% less)     │
                    │                                           │
                    │  1. Check context files first             │
                    │     ├── context/competitors.md            │
                    │     ├── context/search-terms.md           │
                    │     ├── context/hero-products.md          │
                    │     └── context/products.md               │
                    │                                           │
                    │  2. Competitor scraping (Apify)           │
                    │     ├── Titles, bullets, prices           │
                    │     ├── Images (styles, infographics)     │
                    │     └── Reviews (praise, complaints)      │
                    │                                           │
                    │  3. Q&A scraping (top 3-5 competitors)    │
                    │     └── Categorized by theme              │
                    │                                           │
                    │  4. Keyword research                      │
                    │     ├── Primary (3-5)                     │
                    │     ├── Secondary (5-10)                  │
                    │     └── Long-tail (10-20)                 │
                    │                                           │
                    │  5. Brand Analytics validation (if ASINs  │
                    │     exist in same category)               │
                    └────────┬──────────┬──────────────────────┘
                             │          │
                  ┌──────────▼──┐  ┌────▼──────────┐
                  │  LISTING    │  │  IMAGE         │
                  │  CREATOR    │  │  PLANNER       │
                  │             │  │                │
                  │  Consumes   │  │  Consumes      │
                  │  shared     │  │  shared        │
                  │  research:  │  │  research:     │
                  │  • Keywords │  │  • Competitor  │
                  │  • Q&A      │  │    images      │
                  │  • Comps    │  │  • Review      │
                  │             │  │    themes      │
                  │  Generates: │  │  • Q&A         │
                  │  • Title    │  │    insights    │
                  │  • Bullets  │  │                │
                  │  • Backend  │  │  Generates:    │
                  │    keywords │  │  • Main image  │
                  │             │  │    strategy    │
                  │             │  │  • 6-7 image   │
                  │             │  │    plan        │
                  └──────┬──────┘  └────┬───────────┘
                         │              │
                         └──────┬───────┘
                                │
                       ┌────────▼────────┐
                       │  NOTION UPLOAD  │
                       │                 │
                       │  Single page:   │
                       │  • Listing      │
                       │    section      │
                       │  • Image plan   │
                       │    section      │
                       │  • Full         │
                       │    research     │
                       └────────┬────────┘
                                │
                       ┌────────▼────────┐
                       │  Optional:      │
                       │  PUSH TO        │
                       │  AMAZON         │
                       │  (if approved)  │
                       └────────┬────────┘
                                │
                       ┌────────▼────────┐
                       │  UPDATE         │
                       │  TRACKER        │
                       │                 │
                       │  listing_       │
                       │  created: today │
                       │  next_action:   │
                       │  "Monitor 3-4   │
                       │   weeks, then   │
                       │   audit"        │
                       └─────────────────┘
```

---

## 5. State Tracker Lifecycle

How listing-tracker.json evolves for a single product over time.

```
DAY 0 (Product exists, never touched)
┌────────────────────────────────────┐
│  status: "active"                  │
│  listing_created: null             │
│  audits: []                        │
│  changes: []                       │
│  current_score: null               │
│  next_action: "No audit yet"       │
└────────────────────────────────────┘
            │
            │  Rank Optimizer flags conversion waste
            ▼
DAY 30 (First audit triggered)
┌────────────────────────────────────┐
│  audits: [{                        │
│    date: "2026-04-10"              │
│    score: 58                       │
│    weakest: "title"                │
│    trigger: "rank-optimizer:       │
│      conversion waste"             │
│  }]                                │
│  current_score: 58                 │
│  next_action: "Rewrite approved"   │
└────────────────────────────────────┘
            │
            │  User approves rewrite, pushed to Amazon
            ▼
DAY 31 (Change pushed)
┌────────────────────────────────────┐
│  changes: [{                       │
│    date: "2026-04-11"              │
│    type: "title + bullets"         │
│    pushed_to_amazon: true          │
│    ab_scheduled: "2026-05-02"      │
│    ab_status: "pending"            │
│    ab_verdict: null                │
│    before: "Old title: ..."        │
│    after: "New title: ..."         │
│  }]                                │
│  next_action: "AB due 2026-05-02"  │
└────────────────────────────────────┘
            │
            │  3 weeks later, AB analysis runs
            ▼
DAY 52 (AB analysis complete — POSITIVE)
┌────────────────────────────────────┐
│  changes: [{                       │
│    ...                             │
│    ab_status: "complete"           │
│    ab_verdict: "POSITIVE"          │
│  }]                                │
│  next_action: "Healthy — no        │
│    action needed"                  │
└────────────────────────────────────┘


        ─── OR ───


DAY 52 (AB analysis complete — NEGATIVE)
┌────────────────────────────────────┐
│  changes: [{                       │
│    ...                             │
│    ab_status: "complete"           │
│    ab_verdict: "NEGATIVE"          │
│  }]                                │
│  next_action: "ITERATE — revert    │
│    or re-optimize"                 │
└────────────────────────────────────┘
            │
            │  User runs ITERATE mode
            ▼
DAY 53 (Second audit + iteration)
┌────────────────────────────────────┐
│  audits: [                         │
│    { date: "2026-04-10", ... },    │
│    { date: "2026-05-03",           │
│      score: 71,                    │
│      trigger: "iterate after       │
│        negative AB" }              │
│  ]                                 │
│  changes: [                        │
│    { ... first change ... },       │
│    { date: "2026-05-03",           │
│      type: "title iteration v2",   │
│      ab_scheduled: "2026-05-24" }  │
│  ]                                 │
│  current_score: 71                 │
│  next_action: "AB due 2026-05-24"  │
└────────────────────────────────────┘
```

---

## 6. Sub-Skill Delegation Map

What listing-manager delegates vs. what it does itself.

```
┌─────────────────────────────────────────────────────────────────┐
│                     LISTING MANAGER DOES:                        │
│                                                                  │
│  • Product identification (sku-asin-mapping lookup)              │
│  • Mode classification (NEW / OPTIMIZE / CHECK / ITERATE / IMG)  │
│  • Shared research coordination (run once, pass to both)         │
│  • State tracking (listing-tracker.json reads/writes)            │
│  • User interaction (present options, get approval)              │
│  • Notion upload orchestration                                   │
│  • SP-API push orchestration                                     │
│  • AB scheduling (set dates, remind user)                        │
│  • Slack notifications                                           │
│  • LESSONS.md updates                                            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     LISTING MANAGER DELEGATES:                   │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ listing-        │  │ listing-        │  │ image-          │  │
│  │ optimizer       │  │ creator         │  │ planner         │  │
│  │                 │  │                 │  │                 │  │
│  │ • Ranking Juice │  │ • Title gen     │  │ • Main image    │  │
│  │ • Keyword gaps  │  │ • Bullet gen    │  │   strategy      │  │
│  │ • Root coverage │  │ • Backend KW    │  │ • 6-7 image     │  │
│  │ • Rank trends   │  │ • Q&A mapping   │  │   plan          │  │
│  │ • CVR compare   │  │ • Competitor    │  │ • Competitor     │  │
│  │ • AI Copywriter │  │   analysis      │  │   image         │  │
│  │                 │  │ • BA validation │  │   analysis      │  │
│  │ Reads its own   │  │                 │  │                 │  │
│  │ SKILL.md +      │  │ Reads its own   │  │ Reads its own   │  │
│  │ LESSONS.md      │  │ SKILL.md +      │  │ SKILL.md +      │  │
│  │                 │  │ LESSONS.md      │  │ LESSONS.md      │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│                                                                  │
│  ┌─────────────────┐                                             │
│  │ listing-ab-     │                                             │
│  │ analyzer        │                                             │
│  │                 │                                             │
│  │ • SCP funnel    │                                             │
│  │ • SQP keywords  │                                             │
│  │ • PPC correl.   │                                             │
│  │ • Confounders   │                                             │
│  │ • Revenue calc  │                                             │
│  │ • Verdict       │                                             │
│  │                 │                                             │
│  │ Updates tracker │                                             │
│  │ directly        │                                             │
│  └─────────────────┘                                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7. Decision Tree — "What Mode Am I In?"

```
START: Listing Manager receives a request
│
├── Does user say "create" / "new" / "launch"?
│   ├── YES ──► NEW_PRODUCT
│   └── NO ──▼
│
├── Does user say "check results" / "did it work" / "AB"?
│   ├── YES ──► CHECK_RESULTS
│   └── NO ──▼
│
├── Does user say "image plan" only?
│   ├── YES ──► IMAGE_ONLY
│   └── NO ──▼
│
├── Was this triggered by listing-ab-analyzer with NEGATIVE/ITERATE?
│   ├── YES ──► ITERATE
│   └── NO ──▼
│
├── Does the product have an existing listing?
│   ├── YES ──► OPTIMIZE
│   ├── NO  ──► NEW_PRODUCT
│   └── UNSURE ──► ASK USER:
│                  "This product already has a listing.
│                   Do you want to:
│                   1. Optimize the existing listing
│                   2. Create from scratch
│                   3. Check if last change worked"
```

---

*Generated 2026-03-10 for listing-manager skill documentation.*

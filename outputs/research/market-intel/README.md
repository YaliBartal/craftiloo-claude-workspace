# Market Intelligence - Organized Structure

## 🚀 Quick Start

**To run your morning market check:**
```
"market check" or "morning market" or "how are my products doing"
```

---

## 📁 Folder Structure

```
market-intel/
├── 📊 briefs/              # Daily market briefs (YOUR MAIN OUTPUT)
│   ├── 2026-02-09-morning.md
│   ├── 2026-02-09-evening.md
│   └── 2026-02-10-morning.md
│
├── 📄 reports/             # Detailed analysis reports
│   ├── products/          # Individual product deep-dives
│   │   └── cross-stitch-girls-2026-02-09.md
│   └── competitors/       # Competitor analysis
│       └── cross-stitch-2026-02-09.md
│
├── 💾 data/                # Raw scrape data (JSON)
│   ├── products/          # Our product data
│   ├── competitors/       # Competitor data
│   └── search/            # Search results
│
├── 📸 snapshots/           # Historical comparison data
│   ├── 2026-02-09-morning.json
│   └── 2026-02-09-evening.json
│
├── 🔧 scripts/             # Automation scripts
│   ├── generate_report.py
│   └── process_market_data.py
│
└── README.md              # This file
```

---

## 📖 File Naming Conventions

### Daily Briefs (Main Output)
**Format:** `YYYY-MM-DD-{time}.md`
- `2026-02-09-morning.md` - Morning market check
- `2026-02-09-evening.md` - Evening check (if needed)

### Product Reports
**Format:** `{product-slug}-YYYY-MM-DD.md`
- `cross-stitch-girls-2026-02-09.md`
- `embroidery-flowers-2026-02-09.md`

### Competitor Reports
**Format:** `{category-slug}-YYYY-MM-DD.md`
- `cross-stitch-2026-02-09.md`
- `embroidery-2026-02-09.md`

### Data Files
**Format:** `{type}-{slug}-YYYY-MM-DD.json`
- `product-cross-stitch-girls-2026-02-09.json`
- `competitors-cross-stitch-2026-02-09.json`
- `search-cross-stitch-2026-02-09.json`

### Snapshots
**Format:** `YYYY-MM-DD-{time}.json`
- `2026-02-09-morning.json` - Full market snapshot
- `2026-02-09-evening.json` - Evening snapshot (if needed)

---

## 🎯 What Goes Where

| You Want... | Look In... |
|-------------|------------|
| **Today's market brief** | `briefs/2026-02-09-morning.md` |
| **Yesterday's brief** | `briefs/2026-02-08-morning.md` |
| **Deep-dive on one product** | `reports/products/` |
| **Competitor analysis** | `reports/competitors/` |
| **Raw data for custom analysis** | `data/` |
| **Historical comparison data** | `snapshots/` |
| **Scripts to modify** | `scripts/` |

---

## 🔄 Daily Workflow

**Morning Market Check:**
1. Run: "market check"
2. Gets: Fresh data for all hero products + top competitors
3. Creates:
   - `briefs/YYYY-MM-DD-morning.md` ← **START HERE**
   - `snapshots/YYYY-MM-DD-morning.json` ← For tomorrow's comparison
   - Data files in `data/` (organized by type)

**What to Read:**
- **Start with:** `briefs/` folder - your daily brief
- **Deep-dive:** `reports/` if you need more detail on specific products/competitors

---

## 📊 Efficiency Standards

**Each morning check should:**
- ✅ Use <80K tokens
- ✅ Cost <$0.20
- ✅ Complete in <5 minutes
- ✅ Generate 1 brief + 1 snapshot
- ✅ No duplicate/temp files in root

**File count per day:**
- 1 brief in `briefs/`
- 1 snapshot in `snapshots/`
- Optional: detailed reports in `reports/` (only if deep-dive requested)
- Data files in `data/` (automatically organized by type)

---

## 🗑️ Cleanup Policy

**Keep:**
- All `briefs/` (daily history)
- All `snapshots/` (needed for comparisons)
- Recent `reports/` (last 30 days)

**Can Archive/Delete:**
- `data/` files older than 7 days (can regenerate from snapshots)
- `reports/` older than 30 days (unless specifically valuable)

---

## 💰 Cost

- Apify usage: ~$0.15-0.20 per morning check
- Includes: Hero products + top 4-5 competitors
- Recommended: Daily morning check

---

## 📅 Next Steps

1. ✅ Baseline established (2026-02-09)
2. ✅ Folder structure organized
3. Tomorrow: Run "market check" to see first 24-hour changes
4. After 7 days: Weekly trend analysis available

---

*Setup date: 2026-02-09*
*Reorganized: 2026-02-09*

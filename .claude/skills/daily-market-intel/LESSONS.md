# Lessons Learned — Daily Market Intel

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

<!-- Add new entries at the TOP (newest first). Use this exact format: -->

### Run: 2026-02-09
**Goals:**
- [ ] Fetch competitor data via Apify API
- [ ] Generate daily market intel brief

**Result:** ⚠️ Partial

**What happened:**
- Eventually completed the report after user provided data manually

**What didn't work:**
- Assumed API access to Apify would work — tried multiple endpoints without checking if data already existed
- No upfront question — should have asked "where is the scraper output?" immediately
- Wasted attempts on incorrect API endpoints
- Didn't check for existing JSON files in outputs/ before fetching
- Used 60% of context budget on failed API calls

**Is this a repeat error?** No — first run

**Lesson learned:**
- ASK FIRST: "Do you have fresh scraper data, or should I run a new scrape?"
- CHECK for existing recent files in outputs/ before fetching via API
- Don't retry failed API approaches — ask user for guidance immediately
- Be direct with questions early to save context budget

**Tokens/cost:** ~60% of budget wasted on failed API calls

---

## Known Issues

### Issue: Data Source Assumptions
- **First seen:** 2026-02-09
- **Description:** Skill assumes it needs to fetch data via API, but user may already have data locally
- **Workaround:** Always ask user first; check `outputs/` for recent JSON files before fetching
- **Root cause:** SKILL.md said "Use Apify MCP to scrape" without handling pre-existing data case

---

## Repeat Errors

_None yet._

---

## Resolved Issues

_None yet._

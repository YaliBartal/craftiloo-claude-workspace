# Lessons Learned - Daily Market Intel Skill

## Issue: First Run Inefficiency (2026-02-09)

**Problem:** Used 60% of context budget trying to fetch Apify run data via API when user already had the output.

### What Went Wrong

1. **Assumed API access** - Tried multiple Apify API endpoints without checking if data already existed
2. **No upfront question** - Should have asked "where is the scraper output?" immediately
3. **API endpoint confusion** - Wasted attempts on incorrect endpoints
4. **Didn't check existing files first** - Should have looked for recent JSON files before fetching

### Root Cause

The skill instructions said "Use Apify MCP to scrape" but didn't handle the case where:
- User already ran the scraper manually
- Data exists but in a different location
- API access might not work as expected

### Solution

**Updated workflow:**

1. **ASK FIRST:**
   ```
   "Do you have fresh scraper data, or should I run a new Apify scrape?"
   ```

2. **CHECK FOR EXISTING DATA:**
   ```bash
   # Look for recent JSON files
   find outputs/ -name "*.json" -mtime -1
   ```

3. **ONLY THEN fetch via API if needed**

### Skill Updates Needed

**SKILL.md Phase 1 should be:**

```markdown
### Phase 1: Data Location Check

1. ASK USER: "Do you have fresh Amazon data from a recent scraper run, or should I pull new data?"

2. IF USER HAS DATA:
   - Ask for file location
   - Read and process immediately

3. IF NEED FRESH DATA:
   - Check for existing recent files in outputs/
   - Only then use Apify API to scrape

4. NEVER waste time trying API endpoints without confirming approach first
```

## General Principles

**Before any data operation:**
- [ ] Ask where data is if not obvious
- [ ] Check for recent files first
- [ ] Confirm approach before executing
- [ ] Don't assume API access works

**Context efficiency:**
- [ ] Be direct - ask questions early
- [ ] Don't retry failed approaches multiple times
- [ ] If blocked, ask user for guidance immediately

## File Organization

**Keep outputs/ clean:**
- No temp scripts (use .gitignore)
- Clear naming: `amazon_products_YYYY-MM-DD.json`
- Separate by purpose: `/data` vs `/research`

## Next Improvements

1. **Add data source detection** - Auto-detect recent JSON files
2. **Better error messages** - "Can't access Apify API - please provide JSON file"
3. **Streamlined flow** - Question → Data → Report (3 steps max)

---

*Issue date: 2026-02-09*
*Status: Skill needs update for efficiency*

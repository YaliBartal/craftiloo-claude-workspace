---
name: daily-prep
description: Quick daily check-in to discover how Claude can help with today's tasks
triggers:
  - start my day
  - daily prep
  - what can you help me with today
  - morning briefing
  - let's plan today
output_location: outputs/data/ (optional save)
---

# Daily Prep

**USE WHEN** user says: "start my day", "daily prep", "what can you help me with today", "morning briefing"

---

## ⚠️ BEFORE YOU START — Read Lessons

**MANDATORY FIRST STEP:** Read `LESSONS.md` in this skill's folder before doing anything else.

1. Read `.claude/skills/daily-prep/LESSONS.md`
2. Check **Known Issues** — plan around these
3. Check **Repeat Errors** — if you encounter one during this run, tell the user immediately: _"⚠️ Repeat issue (×N): [description]"_
4. Apply all past lessons to this run

**Do NOT skip this step.**

---

## What This Does

Helps users discover what Claude can actually do for them by analyzing their to-do list and showing exactly how each task can be assisted.

---

## Process

### 1. Load Context (if exists)

Check and read these files if they exist:
- `context/profile.md`
- `context/projects.md`
- `context/business.md`

Use this to understand their business and preferences.

### 1b. Pull Yesterday's Business Snapshot (from Seller Board)

**Before asking the user about their day, fetch a quick business pulse:**

1. **Fetch the Daily Dashboard report** using WebFetch:
   - URL: `https://app.sellerboard.com/en/automation/reports?id=913d974aa62049cca4493b384553adaf&format=csv&t=9cf6b6e82d14453e89d923b881b333b8`

2. **Extract yesterday's key metrics:**
   - Total Revenue
   - Total Units Sold
   - Net Profit
   - Profit Margin %
   - Ad Spend
   - TACoS (Ad Spend / Total Revenue)

3. **Optionally fetch the Inventory report** to flag stock alerts:
   - URL: `https://app.sellerboard.com/en/automation/reports?id=0b0c4f03962c4066bc2b22db045edcd2&format=csv&t=9cf6b6e82d14453e89d923b881b333b8`
   - Flag any products with **<7 days of stock left**
   - Flag any products with **reorder recommended NOW**

4. **Present the snapshot BEFORE asking about their day:**

```
## Yesterday's Business Pulse

| Metric | Yesterday | 7-Day Avg |
|--------|-----------|-----------|
| Revenue | ${X} | ${X}/day |
| Units | X | X/day |
| Profit | ${X} | ${X}/day |
| Margin | X% | X% |
| Ad Spend | ${X} | ${X}/day |
| TACoS | X% | X% |

**Stock Alerts:** {any low-stock or reorder-now products, or "All good"}
```

5. **If Seller Board fetch fails:** Skip this section silently, proceed with normal daily prep flow.

### 2. Ask One Question

> "What's on your to-do list today?"

Keep it simple. Let them share what they're working on.

### 3. Output Format: Summary First, Then Breakdown

**ALWAYS structure your response in this order:**

#### Part 1: Quick Overview (dopamine hit)

Start with a quick-scan summary table with emojis, showing task + how you help + time saved:

```
## Today's Tasks - Quick Overview

| Task | How I Can Help | Time Saved |
|------|----------------|------------|
| Find new suppliers | 🚀 Full Autopilot | ~2-3 hrs |
| Prep for negotiation call | ⚡ Accelerate | ~30 min |
| Ship orders | ❌ Can't Help | — |
| Update product listings | 💪 Heavy Lifting | ~1 hr |

**Total time I can save you today: ~4 hours**
```

The emojis give that instant visual scan of where you can help most.

#### Part 2: Detailed Breakdown

THEN provide the detailed breakdown for each task.

---

### 4. Help Levels (with emojis)

| Emoji | Level | When to Use |
|-------|-------|-------------|
| 🚀 | **Full Autopilot** | I can do this entirely without their input |
| 💪 | **Heavy Lifting** | I do the hard part, they review/finish |
| ⚡ | **Accelerate** | I speed them up with templates, research, prep |
| 🔧 | **Workflow Candidate** | Can't help now, but we could build a skill |
| ❌ | **Can't Help** | Physical tasks, personal calls, meetings |

**Always use these emojis** in both the summary table AND the detailed breakdown.

### 5. Detailed Breakdown Format

For EACH task, provide:

1. **Help level** (from above)
2. **Exactly what I'll do** (3-4 specific bullets)
3. **Realistic time/effort saved**

**Example breakdown:**

---

**Task: Find new suppliers for product X**

🚀 **Full Autopilot**

Here's what I can do:
- Search Alibaba for suppliers matching your criteria
- Pull pricing, MOQs, shipping terms, and reviews
- Compile into a comparison spreadsheet
- Highlight top 5 based on your priorities

**Time saved:** ~2-3 hours of manual searching

---

**Task: Prep for supplier negotiation call**

⚡ **Accelerate**

Here's what I can do:
- Research typical MOQ negotiation ranges for your category
- Draft 5 key questions to ask
- Create a one-page cheat sheet with talking points

**Time saved:** ~30-45 min of prep work

---

**Task: Ship orders**

❌ **Can't Help**

That's on you! But let me know if you want help with shipping label templates or tracking notifications later.

---

### 7. Keep It Real

- Don't overpromise
- If something takes 2 hours, say 2 hours
- Be specific, not vague ("I can help with research" = bad)
- Show them the actual value

### 8. Optional: Save Plan

After the breakdown, ask:

> "Want me to save this as today's plan?"

If yes, create: `outputs/data/daily-plan-YYYY-MM-DD.md`

---

## Output

- **Format:** Conversational + optional markdown file
- **Location:** `outputs/data/daily-plan-[date].md` (if saved)

---

## ⚠️ AFTER EVERY RUN — Update Lessons (MANDATORY)

**Before presenting final results, update `.claude/skills/daily-prep/LESSONS.md`.**

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

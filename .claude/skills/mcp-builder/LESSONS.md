# Lessons Learned — MCP Builder

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

<!--
### Run: YYYY-MM-DD
**Goals:**
- [ ] Goal 1
- [ ] Goal 2

**Result:** ✅ Success / ⚠️ Partial / ❌ Failed

**What happened:**
- (Describe what went according to plan)

**What didn't work:**
- (Describe any issues, with specifics)

**Is this a repeat error?** Yes/No — if yes, which one from Known Issues?

**Lesson learned:**
- (What to do differently next time)

**Tokens/cost:** ~XX K tokens
-->

### Run: 2026-02-24
**Goals:**
- [x] Build custom Asana MCP server to replace NPM package
- [x] Register 26 tools covering projects, tasks, sections, subtasks, comments, tags, search, dependencies
- [x] Update .mcp.json, CLAUDE.md, folder structure

**Result:** ✅ Success

**What happened:**
- Built `mcp-servers/asana/server.py` following existing server pattern (dotenv loader, rate limiter, httpx async client, formatted output)
- Replaced NPM `@roychri/mcp-server-asana` with custom Python server in .mcp.json
- 26 tools in 8 groups: User (3), Teams (1), Projects (3), Sections (3), Tasks (5), Subtasks (2), Comments (2), Tags (3), Search (1), Dependencies (3)
- Auto-pagination helper for list endpoints
- Full CRUD for tasks and projects
- Updated CLAUDE.md with complete tool table and documentation

**What didn't work:**
- Nothing — clean build

**Is this a repeat error?** No

**Lesson learned:**
- The existing server pattern (notion, slack, datadive) is well-established and easy to replicate
- Asana API is straightforward REST with Bearer token auth — no OAuth dance needed for PAT
- Tool count: always verify with `mcp._tool_manager._tools` after building

**Tokens/cost:** ~30K tokens

---

## Known Issues

_None yet._

---

## Repeat Errors

_None yet._

---

## Resolved Issues

_None yet._

# Craftiloo Automation System

Self-hosted skill runner on GMKtec NucBox M8 (Ubuntu 24.04).
Replaces GitHub Actions with n8n + Python runner + Claude Code CLI (Max plan).

---

## Architecture

```
n8n (scheduler + UI)  →  skill-runner.py (config + logging)  →  claude -p (skill execution)
```

- **n8n** — visual scheduler at http://10.0.0.22:5678, handles cron triggers, error routing, run history
- **skill-runner.py** — reads config.yaml, manages git, enforces timeouts, writes JSON logs
- **Claude Code** — authenticated via Max plan OAuth token, runs skills headlessly

---

## Quick Reference

### Run a skill manually
```bash
python3 ~/workspace/automation/skill-runner.py ppc-daily-health --verbose
```

### Dry run (see config without executing)
```bash
python3 ~/workspace/automation/skill-runner.py daily-market-intel --dry-run
```

### Skip git operations
```bash
python3 ~/workspace/automation/skill-runner.py weekly-ppc-analysis --no-git --verbose
```

### Check latest log for a skill
```bash
cat /var/log/claude/ppc-daily-health-latest.json | python3 -m json.tool
```

### List today's logs
```bash
ls -la /var/log/claude/*$(date +%Y-%m-%d)*.json
```

---

## File Structure

```
automation/
├── config.yaml                 # All skill settings (edit this to configure)
├── skill-runner.py             # Python runner
├── health-check.sh             # Daily Slack health ping
├── setup.sh                    # One-time server setup
├── n8n-workflows/
│   ├── master-scheduler.json   # Main workflow (all triggers)
│   ├── tuesday-chain.json      # 5 skills sequential
│   └── friday-chain.json       # 3 skills sequential
├── logrotate.d/
│   └── claude-skills           # Log rotation config
└── README.md                   # This file
```

---

## Schedule (IST)

| Day | Time | Skill |
|-----|------|-------|
| Daily | 8:00 AM | daily-market-intel |
| Daily | 8:30 AM | ppc-daily-health |
| Monday | 9:00 AM | weekly-ppc-analysis |
| Tuesday | 9:00 AM | ppc-tacos-optimizer |
| | 9:30 AM | ppc-portfolio-summary |
| | 10:00 AM | keyword-rank-optimizer |
| | 10:30 AM | ppc-bid-recommender (report only) |
| | 11:00 AM | ppc-search-term-harvester (report only) |
| Thursday | 9:00 AM | competitor-price-serp-tracker |
| Friday | 9:00 AM | ppc-portfolio-summary |
| | 10:00 AM | ppc-bid-recommender (report only) |
| | 10:30 AM | ppc-search-term-harvester (report only) |
| Sunday | 9:00 AM | brand-analytics-weekly |
| 1st of month | 10:00 AM | ppc-monthly-review |

---

## Exit Codes

| Code | Meaning | What to check |
|------|---------|---------------|
| 0 | Success | All good |
| 1 | Skill failed | Read `claude_output_tail` in log |
| 2 | Timeout | Increase `timeout_minutes` in config.yaml |
| 3 | Git error | Check `git status` for conflicts |
| 4 | Config error | Skill name missing from config.yaml |
| 5 | Lock conflict | Another skill still running |

---

## Adding a New Skill

1. Add a block to `config.yaml`:
   ```yaml
   new-skill-name:
     timeout_minutes: 15
     slack_channel: "#claude-ppc-updates"
   ```

2. Test:
   ```bash
   python3 ~/workspace/automation/skill-runner.py new-skill-name --dry-run
   python3 ~/workspace/automation/skill-runner.py new-skill-name --verbose
   ```

3. Add trigger in n8n: Schedule Trigger → Execute Command → connect to error handling

---

## n8n Setup

### First-time import
1. Open http://10.0.0.22:5678
2. Menu (☰) → Import from File → select `tuesday-chain.json`
3. Note the workflow ID (visible in URL bar)
4. Repeat for `friday-chain.json`
5. Import `master-scheduler.json`
6. Go to Settings → Variables → Add:
   - `SLACK_BOT_TOKEN` = your Slack bot token
   - `TUESDAY_CHAIN_WORKFLOW_ID` = ID from step 3
   - `FRIDAY_CHAIN_WORKFLOW_ID` = ID from step 4
7. Activate the master scheduler workflow (toggle in top-right)

### n8n Environment Variables

| Variable | Value | Purpose |
|----------|-------|---------|
| `SLACK_BOT_TOKEN` | `xoxb-...` | Failure alerts to #claude-alerts |
| `TUESDAY_CHAIN_WORKFLOW_ID` | (auto from import) | Links master → tuesday chain |
| `FRIDAY_CHAIN_WORKFLOW_ID` | (auto from import) | Links master → friday chain |

---

## Troubleshooting

### Skill failed
1. Check n8n Executions tab → click the failed run
2. Read stdout for the JSON summary
3. SSH in → `cat /var/log/claude/{skill}-latest.json | python3 -m json.tool`
4. Re-run manually: `python3 ~/workspace/automation/skill-runner.py {skill} --verbose`

### Server seems down
- Check Slack #claude-alerts for daily health ping
- SSH: `ssh yali@10.0.0.22`
- Docker: `docker ps` (n8n should be listed)

### Git conflicts
```bash
cd ~/workspace
git status
git stash     # if needed
git pull --ff-only origin master
git stash pop # if stashed
```

### Rate limits (Claude Max)
- Increase wait times in n8n chain workflows (2min → 5min)
- Split Tuesday chain: morning (3 skills) + afternoon (2 skills)
- Check `claude_output_tail` in logs for 429 errors

### DST timezone change
Israel switches DST in late March and late October.
Update all n8n cron expressions: UTC+2 (winter) → UTC+3 (summer).
Example: "8:00 AM IST" = `0 6 * * *` in winter, `0 5 * * *` in summer.

---

## Server Setup (one-time)

```bash
sudo bash ~/workspace/automation/setup.sh
```

This creates log directories, installs logrotate, installs pyyaml, and sets up the health check cron.

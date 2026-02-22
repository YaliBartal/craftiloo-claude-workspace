import json
from pathlib import Path

# Load processed data
data_file = Path(r"c:\Users\barta\OneDrive\Documents\Claude_Code_Workspace_TEMPLATE\Claude Code Workspace TEMPLATE\outputs\research\ppc-weekly\data\processed_data_2026-02-20.json")
with open(data_file, 'r') as f:
    data = json.load(f)

portfolios_full = data['portfolio_details']
acct = data['account_metrics']
negate_p1 = data['negate_p1']
negate_p2 = data['negate_p2']
promote_p1 = data['promote_p1']
top_targets_zero = data['top_targets_zero_orders']

# Build appendix sections
appendix = """
---

## Consolidated Action To-Do List

### P1 — Act Now (Highest Impact)

| # | Source | Portfolio | Campaign/Term | Action | Spend at Risk |
|---|--------|-----------|---------------|--------|---------------|
"""

action_count = 1

# Add P1 search term negations
for term, data in negate_p1[:10]:
    primary_campaign = data['campaigns'][0] if data['campaigns'] else 'Unknown'
    portfolio = 'Unknown'
    for port_name, port_data in portfolios_full.items():
        if any(c['name'] == primary_campaign for c in port_data['campaigns']):
            portfolio = port_name
            break

    appendix += f"| {action_count} | Search Term | {portfolio[:20]} | \"{term[:30]}\" | Negate immediately | ${data['spend']:.2f}/week |\n"
    action_count += 1

# Add zero-order campaigns
for port_name, port_data in sorted(portfolios_full.items(), key=lambda x: x[1]['spend'], reverse=True):
    for camp in port_data['campaigns'][:5]:
        if camp['orders'] == 0 and camp['spend'] >= 10:
            appendix += f"| {action_count} | Campaign | {port_name[:20]} | {camp['name'][:30]} | Pause or lower bid -50% | ${camp['spend']:.2f} |\n"
            action_count += 1
            if action_count > 15:
                break
    if action_count > 15:
        break

# Add zero-order targets
for target, campaign, spend, clicks in top_targets_zero[:5]:
    portfolio = 'Check report'
    appendix += f"| {action_count} | Target | {portfolio} | {target[:30]} | Pause or lower bid -40% | ${spend:.2f} |\n"
    action_count += 1

appendix += """
### P2 — Investigate & Adjust

"""

# Add P2 negations
for term, data in negate_p2[:8]:
    appendix += f"- [ ] Review search term \"{term}\" — ${data['spend']:.2f} spend, {data['orders']} orders\n"

# Add high ACoS campaigns
for port_name, port_data in sorted(portfolios_full.items(), key=lambda x: x[1]['acos'], reverse=True)[:3]:
    if port_data['acos'] > 40:
        for camp in port_data['campaigns'][:3]:
            if camp['acos'] > 50:
                appendix += f"- [ ] {port_name} — {camp['name'][:40]} — Lower bids -25%. ACoS {camp['acos']:.1f}%\n"

appendix += """
### P3 — Monitor / Scale

"""

# Add promotions
for term, data in promote_p1[:5]:
    appendix += f"- [ ] Promote \"{term}\" to exact match — {data['orders']} orders, {data['acos']:.1f}% ACoS\n"

# Add scale opportunities
for port_name, port_data in sorted(portfolios_full.items(), key=lambda x: x[1]['acos'])[:3]:
    if port_data['acos'] < 25 and port_data['cvr'] > 12:
        top_camp = port_data['campaigns'][0] if port_data['campaigns'] else None
        if top_camp:
            appendix += f"- [ ] {port_name} — Scale {top_camp['name'][:40]} — {top_camp['acos']:.1f}% ACoS\n"

appendix += """
### Structure Gaps

"""

# Check structure
for port_name, port_data in sorted(portfolios_full.items(), key=lambda x: x[1]['spend'], reverse=True)[:8]:
    if port_data['spend'] < 50:
        continue

    campaign_types = [c['type'] for c in port_data['campaigns']]
    gaps = []
    if 'Auto' not in campaign_types:
        gaps.append('Auto campaign')
    if 'Broad' not in campaign_types and not any('Multi Keyword' in ct for ct in campaign_types):
        gaps.append('Broad/MK campaign')

    if gaps:
        appendix += f"- [ ] {port_name}: Missing {', '.join(gaps)}\n"

appendix += """
---

## Appendix

### A. Portfolio Stage Distribution

**Note:** Portfolio stages require user input. These cannot be auto-determined.

| Stage | Count | Portfolios |
|-------|-------|------------|
| To be determined | All | User should classify each portfolio as Stage 1-4 |

### B. ACoS Distribution

| Range | Count | Portfolios |
|-------|-------|------------|
"""

acos_ranges = {
    '< 25% (Excellent)': [],
    '25-35% (Healthy)': [],
    '35-50% (Above Target)': [],
    '> 50% (Red Flag)': []
}

for port_name, port_data in portfolios_full.items():
    if port_data['spend'] < 50:
        continue
    acos = port_data['acos']
    if acos < 25:
        acos_ranges['< 25% (Excellent)'].append(port_name)
    elif acos < 35:
        acos_ranges['25-35% (Healthy)'].append(port_name)
    elif acos < 50:
        acos_ranges['35-50% (Above Target)'].append(port_name)
    else:
        acos_ranges['> 50% (Red Flag)'].append(port_name)

for range_name, ports in acos_ranges.items():
    port_names = ', '.join(ports[:3]) if ports else 'None'
    if len(ports) > 3:
        port_names += f', +{len(ports)-3} more'
    appendix += f"| {range_name} | {len(ports)} | {port_names} |\n"

appendix += """
### C. Budget Concentration

| Top 3 Portfolios | Spend | % of Total |
|-------------------|-------|------------|
"""

for port_name, port_data in sorted(portfolios_full.items(), key=lambda x: x[1]['spend'], reverse=True)[:3]:
    pct = port_data['spend'] / acct['spend'] * 100
    appendix += f"| {port_name} | ${port_data['spend']:,.2f} | {pct:.1f}% |\n"

top3_pct = sum(p['spend'] for _, p in sorted(portfolios_full.items(), key=lambda x: x[1]['spend'], reverse=True)[:3]) / acct['spend'] * 100

if top3_pct > 70:
    concentration = f"HIGH — Top 3 = {top3_pct:.1f}% of spend. Diversify."
elif top3_pct > 50:
    concentration = f"MODERATE — Top 3 = {top3_pct:.1f}% of spend."
else:
    concentration = f"LOW — Well-distributed spend."

appendix += f"""
**Concentration Risk:** {concentration}

---

## Data Dive Checks Needed

The following campaigns need rank verification before adjusting bids:

"""

# TOS campaigns
checked = 0
for port_name, port_data in sorted(portfolios_full.items(), key=lambda x: x[1]['spend'], reverse=True):
    for camp in port_data['campaigns']:
        if ('TOS' in camp['type'] or 'TOS' in camp['name'].upper()) and camp['spend'] > 30:
            if camp['acos'] > 40:
                appendix += f"- {port_name} — {camp['name'][:55]} — {camp['acos']:.1f}% ACoS, ${camp['spend']:.2f} spend\n"
                checked += 1
        if checked >= 10:
            break
    if checked >= 10:
        break

if checked == 0:
    appendix += "- No high-spend TOS campaigns flagged\n"

appendix += """
---

**END OF REPORT**

*Generated: 2026-02-20*
*Data Window: Feb 08-14, 2026*
*Next Analysis: Week of Feb 22, 2026*
"""

# Append to report
report_path = Path(r"c:\Users\barta\OneDrive\Documents\Claude_Code_Workspace_TEMPLATE\Claude Code Workspace TEMPLATE\outputs\research\ppc-weekly\briefs\weekly-ppc-analysis-2026-02-20.md")
with open(report_path, 'a', encoding='utf-8') as f:
    f.write(appendix)

print(f"Appendix added to report at {report_path}")

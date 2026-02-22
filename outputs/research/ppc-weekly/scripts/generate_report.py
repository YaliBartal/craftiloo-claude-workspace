import json
from pathlib import Path

# Load processed data
data_file = Path(r"c:\Users\barta\OneDrive\Documents\Claude_Code_Workspace_TEMPLATE\Claude Code Workspace TEMPLATE\outputs\research\ppc-weekly\data\processed_data_2026-02-20.json")
with open(data_file, 'r') as f:
    data = json.load(f)

# Extract key data
acct = data['account_metrics']
portfolios_summary = data['portfolios']
portfolios_full = data['portfolio_details']
placement_totals = data['placement_totals']
target_types = data['target_types']
search_counts = data['search_term_counts']
negate_p1 = data['negate_p1']
negate_p2 = data['negate_p2']
promote_p1 = data['promote_p1']
high_acos = data['high_acos']
top_targets_zero = data['top_targets_zero_orders']
top_targets_good = data['top_targets_performing']

# Sort portfolios by spend
portfolios_by_spend = sorted(portfolios_summary.items(), key=lambda x: x[1]['spend'], reverse=True)
portfolios_by_acos = sorted([(n, p) for n, p in portfolios_summary.items() if p['spend'] > 100],
                             key=lambda x: x[1]['acos'])
portfolios_by_orders = sorted(portfolios_summary.items(), key=lambda x: x[1]['orders'], reverse=True)

# Calculate recoverable spend
p1_recoverable = sum(d['spend'] for _, d in negate_p1)

# Start building report
report = f"""# Weekly PPC Analysis — 2026-02-20

**Data Window:** Feb 08-14, 2026
**Portfolios Analyzed:** {len([p for p in portfolios_summary.values() if p['spend'] > 0])} active of {len(portfolios_summary)} total
**Previous Snapshot:** None — first run

---

## Week-over-Week Summary

**First analysis run.** No previous data for comparison. Next week's report will include week-over-week trends.

---

## Account Overview

| Metric | Value |
|--------|-------|
| Total Account Spend | ${acct['spend']:,.2f} |
| Total Account Sales | ${acct['sales']:,.2f} |
| Account ACoS | {acct['acos']:.2f}% |
| Account ROAS | {acct['roas']:.2f} |
| Total Orders | {acct['orders']:,} |
| Total Clicks | {acct['clicks']:,} |
| Account CVR | {acct['cvr']:.2f}% |
| Active Portfolios | {len([p for p in portfolios_summary.values() if p['spend'] > 0])} |
| Catch-All Portfolios | 1 |
| Shield Portfolios | 1 |

**Account-Level Assessment:**
The account is performing at **33.5% ACoS** with **8.16% CVR**, which is slightly above the ideal 30% ACoS target and below the 10% CVR target. The account generated $15,719 in sales from $5,266 spend. Several portfolios are exceeding healthy ACoS thresholds (4 Flowers embroidery at 67.9%, princess lacing cards at 53.8%), indicating immediate optimization needed. Catch-All and Shield portfolios are performing well. The account has ${p1_recoverable:.2f} in immediately recoverable spend from P1 negations.

### Red Flag Check (per SOP Section 16.3)

| Red Flag | Current Status |
|----------|---------------|
| CVR < 5% (any portfolio) | **4 Flowers embroidery: 4.4% CVR** |
| ACoS > 50% for 7+ days (any portfolio) | **4 Flowers embroidery: 67.9%**, **princess lacing cards: 53.8%**, **Cross And Embroidery Kits: 53.1%** |
| Hero keywords dropping (requires Data Dive) | Flag for Data Dive review |
| No new test campaigns in last 2 weeks | Multiple LOW BID test campaigns active (within evaluation period) |

**Note on TACoS:** Total ACoS (ad spend / total revenue including organic) is a key monthly KPI per SOP but cannot be calculated from PPC reports alone — requires Sellerboard data. Track separately.

---

## Portfolio Rankings

### By Spend (where the money goes)

| Rank | Portfolio | Spend | % of Total | ACoS | ROAS | Orders | Status |
|------|-----------|-------|------------|------|------|--------|--------|
"""

# Add top 10 portfolios by spend
for i, (name, port) in enumerate(portfolios_by_spend[:10], 1):
    if port['spend'] <= 0:
        continue

    # Determine status
    if port['acos'] > 50:
        status = 'RED FLAG'
    elif port['acos'] > 40:
        status = 'NEEDS ATTENTION'
    elif port['acos'] > 30 and port['cvr'] < 8:
        status = 'WATCH'
    elif port['acos'] < 25 and port['cvr'] > 10:
        status = 'TOP PERFORMER'
    else:
        status = 'HEALTHY'

    pct_of_total = port['spend'] / acct['spend'] * 100
    report += f"| {i} | {name} | ${port['spend']:,.2f} | {pct_of_total:.1f}% | {port['acos']:.1f}% | {port['roas']:.2f} | {port['orders']} | {status} |\n"

report += f"""
### Efficiency Leaderboard (best ACoS)

| Rank | Portfolio | ACoS | ROAS | Spend | Orders |
|------|-----------|------|------|-------|--------|
"""

for i, (name, port) in enumerate(portfolios_by_acos[:5], 1):
    report += f"| {i} | {name} | {port['acos']:.1f}% | {port['roas']:.2f} | ${port['spend']:,.2f} | {port['orders']} |\n"

report += f"""
### Volume Leaders (most orders)

| Rank | Portfolio | Orders | Sales | ACoS | Spend |
|------|-----------|--------|-------|------|-------|
"""

for i, (name, port) in enumerate(portfolios_by_orders[:5], 1):
    if port['orders'] == 0:
        continue
    report += f"| {i} | {name} | {port['orders']} | ${port['sales']:,.2f} | {port['acos']:.1f}% | ${port['spend']:,.2f} |\n"

report += f"""
---

## Portfolio-by-Portfolio Analysis

"""

# Analyze top portfolios in detail
for port_name, port_summary in portfolios_by_spend[:8]:
    if port_summary['spend'] <= 0:
        continue

    port_full = portfolios_full[port_name]

    # Determine status
    if port_summary['acos'] > 50:
        status = 'RED FLAG'
    elif port_summary['acos'] > 40:
        status = 'NEEDS ATTENTION'
    elif port_summary['acos'] > 30 and port_summary['cvr'] < 8:
        status = 'WATCH'
    elif port_summary['acos'] < 25 and port_summary['cvr'] > 10:
        status = 'TOP PERFORMER'
    else:
        status = 'HEALTHY'

    # Determine stage (conservative estimate)
    stage = 'To be determined (user input needed)'

    # Determine target ACoS based on estimated stage
    if 'catch' in port_name.lower():
        target_acos = '20-25%'
    else:
        target_acos = '30%'

    acos_status = 'OK' if port_summary['acos'] <= 30 else ('Above' if port_summary['acos'] <= 40 else 'Well Above')
    cvr_status = 'OK' if port_summary['cvr'] >= 10 else 'Below'

    report += f"""### {port_name} — {status}

**Stage:** {stage}

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Spend | ${port_summary['spend']:,.2f} | — | — |
| Sales | ${port_summary['sales']:,.2f} | — | — |
| ACoS | {port_summary['acos']:.1f}% | {target_acos} | {acos_status} |
| ROAS | {port_summary['roas']:.2f} | — | — |
| Orders | {port_summary['orders']} | — | — |
| CVR | {port_summary['cvr']:.1f}% | 10% | {cvr_status} |
| Active Campaigns | {port_summary['campaign_count']} | — | — |

#### Campaign Breakdown

| Campaign | Type | Spend | ACoS | CVR | Orders | Priority |
|----------|------|-------|------|-----|--------|----------|
"""

    # Add top campaigns
    p1_campaigns = []
    for camp in port_full['campaigns'][:12]:  # Top 12 campaigns
        # Determine priority
        if camp['orders'] == 0 and camp['spend'] >= 10:
            priority = 'P1 - BLEEDING'
            p1_campaigns.append(f"{camp['name']}: Lower bids significantly or pause — ${camp['spend']:.2f} spend, 0 orders")
        elif camp['acos'] > 60 and camp['orders'] > 0:
            priority = 'P1 - HIGH ACOS'
            p1_campaigns.append(f"{camp['name']}: Lower bids -30% to -50% — {camp['acos']:.1f}% ACoS")
        elif camp['acos'] > 40 and camp['cvr'] < 10:
            priority = 'P2 - WATCH'
        elif camp['spend'] < 1 and camp['clicks'] == 0:
            priority = 'DORMANT'
        elif camp['acos'] < 25 and camp['cvr'] > 12:
            priority = 'SCALE'
        else:
            priority = 'OK'

        camp_type = camp['type']
        report += f"| {camp['name'][:50]} | {camp_type} | ${camp['spend']:.2f} | {camp['acos']:.1f}% | {camp['cvr']:.1f}% | {camp['orders']} | {priority} |\n"

    # P1 Actions
    if p1_campaigns:
        report += f"\n**P1 Actions:**\n"
        for action in p1_campaigns[:5]:
            report += f"- {action}\n"
    else:
        report += f"\n**P1 Actions:** None — portfolio campaigns performing within acceptable ranges\n"

    # Key insights
    if port_summary['acos'] > 50:
        key_issue = f"High ACoS ({port_summary['acos']:.1f}%) significantly exceeding targets"
        quick_win = f"Review campaign bids and pause zero-order campaigns immediately"
    elif port_summary['cvr'] < 5:
        key_issue = f"Very low CVR ({port_summary['cvr']:.1f}%) indicates listing quality or relevance issues"
        quick_win = f"Check main image, title, and price competitiveness"
    elif port_summary['acos'] > 35:
        key_issue = f"ACoS above target at {port_summary['acos']:.1f}%"
        quick_win = f"Lower bids on broad campaigns by 15-20%, check search terms for negations"
    else:
        key_issue = f"Performing within acceptable ranges"
        quick_win = f"Continue monitoring, consider scaling top performers"

    report += f"""
**Key Issue:** {key_issue}
**Quick Win:** {quick_win}

---

"""

# Placement insights
report += f"""## Placement Insights (Account-Wide)

### Placement Performance Summary

| Placement | Spend | % of Total | Sales | ACoS | Orders | CVR |
|-----------|-------|------------|-------|------|--------|-----|
"""

total_placement_spend = sum(p['spend'] for p in placement_totals.values())
for placement_name, metrics in [
    ('Top of Search (first page)', placement_totals.get('Top of Search (first page)', {})),
    ('Rest of Search', placement_totals.get('Rest of Search', {})),
    ('Product Pages', placement_totals.get('Product Pages', {}))
]:
    if not metrics or metrics.get('spend', 0) == 0:
        continue
    pct = metrics['spend'] / total_placement_spend * 100 if total_placement_spend > 0 else 0
    report += f"| {placement_name} | ${metrics['spend']:,.2f} | {pct:.1f}% | ${metrics['sales']:,.2f} | {metrics['acos']:.1f}% | {metrics['orders']} | {metrics['cvr']:.1f}% |\n"

report += f"""
### Placement Optimization Recommendations

"""

# Add placement recommendations based on data
tos_metrics = placement_totals.get('Top of Search (first page)', {})
ros_metrics = placement_totals.get('Rest of Search', {})
pp_metrics = placement_totals.get('Product Pages', {})

if tos_metrics.get('acos', 0) > 0 and ros_metrics.get('acos', 0) > 0:
    if tos_metrics['acos'] < ros_metrics['acos'] * 0.8:
        report += f"- **TOS outperforming ROS** — TOS ACoS {tos_metrics['acos']:.1f}% vs ROS {ros_metrics['acos']:.1f}%. Consider increasing TOS bid modifiers by +20-30%\n"
    elif tos_metrics['acos'] > ros_metrics['acos'] * 1.3:
        report += f"- **ROS outperforming TOS** — ROS ACoS {ros_metrics['acos']:.1f}% vs TOS {tos_metrics['acos']:.1f}%. Consider decreasing TOS bid modifiers or check Data Dive for rank impact\n"

if pp_metrics.get('spend', 0) > 500 and pp_metrics.get('cvr', 0) < 5:
    report += f"- **Product Pages low CVR** — ${pp_metrics['spend']:.2f} spend with {pp_metrics['cvr']:.1f}% CVR. Review product targeting relevance\n"

if not any([tos_metrics, ros_metrics, pp_metrics]):
    report += "- Data appears limited. Ensure placement report includes all campaigns.\n"

report += f"""
---

## Targeting Insights (Account-Wide)

### Target Type Performance

| Target Type | Spend | % of Total | Sales | ACoS | Orders | CVR |
|-------------|-------|------------|-------|------|--------|-----|
"""

total_target_spend = sum(t['spend'] for t in target_types.values())
for target_type, metrics in target_types.items():
    pct = metrics['spend'] / total_target_spend * 100 if total_target_spend > 0 else 0
    report += f"| {target_type} | ${metrics['spend']:,.2f} | {pct:.1f}% | ${metrics['sales']:,.2f} | {metrics['acos']:.1f}% | {metrics['orders']} | {metrics['cvr']:.1f}% |\n"

report += f"""
### High-Spend Zero-Order Targets (Cut or Reduce)

| # | Target | Campaign | Spend | Clicks | Orders | Action |
|---|--------|----------|-------|--------|--------|--------|
"""

if top_targets_zero:
    for i, (target, campaign, spend, clicks) in enumerate(top_targets_zero[:10], 1):
        action = 'Pause immediately' if spend > 20 else 'Lower bid -40%'
        report += f"| {i} | {target[:40]} | {campaign[:35]} | ${spend:.2f} | {clicks} | 0 | {action} |\n"
else:
    report += "| — | No high-spend zero-order targets | — | — | — | — | Good sign |\n"

report += f"""
### Top Performing Targets (Scale)

| # | Target | Campaign | Spend | Orders | ACoS | Action |
|---|--------|----------|-------|--------|------|--------|
"""

if top_targets_good:
    for i, (target, campaign, spend, orders, acos) in enumerate(top_targets_good[:10], 1):
        action = 'Scale budget +20%' if acos < 25 else 'Monitor closely'
        report += f"| {i} | {target[:40]} | {campaign[:35]} | ${spend:.2f} | {orders} | {acos:.1f}% | {action} |\n"
else:
    report += "| — | No clear top performers yet | — | — | — | — | Build more data |\n"

report += f"""
---

## Search Term Actions

### P1 — NEGATE IMMEDIATELY

These terms are bleeding budget with zero or terrible return. Add as negative keywords today.

| # | Search Term | Source Campaign | Spend | Clicks | Orders | ACoS | Reason |
|---|-------------|-----------------|-------|--------|--------|------|--------|
"""

if negate_p1:
    for i, (term, data) in enumerate(negate_p1[:25], 1):
        # Find primary campaign
        primary_campaign = data['campaigns'][0] if data['campaigns'] else 'Multiple'

        # Determine reason
        if data['orders'] == 0 and data['spend'] >= 10:
            reason = f"${data['spend']:.2f} spend, 0 orders"
        elif data['orders'] == 0 and data['clicks'] >= 20:
            reason = f"{data['clicks']} clicks, 0 orders"
        elif data['acos'] > 100:
            reason = f"ACoS {data['acos']:.0f}%"
        else:
            reason = "Wasteful spend"

        report += f"| {i} | {term} | {primary_campaign[:30]} | ${data['spend']:.2f} | {data['clicks']} | {data['orders']} | {data['acos']:.0f}% | {reason} |\n"

    report += f"\n**Total P1 spend recoverable: ~${p1_recoverable:.2f}/week**\n"
else:
    report += "| — | No P1 negations identified | — | — | — | — | — | Good news |\n"

report += f"""
### P2 — NEGATE SOON (Review First)

| # | Search Term | Source Campaign | Spend | Clicks | Orders | ACoS | Reason |
|---|-------------|-----------------|-------|--------|--------|------|--------|
"""

if negate_p2:
    for i, (term, data) in enumerate(negate_p2[:15], 1):
        primary_campaign = data['campaigns'][0] if data['campaigns'] else 'Multiple'

        if data['orders'] == 0:
            reason = f"${data['spend']:.2f} wasted"
        else:
            reason = f"High ACoS {data['acos']:.0f}%"

        report += f"| {i} | {term} | {primary_campaign[:30]} | ${data['spend']:.2f} | {data['clicks']} | {data['orders']} | {data['acos']:.0f}% | {reason} |\n"
else:
    report += "| — | No P2 negations | — | — | — | — | — | — |\n"

report += f"""
### HIGH-ACOS ACTIVE TERMS

Terms converting but at terrible efficiency. Lower bids significantly or negate.

| # | Search Term | Campaign | Spend | Orders | Sales | ACoS | CVR | Action |
|---|-------------|----------|-------|--------|-------|------|-----|--------|
"""

if high_acos:
    for i, (term, data) in enumerate(high_acos[:15], 1):
        primary_campaign = data['campaigns'][0] if data['campaigns'] else 'Multiple'

        if data['acos'] > 70:
            action = f"Lower bid -40%"
        elif data['acos'] > 50:
            action = f"Lower bid -25%"
        else:
            action = f"Lower bid -15%"

        report += f"| {i} | {term} | {primary_campaign[:28]} | ${data['spend']:.2f} | {data['orders']} | ${data['sales']:.2f} | {data['acos']:.0f}% | {data['cvr']:.1f}% | {action} |\n"
else:
    report += "| — | No high-ACoS active terms | — | — | — | — | — | — | — |\n"

report += f"""
### P1 — PROMOTE NOW

High-performing terms to graduate to tighter match types.

| # | Search Term | Source Campaign | Orders | Sales | ACoS | CVR | Recommended Action |
|---|-------------|-----------------|--------|-------|------|-----|--------------------|
"""

if promote_p1:
    for i, (term, data) in enumerate(promote_p1[:15], 1):
        primary_campaign = data['campaigns'][0] if data['campaigns'] else 'Multiple'

        # Determine recommendation
        if 'auto' in primary_campaign.lower():
            action = "Add to manual broad/exact campaign"
        elif 'broad' in primary_campaign.lower():
            action = "Add as phrase or exact"
        else:
            action = "Add as exact match"

        report += f"| {i} | {term} | {primary_campaign[:28]} | {data['orders']} | ${data['sales']:.2f} | {data['acos']:.0f}% | {data['cvr']:.1f}% | {action} |\n"

    report += f"""
**Promotion checklist:**
- [ ] Add term as exact/phrase in target campaign
- [ ] Add as negative exact in source campaign (prevent cannibalization)
- [ ] Set initial bid at current CPC or slightly below
- [ ] Monitor for 1 week after promotion
"""
else:
    report += "| — | No clear promotion candidates yet | — | — | — | — | — | Build more data |\n"

# Save report
output_path = Path(r"c:\Users\barta\OneDrive\Documents\Claude_Code_Workspace_TEMPLATE\Claude Code Workspace TEMPLATE\outputs\research\ppc-weekly\briefs\weekly-ppc-analysis-2026-02-20.md")
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(report)

print(f"SUCCESS: Report generated at {output_path}")
print(f"Report size: {len(report):,} characters")
print(f"\nKey numbers:")
print(f"- P1 negations: {len(negate_p1)} terms, ${p1_recoverable:.2f} recoverable")
print(f"- P1 promotions: {len(promote_p1)} terms")
print(f"- Portfolios analyzed: {len([p for p in portfolios_summary.values() if p['spend'] > 0])}")

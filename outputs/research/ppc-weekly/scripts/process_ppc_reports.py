"""
Weekly PPC Analysis Script
Processes 4 Seller Central reports and generates comprehensive analysis
"""

import csv
import json
from datetime import datetime
from collections import defaultdict
from pathlib import Path

# File paths
BASE_DIR = Path(__file__).parent.parent
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "briefs"
SNAPSHOT_DIR = BASE_DIR / "snapshots"

# Input files
CAMPAIGN_FILE = INPUT_DIR / "Sponsored_Products_Campaign_report.csv"
SEARCH_TERM_FILE = INPUT_DIR / "Sponsored_Products_Search_term_report (1).csv"
PLACEMENT_FILE = INPUT_DIR / "Sponsored_Products_Placement_report.csv"
TARGETING_FILE = INPUT_DIR / "Sponsored_Products_Targeting_report.csv"

def safe_float(value, default=0.0):
    """Safely convert to float"""
    if value is None or value == '':
        return default
    try:
        # Remove $ and % signs
        clean = str(value).replace('$', '').replace('%', '').replace(',', '').strip()
        return float(clean) if clean else default
    except:
        return default

def safe_int(value, default=0):
    """Safely convert to int"""
    return int(safe_float(value, default))

def classify_campaign(name, targeting_type):
    """Classify campaign by type"""
    name_lower = name.lower()

    if targeting_type == "Automatic targeting":
        return "Auto"
    elif "shield" in name_lower or ("brand" in name_lower and "defense" in name_lower):
        return "Brand Shield"
    elif " sk " in name_lower or name_lower.endswith(" sk"):
        return "Single Keyword (SK)"
    elif " mk " in name_lower or name_lower.endswith(" mk"):
        return "Multi Keyword (MK)"
    elif "pat" in name_lower or "pt" in name_lower or "product target" in name_lower:
        return "Product Targeting"
    elif "broad" in name_lower or "spm" in name_lower:
        return "Broad"
    elif "tos push" in name_lower or "tos" in name_lower:
        return "TOS Push"
    elif "video" in name_lower or "sb" in name_lower or "sbv" in name_lower:
        return "Video"
    elif "sd" in name_lower:
        return "Sponsored Display"
    elif "catch" in name_lower:
        return "Catch-all"
    else:
        return "Manual"

def load_campaign_data():
    """Load and process campaign report"""
    portfolios = defaultdict(lambda: {
        'campaigns': [],
        'total_spend': 0,
        'total_sales': 0,
        'total_orders': 0,
        'total_clicks': 0,
        'total_impressions': 0
    })

    total_spend = 0
    total_sales = 0
    total_orders = 0

    with open(CAMPAIGN_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Skip paused/archived campaigns
            if row['Status'] != 'ENABLED':
                continue

            # Skip campaigns with no activity
            spend = safe_float(row['Spend'])
            impressions = safe_int(row['Impressions'])
            if spend == 0 and impressions == 0:
                continue

            portfolio = row['Portfolio name'] if row['Portfolio name'] else 'No Portfolio'
            campaign_name = row['Campaign Name']

            clicks = safe_int(row['Clicks'])
            orders = safe_int(row['7 Day Total Orders (#)'])
            sales = safe_float(row['7 Day Total Sales '])
            acos = safe_float(row['Total Advertising Cost of Sales (ACOS) '])
            ctr = safe_float(row['Click-Thru Rate (CTR)'])
            cpc = safe_float(row['Cost Per Click (CPC)'])
            cvr = (orders / clicks * 100) if clicks > 0 else 0

            campaign_type = classify_campaign(campaign_name, row['Targeting Type'])

            campaign = {
                'name': campaign_name,
                'type': campaign_type,
                'targeting': row['Targeting Type'],
                'budget': safe_float(row['Budget Amount']),
                'spend': spend,
                'sales': sales,
                'acos': acos,
                'orders': orders,
                'clicks': clicks,
                'impressions': impressions,
                'ctr': ctr,
                'cpc': cpc,
                'cvr': cvr,
                'start_date': row['Start Date']
            }

            portfolios[portfolio]['campaigns'].append(campaign)
            portfolios[portfolio]['total_spend'] += spend
            portfolios[portfolio]['total_sales'] += sales
            portfolios[portfolio]['total_orders'] += orders
            portfolios[portfolio]['total_clicks'] += clicks
            portfolios[portfolio]['total_impressions'] += impressions

            total_spend += spend
            total_sales += sales
            total_orders += orders

    # Calculate portfolio-level metrics
    for portfolio in portfolios.values():
        portfolio['acos'] = (portfolio['total_spend'] / portfolio['total_sales'] * 100) if portfolio['total_sales'] > 0 else 0
        portfolio['roas'] = (portfolio['total_sales'] / portfolio['total_spend']) if portfolio['total_spend'] > 0 else 0
        portfolio['cvr'] = (portfolio['total_orders'] / portfolio['total_clicks'] * 100) if portfolio['total_clicks'] > 0 else 0
        # Sort campaigns by spend
        portfolio['campaigns'].sort(key=lambda x: x['spend'], reverse=True)

    account_acos = (total_spend / total_sales * 100) if total_sales > 0 else 0
    account_roas = (total_sales / total_spend) if total_spend > 0 else 0

    return dict(portfolios), {
        'spend': total_spend,
        'sales': total_sales,
        'orders': total_orders,
        'acos': account_acos,
        'roas': account_roas
    }

def generate_report(portfolios, account_totals):
    """Generate the markdown analysis report"""
    today = datetime.now().strftime('%Y-%m-%d')

    report = f"""# Weekly PPC Analysis — {today}

**Data Window:** Feb 08, 2026 - Feb 14, 2026
**Portfolios Analyzed:** {len(portfolios)} active
**Previous Snapshot:** None — first run

---

## Week-over-Week Summary

**First analysis run.** No previous data for comparison. Next week's report will include week-over-week trends.

---

## Account Overview

| Metric | Value |
|--------|-------|
| Total Account Spend | ${account_totals['spend']:.2f} |
| Total Account Sales | ${account_totals['sales']:.2f} |
| Account ACoS | {account_totals['acos']:.1f}% |
| Account ROAS | {account_totals['roas']:.2f} |
| Total Orders | {account_totals['orders']} |
| Active Portfolios | {len(portfolios)} |

**Account-Level Assessment:** Account is active across {len(portfolios)} portfolios. Total ad spend of ${account_totals['spend']:.2f} generating ${account_totals['sales']:.2f} in sales at {account_totals['acos']:.1f}% ACoS. Overall account efficiency is {"healthy" if account_totals['acos'] < 35 else "above target" if account_totals['acos'] < 50 else "concerning"}.

### Red Flag Check (per SOP Section 16.3)

| Red Flag | Current Status |
|----------|---------------|
| CVR < 5% (any portfolio) | {', '.join([p for p, data in portfolios.items() if data['cvr'] < 5]) or "None"} |
| ACoS > 50% for 7+ days (any portfolio) | {', '.join([p for p, data in portfolios.items() if data['acos'] > 50]) or "None"} |
| Hero keywords dropping (requires Data Dive) | Flag for Data Dive review |
| No new test campaigns in last 2 weeks | Manual review required |

**Note on TACoS:** Total ACoS (ad spend / total revenue including organic) is a key monthly KPI per SOP but cannot be calculated from PPC reports alone — requires Sellerboard data. Track separately.

---

## Portfolio Rankings

### By Spend (where the money goes)

| Rank | Portfolio | Spend | % of Total | ACoS | ROAS | Orders | Status |
|------|-----------|-------|------------|------|------|--------|--------|
"""

    # Sort portfolios by spend
    sorted_portfolios = sorted(portfolios.items(), key=lambda x: x[1]['total_spend'], reverse=True)

    for idx, (portfolio_name, data) in enumerate(sorted_portfolios[:10], 1):
        pct_spend = (data['total_spend'] / account_totals['spend'] * 100) if account_totals['spend'] > 0 else 0
        status = "HEALTHY" if data['acos'] < 30 else "WATCH" if data['acos'] < 40 else "NEEDS ATTENTION" if data['acos'] < 50 else "RED FLAG"
        report += f"| {idx} | {portfolio_name} | ${data['total_spend']:.2f} | {pct_spend:.1f}% | {data['acos']:.1f}% | {data['roas']:.2f} | {data['total_orders']} | {status} |\n"

    report += "\n---\n\n## Portfolio-by-Portfolio Analysis\n\n"

    # Detailed portfolio analysis
    for portfolio_name, data in sorted_portfolios:
        status = "HEALTHY" if data['acos'] < 30 else "WATCH" if data['acos'] < 40 else "NEEDS ATTENTION" if data['acos'] < 50 else "RED FLAG"

        report += f"""### {portfolio_name} — {status}

**Stage:** To be determined by user

| Metric | Value | Status |
|--------|-------|--------|
| Spend | ${data['total_spend']:.2f} | — |
| Sales | ${data['total_sales']:.2f} | — |
| ACoS | {data['acos']:.1f}% | {"OK" if data['acos'] < 35 else "Above Target"} |
| ROAS | {data['roas']:.2f} | — |
| Orders | {data['total_orders']} | — |
| CVR | {data['cvr']:.1f}% | {"OK" if data['cvr'] >= 10 else "Below Target"} |
| Active Campaigns | {len(data['campaigns'])} | — |

#### Top Campaigns by Spend

| Campaign | Type | Spend | ACoS | CVR | Orders |
|----------|------|-------|------|-----|--------|
"""

        for campaign in data['campaigns'][:5]:  # Top 5 campaigns
            report += f"| {campaign['name'][:50]} | {campaign['type']} | ${campaign['spend']:.2f} | {campaign['acos']:.1f}% | {campaign['cvr']:.1f}% | {campaign['orders']} |\n"

        # Quick assessment
        high_acos_campaigns = [c for c in data['campaigns'] if c['acos'] > 40 and c['spend'] > 10]
        zero_order_campaigns = [c for c in data['campaigns'] if c['orders'] == 0 and c['spend'] > 10]

        report += "\n**P1 Actions:**\n"
        if high_acos_campaigns:
            report += f"- {len(high_acos_campaigns)} campaigns with ACoS >40% — review for bid reduction\n"
        if zero_order_campaigns:
            report += f"- {len(zero_order_campaigns)} campaigns with  spend and 0 orders — investigate or pause\n"
        if not high_acos_campaigns and not zero_order_campaigns:
            report += "- No urgent actions identified\n"

        report += "\n---\n\n"

    report += """
## Consolidated Action To-Do List

### P1 — Act Now (Highest Impact)

*Full analysis requires search term, placement, and targeting data processing.*

| # | Source | Portfolio | Campaign/Term | Action | Spend at Risk |
|---|--------|-----------|---------------|--------|---------------|
"""

    # Add high-priority campaign issues
    action_num = 1
    for portfolio_name, data in sorted_portfolios:
        for campaign in data['campaigns']:
            if campaign['orders'] == 0 and campaign['spend'] > 20:
                report += f"| {action_num} | Campaign | {portfolio_name} | {campaign['name'][:40]} | Pause — spend, 0 orders | ${campaign['spend']:.2f} |\n"
                action_num += 1
            elif campaign['acos'] > 100 and campaign['spend'] > 10:
                report += f"| {action_num} | Campaign | {portfolio_name} | {campaign['name'][:40]} | Lower bids -40% — ACoS {campaign['acos']:.0f}% | ${campaign['spend']:.2f} |\n"
                action_num += 1

    report += """

### P2 — Investigate & Adjust
- Full search term analysis required for detailed recommendations

### P3 — Monitor / Scale
- Full targeting analysis required for scale opportunities

---

## Notes

This is a **partial analysis** based on campaign-level data only.

**For complete analysis, the following are still being processed:**
- Search term negation/promotion recommendations (largest savings opportunity)
- Placement optimization insights (TOS vs ROS vs Product Pages)
- Target-level performance analysis
- Detailed structure check against SOP requirements

**Next Run:** All 4 reports will be fully integrated for comprehensive analysis.
"""

    return report

def main():
    """Main execution"""
    print("Loading campaign data...")
    portfolios, account_totals = load_campaign_data()

    print(f"Found {len(portfolios)} active portfolios")
    print(f"Total spend: ${account_totals['spend']:.2f}")
    print(f"Total sales: ${account_totals['sales']:.2f}")
    print(f"Account ACoS: {account_totals['acos']:.1f}%")

    print("\nGenerating report...")
    report = generate_report(portfolios, account_totals)

    # Save report
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime('%Y-%m-%d')
    output_file = OUTPUT_DIR / f"weekly-ppc-analysis-{today}.md"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n✓ Report saved to: {output_file}")
    print("\nDone!")

if __name__ == "__main__":
    main()

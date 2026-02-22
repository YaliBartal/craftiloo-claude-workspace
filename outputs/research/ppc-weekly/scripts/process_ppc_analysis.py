import csv
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# File paths
base_path = Path(r"c:\Users\barta\OneDrive\Documents\Claude_Code_Workspace_TEMPLATE\Claude Code Workspace TEMPLATE\outputs\research\ppc-weekly\input")
campaign_file = base_path / "Sponsored_Products_Campaign_report.csv"
search_term_file = base_path / "Sponsored_Products_Search_term_report (1).csv"
placement_file = base_path / "Sponsored_Products_Placement_report.csv"
targeting_file = base_path / "Sponsored_Products_Targeting_report.csv"

def safe_float(value, default=0.0):
    """Safely convert string to float"""
    if not value or value == '':
        return default
    try:
        return float(str(value).replace('$', '').replace(',', '').replace('%', ''))
    except:
        return default

def safe_int(value, default=0):
    """Safely convert string to int"""
    if not value or value == '':
        return default
    try:
        return int(str(value).replace(',', ''))
    except:
        return default

def classify_campaign(campaign_name, targeting_type):
    """Classify campaign type based on name and targeting"""
    name_lower = campaign_name.lower()

    if targeting_type == 'Automatic targeting':
        return 'Auto'
    elif 'shield' in name_lower or 'brand' in name_lower and 'defense' in name_lower:
        return 'Brand Shield'
    elif ' sk ' in name_lower or campaign_name.endswith(' SK'):
        return 'Single Keyword (SK)'
    elif ' mk ' in name_lower or 'multi' in name_lower:
        return 'Multi Keyword (MK)'
    elif 'broad' in name_lower:
        return 'Broad'
    elif ' pt ' in name_lower or 'product target' in name_lower:
        return 'Product Targeting (PAT)'
    elif 'tos' in name_lower or 'top of search' in name_lower:
        return 'TOS Push'
    elif 'catch' in name_lower:
        return 'Catch-all'
    else:
        return 'Manual targeting'

# Load all campaigns
print("Loading campaign data...")
campaigns = []
with open(campaign_file, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        campaigns.append(row)

# Filter enabled campaigns with activity
enabled_campaigns = []
for c in campaigns:
    if c.get('Status') == 'ENABLED':
        spend = safe_float(c.get('Spend', '0'))
        clicks = safe_int(c.get('Clicks', '0'))
        if spend > 0 or clicks > 0:
            enabled_campaigns.append(c)

print(f"Loaded {len(enabled_campaigns)} ENABLED campaigns with activity")

# Calculate account-level metrics
account_metrics = {
    'spend': sum(safe_float(c.get('Spend')) for c in enabled_campaigns),
    'sales': sum(safe_float(c.get('7 Day Total Sales ')) for c in enabled_campaigns),
    'orders': sum(safe_int(c.get('7 Day Total Orders (#)')) for c in enabled_campaigns),
    'clicks': sum(safe_int(c.get('Clicks')) for c in enabled_campaigns),
    'impressions': sum(safe_int(c.get('Impressions')) for c in enabled_campaigns),
}
account_metrics['acos'] = (account_metrics['spend'] / account_metrics['sales'] * 100) if account_metrics['sales'] > 0 else 0
account_metrics['roas'] = (account_metrics['sales'] / account_metrics['spend']) if account_metrics['spend'] > 0 else 0
account_metrics['cvr'] = (account_metrics['orders'] / account_metrics['clicks'] * 100) if account_metrics['clicks'] > 0 else 0

# Group campaigns by portfolio
portfolios = defaultdict(lambda: {
    'campaigns': [],
    'spend': 0,
    'sales': 0,
    'orders': 0,
    'clicks': 0,
    'impressions': 0
})

for c in enabled_campaigns:
    portfolio = c.get('Portfolio name', 'No Portfolio')
    spend = safe_float(c.get('Spend'))
    sales = safe_float(c.get('7 Day Total Sales '))
    orders = safe_int(c.get('7 Day Total Orders (#)'))
    clicks = safe_int(c.get('Clicks'))
    impressions = safe_int(c.get('Impressions'))

    # Classify campaign
    campaign_type = classify_campaign(c['Campaign Name'], c.get('Targeting Type', ''))

    campaign_data = {
        'name': c['Campaign Name'],
        'type': campaign_type,
        'spend': spend,
        'sales': sales,
        'orders': orders,
        'clicks': clicks,
        'impressions': impressions,
        'ctr': safe_float(c.get('Click-Thru Rate (CTR)')),
        'cpc': safe_float(c.get('Cost Per Click (CPC)')),
        'budget': safe_float(c.get('Budget Amount')),
        'targeting': c.get('Targeting Type', ''),
        'bidding': c.get('Bidding strategy', ''),
        'acos': safe_float(c.get('Total Advertising Cost of Sales (ACOS) ')),
        'roas': safe_float(c.get('Total Return on Advertising Spend (ROAS)')),
    }

    if clicks > 0:
        campaign_data['cvr'] = (orders / clicks * 100)
    else:
        campaign_data['cvr'] = 0

    portfolios[portfolio]['campaigns'].append(campaign_data)
    portfolios[portfolio]['spend'] += spend
    portfolios[portfolio]['sales'] += sales
    portfolios[portfolio]['orders'] += orders
    portfolios[portfolio]['clicks'] += clicks
    portfolios[portfolio]['impressions'] += impressions

# Calculate portfolio metrics
for portfolio in portfolios.values():
    portfolio['acos'] = (portfolio['spend'] / portfolio['sales'] * 100) if portfolio['sales'] > 0 else 0
    portfolio['roas'] = (portfolio['sales'] / portfolio['spend']) if portfolio['spend'] > 0 else 0
    portfolio['cvr'] = (portfolio['orders'] / portfolio['clicks'] * 100) if portfolio['clicks'] > 0 else 0
    portfolio['campaign_count'] = len(portfolio['campaigns'])

    # Sort campaigns by spend
    portfolio['campaigns'].sort(key=lambda x: x['spend'], reverse=True)

# Load placement data
print("Loading placement data...")
placements = defaultdict(lambda: defaultdict(lambda: {
    'impressions': 0, 'clicks': 0, 'spend': 0, 'orders': 0, 'sales': 0
}))

with open(placement_file, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        campaign = row.get('Campaign Name', '')
        placement = row.get('Placement', '')

        placements[campaign][placement]['impressions'] += safe_int(row.get('Impressions'))
        placements[campaign][placement]['clicks'] += safe_int(row.get('Clicks'))
        placements[campaign][placement]['spend'] += safe_float(row.get('Spend'))
        placements[campaign][placement]['orders'] += safe_int(row.get('7 Day Total Orders (#)'))
        placements[campaign][placement]['sales'] += safe_float(row.get('7 Day Total Sales '))

# Calculate placement metrics
placement_totals = {'Top of Search (first page)': {'spend': 0, 'sales': 0, 'orders': 0, 'clicks': 0},
                   'Rest of Search': {'spend': 0, 'sales': 0, 'orders': 0, 'clicks': 0},
                   'Product Pages': {'spend': 0, 'sales': 0, 'orders': 0, 'clicks': 0}}

for campaign_placements in placements.values():
    for placement_name, metrics in campaign_placements.items():
        if placement_name in placement_totals:
            placement_totals[placement_name]['spend'] += metrics['spend']
            placement_totals[placement_name]['sales'] += metrics['sales']
            placement_totals[placement_name]['orders'] += metrics['orders']
            placement_totals[placement_name]['clicks'] += metrics['clicks']

for placement in placement_totals.values():
    placement['acos'] = (placement['spend'] / placement['sales'] * 100) if placement['sales'] > 0 else 0
    placement['cvr'] = (placement['orders'] / placement['clicks'] * 100) if placement['clicks'] > 0 else 0

# Load targeting data
print("Loading targeting data...")
targets = []
with open(targeting_file, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        spend = safe_float(row.get('Spend'))
        if spend >= 5:  # Only include targets with meaningful spend
            targets.append({
                'campaign': row.get('Campaign Name', ''),
                'target': row.get('Targeting', ''),
                'match_type': row.get('Match Type', ''),
                'spend': spend,
                'orders': safe_int(row.get('7 Day Total Orders (#)')),
                'sales': safe_float(row.get('7 Day Total Sales ')),
                'clicks': safe_int(row.get('Clicks')),
                'impressions': safe_int(row.get('Impressions')),
                'acos': safe_float(row.get('Total Advertising Cost of Sales (ACOS) ')),
            })

targets.sort(key=lambda x: x['spend'], reverse=True)

# Calculate target type totals
target_types = defaultdict(lambda: {'spend': 0, 'sales': 0, 'orders': 0, 'clicks': 0})
for t in targets:
    match = t['match_type'].lower()
    if 'broad' in match:
        target_types['Keyword (Broad)']['spend'] += t['spend']
        target_types['Keyword (Broad)']['sales'] += t['sales']
        target_types['Keyword (Broad)']['orders'] += t['orders']
        target_types['Keyword (Broad)']['clicks'] += t['clicks']
    elif 'phrase' in match:
        target_types['Keyword (Phrase)']['spend'] += t['spend']
        target_types['Keyword (Phrase)']['sales'] += t['sales']
        target_types['Keyword (Phrase)']['orders'] += t['orders']
        target_types['Keyword (Phrase)']['clicks'] += t['clicks']
    elif 'exact' in match:
        target_types['Keyword (Exact)']['spend'] += t['spend']
        target_types['Keyword (Exact)']['sales'] += t['sales']
        target_types['Keyword (Exact)']['orders'] += t['orders']
        target_types['Keyword (Exact)']['clicks'] += t['clicks']
    else:
        target_types['Product/ASIN']['spend'] += t['spend']
        target_types['Product/ASIN']['sales'] += t['sales']
        target_types['Product/ASIN']['orders'] += t['orders']
        target_types['Product/ASIN']['clicks'] += t['clicks']

for tt in target_types.values():
    tt['acos'] = (tt['spend'] / tt['sales'] * 100) if tt['sales'] > 0 else 0
    tt['cvr'] = (tt['orders'] / tt['clicks'] * 100) if tt['clicks'] > 0 else 0

# Load search terms
print("Loading search terms (this may take a moment)...")
search_terms = {}
with open(search_term_file, 'r', encoding='latin-1', errors='ignore') as f:
    reader = csv.DictReader(f)
    for row in reader:
        term = row.get('Customer Search Term', '').strip()
        if not term:
            continue

        spend = safe_float(row.get('Spend'))
        if spend < 3:  # Focus on terms with $3+ spend per SOP
            continue

        if term not in search_terms:
            search_terms[term] = {
                'campaigns': [],
                'spend': 0,
                'sales': 0,
                'orders': 0,
                'clicks': 0,
                'impressions': 0,
            }

        search_terms[term]['campaigns'].append(row.get('Campaign Name', ''))
        search_terms[term]['spend'] += spend
        search_terms[term]['sales'] += safe_float(row.get('7 Day Total Sales '))
        search_terms[term]['orders'] += safe_int(row.get('7 Day Total Orders (#)'))
        search_terms[term]['clicks'] += safe_int(row.get('Clicks'))
        search_terms[term]['impressions'] += safe_int(row.get('Impressions'))

# Calculate search term metrics
for term, data in search_terms.items():
    data['acos'] = (data['spend'] / data['sales'] * 100) if data['sales'] > 0 else 0
    data['cvr'] = (data['orders'] / data['clicks'] * 100) if data['clicks'] > 0 else 0
    data['ctr'] = (data['clicks'] / data['impressions'] * 100) if data['impressions'] > 0 else 0

# Classify search terms
negate_p1 = []
negate_p2 = []
promote_p1 = []
promote_p2 = []
high_acos = []
opportunities = []

competitor_brands = ['kraftlab', 'fanzbo', 'krafun', 'joyin', 'hapinest', 'alex']

for term, data in search_terms.items():
    term_lower = term.lower()

    # Check for competitor brands
    is_competitor = any(brand in term_lower for brand in competitor_brands)

    # P1 NEGATE
    if data['orders'] == 0 and data['spend'] >= 10:
        negate_p1.append((term, data, 'P1 - $10+ spend, 0 orders'))
    elif data['orders'] == 0 and data['clicks'] >= 20:
        negate_p1.append((term, data, 'P1 - 20+ clicks, 0 orders'))
    elif data['orders'] > 0 and data['acos'] > 100 and data['clicks'] >= 3:
        negate_p1.append((term, data, f'P1 - ACoS {data["acos"]:.1f}% (>100%)'))
    # P2 NEGATE
    elif data['orders'] == 0 and 5 <= data['spend'] < 10:
        negate_p2.append((term, data, 'P2 - $5-10 spend, 0 orders'))
    elif data['orders'] > 0 and data['acos'] > 70 and data['clicks'] >= 5:
        negate_p2.append((term, data, f'P2 - ACoS {data["acos"]:.1f}% (>70%)'))
    # P1 PROMOTE
    elif data['orders'] >= 3 and data['acos'] < 40 and not is_competitor:
        promote_p1.append((term, data, f'P1 - {data["orders"]} orders, {data["acos"]:.1f}% ACoS'))
    # P2 PROMOTE
    elif data['orders'] >= 2 and data['acos'] < 30 and data['cvr'] > 15:
        promote_p2.append((term, data, f'P2 - {data["orders"]} orders, {data["cvr"]:.1f}% CVR'))
    # HIGH ACOS
    elif data['orders'] > 0 and 40 < data['acos'] <= 100:
        high_acos.append((term, data))
    # OPPORTUNITIES
    elif data['cvr'] > 15 and data['acos'] < 50:
        opportunities.append((term, data))

# Sort lists by spend
negate_p1.sort(key=lambda x: x[1]['spend'], reverse=True)
negate_p2.sort(key=lambda x: x[1]['spend'], reverse=True)
promote_p1.sort(key=lambda x: x[1]['spend'], reverse=True)
promote_p2.sort(key=lambda x: x[1]['spend'], reverse=True)
high_acos.sort(key=lambda x: x[1]['spend'], reverse=True)
opportunities.sort(key=lambda x: x[1]['cvr'], reverse=True)

# Save processed data
output_data = {
    'date': '2026-02-20',
    'data_window': 'Feb 08-14, 2026',
    'account_metrics': account_metrics,
    'portfolios': {name: {k: v for k, v in data.items() if k != 'campaigns'}
                   for name, data in portfolios.items()},
    'portfolio_details': dict(portfolios),
    'placement_totals': placement_totals,
    'target_types': dict(target_types),
    'search_term_counts': {
        'total': len(search_terms),
        'negate_p1': len(negate_p1),
        'negate_p2': len(negate_p2),
        'promote_p1': len(promote_p1),
        'promote_p2': len(promote_p2),
        'high_acos': len(high_acos),
        'opportunities': len(opportunities),
    },
    'negate_p1': [(t, d) for t, d, r in negate_p1[:30]],  # Top 30
    'negate_p2': [(t, d) for t, d, r in negate_p2[:20]],  # Top 20
    'promote_p1': [(t, d) for t, d, r in promote_p1[:20]],  # Top 20
    'promote_p2': [(t, d) for t, d, r in promote_p2[:15]],  # Top 15
    'high_acos': [(t, d) for t, d in high_acos[:20]],  # Top 20
    'top_targets_zero_orders': [(t['target'], t['campaign'], t['spend'], t['clicks'])
                                 for t in targets if t['orders'] == 0 and t['spend'] >= 10][:15],
    'top_targets_performing': [(t['target'], t['campaign'], t['spend'], t['orders'], t['acos'])
                                for t in targets if t['orders'] >= 3 and t['acos'] < 35][:15],
}

output_path = Path(r"c:\Users\barta\OneDrive\Documents\Claude_Code_Workspace_TEMPLATE\Claude Code Workspace TEMPLATE\outputs\research\ppc-weekly\data\processed_data_2026-02-20.json")
with open(output_path, 'w') as f:
    json.dump(output_data, f, indent=2)

print(f"\n✓ Processed data saved to {output_path}")
print(f"\nSummary:")
print(f"- Portfolios analyzed: {len(portfolios)}")
print(f"- Search terms analyzed (>$3 spend): {len(search_terms)}")
print(f"- P1 negations: {len(negate_p1)} (${sum(d['spend'] for _, d, _ in negate_p1):.2f} recoverable)")
print(f"- P1 promotions: {len(promote_p1)}")
print(f"- High-spend zero-order targets: {len([t for t in targets if t['orders'] == 0 and t['spend'] >= 10])}")

"""Cross-reference search terms in unprotected catch-all campaigns (4-6)
against the negative keyword lists from mature campaigns (1-3)."""

import json, sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

BASE = "c:/Users/barta/OneDrive/Documents/Claude_Code_Workspace_TEMPLATE/Claude Code Workspace TEMPLATE"

with open(f'{BASE}/outputs/research/ppc-weekly/data/search-terms-14d-2026-03-02.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Map campaign names
UNPROTECTED = {
    'CATCH ALL NGO - OLD': 'Cmp4 (NGO)',
    'Catch All - Auto - 0.15 - incrementum': 'Cmp5 (0.15)',
    'catch all - auto - 0.19 incrumentum': 'Cmp6 (0.19)',
}

# Load negative keyword lists from saved files
neg_files = {
    '1': f'{BASE}/outputs/research/ppc-agent/portfolio-action-plan/data/neg-campaign-1.json',
    '2': f'{BASE}/outputs/research/ppc-agent/portfolio-action-plan/data/neg-campaign-2.json',
    '3': f'{BASE}/outputs/research/ppc-agent/portfolio-action-plan/data/neg-campaign-3.json',
}

neg_sets = {}
for key, path in neg_files.items():
    with open(path, 'r', encoding='utf-8') as f:
        neg_data = json.load(f)
    neg_sets[key] = set(t.lower().strip() for t in neg_data if t.strip())

all_negatives = neg_sets['1'] | neg_sets['2'] | neg_sets['3']

neg_in_2plus = set()
for term in all_negatives:
    count = sum(term in neg_sets[k] for k in ['1', '2', '3'])
    if count >= 2:
        neg_in_2plus.add(term)

print(f'Total unique negatives across campaigns 1-3: {len(all_negatives)}')
print(f'Negatives appearing in 2+ campaigns (high confidence): {len(neg_in_2plus)}')
print()

# Filter for unprotected campaigns
unprotected_terms = []
for row in data:
    cn = row.get('campaignName', '')
    if cn in UNPROTECTED:
        unprotected_terms.append({
            'campaign': UNPROTECTED[cn],
            'searchTerm': row.get('searchTerm', ''),
            'cost': float(row.get('cost', 0)),
            'sales': float(row.get('sales7d', 0)),
            'orders': int(row.get('purchases7d', 0)),
            'clicks': int(row.get('clicks', 0)),
            'impressions': int(row.get('impressions', 0)),
        })

print(f'Search terms in unprotected campaigns (4-6): {len(unprotected_terms)}')
print()

# Aggregate by search term
agg = defaultdict(lambda: {'cost': 0, 'sales': 0, 'orders': 0, 'clicks': 0, 'impressions': 0, 'campaigns': set()})
for row in unprotected_terms:
    key = row['searchTerm'].lower().strip()
    agg[key]['cost'] += row['cost']
    agg[key]['sales'] += row['sales']
    agg[key]['orders'] += row['orders']
    agg[key]['clicks'] += row['clicks']
    agg[key]['impressions'] += row['impressions']
    agg[key]['campaigns'].add(row['campaign'])

# Split
would_negate = []
safe_terms = []
for term, stats in agg.items():
    in_neg = term in neg_in_2plus
    acos = (stats['cost'] / stats['sales'] * 100) if stats['sales'] > 0 else float('inf')
    cvr = (stats['orders'] / stats['clicks'] * 100) if stats['clicks'] > 0 else 0
    entry = {
        'term': term,
        'cost': stats['cost'],
        'sales': stats['sales'],
        'orders': stats['orders'],
        'clicks': stats['clicks'],
        'impressions': stats['impressions'],
        'acos': acos,
        'cvr': cvr,
        'in_negative_list': in_neg,
        'campaigns': ', '.join(sorted(stats['campaigns']))
    }
    if in_neg:
        would_negate.append(entry)
    else:
        safe_terms.append(entry)

would_negate.sort(key=lambda x: x['cost'], reverse=True)
safe_terms.sort(key=lambda x: x['cost'], reverse=True)

# Summary
total_spend = sum(s['cost'] for s in agg.values())
neg_spend = sum(e['cost'] for e in would_negate)
neg_sales = sum(e['sales'] for e in would_negate)
neg_orders = sum(e['orders'] for e in would_negate)
safe_spend = sum(e['cost'] for e in safe_terms)
safe_sales = sum(e['sales'] for e in safe_terms)
safe_orders = sum(e['orders'] for e in safe_terms)

print(f'=== SUMMARY (14-day: Feb 17 - Mar 2) ===')
print(f'Total spend in campaigns 4-6: ${total_spend:.2f}')
print()
print(f'WOULD-BE-NEGATED terms (in 2+ mature neg lists):')
print(f'  Count: {len(would_negate)} search terms')
print(f'  Spend: ${neg_spend:.2f} ({neg_spend/total_spend*100:.1f}%)')
print(f'  Sales: ${neg_sales:.2f}')
print(f'  Orders: {neg_orders}')
neg_acos = neg_spend/neg_sales*100 if neg_sales > 0 else float('inf')
print(f'  Blended ACoS: {neg_acos:.1f}%')
print()
print(f'SAFE terms (not in neg lists):')
print(f'  Count: {len(safe_terms)} search terms')
print(f'  Spend: ${safe_spend:.2f} ({safe_spend/total_spend*100:.1f}%)')
print(f'  Sales: ${safe_sales:.2f}')
print(f'  Orders: {safe_orders}')
safe_acos = safe_spend/safe_sales*100 if safe_sales > 0 else float('inf')
print(f'  Blended ACoS: {safe_acos:.1f}%')
print()

# Converting negated terms (orders > 0) - THE KEY DATA
converting = [e for e in would_negate if e['orders'] > 0]
converting.sort(key=lambda x: x['orders'], reverse=True)

print(f'=== CONVERTING TERMS THAT WOULD BE NEGATED ({len(converting)} terms) ===')
print(f'These terms are in the neg lists BUT are generating orders in campaigns 4-6:')
print()
print(f'| # | Search Term | 14d Spend | 14d Sales | Orders | ACoS | CVR | Clicks |')
print(f'|---|-------------|-----------|-----------|--------|------|-----|--------|')
for i, e in enumerate(converting, 1):
    acos_str = f'{e["acos"]:.1f}%' if e['acos'] != float('inf') else 'INF'
    print(f'| {i} | {e["term"][:50]} | ${e["cost"]:.2f} | ${e["sales"]:.2f} | {e["orders"]} | {acos_str} | {e["cvr"]:.1f}% | {e["clicks"]} |')

conv_spend = sum(e['cost'] for e in converting)
conv_sales = sum(e['sales'] for e in converting)
conv_orders = sum(e['orders'] for e in converting)
print()
print(f'Converting negated totals: ${conv_spend:.2f} spend, ${conv_sales:.2f} sales, {conv_orders} orders')
if conv_sales > 0:
    print(f'Converting negated ACoS: {conv_spend/conv_sales*100:.1f}%')
print()

# Zero-order negated terms (pure waste)
zero_order = [e for e in would_negate if e['orders'] == 0]
zero_order.sort(key=lambda x: x['cost'], reverse=True)
zero_spend = sum(e['cost'] for e in zero_order)
print(f'=== ZERO-ORDER NEGATED TERMS (top 20 by spend) ===')
print(f'Total: {len(zero_order)} terms, ${zero_spend:.2f} pure waste in 14 days')
print()
print(f'| # | Search Term | 14d Spend | Clicks | Impressions |')
print(f'|---|-------------|-----------|--------|-------------|')
for i, e in enumerate(zero_order[:20], 1):
    print(f'| {i} | {e["term"][:50]} | ${e["cost"]:.2f} | {e["clicks"]} | {e["impressions"]} |')

print()
# Also show top safe terms
print(f'=== TOP 20 SAFE TERMS (not negated, by spend) ===')
print(f'| # | Search Term | 14d Spend | 14d Sales | Orders | ACoS | CVR | Clicks |')
print(f'|---|-------------|-----------|-----------|--------|------|-----|--------|')
for i, e in enumerate(safe_terms[:20], 1):
    acos_str = f'{e["acos"]:.1f}%' if e['acos'] != float('inf') else 'INF'
    print(f'| {i} | {e["term"][:50]} | ${e["cost"]:.2f} | ${e["sales"]:.2f} | {e["orders"]} | {acos_str} | {e["cvr"]:.1f}% | {e["clicks"]} |')

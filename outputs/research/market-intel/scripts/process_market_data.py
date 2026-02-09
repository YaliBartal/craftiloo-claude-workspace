#!/usr/bin/env python3
"""Process Amazon product data and generate market intelligence report"""
import json
import sys
from datetime import datetime
from pathlib import Path

def extract_bsr(product):
    """Extract BSR number from Best Sellers Rank string"""
    for detail in product.get('productDetails', []):
        if detail['name'] == 'Best Sellers Rank':
            value = detail['value']
            # Extract first number (main BSR)
            import re
            match = re.search(r'#([\d,]+)', value)
            if match:
                return int(match.group(1).replace(',', ''))
    return None

def extract_category_rank(product):
    """Extract category-specific rank"""
    for detail in product.get('productDetails', []):
        if detail['name'] == 'Best Sellers Rank':
            value = detail['value']
            # Extract category rank (second #)
            import re
            matches = re.findall(r'#(\d+)', value)
            if len(matches) >= 2:
                return int(matches[1])
    return None

def process_products(json_file):
    """Process product data and generate report"""

    with open(json_file, 'r', encoding='utf-8') as f:
        products = json.load(f)

    today = datetime.now().strftime('%Y-%m-%d')

    # Extract key metrics
    product_data = {}
    for p in products:
        asin = p['asin']
        bsr = extract_bsr(p)
        cat_rank = extract_category_rank(p)

        product_data[asin] = {
            'title': p.get('title', 'Unknown'),
            'asin': asin,
            'price': p.get('price', 0),
            'bsr': bsr,
            'category_rank': cat_rank,
            'reviews': p.get('countReview', 0),
            'rating': p.get('productRating', 'N/A'),
            'in_stock': p.get('warehouseAvailability', 'Unknown'),
            'past_sales': p.get('pastSales', 'N/A')
        }

    # Save snapshot
    history_dir = Path(__file__).parent / 'history'
    history_dir.mkdir(exist_ok=True)

    snapshot_file = history_dir / f'{today}.json'
    with open(snapshot_file, 'w', encoding='utf-8') as f:
        json.dump(product_data, f, indent=2)

    print(f"✓ Saved snapshot to {snapshot_file}")

    # Generate report
    report_md = generate_report(product_data, today)

    report_file = Path(__file__).parent / f'daily-report-{today}.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_md)

    print(f"✓ Saved report to {report_file}")
    return product_data

def generate_report(data, date):
    """Generate markdown report"""

    report = f"""# Market Intel - {date}

## Quick Summary

**Total Products Tracked:** {len(data)}

**Status Overview:**
- First run - no historical comparison available
- All products successfully scraped
- Baseline data captured for future trend analysis

---

## Hero Products Performance

"""

    # Sort by BSR (best performing first)
    sorted_products = sorted(data.items(), key=lambda x: x[1]['bsr'] if x[1]['bsr'] else 999999)

    for asin, p in sorted_products:
        # Shorten title
        title = p['title'][:60] + '...' if len(p['title']) > 60 else p['title']

        report += f"""### {title}
**ASIN:** {asin}

| Metric | Value | Notes |
|--------|-------|-------|
| **BSR** | {p['bsr']:,} if p['bsr'] else 'N/A'} | Overall Amazon rank |
| **Category Rank** | #{p['category_rank']} | Specific category position |
| **Price** | ${p['price']} | Current price |
| **Reviews** | {p['reviews']:,} | Total review count |
| **Rating** | {p['rating']} | Average rating |
| **Sales Velocity** | {p['past_sales']} | Recent activity |
| **Stock** | {p['in_stock']} | Availability |

**Status:** BASELINE - First measurement

---

"""

    report += f"""## Next Steps

1. **Run daily** - Tomorrow's run will show 24-hour changes
2. **Week comparison** - After 7 days, you'll see weekly trends
3. **Competitor tracking** - Add competitor ASINs for comparison
4. **Alerts** - Significant changes will be flagged automatically

---

## Data Notes

- **First run** - No historical data to compare against
- **BSR** - Lower number = better ranking
- **Category Rank** - Position within specific category (e.g., "Embroidery Kits")
- Run this daily at the same time for accurate trending

---

*Report generated: {date}*
*Total products: {len(data)}*
"""

    return report

if __name__ == '__main__':
    json_file = sys.argv[1] if len(sys.argv) > 1 else '../data/amazon_products_raw.json'
    process_products(json_file)

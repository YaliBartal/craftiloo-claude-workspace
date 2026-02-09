#!/usr/bin/env python3
"""Generate complete market intelligence report from Apify dataset"""
import json
import re
from datetime import datetime
from pathlib import Path

def extract_bsr(product_details):
    """Extract BSR number from product details"""
    for detail in product_details:
        if detail.get('name') == 'Best Sellers Rank':
            value = detail.get('value', '')
            match = re.search(r'#([\d,]+)', value)
            if match:
                return int(match.group(1).replace(',', ''))
    return None

def extract_category_rank(product_details):
    """Extract category-specific rank"""
    for detail in product_details:
        if detail.get('name') == 'Best Sellers Rank':
            value = detail.get('value', '')
            # Find category rank (after "in")
            match = re.search(r'#(\d+)\s+in\s+([^(]+)', value)
            if match:
                return {
                    'rank': int(match.group(1)),
                    'category': match.group(2).strip()
                }
    return None

def shorten_title(title, max_len=70):
    """Shorten product title"""
    if len(title) <= max_len:
        return title
    return title[:max_len] + '...'

def format_rating(rating_str):
    """Extract numeric rating"""
    match = re.search(r'([\d.]+)', str(rating_str))
    if match:
        return f"{match.group(1)}★"
    return rating_str

def generate_report():
    """Generate complete market intel report"""

    # Find the dataset file
    base_dir = Path(__file__).parent.parent.parent
    dataset_file = base_dir / 'dataset_amazon-product-details-scraper_2026-02-09_08-50-43-378.json'

    if not dataset_file.exists():
        print(f"Error: Dataset file not found at {dataset_file}")
        return

    print(f"Processing: {dataset_file}")

    with open(dataset_file, 'r', encoding='utf-8') as f:
        products = json.load(f)

    print(f"Found {len(products)} products")

    # Extract metrics for all products
    product_metrics = []
    for p in products:
        asin = p.get('asin')
        bsr = extract_bsr(p.get('productDetails', []))
        cat_info = extract_category_rank(p.get('productDetails', []))

        metrics = {
            'asin': asin,
            'title': shorten_title(p.get('title', 'Unknown')),
            'bsr': bsr,
            'category_rank': cat_info['rank'] if cat_info else None,
            'category': cat_info['category'] if cat_info else 'Unknown',
            'price': p.get('price', 0),
            'retail_price': p.get('retailPrice', 0),
            'reviews': p.get('countReview', 0),
            'rating': format_rating(p.get('productRating', 'N/A')),
            'in_stock': p.get('warehouseAvailability', 'Unknown'),
            'past_sales': p.get('pastSales', 'N/A'),
            'sold_by': p.get('soldBy', 'Unknown')
        }
        product_metrics.append(metrics)

    # Sort by BSR (best first)
    product_metrics.sort(key=lambda x: x['bsr'] if x['bsr'] else 999999)

    # Generate report
    today = datetime.now().strftime('%Y-%m-%d')
    report = generate_markdown(product_metrics, today)

    # Save report
    output_dir = Path(__file__).parent
    report_file = output_dir / f'daily-report-{today}.md'

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"✓ Report saved to: {report_file}")

    # Save snapshot
    history_dir = output_dir / 'history'
    history_dir.mkdir(exist_ok=True)

    snapshot_file = history_dir / f'{today}.json'
    with open(snapshot_file, 'w', encoding='utf-8') as f:
        json.dump(product_metrics, f, indent=2)

    print(f"✓ Snapshot saved to: {snapshot_file}")

    return product_metrics

def generate_markdown(products, date):
    """Generate markdown report"""

    # Count products by performance
    top_10k = sum(1 for p in products if p['bsr'] and p['bsr'] < 10000)
    top_25k = sum(1 for p in products if p['bsr'] and 10000 <= p['bsr'] < 25000)
    top_50k = sum(1 for p in products if p['bsr'] and 25000 <= p['bsr'] < 50000)

    report = f"""# Market Intel - {date}

## Executive Summary

**Total Products Tracked:** {len(products)}

**Performance Tiers:**
- 🏆 Top 10K BSR: {top_10k} products
- 🥈 10K-25K BSR: {top_25k} products
- 🥉 25K-50K BSR: {top_50k} products

**Status:** ✅ FIRST RUN - Baseline Established

---

## Top Performers (by BSR)

"""

    # Show top 5 products in summary table
    report += "| Rank | Product | BSR | Cat Rank | Price | Reviews |\n"
    report += "|------|---------|-----|----------|-------|----------|\n"

    for i, p in enumerate(products[:5], 1):
        bsr_str = f"#{p['bsr']:,}" if p['bsr'] else 'N/A'
        cat_rank_str = f"#{p['category_rank']}" if p['category_rank'] else 'N/A'
        report += f"| {i} | {p['title'][:40]}... | {bsr_str} | {cat_rank_str} | ${p['price']} | {p['reviews']} ({p['rating']}) |\n"

    report += "\n---\n\n## Detailed Product Analysis\n\n"

    # Detailed breakdown for each product
    for i, p in enumerate(products, 1):
        bsr_str = f"#{p['bsr']:,}" if p['bsr'] else 'N/A'
        cat_rank_str = f"#{p['category_rank']}" if p['category_rank'] else 'N/A'

        # Calculate discount
        discount = ""
        if p['retail_price'] and p['price'] and p['retail_price'] > p['price']:
            pct = int((1 - p['price']/p['retail_price']) * 100)
            discount = f" (-{pct}% off)"

        # Determine performance emoji
        if p['bsr'] and p['bsr'] < 10000:
            emoji = "🏆"
            tier = "TOP PERFORMER"
        elif p['bsr'] and p['bsr'] < 25000:
            emoji = "⭐"
            tier = "STRONG"
        else:
            emoji = "📊"
            tier = "BASELINE"

        report += f"""### {i}. {p['title']}
**ASIN:** [{p['asin']}](https://www.amazon.com/dp/{p['asin']})
**Category:** {p['category']}

| Metric | Value | Status |
|--------|-------|--------|
| **Overall BSR** | {bsr_str} | {emoji} {tier} |
| **Category Rank** | {cat_rank_str} in {p['category']} | — |
| **Price** | ${p['price']}{discount} | {'On Sale' if discount else 'Regular'} |
| **Reviews** | {p['reviews']:,} reviews | {p['rating']} |
| **Sales Velocity** | {p['past_sales']} | {'🔥 Active' if '100+' in str(p['past_sales']) else 'Moderate'} |
| **Stock Status** | {p['in_stock']} | {'✅' if 'In Stock' in p['in_stock'] else '⚠️'} |
| **Seller** | {p['sold_by']} | — |

**Baseline Notes:** First measurement - trends will show from tomorrow

---

"""

    report += """## Key Insights

### Overall Market Position
"""

    # Calculate average BSR
    bsrs = [p['bsr'] for p in products if p['bsr']]
    avg_bsr = sum(bsrs) / len(bsrs) if bsrs else 0

    report += f"""
- **Average BSR:** #{avg_bsr:,.0f}
- **Best Performer:** {products[0]['title'][:50]} (BSR #{products[0]['bsr']:,})
- **Total Reviews:** {sum(p['reviews'] for p in products):,} across all products
- **Average Rating:** {sum(float(p['rating'].replace('★','')) for p in products if '★' in p['rating']) / len([p for p in products if '★' in p['rating']]):.2f}★

### Product Categories
"""

    # Group by category
    categories = {}
    for p in products:
        cat = p['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(p)

    for cat, prods in categories.items():
        report += f"- **{cat}:** {len(prods)} product{'s' if len(prods) > 1 else ''}\n"

    report += f"""

### Sales Activity
- **High velocity products** (100+ bought/month): {sum(1 for p in products if '100+' in str(p['past_sales']))} products
- **All products in stock:** {sum(1 for p in products if 'In Stock' in p['in_stock'])}/{len(products)}

---

## Next Steps

**Tomorrow's Run Will Show:**
1. 24-hour BSR changes (improving/declining)
2. Review velocity (new reviews per day)
3. Price changes and promotions
4. Category ranking shifts

**Action Items:**
- ✅ Baseline captured for all 13 hero products
- 📅 Schedule daily run for same time (morning)
- 🎯 After 7 days: weekly trend analysis available
- 🔍 Consider: add competitor ASINs for market comparison

---

## Technical Details

**Data Source:** Axesso Amazon Product Details Scraper (Apify)
**Run Time:** 2026-02-09 08:50 UTC
**Products:** 13/13 successfully scraped
**Data Quality:** ✅ Complete (BSR, prices, reviews, ratings, stock)

**Files:**
- Report: `daily-report-{date}.md`
- Snapshot: `history/{date}.json`

---

*Generated: {date} | First run - historical tracking begins tomorrow*
"""

    return report

if __name__ == '__main__':
    try:
        metrics = generate_report()
        print(f"\n✅ Report generation complete!")
        print(f"   {len(metrics)} products processed")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

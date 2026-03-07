"""
Fetch DataDive competitor data for 11 niches using urllib (no external deps).
"""
import os
import json
import time
import urllib.request
import urllib.parse
from pathlib import Path

# Load .env
env_file = Path(r'C:\Users\Dell\OneDrive\מסמכים\craftiloo-claude-workspace\.env')
with open(env_file, encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, _, v = line.partition('=')
            os.environ.setdefault(k.strip(), v.strip())

API_KEY = os.environ.get('DATADIVE_API_KEY', '')
BASE_URL = 'https://api.datadive.tools'
RATE_DELAY = 1.1  # seconds between requests

HERO_ASINS = {
    'B08DDJCQKF', 'B0F6YTG1CH', 'B09X55KL2C', 'B0DC69M3YD',
    'B09WQSBZY7', 'B096MYBLS1', 'B08FYH13CL', 'B0F8R652FX',
    'B0F8DG32H5', 'B09THLVFZK', 'B07D6D95NG', 'B0FQC7YFX6',
    'B09HVSLBS6'
}

NICHES = [
    ('u1y83aQfmK', 'Kids Cross Stitch Kit'),
    ('gfot2FZUBU', 'Embroidery Stitch Practice Kit'),
    ('Er21lin0KC', 'Beginners Embroidery Kit for Kids'),
    ('RmbSD3OH6t', 'Sewing Kit for Kids'),
    ('3qbggwOhO2', 'Latch Hook Kits for Kids'),
    ('AY4AlnSj9g', 'Mini Perler Beads'),
    ('O6b4XATpTj', 'Loom Knitting'),
    ('Aw4EQhG6bP', 'Lacing Cards for Kids'),
    ('5IGkCmOM0h', 'Needlepoint Pouch Kit'),
    ('kZRreyE7kJ', 'Cross Stitch Kits (broad)'),
    ('WFV3TE3beK', 'Fuse Beads'),
]


def api_get(path, params=None):
    url = BASE_URL + path
    if params:
        url += '?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        'x-api-key': API_KEY,
        'Accept': 'application/json',
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        return {'error': f'HTTP {e.code}: {body[:200]}'}
    except Exception as e:
        return {'error': str(e)}


def compress_competitor(raw):
    """Extract only needed fields, omit nulls."""
    out = {}

    # ASIN
    asin = raw.get('asin') or raw.get('ASIN') or raw.get('parentAsin') or raw.get('id')
    if asin:
        out['asin'] = asin

    # Hero flag
    if asin and asin in HERO_ASINS:
        out['is_hero'] = True

    # Brand / title
    brand = raw.get('brand') or raw.get('brandName')
    title = raw.get('title') or raw.get('productTitle') or raw.get('name')
    if brand:
        out['brand'] = brand
    elif title:
        out['brand'] = title[:60]

    # BSR
    bsr = raw.get('bsr') or raw.get('bestSellerRank') or raw.get('salesRank')
    if bsr is not None:
        out['bsr'] = int(bsr)

    # Sales (monthly JS estimate)
    sales = raw.get('monthlySales') or raw.get('sales') or raw.get('estimatedSales') or raw.get('unitsSold')
    if sales is not None:
        out['sales'] = int(sales)

    # Revenue (monthly JS estimate)
    revenue = raw.get('monthlyRevenue') or raw.get('revenue') or raw.get('estimatedRevenue')
    if revenue is not None:
        out['revenue'] = int(revenue)

    # Price
    price = raw.get('price') or raw.get('currentPrice') or raw.get('buyBoxPrice')
    if price is not None:
        out['price'] = float(price)

    # Rating
    rating = raw.get('rating') or raw.get('averageRating') or raw.get('stars')
    if rating is not None:
        out['rating'] = float(rating)

    # Reviews
    reviews = raw.get('reviewCount') or raw.get('reviews') or raw.get('numberOfReviews') or raw.get('ratingsTotal')
    if reviews is not None:
        out['reviews'] = int(reviews)

    # P1 keywords
    p1 = raw.get('kwRankedOnP1') or raw.get('p1Keywords') or raw.get('keywordsOnPage1') or raw.get('organicP1Count')
    if p1 is not None:
        out['p1_keywords'] = int(p1)

    return out


def main():
    result = {
        'niches': {},
        'hero_ratings_reviews': {},
        'errors': [],
        '_raw_sample': {}  # store one raw sample to understand structure
    }

    first_raw_saved = False

    for i, (niche_id, label) in enumerate(NICHES):
        print(f'[{i+1}/11] Fetching: {label} ({niche_id})...')

        if i > 0:
            time.sleep(RATE_DELAY)

        # Try the competitors endpoint
        data = api_get(f'/niches/{niche_id}/competitors', params={'pageSize': 4, 'sortBy': 'sales', 'sortOrder': 'desc'})

        if isinstance(data, dict) and 'error' in data:
            # Try alternate params
            data = api_get(f'/niches/{niche_id}/competitors', params={'page_size': 4})
            if isinstance(data, dict) and 'error' in data:
                result['errors'].append({'niche': niche_id, 'label': label, 'error': data['error']})
                print(f'  ERROR: {data["error"]}')
                continue

        # Save one raw sample
        if not first_raw_saved:
            result['_raw_sample'][niche_id] = data
            first_raw_saved = True

        # Extract competitor list from response
        competitors_raw = []
        if isinstance(data, list):
            competitors_raw = data[:4]
        elif isinstance(data, dict):
            # Try common wrapper keys
            for key in ['competitors', 'data', 'items', 'results', 'products']:
                if key in data and isinstance(data[key], list):
                    competitors_raw = data[key][:4]
                    break
            if not competitors_raw:
                # Dump the keys for debugging
                print(f'  Response keys: {list(data.keys())}')
                result['errors'].append({'niche': niche_id, 'label': label, 'error': f'Unexpected structure: {list(data.keys())}'})
                continue

        print(f'  Got {len(competitors_raw)} competitors')

        # Compress
        compressed = []
        for raw in competitors_raw:
            if isinstance(raw, dict):
                c = compress_competitor(raw)
                if c.get('asin'):
                    compressed.append(c)
                    # Update hero ratings/reviews
                    asin = c['asin']
                    if asin in HERO_ASINS and ('rating' in c or 'reviews' in c):
                        if asin not in result['hero_ratings_reviews']:
                            result['hero_ratings_reviews'][asin] = {}
                        if 'rating' in c:
                            result['hero_ratings_reviews'][asin]['rating'] = c['rating']
                        if 'reviews' in c:
                            result['hero_ratings_reviews'][asin]['reviews'] = c['reviews']

        result['niches'][niche_id] = {
            'label': label,
            'competitors': compressed
        }

    # Output
    out_path = Path(r'C:\Users\Dell\OneDrive\מסמכים\craftiloo-claude-workspace\outputs\data\datadive_competitors_raw.json')
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f'\nDone. Saved to {out_path}')
    print(f'Niches fetched: {len(result["niches"])}/11')
    print(f'Errors: {len(result["errors"])}')
    if result['errors']:
        for e in result['errors']:
            print(f'  - {e["label"]}: {e["error"]}')

    # Print compact summary
    print('\n--- RESULT SUMMARY ---')
    print(json.dumps(result, indent=2, ensure_ascii=False)[:8000])


if __name__ == '__main__':
    main()

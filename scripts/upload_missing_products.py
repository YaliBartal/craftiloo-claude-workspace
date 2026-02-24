"""
Upload all MISSING Craftiloo products to Notion Master Product List.
Covers: catalog products not yet on Amazon, closed/0-stock listings, and newly found ASINs.
"""

import os
import json
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
DATABASE_ID = "2e157318-d05c-815f-9fe8-c18ec3f3d0cb"
NOTION_VERSION = "2022-06-28"
HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": NOTION_VERSION,
}

# ─── Products with Amazon ASINs (closed/inactive or newly found) ───
PRODUCTS_WITH_ASIN = [
    {
        "name": "Dogs Cross Stitch Kit (5 Pack)",
        "asin": "B0B1935V5N",
        "sku": "CS05",
        "status": "Closed",
        "stock_level": "Out of Stock",
        "note": "5 plastic hoops (black), 4 pointless needles + 2 threaders, 5 keychain clips, 5 printed fabric patterns (dogs), felt sticker decorations + 8cm circle stickers x5, instructions + gift box"
    },
    {
        "name": "2 in 1 Cross Stitch & Embroidery Kit (8 Projects)",
        "asin": "B0F8QZZQQM",
        "sku": "FCE02",
        "status": "Active",
        "stock_level": None,
        "note": "1 embroidery hoop (blue), 3 plastic keychains, stuffing for pillow & fairy (~70-80g), 10-color floss, 2 plastic + 2 embroidery needles + 2 threaders, decorative beads, instructions + color box"
    },
    {
        "name": "Stitch Dictionary: Heart (Embroidery)",
        "asin": "B0BPDCDXNK",
        "sku": "EK05",
        "status": "Closed",
        "stock_level": "Out of Stock",
        "note": "3 design printed fabrics (25x25cm), 1 plastic hoop (20cm), 10 embroidery needles + 2 threaders, 1 unthread device, sufficient floss, instruction booklet + zipper bag"
    },
    {
        "name": "Stitch Dictionary: Practice (Embroidery)",
        "asin": "B0C8PHS3FS",
        "sku": "EK06",
        "status": "Closed",
        "stock_level": "Out of Stock",
        "note": "3 design printed fabrics (25x25cm), 1 plastic hoop (20cm), 10 embroidery needles + 2 threaders, 1 unthread device, sufficient floss, instruction booklet + zipper bag"
    },
    {
        "name": "Stitch Dictionary: Butterfly (Embroidery)",
        "asin": "B0C5S1FW5L",
        "sku": "EK07",
        "status": "Closed",
        "stock_level": "Out of Stock",
        "note": "3 design printed fabrics (25x25cm), 1 plastic hoop (20cm), 10 embroidery needles + 2 threaders, 1 unthread device, sufficient floss, instruction booklet + zipper bag"
    },
    {
        "name": "Latch Hook Pencil Cases V2 (2 Pack)",
        "asin": "B0BXHJJMX1",
        "sku": "LK02",
        "status": "Closed",
        "stock_level": "Out of Stock",
        "note": "2 pencil cases (2 patterns), yarn (Purple x3, Light Grey x3, Pink, Blue, Dark Grey), 2 latch needles, instructions + color box"
    },
    {
        "name": "3D Unicorn Latch Hook Pouch",
        "asin": "B0B3PGPVV5",
        "sku": "LK03D",
        "status": "Closed",
        "stock_level": "Out of Stock",
        "note": "3D unicorn mini latch bag (pink), yarn (6cm background, 7cm unicorn/star), 1 latch tool, instructions + color box"
    },
    {
        "name": "Latch Hook Pillow: Googly Eyes Heart",
        "asin": "B0F8R6J7JR",
        "sku": "LH04",
        "status": "Active",
        "stock_level": None,
        "note": "1 latch pillow + 1 latch heart, yarn for design, 130g stuffing, 4cm plastic eyes with back closer, instructions + gift box"
    },
    {
        "name": "Needlepoint Wallet: Cat & Dog",
        "asin": "B09HVSLBS6",
        "sku": "NPW-DC",
        "status": "Closed",
        "stock_level": "Out of Stock",
        "note": "1 wallet (4\"x4\"), 4 needles + 2 threaders, embroidery floss, zipper bag + instructions + outer box"
    },
    {
        "name": "Needlepoint Wallet: Mermaid",
        "asin": "B09HVDYMDK",
        "sku": "NPW-M",
        "status": "Closed",
        "stock_level": "Out of Stock",
        "note": "1 wallet (4\"x4\"), 4 needles + 2 threaders, embroidery floss, zipper bag + instructions + outer box"
    },
    {
        "name": "Needlepoint Wallet: Cupcake",
        "asin": "B09HVCQTVS",
        "sku": "NPW-C",
        "status": "Closed",
        "stock_level": "Out of Stock",
        "note": "1 wallet (4\"x4\"), 4 needles + 2 threaders, embroidery floss, zipper bag + instructions + outer box"
    },
    {
        "name": "Fuse Beads Kit (5,200pcs)",
        "asin": "B0GNQZ79D5",
        "sku": "CS24-5200",
        "status": "Active",
        "stock_level": None,
        "note": "5,200 x 5mm beads, 1 large ironing paper, 1 L squared pegboard + 1 S round + 1 S hexagon, 60 patterns + 1 pattern book, 1 plastic tweezer + color box"
    },
    {
        "name": "Unicorn Sewing Kit (5 Mini Desserts)",
        "asin": "B099Q5MQJC",
        "sku": "USK03",
        "status": "Closed",
        "stock_level": "Out of Stock",
        "note": "Pre-cut felt for 5 mini desserts, 3-color embroidery floss, 4 needles + 2 threaders, 27g stuffing + glue, instructions + color box"
    },
    {
        "name": "Cross Stitch 10 Necklace Kit",
        "asin": "B0975128H8",
        "sku": "CS03",
        "status": "Closed",
        "stock_level": "Out of Stock",
        "note": "8 cross stitch preprinted patterns, sufficient floss, 10 silver pendants (30mm) + 10 glass covers + 6 tags, 10 black necklaces (42cm) with extender, 2 hoops + 4 needles + 2 threaders, glue + 5 sticker sheets, instructions + color box"
    },
    {
        "name": "Embroidery 10 Necklace Kit",
        "asin": "B0974Z78X5",
        "sku": "EK02",
        "status": "Closed",
        "stock_level": "Out of Stock",
        "note": "10 embroidery preprinted patterns, sufficient floss, 7 round + 3 oval pendants with glass covers & tags, 10 black necklaces with extender, 2 hoops + 4 needles + 2 threaders, glue + 6 sticker sheets, instructions + color box"
    },
    {
        "name": "3 Embroidery Jewelry/Necklace Kit",
        "asin": "B099Q4Z1Q7",
        "sku": "EK03",
        "status": "Closed",
        "stock_level": "Out of Stock",
        "note": "3 embroidery preprinted patterns, sufficient floss, 3 silver pendants (30mm) + 3 tags, 3 black necklaces with extender, 1 hoop (7cm) + 4 needles + 2 threaders, 20ml glue, instructions + bag package"
    },
    {
        "name": "Owl Latch Hook + Butterfly Needlepoint Bag",
        "asin": "B09BRBGD3D",
        "sku": "LNB1",
        "status": "Closed",
        "stock_level": "Out of Stock",
        "note": "1 latch pouch + yarn, 1 latch hook, 1 locker hook bag + rug yarn, 1 locker hook needle + big hole needle, instructions + color box"
    },
    {
        "name": "Puppy & Kitten Pet Sewing Kit",
        "asin": "B0G2STK9BM",
        "sku": "NEW",
        "status": "Closed",
        "stock_level": "Out of Stock",
        "note": "Pre-cut pet felt pieces (puppies & kittens), sewing needles, embroidery floss, stuffing, instructions"
    },
]

# ─── Products from catalog with NO Amazon ASIN (not yet listed) ───
PRODUCTS_NO_ASIN = [
    {
        "name": "Stitch Dictionary V5 (4 Designs, Embroidery)",
        "sku": "EK09",
        "note": "4 design printed fabrics (25x25cm), 1 plastic hoop (20cm), 10 embroidery needles + 2 threaders, 1 unthread device, sufficient floss, instruction booklet + zipper bag"
    },
    {
        "name": "\"Be The Change\" Embroidery Kit (3 Designs, Adults)",
        "sku": "EK14",
        "note": "3 design printed fabrics (25x25cm), 1 wood hoop (23cm), 10 embroidery needles + 4 threaders, 1 unthread device + floss, instruction booklet + color box"
    },
    {
        "name": "Pencil Toppers Sewing Kit (24 Mini Figures)",
        "sku": "PSK08",
        "note": "24 mini felt figures, 6-color floss, 4 cross stitch needles + 2 threaders, instructions + color box"
    },
    {
        "name": "Forest Sewing Kit",
        "sku": "FSK11",
        "note": "Pre-cut forest animal felt, 7-color floss, 4 needles + threader, play mat 60x60cm, stuffing + color box + instructions"
    },
    {
        "name": "Safari Sewing Kit",
        "sku": "SSK12",
        "note": "Pre-cut safari animal felt, 8-color floss, 4 needles + threader, play mat 60x60cm, stuffing + color box + instructions"
    },
    {
        "name": "Locker Hooking Kit (2 Pencil Cases)",
        "sku": "LH01",
        "note": "2 pencil cases (2 patterns), yarn (Purple, Pink, Aqua, Yellow Cream, Milky White), middle wool, 2 locker hooking hooks, instructions + color box"
    },
    {
        "name": "Needlepoint Wallet: Brown Spot",
        "sku": "NPW-BS",
        "note": "1 wallet (4\"x4\"), 4 needles + 2 threaders, embroidery floss, zipper bag + instructions + outer box"
    },
    {
        "name": "Needlepoint Wallet: Pink Spot",
        "sku": "NPW-P",
        "note": "1 wallet (4\"x4\"), 4 needles + 2 threaders, embroidery floss, zipper bag + instructions + outer box"
    },
    {
        "name": "Needlepoint Wallet: Zebra",
        "sku": "NPW-Z",
        "note": "1 wallet (4\"x4\"), 4 needles + 2 threaders, embroidery floss, zipper bag + instructions + outer box"
    },
    {
        "name": "Fuse Beads Mixed Kit (10,000pcs Strip+Normal)",
        "sku": "CSD12",
        "note": "5,831 strip beads + 4,165 normal beads, 1 large ironing paper, 2 L squared + 1 L hexagon pegboard, 28 L square + 4 L hexagon patterns, 1 plastic tweezer + color box"
    },
    {
        "name": "Mini Fuse Beads V2 (24,000pcs)",
        "sku": "CC48-V2",
        "note": "24,000 mini beads + 2,000 black/white beads, 4 ironing sheets + 1 L ironing paper, 4 L squared + 1 L round pegboard, 1 metal tweezer + color box (different bead mix from V1)"
    },
    {
        "name": "Mermaid Sewing Kit",
        "sku": "MSK02",
        "note": "Pre-cut mermaid felt pattern, blue fabric + 27cm hoop, fabric glue, 4-color embroidery floss, 2 large + 2 bead needles + 2 threaders, 20 pins + 2 ribbons, pearl beads + 500 small beads + 100 sequins, instructions + color box"
    },
    {
        "name": "Cross Stitch 3 Necklace Kit",
        "sku": "CS07",
        "note": "3 cross stitch preprinted patterns, sufficient floss, 3 silver pendants (30mm) + 3 tags, 3 black necklaces with extender, 1 hoop (7cm) + 4 needles + 2 threaders, 20ml glue, instructions + bag package"
    },
    {
        "name": "Latch Needlepoint Bag: Cupcake + Owl",
        "sku": "LNB2",
        "note": "1 latch pouch + yarn, 1 latch hook, 1 locker hook bag + rug yarn, 1 locker hook needle + big hole needle, instructions + color box"
    },
    # ─── Barbie Licensed Kits (8 products) ───
    {
        "name": "Barbie Embroidery Kit",
        "sku": "BB01",
        "note": "2 plastic hoops (16cm, light blue + pink), 8 waterproof embroidery designs, floss for all designs, 10 embroidery needles + 2 threaders, 1 unthread device, instructions + gift box"
    },
    {
        "name": "Barbie Cross Stitch Kit",
        "sku": "BB02",
        "note": "7 cross stitch designs, 1 page sticker, 6-color floss, 7 plastic keychains (3 pink, 2 blue, 2 purple), 4 plastic needles + 2 threaders, instructions + color box"
    },
    {
        "name": "Barbie Latch Kit (Heart)",
        "sku": "BB03",
        "note": "1 latch heart, multi-color yarn, 1 latch hook, 120g stuffing, instructions + gift box"
    },
    {
        "name": "Barbie Minibag (Felt)",
        "sku": "BB04",
        "note": "Felt bag, 5-color floss + stickers, 2 buttons + 2 strings + needle + threader, booklet + color box"
    },
    {
        "name": "Barbie Illustration Lacing Card",
        "sku": "BB05",
        "note": "8 Barbie lacing cards, 8 laces, felt stickers + color box"
    },
    {
        "name": "Barbie Real Lacing Card",
        "sku": "BB06",
        "note": "8 Barbie lacing cards, 8 laces, transparent stickers + color box"
    },
    {
        "name": "Barbie Stitch Card",
        "sku": "BB07",
        "note": "8 square cards, gem stickers (2 round, 2 heart, 1 rectangle), satin ribbons (5 colors), hanger + double sticker, instructions + color box"
    },
    {
        "name": "Barbie Pet Sewing Kit",
        "sku": "BB08",
        "note": "7 pet fabric pieces, 2 plastic needles + 1 thread, 60g stuffing, instructions + color box"
    },
]


def get_existing_asins():
    """Get all existing ASINs in the database."""
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    all_asins = set()
    all_names = set()
    has_more = True
    start_cursor = None

    while has_more:
        payload = {}
        if start_cursor:
            payload["start_cursor"] = start_cursor

        resp = requests.post(url, headers=HEADERS, json=payload)
        data = resp.json()

        for page in data.get("results", []):
            props = page.get("properties", {})
            asin_arr = props.get("ASIN", {}).get("rich_text", [])
            if asin_arr:
                all_asins.add(asin_arr[0]["text"]["content"])
            title_arr = props.get("Name", {}).get("title", [])
            if title_arr:
                all_names.add(title_arr[0]["text"]["content"])

        has_more = data.get("has_more", False)
        start_cursor = data.get("next_cursor")

    return all_asins, all_names


def create_page(product, has_asin=True):
    """Create a single Notion database page for a product."""
    url = "https://api.notion.com/v1/pages"

    properties = {
        "Name": {"title": [{"text": {"content": product["name"]}}]},
        "Kit Content": {"rich_text": [{"text": {"content": product["note"]}}]},
    }

    if has_asin and product.get("asin"):
        properties["ASIN"] = {"rich_text": [{"text": {"content": product["asin"]}}]}
        properties["Listing Link"] = {"rich_text": [{
            "text": {
                "content": f"https://www.amazon.com/dp/{product['asin']}",
                "link": {"url": f"https://www.amazon.com/dp/{product['asin']}"}
            }
        }]}

    if product.get("status"):
        properties["Listing Status"] = {"select": {"name": product["status"]}}

    if product.get("stock_level"):
        properties["Stock Level"] = {"select": {"name": product["stock_level"]}}

    payload = {"parent": {"database_id": DATABASE_ID}, "properties": properties}
    return requests.post(url, headers=HEADERS, json=payload)


def main():
    if not NOTION_API_KEY:
        print("ERROR: NOTION_API_KEY not found in .env")
        return

    existing_asins, existing_names = get_existing_asins()
    print(f"Existing entries: {len(existing_asins)} ASINs, {len(existing_names)} named products")
    print()

    # ─── Upload products with ASINs ───
    print("--- Products with ASINs (closed/inactive/newly found) ---")
    created = 0
    skipped = 0

    for p in PRODUCTS_WITH_ASIN:
        if p["asin"] in existing_asins:
            print(f"  SKIP (exists): {p['name']} ({p['asin']})")
            skipped += 1
            continue
        resp = create_page(p, has_asin=True)
        if resp.status_code == 200:
            print(f"  OK: {p['name']} ({p['asin']})")
            created += 1
        else:
            err = resp.json().get("message", resp.text[:100])
            print(f"  FAIL: {p['name']} — {err}")
        time.sleep(0.35)

    print(f"\n  Created: {created} | Skipped: {skipped}")
    print()

    # ─── Upload catalog-only products (no ASIN) ───
    print("--- Catalog-only products (not yet on Amazon) ---")
    created2 = 0
    skipped2 = 0

    for p in PRODUCTS_NO_ASIN:
        if p["name"] in existing_names:
            print(f"  SKIP (exists): {p['name']}")
            skipped2 += 1
            continue
        resp = create_page(p, has_asin=False)
        if resp.status_code == 200:
            print(f"  OK: {p['name']} [SKU: {p['sku']}]")
            created2 += 1
        else:
            err = resp.json().get("message", resp.text[:100])
            print(f"  FAIL: {p['name']} — {err}")
        time.sleep(0.35)

    print(f"\n  Created: {created2} | Skipped: {skipped2}")
    print()
    print(f"=== TOTAL ADDED: {created + created2} ===")


if __name__ == "__main__":
    main()

"""
Upload all Craftiloo products to Notion Master Product List database.
Cross-references Amazon active listings with FBA inventory data.
"""

import os
import json
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load .env from workspace root
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

# All active products from Amazon listings with kit contents
PRODUCTS = [
    {
        "name": "Dogs Sewing Kit (8 Pre-Cut)",
        "asin": "B0CDH84QDP",
        "price": 26.98,
        "stock": 40,
        "stock_level": "Understocked",
        "note": "8 pre-cut felt dog pieces, sewing needles, embroidery floss, stuffing, clear glue, easy-to-follow instructions"
    },
    {
        "name": "Pirates Sewing Kit",
        "asin": "B0C3YQ5RG1",
        "price": 26.98,
        "stock": 139,
        "stock_level": "Optimal",
        "note": "Pre-cut felt pirate pieces, sewing needles, embroidery floss, stuffing, clear glue, instructions"
    },
    {
        "name": "Ballerina Dancers Sewing Kit",
        "asin": "B0BNDVTTSH",
        "price": 28.98,
        "stock": 960,
        "stock_level": "Overstocked",
        "note": "5 pre-cut/pre-punched felt ballerina sets, embroidery floss, blunt needles, stuffing, glue, threaders, instruction booklet + video tutorials, ballet stage backdrop"
    },
    {
        "name": "\"You Are\" Embroidery Kit",
        "asin": "B0CY2SXF6P",
        "price": 24.98,
        "stock": 37,
        "stock_level": "Understocked",
        "note": "Stamped embroidery pattern, embroidery hoop, embroidery floss, needles, instructions"
    },
    {
        "name": "5 Stamped Embroidery Kit (Kids)",
        "asin": "B08DJYBH4D",
        "price": 28.98,
        "stock": 313,
        "stock_level": "Optimal",
        "note": "5 colorful hoops (2.75\"), 5 pre-printed stamped embroidery fabric, 2 needles, 16 colors cotton thread floss, instructions, 1 needle threader"
    },
    {
        "name": "XXL Fuse Beads Kit (22,000pcs)",
        "asin": "B07PXN4K8N",
        "price": 42.95,
        "stock": 118,
        "stock_level": "Optimal",
        "note": "22,000 fuse beads (5mm), fuse pegboards, ironing paper, storage case"
    },
    {
        "name": "\"Into The Water\" Embroidery Kit",
        "asin": "B0CSPRD746",
        "price": 24.98,
        "stock": 49,
        "stock_level": "Understocked",
        "note": "Stamped embroidery pattern, embroidery hoop, embroidery floss, needles, instructions"
    },
    {
        "name": "Princess Lacing Card Kit",
        "asin": "B0FQC7YFX6",
        "price": 16.98,
        "stock": 395,
        "stock_level": "Optimal",
        "note": "8 princess-themed lacing cards, durable laces, gem stickers, instructions, reusable storage box"
    },
    {
        "name": "My First Cross Stitch Kit (4 Keyrings)",
        "asin": "B0F6YTG1CH",
        "price": 16.99,
        "stock": 241,
        "stock_level": "Optimal",
        "note": "4 pre-cut felt shapes (unicorn, rainbow, winged heart), 4 sticky felt backings, embroidery floss, 4 keyring clasps, needles & threader, instruction leaflet + video tutorials"
    },
    {
        "name": "Sunflower Embroidery Kit (4 Pack, Adults)",
        "asin": "B0DC69M3YD",
        "price": 28.98,
        "stock": 675,
        "stock_level": "Overstocked",
        "note": "4 stamped cross stitch/embroidery patterns (sunflower), embroidery hoops, embroidery floss, needles, instructions"
    },
    {
        "name": "Knitting Kit (Hat & Cat)",
        "asin": "B0F8DG32H5",
        "price": 36.99,
        "stock": 529,
        "stock_level": "Overstocked",
        "note": "2 loom rings, soft yarn, pom pom maker, all tools needed, illustrated guide + QR code video tutorials — makes a real hat and plush cat"
    },
    {
        "name": "Superhero Sewing Kit (5 Projects)",
        "asin": "B0B8TFW4MN",
        "price": 24.98,
        "stock": 101,
        "stock_level": "Optimal",
        "note": "Pre-cut felt fabric (5 superheroes), sewing needles, embroidery floss, stuffing, clear glue, easy-to-follow instructions"
    },
    {
        "name": "Unicorn Latch Hook Pouch + Heart Bag",
        "asin": "B09BRC2VYV",
        "price": 16.98,
        "stock": 14,
        "stock_level": "Understocked",
        "note": "2 minibags (unicorn latch hook + heart needlepoint), yarn, latch hook, needles, 1 strap, instructions"
    },
    {
        "name": "10 Pre-Stamped Embroidery Kit (Kids)",
        "asin": "B09X55KL2C",
        "price": 28.98,
        "stock": 1864,
        "stock_level": "Overstocked",
        "note": "10 pre-printed fabric designs, colorful embroidery threads, hoops, needles, all essential supplies, video tutorials"
    },
    {
        "name": "Cross Stitch Backpack Charms (5 Pack)",
        "asin": "B08DDJCQKF",
        "price": 28.98,
        "stock": 1582,
        "stock_level": "Overstocked",
        "note": "5 mini pre-stamped cross stitch kits, 5 plastic hoops, 16 skeins embroidery floss, 2 blunt needles, 5 keychain rings, instruction booklet"
    },
    {
        "name": "Punch Needle Kit (3 Mini Pillows)",
        "asin": "B092SW839H",
        "price": 36.98,
        "stock": 695,
        "stock_level": "Overstocked",
        "note": "3 pattern printed fabrics, yarn, punch needle, needle threader, embroidery hoop, embroidery floss, embroidery needles, felt fabric, ribbons, stuffing, instructions"
    },
    {
        "name": "Fairy Sewing Kit (5 Projects)",
        "asin": "B09WQSBZY7",
        "price": 32.98,
        "stock": 797,
        "stock_level": "Overstocked",
        "note": "Pre-cut felt fabric (4 fairies + mushroom house), sewing needles, embroidery floss, stuffing, clear glue, instructions"
    },
    {
        "name": "Cactus Embroidery Kit (Adults)",
        "asin": "B0CP2KCF9R",
        "price": 26.98,
        "stock": 76,
        "stock_level": "Optimal",
        "note": "Stamped embroidery patterns, embroidery hoop, embroidery floss, needles, instructions"
    },
    {
        "name": "XL Fuse Beads Kit (11,000pcs)",
        "asin": "B0BVHMZFSQ",
        "price": 34.98,
        "stock": 4,
        "stock_level": "Understocked",
        "note": "11,000 fuse beads (5mm), fuse pegboards, ironing paper, storage case"
    },
    {
        "name": "Mini Fuse Beads Kit (24,000 Pastel)",
        "asin": "B0CRZ8M2G1",
        "price": 34.98,
        "stock": 147,
        "stock_level": "Optimal",
        "note": "24,000 mini beads (2.6mm) in 48 pastel colors, 5 pegboards, 2 tweezers, compatible with Hama, bulk storage"
    },
    {
        "name": "Butterflies Embroidery Kit (Adults)",
        "asin": "B0CT962TMN",
        "price": 26.98,
        "stock": None,
        "stock_level": None,
        "note": "Stamped embroidery patterns (butterflies), embroidery hoop, embroidery floss, needles, instructions"
    },
    {
        "name": "Cat Embroidery Kit (30 Stitches)",
        "asin": "B0BWSGRTB1",
        "price": 23.98,
        "stock": None,
        "stock_level": None,
        "note": "Stamped embroidery patterns (cat, 30 different stitches), embroidery hoop, embroidery floss, needles, instructions"
    },
    {
        "name": "Elephant Embroidery Kit (30 Stitches)",
        "asin": "B0B2XL9D8D",
        "price": 24.98,
        "stock": None,
        "stock_level": None,
        "note": "Stamped embroidery patterns (elephant, 30 different stitches), embroidery hoop, embroidery floss, needles, instructions"
    },
    {
        "name": "Dessert Treats Sewing Kit (12 Pre-Cut)",
        "asin": "B096MYBLS1",
        "price": 24.98,
        "stock": None,
        "stock_level": None,
        "note": "12 pre-cut figures, embroidery floss, glue, beads, 12 key rings, pins, embroidery needles, ribbons, stuffing, illustrated instructions"
    },
    {
        "name": "Loom Knitting & Crochet Kit (Bunny)",
        "asin": "B0DKD2S3JT",
        "price": 28.98,
        "stock": None,
        "stock_level": None,
        "note": "2 loom rings, crochet hook, soft yarn, stuffing, safety eyes & nose, yarn needle, threader, reusable cookie tin, step-by-step booklet + video tutorials — makes a plush bunny"
    },
    {
        "name": "Needlepoint Wallet (Unicorn)",
        "asin": "B09HVCCNM2",
        "price": 17.98,
        "stock": None,
        "stock_level": None,
        "note": "1 pre-stamped needlepoint wallet (4\"x4\"), 4 needles, cotton thread floss, instructions"
    },
    {
        "name": "Fairy Elves Sewing Kit",
        "asin": "B0BP8GCK1G",
        "price": 22.98,
        "stock": None,
        "stock_level": None,
        "note": "Pre-cut felt fairy/elf pieces, sewing needles, embroidery floss, stuffing, glue, instructions"
    },
    {
        "name": "Goldfish Embroidery Kit",
        "asin": "B0CQHMJWR9",
        "price": 24.98,
        "stock": None,
        "stock_level": None,
        "note": "Stamped embroidery pattern (goldfish), embroidery hoop, embroidery floss, needles, instructions"
    },
    {
        "name": "\"I Am The Storm\" Embroidery Kit",
        "asin": "B0CRHX8G72",
        "price": 24.98,
        "stock": None,
        "stock_level": None,
        "note": "Stamped embroidery pattern, embroidery hoop, embroidery floss, needles, instructions"
    },
    {
        "name": "Latch Hook Pencil Cases (2 Pack)",
        "asin": "B08FYH13CL",
        "price": 28.98,
        "stock": None,
        "stock_level": None,
        "note": "2 pencil cases (7.9\" x 3.9\"), 9 yarn bundles, 2 latch hooks, instructions"
    },
    {
        "name": "Latch Hook Pillow Kit (Wise Owl)",
        "asin": "B0FHMRQWRX",
        "price": 32.99,
        "stock": None,
        "stock_level": None,
        "note": "Pre-printed pillow base with color grid, pre-cut yarn, soft stuffing, plastic eyes, instruction booklet + video tutorials"
    },
    {
        "name": "Needlepoint Wallet (Cat)",
        "asin": "B09HVDNFMR",
        "price": 17.98,
        "stock": None,
        "stock_level": None,
        "note": "1 pre-stamped needlepoint wallet (4\"x4\"), 4 needles, cotton thread floss, instructions"
    },
    {
        "name": "Jumbo Fuse Beads Kit (1,500 x 10mm)",
        "asin": "B07D6D95NG",
        "price": 32.96,
        "stock": None,
        "stock_level": None,
        "note": "1,500 jumbo beads (10mm) in 15 colors, 2 large pegboards, 48 patterns incl. English letters, ironing paper — ages 4-7"
    },
    {
        "name": "Flowers Embroidery Kit (Adults)",
        "asin": "B0CKTS6ZFZ",
        "price": 22.98,
        "stock": None,
        "stock_level": None,
        "note": "Stamped embroidery patterns (flowers with health affirmations), embroidery hoop, embroidery floss, needles, instructions"
    },
    {
        "name": "Latch Hook Pillow Kit (Rainbow Heart)",
        "asin": "B0F8R652FX",
        "price": 28.99,
        "stock": None,
        "stock_level": None,
        "note": "Pre-printed pillow base with color grid, pre-cut yarn, soft stuffing, plastic eyes, instruction booklet + video tutorials"
    },
    {
        "name": "Mini Fuse Beads Kit (24,000 x 48 Colors)",
        "asin": "B09THLVFZK",
        "price": 34.98,
        "stock": None,
        "stock_level": None,
        "note": "24,000 mini beads (2.6mm), 48 colors, 4 square pegboards, 1 round pegboard, 2 metal tweezers, 4 ironing sheets, 1 large ironing paper"
    },
    {
        "name": "Cats Cross Stitch Kit (5 Pack)",
        "asin": "B0B18ZRRCQ",
        "price": 28.98,
        "stock": None,
        "stock_level": None,
        "note": "5 embroidery hoops, 5 pre-printed Aida fabric (11CT) with cat designs, 2 blunt needles, 16 colors embroidery floss, felt stickers, 5 keychains, accessories, instructions"
    },
    {
        "name": "Superhero Cross Stitch Kit (5 Pack)",
        "asin": "B08L8BHD4Z",
        "price": 24.98,
        "stock": 12,
        "stock_level": "Understocked",
        "note": "5 colorful hoops (2.75\"), 5 pre-printed 11CT stamped Aida cloth, 2 pointless needles, cotton thread floss, instructions, 1 needle threader"
    },
    {
        "name": "Safari Animals Cross Stitch Kit (5 Pack)",
        "asin": "B0B18ZHYKR",
        "price": 28.98,
        "stock": None,
        "stock_level": None,
        "note": "5 colorful hoops, 5 pre-printed stamped Aida cloth (safari animal designs), 2 blunt needles, cotton thread floss, keychains, instructions"
    },
]


def create_page(product):
    """Create a single Notion database page for a product."""
    url = "https://api.notion.com/v1/pages"

    properties = {
        "Name": {
            "title": [{"text": {"content": product["name"]}}]
        },
        "ASIN": {
            "rich_text": [{"text": {"content": product["asin"]}}]
        },
        "Listing Status": {
            "select": {"name": "Active"}
        },
        "Listing Link": {
            "rich_text": [{
                "text": {
                    "content": f"https://www.amazon.com/dp/{product['asin']}",
                    "link": {"url": f"https://www.amazon.com/dp/{product['asin']}"}
                }
            }]
        },
        "Note": {
            "rich_text": [{"text": {"content": product["note"]}}]
        },
    }

    # Only set Stock Level if we have data
    if product.get("stock_level"):
        properties["Stock Level"] = {
            "select": {"name": product["stock_level"]}
        }

    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": properties,
    }

    response = requests.post(url, headers=HEADERS, json=payload)
    return response


def delete_page(page_id):
    """Archive (delete) a Notion page."""
    url = f"https://api.notion.com/v1/pages/{page_id}"
    payload = {"archived": True}
    response = requests.patch(url, headers=HEADERS, json=payload)
    return response


def get_existing_pages():
    """Get all existing pages in the database."""
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    response = requests.post(url, headers=HEADERS, json={})
    if response.status_code == 200:
        return response.json().get("results", [])
    return []


def main():
    if not NOTION_API_KEY:
        print("ERROR: NOTION_API_KEY not found in .env")
        return

    print(f"Found {len(PRODUCTS)} products to upload")
    print(f"Using database: {DATABASE_ID}")
    print()

    # Step 1: Get existing pages and clean up untitled/empty ones
    print("--- Checking existing entries ---")
    existing = get_existing_pages()
    existing_asins = set()

    for page in existing:
        props = page.get("properties", {})
        title_arr = props.get("Name", {}).get("title", [])
        name = title_arr[0]["text"]["content"] if title_arr else "(untitled)"
        asin_arr = props.get("ASIN", {}).get("rich_text", [])
        asin = asin_arr[0]["text"]["content"] if asin_arr else ""

        if name in ["(untitled)", ""] or (not asin and name not in ["Barbie", "Bamboo Ashtray"]):
            print(f"  Archiving empty entry: '{name}'")
            delete_page(page["id"])
            time.sleep(0.35)
        else:
            existing_asins.add(asin)
            print(f"  Keeping: '{name}' (ASIN: {asin})")

    print()

    # Step 2: Upload all products (skip if ASIN already exists)
    print("--- Uploading products ---")
    success = 0
    skipped = 0
    failed = 0

    for i, product in enumerate(PRODUCTS, 1):
        if product["asin"] in existing_asins:
            print(f"  [{i}/{len(PRODUCTS)}] SKIP (exists): {product['name']}")
            skipped += 1
            continue

        response = create_page(product)
        if response.status_code == 200:
            print(f"  [{i}/{len(PRODUCTS)}] OK: {product['name']}")
            success += 1
        else:
            error = response.json().get("message", response.text[:100])
            print(f"  [{i}/{len(PRODUCTS)}] FAIL: {product['name']} — {error}")
            failed += 1

        time.sleep(0.35)  # Rate limiting

    print()
    print(f"--- Done ---")
    print(f"  Created: {success}")
    print(f"  Skipped: {skipped}")
    print(f"  Failed:  {failed}")
    print(f"  Total in DB: {success + skipped + len([p for p in existing if p['id'] not in []])}")


if __name__ == "__main__":
    main()

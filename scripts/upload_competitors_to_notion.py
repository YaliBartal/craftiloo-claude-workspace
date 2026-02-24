"""
Create a Competitor Master List on Notion with inline database.
Mirrors the Master Product List structure but only includes: Name, ASIN, Listing Link, Brand, Category.
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
NOTION_VERSION = "2022-06-28"
HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": NOTION_VERSION,
}

# Parent page: "Master Product List" is at workspace level.
# We'll create under "01. Product Development" for organization.
PARENT_PAGE_ID = "2e157318-d05c-8193-931f-d2558f66c2c7"

# ─── All competitors by category ───
COMPETITORS = [
    # --- Cross Stitch Kits for Kids ---
    {"name": "Pllieay 10-in-1 Cross Stitch Beginner Kit", "brand": "Pllieay", "asin": "B08T5QC9FS", "category": "Cross Stitch (Kids)"},
    {"name": "KRAFUN My First Cross Stitch Kit", "brand": "KRAFUN", "asin": "B0B7JHN4F1", "category": "Cross Stitch (Kids)"},
    {"name": "Caydo Woodland Animal Cross Stitch Kit", "brand": "Caydo", "asin": "B0CM9JKNCC", "category": "Cross Stitch (Kids)"},
    {"name": "EZCRA Beginner Cross Stitch Kit (Ages 5-8)", "brand": "EZCRA", "asin": "B0DFHN42QB", "category": "Cross Stitch (Kids)"},

    # --- Embroidery Kits for Kids ---
    {"name": "CraftLab Embroidery Kit (Parents Picks Award)", "brand": "CraftLab", "asin": "B087DYHMZ2", "category": "Embroidery (Kids)"},
    {"name": "KRAFUN My First Embroidery Kit", "brand": "KRAFUN", "asin": "B0D8171TF1", "category": "Embroidery (Kids)"},
    {"name": "Pllieay Punch Needle / Cross Stitch Combo Kit", "brand": "Pllieay", "asin": "B08TC7423N", "category": "Embroidery (Kids)"},
    {"name": "Louise Maelys Beginner Needlepoint Kit", "brand": "Louise Maelys", "asin": "B0DP654CSV", "category": "Embroidery (Kids)"},

    # --- Embroidery Kits for Beginners (Adults) ---
    {"name": "CYANFOUR 4-Stage Embroidery Kit (38 Stitches)", "brand": "CYANFOUR", "asin": "B0CZHKSSL4", "category": "Embroidery (Adults)"},
    {"name": "CYANFOUR 5-Pack Beginner Embroidery Kit", "brand": "CYANFOUR", "asin": "B0DMHY2HF3", "category": "Embroidery (Adults)"},
    {"name": "Santune Embroidery Kit 3-4 Pack", "brand": "Santune", "asin": "B0BB9N74SG", "category": "Embroidery (Adults)"},
    {"name": "Bradove Stitch Practice Embroidery Kit", "brand": "Bradove", "asin": "B0B762JW55", "category": "Embroidery (Adults)"},
    {"name": "ETSPIL 4 Floral Pattern Embroidery Kit (33 Stitches)", "brand": "ETSPIL", "asin": "B0C3ZVKB46", "category": "Embroidery (Adults)"},
    {"name": "Craftwiz 4-Piece Starter Embroidery Kit", "brand": "Craftwiz", "asin": "B0C8F87C6Y", "category": "Embroidery (Adults)"},
    {"name": "BERYA Flowers Embroidery Kit", "brand": "BERYA", "asin": "B07Q4375WF", "category": "Embroidery (Adults)"},
    {"name": "wtisan 4-Pack Embroidery Kit (Stamped Flowers)", "brand": "wtisan", "asin": "B0D1Y28SQB", "category": "Embroidery (Adults)"},
    {"name": "Uphome 3-Pack Embroidery Starter Kit", "brand": "Uphome", "asin": "B08JQ47WV1", "category": "Embroidery (Adults)"},
    {"name": "Akacraft Chinese Plum Blossom Embroidery Kit", "brand": "Akacraft", "asin": None, "category": "Embroidery (Adults)"},

    # --- Sewing Kits for Kids ---
    {"name": "KRAFUN My First Sewing Kit (Stuffed Animals)", "brand": "KRAFUN", "asin": "B091GXM2Y6", "category": "Sewing (Kids)"},
    {"name": "KRAFUN Sewing Kit (Animals)", "brand": "KRAFUN", "asin": "B0C2XYP6L3", "category": "Sewing (Kids)"},
    {"name": "KRAFUN Sewing Kit", "brand": "KRAFUN", "asin": "B0CV1F5CFS", "category": "Sewing (Kids)"},
    {"name": "EZCRA Unicorn Sewing Kit", "brand": "EZCRA", "asin": "B0CXY8JMTK", "category": "Sewing (Kids)"},
    {"name": "EZCRA Beginner 8-in-1 Sewing Kit", "brand": "EZCRA", "asin": "B0CYNNT2ZT", "category": "Sewing (Kids)"},
    {"name": "Klever Kits Themed Pillow Sewing Kit (Unicorn/Mermaid)", "brand": "Klever Kits", "asin": "B0CTTMWXYP", "category": "Sewing (Kids)"},

    # --- Latch Hook Kits ---
    {"name": "LatchKits Latch Hook Kit (Wall Art)", "brand": "LatchKits (PlayMonster)", "asin": "B06XRRN4VL", "category": "Latch Hook"},
    {"name": "LatchKits Strawberry Pillow", "brand": "LatchKits (PlayMonster)", "asin": "B0CX9H8YGR", "category": "Latch Hook"},
    {"name": "Vervaco Cushion Latch Hook Kit", "brand": "Vervaco", "asin": "B0063G6RUM", "category": "Latch Hook"},
    {"name": "MIAOLLUN Latch Hook Rug Kit (Sunflower)", "brand": "MIAOLLUN", "asin": "B08KLQ9JLJ", "category": "Latch Hook"},

    # --- Loom Knitting Kits for Kids ---
    {"name": "Creativity for Kids Quick Knit Loom", "brand": "Creativity for Kids", "asin": "B004JIFCXO", "category": "Loom Knitting"},
    {"name": "Hapinest Hat & Scarf Loom Kit (Ages 8-12)", "brand": "Hapinest", "asin": "B0B8W4FK4Q", "category": "Loom Knitting"},

    # --- Mini Fuse Beads (2.6mm) ---
    {"name": "INSCRAFT 28,000 Mini Fuse Beads (48 Colors)", "brand": "INSCRAFT", "asin": "B0C5WQD914", "category": "Mini Fuse Beads"},
    {"name": "ARTKAL Mini Fuse Beads (Food-Grade, 110+ Colors)", "brand": "ARTKAL", "asin": "B0FN4CT867", "category": "Mini Fuse Beads"},
    {"name": "LIHAO 24,000 Mini Fuse Beads (48 Colors)", "brand": "LIHAO", "asin": "B08QV9CMFQ", "category": "Mini Fuse Beads"},
    {"name": "Perler Mini Beads", "brand": "Perler", "asin": "B01AMXJA9Q", "category": "Mini Fuse Beads"},
    {"name": "FUNZBO 28,000 Mini Fuse Beads (48 Colors)", "brand": "FUNZBO", "asin": "B0D5LF666P", "category": "Mini Fuse Beads"},
    {"name": "Psykade 53,000 Fuse Beads Kit (96 Colors)", "brand": "Psykade", "asin": "B0FQ2YBX9W", "category": "Mini Fuse Beads"},
    {"name": "Hama Mini Beads", "brand": "Hama", "asin": None, "category": "Mini Fuse Beads"},

    # --- Lacing Cards ---
    {"name": "Melissa & Doug Lacing Cards", "brand": "Melissa & Doug", "asin": "B00JM5G05I", "category": "Lacing Cards"},
    {"name": "KRAFUN Safari Lacing Cards", "brand": "KRAFUN", "asin": "B0BRYRD91V", "category": "Lacing Cards"},
    {"name": "Serabeena Safari Animal Lacing Cards", "brand": "Serabeena", "asin": "B0D178S25M", "category": "Lacing Cards"},
    {"name": "Funrous 10-Piece Recognition Lacing Cards", "brand": "Funrous", "asin": "B0CLGD9JZC", "category": "Lacing Cards"},
    {"name": "Lauri Lacing Laces (PlayMonster)", "brand": "Lauri", "asin": "B000F8TAQW", "category": "Lacing Cards"},

    # --- Gem Art Kits (Kids) ---
    {"name": "EZCRA Gem Art Kit (990+ Stickers, 8 Themes)", "brand": "EZCRA", "asin": "B0CWLTTZ2G", "category": "Gem Art"},
]


def create_page(title, parent_id):
    """Create a new Notion page."""
    url = "https://api.notion.com/v1/pages"
    payload = {
        "parent": {"page_id": parent_id},
        "properties": {
            "title": {"title": [{"text": {"content": title}}]}
        },
    }
    resp = requests.post(url, headers=HEADERS, json=payload)
    if resp.status_code == 200:
        page_id = resp.json()["id"]
        print(f"Created page: {title} ({page_id})")
        return page_id
    else:
        print(f"FAIL creating page: {resp.json().get('message', resp.text[:200])}")
        return None


def create_database(parent_page_id, title):
    """Create an inline database with competitor-relevant properties."""
    url = "https://api.notion.com/v1/databases"
    payload = {
        "parent": {"type": "page_id", "page_id": parent_page_id},
        "title": [{"text": {"content": title}}],
        "properties": {
            "Name": {"title": {}},
            "ASIN": {"rich_text": {}},
            "Brand": {"rich_text": {}},
            "Listing Link": {"url": {}},
            "Category": {
                "select": {
                    "options": [
                        {"name": "Cross Stitch (Kids)", "color": "red"},
                        {"name": "Embroidery (Kids)", "color": "pink"},
                        {"name": "Embroidery (Adults)", "color": "purple"},
                        {"name": "Sewing (Kids)", "color": "blue"},
                        {"name": "Latch Hook", "color": "green"},
                        {"name": "Loom Knitting", "color": "yellow"},
                        {"name": "Mini Fuse Beads", "color": "orange"},
                        {"name": "Lacing Cards", "color": "brown"},
                        {"name": "Gem Art", "color": "gray"},
                    ]
                }
            },
        },
    }
    resp = requests.post(url, headers=HEADERS, json=payload)
    if resp.status_code == 200:
        db_id = resp.json()["id"]
        print(f"Created database: {title} ({db_id})")
        return db_id
    else:
        print(f"FAIL creating database: {resp.json().get('message', resp.text[:200])}")
        return None


def create_competitor_entry(db_id, competitor):
    """Create a single competitor entry in the database."""
    url = "https://api.notion.com/v1/pages"

    properties = {
        "Name": {"title": [{"text": {"content": competitor["name"]}}]},
        "Brand": {"rich_text": [{"text": {"content": competitor["brand"]}}]},
        "Category": {"select": {"name": competitor["category"]}},
    }

    if competitor.get("asin"):
        properties["ASIN"] = {"rich_text": [{"text": {"content": competitor["asin"]}}]}
        properties["Listing Link"] = {"url": f"https://www.amazon.com/dp/{competitor['asin']}"}

    payload = {"parent": {"database_id": db_id}, "properties": properties}
    return requests.post(url, headers=HEADERS, json=payload)


def main():
    if not NOTION_API_KEY:
        print("ERROR: NOTION_API_KEY not found in .env")
        return

    # Step 1: Create the parent page
    print("=== Creating Competitor Master List page ===")
    page_id = create_page("Competitor Master List", PARENT_PAGE_ID)
    if not page_id:
        return
    time.sleep(0.5)

    # Step 2: Create inline database
    print("\n=== Creating competitor database ===")
    db_id = create_database(page_id, "Competitor Products")
    if not db_id:
        return
    time.sleep(0.5)

    # Step 3: Upload all competitors
    print(f"\n=== Uploading {len(COMPETITORS)} competitors ===")
    created = 0
    failed = 0

    for comp in COMPETITORS:
        resp = create_competitor_entry(db_id, comp)
        if resp.status_code == 200:
            asin_str = f" ({comp['asin']})" if comp.get("asin") else " (no ASIN)"
            print(f"  OK: {comp['brand']} - {comp['name']}{asin_str}")
            created += 1
        else:
            err = resp.json().get("message", resp.text[:100])
            print(f"  FAIL: {comp['name']} — {err}")
            failed += 1
        time.sleep(0.35)

    print(f"\n=== DONE: {created} created, {failed} failed ===")
    print(f"Database ID: {db_id}")
    print(f"Page URL: https://www.notion.so/{page_id.replace('-', '')}")


if __name__ == "__main__":
    main()

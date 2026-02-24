"""Fetch Rank Radar detailed data from DataDive API and save as JSON."""

import json
import requests

API_KEY = "pDbBQZJBAd6rome2KvVWN2jxDxGRdSHWazx1KLF9"
RANK_RADAR_ID = "07f05d65-4059-4ecc-8ab1-830bbb6dd42d"
START_DATE = "2026-01-24"
END_DATE = "2026-02-23"

URL = f"https://api.datadive.tools/v1/niches/rank-radars/{RANK_RADAR_ID}?startDate={START_DATE}&endDate={END_DATE}"

HEADERS = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json",
    "Accept": "application/json",
}

OUTPUT_PATH = r"c:\Users\barta\OneDrive\Documents\Claude_Code_Workspace_TEMPLATE\Claude Code Workspace TEMPLATE\outputs\research\listing-optimizer\snapshots\datadive-rankradar-detail-2026-02-23.json"

response = requests.get(URL, headers=HEADERS, timeout=60)
response.raise_for_status()

data = response.json()

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Status: {response.status_code}")
print(f"Saved to: {OUTPUT_PATH}")
print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else f'array of {len(data)} items'}")

"""Un-negate campaign-level negative keywords by archiving them via Amazon Ads API."""

import os, json, time, sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

# Load .env
BASE = Path("c:/Users/barta/OneDrive/Documents/Claude_Code_Workspace_TEMPLATE/Claude Code Workspace TEMPLATE")
env_file = BASE / ".env"
if env_file.exists():
    with open(env_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                key, value = key.strip(), value.strip()
                if key and not os.environ.get(key, ""):
                    os.environ[key] = value

import httpx

BASE_URL = "https://advertising-api.amazon.com"
LWA_TOKEN_URL = "https://api.amazon.com/auth/o2/token"

def get_token():
    resp = httpx.post(LWA_TOKEN_URL, data={
        "grant_type": "refresh_token",
        "client_id": os.environ["ADS_API_CLIENT_ID"],
        "client_secret": os.environ["ADS_API_CLIENT_SECRET"],
        "refresh_token": os.environ["ADS_API_REFRESH_TOKEN"],
    }, timeout=15)
    resp.raise_for_status()
    return resp.json()["access_token"]

def archive_campaign_negatives(token, keyword_updates, campaign_label):
    headers = {
        "Authorization": f"Bearer {token}",
        "Amazon-Advertising-API-ClientId": os.environ["ADS_API_CLIENT_ID"],
        "Amazon-Advertising-API-Scope": os.environ["ADS_API_PROFILE_US"],
        "Content-Type": "application/vnd.spCampaignNegativeKeyword.v3+json",
        "Accept": "application/vnd.spCampaignNegativeKeyword.v3+json",
    }
    body = {"campaignNegativeKeywords": keyword_updates}

    time.sleep(0.5)  # rate limit
    resp = httpx.put(f"{BASE_URL}/sp/campaignNegativeKeywords", headers=headers, json=body, timeout=30)

    print(f"\n=== {campaign_label} ===")
    print(f"Status: {resp.status_code}")

    if resp.status_code in (200, 201, 202, 207):
        data = resp.json()
        success = data.get("campaignNegativeKeywords", {}).get("success", [])
        errors = data.get("campaignNegativeKeywords", {}).get("error", [])
        print(f"Success: {len(success)} keywords archived")
        if errors:
            print(f"Errors: {len(errors)}")
            for e in errors:
                print(f"  - {e}")
        return len(success), len(errors)
    else:
        print(f"Error: {resp.text[:500]}")
        return 0, len(keyword_updates)

# Keyword IDs to archive per campaign
cmp1_updates = [
    {"keywordId": "271814235197327", "state": "PAUSED"},
    {"keywordId": "7635776857618", "state": "PAUSED"},
    {"keywordId": "138144845451700", "state": "PAUSED"},
    {"keywordId": "167794989057597", "state": "PAUSED"},
    {"keywordId": "236504055098426", "state": "PAUSED"},
    {"keywordId": "279135132341195", "state": "PAUSED"},
    {"keywordId": "89177849431363", "state": "PAUSED"},
    {"keywordId": "202654677676990", "state": "PAUSED"},
    {"keywordId": "16182602363248", "state": "PAUSED"},
    {"keywordId": "277392023686114", "state": "PAUSED"},
    {"keywordId": "235715313979544", "state": "PAUSED"},
    {"keywordId": "280138125291970", "state": "PAUSED"},
    {"keywordId": "136968753903866", "state": "PAUSED"},
    {"keywordId": "125890487455014", "state": "PAUSED"},
    {"keywordId": "14807827184747", "state": "PAUSED"},
]

cmp2_updates = [
    {"keywordId": "49304210242739", "state": "PAUSED"},
    {"keywordId": "130998276280160", "state": "PAUSED"},
    {"keywordId": "213917214554740", "state": "PAUSED"},
    {"keywordId": "49812857733667", "state": "PAUSED"},
    {"keywordId": "11519795818789", "state": "PAUSED"},
    {"keywordId": "119243569347561", "state": "PAUSED"},
    {"keywordId": "140893402555279", "state": "PAUSED"},
    {"keywordId": "222784438050858", "state": "PAUSED"},
    {"keywordId": "124235896927278", "state": "PAUSED"},
    {"keywordId": "131862665396434", "state": "PAUSED"},
    {"keywordId": "105413164864607", "state": "PAUSED"},
    {"keywordId": "131895685368903", "state": "PAUSED"},
    {"keywordId": "268950536873251", "state": "PAUSED"},
    {"keywordId": "147005324665403", "state": "PAUSED"},
    {"keywordId": "275782062465645", "state": "PAUSED"},
    {"keywordId": "176044834975190", "state": "PAUSED"},
    {"keywordId": "210932939679080", "state": "PAUSED"},
    {"keywordId": "268471810600957", "state": "PAUSED"},
    {"keywordId": "8015644563760", "state": "PAUSED"},
    {"keywordId": "215209594813172", "state": "PAUSED"},
    {"keywordId": "187369167731317", "state": "PAUSED"},
    {"keywordId": "240640602917273", "state": "PAUSED"},
    {"keywordId": "210235541259376", "state": "PAUSED"},
    {"keywordId": "75225785491666", "state": "PAUSED"},
]

cmp3_updates = [
    {"keywordId": "6733182250805", "state": "PAUSED"},
    {"keywordId": "72755544026330", "state": "PAUSED"},
    {"keywordId": "177430038175856", "state": "PAUSED"},
    {"keywordId": "76416841363938", "state": "PAUSED"},
    {"keywordId": "15860186752471", "state": "PAUSED"},
    {"keywordId": "212723596032612", "state": "PAUSED"},
    {"keywordId": "40495922364409", "state": "PAUSED"},
    {"keywordId": "280964335388875", "state": "PAUSED"},
    {"keywordId": "52973401302857", "state": "PAUSED"},
    {"keywordId": "176426714768042", "state": "PAUSED"},
    {"keywordId": "262302170553589", "state": "PAUSED"},
    {"keywordId": "243247328203600", "state": "PAUSED"},
    {"keywordId": "261328445119102", "state": "PAUSED"},
    {"keywordId": "43133182090049", "state": "PAUSED"},
    {"keywordId": "42528119312438", "state": "PAUSED"},
    {"keywordId": "201693419311493", "state": "PAUSED"},
    {"keywordId": "204907366593300", "state": "PAUSED"},
    {"keywordId": "11491375642947", "state": "PAUSED"},
    {"keywordId": "70313894141653", "state": "PAUSED"},
]

if __name__ == "__main__":
    print("Getting access token...")
    token = get_token()
    print("Token obtained.\n")

    total_success = 0
    total_errors = 0

    s, e = archive_campaign_negatives(token, cmp1_updates, "Campaign 1 (Auto 0.39) — 15 keywords")
    total_success += s; total_errors += e

    s, e = archive_campaign_negatives(token, cmp2_updates, "Campaign 2 (Auto 0.49) — 24 keywords")
    total_success += s; total_errors += e

    s, e = archive_campaign_negatives(token, cmp3_updates, "Campaign 3 (Auto 0.29) — 19 keywords")
    total_success += s; total_errors += e

    print(f"\n=== TOTAL ===")
    print(f"Successfully archived: {total_success} / 58 keywords")
    if total_errors:
        print(f"Errors: {total_errors}")

"""Debug: inspect raw DataDive response structure - find competitors list."""

import urllib.request
import urllib.parse
import json
import ssl

API_KEY = "pDbBQZJBAd6rome2KvVWN2jxDxGRdSHWazx1KLF9"
BASE_URL = "https://api.datadive.tools"

ctx = ssl.create_default_context()

def api_get(path, params=None):
    url = BASE_URL + path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        "x-api-key": API_KEY,
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
            data = resp.read().decode("utf-8")
            return json.loads(data)
    except Exception as e:
        return {"error": str(e)}

raw = api_get("/v1/niches/u1y83aQfmK/competitors", params={"pageSize": 4})
data = raw.get("data", raw)
print("data keys:", list(data.keys()) if isinstance(data, dict) else "LIST")
if isinstance(data, dict):
    for k, v in data.items():
        if isinstance(v, list):
            print(f"  LIST key '{k}': {len(v)} items")
            if v:
                print(f"    First item keys: {list(v[0].keys()) if isinstance(v[0], dict) else type(v[0])}")
                print(f"    First item (first 500): {json.dumps(v[0])[:500]}")
        elif isinstance(v, dict):
            print(f"  DICT key '{k}': subkeys={list(v.keys())}")
        else:
            print(f"  SCALAR key '{k}': {str(v)[:100]}")

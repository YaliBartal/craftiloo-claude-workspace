#!/usr/bin/env python3
"""
filter_search_terms.py

Streams the Brand Analytics Search Terms .gz file and extracts only rows
where any of our ASINs appears in the top-3 clicked positions.

Runs in ~1-2 minutes. Uses ~50MB RAM regardless of input file size.

Usage:
    python3 filter_search_terms.py <gz_file_path> <asin1> [asin2 ...] [--output <path>]

Output:
    JSON array of matching rows. Written to --output path if provided, else stdout.

Actual Amazon BA Search Terms row structure (one row per ASIN per search term):
    {
        "departmentName": "...",
        "searchTerm": "...",
        "searchFrequencyRank": 1,
        "clickedAsin": "B0XXXXX",
        "clickedItemName": "Product Name",
        "clickShareRank": 1,        # 1, 2, or 3 — position in top-3
        "clickShare": 0.XX,
        "conversionShare": 0.XX
    }

NOTE: The structure is NOT denormalized with clickedAsin1/2/3 fields.
Each row = one (searchTerm, clickedAsin, clickShareRank) combination.
Each search term appears up to 3 times (once per rank position).
"""

import sys
import json
import gzip
import argparse

try:
    import ijson
except ImportError:
    print("Error: ijson not installed. Run: pip install ijson", file=sys.stderr)
    sys.exit(1)


def parse_args():
    parser = argparse.ArgumentParser(description="Filter BA Search Terms .gz for specific ASINs")
    parser.add_argument("gz_file", help="Path to the .gz file downloaded from Amazon")
    parser.add_argument("asins", nargs="+", help="One or more ASINs to filter for")
    parser.add_argument("--output", "-o", default=None, help="Output JSON file path (default: stdout)")
    return parser.parse_args()


def filter_search_terms(gz_path: str, our_asins: set) -> list:
    results = []
    processed = 0

    print(f"Reading: {gz_path}", file=sys.stderr)
    print(f"Filtering for {len(our_asins)} ASINs: {', '.join(sorted(our_asins))}", file=sys.stderr)

    with gzip.open(gz_path, "rb") as f:
        for item in ijson.items(f, "dataByDepartmentAndSearchTerm.item"):
            processed += 1

            if processed % 1_000_000 == 0:
                print(f"  Processed {processed:,} rows, {len(results)} matches so far...", file=sys.stderr)

            if item.get("clickedAsin") in our_asins:
                results.append(item)

    print(f"Done. Total rows: {processed:,} | Matches: {len(results)}", file=sys.stderr)
    return results


def main():
    args = parse_args()
    our_asins = set(args.asins)

    results = filter_search_terms(args.gz_file, our_asins)

    output_data = json.dumps(results, indent=2, default=float)

    if args.output:
        import os
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_data)
        print(f"Saved {len(results)} rows to: {args.output}", file=sys.stderr)
    else:
        print(output_data)


if __name__ == "__main__":
    main()

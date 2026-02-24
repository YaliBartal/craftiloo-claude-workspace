"""
Seller Board MCP Server
Exposes 5 Seller Board CSV report endpoints as MCP tools.
Each tool fetches the CSV data and returns it for analysis.
"""

import os
import csv
import io
from pathlib import Path
from mcp.server.fastmcp import FastMCP
import httpx


def _load_dotenv():
    """Load .env file from workspace root as fallback if env vars aren't set."""
    for d in [Path.cwd(), Path(__file__).resolve().parent.parent.parent]:
        env_file = d / ".env"
        if env_file.exists():
            with open(env_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, _, value = line.partition("=")
                        key = key.strip()
                        value = value.strip()
                        current = os.environ.get(key, "")
                        if key and (not current or current.startswith("${")):
                            os.environ[key] = value
            return


_load_dotenv()

mcp = FastMCP("sellerboard")

# Report configuration — env var name → description
REPORTS = {
    "inventory": {
        "env": "SELLERBOARD_INVENTORY_REPORT",
        "description": "FBA Inventory report — stock levels, ROI, margin, reorder recommendations, velocity, days of stock",
    },
    "sales_detailed": {
        "env": "SELLERBOARD_SALES_DETAILED",
        "description": "Sales Detailed report (59 cols) — per-ASIN organic/PPC sales, FBA fees, COGS, profit, ACOS, sessions by date",
    },
    "sales_summary": {
        "env": "SELLERBOARD_SALES_SUMMARY",
        "description": "Sales Summary report (41 cols) — daily financials, ad spend by channel, profit by ASIN/marketplace",
    },
    "daily_dashboard": {
        "env": "SELLERBOARD_DAILY_DASHBOARD",
        "description": "Daily Dashboard report (31 cols) — daily aggregate: sales, units, ad spend, profit, margin, sessions",
    },
    "ppc_marketing": {
        "env": "SELLERBOARD_PPC_MARKETING",
        "description": "PPC Marketing Performance report (15 cols) — PPC sales, organic turnover, ad spend, TACOS, ROAS, ACOS, CPC, conversion rate, period comparison",
    },
}


async def fetch_report(env_var: str) -> str:
    """Fetch CSV data from a Seller Board report URL."""
    url = os.environ.get(env_var)
    if not url:
        return f"Error: Environment variable {env_var} is not set. Check your .env file."

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        response = await client.get(url)
        if response.status_code != 200:
            return f"Error: HTTP {response.status_code} fetching report. The URL token may have expired — check Seller Board > Settings > Automation > Reports."
        return response.text


def csv_to_summary(csv_text: str, max_rows: int = 100) -> str:
    """Parse CSV and return a formatted summary with headers and data."""
    reader = csv.reader(io.StringIO(csv_text))
    rows = list(reader)

    if not rows:
        return "No data returned."

    headers = rows[0]
    data_rows = rows[1:]
    total_rows = len(data_rows)

    output = f"**Columns ({len(headers)}):** {', '.join(headers)}\n"
    output += f"**Total rows:** {total_rows}\n\n"

    # Return raw CSV (capped) for analysis
    displayed = data_rows[:max_rows]
    csv_output = io.StringIO()
    writer = csv.writer(csv_output)
    writer.writerow(headers)
    writer.writerows(displayed)

    output += csv_output.getvalue()

    if total_rows > max_rows:
        output += f"\n... ({total_rows - max_rows} more rows truncated)"

    return output


@mcp.tool()
async def get_inventory_report() -> str:
    """Fetch the FBA Inventory report from Seller Board.
    Returns stock levels, ROI, margin, reorder recommendations, velocity, and days of stock."""
    raw = await fetch_report("SELLERBOARD_INVENTORY_REPORT")
    if raw.startswith("Error:"):
        return raw
    return csv_to_summary(raw)


@mcp.tool()
async def get_sales_detailed_report() -> str:
    """Fetch the Sales Detailed report from Seller Board.
    Returns per-ASIN data: organic/PPC sales, FBA fees, COGS, profit, ACOS, sessions by date."""
    raw = await fetch_report("SELLERBOARD_SALES_DETAILED")
    if raw.startswith("Error:"):
        return raw
    return csv_to_summary(raw)


@mcp.tool()
async def get_sales_summary_report() -> str:
    """Fetch the Sales Summary report from Seller Board.
    Returns daily financials, ad spend by channel, profit by ASIN/marketplace."""
    raw = await fetch_report("SELLERBOARD_SALES_SUMMARY")
    if raw.startswith("Error:"):
        return raw
    return csv_to_summary(raw)


@mcp.tool()
async def get_daily_dashboard_report() -> str:
    """Fetch the Daily Dashboard report from Seller Board.
    Returns daily aggregate: sales, units, ad spend, profit, margin, sessions."""
    raw = await fetch_report("SELLERBOARD_DAILY_DASHBOARD")
    if raw.startswith("Error:"):
        return raw
    return csv_to_summary(raw)


@mcp.tool()
async def get_ppc_marketing_report() -> str:
    """Fetch the PPC Marketing Performance report from Seller Board.
    Returns PPC sales, organic turnover, ad spend, TACOS, ROAS, ACOS, CPC, conversion rate with period-over-period comparison."""
    raw = await fetch_report("SELLERBOARD_PPC_MARKETING")
    if raw.startswith("Error:"):
        return raw
    return csv_to_summary(raw)


@mcp.tool()
async def get_all_reports_summary() -> str:
    """Fetch all 5 Seller Board reports and return a combined summary.
    Useful for a complete business snapshot."""
    results = []
    for name, config in REPORTS.items():
        results.append(f"\n{'='*60}\n## {name.replace('_', ' ').title()}\n{'='*60}")
        raw = await fetch_report(config["env"])
        if raw.startswith("Error:"):
            results.append(raw)
        else:
            results.append(csv_to_summary(raw, max_rows=30))

    return "\n".join(results)


if __name__ == "__main__":
    mcp.run(transport="stdio")

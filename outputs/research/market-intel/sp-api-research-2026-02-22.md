# Amazon Selling Partner API (SP-API) Research

**Date:** 2026-02-22
**Purpose:** Comprehensive breakdown of SP-API capabilities, access requirements, MCP servers, and recommendations for Craftiloo

---

## 1. API Overview & Available Endpoints

SP-API is Amazon's REST-based API that replaced MWS (fully sunset March 2024). It gives sellers programmatic access to their business data across orders, inventory, listings, financials, reports, and more.

**Important 2026 change:** Amazon is moving SP-API to a **paid model** for third-party developers starting January 2026. However, **sellers using SP-API only for their own business are exempt from fees.**

---

## 2. API Categories & What Data You Can Pull

### A. Orders API
| Data Point | Description |
|-----------|-------------|
| Order details | Order ID, status, dates, fulfillment channel |
| Order items | ASINs, quantities, prices, tax |
| Buyer info | Shipping address (limited), buyer name |
| Order metrics | Aggregated order statistics |

**Use case:** Order tracking, fulfillment monitoring, sales velocity calculations.

---

### B. Catalog Items API
| Data Point | Description |
|-----------|-------------|
| Product search | Search by keyword, identifier, or brand |
| Item details | Title, brand, manufacturer, images, dimensions |
| Product identifiers | ASIN, UPC, EAN, ISBN |
| Classifications | Browse node, product type |
| Sales rank | **BSR data included in item attributes** |

**Use case:** Product research, competitor product analysis, catalog enrichment.

---

### C. Product Pricing API
| Data Point | Description |
|-----------|-------------|
| Competitive pricing | Current Buy Box price, landed price |
| Listing offers | All active offers on an ASIN |
| Item offers | Offer-level pricing data |
| Competitive summary | `getCompetitiveSummary` (v2022-05-01) -- detailed competitive pricing per ASIN |
| Price notifications | Subscribe to price change events |

**Use case:** Price monitoring, Buy Box tracking, competitive pricing analysis.

---

### D. Reports API (MAJOR data source)
This is the **most powerful API for analytics**. Report categories include:

#### Inventory Reports
- FBA inventory levels, age, health, planning
- Manage inventory (all listings)
- Reserved inventory, restock recommendations

#### Sales & Order Reports
- Flat file orders (all, pending, archived)
- Sales and traffic by ASIN and date
- Buy Box percentage per ASIN

#### Business Reports (via Data Kiosk)
- **Sales and Traffic by ASIN** -- ordered product sales, revenue, units, page views, buy box %
- **Sales and Traffic by Date** -- aggregate daily/weekly/monthly
- **Seller Economics** -- fees, ad spend, net proceeds, COGS tracking

#### Brand Analytics Reports (BRAND REGISTERED SELLERS ONLY)
- **Market Basket Analysis** -- items commonly purchased together
- **Amazon Search Terms Report** -- top search terms, click share, conversion share
- **Repeat Purchase Report** -- customer retention metrics
- **Search Query Performance (SQP)** -- impressions, clicks, purchases by search term at brand and ASIN level

#### FBA Reports
- Removal/return/reimbursement reports
- Long-term storage fees
- Stranded inventory

**Use case:** Daily sales tracking, traffic analysis, keyword performance, market basket insights, inventory management.

---

### E. Data Kiosk API (GraphQL)
A newer, more flexible reporting interface using GraphQL queries.

| Schema | Data Available |
|--------|---------------|
| `Analytics_SalesAndTraffic` | Sales and traffic by ASIN (parent/child/SKU) or by date (day/week/month) |
| `Analytics_vendorAnalytics` | Manufacturing view, sourcing view, costs, orders, availability |
| `Analytics_Economics` | Ad spend, unit costs, fees, net proceeds, sales breakdown by FNSKU/MSKU |

**Use case:** Custom analytics queries, bulk data pulls, financial analysis.

---

### F. Listings Items API
| Data Point | Description |
|-----------|-------------|
| Get listing | Full listing details by SKU |
| Put listing | Create/update listings |
| Patch listing | Partial updates (title, bullets, description) |
| Delete listing | Remove listings |
| Listing issues | Compliance/quality issues on listings |

**Use case:** Listing optimization, bulk listing updates, compliance monitoring.

---

### G. Feeds API
| Capability | Description |
|-----------|-------------|
| Submit feeds | Bulk data uploads (listings, prices, inventory) |
| Feed processing | Track feed submission status |

**Use case:** Bulk listing updates, price changes, inventory adjustments.

---

### H. Finances API
| Data Point | Description |
|-----------|-------------|
| Financial events | Individual transaction details |
| Financial event groups | Settlement periods |
| Shipment events | Per-shipment financial breakdown |

**Use case:** P&L tracking, fee analysis, refund monitoring.

---

### I. FBA Inventory API
| Data Point | Description |
|-----------|-------------|
| Inventory summaries | Stock levels across all FCs |
| Granular inventory | Per-FNSKU, per-condition breakdown |
| Inventory age | Days in warehouse |

**Use case:** Stock monitoring, restock planning, excess inventory alerts.

---

### J. Notifications API
| Capability | Description |
|-----------|-------------|
| Subscribe to events | Real-time notifications for order changes, pricing changes, listing changes |
| Event types | ANY_OFFER_CHANGED, ORDER_STATUS_CHANGE, ITEM_PRODUCT_TYPE_CHANGE, etc. |

**Use case:** Real-time monitoring, automated alerts, event-driven workflows.

---

### K. A+ Content API
| Capability | Description |
|-----------|-------------|
| Create A+ content | Rich product descriptions |
| Edit A+ content | Update existing content modules |
| Content status | Track approval status |

**Use case:** Enhanced product pages, brand storytelling.

---

## 3. Amazon Advertising API (SEPARATE from SP-API)

**Critical note:** The Advertising API is a **separate API** from SP-API with its own registration, credentials, and endpoints.

| Feature | Data Available |
|---------|---------------|
| **Sponsored Products** | Campaigns, ad groups, keywords, bids, targeting, search term reports |
| **Sponsored Brands** | Headline search campaigns, brand video ads |
| **Sponsored Display** | Audience targeting, retargeting campaigns |
| **DSP** | Demand-side platform programmatic ads |
| **Reports** | Performance metrics (impressions, clicks, spend, sales, ACoS, ROAS) |
| **Search Term Reports** | Actual customer search terms triggering ads |
| **Placement Reports** | Top of search, rest of search, product pages |
| **Campaign Management** | Create, update, pause campaigns programmatically |
| **Bid Optimization** | Adjust bids, set bid strategies |
| **Negative Keywords** | Add/manage negative keywords |

### 2025 Advertising API Updates
- **Unified Account Structure** (Oct 2025) -- single account for all ad products
- **Unified Reporting System** (Nov 2025) -- consolidated reporting across all campaign types
- **MCP Support** -- Amazon opened advertising APIs to AI agents through MCP protocol

**Registration:** `advertising.amazon.com/API` -- separate from SP-API registration.

---

## 4. How to Get Access

### Step 1: Prerequisites
- **Professional Seller Account** on Amazon (Individual accounts NOT eligible)
- **Brand Registry** (required for Brand Analytics reports)
- Active selling history recommended

### Step 2: Register as SP-API Developer
1. Go to **Seller Central > Apps & Services > Develop Apps**
2. Register as a developer (must be primary account user)
3. Choose application type:
   - **Private seller app** (for your own account only -- self-authorized, no OAuth needed)
   - **Public app** (for other sellers -- requires OAuth, website, review process)

### Step 3: Create AWS IAM Credentials
1. Create an **AWS account** (free)
2. Create an **IAM user** with programmatic access
3. Attach the SP-API execution role policy
4. Save the **Access Key ID** and **Secret Access Key**

### Step 4: Register Your Application
1. In Seller Central, register your app
2. Receive **LWA (Login with Amazon) credentials:**
   - Client ID
   - Client Secret
3. Generate a **Refresh Token** (for private apps, this is self-authorized)

### Step 5: Credentials Summary

| Credential | Source | Purpose |
|-----------|--------|---------|
| AWS Access Key ID | AWS IAM | API authentication |
| AWS Secret Access Key | AWS IAM | API authentication |
| LWA Client ID | Seller Central app registration | OAuth token exchange |
| LWA Client Secret | Seller Central app registration | OAuth token exchange |
| LWA Refresh Token | Self-authorization (private app) | Generate access tokens |
| Seller ID | Seller Central | Identify your account |
| Marketplace ID | Amazon (ATVPDKIKX0DER for US) | Target marketplace |

### For Advertising API (separate)
1. Go to `advertising.amazon.com`
2. Register for API access
3. Receive separate Client ID / Client Secret
4. Generate Advertising API refresh token

---

## 5. Existing MCP Servers for Amazon SP-API

### Option A: `amazon_sp_mcp` by jay-trivedi (RECOMMENDED)
**GitHub:** https://github.com/jay-trivedi/amazon_sp_mcp

**Status:** Phase 1 MVP -- functional for core operations

**Available Tools:**
| Category | Tools |
|----------|-------|
| **Sales** | `get_orders`, `get_order_details`, `get_sales_metrics` |
| **Returns** | `get_returns`, `get_return_details`, `get_refund_info` |
| **Inventory** | `get_inventory_summary`, `get_fba_inventory`, `get_inventory_health`, `check_stock_levels` |
| **Listings** | `get_listings`, `get_product_details`, `search_catalog` |
| **Reports** | `request_report`, `get_report`, `list_reports`, `get_report_document` |

**Planned (not yet built):** Pricing analysis, advertising integration, customer messaging, performance notifications

**Setup:**
```bash
git clone https://github.com/jay-trivedi/amazon_sp_mcp
cd amazon_sp_mcp
npm install
cp .env.example .env
# Add credentials to .env
npm run build
```

**MCP config for Claude Code:**
```json
{
  "mcpServers": {
    "amazon-sp": {
      "command": "node",
      "args": ["/path/to/amazon_sp_mcp/build/index.js"],
      "env": {
        "AWS_ACCESS_KEY_ID": "...",
        "AWS_SECRET_ACCESS_KEY": "...",
        "LWA_CLIENT_ID": "...",
        "LWA_CLIENT_SECRET": "...",
        "LWA_REFRESH_TOKEN": "...",
        "SELLER_ID": "...",
        "MARKETPLACE_ID": "ATVPDKIKX0DER"
      }
    }
  }
}
```

**Limitations:**
- Rate limiting (Amazon enforces strict limits, e.g., 0.0167 req/sec for Orders API)
- Some reports require async processing
- No advertising API integration yet
- Phase 1 -- may have rough edges

---

### Option B: `AmazonSeller-mcp-server` by mattcoatsworth
**GitHub:** https://github.com/mattcoatsworth/AmazonSeller-mcp-server

**Broader coverage** -- includes authentication, catalog management, inventory, orders, reports, feeds, financials, pricing, listings, FBA operations, and notifications.

**Setup:**
```bash
npm install amazon-sp-api-mcp-server
# or
npx amazon-sp-api-mcp-server
```

**Credentials needed:**
- `SP_API_CLIENT_ID`, `SP_API_CLIENT_SECRET`, `SP_API_REFRESH_TOKEN`
- `SP_API_AWS_ACCESS_KEY`, `SP_API_AWS_SECRET_KEY`
- `SP_API_ROLE_ARN`, `SP_API_MARKETPLACE_ID`, `SP_API_REGION`

---

### Option C: Build a Custom MCP Server
Given Craftiloo's specific needs, a custom MCP server could combine:
- SP-API for sales, inventory, listings, and reports
- Advertising API for PPC data
- Apify (already configured) for BSR/rank scraping where SP-API has gaps

---

## 6. Recommendations for Craftiloo

### Priority Matrix: What's Most Useful

| Use Case | Best API Source | Value | Effort |
|----------|----------------|-------|--------|
| **Daily BSR/rank tracking** | Catalog Items API + Apify scraping | HIGH | Medium |
| **PPC analysis** | Advertising API (SEPARATE) | HIGH | Medium |
| **Market research** | Brand Analytics reports (SQP, Search Terms, Market Basket) | HIGH | Low-Medium |
| **Product listing optimization** | Listings API + A+ Content API | HIGH | Low |
| **Competitor analysis** | Product Pricing API + Catalog Items API | HIGH | Medium |
| **Sales tracking** | Reports API / Data Kiosk | HIGH | Low |
| **Inventory management** | FBA Inventory API | MEDIUM | Low |

### Recommended Implementation Path

**Phase 1: Get SP-API Access (Week 1)**
1. Register as SP-API developer in Seller Central
2. Create AWS IAM credentials
3. Register private seller application
4. Generate refresh token
5. Test with basic API calls (orders, catalog)

**Phase 2: Install MCP Server (Week 1-2)**
1. Deploy `amazon_sp_mcp` (jay-trivedi) or `AmazonSeller-mcp-server` (mattcoatsworth)
2. Configure in `.mcp.json`
3. Test basic queries through Claude Code

**Phase 3: Brand Analytics Reports (Week 2-3)**
1. Set up automated report requests for:
   - Search Query Performance (daily/weekly)
   - Market Basket Analysis (weekly)
   - Sales and Traffic by ASIN (daily)
2. Build reporting workflow

**Phase 4: Advertising API (Week 3-4)**
1. Register for Advertising API access separately
2. Connect to campaign data
3. Pull search term reports, placement reports
4. Integrate with existing PPC analysis skill

**Phase 5: Automation (Ongoing)**
1. Daily BSR tracking (Catalog Items API + Apify as backup)
2. Automated PPC report pulls
3. Competitive price monitoring
4. Inventory alerts

### Key Limitations to Know

| Limitation | Impact | Workaround |
|-----------|--------|------------|
| **BSR is NOT real-time via API** | Catalog Items returns BSR but not historical | Use Apify for frequent polling; SP-API for snapshots |
| **Brand Analytics requires Brand Registry** | Can't get SQP/Market Basket without it | Craftiloo should already have this |
| **Advertising API is separate** | No single MCP covers both | Need two integrations or custom MCP |
| **Rate limits are strict** | Can't poll rapidly | Batch requests, use notifications API for events |
| **No direct competitor sales data** | Can't see competitor unit sales | Use BSR estimation, Brand Analytics search terms |

### Cost Considerations

- **For private seller apps (your own data):** FREE -- no subscription or API call fees
- **For third-party developers:** $1,400/year + tiered call pricing starting April 2026
- **Advertising API:** Free to use (no separate fee)
- **AWS costs:** Negligible (IAM is free, minimal Lambda/compute if used)

---

## Sources

- [Amazon SP-API Developer Portal](https://developer-docs.amazon.com/sp-api)
- [SP-API Report Type Values](https://developer-docs.amazon.com/sp-api/docs/report-type-values)
- [SP-API Registration Overview](https://developer-docs.amazon.com/sp-api/docs/sp-api-registration-overview)
- [AWS Prescriptive Guidance: Data Available Through SP-API](https://docs.aws.amazon.com/prescriptive-guidance/latest/strategy-gen-ai-selling-partner-api/data-sp-api.html)
- [Amazon Advertising API](https://advertising.amazon.com/API/docs/en-us/reference/api-overview)
- [Sponsored Products API Overview](https://advertising.amazon.com/API/docs/en-us/guides/sponsored-products/overview)
- [amazon_sp_mcp GitHub](https://github.com/jay-trivedi/amazon_sp_mcp)
- [AmazonSeller-mcp-server GitHub](https://github.com/mattcoatsworth/AmazonSeller-mcp-server)
- [SP-API Paid Model 2026 Announcement](https://developer.amazonservices.com/spp-announcement)
- [Amazon Advertising MCP Protocol Support](https://ppc.land/amazon-opens-its-advertising-apis-to-ai-agents-through-industry-protocol/)
- [Product Pricing API Reference](https://developer-docs.amazon.com/sp-api/docs/product-pricing-api-v0-reference)
- [Analytics Reports Documentation](https://developer-docs.amazon.com/sp-api/docs/report-type-values-analytics)

# MCP Server Reference

> Detailed tool-by-tool documentation for all MCP servers. CLAUDE.md has the compressed version (gotchas + env vars). This file has the full tables.

---

## Apify MCP Server (`mcp-servers/apify/server.py`)

Custom Python MCP server for Apify Platform API. Auth: Bearer token. Rate limiting: 0.5s between requests.

| Tool | API | Key Data |
|------|-----|----------|
| `search_store_actors` | Store Search | Find actors by use case — name, stats, actorId |
| `run_actor` | Run Actor (async) | Start actor, get run ID + dataset ID |
| `run_actor_sync` | Run Actor (sync) | Run + wait + return results (max 300s) |
| `get_run_status` | Run Details | Status, timing, compute units, dataset ID |
| `get_run_dataset` | Dataset Items | Scraped data from completed runs |
| `list_recent_runs` | List Runs | Recent runs with status, filterable by actor |
| `abort_run` | Abort Run | Cancel a running/ready actor |

**Commonly used actors:**
- `saswave~amazon-product-scraper` — Product data (BSR, price, reviews, ratings)
- `axesso_data~amazon-search-scraper` — Keyword search results (position, badges, prices). Input: `{"input": [{"keyword": "...", "country": "US"}]}`. Fields: `searchResultPosition` (0-indexed), `productDescription` (title), `price` (float), `productRating` (string), `countReview`, `salesVolume`, `sponsored` (bool).

---

## Seller Board MCP Server (`mcp-servers/sellerboard/server.py`)

Custom Python MCP server exposing 7 tools for all Seller Board CSV reports.

| Tool | Report | Key Data |
|------|--------|----------|
| `get_inventory_report` | FBA Inventory | Stock levels, ROI, margin, reorder recs, velocity |
| `get_sales_detailed_report` | Sales Detailed 30d (59 cols) | Per-ASIN: organic/PPC sales, fees, COGS, profit, ACOS, sessions |
| `get_sales_detailed_7d_report` | Sales Detailed 7d (41 cols) | Same as above but 7-day window (~460 rows). **Preferred for daily market intel.** |
| `get_sales_summary_report` | Sales Summary (41 cols) | Daily financials, ad spend by channel, profit by ASIN |
| `get_daily_dashboard_report` | Daily Dashboard (31 cols) | Daily aggregate: revenue, units, ad spend, profit, margin |
| `get_ppc_marketing_report` | PPC Marketing (15 cols) | PPC sales, organic turnover, TACOS, ROAS, ACOS, CPC, conversion |
| `get_all_reports_summary` | All 6 combined | Complete business snapshot |

---

## DataDive MCP Server (`mcp-servers/datadive/server.py`)

Custom Python MCP server exposing 12 tools for all DataDive API endpoints. Auth via `x-api-key` header. Built-in rate limiting (1 req/sec).

| Tool | Endpoint | Key Data |
|------|----------|----------|
| `get_profile` | Account Profile | Token balance, account info |
| `list_niches` | List Niches | nicheId, nicheLabel, heroKeyword (23 active) |
| `get_niche_keywords` | Master Keyword List | keyword, searchVolume, relevancy, organic/sponsored ranks |
| `get_niche_competitors` | Competitor Data | ASIN, BSR, sales, revenue, rating, reviews, P1 keywords |
| `get_niche_ranking_juices` | Ranking Juice | Title/bullets/description optimization scores |
| `get_niche_roots` | Keyword Roots | Root words, frequency, broadSearchVolume |
| `run_ai_copywriter` | AI Copywriter | Optimized listing copy (4 modes: cosmo, ranking-juice, nlp, cosmo-rufus) |
| `list_rank_radars` | List Rank Radars | 15 active radars, keyword counts, top10/50 stats |
| `get_rank_radar_data` | Rank Radar Data | Daily organicRank + impressionRank per keyword |
| `create_niche_dive` | Create Dive | Token-consuming niche discovery from seed ASIN |
| `get_niche_dive_status` | Dive Status | in_progress/success/error + results |
| `get_niche_overview` | Niche Overview | Combined competitors + keywords + roots snapshot |

---

## Amazon SP-API MCP Server (`mcp-servers/amazon-sp-api/server.py`)

Custom Python MCP server for direct Amazon Selling Partner API access. Auth: LWA OAuth2 (auto-refreshing access token). Rate limiting: 0.5s between requests.

| Tool | API | Key Data |
|------|-----|----------|
| `get_marketplace_participations` | Sellers | Registered marketplaces (US, CA, MX) |
| `get_orders` | Orders | Recent orders: ID, status, date, total, fulfillment |
| `get_order_items` | Orders | Line items for an order: ASIN, SKU, qty, price |
| `get_catalog_item` | Catalog 2022 | ASIN details: title, brand, images, dimensions, sales rank |
| `search_catalog` | Catalog 2022 | Search by keywords: matching ASINs with titles, brands |
| `get_competitive_pricing` | Pricing | Landed price, listing price, Buy Box data |
| `get_item_offers` | Pricing | All active offers for an ASIN with prices, seller info |
| `get_fba_inventory` | FBA Inventory | SKU/ASIN stock: fulfillable, inbound, reserved quantities |
| `create_report` | Reports | Request any Amazon report (orders, traffic, inventory) |
| `create_brand_analytics_report` | Brand Analytics | Calendar-aligned BA reports (see below) |
| `get_report_status` | Reports | Check report progress (DONE/IN_PROGRESS/FATAL) |
| `get_report_document` | Reports | Download completed report data (CSV/TSV/JSON) |
| `get_my_listings` | Reports | Shortcut: request all-listings report |
| `get_listing` | Listings | Current listing attributes: title, bullets, description, keywords, product type |
| `update_listing` | Listings | PATCH listing text: title, bullets, description, backend keywords |

### Brand Analytics Tool (`create_brand_analytics_report`)

| report_name | Data | Processing Time |
|-------------|------|----------------|
| `search_terms` | Top search keywords + top 3 clicked ASINs + click/conversion share | ~5 min |
| `market_basket` | Products frequently bought together with yours | ~45s |
| `repeat_purchase` | Repeat vs one-time purchase quantities per ASIN | ~60s |
| `sqp` | Search Query Performance — per-query impressions, clicks, carts, purchases (**requires asins param**) | ~60s |
| `scp` | Search Catalog Performance — same funnel metrics organized by ASIN | ~60s |

**Key parameters:** `period` (WEEK/MONTH/QUARTER), `periods_back` (default 1), `asins` (space-separated, required for sqp, max 200 chars)

**Registered roles:** Product Listing, Pricing, Brand Analytics, Amazon Fulfillment

---

## Amazon Ads API MCP Server (`mcp-servers/amazon-ads-api/server.py`)

Custom Python MCP server for Amazon Advertising API (SP/SB/SD campaigns). Auth: LWA OAuth2 (auto-refreshing). Rate limiting: 0.5s between requests. v3 endpoints use versioned Content-Type headers.

| Tool | Group | Key Capability |
|------|-------|----------------|
| `list_profiles` | Profiles | List advertising profiles (account IDs) |
| `list_sp_campaigns` | SP Campaigns | Filter by state/name/portfolio, paginated |
| `create_sp_campaigns` | SP Campaigns | Batch create campaigns |
| `update_sp_campaigns` | SP Campaigns | Batch update state/budget/bidding |
| `list_sp_ad_groups` | SP Ad Groups | Filter by campaign/state |
| `create_sp_ad_groups` | SP Ad Groups | Batch create ad groups |
| `update_sp_ad_groups` | SP Ad Groups | Batch update bid/state |
| `list_sp_keywords` | SP Keywords | Filter by campaign/ad group/state |
| `manage_sp_keywords` | SP Keywords | Create or update keywords (action param) |
| `list_sp_negative_keywords` | SP Negatives | Ad group level negatives |
| `manage_sp_negative_keywords` | SP Negatives | Create or update ad group negatives |
| `list_sp_campaign_negative_keywords` | SP Negatives | Campaign level negatives |
| `create_sp_campaign_negative_keywords` | SP Negatives | Create campaign level negatives |
| `update_sp_campaign_negative_keywords` | SP Negatives | Update campaign level negatives |
| `list_sp_targets` | SP Targeting | ASIN/category targets |
| `list_sp_product_ads` | SP Product Ads | List advertised ASINs in ad groups |
| `manage_sp_product_ads` | SP Product Ads | Create or update product ads (ASIN associations) |
| `manage_sp_targets` | SP Targeting | Create or update product targets |
| `manage_sp_negative_targets` | SP Targeting | Create or list negative targets |
| `get_sp_bid_recommendations` | SP Bids | Suggested bids by competitiveness |
| `get_sp_campaign_budget_usage` | SP Budget | Budget utilization + constraint check |
| `create_ads_report` | Reporting | Async report creation (6 presets) |
| `get_ads_report_status` | Reporting | Poll report status |
| `download_ads_report` | Reporting | Download + decompress + format |
| `list_sb_campaigns` | SB Campaigns | Sponsored Brands campaigns |
| `update_sb_campaigns` | SB Campaigns | Update SB state/budget |
| `list_sd_campaigns` | SD Campaigns | Sponsored Display campaigns |
| `update_sd_campaigns` | SD Campaigns | Update SD state/budget |
| `list_portfolios` | Portfolios | List all portfolios with IDs |
| `manage_portfolios` | Portfolios | Create or update portfolios |

**Report presets:** `sp_campaigns`, `sp_search_terms`, `sp_keywords`, `sp_targets`, `sp_placements`, `sp_purchased_products`

---

## Notion MCP Server (`mcp-servers/notion/server.py`)

Custom Python MCP server. Full workspace access with 28 tools in 7 groups. Auth: Bearer token. Rate limiting: 0.33s between requests (~3/sec).

| Tool | Group | Key Capability |
|------|-------|----------------|
| `search` | Search | Search pages/databases by title across workspace |
| `get_self` | Search | Verify integration connection |
| `get_page` | Pages | Page metadata + all properties |
| `get_page_property` | Pages | Single property with pagination |
| `create_page` | Pages | Create page (with optional initial content) |
| `update_page` | Pages | Update properties / archive |
| `move_page` | Pages | Move to new parent |
| `archive_page` | Pages | Soft-delete convenience wrapper |
| `get_blocks` | Blocks | Direct child blocks (auto-paginates) |
| `get_block` | Blocks | Single block details |
| `append_blocks` | Blocks | Raw JSON blocks (auto-chunks at 100) |
| `append_markdown` | Blocks | Simplified markdown → Notion blocks |
| `update_block` | Blocks | Update block content |
| `delete_block` | Blocks | Delete block + children |
| `get_page_tree` | Blocks | Recursive full page content (max 3 levels) |
| `get_database` | Databases | Schema, properties, types |
| `query_database` | Databases | Filter + sort + auto-paginate |
| `update_database` | Databases | Update title/description/schema |
| `create_database` | Databases | Create inline database with properties |
| `get_comments` | Comments | All comments on page/block |
| `add_comment` | Comments | Add discussion comment |
| `get_user` | Users | User name, email, type |
| `list_users` | Users | All workspace users |
| `create_page_with_content` | Higher-level | Page + full markdown content in one call |
| `replace_page_content` | Higher-level | Delete all blocks + append new content |
| `find_or_create_page` | Higher-level | Search → return if found, create if not |
| `delete_all_blocks` | Higher-level | Clear all blocks from a page |
| `get_child_pages` | Higher-level | List child pages under a parent |

---

## Slack MCP Server (`mcp-servers/slack/server.py`)

Custom Python MCP server. Single server handles both workspaces via `workspace` parameter. Auth: Bot token per workspace. Rate limiting: 1 req/sec (Slack Tier 2).

**Workspaces:**

| Key | Aliases | Team ID | Description |
|-----|---------|---------|-------------|
| `craft` | `crafti` | T06KHD4CS6N | Workspace 1 |
| `craftiloo` | — | T01Q3BTU0DA | Workspace 2 |

| Tool | Group | Slack API Method | Key Capability |
|------|-------|------------------|----------------|
| `list_workspaces` | Utility | — | Show configured workspaces + aliases |
| `list_channels` | Channels | `conversations.list` | List channels with pagination |
| `get_channel_info` | Channels | `conversations.info` | Channel details: topic, purpose, members |
| `create_channel` | Channels | `conversations.create` | Create public/private channel |
| `invite_to_channel` | Channels | `conversations.invite` | Invite users to channel |
| `set_channel_topic` | Channels | `conversations.setTopic` | Update channel topic |
| `post_message` | Messages | `chat.postMessage` | Post to channel |
| `reply_to_thread` | Messages | `chat.postMessage` (threaded) | Reply in thread |
| `add_reaction` | Messages | `reactions.add` | Add emoji reaction |
| `get_channel_history` | Messages | `conversations.history` | Recent messages |
| `get_thread_replies` | Messages | `conversations.replies` | Thread replies |
| `search_messages` | Messages | `search.messages` | Search across channels (needs user token) |
| `get_users` | Users | `users.list` | List workspace users |
| `get_user_profile` | Users | `users.profile.get` | User details |
| `upload_snippet` | Files | `files.upload` | Upload text/code snippet |
| `schedule_message` | Scheduling | `chat.scheduleMessage` | Schedule future message |
| `list_scheduled_messages` | Scheduling | `chat.scheduledMessages.list` | View pending messages |
| `delete_scheduled_message` | Scheduling | `chat.deleteScheduledMessage` | Cancel scheduled message |

---

## Asana MCP Server (`mcp-servers/asana/server.py`)

Custom Python MCP server. Full project/task management with 26 tools in 8 groups. Auth: Personal Access Token (Bearer). Rate limiting: 0.2s between requests (~5/sec).

| Tool | Group | Asana API | Key Capability |
|------|-------|-----------|----------------|
| `get_me` | User | `GET /users/me` | Current user info + workspace list |
| `list_workspaces` | User | `GET /workspaces` | All workspaces/organizations |
| `list_users` | User | `GET /workspaces/{gid}/users` | Users in a workspace |
| `list_teams` | Teams | `GET /organizations/{gid}/teams` | Teams in an organization |
| `list_projects` | Projects | `GET /workspaces/{gid}/projects` | Projects, filterable by team |
| `get_project` | Projects | `GET /projects/{gid}` | Full project details + members + custom fields |
| `create_project` | Projects | `POST /projects` | Create project with name, dates, team, color |
| `list_sections` | Sections | `GET /projects/{gid}/sections` | Sections within a project |
| `create_section` | Sections | `POST /projects/{gid}/sections` | Create section with ordering |
| `move_task_to_section` | Sections | `POST /sections/{gid}/addTask` | Move task between sections |
| `list_tasks` | Tasks | `GET /projects/{gid}/tasks` | Tasks by project, section, or assignee |
| `get_task` | Tasks | `GET /tasks/{gid}` | Full task details + notes + custom fields |
| `create_task` | Tasks | `POST /tasks` | Create task with assignee, dates, section |
| `update_task` | Tasks | `PUT /tasks/{gid}` | Update name, notes, completed, dates, assignee |
| `delete_task` | Tasks | `DELETE /tasks/{gid}` | Permanently delete a task |
| `list_subtasks` | Subtasks | `GET /tasks/{gid}/subtasks` | Child tasks under a parent |
| `create_subtask` | Subtasks | `POST /tasks/{gid}/subtasks` | Create subtask under parent |
| `get_task_stories` | Comments | `GET /tasks/{gid}/stories` | Comments + activity history |
| `add_comment` | Comments | `POST /tasks/{gid}/stories` | Add comment to a task |
| `list_tags` | Tags | `GET /workspaces/{gid}/tags` | All tags in workspace |
| `add_tag_to_task` | Tags | `POST /tasks/{gid}/addTag` | Tag a task |
| `remove_tag_from_task` | Tags | `POST /tasks/{gid}/removeTag` | Remove tag from task |
| `search_tasks` | Search | `GET /workspaces/{gid}/tasks/search` | Full-text search with filters |
| `add_dependency` | Dependencies | `POST /tasks/{gid}/addDependencies` | Set task dependency |
| `get_dependencies` | Dependencies | `GET /tasks/{gid}/dependencies` | Tasks this task depends on |
| `get_dependents` | Dependencies | `GET /tasks/{gid}/dependents` | Tasks blocked by this task |

# Asana-Driven Agent Orchestration Plan

> **Date:** 2026-03-13 | **Status:** Planning | **Phase:** Architecture Design

---

## Vision

Transform Asana from a passive task tracker into the **central work queue** for all Claude agents. Every skill run becomes an Asana task with status tracking, human review gates, and dependency chains.

**Before:** `n8n schedule → skill-runner → Claude → Slack notification`
**After:** `n8n schedule → Asana task created → agent picks up → executes → updates Asana → human reviews → next task unblocks`

---

## Architecture Flowcharts

### 1. Core Agent Loop

```mermaid
flowchart TD
    A[/"n8n Trigger (schedule or webhook)"/] --> B["Create Asana Task\nin Queued section"]
    B --> C{"Agent Picks Up\nHighest Priority Task"}
    C --> D["Move Task → Running"]
    D --> E["Read Task Description\nfor Parameters"]
    E --> F["Execute Skill\n(skill-runner.py)"]
    F --> G{Success?}
    G -->|Yes| H{"Has tag:\nneeds-human-review?"}
    G -->|No| I["Move Task → Inbox\n+ Add error tag\n+ Comment with error details"]
    I --> J[/"Human Investigates\nRetry or Reassign"/]
    H -->|Yes| K["Post Results as Comment\nMove Task → Needs Review"]
    H -->|No| L["Post Results as Comment\nMove Task → Done\n(auto-complete)"]
    K --> M[/"Human Reviews Results"/]
    M --> N{Approved?}
    N -->|Yes| O["Move Task → Approved\nDependent tasks unblock"]
    N -->|No| P["Comment with feedback\nMove Task → Queued\n(re-run with changes)"]
    O --> Q["Move Task → Done"]

    style A fill:#4a90d9,color:#fff
    style C fill:#f5a623,color:#fff
    style G fill:#d0021b,color:#fff
    style H fill:#7b68ee,color:#fff
    style K fill:#f5a623,color:#fff
    style L fill:#4caf50,color:#fff
    style N fill:#d0021b,color:#fff
    style O fill:#4caf50,color:#fff
    style Q fill:#4caf50,color:#fff
```

### 2. Asana Project Board Structure

```mermaid
flowchart LR
    subgraph Board["Claude Agent Operations"]
        direction LR
        IN["📥 Inbox\n─────────\nNew tasks\nAnomaly alerts\nFailed tasks"]
        QU["📋 Queued\n─────────\nApproved by human\nWaiting for agent\nPriority-ordered"]
        RU["⚡ Running\n─────────\nAgent executing\nOne per skill\nTimeout: 25min"]
        NR["👁️ Needs Review\n─────────\nAgent finished\nResults posted\nHuman must verify"]
        AP["✅ Approved\n─────────\nHuman verified\nUnblocks dependents\nReady to archive"]
        DN["📦 Done\n─────────\nCompleted\nArchived weekly"]
    end
    IN --> QU --> RU --> NR --> AP --> DN

    style IN fill:#e8eaf6
    style QU fill:#fff3e0
    style RU fill:#fff9c4
    style NR fill:#fce4ec
    style AP fill:#e8f5e9
    style DN fill:#f5f5f5
```

### 3. Daily Operations Flow

```mermaid
flowchart TD
    subgraph Morning["☀️ Morning Automation (7:50 AM)"]
        T1["n8n: Create Task\n'Daily Market Intel — Mar 13'"]
        T2["n8n: Create Task\n'Daily PPC Health — Mar 13'"]
    end

    T1 --> A1["Agent runs\ndaily-market-intel"]
    T2 --> A2["Agent runs\nppc-daily-health"]

    A1 --> R1{"Anomaly\nDetected?"}
    A2 --> R2{"Anomaly\nDetected?"}

    R1 -->|No| D1["Auto-complete\n→ Done"]
    R1 -->|Yes| AN1["Create Alert Task\n⚠️ BSR Drop / Stockout"]

    R2 -->|No| D2["Auto-complete\n→ Done"]
    R2 -->|Yes| AN2["Create Alert Task\n⚠️ Spend Spike / CTR Drop"]

    AN1 --> INB["→ Inbox\nHigh Priority\nAssigned to Yali"]
    AN2 --> INB

    INB --> HUM[/"Human Reviews Alert\nDecides Action"/]
    HUM --> FOL["Creates Follow-up\nTask in Queued"]

    D1 --> SL["Post Summary\nto Slack"]
    D2 --> SL

    style Morning fill:#fff3e0
    style D1 fill:#4caf50,color:#fff
    style D2 fill:#4caf50,color:#fff
    style AN1 fill:#ff5722,color:#fff
    style AN2 fill:#ff5722,color:#fff
    style INB fill:#e8eaf6
```

### 4. Tuesday PPC Pipeline (Dependency Chain)

```mermaid
flowchart TD
    subgraph Chain["Tuesday PPC Pipeline — Week of Mar 10"]
        TC["TACoS Analysis\n⏱️ ~15 min"]
        PS["Portfolio Summary\n⏱️ ~20 min"]
        KR["Keyword Rank Optimizer\n⏱️ ~15 min"]
        BR["Bid Recommender\n⏱️ ~20 min"]
        ST["Search Term Harvester\n⏱️ ~15 min"]
    end

    TC -->|"auto-complete\n(read-only)"| PS
    PS -->|"auto-complete\n(read-only)"| KR
    KR -->|"auto-complete\n(read-only)"| BR
    BR -->|"⛔ REVIEW GATE\n(writes bids)"| HUM1
    HUM1[/"Human Reviews\nBid Changes"/]
    HUM1 -->|Approved| ST
    HUM1 -->|Rejected| BR2["Revise Bids\n(re-queued)"]
    BR2 --> HUM1
    ST -->|"⛔ REVIEW GATE\n(negates keywords)"| HUM2
    HUM2[/"Human Reviews\nNegations"/]
    HUM2 -->|Approved| DONE["✅ Pipeline Complete"]

    style TC fill:#e3f2fd
    style PS fill:#e3f2fd
    style KR fill:#e3f2fd
    style BR fill:#fff3e0
    style ST fill:#fff3e0
    style HUM1 fill:#fce4ec
    style HUM2 fill:#fce4ec
    style DONE fill:#4caf50,color:#fff
```

### 5. Product Launch Workflow (Barbie Kits)

```mermaid
flowchart TD
    PARENT["🎀 Launch Barbie Cross Stitch Kit\n(Parent Task)"]

    PARENT --> S1["Subtask 1:\nCompetitor Research\n─────────\nSkill: niche-category-analysis\nTag: auto-complete"]
    S1 --> S2["Subtask 2:\nCreate Amazon Listing\n─────────\nSkill: listing-manager (NEW)\nTag: needs-human-review"]
    S2 --> REV1[/"Human Reviews\nListing Copy"/]
    REV1 -->|"✏️ Edit needed"| S2
    REV1 -->|"✅ Approved"| S3
    S3["Subtask 3:\nImage Plan\n─────────\nSkill: image-planner\nTag: needs-human-review"]
    S3 --> REV2[/"Human Reviews\nImage Strategy"/]
    REV2 -->|"✅ Approved"| S4
    S4["Subtask 4:\nCreate PPC Campaigns\n─────────\nSkill: ppc-campaign-creator\nTag: needs-human-review"]
    S4 --> REV3[/"Human Reviews\nCampaign Structure"/]
    REV3 -->|"✅ Approved"| S5
    S5["Subtask 5:\nPost-Launch Monitor (7d)\n─────────\nSkill: daily-market-intel\nDue: +7 days\nTag: auto-complete"]
    S5 --> DONE["🎉 Launch Complete"]

    style PARENT fill:#e91e63,color:#fff
    style S1 fill:#e3f2fd
    style S2 fill:#fff3e0
    style S3 fill:#fff3e0
    style S4 fill:#fff3e0
    style S5 fill:#e3f2fd
    style DONE fill:#4caf50,color:#fff
```

### 6. Listing Optimization Cycle

```mermaid
flowchart TD
    TRIG["Weekly Trigger:\nRun listing-optimizer\non all hero products"] --> SCAN["Agent scans\n13 hero products"]

    SCAN --> CHECK{"Product\nScore < 70?"}
    CHECK -->|"Score ≥ 70"| SKIP["Skip — no action"]
    CHECK -->|"Score < 70"| CREATE["Create Asana Task:\n'Optimize Listing — {Product}'"]

    CREATE --> SUB1["Subtask: Rewrite Bullets\nTag: needs-human-review"]
    SUB1 --> REV[/"Human Reviews\nNew Copy"/]
    REV -->|Approved| SUB2["Subtask: Update Backend Keywords"]
    SUB2 --> SUB3["Subtask: Measure Impact\nSkill: listing-ab-analyzer\nDue: +14 days"]
    SUB3 --> REPORT["Results Posted:\nRevenue delta, rank changes,\nconversion impact"]

    style TRIG fill:#4a90d9,color:#fff
    style CHECK fill:#f5a623,color:#fff
    style CREATE fill:#e3f2fd
    style SUB1 fill:#fff3e0
    style REV fill:#fce4ec
    style SUB2 fill:#e3f2fd
    style SUB3 fill:#e3f2fd
    style REPORT fill:#4caf50,color:#fff
```

### 7. System-Wide Architecture

```mermaid
flowchart TD
    subgraph Triggers["Trigger Layer"]
        SCH["⏰ n8n Schedules\n(cron-based)"]
        MAN["👤 Human\n(manual task creation)"]
        AGT["🤖 Agent\n(anomaly detection)"]
    end

    subgraph Asana["Asana Work Queue"]
        TASK["Task Pool\n(Queued section)"]
    end

    subgraph Execution["Execution Layer"]
        SR["skill-runner.py\n(picks from queue)"]
        CL["Claude Agent\n(executes skill)"]
        MCP["MCP Services\n(Amazon, DataDive, etc.)"]
    end

    subgraph Output["Output Layer"]
        FILES["📁 Output Files\n(outputs/research/)"]
        SLACK["💬 Slack\n(notifications)"]
        ASANA_CMT["📝 Asana Comments\n(results summary)"]
    end

    subgraph Review["Review Layer"]
        HUM["👁️ Human Review\n(Needs Review section)"]
        AUTO["🤖 Auto-Complete\n(read-only tasks)"]
    end

    SCH --> TASK
    MAN --> TASK
    AGT --> TASK
    TASK --> SR
    SR --> CL
    CL --> MCP
    CL --> FILES
    CL --> SLACK
    CL --> ASANA_CMT
    ASANA_CMT --> HUM
    ASANA_CMT --> AUTO
    HUM -->|"Approved"| TASK
    AUTO --> DONE["✅ Done"]
    HUM -->|"Next task unblocked"| TASK

    style Triggers fill:#e8eaf6
    style Asana fill:#fff3e0
    style Execution fill:#e3f2fd
    style Output fill:#f3e5f5
    style Review fill:#e8f5e9
```

---

## Review Gate Policy

| Skill Type | Review Needed? | Rationale |
|------------|---------------|-----------|
| **Read-only analysis** (market-intel, PPC health, TACoS) | No — auto-complete | No risk, informational only |
| **Bid changes** (bid-recommender) | **Yes** | Money at stake, irreversible short-term |
| **Keyword negation** (search-term-harvester) | **Yes** | Can kill traffic to good terms |
| **Campaign creation** (ppc-campaign-creator) | **Yes** | Structural change, budget commitment |
| **Listing copy** (listing-manager, listing-optimizer) | **Yes** | Customer-facing, brand impact |
| **Image planning** (image-planner) | **Yes** | Drives photography/design spend |
| **Competitor research** (niche-analysis, review-analyzer) | No — auto-complete | No writes, pure research |

---

## Asana Custom Fields (Proposed)

| Field | Type | Values | Purpose |
|-------|------|--------|---------|
| `skill` | Dropdown | All 28 skill names | Which agent handles this |
| `priority` | Dropdown | Critical / High / Medium / Low | Queue ordering |
| `run-type` | Dropdown | Scheduled / Reactive / Manual | How the task was created |
| `review-gate` | Checkbox | True/False | Does human need to approve? |
| `parameters` | Text | JSON blob | Skill input (ASIN, portfolio, dates) |
| `output-path` | Text | File path | Where results were saved |
| `run-duration` | Number | Minutes | Execution time tracking |

---

## Implementation Phases

### Phase 1: Foundation (1 session)
- [ ] Create "Claude Agent Operations" project in Asana
- [ ] Set up 6 sections (Inbox → Queued → Running → Needs Review → Approved → Done)
- [ ] Create custom fields
- [ ] Create tags: `needs-human-review`, `auto-complete`, `anomaly`, `error`
- [ ] Build Asana helper functions in skill-runner.py

### Phase 2: Daily Skills (1-2 sessions)
- [ ] n8n creates Asana tasks for daily-market-intel and ppc-daily-health
- [ ] skill-runner reads from Asana queue instead of direct execution
- [ ] Auto-complete for routine runs, alert tasks for anomalies
- [ ] Slack notifications still fire (parallel to Asana)

### Phase 3: Dependency Chains (1 session)
- [ ] Tuesday PPC pipeline as linked Asana tasks with dependencies
- [ ] Review gates on bid-recommender and search-term-harvester
- [ ] n8n polls Approved section to trigger next skill

### Phase 4: Reactive Workflows (1 session)
- [ ] Skills create follow-up tasks on anomaly detection
- [ ] Product launch parent+subtask templates
- [ ] Listing optimization cycle with scheduled impact measurement

---

## Key Design Decisions

| Decision | Choice | Reasoning |
|----------|--------|-----------|
| Review gate default | **Opt-in** (tag-based) | Most runs are read-only; don't slow them down |
| Task creation | **n8n for scheduled, skills for reactive** | Clean separation of concerns |
| Parameters | **Custom fields for structured, description for context** | Parseable by agent + readable by human |
| Failure handling | **Move to Inbox + error tag** | Human decides retry vs. investigate |
| Slack integration | **Keep parallel** | Slack for quick alerts, Asana for tracking |

---
name: automation-discovery-interview
description: 30-40 minute structured interview to map workflows and identify automation opportunities with interactive dashboard output
triggers:
  - automation audit
  - map my workflows
  - what should I automate
  - business audit
  - automation discovery
  - find automation opportunities
output_location: outputs/data/automation-dashboard-[date].html
---

# Automation Discovery Interview

**USE WHEN** user says: "automation audit", "map my workflows", "what should I automate", "business audit", "automation discovery"

---

## ⚠️ BEFORE YOU START — Read Lessons

**MANDATORY FIRST STEP:** Read `LESSONS.md` in this skill's folder before doing anything else.

1. Read `.claude/skills/automation-discovery-interview/LESSONS.md`
2. Check **Known Issues** — plan around these
3. Check **Repeat Errors** — if you encounter one during this run, tell the user immediately: _"⚠️ Repeat issue (×N): [description]"_
4. Apply all past lessons to this run

**Do NOT skip this step.**

---

## What This Does

Conducts a 30-40 minute structured interview to:
1. Map the seller's actual workflows (not what they think they do)
2. Identify where AI/automation fits across three levels
3. Generate an interactive dashboard with clear recommendations

---

## Automation Level Framework

| Level | When to Use | Build With |
|-------|-------------|------------|
| 🎯 **Advisor** | Nuanced, strategic work requiring judgment | Claude as thinking partner (no build) |
| 🛠️ **Assistant** | Repeatable workflows with structure | Claude Skills + MCPs |
| ⚡ **Automation** | High-volume, deterministic, crystal-clear process | n8n or similar |

**Key principle:** Most work belongs at Advisor or Assistant. Full automation is rare and requires certainty.

### Categorization Guidelines

**🎯 Advisor Level** — Assign when:
- Requires significant judgment or strategic thinking
- Context-dependent decisions
- Nuanced analysis of market/business conditions
- Too complex or variable to systematize
- Examples: PPC strategy, business planning, creative decisions

**🛠️ Assistant Level** — Assign when:
- Repeatable structure exists
- Mix of judgment + execution
- Follows consistent procedure with some variation
- Can be triggered manually
- Examples: Review analysis, competitor reports, performance dashboards

**⚡ Automation Level** — Assign when:
- High volume and frequency
- Completely deterministic
- Clear triggers and outputs
- No judgment required
- ROI justifies build effort
- Examples: Inventory alerts, data syncing, notification triggers

**❌ Not Ready** — Assign when:
- Process isn't well-defined
- Too low volume to justify effort
- Requires too much human judgment
- Lacks clear structure

---

## Interview Structure

### Phase 1: Prep (5 min)

**Goal:** Understand role, responsibilities, and tools.

**Opening:**
> "Let's map out your operations so I can show you exactly where AI and automation can help. I'll ask about your role, main responsibilities, tools, and team structure.
>
> Walk me through your role in 2-3 sentences—what are you primarily responsible for?"

**Follow-up questions** (ask 2-3 at once):
- What are your 5-7 main responsibilities? (List them—we'll prioritize next)
- What tools do you use most frequently? (Seller Central, Helium 10, Notion, spreadsheets, etc.)
- Team context: Are you solo, or do you manage others? Who do you report to / work with?

**Transition:**
> "Thanks for sharing. I can see you're [Role] responsible for [brief summary]. Let's understand where your time actually goes."

---

### Phase 2: Quick Time Assessment (10 min)

**Goal:** Quantify time spent on each responsibility.

Go through each responsibility. For each one, ask:
- How much time per week/month?
- Frequency (daily, weekly, monthly, ad-hoc)?
- Quick confirmation: Is this accurately described?

**Ask about 2-3 responsibilities at a time** to maintain flow.

**Example:**
> "Let's start with [R1] and [R2]:
> - For [R1], how much time per week? Daily task or weekly?
> - For [R2], same question—time investment and frequency?
> - Does the description capture what you actually do, or should we adjust?"

**After all responsibilities**, summarize:
> "Based on what you've shared, these [X] responsibilities account for roughly [Y] hours per week. Does that sound right? Anything major we're missing?"

---

### Phase 3: Deep Dive (25 min)

**Goal:** Understand workflows in detail for top time investments.

Identify the **top 3-4 responsibilities by time investment**.

#### For top 3-4 (deep dive, 6-8 min each):

**Opening:**
> "Let's dive deeper into [Responsibility]. Walk me through your typical process."

**Follow-up questions** (ask 2-3 at a time):
- What triggers this work? (Scheduled, request-based, alert-based?)
- What data or inputs do you need? Where does that data come from?
- What tools do you use? Walk me through the steps.
- Where do you make decisions or judgments? What are you analyzing?
- What's the output? Who receives it or where does it go?

**Probe vague answers:**
> "Can you give me a specific example of the last time you did this?"

**Redirect rambling:**
> "Got it. Let me focus on [specific aspect]..."

#### For remaining responsibilities (quick overview, 2-3 min each):

**Ask:**
- What triggers this?
- High-level process (one sentence)
- What's the output?

---

### Phase 4: Closing & Validation (5 min)

**Goal:** Confirm accuracy before generating dashboard.

> "Before I create your dashboard, let me make sure I captured everything:
> - [Summarize main workflows with key details]
> - [Note any gaps or unclear areas]
>
> Does this sound accurate? Anything I missed or got wrong?"

**If they confirm**, proceed to generate dashboard.

---

## Interview Style

- **Conversational but efficient** — move quickly without rushing
- **Ask 2-4 questions at once** to maintain flow
- **Probe vague answers** with specific examples
- **Don't infer or fill gaps** — if unclear, ask
- **Redirect gently** if they ramble
- **Keep them talking about process**, not philosophy

---

## Constraints

- Do not recommend automation without understanding the full workflow
- Do not oversell automation — most processes aren't ready
- If seller has <3 people on team, flag that automation may be premature
- Escalate to human review for regulated/compliance-heavy workflows

---

## Dashboard Generation

After completing the interview, generate a self-contained HTML dashboard.

### Dashboard Data Structure

Populate this structure based on interview responses:

```javascript
const dashboardData = {
  overview: {
    role: "[Their role]",
    timeMapped: "[Total hours/week]",
    workflowsAnalyzed: [Number],
    keyFinding: "[One-sentence insight]"
  },

  timeBreakdown: [
    {
      responsibility: "[Name]",
      timePerWeek: "[X hrs]",
      frequency: "[Daily/Weekly/Monthly]",
      complexity: "[High/Medium/Low]"
    }
  ],

  advisorLevel: [
    {
      workflow: "[Name]",
      why: "[Why advisor-level]",
      whatToBuild: "[Agent recommendation]",
      implementation: ["Step 1", "Step 2", "Step 3"],
      impact: "[Expected impact]"
    }
  ],

  assistantLevel: [
    {
      workflow: "[Name]",
      why: "[Why assistant-level]",
      whatToBuild: "[Claude Skill recommendation]",
      implementation: ["Step 1", "Step 2", "Step 3"],
      impact: "[Time savings]"
    }
  ],

  automationLevel: [
    {
      workflow: "[Name]",
      why: "[Why automation-level]",
      whatToBuild: "[n8n automation]",
      implementation: ["Step 1", "Step 2", "Step 3"],
      impact: "[Time savings]"
    }
  ],

  quickWins: [
    { action: "[Specific action]", tool: "[Tool/skill]" }
  ],

  notReady: [
    { workflow: "[Name]", reason: "[Why not ready]" }
  ],

  nextSteps: {
    thisWeek: "[Quick win]",
    thisMonth: "[First assistant skill]",
    thisQuarter: "[Automation consideration]"
  }
};
```

### Quality Check Before Delivery

Verify:
- [ ] All workflows from interview are represented
- [ ] Automation levels are justified by interview details
- [ ] Time breakdown matches what they shared
- [ ] Quick wins are achievable this week
- [ ] "Not Ready" section is honest with clear reasoning
- [ ] Recommendations are specific, not generic
- [ ] Implementation steps are actionable

---

## HTML Dashboard Template

Generate a complete HTML file using this template. Replace `DASHBOARD_DATA_HERE` with the actual JSON data from the interview.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Automation Discovery Dashboard</title>
  <script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
  <script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    .tab-active { border-bottom: 3px solid; }
    .card-expand { transition: max-height 0.3s ease-out; overflow: hidden; }
  </style>
</head>
<body class="bg-gray-50">
  <div id="root"></div>

  <script type="text/babel">
    const dashboardData = DASHBOARD_DATA_HERE;

    function App() {
      const [activeTab, setActiveTab] = React.useState('overview');
      const [expandedCards, setExpandedCards] = React.useState({});

      const toggleCard = (id) => {
        setExpandedCards(prev => ({ ...prev, [id]: !prev[id] }));
      };

      const tabs = [
        { id: 'overview', label: 'Overview', icon: '📊' },
        { id: 'advisor', label: 'Advisor', icon: '🎯', color: 'blue' },
        { id: 'assistant', label: 'Assistant', icon: '🛠️', color: 'green' },
        { id: 'automation', label: 'Automation', icon: '⚡', color: 'orange' },
        { id: 'roadmap', label: 'Roadmap', icon: '🗺️' }
      ];

      const WorkflowCard = ({ item, color, index }) => {
        const id = `${color}-${index}`;
        const isExpanded = expandedCards[id];
        const colorClasses = {
          blue: 'border-blue-500 bg-blue-50',
          green: 'border-green-500 bg-green-50',
          orange: 'border-orange-500 bg-orange-50'
        };

        return (
          <div className={`border-l-4 ${colorClasses[color]} p-4 rounded-r-lg mb-4`}>
            <div
              className="flex justify-between items-start cursor-pointer"
              onClick={() => toggleCard(id)}
            >
              <div>
                <h3 className="font-semibold text-lg">{item.workflow}</h3>
                <p className="text-gray-600 text-sm mt-1">{item.why}</p>
              </div>
              <span className="text-xl">{isExpanded ? '−' : '+'}</span>
            </div>

            {isExpanded && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <div className="mb-3">
                  <span className="font-medium">What to Build:</span>
                  <p className="text-gray-700">{item.whatToBuild}</p>
                </div>
                <div className="mb-3">
                  <span className="font-medium">Implementation:</span>
                  <ol className="list-decimal list-inside text-gray-700 mt-1">
                    {item.implementation.map((step, i) => (
                      <li key={i} className="ml-2">{step}</li>
                    ))}
                  </ol>
                </div>
                <div className="bg-white p-2 rounded inline-block">
                  <span className="font-medium">Impact:</span> {item.impact}
                </div>
              </div>
            )}
          </div>
        );
      };

      return (
        <div className="max-w-5xl mx-auto p-6">
          <header className="mb-8">
            <h1 className="text-3xl font-bold text-gray-800">Automation Discovery Dashboard</h1>
            <p className="text-gray-600 mt-2">
              {dashboardData.overview.role} • {dashboardData.overview.timeMapped} mapped • {dashboardData.overview.workflowsAnalyzed} workflows analyzed
            </p>
          </header>

          {/* Tabs */}
          <nav className="flex space-x-1 border-b border-gray-200 mb-6">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-3 font-medium transition-colors ${
                  activeTab === tab.id
                    ? `tab-active border-${tab.color || 'gray'}-500 text-gray-900`
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                {tab.icon} {tab.label}
              </button>
            ))}
          </nav>

          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div>
              <div className="bg-white p-6 rounded-xl shadow-sm mb-6">
                <h2 className="text-xl font-semibold mb-4">Key Finding</h2>
                <p className="text-lg text-gray-700">{dashboardData.overview.keyFinding}</p>
              </div>

              <div className="bg-white p-6 rounded-xl shadow-sm mb-6">
                <h2 className="text-xl font-semibold mb-4">Time Breakdown</h2>
                <div className="space-y-3">
                  {dashboardData.timeBreakdown.map((item, i) => (
                    <div key={i} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div>
                        <span className="font-medium">{item.responsibility}</span>
                        <span className="text-gray-500 text-sm ml-2">({item.frequency})</span>
                      </div>
                      <div className="flex items-center gap-4">
                        <span className={`px-2 py-1 rounded text-xs ${
                          item.complexity === 'High' ? 'bg-red-100 text-red-700' :
                          item.complexity === 'Medium' ? 'bg-yellow-100 text-yellow-700' :
                          'bg-green-100 text-green-700'
                        }`}>
                          {item.complexity}
                        </span>
                        <span className="font-semibold">{item.timePerWeek}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-white p-6 rounded-xl shadow-sm">
                <h2 className="text-xl font-semibold mb-4">🚀 Quick Wins (This Week)</h2>
                <div className="space-y-2">
                  {dashboardData.quickWins.map((win, i) => (
                    <div key={i} className="flex items-center gap-3 p-3 bg-green-50 rounded-lg">
                      <span className="text-green-600">✓</span>
                      <span>{win.action}</span>
                      <span className="text-sm text-gray-500">→ {win.tool}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Advisor Tab */}
          {activeTab === 'advisor' && (
            <div>
              <div className="mb-4 p-4 bg-blue-50 rounded-lg">
                <p className="text-blue-800">
                  <strong>🎯 Advisor Level:</strong> These workflows require nuanced judgment.
                  Use Claude as a strategic thinking partner—no automation needed.
                </p>
              </div>
              {dashboardData.advisorLevel.length > 0 ? (
                dashboardData.advisorLevel.map((item, i) => (
                  <WorkflowCard key={i} item={item} color="blue" index={i} />
                ))
              ) : (
                <p className="text-gray-500 italic">No workflows identified at this level.</p>
              )}
            </div>
          )}

          {/* Assistant Tab */}
          {activeTab === 'assistant' && (
            <div>
              <div className="mb-4 p-4 bg-green-50 rounded-lg">
                <p className="text-green-800">
                  <strong>🛠️ Assistant Level:</strong> These workflows have repeatable structure.
                  Build as Claude Skills with MCPs—manually triggered but streamlined.
                </p>
              </div>
              {dashboardData.assistantLevel.length > 0 ? (
                dashboardData.assistantLevel.map((item, i) => (
                  <WorkflowCard key={i} item={item} color="green" index={i} />
                ))
              ) : (
                <p className="text-gray-500 italic">No workflows identified at this level.</p>
              )}
            </div>
          )}

          {/* Automation Tab */}
          {activeTab === 'automation' && (
            <div>
              <div className="mb-4 p-4 bg-orange-50 rounded-lg">
                <p className="text-orange-800">
                  <strong>⚡ Automation Level:</strong> These workflows are high-volume and deterministic.
                  Build with n8n or similar—fully automated, no human trigger needed.
                </p>
              </div>
              {dashboardData.automationLevel.length > 0 ? (
                dashboardData.automationLevel.map((item, i) => (
                  <WorkflowCard key={i} item={item} color="orange" index={i} />
                ))
              ) : (
                <p className="text-gray-500 italic">No workflows ready for full automation yet. This is normal—most work belongs at Advisor or Assistant level.</p>
              )}

              {dashboardData.notReady.length > 0 && (
                <div className="mt-8">
                  <h3 className="text-lg font-semibold mb-3 text-gray-700">❌ Not Ready for Automation</h3>
                  {dashboardData.notReady.map((item, i) => (
                    <div key={i} className="p-3 bg-gray-100 rounded-lg mb-2">
                      <span className="font-medium">{item.workflow}:</span>
                      <span className="text-gray-600 ml-2">{item.reason}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Roadmap Tab */}
          {activeTab === 'roadmap' && (
            <div className="space-y-6">
              <div className="bg-white p-6 rounded-xl shadow-sm border-l-4 border-green-500">
                <h3 className="font-semibold text-lg mb-2">📅 This Week</h3>
                <p className="text-gray-700">{dashboardData.nextSteps.thisWeek}</p>
              </div>
              <div className="bg-white p-6 rounded-xl shadow-sm border-l-4 border-blue-500">
                <h3 className="font-semibold text-lg mb-2">📅 This Month</h3>
                <p className="text-gray-700">{dashboardData.nextSteps.thisMonth}</p>
              </div>
              <div className="bg-white p-6 rounded-xl shadow-sm border-l-4 border-orange-500">
                <h3 className="font-semibold text-lg mb-2">📅 This Quarter</h3>
                <p className="text-gray-700">{dashboardData.nextSteps.thisQuarter}</p>
              </div>
            </div>
          )}

          <footer className="mt-12 pt-6 border-t border-gray-200 text-center text-gray-500 text-sm">
            Generated by Automation Discovery Interview • {new Date().toLocaleDateString()}
          </footer>
        </div>
      );
    }

    ReactDOM.createRoot(document.getElementById('root')).render(<App />);
  </script>
</body>
</html>
```

### Generating the Dashboard

1. Complete the interview and gather all data
2. Populate the `dashboardData` object with actual interview responses
3. Replace `DASHBOARD_DATA_HERE` in the template with the JSON (no quotes around it)
4. Save as `outputs/data/automation-dashboard-YYYY-MM-DD.html`
5. Tell user: "Your dashboard is ready. Open the file in any browser to view it."

---

## Output

- **Format:** Interactive HTML dashboard
- **Location:** `outputs/data/automation-dashboard-YYYY-MM-DD.html`

---

## ⚠️ AFTER EVERY RUN — Update Lessons (MANDATORY)

**Before presenting final results, update `.claude/skills/automation-discovery-interview/LESSONS.md`.**

### 1. Write a Run Log Entry

Add a new entry at the **TOP** of the Run Log section:

```
### Run: YYYY-MM-DD
**Goals:**
- [ ] Goal 1
- [ ] Goal 2

**Result:** ✅ Success / ⚠️ Partial / ❌ Failed

**What happened:**
- (What went according to plan)

**What didn't work:**
- (Any issues, with specifics)

**Is this a repeat error?** Yes/No — if yes, which one?

**Lesson learned:**
- (What to do differently next time)

**Tokens/cost:** ~XX K tokens
```

### 2. Update Issue Tracking

| Situation | Action |
|-----------|--------|
| New problem | Add to **Known Issues** |
| Known Issue happened again | Move to **Repeat Errors**, increment count, **tell the user** |
| Fixed a Known Issue | Move to **Resolved Issues** |

### 3. Tell the User

End your output with a **Lessons Update** note:
- What you logged
- Any repeat errors encountered
- Suggestions for skill improvement

**Do NOT skip this. The system only improves if every run is logged honestly.**

# Mode: Draft a Category Strategy Document

## Goal
Produce a complete, board-ready category strategy document for a specific category. This document defines what the organisation will do, why, how, and by when — and becomes the mandate for all sourcing activity in that category for the next 12–36 months.

A good category strategy is not a wish list. It is a defensible, evidence-based plan with specific actions, owners, timelines, and a quantified value case.

---

## Prerequisites

Before drafting, confirm:
- [ ] Kraljic segmentation is complete for this category (run `modes/segmentation-mode.md` first)
- [ ] Market intelligence brief is complete (run `modes/market-analysis-mode.md` first)
- [ ] Spend data is available (from `spend-analyzer` or user-provided)
- [ ] Key stakeholders have been identified (internal business owner, finance sponsor, operations lead)

If any prerequisite is missing, ask: "Shall I run the [segmentation / market analysis] first, or do you want to proceed with what we have and flag gaps?"

---

## Step 1 — Confirm the strategy parameters

Do not draft until you have confirmed:

- [ ] **Category scope** — exact definition of what is / is not in scope
- [ ] **Strategy horizon** — 12 months (tactical), 24 months (standard), or 36 months (transformational)
- [ ] **Stakeholders** — who owns this category commercially, who are the end users, who signs off
- [ ] **Current state** — incumbent suppliers, current contract status, known pain points
- [ ] **Constraints** — any suppliers that cannot be changed (embedded systems, regulatory, political), any budgets locked
- [ ] **Ambition level** — is the primary objective savings, risk reduction, quality improvement, innovation, or sustainability?

If the primary objective is unclear, ask: "What is the #1 outcome you need this strategy to deliver — cost reduction, supply security, quality improvement, or something else?"

---

## Step 2 — Define the strategic approach

Based on the Kraljic quadrant, select and confirm the primary strategic approach:

| Quadrant | Primary Strategic Approach | Typical Levers |
|---|---|---|
| **Strategic** | Supplier Partnership & Joint Value Improvement | Executive sponsorship, shared roadmaps, gain-share mechanisms, innovation pipeline |
| **Leverage** | Competitive Sourcing & Volume Consolidation | Competitive tender, consolidated volumes, payment terms optimisation, TCO challenge |
| **Bottleneck** | Supply Security & Risk Mitigation | Dual sourcing, buffer inventory, long-term supply agreements, qualification of alternatives |
| **Routine** | Process Efficiency & Demand Management | P-card / catalogue adoption, demand aggregation, guided buying, automated reorder |

Always explain to the user why this approach is recommended for their Kraljic position. Do not impose the approach — the user must agree with it.

**Cross-check: stakeholder alignment**
For each key stakeholder identified in Step 1, note: will this strategy require them to change their behaviour? If yes, flag the change management requirement in the strategy.

---

## Step 3 — Define the sourcing approach

Within the strategic approach, define the specific sourcing action:

| Sourcing Action | When to use |
|---|---|
| Competitive RFP | Leverage / large value, multiple viable suppliers, contract expiring |
| Direct negotiation | Strategic supplier, high switching cost, relationship critical |
| Framework / DPS call-off | Routine / Bottleneck, pre-qualified supplier pool exists |
| Re-negotiation of existing contract | Any quadrant, mid-contract but significant leverage event (e.g. volume growth, market price drop) |
| Demand management / specification review | Routine / Leverage, significant demand reduction opportunity exists |
| Do nothing | Only valid if contract is locked, switching cost exceeds savings, or market is unfavourable |

If recommending "do nothing", always document why and set a review trigger date.

---

## Step 4 — Build the savings / value case

For each identified lever, quantify the opportunity using `modes/opportunity-mode.md`. Minimum required for a strategy:

| Lever | Est. Annual Value | Confidence | Timeframe | Action Required |
|---|---|---|---|---|
| [e.g. Volume consolidation] | [Amount] | [High/Med/Low] | [Months] | [Specific action] |

**Total potential value:** [sum]

Caveats:
- All figures are estimates subject to market conditions and negotiation outcomes
- Confidence levels: High = evidence-based benchmark; Medium = comparable market data; Low = directional estimate

---

## Step 5 — Define the implementation roadmap

Break the strategy into three phases. Every action must have an owner role and a date:

**Phase 1 — Quick Wins (Months 1–3)**
Focus: Immediate actions with low effort, visible results, stakeholder credibility

| Action | Owner Role | Deadline | Expected Value |
|---|---|---|---|

**Phase 2 — Core Programme (Months 4–12)**
Focus: Main sourcing activity, competitive process or negotiation, contract execution

| Action | Owner Role | Deadline | Expected Value |
|---|---|---|---|

**Phase 3 — Sustain & Optimise (Months 13–24/36)**
Focus: Contract management, performance improvement, market monitoring

| Action | Owner Role | Deadline | Expected Value |
|---|---|---|---|

---

## Step 6 — Define KPIs and governance

Every strategy needs measurable success criteria. Propose KPIs based on the primary objective:

| Objective | Suggested KPIs |
|---|---|
| Cost reduction | % savings vs. baseline; TCO reduction; price per unit trend |
| Risk reduction | Supplier risk score (from scorecard); dual-source coverage %; contract coverage % |
| Quality improvement | Supplier defect rate; SLA achievement; customer complaint rate |
| Process efficiency | PO cycle time; catalogue adoption rate; tail spend % |

Propose a governance cadence:
- Monthly: Category performance review (operational)
- Quarterly: Stakeholder review (commercial progress vs. strategy)
- Annual: Strategy refresh (re-run Kraljic, update market data)

---

## Step 7 — Produce the strategy document

Populate `templates/category-strategy-template.md` with all findings. Use `lib/strategy_generator.py` to assemble and format the document.

Generate a `.docx` file using the `docx` skill.

Document naming convention:
```
[ORG_NAME]-Category-Strategy-[CATEGORY]-[YYYY].docx
```

Formatting:
- Section headers in navy (#1B3A6B)
- Kraljic matrix in a formatted table
- Implementation roadmap as a timeline table
- KPI dashboard section with target vs. baseline columns
- Footer: "Confidential — [ORG_NAME] Procurement | moleculeone.ai"

---

## Step 8 — Pre-flight review

Before finalising, confirm with the user:
1. The Kraljic classification is correct
2. The strategic approach is agreed
3. The savings / value case figures have been reviewed and are defensible (or data gaps are clearly marked)
4. All named stakeholders are correct
5. No confidential market data has been included that should not be in the document

Ask: "Any changes before I generate the final strategy document?"

---

## Step 9 — Log the event

Append to `${CLAUDE_PLUGIN_DATA}/category-strategy-history.log`:
```
DATE: [date]
MODE: Strategy Drafting
CATEGORY: [name]
QUADRANT: [Strategic / Leverage / Bottleneck / Routine]
SPEND: [user-provided amount, or DATA_REQUIRED]
STRATEGY: [one-line description of approach]
TARGET_SAVINGS: [data-backed amount or %, or DATA_REQUIRED]
HORIZON: [12 / 24 / 36 months]
STATUS: Draft issued
```

---

## Step 10 — Offer the interactive HTML dashboard (add-on)

After the Word document is ready, offer the user an optional interactive HTML dashboard:

> "Would you like an interactive HTML dashboard to accompany the strategy document? It includes:
> - A visual **Kraljic matrix** — a 2×2 grid with your categories plotted by spend impact and supply risk
> - An **opportunity waterfall chart** — showing value by lever from largest to smallest
> - A **phased implementation timeline** — colour-coded Gantt-style view of Phases 1–3
>
> It opens in a browser and is useful for presenting to stakeholders. Just say yes and I'll build it."

If the user says yes, generate a self-contained `.html` file using inline Chart.js (via cdnjs.cloudflare.com). The dashboard must:

- Use only data the user has provided — no fabricated figures in any chart
- Show `[DATA REQUIRED]` in chart tooltips or labels wherever spend or savings data is missing
- Include the Molekuleone.ai branding (navy #1B3A6B header, org name in the title)
- Be fully self-contained (single file, no external dependencies beyond the CDN scripts)

Name the file using the same convention as the Word document:
```
[ORG_NAME]-Category-Strategy-[CATEGORY]-[YYYY]-dashboard.html
```

If the user declines, proceed without the dashboard — it is strictly optional.

---

## What Good Looks Like

- Every section of `templates/category-strategy-template.md` is populated — no placeholder text (or [DATA REQUIRED] where data was not provided)
- The value case has specific lever estimates grounded in real data — not a single aggregate percentage or fabricated figure
- The implementation roadmap has named owner roles and dates — not "TBC"
- KPIs have baseline values (or a plan to establish baseline in Phase 1)
- The document can be presented to a CFO or CPO without further editing
- If the HTML dashboard was requested, all charts reflect only user-provided data

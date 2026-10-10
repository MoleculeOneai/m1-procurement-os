# Mode: Scorecard Design

## Goal
Design a complete, defensible supplier scorecard for a specific category or supplier type. The output is a criterion set with weights, scoring anchors (what 1/3/5 looks like), identified data sources, and a review cadence — ready to use in a live scoring session.

---

## Step 1 — Establish context

Before designing, confirm:
- [ ] **Supplier category** — what type of supplier is this scorecard for? (logistics, IT services, facilities, raw materials, professional services, etc.)
- [ ] **Supplier tier** — Strategic, Leverage, Bottleneck, or Routine (from `category-strategy-builder`)
- [ ] **Primary objective** — is the primary goal cost management, quality assurance, risk reduction, service improvement, or innovation?
- [ ] **Review frequency** — how often will this scorecard be run? (Monthly / Quarterly / Bi-annual / Annual)
- [ ] **Data availability** — what operational data is actually accessible? (ERP, helpdesk tickets, delivery records, invoice data, survey responses)
- [ ] **Stakeholders who will score** — who provides input? (procurement only, or cross-functional: operations, IT, finance, end users?)

If the user hasn't shared the Kraljic quadrant for this supplier, ask — it materially affects which dimensions to weight most heavily.

---

## Step 2 — Select the dimension set

Use the category type and Kraljic tier to propose the right 6–10 dimensions from the standard library below. Present as a proposed list and ask for confirmation before adding weights.

### Standard Dimension Library

**Commercial Performance**
- Price Competitiveness — Are prices tracking against market benchmarks and contractual commitments?
- Invoice Accuracy — What % of invoices are correct on first submission?
- Payment Terms Compliance — Is the supplier honouring agreed payment terms?
- Contract Compliance (commercial) — Are all commercial terms being adhered to?

**Quality & Delivery**
- On-Time In-Full (OTIF) — What % of orders/deliveries arrive on time and complete?
- Defect / Error Rate — What % of delivered goods/services require rework, return, or correction?
- SLA Achievement — What % of defined SLAs are met in the period?
- Quality Consistency — Are quality levels consistent, or are there periodic drops?

**Relationship & Responsiveness**
- Responsiveness — How quickly does the supplier respond to queries, issues, and escalations?
- Proactive Communication — Does the supplier flag issues early, or do problems have to be chased?
- Account Management Quality — Is the supplier relationship well-managed at the right seniority level?
- Escalation Resolution — When issues are escalated, are they resolved effectively and within SLA?

**Risk & Compliance**
- Financial Stability — Are there any signs of financial distress? (credit risk, late payments to sub-suppliers)
- Regulatory Compliance — Are all required certifications and regulatory obligations current?
- Data Security / Cyber Risk — Does the supplier meet your data handling and cyber security requirements?
- ESG / Sustainability — Are they meeting any contractual ESG commitments?
- Business Continuity — Do they have tested continuity plans?

**Innovation & Development**
- Innovation Contribution — Has the supplier proactively brought cost reduction, process improvement, or new capability ideas?
- Technology Currency — Is the supplier investing in their technology and capabilities?
- Talent & Capacity — Do they have sufficient skilled resource to scale with your needs?

---

## Step 3 — Assign weights

Weights must sum to 100%. Use the Kraljic tier as the primary guide:

| Tier | Suggested dimension emphasis |
|---|---|
| **Strategic** | Relationship (25%) / Innovation (20%) / Quality & Delivery (20%) / Risk (20%) / Commercial (15%) |
| **Leverage** | Commercial (35%) / Quality & Delivery (30%) / Compliance (20%) / Relationship (15%) |
| **Bottleneck** | Risk & Compliance (35%) / Quality & Delivery (30%) / Relationship (20%) / Commercial (15%) |
| **Routine** | Commercial (40%) / Quality & Delivery (35%) / Compliance (15%) / Responsiveness (10%) |

Present the proposed weights. Ask: "Do these weights reflect what matters most for this supplier relationship? Any you'd shift?"

**Hard rule:** No single dimension should exceed 40% of total weight. If the user proposes this, challenge it — a scorecard dominated by one dimension is fragile.

---

## Step 4 — Define scoring anchors

For each criterion, define what 1, 3, and 5 look like. **This is the most important step** — without anchors, scores mean whatever the reviewer decides.

Present anchors in this format for each dimension:

| Score | Definition |
|---|---|
| 5 — Excellent | [Specific, measurable description] |
| 3 — Acceptable | [Specific, measurable description] |
| 1 — Unacceptable | [Specific, measurable description] |

Example for OTIF:
| Score | Definition |
|---|---|
| 5 | ≥98% OTIF for the period |
| 3 | 90–97% OTIF |
| 1 | <85% OTIF |

If metric data isn't available for a dimension (e.g. "Innovation"), define behavioural anchors:
| Score | Definition |
|---|---|
| 5 | Proactively brought ≥2 documented improvement ideas in the period; at least 1 actioned |
| 3 | Responded positively to innovation requests but no proactive suggestions |
| 1 | No innovation engagement; resistant to change |

---

## Step 5 — Identify data sources

For each criterion, document:
- **Data source** — where does the number come from? (ERP, helpdesk system, delivery tracking, invoice system, stakeholder survey, manual tracker)
- **Data owner** — who is responsible for providing this data for each review cycle?
- **Availability** — is the data available right now, or does collection need to be set up?

Flag any criterion where the data source is "survey" or "manual" — these are the highest failure points. Ask: "Is there a structured way to collect this, or will it rely on someone's memory?"

---

## Step 6 — Set the review cadence and governance

Define:
- **Review frequency** — confirmed from Step 1
- **Who scores** — named roles (not individuals, for longevity)
- **Who approves** — who reviews the completed scorecard before it is shared with the supplier?
- **Who presents to supplier** — the scorecard owner; should be the category manager or relationship lead
- **Supplier input** — will the supplier provide their own data as input? (recommended for Strategic suppliers)

---

## Step 7 — Save and version the scorecard design

Save the completed criterion set to `${CLAUDE_PLUGIN_DATA}/scorecards/[CATEGORY]-scorecard-v1.0.md` using `lib/scorecard_builder.py`.

Naming: `[CATEGORY]-scorecard-v[N.N].md`
Increment the version whenever criteria, weights, or anchors are changed.

Append to `${CLAUDE_PLUGIN_DATA}/scorecard-history.log`:
```
DATE: [date]
EVENT: Scorecard design
CATEGORY: [category]
VERSION: [version]
DIMENSIONS: [n]
REVIEW_FREQUENCY: [frequency]
```

---

## What Good Looks Like

- 6–10 dimensions — not 3 (too narrow) and not 15 (impossible to run consistently)
- Every dimension has explicit scoring anchors — no dimension scored on "gut feel"
- Every dimension has a named data source and data owner
- Weights reflect actual business priorities, not political compromise or lazy equal-weighting
- The scorecard has been confirmed by at least one stakeholder before first use

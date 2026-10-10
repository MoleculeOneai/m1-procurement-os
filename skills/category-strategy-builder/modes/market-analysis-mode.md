# Mode: Supply Market Analysis

## Goal
Build a structured intelligence brief on the supply market for a specific category. The output is a supplier landscape, market structure assessment, price driver analysis, and supply risk profile — the factual foundation that every category strategy must rest on.

---

## Step 1 — Confirm the category scope

Before starting, confirm:
- [ ] **Category name** — at the right level of granularity (e.g. "Cloud Infrastructure" not "IT" — not "AWS EC2 On-Demand Compute in us-east-1")
- [ ] **Geographic scope** — global sourcing possible, or limited to specific regions/countries?
- [ ] **Approximate annual spend** — used to assess which suppliers are viable at your volume
- [ ] **Key specification constraints** — certifications required, quality standards, regulatory requirements that limit the supplier universe

If the category is too broad (e.g. "IT"), ask the user to narrow it: "Shall I focus on IT Hardware, IT Software, Cloud Services, or IT Professional Services?"

---

## Step 2 — Identify the supplier landscape

Research and document the supply market. Use web search where needed. Cover:

**Market structure:**
- Estimated number of viable global suppliers
- Number of viable suppliers in the user's geography (based on confirmed geographic scope)
- Market concentration: HHI or informal assessment (Highly concentrated / Moderately concentrated / Fragmented)
- Whether the market is dominated by large global players, regional specialists, or SMEs
- Key market dynamics: consolidation, new entrants, exits, M&A activity in the last 24 months

**Named suppliers (top 6–10):**
For each viable supplier, compile:
| Supplier | HQ | Revenue (approx.) | Ownership | Key Strengths | Key Weaknesses | Notes |
|---|---|---|---|---|---|---|

If financial data for private companies is unavailable, state this clearly — do not estimate or invent revenue figures.

**Incumbent supplier position:**
If the user has an incumbent, assess:
- How entrenched is the incumbent? (switching cost, integration depth, data migration complexity)
- Are there known performance issues? (ask the user)
- When does the current contract expire?

---

## Step 3 — Analyse price drivers and benchmarks

Identify the 3–5 primary cost drivers for this category. Examples:

| Category type | Common price drivers |
|---|---|
| IT Hardware | Semiconductor prices, logistics costs, currency (USD/JPY/TWD), demand cycles |
| Logistics | Fuel costs, driver availability, equipment utilisation rates, route density |
| Professional Services | Labour market tightness, specialist skill scarcity, utilisation rates, offshore vs onshore mix |
| Raw Materials | Commodity index prices, energy costs, exchange rates, seasonal demand |
| SaaS / Software | Seat volume, contract length, competitor pricing pressure, vendor growth targets |

Present benchmark pricing ranges if obtainable. Always date-stamp and source any benchmark figures. Never present a single price point without a range and confidence level.

**Key questions for the user:**
> "When did you last benchmark your pricing for this category? Do you have any external benchmark data we should incorporate?"

---

## Step 4 — Assess supply risk

Score and explain each risk dimension:

| Risk Dimension | Score (1–5) | Evidence / Rationale |
|---|---|---|
| Supplier concentration | | |
| Switching cost & lock-in | | |
| Lead time & fulfilment reliability | | |
| Geopolitical / country risk | | |
| Financial stability of key suppliers | | |
| Technology / obsolescence risk | | |
| Regulatory / compliance risk | | |
| ESG / reputational risk | | |

**Overall supply risk rating:** Low / Medium / High / Critical

Flag any risk dimension scoring 4 or 5 as requiring a specific mitigation action in the strategy.

---

## Step 5 — Identify market opportunities

Based on the market analysis, identify 3–5 opportunities for the buyer. Examples:
- Volume consolidation potential (are you splitting spend across too many suppliers?)
- New entrant advantage (is there a challenger supplier offering better value?)
- Specification challenge (is the current spec over-engineered for the actual need?)
- Geographic expansion (is sourcing from a different market feasible and cheaper?)
- Commercial model innovation (could a subscription model replace CAPEX spend?)

---

## Step 6 — Produce the Market Intelligence Brief

Populate `templates/market-intelligence-brief.md` with all findings.

Save to `${CLAUDE_PLUGIN_DATA}/category-strategy/[CATEGORY]-market-brief.md`.

Append to `${CLAUDE_PLUGIN_DATA}/category-strategy-history.log`:
```
DATE: [date]
MODE: Market Analysis
CATEGORY: [name]
MARKET_STRUCTURE: [Concentrated / Fragmented]
SUPPLY_RISK: [Low / Medium / High / Critical]
VIABLE_SUPPLIERS: [n]
TOP_OPPORTUNITY: [one-line]
```

---

## What Good Looks Like

- Every supplier in the landscape table has a named entry — no "various others" rows
- Price drivers are specific to the category — not generic procurement boilerplate
- All benchmarks are dated and sourced
- At least one supply risk dimension is scored ≥4 (if none are, the analysis is probably too shallow)
- The brief ends with a clear "So what?" — actionable opportunities, not just a description of the market

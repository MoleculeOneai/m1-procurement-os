# Mode: Supplier Risk Assessment and Concentration

## Goal
Identify, score and plan mitigation for supplier risks, for one supplier, a category, or the whole base.

## Risk Categories
- **Financial:** insolvency, liquidity stress, price increases, currency exposure
- **Operational:** capacity, quality, delivery failure, key-person dependency
- **Supply and concentration:** single-source, sole-region, thin market, long switch time
- **Security and data:** breach, weak access control, fourth-party exposure
- **Compliance and legal:** sanctions, anti-bribery, regulatory breach, contract gaps
- **ESG and reputational:** labour, environment, adverse publicity (detail in `esg-sustainability-assessor`)
- **Geopolitical and logistics:** conflict, trade restriction, port or route disruption
- **Strategic:** acquisition, change of control, roadmap divergence, technology obsolescence

## Scoring
**Severity (1–5)** — impact if it happens: 1 Negligible, 2 Low, 3 Moderate, 4 High, 5 Critical. Anchor it to the user's own context (share of revenue, days of production, regulatory exposure). If the user gives no thresholds, use the bands below and label them as default assumptions.

| Level | Default anchor |
|---|---|
| 1 | Absorbed in normal operations |
| 2 | Minor cost or delay, no customer impact |
| 3 | Material cost or noticeable disruption |
| 4 | Significant disruption, customer or regulatory attention |
| 5 | Business-critical outage or major regulatory action |

**Likelihood (1–5)** — 1 Remote, 2 Unlikely, 3 Possible, 4 Likely, 5 Almost certain.

**Score = Severity × Likelihood.** 1–4 Low, 5–9 Medium, 10–15 High, 16–25 Critical.

## Step-by-Step

**Step 1 — Scope.** One supplier, a category, or the supplier base. Ask for the data available: spend, criticality, alternatives, contract status, performance history.

**Step 2 — Identify risks.** Work through each category. Only record risks supported by evidence or a clear, stated assumption.

**Step 3 — Score** each risk for severity and likelihood. Show the reasoning in one line.

**Step 4 — Test concentration** (when a supplier list with spend is supplied):
- Top 10 suppliers' share of total spend and of category spend
- Categories with a single supplier or one dominant supplier (state your threshold, default over 60%)
- Single-region or single-site dependence
- Critical items with no qualified alternative
- Time and cost to switch, where known

**Step 5 — Plan mitigations.** For every High or Critical risk: a specific action (dual-source, buffer stock, step-in rights, financial monitoring, escrow, continuity plan, contract change), an owner, a date, and the target score after mitigation.

**Step 6 — Produce the register.**

| ID | Supplier | Category | Description | Severity | Likelihood | Score / Level | Mitigation | Owner | Due | Status |
|---|---|---|---|---|---|---|---|---|---|---|

Status: Open / Mitigating / Accepted / Closed. Follow with a one-page summary: top five risks, concentration findings, and decisions needed from leadership.

## Output Rules
- A risk with no evidence is a hypothesis. Mark it as such.
- Never assign a financial-health rating from memory about a named company. Use only supplied data and tell the user what to obtain.
- Accepted risks need a named owner and a review date.

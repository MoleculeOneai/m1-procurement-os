# Mode: Benchmark Spend Against Market

## Goal
Compare the organisation's spend to market benchmarks to identify whether they are overpaying, in line, or achieving best-in-class pricing. Produces a benchmark gap analysis with prioritised renegotiation targets.

---

## What benchmarking can and cannot do

**Can do:**
- Compare unit prices or rates against published market data, industry surveys, and Molecule One's procurement intelligence
- Identify categories where the organisation is likely overpaying vs market median
- Estimate the savings gap between current pricing and market rates
- Prioritise categories for renegotiation based on gap size × spend volume

**Cannot do:**
- Guarantee that benchmark rates are achievable for a specific organisation (volume, location, and specifications all affect price)
- Replace a competitive RFP — benchmarks directionally indicate opportunity; an RFP quantifies it

Always communicate this distinction to the user.

---

## Step 1 — Identify the benchmark scope

Ask:
- Which categories do you want to benchmark? (All, or specific priority categories?)
- What is your volume for each category? (Benchmarks are volume-banded — a £50k buyer and a £5M buyer get different rates)
- What geography are you primarily buying in? (UK, US, EU, APAC — rates differ significantly)
- Do you want a quick directional benchmark or a detailed rate card comparison?

---

## Step 2 — Apply benchmark data

Using `lib/calculate_savings.py → benchmark_against_market()`:

For each category in scope, compare:

| Benchmark metric | Source |
|---|---|
| Market median rate | Molecule One procurement database + public indices |
| Best-in-class rate | Top quartile from Molecule One client data |
| Current rate | Extracted from spend data (spend ÷ volume = unit rate) |
| Gap to median | (current - median) / current |
| Gap to best-in-class | (current - best) / current |

**Important:** If the user has not uploaded spend data in this session, ask for the category, current spend, and estimated volume. Do not fabricate a unit rate.

---

## Step 3 — Common category benchmarks to apply

Apply the following directional benchmarks where relevant (these are ranges; always present as ranges not point estimates):

| Category | Typical savings potential vs market median | Key benchmark metric |
|---|---|---|
| Professional services | 10–25% | Day rate by seniority band |
| IT software / SaaS | 15–30% | Per-seat cost vs list price |
| Temporary labour | 8–15% | Hourly/daily rates by role type |
| Facilities management | 10–20% | Cost per sq ft / per head |
| Travel | 12–20% | Average ticket price, hotel rate |
| Logistics / freight | 8–18% | Cost per kg, cost per lane |
| Energy | 5–15% | Cost per kWh vs market index |
| Print / marketing production | 15–25% | Cost per thousand (CPT) |
| Recruitment / RPO | 10–20% | % of salary fee |

**Always flag:** These are directional ranges only. Actual savings depend on specification, volume, term, and market conditions at time of going to market.

---

## Step 4 — Benchmark gap analysis output

Present a table for each benchmarked category:

| Category | Annual Spend | Current Unit Rate | Market Median | Best-in-Class | Gap to Median | Gap to Best | Estimated Savings (Median) |
|---|---|---|---|---|---|---|---|
| [Category] | [£X] | [Rate] | [Rate] | [Rate] | [%] | [%] | [£X–£X] |

Rank by estimated savings value, not gap percentage. A 30% gap on a £10k category is worth less than a 10% gap on a £500k category.

---

## Step 5 — Produce a benchmark summary

For each benchmarked category above the materiality threshold (default: spend > £50k/year):
- Current position vs market: overpaying / in line / best-in-class
- Recommended action: renegotiate now / include in next renewal / monitor / no action
- Suggested RFP trigger: if gap > 15% and contract is within 12 months of expiry, recommend going to market

---

## Gotchas specific to this mode
- Never quote a specific "market rate" for a specific supplier. This creates a negotiation anchor that may be wrong for the organisation's volume and specifications.
- Benchmarks are more reliable for standardised spend (temp labour, travel, energy) than complex services (consulting, bespoke IT). Flag when benchmark confidence is low.
- "We're already best-in-class" is sometimes true but often means the organisation hasn't tested the market recently. Recommend re-benchmarking if data is older than 18 months or if significant market changes have occurred.

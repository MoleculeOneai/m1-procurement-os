# Mode: Savings & Opportunity Analysis

## Goal
Identify, quantify, and prioritise value improvement opportunities for a specific category or for the full spend portfolio. The output is a structured opportunity register with estimates, confidence levels, required actions, and a ranked implementation sequence.

This is not a savings target exercise. Every opportunity must be grounded in a specific lever with a specific mechanism. "10% savings" is not an opportunity — "consolidating spend to 2 suppliers to achieve volume discount" is.

---

## ⚠️ Data Gate — Check Before Proceeding

Before running Steps 2–5, confirm whether real spend data was provided in the Pre-Run Intake.

**If real spend data was provided:**
Proceed normally. Use the actual spend figures to compute opportunity values in Step 2.

**If no real spend data was provided:**
- Complete Step 1 (lever applicability) in full — this is qualitative and does not require data.
- In Steps 2–5, leave all currency cells as `[DATA REQUIRED — provide annual spend to calculate]`.
- Show the industry benchmark % ranges from the Lever Library clearly labelled as external benchmarks (see label instructions below).
- Do not invent or estimate a spend figure to make the maths work. Not even "for illustration". The user will insert their real numbers.
- Tell the user: *"I've identified the applicable levers below. To calculate actual savings estimates, I'll need your annual spend for this category. Once you provide that, I can populate the values."*

---

## Lever Library

Use this library to identify relevant opportunities. Apply only levers that are genuinely applicable — do not include every lever as a checkbox exercise.

The % ranges in this library are **external industry benchmarks** — they represent what organisations in comparable situations have achieved. They are **not** an estimate of what your organisation will save. Treat them as directional context only, and always label them as such when presenting to the user.

### Commercial Levers

| Lever | When applicable | External Benchmark Range ⚠️ |
|---|---|---|
| Competitive re-tender | Contract expiring, Leverage quadrant, >2 viable suppliers | 5–20% price reduction |
| Volume consolidation | Spend split across 3+ suppliers for same category | 5–15% through increased volume to fewer suppliers |
| Demand aggregation | Multiple business units buying independently | 3–10% by combining volumes |
| Payment terms extension | Suppliers with strong balance sheets, buyer has cash need | 0.5–2% of spend value per 30 days extended |
| Early payment discount | Supplier cash flow need, buyer has surplus liquidity | 1–3% discount for early payment |
| Total Cost of Ownership (TCO) challenge | Focus has been on unit price only | 5–20% reduction by including freight, installation, warranty, disposal |
| Pricing model change | Fixed price where market prices are falling; or T&M where fixed is feasible | Varies — must model both scenarios with real data |
| Currency hedging / FX clause | Category with significant cross-border procurement | Risk reduction value, not always cash savings |

### Specification & Demand Levers

| Lever | When applicable | External Benchmark Range ⚠️ |
|---|---|---|
| Specification right-sizing | Over-specified products / services vs. actual need | 5–25% — specification gold-plating is common |
| Demand reduction / challenge | Is all the demand justified? Could some be eliminated? | 3–15% of volume |
| Standardisation | Multiple variants bought; consolidation possible | 5–20% through reduced complexity |
| Catalogue / guided buying | Tail spend, Routine quadrant | 10–30% off-contract spend brought on-contract |
| Insource vs. outsource review | Currently outsourced; internal capacity exists | Depends entirely on org — must model with real data |
| Make vs. buy review | Currently made internally; market alternative cheaper | Depends entirely on org — must model with real data |

### Supply Base Levers

| Lever | When applicable | External Benchmark Range ⚠️ |
|---|---|---|
| Supplier rationalisation | Too many suppliers, fragmented spend | 5–15% through volume concentration |
| New entrant introduction | Market has new/challenger suppliers | 5–15% competitive pressure on incumbent |
| Dual sourcing (Bottleneck) | Single source supply risk | Risk value — cost may increase slightly |
| Geographic diversification | Single-country supply risk | Risk value — cost may be neutral or increase |
| Supplier development | Strategic supplier underperforming | Operational improvement value, indirect savings |

### Process & Compliance Levers

| Lever | When applicable | External Benchmark Range ⚠️ |
|---|---|---|
| Maverick spend reduction | Spend outside contract (off-contract buying) | Recover 5–15% of off-contract spend |
| Contract compliance audit | Supplier billing vs. contract terms | 1–5% recoveries from overbilling |
| Auto-renewal prevention | Contracts renewing without review | Preserve negotiating leverage |
| Invoice accuracy improvement | High invoice error rate | Reduce cost of processing and disputed invoices |

> ⚠️ **Benchmark label**: When presenting any % from this library to the user, always display it with the label: *"External industry benchmark — not your data."* Never convert a benchmark % into a dollar figure unless using the user's actual spend.

---

## Step 1 — Assess applicable levers

For each lever in the library, score applicability (1–3) for this category:
- 3 — Clearly applicable, evidence exists
- 2 — Potentially applicable, needs validation
- 1 — Not applicable for this category

Present only levers scoring 2 or 3. Do not include every lever in the register.

This step can be completed with or without spend data — it is qualitative.

---

## Step 2 — Quantify each opportunity

**Only proceed with quantification if real spend data was provided.** If not, mark all currency fields `[DATA REQUIRED]` and skip to Step 3.

For each applicable lever, compute:

**Formula for savings estimate:**
```
Estimated savings = User's actual annual spend in scope × Savings % estimate
```

The savings % estimate must be grounded in at least one of:
- The user's own historical data
- An external benchmark explicitly disclosed as such
- A specific commercial mechanism with a named counterparty

Always provide a range, not a point estimate:
- Conservative: lower end of the applicable range
- Central: midpoint based on market analysis and user context
- Optimistic: upper end assuming favourable conditions

**Confidence levels:**
- High: grounded in external benchmark data or prior run of this lever in this category
- Medium: directional estimate based on comparable categories or market data
- Low: rough order of magnitude — needs validation before committing

---

## Step 3 — Build the Opportunity Register

Populate `templates/opportunity-register.md`. One row per lever:

| # | Lever | Spend in Scope | Conservative | Central | Optimistic | Benchmark Range ⚠️ | Confidence | Effort (H/M/L) | Timeframe | Owner Role | Dependencies |
|---|---|---|---|---|---|---|---|---|---|---|---|

If no spend data: fill currency columns with `[DATA REQUIRED]`. Fill the Benchmark Range column from the Lever Library, labelled as external benchmarks.

Sort by: Confidence × Central Value × (1 / Effort) — highest priority first.

**Prioritisation guidance:**
- Quick wins: High confidence + Low effort + Months 1–6
- Core programme: Medium/High confidence + Medium effort + Months 3–12
- Stretch targets: Low confidence + High effort + Months 12+

---

## Step 4 — Identify inter-dependencies and conflicts

Not all levers can be pursued simultaneously. Flag conflicts:
- Volume consolidation AND dual sourcing cannot both maximise impact on the same category
- Competitive tender AND direct negotiation are mutually exclusive for the same contract event
- Demand reduction must be agreed with the business owner before any sourcing action begins

---

## Step 5 — Summarise the value case

**If spend data was provided**, present the full summary:

> **Category: [name]**
> Total spend in scope: [user-provided amount]
> Number of opportunities identified: [n]
>
> | Horizon | Conservative | Central | Optimistic |
> |---|---|---|---|
> | Year 1 (quick wins only) | | | |
> | Year 1–2 (full programme) | | | |
> | Year 1–3 (full strategy period) | | | |
>
> **Top 3 priority actions:**
> 1. [lever] — [central estimate] — [confidence] — [timeframe]
> 2. [lever] — [central estimate] — [confidence] — [timeframe]
> 3. [lever] — [central estimate] — [confidence] — [timeframe]
>
> **Key caveats:** [list any material assumptions or constraints on the above]

**If no spend data was provided**, present the lever summary only:

> **Category: [name]**
> Spend in scope: [DATA REQUIRED]
> Opportunities identified: [n] applicable levers
>
> | Lever | Priority | External Benchmark ⚠️ | Effort | Timeframe |
> |---|---|---|---|---|
>
> *To calculate actual savings values, provide your annual spend for this category.*

Always include: *"All estimates are potential savings subject to market conditions, negotiation outcomes, and demand assumptions. They do not constitute committed targets. Industry benchmark ranges are sourced from external data and are not specific to your organisation."*

---

## Step 6 — Save and log

Save the completed opportunity register to `${CLAUDE_PLUGIN_DATA}/category-strategy/[CATEGORY]-opportunity-register.md`.

Append to `${CLAUDE_PLUGIN_DATA}/category-strategy-history.log`:
```
DATE: [date]
MODE: Opportunity Analysis
CATEGORY: [name]
SPEND_IN_SCOPE: [user-provided amount, or DATA_REQUIRED]
LEVERS_IDENTIFIED: [n]
CENTRAL_YEAR1_VALUE: [calculated amount, or DATA_REQUIRED]
CENTRAL_FULL_PERIOD_VALUE: [calculated amount, or DATA_REQUIRED]
TOP_LEVER: [name]
```

---

## What Good Looks Like

- Every opportunity has a specific lever, not just a savings percentage
- All benchmark % ranges are clearly labelled as external industry data — not the user's savings
- No dollar figures appear unless computed from real user-provided spend
- All estimates have confidence levels and ranges — no single-point estimates presented as commitments
- The register is sorted by priority, not by order of thinking
- Conflicts and dependencies between levers are called out
- The summary can be presented to a CFO in 2 minutes

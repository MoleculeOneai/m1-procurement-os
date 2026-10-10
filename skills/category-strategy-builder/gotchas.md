# Gotchas — Category Strategy Builder

Add a line each time Claude trips on something new. This file is the highest-signal content in this skill.

---

## ⚠️ CARDINAL RULE — Read This First, Every Time

**Never generate dollar figures, spend amounts, savings estimates, or any spend-based numbers unless the user has provided real data.**

This is not a style preference — it is the non-negotiable foundation of this skill. Fabricated or "illustrative" numbers in a procurement strategy document will be used to make real decisions. They cause real harm.

Specifically:
- Do not invent a spend figure, even as a placeholder or example
- Do not compute a savings amount from a made-up spend base
- Do not present industry benchmark percentages as if they are the user's actual savings
- Do not fill in a table cell with an estimated dollar value when no data was provided

If data is missing, mark the cell `[DATA REQUIRED]` and tell the user what data would be needed to complete it. Industry benchmark % ranges (e.g. "5–15% for volume consolidation") may be shown only when explicitly labelled as **external industry benchmarks — not your data**.

There are no exceptions to this rule. Not for demos, not for examples, not because the user seems to want a number.

---

## Segmentation & Kraljic Gotchas

- **Never place a category on the Kraljic matrix without data.** If you don't have spend volume AND supply risk data, you have half the picture. A high-spend category with easy substitution is not "Strategic" — it's "Leverage". Always assess BOTH axes before placing.
- **Spend data alone is not a category strategy.** Knowing you spend $2M on IT Hardware tells you the size of the prize, not the approach. Always layer in supply market analysis before recommending a strategy.
- **"Strategic" is the most overused quadrant.** Procurement teams routinely classify too many categories as Strategic because it feels important. Challenge any classification of more than 10–15% of categories as Strategic — true Strategic categories require dedicated relationship management that teams rarely have capacity for.
- **Spend concentration ≠ supply risk.** A category where you spend 80% with one supplier may have low supply risk if that supplier is easily replaceable. Never conflate spend concentration with criticality without assessing the actual market.
- **Categories shift quadrants over time.** A category that was Bottleneck (single source, low spend) can become Leverage if new suppliers enter the market. Always note when a Kraljic classification is time-sensitive and flag for review.
- **Tail spend should not get category strategy treatment.** Categories under 0.5% of total spend rarely justify a full strategy. Recommend consolidation or p-card/catalogue management rather than a dedicated strategy.

---

## Market Analysis Gotchas

- **Supply market analysis from the internet has a freshness problem.** Pricing benchmarks, supplier counts, and concentration ratios change. Always date-stamp market data and flag anything older than 12 months as potentially stale.
- **Market share data for private companies is unreliable.** Many supplier markets are fragmented with private companies — do not present market share figures as precise. Use ranges and flag the source.
- **"Global" and "local" markets behave differently.** A category that has 50 global suppliers may have only 2 viable local suppliers. Always specify the geographic scope of the market analysis. Never present global supplier counts as if they were locally accessible.
- **Supplier financial health must be checked.** A category strategy that relies on a single supplier without checking their credit rating, revenue trends, and ownership structure is incomplete. Flag this if no financial data is available.
- **Do not confuse the number of suppliers with the number of qualified suppliers.** The fact that 100 companies exist in a category does not mean 100 can meet your spec, volume, quality, and compliance requirements. Ask the user for qualification criteria before assessing market depth.

---

## Strategy Drafting Gotchas

- **Every strategy needs a "do nothing" baseline.** Before recommending a sourcing approach, state what happens if the organization takes no action. This anchors the value of the strategy and sets up the savings case.
- **Strategies that require headcount rarely get approved.** If your recommended strategy requires hiring a category manager, running a competitive tender, and re-negotiating contracts simultaneously — it will stall. Always include a phased implementation with quick wins in months 1–3.
- **Single-sourcing strategies need a documented risk mitigation plan.** Any recommendation to consolidate to one supplier must include what happens if that supplier fails. Without a mitigation plan, the strategy is incomplete.
- **Target savings percentages must be grounded.** "10–15% savings" is not a savings target — it's a guess. Always anchor savings targets to specific levers: demand reduction, commercial re-negotiation, specification change, supplier consolidation, payment terms. Each lever should have its own estimate — and every estimate must come from real user data, not assumptions.
- **Internal stakeholder alignment is a deliverable, not an assumption.** Category strategies that skip a stakeholder map fail at implementation. Always include a stakeholder analysis section — who needs to approve, who influences, who will resist, and why.
- **Never recommend a competitive tender for a Strategic supplier relationship.** Running a full tender on a deeply embedded Strategic supplier signals that you are willing to switch — this damages the relationship and rarely results in savings. Recommend collaborative value improvement instead.

---

## Data & File Gotchas

- **Spend-analyzer output files may have category names that don't match common taxonomy.** Before running Kraljic analysis, normalise category names against the user's taxonomy (or UNSPSC) so like-for-like comparison is possible.
- **Excel spend data often has allocation errors.** IT Software spend routinely ends up under Professional Services due to PO coding errors. Always ask the user: "Has this spend been reviewed for miscoding?" before building strategies on raw GL data.
- **Never present a savings figure as committed.** All savings estimates are "potential savings subject to market conditions and commercial negotiation." Always include this caveat.
- **Strategies built on a single year of spend data can be misleading.** One-year snapshots miss seasonality, project-based spend, and buying pattern anomalies. Always ask if multi-year data is available.

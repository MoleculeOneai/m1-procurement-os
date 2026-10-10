# Mode: Scope 3 Spend-Based Screening

## Goal
Produce a screening-level estimate of emissions from purchased goods and services and find the categories and suppliers worth deeper data collection.

This is an estimate for prioritisation. It is not a reportable inventory.

## Step-by-Step

**Step 1 — Establish method and factors.** Ask which emission factors to use. Acceptable inputs:
1. Supplier-specific data supplied by suppliers (best)
2. Activity data such as tonnes, kWh or kilometres with the user's factors
3. Spend-based factors (emissions per currency unit by category) from a database the user names and provides

**Do not supply emission factors from memory.** If the user has none, stop at a hotspot ranking by spend and the category's typical emissions intensity described qualitatively (high, medium, low), and explain what factor source they need. Record the factor source, version, year and currency basis for every figure.

**Step 2 — Prepare the spend data.** Use `spend-analyzer` output or a file the user provides. Check categorisation, currency (convert to the factor basis and state the rate), and year. Exclude non-emitting items (tax, interest, intercompany) and list the exclusions. Flag the CapEx and OpEx split, since capital goods are a separate reporting category.

**Step 3 — Map spend to factor categories.** Map each category to the closest factor. Show the mapping table and mark low-confidence matches. Services categories often map poorly. Say so.

**Step 4 — Calculate.** Emissions = spend × factor for each line, summed by category and supplier. Show units and the formula. Report totals as ranges or with a stated uncertainty band when the user's method defines one. Otherwise label as "indicative".

**Step 5 — Find hotspots.** Rank categories and suppliers by estimated emissions. Compare with spend share: categories whose emissions share exceeds their spend share are carbon-intensive. Identify the top suppliers worth asking for primary data (typically a small group covers most of the estimate).

**Step 6 — Recommend actions.** Primary-data requests for hotspot suppliers, specification or demand changes, low-carbon alternatives in sourcing events, and supplier target-setting. Do not state reduction percentages unless backed by supplied data.

**Step 7 — Output.** Method note and factor sources, exclusions, category table, supplier hotspot list, data-quality rating per line (primary, activity-based, spend-based), and the next-step plan.

## Output Rules
- Every number carries its factor source and year.
- Never present a spend-based estimate as precise. Keep the "screening estimate" label in the title.
- If the user needs a figure for external reporting, say it must be produced and assured under their reporting method, with Sustainability and Finance.

# Gotchas — Spend Intelligence Analyzer

Add a line each time Claude trips on something new. This file is the highest-signal content in this skill.

---

## Data Quality Gotchas

- **Never assume the data is clean.** Spend exports almost always contain duplicates, split supplier names (e.g. "Microsoft", "Microsoft Ltd", "MSFT", "Microsoft Corp"), inconsistent currencies, and missing fields. Always run `parse_spend_data.py → audit_data_quality()` first and surface the quality score before any analysis.
- **Supplier name deduplication is the single most important step.** Spend with the same supplier under different names inflates the supplier count, hides true concentration, and makes consolidation opportunities invisible. Never skip this step.
- **Inter-company transactions will distort the analysis.** If the organisation has multiple entities, spend between them appears as supplier spend. Ask the user if inter-company transactions should be excluded before proceeding.
- **P-card and corporate card data is the messiest.** Merchant category codes (MCCs) are unreliable for procurement categorisation. Treat card data as requiring manual review unless the description field is detailed.
- **One-off capital expenditure items distort recurring spend analysis.** A single large asset purchase (building, fleet, equipment) will dominate category totals. Identify and flag CapEx items — report OpEx and CapEx separately.
- **Foreign currency spend must be converted before aggregating.** Never add USD and GBP totals. Always confirm with the user which exchange rate to use: spot rate on transaction date, period average, or a fixed rate for budget comparison. State the rate used in the report.
- **PO-backed vs non-PO (invoice-only) spend tells a story.** High non-PO spend = high maverick risk. Always calculate the PO compliance rate if the data includes a PO number field.
- **Partial-year data requires annualisation — but flag it.** If the data covers 9 months, annualised spend = total × 12/9. Always state explicitly that figures are annualised estimates, not actual full-year spend.

---

## Categorisation Gotchas

- **Never present uncategorised spend as zero.** If a line item has no category, flag it as "Unclassified" and include it in the total. Uncategorised spend hidden from analysis leads to missed savings.
- **UNSPSC codes are often wrong in ERP systems.** Procurement teams frequently use default or catch-all codes. Treat existing category codes as a starting point, not ground truth — validate the top 20% of spend lines by value.
- **Description fields are your best categorisation signal, not the GL code.** General Ledger accounts are accounting constructs, not procurement categories. "Office supplies" in the GL could include marketing merchandise, safety equipment, and IT peripherals.
- **Services spend is systematically undercategorised.** It's easy to see "consultancy fees" as a single category. Break it down: IT consulting, HR consulting, legal, management consulting, etc. The savings levers are completely different.
- **Tail spend (the bottom 80% of suppliers by spend) is rarely worth deep analysis.** Focus the categorisation effort on the top 20% of suppliers that represent 80% of spend. Flag tail spend as an aggregated opportunity rather than line-by-line analysis.

---

## Savings Opportunity Gotchas

- **Never present a savings number without stating the assumption.** "Up to 15% savings" means nothing without the basis: benchmark comparison, consolidation model, price variance analysis, or demand review. Always cite the method.
- **Supplier consolidation savings are often overstated.** Consolidating from 5 to 1 supplier assumes the remaining supplier can absorb all volume at a better rate. This is often not true. Flag consolidation opportunities as "subject to supplier capacity confirmation."
- **Price variance is not always a savings opportunity.** Different prices for the same item across business units may reflect different specifications, service levels, or contract terms. Flag price variance for investigation — do not assume it's all recoverable.
- **Demand management is the highest-value lever and the hardest to quantify.** Reducing consumption is always better than negotiating lower unit prices. Flag high-spend categories where demand management is likely feasible (travel, professional services, print) — but do not put a savings figure on it without stakeholder input.
- **Contract savings vs. addressable spend.** Not all spend is under contract or re-contestable. Always identify the addressable spend (spend that could be put to market) separately from contracted, regulated, or single-source spend.
- **Year-on-year comparisons require like-for-like volume.** A 10% price increase is fine if volumes grew 10%. Always normalise for volume before declaring a price trend.

---

## Reporting Gotchas

- **Never share raw spend data with more people than necessary.** Spend data often reveals commercially sensitive relationships (e.g. which supplier is largest, which categories are undermanaged). Always confirm the intended audience before generating a report.
- **Executive reports need a "so what", not just charts.** A spend cube with no recommendations is interesting but not useful. Always lead with the top 3 action priorities and a rough savings potential range.
- **"Spend under management" is a metric executives love but organisations define differently.** Always state your definition: spend under a current contract? spend through approved channels? spend with preferred suppliers? Agree the definition before reporting.

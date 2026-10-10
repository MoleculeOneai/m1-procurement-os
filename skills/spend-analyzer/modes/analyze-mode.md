# Mode: Analyze Spend Data

## Goal
Transform raw spend data — however messy — into a structured spend cube: categorised, supplier-deduplicated, and ready for opportunity identification. By the end of this mode, the user has a clean spend picture and a prioritised list of savings opportunities.

---

## Step 1 — Receive data and taxonomy file

Ask the user to upload two things:

**1. Spend data (required)**
Accept: CSV, Excel (.xlsx/.xls), or pasted tabular data.

**2. Custom category taxonomy file (optional)**
Ask: *"Do you have a category taxonomy or supplier-category mapping file you'd like me to use? If yes, please upload it as a CSV. If not, I'll use the Molecule One default taxonomy."*

If they provide a taxonomy file, immediately run `lib/categorize_spend.py → load_custom_taxonomy()` on it and show the user a **Taxonomy Load Summary**:
- Number of L1 / L2 categories loaded
- Number of suppliers pre-mapped
- Whether keywords are present (for description matching)
- Any warnings (unknown columns, missing L1/L2 etc.)

Then ask: *"Should I use ONLY your taxonomy, or use it as the primary source with the Molecule One default as a fallback for any categories not covered?"*

Save the loaded taxonomy to `${CLAUDE_PLUGIN_DATA}/custom-taxonomy.json` so it persists for future sessions. On subsequent runs, check if this file exists and offer to reuse it or upload a new one.

**Custom taxonomy file format (share with user if they ask):**

The file should be a CSV with these columns:

| Column name | Required | Description |
|---|---|---|
| `l1` | Yes | Top-level spend family (e.g. "Indirect Services") |
| `l2` | Yes | Category (e.g. "Technology & IT") |
| `l3` | No | Sub-category (e.g. "Software & SaaS") |
| `keywords` | No | Comma-separated keywords for description matching (e.g. "software, licence, SaaS, cloud") |
| `supplier` | No | Supplier name to pre-assign to this category |

One row per category or per supplier mapping. Multiple rows with the same L1/L2 will be merged (keywords combined). Example:

```
l1,l2,l3,keywords,supplier
Indirect Services,Technology & IT,Software & SaaS,"software,licence,SaaS,cloud,subscription",
Indirect Services,Technology & IT,Software & SaaS,,,Microsoft
Indirect Services,Technology & IT,Software & SaaS,,,Salesforce
Indirect Services,Professional Services,Management Consulting,"consulting,advisory,strategy",Deloitte
```

Immediately run `lib/parse_spend_data.py → audit_data_quality()` and present the user with the **Data Quality Report** before proceeding. This should cover:
- Total rows and total spend value detected
- Currency fields found (and whether multi-currency is present)
- Data completeness: which fields are populated vs blank (supplier name, date, amount, category, PO number, GL code, cost centre, description)
- Duplicate transaction detection
- Date range covered (and whether this is a full financial year or partial)

**Do not proceed to analysis until the user has reviewed and acknowledged the data quality report.** If quality score is below 60%, strongly recommend the user clean the data first and provide guidance on the most impactful fixes.

---

## Step 2 — Normalise the data

Using `lib/parse_spend_data.py`:

1. **Standardise supplier names** — deduplicate variants of the same supplier. Show the user the deduplication mapping (e.g. "Microsoft / Microsoft Ltd / MSFT → Microsoft") and ask them to confirm before applying. Do not silently merge suppliers.

2. **Convert currencies** — if `audit_data_quality()` reports `is_multicurrency: true`, this step is **mandatory** before any spend totals are shown. A skipped or incomplete currency conversion is the most common cause of spend total gaps (e.g. £14.6M reported vs £18.2M expected).

   Call `lib/parse_spend_data.py → convert_and_summarise_currency()` and show the user the **Currency Conversion Summary** before proceeding:

   | Currency | Rows | Face Value | Rate Used | Converted (GBP/USD/etc.) | Status |
   |---|---|---|---|---|---|
   | GBP | 1,020 | £12.4M | 1.00 | £12.4M | Already target |
   | USD | 456 | $5.8M | 0.79 | £4.6M | Converted |
   | EUR | 24 | €0.3M | 0.86 | £0.26M | Converted |
   | **Total** | **1,500** | | | **£17.3M** | |

   Ask the user which rate method to use:
   - Transaction-date spot rate (most accurate, requires rate lookup)
   - Period average rate (simplest — ask user to provide one rate per currency)
   - Fixed budget rate (for budget comparison — ask user to provide)

   If the user cannot provide rates, use period average rates from a public source (state the source), and flag clearly in the report: *"Exchange rates used: USD 0.79, EUR 0.86 (Bank of England period average [PERIOD]). Actual converted values may differ."*

   Show `exclusion_impact` from the summary: if any rows were excluded because no rate was available, surface this as: **"CAUTION: £X of spend in [CURRENCY] has been excluded from this analysis because no exchange rate was provided. The total spend figure below understates actual spend by this amount."**

   Always state in the report which rate was used and its reference date.

3. **Separate CapEx from OpEx** — flag any transactions that appear to be capital expenditure (large one-off amounts, asset descriptions, depreciation accounts). Confirm with user. Report these separately.

4. **Exclude inter-company transactions** — ask if any suppliers are related entities. Exclude confirmed inter-company from external spend totals.

---

## Step 3 — Categorise the spend

Using `lib/categorize_spend.py`:

1. Apply the user's taxonomy from config.json. If taxonomy is "NOT_CONFIGURED" or "none", use the default Molecule One procurement taxonomy (Direct / Indirect / Services, then 3-level sub-categories).

2. Categorise each spend line using the description, GL code, and supplier name as signals — in that priority order.

3. Present a **categorisation confidence summary**:
   - High confidence (auto-assigned): lines with clear description or matching supplier-category history
   - Medium confidence (review suggested): lines where category is inferred from GL code only
   - Low confidence / Unclassified: lines with no useful signals

4. For medium and low confidence lines above £/$/€ 10,000: present to the user for manual confirmation before finalising. Do not silently categorise high-value lines with low confidence.

5. Calculate the **categorisation coverage rate**: % of spend value that has been successfully categorised. Flag if below 85%.

---

## Step 4 — Build the spend cube

Present the following views:

**By Category (L1 → L2 → L3):**
- Total spend per category
- % of total spend
- Number of suppliers per category
- YTD vs prior period comparison (if prior period data available)

**By Supplier (top 20 by spend):**
- Supplier name, category, total spend, % of total
- PO compliance rate per supplier (if PO data available)
- Number of business units / cost centres buying from this supplier

**By Business Unit / Cost Centre (if field available):**
- Spend per BU, top 5 categories per BU
- Cross-BU suppliers (same supplier bought by 3+ BUs — consolidation signal)

**Concentration metrics:**
- Top 10 suppliers as % of total spend
- Pareto: how many suppliers represent 80% of spend?
- Number of "tail" suppliers (spend < £/$5,000 per year)

---

## Step 5 — Identify savings opportunities

Using `lib/calculate_savings.py`, run the following opportunity screens:

**1. Supplier consolidation**
Identify categories with 5+ suppliers where the top supplier has <40% share — high consolidation potential. Estimate: consolidating to 2–3 preferred suppliers typically yields 8–15% savings through volume leverage.

**2. Price variance — two screens, run both:**

*Screen A — Transaction-level variance* (`screen_price_variance()`): identifies the same supplier/category combination with invoice amounts varying >15% across transactions. Good for commodity and SaaS categories.

*Screen B — Cost centre rate variance* (`screen_price_variance_by_cost_centre()`): compares each supplier's **average invoice amount per business unit**. This is the correct screen for professional services and project-based spend where the same supplier (e.g. Deloitte, McKinsey) charges materially different implied rates to different BUs. Flag variance >20% between BUs as a rate card investigation priority. Show the BU-by-BU breakdown in the output.

Always run Screen B for these categories: Professional Services, Technology & IT, Marketing & Communications, HR & People Services.

**3. Maverick spend — two screens, run both:**

*Screen A — Preferred supplier list* (`screen_maverick_spend()`): requires the user's preferred/contracted supplier list. If not available, note this and skip.

*Screen B — Consumer platform detection* (`detect_consumer_maverick()` in `lib/categorize_spend.py`): runs WITHOUT a preferred supplier list. Automatically flags well-known consumer-grade platforms that should not appear in corporate spend — e.g. Booking.com/Airbnb in Travel, Npower/EDF in Facilities, Zoom/Notion/Figma without enterprise agreements in Tech, Fiverr/Upwork in Marketing. **Always run Screen B** regardless of whether the user has a preferred supplier list. This catches the most obvious maverick spend that PO-absence alone misses.

Present consumer maverick findings separately with the reason for each flag, so the user can confirm whether an enterprise agreement exists before treating it as confirmed maverick.

**4. Tail spend rationalisation**
Count suppliers with <£/$5,000 annual spend. Calculate administrative cost of managing each relationship (default: £500 per supplier per year). Flag categories with high tail supplier counts for rationalisation.

**5. Demand management candidates**
Flag categories where spend has grown >15% YoY without a clear volume justification: travel, professional services, subscriptions, print. These are demand management candidates, not just price negotiation.

**6. Contract expiry pipeline**
If contract data is available, flag spend in categories where contracts expire within 6 months — procurement action needed.

Rank all identified opportunities by estimated savings value. Present as an **Opportunity Register** (use `templates/opportunity-register.md`).

---

## Step 6 — Summarise and choose output format

Present a brief inline summary:
1. **Spend snapshot** — total spend, active suppliers, top 5 categories, key ratios
2. **Top 3 priority actions** with rationale and estimated savings range
3. **Data quality issues to fix** before the next analysis cycle

Then ask the user which output format they want:

> *"How would you like the full report delivered?"*
> - **A) Interactive HTML dashboard** — a self-contained HTML file with clickable charts, filterable tables, and a savings opportunity register. Opens in any browser, no software needed.
> - **B) Excel workbook** — structured sheets for spend by category, top suppliers, quality metrics, and the opportunity register. Editable and shareable.
> - **C) Both** — HTML dashboard + Excel workbook
> - **D) Word document** — executive narrative report using `templates/spend-report.md`

For **HTML dashboard**: follow `report-mode.md → HTML Dashboard` instructions. Use `templates/spend-dashboard.html` as the base.
For **Excel**: use the `xlsx` skill. Create sheets: Summary, Spend by Category, Top Suppliers, Quality Metrics, Opportunity Register.
For **Word**: use `report-mode.md` and `templates/spend-report.md`.

---

## Tone & Style
- Numbers first, always. Lead with the data, then the interpretation.
- Ranges over false precision: "£1.2M–£1.8M savings potential" not "£1,542,000 savings."
- Flag assumptions explicitly — every savings figure must have a stated basis.
- "Addressable" spend, not "total" spend when discussing savings potential.

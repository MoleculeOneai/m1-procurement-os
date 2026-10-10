# Mode: Generate Executive Spend Report

## Goal
Produce a polished, executive-ready spend intelligence report. This is the output that goes to the CPO, CFO, or board — it must be clear, credible, and action-oriented.

---

## Step 1 — Confirm the audience and purpose

Ask:
- Who is the primary audience? (CPO / CFO / Board / Category manager / Procurement team)
- Is this a regular report (monthly/quarterly) or a one-off strategic review?
- Are there any areas to highlight or avoid? (e.g. a sensitive supplier relationship, ongoing negotiations that shouldn't be pre-empted)
- What decision does this report need to support? (Budget setting / savings programme launch / board update / supplier review)

The audience determines the depth and framing. Board-level = 1–2 pages, strategic narrative. CPO-level = 5–10 pages, opportunity pipeline. Category manager = deep dive, line-level data.

---

## Step 2 — Confirm data inputs

What is available:
- [ ] Categorised spend cube (from analyze-mode or user-provided)
- [ ] Prior period comparison data (YoY or QoQ)
- [ ] Benchmark data (from benchmark-mode or user-provided)
- [ ] Savings opportunity register (from analyze-mode)
- [ ] Contract expiry data (if available)
- [ ] KPI data (if regular report: savings delivered, PO compliance rate, supplier count trend)

Flag any gaps and ask the user to provide missing data or confirm they want the report to note where data was unavailable.

---

## Step 3 — Generate the report using `templates/spend-report.md`

Populate all sections. The structure is:

**Section 1 — Executive Summary (max 1 page)**
- Total spend: [£X] across [N] suppliers in [N] categories
- Key change vs prior period: [+/-X%] overall, key category movements
- Top 3 findings: what matters most and why
- Top 3 recommended actions: specific, owned, time-bound

**Section 2 — Spend Overview**
- Total spend by top 10 categories (table + visual description)
- Top 20 suppliers by spend
- Spend concentration: top 10 suppliers = X% of total
- Pareto analysis: X suppliers = 80% of spend

**Section 3 — Savings Opportunity Pipeline**
- Opportunity register with ranked savings potential
- Total addressable savings range: £X–£X
- Quick wins (deliverable in <3 months) highlighted separately
- Longer-term strategic opportunities

**Section 4 — Spend Quality Metrics**
- PO compliance rate (if data available): X% of spend is PO-backed
- Maverick spend: X% of spend is with non-preferred suppliers
- Contract coverage: X% of spend is under a current contract
- Tail spend: [N] suppliers represent only [X]% of spend but [Y]% of transaction volume

**Section 5 — Recommended Actions**
Produce an action table:

| Priority | Action | Category | Estimated Savings | Owner | Target Date |
|---|---|---|---|---|---|
| 1 | [Action] | [Category] | [£X–£X] | [Team] | [Date] |

Maximum 5 actions. Specific, achievable, owned.

---

## Step 4 — Choose output format

Before generating, ask:

> *"How would you like the report delivered?"*
> - **A) Interactive HTML Dashboard** — self-contained single-file HTML with clickable charts, filterable supplier and opportunity tables, and KPI cards. Opens in any browser, no software required. Best for sharing with stakeholders who want to explore the data.
> - **B) Excel Workbook** — structured sheets for Summary, Spend by Category, Top Suppliers, Quality Metrics, and Opportunity Register. Editable and easy to share.
> - **C) Word Document** — executive narrative report, best for formal board or CFO submissions.
> - **D) All three** — deliver HTML + Excel + Word.

---

## Step 4A — HTML Dashboard output

Use `templates/spend-dashboard.html` as the base. Inject real data by replacing all `{{PLACEHOLDER}}` tokens with JSON-serialised values from the analysis.

### Required data tokens

**Scalar tokens** — replaced with a plain value:

| Token | Format | Source |
|---|---|---|
| `{{ORG_NAME}}` | string | config.json → org_name |
| `{{REPORT_PERIOD}}` | string | e.g. `"FY2025 Q1–Q4"` |
| `{{GENERATED_DATE}}` | string | today's date |
| `{{CURRENCY}}` | string | `"£"`, `"$"`, or `"€"` |
| `{{TOTAL_SPEND}}` | string | formatted e.g. `"£18.2M"` |
| `{{TOTAL_SPEND_RAW}}` | number | raw value e.g. `18200000` |
| `{{SUPPLIER_COUNT}}` | number | distinct active suppliers |
| `{{CATEGORY_COUNT}}` | number | distinct L2 categories |
| `{{PO_COMPLIANCE_RATE}}` | number or `null` | 0–100, null if unavailable |
| `{{CONTRACT_COVERAGE}}` | number or `null` | 0–100, null if unavailable |
| `{{MAVERICK_RATE}}` | number or `null` | 0–100, null if unavailable |
| `{{QUALITY_SCORE}}` | number | 0–100 from `audit_data_quality()` |
| `{{SAVINGS_LOW}}` | string | formatted e.g. `"£1.2M"` |
| `{{SAVINGS_HIGH}}` | string | formatted e.g. `"£2.1M"` |
| `{{OPP_COUNT}}` | number | count of opportunities identified |
| `{{TOP10_SPEND_PCT}}` | number | % of total spend in top 10 suppliers |
| `{{PARETO_SUPPLIER_COUNT}}` | number | how many suppliers = 80% of spend |
| `{{TAIL_SUPPLIER_COUNT}}` | number | suppliers with < 1% of avg annual spend |
| `{{UNCAT_PCT}}` | number | % of spend not yet categorised |
| `{{UNCAT_VALUE}}` | string | formatted uncategorised spend value |
| `{{DUPLICATE_COUNT}}` | number | duplicate transactions detected |
| `{{DATE_RANGE}}` | string | e.g. `"Jan 2025 – Dec 2025"` |
| `{{ANNUALISED_NOTE}}` | string | e.g. `"Full year FY2025"` or `"Annualised from 10 months"` |

**JSON array tokens** — replaced with `json.dumps(list)`:

**`{{CATEGORIES_JSON}}`** — extended format with drill-down data:
```json
[{
  "name": "Software & SaaS",
  "l1": "Technology & IT",
  "spend": 2340000,
  "pct": 12.8,
  "suppliers": 23,
  "yoy_change": 8.2,
  "po_compliance": 88.0,
  "top_suppliers": [
    {"name": "Microsoft", "spend": 450000, "pct_of_cat": 19.2, "po_rate": 95, "status": "preferred"},
    {"name": "Salesforce", "spend": 320000, "pct_of_cat": 13.7, "po_rate": 72, "status": "preferred"}
  ]
}]
```
`top_suppliers` enables the category drill-down view to show clickable supplier rows. Omit it and the dashboard falls back to filtering the global suppliers list by category name.

**`{{SUPPLIERS_JSON}}`** — extended format with drill-down data:
```json
[{
  "name": "Deloitte",
  "category": "Management Consulting",
  "l1": "Professional Services",
  "l2": "Management Consulting",
  "spend": 380000,
  "pct": 2.1,
  "po_rate": 72,
  "bus": 3,
  "bu_list": ["Tech", "Product", "Finance"],
  "bu_spend": [
    {"bu": "Tech", "spend": 192000},
    {"bu": "Product", "spend": 120000},
    {"bu": "Finance", "spend": 68000}
  ],
  "status": "preferred",
  "monthly": [
    {"month": "Jan", "spend": 32000},
    {"month": "Feb", "spend": 28000}
  ],
  "related_opps": ["OPP-003"],
  "price_variance_flag": true,
  "notes": "Day rates vary £6k–£16k across BUs — rate card review recommended"
}]
```
`monthly` enables the spend trend chart in the supplier detail view. `bu_spend` enables the BU breakdown bars. `notes` + `price_variance_flag` surface a warning banner.

**`{{OPPORTUNITIES_JSON}}`** — extended format with full detail for accordion expansion:
```json
[{
  "id": "OPP-001",
  "type": "consolidation",
  "category": "Software & SaaS",
  "description": "12 software contracts with overlapping functionality across 4 BUs",
  "savings_low": 120000,
  "savings_high": 180000,
  "horizon": "quick",
  "effort": "Low",
  "priority": 1,
  "basis": "Asana, Monday.com, and Jira all active simultaneously. Usage audit shows 60% overlap in feature use.",
  "affected_suppliers": ["Asana", "Monday.com", "Atlassian"],
  "affected_categories": [],
  "actions": [
    "Conduct tool usage audit across all BUs within 30 days",
    "Select single preferred vendor based on audit output",
    "Migrate remaining users and cancel redundant contracts by Q3"
  ]
}]
```
`affected_suppliers` renders as clickable chips → supplier drill-down. `actions` renders as a checklist. `basis` is the evidence narrative shown on expand.

**`{{MONTHLY_JSON}}`** — overview trend chart:
```json
[{"month": "Jan", "spend": 1520000}, {"month": "Feb", "spend": 1380000}]
```
Use available months only if data is incomplete. The chart renders whatever is provided.

**`{{FIELD_COMPLETENESS_JSON}}`** — data quality table:
```json
[{"field": "Supplier Name", "pct": 98.2}, {"field": "Invoice Date", "pct": 91.4}]
```

**`{{CURRENCY_BREAKDOWN_JSON}}`** — currency mix bars:
```json
[{"currency": "GBP", "pct": 85.4, "count": 1284}, {"currency": "USD", "pct": 12.1, "count": 182}]
```

**`{{PRIORITY_ACTIONS_JSON}}`** — overview action table (max 5):
```json
[{
  "action": "Consolidate SaaS project management tools to single vendor",
  "category": "Software & SaaS",
  "savings": "£120k–£180k",
  "owner": "IT Procurement",
  "timeline": "Q3 2025"
}]
```

### Injection method

1. Read the full contents of `templates/spend-dashboard.html`
2. Replace each `{{TOKEN}}` with the real value using Python string `.replace()` or a template engine
3. For JSON arrays: `json.dumps(list_of_dicts)` — no pretty-printing needed
4. Write the populated file to the outputs folder: `[ORG_NAME]-Spend-Dashboard-[PERIOD].html`
5. Verify: open the file and check no `{{` remains in the output

### Fallbacks for missing data

- If PO compliance is unavailable: set `{{PO_COMPLIANCE_RATE}}` to `null` — the dashboard will hide that KPI card automatically
- If monthly data is sparse: set available months only; the chart will render what it has
- If no opportunity register: set `{{OPPORTUNITIES_JSON}}` to `[]` — the tab will show "No opportunities identified yet"

---

## Step 4B — Excel Workbook output

Use the `xlsx` skill. Create the following sheets in order:

**Sheet 1: Summary**
- KPI table: Total Spend, Supplier Count, Category Count, PO Compliance %, Maverick Rate %, Data Quality Score
- Top 3 findings (text)
- Top 3 recommended actions (text)

**Sheet 2: Spend by Category**
Columns: L1 Category | L2 Category | L3 Sub-category | Total Spend | % of Total | Supplier Count | YoY Change (if available)
Sort: descending by Total Spend. Apply conditional formatting: top 5 rows highlighted in light blue.

**Sheet 3: Top Suppliers**
Columns: Rank | Supplier Name | L2 Category | Total Spend | % of Total | PO Compliance % | Business Units | Status (preferred/tail/unclassified)
Top 50 suppliers. Conditional formatting: Status column — green for preferred, amber for unclassified, grey for tail.

**Sheet 4: Quality Metrics**
- Field completeness table (field name, % populated, RAG status)
- Duplicate transaction count
- Currency breakdown
- Date range covered

**Sheet 5: Opportunity Register**
Columns: ID | Opportunity Type | Category | Description | Savings Low | Savings High | Horizon | Effort | Priority | Status
Sort: by Priority ascending. Apply colour banding by Horizon (Quick = green, Medium = amber, Strategic = blue).

File naming convention: `[ORG_NAME]-Spend-Analysis-[PERIOD]-[DATE].xlsx`

---

## Step 4C — Word Document output

Use the `docx` skill to produce a formatted Word document from `templates/spend-report.md`.

File naming convention: `[ORG_NAME]-Spend-Intelligence-[PERIOD]-[DATE].docx`

Formatting:
- Executive summary on page 1, standalone
- Tables use light blue headers
- Key figures in bold
- Assumptions footnoted on every page with a savings figure
- Footer: "Confidential — [ORG_NAME] Procurement | moleculeone.ai"

---

## What good looks like
- An executive who wasn't in the analysis can read the summary and know: total spend, biggest risk, biggest opportunity, and what action to take
- Every savings figure has a stated method and range (never a false-precision single number)
- The report takes a position — it does not just present data and leave the reader to conclude
- Prior period comparison is present wherever data allows
- HTML dashboard: no `{{` tokens remain in the rendered file; all charts render; tables are filterable
- Excel workbook: conditional formatting applied; no empty sheets; column widths auto-fitted

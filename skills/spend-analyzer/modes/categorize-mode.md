# Mode: Categorise or Reclassify Spend

## Goal
Fix, improve, or build a spend taxonomy for an organisation. Use when the user has spend data with missing, inconsistent, or wrong categories, or when they want to migrate from one taxonomy to another.

---

## When to use this mode vs analyze-mode
- Use **analyze-mode** when the user has raw spend data and wants the full analysis end-to-end
- Use **this mode** when the user specifically wants to fix their categorisation, or has a taxonomy problem to solve independent of the full analysis

---

## Step 1 — Understand the current state

Ask:
- Do you have an existing taxonomy you want to keep, or are we building one?
- Is the issue that lines are uncategorised, or that existing categories are wrong?
- Do you have a standard you need to comply with (e.g. UNSPSC, eCl@ss, company standard)?
- How many spend lines need to be categorised (roughly)?

---

## Step 2 — Taxonomy design or confirmation

If the user needs a new taxonomy, propose the **Molecule One default procurement taxonomy**:

**Level 1 (Spend Family):**
- Direct Materials (goods that go into the product)
- Indirect Goods (goods that support operations but don't go into the product)
- Indirect Services (services that support operations)
- Capital Expenditure

**Level 2 (Category) — examples under Indirect Services:**
- Professional Services (consulting, legal, audit, recruitment)
- Facilities & Real Estate (rent, cleaning, maintenance, utilities)
- Technology & IT (software, hardware, cloud, telecoms)
- Marketing & Communications (agencies, media, print, events)
- Travel & Expenses (flights, hotels, ground transport, subsistence)
- HR & People (training, benefits, payroll services, temporary labour)
- Logistics & Distribution (freight, warehousing, courier)
- Financial Services (banking, insurance, FX)

**Level 3 (Sub-category):** Propose based on spend data — do not pre-build L3 without seeing what the spend actually contains.

If the user has an existing taxonomy, ask them to share it before proceeding. Do not override an existing taxonomy without explicit instruction.

---

## Step 3 — Batch categorisation

Using `lib/categorize_spend.py → batch_categorize()`:

Process spend lines in batches. For each line, use this signal hierarchy:
1. Supplier name → known supplier category mapping (check `${CLAUDE_PLUGIN_DATA}/supplier-category-map.json` if it exists)
2. Line item description → keyword matching
3. GL/account code → account-to-category mapping
4. Historical pattern for this cost centre

For every batch, present the results to the user with confidence scores. Ask for approval before committing. Never silently apply categorisation to high-value lines.

---

## Step 4 — Build and save the supplier-category map

After categorisation is confirmed, extract the supplier → category mapping and save to `${CLAUDE_PLUGIN_DATA}/supplier-category-map.json`. This becomes the training data for future analyses — over time, categorisation becomes faster and more accurate.

Format:
```json
{
  "Microsoft": { "category": "Technology & IT", "sub_category": "Software & SaaS", "confidence": "high" },
  "WeWork": { "category": "Facilities & Real Estate", "sub_category": "Flexible Workspace", "confidence": "high" }
}
```

---

## Step 5 — Categorisation quality report

Produce a summary:
- % of spend value now categorised (target: >95%)
- % of spend lines categorised
- Residual unclassified spend — list the top 10 by value for manual review
- Supplier-category conflicts detected (same supplier in 2+ categories — flag for review)

---

## Gotchas specific to this mode
- A supplier can legitimately span multiple categories (e.g. Amazon = IT hardware + office supplies + logistics). Flag multi-category suppliers rather than forcing them into one.
- Reclassification from an old taxonomy to a new one requires mapping every old category to a new one. Do not start reclassifying line by line — build the mapping table first and get user approval.
- Some organisations use GL codes as their "taxonomy" — this is fine as an input signal but should not be the output. GL codes are accounting constructs; procurement categories are strategic constructs.

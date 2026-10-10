# Mode: Draft a New RFQ

## Goal
Generate a Request for Quotation for well-defined goods or services where specifications are fixed and the primary evaluation criterion is price. RFQs are used when the what is known — only the price needs to be determined.

## Key Differences vs RFP
- Specifications are locked before issuing — do not draft an RFQ if scope is still evolving
- Primary scoring criterion is price (typically 70–100% weight)
- Shorter and more structured than an RFP
- Suppliers are not asked to propose a solution — they are asked to price a defined one
- Response time is shorter (5–10 days typical vs. 2–4 weeks for RFP)

## When NOT to Use RFQ Mode
If the user's requirements include any of the following, redirect to RFP mode:
- "We're not sure exactly what we need"
- "We want suppliers to suggest an approach"
- "Quality and capability matter as much as price"
- "This is a complex or professional services engagement"

## Step-by-Step

**Step 1 — Confirm specifications are complete and fixed.**
Ask: "Are the specifications finalised, or do you expect to refine them based on supplier input?" If the latter, use RFP mode instead.

**Step 2 — Collect the specification.**
Required: exact item descriptions, quantities, units of measure, delivery requirements, quality standards, incoterms (if relevant), payment terms expected.

**Step 3 — Draft the RFQ with these sections:**
1. Introduction & instructions
2. Specification table (item / description / quantity / unit / required delivery date)
3. Pricing schedule (suppliers fill in unit price / total — exactly matching spec table)
4. T&Cs and payment terms
5. Submission instructions (format, deadline, contact)

**Step 4 — Pricing schedule must mirror the specification.**
Use `lib/generate_report.py` with mode="rfq_pricing_table" to produce a clean, locked pricing schedule that suppliers fill in. Column order: Item No. | Description | Qty | Unit | Unit Price | Total Price | Lead Time.

**Step 5 — Log and distribute.**
Same distribution and logging steps as RFP mode.

## What Good Looks Like
- Specification table and pricing schedule are identical in line items (no mismatch)
- No ambiguity in quantity or unit of measure
- Suppliers can complete the pricing schedule in under 30 minutes
- Winner is deterministic from price alone (or price + lead time if stated)

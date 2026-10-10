# Mode: Supplier Performance Reporting

## Goal
Generate a complete, share-ready supplier performance report for a named supplier, covering: the current period scorecard, trend analysis vs. prior periods, key findings, action items, and (where required) a formal Supplier Improvement Plan. The output is a formatted .docx report ready to share internally and, in a tailored version, with the supplier.

---

## Step 1 — Load data

1. Load the most recent scored session from `${CLAUDE_PLUGIN_DATA}/scored-sessions/[SUPPLIER]-*.json`
2. Load prior sessions for this supplier from the same folder (up to the last 4 periods for trend analysis)
3. Load the original scorecard design to retrieve criteria names, weights, and anchors
4. Check `${CLAUDE_PLUGIN_DATA}/scorecard-history.log` for the full history entry

If no scored session exists for the requested supplier/period, route to `modes/scoring-mode.md` first.

---

## Step 2 — Determine the report type

Ask: "Which report format do you need?"

| Type | Audience | Content |
|---|---|---|
| **Internal summary** | Category manager, CPO, finance | Full scorecard, trend, actions, internal commentary |
| **Supplier-facing report card** | Supplier account manager | Summary scores, key findings, agreed actions — NO internal commentary |
| **Formal Performance Improvement Plan (PIP)** | Supplier leadership | Triggered by Red rating — formal corrective action requirements |
| **Executive dashboard update** | CPO / Board | One-page: RAG, trend arrow, top issue, top action |

Never send an internal summary to the supplier. The internal version contains reviewer commentary that can damage the relationship and may be legally sensitive.

---

## Step 3 — Build the trend analysis

Use data from the last 2–4 periods (if available) to compute:

**Trend table:**
| Period | Overall Score | RAG | Delta | Key Issue |
|---|---|---|---|---|
| [Q-3] | [score] | [RAG] | — | [issue] |
| [Q-2] | [score] | [RAG] | [+/-] | [issue] |
| [Q-1] | [score] | [RAG] | [+/-] | [issue] |
| **Current** | [score] | [RAG] | [+/-] | [issue] |

**Trend summary:**
- Overall trajectory: 🔺 Improving / ➡ Stable / 🔻 Declining
- Consistently strong dimensions (Green in all periods): [list]
- Consistently weak dimensions (Amber/Red in 2+ periods): [list]
- Most improved dimension vs. prior period: [name] (+[delta])
- Most deteriorated dimension vs. prior period: [name] (-[delta])

**Minimum data requirement for trend:** 2 periods. If only 1 period exists, state: "Trend analysis will be available from the next review period."

---

## Step 4 — Identify key findings

From the current period scores and trend data, generate 3–5 specific findings. A finding is not a dimension score — it is an insight derived from the data. Format:

> **Finding 1 — [Short title]**
> [2–3 sentences: what the data shows, why it matters, any context from reviewer evidence]

Example:
> **Finding 1 — OTIF has deteriorated for the third consecutive quarter**
> OTIF scored 3 (94%) in Q4 2025, 2 (89%) in Q1 2026, and 2 (87%) in Q2 2026. This is now below the contractual threshold of 90% and has been flagged by the operations team as impacting production scheduling. No root cause has been provided by the supplier to date.

---

## Step 5 — Compile action items

Aggregate all action items from the scored session. Categorise as:
- **Supplier actions** — things the supplier must do
- **Buyer actions** — things our team must do (e.g. provide clearer specifications, respond to supplier queries)
- **Joint actions** — require both parties

| # | Action | Category | Owner | Deadline | Status |
|---|---|---|---|---|---|

**Important:** Buyer actions must be included. A report that only asks the supplier to improve, without acknowledging any buyer-side contribution to issues, will not be trusted by the supplier.

---

## Step 6 — Determine if a Supplier Improvement Plan is required

Trigger a formal SIP if ANY of:
- Overall score is Red (<50)
- The same dimension has been Amber or Red for 3+ consecutive periods
- A critical dimension (weight ≥20%) has scored 1 in the current period

If triggered, say:
> "This supplier's performance meets the threshold for a formal Supplier Improvement Plan. I recommend including one in this report. Shall I draft it?"

If yes, use `templates/improvement-plan.md` to generate the SIP. A SIP must include:
- Specific, measurable improvement targets for each Red/chronic Amber dimension
- A defined review checkpoint (typically 30/60/90 days)
- Escalation path if targets are not met
- Statement that failure to meet SIP targets may trigger a re-sourcing event

---

## Step 7 — Generate the report document

Use `lib/report_generator.py` to assemble and populate `templates/supplier-report-card.md`.

Generate a `.docx` file using the `docx` skill.

Document naming:
```
[ORG_NAME]-Supplier-Report-[SUPPLIER]-[YYYY-QN].docx
```

For the supplier-facing version:
```
[ORG_NAME]-[SUPPLIER]-Performance-Report-[YYYY-QN].docx
```

Formatting:
- RAG colour-coding: Green (#70AD47), Amber (#FFC000), Red (#FF0000) in score cells
- Trend arrows: 🔺 🔻 ➡ in trend table
- Section headers in navy (#1B3A6B)
- Footer: "Confidential — [ORG_NAME] Procurement | moleculeone.ai"

---

## Step 8 — Pre-distribution checklist

Before generating the supplier-facing version, confirm:
- [ ] Internal commentary has been stripped
- [ ] Any commercially sensitive data (budget, competitor names) has been removed
- [ ] All action items are agreed and assigned
- [ ] The report has been approved by the category manager
- [ ] A meeting has been scheduled to walk through the report with the supplier

For Red-rated suppliers: "Has a review meeting been scheduled within 10 business days?"

---

## Step 9 — Log

Append to `${CLAUDE_PLUGIN_DATA}/scorecard-history.log`:
```
DATE: [date]
EVENT: Report generated
SUPPLIER: [name]
PERIOD: [period]
REPORT_TYPE: [Internal / Supplier-facing / SIP]
RAG: [rating]
SIP_TRIGGERED: [Yes / No]
```

---

## What Good Looks Like

- Trend section covers at least 2 periods — single-period reports note this limitation
- Key findings are specific and evidence-based — not generic ("performance was acceptable")
- Buyer-side actions are included alongside supplier actions
- Supplier-facing version contains no internal commentary
- SIP is triggered automatically when thresholds are met — not left to the user to decide

# Mode: Draft a New RFP

## Goal
Generate a complete, supplier-ready Request for Proposal document from the user's SOW or requirements brief. The output is a **structured questionnaire** — not a narrative brief — so that all suppliers answer the same numbered questions in the same format, enabling direct comparison and weighted scoring.

---

## The Output Format — Always Use the Structured Questionnaire

Every RFP you generate **must** use the structured questionnaire format defined in `templates/rfp-template.md`. This is non-negotiable. Never generate a narrative RFP that leaves suppliers free to respond however they choose.

The structured format means:
- **Numbered questions** (Q1.1.1, Q1.2.1 etc.) so responses can be cross-referenced exactly
- **Response type tags** on every question — `[TEXT]`, `[TABLE]`, `[ATTACHMENT]`, `[WORK SAMPLE]`, `[YES / NO + EVIDENCE]`, `[FINANCIAL DATA]` — so suppliers know exactly what format to provide
- **Section weights and subsection weights** — so suppliers can see how their response will be scored and allocate effort accordingly
- **Word limits** on text responses — so responses are comparable in scope
- **Guidance notes** under each question ("What a strong response looks like...") — so suppliers understand the bar, and evaluators know what to look for
- **A mandatory requirements table** at the top — so disqualification criteria are explicit
- **A submission checklist** at the end — so nothing is missed

When you populate the template, replace all `[PLACEHOLDER]` tokens with real content derived from the SOW. Flag any section where the SOW was ambiguous with a `[REVIEW NEEDED: reason]` marker.

---

## Step 1 — Gather source documents

Ask the user to share whatever documents they have that describe the requirement. You do not need a formal SOW. Accept any combination of:

| Document type | What to extract |
|---|---|
| Statement of Work (SOW) | Deliverables, scope, timelines, acceptance criteria |
| Old / existing contract | Previous scope (not pricing), commercial terms as baseline, contract end date |
| Email thread | Current intent, decisions made, deadlines mentioned, attachments referenced |
| Meeting notes / minutes | Decisions, action items, implied requirements, unresolved items |
| Business Requirements Document (BRD/FRD) | Must Have / Should Have / Could Have split, requirement IDs, non-functional requirements |
| Presentation slides | High-level objectives, key numbers — flag that slides lose structure when extracted |
| Description in words | Take what the user says and treat it as informal requirements |

**If multiple documents are provided, process each separately.** Call `lib/extract_sow.py → extract_from_any_document()` once per document, then merge using `merge_extractions()`. Do not concatenate the texts — type detection will fail.

**After extraction, always show the user:**
1. The detected document type(s) and confidence level — ask them to confirm if confidence is "low"
2. The full ambiguities list — every item must be resolved or explicitly waived before drafting
3. Any conflicts found across documents (e.g. different timelines in an email vs a contract)
4. Any recommendations from the extractor (e.g. "email content takes precedence over contract scope")

**Never proceed to drafting with unresolved ambiguities.** The quality of the RFP is entirely dependent on the quality of the source material. A 10-minute clarification conversation saves days of revision.

---

## Step 2 — Confirm key parameters before drafting

Do not draft until you have confirmed:

- [ ] **Category** — what is being procured (used in RFP reference, header, and pricing schedule)
- [ ] **Supplier shortlist** — names and contact emails for distribution
- [ ] **Submission deadline** — exact date, time, and timezone (never "in 14 days")
- [ ] **Section weights** — confirm or override the 5-section split (Company & Capability / Technical Approach / Delivery & Implementation / Commercial Proposal / Risk & Compliance). If the user has no preference, propose a default based on the category:
  - Professional services: 20 / 30 / 20 / 20 / 10
  - Technology / SaaS: 15 / 35 / 20 / 20 / 10
  - Logistics / operations: 15 / 25 / 25 / 25 / 10
  - Commodity / goods: 10 / 20 / 20 / 40 / 10
- [ ] **Mandatory requirements** — certifications, insurance, geographic, regulatory. These go in the disqualification table.
- [ ] **Budget disclosure** — include a budget range or keep blind? Never assume; always ask.
- [ ] **Governing law / jurisdiction** — for the commercial terms section

If any of these are missing, ask before drafting. Do not make assumptions about weights or mandatory requirements.

---

## Step 3 — Populate the structured questionnaire template

Open `templates/rfp-template.md` and populate every section:

**Header block:**
- Replace `[ORG_NAME]` with the user's organisation name (from config.json `org_name` field)
- Set `[CATEGORY]`, `[RFP-YYYY-NNN]`, `[DATE]`, `[SUBMISSION DEADLINE]`, `[CONTACT_EMAIL]`

**PART A — Information for Suppliers (no vendor responses required):**
Populate all of Part A from the SOW and confirmed parameters before moving to Part B questions. This is the context suppliers need to write a strong proposal.
- Section 1 (About [ORG_NAME]): Pull from config.json `org_name` and any company description in the SOW. If not provided, draft 2–3 sentences based on the category and flag with [REVIEW NEEDED].
- Section 2 (Background & Purpose): Summarise the business need from the SOW. Explain why this procurement is happening now.
- Section 3 (Scope of Requirement): Extract the in-scope deliverables and volumes from the SOW. Explicitly state what is out of scope if the SOW indicates any boundaries.
- Section 4 (Contract Details): Populate from confirmed parameters. Set budget to "Not disclosed" unless the user has approved disclosure.
- Section 5 (Procurement Timeline): Populate with all confirmed dates. Every milestone row must have a date — no blank rows.
- Section 6 (Contact Persons): Use the contact email from config.json. Ask the user for names if not already provided.
- Section 7 (Important Rules): These are standard — populate as-is unless the user instructs otherwise.

**Mandatory requirements table (top of Part B):**
- Populate M1–M4 rows with the confirmed mandatory requirements
- Add or remove rows as needed — the template shows 4 but there can be more

**Scoring overview table:**
- Replace `[W1]` through `[W5]` with the confirmed section weights (must sum to 100)

**Section and subsection weights — INTERNAL USE ONLY:**
- Weights are **never** included in the supplier-facing RFP document. They live only in the internal scorecard (`templates/scorecard.md`) and the evaluator's working files.
- The supplier document states only that "evaluation criteria and weightings are confidential to the evaluation panel." This is deliberate — disclosing weights tells suppliers where to game their responses.
- Distribute each section weight across its subsections. Suggested defaults:
  - Section 1 (Company & Capability): 1.1 Company Overview 40% | 1.2 Relevant Experience 60%
  - Section 2 (Technical Approach): 2.1 Understanding of Requirement 25% | 2.2 Proposed Methodology 50% | 2.3 Team & Resourcing 25%
  - Section 3 (Delivery & Implementation): 3.1 Mobilisation & Transition 50% | 3.2 Ongoing Service Delivery 50%
  - Section 4 (Commercial Proposal): 4.1 Pricing 70% | 4.2 Commercial Terms 30%
  - Section 5 (Risk & Compliance): 5.1 Risk Management 50% | 5.2 Compliance & Certifications 50%
- Adjust based on what matters most for this category

**Questions (Q1.1.1 through Q5.2.3):**
- Keep all standard questions from the template
- Add category-specific questions where the SOW demands them — insert as Q[X.Y.Z] following the numbering convention
- Remove questions that are genuinely irrelevant (e.g. Q3.1.2 transition plan if there is no incumbent supplier) — note any removals at the top of the relevant section
- For `[FINANCIAL DATA]` questions: populate the pricing schedule line items to exactly match the scope deliverables from the SOW — 1:1 line items, no generic entries

**Certification requirements (Q5.2.1 table):**
- Populate with the actual certifications required for this category
- Set insurance minimum amounts based on the contract value

---

## Step 4 — Review before generating the document

Before generating the final Word document, present the user with:

1. The confirmed section weights (confirm they sum to 100%)
2. The mandatory requirements list (confirm these are correct — a wrongly stated mandatory requirement can invalidate the process)
3. Any `[REVIEW NEEDED]` flags — these must be resolved or explicitly waived before distribution
4. The pricing schedule line items — confirm these match the actual deliverables

Ask: "Any changes before I generate the final document?"

---

## Step 5 — Generate the RFP Word document

Use the `docx` skill to produce a formatted `.docx` file.

Document naming convention (from `assets/branding.md`):
```
[ORG_NAME]-RFP-[YYYY]-[NNN]-[CATEGORY].docx
```

Formatting requirements:
- Section headers in navy (#1B3A6B)
- Question numbers bold
- Response type tags in monospace / code formatting
- Tables use light blue (#D5E8F0) headers
- Footer: "Confidential — [ORG_NAME] Procurement | moleculeone.ai"

---

## Step 6 — Generate supplier distribution materials

Alongside the RFP, generate:
- Cover email using `templates/cover-email.md`
- Q&A log template using `templates/qa-log.md`
- Blank scorecard using `templates/scorecard.md` — pre-populated with the question numbers and weights from this RFP

---

## Step 7 — Confirm before distribution

State explicitly:
> "Ready to distribute to [n] suppliers: [names]. The RFP contains [X] sections and [Y] questions. Submission deadline is [DATE] at [TIME] [TIMEZONE]. Shall I proceed?"

---

## Step 8 — Log the event

Append to `${CLAUDE_PLUGIN_DATA}/rfx-history.log`:
```
DATE: [date]
CATEGORY: [category]
MODE: RFP
RFP_REFERENCE: [ref]
SUPPLIERS_INVITED: [n] — [names]
DEADLINE: [date]
SECTION_WEIGHTS: C&C [W1]% | Tech [W2]% | Delivery [W3]% | Commercial [W4]% | Risk [W5]%
BUDGET_DISCLOSED: yes/no
STATUS: Issued
```

---

## Tone & Style

Follow `assets/branding.md` for all terminology. Key rules:
- "Supplier" not "vendor"
- "Proposal" not "bid" or "tender response"
- Active voice: "The supplier will provide..." not "It is expected that..."
- All deadlines as absolute dates and times, never relative
- No jargon without explanation — suppliers from adjacent industries must be able to understand every question

---

## What Good Looks Like

- Every question has a response type tag — no open-ended questions without format guidance
- Section weights sum to exactly 100%
- The pricing schedule line items match the SOW scope 1:1
- No `[REVIEW NEEDED]` markers remain before distribution
- Mandatory requirements table is populated with verifiable, binary criteria
- A blank scorecard is ready alongside the RFP — one cannot be sent without the other

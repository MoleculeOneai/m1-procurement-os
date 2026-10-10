# Mode: Full Evaluation (End-to-End)

## Goal
Read all supplier response files from a folder, extract scoring criteria (from the original RFP or user-defined), score each supplier section by section, produce a side-by-side comparison, and generate both a Word narrative report and an Excel scoring grid. This is the primary mode — used for the majority of evaluation sessions.

---

## Step 1 — Confirm output format

Before reading any files, confirm the output format with the user:

> "Before we start, what format would you like the outputs in?
> - **Both Word + Excel (recommended):** Word for the narrative report and supplier letters; Excel for the scoring grid with RAG colours and formulas
> - **Word only:** Full report in a single document
> - **Excel only:** Scoring grid only — no narrative"

If the user has no preference, default to **Both** and proceed.

---

## Step 2 — Inventory supplier response files

Use `lib/response_reader.py` with `mode="inventory"` to scan the folder and list all files found.

Present the inventory to the user:

> "I've found the following files in the folder:
> - [Filename] — [Supplier Name] — [Format: PDF / Word / Excel]
> - [Filename] — [Supplier Name] — [Format]
> ...
>
> **Questions before I proceed:**
> 1. Have I correctly matched each file to a supplier? Are any files missing or incorrectly assigned?
> 2. Are there any suppliers you expected to receive a response from who are not listed here?
> 3. If multiple files exist for one supplier (e.g. a narrative doc + a pricing spreadsheet), confirm which is which."

Do not proceed until the user confirms the inventory is complete and correctly assigned.

---

## Step 3 — Load the original RFP and extract scoring criteria

**If the original RFP document is available:**

Use `lib/criteria_extractor.py` with `mode="from_rfp"` to:
1. Parse the RFP document (PDF or .docx)
2. Identify scoreable sections (exclude administrative sections: T&Cs, submission instructions, company background)
3. Propose a section list and weights based on the RFP structure

Present proposed criteria to the user:

> "I've extracted the following scoreable sections from your RFP:
>
> | # | Section | Proposed Weight |
> |---|---|---|
> | 1 | [Section name from RFP] | [W]% |
> | 2 | ... | ... |
> | **TOTAL** | | **100%** |
>
> Do these sections and weights look right? You can: (a) approve as-is, (b) adjust weights, or (c) add/remove sections."

**If no RFP document is available:**

Route to `modes/criteria-setup-mode.md` to define criteria with the user, then return here at Step 4.

---

## Step 4 — Lock weights and confirm mandatory requirements

State clearly:
> "I'm locking these weights now. Changing them after scoring begins will require a full rescore — which I can do via the Rerun mode. Do you confirm these weights?"

Wait for explicit confirmation before proceeding.

Then ask:
> "Are there any mandatory pass/fail requirements a supplier must meet to be considered? Examples: ISO certification, minimum company revenue, geographic coverage, insurance minimums."

Record any mandatory requirements for the disqualification check.

---

## Step 5 — Run disqualification check

Before scoring, check each supplier against mandatory requirements.

Use `lib/response_scorer.py` with `mode="disqualification"`.

Present results:

> **Disqualification Check**
>
> | Requirement | [Supplier A] | [Supplier B] | [Supplier C] |
> |---|---|---|---|
> | [Requirement 1] | ✅ Pass | ✅ Pass | ❌ Fail |
> | [Requirement 2] | ✅ Pass | ✅ Pass | ✅ Pass |
> | **Proceeds to scoring?** | ✅ Yes | ✅ Yes | ❌ No — DQ |

Ask the user to confirm any disqualifications before proceeding. Disqualified suppliers are excluded from scoring entirely — not given a zero score.

---

## Step 6 — Extract data from each supplier's response

Use `lib/response_reader.py` with `mode="extract"` to pull structured content from each qualified supplier's files.

For each section/criterion, extract:
- The supplier's stated response or approach (narrative sections)
- Specific data points: pricing, timelines, certifications, references, capacity figures
- Any caveats, assumptions, or conditions the supplier has stated

For pricing sections specifically: use `lib/response_scorer.py` with `mode="normalise_pricing"` to convert all pricing structures to TCO over the contract term before scoring.

Flag any "Not stated" sections — where the supplier did not address a section at all. Send a clarification request template:
> "Supplier [X] did not address [Section Y] in their submission. I recommend sending a clarification request before finalising their score. Shall I draft one?"

---

## Step 7 — Score each supplier section by section

Use `lib/response_scorer.py` with `mode="score"`.

Score each qualified supplier against each section on a 1–10 scale. For each score:
- Link the score to specific evidence from the supplier's submission
- Apply consistent calibration across all suppliers (a 7/10 for Supplier A means the same as 7/10 for Supplier B)
- Flag any section where evidence is thin or absent

Present scores dimension by dimension — not all at once — so the user can review and challenge before the full scorecard is finalised.

After all sections are scored, show the preliminary summary and ask: "Do these scores look right to you? Any you'd like to revisit before I generate the outputs?"

---

## Step 8 — Build the side-by-side comparison

Use `lib/response_scorer.py` to compute weighted totals and produce the comparison matrix.

Format using `templates/comparison-matrix.md`:

| Section | Weight | [Supplier A] | [Supplier B] | [Supplier C] | Best in section |
|---|---|---|---|---|---|
| [Section 1] | [W]% | [score/10] | [score/10] | [score/10] | [Supplier name] |
| **Weighted Total** | **100%** | **[N.N]/10** | **[N.N]/10** | **[N.N]/10** | |
| **RAG** | | 🟢/🟡/🔴 | 🟢/🟡/🔴 | 🟢/🟡/🔴 | |
| **Rank** | | [#] | [#] | [#] | |

Highlight best-in-section for each row.

---

## Step 9 — Generate the summary page

Using `templates/summary-page.md`, produce a one-page executive summary covering:

- Evaluation overview: category, RFP reference, number of suppliers, date
- Disqualifications (if any) with reason
- Ranked scorecard table with RAG ratings
- Top 2–3 strengths and weaknesses per supplier (bullet points)
- **Recommended shortlist** (top 2 suppliers) with rationale citing specific scores
- **Recommended for award** (if proceeding to direct award) — top-ranked supplier with conditions

State clearly:
> "This recommendation is based solely on the evaluation criteria and weights agreed before scoring. The final award decision rests with [ORG_NAME]."

---

## Step 10 — Generate output documents

Use `lib/report_builder.py` to assemble the outputs.

**Word report** (internal) — `templates/evaluation-report.md`:
- Cover page with evaluation reference, category, date, evaluator
- Methodology section: criteria source, weights used, scoring scale, disqualification rules
- Section-by-section findings (narrative per section, per supplier)
- Side-by-side comparison matrix
- Summary page and recommendation
- Appendix: disqualification log, clarification requests sent

**Excel scorecard** — produce using the `xlsx` skill:
- Tab 1: Summary — ranked table, RAG colours, overall scores
- Tab 2: Section Scores — full scoring grid with weights, raw scores, weighted scores per section per supplier
- Tab 3: Pricing — TCO normalisation workings and price score derivation
- Tab 4: Disqualifications — suppliers removed and reasons

File naming (from `assets/branding.md`):
```
[ORG_NAME]-RFP-Evaluation-[REF]-[YYYY-MM-DD].docx
[ORG_NAME]-RFP-Scorecard-[REF]-[YYYY-MM-DD].xlsx
```

---

## Step 11 — Draft supplier outcome letters

For each supplier, draft an outcome letter using the appropriate template:
- **Shortlisted suppliers:** confirm they are on the shortlist, outline next steps
- **Unsuccessful suppliers:** notify they have not been shortlisted; offer a debrief

Ask: "Shall I draft outcome letters for all [n] suppliers now?"

---

## Step 12 — Log the evaluation

Append to `${CLAUDE_PLUGIN_DATA}/evaluation-history.log` (see SKILL.md for format).

---

## What Good Looks Like

- Every file in the folder is accounted for and assigned to a supplier before scoring begins
- Disqualification check is completed and confirmed before scoring — never silently included
- Pricing is normalised to TCO before a price score is assigned
- Every score has a specific evidence citation from the supplier's submission
- Calibration is confirmed across all suppliers before outputs are generated
- Both outputs (Word + Excel) are produced unless the user explicitly opts for one only
- Outcome letters drafted for all suppliers — not just the winner
- Evaluation history log updated before the session ends

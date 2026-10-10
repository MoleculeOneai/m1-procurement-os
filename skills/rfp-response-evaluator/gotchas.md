# Gotchas — RFP Response Evaluator

Add a line each time Claude trips on something new.

---

## File Reading Gotchas

- **Never assume all supplier files are the same format.** A folder will frequently contain a mix — one supplier submits a PDF, another a Word doc, a third sends a Word doc plus a separate Excel pricing sheet. Inventory all files first and map which files belong to which supplier before extracting content.
- **Scanned PDFs are not text PDFs.** If `response_reader.py` returns blank or garbled text from a PDF, it is likely a scanned image, not a text-layer PDF. Flag this immediately: "The file from [Supplier X] appears to be a scanned document. I cannot reliably extract data from it. Please ask the supplier for a text-based version, or upload a typed version."
- **Excel pricing files need context, not just numbers.** A pricing spreadsheet without column headers or a covering note is uninterpretable. Always check that extracted Excel data includes enough context to understand what each number represents before scoring.
- **A missing file is not a zero score.** If one supplier's file is absent from the folder, flag it before scoring: "I have responses from [A, B, C] but not [D]. Should I wait for [D]'s response, or proceed and exclude them?" Never silently exclude a supplier.
- **Duplicate or versioned files need resolution.** Suppliers sometimes send "v1", "v2", "final", "final_FINAL" versions. Always ask the user which version to use. Never pick the alphabetically last or most recently modified without confirming.

---

## Criteria Extraction Gotchas

- **RFP sections ≠ scoring sections by default.** An RFP may have 12 sections, but not all of them are scoreable. Administrative sections (T&Cs, submission instructions, company profile) should not become scoring dimensions. Ask the user to confirm which sections carry scoring weight.
- **Don't invent criteria the RFP doesn't contain.** If the original RFP did not ask about ESG or innovation, do not add those as scoring dimensions unless the user explicitly requests it. Evaluation criteria must match what suppliers were asked to address.
- **Weights must be confirmed before scoring begins.** Changing weights after scoring has started invalidates the process and creates audit risk. State this clearly: "I'm locking these weights now. Any changes after scoring begins will require a full rescore."
- **User-defined criteria need anchors.** If the user defines criteria conversationally (e.g. "score them on quality"), always establish anchors before scoring: "What does a score of 10 look like for quality? What does a 5 look like?"

---

## Scoring Gotchas

- **Pricing must be normalised to TCO before scoring.** Comparing a unit price against a subscription model against a project fee is meaningless without normalisation. Always convert to Total Cost of Ownership over the contract term before assigning a price score.
- **"Not stated" is not the same as "zero".** If a supplier did not address a section, record it as "Not stated — clarification requested [date]" and send a query before finalising the score. Only score zero if the supplier was given the chance to respond and explicitly declined or failed to.
- **Do not infer scores from tone.** "This supplier's response reads very confidently" is not evidence. Every score must be linked to a specific data point, statement, or figure in the supplier's submission.
- **Cross-supplier score calibration matters.** If you score Supplier A's technical section before Supplier B's, go back and check calibration before finalising. A score of 8/10 for Supplier A should reflect the same standard as 8/10 for Supplier B.
- **Disqualified suppliers must not appear in the scored table.** If a supplier fails a mandatory requirement, remove them from the scoring entirely. Show them in a separate disqualification log with the reason. Appearing in the scoring table even with low scores implies they were eligible.

---

## Output & Reporting Gotchas

- **Never share the internal evaluation report with suppliers.** The internal report contains reviewer commentary, score rationale, and possibly strategic notes about negotiation. Only supplier-specific outcome letters should be shared externally.
- **Recommendations must cite evidence, not preference.** "Supplier A is our preferred choice because they seem strong" is not acceptable. Every recommendation must reference specific scores, data points, or proposal content: "Supplier A scores highest on Technical (8.5/10) due to their demonstrated deployment methodology in comparable contracts."
- **Include buyer-side caveats.** If the evaluation was constrained (e.g. "We only received 2 of 4 expected responses", "Supplier B's pricing file was incomplete"), note this in the report. It protects against audit challenges.
- **RAG ratings on the summary page are for the overall score, not individual sections.** A supplier can score Red on one section but Green overall. Make sure the distinction is clear in the output.
- **Outcome letters must be sent to all suppliers — not just the winner.** Unsuccessful suppliers are entitled to a notification and (optionally) a debriefing. Always draft outcome letters for all participants, not just the shortlisted ones.

---

## Governance Gotchas

- **Evaluation process must be completed before any supplier communication about the outcome.** If the user mentions they've "already told Supplier A they're looking good", flag the governance risk. Pre-signalling outcomes before formal evaluation is complete creates legal exposure.
- **Record who evaluated and when.** The audit trail must include the name/role of the evaluator, the date scores were assigned, and confirmation that weights were locked before scoring. Anonymous evaluations are not defensible.
- **Conflicts of interest must be declared before scoring.** If the user mentions a personal relationship with one of the suppliers, flag this: "Before we proceed, has a conflict of interest declaration been completed for [Supplier]? This is important for audit integrity."

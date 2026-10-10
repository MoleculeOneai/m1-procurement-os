# Gotchas — RFP Generator & Evaluator

Add a line each time Claude trips on something new. This file is the highest-signal content in this skill.

---

## Source Document Gotchas

- **Accept any document type — not just SOWs.** Source material may be an old contract, an email thread, meeting notes, a BRD, a presentation, or a user's verbal description. Use `extract_from_any_document()` on each file and `merge_extractions()` when multiple are provided. Never refuse to proceed just because there is no formal SOW.
- **Old contracts: extract scope, never pricing.** When a previous contract is provided as context, the pricing terms must not be carried forward into the new RFP. Scope clauses and commercial term structure are fair game; numbers are not.
- **Email threads read top-to-bottom, but recent = top.** The most current version of a requirement is usually in the first email (most recent). Later (lower) messages provide history and context — treat them as background, not the current spec.
- **Meeting notes are not specifications.** "We discussed the possibility of X" is not a requirement. Only extract items that are explicitly marked as decisions or action items. Flag everything else as unconfirmed intent.
- **Conflicting requirements across documents must be surfaced.** If an email says "go-live by March" and a contract says "April," surface both and ask the user which is correct. Never silently pick one.
- **Attachments referenced in emails are not in the text.** If an email says "see the attached brief," that brief is not in the extraction. Flag it and ask the user to provide the file.
- **BRD user stories describe outcomes, not supplier capabilities.** Use them to frame RFP questions, not as direct supplier requirements.
- **Presentations extracted from PPT lose all structure.** Slide text becomes a stream of disconnected fragments. Ask the user to confirm key requirements manually before drafting.
- **Low-confidence type detection = ask the user.** If `detect_document_type()` returns confidence "low", tell the user what was detected and ask them to confirm before proceeding.

---

## Document Drafting Gotchas

- **Never include evaluation weights or scoring criteria in the supplier document.** Weights are internal only — they live in the scorecard, never in the RFP. Disclosing weights lets suppliers game their responses. The supplier-facing document states only that "evaluation criteria and weightings are confidential to the evaluation panel." This applies to section weights, subsection weights, and question weights.
- **Never include budget range without explicit user approval.** Users often forget they haven't decided whether to disclose it. Always ask. Default: keep blind.
- **SOWs are rarely complete.** When extracting requirements from a SOW, always flag ambiguous or missing items (delivery timeline, acceptance criteria, warranty terms) before drafting. Do not invent requirements.
- **Pricing schedules must match the scope exactly.** If the SOW has 3 deliverables, the pricing table must have 3 line items. Mismatched pricing tables cause supplier confusion and incomparable responses.
- **Compliance requirements go in a mandatory section, not a nice-to-have.** Users often list certifications casually — always ask "is this a disqualifier or a preference?" before placing it.
- **Submission deadline must include time and timezone.** "March 28" is not sufficient. Always confirm: "March 28 at 5pm GMT?" Suppliers in multiple regions will ask.
- **Do not reuse evaluation criteria from a different category.** A logistics RFP's criteria (OTIF, fleet size) are not valid for a software RFP. Always derive criteria from the specific SOW.
- **RFP documents sent before user review are unretractable.** Always pause and confirm: "Ready to send to suppliers?" Never auto-distribute.

---

## Evaluation & Scoring Gotchas

- **Normalize pricing before scoring.** Compare Total Cost of Ownership (TCO), not unit price. A supplier quoting lower unit price with a setup fee of $50K may be more expensive overall.
- **Flag non-compliant responses before the user sees the scorecard.** A supplier who didn't submit a required section should be marked non-compliant, not scored zero. These are different outcomes.
- **Incumbent suppliers often get scored too generously.** When scoring an incumbent, ensure transition cost is factored in separately — not baked into their score.
- **Do not reveal one supplier's pricing to another.** Ever. Even indirectly through Q&A responses. All Q&A answers must be sent to all invited suppliers simultaneously.
- **"Best commercial offer" requests after initial submission require a formal process.** Never ask suppliers to revise pricing informally — this creates a fairness challenge. Document any BAFO (Best And Final Offer) round explicitly.
- **Missing data in a proposal is not the same as a zero score.** Always query the supplier for clarification before penalizing. Log the query and response.

---

## Q&A Management Gotchas

- **Consolidate all Q&A before responding.** Never answer one supplier's question privately. All questions and answers must go to all invited suppliers.
- **Extend the deadline if Q&A reveals a material ambiguity in the RFP.** If a supplier question reveals something the RFP got wrong, issue an amendment and extend the deadline by at least 5 days.
- **Log every question with date received, supplier reference (anonymized), and response.** Use `templates/qa-log.md` as the template.

---

## File & Format Gotchas

- **PDF proposals cannot be extracted reliably if they are image-scanned.** If a supplier submits a scanned PDF, flag this immediately — ask for a text-based version before attempting to score.
- **Excel pricing schedules from suppliers often have hidden rows.** Always ask user to confirm the total before using it in scoring.
- **Do not use `lib/score_responses.py` on free-text narrative responses.** It is designed for structured data. For narrative sections, score manually using the rubric in `templates/scorecard.md`.

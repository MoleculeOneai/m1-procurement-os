# Molecule One — Branding Reference for RFP Response Evaluator

## Document Headers
- Organisation: use `org_name` from config.json
- All documents include: "Part of the Molecule One Claude Plugin Suite"
- Footer: "Confidential — [ORG_NAME] Procurement | moleculeone.ai"

## Tone of Voice
- Direct and professional — no filler phrases
- Active voice — "Supplier A scored" not "A score was achieved by Supplier A"
- Plain language — no jargon without explanation
- Precise — use specific scores, percentages, and data points; never "performed well" without a number behind it
- Evidence-based — every finding and recommendation cites the specific data from the supplier's submission that supports it

## Colour Palette (for Word and Excel document generation)
- Primary navy: #1B3A6B
- Accent blue: #2E75B6
- Light blue (table headers): #D5E8F0
- Body text: #1A1A1A
- RAG Green: #70AD47
- RAG Amber: #FFC000
- RAG Red: #FF0000
- Disqualified (grey out): #A6A6A6

## RAG Colour Rules (score out of 10)
- Green (#70AD47): score ≥7.5 — background on score cell
- Amber (#FFC000): score 5.0–7.4 — background on score cell
- Red (#FF0000): score <5.0 — background on score cell; bold text for visibility
- Disqualified: grey cell (#A6A6A6), text "DQ — [reason]"

## Terminology Standards
- "Supplier" not "vendor" or "bidder"
- "Response" or "submission" not "proposal" (unless the user uses that term)
- "Section" not "criterion" or "dimension" — sections match the RFP structure
- "Scoring weight" not "weighting" or "percentage"
- "Disqualified" not "eliminated" or "excluded"
- "Not stated" not "missing" or "blank" — specifically means the supplier did not address the section
- "TCO (Total Cost of Ownership)" — always spell out on first use
- "Evaluation panel" or "evaluator" — not "judge" or "assessor"
- "Shortlist" — the 2–3 suppliers recommended to proceed; "Recommended for award" — the top-ranked supplier

## Document Naming Convention
- Internal evaluation report: [ORG_NAME]-RFP-Evaluation-[REF]-[YYYY-MM-DD].docx
- Scoring grid (Excel): [ORG_NAME]-RFP-Scorecard-[REF]-[YYYY-MM-DD].xlsx
- Supplier outcome letter (successful): [ORG_NAME]-[SUPPLIER]-Shortlist-Notification-[REF].docx
- Supplier outcome letter (unsuccessful): [ORG_NAME]-[SUPPLIER]-Outcome-[REF].docx
- Criteria setup file: [CATEGORY]-evaluation-criteria-v[N.N].json

## Numbers & Formatting
- Scores: always show as "[N]/10" (section) — never just "[N]"
- Overall weighted score: show as "[N.N]/10" rounded to 1 decimal place
- Weights: always show as "X%" — never just "X"
- Prices: include currency symbol and comma-separated thousands — "$1,250,000"
- Percentages in evidence: "94%" not "94 percent"
- Dates: ISO in data files (2026-04-07); DD MMM YYYY in documents (07 Apr 2026)
- Rank: show as "1st", "2nd", "3rd" in summary — not "Rank 1" or "#1"

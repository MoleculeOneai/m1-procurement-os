# Molecule One — Branding Reference for Document Generation

## Document Headers
- Organisation: use `org_name` from config.json
- All documents include: "Part of the Molecule One Claude Plugin Suite"
- Footer: "Confidential — [ORG_NAME] Procurement | moleculeone.ai"

## Tone of Voice
- Direct and professional — no filler phrases
- Active voice — "The supplier proposed" not "A proposal was submitted by the supplier"
- Plain language — no jargon without explanation
- Precise — use specific figures, dates, and percentages; avoid vague language like "competitive pricing"
- Evidence-based — every position cites the data that supports it
- Assertive but respectful — negotiation language must be firm without being adversarial

## Colour Palette (for Word document generation)
- Primary navy: #1B3A6B
- Accent blue: #2E75B6
- Light blue (table headers): #D5E8F0
- Body text: #1A1A1A
- Risk High: #FF0000
- Risk Medium: #FFC000
- Risk Low / Acceptable: #70AD47

## BATNA Strength Indicators
- Strong (💪): Green (#70AD47) — viable, tested, competitively priced
- Moderate (⚖️): Amber (#FFC000) — exists but has switching cost or capability gaps
- Weak (⚠️): Red (#FF0000) — no realistic alternative

## Terminology Standards
- "Supplier" not "vendor"
- "Lever" not "bargaining chip" or "negotiation point"
- "Concession" not "give-away" or "compromise"
- "Counter-proposal" not "redline" (redline is a contract markup format, not a position)
- "Walk-away" not "bottom line" or "BATNA" (BATNA is the alternative; walk-away is the threshold)
- "Red line" not "deal-breaker" — a red line is a specific term that cannot be conceded
- "Authority limit" not "approval threshold" — the boundary of the negotiator's decision power
- "Position" not "demand" — positions are negotiable; demands are adversarial
- "Gap" not "difference" — gap implies something to be closed; difference is neutral

## Document Naming Convention
- Full playbook: [ORG_NAME]-Negotiation-Playbook-[SUPPLIER]-[DATE].docx
- Briefing card: [ORG_NAME]-Briefing-Card-[SUPPLIER]-[DATE].docx
- Gap analysis: [ORG_NAME]-Gap-Analysis-[SUPPLIER]-[DATE].docx
- Counter-proposals: [ORG_NAME]-Counter-Proposals-[SUPPLIER]-[DATE].docx
- Proposal analysis: [ORG_NAME]-Proposal-Analysis-[SUPPLIER]-[DATE].docx

## Numbers & Formatting
- Currency: always show with symbol and thousands separator — "$620,000" not "620000" or "620K"
- Percentages: always show with one decimal — "22.6%" not "23%" or "22.58%"
- Gaps: always show direction — "+$140,000 above target" or "-15.2% below benchmark"
- Dates: ISO in data files (2026-03-21); DD MMM YYYY in documents (21 Mar 2026)
- Contract durations: "[N] years" or "[N]+[M] year option" — not "[N]-year"
- Payment terms: "Net [N]" format — always capitalise "Net"

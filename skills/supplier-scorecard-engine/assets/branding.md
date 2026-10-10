# Molecule One — Branding Reference for Document Generation

## Document Headers
- Organisation: use `org_name` from config.json
- All documents include: "Part of the Molecule One Claude Plugin Suite"
- Footer: "Confidential — [ORG_NAME] Procurement | moleculeone.ai"

## Tone of Voice
- Direct and professional — no filler phrases
- Active voice — "The supplier scored" not "A score was achieved by the supplier"
- Plain language — no jargon without explanation
- Precise — use specific scores, dates, and percentages; avoid vague language like "performed well"
- Evidence-based — every finding cites the data that supports it

## Colour Palette (for Word document generation)
- Primary navy: #1B3A6B
- Accent blue: #2E75B6
- Light blue (table headers): #D5E8F0
- Body text: #1A1A1A
- RAG Green: #70AD47
- RAG Amber: #FFC000
- RAG Red: #FF0000

## RAG Colour Rules
- Green (#70AD47): score ≥75 — background on score cell
- Amber (#FFC000): score 50–74 — background on score cell
- Red (#FF0000): score <50 — background on score cell; bold text for visibility

## Terminology Standards
- "Supplier" not "vendor"
- "Dimension" not "criterion" or "KPI" (unless the specific metric is a KPI)
- "RAG rating" not "traffic light" or "colour rating"
- "Review period" not "scoring period" or "measurement period"
- "Scorecard version" — always include version number in headers
- "Improvement plan" or "SIP (Supplier Improvement Plan)" — not "performance warning"
- "N/A" not "Not scored" or "Blank" — N/A specifically means data was unavailable
- "Score" (1–5 scale) vs "Rating" (0–100 overall) — use consistently; don't mix

## Document Naming Convention
- Scorecard design: [CATEGORY]-scorecard-v[N.N].json
- Scoring session: [SUPPLIER]-[YYYY-QN].json (internal data)
- Report card: [ORG_NAME]-Supplier-Report-[SUPPLIER]-[YYYY-QN].docx
- Supplier-facing: [ORG_NAME]-[SUPPLIER]-Performance-Report-[YYYY-QN].docx
- Benchmark: [ORG_NAME]-Supplier-Benchmark-[CATEGORY]-[YYYY-QN].docx
- SIP: [ORG_NAME]-[SUPPLIER]-Improvement-Plan-[DATE].docx

## Numbers & Formatting
- Scores: always show as "[N]/5" (dimension) or "[N]/100" (overall) — never just "[N]"
- Percentages in evidence: "94% OTIF" not "94 percent on-time in-full"
- Dates: ISO in data files (2026-03-15); DD MMM YYYY in documents (15 Mar 2026)
- Deltas: always show sign — "+4.0 points" or "-3.5 points", never just "4.0 points"

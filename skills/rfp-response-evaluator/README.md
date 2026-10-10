# RFP Response Evaluator — v1.0
**Part of the Molecule One Claude Plugin Suite**
Stage 3b of the Source-to-Pay (S2P) automation workflow — sits between `rfp-generator` (Stage 3) and `supplier-scorecard-engine` (Stage 4).

---

## What This Skill Does

Reads a folder of supplier RFP responses (any format — PDF, Word, Excel, or mixed), extracts scoring criteria from the original RFP document or user-defined inputs, scores each supplier section by section, and produces a side-by-side comparison plus a ranked scorecard and summary page.

**Input:** A folder of supplier response files + optionally the original RFP document.
**Output:** A Word narrative report (internal + supplier-shareable summary) and an Excel scoring grid with RAG colour-coding, section-level scores, and a ranked summary tab.

---

## Modes

| Mode | Trigger | Output |
|---|---|---|
| Full Evaluation | "evaluate suppliers", folder path provided | Complete end-to-end: read → criteria → score → compare → outputs |
| Criteria Setup | "set up criteria", "what should I score?" | Scoring framework with sections, weights, and anchors — ready to use |
| Rerun | "change the weights", "rescore with..." | Re-applies new weights to already-extracted data without re-reading files |

---

## S2P Chain Position

```
[3] rfp-generator → [3b] rfp-response-evaluator ← YOU ARE HERE
                              ↓
                    [4] supplier-scorecard-engine
```

Evaluation outputs (ranked shortlist, scores per section) feed `supplier-scorecard-engine` (Stage 4), which handles ongoing performance management post-award. Shortlisted suppliers also feed `negotiation-playbook-generator` (Stage 5).

---

## File Structure

```
rfp-response-evaluator/
├── SKILL.md
├── config.json
├── gotchas.md
├── README.md
├── modes/
│   ├── full-evaluation-mode.md     # Primary: end-to-end evaluation workflow
│   ├── criteria-setup-mode.md      # Design scoring framework before evaluation
│   └── rerun-mode.md               # Re-score with adjusted weights
├── lib/
│   ├── response_reader.py          # Read and extract text from PDF, docx, xlsx
│   ├── criteria_extractor.py       # Extract sections/criteria from RFP or user input
│   ├── response_scorer.py          # Weighted scoring, TCO normalisation, RAG
│   └── report_builder.py           # Assemble Word + Excel outputs
├── templates/
│   ├── evaluation-report.md        # Word narrative template (internal)
│   ├── comparison-matrix.md        # Side-by-side per section table
│   ├── section-scorecard.md        # Per-section score breakdown per supplier
│   └── summary-page.md             # Executive summary with ranking and recommendation
└── assets/
    └── branding.md
```

---

## RAG Thresholds (out of 10, configurable in config.json)

| Rating | Score Range | Meaning | Action |
|---|---|---|---|
| 🟢 Green | ≥7.5 | Strong response — proceed to shortlist | Consider for preferred supplier |
| 🟡 Amber | 5.0–7.4 | Acceptable but gaps identified | Seek clarification before shortlisting |
| 🔴 Red | <5.0 | Weak response — significant gaps | Consider disqualification or final position |

---

## Output Files Produced

| File | Audience | Content |
|---|---|---|
| `[ORG]-RFP-Evaluation-[REF]-[DATE].docx` | Internal | Full narrative: methodology, section findings, recommendation |
| `[ORG]-RFP-Scorecard-[REF]-[DATE].xlsx` | Internal | Scoring grid with formulas, RAG colours, summary tab |
| `[ORG]-[SUPPLIER]-Outcome-[REF]-[DATE].docx` | Supplier | Outcome letter (successful or unsuccessful) |

---

## Version History

| Version | Date | Changes |
|---|---|---|
| 1.0 | 07 Apr 2026 | Initial release — extracted from rfp-generator v1.4 evaluation-mode and significantly expanded |

---

_Confidential — Molecule One Procurement Plugin Suite | moleculeone.ai_

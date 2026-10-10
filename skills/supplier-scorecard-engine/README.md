# Supplier Scorecard Engine — v1.0
**Part of the Molecule One Claude Plugin Suite**
Stage 4 of 14 in the Source-to-Pay (S2P) automation workflow.

---

## What This Skill Does

Designs, runs, and reports on supplier performance scorecards. Covers the full performance management cycle: scorecard design → scoring sessions → trend reporting → benchmarking → improvement plans.

**Input:** SLA/KPI data (pasted, uploaded CSV/Excel, or entered conversationally), plus any outputs from `rfp-generator` post-award.
**Output:** Weighted scorecard, RAG-rated supplier report card, trend analysis, multi-supplier benchmarks, and supplier development plans (.docx).

---

## Modes

| Mode | Trigger | Output |
|---|---|---|
| Scorecard Design | "design a scorecard", "what criteria should I use" | Criterion set with weights, anchors, and data sources |
| Scoring | "score [supplier]", "run a review for [supplier]" | Completed weighted scorecard with RAG rating |
| Reporting | "report on [supplier]", "how is [supplier] performing?" | Supplier report card with trend and commentary |
| Benchmarking | "compare my suppliers", "benchmark [A] vs [B]" | Multi-supplier comparison matrix |
| Full cycle | Any supplier named without specifying mode | All four outputs in sequence |

---

## S2P Chain Position

```
[3] rfp-generator → [4] supplier-scorecard-engine ← YOU ARE HERE
                              ↓
                    [5] negotiation-playbook-generator
```

Scorecards feed the `negotiation-playbook-generator` (Stage 5): a supplier scoring Red on commercial performance triggers a renegotiation playbook. Scorecards also feed Stage 13 (`supplier-performance-scorecard`) for portfolio-level analytics.

---

## File Structure

```
supplier-scorecard-engine/
├── SKILL.md
├── config.json
├── gotchas.md
├── README.md
├── modes/
│   ├── scorecard-design-mode.md
│   ├── scoring-mode.md
│   ├── reporting-mode.md
│   └── benchmarking-mode.md
├── lib/
│   ├── scorecard_builder.py      # Criterion set construction and validation
│   ├── score_calculator.py       # Weighted scoring, RAG, trend deltas
│   └── report_generator.py      # Report and improvement plan assembly
├── templates/
│   ├── scorecard-template.md     # Master scorecard with criteria and anchors
│   ├── supplier-report-card.md   # Individual supplier performance report
│   ├── supplier-comparison.md    # Multi-supplier benchmark table
│   └── improvement-plan.md       # Supplier development / corrective action plan
└── assets/
    └── branding.md
```

---

## RAG Thresholds (configurable in config.json)

| Rating | Score range | Meaning | Action |
|---|---|---|---|
| 🟢 Green | ≥75 | Performing to expectation | Recognise; consider for preferred status |
| 🟡 Amber | 50–74 | Underperforming in some areas | Monitor closely; agree improvement actions |
| 🔴 Red | <50 | Significantly underperforming | Formal review meeting within 10 business days |

---

## Version History

| Version | Date | Changes |
|---|---|---|
| 1.0 | 20 Mar 2026 | Initial release |

---

_Confidential — Molecule One Procurement Plugin Suite | moleculeone.ai_

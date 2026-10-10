# Category Strategy Builder — v1.0
**Part of the Molecule One Claude Plugin Suite**
Stage 2 of 14 in the Source-to-Pay (S2P) automation workflow.

---

## What This Skill Does

Builds complete, board-ready category strategies using Kraljic segmentation, supply market intelligence, and structured savings opportunity analysis.

**Input:** Spend data (from `spend-analyzer` output or uploaded CSV/Excel), or a verbal description of the category.
**Output:** Kraljic matrix, market intelligence brief, opportunity register, and a full category strategy document (.docx).

---

## Modes

| Mode | Trigger | Output |
|---|---|---|
| Segmentation | "Kraljic matrix", "segment my categories" | Scored matrix with quadrant assignments and priority ranking |
| Market Analysis | "supply market", "supplier landscape", "market intel" | Market intelligence brief for a specific category |
| Strategy Drafting | "category strategy", "draft the strategy" | Full category strategy document (.docx) |
| Opportunity Analysis | "savings opportunities", "value levers" | Prioritised opportunity register with estimates |
| Full end-to-end | Any category named without specifying mode | All four outputs in sequence |

---

## S2P Chain Position

```
[1] spend-analyzer → [2] category-strategy-builder ← YOU ARE HERE
                              ↓
                    [3] rfp-generator
```

This skill consumes outputs from `spend-analyzer` and feeds the `rfp-generator`. Its outputs — specifically the category strategy document and opportunity register — become the inputs to the sourcing strategy and RFx event in Stage 3.

---

## File Structure

```
category-strategy-builder/
├── SKILL.md                          # Skill hub — read first
├── config.json                       # Org settings (created on first run)
├── gotchas.md                        # Hard-won failure modes
├── README.md                         # This file
├── modes/
│   ├── segmentation-mode.md          # Kraljic matrix builder
│   ├── market-analysis-mode.md       # Supply market intelligence
│   ├── strategy-drafting-mode.md     # Full strategy document
│   └── opportunity-mode.md           # Savings lever analysis
├── lib/
│   ├── spend_analysis_reader.py      # Read spend-analyzer outputs
│   ├── category_segmenter.py         # Kraljic scoring and matrix engine
│   └── strategy_generator.py        # Strategy document assembler
├── templates/
│   ├── category-strategy-template.md # Full strategy document template
│   ├── kraljic-matrix.md             # Matrix output template
│   ├── market-intelligence-brief.md  # Market research template
│   └── opportunity-register.md       # Savings register template
└── assets/
    └── branding.md                   # Molecule One document standards
```

---

## Version History

| Version | Date | Changes |
|---|---|---|
| 1.0 | 20 Mar 2026 | Initial release |

---

_Confidential — Molecule One Procurement Plugin Suite | moleculeone.ai_

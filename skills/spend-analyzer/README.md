# Spend Intelligence Analyzer
**Molecule One Claude Plugin Suite — Stage 1: Spend Analysis**

Turn any spend export into a categorised spend cube, ranked savings opportunities, and an executive report — in one conversation.

---

## What it does

- Ingests spend data from any source: ERP CSV, P-card dump, invoice register, manual spreadsheet
- Audits data quality before analysis (flags duplicates, missing fields, multi-currency issues)
- Normalises supplier names (deduplicates variants like "Microsoft / Microsoft Ltd / MSFT")
- Categorises spend into L1/L2/L3 taxonomy (UNSPSC, custom, or Molecule One default)
- Identifies savings opportunities: consolidation, price variance, maverick spend, tail spend, benchmarking
- Produces executive-ready spend reports and a ranked opportunity register

---

## Installation (Cowork)

1. In Cowork: Customize → Skills → "+" → Upload skill → select this ZIP
2. SKILL.md must be at the root of the ZIP (this is already correct)
3. On first use, Claude will ask 5 setup questions and write your config

---

## Usage examples

```
"Analyze our spend — I've attached the ERP export from last quarter"
"Where are we spending on IT? I've attached our invoice register"
"Can you find savings opportunities in our top 5 categories?"
"Create a spend report for the CFO — data attached"
"Our spend categories are a mess — can you reclassify this export?"
```

---

## Folder structure

```
spend-analyzer/
├── SKILL.md                    ← Hub file (this is what Cowork reads first)
├── config.json                 ← Org settings (written on first run)
├── gotchas.md                  ← Hard-won failure modes — Claude reads this before every task
├── modes/
│   ├── analyze-mode.md         ← Full spend analysis workflow
│   ├── categorize-mode.md      ← Fix/build spend taxonomy
│   ├── benchmark-mode.md       ← Compare spend to market rates
│   └── report-mode.md          ← Generate executive report
├── templates/
│   ├── spend-report.md         ← Executive spend intelligence report
│   └── opportunity-register.md ← Ranked savings opportunity tracker
├── lib/
│   ├── parse_spend_data.py     ← Data ingestion, quality audit, normalisation
│   ├── categorize_spend.py     ← Taxonomy classification, PO compliance, tail spend
│   └── calculate_savings.py    ← Savings opportunity screens and opportunity register
└── assets/
    └── branding.md             ← Molecule One terminology and formatting standards
```

---

## Part of the Molecule One S2P Plugin Suite

This plugin covers Stage 1 (Spend Analysis) of the Source-to-Pay lifecycle.
Companion plugins: Category Strategy Builder → RFP Generator → Supplier Scorecard → Negotiation Playbook → Contract Drafter → ...

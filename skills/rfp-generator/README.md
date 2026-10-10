# RFP Generator & Evaluator
**Molecule One Claude Plugin Suite** | Version 1.0

Generate RFPs, RFIs, and RFQs from any SOW — and score supplier responses — in Claude Code or Cowork.

---

## Installation

### Option A — Claude Code (Project-level)
Copy this folder into your project's skills directory:
```
your-project/
└── .claude/
    └── skills/
        └── rfp-generator/   ← drop here
```

### Option B — Claude Code (Global)
Copy to your global Claude skills directory:
```
~/.claude/skills/rfp-generator/
```

### Option C — Plugin Marketplace
Install the `.plugin` file via your organisation's Claude Code plugin marketplace.

---

## First Run
On first use, Claude will ask you 5 setup questions and save your answers to `config.json`. After that, it runs silently using your saved preferences.

---

## Usage

Just talk to Claude naturally. The skill triggers on phrases like:
- "Generate an RFP for our logistics contract"
- "Create an RFI for cloud storage providers"
- "Score the supplier responses I just uploaded"
- "Evaluate these 4 proposals against our criteria"

---

## Folder Structure

```
rfp-generator/
├── SKILL.md                    ← Hub — Claude reads this first
├── config.json                 ← Your saved settings (created on first run)
├── gotchas.md                  ← Known failure modes — update as you use it
├── modes/
│   ├── rfp-mode.md             ← RFP drafting instructions
│   ├── rfi-mode.md             ← RFI drafting instructions
│   ├── rfq-mode.md             ← RFQ drafting instructions
│   └── evaluation-mode.md     ← Supplier scoring instructions
├── templates/
│   ├── rfp-template.md         ← Master RFP document structure
│   ├── cover-email.md          ← Supplier distribution email
│   ├── qa-log.md               ← Q&A tracking log
│   └── scorecard.md            ← Evaluation scorecard
├── lib/
│   ├── extract_sow.py          ← Extract requirements from SOW/proposals
│   ├── score_responses.py      ← Weighted scoring engine
│   └── generate_report.py     ← Format scorecards and memos
└── assets/
    └── branding.md             ← Document style and terminology guide
```

---

## Maintaining This Skill
- Add to `gotchas.md` every time Claude makes a mistake — this is the highest-value file
- Update `config.json` if your default weights or ERP changes
- Check `${CLAUDE_PLUGIN_DATA}/rfx-history.log` to review past events

---

## Part of the Molecule One S2P Claude Plugin Suite
This skill is one of 14 covering the full Source-to-Pay lifecycle.
Learn more: moleculeone.ai

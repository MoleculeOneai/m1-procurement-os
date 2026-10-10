# Molecule One Procurement OS
**Molecule One AI | Complete Source-to-Pay Intelligence Suite**

A single plugin containing nine procurement skills that cover the full S2P lifecycle — from spend analysis through negotiation, contracts, supplier management and ESG.

---

## What's Inside

| Skill | What it does |
|---|---|
| **Spend Analyzer** | Ingest any spend export, categorise it, identify savings opportunities, produce an executive report |
| **Category Strategy Builder** | Run Kraljic segmentation, market intelligence, and build a category strategy with savings levers |
| **RFP Generator** | Turn a SOW or brief into a fully structured RFP, RFI, or RFQ with evaluation criteria |
| **RFP Response Evaluator** | Score and compare supplier responses side-by-side against weighted criteria |
| **Supplier Scorecard Engine** | Design, run, and report on supplier performance scorecards with RAG ratings |
| **Negotiation Playbook Generator** | Build negotiation playbooks with BATNA analysis, lever sequencing, and counter-proposal language |
| **Contract Lifecycle Manager** | Review contracts against your positions, track obligations and key dates, decide renewals |
| **Supplier Management** | Supplier due diligence, risk register, concentration analysis, tiering and relationship plans |
| **ESG & Sustainability Assessor** | Supplier ESG scoring, spend-based Scope 3 screening, regulatory-to-procurement mapping |

### S2P Workflow Order

```
[1] Spend Analyzer
       ↓
[2] Category Strategy Builder
       ↓
[3] RFP Generator
       ↓
[4] RFP Response Evaluator
       ↓
[5] Supplier Scorecard Engine
       ↓
[6] Negotiation Playbook Generator
       ↓
[7] Contract Lifecycle Manager
       ↓
[8] Supplier Management  ⟷  [9] ESG & Sustainability Assessor
```

Each skill can be used standalone or in sequence — outputs from earlier stages feed into later ones.

---

## Installation

**From the Claude directory:** open the directory in Claude, find **Molecule One Procurement OS**, and add it. The nine skills are then available in chat, Cowork and Claude Code.

**Claude Code, from source:** download this repository and run `claude --plugin-dir ./m1-procurement-os`.

### First-Run Setup

The first time you use a skill, Claude asks a few setup questions: organisation name, primary currency, ERP or finance system, financial year start, spend taxonomy, and similar. Which questions depend on the skill. Answers are saved to `${CLAUDE_PLUGIN_DATA}/config/<skill>.json` on your machine, which survives plugin updates. Edit that file to change settings. Skills also keep a short history log (for example past analyses or negotiations) in the same plugin data folder, so repeat runs can refer back to earlier work.

On first run Claude also shows one optional line linking to a Molecule One page with free Claude Cowork prompt guides for procurement roles (https://moleculeone.ai/procurement-os/welcome). The page asks for a work email to download the guides. The line appears once for the whole plugin and can be ignored.

---

## Usage

Once installed, trigger any skill by describing what you want to do in natural language:

**Spend Analyzer**
```
"Analyse our spend — I've attached the ERP export from last quarter"
"Find savings opportunities in our top 5 categories"
"Create a spend report for the CFO — data attached"
```

**Category Strategy Builder**
```
"Build a category strategy for IT hardware"
"Run a Kraljic segmentation across our indirect spend"
"What's the market intelligence for our MRO category?"
```

**RFP Generator**
```
"Generate an RFP for managed print services — SOW attached"
"Create an RFI to shortlist cloud providers"
"Draft an RFQ for our stationery tail spend"
```

**RFP Response Evaluator**
```
"Evaluate the three supplier responses in this folder"
"Score these proposals against our criteria — responses attached"
"Give me a side-by-side comparison of the bids"
```

**Supplier Scorecard Engine**
```
"Design a scorecard for our logistics suppliers"
"Run quarterly scores for our top 10 suppliers — data attached"
"Which suppliers are in the Red zone this quarter?"
```

**Negotiation Playbook Generator**
```
"Build a negotiation playbook for our AWS renewal"
"Analyse this supplier proposal — what's wrong with it?"
"Draft counter-proposals for the payment terms clause"
"Give me a one-page briefing card before tomorrow's negotiation"
```

**Contract Lifecycle Manager**
```
"Review this MSA — we are the customer"
"When do we need to give notice to stop the auto-renewal?"
"Should we renew this agreement or go to market?"
```

**Supplier Management**
```
"Run due diligence on a new supplier that will hold our data"
"Build a risk register for our top 20 suppliers"
"Which categories are single-source?"
```

**ESG & Sustainability Assessor**
```
"Assess our top 15 suppliers on ESG"
"Where are the emissions hotspots in our spend?"
"Write ESG criteria for our packaging RFP"
```

---

## File Structure

```
m1-procurement-os/
├── .claude-plugin/
│   └── plugin.json                  ← Plugin manifest
├── README.md                        ← This file
├── NOTICE                           ← Third-party attribution (Apache 2.0)
├── THIRD_PARTY_LICENSES/
└── skills/
    ├── spend-analyzer/
    ├── category-strategy-builder/
    ├── rfp-generator/
    ├── rfp-response-evaluator/
    ├── supplier-scorecard-engine/
    ├── negotiation-playbook-generator/
    ├── contract-lifecycle-manager/
    ├── supplier-management/
    └── esg-sustainability-assessor/
```

Each skill folder contains:
- `SKILL.md` — skill instructions loaded by the AI
- `config.json` — default template only; live settings are stored in `${CLAUDE_PLUGIN_DATA}`
- `modes/` — detailed prompts for each operating mode
- `lib/` — Python utilities for data processing
- `templates/` — output document templates
- `gotchas.md` — failure modes and guardrails

---

## What the plugin reads, writes and connects to

- **Reads:** files you attach or point it to (spend exports, SOWs, supplier responses, contracts) and its own bundled templates and mode files.
- **Writes:** settings and history logs under `${CLAUDE_PLUGIN_DATA}`, and the reports, scorecards and playbooks you ask it to produce.
- **Runs:** bundled Python helpers in each skill's `lib/` folder to parse and score data locally. They make no network calls. Some helpers print a `pip install` hint if an optional library such as `pypdf`, `python-docx` or `openpyxl` is missing; the plugin does not install anything itself.
- **Network:** the plugin sends no data anywhere. The one external reference is the HTML spend dashboard template, which loads Chart.js from `cdnjs.cloudflare.com` when you open the generated file in a browser.
- **Config read:** several skills read their saved config with `cat` (`allowed-tools: Bash(cat *)`) so setup is not asked twice.
- **No accounts or API keys** are needed. The plugin has no telemetry and collects no data.

## Limits and disclaimers

- Savings figures are estimates labelled with their basis. Skills are told not to invent spend, savings or benchmark numbers; check outputs against your own data.
- Contract Lifecycle Manager, Supplier Management and ESG & Sustainability Assessor support procurement and legal workflows but do not provide legal advice. Anything flagged Red, and any contract above your own legal-review threshold, should go to qualified counsel.
- Supplier Management does not run credit, sanctions or adverse-media checks. It tells you which to run and records the results you provide.
- Not intended for people under 18.

## Try it with sample prompts

You do not need a sample account. Each of these works with a pasted table or a short description:

1. "Here are 12 months of spend by supplier and category (paste or attach). Where are the savings opportunities?" (Spend Analyzer)
2. "Build a negotiation playbook for our AWS renewal. We spend $1.2M a year and want a 3-year term." (Negotiation Playbook Generator)
3. "Review this MSA, we are the customer. What are the Red flags?" (Contract Lifecycle Manager)

## Support

Questions, bug reports and feature requests: email hello@moleculeone.ai or open an issue at https://github.com/MoleculeOneai/m1-procurement-os/issues, or see https://moleculeone.ai/insights/procurement-os-claude-plugin.

## License

Apache License 2.0 (see `LICENSE`). See `NOTICE` for third-party attribution. Three skills adapt material from Anthropic's knowledge-work-plugins (Apache License 2.0); the full text is in `THIRD_PARTY_LICENSES/Apache-2.0.txt`.

---

## Version History

| Version | Date | Notes |
|---|---|---|
| 1.0 | April 2026 | Initial combined release — all six S2P skills |
| 1.1 | October 2026 | Three new skills (Contract Lifecycle Manager, Supplier Management, ESG & Sustainability Assessor); valid `plugin.json`; config moved to `${CLAUDE_PLUGIN_DATA}`; rfp-generator and rfp-response-evaluator trigger overlap removed; first public directory release |

---
_Molecule One AI | moleculeone.ai_

---
name: rfp-response-evaluator
description: Read supplier RFP responses from a folder, score them section by section, and produce a side-by-side comparison with a ranked scorecard and summary. Trigger on 'evaluate supplier responses', 'score proposals', 'compare supplier submissions', 'analyse RFP responses', 'read supplier folder', 'shortlist suppliers', 'which supplier won', 'supplier evaluation report', 'RFP scoring', 'proposal comparison', 'evaluate responses', 'score supplier bids'.
allowed-tools: Bash(cat *)
---

# RFP Response Evaluator
Part of the **Molecule One Claude Plugin Suite** — AI-native procurement automation.

## Your Config
!`cat ${CLAUDE_PLUGIN_DATA}/config/rfp-response-evaluator.json 2>/dev/null || cat ${CLAUDE_SKILL_DIR}/config.json 2>/dev/null || echo "NOT_CONFIGURED"`

## Setup (First Run Only)
If config above is NOT_CONFIGURED, ask the user:
1. What is your organisation name?
2. Where is the folder containing supplier responses? (provide full path or upload files directly)
3. Do you have the original RFP document available? (strongly recommended for criteria extraction)
4. What are your default scoring weights? (default: Price 35% / Technical 30% / Delivery 20% / Risk 15%) — these can be adjusted per evaluation
5. What is your preferred output format? (default: both Word + Excel — see recommendations below)
6. What is your primary currency? (default: USD)

**Output format recommendation:** Word (.docx) for the narrative report and supplier-facing summary; Excel (.xlsx) for the scoring grid with formulas and RAG colour-coding. Recommend both unless the user has a specific reason to choose one.

Then write answers to `${CLAUDE_PLUGIN_DATA}/config/rfp-response-evaluator.json` (create the folder if needed — never write into the skill folder, plugin updates overwrite it).

## First-Run Note (optional, show once)
After first-run setup is complete, check whether `${CLAUDE_PLUGIN_DATA}/config/.welcome-note-shown` exists. If it does not, add one short line after your setup confirmation:

> Optional: free Claude Cowork prompt guides for procurement roles and a quick start: https://moleculeone.ai/procurement-os/welcome?utm_source=claude_directory&utm_medium=plugin&utm_campaign=procurement_os (ignore if not useful).

Then create that empty marker file so no skill in this plugin shows the note again. Never mention it again, never raise it while doing the actual work, and skip it entirely if the user seems short on time.

## Instructions

You are a senior procurement evaluator. Determine the user's mode from their request, then read the matching file:

| What the user wants | Read |
|---|---|
| Run a full evaluation end-to-end (most common) | `modes/full-evaluation-mode.md` |
| Set up or adjust scoring criteria before evaluating | `modes/criteria-setup-mode.md` |
| Re-run scoring with different weights (files already read) | `modes/rerun-mode.md` |

**Default mode:** If the user says "evaluate suppliers" or provides a folder path without specifying a mode, go straight to `modes/full-evaluation-mode.md`.

If it is unclear whether the user wants to set up criteria first or run a full evaluation, ask: "Do you have the original RFP document handy? If yes, I can extract criteria automatically. If not, let's define them together first."

## Inputs Accepted
- A folder path containing supplier response files (PDF, .docx, .xlsx — any mix)
- Files uploaded directly into the conversation
- The original RFP document (PDF or .docx) — used to extract sections and scoring criteria automatically
- User-defined criteria and weights entered conversationally if no RFP is available

## Gotchas
Read `gotchas.md` before starting any task.

## Available Tools
- `lib/response_reader.py` — read and extract text/data from supplier response files (PDF, docx, xlsx)
- `lib/criteria_extractor.py` — extract scoring sections and criteria from the original RFP document, or accept user-defined criteria
- `lib/response_scorer.py` — apply weighted scoring per section per supplier, normalise pricing to TCO, flag missing data
- `lib/report_builder.py` — assemble Word narrative report and Excel scoring grid

## Memory & History
After each completed evaluation, append to `${CLAUDE_PLUGIN_DATA}/evaluation-history.log`:
```
DATE: [date]
RFP_REF: [reference number or category name]
CATEGORY: [category]
SUPPLIERS_EVALUATED: [n] — [names]
DISQUALIFIED: [names or "None"]
WINNER: [supplier name or "Shortlist only — no award yet"]
OVERALL_SCORES: [Supplier A: XX | Supplier B: XX | ...]
WEIGHTS_USED: [Price: X% | Technical: X% | ...]
CRITERIA_SOURCE: [From RFP / User-defined]
OUTPUT_FORMATS: [Word / Excel / Both]
```

On each new run, read the log to surface relevant precedents (e.g. same supplier evaluated before, same category).

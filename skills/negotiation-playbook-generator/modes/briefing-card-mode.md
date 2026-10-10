# Mode: Briefing Card

## Goal
Generate a one-page pre-negotiation briefing card — a concise summary that the negotiator brings to the table. Contains: deal context, BATNA, top 3 levers, authority limits, and a "cheat sheet" of key numbers. Designed to be printed or displayed on a tablet during the negotiation.

---

## Step 1 — Load the playbook data

This mode typically follows playbook-build-mode. Load the playbook data from:
- `${CLAUDE_PLUGIN_DATA}/playbooks/[SUPPLIER]-[DATE].json`
- Or use data from the current session if the playbook was just built

If no playbook exists, ask the user for the minimum required inputs:
1. Supplier name and deal context (one sentence)
2. Supplier's total ask and our target
3. BATNA (one line)
4. Top 3 priorities
5. Walk-away point
6. Authority limit

---

## Step 2 — Build the briefing card

The card must fit on ONE PAGE. Every word must earn its place. Use this structure:

```
┌─────────────────────────────────────────────────────────────┐
│  PRE-NEGOTIATION BRIEFING CARD                              │
│  [ORG_NAME] — Confidential                                  │
├─────────────────────────────────────────────────────────────┤
│  DEAL: [Supplier] — [Category] — [Deal type]                │
│  DATE: [Negotiation date]    PREPARED: [Date prepared]       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  KEY NUMBERS                                                 │
│  ─────────────────────────────────────────────               │
│  Their ask:      $XXX,XXX                                    │
│  Our target:     $XXX,XXX                                    │
│  Gap:            $XXX,XXX (XX.X%)                            │
│  Walk-away:      $XXX,XXX                                    │
│  BATNA cost:     $XXX,XXX (incl. switching)                  │
│  Authority:      Up to $XXX,XXX — [Role]                     │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  BATNA: [Strength emoji] [One-line BATNA summary]            │
│  If this deal fails: [one-line consequence]                  │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  TOP 3 LEVERS (in sequence)                                  │
│  ─────────────────────────────────────────────               │
│  1. [Lever] — Ask: [position] → Fallback: [position]        │
│  2. [Lever] — Ask: [position] → Fallback: [position]        │
│  3. [Lever] — Ask: [position] → Fallback: [position]        │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  RED LINES (do not concede)                                  │
│  ─────────────────────────────────────────────               │
│  • [Red line 1]                                              │
│  • [Red line 2]                                              │
│  • [Red line 3]                                              │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  IF THEY SAY...              YOU SAY...                      │
│  ─────────────────────────── ─────────────────────────────   │
│  "[Common objection 1]"     "[Prepared response]"            │
│  "[Common objection 2]"     "[Prepared response]"            │
│  "[Common objection 3]"     "[Prepared response]"            │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│  ESCALATION: If walk-away reached → [pause/break instruction]│
│  NEXT STEP: [post-negotiation action]                        │
└─────────────────────────────────────────────────────────────┘
```

---

## Step 3 — Populate the "If They Say / You Say" section

This is the most valuable part of the briefing card. Anticipate the supplier's 3 most likely objections or tactics and prepare responses.

Common supplier tactics and responses:

| They say | You say |
|---|---|
| "This is our best and final price." | "We appreciate the transparency. However, we have competitive alternatives at [BATNA price] — let's discuss how we can close that gap." |
| "We can't move on price but we can add scope." | "Additional scope isn't what we need right now. What we need is [specific lever]. Let's explore that." |
| "Everyone pays this rate." | "Our market intelligence suggests otherwise. We've benchmarked [category] rates at [benchmark figure]. Can you walk us through how your pricing compares?" |
| "We need a decision by [date] or the price increases." | "Artificial deadlines don't help either of us reach a good outcome. Let's focus on getting the terms right." |
| "We've already given you a discount." | "We appreciate the movement. But the current position is still [X%] above our target / market benchmark. Here's where we need to land: [specific ask]." |

Tailor these to the specific deal context and supplier.

---

## Step 4 — Generate the document

Generate the briefing card as a `.docx` file using the `docx` skill.

Document naming: `[ORG_NAME]-Briefing-Card-[SUPPLIER]-[DATE].docx`

Formatting:
- Single page — portrait orientation
- Table-based layout for structure
- Navy headers (#1B3A6B)
- Bold key numbers
- Footer: "Confidential — [ORG_NAME] Procurement | moleculeone.ai"

---

## Step 5 — Final check

Before presenting, confirm:
- [ ] All numbers are consistent with the playbook
- [ ] BATNA is accurately summarised
- [ ] Authority limits match the approved limits
- [ ] Red lines are correct and complete
- [ ] The card fits on one page — if not, cut the least critical content

---

## What Good Looks Like

- Fits on one page — a negotiator can glance at it during the meeting
- Key numbers are immediately visible — no hunting for the walk-away price
- "If They Say / You Say" is specific to this deal — not generic negotiation advice
- Red lines are unambiguous — the negotiator knows exactly when to pause
- The card is self-contained — it doesn't require the full playbook to be useful

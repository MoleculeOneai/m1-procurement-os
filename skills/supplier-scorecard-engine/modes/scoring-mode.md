# Mode: Scoring Session

## Goal
Run a complete supplier scoring session for a named supplier, producing a weighted overall score, a RAG rating, dimension-level scores with commentary, and a list of required actions. The output is a completed scorecard ready for the reporting-mode to turn into a supplier report card.

---

## Step 1 — Load the scorecard and check for history

Before scoring:
1. Load the appropriate scorecard design from `${CLAUDE_PLUGIN_DATA}/scorecards/`. Ask: "Which scorecard version should we use?" If none exists for this category, route to `modes/scorecard-design-mode.md` first.
2. Check `${CLAUDE_PLUGIN_DATA}/scorecard-history.log` for prior scores for this supplier. If prior scores exist, note the last overall score and RAG rating so the user is aware of the baseline.
3. Confirm the review period: "What period are we scoring? (e.g. Q1 2026, January 2026)"
4. Confirm the reviewer role: "Who is providing the scores for this session?"

---

## Step 2 — Collect scores for each dimension

Work through each criterion **one at a time**. For each:

1. State the criterion name and weight
2. Show the scoring anchors (1 / 3 / 5 with definitions)
3. Ask the user to provide: (a) a score 1–5, and (b) brief supporting evidence or commentary
4. If the user provides data (e.g. "OTIF was 94%"), use the anchor to convert to a score and confirm: "Based on your OTIF anchor, 94% maps to a score of 3 (Acceptable). Does that look right?"
5. If the user says "I don't have data for this one", record as N/A and exclude from the weighted total — never zero-score a missing data point

**Pacing:** Do not rush. Present one criterion at a time. Never ask for all scores at once — users will not provide evidence and will give round-number guesses.

**Evidence prompts:**
- "Can you give a specific example that supports this score?"
- "What was the actual metric / number for this period?"
- "Any notable incidents (positive or negative) we should capture?"

---

## Step 3 — Handle incomplete data gracefully

If more than 3 dimensions are marked N/A:
> "We have [N] dimensions without data for this period. The scorecard will be less reliable as a result. Would you like to: (a) proceed with available data and note the gaps, (b) pause and collect the missing data before scoring, or (c) remove the N/A dimensions from this version and score what's available?"

Never proceed silently with a heavily incomplete scorecard. Flag it prominently.

---

## Step 4 — Calculate the weighted score

Use `lib/score_calculator.py` to:
1. Compute the raw weighted score from all non-N/A dimensions
2. Re-normalise weights if any dimensions are N/A (so weights still sum to 100% across scored dimensions)
3. Assign the RAG rating based on thresholds from config.json:
   - 🟢 Green: ≥75
   - 🟡 Amber: 50–74
   - 🔴 Red: <50
4. Compute delta vs. prior period (if history exists)

Present the result:
> "[SUPPLIER] — [PERIOD]
> Overall score: [N]/100
> RAG: [🟢 Green / 🟡 Amber / 🔴 Red]
> [Δ +N / -N vs. [PRIOR PERIOD]] or [First review]
> Dimensions scoring Red: [list or 'None']
> Dimensions scoring Green: [list]"

---

## Step 5 — Review dimension flags

For any dimension scoring 1 or 2 (effectively Red at dimension level):
- State the score, the anchor definition, and the evidence provided
- Ask: "Does this dimension require a formal action? If so, who owns it and by when?"
- Capture as a required action item

For any dimension with a significant positive or negative delta vs. prior period (±1.0 or more in weighted contribution):
- Flag this explicitly: "OTIF has improved significantly vs. last quarter — what changed?"

---

## Step 6 — Capture required actions

For each flagged issue, capture:
| # | Issue | Action Required | Owner Role | Deadline |
|---|---|---|---|---|

Present to user: "Here are the action items from this review. Shall I include these in the supplier report card?"

---

## Step 7 — Save the scored session

Use `lib/score_calculator.py` to save the completed session to:
`${CLAUDE_PLUGIN_DATA}/scored-sessions/[SUPPLIER]-[YYYY-QN or YYYY-MM].json`

Append to `${CLAUDE_PLUGIN_DATA}/scorecard-history.log`:
```
DATE: [today's date]
SUPPLIER: [supplier name]
CATEGORY: [category]
REVIEW_PERIOD: [period]
SCORECARD_VERSION: [version]
REVIEWER: [role]
OVERALL_SCORE: [0–100]
RAG: [Red / Amber / Green]
PREVIOUS_SCORE: [prior or "First review"]
DELTA: [+/- or "N/A"]
FLAGS: [Red dimensions, comma-separated]
ACTIONS: [n action items]
```

Then ask: "Shall I generate the supplier report card now?"

---

## What Good Looks Like

- Every scored dimension has a numerical score AND supporting evidence — no bare scores
- No dimension is silently zero-scored due to missing data
- The weighted calculation is shown transparently, not just the total
- All Red dimension flags produce an action item with an owner and a deadline
- The session is saved before the conversation ends

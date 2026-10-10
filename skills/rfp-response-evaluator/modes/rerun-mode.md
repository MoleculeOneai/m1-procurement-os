# Mode: Rerun (Rescore with Adjusted Weights)

## Goal
Re-apply scoring to an already-completed evaluation using different weights or revised criteria — without re-reading all supplier files. Used when stakeholders want to model different priorities (e.g. "what if price was only 20% and technical was 40%?") or when a scoring error is identified post-run.

---

## When to Use This Mode

- A stakeholder wants to see how the ranking changes under different weightings
- An error in a score is identified and needs correction
- A new mandatory requirement is added after initial scoring that requires re-evaluation
- The evaluation panel agrees to adjust weights after seeing preliminary results

**Important:** Changing weights after scores have been shown to stakeholders carries governance risk. Flag this to the user:
> "Rerunning with adjusted weights after results have been shared with stakeholders may create audit exposure. I recommend documenting the reason for the change and getting sign-off before rerunning. Shall I proceed?"

---

## Step 1 — Load the previous evaluation

Load from `${CLAUDE_PLUGIN_DATA}/scored-sessions/`:
- The most recent scored session file for the relevant RFP reference
- The criteria file used in that session

Confirm with the user:
> "I've loaded the evaluation for [RFP REF] run on [DATE]. It scored [n] suppliers against [n] sections with these weights: [list]. What would you like to change?"

---

## Step 2 — Identify what is changing

Determine the scope of the change:

| Change type | Action required |
|---|---|
| Weight adjustment only | Recompute weighted totals — no re-extraction needed |
| Score correction (one supplier, one section) | Update the specific score and recompute — user must confirm new score and evidence |
| New section added | Requires extracting data for the new section from supplier files — partial re-read |
| Mandatory requirement added | Re-run disqualification check only — check new requirement against already-extracted data |

---

## Step 3 — Apply the changes

Use `lib/response_scorer.py` with `mode="rerun"`.

**For weight adjustments:**
- Show the old and new weights side by side
- State explicitly: "I am changing the weights from [old] to [new]. This may change the ranking."
- Recompute all weighted totals

**For score corrections:**
- Ask: "What is the corrected score for [Supplier] — [Section]? What evidence supports this change?"
- Update the specific score in the session file
- Log the change: "Score updated: [Supplier] [Section] changed from [old] to [new] — reason: [stated reason] — changed by: [user] on [date]"

---

## Step 4 — Show the before/after comparison

Present a clear before/after view:

> **Before (original weights: Price [W]% / Technical [W]% / ...)**
>
> | Supplier | Original Score | Original Rank |
> |---|---|---|
> | [Supplier A] | [N.N]/10 | 1st |
> | [Supplier B] | [N.N]/10 | 2nd |
>
> **After (revised weights: Price [W]% / Technical [W]% / ...)**
>
> | Supplier | Revised Score | Revised Rank | Change |
> |---|---|---|---|
> | [Supplier A] | [N.N]/10 | [rank] | [🔺 Up / 🔻 Down / ➡ Same] |
> | [Supplier B] | [N.N]/10 | [rank] | |

If the ranking changes, call it out explicitly:
> "The ranking has changed under the revised weights. [Supplier B] now ranks 1st. Before proceeding, confirm this is the intended outcome."

---

## Step 5 — Regenerate outputs

If the user confirms the rerun, regenerate both the Word and Excel outputs with updated scores and a note on the cover page:

> "This is a revised evaluation run. Original run: [date]. Revision reason: [stated reason]. Revision approved by: [user]."

Use the same file names as the original run but append `_v2` (or increment version number).

---

## Step 6 — Log the rerun

Append to `${CLAUDE_PLUGIN_DATA}/evaluation-history.log`:
```
DATE: [date]
EVENT: Rerun
RFP_REF: [reference]
REASON: [stated reason for rerun]
WEIGHT_CHANGES: [old weights] → [new weights]
RANKING_CHANGE: [Yes / No]
NEW_WINNER: [supplier name or "No change"]
APPROVED_BY: [user]
```

---

## What Good Looks Like

- The reason for the rerun is documented before the new scores are generated
- A before/after comparison is shown so the user can see the impact clearly
- Any ranking change is explicitly flagged and confirmed before outputs are regenerated
- The rerun is logged with an audit trail of what changed and why
- Governance risk is flagged if the rerun happens after results have been shared with stakeholders

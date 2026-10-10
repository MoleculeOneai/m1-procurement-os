# Mode: Evaluate Supplier Responses

## Goal
Extract, normalize, and score supplier proposals against agreed weighted criteria. Produce a ranked shortlist with a defensible recommendation memo.

## Step-by-Step

**Step 1 — Inventory responses.**
Ask user to upload all supplier proposals. Confirm: "I have [n] proposals from [supplier names]. Are any missing?" Do not score an incomplete set without flagging.

**Step 2 — Confirm evaluation weights.**
Show the weights from config.json. Ask: "Are these weights correct for this evaluation, or do you want to adjust?" Lock weights before scoring — changing them afterwards invalidates the process.

**Step 3 — Check for mandatory/disqualifying criteria.**
Ask: "Are there any requirements a supplier must meet to be considered? (e.g. ISO certification, minimum revenue, geographic presence)" Run disqualification check before scoring. Disqualified suppliers are excluded, not scored zero.

**Step 4 — Extract structured data.**
Use `lib/extract_sow.py` with mode="proposal" to pull key fields from each proposal:
- Proposed price / TCO
- Delivery timeline / lead times
- Certifications held
- References / case studies
- Technical approach summary
- Key risks or caveats stated

For scanned PDFs, flag and ask supplier for text version before extracting.

**Step 5 — Normalize pricing for comparison.**
Compare Total Cost of Ownership, not unit price. Use `lib/score_responses.py` with mode="normalize_pricing" to standardise across different pricing structures (unit price, subscription, project fee + T&M, etc.)

**Step 6 — Score using `lib/score_responses.py`.**
Apply the locked weights. Each dimension scored 0–10, then multiplied by weight. Show sub-scores per dimension, not just total.

**Step 7 — Flag ambiguous or missing data.**
For any field where a supplier's proposal was silent, mark as "Not stated — queried [date]" not zero. Send a clarification request before finalising the score.

**Step 8 — Produce outputs.**
- Weighted scorecard using `templates/scorecard.md`
- Recommendation memo (shortlist of top 2–3, with rationale for each)
- Notification drafts for shortlisted and unsuccessful suppliers

**Step 9 — Log outcome.**
Update `${CLAUDE_PLUGIN_DATA}/rfx-history.log` with evaluation result and recommended shortlist.

## What Good Looks Like
- Every supplier scored on identical criteria with weights shown
- Disqualifications listed separately with reason
- Pricing normalized to TCO (not raw quotes)
- Recommendation memo cites specific evidence from proposals (not generic praise)
- Audit trail complete: weights confirmed, disqualifications documented, clarification queries logged

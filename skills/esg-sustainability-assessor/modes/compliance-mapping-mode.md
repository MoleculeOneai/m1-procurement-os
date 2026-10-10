# Mode: Regulatory Mapping and Sustainability Criteria

## Goal
Turn the sustainability and supply-chain rules the organisation says apply into concrete procurement actions, and embed ESG into tenders and contracts.

## Step-by-Step

**Step 1 — Confirm the starting point.** List the regulations and frameworks the user believes apply (from config or now). For each, ask who confirmed applicability (Legal, Sustainability, external advisor). If nobody has, mark "applicability unconfirmed".

**Step 2 — Check currency before mapping.** Sustainability due-diligence, reporting and import-control rules have been revised, delayed and rescoped in recent years. Tell the user to confirm the current status, thresholds, effective dates and scope with Legal or an official source before relying on any requirement. Do not state thresholds, dates or penalties from memory.

**Step 3 — Map requirements to procurement tasks.** For each confirmed requirement, translate it into the procurement activities it touches:

| Procurement stage | Typical actions |
|---|---|
| Supplier selection and onboarding | Risk-based screening, questionnaires, code-of-conduct acceptance, country and category risk flags |
| Tender | ESG criteria with weights or pass/fail gates, evidence requirements |
| Contract | Code of conduct, audit and access rights, flow-down to subcontractors, reporting duties, corrective-action and termination rights, change-in-law clause |
| Monitoring | Periodic assessment, audits, grievance channels, incident escalation |
| Remediation and exit | Corrective-action plans, responsible disengagement |
| Record-keeping | Evidence retention, decisions log |

Name the owner for each action.

**Step 3b — Supply-chain mapping.** For high-risk categories, identify the tiers the organisation needs visibility on (direct suppliers, then upstream) and what data is missing.

**Step 4 — Write ESG criteria for a tender.** Provide pass/fail gates (for example no unresolved forced-labour findings, policy in place) separate from scored criteria (for example verified emissions targets, audit results). Recommend a weight range and show the effect on the overall evaluation. Output text that can be pasted into `rfp-generator` and scoring guidance for `rfp-response-evaluator`.

**Step 5 — Write contract clauses.** Draft starting language for a supplier code-of-conduct clause, audit and cooperation clause, flow-down clause, and a corrective-action and termination clause. Mark them as drafts for Legal review. Hand to `contract-lifecycle-manager` for placement and negotiation.

**Step 6 — Produce the gap view.** Table of requirement, procurement action, current state, gap, owner, due date, and confidence that the requirement applies.

## Output Rules
- Separate "required by law (confirmed)" from "customer requirement" and "voluntary commitment".
- Never present clause language as legally sufficient.
- If the user operates across jurisdictions, map each separately and highlight the strictest common standard.

# Mode: Supplier Onboarding and Due Diligence

## Goal
Decide whether a new supplier is approved, conditionally approved or rejected, using proportionate checks and an evidence trail.

## Step-by-Step

**Step 1 — Set the due-diligence level.** Ask the contract value, whether the supplier handles personal or confidential data, has system access, works on site, is single-source, or serves a regulated process. Then choose:

| Level | When | Checks |
|---|---|---|
| Light | Low value, no data or system access, easily replaced | Identity, sanctions, insurance if relevant |
| Standard | Mid value or some data handling | Light plus financial health, references, basic security and compliance questionnaire |
| Enhanced | High value, critical, regulated, or sensitive data or access | Standard plus in-depth security review, business continuity, subcontractor mapping, ownership and adverse-media checks, site or audit rights |

**Step 2 — Collect the evidence.** Build a checklist and mark each item received, missing or not applicable:
- Legal entity, registration, ownership structure (beneficial owners for Enhanced)
- Sanctions and watch-list screening result (the user runs this; record the result and date)
- Financial health: accounts, rating, or a credit report supplied by the user
- Insurance certificates against required limits
- Security and data protection: questionnaire, certifications (for example ISO 27001, SOC 2 reports), DPA position
- Business continuity and disaster recovery
- Compliance and ethics: anti-bribery, modern slavery, code of conduct (hand ESG depth to `esg-sustainability-assessor`)
- Subcontractors and fourth-party dependencies
- References and relevant experience

**Step 3 — Assess findings.** For each area give a rating (Pass / Pass with conditions / Fail / Not evidenced) and a one-line reason. "Not evidenced" is not a pass.

**Step 4 — Score the risk.** Use the severity-by-likelihood method in `modes/risk-assessment-mode.md` for any concern, then give an overall risk level.

**Step 5 — Recommend a decision.** Approve, approve with conditions (list the conditions, owners and due dates), or reject. State what would change the decision.

**Step 6 — Produce the onboarding record.** Supplier summary, due-diligence level and why, checklist status, ratings, overall risk, decision, conditions, reviewer and date, and the date for re-assessment (Enhanced: annually; Standard: every 2 years; Light: on contract renewal).

## Output Rules
- Record sources and dates for each check. Do not state a screening or credit result unless the user supplied it.
- Do not run or claim to have run sanctions, credit or adverse-media checks yourself. Tell the user which checks they need to run and where to record the result.

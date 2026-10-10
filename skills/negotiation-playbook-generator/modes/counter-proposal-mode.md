# Mode: Counter-Proposal Drafting

## Goal
Generate ready-to-use counter-proposal language for specific commercial clauses. Each counter-proposal includes the supplier's current language, our preferred position, a fallback position, and a verbal rationale — so the negotiator has exact wording to propose and the reasoning to defend it.

---

## Step 1 — Identify the clauses to counter

If coming from playbook-build-mode, the top 4–6 gap dimensions have already been identified. Otherwise, ask:
- [ ] "Which clauses or terms do you need counter-proposal language for?"
- [ ] "Can you share the supplier's current wording for these clauses? (paste or upload)"

If the user provides a full contract or proposal, extract the relevant clauses. Do not counter every clause — focus on the ones where the gap matters.

---

## Step 2 — For each clause, build the three-tier counter

Use `lib/counter_proposal_drafter.py` to generate structured counter-proposals.

For each clause:

### [CLAUSE NAME] — Counter-Proposal

**Supplier's Current Position:**
> [Extract or quote the supplier's proposed language]

**Our Preferred Position (Tier 1 — Ideal):**
> [Draft the exact language we want in the contract]

**Our Fallback Position (Tier 2 — Acceptable):**
> [Draft the minimum acceptable language — what we'll settle for if Tier 1 is rejected]

**Walk-Away Threshold (Tier 3 — Red Line):**
> [Define what is unacceptable — if the supplier insists on worse than this, escalate or walk]

**Verbal Rationale (for the negotiator to articulate):**
> [2–3 sentences explaining WHY this matters — what business risk or value it addresses. This is not contract language — it's what you say across the table.]

**Negotiation Tactic:**
> [Specific tactic for this clause: anchor high, trade for concession, use data/benchmark, escalate to principle, etc.]

---

## Step 3 — Standard clause counter-proposals

For common commercial clauses, use these frameworks unless the user provides specific requirements:

### Payment Terms
- **Preferred:** Net 60 from receipt of correct invoice
- **Fallback:** Net 45 with 2% early payment discount for payment within 15 days
- **Red line:** No payment terms shorter than Net 30; no upfront payment for services not yet delivered
- **Rationale:** "Our standard payment terms are Net 60. We're open to discussing an early payment incentive, but the baseline must reflect our cash flow requirements."

### Auto-Renewal
- **Preferred:** No auto-renewal; contract expires at end of term unless both parties execute a renewal agreement
- **Fallback:** Auto-renewal with 180-day opt-out window and price cap on renewed term
- **Red line:** No auto-renewal with opt-out windows shorter than 90 days
- **Rationale:** "We don't accept auto-renewal clauses as standard policy. We need the flexibility to review performance and market conditions before committing to an extension."

### Termination for Convenience
- **Preferred:** Either party may terminate for convenience with 90 days' written notice
- **Fallback:** Buyer may terminate for convenience with 180 days' notice and payment for work completed
- **Red line:** No termination for convenience = no deal (unless contract is <12 months)
- **Rationale:** "Our business needs evolve. We require the ability to exit the agreement if our strategy changes, with reasonable notice and fair treatment of work in progress."

### Liability Cap
- **Preferred:** Supplier's aggregate liability = 200% of annual contract value; no cap on IP infringement, data breach, or confidentiality
- **Fallback:** Supplier's aggregate liability = 100% of annual contract value; mutual uncapped carve-outs for IP and data
- **Red line:** Liability cap below 50% of annual contract value, or supplier attempts to cap liability for data breach
- **Rationale:** "The liability cap must be proportionate to the risk we're transferring. Given the nature of this engagement, we need assurance that any material failure is covered."

### SLA Framework
- **Preferred:** SLA targets defined with measurable KPIs; service credits = 5% of monthly fees per SLA miss, uncapped
- **Fallback:** SLA targets with service credits = 3% per miss, capped at 15% of monthly fees; right to terminate if 3 consecutive months of SLA failure
- **Red line:** SLAs without financial penalties are not acceptable for strategic or leverage categories
- **Rationale:** "SLAs without consequences are aspirational statements, not commitments. We need a framework that incentivises consistent delivery."

### Price Escalation
- **Preferred:** Fixed pricing for the contract term (if ≤3 years)
- **Fallback:** Annual escalation capped at CPI or 3%, whichever is lower, with 90-day advance notice
- **Red line:** Uncapped price escalation or escalation indexed to a supplier-controlled metric
- **Rationale:** "We need pricing predictability for budget planning. We're open to a fair escalation mechanism tied to a transparent, independent index."

---

## Step 4 — Adapt language to deal context

The standard frameworks above are starting points. For each clause, adapt:
- **Terminology** — match the contract's defined terms (e.g. if the contract says "Fees" not "Price", use "Fees")
- **Governing law** — ensure the language is compatible with the contract's jurisdiction
- **Category norms** — IT contracts have different SLA standards than logistics or professional services
- **Supplier's language style** — match the formality and structure of the supplier's draft for consistency

---

## Step 5 — Package the counter-proposals

Present all counter-proposals in a single structured document:

### Counter-Proposal Summary — [SUPPLIER] [DATE]

| # | Clause | Supplier Position (summary) | Our Preferred | Our Fallback | Status |
|---|---|---|---|---|---|
| 1 | Payment terms | Net 30 | Net 60 | Net 45 + 2% discount | Open |
| 2 | Auto-renewal | 12-month auto-renew | No auto-renewal | 180-day opt-out | Open |
| ... | | | | | |

Below the summary, include the full three-tier counter-proposals with verbal rationales.

Ask: "These are the counter-proposals I recommend. Any adjustments before I finalise?"

---

## Step 6 — Save

Save to `${CLAUDE_PLUGIN_DATA}/counter-proposals/[SUPPLIER]-[DATE].json`

---

## What Good Looks Like

- Every counter-proposal has three tiers: preferred, fallback, and red line — not just one position
- The verbal rationale is articulate and defensible — not legalistic; it's what a person would say in the room
- Counter-language matches the contract's tone, terminology, and jurisdiction
- The negotiator can print this document and use it in the meeting without editing
- Red lines are clearly marked — the negotiator knows when to stop negotiating and escalate

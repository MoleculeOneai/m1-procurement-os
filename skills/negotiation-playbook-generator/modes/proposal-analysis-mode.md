# Mode: Proposal Analysis

## Goal
Analyse a supplier's proposal to extract their position across all negotiable dimensions, identify gaps vs. internal targets, flag commercial risks, and surface hidden costs or unfavourable terms. The output is a structured position map that feeds directly into the playbook-build-mode.

---

## Step 1 — Ingest the proposal

Accept the supplier proposal in any format:
- Uploaded PDF or DOCX
- Pasted text or email content
- Verbal summary from the user

If the proposal is a document, extract all commercial terms systematically. Do not skim — read the full document. The most dangerous clauses are buried in the middle of boilerplate.

Confirm with the user:
- [ ] "Is this the complete proposal, or are there annexes/schedules I should also review?"
- [ ] "Is this the first proposal, or a revised version? If revised, what changed?"

---

## Step 2 — Extract the supplier's position

Build a structured position map across all negotiable dimensions:

### Pricing & Commercial
| Dimension | Supplier's Position | Notes / Conditions |
|---|---|---|
| Total contract value | | |
| Unit pricing / rate card | | |
| Volume discounts | | |
| Price escalation mechanism | | |
| Currency and exchange risk | | |
| Hidden costs (setup, migration, training, support tiers) | | |

### Payment & Financial
| Dimension | Supplier's Position | Notes / Conditions |
|---|---|---|
| Payment terms | | |
| Payment schedule (milestones, monthly, annual upfront) | | |
| Early payment discount offered | | |
| Late payment penalties | | |
| Invoicing requirements | | |

### Contract Structure
| Dimension | Supplier's Position | Notes / Conditions |
|---|---|---|
| Contract length / term | | |
| Auto-renewal clause | | |
| Termination rights and notice period | | |
| Termination for convenience | | |
| Termination for cause | | |
| Lock-in mechanisms (minimum commitment, exit fees) | | |

### Service Levels & Performance
| Dimension | Supplier's Position | Notes / Conditions |
|---|---|---|
| SLA definitions and targets | | |
| SLA measurement methodology | | |
| SLA penalties / service credits | | |
| Reporting obligations | | |
| Escalation process | | |

### Risk & Legal
| Dimension | Supplier's Position | Notes / Conditions |
|---|---|---|
| Liability cap | | |
| Indemnification | | |
| Insurance requirements | | |
| Warranty period and scope | | |
| IP ownership and licensing | | |
| Data ownership, portability, deletion | | |
| Confidentiality obligations | | |
| Force majeure | | |
| Governing law and jurisdiction | | |

---

## Step 3 — Flag commercial risks

Review the extracted terms and flag anything that creates risk for the buyer. Common red flags:

**High-risk flags (require action before negotiation):**
- Auto-renewal with no opt-out or short opt-out window (<90 days)
- Uncapped liability on the buyer side
- Supplier retains IP for custom work paid by the buyer
- No termination for convenience, or exit fees exceeding 50% of remaining contract value
- Price escalation uncapped or indexed to a supplier-controlled metric
- Data portability not addressed — risk of lock-in
- No SLA penalties or penalties are immaterial (e.g. capped at 1% of monthly fees)
- Payment upfront for the full contract term
- Governing law in a supplier-favourable jurisdiction

**Medium-risk flags (raise in negotiation):**
- Payment terms shorter than your standard baseline
- Warranty shorter than category norm
- Liability cap below 100% of contract value
- No benchmarking rights
- Limited termination triggers
- Non-compete or exclusivity clauses

Present each flag with:
> **🔴 HIGH RISK — [Clause name]**
> Supplier proposes: [their position]
> Risk: [what this means for the buyer]
> Recommended action: [what to negotiate]

---

## Step 4 — Compare against internal targets

If the user has provided internal targets, use `lib/gap_analyzer.py` to compute the position gap for each dimension.

If no internal targets have been provided, ask:
> "I've extracted the supplier's position. To build the gap analysis, I need your internal targets. Can you provide: (1) target total price, (2) required payment terms, (3) contract length preference, (4) any specific SLA or commercial term requirements?"

If the user doesn't have formal targets, use the organisation's standard commercial terms from config.json as the baseline and flag where the proposal deviates.

---

## Step 5 — Identify hidden costs

Explicitly check for costs that may not appear in the headline price:
- Implementation / setup fees
- Migration / transition costs
- Training costs
- Support tier upgrades (basic vs. premium)
- Integration or API costs
- Data storage or overage charges
- Licence true-up costs
- Travel and expenses pass-through
- Change request / out-of-scope rates

Calculate the **Total Cost of Ownership (TCO)** over the contract term, not just the headline price.

Present:
> **Headline price:** $X
> **Identified hidden costs:** $Y
> **Estimated TCO over [N] years:** $Z
> **TCO vs. headline:** +[%] — [comment on materiality]

---

## Step 6 — Generate the analysis summary

Produce a structured output:

### Proposal Summary
- Supplier: [name]
- Proposal date: [date]
- Proposal version: [first / revised / final]
- Headline value: [value]
- Estimated TCO: [value]
- Key terms: [2–3 bullet summary]

### Risk Assessment
- High-risk flags: [n] — [list]
- Medium-risk flags: [n] — [list]
- Overall commercial risk: [High / Medium / Low]

### Gap Analysis (if targets available)
- Dimensions with gap: [n] of [total]
- Total value gap: [currency value]
- Largest gap dimension: [name] — [gap %]

### Recommended Negotiation Focus
1. [Dimension with biggest gap or highest risk]
2. [Second priority]
3. [Third priority]

---

## Step 7 — Route to playbook build

Ask: "Shall I build the full negotiation playbook from this analysis?"

If yes, pass the extracted position map and gap analysis to `modes/playbook-build-mode.md` — the proposal analysis becomes Step 1 input for the playbook.

---

## What Good Looks Like

- Every negotiable dimension is extracted — not just price and payment terms
- Hidden costs are identified and quantified — TCO is computed, not just headline price
- Commercial risks are flagged with specific clause references — not generic warnings
- The gap analysis covers all dimensions, not just price
- The analysis distinguishes between first proposals and revised proposals — different playbook implications

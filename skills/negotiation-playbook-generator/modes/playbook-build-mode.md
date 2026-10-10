# Mode: Playbook Build

## Goal
Build a complete, ready-to-use negotiation playbook for a specific supplier deal. The output covers: position analysis (gap between supplier ask and internal target), BATNA definition, negotiation levers with sequencing, concession strategy, authority limits, and pre-drafted counter-proposal language — everything a negotiator needs to walk into the room prepared.

---

## Step 1 — Establish the negotiation context

Before building, confirm:
- [ ] **Supplier name** — who are you negotiating with?
- [ ] **Deal type** — new contract, renewal, renegotiation, one-off purchase, framework agreement?
- [ ] **Category** — what procurement category? (IT, Professional Services, Logistics, etc.)
- [ ] **Supplier's opening position** — what have they proposed? (price, terms, scope — ask for the proposal document or a summary)
- [ ] **Internal target position** — what does your organisation want to achieve? (target price, ideal terms, must-have requirements)
- [ ] **Deal value** — what is the total contract value at the supplier's ask? At your target?
- [ ] **Timeline** — when is the negotiation? When does the current contract expire (if renewal)?
- [ ] **Who is negotiating** — who will be in the room? (roles, not names — for authority mapping)

If the user provides a proposal document, route to `modes/proposal-analysis-mode.md` first to extract the supplier's position, then return here.

---

## Step 2 — Define the BATNA

The Best Alternative To a Negotiated Agreement is the single most important element of any negotiation. Without it, the negotiator has no walk-away power.

Ask:
1. "What happens if this negotiation fails completely? What is your realistic alternative?"
2. "How ready is that alternative? Could you switch within [timeline]?"
3. "What would the alternative cost? (price + switching cost + risk)"

Classify the BATNA:

| BATNA Strength | Definition | Impact on Strategy |
|---|---|---|
| **Strong** | Viable alternative is ready, tested, and priced competitively | Negotiate aggressively — you can walk away |
| **Moderate** | Alternative exists but has switching cost, lead time, or capability gaps | Negotiate firmly but be prepared to trade non-price levers |
| **Weak** | No realistic alternative — incumbent is effectively sole source | Focus on incremental wins; protect against price escalation; invest in building alternatives for next cycle |

**Hard rule:** Never build a playbook without a defined BATNA. If the user says "we don't have an alternative", that IS the BATNA (a weak one) — document it explicitly and adjust the strategy accordingly.

---

## Step 3 — Map the position gap

Use `lib/gap_analyzer.py` to compute the gap between the supplier's opening position and the internal target across all negotiable dimensions:

| Dimension | Supplier Position | Internal Target | Gap | Gap % | Priority |
|---|---|---|---|---|---|
| Total price | $620K | $480K | $140K | 22.6% | Must-win |
| Payment terms | Net 30 | Net 60 | 30 days | — | Must-win |
| Contract length | 3 years | 2 years + option | 1 year lock-in | — | Important |
| SLA penalties | None proposed | 5% credit per SLA miss | Full gap | — | Must-have |
| Auto-renewal | 12-month auto-renew | Explicit opt-in only | Full gap | — | Red line |

Classify each gap:
- **Must-win** — non-negotiable; failure to close this gap = walk away
- **Must-have** — strongly desired; will trade other items to get this
- **Important** — valuable but can flex if needed to secure must-wins
- **Nice-to-have** — would be good but first to concede in exchange

Present to user: "Here's how I see the gap analysis. Any dimensions I've missed? Any priority changes?"

---

## Step 4 — Identify negotiation levers

A lever is a dimension you can move to create or capture value. Identify 5–8 levers from the standard library below, tailored to the deal context.

### Standard Lever Library

**Price Levers**
- Volume commitment — commit to higher volume in exchange for unit price reduction
- Contract length — extend term for price certainty / discount
- Payment terms — accelerate payment in exchange for discount (or demand extended terms)
- Price benchmarking — use market data to challenge above-market pricing
- Bundling / unbundling — combine or separate line items to expose cross-subsidisation
- Multi-year pricing — lock in year-1 price with capped escalation

**Non-Price Levers**
- SLA / penalty framework — tighten service commitments with financial consequences
- Warranty / liability — extend warranty period or raise liability cap
- Termination rights — shorten notice period, remove lock-in clauses
- Auto-renewal removal — require explicit opt-in for contract extension
- Data rights / portability — ensure data export and IP ownership
- Scope adjustment — add or remove deliverables to change the value equation
- Implementation / transition support — negotiate free migration, training, or onboarding
- Benchmarking rights — include a clause allowing periodic price benchmarking against market
- Most-favoured-customer clause — guarantee the buyer gets the best available terms

**Relationship Levers**
- Reference / case study — offer marketing value in exchange for pricing concession
- Joint innovation / roadmap input — trade strategic engagement for commercial terms
- Preferred supplier status — offer volume allocation in exchange for pricing tier
- Executive sponsorship — escalate to executive level for relationship-based concessions

For each lever, note:
- **Our position** — what are we asking for?
- **Their likely resistance** — why will they push back?
- **Our fallback** — what's the minimum we'll accept on this lever?
- **Trade value** — what can we offer in return?

---

## Step 5 — Sequence the concession strategy

This is where most negotiators fail. They give away their best levers early and have nothing left to trade. The concession strategy defines: what to give first, what to hold back, and what never to concede.

Build the sequence:

### Phase 1 — Opening (anchoring)
- Open with the most ambitious position on every dimension (target, not walk-away)
- Lead with your strongest lever — the one backed by data or competitive alternatives
- Signal firmness on must-win items from the start

### Phase 2 — Trading (value exchange)
- Concede nice-to-haves first — explicitly frame them as concessions: "We're prepared to move on [X] if you can move on [Y]"
- Trade important items only in exchange for must-have items
- Never concede two items in a row without getting something back
- Keep a running tally of what each side has conceded — show the balance

### Phase 3 — Closing (final package)
- Must-win items are last to move — and only within the pre-approved range
- Frame the final offer as a complete package: "If you can do [X, Y, Z], we're ready to sign"
- If the supplier tries to reopen settled items, pause: "We've already agreed on that. Let's focus on the remaining open items."

**Hard rule:** The concession sequence must be approved before the negotiation. Changes mid-negotiation require a break to reassess.

Present the sequence as a numbered list:
1. **Concede first:** [nice-to-have lever] → in exchange for [their concession]
2. **Trade second:** [important lever] → in exchange for [must-have item]
3. ...
4. **Hold firm:** [must-win items] — only move within authority limits

---

## Step 6 — Set authority limits

Define the negotiator's decision boundaries:

| Dimension | Target | Walk-away | Authority to agree | Requires escalation |
|---|---|---|---|---|
| Total price | $480K | $520K | Up to $520K — [role] | Above $520K — CPO |
| Payment terms | Net 60 | Net 45 | Net 45+ — [role] | Below Net 45 — Director |

**Hard rule:** Walk-away limits must be defined before the negotiation starts. If the negotiator reaches the walk-away point, the instruction is to pause and escalate — not to keep negotiating.

---

## Step 7 — Draft counter-proposal language

For the top 4–6 clauses where the gap is significant, use `lib/counter_proposal_drafter.py` to generate ready-to-use language. See `modes/counter-proposal-mode.md` for the detailed approach.

For each clause, provide:
- **Supplier's current language** (from proposal)
- **Our preferred position** (counter-proposal)
- **Fallback position** (if they reject the preferred)
- **Rationale** (why this matters — for the negotiator to articulate verbally)

---

## Step 8 — Assemble the playbook

Use `lib/playbook_builder.py` to compile the complete playbook. Generate two outputs:

1. **Full playbook** (.docx) — the comprehensive negotiation strategy document
   - Naming: `[ORG_NAME]-Negotiation-Playbook-[SUPPLIER]-[DATE].docx`

2. **Pre-negotiation briefing card** — a one-page summary for the negotiation table
   - Route to `modes/briefing-card-mode.md` to generate
   - Naming: `[ORG_NAME]-Briefing-Card-[SUPPLIER]-[DATE].docx`

---

## Step 9 — Save and log

Save the playbook data to `${CLAUDE_PLUGIN_DATA}/playbooks/[SUPPLIER]-[DATE].json`

Append to `${CLAUDE_PLUGIN_DATA}/negotiation-history.log`:
```
DATE: [date]
EVENT: Playbook created
SUPPLIER: [supplier]
CATEGORY: [category]
DEAL_TYPE: [new / renewal / renegotiation]
SUPPLIER_ASK: [total value]
INTERNAL_TARGET: [total value]
GAP: [value and %]
BATNA_STRENGTH: [Strong / Moderate / Weak]
LEVERS: [n identified]
AUTHORITY_LIMIT: [walk-away value]
```

---

## What Good Looks Like

- BATNA is explicitly defined and classified — never missing or vague
- Every lever has a fallback position — the playbook handles "what if they say no"
- Concession sequence is numbered and pre-approved — not improvised in the room
- Authority limits have a clear escalation path — the negotiator knows when to pause
- Counter-proposal language is ready to use — not placeholder text
- The playbook accounts for the supplier's likely tactics — it's not just our wishlist

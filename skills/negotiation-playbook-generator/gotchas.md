# Gotchas — Negotiation Playbook Generator

Add a line each time Claude trips on something new.

---

## BATNA Gotchas

- **A BATNA that doesn't exist is not a BATNA.** "We could go to market" is not a BATNA — it's a vague threat. A BATNA must be a specific, actionable alternative with a known cost and timeline. If the user says "we could probably find someone else", push back: "Has another supplier been evaluated? What would it cost including switching? How long would it take?" If the answer is all vague, the BATNA is Weak — document it as such.
- **BATNA cost must include switching costs.** An alternative at $510K sounds cheaper than the incumbent at $520K — until you add $80K switching cost. Always compute the fully loaded BATNA cost: alternative price + migration + training + productivity loss + risk premium. Present the real number.
- **The supplier knows your BATNA better than you think.** If you're negotiating a renewal and haven't spoken to another supplier in 3 years, the incumbent knows you have no alternative. Don't bluff a BATNA you don't have — experienced suppliers will call it. Better to be honest about a Weak BATNA and adjust strategy accordingly.
- **A strong BATNA doesn't mean you should use it aggressively.** Walking away is always more expensive than getting a good deal. Even with a strong BATNA, the goal is a fair agreement — not to punish the supplier.

---

## Lever & Concession Gotchas

- **Don't lead with price if you have non-price levers.** Price is the most contentious dimension. Start with contract structure, SLAs, payment terms, or scope — these often have more room for creative solutions. Move to price once non-price items are settled.
- **Never concede without getting something back.** Unilateral concessions signal weakness and train the supplier to push harder. Every concession must be framed as a trade: "We'll move on X if you move on Y." If the user wants to "give them something as a goodwill gesture", explain: goodwill gestures in procurement negotiations are just free concessions.
- **Concession size matters.** Making your biggest concession first signals panic. Start with small concessions on low-priority items. Decrease concession size as you progress — this signals you're approaching your limit.
- **Don't negotiate against yourself.** If you make an offer and the supplier says nothing, wait. Silence is a negotiation tactic. If you immediately improve your offer without them countering, you're bidding against yourself.
- **Bundling changes the game.** A supplier who won't move on price may move on a bundle: "We'll accept your price if you include implementation, training, and 2 years of premium support." Unbundling works too: "We don't need the platinum package — price the core only."

---

## Counter-Proposal Gotchas

- **Counter-proposals are not legal documents.** They are negotiation positions written in commercial language. Always flag: "Have legal counsel review before signing." Claude is not a lawyer and must not represent its output as legal advice.
- **Tier 2 must be genuinely acceptable.** If your fallback position is actually unacceptable, it's not a real fallback — it's a Tier 1 variant. The user should be able to sign at Tier 2 without regret. Test: "Would you actually sign this?" If the answer is no, it's not Tier 2.
- **Match the contract's terminology.** If the contract says "Fees" not "Price", the counter-proposal must say "Fees". If it says "Service Provider" not "Supplier", match that. Inconsistent terminology creates ambiguity that works against the buyer.
- **Don't redline every clause.** Returning a contract with 40 markups signals that you haven't prioritised. Focus counter-proposals on the 4–6 clauses that actually matter. Accept standard boilerplate unless it contains a trap.
- **Auto-renewal is not a minor clause.** It is the single most common source of unnecessary procurement spend. A 12-month auto-renewal with a 30-day opt-out means you have one month per year to exit. Miss the window and you're locked in for another year. Always counter this.

---

## Authority & Escalation Gotchas

- **Target price is not walk-away price.** Target is what you aim for. Walk-away is where you stop. If they're the same number, the negotiator has zero flexibility and will either cave or deadlock. There must be a range between target and walk-away.
- **Authority limits must be set before the negotiation, not during.** A negotiator who has to "check with my boss" mid-negotiation loses credibility — unless it's a deliberate tactic (which should be pre-planned). Set the limits. If the limit is hit, the playbook says: pause, break, escalate. Not: keep talking.
- **"I need to check with my manager" is a legitimate tactic — when planned.** Some organisations deliberately limit the negotiator's authority as a tactic to create a natural break point. But this must be planned and documented in the playbook, not improvised.
- **The CPO should never be the first person in the room.** If the CPO negotiates directly, there's no escalation available. The negotiation structure should be: Category Manager leads → Director available for escalation → CPO as final authority.

---

## Strategy Gotchas

- **Anchoring works — but only if credible.** Opening at 40% below the supplier's ask is a strong anchor. Opening at 80% below is insulting and damages the relationship. The anchor must be defensible: market data, competitive quotes, or cost modelling. "Because we want to" is not an anchor.
- **Time pressure is usually artificial.** "The price goes up on Friday" is almost always a tactic. Legitimate price changes come with documented cost increases, not ultimatums. Push back: "Can you share the cost basis for the increase?"
- **Renewal negotiations are different from new deals.** In a renewal, the supplier has the advantage of switching costs. You're not starting from zero — you're starting from "already installed and integrated." Account for this in the strategy: switching cost weakens your BATNA, but so does the supplier losing a current customer.
- **Don't negotiate scope and price simultaneously.** If scope is still being defined, lock it down before discussing price. A supplier who negotiates price while scope is vague will price for the maximum scope — and then claim any reduction is a "change order."
- **A bad deal is worse than no deal.** If the terms don't work, walk away. A deal at the wrong price or with the wrong terms creates problems for 3+ years. The pressure to "get the deal done" is the enemy of good procurement.
- **Document everything in real time.** Verbal agreements in negotiation meetings are forgotten, misremembered, or denied. Summarise agreed points at the end of each session and confirm in writing within 24 hours.

---

## Data & Benchmarking Gotchas

- **Market benchmarks are directional, not precise.** A benchmark that says "the market rate is $X" is an estimate based on aggregated data. It won't match your exact scope, location, and requirements. Use benchmarks to validate ranges, not to dictate targets.
- **Supplier cost breakdowns are often fiction.** If a supplier provides a cost breakdown showing 2% margin, they're either lying or about to go bankrupt. Use cost modelling to validate — don't take their breakdown at face value.
- **Historical spend is not the same as market rate.** "We've always paid $X" doesn't mean $X is fair. Prices drift, markets change, and lazy renewals accumulate overpayment. Always benchmark against current market, not historical spend.

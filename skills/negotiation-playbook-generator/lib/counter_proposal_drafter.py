"""
counter_proposal_drafter.py — Clause-Level Counter-Proposal Generator
Part of the Molecule One Negotiation Playbook Generator skill.

Generates three-tier counter-proposal language for specific commercial
clauses: preferred position, fallback position, and walk-away threshold.
Each counter includes verbal rationale for the negotiator.

Usage:
    from lib.counter_proposal_drafter import CounterProposal, CounterProposalSet
    from lib.counter_proposal_drafter import draft_counter, build_counter_set

Gotchas:
    - Counter-proposals are NOT legal advice. They are negotiation positions
      drafted in commercial language. Always flag: "These counter-proposals
      are negotiation positions — have legal counsel review before signing."
    - The verbal rationale is critical. Contract language alone doesn't win
      negotiations — the negotiator needs to articulate WHY something matters.
      Rationales should be 2–3 sentences, plain language, business-focused.
    - Tier 2 (fallback) must be genuinely acceptable, not a throwaway.
      If the fallback is unacceptable, it's really a Tier 1 variant, not
      a true fallback. The user should be able to sign at Tier 2 without
      feeling they lost.
    - Tier 3 (red line) defines where to stop. Below this threshold, the
      instruction is to pause and escalate — not to keep negotiating.
"""

import json
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


@dataclass
class CounterProposal:
    """
    A three-tier counter-proposal for a single commercial clause.

    Gotcha: supplier_current_language should be the actual text from the
    proposal, not a summary. If the exact text isn't available, note
    "[SUMMARY — confirm against actual contract language]".
    """
    clause_name: str
    clause_category: str            # Payment / Contract / SLA / Risk / Pricing / Other
    supplier_current_language: str   # What the supplier has proposed
    tier_1_preferred: str            # Our ideal position — exact language
    tier_2_fallback: str             # Acceptable alternative — exact language
    tier_3_red_line: str             # Below this = escalate or walk
    verbal_rationale: str            # What to say across the table
    negotiation_tactic: str          # anchor / trade / benchmark / escalate / principle
    priority: str = ""               # Must-win / Must-have / Important / Nice-to-have
    notes: str = ""


@dataclass
class CounterProposalSet:
    """A complete set of counter-proposals for a negotiation."""
    supplier_name: str
    prepared_date: str
    org_name: str
    proposals: list[CounterProposal]
    general_notes: str = ""


STANDARD_COUNTERS = {
    "payment_terms": {
        "clause_name": "Payment Terms",
        "clause_category": "Payment",
        "tier_1_preferred": (
            "All invoices shall be payable within sixty (60) days of receipt of a "
            "correct and undisputed invoice by the Buyer."
        ),
        "tier_2_fallback": (
            "All invoices shall be payable within forty-five (45) days of receipt of a "
            "correct and undisputed invoice. A prompt payment discount of 2% shall apply "
            "for payments made within fifteen (15) days."
        ),
        "tier_3_red_line": (
            "Payment terms shorter than thirty (30) days are not acceptable. "
            "No payment shall be required in advance of service delivery."
        ),
        "verbal_rationale": (
            "Our standard payment terms are Net 60. We're open to discussing an early "
            "payment incentive, but the baseline must reflect our cash flow requirements "
            "and procurement policy."
        ),
        "negotiation_tactic": "anchor",
    },
    "auto_renewal": {
        "clause_name": "Auto-Renewal",
        "clause_category": "Contract",
        "tier_1_preferred": (
            "This Agreement shall expire at the end of the Initial Term. Renewal shall "
            "require written agreement by both parties executed no later than ninety (90) "
            "days prior to the expiry date."
        ),
        "tier_2_fallback": (
            "This Agreement may be renewed for successive periods of twelve (12) months "
            "each, unless either party provides written notice of non-renewal at least "
            "one hundred and eighty (180) days prior to the end of the then-current term. "
            "Any renewal shall be at pricing no higher than the prior term plus CPI adjustment."
        ),
        "tier_3_red_line": (
            "Auto-renewal with an opt-out window shorter than ninety (90) days is not acceptable."
        ),
        "verbal_rationale": (
            "We don't accept auto-renewal as standard policy. We need the flexibility to "
            "review performance and market conditions before committing to an extension. "
            "This protects both parties."
        ),
        "negotiation_tactic": "principle",
    },
    "termination_convenience": {
        "clause_name": "Termination for Convenience",
        "clause_category": "Contract",
        "tier_1_preferred": (
            "Either party may terminate this Agreement for convenience by providing "
            "ninety (90) days' prior written notice. Upon termination, the Buyer shall "
            "pay for all services satisfactorily performed through the effective date of termination."
        ),
        "tier_2_fallback": (
            "The Buyer may terminate this Agreement for convenience by providing one hundred "
            "and eighty (180) days' prior written notice. The Supplier shall be entitled to "
            "payment for services performed and reasonable wind-down costs, not to exceed "
            "the equivalent of three (3) months' fees."
        ),
        "tier_3_red_line": (
            "Absence of termination for convenience is not acceptable for agreements "
            "exceeding twelve (12) months in duration."
        ),
        "verbal_rationale": (
            "Our business needs evolve. We require the ability to exit the agreement if "
            "our strategy changes, with reasonable notice and fair treatment of work in "
            "progress. This is a standard commercial provision."
        ),
        "negotiation_tactic": "principle",
    },
    "liability_cap": {
        "clause_name": "Liability Cap",
        "clause_category": "Risk",
        "tier_1_preferred": (
            "The Supplier's aggregate liability under this Agreement shall not exceed "
            "two hundred percent (200%) of the total annual fees payable. This cap shall "
            "not apply to: (a) liability arising from wilful misconduct or gross negligence; "
            "(b) breach of confidentiality obligations; (c) infringement of intellectual "
            "property rights; (d) breach of data protection obligations."
        ),
        "tier_2_fallback": (
            "The Supplier's aggregate liability under this Agreement shall not exceed "
            "one hundred percent (100%) of the total annual fees payable. Mutual uncapped "
            "carve-outs shall apply to intellectual property infringement and data breach."
        ),
        "tier_3_red_line": (
            "A liability cap below fifty percent (50%) of annual fees is not acceptable. "
            "Supplier attempts to cap liability for data breach are not acceptable."
        ),
        "verbal_rationale": (
            "The liability cap must be proportionate to the risk being transferred. "
            "Given the nature of this engagement, we need assurance that material failures "
            "are covered — particularly around data and IP."
        ),
        "negotiation_tactic": "anchor",
    },
    "sla_penalties": {
        "clause_name": "SLA Penalties / Service Credits",
        "clause_category": "SLA",
        "tier_1_preferred": (
            "For each Service Level not met in a calendar month, the Supplier shall issue "
            "a service credit equal to five percent (5%) of the monthly fees for the "
            "affected service. Service credits are cumulative and uncapped. Three (3) "
            "consecutive months of SLA failure shall constitute a material breach entitling "
            "the Buyer to terminate for cause."
        ),
        "tier_2_fallback": (
            "For each Service Level not met in a calendar month, the Supplier shall issue "
            "a service credit equal to three percent (3%) of the monthly fees, capped at "
            "fifteen percent (15%) of monthly fees per month. Persistent SLA failure over "
            "three (3) consecutive months shall trigger a formal performance review."
        ),
        "tier_3_red_line": (
            "Service Level Agreements without financial penalties or service credits are "
            "not acceptable for strategic or leverage category suppliers."
        ),
        "verbal_rationale": (
            "SLAs without consequences are aspirational statements, not commitments. "
            "We need a framework that incentivises consistent delivery and gives us a "
            "remedy when service falls short."
        ),
        "negotiation_tactic": "benchmark",
    },
    "price_escalation": {
        "clause_name": "Price Escalation",
        "clause_category": "Pricing",
        "tier_1_preferred": (
            "Pricing shall remain fixed for the duration of the Initial Term."
        ),
        "tier_2_fallback": (
            "Annual price adjustments shall not exceed the lower of: (a) the Consumer Price "
            "Index (CPI) increase for the preceding twelve (12) months; or (b) three percent "
            "(3%). The Supplier shall provide ninety (90) days' advance written notice of "
            "any price adjustment, together with supporting data."
        ),
        "tier_3_red_line": (
            "Uncapped price escalation or escalation indexed to a metric controlled by the "
            "Supplier is not acceptable."
        ),
        "verbal_rationale": (
            "We need pricing predictability for budget planning. We're open to a fair "
            "escalation mechanism tied to a transparent, independent index — but it must "
            "be capped and notified in advance."
        ),
        "negotiation_tactic": "anchor",
    },
}


def draft_counter(
    clause_key: str,
    supplier_language: str = "",
    custom_overrides: Optional[dict] = None,
) -> CounterProposal:
    """
    Draft a counter-proposal for a standard clause.

    Parameters:
      clause_key: key from STANDARD_COUNTERS (e.g. "payment_terms")
      supplier_language: the supplier's current proposed language
      custom_overrides: dict of fields to override (e.g. {"tier_1_preferred": "..."})

    Returns a CounterProposal.

    Gotchas:
      - If supplier_language is empty, the counter will note
        "[Supplier language not provided — confirm against actual contract]".
      - Custom overrides are applied AFTER the standard template, so you
        can selectively change just one tier without rewriting everything.
    """
    if clause_key not in STANDARD_COUNTERS:
        raise ValueError(
            f"Unknown clause key: '{clause_key}'. "
            f"Available: {', '.join(STANDARD_COUNTERS.keys())}"
        )

    template = STANDARD_COUNTERS[clause_key].copy()

    if custom_overrides:
        template.update(custom_overrides)

    return CounterProposal(
        clause_name=template["clause_name"],
        clause_category=template["clause_category"],
        supplier_current_language=supplier_language or "[Supplier language not provided — confirm against actual contract]",
        tier_1_preferred=template["tier_1_preferred"],
        tier_2_fallback=template["tier_2_fallback"],
        tier_3_red_line=template["tier_3_red_line"],
        verbal_rationale=template["verbal_rationale"],
        negotiation_tactic=template["negotiation_tactic"],
    )


def draft_custom_counter(
    clause_name: str,
    clause_category: str,
    supplier_language: str,
    preferred: str,
    fallback: str,
    red_line: str,
    rationale: str,
    tactic: str = "trade",
) -> CounterProposal:
    """
    Draft a fully custom counter-proposal (not from the standard library).

    Gotchas:
      - All three tiers must be provided. A counter with only a preferred
        position and no fallback is incomplete.
      - The rationale should be plain language, not legalese. It's what
        the negotiator says, not what the contract says.
    """
    if not preferred or not fallback or not red_line:
        raise ValueError("All three tiers (preferred, fallback, red_line) must be provided.")

    return CounterProposal(
        clause_name=clause_name,
        clause_category=clause_category,
        supplier_current_language=supplier_language,
        tier_1_preferred=preferred,
        tier_2_fallback=fallback,
        tier_3_red_line=red_line,
        verbal_rationale=rationale,
        negotiation_tactic=tactic,
    )


def build_counter_set(
    supplier_name: str,
    prepared_date: str,
    org_name: str,
    proposals: list[CounterProposal],
    general_notes: str = "",
) -> CounterProposalSet:
    """Build a complete counter-proposal set."""
    return CounterProposalSet(
        supplier_name=supplier_name,
        prepared_date=prepared_date,
        org_name=org_name,
        proposals=proposals,
        general_notes=general_notes,
    )


def render_counter_summary(counter_set: CounterProposalSet) -> str:
    """Render a human-readable counter-proposal summary."""
    lines = [
        f"## Counter-Proposal Summary — {counter_set.supplier_name}",
        f"Prepared: {counter_set.prepared_date} | Org: {counter_set.org_name}",
        "",
        f"{'#':<3} {'Clause':<25} {'Category':<12} {'Tactic':<12} {'Priority'}",
        "-" * 70,
    ]

    for i, cp in enumerate(counter_set.proposals, 1):
        lines.append(
            f"{i:<3} {cp.clause_name:<25} {cp.clause_category:<12} "
            f"{cp.negotiation_tactic:<12} {cp.priority or 'Not set'}"
        )

    lines += ["", "---", ""]

    for i, cp in enumerate(counter_set.proposals, 1):
        lines += [
            f"### {i}. {cp.clause_name}",
            "",
            f"**Supplier's position:** {cp.supplier_current_language[:100]}{'...' if len(cp.supplier_current_language) > 100 else ''}",
            "",
            f"**Tier 1 — Preferred:** {cp.tier_1_preferred[:120]}{'...' if len(cp.tier_1_preferred) > 120 else ''}",
            f"**Tier 2 — Fallback:** {cp.tier_2_fallback[:120]}{'...' if len(cp.tier_2_fallback) > 120 else ''}",
            f"**Tier 3 — Red line:** {cp.tier_3_red_line[:100]}{'...' if len(cp.tier_3_red_line) > 100 else ''}",
            "",
            f"**Rationale:** {cp.verbal_rationale}",
            f"**Tactic:** {cp.negotiation_tactic}",
            "",
        ]

    lines.append("_These counter-proposals are negotiation positions — have legal counsel review before signing._")

    return "\n".join(lines)


def save_counter_set(counter_set: CounterProposalSet, output_dir: str) -> str:
    """Save a counter-proposal set to JSON."""
    safe_supplier = counter_set.supplier_name.lower().replace(" ", "-")
    filename = f"{safe_supplier}-counters-{counter_set.prepared_date}.json"
    path = Path(output_dir) / filename

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    data = {
        "supplier_name": counter_set.supplier_name,
        "prepared_date": counter_set.prepared_date,
        "org_name": counter_set.org_name,
        "general_notes": counter_set.general_notes,
        "proposals": [asdict(p) for p in counter_set.proposals],
    }
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"[counter_proposal_drafter] Saved to {path}", file=sys.stderr)
    return str(path)


if __name__ == "__main__":
    # Demo counter-proposals
    counters = [
        draft_counter("payment_terms", "Payment is due within 30 days of invoice date."),
        draft_counter("auto_renewal", "This agreement will automatically renew for successive 12-month periods unless cancelled with 30 days notice."),
        draft_counter("sla_penalties", "The Supplier will use commercially reasonable efforts to meet service levels."),
        draft_counter("termination_convenience"),
        draft_counter("liability_cap", "Supplier's total liability shall not exceed fees paid in the preceding 12 months."),
        draft_counter("price_escalation", "Prices may be adjusted annually at the Supplier's discretion."),
    ]

    counter_set = build_counter_set(
        supplier_name="Salesforce",
        prepared_date="2026-03-21",
        org_name="Acme Corp",
        proposals=counters,
        general_notes="CRM renewal — 3-year deal. Priority is total price and removal of auto-renewal.",
    )
    print(render_counter_summary(counter_set))

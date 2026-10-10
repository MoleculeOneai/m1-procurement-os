"""
strategy_generator.py — Category Strategy Document Assembler
Part of the Molecule One Category Strategy Builder skill.

Assembles structured data from the segmentation and opportunity analysis
into a formatted category strategy document (Markdown → ready for docx export).

Usage:
    from lib.strategy_generator import build_strategy_doc, format_opportunity_table

Gotchas:
    - This script produces a Markdown intermediate. The final .docx is produced
      by the `docx` skill. Do not attempt to generate .docx directly from this script.
    - All savings figures passed to this function must have already been reviewed
      and approved by the user. Never auto-populate savings targets.
    - Strategy documents must not include the internal Kraljic scores or supply risk
      scores — these are internal calibration tools. The final document states the
      quadrant and approach, not the raw numbers.
    - Placeholder text `[REVIEW NEEDED: ...]` must be resolved before the docx is shared
      outside procurement. Flag any unresolved placeholders on export.
"""

import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Optional


# ─────────────────────────────────────────────
# Data model (plain dicts — no external deps)
# ─────────────────────────────────────────────

def build_strategy_doc(
    org_name: str,
    category: str,
    quadrant: str,
    strategy_horizon_months: int,
    annual_spend: float,
    currency: str,
    current_state: dict,
    market_summary: dict,
    strategic_approach: str,
    sourcing_action: str,
    opportunities: list[dict],
    implementation_phases: list[dict],
    kpis: list[dict],
    stakeholders: list[dict],
    prepared_by: str = "Molecule One Claude Plugin Suite",
    review_date: Optional[str] = None,
) -> str:
    """
    Build a complete category strategy document in Markdown format.

    Parameters:
      org_name: str — from config.json
      category: str — category name
      quadrant: str — Strategic / Leverage / Bottleneck / Routine
      strategy_horizon_months: int — 12, 24, or 36
      annual_spend: float — total annual spend for this category
      currency: str — e.g. "USD", "GBP", "EUR"
      current_state: dict — keys: supplier_count, incumbent_name, contract_expiry,
                            known_issues, buying_channels
      market_summary: dict — keys: market_structure, viable_suppliers, supply_risk,
                             key_price_drivers, top_market_opportunity
      strategic_approach: str — the recommended approach (from segmentation-mode)
      sourcing_action: str — specific sourcing action (RFP / negotiation / framework / etc.)
      opportunities: list of dicts — each with:
                     { lever, spend_in_scope, conservative, central, optimistic,
                       confidence, effort, timeframe_months, owner_role, dependencies }
      implementation_phases: list of dicts — each with:
                     { phase_name, actions: [ { action, owner_role, deadline, expected_value } ] }
      kpis: list of dicts — each with: { metric, baseline, target, measurement_frequency }
      stakeholders: list of dicts — each with: { name, role, interest, influence (H/M/L) }
      prepared_by: str
      review_date: str — ISO date string for when the strategy should next be reviewed

    Returns a Markdown string for the full strategy document.

    Gotchas:
      - If current_state["contract_expiry"] is None, the document will flag this
        as [REVIEW NEEDED: confirm contract expiry date]. Do not leave it blank.
      - If opportunities is empty, the function will insert a placeholder section.
        An approved strategy with zero opportunities is a red flag — flag it.
      - Savings totals are computed from the opportunities list. If any opportunity
        has confidence="Low", the total will include a caveat.
    """

    doc_date = date.today().strftime("%d %b %Y")
    review_str = review_date or f"12 months from {doc_date}"
    spend_fmt = _fmt_currency(annual_spend, currency)

    lines = [
        f"# {org_name} — Category Strategy: {category}",
        f"**Prepared by:** {prepared_by}",
        f"**Date:** {doc_date}",
        f"**Strategy Horizon:** {strategy_horizon_months} months",
        f"**Annual Spend:** {spend_fmt}",
        f"**Category Classification:** {quadrant}",
        f"**Next Review Date:** {review_str}",
        "",
        "_Part of the Molecule One Claude Plugin Suite_",
        f"_Confidential — {org_name} Procurement | moleculeone.ai_",
        "",
        "---",
        "",
        "## 1. Executive Summary",
        "",
        f"This category strategy covers **{category}** for **{org_name}**, "
        f"representing approximately **{spend_fmt}** in annual spend. "
        f"The category is classified as **{quadrant}** on the Kraljic matrix.",
        "",
        f"**Recommended approach:** {strategic_approach}",
        "",
        f"**Primary sourcing action:** {sourcing_action}",
        "",
        _opportunity_headline(opportunities, currency),
        "",
        "---",
        "",
        "## 2. Current State",
        "",
        _render_current_state(current_state),
        "",
        "---",
        "",
        "## 3. Supply Market Overview",
        "",
        _render_market_summary(market_summary),
        "",
        "---",
        "",
        "## 4. Category Classification",
        "",
        f"**Kraljic quadrant: {quadrant}**",
        "",
        _quadrant_rationale(quadrant),
        "",
        "---",
        "",
        "## 5. Strategic Approach",
        "",
        f"**Recommended strategy:** {strategic_approach}",
        "",
        f"**Sourcing action:** {sourcing_action}",
        "",
        "### Stakeholder Alignment",
        "",
        _render_stakeholder_table(stakeholders),
        "",
        "---",
        "",
        "## 6. Value & Savings Opportunities",
        "",
        _render_opportunity_table(opportunities, currency),
        "",
        "---",
        "",
        "## 7. Implementation Roadmap",
        "",
        _render_implementation_phases(implementation_phases),
        "",
        "---",
        "",
        "## 8. KPIs & Governance",
        "",
        _render_kpi_table(kpis),
        "",
        "### Governance Cadence",
        "",
        "- **Monthly:** Category performance review (operational metrics, supplier issues)",
        "- **Quarterly:** Stakeholder review — commercial progress against strategy",
        "- **Annual:** Strategy refresh — re-run Kraljic assessment, update market intelligence",
        "",
        "---",
        "",
        "## 9. Risks & Mitigations",
        "",
        _render_risks(quadrant, current_state, market_summary),
        "",
        "---",
        "",
        "_All savings estimates are potential savings subject to market conditions, "
        "negotiation outcomes, and demand assumptions. They do not constitute committed targets._",
    ]

    doc = "\n".join(lines)
    _check_unresolved_placeholders(doc)
    return doc


# ─────────────────────────────────────────────
# Section renderers
# ─────────────────────────────────────────────

def _render_current_state(cs: dict) -> str:
    supplier_count = cs.get("supplier_count", "[REVIEW NEEDED: confirm supplier count]")
    incumbent = cs.get("incumbent_name") or "No single incumbent"
    expiry = cs.get("contract_expiry") or "[REVIEW NEEDED: confirm contract expiry date]"
    issues = cs.get("known_issues") or "No known issues reported"
    channels = cs.get("buying_channels") or "[REVIEW NEEDED: describe current buying channels]"

    return (
        f"| Field | Detail |\n"
        f"|---|---|\n"
        f"| Active supplier count | {supplier_count} |\n"
        f"| Primary incumbent | {incumbent} |\n"
        f"| Contract expiry | {expiry} |\n"
        f"| Known issues | {issues} |\n"
        f"| Current buying channels | {channels} |"
    )


def _render_market_summary(ms: dict) -> str:
    structure = ms.get("market_structure", "[REVIEW NEEDED: market structure]")
    viable = ms.get("viable_suppliers", "[REVIEW NEEDED: viable supplier count]")
    risk = ms.get("supply_risk", "[REVIEW NEEDED: supply risk rating]")
    drivers = ms.get("key_price_drivers", "[REVIEW NEEDED: list price drivers]")
    opportunity = ms.get("top_market_opportunity", "[REVIEW NEEDED: top market opportunity]")

    return (
        f"| Dimension | Assessment |\n"
        f"|---|---|\n"
        f"| Market structure | {structure} |\n"
        f"| Viable suppliers (in scope geography) | {viable} |\n"
        f"| Supply risk rating | {risk} |\n"
        f"| Key price drivers | {drivers} |\n"
        f"| Top market opportunity | {opportunity} |"
    )


def _quadrant_rationale(quadrant: str) -> str:
    rationales = {
        "Strategic": (
            "This category scores high on both spend impact and supply risk. "
            "It is critical to operational performance and has limited supplier alternatives. "
            "A relationship-based approach is required — competitive tendering would "
            "damage the supplier relationship without delivering material savings."
        ),
        "Leverage": (
            "This category has high spend impact but manageable supply risk. "
            "Multiple viable suppliers exist and switching cost is acceptable. "
            "The primary lever is competitive sourcing to extract best commercial terms."
        ),
        "Bottleneck": (
            "This category has low spend but high supply risk. "
            "A supply disruption would have an impact disproportionate to the spend value. "
            "The priority is securing supply continuity rather than cost reduction."
        ),
        "Routine": (
            "This category has low spend impact and low supply risk. "
            "It does not warrant dedicated category management. "
            "The focus should be on process efficiency, catalogue adoption, and demand aggregation "
            "to reduce the cost of buying, not the price of what is bought."
        ),
    }
    return rationales.get(quadrant, "[REVIEW NEEDED: quadrant rationale]")


def _render_stakeholder_table(stakeholders: list[dict]) -> str:
    if not stakeholders:
        return "[REVIEW NEEDED: complete stakeholder analysis before finalising strategy]"
    header = "| Name | Role | Interest | Influence | Engagement Approach |\n|---|---|---|---|---|"
    rows = []
    for s in stakeholders:
        rows.append(
            f"| {s.get('name','')} | {s.get('role','')} | "
            f"{s.get('interest','')} | {s.get('influence','')} | "
            f"{s.get('engagement_approach', 'TBC')} |"
        )
    return header + "\n" + "\n".join(rows)


def _render_opportunity_table(opportunities: list[dict], currency: str) -> str:
    if not opportunities:
        return "[REVIEW NEEDED: complete opportunity analysis before finalising strategy]"

    header = (
        "| # | Lever | Spend in Scope | Conservative | Central | Optimistic | "
        "Confidence | Effort | Timeframe | Owner |\n"
        "|---|---|---|---|---|---|---|---|---|---|"
    )
    rows = []
    total_central = 0.0
    has_low_confidence = False

    for i, op in enumerate(opportunities, start=1):
        central = op.get("central", 0)
        total_central += central
        if op.get("confidence", "").lower() == "low":
            has_low_confidence = True
        rows.append(
            f"| {i} | {op.get('lever','')} | "
            f"{_fmt_currency(op.get('spend_in_scope', 0), currency)} | "
            f"{_fmt_currency(op.get('conservative', 0), currency)} | "
            f"{_fmt_currency(central, currency)} | "
            f"{_fmt_currency(op.get('optimistic', 0), currency)} | "
            f"{op.get('confidence','')} | {op.get('effort','')} | "
            f"{op.get('timeframe_months', '')} months | {op.get('owner_role','')} |"
        )

    table = header + "\n" + "\n".join(rows)
    table += f"\n\n**Total central value estimate: {_fmt_currency(total_central, currency)}**"

    if has_low_confidence:
        table += (
            "\n\n_Note: One or more opportunities are rated Low confidence. "
            "Treat the total with caution — validate before committing to targets._"
        )
    return table


def _render_implementation_phases(phases: list[dict]) -> str:
    if not phases:
        return "[REVIEW NEEDED: define implementation roadmap phases]"
    sections = []
    for phase in phases:
        name = phase.get("phase_name", "Unnamed Phase")
        actions = phase.get("actions", [])
        sections.append(f"### {name}")
        if not actions:
            sections.append("_No actions defined yet._")
            continue
        header = "| Action | Owner | Deadline | Expected Value |\n|---|---|---|---|"
        rows = [
            f"| {a.get('action','')} | {a.get('owner_role','')} | "
            f"{a.get('deadline','')} | {a.get('expected_value','')} |"
            for a in actions
        ]
        sections.append(header + "\n" + "\n".join(rows))
    return "\n\n".join(sections)


def _render_kpi_table(kpis: list[dict]) -> str:
    if not kpis:
        return "[REVIEW NEEDED: define KPIs and baselines]"
    header = "| Metric | Baseline | Target | Measurement Frequency |\n|---|---|---|---|"
    rows = [
        f"| {k.get('metric','')} | {k.get('baseline','TBC')} | "
        f"{k.get('target','TBC')} | {k.get('measurement_frequency','')} |"
        for k in kpis
    ]
    return header + "\n" + "\n".join(rows)


def _render_risks(quadrant: str, current_state: dict, market_summary: dict) -> str:
    risks = []
    risk_rating = market_summary.get("supply_risk", "Unknown")
    if risk_rating in ("High", "Critical"):
        risks.append(
            f"| Supply disruption | {risk_rating} | Dual source qualification; "
            "buffer stock policy; contract force-majeure provisions |"
        )
    if current_state.get("supplier_count") == 1 or current_state.get("incumbent_name"):
        risks.append(
            "| Single supplier dependency | Medium | Qualify at least one alternative "
            "supplier within 12 months |"
        )
    if quadrant == "Strategic":
        risks.append(
            "| Relationship deterioration | Medium | Establish exec sponsor pairing; "
            "quarterly relationship health review |"
        )
    if quadrant == "Leverage":
        risks.append(
            "| Incumbent exit / non-renewal risk | Low | Ensure incumbent is invited "
            "to compete; manage transition risk in contract terms |"
        )
    risks.append(
        "| Market price increase | Medium | Include price adjustment mechanism "
        "and benchmarking rights in contract |"
    )
    risks.append(
        "| Stakeholder non-adoption | Medium | Early business owner engagement; "
        "change management plan in Phase 1 |"
    )

    header = "| Risk | Likelihood | Mitigation |\n|---|---|---|"
    return header + "\n" + "\n".join(risks)


def _opportunity_headline(opportunities: list[dict], currency: str) -> str:
    if not opportunities:
        return ""
    total_central = sum(op.get("central", 0) for op in opportunities)
    count = len(opportunities)
    return (
        f"**Value identified:** {count} opportunit{'y' if count == 1 else 'ies'} with a "
        f"central value estimate of **{_fmt_currency(total_central, currency)}**."
    )


def _fmt_currency(amount: float, currency: str = "USD") -> str:
    symbols = {"USD": "$", "GBP": "£", "EUR": "€", "AUD": "A$", "CAD": "C$"}
    sym = symbols.get(currency.upper(), currency + " ")
    return f"{sym}{amount:,.0f}"


def _check_unresolved_placeholders(doc: str) -> None:
    placeholders = re.findall(r'\[REVIEW NEEDED:[^\]]+\]', doc)
    if placeholders:
        print(
            f"[strategy_generator] WARNING: {len(placeholders)} unresolved placeholder(s) "
            "in strategy document. Resolve before sharing outside procurement:",
            file=sys.stderr
        )
        for p in set(placeholders):
            print(f"  - {p}", file=sys.stderr)


# ─────────────────────────────────────────────
# Opportunity table formatter (standalone use)
# ─────────────────────────────────────────────

def format_opportunity_table(opportunities: list[dict], currency: str = "USD") -> str:
    """
    Format an opportunity register as a Markdown table.
    Standalone function — can be called without build_strategy_doc().
    """
    return _render_opportunity_table(opportunities, currency)


if __name__ == "__main__":
    # Minimal demo
    sample_doc = build_strategy_doc(
        org_name="Acme Corp",
        category="IT Software",
        quadrant="Strategic",
        strategy_horizon_months=24,
        annual_spend=2_500_000,
        currency="USD",
        current_state={
            "supplier_count": 3,
            "incumbent_name": "SAP",
            "contract_expiry": "2025-12-31",
            "known_issues": "Auto-renewal clause — must flag 6 months in advance",
            "buying_channels": "Direct PO via ERP"
        },
        market_summary={
            "market_structure": "Highly concentrated — SAP/Oracle/Microsoft dominate",
            "viable_suppliers": "2–3 at this scale",
            "supply_risk": "High",
            "key_price_drivers": "Seat volume, contract length, competitive pressure at renewal",
            "top_market_opportunity": "Use Oracle/Microsoft as leverage at SAP renewal"
        },
        strategic_approach="Manage as a relationship — joint value improvement and renewal negotiation",
        sourcing_action="Direct negotiation at contract renewal with competitive benchmark prepared",
        opportunities=[
            {
                "lever": "Renewal negotiation with benchmark threat",
                "spend_in_scope": 2_500_000,
                "conservative": 125_000,
                "central": 250_000,
                "optimistic": 375_000,
                "confidence": "Medium",
                "effort": "M",
                "timeframe_months": 6,
                "owner_role": "Category Manager",
                "dependencies": "Legal review of auto-renewal clause"
            }
        ],
        implementation_phases=[
            {
                "phase_name": "Phase 1 — Quick Wins (Months 1–3)",
                "actions": [
                    {"action": "Audit current licence usage and identify shelfware", "owner_role": "IT + Procurement", "deadline": "Month 2", "expected_value": "Up to $75K licence reduction"},
                    {"action": "Flag auto-renewal clause and serve notice if needed", "owner_role": "Procurement Lead", "deadline": "Month 1", "expected_value": "Preserve negotiating leverage"},
                ]
            },
            {
                "phase_name": "Phase 2 — Core Programme (Months 4–6)",
                "actions": [
                    {"action": "Prepare competitive benchmark from Oracle/Microsoft", "owner_role": "Category Manager", "deadline": "Month 4", "expected_value": "Negotiation anchor"},
                    {"action": "Negotiate renewal terms with SAP", "owner_role": "Category Manager + Legal", "deadline": "Month 6", "expected_value": "$250K central estimate"},
                ]
            }
        ],
        kpis=[
            {"metric": "Annual licence cost vs. baseline", "baseline": "$2.5M", "target": "$2.25M", "measurement_frequency": "Annual"},
            {"metric": "Unused licence %", "baseline": "TBC — audit in Month 2", "target": "<5%", "measurement_frequency": "Quarterly"},
        ],
        stakeholders=[
            {"name": "CTO", "role": "Technology sponsor", "interest": "Capability continuity", "influence": "H", "engagement_approach": "Exec briefing before any negotiation"},
            {"name": "CFO", "role": "Finance approver", "interest": "Cost reduction", "influence": "H", "engagement_approach": "Quarterly savings report"},
        ],
    )
    print(sample_doc)

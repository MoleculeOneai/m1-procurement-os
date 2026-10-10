"""
gap_analyzer.py — Position Gap Computation & Risk Flagging
Part of the Molecule One Negotiation Playbook Generator skill.

Computes the gap between a supplier's opening position and the buyer's
internal target across all negotiable dimensions. Classifies each gap
by priority and flags commercial risks in the supplier's proposal.

Usage:
    from lib.gap_analyzer import DimensionGap, GapAnalysis
    from lib.gap_analyzer import compute_gaps, flag_risks, compute_tco

Gotchas:
    - Not all gaps are numeric. Payment terms (Net 30 vs Net 60) and
      auto-renewal (yes/no) are qualitative gaps. The gap_type field
      distinguishes between "monetary", "percentage", "duration", and
      "qualitative" gaps. Only monetary gaps contribute to total_value_gap.
    - A zero gap is not necessarily good. If the supplier's first offer
      matches your target, either you set the target too high or they
      have room to go lower. Flag this as a "suspiciously aligned" dimension.
    - Hidden costs are gaps too. Setup fees, migration costs, and training
      that weren't in your target are net-new gaps. Always compute TCO,
      not just headline price.
"""

import json
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


@dataclass
class DimensionGap:
    """
    A single negotiable dimension with supplier position, buyer target, and gap.

    Gotcha: gap_value is always expressed as "how far the supplier is
    from our target". A positive gap means the supplier's position is
    worse for us (e.g. higher price, shorter payment terms). The
    convention is: gap > 0 = we need them to move.
    """
    dimension: str
    category: str               # Pricing / Payment / Contract / SLA / Risk / Other
    supplier_position: str       # The supplier's stated position (may be text)
    buyer_target: str            # Our internal target (may be text)
    gap_value: Optional[float]   # Numeric gap where computable (always positive = bad for buyer)
    gap_percentage: Optional[float]  # Gap as % of buyer target (where applicable)
    gap_type: str                # "monetary" / "percentage" / "duration" / "qualitative"
    priority: str = ""           # Must-win / Must-have / Important / Nice-to-have
    notes: str = ""


@dataclass
class RiskFlag:
    """A commercial risk identified in the supplier's proposal."""
    clause: str
    severity: str               # "high" / "medium"
    supplier_position: str
    risk_description: str
    recommended_action: str


@dataclass
class GapAnalysis:
    """Complete gap analysis for a negotiation."""
    supplier_name: str
    analysis_date: str
    headline_value_supplier: Optional[float]    # Supplier's total ask
    headline_value_target: Optional[float]       # Our target total value
    estimated_tco: Optional[float]               # Total cost of ownership
    hidden_costs: list[dict] = field(default_factory=list)  # [{item, amount, notes}]
    gaps: list[DimensionGap] = field(default_factory=list)
    risk_flags: list[RiskFlag] = field(default_factory=list)
    total_value_gap: float = 0.0
    total_gap_percentage: float = 0.0
    dimensions_with_gap: int = 0
    dimensions_total: int = 0
    overall_risk: str = ""      # High / Medium / Low


def compute_gaps(
    supplier_name: str,
    analysis_date: str,
    dimensions: list[DimensionGap],
    headline_supplier: Optional[float] = None,
    headline_target: Optional[float] = None,
    hidden_costs: Optional[list[dict]] = None,
) -> GapAnalysis:
    """
    Compute the full gap analysis from a list of dimension gaps.

    Returns a GapAnalysis with aggregated metrics.

    Gotchas:
      - total_value_gap sums only monetary gap_values. Duration and qualitative
        gaps don't contribute to the value total — they're tracked separately.
      - total_gap_percentage is computed from headline values, not from
        summing individual percentage gaps (which would double-count).
    """
    analysis = GapAnalysis(
        supplier_name=supplier_name,
        analysis_date=analysis_date,
        headline_value_supplier=headline_supplier,
        headline_value_target=headline_target,
        estimated_tco=None,
        hidden_costs=hidden_costs or [],
        gaps=dimensions,
    )

    # Compute monetary gap total
    monetary_gaps = [g for g in dimensions if g.gap_type == "monetary" and g.gap_value is not None]
    analysis.total_value_gap = sum(g.gap_value for g in monetary_gaps)

    # Compute headline gap percentage
    if headline_supplier and headline_target and headline_target > 0:
        analysis.total_gap_percentage = round(
            ((headline_supplier - headline_target) / headline_target) * 100, 1
        )

    # Count dimensions with gap
    analysis.dimensions_total = len(dimensions)
    analysis.dimensions_with_gap = sum(
        1 for g in dimensions
        if (g.gap_value is not None and g.gap_value > 0) or g.gap_type == "qualitative"
    )

    # Compute TCO
    hidden_total = sum(c.get("amount", 0) for c in analysis.hidden_costs)
    if headline_supplier is not None:
        analysis.estimated_tco = headline_supplier + hidden_total

    return analysis


def flag_risks(proposal_terms: dict) -> list[RiskFlag]:
    """
    Scan proposal terms for commercial risks.

    Parameters:
      proposal_terms: dict with keys matching standard dimension names
        and values being the supplier's position text.

    Returns a list of RiskFlag objects.

    Gotchas:
      - This function catches common structural risks but cannot replace
        legal review. Always flag: "This analysis identifies commercial
        negotiation risks — it is not legal advice."
      - Risk flags are ordered: high severity first, then medium.
    """
    flags = []

    # Auto-renewal check
    auto_renewal = proposal_terms.get("auto_renewal", "").lower()
    if "auto" in auto_renewal and ("renew" in auto_renewal or "extend" in auto_renewal):
        opt_out_days = _extract_days(auto_renewal)
        if opt_out_days is not None and opt_out_days < 90:
            flags.append(RiskFlag(
                clause="Auto-Renewal",
                severity="high",
                supplier_position=proposal_terms.get("auto_renewal", ""),
                risk_description=(
                    f"Auto-renewal with only {opt_out_days}-day opt-out window. "
                    "Risk of unintended contract extension and price lock-in."
                ),
                recommended_action="Counter with no auto-renewal, or extend opt-out to ≥180 days.",
            ))
        elif "auto" in auto_renewal:
            flags.append(RiskFlag(
                clause="Auto-Renewal",
                severity="medium",
                supplier_position=proposal_terms.get("auto_renewal", ""),
                risk_description="Auto-renewal clause present. Review opt-out terms carefully.",
                recommended_action="Counter with explicit renewal requirement or ≥180-day opt-out.",
            ))

    # Liability cap check
    liability = proposal_terms.get("liability_cap", "").lower()
    if "limited" in liability or "cap" in liability:
        if any(term in liability for term in ["12 month", "annual fee", "monthly"]):
            flags.append(RiskFlag(
                clause="Liability Cap",
                severity="medium",
                supplier_position=proposal_terms.get("liability_cap", ""),
                risk_description="Liability capped at fees — may be insufficient for data breach or IP claims.",
                recommended_action="Negotiate uncapped carve-outs for data breach, IP infringement, and confidentiality.",
            ))

    # No termination for convenience
    term_convenience = proposal_terms.get("termination_convenience", "").lower()
    if not term_convenience or "not" in term_convenience or "no " in term_convenience:
        flags.append(RiskFlag(
            clause="Termination for Convenience",
            severity="high",
            supplier_position=proposal_terms.get("termination_convenience", "Not addressed"),
            risk_description="No termination for convenience — buyer is locked in for the full term.",
            recommended_action="Require termination for convenience with 90-day notice.",
        ))

    # No SLA penalties
    sla_penalties = proposal_terms.get("sla_penalties", "").lower()
    if not sla_penalties or "none" in sla_penalties or "no " in sla_penalties:
        flags.append(RiskFlag(
            clause="SLA Penalties",
            severity="high",
            supplier_position=proposal_terms.get("sla_penalties", "Not addressed"),
            risk_description="No SLA penalties — SLAs are aspirational without financial consequence.",
            recommended_action="Introduce service credits of 3–5% of monthly fees per SLA miss.",
        ))

    # Upfront payment
    payment_schedule = proposal_terms.get("payment_schedule", "").lower()
    if "upfront" in payment_schedule or "advance" in payment_schedule:
        flags.append(RiskFlag(
            clause="Payment Schedule",
            severity="high",
            supplier_position=proposal_terms.get("payment_schedule", ""),
            risk_description="Full or substantial upfront payment — cash flow risk and reduced leverage.",
            recommended_action="Counter with quarterly or monthly payments in arrears.",
        ))

    # Price escalation
    escalation = proposal_terms.get("price_escalation", "").lower()
    if escalation and ("uncapped" in escalation or "supplier discretion" in escalation):
        flags.append(RiskFlag(
            clause="Price Escalation",
            severity="high",
            supplier_position=proposal_terms.get("price_escalation", ""),
            risk_description="Price escalation uncapped or at supplier's discretion — unpredictable cost.",
            recommended_action="Cap at CPI or 3% (whichever lower), with 90-day advance notice.",
        ))

    # Data portability
    data_portability = proposal_terms.get("data_portability", "").lower()
    if not data_portability or "not addressed" in data_portability:
        flags.append(RiskFlag(
            clause="Data Portability",
            severity="medium",
            supplier_position=proposal_terms.get("data_portability", "Not addressed"),
            risk_description="Data portability and export rights not addressed — risk of vendor lock-in.",
            recommended_action="Require data export in standard formats at no additional cost on termination.",
        ))

    # Sort by severity
    severity_order = {"high": 0, "medium": 1}
    flags.sort(key=lambda f: severity_order.get(f.severity, 2))

    return flags


def compute_tco(
    headline_price: float,
    contract_years: int,
    hidden_costs: list[dict],
    annual_escalation_pct: float = 0.0,
) -> dict:
    """
    Compute Total Cost of Ownership over the contract term.

    Parameters:
      headline_price: total contract value at supplier's proposed rates
      contract_years: number of years
      hidden_costs: list of {item: str, amount: float, notes: str}
      annual_escalation_pct: annual price increase % (0 = fixed pricing)

    Returns:
      {
        "headline_price": float,
        "hidden_costs_total": float,
        "escalation_cost": float,
        "tco": float,
        "tco_vs_headline_pct": float,
        "annual_breakdown": [{year, base, escalation, hidden, total}]
      }

    Gotchas:
      - Escalation applies to the base price only, not hidden costs.
      - Hidden costs may be one-time (implementation) or recurring (annual support).
        Use the "recurring" flag in the cost dict to handle this correctly.
      - If contract_years is 0 or 1, escalation cost is 0.
    """
    hidden_total = sum(c.get("amount", 0) for c in hidden_costs)
    annual_base = headline_price / max(contract_years, 1)
    escalation_total = 0.0
    breakdown = []

    for year in range(1, contract_years + 1):
        esc_multiplier = (1 + annual_escalation_pct / 100) ** (year - 1)
        year_base = annual_base * esc_multiplier
        year_escalation = year_base - annual_base
        escalation_total += year_escalation

        year_hidden = sum(
            c.get("amount", 0)
            for c in hidden_costs
            if c.get("recurring", False) or year == 1
        )

        breakdown.append({
            "year": year,
            "base": round(year_base, 2),
            "escalation": round(year_escalation, 2),
            "hidden": round(year_hidden, 2),
            "total": round(year_base + year_hidden, 2),
        })

    tco = headline_price + escalation_total + hidden_total
    tco_pct = round(((tco - headline_price) / headline_price) * 100, 1) if headline_price > 0 else 0

    return {
        "headline_price": headline_price,
        "hidden_costs_total": round(hidden_total, 2),
        "escalation_cost": round(escalation_total, 2),
        "tco": round(tco, 2),
        "tco_vs_headline_pct": tco_pct,
        "annual_breakdown": breakdown,
    }


def render_gap_summary(analysis: GapAnalysis) -> str:
    """Render a human-readable gap analysis summary."""
    lines = [
        f"## Gap Analysis — {analysis.supplier_name}",
        f"Date: {analysis.analysis_date}",
        "",
    ]

    if analysis.headline_value_supplier is not None and analysis.headline_value_target is not None:
        lines += [
            f"Supplier ask:   ${analysis.headline_value_supplier:,.0f}",
            f"Our target:     ${analysis.headline_value_target:,.0f}",
            f"Headline gap:   ${analysis.total_value_gap:,.0f} ({analysis.total_gap_percentage:+.1f}%)",
        ]
        if analysis.estimated_tco:
            lines.append(f"Estimated TCO:  ${analysis.estimated_tco:,.0f}")
        lines.append("")

    lines += [
        f"{'Dimension':<30} {'Supplier':>15} {'Target':>15} {'Gap':>12} {'Priority':<12}",
        "-" * 90,
    ]

    for g in analysis.gaps:
        gap_str = f"${g.gap_value:,.0f}" if g.gap_value and g.gap_type == "monetary" else (str(g.gap_value) if g.gap_value else "Qualitative")
        lines.append(
            f"{g.dimension:<30} {g.supplier_position:>15} {g.buyer_target:>15} {gap_str:>12} {g.priority:<12}"
        )

    lines.append("-" * 90)
    lines.append(f"Dimensions with gap: {analysis.dimensions_with_gap} of {analysis.dimensions_total}")

    if analysis.risk_flags:
        lines += ["", f"Commercial risks identified: {len(analysis.risk_flags)}"]
        for rf in analysis.risk_flags:
            icon = "🔴" if rf.severity == "high" else "🟡"
            lines.append(f"  {icon} [{rf.severity.upper()}] {rf.clause}: {rf.risk_description[:80]}")

    return "\n".join(lines)


def save_analysis(analysis: GapAnalysis, output_dir: str) -> str:
    """Save a gap analysis to JSON."""
    safe_supplier = analysis.supplier_name.lower().replace(" ", "-")
    filename = f"{safe_supplier}-gap-analysis-{analysis.analysis_date}.json"
    path = Path(output_dir) / filename

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    data = {
        "supplier_name": analysis.supplier_name,
        "analysis_date": analysis.analysis_date,
        "headline_value_supplier": analysis.headline_value_supplier,
        "headline_value_target": analysis.headline_value_target,
        "estimated_tco": analysis.estimated_tco,
        "total_value_gap": analysis.total_value_gap,
        "total_gap_percentage": analysis.total_gap_percentage,
        "dimensions_with_gap": analysis.dimensions_with_gap,
        "dimensions_total": analysis.dimensions_total,
        "overall_risk": analysis.overall_risk,
        "hidden_costs": analysis.hidden_costs,
        "gaps": [asdict(g) for g in analysis.gaps],
        "risk_flags": [asdict(r) for r in analysis.risk_flags],
    }
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"[gap_analyzer] Saved to {path}", file=sys.stderr)
    return str(path)


def _extract_days(text: str) -> Optional[int]:
    """Extract a number of days from text like '30-day' or '30 days'."""
    import re
    match = re.search(r"(\d+)\s*[-–]?\s*day", text)
    return int(match.group(1)) if match else None


if __name__ == "__main__":
    # Demo gap analysis
    gaps = [
        DimensionGap("Total price", "Pricing", "$620,000", "$480,000", 140000, 29.2, "monetary", "Must-win"),
        DimensionGap("Payment terms", "Payment", "Net 30", "Net 60", None, None, "duration", "Must-win"),
        DimensionGap("Contract length", "Contract", "3 years fixed", "2+1 year option", None, None, "qualitative", "Important"),
        DimensionGap("SLA penalties", "SLA", "None", "5% credit per miss", None, None, "qualitative", "Must-have"),
        DimensionGap("Auto-renewal", "Contract", "12-month auto-renew", "No auto-renewal", None, None, "qualitative", "Must-have"),
        DimensionGap("Price escalation", "Pricing", "5% annual", "CPI or 3% cap", None, None, "qualitative", "Important"),
    ]

    analysis = compute_gaps(
        supplier_name="Salesforce",
        analysis_date="2026-03-21",
        dimensions=gaps,
        headline_supplier=620000,
        headline_target=480000,
        hidden_costs=[
            {"item": "Implementation", "amount": 45000, "recurring": False},
            {"item": "Premium support", "amount": 12000, "recurring": True, "notes": "Annual"},
        ],
    )

    analysis.risk_flags = flag_risks({
        "auto_renewal": "12-month auto-renewal with 30-day opt-out",
        "sla_penalties": "None",
        "termination_convenience": "Not permitted",
        "price_escalation": "5% annual increase at supplier discretion",
    })
    analysis.overall_risk = "High"

    print(render_gap_summary(analysis))
    print()
    tco = compute_tco(620000, 3, analysis.hidden_costs, 5.0)
    print(f"TCO: ${tco['tco']:,.0f} (+{tco['tco_vs_headline_pct']}% vs headline)")

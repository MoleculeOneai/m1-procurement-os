"""
calculate_savings.py — Savings Opportunity Identification
Part of the Molecule One Spend Intelligence Analyzer skill.

Screens categorised spend data for consolidation, price variance,
maverick spend, demand management, and benchmarking opportunities.
Produces a ranked savings opportunity register.

All savings figures are presented as ranges, never point estimates.
Every figure must have a stated basis — this is enforced in the output format.

Gotchas are in the docstrings — read them before use.
"""

from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Opportunity data structure
# ---------------------------------------------------------------------------

@dataclass
class SavingsOpportunity:
    """
    A single identified savings opportunity.

    opportunity_id: sequential reference (OPP-001, OPP-002...)
    category: procurement category
    opportunity_type: consolidation | price_variance | maverick | tail_spend |
                      demand_management | benchmark_gap | contract_renewal
    addressable_spend: the spend that could be affected (not total category spend)
    savings_pct_low: conservative savings estimate as % of addressable spend
    savings_pct_high: optimistic savings estimate as % of addressable spend
    savings_value_low: low estimate in £/$
    savings_value_high: high estimate in £/$
    basis: explanation of how the savings estimate was derived
    effort: high | medium | low (implementation effort)
    timeline: "0-3 months" | "3-6 months" | "6-12 months" | "12+ months"
    owner: suggested team responsible (procurement / finance / business unit)
    dependencies: list of str — what needs to happen first
    """
    opportunity_id: str
    category: str
    opportunity_type: str
    addressable_spend: float
    savings_pct_low: float
    savings_pct_high: float
    basis: str
    effort: str = "medium"
    timeline: str = "3-6 months"
    owner: str = "Procurement"
    dependencies: list = field(default_factory=list)

    @property
    def savings_value_low(self) -> float:
        return round(self.addressable_spend * self.savings_pct_low / 100, 2)

    @property
    def savings_value_high(self) -> float:
        return round(self.addressable_spend * self.savings_pct_high / 100, 2)

    def to_dict(self) -> dict:
        return {
            "opportunity_id": self.opportunity_id,
            "category": self.category,
            "type": self.opportunity_type,
            "addressable_spend": self.addressable_spend,
            "savings_low": self.savings_value_low,
            "savings_high": self.savings_value_high,
            "savings_pct_range": f"{self.savings_pct_low}–{self.savings_pct_high}%",
            "basis": self.basis,
            "effort": self.effort,
            "timeline": self.timeline,
            "owner": self.owner,
            "dependencies": self.dependencies
        }


# ---------------------------------------------------------------------------
# Opportunity screens
# ---------------------------------------------------------------------------

def screen_consolidation(spend_by_category_supplier: dict,
                         min_spend_threshold: float = 50000,
                         consolidation_threshold_suppliers: int = 5,
                         top_supplier_share_threshold: float = 0.4) -> list:
    """
    Identify categories where spend is fragmented across many suppliers
    and consolidation to fewer preferred suppliers would yield savings.

    spend_by_category_supplier: {category: {supplier: spend_value}}

    Returns a list of SavingsOpportunity objects.

    Consolidation savings benchmarks by category type:
      - Commoditised goods: 10–20% (high competition, easy to consolidate)
      - Services (non-complex): 8–15%
      - Complex services: 5–10% (consolidation harder to achieve)
      - Technology: 10–25% (volume licensing discounts are significant)

    Gotchas:
      - Consolidation savings are volume leverage savings — they require
        the consolidated supplier to absorb the volume at a better rate.
        Flag as "subject to supplier capacity confirmation."
      - Some category fragmentation is intentional (dual-sourcing for resilience,
        local supplier mandates). Always present as an opportunity to investigate,
        not a guaranteed saving.
      - Do not recommend consolidating to a single supplier in any category
        where supply risk is material. Recommend 2–3 preferred suppliers.
    """
    opportunities = []
    opp_count = 0

    for category, suppliers in spend_by_category_supplier.items():
        total_category_spend = sum(suppliers.values())
        if total_category_spend < min_spend_threshold:
            continue

        supplier_count = len(suppliers)
        if supplier_count < consolidation_threshold_suppliers:
            continue

        # Check if top supplier has low share (fragmented = high consolidation potential)
        top_spend = max(suppliers.values()) if suppliers else 0
        top_share = top_spend / total_category_spend if total_category_spend > 0 else 0

        if top_share > top_supplier_share_threshold:
            continue  # Already concentrated — low consolidation opportunity

        opp_count += 1
        opp_id = f"OPP-{opp_count:03d}"

        # Savings rate depends on category type and fragmentation level
        if supplier_count >= 10:
            low_pct, high_pct = 10, 18
        else:
            low_pct, high_pct = 6, 12

        # Addressable = spend with non-top suppliers (they can be consolidated)
        addressable = total_category_spend - top_spend

        opportunities.append(SavingsOpportunity(
            opportunity_id=opp_id,
            category=category,
            opportunity_type="consolidation",
            addressable_spend=round(addressable, 2),
            savings_pct_low=low_pct,
            savings_pct_high=high_pct,
            basis=(
                f"Category has {supplier_count} suppliers; top supplier holds only "
                f"{round(top_share*100,1)}% share. "
                f"Consolidating to 2–3 preferred suppliers typically yields {low_pct}–{high_pct}% "
                "savings through volume leverage. Subject to supplier capacity confirmation."
            ),
            effort="medium",
            timeline="3-6 months",
            dependencies=["Category strategy decision on number of preferred suppliers"]
        ))

    return opportunities


def screen_price_variance(spend_lines: list,
                          variance_threshold_pct: float = 15.0,
                          min_line_value: float = 1000) -> list:
    """
    Identify the same or similar items purchased at materially different
    prices across business units, time periods, or cost centres.

    spend_lines: list of normalised spend line dicts with description, amount,
                 cost_centre, and date fields.

    Returns a list of SavingsOpportunity objects for categories with high variance.

    Gotchas:
      - Price variance is not always a savings opportunity. Different prices
        may reflect different specifications, service levels, or contract terms.
        Always present as "investigate" not "save."
      - Comparing prices requires a unit rate, not just a line total.
        If unit data is not available, flag this and skip the screen rather
        than comparing non-comparable totals.
      - Price variance across time periods may reflect market movements,
        not procurement failure. Check the market index before blaming the team.
    """
    opportunities = []

    # Group lines by normalised description + category
    from collections import defaultdict
    description_groups = defaultdict(list)
    for line in spend_lines:
        key = str(line.get("category_l2", "")) + "|" + str(line.get("supplier_name_normalised", ""))
        amount = float(line.get("amount", 0) or 0)
        if amount >= min_line_value:
            description_groups[key].append(amount)

    opp_count = 100  # Start price variance IDs from 100 to avoid collision
    for key, amounts in description_groups.items():
        if len(amounts) < 3:
            continue

        min_price = min(amounts)
        max_price = max(amounts)
        if min_price <= 0:
            continue

        variance_pct = (max_price - min_price) / min_price * 100
        if variance_pct < variance_threshold_pct:
            continue

        opp_count += 1
        category = key.split("|")[0]
        total_spend = sum(amounts)
        # Addressable = difference between actual and if all at lowest price
        theoretical_min = min_price * len(amounts)
        addressable = total_spend - theoretical_min

        opportunities.append(SavingsOpportunity(
            opportunity_id=f"OPP-{opp_count:03d}",
            category=category,
            opportunity_type="price_variance",
            addressable_spend=round(addressable, 2),
            savings_pct_low=5,
            savings_pct_high=round(variance_pct * 0.6, 1),  # Conservative: recover 60% of variance
            basis=(
                f"Price variance of {round(variance_pct,1)}% detected across {len(amounts)} transactions. "
                f"Lowest observed: {min_price:,.0f}, Highest: {max_price:,.0f}. "
                "Investigate whether variation reflects specification differences or pricing inconsistency."
            ),
            effort="low",
            timeline="0-3 months",
            dependencies=["Confirm like-for-like specification before comparing prices"]
        ))

    return opportunities


def screen_price_variance_by_cost_centre(
        spend_lines: list,
        categories_to_check: list = None,
        variance_threshold_pct: float = 20.0,
        min_transactions_per_bu: int = 2,
        min_total_spend: float = 20000) -> list:
    """
    Detect suppliers whose average invoice rate differs materially across
    business units / cost centres. This is the correct way to catch rate
    card inconsistencies like Deloitte charging £14k/day to Tech but
    £8k/day to Finance.

    The key insight: use average invoice amount per cost centre as a proxy
    for unit rate. This works for professional services and SaaS where each
    invoice roughly represents one engagement or one period's subscription.
    It does NOT work for variable-quantity purchases (e.g. logistics, raw
    materials) — the function skips those categories by default.

    Parameters:
      spend_lines             — list of categorised spend line dicts
      categories_to_check     — L2 categories to analyse (default: Professional
                                Services, Technology & IT, Marketing & Communications,
                                HR & People Services). Avoid logistics/distribution.
      variance_threshold_pct  — flag if max_avg / min_avg exceeds this (default 20%)
      min_transactions_per_bu — minimum transactions in a BU to include in comparison
      min_total_spend         — minimum total supplier spend to be worth flagging

    Returns a list of SavingsOpportunity-compatible dicts (not SavingsOpportunity objects
    because we need richer metadata for the drill-down).

    Gotchas:
      - Average invoice ≠ unit rate when invoice sizes vary (e.g. one large
        statement of work vs many small ones). Treat findings as "investigate"
        not "confirmed variance."
      - A supplier may legitimately charge different rates for different service
        lines delivered to different BUs (e.g. audit vs consulting vs tax).
        Always present with the BU breakdown so the user can judge.
      - This function is a complement to screen_price_variance(), not a
        replacement. Run both and deduplicate results before presenting.
    """
    from collections import defaultdict

    if categories_to_check is None:
        categories_to_check = [
            "Professional Services",
            "Technology & IT",
            "Marketing & Communications",
            "HR & People Services",
            "Financial Services",
        ]

    # Group: supplier → cost_centre → list of invoice amounts
    supplier_bu_amounts = defaultdict(lambda: defaultdict(list))

    for line in spend_lines:
        cat = str(line.get("category_l2", ""))
        if cat not in categories_to_check:
            continue

        supplier = str(line.get("supplier_name_normalised", line.get("supplier_name_raw", ""))).strip()
        bu = str(line.get("cost_centre", "")).strip() or "Unknown BU"
        amount = float(line.get("amount", 0) or 0)

        if amount <= 0 or not supplier:
            continue

        supplier_bu_amounts[supplier][bu].append(amount)

    opportunities = []
    opp_count = 150  # Price variance by cost centre: IDs from 150

    for supplier, bu_data in supplier_bu_amounts.items():
        # Only compare BUs with enough transactions
        eligible_bus = {
            bu: amounts
            for bu, amounts in bu_data.items()
            if len(amounts) >= min_transactions_per_bu
        }

        if len(eligible_bus) < 2:
            continue  # Need at least 2 BUs to compare

        # Compute average invoice per BU
        bu_avgs = {bu: sum(amounts) / len(amounts) for bu, amounts in eligible_bus.items()}
        total_supplier_spend = sum(sum(amounts) for amounts in eligible_bus.values())

        if total_supplier_spend < min_total_spend:
            continue

        max_avg_bu = max(bu_avgs, key=lambda b: bu_avgs[b])
        min_avg_bu = min(bu_avgs, key=lambda b: bu_avgs[b])
        max_avg = bu_avgs[max_avg_bu]
        min_avg = bu_avgs[min_avg_bu]

        if min_avg <= 0:
            continue

        variance_pct = (max_avg - min_avg) / min_avg * 100

        if variance_pct < variance_threshold_pct:
            continue

        opp_count += 1

        # Build BU detail string for basis
        bu_detail = "; ".join(
            f"{bu}: avg {sum(eligible_bus[bu])/len(eligible_bus[bu]):,.0f} "
            f"({len(eligible_bus[bu])} invoices, {sum(eligible_bus[bu]):,.0f} total)"
            for bu in sorted(bu_avgs, key=lambda b: bu_avgs[b], reverse=True)
        )

        # Addressable: spend above the lowest BU average rate
        addressable = sum(
            max(0, sum(amounts) - (min_avg * len(amounts)))
            for bu, amounts in eligible_bus.items()
        )

        opportunities.append({
            "id": f"OPP-{opp_count:03d}",
            "type": "price_variance",
            "category": next(
                (str(line.get("category_l2", "")) for line in spend_lines
                 if str(line.get("supplier_name_normalised", "")) == supplier),
                "Unknown"
            ),
            "description": (
                f"{supplier}: average invoice rate varies {round(variance_pct, 0):.0f}% "
                f"across business units — possible rate card inconsistency"
            ),
            "savings_low": round(addressable * 0.05, 2),
            "savings_high": round(addressable * 0.5, 2),  # Up to 50% of variance is recoverable
            "horizon": "quick",
            "effort": "Low",
            "priority": opp_count - 149,
            "basis": (
                f"Average invoice amount for {supplier} varies {round(variance_pct,1)}% "
                f"across BUs: {bu_detail}. "
                f"Highest-rate BU ({max_avg_bu}: avg {max_avg:,.0f}) vs "
                f"lowest-rate BU ({min_avg_bu}: avg {min_avg:,.0f}). "
                "Investigate whether rates reflect different service lines or a rate card inconsistency. "
                "If inconsistency confirmed, renegotiate to lowest observed rate across all BUs."
            ),
            "affected_suppliers": [supplier],
            "actions": [
                f"Request itemised rate card from {supplier} for all BUs",
                f"Compare {max_avg_bu} and {min_avg_bu} engagement scopes to confirm like-for-like",
                "If rates are comparable, renegotiate all BUs to the lowest confirmed rate",
                "Add to next contract renewal scope with standardised rate card clause",
            ],
            "_detail": {
                "supplier": supplier,
                "total_spend": round(total_supplier_spend, 2),
                "bu_averages": {bu: round(avg, 2) for bu, avg in bu_avgs.items()},
                "bu_transaction_counts": {bu: len(amounts) for bu, amounts in eligible_bus.items()},
                "variance_pct": round(variance_pct, 1),
                "addressable_spend": round(addressable, 2),
            }
        })

    # Sort by variance_pct descending so biggest discrepancies surface first
    opportunities.sort(key=lambda x: x["_detail"]["variance_pct"], reverse=True)

    return opportunities


def screen_maverick_spend(spend_lines: list,
                          preferred_suppliers: dict = None,
                          maverick_threshold_pct: float = 20.0) -> list:
    """
    Identify spend with non-preferred suppliers in categories where
    a preferred supplier or contract exists.

    preferred_suppliers: {category: [supplier_name, ...]}

    Gotchas:
      - Maverick spend is a compliance and savings issue simultaneously.
        It should be reported to category managers and business units, not just
        presented as a financial opportunity.
      - Some maverick spend reflects a genuine gap in the preferred supplier's
        coverage (e.g. a preferred hotel that isn't available in a location).
        Investigate before assuming non-compliance.
      - If preferred_suppliers is None or empty, this screen cannot run.
        Note this in the output rather than skipping silently.
    """
    if not preferred_suppliers:
        return [{
            "note": "Maverick spend screen skipped — no preferred supplier list provided. "
                    "Ask the user for their contracted/preferred supplier list to enable this screen."
        }]

    opportunities = []
    opp_count = 200

    from collections import defaultdict
    category_spend = defaultdict(lambda: {"total": 0.0, "preferred": 0.0, "maverick": 0.0, "maverick_suppliers": set()})

    for line in spend_lines:
        cat = str(line.get("category_l2", "Unknown"))
        supplier = str(line.get("supplier_name_normalised", ""))
        amount = float(line.get("amount", 0) or 0)

        if cat not in preferred_suppliers:
            continue

        category_spend[cat]["total"] += amount
        preferred_list = [s.upper() for s in preferred_suppliers[cat]]

        if supplier.upper() in preferred_list:
            category_spend[cat]["preferred"] += amount
        else:
            category_spend[cat]["maverick"] += amount
            category_spend[cat]["maverick_suppliers"].add(supplier)

    for cat, data in category_spend.items():
        if data["total"] == 0:
            continue

        maverick_rate = data["maverick"] / data["total"] * 100
        if maverick_rate < maverick_threshold_pct:
            continue

        opp_count += 1
        # Savings estimate: route maverick spend to preferred supplier
        # Preferred supplier typically 10–15% cheaper (reason it was preferred)
        opportunities.append(SavingsOpportunity(
            opportunity_id=f"OPP-{opp_count:03d}",
            category=cat,
            opportunity_type="maverick_spend",
            addressable_spend=round(data["maverick"], 2),
            savings_pct_low=8,
            savings_pct_high=15,
            basis=(
                f"Maverick spend rate of {round(maverick_rate,1)}% in {cat} "
                f"({data['total'] - data['preferred']:,.0f} of {data['total']:,.0f} total). "
                f"Maverick suppliers: {', '.join(list(data['maverick_suppliers'])[:5])}. "
                "Routing spend to preferred suppliers typically yields 8–15% savings."
            ),
            effort="low",
            timeline="0-3 months",
            dependencies=["Business unit awareness campaign", "Preferred supplier capacity confirmation"]
        ))

    return opportunities


def benchmark_against_market(category: str, current_spend: float,
                              estimated_volume: float,
                              geography: str = "UK") -> dict:
    """
    Compare a category's current implied unit rate against market benchmarks.

    Returns a benchmark result dict with gap analysis.

    Gotchas:
      - Benchmark rates in this function are directional estimates based on
        Molecule One's procurement intelligence. They are not guaranteed rates.
      - Volume matters significantly — a £100k buyer and a £10M buyer in the
        same category get very different rates. Rates below are for mid-market
        organisations (£500k–£5M annual category spend).
      - Always present savings as a range, never a point estimate.
      - State "directional only" and recommend an RFP to quantify precisely.
    """
    # Directional benchmark ranges by category (low end = market median, high = best-in-class)
    # Savings % vs typical mid-market buyer paying list/standard rates
    BENCHMARK_SAVINGS_RANGES = {
        "Professional Services": (10, 25, "Day rate negotiation + volume commitment"),
        "Technology & IT": (15, 30, "Volume licensing + competitive tender"),
        "Marketing & Communications": (12, 25, "Agency consolidation + rate card negotiation"),
        "Travel & Expenses": (10, 20, "Travel policy + preferred hotel/airline programme"),
        "HR & People Services": (8, 18, "Preferred agency + volume rebates"),
        "Logistics & Distribution": (8, 18, "Lane consolidation + volume leverage"),
        "Facilities & Real Estate": (8, 15, "FM bundling + benchmark renegotiation"),
        "Financial Services": (5, 15, "Competitive tender + fee benchmarking"),
        "Office Supplies": (10, 20, "Catalogue contract + compliance"),
        "Facilities Consumables": (8, 15, "Contract + managed service"),
    }

    if current_spend <= 0 or estimated_volume <= 0:
        return {"error": "current_spend and estimated_volume must be positive"}

    current_unit_rate = current_spend / estimated_volume
    match = BENCHMARK_SAVINGS_RANGES.get(category)

    if not match:
        return {
            "category": category,
            "note": f"No benchmark data available for '{category}'. "
                    "Recommend running a competitive RFP to establish market rate.",
            "current_unit_rate": current_unit_rate,
            "recommendation": "RFP to establish benchmark"
        }

    low_pct, high_pct, lever = match
    savings_low = current_spend * low_pct / 100
    savings_high = current_spend * high_pct / 100

    return {
        "category": category,
        "current_spend": current_spend,
        "estimated_volume": estimated_volume,
        "current_unit_rate": round(current_unit_rate, 4),
        "benchmark_savings_range": f"{low_pct}–{high_pct}%",
        "estimated_savings_low": round(savings_low, 2),
        "estimated_savings_high": round(savings_high, 2),
        "primary_savings_lever": lever,
        "geography": geography,
        "caveat": (
            "Directional estimate only. Based on Molecule One's procurement intelligence "
            f"for {geography} mid-market organisations. Actual savings depend on specification, "
            "volume commitment, and market conditions at time of going to market. "
            "Recommend competitive RFP to quantify precisely."
        )
    }


# ---------------------------------------------------------------------------
# Opportunity register
# ---------------------------------------------------------------------------

def build_opportunity_register(opportunities: list,
                                 exclude_types: list = None) -> dict:
    """
    Consolidate all opportunity screens into a ranked register.

    Sorts by savings_value_high descending (biggest opportunity first).
    Groups into: Quick Wins (<3 months), Medium-term (3-12 months), Strategic (12+ months).

    Gotchas:
      - Total savings is not additive — some opportunities overlap
        (e.g. consolidation + price variance in the same category).
        State total as "up to £X" not "£X savings identified."
      - Never present quick wins as guaranteed. They still require supplier
        engagement and stakeholder buy-in.
    """
    if exclude_types:
        opportunities = [o for o in opportunities if isinstance(o, SavingsOpportunity)
                         and o.opportunity_type not in exclude_types]

    valid_opps = [o for o in opportunities if isinstance(o, SavingsOpportunity)]
    valid_opps.sort(key=lambda x: x.savings_value_high, reverse=True)

    quick_wins = [o for o in valid_opps if o.timeline == "0-3 months"]
    medium_term = [o for o in valid_opps if o.timeline in ("3-6 months", "6-12 months")]
    strategic = [o for o in valid_opps if o.timeline == "12+ months"]

    total_low = sum(o.savings_value_low for o in valid_opps)
    total_high = sum(o.savings_value_high for o in valid_opps)

    return {
        "total_opportunities": len(valid_opps),
        "total_savings_range": {
            "low": round(total_low, 2),
            "high": round(total_high, 2),
            "caveat": "Total is indicative. Opportunities may overlap — do not sum without overlap analysis."
        },
        "quick_wins": [o.to_dict() for o in quick_wins],
        "medium_term": [o.to_dict() for o in medium_term],
        "strategic": [o.to_dict() for o in strategic],
        "full_register": [o.to_dict() for o in valid_opps]
    }

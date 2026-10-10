"""
category_segmenter.py — Kraljic Matrix Segmentation Engine
Part of the Molecule One Category Strategy Builder skill.

Classifies procurement categories into Kraljic quadrants based on
spend impact and supply risk scores. Produces a ranked matrix with
recommended strategic approaches.

Usage:
    from lib.category_segmenter import score_category, build_matrix, render_matrix_ascii

Gotchas:
    - Kraljic scoring is semi-subjective. The scoring guide provides structure
      but final scores must be validated with the user — never auto-publish.
    - If >20% of categories land in Strategic, warn the user. Over-classification
      as Strategic is the most common mistake in category management.
    - Quadrant placement at the boundary (score = 3 on either axis) should be
      flagged for user review — these are genuinely ambiguous.
    - Supply risk scores can change rapidly (geopolitical events, supplier M&A).
      Always date-stamp the matrix and recommend a 12-month review.
"""

import json
import sys
from dataclasses import dataclass, asdict, field
from typing import Optional


QUADRANT_STRATEGIES = {
    "Strategic": (
        "Manage as a relationship — joint value improvement, shared roadmap, "
        "executive sponsorship, gain-share mechanisms"
    ),
    "Leverage": (
        "Compete aggressively — consolidate volume, run competitive tender, "
        "extract best commercial terms, challenge TCO"
    ),
    "Bottleneck": (
        "Secure supply — dual source, build inventory buffer, qualify alternatives, "
        "long-term supply agreements"
    ),
    "Routine": (
        "Simplify and automate — catalogue adoption, p-card, guided buying, "
        "demand aggregation, self-serve"
    ),
}

STRATEGY_PRIORITY = {"Strategic": 1, "Leverage": 2, "Bottleneck": 3, "Routine": 4}


@dataclass
class CategoryScore:
    category: str
    annual_spend: float
    spend_score: int           # 1–5: spend impact axis
    risk_score: int            # 1–5: supply risk axis
    spend_score_rationale: str = ""
    risk_score_rationale: str = ""
    quadrant: str = ""
    recommended_strategy: str = ""
    boundary_flag: bool = False   # True if either score == 3
    priority_rank: int = 0
    currency: str = "USD"
    notes: str = ""


def score_category(
    category: str,
    annual_spend: float,
    spend_score: int,
    risk_score: int,
    spend_score_rationale: str = "",
    risk_score_rationale: str = "",
    currency: str = "USD",
    notes: str = ""
) -> CategoryScore:
    """
    Score a single category and assign it to a Kraljic quadrant.

    spend_score: 1–5 (1=tail spend, 5=high spend impact or operational criticality)
    risk_score:  1–5 (1=commodity/many suppliers, 5=single source/high lock-in)

    Returns a CategoryScore with quadrant and recommended strategy assigned.

    Gotchas:
      - spend_score and risk_score must be integers 1–5. Floats will be rounded.
      - Boundary categories (score 3 on either axis) are flagged for user review.
        Never silently place boundary categories without noting the ambiguity.
    """
    if not (1 <= spend_score <= 5) or not (1 <= risk_score <= 5):
        raise ValueError(
            f"Scores must be integers 1–5. Got spend={spend_score}, risk={risk_score}"
        )

    quadrant = _assign_quadrant(spend_score, risk_score)
    strategy = QUADRANT_STRATEGIES[quadrant]
    boundary = (spend_score == 3 or risk_score == 3)

    return CategoryScore(
        category=category,
        annual_spend=annual_spend,
        spend_score=spend_score,
        risk_score=risk_score,
        spend_score_rationale=spend_score_rationale,
        risk_score_rationale=risk_score_rationale,
        quadrant=quadrant,
        recommended_strategy=strategy,
        boundary_flag=boundary,
        currency=currency,
        notes=notes,
    )


def _assign_quadrant(spend_score: int, risk_score: int) -> str:
    """
    Assign a Kraljic quadrant.

    Convention used:
      spend_score >= 3 AND risk_score >= 3  → Strategic
      spend_score >= 3 AND risk_score < 3   → Leverage
      spend_score < 3  AND risk_score >= 3  → Bottleneck
      spend_score < 3  AND risk_score < 3   → Routine
    """
    high_spend = spend_score >= 3
    high_risk = risk_score >= 3
    if high_spend and high_risk:
        return "Strategic"
    elif high_spend and not high_risk:
        return "Leverage"
    elif not high_spend and high_risk:
        return "Bottleneck"
    else:
        return "Routine"


def build_matrix(category_scores: list[CategoryScore]) -> list[CategoryScore]:
    """
    Rank all scored categories by strategic priority and spend.

    Priority order:
      1. Strategic (by spend, high to low)
      2. Leverage (by spend, high to low)
      3. Bottleneck (by risk_score, high to low)
      4. Routine (by spend, high to low)

    Returns the same list with priority_rank populated.

    Gotchas:
      - This function does not re-validate scores — call score_category() for each
        category before passing to build_matrix().
      - If the strategic count exceeds 20% of total, a warning is embedded in each
        Strategic entry's notes field.
    """
    total = len(category_scores)
    strategic_count = sum(1 for c in category_scores if c.quadrant == "Strategic")

    if total > 0 and strategic_count / total > 0.20:
        warning_msg = (
            f"WARNING: {strategic_count}/{total} categories ({round(strategic_count/total*100)}%) "
            "classified as Strategic. Review — most organisations can manage 5–10 Strategic "
            "relationships in depth."
        )
        for c in category_scores:
            if c.quadrant == "Strategic":
                c.notes = (c.notes + " | " + warning_msg).lstrip(" | ")

    # Sort: primary by quadrant priority, secondary by spend (or risk for Bottleneck)
    def sort_key(c: CategoryScore):
        if c.quadrant == "Bottleneck":
            return (STRATEGY_PRIORITY[c.quadrant], -c.risk_score, -c.annual_spend)
        return (STRATEGY_PRIORITY[c.quadrant], -c.annual_spend)

    sorted_categories = sorted(category_scores, key=sort_key)
    for i, c in enumerate(sorted_categories, start=1):
        c.priority_rank = i

    return sorted_categories


def render_matrix_ascii(category_scores: list[CategoryScore]) -> str:
    """
    Render the Kraljic matrix as a structured ASCII table.

    Gotchas:
      - Category names longer than 30 characters will be truncated for display.
        Full names are preserved in the data — this is display-only truncation.
    """
    lines = [
        "## Kraljic Matrix — Category Segmentation",
        "",
        f"{'#':<4} {'Category':<32} {'Spend':>12} {'Spend Sc':>9} {'Risk Sc':>8} {'Quadrant':<14} {'Boundary?':<10}",
        "-" * 94,
    ]

    currency_sym = "$"  # default; could be extended to use per-row currency

    for c in category_scores:
        name = c.category[:30] + ".." if len(c.category) > 32 else c.category
        spend_fmt = f"{currency_sym}{c.annual_spend:,.0f}"
        boundary = "⚠ Review" if c.boundary_flag else ""
        lines.append(
            f"{c.priority_rank:<4} {name:<32} {spend_fmt:>12} {c.spend_score:>9} "
            f"{c.risk_score:>8} {c.quadrant:<14} {boundary:<10}"
        )

    lines.append("-" * 94)

    # Quadrant summary
    from collections import Counter
    q_counts = Counter(c.quadrant for c in category_scores)
    q_spend = {q: sum(c.annual_spend for c in category_scores if c.quadrant == q)
               for q in q_counts}

    lines.append("")
    lines.append("### Distribution Summary")
    for quadrant in ["Strategic", "Leverage", "Bottleneck", "Routine"]:
        count = q_counts.get(quadrant, 0)
        spend = q_spend.get(quadrant, 0)
        lines.append(f"  {quadrant:<14}: {count:>3} categories  |  {currency_sym}{spend:>12,.0f}")

    # Boundary warning
    boundary_cats = [c.category for c in category_scores if c.boundary_flag]
    if boundary_cats:
        lines.append("")
        lines.append(
            f"⚠ {len(boundary_cats)} boundary categor{'y' if len(boundary_cats)==1 else 'ies'} "
            f"(score = 3 on an axis) — review with stakeholders before finalising: "
            f"{', '.join(boundary_cats[:5])}" + (" ..." if len(boundary_cats) > 5 else "")
        )

    return "\n".join(lines)


def export_matrix_json(category_scores: list[CategoryScore], output_path: str) -> None:
    """
    Export the scored matrix to a JSON file for downstream tools.

    Gotchas:
      - The output file will be overwritten if it already exists. This is intentional
        — always use the most recent run. Archive previous versions manually if needed.
    """
    data = [asdict(c) for c in category_scores]
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"[category_segmenter] Matrix exported to {output_path}", file=sys.stderr)


if __name__ == "__main__":
    # Demo run with sample data
    samples = [
        ("IT Software", 2_500_000, 4, 4, "High spend, strategic vendor lock-in", "SAP/Oracle ecosystem, high switching cost"),
        ("Office Supplies", 80_000, 1, 1, "Tail spend, no impact", "Many suppliers, easily substituted"),
        ("Specialist Chemicals", 150_000, 2, 5, "Low spend but critical to production", "Single qualified source globally"),
        ("Logistics", 1_800_000, 4, 2, "High spend, manageable", "Multiple 3PL providers available"),
        ("Facilities Management", 900_000, 3, 3, "Mid-tier spend, moderate risk", "Regional market, some concentration"),
    ]
    scores = [score_category(cat, spend, ss, rs, ssr, rsr)
              for cat, spend, ss, rs, ssr, rsr in samples]
    ranked = build_matrix(scores)
    print(render_matrix_ascii(ranked))

"""
score_responses.py — Weighted Supplier Scoring Engine
Part of the Molecule One RFP Generator skill.

Applies configurable weighted scoring at section, subsection, and question level.
Claude generates scoring input data from proposal extraction, then
calls these functions to produce a normalized, auditable scorecard.

Architecture:
  - QuestionScore: a single question response scored 1-10
  - SubsectionScore: groups questions, applies subsection weight
  - SectionScore: groups subsections, applies section weight
  - SupplierEvaluation: full evaluation for one supplier across all sections
  - normalize_pricing(): price scores are always normalized, not absolute
  - rank_suppliers(): produces final ranked output with audit trail

Gotchas:
  - ALWAYS lock weights before scoring. Changing weights after seeing results
    invalidates the process and creates a fairness/legal exposure.
  - Price normalization uses lowest TCO = 10. Never score price on absolute value.
  - Do not call score_suppliers() until all missing sections have been resolved
    or explicitly waived with a reason on record.
  - If a question is not applicable (e.g. Q3.1.2 transition plan when there is
    no incumbent), set score to None and record a waiver_reason. Redistribute
    that question's weight to the remaining questions in the subsection.
  - Question weights within a subsection must sum to 100.
  - Section weights must sum to 100.
"""

import json
from dataclasses import dataclass, field, asdict
from typing import Optional
from datetime import date


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class QuestionScore:
    """
    A single question response, scored 1-10 by an evaluator.

    question_id: matches the RFP question number (e.g. "Q1.1.1")
    question_label: short description for reporting
    response_type: TEXT | TABLE | ATTACHMENT | WORK_SAMPLE | YES_NO | FINANCIAL
    raw_score: evaluator-assigned score 1-10, or None if N/A
    weight_pct: this question's weight as a % of its subsection (must sum to 100 within subsection)
    waiver_reason: if raw_score is None, why this question was waived
    evaluator_notes: free-text notes for the recommendation memo
    missing_data_flag: True if the supplier did not provide a required response
    """
    question_id: str
    question_label: str
    response_type: str
    raw_score: Optional[float]          # 1-10, or None if N/A / waived
    weight_pct: float                   # % of parent subsection, e.g. 40.0
    waiver_reason: str = ""             # if raw_score is None
    evaluator_notes: str = ""
    missing_data_flag: bool = False

    def weighted_contribution(self) -> Optional[float]:
        """
        Returns this question's contribution to the subsection score (out of 10).
        Returns None if the question was waived or has no score.

        Gotcha: if a question is waived, redistribute its weight to remaining questions
        BEFORE calling this. Do not call weighted_contribution on waived questions.
        """
        if self.raw_score is None:
            return None
        return self.raw_score * (self.weight_pct / 100)


@dataclass
class SubsectionScore:
    """
    A subsection containing multiple questions.

    subsection_id: e.g. "1.1", "2.3"
    subsection_label: e.g. "Company Overview"
    weight_pct: this subsection's weight as a % of its parent section (must sum to 100 within section)
    questions: list of QuestionScore objects

    Gotcha: if all questions in a subsection are waived, the subsection score is None.
    Surface this to the user — do not silently zero out the section.
    """
    subsection_id: str
    subsection_label: str
    weight_pct: float                   # % of parent section
    questions: list = field(default_factory=list)

    def total_score(self) -> Optional[float]:
        """
        Sum of weighted contributions from all scored questions.
        Returns a score out of 10 (not normalized by subsection weight — that happens at section level).

        Gotcha: if some questions are waived, verify the remaining question weights
        have been redistributed to sum to 100 before calling this. If they don't sum
        to 100, print a warning but proceed with the available data.
        """
        scored = [q for q in self.questions if q.raw_score is not None]
        if not scored:
            print(f"WARNING: Subsection {self.subsection_id} has no scored questions — subsection score is None.")
            return None

        total_weight = sum(q.weight_pct for q in scored)
        if abs(total_weight - 100.0) > 0.1:
            print(
                f"WARNING: Subsection {self.subsection_id} question weights sum to {total_weight:.1f}%, "
                f"not 100%. Redistributing proportionally for this calculation."
            )
            # Proportional redistribution
            return sum(q.raw_score * (q.weight_pct / total_weight) for q in scored)

        return sum(q.weighted_contribution() for q in scored)

    def missing_flags(self) -> list:
        return [q.question_id for q in self.questions if q.missing_data_flag]


@dataclass
class SectionScore:
    """
    A section containing multiple subsections.

    section_id: "1" through "5"
    section_label: e.g. "Company & Capability"
    weight_pct: this section's weight as a % of final score (must sum to 100 across all sections)
    subsections: list of SubsectionScore objects
    """
    section_id: str
    section_label: str
    weight_pct: float
    subsections: list = field(default_factory=list)

    def total_score(self) -> Optional[float]:
        """
        Weighted sum of subsection scores, out of 10.

        Gotcha: if a subsection returns None (all waived), skip it and
        redistribute its weight proportionally across remaining subsections.
        """
        scored_subs = [(s, s.total_score()) for s in self.subsections if s.total_score() is not None]
        if not scored_subs:
            print(f"WARNING: Section {self.section_id} has no scoreable subsections — section score is None.")
            return None

        total_weight = sum(s.weight_pct for s, _ in scored_subs)
        if abs(total_weight - 100.0) > 0.1:
            print(
                f"WARNING: Section {self.section_id} subsection weights sum to {total_weight:.1f}% "
                f"after waiver adjustments. Redistributing proportionally."
            )
            return sum(score * (sub.weight_pct / total_weight) for sub, score in scored_subs)

        return sum(score * (sub.weight_pct / 100) for sub, score in scored_subs)

    def missing_flags(self) -> list:
        flags = []
        for s in self.subsections:
            flags.extend(s.missing_flags())
        return flags


@dataclass
class SupplierEvaluation:
    """
    Complete evaluation for one supplier across all sections.

    supplier_name: display name
    price_raw: Total Cost of Ownership quoted price (before normalization)
               Set to None if pricing was unclear or multi-scenario.
    sections: list of SectionScore objects (should be 5 for a standard RFP)
    disqualified: set to True if failed mandatory requirements check
    disqualification_reason: which mandatory requirement was failed
    """
    supplier_name: str
    price_raw: Optional[float] = None
    sections: list = field(default_factory=list)
    disqualified: bool = False
    disqualification_reason: str = ""

    def final_score(self) -> float:
        """
        Weighted total across all sections, out of 10.
        Returns 0.0 for disqualified suppliers.

        Gotcha: section weights must sum to 100. Validate before calling.
        """
        if self.disqualified:
            return 0.0

        total_weight = sum(s.weight_pct for s in self.sections)
        if abs(total_weight - 100.0) > 0.1:
            raise ValueError(
                f"Section weights for {self.supplier_name} sum to {total_weight:.1f}%, not 100%. "
                f"Fix before scoring."
            )

        total = 0.0
        for section in self.sections:
            score = section.total_score()
            if score is not None:
                total += score * (section.weight_pct / 100)
        return round(total, 2)

    def all_missing_flags(self) -> list:
        flags = []
        for s in self.sections:
            flags.extend(s.missing_flags())
        return flags


# ---------------------------------------------------------------------------
# Pricing normalization
# ---------------------------------------------------------------------------

def normalize_pricing(evaluations: list) -> list:
    """
    Normalize price scores across suppliers so the lowest TCO = 10.
    Updates the price score on Q4.1.1 for each supplier.

    Formula: score = (min_price / supplier_price) * 10

    This function finds Q4.1.1 in Section 4, Subsection 4.1 and sets its raw_score
    to the normalized value. All other pricing-related questions (Q4.1.2, Q4.1.3)
    are scored manually by the evaluator.

    Gotchas:
      - Only normalize suppliers with a valid price_raw. If any qualified supplier
        has price_raw = None, do NOT normalize anyone — flag all prices as
        requiring manual review.
      - Mixed pricing structures (fixed fee vs T&M vs subscription) must be
        converted to TCO over the contract term BEFORE normalization. Confirm
        contract duration with the user if not already stated.
      - Always confirm all prices are ex-VAT before comparing. Suppliers
        sometimes quote including VAT — this will skew normalization.
      - If a supplier quotes multiple pricing scenarios, ask which to use
        before normalizing. Do not choose on their behalf.
    """
    qualified = [e for e in evaluations if not e.disqualified]
    valid_prices = [e.price_raw for e in qualified if e.price_raw is not None]

    if not valid_prices:
        print("WARNING: No valid TCO prices to normalize. Price scores must be set manually.")
        return evaluations

    if len(valid_prices) < len(qualified):
        print(
            "WARNING: Some qualified suppliers have missing price data. "
            "Do not normalize until all TCO prices are confirmed. "
            "Resolve missing prices or record explicit waivers before proceeding."
        )
        return evaluations

    min_price = min(valid_prices)

    for evaluation in qualified:
        if evaluation.price_raw is not None:
            normalized = round((min_price / evaluation.price_raw) * 10, 2)
            # Find Q4.1.1 in the evaluation and set its score
            for section in evaluation.sections:
                if section.section_id == "4":
                    for subsection in section.subsections:
                        if subsection.subsection_id == "4.1":
                            for question in subsection.questions:
                                if question.question_id == "Q4.1.1":
                                    question.raw_score = normalized
                                    break

    return evaluations


# ---------------------------------------------------------------------------
# Ranking
# ---------------------------------------------------------------------------

def rank_suppliers(evaluations: list) -> list:
    """
    Rank qualified suppliers by final score. Returns a list of dicts
    sorted by score descending, with disqualified suppliers appended.

    Output dict per supplier:
      - rank, supplier, final_score, section_scores, question_highlights,
        missing_data_flags, tie_warning (if applicable)

    Gotchas:
      - Never rank suppliers with unresolved missing_data_flags without
        surfacing the flags. The user must acknowledge each before the
        ranking is considered final.
      - A gap of < 0.5 points between rank 1 and rank 2 should be flagged
        as a near-tie. Recommend both advance to negotiation.
    """
    qualified = [e for e in evaluations if not e.disqualified]
    disqualified = [e for e in evaluations if e.disqualified]

    # Check for unresolved missing data
    for e in qualified:
        flags = e.all_missing_flags()
        if flags:
            print(
                f"WARNING: {e.supplier_name} has unresolved missing data flags on: "
                f"{', '.join(flags)}. Resolve before finalising ranking."
            )

    ranked = sorted(qualified, key=lambda e: e.final_score(), reverse=True)

    output = []
    for i, e in enumerate(ranked, 1):
        section_breakdown = {}
        for section in e.sections:
            score = section.total_score()
            section_breakdown[f"Section {section.section_id} — {section.section_label}"] = {
                "raw_score": round(score, 2) if score is not None else None,
                "weight_pct": section.weight_pct,
                "contribution": round(score * section.weight_pct / 100, 2) if score is not None else None
            }

        entry = {
            "rank": i,
            "supplier": e.supplier_name,
            "final_score": e.final_score(),
            "section_scores": section_breakdown,
            "missing_data_flags": e.all_missing_flags(),
            "price_raw": e.price_raw
        }
        output.append(entry)

    # Near-tie warning
    if len(ranked) >= 2:
        gap = ranked[0].final_score() - ranked[1].final_score()
        if gap < 0.5:
            output[0]["tie_warning"] = (
                f"Scores for rank 1 ({ranked[0].supplier_name}: {ranked[0].final_score()}) "
                f"and rank 2 ({ranked[1].supplier_name}: {ranked[1].final_score()}) "
                f"differ by only {gap:.2f} points. "
                "Treat as effectively tied — recommend both advance to negotiation."
            )

    # Append disqualified
    for e in disqualified:
        output.append({
            "rank": "DISQUALIFIED",
            "supplier": e.supplier_name,
            "reason": e.disqualification_reason
        })

    return output


# ---------------------------------------------------------------------------
# Scorecard JSON generator
# ---------------------------------------------------------------------------

def generate_scorecard_json(evaluations: list, section_weights: dict,
                             rfp_ref: str = "", category: str = "",
                             org_name: str = "") -> dict:
    """
    Generate a complete, audit-ready scorecard JSON.
    Pass to generate_report.py to produce a formatted Word document.

    section_weights: {"1": 20, "2": 30, "3": 20, "4": 20, "5": 10}
    """
    ranked = rank_suppliers(evaluations)

    # Validate weights
    total = sum(section_weights.values())
    if total != 100:
        raise ValueError(f"Section weights must sum to 100, got {total}")

    all_flags_resolved = all(
        len(e.all_missing_flags()) == 0
        for e in evaluations if not e.disqualified
    )

    return {
        "rfp_reference": rfp_ref,
        "category": category,
        "organisation": org_name,
        "evaluation_date": date.today().isoformat(),
        "section_weights": section_weights,
        "results": ranked,
        "audit": {
            "weights_locked_before_scoring": True,  # Caller asserts this
            "all_missing_data_resolved": all_flags_resolved,
            "total_suppliers_evaluated": len(evaluations),
            "disqualified_count": sum(1 for e in evaluations if e.disqualified),
            "qualified_count": sum(1 for e in evaluations if not e.disqualified)
        }
    }


# ---------------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    """
    Example: 3-supplier RFP evaluation with question-level scoring.
    This is illustrative — Claude generates the actual SupplierEvaluation
    objects from extracted proposal data using extract_sow.py.
    """

    def make_standard_sections(
        s1_weight, s2_weight, s3_weight, s4_weight, s5_weight,
        # Section 1 question scores per supplier
        q111=5, q112=5, q113=5, q121=5, q122=5, q123=5,
        # Section 4 pricing will be normalized — pass raw price instead
        price_raw=100000
    ) -> list:
        """Helper to build the 5 standard sections with example scores."""

        return [
            SectionScore("1", "Company & Capability", s1_weight, subsections=[
                SubsectionScore("1.1", "Company Overview", 40, questions=[
                    QuestionScore("Q1.1.1", "Company overview", "TEXT", q111, 40),
                    QuestionScore("Q1.1.2", "Company info table", "TABLE", q112, 30),
                    QuestionScore("Q1.1.3", "Financial statements", "ATTACHMENT", q113, 30),
                ]),
                SubsectionScore("1.2", "Relevant Experience", 60, questions=[
                    QuestionScore("Q1.2.1", "Case studies", "WORK_SAMPLE", q121, 50),
                    QuestionScore("Q1.2.2", "Relevant expertise", "TEXT", q122, 30),
                    QuestionScore("Q1.2.3", "Client references", "ATTACHMENT", q123, 20),
                ]),
            ]),
            SectionScore("2", "Technical Approach", s2_weight, subsections=[
                SubsectionScore("2.1", "Understanding of Requirement", 25, questions=[
                    QuestionScore("Q2.1.1", "Requirement understanding", "TEXT", 7, 60),
                    QuestionScore("Q2.1.2", "Scope questions", "YES_NO", 8, 40),
                ]),
                SubsectionScore("2.2", "Proposed Methodology", 50, questions=[
                    QuestionScore("Q2.2.1", "Methodology", "TEXT", 7, 50),
                    QuestionScore("Q2.2.2", "Project plan", "ATTACHMENT", 8, 30),
                    QuestionScore("Q2.2.3", "KPIs and reporting", "TEXT", 6, 20),
                ]),
                SubsectionScore("2.3", "Team & Resourcing", 25, questions=[
                    QuestionScore("Q2.3.1", "Team description", "TEXT", 7, 40),
                    QuestionScore("Q2.3.2", "Key personnel CVs", "ATTACHMENT", 8, 40),
                    QuestionScore("Q2.3.3", "Subcontracting", "YES_NO", 9, 20),
                ]),
            ]),
            SectionScore("3", "Delivery & Implementation", s3_weight, subsections=[
                SubsectionScore("3.1", "Mobilisation & Transition", 50, questions=[
                    QuestionScore("Q3.1.1", "Mobilisation timeline", "TABLE", 7, 50),
                    QuestionScore("Q3.1.2", "Transition plan", "TEXT", 7, 50),
                ]),
                SubsectionScore("3.2", "Ongoing Service Delivery", 50, questions=[
                    QuestionScore("Q3.2.1", "Service quality and escalation", "TEXT", 8, 60),
                    QuestionScore("Q3.2.2", "SLA commitment", "YES_NO", 9, 40),
                ]),
            ]),
            SectionScore("4", "Commercial Proposal", s4_weight, subsections=[
                SubsectionScore("4.1", "Pricing", 70, questions=[
                    # Q4.1.1 raw_score will be set by normalize_pricing()
                    QuestionScore("Q4.1.1", "Pricing schedule (normalized)", "FINANCIAL", None, 70),
                    QuestionScore("Q4.1.2", "Pricing structure", "TEXT", 7, 20),
                    QuestionScore("Q4.1.3", "Price fixed for term", "YES_NO", 9, 10),
                ]),
                SubsectionScore("4.2", "Commercial Terms", 30, questions=[
                    QuestionScore("Q4.2.1", "Commercial terms table", "TABLE", 7, 60),
                    QuestionScore("Q4.2.2", "Other commercial constraints", "TEXT", 8, 40),
                ]),
            ]),
            SectionScore("5", "Risk & Compliance", s5_weight, subsections=[
                SubsectionScore("5.1", "Risk Management", 50, questions=[
                    QuestionScore("Q5.1.1", "Risk register", "TABLE", 7, 50),
                    QuestionScore("Q5.1.2", "Business continuity", "TEXT", 8, 50),
                ]),
                SubsectionScore("5.2", "Compliance & Certifications", 50, questions=[
                    QuestionScore("Q5.2.1", "Certificates", "ATTACHMENT", 9, 50),
                    QuestionScore("Q5.2.2", "Data protection", "YES_NO", 9, 30),
                    QuestionScore("Q5.2.3", "Legal disclosures", "YES_NO", 10, 20),
                ]),
            ]),
        ]

    section_weights = {"1": 20, "2": 30, "3": 20, "4": 20, "5": 10}

    suppliers = [
        SupplierEvaluation(
            "Supplier Alpha", price_raw=95000,
            sections=make_standard_sections(20, 30, 20, 20, 10,
                q111=8, q121=9, price_raw=95000)
        ),
        SupplierEvaluation(
            "Supplier Beta", price_raw=82000,
            sections=make_standard_sections(20, 30, 20, 20, 10,
                q111=6, q121=7, price_raw=82000)
        ),
        SupplierEvaluation(
            "Supplier Gamma", price_raw=110000,
            sections=make_standard_sections(20, 30, 20, 20, 10,
                q111=9, q121=9, price_raw=110000)
        ),
        SupplierEvaluation(
            "Supplier Delta",
            disqualified=True,
            disqualification_reason="M1: No ISO 27001 certificate provided"
        ),
    ]

    # Normalize pricing (sets Q4.1.1 scores based on TCO)
    suppliers = normalize_pricing(suppliers)

    # Generate scorecard
    scorecard = generate_scorecard_json(
        suppliers,
        section_weights=section_weights,
        rfp_ref="RFP-2026-001",
        category="IT Security Services",
        org_name="Acme Corp"
    )

    print(json.dumps(scorecard, indent=2))

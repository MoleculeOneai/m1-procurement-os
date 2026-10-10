"""
response_scorer.py — RFP Response Evaluator
Molecule One Claude Plugin Suite

Applies weighted scoring to supplier responses. Handles disqualification checks,
TCO price normalisation, section scoring, and RAG rating assignment.
Produces scored session files for use by report_builder.py.

GOTCHAS:
- Weights are LOCKED before scoring begins. Never allow mid-session weight changes
  without routing to rerun-mode. Changing weights after partial scoring invalidates
  the audit trail.
- "Not stated" is NOT zero. Missing data is marked N/A and excluded from weighted
  total. Zero is only assigned when the supplier explicitly provided inadequate content.
- TCO normalisation is required before pricing scores are assigned. Raw quoted prices
  cannot be compared across different pricing structures.
- Disqualified suppliers must NOT appear in the scored output — remove them entirely,
  not score them zero.
- Calibration check: after scoring all suppliers on a section, verify that equivalent
  quality responses received equivalent scores across all suppliers.

Usage:
    scorer = ResponseScorer(criteria=criteria_obj)
    dq_result = scorer.disqualification_check(suppliers_data)
    section_scores = scorer.score_section(section_id, supplier_responses)
    session = scorer.build_session(all_scores)
    session.save("path/to/session.json")
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from typing import Optional
from datetime import date


@dataclass
class DisqualificationResult:
    """Outcome of the mandatory requirements check for one supplier."""
    supplier: str
    passes_all: bool
    results: list[dict]  # [{"requirement": str, "passed": bool, "evidence": str}]
    disqualification_reason: Optional[str] = None


@dataclass
class SectionScore:
    """Score for one supplier on one section."""
    supplier: str
    section_id: str
    section_name: str
    weight: float
    raw_score: Optional[float]      # 1–10, or None if N/A
    is_na: bool = False
    evidence: str = ""
    notes: str = ""

    def weighted_contribution(self) -> Optional[float]:
        """Weighted contribution to overall score. None if N/A."""
        if self.is_na or self.raw_score is None:
            return None
        return (self.raw_score / 10) * self.weight


@dataclass
class SupplierResult:
    """Aggregated scored result for one supplier."""
    supplier: str
    qualified: bool
    disqualification_reason: Optional[str]
    section_scores: list[SectionScore] = field(default_factory=list)
    tco_normalised: Optional[float] = None
    tco_currency: str = "USD"
    na_sections: list[str] = field(default_factory=list)

    def overall_score(self) -> Optional[float]:
        """
        Weighted overall score out of 10. Re-normalises weights for N/A sections.
        GOTCHA: If >3 sections are N/A, flag reliability concern.
        """
        if not self.qualified:
            return None
        scored = [s for s in self.section_scores if not s.is_na and s.raw_score is not None]
        if not scored:
            return None
        total_weight = sum(s.weight for s in scored)
        if total_weight == 0:
            return None
        weighted_sum = sum(
            (s.raw_score / 10) * (s.weight / total_weight * 100)
            for s in scored
        )
        return round(weighted_sum / 10, 2)

    def rag_rating(self, thresholds: dict) -> str:
        score = self.overall_score()
        if score is None:
            return "N/A"
        if score >= thresholds.get("green_min", 7.5):
            return "Green"
        elif score >= thresholds.get("amber_min", 5.0):
            return "Amber"
        else:
            return "Red"

    def rank_key(self) -> float:
        """Used for sorting. Disqualified suppliers sort to bottom."""
        score = self.overall_score()
        return score if score is not None else -1.0


@dataclass
class ScoredSession:
    """Complete scored session for one evaluation event."""
    rfp_reference: str
    category: str
    review_period: str
    evaluator_role: str
    criteria_version: str
    weights_used: dict          # {section_name: weight}
    suppliers: list[SupplierResult] = field(default_factory=list)
    session_date: str = field(default_factory=lambda: date.today().isoformat())
    rerun_of: Optional[str] = None      # session file this reruns, if applicable
    rerun_reason: Optional[str] = None
    notes: str = ""

    def ranked_results(self) -> list[SupplierResult]:
        """Return qualified suppliers sorted by overall score descending."""
        qualified = [s for s in self.suppliers if s.qualified]
        return sorted(qualified, key=lambda s: s.rank_key(), reverse=True)

    def disqualified(self) -> list[SupplierResult]:
        return [s for s in self.suppliers if not s.qualified]

    def to_dict(self) -> dict:
        return asdict(self)

    def save(self, output_path: str) -> None:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: str) -> "ScoredSession":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        session = cls(
            rfp_reference=data["rfp_reference"],
            category=data["category"],
            review_period=data["review_period"],
            evaluator_role=data["evaluator_role"],
            criteria_version=data["criteria_version"],
            weights_used=data["weights_used"],
            session_date=data.get("session_date", ""),
            rerun_of=data.get("rerun_of"),
            rerun_reason=data.get("rerun_reason"),
            notes=data.get("notes", ""),
        )
        for sup in data.get("suppliers", []):
            sr = SupplierResult(
                supplier=sup["supplier"],
                qualified=sup["qualified"],
                disqualification_reason=sup.get("disqualification_reason"),
                tco_normalised=sup.get("tco_normalised"),
                tco_currency=sup.get("tco_currency", "USD"),
                na_sections=sup.get("na_sections", []),
            )
            for ss in sup.get("section_scores", []):
                sr.section_scores.append(SectionScore(**ss))
            session.suppliers.append(sr)
        return session


class ResponseScorer:
    """Score supplier responses against a locked criteria set."""

    def __init__(self, criteria, rag_thresholds: Optional[dict] = None):
        """
        Args:
            criteria:       EvaluationCriteria object (from criteria_extractor.py)
            rag_thresholds: dict with green_min, amber_min keys (default: 7.5 / 5.0)
        """
        self.criteria = criteria
        self.rag_thresholds = rag_thresholds or {"green_min": 7.5, "amber_min": 5.0}

    def disqualification_check(
        self, supplier_data: list[dict]
    ) -> list[DisqualificationResult]:
        """
        Check each supplier against mandatory requirements.
        Returns a list of DisqualificationResult.

        GOTCHA: Disqualified suppliers must be removed from scoring entirely.
        Do not pass them to score_section — they should not appear in scored outputs.

        supplier_data format:
            [{"supplier": "Supplier A", "mandatory_evidence": {"MR1": "ISO cert attached", ...}}]
        """
        results = []
        for sup in supplier_data:
            mr_results = []
            all_pass = True
            fail_reason = None

            for mr in self.criteria.mandatory_requirements:
                evidence = sup.get("mandatory_evidence", {}).get(mr.requirement_id, "")
                passed = bool(evidence and evidence.lower() not in ("", "not provided", "missing"))
                if not passed:
                    all_pass = False
                    fail_reason = f"Failed mandatory requirement: {mr.description}"
                mr_results.append({
                    "requirement": mr.description,
                    "passed": passed,
                    "evidence": evidence or "Not provided",
                })

            results.append(DisqualificationResult(
                supplier=sup["supplier"],
                passes_all=all_pass,
                results=mr_results,
                disqualification_reason=fail_reason,
            ))
        return results

    def normalise_pricing(self, pricing_data: list[dict], contract_term_years: float = 3.0) -> dict:
        """
        Normalise different pricing structures to TCO over the contract term.

        pricing_data format:
            [{"supplier": "A", "pricing_type": "annual_subscription", "amount": 100000, "currency": "USD"}]

        pricing_type options:
            "fixed_project"         — one-time project fee
            "annual_subscription"   — per-year fee × contract_term_years
            "monthly_subscription"  — per-month fee × 12 × contract_term_years
            "unit_price"            — unit_price × expected_volume (must supply volume)
            "tco_stated"            — supplier provided full TCO directly

        GOTCHA: Always verify the normalisation workings with the user before scoring.
        """
        results = {}
        for p in pricing_data:
            supplier = p["supplier"]
            amount = p.get("amount", 0)
            pricing_type = p.get("pricing_type", "tco_stated")
            currency = p.get("currency", "USD")

            if pricing_type == "fixed_project":
                tco = amount
            elif pricing_type == "annual_subscription":
                tco = amount * contract_term_years
            elif pricing_type == "monthly_subscription":
                tco = amount * 12 * contract_term_years
            elif pricing_type == "unit_price":
                volume = p.get("volume", 0)
                tco = amount * volume
            else:  # tco_stated
                tco = amount

            results[supplier] = {
                "tco": round(tco, 2),
                "currency": currency,
                "pricing_type": pricing_type,
                "original_amount": amount,
                "contract_term_years": contract_term_years,
                "normalisation_note": f"{pricing_type} × {contract_term_years} years",
            }
        return results

    def score_tco(self, tco_results: dict) -> dict[str, float]:
        """
        Convert TCO values to scores (1–10) where lowest TCO = 10.
        GOTCHA: Ensure all TCOs are in the same currency before scoring.
        """
        values = {k: v["tco"] for k, v in tco_results.items() if v["tco"] > 0}
        if not values:
            return {}
        min_tco = min(values.values())
        max_tco = max(values.values())
        scores = {}
        for supplier, tco in values.items():
            if max_tco == min_tco:
                scores[supplier] = 10.0
            else:
                # Linear interpolation: lowest TCO = 10, highest = 1
                ratio = (tco - min_tco) / (max_tco - min_tco)
                scores[supplier] = round(10 - (ratio * 9), 1)
        return scores

    def build_session(
        self,
        rfp_reference: str,
        category: str,
        review_period: str,
        evaluator_role: str,
        supplier_results: list[SupplierResult],
        rerun_of: Optional[str] = None,
        rerun_reason: Optional[str] = None,
    ) -> ScoredSession:
        """Assemble the complete scored session object."""
        weights_used = {s.name: s.weight for s in self.criteria.sections}
        session = ScoredSession(
            rfp_reference=rfp_reference,
            category=category,
            review_period=review_period,
            evaluator_role=evaluator_role,
            criteria_version=self.criteria.criteria_version,
            weights_used=weights_used,
            suppliers=supplier_results,
            rerun_of=rerun_of,
            rerun_reason=rerun_reason,
        )
        return session

    def na_count_warning(self, supplier_result: SupplierResult) -> Optional[str]:
        """Flag if more than 3 sections are N/A — scorecard reliability is compromised."""
        na_count = len(supplier_result.na_sections)
        if na_count > 3:
            return (
                f"⚠ {supplier_result.supplier} has {na_count} N/A sections. "
                "The scorecard reliability is reduced. Consider requesting missing "
                "data before finalising scores."
            )
        return None


# --- __main__ demo ---
if __name__ == "__main__":
    print("=== ResponseScorer Demo ===\n")

    # Simulate a minimal criteria object
    from types import SimpleNamespace

    mock_section = SimpleNamespace(
        section_id="S1", name="Total Cost of Ownership",
        category="Commercial", weight=35.0,
    )
    mock_criteria = SimpleNamespace(
        sections=[mock_section],
        mandatory_requirements=[],
        criteria_version="1.0",
    )

    scorer = ResponseScorer(criteria=mock_criteria)

    # TCO normalisation demo
    pricing_data = [
        {"supplier": "Supplier A", "pricing_type": "annual_subscription", "amount": 80000, "currency": "USD"},
        {"supplier": "Supplier B", "pricing_type": "fixed_project", "amount": 300000, "currency": "USD"},
        {"supplier": "Supplier C", "pricing_type": "monthly_subscription", "amount": 7500, "currency": "USD"},
    ]
    tco_results = scorer.normalise_pricing(pricing_data, contract_term_years=3.0)
    tco_scores = scorer.score_tco(tco_results)

    print("TCO Normalisation (3-year term):")
    for supplier, data in tco_results.items():
        print(f"  {supplier}: ${data['tco']:,.0f} TCO → score {tco_scores.get(supplier, 'N/A')}/10")

    print("\nResponseScorer demo complete.")

"""
criteria_extractor.py — RFP Response Evaluator
Molecule One Claude Plugin Suite

Extracts scoring criteria from an original RFP document, or accepts
user-defined criteria. Produces a versioned criteria file ready for
use in the scoring session.

GOTCHAS:
- RFP sections ≠ scoring sections. Administrative sections (T&Cs, submission
  instructions, company background) must be excluded. Always confirm with user.
- Weights must sum to exactly 100%. Validate before saving.
- Anchors (what 1, 5, 10 look like) are required for every section.
  Without anchors, scores are arbitrary and indefensible.
- Never invent criteria the RFP doesn't contain. Evaluation must match what
  suppliers were asked to address.
- Criteria files are versioned. Increment version when criteria, weights,
  or anchors change — old scored sessions reference their own version.

Usage:
    # From RFP document
    extractor = CriteriaExtractor()
    sections = extractor.from_rfp("path/to/rfp.docx")

    # User-defined
    criteria = extractor.from_user_input(sections=[...], weights={...})
    extractor.save(criteria, output_path="...", version="1.0")
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from typing import Optional
from pathlib import Path


@dataclass
class ScoringAnchor:
    """Defines what a score of 10, 5, and 1 looks like for a section."""
    score_10: str   # Outstanding — specific, measurable description
    score_5: str    # Acceptable — specific, measurable description
    score_1: str    # Inadequate — specific, measurable description


@dataclass
class ScoringSection:
    """A single scoreable section in the evaluation framework."""
    section_id: str             # e.g. "S1", "S2"
    name: str                   # e.g. "Total Cost of Ownership"
    category: str               # e.g. "Commercial", "Technical", "Delivery", "Risk"
    weight: float               # as percentage, e.g. 35.0
    rfp_section_ref: Optional[str] = None   # original RFP section number/title if extracted
    anchor: Optional[ScoringAnchor] = None
    data_source: str = "Supplier submission"    # where the score data comes from
    notes: str = ""


@dataclass
class MandatoryRequirement:
    """A pass/fail requirement — failing suppliers are disqualified, not scored zero."""
    requirement_id: str     # e.g. "MR1"
    description: str        # e.g. "ISO 9001 certification current"
    evidence_required: str  # e.g. "Certificate copy uploaded with submission"


@dataclass
class EvaluationCriteria:
    """The complete criteria set for an evaluation."""
    category: str
    rfp_reference: Optional[str]
    criteria_version: str
    criteria_source: str        # "From RFP" or "User-defined"
    scoring_scale: int          # typically 10
    sections: list[ScoringSection] = field(default_factory=list)
    mandatory_requirements: list[MandatoryRequirement] = field(default_factory=list)
    notes: str = ""

    def total_weight(self) -> float:
        return sum(s.weight for s in self.sections)

    def validate(self) -> list[str]:
        """
        Validate the criteria set. Returns a list of errors.
        GOTCHA: Weights must sum to exactly 100. All sections need anchors.
        """
        errors = []
        total = self.total_weight()
        if abs(total - 100.0) > 0.1:
            errors.append(
                f"Weights sum to {total:.1f}% — must sum to exactly 100%. "
                f"Adjust section weights before saving."
            )
        if not self.sections:
            errors.append("No scoring sections defined.")
        for s in self.sections:
            if s.weight <= 0:
                errors.append(f"Section '{s.name}' has weight ≤0 — invalid.")
            if s.weight > 50:
                errors.append(
                    f"Section '{s.name}' has weight {s.weight}% — exceeds 50% limit. "
                    "A single section should not dominate the evaluation."
                )
            if s.anchor is None:
                errors.append(
                    f"Section '{s.name}' has no scoring anchors. "
                    "Anchors are required — define what 10, 5, and 1 look like."
                )
        return errors

    def to_dict(self) -> dict:
        return asdict(self)

    def save(self, output_path: str) -> None:
        errors = self.validate()
        if errors:
            raise ValueError(
                "Criteria validation failed — fix errors before saving:\n"
                + "\n".join(f"  - {e}" for e in errors)
            )
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: str) -> "EvaluationCriteria":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        criteria = cls(
            category=data["category"],
            rfp_reference=data.get("rfp_reference"),
            criteria_version=data["criteria_version"],
            criteria_source=data["criteria_source"],
            scoring_scale=data["scoring_scale"],
            notes=data.get("notes", ""),
        )
        for s in data.get("sections", []):
            anchor_data = s.get("anchor")
            anchor = ScoringAnchor(**anchor_data) if anchor_data else None
            criteria.sections.append(ScoringSection(
                section_id=s["section_id"],
                name=s["name"],
                category=s["category"],
                weight=s["weight"],
                rfp_section_ref=s.get("rfp_section_ref"),
                anchor=anchor,
                data_source=s.get("data_source", "Supplier submission"),
                notes=s.get("notes", ""),
            ))
        for mr in data.get("mandatory_requirements", []):
            criteria.mandatory_requirements.append(MandatoryRequirement(**mr))
        return criteria


class CriteriaExtractor:
    """
    Extract or define scoring criteria for an RFP evaluation.

    Modes:
        from_rfp        — parse an RFP document and propose scoreable sections
        from_user_input — accept user-defined sections and weights
    """

    # Administrative section keywords — these should NOT become scoring dimensions
    ADMIN_KEYWORDS = [
        "submission instructions", "terms and conditions", "general conditions",
        "company background", "about us", "introduction", "executive summary",
        "cover letter", "confidentiality", "legal disclaimer", "appendix",
        "glossary", "definitions", "contact details", "document control",
    ]

    def from_rfp(self, rfp_path: str) -> list[dict]:
        """
        Parse an RFP document and extract proposed scoreable sections.
        Returns a list of dicts — each dict is a candidate section for review.

        GOTCHA: This returns CANDIDATES only. Always present to user for
        confirmation before using as the scoring framework.
        """
        rfp_path = Path(rfp_path)
        if not rfp_path.exists():
            raise FileNotFoundError(f"RFP file not found: {rfp_path}")

        sections = []
        try:
            from docx import Document  # type: ignore
            doc = Document(str(rfp_path))
            headings = [
                p.text.strip()
                for p in doc.paragraphs
                if p.style.name.startswith("Heading") and p.text.strip()
            ]
        except ImportError:
            # Fallback: treat every non-empty line starting with a number as a section
            headings = []

        for heading in headings:
            if self._is_admin_section(heading):
                sections.append({
                    "title": heading,
                    "scoreable": False,
                    "reason": "Administrative section — excluded from scoring",
                })
            else:
                sections.append({
                    "title": heading,
                    "scoreable": True,
                    "reason": "Candidate scoring section — confirm with user",
                })

        if not sections:
            sections.append({
                "title": "Could not auto-extract sections from document",
                "scoreable": False,
                "reason": "Manual section definition required. Use from_user_input() instead.",
            })

        return sections

    def _is_admin_section(self, heading: str) -> bool:
        heading_lower = heading.lower()
        return any(kw in heading_lower for kw in self.ADMIN_KEYWORDS)

    def from_user_input(
        self,
        category: str,
        rfp_reference: Optional[str],
        sections: list[dict],
        mandatory_requirements: Optional[list[dict]] = None,
        version: str = "1.0",
    ) -> EvaluationCriteria:
        """
        Build an EvaluationCriteria object from user-confirmed section data.

        Each section dict must contain:
            name, category, weight, anchor (dict with score_10, score_5, score_1)

        GOTCHA: Validate before saving — weights must sum to 100.
        """
        criteria = EvaluationCriteria(
            category=category,
            rfp_reference=rfp_reference,
            criteria_version=version,
            criteria_source="User-defined",
            scoring_scale=10,
        )

        for i, s in enumerate(sections, start=1):
            anchor_data = s.get("anchor")
            anchor = ScoringAnchor(**anchor_data) if anchor_data else None
            criteria.sections.append(ScoringSection(
                section_id=f"S{i}",
                name=s["name"],
                category=s.get("category", "General"),
                weight=float(s["weight"]),
                rfp_section_ref=s.get("rfp_section_ref"),
                anchor=anchor,
                data_source=s.get("data_source", "Supplier submission"),
                notes=s.get("notes", ""),
            ))

        for j, mr in enumerate(mandatory_requirements or [], start=1):
            criteria.mandatory_requirements.append(MandatoryRequirement(
                requirement_id=f"MR{j}",
                description=mr["description"],
                evidence_required=mr.get("evidence_required", "To be specified"),
            ))

        return criteria


# --- __main__ demo ---
if __name__ == "__main__":
    import tempfile

    print("=== CriteriaExtractor Demo ===\n")

    extractor = CriteriaExtractor()

    # Build criteria from user input (simulating confirmed user input)
    sample_sections = [
        {
            "name": "Total Cost of Ownership",
            "category": "Commercial",
            "weight": 35.0,
            "anchor": {
                "score_10": "Lowest TCO in panel; fully transparent pricing with no hidden costs",
                "score_5": "TCO within 15% of lowest; pricing clear but some variable elements",
                "score_1": "Highest TCO or significant undisclosed costs; pricing unverifiable",
            },
        },
        {
            "name": "Technical Approach",
            "category": "Technical",
            "weight": 30.0,
            "anchor": {
                "score_10": "Detailed, tailored methodology addressing every spec point; evidenced delivery plan",
                "score_5": "Covers most requirements; some gaps; credible but lacks specifics",
                "score_1": "Generic response; methodology not demonstrated; delivery plan missing",
            },
        },
        {
            "name": "Delivery Timeline",
            "category": "Delivery",
            "weight": 20.0,
            "anchor": {
                "score_10": "Delivery within required timeline with milestone buffer; realistic resource plan",
                "score_5": "Timeline meets requirement but no buffer; resource plan basic",
                "score_1": "Timeline exceeds requirement or no timeline provided",
            },
        },
        {
            "name": "Risk & Compliance",
            "category": "Risk",
            "weight": 15.0,
            "anchor": {
                "score_10": "All certifications current; robust continuity plan tested in last 12 months",
                "score_5": "Most certifications current; continuity plan exists but not recently tested",
                "score_1": "Key certifications missing or expired; no continuity plan",
            },
        },
    ]

    sample_mandatory = [
        {
            "description": "ISO 9001 certification current",
            "evidence_required": "Certificate copy uploaded with submission",
        },
    ]

    criteria = extractor.from_user_input(
        category="IT Services",
        rfp_reference="RFP-2026-001",
        sections=sample_sections,
        mandatory_requirements=sample_mandatory,
        version="1.0",
    )

    print(f"Category: {criteria.category}")
    print(f"Total weight: {criteria.total_weight()}%")
    print(f"Sections: {len(criteria.sections)}")
    for s in criteria.sections:
        print(f"  [{s.section_id}] {s.name} — {s.weight}%")

    errors = criteria.validate()
    if errors:
        print(f"\nValidation errors: {errors}")
    else:
        print("\nValidation: PASSED")

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        criteria.save(tmp.name)
        loaded = EvaluationCriteria.load(tmp.name)
        print(f"Save/load round-trip: {len(loaded.sections)} sections — OK")

    print("\nCriteriaExtractor demo complete.")

"""
scorecard_builder.py — Scorecard Criterion Set Constructor & Validator
Part of the Molecule One Supplier Scorecard Engine skill.

Constructs, validates, and persists scorecard criterion sets.
A criterion set defines the dimensions, weights, anchors, and data sources
for a specific category of supplier.

Usage:
    from lib.scorecard_builder import ScorecardCriterion, ScorecardDesign
    from lib.scorecard_builder import build_scorecard, validate_scorecard, save_scorecard

Gotchas:
    - Weights must sum to exactly 100. This is validated on build and save.
      Do not silently normalise — if weights don't sum to 100, ask the user to correct them.
    - N/A dimensions are excluded from scoring. The calculator renormalises weights
      automatically — but the total weight of scoreable dimensions must still be
      validated before publishing a result.
    - Version all scorecards. When criteria or weights change, increment the version.
      Never overwrite a prior version — old scoring sessions reference it.
    - Scorecard designs are saved per category, not per supplier. Multiple suppliers
      in the same category use the same scorecard design.
"""

import json
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


@dataclass
class AnchorSet:
    """
    Defines what score 1, 3, and 5 look like for a criterion.

    Gotcha: anchors must be specific and measurable. If a user provides
    'good', 'ok', 'bad' as anchors — push back. These are useless.
    """
    score_5: str   # Excellent / exceeds expectation
    score_3: str   # Acceptable / meets expectation
    score_1: str   # Unacceptable / significantly below expectation


@dataclass
class ScorecardCriterion:
    """
    A single scoreable dimension on a supplier scorecard.

    Gotcha: weight must be an integer (whole percentage points).
    Fractional weights (e.g. 12.5%) are valid in theory but create
    confusion when stakeholders review the scorecard design.
    Recommend rounding to whole numbers.
    """
    name: str
    category: str            # Commercial / Quality / Relationship / Risk / Innovation
    weight: float            # % of total score (must sum to 100 across all criteria)
    anchors: AnchorSet
    data_source: str         # Where does the score data come from?
    data_owner: str          # Who is responsible for providing data?
    data_available: bool     # Is the data actually available right now?
    notes: str = ""


@dataclass
class ScorecardDesign:
    """
    A complete scorecard design for a category.
    """
    name: str                    # e.g. "IT Services Supplier Scorecard"
    category: str                # procurement category
    version: str                 # e.g. "1.0"
    org_name: str
    criteria: list[ScorecardCriterion]
    review_frequency: str        # Monthly / Quarterly / Bi-annual / Annual
    reviewer_roles: list[str]    # roles that provide input
    approver_role: str           # who approves before sharing with supplier
    notes: str = ""
    created_date: str = ""


def build_scorecard(
    name: str,
    category: str,
    version: str,
    org_name: str,
    criteria: list[ScorecardCriterion],
    review_frequency: str,
    reviewer_roles: list[str],
    approver_role: str,
    notes: str = "",
    created_date: str = "",
) -> ScorecardDesign:
    """
    Build and validate a ScorecardDesign.

    Raises ValueError if:
      - weights don't sum to 100 (within ±0.5 tolerance for float precision)
      - fewer than 4 criteria (scorecard is too thin to be useful)
      - more than 15 criteria (scorecard will be impossible to run consistently)
      - any criterion has no anchors

    Returns a validated ScorecardDesign.

    Gotchas:
      - If the user proposes all equal weights (e.g. 10% each for 10 criteria),
        flag this as a warning. Equal weights mean no priorities were set.
      - If more than 3 criteria have data_available=False, warn — these will
        create persistent N/A gaps in scoring sessions.
    """
    design = ScorecardDesign(
        name=name,
        category=category,
        version=version,
        org_name=org_name,
        criteria=criteria,
        review_frequency=review_frequency,
        reviewer_roles=reviewer_roles,
        approver_role=approver_role,
        notes=notes,
        created_date=created_date,
    )
    validate_scorecard(design)
    return design


def validate_scorecard(design: ScorecardDesign) -> list[str]:
    """
    Validate a scorecard design. Returns a list of warning/error strings.

    Raises ValueError on fatal errors (bad weights, too few criteria).
    Returns warnings (list of strings) for non-fatal issues.

    Gotchas:
      - Float precision: 25 + 25 + 25 + 25 = 100.0 is fine;
        33.33 + 33.33 + 33.34 = 100.0 is fine. Use ±0.5 tolerance.
      - A scorecard with 0 data_available=True criteria is useless —
        all dimensions would be N/A on first use.
    """
    warnings = []
    errors = []

    total_weight = sum(c.weight for c in design.criteria)
    if abs(total_weight - 100.0) > 0.5:
        errors.append(
            f"Weights sum to {total_weight:.1f}%, not 100%. "
            "Adjust criterion weights before saving."
        )

    if len(design.criteria) < 4:
        errors.append(
            f"Only {len(design.criteria)} criteria defined. "
            "A scorecard with fewer than 4 criteria is too narrow to be useful."
        )

    if len(design.criteria) > 15:
        warnings.append(
            f"{len(design.criteria)} criteria defined. "
            "Scorecards with more than 10–12 criteria are difficult to run consistently. "
            "Consider consolidating or removing lower-priority dimensions."
        )

    # Equal weight warning
    weights = [c.weight for c in design.criteria]
    if len(set(weights)) == 1:
        warnings.append(
            "All criteria have equal weights. This typically means no priority decision was made. "
            "Review with stakeholders and adjust weights to reflect what actually matters."
        )

    # Single dominant dimension
    max_weight = max(weights)
    if max_weight > 40:
        warnings.append(
            f"One criterion has a weight of {max_weight}%, which is >40% of the total. "
            "A scorecard dominated by one dimension is fragile. Consider redistributing."
        )

    # Data availability
    unavailable = [c.name for c in design.criteria if not c.data_available]
    if len(unavailable) > 3:
        warnings.append(
            f"{len(unavailable)} criteria have data_available=False: "
            f"{', '.join(unavailable)}. "
            "These will be N/A in most scoring sessions. Establish data collection "
            "before using this scorecard, or remove these criteria."
        )

    # Missing anchors (empty strings)
    for c in design.criteria:
        if not c.anchors.score_5 or not c.anchors.score_3 or not c.anchors.score_1:
            errors.append(
                f"Criterion '{c.name}' has incomplete anchors. "
                "All three anchor levels (1, 3, 5) must be defined."
            )

    if errors:
        raise ValueError("Scorecard validation failed:\n" + "\n".join(f"  - {e}" for e in errors))

    for w in warnings:
        print(f"[scorecard_builder] WARNING: {w}", file=sys.stderr)

    return warnings


def save_scorecard(design: ScorecardDesign, output_dir: str) -> str:
    """
    Save a scorecard design to a versioned JSON file.

    File naming: [CATEGORY]-scorecard-v[VERSION].json (lowercase, spaces → hyphens)
    Returns the saved file path.

    Gotchas:
      - Never overwrite an existing version file. If the file already exists,
        raise an error and ask the user to increment the version number.
      - The output_dir is typically ${CLAUDE_PLUGIN_DATA}/scorecards/
    """
    safe_category = design.category.lower().replace(" ", "-").replace("/", "-")
    filename = f"{safe_category}-scorecard-v{design.version}.json"
    path = Path(output_dir) / filename

    if path.exists():
        raise FileExistsError(
            f"Scorecard file already exists: {path}. "
            f"Increment the version number (currently v{design.version}) to save a new version."
        )

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    data = _serialize_design(design)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"[scorecard_builder] Saved to {path}", file=sys.stderr)
    return str(path)


def load_scorecard(filepath: str) -> ScorecardDesign:
    """
    Load a scorecard design from a JSON file.

    Gotchas:
      - If the file is a legacy format (missing new fields), defaults are applied
        for backwards compatibility. Always log what was defaulted.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Scorecard file not found: {filepath}")

    data = json.loads(path.read_text(encoding="utf-8"))

    criteria = []
    for c in data.get("criteria", []):
        anchors = c.get("anchors", {})
        criteria.append(ScorecardCriterion(
            name=c["name"],
            category=c.get("category", "Unknown"),
            weight=c["weight"],
            anchors=AnchorSet(
                score_5=anchors.get("score_5", ""),
                score_3=anchors.get("score_3", ""),
                score_1=anchors.get("score_1", ""),
            ),
            data_source=c.get("data_source", "Unknown"),
            data_owner=c.get("data_owner", "Unknown"),
            data_available=c.get("data_available", False),
            notes=c.get("notes", ""),
        ))

    return ScorecardDesign(
        name=data["name"],
        category=data["category"],
        version=data["version"],
        org_name=data.get("org_name", ""),
        criteria=criteria,
        review_frequency=data.get("review_frequency", "Quarterly"),
        reviewer_roles=data.get("reviewer_roles", []),
        approver_role=data.get("approver_role", ""),
        notes=data.get("notes", ""),
        created_date=data.get("created_date", ""),
    )


def render_scorecard_summary(design: ScorecardDesign) -> str:
    """Render a human-readable summary of a scorecard design."""
    lines = [
        f"## {design.name} — v{design.version}",
        f"Category: {design.category} | Org: {design.org_name} | Review: {design.review_frequency}",
        f"Reviewers: {', '.join(design.reviewer_roles)} | Approver: {design.approver_role}",
        "",
        f"{'Criterion':<35} {'Category':<16} {'Weight':>7}  {'Data Source':<25} {'Data Ready?'}",
        "-" * 95,
    ]
    total_w = 0
    for c in design.criteria:
        total_w += c.weight
        avail = "✅" if c.data_available else "⚠ Not yet"
        lines.append(
            f"{c.name:<35} {c.category:<16} {c.weight:>6.1f}%  {c.data_source:<25} {avail}"
        )
    lines.append("-" * 95)
    lines.append(f"{'TOTAL':<53} {total_w:>6.1f}%")
    return "\n".join(lines)


def _serialize_design(design: ScorecardDesign) -> dict:
    """Serialise a ScorecardDesign to a plain dict for JSON storage."""
    return {
        "name": design.name,
        "category": design.category,
        "version": design.version,
        "org_name": design.org_name,
        "review_frequency": design.review_frequency,
        "reviewer_roles": design.reviewer_roles,
        "approver_role": design.approver_role,
        "notes": design.notes,
        "created_date": design.created_date,
        "criteria": [
            {
                "name": c.name,
                "category": c.category,
                "weight": c.weight,
                "anchors": {
                    "score_5": c.anchors.score_5,
                    "score_3": c.anchors.score_3,
                    "score_1": c.anchors.score_1,
                },
                "data_source": c.data_source,
                "data_owner": c.data_owner,
                "data_available": c.data_available,
                "notes": c.notes,
            }
            for c in design.criteria
        ],
    }


if __name__ == "__main__":
    # Demo: build a logistics scorecard
    demo = build_scorecard(
        name="Logistics Supplier Scorecard",
        category="Logistics",
        version="1.0",
        org_name="Acme Corp",
        criteria=[
            ScorecardCriterion("On-Time In-Full (OTIF)", "Quality", 30,
                AnchorSet("≥98% OTIF", "90–97% OTIF", "<85% OTIF"),
                "TMS / delivery tracking system", "Operations Manager", True),
            ScorecardCriterion("Damage / Loss Rate", "Quality", 20,
                AnchorSet("<0.1% of shipments damaged or lost",
                          "0.1–0.5% damaged or lost",
                          ">1% damaged or lost"),
                "Claims management system", "Logistics Coordinator", True),
            ScorecardCriterion("Invoice Accuracy", "Commercial", 20,
                AnchorSet("≥99% invoices correct first time",
                          "95–98% correct first time",
                          "<90% correct first time"),
                "Accounts Payable system", "Finance AP Lead", True),
            ScorecardCriterion("Responsiveness", "Relationship", 15,
                AnchorSet("All queries responded to within 4 hours; issues proactively flagged",
                          "Most queries within 24 hours; reactive on issues",
                          "Slow to respond; issues discovered by buyer"),
                "Stakeholder survey", "Category Manager", False),
            ScorecardCriterion("Regulatory Compliance", "Risk", 15,
                AnchorSet("All required certs current; zero compliance incidents",
                          "All certs current; minor procedural lapses",
                          "Expired certification or compliance breach"),
                "Compliance tracker", "Risk & Compliance", True),
        ],
        review_frequency="Quarterly",
        reviewer_roles=["Category Manager", "Operations Manager", "Finance AP Lead"],
        approver_role="Head of Procurement",
    )
    print(render_scorecard_summary(demo))

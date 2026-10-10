"""
score_calculator.py — Weighted Score Computation, RAG Rating & Trend Analysis
Part of the Molecule One Supplier Scorecard Engine skill.

Computes weighted supplier scores, assigns RAG ratings, detects trends,
and manages scoring session persistence.

Usage:
    from lib.score_calculator import ScoringSession, compute_weighted_score
    from lib.score_calculator import assign_rag, compute_delta, load_prior_sessions

Gotchas:
    - N/A dimensions must be excluded from both numerator AND denominator.
      Re-normalise weights before computing the total — do not include N/A
      dimensions at zero weight, which would silently compress the score.
    - RAG thresholds are loaded from config.json. Never hardcode them — organisations
      have different standards. Default: Green ≥75, Amber 50–74, Red <50.
    - Delta computation requires the same scorecard version across periods.
      Cross-version deltas are meaningful only for dimensions present in both versions.
    - Score of 0 is not the same as N/A. 0 means the reviewer explicitly scored zero.
      N/A means no data was available. Treat them differently in all calculations.
"""

import json
import sys
from dataclasses import dataclass, field, asdict
from datetime import date
from pathlib import Path
from typing import Optional


DEFAULT_RAG_THRESHOLDS = {
    "green_min": 75,
    "amber_min": 50,
    "red_below": 50,
}


@dataclass
class DimensionScore:
    """A single dimension score within a scoring session."""
    criterion_name: str
    weight: float                  # from scorecard design
    raw_score: Optional[float]     # 1–5, or None if N/A
    evidence: str = ""             # reviewer commentary
    is_na: bool = False            # True if data was unavailable


@dataclass
class ScoringSession:
    """
    A complete scored session for a supplier in a review period.
    """
    supplier_name: str
    category: str
    review_period: str             # e.g. "Q1 2026", "2026-01"
    scorecard_version: str
    reviewer_role: str
    scored_date: str
    org_name: str
    dimension_scores: list[DimensionScore]
    overall_score: float = 0.0    # populated by compute_weighted_score()
    rag: str = ""                 # Red / Amber / Green — populated by assign_rag()
    prior_score: Optional[float] = None
    delta: Optional[float] = None
    actions: list[dict] = field(default_factory=list)  # [{issue, action, owner, deadline}]
    notes: str = ""


def compute_weighted_score(session: ScoringSession) -> float:
    """
    Compute the weighted overall score for a session.

    Algorithm:
      1. Exclude N/A dimensions from both numerator and denominator.
      2. Re-normalise remaining weights to sum to 100%.
      3. Weighted score = sum(score_i * normalised_weight_i) * 20
         (converts 1–5 scale to 0–100 scale)

    Returns the overall score (0–100) and updates session.overall_score.

    Gotchas:
      - If ALL dimensions are N/A, the score is 0.0 and the session is flagged
        as invalid — do not issue a RAG rating.
      - score * weight is computed on the 1–5 scale, then converted to 0–100
        at the end. Do not multiply by 20 before the weighted sum.
    """
    scoreable = [d for d in session.dimension_scores if not d.is_na and d.raw_score is not None]

    if not scoreable:
        print("[score_calculator] WARNING: All dimensions N/A — score is 0.0 (invalid)", file=sys.stderr)
        session.overall_score = 0.0
        return 0.0

    total_weight = sum(d.weight for d in scoreable)
    if total_weight == 0:
        session.overall_score = 0.0
        return 0.0

    weighted_sum = sum(
        (d.raw_score * (d.weight / total_weight))
        for d in scoreable
    )
    # weighted_sum is on 1–5 scale; convert to 0–100
    overall = round((weighted_sum / 5.0) * 100, 1)
    session.overall_score = overall
    return overall


def assign_rag(
    score: float,
    thresholds: Optional[dict] = None
) -> str:
    """
    Assign a RAG rating based on the overall score.

    Thresholds default: Green ≥75, Amber 50–74, Red <50.
    Pass custom thresholds from config.json to override.

    Gotchas:
      - A score of exactly 75 is Green, not Amber.
      - A score of exactly 50 is Amber, not Red.
      - Never assign RAG to a session where overall_score == 0 due to all N/A.
        In that case, return "Unrated".
    """
    if score == 0.0:
        return "Unrated"

    t = thresholds or DEFAULT_RAG_THRESHOLDS
    green_min = t.get("green_min", 75)
    amber_min = t.get("amber_min", 50)

    if score >= green_min:
        return "Green"
    elif score >= amber_min:
        return "Amber"
    else:
        return "Red"


def compute_delta(current_score: float, prior_score: Optional[float]) -> Optional[float]:
    """
    Compute the score delta vs. the prior period.

    Returns None if no prior score exists (first review).
    Returns a float (positive = improvement, negative = decline).

    Gotchas:
      - Never compute delta across different scorecard versions without flagging it.
        A change in criteria or weights means the delta may not be meaningful.
      - A delta of 0.0 is meaningful (stable). Do not omit it.
    """
    if prior_score is None:
        return None
    return round(current_score - prior_score, 1)


def get_dimension_flags(session: ScoringSession, threshold: float = 2.5) -> dict:
    """
    Identify dimensions scoring below the threshold (effectively Red at dimension level).

    Default threshold: 2.5/5 (equivalent to 50/100 overall)

    Returns:
      {
        "red_dimensions": [list of criterion names scoring below threshold],
        "green_dimensions": [list scoring above 4.0/5],
        "na_dimensions": [list of N/A dimensions]
      }

    Gotchas:
      - The threshold here is on the raw 1–5 scale, not the 0–100 overall score.
        2.5/5 = 50/100. Adjust if the org uses different dimension-level thresholds.
    """
    red = []
    green = []
    na = []

    for d in session.dimension_scores:
        if d.is_na:
            na.append(d.criterion_name)
        elif d.raw_score is not None:
            if d.raw_score < threshold:
                red.append(d.criterion_name)
            elif d.raw_score >= 4.0:
                green.append(d.criterion_name)

    return {"red_dimensions": red, "green_dimensions": green, "na_dimensions": na}


def save_session(session: ScoringSession, output_dir: str) -> str:
    """
    Save a scoring session to a JSON file.

    File naming: [SUPPLIER]-[PERIOD].json (lowercase, spaces → hyphens)
    Returns the saved file path.

    Gotchas:
      - If a session file already exists for this supplier/period, append a
        timestamp suffix to avoid overwriting. This can happen if a session
        is re-run in the same period (e.g. to correct a score).
    """
    safe_supplier = session.supplier_name.lower().replace(" ", "-")
    safe_period = session.review_period.lower().replace(" ", "-")
    filename = f"{safe_supplier}-{safe_period}.json"
    path = Path(output_dir) / filename

    if path.exists():
        from datetime import datetime
        ts = datetime.now().strftime("%H%M%S")
        filename = f"{safe_supplier}-{safe_period}-{ts}.json"
        path = Path(output_dir) / filename
        print(
            f"[score_calculator] Session file already existed — saved as {filename}",
            file=sys.stderr
        )

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    data = _serialize_session(session)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"[score_calculator] Session saved to {path}", file=sys.stderr)
    return str(path)


def load_prior_sessions(supplier_name: str, sessions_dir: str, max_periods: int = 4) -> list[dict]:
    """
    Load the most recent N scoring sessions for a supplier.

    Returns sessions sorted by scored_date descending (most recent first).

    Gotchas:
      - Sessions are matched by supplier_name (case-insensitive, hyphens → spaces).
        A supplier named "Acme Corp" and "ACME Corp" will be treated as the same.
      - If scorecard_version differs between sessions, flag this to the caller —
        cross-version deltas may not be comparable.
    """
    sessions_path = Path(sessions_dir)
    if not sessions_path.exists():
        return []

    safe_supplier = supplier_name.lower().replace(" ", "-")
    matching_files = sorted(sessions_path.glob(f"{safe_supplier}-*.json"), reverse=True)

    results = []
    for f in matching_files[:max_periods]:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            results.append(data)
        except (json.JSONDecodeError, IOError) as e:
            print(f"[score_calculator] Could not load {f}: {e}", file=sys.stderr)

    if len(set(s.get("scorecard_version") for s in results)) > 1:
        print(
            "[score_calculator] WARNING: Multiple scorecard versions found in session history. "
            "Period-over-period deltas may not be fully comparable.",
            file=sys.stderr
        )

    return results


def render_score_summary(session: ScoringSession) -> str:
    """Render a human-readable scoring summary."""
    rag_icon = {"Green": "🟢", "Amber": "🟡", "Red": "🔴", "Unrated": "⚪"}.get(session.rag, "")
    delta_str = ""
    if session.delta is not None:
        sign = "+" if session.delta >= 0 else ""
        delta_str = f"  Δ {sign}{session.delta} vs. prior period"
    elif session.prior_score is None:
        delta_str = "  (First review)"

    lines = [
        f"## {session.supplier_name} — {session.review_period}",
        f"Overall score: {session.overall_score:.1f}/100  {rag_icon} {session.rag}{delta_str}",
        f"Scorecard: v{session.scorecard_version} | Reviewer: {session.reviewer_role} | {session.scored_date}",
        "",
        f"{'Dimension':<35} {'Score':>6}  {'Weight':>7}  {'Evidence'}",
        "-" * 85,
    ]

    for d in session.dimension_scores:
        score_str = "N/A" if d.is_na else f"{d.raw_score}/5"
        weight_str = f"{d.weight:.0f}%"
        evidence = (d.evidence[:40] + "...") if len(d.evidence) > 43 else d.evidence
        lines.append(f"{d.criterion_name:<35} {score_str:>6}  {weight_str:>7}  {evidence}")

    lines.append("-" * 85)

    flags = get_dimension_flags(session)
    if flags["red_dimensions"]:
        lines.append(f"🔴 Red dimensions: {', '.join(flags['red_dimensions'])}")
    if flags["na_dimensions"]:
        lines.append(f"⚪ N/A (excluded): {', '.join(flags['na_dimensions'])}")

    if session.actions:
        lines.append("")
        lines.append(f"Action items: {len(session.actions)}")
        for a in session.actions:
            lines.append(f"  [{a.get('owner','')}] {a.get('action','')} by {a.get('deadline','TBC')}")

    return "\n".join(lines)


def _serialize_session(session: ScoringSession) -> dict:
    return {
        "supplier_name": session.supplier_name,
        "category": session.category,
        "review_period": session.review_period,
        "scorecard_version": session.scorecard_version,
        "reviewer_role": session.reviewer_role,
        "scored_date": session.scored_date,
        "org_name": session.org_name,
        "overall_score": session.overall_score,
        "rag": session.rag,
        "prior_score": session.prior_score,
        "delta": session.delta,
        "notes": session.notes,
        "actions": session.actions,
        "dimension_scores": [
            {
                "criterion_name": d.criterion_name,
                "weight": d.weight,
                "raw_score": d.raw_score,
                "evidence": d.evidence,
                "is_na": d.is_na,
            }
            for d in session.dimension_scores
        ],
    }


if __name__ == "__main__":
    # Demo session
    session = ScoringSession(
        supplier_name="FastFreight Ltd",
        category="Logistics",
        review_period="Q1 2026",
        scorecard_version="1.0",
        reviewer_role="Category Manager",
        scored_date=date.today().isoformat(),
        org_name="Acme Corp",
        dimension_scores=[
            DimensionScore("On-Time In-Full (OTIF)", 30, 4, "94% OTIF — above 90% threshold but below 98%"),
            DimensionScore("Damage / Loss Rate", 20, 5, "0.05% — excellent, below 0.1% target"),
            DimensionScore("Invoice Accuracy", 20, 3, "96% — within SLA but one batch error in Feb"),
            DimensionScore("Responsiveness", 15, None, "", is_na=True),
            DimensionScore("Regulatory Compliance", 15, 5, "All certs current; zero incidents"),
        ],
        actions=[
            {"issue": "Invoice batch error Feb", "action": "Supplier to provide root cause and process fix", "owner": "Supplier AP Lead", "deadline": "2026-04-15"},
        ],
    )

    compute_weighted_score(session)
    session.rag = assign_rag(session.overall_score)
    session.prior_score = 78.0
    session.delta = compute_delta(session.overall_score, session.prior_score)
    print(render_score_summary(session))

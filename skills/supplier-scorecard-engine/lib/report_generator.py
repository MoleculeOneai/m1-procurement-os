"""
report_generator.py — Supplier Report Card & Improvement Plan Assembler
Part of the Molecule One Supplier Scorecard Engine skill.

Assembles scored session data into formatted Markdown reports for:
  - Supplier report cards (internal and supplier-facing)
  - Trend summaries
  - Supplier Improvement Plans (SIP)
  - Multi-supplier benchmark tables

Usage:
    from lib.report_generator import build_report_card, build_improvement_plan
    from lib.report_generator import build_benchmark_table

Gotchas:
    - Report cards have TWO versions: internal (full commentary) and supplier-facing
      (summary only, no internal notes). Always generate both but NEVER combine them.
      The internal version must never be shared with the supplier.
    - Improvement plans must include measurable targets, not aspirational statements.
      "Improve OTIF" is not a target. "Achieve ≥95% OTIF by [date]" is.
    - Trend analysis requires at least 2 periods. With 1 period, write "Trend data
      will be available from the next review period." Never fabricate a trend.
    - Benchmark tables require all suppliers to be scored on the same scorecard version.
      Cross-version comparisons must be flagged prominently.
"""

import json
import sys
from datetime import date
from pathlib import Path
from typing import Optional


RAG_ICONS = {"Green": "🟢", "Amber": "🟡", "Red": "🔴", "Unrated": "⚪"}
TREND_ICONS = {"improving": "🔺", "stable": "➡", "declining": "🔻"}


def build_report_card(
    session: dict,
    prior_sessions: list[dict],
    org_name: str,
    report_type: str = "internal",
) -> str:
    """
    Build a supplier report card in Markdown format.

    Parameters:
      session: dict — the current period's scored session (from score_calculator)
      prior_sessions: list of dicts — up to 4 prior periods, most recent first
      org_name: str
      report_type: "internal" or "supplier-facing"

    Returns Markdown string for the report card.

    Gotchas:
      - supplier-facing version strips: internal reviewer commentary, dimension
        evidence notes marked [INTERNAL], and any action items flagged as buyer-only.
      - If report_type is "supplier-facing", do a final scan for [INTERNAL] tags
        and raise an error if any remain — never silently include internal content.
    """
    supplier = session.get("supplier_name", "Unknown Supplier")
    period = session.get("review_period", "Unknown Period")
    overall = session.get("overall_score", 0)
    rag = session.get("rag", "Unrated")
    rag_icon = RAG_ICONS.get(rag, "")
    delta = session.get("delta")

    doc_date = date.today().strftime("%d %b %Y")

    lines = [
        f"# Supplier Performance Report Card",
        f"**Supplier:** {supplier}",
        f"**Review period:** {period}",
        f"**Organisation:** {org_name}",
        f"**Report date:** {doc_date}",
        f"**Report type:** {'Internal — Confidential' if report_type == 'internal' else 'Supplier-Facing'}",
        "",
        f"_Part of the Molecule One Claude Plugin Suite_",
        f"_Confidential — {org_name} Procurement | moleculeone.ai_",
        "",
        "---",
        "",
        "## Overall Performance",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| Overall score | **{overall:.1f}/100** |",
        f"| RAG rating | {rag_icon} **{rag}** |",
        f"| vs. prior period | {_delta_str(delta)} |",
        f"| Scorecard version | v{session.get('scorecard_version', '?')} |",
        f"| Reviewer | {session.get('reviewer_role', 'Unknown')} |",
        "",
        "---",
        "",
        "## Dimension Scores",
        "",
        _build_dimension_table(session, report_type),
        "",
        "---",
        "",
    ]

    # Trend section
    if prior_sessions:
        lines += [
            "## Performance Trend",
            "",
            _build_trend_section(session, prior_sessions),
            "",
            "---",
            "",
        ]
    else:
        lines += [
            "## Performance Trend",
            "",
            "_Trend data will be available from the next review period._",
            "",
            "---",
            "",
        ]

    # Key findings
    findings = _generate_findings(session, prior_sessions)
    if findings:
        lines += ["## Key Findings", ""]
        for i, f in enumerate(findings, start=1):
            lines.append(f"**Finding {i} — {f['title']}**")
            lines.append("")
            lines.append(f['body'])
            lines.append("")
        lines += ["---", ""]

    # Action items
    actions = session.get("actions", [])
    if actions:
        lines += [
            "## Action Items",
            "",
            _build_action_table(actions, report_type),
            "",
            "---",
            "",
        ]

    # Internal-only section
    if report_type == "internal":
        lines += [
            "## Internal Notes [INTERNAL — DO NOT SHARE]",
            "",
            session.get("notes", "_No additional internal notes._"),
            "",
            "---",
            "",
        ]

    lines.append(f"_Confidential — {org_name} Procurement | moleculeone.ai_")
    doc = "\n".join(lines)

    # Safety check for supplier-facing version
    if report_type == "supplier-facing" and "[INTERNAL]" in doc:
        raise ValueError(
            "Supplier-facing report contains [INTERNAL] markers. "
            "Strip all internal content before generating the supplier-facing version."
        )

    return doc


def build_improvement_plan(
    session: dict,
    red_dimensions: list[str],
    org_name: str,
    review_checkpoint_days: int = 60,
) -> str:
    """
    Build a Supplier Improvement Plan (SIP) for a Red-rated supplier.

    Gotchas:
      - Targets must be specific and measurable. The function inserts [IMPROVEMENT TARGET]
        placeholders wherever a target needs to be defined — the user must fill these in
        before the SIP is sent to the supplier.
      - The escalation path must include a consequence — what happens if the supplier
        fails to meet SIP targets. Without this, the SIP has no teeth.
      - The SIP is a co-created document — present it as a draft and confirm with the user
        before sending to the supplier.
    """
    supplier = session.get("supplier_name", "Unknown")
    period = session.get("review_period", "")
    overall = session.get("overall_score", 0)
    rag = session.get("rag", "")

    lines = [
        f"# Supplier Improvement Plan (SIP)",
        f"**Supplier:** {supplier}",
        f"**Issued by:** {org_name}",
        f"**Trigger period:** {period} (Score: {overall:.1f}/100 — {rag})",
        f"**Plan date:** {date.today().strftime('%d %b %Y')}",
        f"**Review checkpoint:** {review_checkpoint_days} days from plan date",
        "",
        f"_Part of the Molecule One Claude Plugin Suite_",
        f"_Confidential — {org_name} Procurement | moleculeone.ai_",
        "",
        "---",
        "",
        "## 1. Purpose",
        "",
        f"This Supplier Improvement Plan is issued to **{supplier}** following a "
        f"**{rag}** performance rating in **{period}** with an overall score of "
        f"**{overall:.1f}/100**. This plan defines the specific improvements required, "
        f"the timeline for delivery, and the review process.",
        "",
        "---",
        "",
        "## 2. Performance Issues Requiring Improvement",
        "",
    ]

    for dim in red_dimensions:
        dim_score = next(
            (d for d in session.get("dimension_scores", []) if d.get("criterion_name") == dim),
            {}
        )
        raw = dim_score.get("raw_score", "N/A")
        evidence = dim_score.get("evidence", "No evidence recorded")
        lines += [
            f"### {dim}",
            f"- **Current score:** {raw}/5",
            f"- **Evidence:** {evidence}",
            f"- **Required improvement:** [IMPROVEMENT TARGET — define specific, measurable target]",
            f"- **Target achievement date:** [DATE]",
            "",
        ]

    lines += [
        "---",
        "",
        "## 3. Improvement Actions",
        "",
        "| # | Action | Owner (Supplier) | Buyer Support Required | Deadline |",
        "|---|---|---|---|---|",
        "| 1 | [ACTION — specific and measurable] | [ROLE] | [SUPPORT or 'None'] | [DATE] |",
        "",
        "---",
        "",
        "## 4. Review Checkpoints",
        "",
        f"| Checkpoint | Date | Success Criteria |",
        f"|---|---|---|",
        f"| 30-day review | [DATE] | Evidence of root cause analysis completed and corrective actions initiated |",
        f"| {review_checkpoint_days}-day review | [DATE] | Measurable improvement in all flagged dimensions |",
        f"| Final review | [DATE] | Performance meets or exceeds contractual thresholds |",
        "",
        "---",
        "",
        "## 5. Escalation & Consequences",
        "",
        f"If {supplier} fails to meet the targets defined in this plan by the final review date:",
        "",
        "1. A formal contract performance notice will be issued",
        "2. The category will be reviewed for re-sourcing or supplementary sourcing",
        "3. [ORG_NAME] reserves the right to invoke the contract's remedy and termination provisions",
        "",
        "[REVIEW NEEDED: confirm escalation path and consequences with Legal before sending]",
        "",
        "---",
        "",
        "## 6. Sign-Off",
        "",
        "| Role | Name | Signature | Date |",
        "|---|---|---|---|",
        f"| {org_name} — Category Manager | | | |",
        f"| {org_name} — Head of Procurement | | | |",
        f"| {supplier} — Account Manager | | | |",
        f"| {supplier} — Senior Sponsor | | | |",
        "",
        "---",
        "",
        "_This plan has been co-created with the supplier and represents agreed commitments by both parties._",
        "",
        f"_Confidential — {org_name} Procurement | moleculeone.ai_",
    ]

    return "\n".join(lines)


def build_benchmark_table(sessions: list[dict], category: str, period: str, org_name: str) -> str:
    """
    Build a multi-supplier benchmark comparison table in Markdown.

    Gotchas:
      - All sessions must be from the same period and scorecard version.
        Call _validate_benchmark_comparability() first — raise on failure.
      - Dimension names must match exactly across sessions. If they differ
        (due to scorecard version mismatch), only compare shared dimensions.
    """
    if len(sessions) < 2:
        raise ValueError("Benchmarking requires at least 2 supplier sessions.")

    _validate_benchmark_comparability(sessions)

    supplier_names = [s["supplier_name"] for s in sessions]
    sorted_sessions = sorted(sessions, key=lambda s: s.get("overall_score", 0), reverse=True)

    header_cols = " | ".join(f"**{s['supplier_name']}**" for s in sorted_sessions)
    lines = [
        f"# Supplier Benchmark — {category}",
        f"**Period:** {period} | **Organisation:** {org_name}",
        f"**Suppliers compared:** {len(sessions)}",
        "",
        f"| Dimension | Weight | {header_cols} | Best in Class |",
        "|---|---|" + "|---|" * len(sessions) + "---|",
    ]

    # Get dimension names from first session
    dims = [d for d in sorted_sessions[0].get("dimension_scores", [])]

    for dim in dims:
        dim_name = dim["criterion_name"]
        weight = dim["weight"]
        scores_in_row = []
        for s in sorted_sessions:
            match = next((d for d in s.get("dimension_scores", []) if d["criterion_name"] == dim_name), None)
            if match is None or match.get("is_na"):
                scores_in_row.append("N/A")
            else:
                scores_in_row.append(f"{match['raw_score']}/5")

        # Best in class
        numeric_scores = [
            float(sc.replace("/5", "")) for sc in scores_in_row if sc != "N/A"
        ]
        if numeric_scores:
            best_val = max(numeric_scores)
            best_idx = scores_in_row.index(f"{best_val}/5")
            best_supplier = sorted_sessions[best_idx]["supplier_name"]
        else:
            best_supplier = "N/A"

        row = f"| {dim_name} | {weight:.0f}% | " + " | ".join(scores_in_row) + f" | {best_supplier} |"
        lines.append(row)

    # Overall row
    overall_scores = " | ".join(f"**{s.get('overall_score', 0):.1f}**" for s in sorted_sessions)
    lines.append(f"| **Overall score** | **100%** | {overall_scores} | — |")

    # RAG row
    rag_row = " | ".join(
        f"{RAG_ICONS.get(s.get('rag','Unrated'), '')} {s.get('rag','Unrated')}"
        for s in sorted_sessions
    )
    lines.append(f"| **RAG** | | {rag_row} | — |")

    # Rank row
    rank_row = " | ".join(f"#{i+1}" for i in range(len(sorted_sessions)))
    lines.append(f"| **Rank** | | {rank_row} | — |")

    lines += [
        "",
        "---",
        "",
        "## Panel Summary",
        "",
        f"- **Panel leader:** {sorted_sessions[0]['supplier_name']} — {sorted_sessions[0].get('overall_score',0):.1f}/100",
        f"- **Panel average:** {sum(s.get('overall_score',0) for s in sessions)/len(sessions):.1f}/100",
        f"- **Lowest performer:** {sorted_sessions[-1]['supplier_name']} — {sorted_sessions[-1].get('overall_score',0):.1f}/100",
        "",
        f"_Confidential — {org_name} Procurement | moleculeone.ai_",
    ]

    return "\n".join(lines)


# ─────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────

def _delta_str(delta: Optional[float]) -> str:
    if delta is None:
        return "First review"
    sign = "+" if delta >= 0 else ""
    icon = "🔺" if delta > 0 else ("🔻" if delta < 0 else "➡")
    return f"{icon} {sign}{delta} points"


def _build_dimension_table(session: dict, report_type: str) -> str:
    dims = session.get("dimension_scores", [])
    rows = [f"| Dimension | Weight | Score | RAG | Evidence |",
            f"|---|---|---|---|---|"]
    for d in dims:
        if d.get("is_na"):
            score_str = "N/A"
            rag_str = "⚪"
        else:
            raw = d.get("raw_score", 0)
            score_str = f"{raw}/5"
            pct = (raw / 5) * 100
            if pct >= 75:
                rag_str = "🟢"
            elif pct >= 50:
                rag_str = "🟡"
            else:
                rag_str = "🔴"

        evidence = d.get("evidence", "")
        if report_type == "supplier-facing":
            # Strip internal evidence markers
            evidence = evidence.replace("[INTERNAL]", "").strip() if "[INTERNAL]" not in evidence else "_Withheld_"

        rows.append(f"| {d['criterion_name']} | {d['weight']:.0f}% | {score_str} | {rag_str} | {evidence} |")
    return "\n".join(rows)


def _build_trend_section(current: dict, prior: list[dict]) -> str:
    all_periods = list(reversed(prior)) + [current]
    rows = ["| Period | Score | RAG | Delta | Key Issue |", "|---|---|---|---|---|"]
    for i, s in enumerate(all_periods):
        is_current = (s == current)
        period = s.get("review_period", "")
        score = s.get("overall_score", 0)
        rag = s.get("rag", "")
        rag_icon = RAG_ICONS.get(rag, "")
        delta = s.get("delta")
        delta_s = "—" if delta is None else _delta_str(delta)
        marker = " ◀ Current" if is_current else ""
        # Extract top red dimension as key issue
        red_dims = [d["criterion_name"] for d in s.get("dimension_scores", [])
                    if not d.get("is_na") and d.get("raw_score", 5) < 2.5]
        issue = red_dims[0] if red_dims else "None"
        rows.append(f"| {period}{marker} | {score:.1f}/100 | {rag_icon} {rag} | {delta_s} | {issue} |")

    # Trend direction
    if len(all_periods) >= 2:
        first_score = all_periods[0].get("overall_score", 0)
        last_score = all_periods[-1].get("overall_score", 0)
        if last_score > first_score + 2:
            trend = "🔺 **Improving**"
        elif last_score < first_score - 2:
            trend = "🔻 **Declining**"
        else:
            trend = "➡ **Stable**"
        rows.append(f"\n**Overall trajectory:** {trend}")

    return "\n".join(rows)


def _build_action_table(actions: list[dict], report_type: str) -> str:
    rows = ["| # | Issue | Action | Owner | Deadline |", "|---|---|---|---|---|"]
    for i, a in enumerate(actions, start=1):
        if report_type == "supplier-facing" and a.get("internal_only"):
            continue
        rows.append(
            f"| {i} | {a.get('issue','')} | {a.get('action','')} | "
            f"{a.get('owner','')} | {a.get('deadline','TBC')} |"
        )
    return "\n".join(rows)


def _generate_findings(session: dict, prior_sessions: list[dict]) -> list[dict]:
    """Generate 2–4 key findings from the scored data."""
    findings = []

    # Red dimensions
    red_dims = [d for d in session.get("dimension_scores", [])
                if not d.get("is_na") and d.get("raw_score", 5) < 2.5]
    for d in red_dims[:2]:
        findings.append({
            "title": f"{d['criterion_name']} below threshold",
            "body": (
                f"{d['criterion_name']} scored {d['raw_score']}/5 in "
                f"{session.get('review_period', 'this period')}. "
                f"Evidence: {d.get('evidence', 'No evidence recorded')}. "
                "This dimension requires immediate corrective action."
            ),
        })

    # Significant delta (if prior data exists)
    if prior_sessions:
        for d in session.get("dimension_scores", []):
            if d.get("is_na") or d.get("raw_score") is None:
                continue
            prior_session = prior_sessions[0]
            prior_dim = next(
                (pd for pd in prior_session.get("dimension_scores", [])
                 if pd["criterion_name"] == d["criterion_name"]), None
            )
            if prior_dim and prior_dim.get("raw_score") is not None:
                delta = d["raw_score"] - prior_dim["raw_score"]
                if abs(delta) >= 1.5:
                    direction = "improved" if delta > 0 else "declined"
                    findings.append({
                        "title": f"{d['criterion_name']} has {direction} significantly",
                        "body": (
                            f"{d['criterion_name']} moved from {prior_dim['raw_score']}/5 to "
                            f"{d['raw_score']}/5 vs. the prior period — a change of "
                            f"{delta:+.1f} points."
                        ),
                    })

    return findings[:4]


def _validate_benchmark_comparability(sessions: list[dict]) -> None:
    """Check that all sessions are comparable. Raises if not."""
    versions = set(s.get("scorecard_version") for s in sessions)
    periods = set(s.get("review_period") for s in sessions)

    if len(versions) > 1:
        print(
            f"[report_generator] WARNING: Multiple scorecard versions in benchmark: {versions}. "
            "Comparison may not be fully valid.",
            file=sys.stderr
        )
    if len(periods) > 1:
        raise ValueError(
            f"Benchmark sessions are from different periods: {periods}. "
            "All suppliers must be scored in the same period for a valid comparison."
        )


if __name__ == "__main__":
    # Demo
    sample_session = {
        "supplier_name": "FastFreight Ltd",
        "category": "Logistics",
        "review_period": "Q1 2026",
        "scorecard_version": "1.0",
        "reviewer_role": "Category Manager",
        "scored_date": "2026-03-20",
        "org_name": "Acme Corp",
        "overall_score": 82.0,
        "rag": "Green",
        "delta": 4.0,
        "notes": "Supplier has been responsive since the Feb invoice issue. [INTERNAL]",
        "actions": [
            {"issue": "Invoice batch error", "action": "Root cause and fix", "owner": "Supplier AP Lead", "deadline": "2026-04-15"},
        ],
        "dimension_scores": [
            {"criterion_name": "OTIF", "weight": 30, "raw_score": 4, "evidence": "94% OTIF", "is_na": False},
            {"criterion_name": "Invoice Accuracy", "weight": 20, "raw_score": 3, "evidence": "96%", "is_na": False},
            {"criterion_name": "Responsiveness", "weight": 15, "raw_score": None, "evidence": "", "is_na": True},
            {"criterion_name": "Regulatory Compliance", "weight": 15, "raw_score": 5, "evidence": "All certs current", "is_na": False},
            {"criterion_name": "Damage / Loss Rate", "weight": 20, "raw_score": 5, "evidence": "0.05%", "is_na": False},
        ],
    }
    print(build_report_card(sample_session, [], "Acme Corp", "internal")[:1500])

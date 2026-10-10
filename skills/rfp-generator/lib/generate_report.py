"""
generate_report.py — Report Formatter & Output Writer
Part of the Molecule One RFP Generator skill.

Formats scorecard data and evaluation outputs into structured markdown
or plain text that Claude can include in Word document generation.

Gotchas:
  - This module produces formatted TEXT output, not Word files directly.
    Claude uses the output as content for Word document generation via the docx skill.
  - Always include the weights used in every report output — an undocumented
    scorecard is not audit-ready.
  - Never suppress disqualified suppliers from the report. List them with reasons.
"""

import json
from datetime import date
from typing import Optional


def format_scorecard_report(scorecard: dict, org_name: str = "",
                             evaluator: str = "Claude / Procurement Team") -> str:
    """
    Format a scorecard JSON (from score_responses.generate_scorecard_json)
    into a clean markdown report ready for insertion into a Word document.

    Gotchas:
      - If audit.all_missing_data_resolved is False, add a prominent warning
        at the top — a scorecard with unresolved flags is not final.
      - Include the date of evaluation in the header — scorecards without
        dates cannot be relied on as records.
    """
    lines = []
    today = date.today().strftime("%d %b %Y")

    lines.append(f"# Supplier Evaluation Scorecard")
    lines.append(f"**RFP Reference:** {scorecard.get('rfp_reference', 'N/A')}")
    lines.append(f"**Category:** {scorecard.get('category', 'N/A')}")
    lines.append(f"**Organisation:** {org_name}")
    lines.append(f"**Evaluation Date:** {today}")
    lines.append(f"**Evaluator:** {evaluator}")
    lines.append("")

    # Audit warning
    audit = scorecard.get("audit", {})
    if not audit.get("all_missing_data_resolved", True):
        lines.append("> ⚠️ **WARNING: This scorecard contains unresolved data flags.**")
        lines.append("> It is NOT final until all flags below are resolved and acknowledged.")
        lines.append("")

    # Weights
    weights = scorecard.get("weights_applied", {})
    lines.append("## Evaluation Weights Applied")
    for k, v in weights.items():
        lines.append(f"- {k.title()}: {v}%")
    lines.append("")

    # Results table — section-level breakdown
    lines.append("## Ranked Results")
    lines.append("")

    qualified = [r for r in scorecard.get("results", []) if r["rank"] != "DISQUALIFIED"]
    disqualified = [r for r in scorecard.get("results", []) if r["rank"] == "DISQUALIFIED"]

    # Build dynamic header from section scores of first qualified supplier
    section_headers = []
    if qualified:
        section_scores = qualified[0].get("section_scores", {})
        for sec_label, sec_data in section_scores.items():
            short = sec_label.split(" — ")[-1][:12]  # Truncate for table width
            pct = sec_data.get("weight_pct", "")
            section_headers.append(f"{short} ({pct}%)")

    header = "| Rank | Supplier | " + " | ".join(section_headers) + " | **Total** |"
    divider = "|---|---|" + "|---|" * len(section_headers) + "---|"
    lines.append(header)
    lines.append(divider)

    for r in qualified:
        tie_note = " ⚠️ Near-tie" if "tie_warning" in r else ""
        section_scores = r.get("section_scores", {})
        section_cells = " | ".join(
            str(v.get("contribution", "N/A")) for v in section_scores.values()
        )
        lines.append(
            f"| {r['rank']}{tie_note} | {r['supplier']} | "
            f"{section_cells} | "
            f"**{r.get('final_score', r.get('weighted_total', 'N/A'))}** |"
        )
        if r.get("missing_data_flags"):
            for flag in r["missing_data_flags"]:
                lines.append(f"  - ⚠️ Data flag: {flag}")

    lines.append("")

    # Near-tie warning
    for r in qualified:
        if "tie_warning" in r:
            lines.append(f"> ⚠️ **Near-tie:** {r['tie_warning']}")
            lines.append("")

    # Disqualified
    if disqualified:
        lines.append("## Disqualified Suppliers")
        for r in disqualified:
            lines.append(f"- **{r['supplier']}** — {r.get('reason', 'No reason recorded')}")
        lines.append("")

    lines.append("---")
    lines.append("*This document is confidential. Do not share with suppliers.*")

    return "\n".join(lines)


def format_recommendation_memo(scorecard: dict, recommendation_text: str,
                                next_steps: list[str] = None,
                                org_name: str = "") -> str:
    """
    Format a recommendation memo for CPO or decision-maker review.

    recommendation_text: 2-3 sentences citing specific evidence.
    next_steps: list of action items (e.g. ["Issue shortlist notifications", "Schedule negotiations"])

    Gotchas:
      - The memo should cite specific evidence from proposals — not generic praise.
        "Supplier B's proposal demonstrated X, scoring Y on Z" not "Supplier B looks strong."
      - Always note any risks or conditions attached to the recommendation.
      - This memo is not an award decision — make that clear in the language.
    """
    today = date.today().strftime("%d %b %Y")
    ranked = [r for r in scorecard.get("results", []) if r["rank"] != "DISQUALIFIED"]
    top_supplier = ranked[0]["supplier"] if ranked else "N/A"

    lines = [
        f"# Procurement Recommendation Memo",
        f"**To:** CPO / Decision-Maker",
        f"**From:** Procurement Team",
        f"**Date:** {today}",
        f"**Re:** {scorecard.get('category', 'N/A')} — {scorecard.get('rfp_reference', 'N/A')}",
        "",
        "## Recommendation",
        recommendation_text,
        "",
        "## Evaluation Summary",
        f"**Suppliers evaluated:** {len(ranked)} (plus {len([r for r in scorecard.get('results', []) if r['rank'] == 'DISQUALIFIED'])} disqualified)",
        f"**Shortlist recommended:** {', '.join([r['supplier'] for r in ranked[:2]])}",
        f"**Recommended for award (subject to negotiation):** {top_supplier}",
        "",
        "## Next Steps"
    ]

    default_steps = [
        "Issue shortlist notification to successful suppliers",
        "Issue decline notification to unsuccessful suppliers",
        "Schedule negotiation sessions with shortlisted suppliers",
        "Confirm internal approval authority for contract award",
        "Target contract award: [DATE]"
    ]
    for step in (next_steps or default_steps):
        lines.append(f"- {step}")

    lines.append("")
    lines.append("---")
    lines.append("*This memo is for internal decision-making purposes only.*")

    return "\n".join(lines)


def format_rfx_log_entry(rfp_ref: str, category: str, mode: str,
                          suppliers_invited: list[str],
                          outcome: str = "Issued",
                          lessons: str = "") -> str:
    """
    Format a log entry for appending to ${CLAUDE_PLUGIN_DATA}/rfx-history.log

    Gotchas:
      - Log entries must be appended, never overwritten.
      - Include supplier names for future reference — anonymise only if the
        user explicitly requests it.
    """
    today = date.today().isoformat()
    entry = (
        f"\n---\n"
        f"DATE: {today}\n"
        f"REFERENCE: {rfp_ref}\n"
        f"CATEGORY: {category}\n"
        f"MODE: {mode}\n"
        f"SUPPLIERS_INVITED: {len(suppliers_invited)} — {', '.join(suppliers_invited)}\n"
        f"OUTCOME: {outcome}\n"
        f"LESSONS: {lessons or 'None recorded'}\n"
    )
    return entry


if __name__ == "__main__":
    # Example — Claude generates an investigate script using these helpers
    sample_scorecard = {
        "rfp_reference": "RFP-2026-001",
        "category": "IT Security Services",
        "weights_applied": {"price": 40, "quality": 30, "delivery": 20, "risk": 10},
        "results": [
            {"rank": 1, "supplier": "SecureNet Ltd", "weighted_total": 8.2,
             "sub_scores": {"price": 9.1, "quality": 7.5, "delivery": 8.0, "risk": 7.5},
             "missing_data_flags": [], "notes": {}},
            {"rank": 2, "supplier": "CyberGuard Inc", "weighted_total": 7.9,
             "sub_scores": {"price": 7.0, "quality": 9.0, "delivery": 8.5, "risk": 8.0},
             "missing_data_flags": [], "notes": {}},
            {"rank": "DISQUALIFIED", "supplier": "QuickSec Ltd",
             "reason": "No ISO 27001 certificate provided"}
        ],
        "audit": {"weights_locked_before_scoring": True, "all_missing_data_resolved": True}
    }

    print(format_scorecard_report(sample_scorecard, org_name="Acme Corp"))
    print("\n" + "="*60 + "\n")
    print(format_recommendation_memo(
        sample_scorecard,
        recommendation_text=(
            "SecureNet Ltd is recommended for shortlisting based on the highest weighted "
            "total score of 8.2/10, driven by competitive pricing (£82,000 TCO — lowest bid) "
            "and strong risk management documentation. CyberGuard Inc is recommended as "
            "second-ranked shortlist supplier, leading on technical quality (9.0/10)."
        )
    ))

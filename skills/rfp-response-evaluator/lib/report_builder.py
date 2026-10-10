"""
report_builder.py — RFP Response Evaluator
Molecule One Claude Plugin Suite

Assembles the final evaluation outputs from a ScoredSession object:
  1. Word narrative report (.docx) — internal, with methodology and findings
  2. Excel scoring grid (.xlsx)    — 4 tabs: Summary, Section Scores, Pricing, Disqualifications

GOTCHAS:
- Never include internal commentary or strategic notes in supplier-facing outputs.
  The internal report and the supplier outcome letter are two separate documents.
- RAG colours in Excel: Green #70AD47, Amber #FFC000, Red #FF0000.
  Use cell background colour — not font colour — for score cells.
- Recommendations must cite specific evidence and scores — never generic praise.
- Outcome letters must be drafted for ALL suppliers — not just the winner.
- Rerun reports must clearly show "Revised Evaluation" on the cover page with
  the reason for revision and the approval record.

Usage:
    builder = ReportBuilder(session=scored_session, config=config_dict)
    builder.build_word_report(output_path="...", template_dir="...")
    builder.build_excel_scorecard(output_path="...")
    builder.build_outcome_letter(supplier="Supplier A", outcome="shortlisted", output_path="...")
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Optional
from pathlib import Path
from datetime import date


@dataclass
class ReportConfig:
    """Configuration for report generation."""
    org_name: str
    rfp_reference: str
    category: str
    evaluator_role: str
    currency: str = "USD"
    include_rerun_notice: bool = False
    rerun_reason: Optional[str] = None


class ReportBuilder:
    """
    Assemble Word and Excel outputs from a ScoredSession.
    Calls the docx and xlsx skills for document generation.
    """

    RAG_COLOURS = {
        "Green": "#70AD47",
        "Amber": "#FFC000",
        "Red": "#FF0000",
        "NA": "#D9D9D9",
        "Disqualified": "#A6A6A6",
    }

    def __init__(self, session, config: ReportConfig):
        self.session = session
        self.config = config

    # ------------------------------------------------------------------ #
    # WORD REPORT                                                          #
    # ------------------------------------------------------------------ #

    def build_word_report(self, output_path: str, template_path: Optional[str] = None) -> str:
        """
        Assemble the internal Word evaluation report.

        Structure:
          1. Cover page
          2. Evaluation methodology
          3. Disqualification log
          4. Section-by-section findings (per supplier)
          5. Side-by-side comparison matrix
          6. Summary and recommendation
          7. Appendix: clarification log

        GOTCHA: This is the INTERNAL version. Never send this to suppliers.
        Use build_outcome_letter() for supplier-facing communications.

        Returns the populated template as a string (for use with docx skill).
        """
        ranked = self.session.ranked_results()
        disqualified = self.session.disqualified()

        sections_text = self._build_section_findings(ranked)
        matrix_text = self._build_comparison_matrix(ranked)
        summary_text = self._build_summary(ranked, disqualified)
        dq_log = self._build_dq_log(disqualified)

        report = f"""# {self.config.org_name} — RFP Evaluation Report
**Category:** {self.config.category}
**RFP Reference:** {self.config.rfp_reference}
**Evaluation Date:** {date.today().strftime("%d %b %Y")}
**Evaluator:** {self.config.evaluator_role}
**Criteria Version:** {self.session.criteria_version}
**Part of the Molecule One Claude Plugin Suite**
_Confidential — {self.config.org_name} Procurement | moleculeone.ai_

{"---" if self.config.include_rerun_notice else ""}
{"**⚠ REVISED EVALUATION**" if self.config.include_rerun_notice else ""}
{"Reason for revision: " + (self.config.rerun_reason or "") if self.config.include_rerun_notice else ""}

---

## 1. Evaluation Methodology

**Scoring scale:** 1–10 per section (10 = Outstanding, 5 = Acceptable, 1 = Inadequate)
**Overall score:** Weighted average across all sections (out of 10)
**Weights applied:**
{self._format_weights()}

**RAG thresholds:**
- 🟢 Green: ≥7.5/10 — Strong response; proceed to shortlist
- 🟡 Amber: 5.0–7.4/10 — Acceptable but gaps identified; seek clarification
- 🔴 Red: <5.0/10 — Significant gaps; consider disqualification or final position

**Criteria source:** {self.session.criteria_version} ({getattr(self.session, "criteria_source", "confirmed by evaluation panel")})

---

## 2. Disqualification Log

{dq_log}

---

## 3. Section-by-Section Findings

{sections_text}

---

## 4. Side-by-Side Comparison Matrix

{matrix_text}

---

## 5. Summary and Recommendation

{summary_text}

---

_Confidential — {self.config.org_name} Procurement | moleculeone.ai_
"""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)
        return output_path

    def _format_weights(self) -> str:
        lines = []
        for section_name, weight in self.session.weights_used.items():
            lines.append(f"- {section_name}: {weight}%")
        return "\n".join(lines)

    def _build_section_findings(self, ranked: list) -> str:
        """Build section-by-section narrative findings per supplier."""
        if not ranked:
            return "_No qualified suppliers to report on._"
        lines = []
        # Gather all section IDs from first supplier
        if ranked and ranked[0].section_scores:
            section_ids = list({ss.section_id: ss for ss in ranked[0].section_scores}.keys())
        else:
            return "_No section scores available._"

        for ss_ref in ranked[0].section_scores:
            lines.append(f"### {ss_ref.section_name} ({ss_ref.weight}% weight)\n")
            for supplier_result in ranked:
                ss = next((s for s in supplier_result.section_scores
                           if s.section_id == ss_ref.section_id), None)
                if ss:
                    score_str = "N/A" if ss.is_na else f"{ss.raw_score}/10"
                    lines.append(f"**{supplier_result.supplier}:** {score_str}")
                    if ss.evidence:
                        lines.append(f"> {ss.evidence}")
                    if ss.notes:
                        lines.append(f"_Note: {ss.notes}_")
            lines.append("")
        return "\n".join(lines)

    def _build_comparison_matrix(self, ranked: list) -> str:
        """Build side-by-side comparison table."""
        if not ranked:
            return "_No qualified suppliers._"
        suppliers = [r.supplier for r in ranked]
        header = "| Section | Weight | " + " | ".join(suppliers) + " | Best in Section |"
        divider = "|---|---|" + "---|" * (len(suppliers) + 1)
        rows = [header, divider]

        if ranked and ranked[0].section_scores:
            for ss_ref in ranked[0].section_scores:
                scores = []
                best_score = -1
                best_supplier = ""
                for r in ranked:
                    ss = next((s for s in r.section_scores
                               if s.section_id == ss_ref.section_id), None)
                    if ss and not ss.is_na and ss.raw_score is not None:
                        scores.append(f"{ss.raw_score}/10")
                        if ss.raw_score > best_score:
                            best_score = ss.raw_score
                            best_supplier = r.supplier
                    else:
                        scores.append("N/A")
                row = f"| {ss_ref.section_name} | {ss_ref.weight}% | " + " | ".join(scores) + f" | {best_supplier} |"
                rows.append(row)

        # Overall row
        overall_scores = [
            f"**{r.overall_score()}/10**" if r.overall_score() else "N/A"
            for r in ranked
        ]
        rows.append(
            "| **Weighted Total** | **100%** | " + " | ".join(overall_scores) + " | |"
        )
        # Rank row
        ranks = ["1st", "2nd", "3rd", "4th", "5th", "6th"]
        rank_cells = [ranks[i] if i < len(ranks) else f"{i+1}th" for i in range(len(ranked))]
        rows.append("| **Rank** | | " + " | ".join(rank_cells) + " | |")

        return "\n".join(rows)

    def _build_summary(self, ranked: list, disqualified: list) -> str:
        """Build executive summary with recommendation."""
        if not ranked:
            return "_No qualified suppliers proceeded to scoring._"
        top = ranked[0]
        shortlist = ranked[:min(2, len(ranked))]
        shortlist_names = " and ".join(r.supplier for r in shortlist)
        lines = [
            f"**Panel overview:** {len(ranked) + len(disqualified)} suppliers evaluated "
            f"| {len(disqualified)} disqualified | {len(ranked)} scored\n",
            "**Ranked results:**\n",
        ]
        for i, r in enumerate(ranked):
            rag = r.rag_rating({"green_min": 7.5, "amber_min": 5.0})
            rag_emoji = {"Green": "🟢", "Amber": "🟡", "Red": "🔴"}.get(rag, "")
            lines.append(
                f"{i+1}. **{r.supplier}** — {r.overall_score()}/10 — {rag_emoji} {rag}"
            )
        lines.append(f"\n**Recommended shortlist:** {shortlist_names}")
        lines.append(
            f"\n**Recommended for award:** {top.supplier} — "
            f"overall score {top.overall_score()}/10. "
            "This recommendation is based solely on the agreed evaluation criteria. "
            f"Subject to reference checks and contract negotiation."
        )
        return "\n".join(lines)

    def _build_dq_log(self, disqualified: list) -> str:
        if not disqualified:
            return "_No suppliers disqualified._"
        lines = ["| Supplier | Reason |", "|---|---|"]
        for d in disqualified:
            lines.append(f"| {d.supplier} | {d.disqualification_reason or 'Not specified'} |")
        return "\n".join(lines)

    # ------------------------------------------------------------------ #
    # EXCEL SCORECARD                                                      #
    # ------------------------------------------------------------------ #

    def get_excel_data(self) -> dict:
        """
        Return structured data for Excel generation via the xlsx skill.

        Returns a dict with 4 tabs:
            summary         — ranked scores with RAG
            section_scores  — full scoring grid
            pricing         — TCO normalisation workings
            disqualifications — DQ log
        """
        ranked = self.session.ranked_results()
        disqualified = self.session.disqualified()

        summary_rows = []
        for i, r in enumerate(ranked):
            rag = r.rag_rating({"green_min": 7.5, "amber_min": 5.0})
            summary_rows.append({
                "Rank": i + 1,
                "Supplier": r.supplier,
                "Overall Score (/10)": r.overall_score(),
                "RAG": rag,
                "RAG Colour": self.RAG_COLOURS.get(rag, ""),
                "N/A Sections": ", ".join(r.na_sections) or "None",
            })

        section_rows = []
        if ranked and ranked[0].section_scores:
            for ss_ref in ranked[0].section_scores:
                row = {
                    "Section": ss_ref.section_name,
                    "Weight (%)": ss_ref.weight,
                }
                for r in ranked:
                    ss = next((s for s in r.section_scores
                               if s.section_id == ss_ref.section_id), None)
                    if ss:
                        row[f"{r.supplier} — Raw (/10)"] = (
                            "N/A" if ss.is_na else ss.raw_score
                        )
                        row[f"{r.supplier} — Weighted"] = (
                            "N/A" if ss.is_na else round(ss.weighted_contribution() or 0, 2)
                        )
                section_rows.append(row)

        pricing_rows = []
        for r in ranked:
            if r.tco_normalised:
                pricing_rows.append({
                    "Supplier": r.supplier,
                    "TCO (Normalised)": r.tco_normalised,
                    "Currency": r.tco_currency,
                })

        dq_rows = []
        for d in disqualified:
            dq_rows.append({
                "Supplier": d.supplier,
                "Disqualified": "Yes",
                "Reason": d.disqualification_reason or "",
            })

        return {
            "summary": summary_rows,
            "section_scores": section_rows,
            "pricing": pricing_rows,
            "disqualifications": dq_rows,
        }

    # ------------------------------------------------------------------ #
    # OUTCOME LETTERS                                                      #
    # ------------------------------------------------------------------ #

    def build_outcome_letter(
        self,
        supplier: str,
        outcome: str,  # "shortlisted" or "unsuccessful"
        output_path: str,
        next_steps: str = "",
    ) -> str:
        """
        Draft a supplier outcome letter.
        GOTCHA: Must be sent to ALL suppliers — shortlisted and unsuccessful.
        GOTCHA: Must not contain internal scores, commentary, or rankings.
        """
        if outcome == "shortlisted":
            body = (
                f"Following a thorough evaluation of all submissions received for "
                f"{self.config.rfp_reference} — {self.config.category}, "
                f"we are pleased to inform you that {supplier} has been shortlisted "
                f"to proceed to the next stage of our procurement process.\n\n"
                f"Next steps: {next_steps or 'We will be in contact shortly with further details.'}"
            )
        else:
            body = (
                f"Following a thorough evaluation of all submissions received for "
                f"{self.config.rfp_reference} — {self.config.category}, "
                f"we regret to inform you that {supplier} has not been shortlisted "
                f"on this occasion.\n\n"
                f"We appreciate the time and effort your team invested in preparing your submission. "
                f"If you would like a debrief on the evaluation outcome, please contact us to arrange this."
            )

        letter = f"""# {self.config.org_name}
## Procurement Outcome Notification

**To:** {supplier}
**RFP Reference:** {self.config.rfp_reference}
**Category:** {self.config.category}
**Date:** {date.today().strftime("%d %b %Y")}

Dear {supplier} Team,

{body}

Yours sincerely,
{self.config.evaluator_role}
{self.config.org_name} Procurement

---
_Confidential — {self.config.org_name} Procurement | moleculeone.ai_
"""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(letter)
        return output_path


# --- __main__ demo ---
if __name__ == "__main__":
    import tempfile

    print("=== ReportBuilder Demo ===\n")

    # Build a minimal mock session
    from types import SimpleNamespace

    ss_a = SimpleNamespace(
        section_id="S1", section_name="Total Cost of Ownership",
        weight=35.0, raw_score=8.5, is_na=False,
        evidence="Quoted $240,000 TCO — lowest in panel", notes="",
        weighted_contribution=lambda: (8.5 / 10) * 35.0,
    )
    ss_b = SimpleNamespace(
        section_id="S1", section_name="Total Cost of Ownership",
        weight=35.0, raw_score=6.0, is_na=False,
        evidence="Quoted $310,000 TCO", notes="",
        weighted_contribution=lambda: (6.0 / 10) * 35.0,
    )

    sup_a = SimpleNamespace(
        supplier="Supplier A", qualified=True,
        disqualification_reason=None, section_scores=[ss_a],
        tco_normalised=240000, tco_currency="USD", na_sections=[],
        overall_score=lambda: 8.5,
        rag_rating=lambda t: "Green",
        rank_key=lambda: 8.5,
    )
    sup_b = SimpleNamespace(
        supplier="Supplier B", qualified=True,
        disqualification_reason=None, section_scores=[ss_b],
        tco_normalised=310000, tco_currency="USD", na_sections=[],
        overall_score=lambda: 6.0,
        rag_rating=lambda t: "Amber",
        rank_key=lambda: 6.0,
    )

    mock_session = SimpleNamespace(
        rfp_reference="RFP-2026-001",
        category="IT Services",
        review_period="Q2 2026",
        evaluator_role="Category Manager",
        criteria_version="1.0",
        weights_used={"Total Cost of Ownership": 35.0},
        suppliers=[sup_a, sup_b],
        ranked_results=lambda: [sup_a, sup_b],
        disqualified=lambda: [],
    )

    config = ReportConfig(
        org_name="AcmeCorp",
        rfp_reference="RFP-2026-001",
        category="IT Services",
        evaluator_role="Category Manager",
    )

    builder = ReportBuilder(session=mock_session, config=config)

    with tempfile.TemporaryDirectory() as tmpdir:
        report_path = f"{tmpdir}/evaluation_report.md"
        builder.build_word_report(output_path=report_path)
        with open(report_path) as f:
            print(f.read()[:500])
        print("...\n[Report truncated for demo]\n")

        excel_data = builder.get_excel_data()
        print("Excel tabs:", list(excel_data.keys()))
        print("Summary rows:", len(excel_data["summary"]))

    print("\nReportBuilder demo complete.")

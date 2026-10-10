"""
extract_sow.py — Source Document Extraction Helpers
Part of the Molecule One RFP Generator skill.

Handles any type of input document — SOW, contract, email thread, meeting notes,
business requirements, or a mix of all of the above.

Claude composes these functions to normalise unstructured source material into
a structured requirements brief before drafting an RFP. The docstrings contain
gotchas — read them before using.

Usage:
    from lib.extract_sow import detect_document_type, extract_from_any_document
"""

import re
import sys
import json
from pathlib import Path


# ---------------------------------------------------------------------------
# Document type detection
# ---------------------------------------------------------------------------

def detect_document_type(text: str) -> dict:
    """
    Infer the type(s) of document from the text content.

    Returns a dict:
      - primary_type: str — the most likely document type
      - secondary_types: list of str — additional types detected (e.g. contract + email)
      - confidence: "high" | "medium" | "low"
      - signals: list of str — evidence that led to the classification

    Document types: "sow", "contract", "email", "meeting_notes",
                    "business_requirements", "presentation", "mixed", "unknown"

    Gotchas:
      - Many documents are hybrid — an old contract forwarded by email, or a
        meeting note with pasted requirements. Detect all types present and
        extract from each.
      - Email threads often contain the most current version of a requirement in
        the most recent message, with older messages below. Extract in reverse
        chronological order.
      - Meeting notes rarely have formal structure — look for action items,
        decisions, and "we need" / "we want" language rather than
        formal requirement headings.
      - Presentations (PowerPoint extracted as text) lose slide structure and
        often appear as disconnected bullet fragments. Flag this and ask the
        user to confirm key requirements manually.
    """
    result = {
        "primary_type": "unknown",
        "secondary_types": [],
        "confidence": "low",
        "signals": []
    }

    text_lower = text.lower()
    scores = {t: 0 for t in ["sow", "contract", "email", "meeting_notes",
                               "business_requirements", "presentation"]}

    # --- Email signals ---
    if re.search(r'\bfrom:\s*\S+@\S+', text, re.IGNORECASE):
        scores["email"] += 3
        result["signals"].append("Email From: header detected")
    if re.search(r'\bsubject:\s*.+', text, re.IGNORECASE):
        scores["email"] += 2
        result["signals"].append("Email Subject: header detected")
    if re.search(r'\bsent:\s*\w+,\s*\d+', text, re.IGNORECASE):
        scores["email"] += 2
        result["signals"].append("Email Sent: datestamp detected")
    if re.search(r'-----original message-----|on .+ wrote:', text, re.IGNORECASE):
        scores["email"] += 3
        result["signals"].append("Email thread separator detected")
    if re.search(r'\bhi\b|\bdear\b|\bregards\b|\bthanks\b', text_lower):
        scores["email"] += 1
        result["signals"].append("Email-style salutation/sign-off detected")

    # --- Contract signals ---
    if re.search(r'\bhereby\s+agrees?\b|\bwhereas\b|\brecitals?\b', text, re.IGNORECASE):
        scores["contract"] += 3
        result["signals"].append("Legal recitals language detected")
    if re.search(r'\bclause\s+\d+|\bschedule\s+[A-Z\d]|\bannex\s+[A-Z\d]', text, re.IGNORECASE):
        scores["contract"] += 3
        result["signals"].append("Contract clause/schedule structure detected")
    if re.search(r'\bindemnif|\bliabilit|\bterminat|\bgovernin\s+law\b', text, re.IGNORECASE):
        scores["contract"] += 2
        result["signals"].append("Legal terms (indemnity/liability/termination) detected")
    if re.search(r'\bparty a\b|\bparty b\b|\bthe supplier\b|\bthe client\b', text, re.IGNORECASE):
        scores["contract"] += 2
        result["signals"].append("Contract party references detected")
    if re.search(r'\beffective date\b|\bcommencement date\b', text, re.IGNORECASE):
        scores["contract"] += 2
        result["signals"].append("Contract date language detected")

    # --- SOW signals ---
    if re.search(r'\bstatement of work\b|\bscope of work\b|\bsow\b', text, re.IGNORECASE):
        scores["sow"] += 4
        result["signals"].append("SOW title/reference detected")
    if re.search(r'\bdeliverable[s]?\b', text, re.IGNORECASE):
        scores["sow"] += 2
        result["signals"].append("Deliverables section detected")
    if re.search(r'\bacceptance criteria\b|\bdefinition of done\b', text, re.IGNORECASE):
        scores["sow"] += 2
        result["signals"].append("Acceptance criteria detected")
    if re.search(r'\bin scope\b|\bout of scope\b', text, re.IGNORECASE):
        scores["sow"] += 2
        result["signals"].append("In-scope / out-of-scope language detected")

    # --- Meeting notes signals ---
    if re.search(r'\bmeeting\s+(?:notes?|minutes?)\b|\baction\s+items?\b', text, re.IGNORECASE):
        scores["meeting_notes"] += 4
        result["signals"].append("Meeting notes/minutes header detected")
    if re.search(r'\battendees?\b|\bpresent:\b|\bfacilitator:\b', text, re.IGNORECASE):
        scores["meeting_notes"] += 2
        result["signals"].append("Meeting attendees list detected")
    if re.search(r'\bdecided\b|\bagreed\b|\baction:\b|\bowner:\b|\bdue:\b', text, re.IGNORECASE):
        scores["meeting_notes"] += 2
        result["signals"].append("Meeting action items / decisions detected")
    if re.search(r'\bnext steps\b|\bfollow.up\b', text, re.IGNORECASE):
        scores["meeting_notes"] += 1
        result["signals"].append("Next steps / follow-up language detected")

    # --- Business requirements signals ---
    if re.search(r'\brequirement[s]?\s+(?:document|spec|specification)\b', text, re.IGNORECASE):
        scores["business_requirements"] += 4
        result["signals"].append("Business requirements document header detected")
    if re.search(r'\bBRD\b|\bFRD\b|\bMRD\b|\bPRD\b', text):
        scores["business_requirements"] += 3
        result["signals"].append("BRD/FRD/MRD/PRD acronym detected")
    if re.search(r'\bMUST\b|\bSHOULD\b|\bSHALL\b|\bWILL\b', text):
        scores["business_requirements"] += 2
        result["signals"].append("MoSCoW / RFC 2119 requirements language detected")
    if re.search(r'\buser stor(?:y|ies)\b|\bas a .+ i want\b', text, re.IGNORECASE):
        scores["business_requirements"] += 2
        result["signals"].append("User story format detected")
    if re.search(r'\bfunctional requirement\b|\bnon.functional\b', text, re.IGNORECASE):
        scores["business_requirements"] += 3
        result["signals"].append("Functional/non-functional requirements structure detected")

    # --- Presentation signals ---
    if re.search(r'\bslide\s+\d+\b|\bslide:\b', text, re.IGNORECASE):
        scores["presentation"] += 3
        result["signals"].append("Slide number references detected (likely extracted from PPT)")
    if re.search(r'\[slide\b|\(slide\b', text, re.IGNORECASE):
        scores["presentation"] += 2
        result["signals"].append("Slide markers detected")

    # Determine types
    sorted_types = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    primary_type, primary_score = sorted_types[0]

    if primary_score == 0:
        result["primary_type"] = "unknown"
        result["confidence"] = "low"
    else:
        result["primary_type"] = primary_type
        result["confidence"] = "high" if primary_score >= 4 else "medium" if primary_score >= 2 else "low"

    # Secondary types: anything with score >= 2 (other than primary)
    result["secondary_types"] = [
        t for t, s in sorted_types[1:]
        if s >= 2
    ]

    return result


# ---------------------------------------------------------------------------
# Type-specific extraction strategies
# ---------------------------------------------------------------------------

def _extract_from_email(text: str) -> dict:
    """
    Extract procurement requirements from an email or email thread.

    Gotchas:
      - Most recent email in the thread is at the TOP — read top-down but
        treat later (lower) emails as background context, not current requirements.
      - "Let's go with X" or "we've decided Y" in a later email may override
        requirements stated in earlier emails — flag any contradictions.
      - Informal tone means requirements are often implied, not stated explicitly.
        "Can we make sure they can handle X?" = a requirement for X.
      - Watch for forwarded threads — the procurement requirements may be buried
        inside quoted text from a different conversation entirely.
      - Attachments referenced in emails ("see attached spec") are not in the
        text — flag these and ask the user to provide them.
    """
    result = {
        "source_type": "email",
        "participants": [],
        "implied_requirements": [],
        "explicit_requirements": [],
        "decisions": [],
        "attachments_referenced": [],
        "ambiguities": [],
        "timeline_mentions": [],
        "budget_mentions": []
    }

    # Extract email participants
    from_matches = re.findall(r'(?:From|To|Cc):\s*([^\n]+)', text, re.IGNORECASE)
    result["participants"] = [m.strip() for m in from_matches]

    # Detect attachment references
    attach_patterns = [
        r'(?:see|refer to|attached|as per)\s+(?:the\s+)?attach\w+',
        r'attach\w+\s+(?:file|doc|document|spec|brief)',
        r'\bassociated\s+(?:file|document|brief)\b'
    ]
    for p in attach_patterns:
        if re.search(p, text, re.IGNORECASE):
            result["attachments_referenced"].append(
                "Attachment reference detected — ask user to provide the attached file"
            )
            break

    # Extract timeline mentions
    date_patterns = [
        r'\b(?:by|before|deadline|due)\s+\w+\s+\d{1,2}(?:st|nd|rd|th)?,?\s*\d{4}',
        r'\b(?:end of|start of)\s+(?:Q[1-4]|\w+\s+\d{4})',
        r'\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}\b',
        r'\b(?:January|February|March|April|May|June|July|August|September|'
        r'October|November|December)\s+\d{1,2},?\s*\d{4}\b'
    ]
    for p in date_patterns:
        matches = re.findall(p, text, re.IGNORECASE)
        result["timeline_mentions"].extend(matches)

    # Budget mentions
    if re.search(r'£[\d,]+|€[\d,]+|\$[\d,]+|\bbudget\b|\bapproved spend\b', text, re.IGNORECASE):
        result["budget_mentions"].append(
            "Budget figure or reference detected — confirm disclosure decision before including in RFP"
        )

    return result


def _extract_from_contract(text: str) -> dict:
    """
    Extract requirements from an existing/previous contract.

    Use case: re-tender from an existing supplier, or using an old contract
    as the baseline specification.

    Gotchas:
      - Contract scope clauses describe what was agreed, not what is wanted next.
        Flag any differences the user may want to change for the new engagement.
      - Pricing terms in old contracts are commercially sensitive and should NOT
        be included in the new RFP. Extract scope only, not pricing.
      - Auto-renewal clauses in old contracts sometimes mean procurement is
        running a re-tender under time pressure — flag contract end date.
      - Schedules / annexes often contain the real technical specification —
        extract these separately if present.
      - Liability caps, IP ownership, and payment terms from old contracts are
        useful starting points for the new RFP's commercial terms table.
    """
    result = {
        "source_type": "contract",
        "existing_scope": [],
        "existing_supplier": None,
        "contract_end_date": None,
        "commercial_terms_found": {},
        "schedules_referenced": [],
        "ambiguities": [],
        "pricing_flagged": False
    }

    # Extract existing supplier name (Party references)
    supplier_match = re.search(
        r'(?:the supplier|service provider|contractor|vendor)["\s:]+([A-Z][^\n,\.]{2,40})',
        text, re.IGNORECASE
    )
    if supplier_match:
        result["existing_supplier"] = supplier_match.group(1).strip()

    # Flag pricing — never carry forward into new RFP
    if re.search(r'£[\d,]+|€[\d,]+|\$[\d,]+|\bday rate\b|\bunit price\b', text, re.IGNORECASE):
        result["pricing_flagged"] = True
        result["ambiguities"].append(
            "Pricing terms found in source contract — do NOT include in new RFP. "
            "Use only scope and commercial terms as reference."
        )

    # Extract referenced schedules
    schedule_matches = re.findall(
        r'(?:Schedule|Annex|Appendix|Exhibit)\s+[A-Z0-9]+[:\s—]+([^\n]{5,60})',
        text, re.IGNORECASE
    )
    result["schedules_referenced"] = schedule_matches

    if schedule_matches:
        result["ambiguities"].append(
            f"Contract references {len(schedule_matches)} schedule(s)/annex(es) — "
            "ask user to provide these as they may contain the technical specification."
        )

    # Extract commercial terms
    term_patterns = {
        "payment_terms": r'payment\s+terms?[:\s]+([^\n.]{5,60})',
        "liability_cap": r'liability\s+(?:cap|limit)[:\s]+([^\n.]{5,80})',
        "termination_notice": r'terminat\w+\s+(?:for convenience)?[:\s]+([^\n.]{5,80})',
        "ip_ownership": r'intellectual\s+property[:\s]+([^\n.]{5,80})'
    }
    for term, pattern in term_patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result["commercial_terms_found"][term] = match.group(1).strip()

    return result


def _extract_from_meeting_notes(text: str) -> dict:
    """
    Extract procurement requirements from meeting notes or minutes.

    Gotchas:
      - Meeting notes capture intent, not specification. Requirements are often
        expressed as problems to solve ("we're struggling with X") rather than
        formal requirements — extract the underlying need, not the complaint.
      - Action items assigned to someone with a due date are often the clearest
        requirements source in meeting notes.
      - Decisions marked "TBC" or "to be confirmed" are not requirements yet —
        flag these as unresolved before drafting.
      - Multiple stakeholders in a meeting may express conflicting requirements —
        flag contradictions and ask the user which view takes precedence.
      - "We discussed" ≠ "we agreed" — only extract items marked as decisions
        or actions, not exploratory discussion.
    """
    result = {
        "source_type": "meeting_notes",
        "attendees": [],
        "decisions": [],
        "action_items": [],
        "requirements_implied": [],
        "unresolved_items": [],
        "ambiguities": []
    }

    # Extract attendees
    attendee_section = re.search(
        r'(?:attendees?|present|participants?)[:\s]+([^\n]{5,200})',
        text, re.IGNORECASE
    )
    if attendee_section:
        # Split on comma, semicolon, or newline
        names = re.split(r'[,;\n]+', attendee_section.group(1))
        result["attendees"] = [n.strip() for n in names if len(n.strip()) > 2]

    # Extract action items
    action_patterns = [
        r'action[:\s]+(.{10,120})',
        r'(?:TODO|TO DO|to-do)[:\s]+(.{10,120})',
        r'([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)\s+to\s+(.{10,80})\s+by\s+(.{5,30})',
    ]
    for p in action_patterns:
        matches = re.findall(p, text, re.IGNORECASE)
        for m in matches:
            if isinstance(m, tuple):
                result["action_items"].append(" — ".join(m))
            else:
                result["action_items"].append(m.strip())

    # Extract decisions
    decision_patterns = [
        r'(?:decided|agreed|confirmed|resolved)[:\s]+(.{10,200})',
        r'decision[:\s]+(.{10,200})',
    ]
    for p in decision_patterns:
        matches = re.findall(p, text, re.IGNORECASE)
        result["decisions"].extend([m.strip() for m in matches])

    # Flag TBC / unresolved items
    tbc_matches = re.findall(
        r'(?:TBC|TBD|to be (?:confirmed|decided|agreed|discussed)|pending)[:\s]*(.{0,80})',
        text, re.IGNORECASE
    )
    for m in tbc_matches:
        item = m.strip() or "unspecified item"
        result["unresolved_items"].append(
            f"Unresolved at time of meeting: '{item}' — must be confirmed before drafting RFP"
        )

    return result


def _extract_from_business_requirements(text: str) -> dict:
    """
    Extract from a Business Requirements Document (BRD), Functional Requirements
    Document (FRD), or similar structured requirements artefact.

    Gotchas:
      - BRDs often mix business requirements (what) with technical requirements
        (how). For an RFP, extract the WHAT and leave the HOW to suppliers —
        over-specifying the how limits competition.
      - Requirements IDs (e.g. BR001, FR-12) should be preserved and referenced
        in the RFP so suppliers can confirm compliance by requirement ID.
      - Priority labels (Must Have / Should Have / Could Have) in MoSCoW-format
        BRDs are extremely useful for RFP evaluation — extract and preserve them.
      - User stories describe desired outcomes, not supplier capabilities — use
        them to frame evaluation questions, not as direct requirements.
      - Non-functional requirements (performance, security, availability) are
        often the most important and most frequently overlooked. Always check
        for an NFR section.
    """
    result = {
        "source_type": "business_requirements",
        "must_have": [],
        "should_have": [],
        "could_have": [],
        "non_functional": [],
        "requirement_ids": [],
        "ambiguities": []
    }

    # Extract MoSCoW-labelled requirements
    must_matches = re.findall(r'MUST\s+(?:have|be|support|provide)[:\s]*(.{10,150})', text, re.IGNORECASE)
    result["must_have"].extend([m.strip() for m in must_matches])

    should_matches = re.findall(r'SHOULD\s+(?:have|be|support|provide)[:\s]*(.{10,150})', text, re.IGNORECASE)
    result["should_have"].extend([m.strip() for m in should_matches])

    could_matches = re.findall(r'(?:COULD|NICE\s+TO\s+HAVE|OPTIONAL)[:\s]*(.{10,150})', text, re.IGNORECASE)
    result["could_have"].extend([m.strip() for m in could_matches])

    # Extract requirement IDs
    id_matches = re.findall(r'\b(?:BR|FR|NFR|REQ|SR)[_\-]?\d+\b', text, re.IGNORECASE)
    result["requirement_ids"] = list(set(id_matches))

    if result["requirement_ids"]:
        result["ambiguities"].append(
            f"Requirement IDs found: {', '.join(result['requirement_ids'][:10])}... "
            "Consider referencing these in the RFP so suppliers can confirm compliance by ID."
        )

    # Extract non-functional requirements section
    nfr_section = re.search(
        r'non.functional\s+requirements?[:\s\n]+(.*?)(?=\n#{1,3}\s|\Z)',
        text, re.IGNORECASE | re.DOTALL
    )
    if nfr_section:
        nfr_text = nfr_section.group(1).strip()
        result["non_functional"].append(nfr_text[:500])  # Truncate for summary

    return result


# ---------------------------------------------------------------------------
# Main extraction entry point — works with any document type
# ---------------------------------------------------------------------------

def extract_from_any_document(text: str, source_label: str = "Document 1") -> dict:
    """
    Primary entry point. Accepts any document type and returns a normalised
    requirements brief suitable for RFP drafting.

    Detects the document type(s), runs the appropriate extractors, then
    merges the results into a common format.

    Returns a dict with:
      - source_label: the filename or label passed in
      - detected_type: from detect_document_type()
      - deliverables: list of str (confirmed requirements)
      - timeline: list of {milestone, date}
      - constraints: list of str
      - ambiguities: list of str — must be resolved before drafting
      - raw_extracts: dict of type-specific raw extraction results
      - recommendations: list of str — guidance for next steps

    Gotchas:
      - If multiple documents are provided, call this function once per document
        and merge with merge_extractions(). Do not concatenate document texts
        before calling — type detection will be confused.
      - If confidence is "low", surface this to the user and ask them to confirm
        the document type manually before proceeding.
      - Always show the user the ambiguities list before drafting — do not silently
        resolve ambiguities by making assumptions.
    """
    doc_type_result = detect_document_type(text)

    result = {
        "source_label": source_label,
        "detected_type": doc_type_result,
        "deliverables": [],
        "timeline": [],
        "constraints": [],
        "ambiguities": [],
        "raw_extracts": {},
        "recommendations": []
    }

    primary = doc_type_result["primary_type"]
    all_types = [primary] + doc_type_result.get("secondary_types", [])

    # Run the core SOW extractor on everything (catches deliverables, compliance, dates)
    sow_result = extract_requirements(text)
    result["ambiguities"].extend(sow_result.get("ambiguities", []))
    result["constraints"].extend(sow_result.get("constraints", []))
    result["raw_extracts"]["sow_pass"] = sow_result

    # Run type-specific extractors
    if "email" in all_types:
        email_result = _extract_from_email(text)
        result["raw_extracts"]["email"] = email_result
        result["ambiguities"].extend(email_result.get("ambiguities", []))
        result["ambiguities"].extend(email_result.get("attachments_referenced", []))
        result["ambiguities"].extend(email_result.get("budget_mentions", []))
        result["timeline"].extend([
            {"milestone": "Email reference", "date": d}
            for d in email_result.get("timeline_mentions", [])
        ])
        result["recommendations"].append(
            "Email thread detected: confirm requirements reflect the MOST RECENT message, "
            "not earlier drafts lower in the thread."
        )

    if "contract" in all_types:
        contract_result = _extract_from_contract(text)
        result["raw_extracts"]["contract"] = contract_result
        result["ambiguities"].extend(contract_result.get("ambiguities", []))
        if contract_result.get("commercial_terms_found"):
            result["recommendations"].append(
                "Previous contract commercial terms extracted — review and update for new RFP: "
                + str(list(contract_result["commercial_terms_found"].keys()))
            )
        result["recommendations"].append(
            "Source is an existing contract: extract scope only. Do NOT carry pricing "
            "forward into the new RFP."
        )

    if "meeting_notes" in all_types:
        meeting_result = _extract_from_meeting_notes(text)
        result["raw_extracts"]["meeting_notes"] = meeting_result
        result["ambiguities"].extend(meeting_result.get("unresolved_items", []))
        result["recommendations"].append(
            "Meeting notes detected: requirements may be expressed as problems or discussions. "
            "Confirm each extracted requirement reflects an actual decision, not a suggestion."
        )

    if "business_requirements" in all_types:
        brd_result = _extract_from_business_requirements(text)
        result["raw_extracts"]["business_requirements"] = brd_result
        result["ambiguities"].extend(brd_result.get("ambiguities", []))
        result["deliverables"].extend(brd_result.get("must_have", []))
        result["recommendations"].append(
            "BRD/requirements document detected: use Must Have items as mandatory RFP requirements. "
            "Should Have items become evaluation criteria. Could Have items are optional."
        )

    if primary in ("unknown", "presentation"):
        result["recommendations"].append(
            f"Document type detected as '{primary}' with {doc_type_result['confidence']} confidence. "
            "Ask the user to confirm the document type and what they want extracted from it "
            "before proceeding."
        )

    # De-duplicate ambiguities
    result["ambiguities"] = list(dict.fromkeys(result["ambiguities"]))

    return result


def merge_extractions(extractions: list) -> dict:
    """
    Merge extraction results from multiple documents into a single brief.

    Use when the user provides several source documents (e.g. an old contract +
    a set of emails + meeting notes from the kick-off call).

    Gotchas:
      - Conflicting requirements across documents must be surfaced to the user —
        never silently resolve a conflict by picking the most recent or most
        detailed version.
      - Requirements from a contract may be out of date if the procurement has
        evolved since the contract was signed. Email and meeting notes take
        precedence over contract text for describing current intent.
      - Timelines from different documents may contradict each other — always
        surface the most restrictive deadline and flag the conflict.
    """
    merged = {
        "sources": [e["source_label"] for e in extractions],
        "deliverables": [],
        "timeline": [],
        "constraints": [],
        "ambiguities": [],
        "recommendations": [],
        "conflicts": []
    }

    all_deliverables = []
    all_timelines = []
    all_constraints = []

    for e in extractions:
        all_deliverables.extend(e.get("deliverables", []))
        all_timelines.extend(e.get("timeline", []))
        all_constraints.extend(e.get("constraints", []))
        merged["ambiguities"].extend(e.get("ambiguities", []))
        merged["recommendations"].extend(e.get("recommendations", []))

    merged["deliverables"] = list(dict.fromkeys(all_deliverables))
    merged["timeline"] = all_timelines  # Don't de-dup — contradictions are useful
    merged["constraints"] = list(dict.fromkeys(all_constraints))

    # Flag obvious conflicts: contradictory timeline entries
    if len(all_timelines) > 1:
        merged["conflicts"].append(
            f"{len(all_timelines)} timeline entries found across documents — "
            "review for contradictions before setting RFP deadlines."
        )

    # Flag if contract + email both present (scope may have evolved)
    sources_with_types = [e.get("detected_type", {}).get("primary_type") for e in extractions]
    if "contract" in sources_with_types and "email" in sources_with_types:
        merged["conflicts"].append(
            "Old contract AND emails provided: email content likely reflects current intent. "
            "Treat contract scope as a baseline only — confirm with user which requirements "
            "have changed."
        )

    # De-duplicate ambiguities
    merged["ambiguities"] = list(dict.fromkeys(merged["ambiguities"]))

    return merged


def summarise_extraction(results: list) -> str:
    """
    Produce a plain-language summary of extraction results across multiple proposals.
    Pass the output of extract_proposal_data() for each supplier.

    Gotchas:
      - Do not interpret missing sections as disqualification — flag for query first.
      - Do not compare prices if pricing structures differ — normalize first.
    """
    lines = ["## Extraction Summary\n"]

    for r in results:
        lines.append(f"### {r['supplier']}")
        lines.append(f"- Pricing structure: {r['pricing_structure']}")
        lines.append(f"- Certifications claimed: {', '.join(r['certifications']) or 'None mentioned'}")
        lines.append(f"- Risks section present: {'Yes' if r['risks_stated'] else 'No'}")
        lines.append(f"- Case studies / references: {r['references_count']}")

        if r["missing_sections"]:
            lines.append(f"- **MISSING SECTIONS:** {', '.join(r['missing_sections'])} — query before scoring")
        if r["ambiguities"]:
            lines.append(f"- **AMBIGUITIES TO RESOLVE:**")
            for a in r["ambiguities"]:
                lines.append(f"  - {a}")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Original SOW extractor (kept for backwards compatibility)
# ---------------------------------------------------------------------------

def extract_requirements(text: str) -> dict:
    """
    Extract structured requirements from a SOW or requirements brief.
    Also used as a general-purpose first pass by extract_from_any_document().

    Returns a dict with keys:
      - deliverables: list of str
      - timeline: list of {milestone, date}
      - constraints: list of str (budget, geography, compliance)
      - ambiguities: list of str — items needing clarification before drafting

    Gotchas:
      - SOWs often use passive voice ("it is expected that...") — rephrase as
        active requirements when extracting ("The supplier shall...")
      - Dates in SOWs are often relative ("within 90 days") — flag these as
        ambiguities since the RFP needs absolute dates
      - "Nice to have" items are frequently mixed with hard requirements —
        flag anything hedged with "ideally", "preferably", "if possible" as optional
      - SOWs from legal/finance teams often include obligations on BOTH parties —
        extract only supplier obligations, not buyer obligations
    """
    result = {
        "deliverables": [],
        "timeline": [],
        "constraints": [],
        "ambiguities": [],
        "raw_word_count": len(text.split())
    }

    # Flag relative dates as ambiguities
    relative_date_patterns = [
        r'\b\d+\s+(?:days?|weeks?|months?)\b',
        r'\bwithin\s+\d+\b',
        r'\bby\s+(?:end of|Q[1-4])\b',
        r'\bASAP\b', r'\bsoon\b', r'\bimmediately\b'
    ]
    for pattern in relative_date_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            result["ambiguities"].append(
                f"Relative date found: '{m}' — needs absolute date for RFP"
            )

    # Flag hedged requirements as optional
    hedge_patterns = [r'\bideally\b', r'\bpreferably\b', r'\bif possible\b',
                      r'\bwould be nice\b', r'\bnice to have\b', r'\bcould\b']
    for pattern in hedge_patterns:
        matches = re.findall(r'.{0,40}' + pattern + r'.{0,40}', text, re.IGNORECASE)
        for m in matches:
            result["ambiguities"].append(
                f"Hedged requirement (may be optional): '...{m.strip()}...'"
            )

    # Extract budget mentions
    budget_patterns = [r'\$[\d,]+(?:k|m|K|M)?', r'£[\d,]+(?:k|m|K|M)?',
                       r'budget of', r'not to exceed', r'NTE']
    for pattern in budget_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            result["constraints"].append(
                "Budget figure detected in source document — confirm disclosure decision before drafting RFP"
            )
            break

    # Flag compliance/certification mentions
    cert_patterns = [r'ISO\s*\d+', r'SOC\s*[12]', r'GDPR', r'HIPAA',
                     r'Cyber Essentials', r'PCI[- ]DSS', r'certified', r'accredited']
    for pattern in cert_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in set(matches):
            result["constraints"].append(
                f"Compliance/certification mentioned: '{m}' — confirm if mandatory (disqualifier) or preferred"
            )

    return result


def extract_proposal_data(text: str, supplier_name: str = "Unknown") -> dict:
    """
    Extract structured data from a supplier proposal for scoring.

    Returns a dict with keys:
      - supplier: str
      - proposed_price: float or None
      - pricing_structure: str (fixed / T&M / subscription / milestone / not stated)
      - certifications: list of str
      - delivery_timeline: str or None
      - references_count: int
      - risks_stated: bool
      - missing_sections: list of str

    Gotchas:
      - Proposals often include multiple pricing scenarios — flag and ask user which to use.
      - Some suppliers embed pricing in narrative text — verify extracted price with user.
      - "We are ISO 27001 certified" ≠ a current certificate — flag for verification.
      - Scanned PDF proposals will return garbled text — request a text-based version.
    """
    result = {
        "supplier": supplier_name,
        "proposed_price": None,
        "pricing_structure": "not stated",
        "certifications": [],
        "delivery_timeline": None,
        "references_count": 0,
        "risks_stated": False,
        "missing_sections": [],
        "ambiguities": []
    }

    if re.search(r'per\s+(?:hour|day|month|year|user|seat)', text, re.IGNORECASE):
        result["pricing_structure"] = "T&M or subscription"
    elif re.search(r'fixed\s+(?:price|fee|cost)', text, re.IGNORECASE):
        result["pricing_structure"] = "fixed price"
    elif re.search(r'milestone', text, re.IGNORECASE):
        result["pricing_structure"] = "milestone-based"

    if re.search(r'option\s+[AB12]|scenario\s+[AB12]|alternative\s+approach', text, re.IGNORECASE):
        result["ambiguities"].append(
            "Multiple pricing options detected — user must select which to use for scoring"
        )

    cert_patterns = [r'ISO\s*\d+[\w:\-]*', r'SOC\s*[12](?:\s+Type\s+[12])?',
                     r'Cyber Essentials(?:\s+Plus)?', r'GDPR\s+compliant',
                     r'PCI[- ]DSS', r'HIPAA']
    for pattern in cert_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        result["certifications"].extend([m.strip() for m in matches])
    result["certifications"] = list(set(result["certifications"]))

    if result["certifications"]:
        result["ambiguities"].append(
            f"Certifications claimed: {result['certifications']} — request copies before finalising score"
        )

    if re.search(r'risk[s]?(?:\s+and\s+assumptions?)?', text, re.IGNORECASE):
        result["risks_stated"] = True

    ref_count = len(re.findall(
        r'(?:case study|client reference|example engagement|previous project)',
        text, re.IGNORECASE
    ))
    result["references_count"] = ref_count

    required_sections = {
        "company overview": r'company\s+overview|about\s+us|our\s+organisation',
        "technical approach": r'technical\s+approach|methodology|our\s+approach',
        "pricing": r'price|cost|fee|pricing|quotation',
        "references": r'reference|case\s+study|client\s+example',
        "risk": r'risk|assumption'
    }
    for section_name, pattern in required_sections.items():
        if not re.search(pattern, text, re.IGNORECASE):
            result["missing_sections"].append(section_name)

    return result


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # CLI usage: python extract_sow.py file1.txt [file2.txt ...]
    if len(sys.argv) < 2:
        print("Usage: python extract_sow.py <filepath> [filepath2 ...]")
        sys.exit(1)

    all_extractions = []
    for filepath_str in sys.argv[1:]:
        filepath = Path(filepath_str)
        if not filepath.exists():
            print(f"File not found: {filepath}")
            continue
        text = filepath.read_text(encoding="utf-8", errors="ignore")
        extraction = extract_from_any_document(text, source_label=filepath.name)
        all_extractions.append(extraction)
        print(f"\n--- {filepath.name} ---")
        print(f"Detected type: {extraction['detected_type']['primary_type']} "
              f"(confidence: {extraction['detected_type']['confidence']})")
        if extraction["ambiguities"]:
            print(f"Ambiguities: {len(extraction['ambiguities'])}")
        if extraction["recommendations"]:
            for r in extraction["recommendations"]:
                print(f"  ⚠ {r}")

    if len(all_extractions) > 1:
        print("\n--- MERGED BRIEF ---")
        merged = merge_extractions(all_extractions)
        print(json.dumps(merged, indent=2))
    elif len(all_extractions) == 1:
        print(json.dumps(all_extractions[0], indent=2))

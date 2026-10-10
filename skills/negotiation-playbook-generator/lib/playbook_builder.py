"""
playbook_builder.py — Negotiation Playbook Constructor & Validator
Part of the Molecule One Negotiation Playbook Generator skill.

Constructs, validates, and persists negotiation playbooks including:
BATNA analysis, lever identification, concession sequencing, authority
limits, and counter-proposal integration.

Usage:
    from lib.playbook_builder import NegotiationLever, ConcessionStep, Playbook
    from lib.playbook_builder import build_playbook, validate_playbook, save_playbook

Gotchas:
    - A playbook without a BATNA is incomplete and must not be used.
      The validator will reject any playbook where batna_summary is empty.
    - Concession steps must be sequenced BEFORE the negotiation. The
      sequence is a numbered list, not a set. Order matters — early
      concessions should be nice-to-haves, not must-wins.
    - Authority limits define the boundary beyond which the negotiator
      must pause and escalate. A playbook without authority limits
      creates uncontrolled negotiation risk.
    - Walk-away price is NOT the same as target price. Target is what
      you aim for; walk-away is where you stop negotiating. These must
      be different values — if they're the same, there's no negotiation
      range and the playbook is unrealistic.
"""

import json
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


@dataclass
class BATNA:
    """
    Best Alternative To a Negotiated Agreement.

    Gotcha: BATNA cost must include switching costs, not just the
    alternative's headline price. A BATNA at $510K with $80K switching
    cost is really $590K — which changes the negotiation calculus.
    """
    summary: str                    # One-line description
    alternative_supplier: str       # Who / what is the alternative
    alternative_cost: Optional[float]  # Total cost including switching
    switching_cost: Optional[float]
    readiness: str                  # "ready" / "6 months" / "not started"
    strength: str                   # "Strong" / "Moderate" / "Weak"
    notes: str = ""


@dataclass
class NegotiationLever:
    """
    A single negotiation lever — a dimension that can be moved to create
    or capture value.

    Gotcha: Every lever must have a fallback position. A lever without
    a fallback is just a demand — and demands get rejected. The fallback
    defines what you'll accept if the ideal position is refused.
    """
    name: str
    category: str                   # Price / Non-Price / Relationship
    our_position: str               # What we're asking for
    their_likely_resistance: str    # Why they'll push back
    fallback_position: str          # Minimum we'll accept
    trade_value: str                # What we offer in return
    priority: str                   # Must-win / Must-have / Important / Nice-to-have
    notes: str = ""


@dataclass
class ConcessionStep:
    """
    A single step in the concession sequence.

    Gotcha: concession_label must be phrased as an explicit trade:
    "We'll move on [X] if you move on [Y]". Never concede without
    getting something in return — unilateral concessions signal weakness.
    """
    sequence_number: int
    phase: str                      # "Opening" / "Trading" / "Closing"
    lever_name: str                 # Which lever is being moved
    concession_label: str           # What we're offering
    in_exchange_for: str            # What we expect in return
    is_conditional: bool = True     # True = only concede if they reciprocate


@dataclass
class AuthorityLimit:
    """
    A decision boundary for the negotiator.

    Gotcha: If target == walk_away, the negotiation range is zero
    and the playbook is unrealistic. Validator catches this.
    """
    dimension: str
    target: str
    walk_away: str
    authority_role: str             # Who can approve up to walk-away
    escalation_role: str            # Who to escalate to beyond walk-away
    notes: str = ""


@dataclass
class Playbook:
    """A complete negotiation playbook."""
    supplier_name: str
    category: str
    deal_type: str                  # new / renewal / renegotiation
    org_name: str
    created_date: str
    negotiation_date: str
    negotiator_roles: list[str]
    batna: BATNA
    supplier_ask: Optional[float]
    internal_target: Optional[float]
    levers: list[NegotiationLever]
    concession_sequence: list[ConcessionStep]
    authority_limits: list[AuthorityLimit]
    counter_proposals: list[dict] = field(default_factory=list)  # from counter_proposal_drafter
    red_lines: list[str] = field(default_factory=list)
    if_they_say: list[dict] = field(default_factory=list)  # [{they_say, you_say}]
    notes: str = ""
    version: str = "1.0"


def build_playbook(
    supplier_name: str,
    category: str,
    deal_type: str,
    org_name: str,
    created_date: str,
    negotiation_date: str,
    negotiator_roles: list[str],
    batna: BATNA,
    supplier_ask: Optional[float],
    internal_target: Optional[float],
    levers: list[NegotiationLever],
    concession_sequence: list[ConcessionStep],
    authority_limits: list[AuthorityLimit],
    counter_proposals: Optional[list[dict]] = None,
    red_lines: Optional[list[str]] = None,
    if_they_say: Optional[list[dict]] = None,
    notes: str = "",
) -> Playbook:
    """
    Build and validate a Playbook.

    Raises ValueError if:
      - BATNA is missing or empty
      - Fewer than 3 levers (playbook is too thin)
      - No concession steps defined
      - No authority limits defined
      - Target == walk-away on any dimension

    Returns a validated Playbook.

    Gotchas:
      - If BATNA strength is "Weak", automatically add a warning to notes:
        the negotiation strategy must account for limited walk-away power.
      - If supplier_ask == internal_target, flag: either the target is
        wrong or this isn't a negotiation.
    """
    playbook = Playbook(
        supplier_name=supplier_name,
        category=category,
        deal_type=deal_type,
        org_name=org_name,
        created_date=created_date,
        negotiation_date=negotiation_date,
        negotiator_roles=negotiator_roles,
        batna=batna,
        supplier_ask=supplier_ask,
        internal_target=internal_target,
        levers=levers,
        concession_sequence=concession_sequence,
        authority_limits=authority_limits,
        counter_proposals=counter_proposals or [],
        red_lines=red_lines or [],
        if_they_say=if_they_say or [],
        notes=notes,
    )
    validate_playbook(playbook)
    return playbook


def validate_playbook(playbook: Playbook) -> list[str]:
    """
    Validate a playbook. Returns a list of warning strings.
    Raises ValueError on fatal errors.

    Gotchas:
      - Concession steps must be in sequence_number order with no gaps.
      - Every lever referenced in a concession step must exist in the levers list.
      - Red lines should not appear in the concession sequence — if something
        is a red line, it should never be conceded.
    """
    warnings = []
    errors = []

    # BATNA check
    if not playbook.batna or not playbook.batna.summary:
        errors.append(
            "BATNA is missing. A playbook without a defined BATNA is incomplete. "
            "Define the best alternative before proceeding."
        )

    # Levers check
    if len(playbook.levers) < 3:
        errors.append(
            f"Only {len(playbook.levers)} levers identified. "
            "A playbook with fewer than 3 levers has insufficient negotiation flexibility."
        )

    if len(playbook.levers) > 12:
        warnings.append(
            f"{len(playbook.levers)} levers identified. "
            "More than 8–10 levers can overwhelm the negotiator. "
            "Consider consolidating or prioritising."
        )

    # Concession sequence check
    if not playbook.concession_sequence:
        errors.append("No concession sequence defined. The negotiator has no plan for what to trade and when.")

    # Authority limits check
    if not playbook.authority_limits:
        errors.append("No authority limits defined. The negotiator has no decision boundaries.")

    # Target vs walk-away check
    for al in playbook.authority_limits:
        if al.target == al.walk_away:
            warnings.append(
                f"Dimension '{al.dimension}': target ({al.target}) equals walk-away ({al.walk_away}). "
                "This leaves zero negotiation range. Review and adjust."
            )

    # Supplier ask vs target check
    if playbook.supplier_ask is not None and playbook.internal_target is not None:
        if playbook.supplier_ask == playbook.internal_target:
            warnings.append(
                "Supplier's ask equals your internal target. "
                "This is unusual — either the target is too generous or the supplier has matched it. "
                "Consider anchoring lower."
            )

    # BATNA weakness warning
    if playbook.batna and playbook.batna.strength == "Weak":
        warnings.append(
            "BATNA is Weak — the supplier likely knows you have limited alternatives. "
            "Strategy should focus on non-price levers, incremental wins, and building "
            "alternatives for the next negotiation cycle."
        )

    # Fallback check
    levers_without_fallback = [l.name for l in playbook.levers if not l.fallback_position]
    if levers_without_fallback:
        warnings.append(
            f"Levers without fallback positions: {', '.join(levers_without_fallback)}. "
            "A lever without a fallback is just a demand."
        )

    # Red line in concession check
    conceded_levers = {cs.lever_name for cs in playbook.concession_sequence}
    for rl in playbook.red_lines:
        if rl in conceded_levers:
            errors.append(
                f"Red line '{rl}' appears in the concession sequence. "
                "Red lines must never be conceded. Remove from the sequence."
            )

    # Lever reference check
    lever_names = {l.name for l in playbook.levers}
    for cs in playbook.concession_sequence:
        if cs.lever_name not in lever_names:
            warnings.append(
                f"Concession step {cs.sequence_number} references lever '{cs.lever_name}' "
                "which is not in the levers list."
            )

    if errors:
        raise ValueError("Playbook validation failed:\n" + "\n".join(f"  - {e}" for e in errors))

    for w in warnings:
        print(f"[playbook_builder] WARNING: {w}", file=sys.stderr)

    return warnings


def save_playbook(playbook: Playbook, output_dir: str) -> str:
    """
    Save a playbook to a versioned JSON file.

    File naming: [SUPPLIER]-[DATE].json (lowercase, spaces → hyphens)
    Returns the saved file path.

    Gotchas:
      - If a playbook file already exists for this supplier/date, append
        a version suffix to avoid overwriting.
      - The output_dir is typically ${CLAUDE_PLUGIN_DATA}/playbooks/
    """
    safe_supplier = playbook.supplier_name.lower().replace(" ", "-")
    filename = f"{safe_supplier}-{playbook.created_date}.json"
    path = Path(output_dir) / filename

    if path.exists():
        from datetime import datetime
        ts = datetime.now().strftime("%H%M%S")
        filename = f"{safe_supplier}-{playbook.created_date}-{ts}.json"
        path = Path(output_dir) / filename
        print(f"[playbook_builder] File existed — saved as {filename}", file=sys.stderr)

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    data = _serialize_playbook(playbook)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"[playbook_builder] Saved to {path}", file=sys.stderr)
    return str(path)


def load_playbook(filepath: str) -> dict:
    """Load a playbook from JSON. Returns raw dict."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Playbook not found: {filepath}")
    return json.loads(path.read_text(encoding="utf-8"))


def render_playbook_summary(playbook: Playbook) -> str:
    """Render a human-readable playbook summary."""
    batna_icon = {"Strong": "💪", "Moderate": "⚖️", "Weak": "⚠️"}.get(playbook.batna.strength, "")

    lines = [
        f"## Negotiation Playbook — {playbook.supplier_name}",
        f"Category: {playbook.category} | Deal: {playbook.deal_type} | Date: {playbook.negotiation_date}",
        f"Org: {playbook.org_name} | Prepared: {playbook.created_date}",
        "",
    ]

    if playbook.supplier_ask and playbook.internal_target:
        gap = playbook.supplier_ask - playbook.internal_target
        gap_pct = (gap / playbook.internal_target * 100) if playbook.internal_target else 0
        lines += [
            f"Their ask:   ${playbook.supplier_ask:,.0f}",
            f"Our target:  ${playbook.internal_target:,.0f}",
            f"Gap:         ${gap:,.0f} ({gap_pct:.1f}%)",
            "",
        ]

    lines += [
        f"BATNA: {batna_icon} {playbook.batna.strength} — {playbook.batna.summary}",
        "",
        f"{'#':<3} {'Lever':<25} {'Priority':<12} {'Our Position':<25} {'Fallback'}",
        "-" * 90,
    ]

    for i, l in enumerate(playbook.levers, 1):
        lines.append(
            f"{i:<3} {l.name:<25} {l.priority:<12} {l.our_position:<25} {l.fallback_position}"
        )

    lines += ["", "Concession Sequence:"]
    for cs in playbook.concession_sequence:
        lines.append(
            f"  {cs.sequence_number}. [{cs.phase}] {cs.concession_label} → in exchange for: {cs.in_exchange_for}"
        )

    if playbook.red_lines:
        lines += ["", "Red Lines (do not concede):"]
        for rl in playbook.red_lines:
            lines.append(f"  🔴 {rl}")

    if playbook.authority_limits:
        lines += ["", f"{'Dimension':<20} {'Target':<15} {'Walk-away':<15} {'Authority':<20} {'Escalate to'}"]
        lines.append("-" * 80)
        for al in playbook.authority_limits:
            lines.append(
                f"{al.dimension:<20} {al.target:<15} {al.walk_away:<15} {al.authority_role:<20} {al.escalation_role}"
            )

    return "\n".join(lines)


def _serialize_playbook(playbook: Playbook) -> dict:
    """Serialise a Playbook to a plain dict for JSON storage."""
    return {
        "supplier_name": playbook.supplier_name,
        "category": playbook.category,
        "deal_type": playbook.deal_type,
        "org_name": playbook.org_name,
        "created_date": playbook.created_date,
        "negotiation_date": playbook.negotiation_date,
        "negotiator_roles": playbook.negotiator_roles,
        "version": playbook.version,
        "supplier_ask": playbook.supplier_ask,
        "internal_target": playbook.internal_target,
        "notes": playbook.notes,
        "batna": asdict(playbook.batna),
        "levers": [asdict(l) for l in playbook.levers],
        "concession_sequence": [asdict(cs) for cs in playbook.concession_sequence],
        "authority_limits": [asdict(al) for al in playbook.authority_limits],
        "counter_proposals": playbook.counter_proposals,
        "red_lines": playbook.red_lines,
        "if_they_say": playbook.if_they_say,
    }


if __name__ == "__main__":
    # Demo playbook
    demo = build_playbook(
        supplier_name="Salesforce",
        category="IT — CRM",
        deal_type="renewal",
        org_name="Acme Corp",
        created_date="2026-03-21",
        negotiation_date="2026-03-27",
        negotiator_roles=["Category Manager — IT", "IT Director"],
        batna=BATNA(
            summary="HubSpot at $510K — evaluated but not contracted",
            alternative_supplier="HubSpot",
            alternative_cost=590000,
            switching_cost=80000,
            readiness="6 months",
            strength="Moderate",
        ),
        supplier_ask=620000,
        internal_target=480000,
        levers=[
            NegotiationLever("Total price", "Price", "$480K", "Below their cost floor", "$520K", "3-year commitment", "Must-win"),
            NegotiationLever("Payment terms", "Price", "Net 60", "Cash flow impact on them", "Net 45", "None — this is standard", "Must-win"),
            NegotiationLever("Auto-renewal removal", "Non-Price", "Explicit opt-in", "Reduces their revenue certainty", "180-day opt-out", "Contract length", "Must-have"),
            NegotiationLever("SLA penalties", "Non-Price", "5% per miss", "Adds financial risk", "3% per miss, 15% cap", "Higher volume commitment", "Must-have"),
            NegotiationLever("Data portability", "Non-Price", "Full export at no cost", "Reduces lock-in", "Export in standard format", "Reference/case study", "Important"),
            NegotiationLever("Contract length", "Price", "2+1 year option", "Prefer 3-year lock-in", "3 years with annual exit clause", "Volume guarantee", "Important"),
        ],
        concession_sequence=[
            ConcessionStep(1, "Opening", "Contract length", "We'll consider a 3-year term", "if you move on total price to $500K"),
            ConcessionStep(2, "Trading", "Data portability", "We'll accept standard format export", "if you add SLA penalties framework"),
            ConcessionStep(3, "Trading", "SLA penalties", "We'll accept 3% cap at 15%", "if you remove auto-renewal"),
            ConcessionStep(4, "Closing", "Total price", "We'll accept $510K", "if the full package (terms, SLAs, portability) is agreed"),
        ],
        authority_limits=[
            AuthorityLimit("Total price", "$480K", "$520K", "Category Manager", "CPO"),
            AuthorityLimit("Payment terms", "Net 60", "Net 45", "Category Manager", "Finance Director"),
        ],
        red_lines=[
            "Payment terms shorter than Net 30",
            "Auto-renewal with <90-day opt-out",
            "No termination for convenience",
        ],
        if_they_say=[
            {"they_say": "This is our best and final price.", "you_say": "We appreciate the transparency, but we have a competitive alternative at $510K. Let's find a way to close the gap."},
            {"they_say": "Everyone pays this rate.", "you_say": "Our benchmarks show differently. We've seen rates 15-20% below this for similar scope."},
            {"they_say": "We need a decision by Friday.", "you_say": "Artificial deadlines don't help either side. Let's focus on getting the terms right."},
        ],
    )
    print(render_playbook_summary(demo))

# Negotiation Playbook Generator — v1.0
**Part of the Molecule One Claude Plugin Suite**
Stage 5 of 14 in the Source-to-Pay (S2P) automation workflow.

---

## What This Skill Does

Builds structured negotiation playbooks with BATNA analysis, lever identification, concession sequencing, authority limits, and pre-drafted counter-proposal language. Takes a supplier's proposal and internal targets, identifies gaps, flags commercial risks, and produces a ready-to-use playbook and one-page briefing card.

**Input:** Supplier proposals (PDF/DOCX/pasted), internal targets, market benchmarks, scorecard data from prior stages.
**Output:** Negotiation playbook (.docx), pre-negotiation briefing card (.docx), gap analysis, counter-proposal package, and TCO computation.

---

## Modes

| Mode | Trigger | Output |
|---|---|---|
| Playbook Build | "build a negotiation playbook", "negotiate with [supplier]" | Full playbook with BATNA, levers, concessions, counters |
| Proposal Analysis | "analyse this proposal", "what's wrong with this offer" | Position extraction, gap analysis, risk flags, TCO |
| Counter-Proposal | "draft counter-proposal for [clause]", "counter this language" | Three-tier counter-proposals with verbal rationale |
| Briefing Card | "one-pager for the negotiation", "briefing card" | One-page pre-negotiation summary |
| Full Cycle | Supplier + deal context without specifying mode | All four outputs in sequence |

---

## S2P Chain Position

```
[4] supplier-scorecard-engine → [5] negotiation-playbook-generator ← YOU ARE HERE
                                            ↓
                                  [6] contract-drafter-reviewer
```

Negotiation playbooks consume outputs from `spend-analyzer` (market benchmarks), `category-strategy-builder` (Kraljic quadrant, market intelligence), and `supplier-scorecard-engine` (supplier performance data — Red commercial scores trigger renegotiation). Agreed terms from the playbook feed Stage 6 (`contract-drafter-reviewer`) for contract formalisation.

---

## File Structure

```
negotiation-playbook-generator/
├── SKILL.md
├── config.json
├── gotchas.md
├── README.md
├── modes/
│   ├── playbook-build-mode.md
│   ├── proposal-analysis-mode.md
│   ├── counter-proposal-mode.md
│   └── briefing-card-mode.md
├── lib/
│   ├── playbook_builder.py        # Playbook construction, validation, persistence
│   ├── gap_analyzer.py            # Position gap computation, risk flagging, TCO
│   └── counter_proposal_drafter.py # Three-tier counter-proposal generation
├── templates/
│   ├── playbook-template.md       # Full negotiation playbook
│   ├── briefing-card-template.md  # One-page pre-negotiation briefing
│   ├── gap-analysis-template.md   # Position gap analysis report
│   └── counter-proposals-template.md # Counter-proposal package
└── assets/
    └── branding.md
```

---

## BATNA Strength Classification

| Strength | Definition | Strategy Impact |
|---|---|---|
| 💪 Strong | Viable alternative ready, tested, and priced competitively | Negotiate aggressively — walk-away is credible |
| ⚖️ Moderate | Alternative exists but has switching cost or capability gaps | Negotiate firmly; trade non-price levers |
| ⚠️ Weak | No realistic alternative — incumbent is sole source | Focus on incremental wins; protect against escalation |

---

## Version History

| Version | Date | Changes |
|---|---|---|
| 1.0 | 21 Mar 2026 | Initial release |

---

_Confidential — Molecule One Procurement Plugin Suite | moleculeone.ai_

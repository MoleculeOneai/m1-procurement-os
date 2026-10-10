# Mode: Criteria Setup

## Goal
Design a complete, agreed scoring framework before an evaluation session — either by extracting sections from an existing RFP document, or by working with the user to define criteria from scratch. The output is a saved criteria file ready to use in `full-evaluation-mode.md`.

Use this mode when:
- The user wants to review or adjust criteria before running an evaluation
- No RFP document is available and criteria need to be built from scratch
- An existing criteria set needs updating for a new evaluation round

---

## Step 1 — Determine the criteria source

Ask:
> "Are you building criteria from an existing RFP document, or defining them from scratch?
> - **From RFP (recommended):** I'll extract the scoreable sections from your RFP document and propose weights — you confirm or adjust
> - **From scratch:** We define sections and weights together based on what matters for this category"

---

## Step 2 — Extract or define sections

**If from RFP:**

Use `lib/criteria_extractor.py` with `mode="from_rfp"`. Parse the document and identify scoreable sections. Exclude administrative sections (submission instructions, T&Cs, company boilerplate).

Present the proposed section list with a rationale for each inclusion/exclusion:
> "I've identified [N] scoreable sections from your RFP. I've excluded [X] sections as they are administrative (submission instructions, T&Cs) rather than evaluable content. Here's my proposed list: [table]"

**If from scratch:**

Ask the user about the category, then propose a standard section set from the library below. Always tailor to the category — do not use a generic template unchanged.

### Standard Section Library

**Commercial / Pricing**
- Total Cost of Ownership (TCO) — all-in price over contract term, normalised to comparable basis
- Pricing structure and transparency — clarity of pricing model, any variable or pass-through costs
- Payment terms — alignment with buyer's preferred terms
- Volume / early payment discounts — any commercial incentives offered

**Technical / Solution**
- Technical approach — methodology, architecture, or service delivery model
- Fit to specification — how closely the solution matches the stated requirements
- Implementation / transition plan — realism of timeline, milestones, and resource plan
- Innovation — any solutions or approaches beyond minimum specification

**Experience & References**
- Relevant experience — comparable contracts, industries, scale
- Case studies / references — verifiable evidence of delivery
- Team qualifications — relevant certifications, experience of key personnel

**Delivery & Service**
- Delivery timeline — proposed schedule vs. required timeline
- SLA commitments — proposed service levels and remedies
- Capacity and scalability — ability to scale up/down as required

**Risk & Compliance**
- Mandatory certifications — ISO, regulatory, sector-specific
- Financial stability — evidence of financial health (accounts, credit rating, Dun & Bradstreet)
- Business continuity — tested continuity plans
- Data security / cyber — data handling and information security credentials
- ESG / sustainability — any contractual ESG commitments met

---

## Step 3 — Assign weights

Weights must sum to 100%. Propose weights based on the category and the buyer's stated primary objective:

| Primary objective | Suggested emphasis |
|---|---|
| Cost reduction | Commercial 40–50%, Technical 25–30%, Delivery 15%, Risk 10% |
| Quality / outcome focus | Technical 35–40%, Commercial 25%, Delivery 20%, Risk 15% |
| Risk reduction | Risk 30–35%, Technical 25%, Commercial 25%, Delivery 15% |
| Speed / urgency | Delivery 35%, Technical 25%, Commercial 25%, Risk 15% |

**Hard rule:** No single section should carry more than 50% of total weight. If the user proposes this, challenge it: "A scorecard dominated by one section is fragile — a supplier could win or lose entirely on one dimension regardless of overall suitability."

Present proposed weights and ask for confirmation:
> "Here are the proposed weights. Do they reflect your priorities for this evaluation? Any you'd shift?"

---

## Step 4 — Define scoring anchors

For each section, define what a score of 10, 5, and 1 looks like. **This is critical** — without anchors, scores are subjective and indefensible.

Format for each section:

| Score | Definition |
|---|---|
| **10 — Outstanding** | [Specific, measurable description] |
| **5 — Acceptable** | [Specific, measurable description] |
| **1 — Inadequate** | [Specific, measurable description] |

Example for TCO section:
| Score | Definition |
|---|---|
| 10 | Lowest TCO in the panel AND full price transparency with no hidden costs; pricing structure fully understood |
| 5 | TCO within 15% of the lowest; pricing model clear but some variable elements require clarification |
| 1 | Highest TCO in the panel OR significant undisclosed costs OR pricing structure unclear and unverifiable |

If a section is qualitative (e.g. Technical Approach), define behavioural anchors:
| Score | Definition |
|---|---|
| 10 | Detailed, tailored methodology addressing every specification point; realistic and well-evidenced delivery plan |
| 5 | Methodology covers most requirements; some gaps; plan is credible but lacks specifics |
| 1 | Generic response not tailored to the specification; methodology not demonstrated; delivery plan missing |

---

## Step 5 — Define mandatory pass/fail requirements

Separate from scored sections, define any criteria that are binary pass/fail — a supplier failing any of these is disqualified before scoring.

Examples: minimum ISO certification, geographic coverage, minimum company revenue or financial health, active insurance certificates, regulatory authorisations.

Record these clearly:
> "Any supplier failing the following requirements will be disqualified and excluded from scoring: [list]"

---

## Step 6 — Save the criteria file

Use `lib/criteria_extractor.py` to save the agreed criteria to:
`${CLAUDE_PLUGIN_DATA}/criteria/[CATEGORY]-criteria-v[N.N].json`

Naming: `[CATEGORY]-criteria-v[N.N].json`
Increment the version whenever sections, weights, or anchors are changed.

Tell the user:
> "Criteria saved as [CATEGORY]-criteria-v[N.N]. Ready to start the evaluation — shall I proceed to reading the supplier responses now?"

If yes, route to `modes/full-evaluation-mode.md` at Step 2.

---

## What Good Looks Like

- Every scoreable section maps to a specific part of the RFP (if available) — no invented criteria
- Weights reflect actual procurement priorities, not equal-split defaults
- Every section has explicit scoring anchors — no section scored on gut feel
- Mandatory pass/fail requirements are defined separately from scored sections
- The criteria file is saved and versioned before evaluation begins

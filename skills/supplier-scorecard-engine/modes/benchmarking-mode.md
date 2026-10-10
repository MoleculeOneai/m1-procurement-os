# Mode: Supplier Benchmarking

## Goal
Compare two or more suppliers using the same scorecard framework, identifying relative strengths, weaknesses, and ranking. Used for: competitive supplier reviews, panel rationalisation, preferred supplier decisions, and renewal vs. re-tender decisions.

---

## Step 1 — Confirm the comparison scope

Before running a benchmark, confirm:
- [ ] **Suppliers to compare** — minimum 2, maximum practical limit ~6 (more than 6 in a comparison table becomes unwieldy)
- [ ] **Time period** — all suppliers must be scored on the same period; cross-period comparisons are invalid
- [ ] **Scorecard version** — all suppliers must have been scored against the same scorecard version; flag any mismatches
- [ ] **Purpose of the comparison** — is this for: panel rationalisation, preferred supplier selection, renewal decision, or general performance visibility?

If any supplier in the comparison set doesn't have a current score, ask: "Shall I run a scoring session for [supplier] now before we compare?"

---

## Step 2 — Validate comparability

Before building the comparison matrix, run a comparability check:

| Check | Pass / Fail | Issue |
|---|---|---|
| All suppliers scored in same period | | |
| All suppliers scored on same scorecard version | | |
| No supplier has >3 N/A dimensions | | |
| All suppliers scored by same reviewer (or same reviewer pool) | | |

If any check fails, flag it prominently:
> "⚠ Comparability warning: [SUPPLIER] was scored on scorecard v1.1, while the others used v1.0. The [DIMENSION] criterion was added in v1.1 — this means [SUPPLIER]'s score includes data the others don't. Recommend either: (a) re-score all on v1.1, or (b) exclude the new criterion from this comparison."

---

## Step 3 — Build the comparison matrix

Use `lib/score_calculator.py` to compute the side-by-side comparison.

Format:

| Dimension | Weight | [SUPPLIER A] | [SUPPLIER B] | [SUPPLIER C] | Best in class |
|---|---|---|---|---|---|
| [Dimension name] | [W]% | [score/5] | [score/5] | [score/5] | [supplier name] |
| **Weighted total** | **100%** | **[/100]** | **[/100]** | **[/100]** | |
| **RAG** | | 🟢/🟡/🔴 | 🟢/🟡/🔴 | 🟢/🟡/🔴 | |
| **Rank** | | [#] | [#] | [#] | |

Highlight the best-in-class score for each dimension (bold or noted separately).

---

## Step 4 — Identify strength/weakness profiles

For each supplier, generate a one-paragraph profile:
> "[SUPPLIER A] ranks [1st/2nd/3rd] overall with a score of [N]. Their strongest dimensions are [X, Y] where they lead the panel. They are weakest on [Z] where they trail by [delta] vs. the panel leader. [One sentence on implication for strategy.]"

---

## Step 5 — Produce the panel summary

Generate a summary statement for the full comparison:

> **Panel overview ([N] suppliers | [PERIOD] | [CATEGORY])**
>
> - Panel leader: [SUPPLIER] — [score]/100 — 🟢 Green
> - Panel average: [score]/100
> - Most consistent performer (fewest dimension score variance): [SUPPLIER]
> - Highest-risk supplier (lowest overall or most Red dimensions): [SUPPLIER]
>
> **Dimensions where no supplier scored well (all ≤3):** [list — these signal a systemic market or specification problem, not just supplier performance]
> **Dimensions where all suppliers scored well (all ≥4):** [list]

---

## Step 6 — Link to strategy decisions

Based on the comparison purpose confirmed in Step 1, generate a recommendation:

**Panel rationalisation:**
> "Based on the scorecard results, [SUPPLIER A] and [SUPPLIER B] are performing above the panel average. [SUPPLIER C] is the weakest performer and is a candidate for removal from the preferred panel. Recommended action: issue a 3-month performance notice to [SUPPLIER C] and confirm intent to remove from panel at next contract break."

**Preferred supplier selection:**
> "[SUPPLIER A] has the strongest overall performance and leads on the highest-weighted dimensions ([X] and [Y]). Recommend awarding preferred supplier status with [%] volume allocation. [SUPPLIER B] should be retained as a secondary source given supply risk."

**Renewal vs. re-tender:**
> "[SUPPLIER A]'s score of [N] with a [trend arrow] [improving/declining] trend [supports direct renewal / suggests a competitive process is warranted]. [One-sentence rationale.]"

Always present the recommendation as a recommendation — the user must make the final call.

---

## Step 7 — Generate the benchmark report

Populate `templates/supplier-comparison.md`. Generate a `.docx` file using the `docx` skill.

Document naming:
```
[ORG_NAME]-Supplier-Benchmark-[CATEGORY]-[YYYY-QN].docx
```

---

## Step 8 — Log

Append to `${CLAUDE_PLUGIN_DATA}/scorecard-history.log`:
```
DATE: [date]
EVENT: Benchmark completed
CATEGORY: [category]
PERIOD: [period]
SUPPLIERS_COMPARED: [n] — [names]
PANEL_LEADER: [supplier name] — [score]
PANEL_AVERAGE: [score]
RECOMMENDATION: [one-line]
```

---

## What Good Looks Like

- All suppliers are scored on the same version of the same scorecard — any deviation is flagged
- The comparison matrix shows dimension-level scores, not just totals
- Dimensions where the whole panel scores poorly are flagged as a systemic issue
- The recommendation is specific and linked to the purpose of the comparison
- The report clearly distinguishes between the internal analysis version and any supplier-shareable outputs

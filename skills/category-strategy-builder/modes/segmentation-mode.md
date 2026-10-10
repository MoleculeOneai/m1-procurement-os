# Mode: Category Segmentation (Kraljic Matrix)

## Goal
Classify the organisation's spend categories into the four Kraljic quadrants, producing a prioritised map that drives which strategy to apply to each category. The output is a completed Kraljic matrix and a ranked list of categories by strategic priority.

---

## The Kraljic Matrix — Framework Reference

The Kraljic matrix plots categories on two axes:

| Axis | Low | High |
|---|---|---|
| **Spend Impact** (x-axis) | Low value / low margin impact | High value / significant impact on cost base or operational performance |
| **Supply Risk** (y-axis) | Many suppliers, easy to switch, standard product/service | Few suppliers, long lead times, high switching cost, proprietary or specialised |

This produces four quadrants:

| Quadrant | Spend Impact | Supply Risk | Strategy |
|---|---|---|---|
| **Routine** (Non-Critical) | Low | Low | Simplify & automate — catalogues, p-cards, self-serve |
| **Leverage** | High | Low | Compete aggressively — consolidate volume, run tenders, extract best commercial terms |
| **Bottleneck** | Low | High | Secure supply — dual source, build inventory buffer, develop alternatives |
| **Strategic** | High | High | Manage as a relationship — joint value improvement, shared roadmap, executive sponsorship |

---

## Step 1 — Gather and normalise spend data

Attempt to read spend data from the spend-analyzer output first:
- Use `lib/spend_analysis_reader.py` to load any available output from `${CLAUDE_PLUGIN_DATA}/spend-analysis/`
- If no spend-analyzer data exists, ask the user to upload a spend file (CSV or Excel) or describe their top categories verbally

Normalise category names: check for miscoding, duplicate category names, and taxonomy mismatches before proceeding. Ask the user: "Do these category names look correct, or are any miscoded?"

---

## Step 2 — Score each category on both axes

For each category, score **Spend Impact** (1–5) and **Supply Risk** (1–5):

**Spend Impact scoring guide:**
- 5 — Category represents >10% of total addressable spend OR directly impacts product/service quality
- 4 — 5–10% of spend OR significant margin impact if supply is disrupted
- 3 — 2–5% of spend, moderate operational importance
- 2 — 1–2% of spend, low operational importance
- 1 — <1% of spend, tail spend, no operational impact

**Supply Risk scoring guide:**
- 5 — Single source globally, no alternatives, proprietary or highly specialised, >12 months lead time
- 4 — 2–3 viable suppliers, high switching cost, long qualification process
- 3 — Several suppliers available but concentrated market, moderate switching cost
- 2 — Many suppliers, some differentiation, manageable switching cost
- 1 — Commodity market, many interchangeable suppliers, no switching cost

Present scores in a table. Ask: "Do these scores reflect your experience? Any category you'd rank differently?"

---

## Step 3 — Place categories on the matrix

Use the scores to assign each category to a quadrant:

```
Spend Impact Score ≥3 AND Supply Risk Score ≥3 → Strategic
Spend Impact Score ≥3 AND Supply Risk Score <3 → Leverage
Spend Impact Score <3 AND Supply Risk Score ≥3 → Bottleneck
Spend Impact Score <3 AND Supply Risk Score <3 → Routine
```

Use `lib/category_segmenter.py` to compute and render the matrix in a clean ASCII or table format.

---

## Step 4 — Present the matrix output

Present a summary table in this format:

| Category | Annual Spend | Spend Score | Risk Score | Quadrant | Recommended Strategy |
|---|---|---|---|---|---|
| [Category] | [Amount] | [1–5] | [1–5] | [Quadrant] | [One-line strategy] |

Then present the distribution summary:
> "You have [N] Strategic categories, [N] Leverage, [N] Bottleneck, and [N] Routine categories.
> Your top priority categories for strategy development are: [list top 3–5 by spend in Strategic and Leverage quadrants]."

Check: if more than 20% of categories are in the Strategic quadrant, flag this:
> "Warning: [X]% of your categories are classified as Strategic. In practice, most organisations can only manage 5–10 Strategic relationships deeply. Consider whether some of these should be reclassified as Leverage."

---

## Step 5 — Prioritise for strategy development

Rank categories for strategy development using this priority order:
1. Strategic categories by spend (highest first) — these need full strategy documents
2. Leverage categories by spend — high commercial opportunity
3. Bottleneck categories by supply risk — business continuity risk
4. Routine categories — recommend process automation, not strategy

Output a prioritised work plan:
> "Recommended order of strategy development:
> 1. [Category] — Strategic — $[spend] — full strategy document required
> 2. [Category] — Leverage — $[spend] — competitive tender recommended
> ..."

---

## Step 6 — Save and log

Save the completed Kraljic matrix to `${CLAUDE_PLUGIN_DATA}/category-strategy/kraljic-matrix.md` using `templates/kraljic-matrix.md` as the base.

Append to `${CLAUDE_PLUGIN_DATA}/category-strategy-history.log`:
```
DATE: [date]
MODE: Segmentation
CATEGORIES_ASSESSED: [n]
STRATEGIC: [n] | LEVERAGE: [n] | BOTTLENECK: [n] | ROUTINE: [n]
TOP_PRIORITY: [category name]
```

---

## What Good Looks Like

- Every category has both a spend score and a supply risk score — no blank cells
- No category is in the Strategic quadrant without a documented justification
- The matrix is shared with the user for validation before strategy work begins
- A prioritised work plan is produced — not just a matrix picture

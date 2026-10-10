"""
categorize_spend.py — Spend Categorisation Engine
Part of the Molecule One Spend Intelligence Analyzer skill.

Classifies spend lines into a procurement taxonomy using supplier name,
description, and GL code signals. Detects maverick spend, tail spend,
and categorisation anomalies.

Gotchas are in the docstrings — read them before use.
"""

import re
import json
import csv
import io
from dataclasses import dataclass
from typing import Optional


# ---------------------------------------------------------------------------
# Custom taxonomy file loader
# ---------------------------------------------------------------------------

def load_custom_taxonomy(file_text: str, file_format: str = "auto") -> dict:
    """
    Load a user-provided taxonomy from a CSV or tab-delimited text file
    and convert it into the nested dict format used by categorize_line().

    Expected columns (flexible naming — auto-detected):
      - L1 / category_l1 / family / level1
      - L2 / category_l2 / category / level2
      - L3 / category_l3 / sub_category / subcategory / level3  (optional)
      - keywords / keyword_list / search_terms               (optional)
      - supplier / supplier_name                              (optional)

    Returns a dict:
      {
        "taxonomy": { L1: { L2: [keywords] } },
        "supplier_map": { supplier_name: { "category_l1": L1, "category": L2,
                                           "sub_category": L3, "confidence": "high" } },
        "warnings": [ str ]
      }

    Supported formats:
      "csv"   — comma-separated
      "tsv"   — tab-separated
      "auto"  — detect from content

    Gotchas:
      - If the file has no keyword column, Claude must still be able to use it
        as a supplier→category map. This is valid and common — many orgs maintain
        a simple supplier list with assigned categories.
      - Column headers are case-insensitive and whitespace-tolerant.
      - If L3 is not present, leave category_l3 blank — do not fabricate sub-categories.
      - Duplicate L1/L2 pairs are merged (their keyword lists are combined).
      - Unknown column names are ignored, not errored — surface as warnings.
      - Excel files (.xlsx) cannot be parsed as text — tell the user to export as CSV first.
    """
    warnings = []
    taxonomy = {}
    supplier_map = {}

    # Auto-detect delimiter
    if file_format == "auto":
        file_format = "tsv" if "\t" in file_text[:500] else "csv"

    delimiter = "\t" if file_format == "tsv" else ","

    try:
        reader = csv.DictReader(io.StringIO(file_text), delimiter=delimiter)
    except Exception as e:
        return {"taxonomy": {}, "supplier_map": {}, "warnings": [f"Failed to parse file: {e}"]}

    # Normalise header names
    COLUMN_ALIASES = {
        "l1": ["l1", "category_l1", "family", "level1", "level 1", "spend family", "l1_category"],
        "l2": ["l2", "category_l2", "category", "level2", "level 2", "spend category", "l2_category"],
        "l3": ["l3", "category_l3", "sub_category", "subcategory", "level3", "level 3", "l3_category", "sub category"],
        "keywords": ["keywords", "keyword_list", "search_terms", "keyword list", "search terms", "tags"],
        "supplier": ["supplier", "supplier_name", "vendor", "vendor_name", "supplier name", "vendor name"],
    }

    def find_col(headers, field):
        for h in headers:
            if h.strip().lower() in COLUMN_ALIASES.get(field, []):
                return h
        return None

    try:
        raw_rows = list(reader)
    except Exception as e:
        return {"taxonomy": {}, "supplier_map": {}, "warnings": [f"Failed to read rows: {e}"]}

    if not raw_rows:
        return {"taxonomy": {}, "supplier_map": {}, "warnings": ["File appears to be empty."]}

    headers = list(raw_rows[0].keys())
    col_l1  = find_col(headers, "l1")
    col_l2  = find_col(headers, "l2")
    col_l3  = find_col(headers, "l3")
    col_kw  = find_col(headers, "keywords")
    col_sup = find_col(headers, "supplier")

    if not col_l1:
        warnings.append("No L1 category column found. Expected column named: l1, category_l1, family, or level1.")
    if not col_l2:
        warnings.append("No L2 category column found. Expected column named: l2, category_l2, category, or level2.")
    if not col_kw:
        warnings.append("No keywords column found — taxonomy will be used for supplier mapping only, not keyword matching.")
    if col_l3 is None:
        warnings.append("No L3 sub-category column found — L3 will be left blank.")

    unknown_cols = [h for h in headers if h not in
                    [col_l1, col_l2, col_l3, col_kw, col_sup] and h]
    if unknown_cols:
        warnings.append(f"Unrecognised columns ignored: {unknown_cols}")

    rows_loaded = 0
    for row in raw_rows:
        l1 = row.get(col_l1, "").strip() if col_l1 else ""
        l2 = row.get(col_l2, "").strip() if col_l2 else ""
        l3 = row.get(col_l3, "").strip() if col_l3 else ""
        kw_raw = row.get(col_kw, "").strip() if col_kw else ""
        supplier = row.get(col_sup, "").strip() if col_sup else ""

        if not l1 or not l2:
            continue

        # Build taxonomy
        if l1 not in taxonomy:
            taxonomy[l1] = {}
        if l2 not in taxonomy[l1]:
            taxonomy[l1][l2] = []

        if kw_raw:
            # Keywords may be comma, semicolon, or pipe-separated
            keywords = [k.strip().lower() for k in re.split(r"[,;|]", kw_raw) if k.strip()]
            taxonomy[l1][l2].extend(keywords)
            # Deduplicate
            taxonomy[l1][l2] = list(dict.fromkeys(taxonomy[l1][l2]))

        # Build supplier map
        if supplier:
            supplier_map[supplier] = {
                "category_l1": l1,
                "category": l2,
                "sub_category": l3,
                "confidence": "high"
            }

        rows_loaded += 1

    return {
        "taxonomy": taxonomy if taxonomy else {},
        "supplier_map": supplier_map if supplier_map else {},
        "stats": {
            "rows_loaded": rows_loaded,
            "l1_categories": len(taxonomy),
            "l2_categories": sum(len(v) for v in taxonomy.values()),
            "suppliers_mapped": len(supplier_map),
            "has_keywords": col_kw is not None,
        },
        "warnings": warnings
    }


def merge_with_default_taxonomy(custom: dict, use_default_as_fallback: bool = True) -> dict:
    """
    Merge a custom taxonomy with the DEFAULT_TAXONOMY.

    If use_default_as_fallback is True:
      - Custom taxonomy takes precedence for any L1/L2 that overlaps
      - Default taxonomy fills in L1/L2 categories not present in custom

    If use_default_as_fallback is False:
      - Only the custom taxonomy is used (default is ignored entirely)

    Gotcha: if the user provides a custom taxonomy, always confirm whether they
    want the default as a fallback or want ONLY their taxonomy applied.
    Mixing taxonomies silently can produce unexpected category assignments.
    """
    if not use_default_as_fallback:
        return custom

    merged = {}
    # Start with default
    for l1, l2_dict in DEFAULT_TAXONOMY.items():
        merged[l1] = {}
        for l2, keywords in l2_dict.items():
            merged[l1][l2] = list(keywords)

    # Override/extend with custom
    for l1, l2_dict in custom.items():
        if l1 not in merged:
            merged[l1] = {}
        for l2, keywords in l2_dict.items():
            if l2 not in merged[l1]:
                merged[l1][l2] = []
            # Custom keywords take precedence — prepend them
            existing = merged[l1][l2]
            merged[l1][l2] = list(dict.fromkeys(keywords + existing))

    return merged


# ---------------------------------------------------------------------------
# Default Molecule One procurement taxonomy
# ---------------------------------------------------------------------------

DEFAULT_TAXONOMY = {
    "Direct Materials": {
        "Raw Materials": ["raw material", "feedstock", "ingredient", "component", "commodity"],
        "Packaging": ["packaging", "label", "carton", "pallet", "container", "bottle", "box"],
        "Sub-assemblies": ["sub-assembly", "sub assembly", "assembly", "module", "kit"]
    },
    "Indirect Goods": {
        "Office Supplies": ["stationery", "office supply", "paper", "toner", "ink", "desk"],
        "Facilities Consumables": ["cleaning", "hygiene", "catering", "vending", "safety equipment", "PPE", "workwear"],
        "IT Hardware": ["laptop", "computer", "server", "monitor", "printer", "device", "hardware", "equipment lease"],
        "Fleet & Vehicles": ["vehicle", "fleet", "car", "van", "fuel", "mileage", "lease car"]
    },
    "Indirect Services": {
        "Professional Services": [
            "consulting", "consultancy", "advisory", "management consulting",
            "strategy", "audit", "accountancy", "accounting", "legal", "solicitor",
            "barrister", "law firm", "tax", "compliance", "due diligence"
        ],
        "Technology & IT": [
            "software", "SaaS", "cloud", "subscription", "licence", "license",
            "IT service", "managed service", "hosting", "telecoms", "broadband",
            "telephony", "cybersecurity", "support contract", "maintenance contract"
        ],
        "Marketing & Communications": [
            "marketing", "advertising", "agency", "creative", "design",
            "brand", "PR", "public relations", "social media", "digital marketing",
            "print", "media", "events", "exhibition", "sponsorship"
        ],
        "Facilities & Real Estate": [
            "rent", "lease", "rates", "utilities", "electricity", "gas", "water",
            "facilities management", "FM", "maintenance", "repair", "HVAC",
            "security", "cleaning service", "waste", "property"
        ],
        "HR & People Services": [
            "recruitment", "staffing", "temporary staff", "temp labour", "agency labour",
            "payroll", "HR service", "training", "learning", "development", "coaching",
            "employee benefits", "occupational health", "EAP"
        ],
        "Travel & Expenses": [
            "travel", "flight", "airline", "hotel", "accommodation",
            "rail", "train", "taxi", "hire car", "car rental", "subsistence",
            "conference", "entertainment"
        ],
        "Logistics & Distribution": [
            "freight", "shipping", "courier", "parcel", "logistics", "transport",
            "warehousing", "distribution", "customs", "duties", "last mile"
        ],
        "Financial Services": [
            "insurance", "banking", "finance charge", "FX", "foreign exchange",
            "hedging", "factoring", "treasury", "merchant services"
        ],
        "Research & Innovation": [
            "research", "R&D", "laboratory", "testing", "certification",
            "patent", "IP", "intellectual property"
        ]
    },
    "Capital Expenditure": {
        "IT Capital": ["server purchase", "infrastructure", "network equipment", "data centre"],
        "Property & Fit-Out": ["fit out", "fit-out", "refurbishment", "construction", "building work"],
        "Plant & Equipment": ["machinery", "plant", "equipment purchase", "asset", "CAPEX"]
    }
}


# ---------------------------------------------------------------------------
# Categorisation
# ---------------------------------------------------------------------------

def categorize_line(description: str, supplier_name: str = "",
                    gl_code: str = "", gl_description: str = "",
                    supplier_category_map: dict = None,
                    taxonomy: dict = None) -> dict:
    """
    Categorise a single spend line into L1/L2/L3 taxonomy.

    Returns:
      - category_l1: str
      - category_l2: str
      - category_l3: str (if match found at L3)
      - confidence: "high" | "medium" | "low" | "unclassified"
      - signal_used: "supplier_map" | "description" | "gl_code" | "none"
      - rationale: str — why this category was assigned

    Signal priority: supplier_category_map > description keywords > GL description > unclassified

    Gotchas:
      - Low-confidence categorisation on high-value lines must be reviewed by a human.
        Do not auto-apply this to lines above the materiality threshold without user confirmation.
      - The same description can mean different things in different contexts.
        "Maintenance" could be IT systems maintenance or building maintenance.
        When the GL code is available, it usually resolves the ambiguity — use it.
      - Some spend lines will genuinely be unclassifiable from description alone
        (e.g. "Payment as agreed", "Invoice 12345"). Flag these — do not guess.
    """
    if taxonomy is None:
        taxonomy = DEFAULT_TAXONOMY

    result = {
        "category_l1": "",
        "category_l2": "",
        "category_l3": "",
        "confidence": "unclassified",
        "signal_used": "none",
        "rationale": "No matching signals found"
    }

    # 1. Check supplier-category map first (highest confidence)
    if supplier_category_map and supplier_name:
        norm_supplier = supplier_name.upper().strip()
        for map_name, map_data in supplier_category_map.items():
            if map_name.upper().strip() in norm_supplier or norm_supplier in map_name.upper().strip():
                result["category_l1"] = map_data.get("category_l1", "")
                result["category_l2"] = map_data.get("category", "")
                result["category_l3"] = map_data.get("sub_category", "")
                result["confidence"] = map_data.get("confidence", "high")
                result["signal_used"] = "supplier_map"
                result["rationale"] = f"Supplier '{supplier_name}' matched in category map"
                return result

    # 2. Description keyword matching
    search_text = f"{description} {gl_description}".lower()
    best_match = None
    best_score = 0

    for l1, l2_dict in taxonomy.items():
        for l2, keywords in l2_dict.items():
            score = sum(1 for kw in keywords if kw.lower() in search_text)
            if score > best_score:
                best_score = score
                best_match = (l1, l2)

    if best_match and best_score >= 2:
        result["category_l1"] = best_match[0]
        result["category_l2"] = best_match[1]
        result["confidence"] = "high" if best_score >= 3 else "medium"
        result["signal_used"] = "description"
        result["rationale"] = f"Matched {best_score} keywords in description/GL"
    elif best_match and best_score == 1:
        result["category_l1"] = best_match[0]
        result["category_l2"] = best_match[1]
        result["confidence"] = "low"
        result["signal_used"] = "description"
        result["rationale"] = f"Weak match (1 keyword) in description/GL — review recommended"

    return result


def batch_categorize(spend_lines: list, supplier_category_map: dict = None,
                     taxonomy: dict = None, materiality_threshold: float = 10000) -> dict:
    """
    Categorise a list of SpendLine dicts or raw row dicts.

    Returns:
      - categorised_lines: list of lines with category fields populated
      - summary: {high_confidence_pct, medium_confidence_pct, low_pct, unclassified_pct}
      - high_value_for_review: lines above materiality_threshold with low/unclassified confidence
      - coverage_rate: % of spend VALUE categorised (not just line count)

    Gotchas:
      - Always check coverage_rate, not just line count. A 95% line coverage rate
        on a dataset where 90% of lines are small transactions might mean 30% of
        spend VALUE is unclassified.
      - Return high_value_for_review to the user before finalising. These are the
        lines where a wrong category has the biggest impact.
    """
    if taxonomy is None:
        taxonomy = DEFAULT_TAXONOMY

    categorised = []
    confidence_counts = {"high": 0, "medium": 0, "low": 0, "unclassified": 0}
    total_value = 0.0
    categorised_value = 0.0
    high_value_review = []

    for line in spend_lines:
        desc = str(line.get("description", ""))
        supplier = str(line.get("supplier_name_normalised", line.get("supplier_name_raw", "")))
        gl_code = str(line.get("gl_code", ""))
        gl_desc = str(line.get("gl_description", ""))
        amount = float(line.get("amount", 0) or 0)

        cat = categorize_line(
            description=desc,
            supplier_name=supplier,
            gl_code=gl_code,
            gl_description=gl_desc,
            supplier_category_map=supplier_category_map,
            taxonomy=taxonomy
        )

        line.update({
            "category_l1": cat["category_l1"],
            "category_l2": cat["category_l2"],
            "category_l3": cat["category_l3"],
            "category_confidence": cat["confidence"],
            "categorisation_signal": cat["signal_used"],
            "categorisation_rationale": cat["rationale"]
        })

        categorised.append(line)
        confidence_counts[cat["confidence"]] = confidence_counts.get(cat["confidence"], 0) + 1
        total_value += amount

        if cat["confidence"] not in ("unclassified",):
            categorised_value += amount

        if amount >= materiality_threshold and cat["confidence"] in ("low", "unclassified"):
            high_value_review.append({
                "supplier": supplier,
                "description": desc[:80],
                "amount": amount,
                "confidence": cat["confidence"],
                "suggested_category": f"{cat['category_l1']} / {cat['category_l2']}" if cat["category_l1"] else "None"
            })

    total_lines = len(categorised)
    coverage_rate = round(categorised_value / max(total_value, 1) * 100, 1)

    return {
        "categorised_lines": categorised,
        "summary": {
            "total_lines": total_lines,
            "high_confidence_pct": round(confidence_counts["high"] / max(total_lines, 1) * 100, 1),
            "medium_confidence_pct": round(confidence_counts["medium"] / max(total_lines, 1) * 100, 1),
            "low_confidence_pct": round(confidence_counts["low"] / max(total_lines, 1) * 100, 1),
            "unclassified_pct": round(confidence_counts["unclassified"] / max(total_lines, 1) * 100, 1)
        },
        "coverage_rate_by_value": coverage_rate,
        "high_value_for_review": sorted(high_value_review, key=lambda x: x["amount"], reverse=True)
    }


# ---------------------------------------------------------------------------
# Category-aware maverick signal detection
# ---------------------------------------------------------------------------

# Known consumer-grade or off-contract supplier patterns by category.
# These are suppliers that are obviously off-contract by their nature —
# i.e. a consumer platform or non-preferred supplier that should never
# appear in corporate spend without a specific approval.
#
# Each entry: category_l2 → list of (pattern, reason) tuples.
# Patterns are case-insensitive substring matches against supplier name.
# Add org-specific known mavericks here or in the custom taxonomy.
KNOWN_CONSUMER_MAVERICK_SIGNALS = {
    "Travel & Expenses": [
        ("booking.com",     "Consumer OTA — corporate travel should route via TMC"),
        ("airbnb",          "Consumer short-stay platform — not a preferred accommodation supplier"),
        ("expedia",         "Consumer OTA — corporate travel should route via TMC"),
        ("hotels.com",      "Consumer OTA — corporate travel should route via TMC"),
        ("trivago",         "Consumer OTA — not a corporate travel supplier"),
        ("lastminute",      "Consumer OTA — not a corporate travel supplier"),
        ("kayak",           "Consumer travel search — not a direct booking channel"),
        ("easyjet",         "Direct airline booking — should route via TMC for policy compliance"),
        ("ryanair",         "Direct airline booking — should route via TMC for policy compliance"),
    ],
    "Facilities & Real Estate": [
        ("npower",          "Residential/SME utility — corporate should be on framework contract"),
        ("edf",             "Residential/SME utility — corporate should be on framework contract"),
        ("british gas",     "Residential/SME utility — corporate should be on framework contract"),
        ("eon ",            "Residential/SME utility — corporate should be on framework contract"),
        ("scottish power",  "Residential/SME utility — corporate should be on framework contract"),
        ("sse ",            "Residential/SME utility — corporate should be on framework contract"),
        ("bulb ",           "Consumer-grade utility provider"),
        ("octopus energy",  "Consumer-grade utility provider"),
    ],
    "Technology & IT": [
        ("zoom ",           "Consumer/SMB SaaS — likely personal account, not enterprise agreement"),
        ("zoom video",      "Consumer/SMB SaaS — check for enterprise agreement"),
        ("notion ",         "Consumer/SMB SaaS — likely personal account"),
        ("figma",           "Consumer/SMB SaaS — check for enterprise agreement"),
        ("trello",          "Consumer/SMB SaaS — part of Atlassian suite, check licence"),
        ("dropbox",         "Consumer cloud storage — corporate data governance risk"),
        ("mailchimp",       "Consumer email marketing — should be on enterprise contract"),
        ("canva",           "Consumer design tool — check for enterprise agreement"),
        ("surveymonkey",    "Consumer survey tool — check for enterprise agreement"),
        ("grammarly",       "Consumer writing tool — check for enterprise agreement"),
        ("chatgpt",         "Consumer AI subscription — check data governance policy"),
        ("openai",          "Consumer AI subscription — check data governance and enterprise terms"),
        ("claude.ai",       "Consumer AI subscription — check data governance and enterprise terms"),
        ("miro.com",        "Consumer/SMB collaboration tool — check enterprise agreement"),
        ("monday.com",      "Consumer/SMB PM tool — check for enterprise agreement and consolidation"),
        ("asana",           "Consumer/SMB PM tool — check for consolidation with other PM tools"),
        ("basecamp",        "Consumer/SMB PM tool — check for consolidation with other PM tools"),
    ],
    "Marketing & Communications": [
        ("fiverr",          "Consumer freelance marketplace — no contract, compliance risk"),
        ("upwork",          "Consumer freelance marketplace — no contract, compliance risk"),
        ("99designs",       "Consumer design marketplace — no preferred agency arrangement"),
        ("shutterstock",    "Direct stock subscription — check for agency-managed licence"),
        ("getty images",    "Direct image purchase — check for agency-managed licence"),
    ],
    "Professional Services": [
        ("mckinsey",        "Check PO compliance — McKinsey typically requires approved PO for each engagement"),
        ("taylor wessing",  "Check PO compliance and preferred panel status"),
    ],
    "HR & People Services": [
        ("indeed",          "Direct job board spend — should route through preferred recruitment agency"),
        ("reed.co.uk",      "Direct job board spend — check preferred recruitment agency arrangement"),
        ("totaljobs",       "Direct job board spend — check preferred recruitment agency arrangement"),
        ("linkedin recruiter", "Direct LinkedIn spend — check preferred agency PSL"),
    ],
}


def detect_consumer_maverick(spend_lines: list,
                              additional_signals: dict = None) -> dict:
    """
    Detect spend with consumer-grade or known off-contract suppliers by
    cross-referencing supplier names against KNOWN_CONSUMER_MAVERICK_SIGNALS
    for each spend category.

    This runs WITHOUT needing a preferred supplier list — it detects maverick
    spend by recognising well-known consumer platforms that should not appear
    in corporate spend.

    Parameters:
      spend_lines       — list of categorised spend line dicts (must have
                          category_l2 and supplier_name_normalised fields)
      additional_signals — optional {category_l2: [(pattern, reason)]} dict
                           to extend the built-in signals with org-specific rules

    Returns:
      - flagged_lines: list of spend line dicts with maverick_flag and maverick_reason added
      - summary: {
            total_flagged_lines: int,
            total_flagged_spend: float,
            by_category: {category: {count, spend, suppliers: [{name, spend, reason}]}},
            by_supplier: [{supplier, category, spend, reason, line_count}]
        }
      - opportunities: list of SavingsOpportunity-compatible dicts (one per flagged category)

    Gotchas:
      - Pattern matching is substring-based (case-insensitive). A match on
        "Zoom " (with trailing space) is intentional to avoid false-matching
        "Zoom Media Ltd" as a consumer Zoom subscription.
      - Some of these suppliers may have legitimate enterprise contracts.
        Always present as "investigate" not "confirmed maverick."
        The flag reason string explains what to look for.
      - PO absence + consumer platform signal = strong maverick indicator.
        PO present + consumer platform = possible enterprise contract; flag for review.
    """
    signals = {k: list(v) for k, v in KNOWN_CONSUMER_MAVERICK_SIGNALS.items()}
    if additional_signals:
        for cat, patterns in additional_signals.items():
            signals.setdefault(cat, []).extend(patterns)

    flagged = []
    summary_by_cat = {}
    summary_by_sup = {}

    for line in spend_lines:
        cat = str(line.get("category_l2", ""))
        supplier = str(line.get("supplier_name_normalised", line.get("supplier_name_raw", ""))).lower()
        amount = float(line.get("amount", 0) or 0)

        cat_signals = signals.get(cat, [])
        matched_pattern = None
        matched_reason = None

        for pattern, reason in cat_signals:
            if pattern.lower() in supplier:
                matched_pattern = pattern
                matched_reason = reason
                break

        if matched_pattern:
            line["maverick_flag"] = True
            line["maverick_signal"] = "consumer_platform"
            line["maverick_reason"] = matched_reason
            line["maverick_pattern_matched"] = matched_pattern
            flagged.append(line)

            # Aggregate by category
            if cat not in summary_by_cat:
                summary_by_cat[cat] = {"count": 0, "spend": 0.0, "suppliers": {}}
            summary_by_cat[cat]["count"] += 1
            summary_by_cat[cat]["spend"] = round(summary_by_cat[cat]["spend"] + amount, 2)

            sup_display = line.get("supplier_name_normalised", line.get("supplier_name_raw", ""))
            if sup_display not in summary_by_cat[cat]["suppliers"]:
                summary_by_cat[cat]["suppliers"][sup_display] = {"spend": 0.0, "reason": matched_reason, "count": 0}
            summary_by_cat[cat]["suppliers"][sup_display]["spend"] = round(
                summary_by_cat[cat]["suppliers"][sup_display]["spend"] + amount, 2
            )
            summary_by_cat[cat]["suppliers"][sup_display]["count"] += 1

            # Aggregate by supplier
            if sup_display not in summary_by_sup:
                summary_by_sup[sup_display] = {"category": cat, "spend": 0.0, "reason": matched_reason, "line_count": 0}
            summary_by_sup[sup_display]["spend"] = round(summary_by_sup[sup_display]["spend"] + amount, 2)
            summary_by_sup[sup_display]["line_count"] += 1
        else:
            line.setdefault("maverick_flag", False)

    # Build category summary with supplier list
    cat_summary_out = {}
    for cat, data in summary_by_cat.items():
        cat_summary_out[cat] = {
            "count": data["count"],
            "spend": data["spend"],
            "suppliers": sorted(
                [{"name": s, "spend": v["spend"], "reason": v["reason"], "line_count": v["count"]}
                 for s, v in data["suppliers"].items()],
                key=lambda x: x["spend"], reverse=True
            )
        }

    # Build per-category savings opportunities
    opportunities = []
    opp_num = 300
    for cat, data in cat_summary_out.items():
        if data["spend"] <= 0:
            continue
        opp_num += 1
        sup_names = ", ".join(s["name"] for s in data["suppliers"][:5])
        reasons = "; ".join(
            f'{s["name"]}: {s["reason"]}'
            for s in data["suppliers"][:3]
        )
        opportunities.append({
            "id": f"OPP-{opp_num:03d}",
            "type": "maverick_spend",
            "category": cat,
            "description": (
                f"{len(data['suppliers'])} consumer-grade/off-contract supplier(s) detected "
                f"in {cat}: {sup_names}"
            ),
            "savings_low": round(data["spend"] * 0.08, 2),
            "savings_high": round(data["spend"] * 0.15, 2),
            "horizon": "quick",
            "effort": "Low",
            "priority": opp_num - 299,
            "basis": (
                f"{data['count']} transactions totalling £{data['spend']:,.0f} with consumer-grade "
                f"platforms in {cat}. Evidence: {reasons}. "
                "Routing to preferred/contracted suppliers typically yields 8–15% savings "
                "plus improved data governance and policy compliance."
            ),
            "affected_suppliers": [s["name"] for s in data["suppliers"]],
            "actions": [
                f"Confirm whether enterprise agreements exist for {', '.join(s['name'] for s in data['suppliers'][:3])}",
                "Check against preferred supplier list / approved vendor register",
                "Issue a policy reminder to the relevant business units",
                "Route future spend to preferred contracted supplier or run mini-tender",
            ]
        })

    total_flagged_spend = sum(v["spend"] for v in summary_by_cat.values())

    return {
        "flagged_lines": flagged,
        "summary": {
            "total_flagged_lines": len(flagged),
            "total_flagged_spend": round(total_flagged_spend, 2),
            "by_category": cat_summary_out,
            "by_supplier": sorted(
                [{"supplier": s, **v} for s, v in summary_by_sup.items()],
                key=lambda x: x["spend"], reverse=True
            )
        },
        "opportunities": opportunities
    }


# ---------------------------------------------------------------------------
# Spend quality metrics
# ---------------------------------------------------------------------------

def calculate_po_compliance(spend_lines: list) -> dict:
    """
    Calculate PO compliance rate — % of spend that is backed by a PO.

    Gotchas:
      - A PO number field being present ≠ a valid PO. Check for dummy PO numbers
        (e.g. "N/A", "0", "NOPOS") and exclude them from the compliant count.
      - Regulated categories (e.g. utilities, government rates) cannot be PO-backed
        by nature. Exclude known non-PO categories before calculating the rate.
    """
    dummy_po_patterns = [r'^0+$', r'^n/?a$', r'^none$', r'^no\s*po$', r'^nopo$']

    total_spend = 0.0
    po_backed_spend = 0.0
    non_po_lines = []

    for line in spend_lines:
        amount = float(line.get("amount", 0) or 0)
        po = str(line.get("po_number", "")).strip()
        total_spend += amount

        is_dummy = any(re.match(p, po, re.IGNORECASE) for p in dummy_po_patterns)
        if po and not is_dummy:
            po_backed_spend += amount
        else:
            non_po_lines.append({
                "supplier": line.get("supplier_name_normalised", ""),
                "amount": amount,
                "category": line.get("category_l2", "")
            })

    compliance_rate = round(po_backed_spend / max(total_spend, 1) * 100, 1)

    # Top non-PO suppliers by value
    supplier_non_po = {}
    for line in non_po_lines:
        s = line["supplier"]
        supplier_non_po[s] = supplier_non_po.get(s, 0) + line["amount"]

    top_non_po_suppliers = sorted(supplier_non_po.items(), key=lambda x: x[1], reverse=True)[:10]

    return {
        "po_compliance_rate": compliance_rate,
        "po_backed_spend": round(po_backed_spend, 2),
        "non_po_spend": round(total_spend - po_backed_spend, 2),
        "total_spend": round(total_spend, 2),
        "top_non_po_suppliers": [{"supplier": s, "non_po_spend": round(v, 2)} for s, v in top_non_po_suppliers],
        "interpretation": (
            "Best-in-class PO compliance is >90%. "
            f"Current rate of {compliance_rate}% is "
            + ("best-in-class." if compliance_rate >= 90
               else "acceptable but improvable." if compliance_rate >= 75
               else "below target — significant maverick spend risk.")
        )
    }


def identify_tail_spend(spend_by_supplier: dict, tail_threshold: float = 5000,
                        admin_cost_per_supplier: float = 500) -> dict:
    """
    Identify tail suppliers (those below a spend threshold) and quantify
    the administrative cost of maintaining these relationships.

    Gotchas:
      - The £5,000 default threshold is for a mid-sized organisation. Adjust
        for the organisation's scale — a £500M company's tail starts at £50k.
      - Admin cost per supplier (default £500/year) includes: invoice processing,
        statement reconciliation, onboarding, compliance checks. This is conservative
        for complex suppliers (e.g. those requiring insurance certificates).
      - Not all tail spend can be eliminated. Some small suppliers are sole-source
        or locally mandated. Always present rationalisation as an opportunity to
        investigate, not a list of suppliers to immediately cut.
    """
    tail_suppliers = {s: v for s, v in spend_by_supplier.items() if v < tail_threshold}
    strategic_suppliers = {s: v for s, v in spend_by_supplier.items() if v >= tail_threshold}

    tail_spend_value = sum(tail_suppliers.values())
    total_spend_value = sum(spend_by_supplier.values())
    admin_cost = len(tail_suppliers) * admin_cost_per_supplier

    return {
        "total_suppliers": len(spend_by_supplier),
        "tail_suppliers_count": len(tail_suppliers),
        "strategic_suppliers_count": len(strategic_suppliers),
        "tail_spend_value": round(tail_spend_value, 2),
        "tail_spend_pct": round(tail_spend_value / max(total_spend_value, 1) * 100, 1),
        "estimated_admin_cost": round(admin_cost, 2),
        "tail_threshold_used": tail_threshold,
        "top_tail_suppliers": sorted(tail_suppliers.items(), key=lambda x: x[1], reverse=True)[:20],
        "recommendation": (
            f"{len(tail_suppliers)} tail suppliers (spend <{tail_threshold:,}) represent "
            f"{round(tail_spend_value/max(total_spend_value,1)*100,1)}% of spend "
            f"but cost an estimated {admin_cost:,.0f} to administer annually. "
            "Consider: P-card mandate for small purchases, aggregation through a single distributor, "
            "or a tail spend management platform."
        )
    }

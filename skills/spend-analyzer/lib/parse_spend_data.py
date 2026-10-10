"""
parse_spend_data.py — Spend Data Ingestion and Normalisation
Part of the Molecule One Spend Intelligence Analyzer skill.

Handles spend exports from any source: ERP CSV exports, P-card dumps,
invoice registers, manual spreadsheets. Normalises into a consistent
spend line format before analysis.

Gotchas are in the docstrings — read them before use.
"""

import re
import json
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


# ---------------------------------------------------------------------------
# Standard spend line format
# ---------------------------------------------------------------------------

@dataclass
class SpendLine:
    """
    One normalised spend transaction.

    All analysis runs on SpendLine objects — not on raw data.
    Always convert source data to SpendLine before proceeding.
    """
    line_id: str                         # Original row identifier
    supplier_name_raw: str               # As it appears in source data
    supplier_name_normalised: str        # After deduplication
    amount: float                        # Always in primary currency, always positive
    currency_original: str               # Original currency code
    amount_original: float               # Original amount before conversion
    date: Optional[str]                  # ISO format YYYY-MM-DD
    description: str                     # Line item description
    category_l1: str = ""                # Direct / Indirect Goods / Indirect Services / CapEx
    category_l2: str = ""                # e.g. Technology & IT
    category_l3: str = ""                # e.g. Software & SaaS
    category_confidence: str = ""        # high / medium / low / unclassified
    po_number: str = ""                  # PO reference if available
    gl_code: str = ""                    # General ledger account code
    cost_centre: str = ""               # Business unit / cost centre
    is_intercompany: bool = False        # True if related-entity transaction
    is_capex: bool = False               # True if capital expenditure
    is_duplicate: bool = False           # True if suspected duplicate
    flags: list = field(default_factory=list)  # Any quality or analysis flags


# ---------------------------------------------------------------------------
# Data quality audit
# ---------------------------------------------------------------------------

def audit_data_quality(rows: list, expected_fields: list = None) -> dict:
    """
    Assess data quality before analysis begins.

    Returns a quality report dict:
      - total_rows: int
      - total_spend_detected: float (sum of amounts found)
      - currency_codes_found: list
      - is_multicurrency: bool
      - date_range: {min, max, period_months}
      - field_completeness: {field: pct_populated}
      - duplicate_count: int (exact row duplicates)
      - quality_score: 0–100 (weighted completeness score)
      - recommendations: list of str

    Gotchas:
      - `rows` should be a list of dicts from csv.DictReader or equivalent.
        Call this before any normalisation or categorisation.
      - A quality score below 60 means the analysis will be unreliable.
        Surface this prominently — do not soft-pedal a bad quality score.
      - The function cannot detect subtle data problems like GL codes being
        used inconsistently, or a supplier being excluded from the export
        due to an ERP filter. Always ask the user to confirm the export
        parameters (date range, entity scope, payment status filter).
    """
    if not rows:
        return {"error": "No data provided"}

    if expected_fields is None:
        expected_fields = [
            "supplier_name", "amount", "date", "description",
            "category", "po_number", "gl_code", "cost_centre", "currency"
        ]

    # Try to auto-detect field names (ERP exports use varying column names)
    field_aliases = {
        "supplier_name": ["supplier", "vendor", "payee", "supplier name", "vendor name", "creditor"],
        "amount": ["amount", "value", "total", "net amount", "spend", "payment amount", "invoice amount"],
        "date": ["date", "invoice date", "payment date", "transaction date", "posting date"],
        "description": ["description", "line description", "narrative", "details", "goods description"],
        "category": ["category", "spend category", "commodity", "unspsc", "gl description"],
        "po_number": ["po number", "po#", "purchase order", "order number", "po ref"],
        "gl_code": ["gl code", "gl account", "account code", "ledger code", "nominal code"],
        "cost_centre": ["cost centre", "cost center", "department", "business unit", "bu"],
        "currency": ["currency", "currency code", "ccy", "iso currency"]
    }

    # Detect which columns are present using aliases
    sample_keys = [k.lower().strip() for k in rows[0].keys()] if rows else []
    detected_fields = {}
    for standard_field, aliases in field_aliases.items():
        for alias in aliases:
            if alias in sample_keys:
                detected_fields[standard_field] = alias
                break

    # Field completeness
    field_completeness = {}
    for standard_field, source_col in detected_fields.items():
        populated = sum(1 for r in rows if r.get(source_col, "").strip())
        field_completeness[standard_field] = round(populated / len(rows) * 100, 1)

    # Missing critical fields
    missing_critical = [f for f in ["supplier_name", "amount", "date"] if f not in detected_fields]

    # Currency detection — count rows and spend by currency
    currencies = set()
    currency_breakdown = {}  # {ccy: {count, total_face_value}}
    currency_col_name = detected_fields.get("currency")
    amount_col_name   = detected_fields.get("amount")

    for r in rows:
        ccy = r.get(currency_col_name, "").strip().upper() if currency_col_name else ""
        if not ccy:
            ccy = "UNKNOWN"
        currencies.add(ccy)
        if ccy not in currency_breakdown:
            currency_breakdown[ccy] = {"count": 0, "total_face_value": 0.0}
        currency_breakdown[ccy]["count"] += 1
        if amount_col_name:
            try:
                val = abs(float(str(r.get(amount_col_name, "0")).replace(",", "").replace("£", "").replace("$", "").replace("€", "")))
                currency_breakdown[ccy]["total_face_value"] = round(
                    currency_breakdown[ccy]["total_face_value"] + val, 2
                )
            except (ValueError, TypeError):
                pass

    currencies.discard("")
    currencies.discard("UNKNOWN")

    # Total spend (face value — pre-conversion, for quality audit only)
    total_spend = 0.0
    amount_col = detected_fields.get("amount")
    if amount_col:
        for r in rows:
            try:
                val = float(str(r.get(amount_col, "0")).replace(",", "").replace("£", "").replace("$", "").replace("€", ""))
                total_spend += abs(val)
            except (ValueError, TypeError):
                pass

    # Date range
    date_range = {"min": None, "max": None, "period_months": None}
    date_col = detected_fields.get("date")
    if date_col:
        dates = []
        for r in rows:
            raw_date = r.get(date_col, "")
            parsed = _try_parse_date(raw_date)
            if parsed:
                dates.append(parsed)
        if dates:
            date_range["min"] = min(dates).strftime("%Y-%m-%d")
            date_range["max"] = max(dates).strftime("%Y-%m-%d")
            delta = max(dates) - min(dates)
            date_range["period_months"] = round(delta.days / 30.44, 1)

    # Duplicate detection (exact amount + supplier + date)
    seen = set()
    duplicates = 0
    for r in rows:
        key = (
            r.get(detected_fields.get("supplier_name", ""), ""),
            r.get(detected_fields.get("amount", ""), ""),
            r.get(detected_fields.get("date", ""), "")
        )
        if key in seen and all(k for k in key):
            duplicates += 1
        seen.add(key)

    # Quality score
    critical_score = 0 if missing_critical else 40
    completeness_score = sum(field_completeness.values()) / max(len(field_completeness), 1) * 0.4
    duplicate_penalty = min(duplicates / max(len(rows), 1) * 100, 20)
    quality_score = min(100, int(critical_score + completeness_score - duplicate_penalty))

    # Recommendations
    recommendations = []
    if missing_critical:
        recommendations.append(
            f"CRITICAL: Required fields not found: {missing_critical}. "
            "Analysis cannot proceed without supplier name, amount, and date."
        )
    non_primary = {c: v for c, v in currency_breakdown.items()
                   if c not in ("UNKNOWN", "") and len(currencies) > 0
                   and c != sorted(currency_breakdown, key=lambda x: currency_breakdown[x]["count"], reverse=True)[0]}
    if len(currencies) > 1:
        ccy_detail = ", ".join(
            f"{c}: {v['count']} rows ({v['total_face_value']:,.0f} face value)"
            for c, v in sorted(currency_breakdown.items(), key=lambda x: x[1]["count"], reverse=True)
            if c != "UNKNOWN"
        )
        recommendations.append(
            f"Multi-currency data detected ({', '.join(sorted(currencies))}). "
            f"Breakdown: {ccy_detail}. "
            "Use convert_and_summarise_currency() before aggregating spend — "
            "rows in non-primary currencies will be EXCLUDED from totals if no rate is provided, "
            "which will cause the reported spend total to be lower than the actual total."
        )
    if duplicates > 0:
        recommendations.append(
            f"{duplicates} suspected duplicate rows detected. "
            "Review before analysis to avoid double-counting spend."
        )
    if date_range["period_months"] and date_range["period_months"] < 11:
        recommendations.append(
            f"Data covers only {date_range['period_months']:.1f} months. "
            "Annualised figures will be estimates — label them clearly."
        )
    if "po_number" not in detected_fields:
        recommendations.append(
            "PO number field not found — PO compliance rate cannot be calculated. "
            "If PO data exists in your ERP, include it for a more complete analysis."
        )
    if quality_score < 60:
        recommendations.append(
            f"Overall quality score is {quality_score}/100 — below the 60-point threshold for reliable analysis. "
            "Address the issues above before proceeding."
        )

    return {
        "total_rows": len(rows),
        "total_spend_face_value": round(total_spend, 2),
        "total_spend_note": (
            "Face value only — currencies NOT converted. "
            "Call convert_and_summarise_currency() to get a reliable single-currency total."
            if len(currencies) > 1 else "Single currency detected — total is reliable."
        ),
        "currency_codes_found": sorted(currencies),
        "currency_breakdown": {
            c: {"count": v["count"], "total_face_value": v["total_face_value"],
                "pct_of_rows": round(v["count"] / len(rows) * 100, 1)}
            for c, v in sorted(currency_breakdown.items(),
                                key=lambda x: x[1]["count"], reverse=True)
            if c != "UNKNOWN"
        },
        "is_multicurrency": len(currencies) > 1,
        "date_range": date_range,
        "detected_fields": detected_fields,
        "missing_fields": [f for f in expected_fields if f not in detected_fields],
        "field_completeness": field_completeness,
        "duplicate_count": duplicates,
        "quality_score": quality_score,
        "recommendations": recommendations
    }


def _try_parse_date(raw: str) -> Optional[datetime]:
    """Try common date formats. Returns None if unparseable."""
    formats = [
        "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y",
        "%d %b %Y", "%d %B %Y", "%Y%m%d", "%d.%m.%Y"
    ]
    for fmt in formats:
        try:
            return datetime.strptime(raw.strip(), fmt)
        except (ValueError, AttributeError):
            continue
    return None


# ---------------------------------------------------------------------------
# Supplier name normalisation
# ---------------------------------------------------------------------------

def deduplicate_suppliers(supplier_names: list) -> dict:
    """
    Identify groups of supplier name variants that likely refer to the same entity.

    Returns a dict mapping each raw name to a normalised name:
      {"Microsoft Ltd": "Microsoft", "MSFT": "Microsoft", ...}

    This function produces CANDIDATE mappings only — Claude must present
    these to the user for confirmation before applying them.

    Gotchas:
      - Never auto-apply deduplication without user confirmation. A match
        that looks obvious (e.g. "IBM" and "IBM UK") may refer to different
        contracting entities with different terms.
      - Short names (3 chars or fewer) are high false-positive risk — flag
        these as "review required" rather than auto-suggesting a match.
      - Legal suffixes to strip for comparison:
        Ltd, Limited, LLC, Inc, Corp, GmbH, SA, PLC, LLP, BV, AG, NV
      - Trading names vs legal names: a supplier's trading name may be
        completely different from their legal name. The user's finance team
        will know which is which.
    """
    legal_suffixes = r'\b(?:Ltd|Limited|LLC|Inc|Corp|GmbH|SA|PLC|LLP|BV|AG|NV|Pty|Co\.?)\b\.?'

    def normalise_for_comparison(name: str) -> str:
        n = name.upper().strip()
        n = re.sub(legal_suffixes, "", n, flags=re.IGNORECASE).strip()
        n = re.sub(r'[^\w\s]', '', n)
        n = re.sub(r'\s+', ' ', n).strip()
        return n

    normalised = {name: normalise_for_comparison(name) for name in supplier_names}

    # Group by normalised form
    groups = {}
    for raw, norm in normalised.items():
        if norm not in groups:
            groups[norm] = []
        groups[norm].append(raw)

    # Build mapping: raw → suggested canonical name
    mapping = {}
    for norm_key, variants in groups.items():
        if len(variants) == 1:
            mapping[variants[0]] = variants[0]  # No change needed
        else:
            # Pick the shortest name as canonical (usually the trading name)
            canonical = min(variants, key=lambda x: len(x))
            for v in variants:
                mapping[v] = canonical

    return mapping


def convert_currency(amount: float, from_currency: str, to_currency: str,
                     rate: float) -> float:
    """
    Convert a spend amount using a provided exchange rate.

    Gotchas:
      - Never hardcode exchange rates. Always receive them as a parameter.
      - Always state in the output report which rate was used and its date.
      - If from_currency == to_currency, return amount unchanged (don't apply rate).
    """
    if from_currency.upper() == to_currency.upper():
        return amount
    return round(amount * rate, 2)


def convert_and_summarise_currency(rows: list,
                                   target_currency: str,
                                   exchange_rates: dict,
                                   amount_col: str = None,
                                   currency_col: str = None) -> dict:
    """
    Convert all spend rows to a single target currency and produce a full
    audit trail showing exactly what happened to every currency group.

    This function exists specifically to make the spend total transparent —
    so a £14.6M vs £18.2M discrepancy can be traced to its root cause.

    Parameters:
      rows             — list of raw row dicts from csv.DictReader
      target_currency  — target currency code, e.g. "GBP"
      exchange_rates   — {currency_code: rate_to_target}, e.g. {"USD": 0.79, "EUR": 0.86}
                         Do NOT include the target currency itself (it will be treated as 1.0)
      amount_col       — column name for the amount field (auto-detected if None)
      currency_col     — column name for the currency field (auto-detected if None)

    Returns a dict:
      - converted_rows: list — same rows with two new fields:
            amount_original   (original numeric amount)
            amount_converted  (amount in target_currency)
            currency_original (original currency code)
            conversion_rate   (rate applied; 1.0 if same currency)
            conversion_status "converted" | "already_target" | "excluded_no_rate" | "excluded_no_amount"
      - summary: dict with:
            target_currency
            exchange_rates_used        {currency: rate}
            rows_by_currency           {currency: {count, total_original, total_converted}}
            rows_excluded              {currency: {count, total_original, reason}}
            grand_total_converted      float — total spend in target currency AFTER conversion
            grand_total_before_exclusion float — what the total would be if excluded rows used face value
            exclusion_impact           float — spend lost due to missing rates (the "missing" amount)
            rate_date_note             str — always "Exchange rates must be provided with their reference date"
            recommendations            list of str

    Gotchas:
      - This is the primary tool for diagnosing spend total gaps.
        If total_spend in the report does not match the user's expectation,
        run this function and show the summary before anything else.
      - exchange_rates must be provided by the user or retrieved from a live source.
        Never fabricate rates. If none are provided and the data is multi-currency,
        surface exclusion_impact prominently as a "CAUTION: excluded spend" figure.
      - Rows with no currency value are assumed to be in target_currency.
      - Rows with a currency not in exchange_rates AND not equal to target_currency
        are excluded from the total — they go into rows_excluded.
        This is the most common cause of spend total gaps.
    """
    # Auto-detect column names if not provided
    field_aliases = {
        "amount":   ["amount", "value", "total", "net amount", "spend", "payment amount", "invoice amount",
                     "amount (gbp)", "amount_gbp"],
        "currency": ["currency", "currency code", "ccy", "iso currency"]
    }

    if rows:
        sample_keys = [k.lower().strip() for k in rows[0].keys()]
        if amount_col is None:
            for alias in field_aliases["amount"]:
                if alias in sample_keys:
                    amount_col = [k for k in rows[0].keys() if k.lower().strip() == alias][0]
                    break
        if currency_col is None:
            for alias in field_aliases["currency"]:
                if alias in sample_keys:
                    currency_col = [k for k in rows[0].keys() if k.lower().strip() == alias][0]
                    break

    target = target_currency.upper()
    rates = {k.upper(): v for k, v in (exchange_rates or {}).items()}
    rates[target] = 1.0  # Target currency always converts at 1.0

    converted_rows = []
    currency_stats = {}   # {currency: {count, total_original, total_converted}}
    excluded_stats = {}   # {currency: {count, total_original, reason}}
    grand_total = 0.0
    grand_total_face_value = 0.0  # What it would be if we used face value for excluded rows

    for row in rows:
        r = dict(row)  # Don't mutate original

        # Parse amount
        raw_amount = r.get(amount_col, "") if amount_col else ""
        try:
            amount_orig = abs(float(
                str(raw_amount).replace(",", "").replace("£", "").replace("$", "").replace("€", "")
            ))
        except (ValueError, TypeError):
            r["amount_original"] = 0.0
            r["amount_converted"] = 0.0
            r["currency_original"] = ""
            r["conversion_rate"] = 1.0
            r["conversion_status"] = "excluded_no_amount"
            converted_rows.append(r)
            excl = excluded_stats.setdefault("NO_AMOUNT", {"count": 0, "total_original": 0.0, "reason": "Could not parse amount"})
            excl["count"] += 1
            continue

        # Parse currency
        ccy = str(r.get(currency_col, "") if currency_col else "").strip().upper()
        if not ccy:
            ccy = target  # Assume target currency if not specified

        grand_total_face_value += amount_orig

        if ccy in rates:
            rate = rates[ccy]
            amount_conv = round(amount_orig * rate, 2)
            status = "already_target" if ccy == target else "converted"

            r["amount_original"] = amount_orig
            r["amount_converted"] = amount_conv
            r["currency_original"] = ccy
            r["conversion_rate"] = rate
            r["conversion_status"] = status

            grand_total += amount_conv
            cs = currency_stats.setdefault(ccy, {"count": 0, "total_original": 0.0, "total_converted": 0.0})
            cs["count"] += 1
            cs["total_original"] = round(cs["total_original"] + amount_orig, 2)
            cs["total_converted"] = round(cs["total_converted"] + amount_conv, 2)
        else:
            # No rate available — exclude from total
            r["amount_original"] = amount_orig
            r["amount_converted"] = None
            r["currency_original"] = ccy
            r["conversion_rate"] = None
            r["conversion_status"] = "excluded_no_rate"

            excl = excluded_stats.setdefault(ccy, {
                "count": 0, "total_original": 0.0,
                "reason": f"No exchange rate provided for {ccy} → {target}"
            })
            excl["count"] += 1
            excl["total_original"] = round(excl["total_original"] + amount_orig, 2)

        converted_rows.append(r)

    exclusion_face_value = sum(v["total_original"] for v in excluded_stats.values()
                               if v.get("reason", "").startswith("No exchange rate"))

    recommendations = []
    if excluded_stats:
        for ccy, excl in excluded_stats.items():
            if "No exchange rate" in excl.get("reason", ""):
                recommendations.append(
                    f"CAUTION: {excl['count']} rows in {ccy} ({excl['total_original']:,.0f} {ccy} face value) "
                    f"were EXCLUDED from the {target} total because no exchange rate was provided. "
                    f"Provide a rate for {ccy} → {target} to include this spend."
                )
    if len(currency_stats) > 1:
        converted_ccys = [c for c in currency_stats if c != target]
        recommendations.append(
            f"Converted {', '.join(converted_ccys)} to {target} using provided rates: "
            + ", ".join(f"{c}={rates[c]}" for c in converted_ccys if c in rates)
            + ". Verify these rates against your finance team's FX policy."
        )

    return {
        "converted_rows": converted_rows,
        "summary": {
            "target_currency": target,
            "exchange_rates_used": {k: v for k, v in rates.items() if k != target},
            "rows_by_currency": currency_stats,
            "rows_excluded": excluded_stats,
            "grand_total_converted": round(grand_total, 2),
            "grand_total_face_value": round(grand_total_face_value, 2),
            "exclusion_impact": round(exclusion_face_value, 2),
            "rate_date_note": "Exchange rates must be provided with their reference date for audit purposes.",
            "recommendations": recommendations
        }
    }


# ---------------------------------------------------------------------------
# Annualisation
# ---------------------------------------------------------------------------

def annualise_spend(total_spend: float, period_months: float) -> dict:
    """
    Annualise partial-year spend.

    Returns:
      - annualised_spend: float
      - period_months: float
      - annualisation_factor: float
      - caveat: str — always include in reports

    Gotchas:
      - Annualisation assumes spend is evenly distributed across the year.
        This is often wrong (Q4 spike in professional services, Q1 spike in
        marketing budgets). Flag this assumption explicitly.
      - If period is <3 months, annualisation is highly unreliable — warn the
        user and recommend waiting for more data.
    """
    if period_months <= 0:
        return {"error": "Invalid period_months"}

    factor = 12 / period_months
    annualised = round(total_spend * factor, 2)

    caveat = (
        f"Annualised estimate based on {period_months:.1f} months of data "
        f"(×{factor:.2f} annualisation factor). "
        "Assumes even spend distribution — actual full-year spend may differ."
    )
    if period_months < 3:
        caveat += " WARNING: Less than 3 months of data — annualised figure is highly unreliable."

    return {
        "annualised_spend": annualised,
        "actual_spend": total_spend,
        "period_months": period_months,
        "annualisation_factor": round(factor, 3),
        "caveat": caveat
    }

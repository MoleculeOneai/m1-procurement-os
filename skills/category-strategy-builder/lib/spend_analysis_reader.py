"""
spend_analysis_reader.py — Spend Analysis Output Reader
Part of the Molecule One Category Strategy Builder skill.

Reads structured outputs from the spend-analyzer skill and transforms them
into the data model needed for Kraljic segmentation and opportunity analysis.

Usage:
    from lib.spend_analysis_reader import load_spend_output, get_top_categories

Gotchas:
    - The spend-analyzer output format may evolve. Always validate the keys
      before processing. Use the validate_spend_output() function first.
    - Category names from spend-analyzer may not match the user's taxonomy.
      Always normalise before building the Kraljic matrix.
    - Multi-year outputs exist — always extract the most recent year unless
      the user specifically asks for a trend view.
"""

import json
import csv
import os
import sys
from pathlib import Path
from typing import Optional


EXPECTED_KEYS = {"category", "spend_amount", "supplier_count", "transaction_count"}


def load_spend_output(filepath: str) -> list[dict]:
    """
    Load and parse a spend-analyzer output file.

    Accepts:
      - JSON array (preferred — spend-analyzer native format)
      - CSV with headers: category, spend_amount, supplier_count, transaction_count

    Returns a list of category dicts with at minimum:
      { category, spend_amount, supplier_count, transaction_count }

    Gotchas:
      - JSON files from spend-analyzer may include nested structures.
        This function flattens one level only. If the structure is deeper,
        tell the user and ask them to export a flat summary.
      - CSV exports from ERP systems often have encoding issues (BOM, Latin-1).
        This function tries UTF-8 first, then falls back to Latin-1.
      - Negative spend amounts indicate credits or reversals. Flag these
        and exclude from totals — do not silently include them.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Spend output file not found: {filepath}")

    suffix = path.suffix.lower()

    if suffix == ".json":
        data = _load_json(path)
    elif suffix in (".csv", ".tsv"):
        delimiter = "\t" if suffix == ".tsv" else ","
        data = _load_csv(path, delimiter)
    else:
        raise ValueError(f"Unsupported file format: {suffix}. Expected .json or .csv")

    # Validate and clean
    validated = []
    skipped = []
    for row in data:
        if not _has_required_keys(row):
            skipped.append(row)
            continue
        row = _coerce_types(row)
        if row["spend_amount"] < 0:
            row["_flag"] = "NEGATIVE_SPEND — likely a credit or reversal; excluded from analysis"
            skipped.append(row)
            continue
        validated.append(row)

    if skipped:
        print(
            f"[spend_analysis_reader] WARNING: {len(skipped)} row(s) skipped "
            f"(missing keys or negative spend). Review excluded rows before proceeding.",
            file=sys.stderr
        )

    return validated


def _load_json(path: Path) -> list[dict]:
    """Load JSON. Handles both array-of-dicts and wrapped {'data': [...]} format."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        for key in ("data", "categories", "results", "rows"):
            if key in raw and isinstance(raw[key], list):
                return raw[key]
    raise ValueError(
        "Unrecognised JSON structure. Expected an array of objects or "
        "a dict with a 'data', 'categories', 'results', or 'rows' key."
    )


def _load_csv(path: Path, delimiter: str) -> list[dict]:
    """Load CSV with UTF-8 fallback to Latin-1."""
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            with open(path, encoding=encoding, newline="") as f:
                reader = csv.DictReader(f, delimiter=delimiter)
                rows = [dict(row) for row in reader]
                # Normalise header names: strip whitespace, lowercase
                rows = [
                    {k.strip().lower().replace(" ", "_"): v.strip()
                     for k, v in row.items()}
                    for row in rows
                ]
                return rows
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Could not decode {path} — tried UTF-8 and Latin-1")


def _has_required_keys(row: dict) -> bool:
    return EXPECTED_KEYS.issubset(row.keys())


def _coerce_types(row: dict) -> dict:
    """Coerce spend_amount, supplier_count, transaction_count to numeric types."""
    try:
        row["spend_amount"] = float(str(row["spend_amount"]).replace(",", "").replace("$", "").replace("£", "").replace("€", "").strip())
    except (ValueError, TypeError):
        row["spend_amount"] = 0.0

    for int_field in ("supplier_count", "transaction_count"):
        try:
            row[int_field] = int(str(row[int_field]).replace(",", "").strip())
        except (ValueError, TypeError):
            row[int_field] = 0

    return row


def validate_spend_output(data: list[dict]) -> dict:
    """
    Validate a loaded spend dataset and return a health report.

    Returns:
      {
        "total_categories": int,
        "total_spend": float,
        "missing_fields": list of str,
        "warnings": list of str,
        "is_valid": bool
      }

    Gotchas:
      - A valid file with bad data (e.g. all spend = 0) will pass this check.
        Always review the summary figures with the user before proceeding.
    """
    report = {
        "total_categories": len(data),
        "total_spend": sum(r.get("spend_amount", 0) for r in data),
        "missing_fields": [],
        "warnings": [],
        "is_valid": True
    }

    if not data:
        report["warnings"].append("Dataset is empty — nothing to analyse")
        report["is_valid"] = False
        return report

    # Check for missing optional but useful fields
    optional_fields = ["year", "department", "currency", "gl_code"]
    for field in optional_fields:
        if not any(field in row for row in data):
            report["missing_fields"].append(field)

    if report["total_spend"] == 0:
        report["warnings"].append("Total spend is zero — likely a data loading issue")
        report["is_valid"] = False

    # Check for duplicate category names
    names = [r.get("category", "") for r in data]
    duplicates = {n for n in names if names.count(n) > 1}
    if duplicates:
        report["warnings"].append(
            f"Duplicate category names detected: {duplicates}. "
            "Merge or deduplicate before running Kraljic analysis."
        )

    return report


def get_top_categories(data: list[dict], n: int = 20, min_spend: Optional[float] = None) -> list[dict]:
    """
    Return the top N categories by spend, optionally filtered by minimum spend.

    Gotchas:
      - Tail spend categories (very small) will inflate category counts
        without contributing meaningful analysis value. Use min_spend to filter.
      - Default n=20 covers most portfolios. For very large or very concentrated
        portfolios, adjust accordingly.
    """
    if min_spend is not None:
        data = [r for r in data if r["spend_amount"] >= min_spend]

    sorted_data = sorted(data, key=lambda r: r["spend_amount"], reverse=True)
    return sorted_data[:n]


def compute_spend_summary(data: list[dict]) -> dict:
    """
    Compute summary statistics for a spend dataset.

    Returns:
      {
        "total_spend": float,
        "category_count": int,
        "top_10_spend": float,
        "top_10_pct": float,
        "avg_spend_per_category": float,
        "tail_spend_count": int,       # categories <0.5% of total
        "tail_spend_amount": float
      }
    """
    if not data:
        return {}

    total = sum(r["spend_amount"] for r in data)
    sorted_data = sorted(data, key=lambda r: r["spend_amount"], reverse=True)

    top10 = sum(r["spend_amount"] for r in sorted_data[:10])
    tail_threshold = total * 0.005  # 0.5%
    tail_rows = [r for r in data if r["spend_amount"] < tail_threshold]

    return {
        "total_spend": total,
        "category_count": len(data),
        "top_10_spend": top10,
        "top_10_pct": round(top10 / total * 100, 1) if total > 0 else 0,
        "avg_spend_per_category": round(total / len(data), 2),
        "tail_spend_count": len(tail_rows),
        "tail_spend_amount": sum(r["spend_amount"] for r in tail_rows),
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python spend_analysis_reader.py <filepath>")
        sys.exit(1)

    filepath = sys.argv[1]
    data = load_spend_output(filepath)
    validation = validate_spend_output(data)
    summary = compute_spend_summary(data)

    print(json.dumps({"validation": validation, "summary": summary}, indent=2))

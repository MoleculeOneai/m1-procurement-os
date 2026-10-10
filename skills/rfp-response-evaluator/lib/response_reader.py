"""
response_reader.py — RFP Response Evaluator
Molecule One Claude Plugin Suite

Reads and extracts content from supplier response files in a folder.
Supports PDF, .docx, and .xlsx formats. Handles mixed-format folders.

GOTCHAS:
- Scanned PDFs will return empty or garbled text — detect and flag immediately.
- One supplier may have multiple files (e.g. narrative .docx + pricing .xlsx). Always confirm mapping with user.
- File names are unreliable for identifying suppliers — confirm mapping explicitly.
- Large Excel files may have irrelevant tabs — only extract tabs that contain response data.
- Do not silently skip unreadable files — always flag them to the user.

Usage:
    reader = ResponseReader(folder_path="path/to/responses/")
    inventory = reader.inventory()
    content = reader.extract(supplier="Supplier A", files=["file1.pdf", "file2.xlsx"])
"""

from __future__ import annotations

import os
import json
from dataclasses import dataclass, field, asdict
from typing import Optional
from pathlib import Path


@dataclass
class SupplierFile:
    """Represents a single file from a supplier's response package."""
    filename: str
    supplier_name: str
    file_type: str          # "pdf", "docx", "xlsx", "unknown"
    file_role: str          # "narrative", "pricing", "technical", "other", "unassigned"
    readable: bool          # False if scanned PDF or corrupt
    warning: Optional[str] = None
    extracted_text: Optional[str] = None
    extracted_data: Optional[dict] = None   # for structured xlsx content


@dataclass
class FolderInventory:
    """Inventory of all files found in the supplier response folder."""
    folder_path: str
    files: list[SupplierFile] = field(default_factory=list)
    suppliers_identified: list[str] = field(default_factory=list)
    unassigned_files: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    def save(self, output_path: str) -> None:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: str) -> "FolderInventory":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        inv = cls(folder_path=data["folder_path"])
        inv.files = [SupplierFile(**sf) for sf in data.get("files", [])]
        inv.suppliers_identified = data.get("suppliers_identified", [])
        inv.unassigned_files = data.get("unassigned_files", [])
        inv.warnings = data.get("warnings", [])
        return inv


class ResponseReader:
    """
    Read and extract content from supplier response files.

    Modes:
        inventory   — scan folder and list all files with type detection
        extract     — extract text/data from specified files for a named supplier
    """

    SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".xlsx", ".xls"}

    def __init__(self, folder_path: str):
        self.folder_path = Path(folder_path)

    def inventory(self) -> FolderInventory:
        """
        Scan the folder and produce an inventory of all files.
        Detects file types. Flags unreadable files. Does NOT assign suppliers
        automatically — supplier assignment must be confirmed by the user.

        GOTCHA: Do not infer supplier names from filenames. File names like
        "response_v2_FINAL.pdf" give no reliable supplier signal.
        """
        inv = FolderInventory(folder_path=str(self.folder_path))

        if not self.folder_path.exists():
            raise FileNotFoundError(f"Folder not found: {self.folder_path}")

        for file in sorted(self.folder_path.iterdir()):
            if file.is_file() and file.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                sf = self._classify_file(file)
                inv.files.append(sf)
                if sf.warning:
                    inv.warnings.append(f"{file.name}: {sf.warning}")
                if sf.file_role == "unassigned":
                    inv.unassigned_files.append(file.name)

        if not inv.files:
            inv.warnings.append(
                "No supported files found in folder. "
                "Supported formats: PDF, .docx, .xlsx"
            )

        return inv

    def _classify_file(self, file: Path) -> SupplierFile:
        """Detect file type and basic readability."""
        ext = file.suffix.lower()
        file_type_map = {".pdf": "pdf", ".docx": "docx", ".xlsx": "xlsx", ".xls": "xlsx"}
        file_type = file_type_map.get(ext, "unknown")

        sf = SupplierFile(
            filename=file.name,
            supplier_name="",       # must be assigned by user
            file_type=file_type,
            file_role="unassigned",
            readable=True,
        )

        # Basic readability check
        try:
            size_bytes = file.stat().st_size
            if size_bytes == 0:
                sf.readable = False
                sf.warning = "File is empty (0 bytes)."
            elif size_bytes > 100_000_000:  # 100MB sanity check
                sf.warning = "File is very large (>100MB). Extraction may be slow."
        except OSError as e:
            sf.readable = False
            sf.warning = f"Cannot access file: {e}"

        return sf

    def extract(
        self,
        supplier: str,
        files: list[str],
        mode: str = "full",
    ) -> dict:
        """
        Extract content from a supplier's files.

        Args:
            supplier:   Supplier name (for labelling output)
            files:      List of filenames to read (must be in self.folder_path)
            mode:       "full" — extract all content
                        "pricing" — extract pricing/commercial data only
                        "sections" — extract section-by-section narrative

        Returns:
            dict with keys: supplier, files_read, extracted_content, warnings

        GOTCHA: If extracted text is empty or <50 chars, the file is likely
        a scanned PDF. Flag this — do not pass empty content to the scorer.
        """
        result = {
            "supplier": supplier,
            "files_read": [],
            "extracted_content": {},
            "warnings": [],
        }

        for filename in files:
            file_path = self.folder_path / filename
            if not file_path.exists():
                result["warnings"].append(
                    f"File not found: {filename}. Cannot extract content."
                )
                continue

            ext = file_path.suffix.lower()
            try:
                if ext == ".pdf":
                    text = self._extract_pdf(file_path)
                elif ext == ".docx":
                    text = self._extract_docx(file_path)
                elif ext in (".xlsx", ".xls"):
                    text = self._extract_xlsx(file_path)
                else:
                    result["warnings"].append(f"Unsupported file type: {filename}")
                    continue

                if not text or len(text.strip()) < 50:
                    result["warnings"].append(
                        f"WARNING — {filename}: Extracted content is empty or very short. "
                        "This file may be a scanned PDF or password-protected. "
                        "Request a text-based version from the supplier."
                    )
                    result["extracted_content"][filename] = ""
                else:
                    result["extracted_content"][filename] = text
                    result["files_read"].append(filename)

            except Exception as e:
                result["warnings"].append(
                    f"ERROR extracting {filename}: {e}. "
                    "File may be corrupt or password-protected."
                )

        return result

    def _extract_pdf(self, file_path: Path) -> str:
        """
        Extract text from a PDF. Uses pypdf if available.
        GOTCHA: Returns empty string for scanned PDFs — caller must detect and flag.
        """
        try:
            from pypdf import PdfReader  # type: ignore
            reader = PdfReader(str(file_path))
            text = "\n".join(
                page.extract_text() or "" for page in reader.pages
            )
            return text.strip()
        except ImportError:
            return (
                f"[PDF extraction requires pypdf — install with: "
                f"pip install pypdf --break-system-packages. "
                f"File: {file_path.name}]"
            )

    def _extract_docx(self, file_path: Path) -> str:
        """Extract text from a Word document."""
        try:
            from docx import Document  # type: ignore
            doc = Document(str(file_path))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            # Also extract tables
            for table in doc.tables:
                for row in table.rows:
                    row_text = " | ".join(
                        cell.text.strip() for cell in row.cells if cell.text.strip()
                    )
                    if row_text:
                        paragraphs.append(row_text)
            return "\n".join(paragraphs)
        except ImportError:
            return (
                f"[Word extraction requires python-docx — install with: "
                f"pip install python-docx --break-system-packages. "
                f"File: {file_path.name}]"
            )

    def _extract_xlsx(self, file_path: Path) -> str:
        """
        Extract data from an Excel file. Returns structured text representation.
        GOTCHA: Only extracts visible/non-empty cells. Skips hidden sheets by default.
        """
        try:
            import openpyxl  # type: ignore
            wb = openpyxl.load_workbook(str(file_path), data_only=True)
            output = []
            for sheet_name in wb.sheetnames:
                ws = wb[sheet_name]
                if ws.sheet_state == "hidden":
                    continue
                output.append(f"--- Sheet: {sheet_name} ---")
                for row in ws.iter_rows(values_only=True):
                    row_values = [str(cell) if cell is not None else "" for cell in row]
                    if any(v.strip() for v in row_values):
                        output.append(" | ".join(row_values))
            return "\n".join(output)
        except ImportError:
            return (
                f"[Excel extraction requires openpyxl — install with: "
                f"pip install openpyxl --break-system-packages. "
                f"File: {file_path.name}]"
            )


# --- __main__ demo ---
if __name__ == "__main__":
    import tempfile

    print("=== ResponseReader Demo ===\n")

    # Create a temp folder with dummy files
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create dummy files
        for name in ["SupplierA_Response.docx", "SupplierB_Proposal.pdf", "SupplierC_Pricing.xlsx"]:
            (Path(tmpdir) / name).write_bytes(b"dummy")

        reader = ResponseReader(folder_path=tmpdir)
        inv = reader.inventory()

        print(f"Folder: {inv.folder_path}")
        print(f"Files found: {len(inv.files)}")
        for sf in inv.files:
            print(f"  [{sf.file_type.upper()}] {sf.filename} — role: {sf.file_role} — readable: {sf.readable}")
        if inv.warnings:
            print(f"\nWarnings:")
            for w in inv.warnings:
                print(f"  ⚠ {w}")

    print("\nResponseReader demo complete.")

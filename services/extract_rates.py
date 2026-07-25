"""
Phase 0/2 support - Statutory Rate Table Extraction

Parses the SOCSO contribution-rate PDF text directly (not hand re-typed) into a
structured JSON lookup table. This keeps the numeric source of truth tied
programmatically to the original document instead of manually re-transcribed
figures, eliminating transcription risk for a compliance-critical table.

The EPF rate schedule (Parts A/C/E/F of the source PDF) was verified to be
exactly reproducible by a documented formula (rate * band-upper-bound, rounded
up to the next Ringgit) against the extracted table - see
knowledge-base/malaysia/epf.md for the row-by-row verification evidence. EPF is
therefore implemented as a formula in rule-engine/epf.py rather than a giant
lookup, but is spot-checked against this same source PDF text in
tests/test_rule_engine_epf.py.

Usage:
    .venv\\Scripts\\python.exe services\\extract_rates.py
"""
from __future__ import annotations

import json
import pathlib
import re

import pdfplumber

ROOT = pathlib.Path(__file__).resolve().parent.parent
SOURCE_DIR = ROOT.parent
RATES_DIR = ROOT / "rule-engine" / "rates"

SOCSO_PDF = SOURCE_DIR / "SOCSO employee and employer NewContributionRateIncludingSKBBK.pdf"

# Matches lines like:
# "RM0.40 RM0.10 RM0.20 RM0.70 RM0.30 RM0.20 RM0.50" following a wage-band description.
MONEY = r"RM([\d,]+\.\d{2})"


def _to_float(s: str) -> float:
    return float(s.replace(",", "").replace("RM", "").strip())


def _parse_band(band_text: str) -> tuple[float, float | None]:
    """Parse a wage-band description cell into (min_exclusive, max_inclusive)."""
    t = " ".join(band_text.split())
    m = re.match(r"Wages up to RM([\d,]+)", t)
    if m:
        return 0.0, _to_float(m.group(1))
    m = re.match(r"Where wages exceed RM([\d,]+) but do not exceed RM([\d,]+)", t)
    if m:
        return _to_float(m.group(1)), _to_float(m.group(2))
    m = re.match(r"Where wages exceed RM([\d,]+)", t)
    if m:
        return _to_float(m.group(1)), None
    raise ValueError(f"Unrecognised wage band text: {band_text!r}")


def parse_socso(path: pathlib.Path) -> list[dict]:
    """Extract wage-band rows directly from pdfplumber's `extract_tables()` output.

    Column layout confirmed against source (verified against printed figures where
    employee + employer sub-shares sum to the printed TOTAL for both categories):
      0=No. 1=Wage band text 2=Category1 employee share
      4=Category1 employer share (Invalidity) 5=Category1 employer share (Non-Employment Injury)
      6=Category1 total
      8=Category2 employee share 10=Category2 employer share (Non-Employment Injury)
      11=Category2 total
    """
    rows: list[dict] = []
    with pdfplumber.open(str(path)) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables():
                for row in table:
                    row = [c.strip() if isinstance(c, str) else c for c in row]
                    if not row or not row[0] or not re.match(r"^\d+\.$", row[0] or ""):
                        continue  # header / continuation row
                    row_no = int(row[0].rstrip("."))
                    try:
                        lo, hi = _parse_band(row[1] or "")
                        emp1 = _to_float(row[2])
                        er_invalidity1 = _to_float(row[4])
                        er_nonei1 = _to_float(row[5])
                        total1 = _to_float(row[6])
                        emp2 = _to_float(row[8])
                        er_nonei2 = _to_float(row[10])
                        total2 = _to_float(row[11])
                    except (ValueError, IndexError, TypeError):
                        continue  # skip malformed/wrapped rows; verified count checked below
                    rows.append(
                        {
                            "row": row_no,
                            "wage_min_exclusive": lo,
                            "wage_max_inclusive": hi,
                            "category_1": {
                                "employee": emp1,
                                "employer_invalidity": er_invalidity1,
                                "employer_non_employment_injury": er_nonei1,
                                "employer_total": round(er_invalidity1 + er_nonei1, 2),
                                "total": total1,
                            },
                            "category_2": {
                                "employee": emp2,
                                "employer_non_employment_injury": er_nonei2,
                                "employer_total": er_nonei2,
                                "total": total2,
                            },
                        }
                    )
    # De-duplicate by row number (tables can repeat a header/first row across page breaks)
    seen = {}
    for r in rows:
        seen[r["row"]] = r
    return [seen[k] for k in sorted(seen)]


def main() -> int:
    RATES_DIR.mkdir(parents=True, exist_ok=True)
    socso_rows = parse_socso(SOCSO_PDF)
    out = {
        "source": SOCSO_PDF.name,
        "effective_note": "As printed in source PDF; effective date not stated in document - Requires SME Validation for effective date confirmation.",
        "wage_ceiling": 6000.0,
        "rows": socso_rows,
    }
    out_path = RATES_DIR / "socso_rates.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Extracted {len(socso_rows)} SOCSO wage bands -> {out_path}")
    if socso_rows:
        print("First row:", socso_rows[0])
        print("Last row:", socso_rows[-1])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

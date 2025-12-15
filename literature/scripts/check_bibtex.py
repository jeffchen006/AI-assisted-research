#!/usr/bin/env python3
"""Validate BibTeX entries for required metadata.

Checks (per entry):
- title
- author
- year
- where published (booktitle/journal or venue)

Usage
  python literature/scripts/check_bibtex.py path/to/library.bib
  python literature/scripts/check_bibtex.py path/to/library.bib --out report.json

Exit codes
- 0: all entries pass required fields
- 2: one or more entries missing required fields
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence

try:
    import bibtexparser
except ModuleNotFoundError as e:  # noqa: BLE001
    print(
        "Missing dependency. Install with: python -m pip install -r requirements.txt\n"
        "(Required package: bibtexparser)",
        file=sys.stderr,
    )
    raise


REQUIRED_ANY_OF = {
    "where_published": ["booktitle", "journal", "venue"],
}

REQUIRED_FIELDS = ["title", "author", "year"]


@dataclass(frozen=True)
class Finding:
    key: str
    entry_type: str
    missing: List[str]


def _get_str(entry: Dict[str, str], field: str) -> str:
    v = entry.get(field, "")
    if v is None:
        return ""
    return str(v).strip()


def _missing_fields(entry: Dict[str, str]) -> List[str]:
    missing: List[str] = []

    for f in REQUIRED_FIELDS:
        if not _get_str(entry, f):
            missing.append(f)

    for label, options in REQUIRED_ANY_OF.items():
        if not any(_get_str(entry, opt) for opt in options):
            missing.append(label + "(" + "|".join(options) + ")")

    return missing


def validate_bibtex(path: Path) -> List[Finding]:
    bib_text = path.read_text(encoding="utf-8")
    bib_db = bibtexparser.loads(bib_text)

    findings: List[Finding] = []
    for entry in bib_db.entries:
        key = entry.get("ID", "<missing-key>")
        entry_type = entry.get("ENTRYTYPE", "<missing-type>")
        missing = _missing_fields(entry)
        if missing:
            findings.append(Finding(key=key, entry_type=entry_type, missing=missing))

    return findings


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Validate BibTeX required metadata fields.")
    p.add_argument("bib", type=Path, help="Path to .bib file")
    p.add_argument("--out", type=Path, default=None, help="Write JSON report to this path")
    args = p.parse_args(argv)

    if not args.bib.exists():
        print(f"BibTeX file not found: {args.bib}", file=sys.stderr)
        return 1

    findings = validate_bibtex(args.bib)

    report = {
        "file": str(args.bib),
        "total_entries": None,
        "invalid_entries": len(findings),
        "findings": [
            {"key": f.key, "type": f.entry_type, "missing": f.missing}
            for f in findings
        ],
    }

    # total_entries is available via bibtexparser but not stored above; compute cheaply
    try:
        bib_db = bibtexparser.loads(args.bib.read_text(encoding="utf-8"))
        report["total_entries"] = len(bib_db.entries)
    except Exception:  # noqa: BLE001
        report["total_entries"] = None

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if findings:
        print(f"Found {len(findings)} invalid BibTeX entries:")
        for f in findings:
            print(f"- {f.key} ({f.entry_type}): missing {', '.join(f.missing)}")
        return 2

    print("All BibTeX entries have required fields.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

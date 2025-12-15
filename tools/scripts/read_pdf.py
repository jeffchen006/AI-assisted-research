#!/usr/bin/env python3
"""Extract text from a PDF.

This is a shared tool (used by literature/research/review workflows).

Usage
  python tools/scripts/read_pdf.py path/to/paper.pdf
  python tools/scripts/read_pdf.py path/to/paper.pdf --out notes.txt
  python tools/scripts/read_pdf.py path/to/paper.pdf --pages 1:5

Notes
- PDF text extraction quality depends on how the PDF is encoded.
- Scanned PDFs (images) require OCR; this tool does NOT do OCR.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional, Sequence, Tuple

try:
    from pypdf import PdfReader
except ModuleNotFoundError:  # noqa: BLE001
    print(
        "Missing dependency. Install with: python -m pip install -r requirements.txt\n"
        "(Required package: pypdf)",
        file=sys.stderr,
    )
    raise


def _parse_pages(pages: str) -> Tuple[Optional[int], Optional[int]]:
    if not pages:
        return None, None
    if ":" not in pages:
        p = int(pages)
        return p, p
    start_s, end_s = pages.split(":", 1)
    start = int(start_s) if start_s else None
    end = int(end_s) if end_s else None
    return start, end


def extract_text(pdf_path: Path, start_page: Optional[int], end_page: Optional[int]) -> str:
    reader = PdfReader(str(pdf_path))
    n = len(reader.pages)

    # Pages are 1-indexed for CLI.
    start = 1 if start_page is None else max(1, start_page)
    end = n if end_page is None else min(n, end_page)

    chunks = []
    for i in range(start, end + 1):
        page = reader.pages[i - 1]
        text = page.extract_text() or ""
        chunks.append(f"\n\n===== Page {i} / {n} =====\n\n")
        chunks.append(text)

    return "".join(chunks).strip() + "\n"


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Extract text from a PDF (no OCR).")
    p.add_argument("pdf", type=Path, help="Path to PDF")
    p.add_argument("--out", type=Path, default=None, help="Write extracted text to file")
    p.add_argument("--pages", default="", help="Page range (1-indexed): N or START:END (open ends allowed)")
    args = p.parse_args(argv)

    if not args.pdf.exists():
        print(f"PDF not found: {args.pdf}", file=sys.stderr)
        return 1

    start, end = _parse_pages(args.pages)
    text = extract_text(args.pdf, start, end)

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
        return 0

    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

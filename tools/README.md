# Shared tools

Shared scripts used across folders.

## PDF reader (text extraction)

- Script: `tools/scripts/read_pdf.py`

Examples
- Print to stdout:
  - `python tools/scripts/read_pdf.py path/to/paper.pdf`
- Write to file:
  - `python tools/scripts/read_pdf.py path/to/paper.pdf --out literature/outputs/paper.txt`
- Page range:
  - `python tools/scripts/read_pdf.py path/to/paper.pdf --pages 1:5`

Limitations
- No OCR for scanned PDFs.

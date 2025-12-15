# Literature tools

This folder contains literature-review artifacts (prompts, checklists, scripts).

## Quick start

1) Install deps

- `python -m pip install -r requirements.txt`

2) Search a subtopic and keep only top CS conferences

- Edit venue allowlist: `literature/top_venues.txt`
- Run:

  `python literature/scripts/search_top_cs_conferences.py --query "<SUBTOPIC>" --years 2020:2025 --venues literature/top_venues.txt --out literature/outputs/<name> --limit 200 --download-pdfs --write-bibtex`

Outputs
- `literature/outputs/<name>.csv`
- `literature/outputs/<name>.jsonl`
- `literature/outputs/<name>.bib` (stub; verify!)
- `literature/outputs/<name>_pdfs/` (OA PDFs only)

## Google Scholar (supported API provider)

This repo supports Google Scholar search via **SerpAPI** (no direct scraping).

- Set `SERPAPI_API_KEY` and run:

  `python literature/scripts/search_google_scholar_serpapi.py --query "<SUBTOPIC>" --years 2020:2025 --venues literature/top_venues.txt --out literature/outputs/<name>_scholar --limit 100 --download-pdfs`

Notes
- Results are “candidate list” quality: verify venue/year/metadata.
- PDF downloads only happen when a direct PDF link is present.

## Validate BibTeX

- `python literature/scripts/check_bibtex.py path/to/library.bib`

## Prompts and checklists

- Prompts: `literature/prompts/`
- Checklists: `literature/checklists/`

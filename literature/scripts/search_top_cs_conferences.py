#!/usr/bin/env python3
"""Search for papers on a subtopic and filter to top CS conferences.

Why not scrape Google Scholar directly?
- Automated scraping of Google Scholar is brittle and may violate its Terms of Service.
- This script defaults to the Semantic Scholar public API, which is intended for programmatic use.

Outputs
- A CSV/JSONL of results with title/authors/year/venue/url/open-access-pdf.
- Optional BibTeX file.
- Optional PDF downloads when an open-access URL is available.

Example
  python literature/scripts/search_top_cs_conferences.py \
    --query "agentic workflows" \
    --years 2020:2025 \
    --venues literature/top_venues.txt \
    --out literature/outputs/agentic_workflows \
    --limit 200 \
    --download-pdfs
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple

try:
    import requests
except ModuleNotFoundError:  # noqa: BLE001
    print(
        "Missing dependency. Install with: python -m pip install -r requirements.txt\n"
        "(Required package: requests)",
        file=sys.stderr,
    )
    raise

SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1"


@dataclass(frozen=True)
class Paper:
    paper_id: str
    title: str
    year: Optional[int]
    venue: Optional[str]
    publication_types: List[str]
    authors: List[str]
    url: Optional[str]
    doi: Optional[str]
    open_access_pdf_url: Optional[str]


def _normalize_venue(venue: str) -> str:
    venue = venue.strip().lower()
    venue = re.sub(r"\s+", " ", venue)
    return venue


def load_venue_allowlist(path: Path) -> List[str]:
    if not path.exists():
        raise FileNotFoundError(f"Venue allowlist not found: {path}")

    venues: List[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        venues.append(_normalize_venue(line))
    return venues


def venue_matches(venue: Optional[str], allowlist: Sequence[str]) -> bool:
    if not venue:
        return False

    normalized = _normalize_venue(venue)

    # Allowlist entries can be full names ("neurips") or substrings ("conference on computer vision")
    for allowed in allowlist:
        if allowed in normalized:
            return True
    return False


def _parse_years(years: str) -> Tuple[Optional[int], Optional[int]]:
    if not years:
        return None, None
    if ":" not in years:
        y = int(years)
        return y, y
    start_s, end_s = years.split(":", 1)
    start = int(start_s) if start_s else None
    end = int(end_s) if end_s else None
    return start, end


def _year_in_range(year: Optional[int], start: Optional[int], end: Optional[int]) -> bool:
    if year is None:
        return False
    if start is not None and year < start:
        return False
    if end is not None and year > end:
        return False
    return True


def semantic_scholar_search(
    query: str,
    limit: int,
    fields: Sequence[str],
    api_key: Optional[str] = None,
    sleep_seconds: float = 0.5,
) -> Iterable[dict]:
    headers = {"User-Agent": "ai-assisted-research/1.0"}
    if api_key:
        headers["x-api-key"] = api_key

    # Semantic Scholar search returns up to 100 per call; we paginate using offset.
    # Docs: https://api.semanticscholar.org/api-docs/graph
    page_size = min(100, max(1, limit))
    offset = 0
    yielded = 0

    while yielded < limit:
        params = {
            "query": query,
            "limit": page_size,
            "offset": offset,
            "fields": ",".join(fields),
        }
        resp = requests.get(f"{SEMANTIC_SCHOLAR_API}/paper/search", params=params, headers=headers, timeout=30)
        if resp.status_code == 429:
            # Rate limited: back off a bit.
            time.sleep(max(2.0, sleep_seconds * 4))
            continue
        resp.raise_for_status()

        payload = resp.json()
        data = payload.get("data", [])
        if not data:
            return

        for item in data:
            yield item
            yielded += 1
            if yielded >= limit:
                return

        offset += len(data)
        time.sleep(sleep_seconds)


def parse_paper(item: dict) -> Paper:
    authors = [a.get("name", "").strip() for a in item.get("authors", []) if a.get("name")]
    publication_types = [p for p in (item.get("publicationTypes") or []) if isinstance(p, str)]

    open_access_pdf_url = None
    open_access_pdf = item.get("openAccessPdf")
    if isinstance(open_access_pdf, dict):
        open_access_pdf_url = open_access_pdf.get("url")

    external_ids = item.get("externalIds") or {}
    doi = None
    if isinstance(external_ids, dict):
        doi = external_ids.get("DOI")

    return Paper(
        paper_id=str(item.get("paperId") or ""),
        title=str(item.get("title") or "").strip(),
        year=item.get("year"),
        venue=(item.get("venue") or None),
        publication_types=publication_types,
        authors=authors,
        url=(item.get("url") or None),
        doi=doi,
        open_access_pdf_url=open_access_pdf_url,
    )


def safe_filename(s: str, max_len: int = 120) -> str:
    s = s.strip()
    s = re.sub(r"[^a-zA-Z0-9._-]+", "_", s)
    s = re.sub(r"_+", "_", s)
    return s[:max_len].strip("_") or "paper"


def download_pdf(url: str, out_path: Path, timeout: int = 60) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=timeout, headers={"User-Agent": "ai-assisted-research/1.0"}) as r:
        r.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 64):
                if chunk:
                    f.write(chunk)


def write_csv(papers: Sequence[Paper], out_csv: Path) -> None:
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "title",
                "authors",
                "year",
                "venue",
                "publication_types",
                "url",
                "doi",
                "open_access_pdf_url",
                "paper_id",
            ],
        )
        w.writeheader()
        for p in papers:
            w.writerow(
                {
                    "title": p.title,
                    "authors": "; ".join(p.authors),
                    "year": p.year or "",
                    "venue": p.venue or "",
                    "publication_types": "; ".join(p.publication_types),
                    "url": p.url or "",
                    "doi": p.doi or "",
                    "open_access_pdf_url": p.open_access_pdf_url or "",
                    "paper_id": p.paper_id,
                }
            )


def write_jsonl(papers: Sequence[Paper], out_jsonl: Path) -> None:
    out_jsonl.parent.mkdir(parents=True, exist_ok=True)
    with open(out_jsonl, "w", encoding="utf-8") as f:
        for p in papers:
            f.write(json.dumps(asdict(p), ensure_ascii=False) + "\n")


def write_bibtex_stub(papers: Sequence[Paper], out_bib: Path) -> None:
    """Write a minimal BibTeX stub.

    Note: Semantic Scholar does not always provide complete BibTeX fields.
    This stub exists to support downstream workflows, but you should verify
    against official publisher pages.
    """

    out_bib.parent.mkdir(parents=True, exist_ok=True)

    def bib_key(p: Paper) -> str:
        first_author = p.authors[0].split()[-1] if p.authors else "Unknown"
        year = str(p.year) if p.year else "n.d."
        title_word = p.title.split()[0] if p.title else "Untitled"
        return safe_filename(f"{first_author}{year}{title_word}", max_len=60)

    with open(out_bib, "w", encoding="utf-8") as f:
        for p in papers:
            key = bib_key(p)
            venue = p.venue or ""
            year = p.year or ""
            authors = " and ".join(p.authors)
            title = p.title.replace("{", "").replace("}", "")

            f.write(f"@inproceedings{{{key},\n")
            f.write(f"  title={{{{{title}}}}},\n")
            if authors:
                f.write(f"  author={{{{{authors}}}}},\n")
            if year:
                f.write(f"  year={{{{{year}}}}},\n")
            if venue:
                f.write(f"  booktitle={{{{{venue}}}}},\n")
            if p.doi:
                f.write(f"  doi={{{{{p.doi}}}}},\n")
            if p.url:
                f.write(f"  url={{{{{p.url}}}}},\n")
            f.write("}\n\n")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Search topic and filter to top CS conferences (Semantic Scholar backend).")
    parser.add_argument("--query", required=True, help="Subtopic query string")
    parser.add_argument("--venues", required=True, type=Path, help="Path to venue allowlist text file")
    parser.add_argument("--years", default="", help="Year range: YYYY or YYYY:YYYY (open ends allowed, e.g., 2020:)")
    parser.add_argument("--limit", type=int, default=200, help="Max results to fetch before filtering")
    parser.add_argument("--out", required=True, type=Path, help="Output path prefix (folder/name without extension)")
    parser.add_argument("--download-pdfs", action="store_true", help="Download open-access PDFs when available")
    parser.add_argument("--pdf-dir", type=Path, default=None, help="Directory to store PDFs (default: <out>_pdfs)")
    parser.add_argument("--write-bibtex", action="store_true", help="Write a minimal BibTeX stub")
    parser.add_argument("--api-key", default=os.environ.get("SEMANTIC_SCHOLAR_API_KEY", ""), help="Semantic Scholar API key (optional)")

    args = parser.parse_args(argv)

    start_year, end_year = _parse_years(args.years)
    allowlist = load_venue_allowlist(args.venues)

    fields = [
        "title",
        "authors",
        "year",
        "venue",
        "publicationTypes",
        "url",
        "externalIds",
        "openAccessPdf",
    ]

    raw_items = semantic_scholar_search(
        query=args.query,
        limit=args.limit,
        fields=fields,
        api_key=(args.api_key or None),
    )

    filtered: List[Paper] = []
    for item in raw_items:
        p = parse_paper(item)
        if not p.title:
            continue
        if not _year_in_range(p.year, start_year, end_year):
            continue
        if not venue_matches(p.venue, allowlist):
            continue
        filtered.append(p)

    # Deduplicate by title+year (simple heuristic)
    seen = set()
    deduped: List[Paper] = []
    for p in filtered:
        k = (_normalize_venue(p.title), p.year)
        if k in seen:
            continue
        seen.add(k)
        deduped.append(p)

    out_prefix = args.out
    out_csv = Path(str(out_prefix) + ".csv")
    out_jsonl = Path(str(out_prefix) + ".jsonl")

    write_csv(deduped, out_csv)
    write_jsonl(deduped, out_jsonl)

    if args.write_bibtex:
        out_bib = Path(str(out_prefix) + ".bib")
        write_bibtex_stub(deduped, out_bib)

    if args.download_pdfs:
        pdf_dir = args.pdf_dir or Path(str(out_prefix) + "_pdfs")
        for p in deduped:
            if not p.open_access_pdf_url:
                continue
            name = safe_filename(f"{p.year or ''}_{p.title}") + ".pdf"
            out_pdf = pdf_dir / name
            if out_pdf.exists():
                continue
            try:
                download_pdf(p.open_access_pdf_url, out_pdf)
            except Exception as e:  # noqa: BLE001
                print(f"[warn] failed pdf download for: {p.title} ({e})", file=sys.stderr)

    print(f"Wrote {len(deduped)} papers")
    print(f"- {out_csv}")
    print(f"- {out_jsonl}")
    if args.write_bibtex:
        print(f"- {Path(str(out_prefix) + '.bib')}")
    if args.download_pdfs:
        print(f"- PDFs under {args.pdf_dir or Path(str(out_prefix) + '_pdfs')}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

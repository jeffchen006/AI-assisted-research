#!/usr/bin/env python3
"""Search Google Scholar via SerpAPI and filter to an allowlist of venues.

Why SerpAPI?
- It is a supported API provider for Google Scholar results.
- Avoids brittle direct scraping.

Requirements
- Set SERPAPI_API_KEY in your environment, or pass --api-key.

Example
  export SERPAPI_API_KEY=... 
  python literature/scripts/search_google_scholar_serpapi.py \
    --query "agentic workflows" \
    --years 2020:2025 \
    --venues literature/top_venues.txt \
    --out literature/outputs/agentic_workflows_scholar \
    --limit 100 \
    --download-pdfs

Outputs
- CSV/JSONL with: title, authors, year, venue, url, pdf_url
- Optional PDF downloads (only if a direct PDF link is present in the result)

Notes
- Scholar metadata is sometimes incomplete; treat outputs as a candidate list.
- This tool does not bypass paywalls.
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


SERPAPI_ENDPOINT = "https://serpapi.com/search.json"


@dataclass(frozen=True)
class ScholarPaper:
    title: str
    authors: List[str]
    year: Optional[int]
    venue: Optional[str]
    url: Optional[str]
    pdf_url: Optional[str]
    snippet: Optional[str]


def _normalize_venue(venue: str) -> str:
    venue = venue.strip().lower()
    venue = re.sub(r"\s+", " ", venue)
    return venue


def load_venue_allowlist(path: Path) -> List[str]:
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


def _extract_year(text: str) -> Optional[int]:
    m = re.search(r"(19\d{2}|20\d{2})", text)
    if not m:
        return None
    try:
        return int(m.group(1))
    except ValueError:
        return None


def _extract_pdf_url(result: dict) -> Optional[str]:
    # SerpAPI may provide resources like [{'title': 'PDF', 'link': '...'}]
    resources = result.get("resources")
    if isinstance(resources, list):
        for r in resources:
            if not isinstance(r, dict):
                continue
            title = str(r.get("title") or "").lower()
            link = r.get("link")
            if not link:
                continue
            if "pdf" in title or str(link).lower().endswith(".pdf"):
                return str(link)
    return None


def _extract_authors(result: dict) -> List[str]:
    pub = result.get("publication_info") or {}
    authors = pub.get("authors")
    if isinstance(authors, list):
        names = []
        for a in authors:
            if isinstance(a, dict) and a.get("name"):
                names.append(str(a["name"]).strip())
        if names:
            return names

    # Fallback: parse from summary "A Author, B Author - Venue, Year"
    summary = str(pub.get("summary") or "")
    if "-" in summary:
        left = summary.split("-", 1)[0].strip()
        if left:
            return [x.strip() for x in left.split(",") if x.strip()]

    return []


def _extract_venue(result: dict) -> Optional[str]:
    pub = result.get("publication_info") or {}
    summary = str(pub.get("summary") or "").strip()

    # Common formats:
    # "A Author, B Author - NeurIPS, 2024 - proceedings.neurips.cc"
    # "A Author - IEEE S&P, 2022"
    if not summary:
        return None

    parts = [p.strip() for p in summary.split("-") if p.strip()]
    # Heuristic: venue often appears after authors segment.
    if len(parts) >= 2:
        return parts[1]

    return summary


def serpapi_scholar_search(
    query: str,
    start_year: Optional[int],
    end_year: Optional[int],
    limit: int,
    api_key: str,
    sleep_seconds: float = 1.0,
) -> Iterable[dict]:
    # SerpAPI paginates in steps of 10 with start=0,10,20...
    fetched = 0
    start = 0

    while fetched < limit:
        params = {
            "engine": "google_scholar",
            "q": query,
            "api_key": api_key,
            "start": start,
        }
        # Scholar year filters use as_ylo/as_yhi
        if start_year is not None:
            params["as_ylo"] = str(start_year)
        if end_year is not None:
            params["as_yhi"] = str(end_year)

        resp = requests.get(SERPAPI_ENDPOINT, params=params, timeout=60)
        resp.raise_for_status()
        payload = resp.json()
        results = payload.get("organic_results") or []
        if not results:
            return

        for r in results:
            yield r
            fetched += 1
            if fetched >= limit:
                return

        start += len(results)
        time.sleep(sleep_seconds)


def parse_result(result: dict) -> ScholarPaper:
    title = str(result.get("title") or "").strip()
    url = result.get("link")
    snippet = result.get("snippet")

    venue = _extract_venue(result)
    authors = _extract_authors(result)

    # Year: try publication summary first, then snippet.
    pub = result.get("publication_info") or {}
    summary = str(pub.get("summary") or "")
    year = _extract_year(summary) or _extract_year(str(snippet or ""))

    pdf_url = _extract_pdf_url(result)

    return ScholarPaper(
        title=title,
        authors=authors,
        year=year,
        venue=venue,
        url=str(url) if url else None,
        pdf_url=pdf_url,
        snippet=str(snippet) if snippet else None,
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


def write_csv(papers: Sequence[ScholarPaper], out_csv: Path) -> None:
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["title", "authors", "year", "venue", "url", "pdf_url"],
        )
        w.writeheader()
        for p in papers:
            w.writerow(
                {
                    "title": p.title,
                    "authors": "; ".join(p.authors),
                    "year": p.year or "",
                    "venue": p.venue or "",
                    "url": p.url or "",
                    "pdf_url": p.pdf_url or "",
                }
            )


def write_jsonl(papers: Sequence[ScholarPaper], out_jsonl: Path) -> None:
    out_jsonl.parent.mkdir(parents=True, exist_ok=True)
    with open(out_jsonl, "w", encoding="utf-8") as f:
        for p in papers:
            f.write(json.dumps(asdict(p), ensure_ascii=False) + "\n")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Search Google Scholar via SerpAPI and filter to top venues.")
    parser.add_argument("--query", required=True, help="Subtopic query string")
    parser.add_argument("--venues", required=True, type=Path, help="Path to venue allowlist text file")
    parser.add_argument("--years", default="", help="Year range: YYYY or YYYY:YYYY (open ends allowed, e.g., 2020:)")
    parser.add_argument("--limit", type=int, default=100, help="Max results to fetch before filtering")
    parser.add_argument("--out", required=True, type=Path, help="Output path prefix (folder/name without extension)")
    parser.add_argument("--download-pdfs", action="store_true", help="Download PDFs when a direct PDF link is present")
    parser.add_argument("--pdf-dir", type=Path, default=None, help="Directory to store PDFs (default: <out>_pdfs)")
    parser.add_argument("--api-key", default=os.environ.get("SERPAPI_API_KEY", ""), help="SerpAPI key (or set SERPAPI_API_KEY)")

    args = parser.parse_args(argv)

    if not args.api_key:
        print("Missing SERPAPI_API_KEY. Set env var or pass --api-key.", file=sys.stderr)
        return 1

    start_year, end_year = _parse_years(args.years)
    allowlist = load_venue_allowlist(args.venues)

    raw = serpapi_scholar_search(
        query=args.query,
        start_year=start_year,
        end_year=end_year,
        limit=args.limit,
        api_key=args.api_key,
    )

    filtered: List[ScholarPaper] = []
    for r in raw:
        p = parse_result(r)
        if not p.title:
            continue
        if not _year_in_range(p.year, start_year, end_year):
            continue
        if not venue_matches(p.venue, allowlist):
            continue
        filtered.append(p)

    # Deduplicate by title+year
    seen = set()
    deduped: List[ScholarPaper] = []
    for p in filtered:
        k = (p.title.strip().lower(), p.year)
        if k in seen:
            continue
        seen.add(k)
        deduped.append(p)

    out_prefix = args.out
    out_csv = Path(str(out_prefix) + ".csv")
    out_jsonl = Path(str(out_prefix) + ".jsonl")
    write_csv(deduped, out_csv)
    write_jsonl(deduped, out_jsonl)

    if args.download_pdfs:
        pdf_dir = args.pdf_dir or Path(str(out_prefix) + "_pdfs")
        for p in deduped:
            if not p.pdf_url:
                continue
            name = safe_filename(f"{p.year or ''}_{p.title}") + ".pdf"
            out_pdf = pdf_dir / name
            if out_pdf.exists():
                continue
            try:
                download_pdf(p.pdf_url, out_pdf)
            except Exception as e:  # noqa: BLE001
                print(f"[warn] failed pdf download for: {p.title} ({e})", file=sys.stderr)

    print(f"Wrote {len(deduped)} papers")
    print(f"- {out_csv}")
    print(f"- {out_jsonl}")
    if args.download_pdfs:
        print(f"- PDFs under {args.pdf_dir or Path(str(out_prefix) + '_pdfs')}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

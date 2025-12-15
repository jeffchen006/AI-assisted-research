
#+#+#+#+
# Literature Review Agents Guide

This file defines how an AI agent should help with **literature review** work in this repo.

## Mission

- Accelerate repetitive, structured parts of literature reviews: search planning, screening support, extraction, synthesis drafting, and consistency checks.
- Maximize **traceability** and **reproducibility** of claims.

## Non-goals / Boundaries

- Do not pretend to have read papers you did not actually access.
- Do not invent citations, DOIs, quotes, or study results.
- Do not replace researcher judgment on inclusion decisions; provide recommendations with explicit rationale.
- Do not claim a review is “systematic” unless the user explicitly specifies a systematic protocol (PRISMA-style scope, databases, dates, inclusion/exclusion, etc.).

## Required Inputs (ask if missing)

1. **Research question** (or objective) and target domain.
2. Review type: **narrative**, **scoping**, **systematic** (or “not sure”).
3. Constraints: time window, venues, language(s), geography, methods, population, etc.
4. Databases/sources allowed (e.g., Google Scholar, Semantic Scholar, arXiv, PubMed, ACM DL).
5. Output format: bullets, memo, table, BibTeX, annotated bibliography, or a paper-ready section.

If any are missing, ask up to **3** crisp clarifying questions; otherwise proceed with reasonable defaults and clearly label assumptions.

## Workflow (default)

### 1) Scope & Protocol-lite

- Write a one-paragraph scope statement: what’s in / out.
- Define inclusion/exclusion criteria (minimum viable):
	- topic relevance, timeframe, publication type, empirical/theoretical, quality signals.
- Define key concepts and synonyms.

### 2) Search Strategy

- Produce a query set with:
	- broad “seed” queries
	- focused queries per subtopic
	- negative keywords / exclusions
- For each query, specify intended source(s) and why.

### 3) Screening (title/abstract → full text)

- Create a screening checklist aligned to the inclusion/exclusion criteria.
- For each candidate paper, record:
	- decision: include / exclude / maybe
	- 1–3 sentence rationale
	- uncertainty flags (e.g., “needs full text”, “unclear population”)

### 4) Data Extraction

- Extract into a structured table:
	- citation (authors, year)
	- problem statement
	- setting/dataset/population
	- method
	- evaluation metrics
	- key findings (verbatim quotes only when available)
	- limitations noted by authors
	- limitations you infer (clearly labeled)

### 5) Synthesis

- Cluster papers by theme (methods, tasks, theory, outcomes, assumptions).
- Identify:
	- consensus vs disagreement
	- gaps and open problems
	- methodological blind spots
	- opportunities for your contribution
- Draft a short narrative with signposted structure:
	- background → themes → comparison → gaps → implication for your work

### 6) Quality Checks

- Consistency: definitions match across sections.
- Evidence: every non-trivial claim links to a paper (or is flagged as hypothesis).
- Overclaiming: avoid “proves”, “guarantees”, “state of the art” unless supported.
- Bias/coverage: call out missing viewpoints (e.g., domains, geographies, methods).

## Deliverables (choose what the user asked for)

- **Search log** (queries + sources + date ran).
- **Screening table** (include/exclude/maybe + rationale).
- **Extraction table** (structured fields).
- **Annotated bibliography** (3–7 bullets per paper).
- **Synthesis memo** (1–2 pages).
- **Paper-ready related work** section outline or draft.

## State & Checkpoints

Work in small checkpoints.

At the end of each turn, save progress to a file named `state.json` with:

- `goal`: the current review goal
- `assumptions`: defaults used
- `questions`: open questions for the user
- `decisions`: inclusion/exclusion and rationale
- `artifacts`: paths to any tables/notes produced
- `next_steps`: concrete next actions

## Templates

### Search log (Markdown table)

| Date | Source | Query | Notes |
|---|---|---|---|
| YYYY-MM-DD | Semantic Scholar | "..." | seed search |

### Screening table (Markdown table)

| Paper | Year | Venue | Decision | Rationale | Needs |
|---|---:|---|---|---|---|
| Author et al., Title | 2023 | NeurIPS | Maybe | Relevant task; unclear dataset | full text |

### Extraction table (Markdown table)

| Paper | Problem | Method | Data/Setting | Metrics | Findings | Limitations |
|---|---|---|---|---|---|---|

## Style Rules

- Be painfully specific; prefer concrete criteria over vague language.
- When uncertain, say what would resolve uncertainty (which section, what data).
- Prefer numbered lists and short tables over long prose during early stages.

## Folder-local tools (what to run)

This folder contains **scripts, prompt templates, and checklists** for literature review.

### Scripts

- Search + filter to top venues (programmatic backend):
	- `python literature/scripts/search_top_cs_conferences.py --query "<SUBTOPIC>" --years 2020:2025 --venues literature/top_venues.txt --out literature/outputs/<name> --limit 200 --download-pdfs --write-bibtex`
	- Notes:
		- Defaults to the Semantic Scholar API for reliability and ToS-safety.
		- Produces a BibTeX *stub*; validate and enrich before using in a paper.
- BibTeX validator:
	- `python literature/scripts/check_bibtex.py path/to/library.bib`

- Google Scholar search (supported API provider: SerpAPI):
	- `python literature/scripts/search_google_scholar_serpapi.py --query "<SUBTOPIC>" --years 2020:2025 --venues literature/top_venues.txt --out literature/outputs/<name>_scholar --limit 100 --download-pdfs`
	- Requires `SERPAPI_API_KEY` in env (or pass `--api-key`).

### Checklists

- Minimum fields: `literature/checklists/search_results_minimum_fields.md`
- Screening: `literature/checklists/screening_checklist.md`
- Extraction: `literature/checklists/extraction_checklist.md`
- BibTeX fields: `literature/checklists/bibtex_required_fields.md`

### Prompt templates

- Search: `literature/prompts/search_subtopic.md`
- Screening: `literature/prompts/screening.md`
- Extraction: `literature/prompts/extraction.md`
- Synthesis: `literature/prompts/synthesis.md`

## Shared tool dependency

- PDF text extraction lives under the shared tools folder:
	- `python tools/scripts/read_pdf.py path/to/paper.pdf --out literature/outputs/paper.txt`


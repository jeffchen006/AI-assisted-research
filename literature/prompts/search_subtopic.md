# Prompt: Search a subtopic (top CS conferences)

## Inputs
- Subtopic:
- Years:
- Venue definition (what counts as “top”):
- Must-include keywords:
- Exclude keywords:

## Output requirements
1. Produce 5–10 candidate search queries.
2. Identify which venues/conferences you will keep.
3. Return a CSV-ready table with columns:
   - title | authors | year | venue | url | pdf_url (if any)
4. Do not fabricate citations. If a field is unknown, leave it blank.

## Agent behavior
- Prefer reproducible sources/APIs over scraping.
- If using an automated tool, record the query and timestamp in a search log.

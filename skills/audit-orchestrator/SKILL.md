---
name: audit-orchestrator
description: >-
  Audit a public website for AI-discoverability and on-site-engagement problems
  and emit one findings report. Use when asked to audit a brand URL.
license: MIT
---

# audit-orchestrator

Sole marketplace entrypoint. Recommend-only. Never mutates the site.

## When to use

Use when the user provides a website URL and wants a Brand AI Readiness audit.

## Inputs

- `url` (string, required): public site to audit
- `max_pages` (int, optional, default 12)
- `render_js` (bool, optional, default false): Playwright only if already installed

## Procedure

1. Normalize the URL. Fetch `/robots.txt`. Honor Disallow for this auditor UA. Stop the crawl if the target path is disallowed; still report CR-01 if AI bots are blocked.
2. Fetch the homepage and up to `max_pages` in-domain links with stdlib HTTP. Record status chains, headers, HTML. Optional: if `render_js` and Playwright is present, capture rendered DOM. Never download a browser.
3. Build one immutable snapshot (pages, HTML, headers, discovered JSON-LD, links).
4. Run, in any order, on that snapshot: `crawl-render-audit`, `structured-data-audit`, `fact-quality-audit`, `freshness-corroboration`, `entity-identity-audit`, `engagement-audit`.
5. Drop findings with empty evidence. Deduplicate. Sort by severity then impact. Add proactive suggested actions where useful.
6. Emit one JSON report matching the Output schema. Runtime must stay under 5 minutes.

## Output (fixed schema)

```json
{
  "site": "example.com",
  "audited_at": "2026-09-20T14:32:00Z",
  "summary": {"total_findings": 6, "critical": 1, "high": 2, "medium": 3},
  "findings": [
    {
      "id": "F-001",
      "title": "No JSON-LD structured data on product pages",
      "severity": "high",
      "evidence": "Crawled 12 product pages; 0/12 contain schema.org markup.",
      "suggested_action": {
        "summary": "Add Product/Offer JSON-LD to every product page.",
        "priority": "high"
      }
    }
  ]
}
```

`suggested_action` is an object. Severity is lowercase. Extra fields allowed. 0-100 scores are not the contest output.

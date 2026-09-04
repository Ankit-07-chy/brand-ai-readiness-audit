# Architecture

Read-only pipeline. One URL in. One Adobe-schema report out.

## Two halves

```
Off-site discoverability          On-site engagement
Reach -> Read -> Extract          Visitor lands (often on a deep URL)
      -> Trust -> Use             Who / what / next?
                                  Nav, breadcrumbs, CTA
```

Mapped to skills:

| Stage | Skill |
| :--- | :--- |
| Reach / Read | `crawl-render-audit` |
| Extract | `structured-data-audit`, `fact-quality-audit` |
| Trust | `freshness-corroboration` |
| Use | `entity-identity-audit` |
| On-site | `engagement-audit` |
| Compose | `audit-orchestrator` (only entrypoint) |

## Runtime pipeline

```
URL
  -> robots.txt + homepage fetch (stdlib HTTP)
  -> snapshot (HTML, headers, discovered links, JSON-LD blocks)
  -> optional Playwright DOM (only if already installed; never in ZIP)
  -> 6 specialist skills (same snapshot; no second crawl)
  -> orchestrator merges, dedupes, sorts by severity x impact
  -> one JSON report (findings + suggested_action objects)
```

## Layers

1. **Deterministic checks** - robots, status, JSON-LD parse, dates, NAP strings, CTA/link counts.
2. **Evidence store** - immutable snippets, URLs, headers. LLM may only read this.
3. **Targeted reasoning** - first-impression clarity, claim ambiguity. Every observation cites evidence.
4. **Composer** - Adobe report. Extra fields allowed. 0-100 scores are not the output.

## Packaging

- Python stdlib for HTTP/HTML by default (`urllib` + `html.parser`).
- Playwright optional. Chromium binary must not ship in the ZIP (cap 50 MB; we budget 45).
- Submission ZIP contains `marketplace.json` + `skills/` (+ lean `scripts/`). Test GUI stays out of the judged ZIP.

## Guardrails

Read-only. Respect robots.txt. No auth. No writes. < 5 minutes. Recommend-only.

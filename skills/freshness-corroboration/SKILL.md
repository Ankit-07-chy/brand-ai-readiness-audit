---
name: freshness-corroboration
description: >-
  Check date signals for disagreement or staleness, then corroborate 2-3
  public sources. No paid APIs.
license: MIT
---

# freshness-corroboration

Trust specialist. Invoked by `audit-orchestrator`.

## When to use

When a snapshot exists and freshness / corroboration must be checked.

## Inputs

- `snapshot`: HTML, headers, JSON-LD dates
- optional public lookups: Wikidata, Wikipedia, `sameAs` targets

## Procedure

1. Collect dateModified, datePublished, HTTP Last-Modified, sitemap lastmod, visible dates. Flag disagreements (FC-01).
2. Flag core pages whose newest date is older than 12 months with no update signal (FC-02). Do not treat a footer copyright year as an update.
3. For brand name, key dates, and key facts, check 2-3 public sources (Wikidata, Wikipedia, official social). Flag mismatches (FC-03).
4. Emit findings with the date values or source URLs, severity, suggested action.

## Output

Array of findings (`id`, `title`, `severity`, `evidence`, `suggested_action`).

---
name: crawl-render-audit
description: >-
  Check whether AI crawlers can reach and read a site: robots.txt, HTTP
  status/redirects, noindex, optional HTML vs rendered DOM gap.
license: MIT
---

# crawl-render-audit

Reach / Read specialist. Invoked by `audit-orchestrator`.

## When to use

When a snapshot exists and crawl/render accessibility must be scored as findings.

## Inputs

- `snapshot`: pages with URL, status chain, headers, raw HTML, optional rendered DOM

## Procedure

1. Parse `robots.txt`. For GPTBot, ClaudeBot, PerplexityBot, Google-Extended, and `*`, record Allow/Disallow on `/` and key content paths (CR-01).
2. For each fetched URL, record status chain. Flag non-200, loops, http-to-https traps, soft-404 (CR-02).
3. If rendered DOM is present, diff visible text and JSON-LD against raw HTML. Flag facts/prices that exist only after JS (CR-03). If no DOM, skip CR-03; do not fail the skill.
4. Flag `X-Robots-Tag` / meta robots `noindex` on pages that otherwise look indexable (CR-04).
5. Emit findings with URL, quoted robots/header/HTML evidence, severity, and a suggested action.

## Output

Array of findings (`id`, `title`, `severity`, `evidence`, `suggested_action`). Orchestrator assigns final `F-00N` ids.

---
name: engagement-audit
description: >-
  Check why a visitor who arrives (often on a deep URL) cannot orient or act:
  who/what/next, navigation, breadcrumbs, CTAs. Not llms.txt or OpenAPI.
license: MIT
---

# engagement-audit

On-site engagement specialist. Invoked by `audit-orchestrator`.

## When to use

When a snapshot exists and on-site orientation/action must be checked.

## Inputs

- `snapshot`: HTML of homepage and interior pages

## Procedure

1. On the landing page and each interior page, extract H1, first subhead, and primary CTA. Flag if who, what, or next is missing in the first screenful (EG-01).
2. Collect nav labels. Compare to claimed offerings (H1/H2). Flag jobs the site claims that nav does not cover (EG-02).
3. On non-homepage URLs, look for breadcrumbs or equivalent parent context. Flag deep pages with no way back to a parent (EG-03).
4. Classify the primary CTA destination (form, product, contact, signup vs another article). Flag "learn more" loops with no action (EG-04).
5. Do **not** flag missing `/llms.txt`, OpenAPI, or chat widgets as core defects. Those may only appear as low-priority proactive suggestions.
6. Emit findings with URL, quoted heading/CTA/nav evidence, severity, suggested action.

## Output

Array of findings (`id`, `title`, `severity`, `evidence`, `suggested_action`).

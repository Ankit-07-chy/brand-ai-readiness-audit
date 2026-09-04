---
name: structured-data-audit
description: >-
  Parse JSON-LD. Flag invalid markup and incomplete Product/Offer on product
  pages. Never report missing schema blindly.
license: MIT
---

# structured-data-audit

Extract specialist. Invoked by `audit-orchestrator`.

## When to use

When a snapshot exists and structured data must be checked.

## Inputs

- `snapshot`: HTML per URL

## Procedure

1. Extract `<script type="application/ld+json">` blocks. Parse JSON. Flag syntax errors with the snippet (SD-01).
2. Detect product pages (path, H1, price-like text, add-to-cart). On those pages only, require Product/Offer fields: name, price, priceCurrency, availability (SD-02).
3. If Organization/WebSite JSON-LD exists, compare `name` to visible title/H1. Flag conflicts (SD-03).
4. Do **not** emit "no FAQPage" or "no schema on site" as a defect. A proactive suggested action to add Product JSON-LD is allowed only on product pages.
5. Emit findings with URL, JSON-LD snippet, severity, suggested action.

## Output

Array of findings (`id`, `title`, `severity`, `evidence`, `suggested_action`).

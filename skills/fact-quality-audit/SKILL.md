---
name: fact-quality-audit
description: >-
  Extract claims from the snapshot. Flag contradictions, numbers without
  units, and ungrounded superlatives that make AI answers unsafe.
license: MIT
---

# fact-quality-audit

Extract specialist. Invoked by `audit-orchestrator`.

## When to use

When a snapshot exists and claim quality must be checked.

## Inputs

- `snapshot`: visible text per URL

## Procedure

1. Extract numeric, price, policy, and spec claims with their URL and snippet (FQ-01).
2. Pair claims of the same type across pages. Flag contradictions (price, hours, refund, spec) (FQ-02).
3. Flag numbers missing units or comparators (FQ-03).
4. Flag ungrounded superlatives ("#1", "best", "only") with no adjacent proof (FQ-04).
5. Emit findings with both snippets when contradicting, severity, suggested action (rewrite, add unit, cite source).

## Output

Array of findings (`id`, `title`, `severity`, `evidence`, `suggested_action`).

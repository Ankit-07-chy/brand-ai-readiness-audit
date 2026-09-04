---
name: entity-identity-audit
description: >-
  Check that Organization name, sameAs links, and NAP stay consistent so AI
  systems can attach facts to one entity.
license: MIT
---

# entity-identity-audit

Use specialist. Invoked by `audit-orchestrator`.

## When to use

When a snapshot exists and entity identity must be checked.

## Inputs

- `snapshot`: HTML, JSON-LD Organization, footer/contact text

## Procedure

1. Collect brand/Organization name from title, H1, JSON-LD `name`. Flag conflicts (EI-01).
2. Fetch `sameAs` URLs. Flag 404s or pages whose title is a different entity (EI-02).
3. Collect NAP (name, address, phone) from footer, contact, JSON-LD. Flag cross-page differences (EI-03).
4. Emit findings with the conflicting strings and URLs, severity, suggested action (one canonical name + working sameAs).

## Output

Array of findings (`id`, `title`, `severity`, `evidence`, `suggested_action`).

---
name: Freshness & Corroboration
description: Checks timestamp metadata, update cadence, external citation consistency, and cross-source corroboration.
---

# Freshness & Corroboration Skill

## Purpose
Assesses content freshness indicators and external corroboration signals to ensure AI models recognize brand information as up-to-date and authoritatively supported.

## When to Use
Invoked by `audit-orchestrator` during recency and authority evaluation.

## High-Level Responsibilities
- Inspect explicit timestamp metadata (`dateModified`, `datePublished`, HTTP `Last-Modified`, sitemap `<lastmod>`).
- Evaluate update cadence across core product pages, blogs, and documentation.
- Verify cross-source corroboration by checking external citations and references.

## Inputs
- `page_metadata_records` (array of header and schema timestamps)
- `external_reference_links` (array of outbound/inbound citation URLs)

## Outputs
- Freshness & Corroboration score (0–100)
- Recency decay report and un-corroborated claim flags

## Evidence Expectations
- Header timestamp dumps
- JSON-LD date field extracts
- Citation link mappings

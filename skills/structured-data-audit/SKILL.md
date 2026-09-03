---
name: Structured Data Audit
description: Validates Schema.org JSON-LD, Microdata, OpenGraph, and semantic HTML markup for AI entity extraction.
---

# Structured Data Audit Skill

## Purpose
Validates the presence, correctness, and completeness of structured metadata markup on brand web pages to optimize machine readability and entity extraction by search LLMs.

## When to Use
Invoked by `audit-orchestrator` during the semantic extraction phase.

## High-Level Responsibilities
- Extract JSON-LD script blocks, Microdata, and OpenGraph tags from DOM snapshots.
- Validate Schema.org compliance (required fields for `Organization`, `Product`, `FAQPage`, etc.).
- Identify syntax errors, missing context attributes, and un-anchored entities.
- Evaluate semantic HTML tag usage (`<article>`, `<section>`, `<table>`).

## Inputs
- `rendered_dom_snapshots` (array of DOM documents)
- `expected_schemas` (array of schema types to check)

## Outputs
- Structured data score (0–100)
- Validation error log and missing schema recommendations

## Evidence Expectations
- Extracted JSON-LD payloads
- Schema validator rule match/fail logs

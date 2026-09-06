---
name: Structured Data Audit
description: Validates Schema.org JSON-LD, Microdata, OpenGraph, and semantic HTML markup for machine readability and entity extraction.
---

# Structured Data Audit Skill

## Purpose
Inspects web page HTML to audit structured data markup (JSON-LD script blocks, Microdata, and relevant meta tags) and reports observable technical findings using the common Evidence/Finding model.

## When to Use
Invoked by `audit-orchestrator` during the semantic structured data analysis phase.

## Standard Check Matrix

| Check ID | Check Title | Severity | Description |
| :--- | :--- | :--- | :--- |
| **`SD-001`** | **JSON-LD Detection** | Info / Low | Detects presence of `<script type="application/ld+json">` blocks. |
| **`SD-002`** | **JSON-LD Parse Validity** | High | Verifies that all detected JSON-LD blocks parse as valid JSON syntax. |
| **`SD-003`** | **Schema Type Detection** | Info / Low | Extracts and lists all declared `@type` (or Microdata `itemtype`) schema values. |
| **`SD-004`** | **Entity Information Completeness** | Info / Medium | Checks completeness of core properties for `Organization`, `Person`, `Product`, `WebSite`, etc. |
| **`SD-005`** | **Structured Data vs Visible Content Consistency** | High | Deterministically verifies consistency between structured entity names and visible `<title>` / `<h1>` text. |
| **`SD-006`** | **Duplicate or Conflicting Structured Data** | Medium | Identifies multiple schema objects of the same type with conflicting canonical property values. |

## Implementation Principles
- **Observable Technical Facts:** Reports technical properties without speculating on search engine ranking algorithms or LLM citation boosts.
- **Traceable Evidence:** Every finding includes precise evidence pointers (`location`, `source_url`, `evidence_type`, `observed`, `expected`).
- **Non-Critical Defaults for Missing Data:** Absence of optional structured data triggers `WARNING` or `INFO` findings rather than critical severity caps.
- **Raw Payload Preservation:** Preserves raw JSON-LD schema dictionaries in evidence payloads while truncating excessively large blocks for memory efficiency.

## Code Entrypoint
- Implementation module: [`src/analysis/structured_data_audit.py`](file:///d:/Adobe/brand-ai-readiness-audit/src/analysis/structured_data_audit.py)
- Unit tests: [`tests/test_structured_data_audit.py`](file:///d:/Adobe/brand-ai-readiness-audit/tests/test_structured_data_audit.py)

---
name: Entity Identity & Consistency
description: Audits brand entity attributes, NAP (Name, Address, Phone) consistency, Knowledge Graph alignment, and canonical branding.
---

# Entity Identity & Consistency Skill

## Purpose
Audits brand identity signals to ensure AI Knowledge Graphs and search engines can construct a unified, canonical entity model for the brand without entity fragmentation.

## When to Use
Invoked by `audit-orchestrator` during entity validation.

## High-Level Responsibilities
- Audit Name, Address, Phone (NAP) uniformity across domain pages.
- Validate `Organization` schema `sameAs` array links (social profiles, Wikipedia, Wikidata).
- Detect conflicting brand names, obsolete trade names, or mismatched logo asset URLs.
- Check Knowledge Graph entity alignment.

## Inputs
- `extracted_entity_attributes` (JSON object containing scraped brand names, addresses, social URIs)
- `canonical_brand_profile` (expected brand entity configuration)

## Outputs
- Entity Consistency sub-score (0–100)
- Identity conflict findings and missing `sameAs` canonical link list

## Evidence Expectations
- Extracted NAP text blocks
- `sameAs` URL list extracts
- Wikidata / Wikipedia lookup response logs

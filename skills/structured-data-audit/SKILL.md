---
name: Structured Data Audit
description: Validates Schema.org JSON-LD, Microdata, OpenGraph, and semantic HTML markup for AI entity extraction and machine readability.
---

# Structured Data Audit Skill

## Purpose
The **Structured Data Audit** skill evaluates the presence, syntax validity, coverage, and entity richness of structured metadata and semantic HTML on a brand's website. It ensures that AI search engines, knowledge graphs, and RAG pipelines can extract unambiguous entity definitions, product specifications, FAQ answers, and content relationships.

---

## When to Use
Invoked by `audit-orchestrator` during the semantic extraction and machine readability evaluation phase.

---

## High-Level Responsibilities

1. **Schema.org JSON-LD & Microdata Extraction**:
   - Extracts all `<script type="application/ld+json">` payloads and embedded Microdata itemscopes from DOM snapshots.
   - Parses nested entity graphs and resolves `@id` references.

2. **Core Schema Type Validation**:
   - **`Organization` / `LocalBusiness`**: Verifies `name`, `legalName`, `url`, `logo`, `contactPoint`, and `sameAs` entity links.
   - **`WebSite`**: Checks `url`, `name`, and potential `potentialAction` (`SearchAction`) markup.
   - **`Product` / `SoftwareApplication`**: Checks `name`, `description`, `image`, `offers` (`price`, `priceCurrency`, `availability`), `aggregateRating`.
   - **`Article` / `BlogPosting`**: Checks `headline`, `author` (linked to `Person`), `datePublished`, `dateModified`, `publisher`.
   - **`FAQPage`**: Validates `mainEntity` array of `Question` and `Answer` objects.

3. **Syntax & Specification Compliance**:
   - Validates JSON-LD against official Schema.org vocabularies.
   - Detects syntax errors, missing mandatory properties, deprecated properties, and malformed URI strings.

4. **Entity Linkage & Social Graph**:
   - Evaluates `sameAs` links pointing to authoritative profiles (Wikidata, Wikipedia, LinkedIn, Twitter/X, Crunchbase, GitHub).
   - Audits OpenGraph (`og:title`, `og:description`, `og:image`, `og:url`) and Twitter Card metadata.

5. **Semantic HTML Document Hierarchy**:
   - Audits structural HTML5 landmark elements: `<main>`, `<article>`, `<section>`, `<nav>`, `<aside>`, `<header>`, `<footer>`.
   - Audits structured presentation elements: `<table>`, `<thead>`, `<tbody>`, `<dl>`, `<dt>`, `<dd>`.

---

## Inputs
- **`rendered_dom_snapshots`** *(array of DOM documents, required)*: Fully rendered DOM snapshots from the Evidence Store.
- **`target_url`** *(string, required)*: Base domain of the audited website.

---

## Outputs
- **`machine_readability_score`** *(number, 0–100)*: Normalized sub-score.
- **`findings`** *(array of objects)*:
  - `finding_id`: Unique identifier (e.g., `FIND-SCHEMA-001`).
  - `category`: `Machine Readability & Entity`.
  - `severity`: `Critical` | `High` | `Medium` | `Low`.
  - `title`: Short summary.
  - `description`: Technical defect explanation.
  - `impact`: Impact on AI entity extraction and knowledge graph assimilation.
  - `evidence_ids`: Referenced Evidence IDs (`EVID-SCHEMA-JSONLD`, etc.).
  - `remediation`: Exact JSON-LD snippet or HTML markup fix.
- **`schema_inventory`**: JSON object mapping all discovered schema types, counts, and validation statuses.

---

## Evidence Expectations
- `EVID-SCHEMA-JSONLD`: Extracted raw JSON-LD code blocks.
- `EVID-SCHEMA-VALIDATION`: Validator error/warning logs and rule compliance tables.
- `EVID-OPENGRAPH`: Key-value pairs of extracted OpenGraph and social metadata.
- `EVID-SEMANTIC-HTML`: Element count and hierarchy tree of semantic HTML5 tags.

---

## False-Positive Considerations
- **Custom Schema Extensions**: Proprietary extension properties not in the base Schema.org vocabulary should be flagged as warnings, not syntax errors, if namespaced properly.
- **Multiple Organizations**: Multi-brand holdings or subsidiaries with multiple nested Organization schemas should not be penalized if parent-child relationships are declared via `parentOrganization` or `subOrganization`.

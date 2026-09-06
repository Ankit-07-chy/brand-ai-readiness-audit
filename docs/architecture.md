# System Architecture Documentation

## Overview

The **Brand AI Readiness Audit** system follows a modular, evidence-first pipeline designed to assess web properties for AI discoverability, technical renderability, and machine readability.

The system decouples **General Evidence Extraction** from **Specialized Audit Skills**, ensuring that all page signals, structured data, resource links, image captions, and page role classifications are captured in a single pass into a unified **Shared Evidence Store** (`WebsiteEvidence`).

---

## High-Level Pipeline Diagram & Data Flow

The core system data flow follows a strict, end-to-end multi-stage pipeline:

```
[ Target URL ]
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│                 1. Discovery & Crawl                    │
│ (robots.txt, sitemap.xml, HTML fetch, page role signals)│
└────────────────────────────┬────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│            2. General Evidence Extraction               │
│ (Metadata, Headings, Text, Images, Links, Forms, JSON-LD)│
└────────────────────────────┬────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│                3. Shared Evidence Store                 │
│      (WebsiteEvidence & PageEvidence with Provenance)   │
└────────────────────────────┬────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│        4. Semantic Understanding (Adapter Layer)        │
│    (SemanticUnderstandingAdapter interface boundary)    │
└────────────────────────────┬────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│                 5. Specialized Audit Skills             │
│ (crawl-render-audit, structured-data-audit, etc.)       │
└────────────────────────────┬────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│             6. Aggregation, Scoring & Report            │
│       (Finding consolidation, cap scoring, JSON report) │
└─────────────────────────────────────────────────────────┘
```

---

## Architectural Component Separation

To prevent hallucination, eliminate duplicate site crawls, and ensure reproducible audits, the architecture strictly segregates responsibilities across clear decoupled layers:

### 1. Discovery & Site Crawler
- **Responsibility:** Discover reachable pages, extract crawler rules, and fetch page HTML.
- **Components:**
  - `RobotsTxtParser`: Parses user-agent specific rules (`*`, `GPTBot`, `ClaudeBot`, `PerplexityBot`) and sitemap locations.
  - `SitemapParser`: Extracts child sitemaps and target URLs from sitemap indices and urlsets.
  - `PageRoleClassifier`: Categorizes URLs into functional roles (`homepage`, `about`, `contact`, `product`, `terms`, `documentation`).
  - `SiteCrawler`: Executes depth-bounded crawl using custom or default HTTP fetchers.

### 2. General Evidence Extraction
- **Responsibility:** Extract sitewide and per-page DOM evidence without domain-specific audit assumptions.
- **Extractors:**
  - `extract_page_metadata`: Extracts page titles, meta descriptions, canonical URLs, OG tags, and language declarations.
  - `extract_page_content`: Parses visible headings, paragraph blocks, lists, tables, blockquotes, dates, and contact signals (emails, phone numbers).
  - `extract_page_images`: Filters tracking pixels and favicons (<=10px or matching pixel patterns) while preserving figure captions (`<figure>/<figcaption>`) and image dimensions.
  - `extract_page_links_and_resources`: Extracts internal/external links, downloadable document resources (PDF, DOCX, CSV), and interactive forms.
  - `extract_structured_data`: Extracts JSON-LD scripts, OpenGraph, Microdata, and validates JSON-LD syntax.

### 3. Shared Evidence Store (`WebsiteEvidence`)
- **Responsibility:** Persist immutable, structured evidence models for the entire audited domain.
- **Key Models:**
  - `WebsiteEvidence`: Container for all `PageEvidence`, `RobotsEvidence`, and `SitemapEvidence`.
  - `PageEvidence`: Structured page snapshot containing metadata, headings, images, links, forms, documents, dates, and contacts.
  - `Provenance`: Standardized tracking of evidence source URL and DOM location context.

### 4. Semantic Understanding Adapter Layer
- **Responsibility:** Provide an extensible interface boundary (`SemanticUnderstandingAdapter`) for future optional LLM or vision semantic enrichment without creating hard dependencies in core audit skills.
- **Operations:**
  - Baseline `BaselineUnderstandingAdapter` provides deterministic fallbacks.
  - Pluggable adapter interface accepts `WebsiteEvidence` and returns enriched semantic insights.

### 5. Specialized Audit Skills
- **Responsibility:** Perform domain audits on top of `WebsiteEvidence`.
- **Skills:**
  - `crawl-render-audit`: Evaluates site crawlability, HTTP status, meta tags, heading hierarchy, content depth, and site coverage.
  - `structured-data-audit`: Evaluates JSON-LD presence, parse validity, schema types, entity completeness, and visible content consistency.

### 6. Scoring Engine & Report Generator
- **Responsibility:** Aggregate audit findings across all skills into a unified `AuditReport`.
- **Scoring Logic:**
  - Calculates percentage score (0–100) based on pass/fail/warning counts.
  - Enforces severity caps for critical failures (e.g. total AI bot block or fatal crawl errors).


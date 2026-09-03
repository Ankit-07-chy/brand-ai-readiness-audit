# System Architecture Documentation

## Overview

The **Brand AI Readiness Audit** system follows a modular, evidence-first pipeline designed to assess web properties for AI discoverability and machine readability.

---

## High-Level Pipeline Diagram

```
[ Target Website ]
       │
       ▼
┌─────────────────────────────────────────┐
│       1. Crawl & Render Pipeline        │
│   (Fetch HTML, JS Render, HTTP Headers) │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│          2. Evidence Collection         │
│  (DOM Snapshots, Schemas, Text Blocks)  │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│       3. Specialized Audit Skills       │
│  (Crawl, Data, Quality, Entity, etc.)   │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│        4. Evidence Validation           │
│   (Verify Deterministic Fact Grounding) │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│      5. Scoring & Prioritization        │
│    (Category Scores & Severity Matrix)  │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│            6. Recommendations           │
│      (Actionable Remediation Steps)     │
└────────────────────┬────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────┐
│            7. Final Report              │
│       (JSON Marketplace Artifact / MD)  │
└─────────────────────────────────────────┘
```

---

## Architectural Component Separation

To prevent model hallucination and ensure reproducible audits, the architecture strictly segregates responsibilities across five distinct layers:

### 1. Deterministic Checks
- **Responsibility:** Execute non-probabilistic parsing and rule-based verification.
- **Operations:**
  - Parsing `robots.txt` rules against standard AI User-Agent strings (`GPTBot`, `ClaudeBot`, `PerplexityBot`).
  - Schema syntax validation (JSON-LD parsing, Microdata extraction, spec compliance).
  - HTTP header inspection (`X-Robots-Tag`, `Content-Type`, `Last-Modified`).
  - Pre-rendering vs. Post-rendering DOM diff calculation.
  - Checking physical file availability (`/llms.txt`, `/sitemap.xml`, `/openapi.json`).

### 2. Evidence Collection & Storage
- **Responsibility:** Capture and persist raw, immutable artifacts extracted during crawling.
- **Artifacts:**
  - Raw HTML responses and rendered DOM snapshots.
  - Extracted Schema JSON-LD payloads.
  - Normalized text blocks and heading trees.
  - HTTP request/response header dumps.
- **Rule:** LLM reasoning components may only inspect data residing within the Evidence Store.

### 3. LLM Reasoning
- **Responsibility:** Perform qualitative and semantic evaluations where deterministic rules are insufficient.
- **Operations:**
  - Analyzing text claims for ambiguity, vagueness, or contradiction.
  - Assessing whether product specs or policy details are clear enough for AI retrieval.
  - Evaluating entity description consistency across unstructured narrative text.
  - Formulating tailored remediation recommendations.
- **Constraint:** LLM reasoning outputs must explicitly cite the evidence ID supporting every observation.

### 4. Scoring Engine
- **Responsibility:** Compute standardized sub-scores (0–100) and overall brand readiness indexes.
- **Formula Model:**
  - Sub-scores are derived from deterministic pass/fail ratios combined with weighted LLM quality ratings.
  - Critical severity failures (e.g., total AI crawler block in `robots.txt`) hard-cap the maximum category score.

### 5. Recommendations & Final Report
- **Responsibility:** Aggregate audit findings into structured JSON artifacts and markdown executive summaries.
- **Outputs:**
  - Categorized list of findings with severity ratings (Critical, High, Medium, Low).
  - Step-by-step remediation instructions for engineering and content teams.
  - Exportable audit report conforming to Agent Skill Marketplace output standards.

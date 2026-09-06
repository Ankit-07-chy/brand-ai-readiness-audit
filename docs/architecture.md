# System Architecture Documentation

## Overview

The **Brand AI Readiness Audit** system is an evidence-first, automated evaluation platform designed to assess a brand's digital presence across two foundational dimensions:
1. **Off-site Discoverability** (How effectively search engines and generative AI systems crawl, index, understand, retrieve, surface, and cite the brand).
2. **On-site Engagement** (How effectively the website helps human visitors and AI agents understand offerings, navigate, trust, and convert).

The system operates strictly on a **URL-only input constraint**: users provide only a target website URL. All brand context, offerings, canonical entity models, and representative discovery queries are derived automatically from the website's structure, content, and observable external signals.

---

## High-Level Architecture Pipeline

```
                                 [ Target Website URL ]
                                           │
                                           ▼
               ┌───────────────────────────────────────────────────────┐
               │              1. Automated Context Discovery           │
               │   (Extract Brand Name, Entity Profile, Core Products, │
               │     Value Props, and Discovery Query Candidates)      │
               └───────────────────────────┬───────────────────────────┘
                                           │
                                           ▼
               ┌───────────────────────────────────────────────────────┐
               │              2. Crawl & Rendering Engine              │
               │   (Fetch Raw HTML, Execute Headless JS Rendering,     │
               │     Capture HTTP Headers, Sitemaps, and robots.txt)   │
               └───────────────────────────┬───────────────────────────┘
                                           │
                                           ▼
               ┌───────────────────────────────────────────────────────┐
               │              3. Immutable Evidence Store              │
               │  (Raw DOM, Rendered DOM, Schema JSON-LD, Text Blocks, │
               │   Header Dumps, Screenshot Viewports, Query Records)  │
               └───────────────────────────┬───────────────────────────┘
                                           │
                     ┌─────────────────────┴─────────────────────┐
                     ▼                                           ▼
┌─────────────────────────────────────────┐ ┌─────────────────────────────────────────┐
│     Dimension A: Off-site Discovery     │ │      Dimension B: On-site Engagement    │
│  ├── A.1 On-Page SEO & Content Quality  │ │  ├── B.1 First-Visit Clarity            │
│  ├── A.2 Technical SEO & Crawlability   │ │  ├── B.2 Content Engagement             │
│  ├── A.3 Off-Page Authority (Observable)│ │  ├── B.3 Navigation & Findability       │
│  ├── A.4 AI / GEO Discoverability       │ │  ├── B.4 CTA & User Journey             │
│  │   ├── Structural AI Readiness        │ │  ├── B.5 Performance & Stability        │
│  │   └── Observed AI Visibility Testing │ │  ├── B.6 Mobile UX & Responsiveness     │
│  ├── A.5 Machine Readability & Entity   │ │  ├── B.7 Trust, Credibility & Compliance│
│  └── A.6 Freshness & Corroboration      │ │  ├── B.8 Observable Accessibility       │
│                                         │ │  └── B.9 AI-Agent Interaction Readiness │
└─────────────────────────────────────────┘ └─────────────────────────────────────────┘
                     │                                           │
                     └─────────────────────┬─────────────────────┘
                                           │
                                           ▼
               ┌───────────────────────────────────────────────────────┐
               │              4. Evidence Validation Engine            │
               │   (Enforce Fact Grounding & Reject Un-anchored Claims)│
               └───────────────────────────┬───────────────────────────┘
                                           │
                                           ▼
               ┌───────────────────────────────────────────────────────┐
               │             5. Audit-Derived Scoring Engine           │
               │   (Compute Normalized 0–100 Scores & Penalty Caps)    │
               └───────────────────────────┬───────────────────────────┘
                                           │
                                           ▼
               ┌───────────────────────────────────────────────────────┐
               │            6. Actionable Remediation Engine           │
               │     (Map Finding ➔ Evidence ➔ Impact ➔ Specific Fix)  │
               └───────────────────────────┬───────────────────────────┘
                                           │
                                           ▼
               ┌───────────────────────────────────────────────────────┐
               │               7. Final Audit Deliverables             │
               │     (Structured JSON Artifact & Executive Report)     │
               └───────────────────────────────────────────────────────┘
```

---

## Architectural Component Separation

To ensure deterministic reliability, eliminate model hallucinations, and guarantee explainable, auditable results, the architecture strictly segregates responsibilities across six core layers:

```
┌─────────────────────────────────────────────────────────────────────────┐
│ 1. Deterministic Extraction Layer (Headless Browser, Parsers, ASTs)     │
├─────────────────────────────────────────────────────────────────────────┤
│ 2. Immutable Evidence Store (Persisted Raw Data, DOMs, HTTP Headers)   │
├─────────────────────────────────────────────────────────────────────────┤
│ 3. Automated Context & Query Synthesis (Entity Inference & Query Gen)   │
├─────────────────────────────────────────────────────────────────────────┤
│ 4. Empirical AI Visibility & LLM Reasoning (Ground-Truth Auditing)     │
├─────────────────────────────────────────────────────────────────────────┤
│ 5. Evidence Validation & Scoring Engine (0–100 Normalized Calibration)  │
├─────────────────────────────────────────────────────────────────────────┤
│ 6. Remediation & Reporting Engine (Prioritized Action Plans)            │
└─────────────────────────────────────────────────────────────────────────┘
```

---

### Layer 1: Deterministic Extraction Layer

- **Responsibility:** Execute objective, non-probabilistic parsing, network fetching, and DOM rendering.
- **Key Operations:**
  - **Crawler & Render Pipeline:** Fetches raw server responses and executes full client-side JavaScript rendering using a headless browser (Playwright).
  - **Robots & Header Parser:** Evaluates `robots.txt` directives per AI bot (`GPTBot`, `ClaudeBot`, `PerplexityBot`, `Google-Extended`, etc.) and parses HTTP headers (`X-Robots-Tag`, `Content-Security-Policy`, `Cache-Control`, `Last-Modified`).
  - **Schema & Metadata Parser:** Extracts embedded JSON-LD scripts, Microdata, OpenGraph tags, Twitter cards, and semantic HTML element trees.
  - **Pre- vs. Post-JS DOM Differ:** Computes differences between server-delivered HTML and hydrated client-side DOM to identify content invisible to non-JavaScript crawlers.
  - **Protocol Checker:** Checks physical endpoint availability (`/sitemap.xml`, `/llms.txt`, `/llms-full.txt`, `/openapi.json`, `/.well-known/ai-plugin.json`).
  - **Frontend Performance & Viewport Metrics:** Computes observable Core Web Vitals (LCP, CLS, TTFB, TBT), responsive viewport metrics, touch target dimensions, and WCAG contrast ratios.

---

### Layer 2: Immutable Evidence Store

- **Responsibility:** Capture and persist all raw audit artifacts with deterministic content addressing and unique Evidence IDs.
- **Evidence Artifacts:**
  - `EVID-DOM-RAW`: Un-rendered HTTP response HTML payload.
  - `EVID-DOM-RENDERED`: Fully hydrated post-JavaScript DOM snapshot.
  - `EVID-HTTP-HEADERS`: Raw HTTP request and response header dump.
  - `EVID-ROBOTS-TXT`: Raw `robots.txt` text content and parsed directive AST.
  - `EVID-SITEMAP-XML`: Sitemap XML content, status verification, and URL registry.
  - `EVID-SCHEMA-JSONLD`: Extracted and normalized JSON-LD schema blocks.
  - `EVID-TEXT-BLOCKS`: Cleaned text blocks mapped to source DOM selectors and line positions.
  - `EVID-AI-VISIBILITY`: Empirical test records `{ query, ai_system, raw_response, citations, evidence_ids }`.
  - `EVID-SCREENSHOTS`: Viewport renders (Desktop 1440px, Mobile 390px) for visual above-the-fold clarity analysis.
- **Core Principle:** Evidence artifacts are **immutable**. LLM analysis and scoring modules are strictly forbidden from inspecting external live websites directly; all reasoning must be performed over the Evidence Store.

---

### Layer 3: Automated Context Discovery & Entity Inference

- **Responsibility:** Automatically construct the brand's canonical profile and domain understanding without requiring manual user input.
- **Inference Pipeline:**
  1. **Canonical Entity Derivation:** Aggregates brand name, legal entity, logos, social links (`sameAs`), and contact details from `Organization` schema, `<title>`, footer copy, and `/about` or `/contact` pages.
  2. **Core Offerings & Positioning:** Extracts core value propositions, product/service categories, and target audience definitions from above-the-fold hero sections and navigation taxonomy.
  3. **Discovery Query Generation:** Automatically generates two classes of queries for empirical AI visibility testing:
     - *Branded Specific Queries*: e.g., "What does [Brand] do?", "What is [Brand]'s pricing model?", "What are the core features of [Brand]'s product?"
     - *Broad Categorical Discovery Queries*: e.g., "What are the best [Industry Category] tools for [Target Audience]?"

---

### Layer 4: Structural AI Readiness vs. Observed AI Visibility

A critical architectural pillar of this system is the rigorous separation between **Structural AI Readiness** and **Observed AI Visibility**:

```
                               AI Readiness
                                    │
         ┌──────────────────────────┴──────────────────────────┐
         ▼                                                     ▼
1. Structural AI Readiness                           2. Observed AI Visibility
(Can AI systems technically access & parse?)         (Does the brand actually appear & get cited?)
─────────────────────────────────────────            ─────────────────────────────────────────
• robots.txt AI bot permissions                      • Brand mention rate in AI responses
• SSR vs CSR JavaScript accessibility                • Citation & source link attribution rate
• Schema.org JSON-LD & entity markup                 • Prominence rank in multi-brand answers
• /llms.txt standard compliance                      • Factual correctness of AI assertions
• Heading & tabular data machine-readability         • Entity disambiguation vs namesake conflation
```

#### Empirical AI Visibility Evaluation Loop
1. The system dispatches derived test queries to available AI/search discovery engines.
2. The raw response, cited URLs, and ranking positions are captured as immutable evidence.
3. The LLM Evaluator compares the generated response against ground-truth facts extracted from the brand's website.
4. Metrics recorded:
   - **Mention Rate**: Did the AI mention the brand? (Yes / No)
   - **Citation Rate**: Did the AI cite the audited domain as a reference? (Yes / No)
   - **Prominence**: Was the brand recommended first, listed neutrally, or omitted?
   - **Factual Accuracy**: Did the AI state correct pricing, capabilities, and positioning?
   - **Source Quality**: Were the citations authoritative or outdated third-party forums?

---

### Layer 5: Inferred On-Site Engagement (No Fabricated Analytics)

Because the audit operates strictly with URL-only input, private analytics (e.g., Google Analytics bounce rates, session durations, conversion funnels) cannot be observed.

**Architectural Rule**: The system **never fabricates behavioral metrics**. Instead, On-site Engagement is inferred exclusively from observable technical, structural, visual, and informational attributes:
- **First-Visit Clarity**: Evaluated from above-the-fold layout, value proposition clarity, and visual hierarchy.
- **Content Engagement**: Evaluated from paragraph lengths, readability indices, and visual content aids.
- **Navigation & Findability**: Evaluated from click depth to key pages, header/footer structure, and internal search parameters.
- **CTA & User Journey**: Evaluated from button contrast, clear action labels, form field counts, and valid target links.
- **Performance**: Evaluated from observable Core Web Vitals (LCP, CLS, TTFB, TBT).
- **Mobile UX**: Evaluated from responsive viewport layout, touch target sizes, and horizontal overflow checks.
- **Trust & Credibility**: Evaluated from presence of Privacy Policy, Terms, contact information, verifiable client logos, and certifications.
- **Accessibility**: Evaluated from observable WCAG AA criteria (form labels, accessible names, contrast ratios, document lang).
- **AI-Agent Readiness**: Evaluated from `/llms.txt`, discoverable OpenAPI specs, and predictable search query APIs.

---

### Layer 6: Evidence Validation & Calibrated Scoring

- **Evidence Validation Rules:**
  1. Every generated finding must cite one or more valid Evidence IDs from the Evidence Store.
  2. Any finding lacking verifiable evidence is stripped during validation.
  3. **Missing Evidence Rule**: When a signal cannot be determined from public observation (e.g., private backlink graphs), it is marked as `Unknown / Unavailable` rather than `Failed`.
- **Scoring Engine:**
  - Computes sub-scores (0–100) across all 6 Off-site and 9 On-site sub-pillars using calibrated, weighted formulas.
  - Critical blockers (e.g., total AI crawler block or invalid SSL) impose hard penalty caps on their respective categories.
  - Scores are explicitly presented as **Audit-Derived Readiness Indexes**, never misattributed as proprietary search engine ranking scores.

---

### Layer 7: Remediation & Output Artifacts

- **Actionable Remediation Pipeline:**
  Each finding is structured as:
  $$\text{Finding} \longrightarrow \text{Evidence ID} \longrightarrow \text{Impact Assessment} \longrightarrow \text{Specific Remediation Code / Copy}$$
- **Standardized Deliverables:**
  - `audit_report.json`: Machine-readable JSON artifact conforming to the Agent Skill Marketplace schema.
  - `executive_summary.md`: Human-readable executive markdown report with visual scoreboards, critical blockers, and prioritized recommendations.

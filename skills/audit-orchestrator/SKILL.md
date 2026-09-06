---
name: Audit Orchestrator
description: Master orchestrator and sole entrypoint skill for coordinating end-to-end Brand AI Readiness Audits across Off-site Discoverability and On-site Engagement using URL-only input.
---

# Audit Orchestrator Skill

## Purpose
The **Audit Orchestrator** is the master entrypoint skill for the Brand AI Readiness Audit package. It receives **strictly a website URL** (`target_url`), derives all necessary brand context automatically, initializes the immutable Evidence Store, coordinates execution across specialized audit sub-skills, validates evidence grounding, and synthesizes normalized scores and actionable remediation reports.

---

## Input Constraint & Automated Context Derivation
The orchestrator operates under a strict **URL-only input constraint**. It does **NOT** require or accept user-provided `brand_domain_context`, `canonical_brand_profile`, keyword lists, or private analytics credentials.

All brand context is derived internally via the **Automated Context Discovery Engine**:
1. Crawls homepage, `/about`, `/contact`, `/pricing`, and sitemap.
2. Extracts brand name, legal entity, official logos, core product/service offerings, and value propositions.
3. Automatically synthesizes candidate branded queries (*"What does [Brand] do?"*, *"What is [Brand]'s pricing model?"*) and categorical discovery queries (*"What are the best [Category] tools for [Target Audience]?"*).

---

## High-Level Responsibilities

```
                                [ target_url ]
                                      │
                                      ▼
                        1. Automated Context Discovery
                                      │
                                      ▼
                        2. Crawl & Render Engine
                                      │
                                      ▼
                        3. Immutable Evidence Store
                                      │
         ┌────────────────────────────┴────────────────────────────┐
         ▼                                                         ▼
Dimension A: Off-site Discoverability                     Dimension B: On-site Engagement
├── crawl-render-audit                                    └── engagement-audit
├── structured-data-audit                                     ├── First-Visit Clarity
├── fact-quality-audit                                        ├── Content Scannability
├── freshness-corroboration                                   ├── Navigation & Findability
└── entity-identity-audit                                     ├── CTA & User Journey
                                                              ├── Performance & Stability
                                                              ├── Mobile UX
                                                              ├── Trust & Credibility
                                                              ├── Observable Accessibility
                                                              └── AI-Agent Readiness
         │                                                         │
         └────────────────────────────┬────────────────────────────┘
                                      │
                                      ▼
                        4. Evidence Validation Engine
                                      │
                                      ▼
                        5. Normalized Scoring & Penalty Caps
                                      │
                                      ▼
                        6. Actionable Recommendations
                                      │
                                      ▼
                        7. Final Audit Deliverables
```

1. **Pipeline Initialization & Context Derivation**: Parse `target_url`, discover core brand pages, and construct internal brand context.
2. **Crawl & Render Execution**: Trigger headless browser (Playwright) to capture raw HTML, hydrated post-JS DOM, HTTP headers, and Core Web Vitals.
3. **Evidence Store Ingestion**: Store all raw payloads with unique deterministic Evidence IDs (`EVID-DOM-RAW`, `EVID-SCHEMA-JSONLD`, `EVID-AI-VISIBILITY`, etc.).
4. **Sub-Skill Dispatch**: Coordinate parallel execution across specialized audit skills:
   - `crawl-render-audit`: Technical SEO, AI crawler `robots.txt`, SSR vs CSR DOM delta, sitemaps.
   - `structured-data-audit`: Schema.org JSON-LD, Microdata, OpenGraph, semantic HTML.
   - `fact-quality-audit`: Proposition extraction, claim ambiguity, cross-page contradictions, hallucination vulnerability.
   - `freshness-corroboration`: Temporal metadata (`dateModified`, `<lastmod>`), update cadence, external corroboration.
   - `entity-identity-audit`: Internally derived canonical entity model, cross-page NAP consistency, `sameAs` links.
   - `engagement-audit`: Comprehensive 9-pillar On-site Engagement evaluation.
5. **Observed AI Visibility Testing**: Dispatches derived queries to AI search engines, recording query + raw response + citations + prominence + accuracy into the Evidence Store.
6. **Evidence Validation**: Enforces that 100% of reported findings cite verifiable Evidence IDs. Strips ungrounded claims.
7. **Scoring & Synthesis**: Computes normalized 0–100 sub-scores and overall readiness index using calibrated weights.
8. **Report Generation**: Emits `audit_report.json` and `executive_summary.md`.

---

## Inputs
- **`target_url`** *(string, required)*: Primary brand domain or URL to audit (e.g., `https://example.com`).
- **`config_path`** *(string, optional)*: Path to custom `audit-config.yaml` for adjusting crawl depth or feature flags.

---

## Outputs

### 1. `audit_report.json`
Machine-readable audit artifact containing:
- `target_url`: Audited domain.
- `timestamp`: Audit execution timestamp.
- `overall_score`: Composite Brand AI Readiness Score (0–100).
- `off_site_discoverability`:
  - `score`: Dimension A composite score (0–100).
  - `sub_scores`: Breakdown across On-page SEO, Technical SEO, Authority, AI/GEO Discoverability, Machine Readability, Freshness.
- `on_site_engagement`:
  - `score`: Dimension B composite score (0–100).
  - `sub_scores`: Breakdown across 9 observable engagement pillars.
- `ai_visibility_tests`: Array of empirical test records `{ query, ai_system, raw_response, brand_mentioned, domain_cited, prominence_rank, factual_accuracy_score, evidence_ids }`.
- `findings`: Array of categorized findings with severity (`Critical`, `High`, `Medium`, `Low`), impact, and evidence IDs.
- `recommendations`: Prioritized, actionable remediation steps.

### 2. `executive_summary.md`
Markdown report formatted with executive scoreboards, key findings, and prioritized developer/content remediation checklists.

---

## Scoring Model & Hierarchy

$$\text{Overall Score} = (0.50 \times \text{Off-site Discoverability}) + (0.50 \times \text{On-site Engagement})$$

```
Brand AI Readiness Audit
─────────────────────────
Target: example.com
Overall Score: 78/100

Off-site Discoverability: 72/100
On-site Engagement:       84/100

OFF-SITE DISCOVERABILITY (72/100)
├── On-page SEO & Content Quality:  81
├── Technical SEO & Crawlability:   76
├── Off-page Authority:             61 (Observable only)
├── AI / GEO Discoverability:       69 (Structural: 78, Observed: 60)
├── Machine Readability & Entity:   82
└── Freshness & Corroboration:      73

ON-SITE ENGAGEMENT (84/100)
├── First-Visit Clarity:            91
├── Content Scannability:           86
├── Navigation & Findability:       88
├── CTA & User Journey:             79
├── Performance & Stability:        75
├── Mobile UX & Responsiveness:     90
├── Trust & Credibility:            83
├── Observable Accessibility:       81
└── AI-Agent Interaction Readiness: 62
```

---

## Evidence & Traceability Rules
- **Rule 1**: Every finding must cite one or more valid Evidence IDs from the Evidence Store.
- **Rule 2**: If an external metric cannot be observed, mark as `Unknown / Unavailable` rather than `Failed`.
- **Rule 3**: Never fabricate behavioral analytics (bounce rate, session duration) — infer engagement from observable UI/UX structure.

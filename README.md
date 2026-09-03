# Brand AI Readiness Audit

> **Adobe University Hackathon 2026 — Round 3 Project**  
> An Agent Skill Marketplace package designed to perform comprehensive, evidence-first audits of brand websites for AI discoverability, factual content quality, entity consistency, structured data, and AI interaction readiness.

---

> [!IMPORTANT]  
> **Development Status: Initial Scaffolding Phase**  
> This repository is currently in the scaffolding and architecture phase. The audit skills, crawler pipelines, and analytical evaluation logic defined here represent planned specifications. No active crawling or auditing logic is implemented yet.

---

## 🎯 Purpose & Problem Statement

As Generative Engine Optimization (GEO), Answer Engine Optimization (AEO), and autonomous AI agents become primary discovery channels for consumers, brands face a critical challenge: **How visible, readable, accurate, and authoritative is their digital presence to AI models and agents?**

Traditional SEO tools focus on search engine keyword rankings and page speed performance. They fail to evaluate:
- **AI Accessibility & Rendering:** Can LLM web crawlers (e.g., GPTBot, ClaudeBot, PerplexityBot) parse and execute client-side JS to reach key brand data?
- **Factual Machine-Readability:** Are claims, product specs, pricing, and policies clear and un-ambiguous enough to prevent AI hallucinations?
- **Entity Identity & Consistency:** Does the brand present a unified, canonical entity model that Knowledge Graphs can reliably absorb?
- **Freshness & Corroboration:** Are update timestamps explicit, and is the brand's core data corroborated across authoritative web sources?

The **Brand AI Readiness Audit** package addresses these challenges by delivering an evidence-backed framework that assesses a website's readiness for the AI-driven search ecosystem.

---

## 🏗️ High-Level Architecture

The framework operates on an **Evidence-First Architecture** (see [`docs/decisions.md`](docs/decisions.md) - ADR-001). Deterministic checks extract verified evidence first, and LLM reasoning operates exclusively on that evidence rather than inventing ungrounded observations.

```
Website Under Audit
  │
  ▼
Crawl & Rendering Pipeline (Playwright / HTTP Parser)
  │
  ▼
Evidence Store (DOM Snapshots, Headers, Schema JSON-LD, Text Snippets)
  │
  ▼
Specialized Audit Skills (Parallel Execution)
  ├── 1. Crawl & Render Audit
  ├── 2. Structured Data Audit
  ├── 3. Fact Quality Audit
  ├── 4. Freshness & Corroboration
  ├── 5. Entity Identity & Consistency
  └── 6. On-Site AI Engagement
  │
  ▼
Evidence Validation & Normalized Scoring
  │
  ▼
Prioritized Remediation & Executive Audit Report
```

---

## 🧩 Marketplace Skills Summary

The package exposes a single entrypoint skill—**`audit-orchestrator`**—which coordinates six specialized audit sub-skills:

| Skill | Path | Description |
| :--- | :--- | :--- |
| **`audit-orchestrator`** *(Entrypoint)* | [`skills/audit-orchestrator/SKILL.md`](skills/audit-orchestrator/SKILL.md) | Coordinates end-to-end audit workflow, invokes sub-skills, aggregates findings, and computes final scores. |
| **`crawl-render-audit`** | [`skills/crawl-render-audit/SKILL.md`](skills/crawl-render-audit/SKILL.md) | Evaluates robots.txt AI rules, HTTP headers, SSR vs. CSR rendering, and crawler access limits. |
| **`structured-data-audit`** | [`skills/structured-data-audit/SKILL.md`](skills/structured-data-audit/SKILL.md) | Inspects JSON-LD, Microdata, OpenGraph, and semantic HTML schema validity and coverage. |
| **`fact-quality-audit`** | [`skills/fact-quality-audit/SKILL.md`](skills/fact-quality-audit/SKILL.md) | Measures claim clarity, ambiguity, factual consistency, and vulnerability to model hallucination. |
| **`freshness-corroboration`** | [`skills/freshness-corroboration/SKILL.md`](skills/freshness-corroboration/SKILL.md) | Validates modification dates, content freshness signals, and external source corroboration. |
| **`entity-identity-audit`** | [`skills/entity-identity-audit/SKILL.md`](skills/entity-identity-audit/SKILL.md) | Checks brand Name-Address-Phone (NAP) uniformity, Organization schema, and Knowledge Graph alignment. |
| **`engagement-audit`** | [`skills/engagement-audit/SKILL.md`](skills/engagement-audit/SKILL.md) | Assesses readiness for direct AI agent interaction, API availability, and site search interoperability. |

---

## 📁 Repository Structure

```
brand-ai-readiness-audit/
├── README.md                          # Project documentation and roadmap
├── marketplace.json                   # Agent Skill Marketplace manifest
├── LICENSE                            # MIT License
├── .gitignore                         # Build, environment, and runtime ignore patterns
│
├── docs/                              # Project design and research documentation
│   ├── audit-matrix.md                # Signal, evidence, scoring, and severity matrix
│   ├── architecture.md                # System flow, separation of concerns, and pipeline
│   ├── research.md                    # Research findings and tool evaluations log
│   └── decisions.md                   # Architecture Decision Records (ADRs)
│
├── skills/                            # Agent Skill Marketplace definitions
│   ├── audit-orchestrator/            # Entrypoint orchestrator skill
│   │   └── SKILL.md
│   ├── crawl-render-audit/            # Crawl accessibility audit skill
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   └── references/
│   ├── structured-data-audit/         # Structured data audit skill
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   └── references/
│   ├── fact-quality-audit/            # Fact & content quality audit skill
│   │   ├── SKILL.md
│   │   └── references/
│   ├── freshness-corroboration/        # Content freshness audit skill
│   │   ├── SKILL.md
│   │   └── references/
│   ├── entity-identity-audit/         # Entity & identity audit skill
│   │   ├── SKILL.md
│   │   └── references/
│   └── engagement-audit/              # On-site AI engagement skill
│       ├── SKILL.md
│       └── references/
│
├── tests/                             # Evaluation schemas and mock test data
│   ├── test-sites.json                # Test target site registry
│   ├── expected-findings.json         # Benchmark audit results schema
│   └── evaluation.md                  # Verification and benchmark plan
│
├── src/                               # Source code modules (scaffolding)
│   ├── crawler/                       # Web crawling and rendering engines
│   ├── extraction/                    # DOM, JSON-LD, and text extractor modules
│   ├── analysis/                      # Deterministic and LLM evaluation engines
│   └── reporting/                     # Report generation and export utilities
│
└── config/                            # Runtime configuration
    └── audit-config.yaml              # Audit thresholds and feature flags
```

---

## 🚀 Development Roadmap

- [x] **Phase 1: Project Scaffolding & Marketplace Manifest** (Current)
- [ ] **Phase 2: Day-1 Research & Audit Matrix Refinement**
- [ ] **Phase 3: Crawler Engine & Evidence Store Implementation**
- [ ] **Phase 4: Specialized Skill Logic & Deterministic Checkers**
- [ ] **Phase 5: Benchmark Evaluation & Report Generator**

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

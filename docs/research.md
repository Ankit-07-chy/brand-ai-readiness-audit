# Research Log & Bibliography

This document serves as the research log for the Brand AI Readiness Audit project. It tracks literature reviews, standards, tool evaluations, and empirical findings.

---

## 1. AI Discoverability Research

*Log research on Generative Engine Optimization (GEO), Answer Engine Optimization (AEO), and LLM search indexing behaviors.*

- **Focus Areas:** Query intent matching for AI engines, direct answer density, citation triggers in ChatGPT Search / Perplexity / Gemini.
- **Notes & Findings:** *(To be populated during Day-1 research)*

---

## 2. Crawler & Rendering Research

*Log research on AI crawler behaviors, User-Agent identification, and JavaScript rendering constraints.*

- **Focus Areas:** Differences in how `GPTBot`, `ClaudeBot`, `Bytespider`, `Google-Extended`, and `PerplexityBot` handle dynamic client-side rendering (CSR), headless browsers vs lightweight HTTP clients.
- **Notes & Findings:** *(To be populated during Day-1 research)*

---

## 3. Structured Data Research

*Log research on Schema.org specifications, JSON-LD parsing, and entity relationship extraction.*

- **Focus Areas:** Essential schemas for AI understanding (`Organization`, `Product`, `FAQPage`, `Article`, `LocalBusiness`), validation tooling, microdata vs JSON-LD preferences of modern LLMs.
- **Notes & Findings:** *(To be populated during Day-1 research)*

---

## 4. Content & Fact Quality Research

*Log research on fact verification, claim extraction, and hallucination reduction mechanisms.*

- **Focus Areas:** Measuring semantic ambiguity, proposition extraction techniques, automated factuality scoring metrics.
- **Notes & Findings:** *(To be populated during Day-1 research)*

---

## 5. Content Freshness Research

*Log research on temporal signals in web documents and LLM recency bias.*

- **Focus Areas:** Metadata date extraction reliability (`dateModified`, `<lastmod>`, HTTP headers), impact of content freshness on AI model citations.
- **Notes & Findings:** *(To be populated during Day-1 research)*

---

## 6. Entity Identity Research

*Log research on Knowledge Graph entity representation, Name-Address-Phone (NAP) consistency, and web identity resolution.*

- **Focus Areas:** Wikidata / DBpedia entity mapping, `sameAs` URI validation, cross-platform identity reconciliation.
- **Notes & Findings:** *(To be populated during Day-1 research)*

---

## 7. On-Site AI Engagement Research

*Log research on emerging protocols for direct AI agent interaction with web servers.*

- **Focus Areas:** `/llms.txt` proposal standard, OpenAPI schema discovery, AI plugin manifests, agentic protocol interoperability.
- **Notes & Findings:** *(To be populated during Day-1 research)*

---

## 8. Tools Evaluated

| Tool / Library | Category | Evaluation Status | Pros / Cons | Decision |
| :--- | :--- | :--- | :--- | :--- |
| **Playwright** | Rendering / Crawling | Pending Evaluation | Headless browser execution; supports JS-rendered DOM extraction. | TBD |
| **BeautifulSoup4 / extruct** | Microdata / JSON-LD Extraction | Pending Evaluation | Python native; fast parsing of embedded schema metadata. | TBD |
| **Schema.org Validator API** | Structured Data Validation | Pending Evaluation | Official validation rules; potential rate limits. | TBD |
| **pydantic** | Data Validation & Schemas | Pending Evaluation | Type safety and strict data modeling for audit evidence. | TBD |

---

## 9. Sources & References

*List academic papers, official specifications, vendor documentation, and standards documents here.*

- [Schema.org Official Specification](https://schema.org/)
- [The llms.txt Standard Proposal](https://llmstxt.org/)
- [Robots.txt Specifications & User-Agent Guidelines](https://www.robotstxt.org/)

---

## 10. Research Decisions Log

- **Log Entries:** *(To be populated as research findings dictate architectural updates)*

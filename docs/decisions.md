# Architecture Decision Records (ADRs)

This document logs significant architectural decisions made during the design and development of the Brand AI Readiness Audit system.

---

## ADR-001: Evidence-first architecture

### Context
Auditing a brand's website for AI readiness requires analyzing both deterministic technical criteria (e.g., `robots.txt` rules, Schema validation syntax) and qualitative content nuances (e.g., claim ambiguity, brand messaging consistency). 

Relying solely on LLM evaluation without structured evidence collection creates risk: models can hallucinate page elements, misjudge raw header configurations, or generate un-anchored observations that cannot be independently audited or reproduced by engineering teams.

### Decision
Deterministic checks should produce evidence first, and LLM reasoning should operate on that evidence rather than inventing observations.

### Consequence & Implementation Rules
1. Every audit skill must separate its logic into **Evidence Extraction** (deterministic) and **Evidence Analysis** (deterministic + LLM).
2. The Evidence Store holds immutable raw artifacts (DOM HTML snapshots, parsed JSON-LD payloads, HTTP response headers, text blocks).
3. LLM prompts must ingest extracted evidence blocks and include supporting evidence IDs in their output findings.
4. Any audit finding lacking an associated evidence payload is marked invalid during validation.

### Reason
Improve traceability, reduce hallucination, and make audit findings explainable to stakeholders.

### Status
**Proposed**

---
name: Audit Orchestrator
description: Master entrypoint skill for orchestrating end-to-end brand AI readiness audits across specialized sub-skills.
---

# Audit Orchestrator Skill

## Purpose
The **Audit Orchestrator** is the sole marketplace entrypoint skill for the Brand AI Readiness Audit package. It validates the target URL, coordinates the execution of registered audit sub-skills, aggregates evidence and findings, enforces error isolation, and synthesizes the overall readiness score.

## When to Use
Invoked as the primary CLI or API entrypoint when initiating an AI readiness audit for a web URL.

## Execution Workflow
1. **URL Validation:** Validates that the provided target URL contains a valid HTTP/HTTPS scheme and domain host.
2. **Sub-Skill Delegation:** Dispatches audit execution to registered specialized sub-skills (`crawl-render-audit`, `structured-data-audit`).
3. **Error Isolation:** Encapsulates skill-level exceptions, generating error findings for failed skills without crashing the orchestrator pipeline.
4. **Aggregation & Scoring:** Aggregates findings from all executed sub-skills and computes a deterministic summary score.
5. **Output Generation:** Returns a unified `AuditReport` JSON structure.

## Registered Sub-Skills (Day 3 Scope)
- `crawl-render-audit`: Evaluates HTTP status, robots metadata directives, and pre-rendered DOM availability.
- `structured-data-audit`: Audits JSON-LD presence, syntax validity, schema types, entity completeness, and visible content consistency.

## Code Entrypoint
- Implementation module: [`src/orchestrator.py`](file:///d:/Adobe/brand-ai-readiness-audit/src/orchestrator.py)
- Unit tests: [`tests/test_orchestrator.py`](file:///d:/Adobe/brand-ai-readiness-audit/tests/test_orchestrator.py)

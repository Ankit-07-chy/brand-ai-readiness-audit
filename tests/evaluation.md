# Audit Evaluation & Verification Plan

This document outlines the testing methodology, ground truth benchmarks, and evaluation metrics used to validate the accuracy of the Brand AI Readiness Audit package.

---

## 1. Evaluation Goals

1. **Deterministic Accuracy:** Ensure 100% precision on rule-based checks (`robots.txt` parsing, JSON-LD syntax validation, header inspection).
2. **LLM Evidence Grounding:** Verify that 100% of LLM reasoning findings map back to valid raw evidence IDs.
3. **Reproducibility:** Guarantee identical scoring outputs when evaluating static DOM/header snapshot sets.
4. **False-Positive Minimization:** Benchmark hallucination flags and schema error flags against human expert audit baselines.

---

## 2. Benchmark Dataset (`test-sites.json`)

The test suite evaluates a curated list of diverse website architectures:
- **Client-Side Rendered (CSR):** React/Vue web applications relying on dynamic hydration.
- **Server-Side Rendered (SSR):** Static and traditional CMS sites with immediate HTML payloads.
- **E-Commerce Portals:** High-density product pages with complex JSON-LD markup.
- **Enterprise SaaS:** Documentation-heavy sites with developer endpoints and security policies.

---

## 3. Verification Metrics

- **Precision & Recall on Skill Flags:** $\text{Precision} = \frac{\text{True Positive Findings}}{\text{Total Flagged Findings}}$
- **Evidence Traceability Index:** Percentage of generated finding cards that contain valid, extractable evidence citations.
- **Schema Validation Match Rate:** Agreement percentage between internal Schema checkers and official Schema.org API results.

---

## 4. Execution Workflow

```bash
# Example test execution command (scaffolding placeholder)
pytest tests/
```

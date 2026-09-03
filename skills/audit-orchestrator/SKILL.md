---
name: Audit Orchestrator
description: Master entrypoint skill for orchestrating end-to-end brand AI readiness audits across crawlability, structured data, content quality, freshness, entity consistency, and AI engagement.
---

# Audit Orchestrator Skill

## Purpose
The **Audit Orchestrator** is the sole marketplace entrypoint skill for the Brand AI Readiness Audit package. It coordinates the execution of specialized audit sub-skills, aggregates evidence, enforces validation rules, and synthesizes overall readiness scores and prioritized remediation reports.

## When to Use
Use this skill when initiating a complete or modular AI readiness audit for a brand's web domain or set of target URLs.

## High-Level Responsibilities
1. **Pipeline Initialization:** Parse audit target configuration, resolve target URLs, and initialize the immutable Evidence Store.
2. **Sub-Skill Dispatch:** Coordinate execution across the specialized audit skills:
   - `crawl-render-audit`
   - `structured-data-audit`
   - `fact-quality-audit`
   - `freshness-corroboration`
   - `entity-identity-audit`
   - `engagement-audit`
3. **Evidence Aggregation & Validation:** Ensure all findings produced by sub-skills are grounded in deterministic evidence items.
4. **Scoring & Synthesis:** Compute normalized composite scores (0–100) across categories and compile executive audit reports.

## Inputs
- **`target_url`** *(string, required)*: Primary brand domain or URL to audit.
- **`config_path`** *(string, optional)*: Path to custom `audit-config.yaml`.
- **`categories`** *(array of strings, optional)*: List of specific sub-skill IDs to execute (defaults to all).

## Outputs
- **`audit_report.json`**: Structured audit results, evidence mappings, category sub-scores, and overall AI readiness index.
- **`executive_summary.md`**: Markdown summary containing key findings and prioritized remediation steps.

## Evidence Expectations
- Aggregates evidence manifests from all dispatched sub-skills.
- Requires 100% trace mapping from generated findings to raw evidence IDs.

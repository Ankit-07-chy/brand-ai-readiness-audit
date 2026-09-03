---
name: On-Site AI Engagement Audit
description: Assesses on-site search readiness, conversational endpoint availability, llms.txt compliance, and interactive AI agent interoperability.
---

# On-Site AI Engagement Audit Skill

## Purpose
Evaluates how effectively autonomous AI agents can interact with, search, and navigate a brand's website to perform tasks or retrieve machine-formatted developer/product metadata.

## When to Use
Invoked by `audit-orchestrator` during the interactive agent readiness evaluation.

## High-Level Responsibilities
- Check for `/llms.txt` and `/llms-full.txt` standard file presence and formatting.
- Audit OpenAPI / REST endpoint discovery (`/openapi.json`, `/.well-known/ai-plugin.json`).
- Evaluate search form accessibility, URL query parameter transparency, and response formatting.
- Assess conversational assistant / chatbot interoperability.

## Inputs
- `domain_root_url` (string)
- `discovered_api_specs` (array of OpenAPI schemas)

## Outputs
- AI Engagement sub-score (0–100)
- Protocol compliance checklist (`llms.txt`, OpenAPI, search parameters)

## Evidence Expectations
- `/llms.txt` GET response headers and body
- OpenAPI endpoint probe logs
- Search form DOM element attributes

---
name: Fact Quality Audit
description: Evaluates factual precision, claim verifiability, content clarity, and hallucination vulnerability across brand assets.
---

# Fact Quality Audit Skill

## Purpose
Evaluates textual content across key brand pages to measure claim precision, semantic clarity, and vulnerability to AI hallucination or misinterpretation during retrieval-augmented generation (RAG).

## When to Use
Invoked by `audit-orchestrator` during the semantic quality analysis phase.

## High-Level Responsibilities
- Extract core factual propositions, numerical claims, pricing details, and policy assertions.
- Flag ambiguous phrasing, marketing hyperbole lacking supporting data, or contradictory statements.
- Evaluate clarity of technical specifications and feature descriptions.
- Highlight content blocks prone to LLM hallucination during RAG extraction.

## Inputs
- `extracted_text_blocks` (array of text nodes mapped to DOM elements)
- `brand_domain_context` (string description of core brand offerings)

## Outputs
- Fact quality sub-score (0–100)
- Ambiguity and contradiction flag report with text snippet line numbers

## Evidence Expectations
- Extracted raw text blocks with source URL and DOM selector paths
- Proposition extraction tables

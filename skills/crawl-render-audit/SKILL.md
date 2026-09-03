---
name: Crawl & Render Audit
description: Evaluates robots.txt rules, HTTP headers, SSR vs CSR rendering parity, and AI crawler accessibility.
---

# Crawl & Render Audit Skill

## Purpose
Audits the technical accessibility of target web pages for AI user-agent crawlers (`GPTBot`, `ClaudeBot`, `PerplexityBot`, etc.), identifying blocks, rendering delays, and indexability hurdles.

## When to Use
Invoked by `audit-orchestrator` during the initial discovery stage of a brand audit.

## High-Level Responsibilities
- Parse `robots.txt` rules against standard AI User-Agent strings.
- Inspect HTTP headers (`X-Robots-Tag`, `Content-Type`, `Cache-Control`).
- Compare Pre-JavaScript HTML with Post-JavaScript rendered DOM to identify content invisible to non-JS crawlers.
- Check XML sitemap accessibility and index completeness.

## Inputs
- `target_urls` (array of strings)
- `user_agents` (array of AI crawler user-agent strings)

## Outputs
- Crawl accessibility score (0–100)
- Array of crawl block findings with HTTP status and directive evidence

## Evidence Expectations
- Raw `robots.txt` file content
- HTTP response header dumps
- Raw vs rendered HTML DOM snapshots

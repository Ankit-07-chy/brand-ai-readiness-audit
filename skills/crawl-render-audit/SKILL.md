---
name: Crawl & Render Audit
description: Evaluates technical SEO, robots.txt AI bot permissions, HTTP headers, pre-JS vs post-JS rendering parity (DOM delta), XML sitemaps, canonicals, and observable performance.
---

# Crawl & Render Audit Skill

## Purpose
The **Crawl & Render Audit** skill evaluates the fundamental technical infrastructure and machine accessibility of a target website. It verifies whether traditional search bots and modern AI crawlers (`GPTBot`, `ClaudeBot`, `PerplexityBot`, `Google-Extended`, `Amazonbot`, `Bytespider`) can fetch, render, and index website assets without technical blockages, client-side rendering failures, or redirect loops.

---

## When to Use
Invoked by `audit-orchestrator` during the initial discovery and technical evaluation phase of an audit.

---

## High-Level Responsibilities

1. **AI User-Agent & `robots.txt` Directive Parsing**:
   - Fetches and parses `robots.txt` against distinct AI crawler User-Agents:
     - `GPTBot` (OpenAI training/retrieval)
     - `OAI-SearchBot` (ChatGPT Search real-time)
     - `ClaudeBot` (Anthropic)
     - `PerplexityBot` (Perplexity AI)
     - `Google-Extended` (Gemini training control)
     - `Bytespider` (ByteDance)
     - `Amazonbot` (Amazon Bedrock/Alexa)
   - Flags blanket blocks (`Disallow: /`) and path-specific crawler restrictions.

2. **HTTP Response & Security Header Inspection**:
   - Evaluates HTTP response status codes (200 OK, 301 clean redirects, 404/410 handling).
   - Detects redirect chains (>2 hops) and circular loops.
   - Inspects `X-Robots-Tag` headers for accidental `noindex` / `nofollow` directives.
   - Audits HTTPS enforcement, SSL certificate validity, and `Strict-Transport-Security` (HSTS).

3. **Client-Side Rendering (CSR) vs. Server-Side Rendering (SSR) Parity**:
   - Calculates the **DOM Delta** between raw pre-JavaScript HTML and fully rendered post-JavaScript DOM.
   - Detects if critical product copy, pricing, FAQs, or navigational links are missing in raw HTML (invisible to lightweight AI fetchers).

4. **XML Sitemap & Canonical Tag Verification**:
   - Verifies `sitemap.xml` availability, schema compliance, and status codes of declared URLs.
   - Validates `<link rel="canonical">` implementation to prevent duplicate indexing.

5. **Observable Performance & Core Web Vitals**:
   - Measures TTFB (Time to First Byte), LCP (Largest Contentful Paint), CLS (Cumulative Layout Shift), and Total Blocking Time (TBT).
   - Flags heavy JavaScript bundles or unoptimized media assets.

---

## Inputs
- **`target_urls`** *(array of strings, required)*: URLs to crawl and analyze.
- **`user_agents`** *(array of strings, optional)*: Specific AI bot User-Agent strings to test against `robots.txt`.

---

## Outputs
- **`technical_score`** *(number, 0–100)*: Normalized Technical SEO & Crawlability score.
- **`findings`** *(array of objects)*:
  - `finding_id`: Unique identifier (e.g., `FIND-CRAWL-001`).
  - `category`: Sub-pillar name.
  - `severity`: `Critical` | `High` | `Medium` | `Low`.
  - `title`: Short descriptive title.
  - `description`: Detailed technical observation.
  - `impact`: Explanation of how this impacts search indexation or AI discovery.
  - `evidence_ids`: Array of referenced Evidence Store keys (`EVID-ROBOTS-TXT`, etc.).
  - `remediation`: Specific, actionable technical fix.
- **`dom_delta_report`**: Token count and content parity metrics across raw vs rendered DOM.

---

## Evidence Expectations
- `EVID-ROBOTS-TXT`: Raw `robots.txt` content and parsed AST per User-Agent.
- `EVID-HTTP-HEADERS`: HTTP status codes, redirect traces, and response headers.
- `EVID-DOM-RAW`: Un-hydrated raw HTML payload.
- `EVID-DOM-RENDERED`: Fully hydrated post-JS DOM snapshot.
- `EVID-SITEMAP-XML`: Sitemap fetch responses and URL status logs.
- `EVID-PERF-METRICS`: Observable browser timing metrics (LCP, CLS, TTFB, TBT).

---

## False-Positive Considerations
- **Staging / Preview Environments**: `Disallow: /` on staging subdomains is intentional and should not be penalized if auditing a live production domain.
- **Anti-DDoS / Rate Limiting**: Cloudflare or firewall challenge pages encountered during automated crawling should be flagged as access limitations rather than site-wide `robots.txt` blocks.
- **Selective Training Bot Restrictions**: A brand may intentionally disallow training bots (e.g., `Bytespider`) while permitting search bots (`PerplexityBot`). This should be reported as an intentional choice with Medium/Informational severity rather than a Critical failure.

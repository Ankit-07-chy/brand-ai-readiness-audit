# Research log

Locked against the Round 3 handout (not a generic GEO toolkit).

## Official problem

- Off-site: AI assistants do not find or cite the brand (Reach -> Read -> Extract -> Trust -> Use).
- On-site: visitors who do arrive do not stay (orientation + action).
- Output: one findings report with evidence, severity, suggested actions. Recommend-only.

## What we will not treat as core defects

- Missing `/llms.txt` or `/llms-full.txt`
- Missing OpenAPI / `ai-plugin.json`
- Missing chatbot
- Missing schema on a non-product page

## Crawler notes

AI crawlers differ on JS execution. Raw HTML vs rendered DOM is a real gap, but Playwright/Chromium cannot ship in the ZIP. Dual path: always HTTP; optional render if the host already has a browser.

## Corroboration sources (public, no paid API)

Wikidata, Wikipedia, official social `sameAs` targets, sitemap lastmod, HTTP Last-Modified. 2-3 sources per identity/date claim is enough.

## References

- [agentskills.io specification](https://agentskills.io/specification)
- [Schema.org](https://schema.org/)
- [robots.txt](https://www.robotstxt.org/)

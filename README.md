# Brand AI Readiness Audit

Adobe University Hackathon 2026 - Round 3.

A **read-only Agent Skill Marketplace**. Give it any public website URL. It reports **why AI assistants cannot find or cite the brand** (off-site discoverability) and **why a visitor who arrives does not stay** (on-site engagement).

Output is **one JSON audit report** (Adobe schema). Recommend-only. Never mutates the site.

> Scaffolding: Python check scripts are not implemented yet. This pass locks the contest contract: marketplace layout, SKILL.md format, report schema, and check definitions.

## What this marketplace must do

**Detect** both halves of the Round 2 problem:

1. **Off-site discoverability** - Reach -> Read -> Extract -> Trust -> Use
2. **On-site engagement** - a visitor (often landing on a deep URL from an AI answer) cannot tell who this is, what they can do, or what to do next

**Report** every finding with evidence, severity, and a suggested action (what to change and how), prioritized by impact. Suggested actions may include proactive improvements even when no explicit defect fired.

## Skills (exactly one entrypoint)

| Skill | Role |
| :--- | :--- |
| `audit-orchestrator` | Entrypoint. Snapshot -> dispatch 6 specialists -> compose one report |
| `crawl-render-audit` | Reach / Read: robots.txt, status, noindex, HTML vs DOM |
| `structured-data-audit` | Extract: JSON-LD parse; Product/Offer completeness on product pages |
| `fact-quality-audit` | Extract: claims, contradictions, missing units, ungrounded superlatives |
| `freshness-corroboration` | Trust: dates, stale content, 2-3 public corroboration sources |
| `entity-identity-audit` | Use: Organization name, `sameAs`, NAP consistency |
| `engagement-audit` | On-site: first impression, nav, breadcrumbs, CTAs |

Each folder independently satisfies [agentskills.io](https://agentskills.io/specification). `SKILL.md` `name` equals the folder name.

## Report schema (Adobe floor)

Required keys. Extra fields (`category`, `confidence`, `why_it_matters`, `affected_urls`) are allowed.

```json
{
  "site": "example.com",
  "audited_at": "2026-09-20T14:32:00Z",
  "summary": {
    "total_findings": 6,
    "critical": 1,
    "high": 2,
    "medium": 3
  },
  "findings": [
    {
      "id": "F-001",
      "title": "No JSON-LD structured data on product pages",
      "severity": "high",
      "evidence": "Crawled 12 product pages; 0/12 contain schema.org markup.",
      "suggested_action": {
        "summary": "Add Product/Offer JSON-LD to every product page.",
        "priority": "high"
      }
    }
  ]
}
```

Severity is lowercase: `critical` | `high` | `medium` | `low`. `suggested_action` is an **object**, not a string. **0-100 composite scores are not the contest output.**

## Guardrails

- Read-only. Respect `robots.txt`. Polite delays. No login, no form posts, no writes.
- Runtime under 5 minutes. Submission ZIP <= 45 MB (Adobe cap 50 MB).
- Default fetch is Python stdlib HTTP + HTML parse. Playwright is optional and **must not** ship Chromium in the ZIP.
- Never report "missing schema" blindly. Never treat missing `/llms.txt` as a core defect.
- Generalize. Do not overfit one site.

## Layout

```
brand-ai-readiness-audit/
|-- marketplace.json
|-- skills/
|   |-- audit-orchestrator/SKILL.md     # entrypoint: true
|   |-- crawl-render-audit/
|   |-- structured-data-audit/
|   |-- fact-quality-audit/
|   |-- freshness-corroboration/
|   |-- entity-identity-audit/
|   `-- engagement-audit/
|-- docs/
|-- tests/
|-- src/            # implementation (not yet)
`-- config/
```

## Authors

Shivam ([shivam99392677](https://github.com/shivam99392677)), Ankit Kumar ([Ankit-07-chy](https://github.com/Ankit-07-chy))

## License

MIT. See [LICENSE](LICENSE).

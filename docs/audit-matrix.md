# Audit matrix

Concrete checks. Each finding must name a URL, quote evidence, and give a suggested action.

Golden rules:
- **Never** report "missing schema" blindly. Only flag schema that is present-and-broken, or Product/Offer that is incomplete **on pages that are already product pages**.
- **Never** treat missing `/llms.txt`, OpenAPI, or a chat widget as a core engagement defect.
- Engagement is **visitor orientation**, not agent-protocol discovery.

Severity = impact x scope x confidence. Values: `critical` | `high` | `medium` | `low`.

## Off-site discoverability

### crawl-render-audit (Reach / Read)

| ID | Check | Evidence | Typical severity |
| :--- | :--- | :--- | :--- |
| CR-01 | robots.txt Disallow for GPTBot / ClaudeBot / PerplexityBot / Google-Extended / * | raw robots.txt + matching UA | critical if core paths blocked |
| CR-02 | Non-200, redirect loops, http to https traps, soft-404 | status chain, final URL | high |
| CR-03 | HTML vs rendered DOM gap (optional Playwright) | text/JSON-LD present in DOM, absent in raw HTML | high if facts/prices only in JS |
| CR-04 | noindex / X-Robots-Tag / meta robots on indexable pages | header or meta | high |

### structured-data-audit (Extract)

| ID | Check | Evidence | Typical severity |
| :--- | :--- | :--- | :--- |
| SD-01 | JSON-LD parses | parse error + snippet | high |
| SD-02 | Product/Offer on product pages: name, price, currency, availability | field presence table | high if product page, offer incomplete |
| SD-03 | Organization / WebSite markup conflicts with visible name | JSON-LD vs visible text | medium |

Do **not** fire "no FAQPage" / "no schema at all" as a defect. Proactive "add Product JSON-LD" is allowed as a suggested action when the page is clearly a product page.

### fact-quality-audit (Extract)

| ID | Check | Evidence | Typical severity |
| :--- | :--- | :--- | :--- |
| FQ-01 | Extract numeric/policy claims | claim + CSS path / snippet | n/a (input to others) |
| FQ-02 | Contradictions across pages (price, hours, policy) | two snippets + URLs | high |
| FQ-03 | Numbers without units or comparators | snippet | medium |
| FQ-04 | Ungrounded superlatives ("#1", "best") | snippet | medium |

### freshness-corroboration (Trust)

| ID | Check | Evidence | Typical severity |
| :--- | :--- | :--- | :--- |
| FC-01 | dateModified / datePublished / Last-Modified / visible dates disagree | the four values | medium |
| FC-02 | Core page dates > 12 months with no update signal | dates + URL | medium |
| FC-03 | Corroborate 2-3 public sources (Wikidata, Wikipedia, official social, news) | source URLs + mismatch | high if identity/price/date conflict |

### entity-identity-audit (Use)

| ID | Check | Evidence | Typical severity |
| :--- | :--- | :--- | :--- |
| EI-01 | Organization / brand name vs title / H1 / JSON-LD | three strings | high if conflict |
| EI-02 | sameAs targets 404 or point at a different entity | URL + status + title | high |
| EI-03 | NAP (name, address, phone) differs across pages | NAP tuples + URLs | high |

## On-site engagement (not llms.txt)

A visitor arrives, often on a **deep URL** from an AI answer. Can they tell who this is, what they can do, and what to do next without hunting?

| ID | Check | Evidence | Typical severity |
| :--- | :--- | :--- | :--- |
| EG-01 | First impression: who / what / next in first screenful | H1, subhead, primary CTA text | high if any of three missing |
| EG-02 | Nav covers the jobs the site claims to do | nav labels vs claimed offerings | medium |
| EG-03 | Deep page has breadcrumbs or equivalent parent context | breadcrumb DOM or none | high on interior pages |
| EG-04 | Actionability: working primary CTA, not only "learn more" loops | CTA href + destination type | high if no action |

Out of scope as **core** findings: `/llms.txt`, OpenAPI, chatbot widgets, MCP manifests. Those may appear only as low-priority **proactive** suggestions.

# Architecture Decision Records

## ADR-001: Evidence-first

**Status:** Accepted

Deterministic checks produce evidence first. Any reasoning step may only inspect that evidence. A finding with no evidence payload is invalid.

## ADR-002: Adobe report schema is the output

**Status:** Accepted

The entrypoint emits one JSON object with `site`, `audited_at`, `summary` counts, and `findings[]`. Each finding has `id`, `title`, `severity` (lowercase), `evidence`, and `suggested_action: {summary, priority}`.

Extra fields are allowed (`category`, `confidence`, `why_it_matters`, `affected_urls`). A 0-100 "AI readiness index" is **not** the contest output and must not replace findings.

## ADR-003: Engagement means visitor orientation

**Status:** Accepted

Round 2 / Round 3 on-site engagement is why a human who arrives (often on a deep URL) does not stay: who/what/next, nav, breadcrumbs, CTAs.

It is **not** `/llms.txt`, OpenAPI, or chatbot interoperability. Those are optional proactive notes at most.

## ADR-004: Stdlib HTTP default; no Chromium in the ZIP

**Status:** Accepted

Adobe ZIP cap is 50 MB (we budget 45). Chromium is ~150 MB. Default crawl is Python stdlib HTTP + HTML. Playwright may run if already installed on the host. Never vendor the browser.

## ADR-005: Do not report missing schema blindly

**Status:** Accepted

Official golden rule. Flag broken JSON-LD, or incomplete Product/Offer **on pages that are already product pages**. Absence of FAQPage / Article / llms.txt is not a defect.

## ADR-006: SKILL.md name equals folder name

**Status:** Accepted

agentskills.io: `name` is lowercase hyphenated and must match the parent directory. Adobe also requires When to use, Inputs, numbered Procedure, Output against the fixed schema.

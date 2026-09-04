# Evaluation plan

Judges score detection accuracy, suggested-action quality, generalization, and agentskills.io / marketplace.json hygiene - not a GUI.

## Must pass

1. `marketplace.json` has exactly one `"entrypoint": true`. Skill `path` is a **folder**.
2. Every `SKILL.md` `name` equals its folder (lowercase hyphens).
3. Entrypoint JSON validates against Adobe floor: `site`, `audited_at`, `summary`, `findings[]` with `suggested_action` object.
4. No finding whose only claim is "missing llms.txt" or "missing schema" on a non-product page.
5. Engagement findings are about who/what/next, nav, breadcrumbs, CTAs - not APIs.
6. Same snapshot in -> same findings out (deterministic checks).
7. ZIP <= 45 MB. Runtime under 5 minutes on a typical public site.

## Calibration sites

See `test-sites.json`. Run after Python scripts exist. Do not hard-code those hostnames into skill logic.

## Precision

False positives (especially missing-schema and llms.txt) hurt more than a missed nice-to-have. Prefer fewer, evidenced findings.

"""Audit Orchestrator - Master Entrypoint skill for marketplace audit package with site-wide crawler integration."""

import argparse
import json
from typing import Callable, Dict, List, Optional
from urllib.parse import urlparse

from src.analysis.crawl_render_audit import audit_crawl_render_skill
from src.analysis.structured_data_audit import audit_structured_data
from src.crawler.engine import CrawlConfig, CrawlManifest, SiteCrawler
from src.models import (
    AuditReport,
    Evidence,
    Finding,
    FindingSeverity,
    FindingStatus,
)


def validate_target_url(url: str) -> str:
    """Validates that the provided target URL is structured correctly."""
    if not url or not isinstance(url, str):
        raise ValueError("Target URL must be a non-empty string.")
    cleaned = url.strip()
    parsed = urlparse(cleaned)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError(f"Invalid target URL '{url}'. URL must include http:// or https:// scheme and domain.")
    return cleaned


def _wrap_crawl_render(url: str, html: str, headers: Dict[str, str], status_code: int, crawl_manifest: Optional[CrawlManifest] = None) -> List[Finding]:
    return audit_crawl_render_skill(
        url=url,
        html_content=html,
        headers=headers,
        status_code=status_code,
        crawl_manifest=crawl_manifest,
    )


def _wrap_structured_data(url: str, html: str, headers: Dict[str, str], status_code: int, crawl_manifest: Optional[CrawlManifest] = None) -> List[Finding]:
    return audit_structured_data(html_content=html, url=url)


DEFAULT_SKILL_REGISTRY: Dict[str, Callable[..., List[Finding]]] = {
    "crawl-render-audit": _wrap_crawl_render,
    "structured-data-audit": _wrap_structured_data,
}


class AuditOrchestrator:
    """Master Entrypoint Orchestrator coordinating site-wide discovery and specialized audit skills."""

    def __init__(
        self,
        skill_registry: Optional[Dict[str, Callable[..., List[Finding]]]] = None,
        crawl_config: Optional[CrawlConfig] = None,
    ):
        self.skill_registry = skill_registry if skill_registry is not None else DEFAULT_SKILL_REGISTRY
        self.crawl_config = crawl_config or CrawlConfig()
        self.crawler = SiteCrawler(config=self.crawl_config)

    def execute_audit(
        self,
        target_url: str,
        html_override: Optional[str] = None,
        headers_override: Optional[Dict[str, str]] = None,
        status_code_override: Optional[int] = None,
        custom_fetcher: Optional[Callable[[str], tuple]] = None,
    ) -> AuditReport:
        """Executes the site-wide discovery, bounded crawl, sub-skill delegation, and report synthesis."""
        valid_url = validate_target_url(target_url)

        # 1. Execute site-wide discovery & crawl
        crawl_manifest = self.crawler.crawl_site(
            start_url=valid_url,
            html_override=html_override,
            custom_fetcher=custom_fetcher,
        )

        # Get primary homepage page evidence
        primary_page = next((p for p in crawl_manifest.pages if p.url == valid_url or p.depth == 0), None)
        if primary_page:
            html_content = primary_page.html_content
            response_headers = primary_page.headers or headers_override or {}
            status_code = primary_page.status_code or status_code_override or 200
        else:
            html_content = html_override or ""
            response_headers = headers_override or {}
            status_code = status_code_override or 200

        skills_run: List[str] = []
        all_findings: List[Finding] = []

        # 2. Delegate execution to registered sub-skills
        for skill_id, skill_fn in self.skill_registry.items():
            skills_run.append(skill_id)
            try:
                try:
                    findings = skill_fn(
                        url=valid_url,
                        html=html_content,
                        headers=response_headers,
                        status_code=status_code,
                        crawl_manifest=crawl_manifest,
                    )
                except TypeError:
                    findings = skill_fn(
                        url=valid_url,
                        html=html_content,
                        headers=response_headers,
                        status_code=status_code,
                    )
                if isinstance(findings, list):
                    all_findings.extend(findings)
            except Exception as skill_err:
                err_ev = Evidence(
                    source_url=valid_url,
                    evidence_type="skill_execution_error",
                    observed={
                        "error_type": type(skill_err).__name__,
                        "error_message": str(skill_err),
                    },
                    location=f"skill:{skill_id}",
                )
                err_finding = Finding(
                    skill=skill_id,
                    check_id=f"{skill_id.upper().replace('-', '_')}_ERR",
                    title=f"Skill Execution Error ({skill_id})",
                    status=FindingStatus.ERROR,
                    severity=FindingSeverity.HIGH,
                    description=f"Skill '{skill_id}' encountered an error during execution: {str(skill_err)}",
                    evidence=[err_ev],
                    recommendation=f"Inspect execution logic for skill '{skill_id}'.",
                )
                all_findings.append(err_finding)

        # 3. Synthesize final AuditReport with top-level crawl manifest & summary
        report = AuditReport.create(
            url=valid_url,
            crawl=crawl_manifest.model_dump(),
            skills_run=skills_run,
            findings=all_findings,
        )

        return report


def main():
    parser = argparse.ArgumentParser(description="Brand AI Readiness Audit Orchestrator CLI")
    parser.add_argument("url", help="Single target URL to audit (e.g. https://example.com)")
    parser.add_argument("--max-pages", type=int, default=100, help="Maximum pages to crawl")
    parser.add_argument("--max-depth", type=int, default=3, help="Maximum crawl depth")
    args = parser.parse_args()

    config = CrawlConfig(max_pages=args.max_pages, max_depth=args.max_depth)
    orchestrator = AuditOrchestrator(crawl_config=config)
    report = orchestrator.execute_audit(target_url=args.url)
    print(json.dumps(report.model_dump(), indent=2))


if __name__ == "__main__":
    main()

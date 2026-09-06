"""Core Site Crawler Engine implementing objective URL discovery, bounded crawling, general evidence extraction, and WebsiteEvidence store."""

import time
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse
import requests
from pydantic import BaseModel, Field

from src.analysis.crawl_render_audit import detect_word_boundary_collapse
from src.crawler.prioritizer import calculate_url_priority, sort_urls_by_priority
from src.crawler.robots import RobotsChecker
from src.crawler.role_classifier import classify_page_role_signals
from src.crawler.sitemap import SitemapDiscoverer
from src.crawler.url_utils import extract_base_domain, is_crawlable_html_url, normalize_url
from src.evidence.models import (
    DiscoveredURLEvidence,
    FailedURLEvidence,
    PageEvidence,
    Provenance,
    RobotsEvidence,
    SitemapEvidence,
    WebsiteEvidence,
)
from src.extraction.images import extract_page_images
from src.extraction.links import extract_page_links_and_resources
from src.extraction.metadata import extract_page_metadata
from src.extraction.page import extract_page_content
from src.extraction.structured_data import extract_structured_data


class CrawlConfig(BaseModel):
    """Configuration for site-wide crawling and discovery bounds."""
    max_depth: int = Field(default=3, ge=0, description="Maximum crawl depth from starting URL")
    max_pages: int = Field(default=100, ge=1, description="Maximum total pages to crawl")
    same_domain_only: bool = Field(default=True, description="Restrict crawling to starting domain")
    respect_robots: bool = Field(default=True, description="Enforce robots.txt fetch permissions")
    request_timeout_seconds: float = Field(default=3.0, ge=1.0, description="HTTP request timeout")
    max_requests_per_second: float = Field(default=2.0, ge=0.1, description="Request rate limit governor")
    discover_sitemap: bool = Field(default=True, description="Discover and parse sitemap.xml")
    user_agent: str = Field(default="AIReadinessAudit/0.1.0", description="User-Agent string for HTTP requests")


class CrawlManifest(BaseModel):
    """Backward-compatible wrapper for WebsiteEvidence store."""
    start_url: str = Field(..., description="Initial starting URL of the audit")
    pages_discovered: int = Field(..., ge=0, description="Total unique URLs discovered during crawl")
    pages_crawled: int = Field(..., ge=0, description="Total pages successfully or attempt-crawled")
    max_depth: int = Field(..., ge=0, description="Configured maximum crawl depth")
    truncated: bool = Field(..., description="True if crawl stopped before discovering all inventory URLs")
    truncation_reason: Optional[str] = Field(default=None, description="Reason for crawl truncation")
    robots_status: Dict[str, Any] = Field(default_factory=dict, description="Robots.txt check metadata")
    sitemap_status: Dict[str, Any] = Field(default_factory=dict, description="Sitemap.xml discovery metadata")
    failed_urls: List[Dict[str, Any]] = Field(default_factory=list, description="URLs that failed during fetch")
    skipped_urls: List[Dict[str, Any]] = Field(default_factory=list, description="URLs skipped due to rules or bounds")
    pages: List[PageEvidence] = Field(default_factory=list, description="Store of all crawled page evidence records")
    website_evidence: Optional[WebsiteEvidence] = Field(default=None, description="Rich general website evidence model")


class SiteCrawler:
    """Site-wide discovery and crawling engine enforcing safety bounds and general evidence extraction.
    
    The crawler is strictly an evidence collector and does NOT make AI readiness evaluations or score judgments.
    """

    def __init__(self, config: Optional[CrawlConfig] = None):
        self.config = config or CrawlConfig()
        self.robots_checker = RobotsChecker(user_agent=self.config.user_agent, timeout=self.config.request_timeout_seconds)
        self.sitemap_discoverer = SitemapDiscoverer(user_agent=self.config.user_agent, timeout=self.config.request_timeout_seconds)

    def crawl_site(
        self,
        start_url: str,
        html_override: Optional[str] = None,
        custom_fetcher: Optional[Callable[[str], Tuple[int, str, Dict[str, str]]]] = None,
    ) -> CrawlManifest:
        """Executes site-wide URL discovery, general evidence extraction, and bounded crawling starting from start_url."""
        start_time = time.time()
        norm_start = normalize_url(start_url)
        if not norm_start:
            raise ValueError(f"Invalid crawl start URL: {start_url}")

        base_domain = extract_base_domain(norm_start)

        # 1. Robots.txt check & evidence collection
        robots_info = {"checked": False, "allowed": True, "found": False, "sitemaps_declared": []}
        robots_evidence: Optional[RobotsEvidence] = None
        if self.config.respect_robots:
            robots_info = self.robots_checker.check_robots(norm_start)
            if "evidence" in robots_info:
                robots_evidence = robots_info["evidence"]

        if not robots_evidence:
            robots_evidence = RobotsEvidence(
                url=f"https://{base_domain}/robots.txt",
                available=False,
                status_code=0,
            )

        # 2. Sitemap discovery & evidence collection
        sitemap_info = {"checked": False, "found": False, "urls_discovered": 0}
        sitemap_urls: List[str] = []
        sitemap_evidence_items: List[SitemapEvidence] = []
        if self.config.discover_sitemap:
            sitemap_info, sitemap_urls = self.sitemap_discoverer.discover_sitemap_urls(
                target_url=norm_start,
                declared_sitemaps=robots_info.get("sitemaps_declared"),
                base_domain=base_domain,
            )
            sitemap_evidence_items = sitemap_info.get("sitemap_evidence_items", [])

        # 3. URL inventory & tracking setup
        discovered_urls: Set[str] = set()
        discovered_url_records: List[DiscoveredURLEvidence] = []
        visited_urls: Set[str] = set()
        skipped_urls: List[Dict[str, Any]] = []
        failed_url_records: List[FailedURLEvidence] = []
        failed_urls_compat: List[Dict[str, Any]] = []
        crawled_pages: List[PageEvidence] = []

        # Inventory queue of tuples: (url, priority_score, depth, parent_url, anchor_text, discovery_method)
        inventory: List[Tuple[str, int, int, Optional[str], Optional[str], str]] = []

        def add_to_inventory(
            target: str,
            depth: int,
            parent_url: Optional[str] = None,
            anchor: Optional[str] = None,
            discovery_method: str = "html_link",
        ):
            n_url = normalize_url(target)
            if not n_url or n_url in discovered_urls:
                return
            if not is_crawlable_html_url(n_url, base_domain=base_domain, same_domain_only=self.config.same_domain_only):
                return
            
            priority = calculate_url_priority(n_url, anchor_text=anchor or "")
            discovered_urls.add(n_url)
            
            disc_ev = DiscoveredURLEvidence(
                url=n_url,
                discovered_from=parent_url,
                anchor_text=anchor,
                discovery_method=discovery_method,
                provenance=Provenance(source_url=parent_url or n_url, location=f"discovery:{discovery_method}"),
            )
            discovered_url_records.append(disc_ev)
            inventory.append((n_url, priority, depth, parent_url, anchor, discovery_method))

        # Add start_url (depth = 0, max priority)
        add_to_inventory(norm_start, depth=0, parent_url=None, anchor=None, discovery_method="start_url")

        # Add discovered sitemap URLs (depth = 1)
        for s_url in sitemap_urls:
            add_to_inventory(s_url, depth=1, parent_url=norm_start, anchor=None, discovery_method="sitemap")

        last_request_time = 0.0
        min_interval = 1.0 / self.config.max_requests_per_second

        # 4. Bounded Crawl loop
        while len(crawled_pages) < self.config.max_pages:
            # Sort inventory by priority score
            inventory_sorted = sorted(inventory, key=lambda x: x[1], reverse=True)
            unvisited = [item for item in inventory_sorted if item[0] not in visited_urls]
            if not unvisited:
                break

            curr_url, curr_priority, curr_depth, parent_url, curr_anchor, disc_method = unvisited[0]
            visited_urls.add(curr_url)

            if self.config.respect_robots and robots_info.get("found"):
                if not self.robots_checker.check_robots(curr_url).get("allowed", True):
                    skipped_urls.append({"url": curr_url, "reason": "robots_disallowed"})
                    continue

            status_code = 200
            html = ""
            headers: Dict[str, str] = {}
            fetch_error: Optional[str] = None
            final_url = curr_url

            if curr_url == norm_start and html_override is not None:
                html = html_override
                status_code = 200
            elif custom_fetcher is not None:
                try:
                    status_code, html, headers = custom_fetcher(curr_url)
                except Exception as err:
                    fetch_error = str(err)
                    status_code = 0
            else:
                now = time.time()
                elapsed = now - last_request_time
                if elapsed < min_interval:
                    time.sleep(min_interval - elapsed)
                last_request_time = time.time()

                try:
                    resp = requests.get(
                        curr_url,
                        headers={"User-Agent": self.config.user_agent},
                        timeout=self.config.request_timeout_seconds,
                    )
                    status_code = resp.status_code
                    headers = dict(resp.headers)
                    html = resp.text
                    final_url = resp.url
                except Exception as net_err:
                    fetch_error = str(net_err)
                    status_code = 0

            if fetch_error or status_code not in (200, 301, 302):
                err_msg = fetch_error or f"HTTP {status_code}"
                failed_ev = FailedURLEvidence(
                    url=curr_url,
                    status_code=status_code,
                    error_reason=err_msg,
                    discovered_from=parent_url,
                    anchor_text=curr_anchor,
                    discovery_method=disc_method,
                    provenance=Provenance(source_url=curr_url, location="http_fetch"),
                )
                failed_url_records.append(failed_ev)
                failed_urls_compat.append({"url": curr_url, "status_code": status_code, "error": err_msg})
                
                crawled_pages.append(PageEvidence(
                    url=curr_url,
                    final_url=final_url,
                    depth=curr_depth,
                    status="failed",
                    status_code=status_code,
                    discovery_source=disc_method,
                    page_role="unknown",
                    error=err_msg,
                ))
                continue

            # 5. GENERAL EVIDENCE EXTRACTION
            meta_info = extract_page_metadata(html_content=html, url=curr_url)
            content_info = extract_page_content(html_content=html, url=curr_url)
            image_items = extract_page_images(html_content=html, url=curr_url)
            resource_info = extract_page_links_and_resources(html_content=html, url=curr_url)
            sd_info = extract_structured_data(html_content=html, url=curr_url)

            heading_texts = [h["text"] for h in content_info["headings"]]
            role_signals = classify_page_role_signals(
                url=curr_url,
                title=meta_info["title"],
                headings=heading_texts,
                anchor_text=curr_anchor,
            )

            # Text extractability indicators
            raw_text = content_info["raw_text"]
            normalized_text = content_info["normalized_text"]
            collapsed, suspicious_toks = detect_word_boundary_collapse(normalized_text)
            extractability_info = {
                "raw_text_length": len(raw_text),
                "normalized_text_length": len(normalized_text),
                "word_boundary_collapse_detected": collapsed,
                "suspicious_tokens": suspicious_toks,
            }

            robots_meta = {
                "x_robots_tag": headers.get("x-robots-tag"),
            }

            # Build structured PageEvidence
            page_ev = PageEvidence(
                url=curr_url,
                final_url=final_url,
                depth=curr_depth,
                status="success",
                status_code=status_code,
                content_type=headers.get("content-type", "text/html"),
                discovery_source=disc_method,
                title=meta_info["title"],
                meta_description=meta_info["meta_description"],
                canonical_url=meta_info["canonical_url"],
                language=meta_info["language"],
                charset=meta_info.get("charset"),
                role_signals=role_signals,
                page_role=role_signals.classified_role,
                word_count=content_info["word_count"],
                headings=content_info["headings"],
                paragraphs=content_info["paragraphs"],
                lists=content_info["lists"],
                tables=content_info["tables"],
                blockquotes=content_info["blockquotes"],
                captions=content_info.get("captions", []),
                links=resource_info["links"],
                internal_links=resource_info["internal_links"],
                external_links=resource_info["external_links"],
                images=image_items,
                forms=resource_info["forms"],
                documents=resource_info["documents"],
                robots_directives=robots_meta,
                structured_data=sd_info["summary"],
                jsonld_raw_blocks=sd_info["jsonld_raw_blocks"],
                meta_tags=meta_info["meta_tags"],
                contacts=content_info["contacts"],
                dates=content_info["dates"],
                text_extractability=extractability_info,
                html_content=html,  # Excluded from serialization
                headers=headers,    # Excluded from serialization
            )
            crawled_pages.append(page_ev)

            # Discover new internal links if below max_depth
            if curr_depth < self.config.max_depth:
                for link_ev in resource_info["links"]:
                    if link_ev.is_internal:
                        add_to_inventory(
                            link_ev.href,
                            depth=curr_depth + 1,
                            parent_url=curr_url,
                            anchor=link_ev.anchor_text,
                            discovery_method="html_link",
                        )

        # 6. Build top-level WebsiteEvidence and CrawlManifest
        total_discovered = len(discovered_urls)
        total_crawled = len(crawled_pages)
        truncated = total_discovered > total_crawled
        truncation_reason = None
        if truncated:
            if total_crawled >= self.config.max_pages:
                truncation_reason = f"max_pages_limit_reached ({total_crawled}/{self.config.max_pages})"
            else:
                truncation_reason = "max_depth_reached"

        # Compute resource summary
        total_images = sum(len(p.images) for p in crawled_pages)
        total_pdf = sum(sum(1 for d in p.documents if d.file_type == "pdf") for p in crawled_pages)
        total_other_doc = sum(sum(1 for d in p.documents if d.file_type != "pdf") for p in crawled_pages)
        total_forms = sum(len(p.forms) for p in crawled_pages)

        resource_summary = {
            "html_pages": total_crawled,
            "images": total_images,
            "pdf_documents": total_pdf,
            "other_documents": total_other_doc,
            "forms": total_forms,
        }

        duration_sec = round(time.time() - start_time, 3)

        website_evidence = WebsiteEvidence(
            start_url=norm_start,
            normalized_start_url=norm_start,
            crawl_metadata={
                "same_domain_only": self.config.same_domain_only,
                "user_agent": self.config.user_agent,
                "request_timeout_seconds": self.config.request_timeout_seconds,
                "duration_seconds": duration_sec,
            },
            robots=robots_evidence,
            sitemaps=sitemap_evidence_items,
            discovered_urls=discovered_url_records,
            crawled_pages=crawled_pages,
            failed_urls=failed_url_records,
            skipped_urls=skipped_urls,
            resource_summary=resource_summary,
            pages_discovered=total_discovered,
            pages_crawled=total_crawled,
            max_depth=self.config.max_depth,
            truncated=truncated,
            truncation_reason=truncation_reason,
        )

        manifest = CrawlManifest(
            start_url=norm_start,
            pages_discovered=total_discovered,
            pages_crawled=total_crawled,
            max_depth=self.config.max_depth,
            truncated=truncated,
            truncation_reason=truncation_reason,
            robots_status=robots_info,
            sitemap_status=sitemap_info,
            failed_urls=failed_urls_compat,
            skipped_urls=skipped_urls,
            pages=crawled_pages,
            website_evidence=website_evidence,
        )

        return manifest

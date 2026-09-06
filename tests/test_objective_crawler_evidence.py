"""Comprehensive unit tests for objective, evaluation-free crawler and WebsiteEvidence store (Step 20)."""

import json
import pytest

from src.crawler.engine import CrawlConfig, SiteCrawler
from src.crawler.robots import parse_robots_txt_rules
from src.crawler.role_classifier import classify_page_role_signals
from src.crawler.sitemap import parse_sitemap_xml_details
from src.evidence.models import (
    ContactCandidate,
    DateCandidate,
    DiscoveredURLEvidence,
    FailedURLEvidence,
    ImageEvidence,
    PageEvidence,
    Provenance,
    RobotsEvidence,
    SitemapEntry,
    SitemapEvidence,
    WebsiteEvidence,
)
from src.extraction.images import extract_page_images


def test_robots_txt_multi_user_agent_groups():
    """1. Test robots.txt parsing preserves arbitrary multi-user-agent rule groups and sitemaps."""
    robots_content = """
    User-agent: *
    Disallow: /admin/
    Allow: /public/
    Crawl-delay: 2.5

    User-agent: GPTBot
    User-agent: CCBot
    Disallow: /private/
    Disallow: /secret/

    Sitemap: https://example.com/sitemap.xml
    Sitemap: https://example.com/sitemap-news.xml
    """
    groups, sitemaps, all_allows, all_disallows, delay = parse_robots_txt_rules(robots_content)

    assert len(groups) == 2
    assert groups[0].user_agents == ["*"]
    assert groups[0].disallow == ["/admin/"]
    assert groups[0].allow == ["/public/"]
    assert groups[0].crawl_delay == 2.5

    assert groups[1].user_agents == ["GPTBot", "CCBot"]
    assert groups[1].disallow == ["/private/", "/secret/"]

    assert sitemaps == ["https://example.com/sitemap.xml", "https://example.com/sitemap-news.xml"]


def test_sitemap_evidence_details():
    """2. Test sitemap XML details parsing into SitemapEntry models."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <url>
            <loc>https://example.com/page1</loc>
            <lastmod>2026-02-01</lastmod>
        </url>
        <url>
            <loc>https://example.com/page2</loc>
        </url>
    </urlset>
    """
    is_index, child_indices, page_urls, lastmod_map = parse_sitemap_xml_details(xml_content, sitemap_url="https://example.com/sitemap.xml")
    assert is_index is False
    assert child_indices == []
    assert len(page_urls) == 2
    assert "https://example.com/page1" in page_urls
    assert lastmod_map["https://example.com/page1"] == "2026-02-01"


def test_localhost_declared_image_url_preservation():
    """3. Test real-world IIT Patna OpenGraph case: declared_url http://localhost:3000/... is preserved without alteration."""
    html = """<!DOCTYPE html>
    <html>
    <head>
        <title>IIT Patna Administration</title>
        <meta property="og:image" content="http://localhost:3000/images/administration.jpg">
    </head>
    <body>
        <h1>Administration Page</h1>
        <img src="http://localhost:3000/images/hero.png" alt="Hero Banner" width="800" height="400" />
    </body>
    </html>
    """
    images = extract_page_images(html, url="https://www.iitp.ac.in/index.php/administration")
    assert len(images) == 2

    og_img = next(img for img in images if img.source_type == "og_image")
    assert og_img.declared_url == "http://localhost:3000/images/administration.jpg"
    assert og_img.resolved_url == "http://localhost:3000/images/administration.jpg"

    hero_img = next(img for img in images if img.source_type == "img")
    assert hero_img.declared_url == "http://localhost:3000/images/hero.png"
    assert hero_img.declared_width == 800
    assert hero_img.declared_height == 400


def test_url_discovery_traceability():
    """4. Test URL discovery preserves discovered_from, anchor_text, and discovery_method."""
    html_home = """
    <html><body>
        <a href="/about">About Us Page</a>
        <a href="/contact">Contact Support</a>
    </body></html>
    """

    def mock_fetcher(url):
        if url == "https://example.com/":
            return 200, html_home, {"content-type": "text/html"}
        return 200, "<html><body>Page Content</body></html>", {"content-type": "text/html"}

    crawler = SiteCrawler(config=CrawlConfig(max_pages=3, discover_sitemap=False, respect_robots=False))
    manifest = crawler.crawl_site("https://example.com/", custom_fetcher=mock_fetcher)

    web_ev = manifest.website_evidence
    assert web_ev is not None

    about_disc = next((d for d in web_ev.discovered_urls if "about" in d.url), None)
    assert about_disc is not None
    assert about_disc.discovered_from == "https://example.com/"
    assert about_disc.anchor_text == "About Us Page"
    assert about_disc.discovery_method == "html_link"


def test_failed_url_evidence_collection():
    """5. Test failed URLs are recorded in failed_urls evidence list with error reason and provenance."""
    def mock_fetcher(url):
        if "broken" in url:
            return 404, "Not Found", {}
        return 200, "<html><body><a href='/broken'>Broken Link</a></body></html>", {"content-type": "text/html"}

    crawler = SiteCrawler(config=CrawlConfig(max_pages=2, discover_sitemap=False, respect_robots=False))
    manifest = crawler.crawl_site("https://example.com/", custom_fetcher=mock_fetcher)

    web_ev = manifest.website_evidence
    assert web_ev is not None
    assert len(web_ev.failed_urls) == 1

    failed_ev = web_ev.failed_urls[0]
    assert failed_ev.status_code == 404
    assert failed_ev.discovered_from == "https://example.com/"
    assert failed_ev.anchor_text == "Broken Link"
    assert failed_ev.provenance is not None


def test_page_role_signals_defaults_to_unknown():
    """6. Test page role classifier returns 'unknown' role when no signals match."""
    signals = classify_page_role_signals("https://example.com/xyz123")
    assert signals.classified_role == "unknown"
    assert "no_explicit_role_keyword_matched" in signals.signals


def test_website_evidence_pure_json_serialization():
    """7. Test WebsiteEvidence model serializes to JSON without findings, status, or AI readiness scores."""
    robots_ev = RobotsEvidence(url="https://example.com/robots.txt", available=True, status_code=200)
    web_ev = WebsiteEvidence(
        start_url="https://example.com/",
        normalized_start_url="https://example.com/",
        robots=robots_ev,
        pages_discovered=1,
        pages_crawled=1,
        resource_summary={"html_pages": 1, "images": 0},
    )

    dumped = json.loads(web_ev.model_dump_json())
    assert "start_url" in dumped
    assert "robots" in dumped
    assert "AI readiness" not in json.dumps(dumped)
    assert "overall_score" not in json.dumps(dumped)

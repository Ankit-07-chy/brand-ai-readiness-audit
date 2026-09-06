"""Comprehensive unit tests for site-wide discovery and crawling engine (src/crawler/)."""

import pytest
from src.analysis.crawl_render_audit import audit_crawl_render_skill
from src.crawler.engine import CrawlConfig, SiteCrawler
from src.crawler.prioritizer import calculate_url_priority
from src.crawler.role_classifier import classify_page_role
from src.crawler.sitemap import parse_sitemap_xml
from src.crawler.url_utils import (
    is_crawlable_html_url,
    is_same_domain,
    normalize_url,
)
from src.models import AuditReport, FindingStatus


def test_url_normalization():
    """1. Test URL normalization resolves relative URLs and strips trailing slash on non-root paths."""
    assert normalize_url("/about/", base_url="https://example.com") == "https://example.com/about"
    assert normalize_url("https://example.com/about#team") == "https://example.com/about"
    assert normalize_url("https://EXAMPLE.com/path/") == "https://example.com/path"
    assert normalize_url("https://example.com/") == "https://example.com/"


def test_fragment_removal():
    """2. Test URL fragments are removed."""
    assert normalize_url("https://example.com/page#section1") == "https://example.com/page"


def test_duplicate_removal_and_filtering():
    """3. Test non-HTML resource and action URL filtering."""
    assert not is_crawlable_html_url("https://example.com/image.png")
    assert not is_crawlable_html_url("https://example.com/document.pdf")
    assert not is_crawlable_html_url("https://example.com/styles.css")
    assert not is_crawlable_html_url("https://example.com/login")
    assert not is_crawlable_html_url("https://example.com/checkout")
    assert is_crawlable_html_url("https://example.com/about")


def test_same_domain_filtering():
    """4. Test same-domain filter verification."""
    assert is_same_domain("https://example.com/about", "example.com")
    assert is_same_domain("https://sub.example.com/page", "example.com")
    assert not is_same_domain("https://external.com/page", "example.com")


def test_page_prioritization():
    """5. Test deterministic priority scoring for high vs low value path signals."""
    p_home = calculate_url_priority("https://example.com/")
    p_about = calculate_url_priority("https://example.com/about")
    p_projects = calculate_url_priority("https://example.com/projects")
    p_terms = calculate_url_priority("https://example.com/terms")

    assert p_home > p_about
    assert p_about == p_projects == 100
    assert p_about > p_terms
    assert p_terms == 1


def test_page_role_classification():
    """6. Test deterministic page role classification."""
    assert classify_page_role("https://example.com/") == "homepage"
    assert classify_page_role("https://example.com/about", title="About Us") == "about"
    assert classify_page_role("https://example.com/projects", headings=["Our Projects"]) == "project"
    assert classify_page_role("https://example.com/contact-us") == "contact"
    assert classify_page_role("https://example.com/privacy-policy") == "legal"
    assert classify_page_role("https://example.com/unknown-random-page") == "unknown"


def test_script_style_nextjs_payloads_excluded_from_visible_text():
    """7. Test that script, style, SVG, and Next.js React server component payloads are excluded from word count."""
    html_nextjs = """
    <!DOCTYPE html>
    <html>
    <head>
        <style> body { color: red; } </style>
        <script>
            self.__next_f.push([1, "1:HL[\\"/_next/static/css/app.css\\",\\"style\\"]\n"]);
            self.__next_f.push([1, "2:I[\\"chunk123.js\\"]\n"]);
        </script>
        <title>Next.js App</title>
    </head>
    <body>
        <h1>Visible Header</h1>
        <p>Visible paragraph text content for users.</p>
        <script> console.log("ignore this javascript code"); </script>
    </body>
    </html>
    """
    crawler = SiteCrawler(config=CrawlConfig(max_pages=1, discover_sitemap=False, respect_robots=False))
    manifest = crawler.crawl_site("https://example.com/", html_override=html_nextjs)

    page = manifest.pages[0]
    # Word count should ONLY count 'Visible', 'Header', 'Visible', 'paragraph', 'text', 'content', 'for', 'users.' (8 words)
    # Framework scripts and styles must NOT inflate word count
    assert page.word_count < 15
    assert "self.__next_f" not in page.paragraphs
    assert page.headings[0]["text"] == "Visible Header"
    assert "Visible paragraph text content for users." in page.paragraphs


def test_raw_html_excluded_from_final_report_dump():
    """8. Test raw HTML is excluded from final AuditReport JSON serialization output."""
    html = "<html><head><title>Test</title></head><body><h1>Content</h1></body></html>"
    crawler = SiteCrawler(config=CrawlConfig(max_pages=1, discover_sitemap=False, respect_robots=False))
    manifest = crawler.crawl_site("https://example.com/", html_override=html)

    report = AuditReport.create("https://example.com/", crawl=manifest.model_dump(), skills_run=[], findings=[])
    report_dict = report.model_dump()

    # Verify 'html_content' is NOT present in any page dictionary in final output
    crawled_page_dict = report_dict["crawl"]["pages"][0]
    assert "html_content" not in crawled_page_dict
    assert "headers" not in crawled_page_dict

    # Verify structured extracted fields ARE present
    assert crawled_page_dict["title"] == "Test"
    assert crawled_page_dict["headings"][0]["text"] == "Content"


def test_cr_012_reports_actual_crawl_coverage():
    """9. Test CR-012 reports Site Crawl Coverage."""
    html = "<html><head><title>Home</title></head><body><a href='/about'>About</a></body></html>"
    crawler = SiteCrawler(config=CrawlConfig(max_pages=1, discover_sitemap=False, respect_robots=False))
    manifest = crawler.crawl_site("https://example.com/", html_override=html)

    findings = audit_crawl_render_skill("https://example.com/", html_content=html, crawl_manifest=manifest)
    cr12 = next(f for f in findings if f.check_id == "CR-012")

    assert cr12.title == "Site Crawl Coverage"
    assert cr12.evidence[0].observed["pages_discovered"] == 2
    assert cr12.evidence[0].observed["pages_crawled"] == 1
    assert cr12.evidence[0].observed["truncated"] is True


def test_cr_010_uses_sitewide_page_evidence():
    """10. Test CR-010 evaluates site-wide discoverability across crawled pages."""
    pages_db = {
        "https://example.com/": (200, "<html><body><a href='/about'>About</a><a href='/projects'>Projects</a></body></html>", {}),
        "https://example.com/about": (200, "<html><head><title>About</title></head><body><p>Detailed about company story with 500 words.</p></body></html>", {}),
        "https://example.com/projects": (200, "<html><head><title>Projects</title></head><body><p>Portfolio of case studies with 800 words.</p></body></html>", {}),
    }

    def fetcher(url):
        return pages_db[url]

    crawler = SiteCrawler(config=CrawlConfig(max_pages=5, discover_sitemap=False, respect_robots=False))
    manifest = crawler.crawl_site("https://example.com/", custom_fetcher=fetcher)

    findings = audit_crawl_render_skill("https://example.com/", html_content=pages_db["https://example.com/"][1], crawl_manifest=manifest)
    cr10 = next(f for f in findings if f.check_id == "CR-010")

    assert cr10.status == FindingStatus.PASS
    assert "OBSERVATION:" in cr10.evidence[0].observed["observation"]
    assert "INTERPRETATION:" in cr10.evidence[0].observed["interpretation"]
    assert cr10.evidence[0].observed["pages_crawled_count"] == 3

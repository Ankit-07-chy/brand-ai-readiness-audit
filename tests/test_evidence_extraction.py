"""Unit tests for General Evidence Models and Extractors."""

import pytest

from src.evidence.models import (
    ContactEvidence,
    DateEvidence,
    DocumentEvidence,
    FormEvidence,
    ImageEvidence,
    LinkEvidence,
    PageEvidence,
    PageRoleSignals,
    Provenance,
    RobotsEvidence,
    SitemapEvidence,
    WebsiteEvidence,
)
from src.extraction.images import extract_page_images, check_is_tracking, infer_image_format
from src.extraction.links import extract_page_links_and_resources
from src.extraction.metadata import extract_page_metadata
from src.extraction.page import extract_page_content
from src.extraction.structured_data import extract_structured_data
from src.crawler.robots import parse_robots_txt_rules
from src.crawler.sitemap import parse_sitemap_xml_details


SAMPLE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <title>Acme Corp — Modern AI Solutions</title>
    <meta name="description" content="Acme Corp builds state-of-the-art AI readiness solutions for enterprise brands.">
    <link rel="canonical" href="https://example.com/about">
    <meta property="og:image" content="https://example.com/images/og-hero.jpg">
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "Acme Corp",
        "url": "https://example.com"
    }
    </script>
</head>
<body>
    <h1>Welcome to Acme Corp</h1>
    <p>Contact our team at contact@example.com or call +1-800-555-0199 for pricing.</p>
    <p>Updated on Jan 15, 2026.</p>
    
    <figure>
        <img src="/images/product-hero.jpg" alt="Acme AI Platform Hero" width="800" height="600" loading="lazy" />
        <figcaption>Acme AI Platform Architecture</figcaption>
    </figure>
    <img src="/tracking/pixel.gif" alt="tracking" width="1" height="1" />

    <h2>Our Key Solutions</h2>
    <ul>
        <li>Autonomous Data Auditing</li>
        <li>Generative Engine Optimization</li>
    </ul>

    <blockquote>Innovating since 2012.</blockquote>

    <table>
        <tr><th>Feature</th><th>Status</th></tr>
        <tr><td>AI Discoverability</td><td>Active</td></tr>
    </table>

    <a href="/docs/guide.pdf">Download Developer Guide (PDF)</a>
    <a href="https://external.org">External Partner</a>

    <form action="/submit-lead" method="post">
        <label for="email-field">Your Email</label>
        <input type="email" id="email-field" name="email" placeholder="name@company.com" />
        <input type="submit" value="Get Started" />
    </form>
</body>
</html>
"""


def test_evidence_models_instantiation():
    prov = Provenance(source_url="https://example.com", location="<h1>")
    assert prov.source_url == "https://example.com"
    assert prov.location == "<h1>"

    img = ImageEvidence(
        url="https://example.com/img.jpg",
        source_page="https://example.com",
        alt="Test",
        width=800,
        height=600,
        is_tracking_or_icon=False,
        provenance=prov,
        visual_analysis=None,
    )
    assert img.url == "https://example.com/img.jpg"
    assert img.visual_analysis is None

    robots_ev = RobotsEvidence(
        robots_url="https://example.com/robots.txt",
        exists=True,
        status_code=200,
        sitemap_declarations=["https://example.com/sitemap.xml"],
    )
    assert robots_ev.exists is True
    assert robots_ev.sitemap_declarations == ["https://example.com/sitemap.xml"]


def test_robots_txt_rule_parsing():
    content = """User-agent: *
Disallow: /admin/
Allow: /public/
Crawl-delay: 2

User-agent: GPTBot
Disallow: /private/

Sitemap: https://example.com/sitemap.xml
"""
    groups, sitemaps, allows, disallows, delay = parse_robots_txt_rules(content)
    assert len(groups) == 2
    assert groups[0].user_agent == "*"
    assert groups[0].disallow_rules == ["/admin/"]
    assert groups[0].allow_rules == ["/public/"]
    assert groups[1].user_agent == "GPTBot"
    assert groups[1].disallow_rules == ["/private/"]
    assert sitemaps == ["https://example.com/sitemap.xml"]
    assert delay == 2.0


def test_sitemap_index_parsing():
    sitemap_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <sitemap>
            <loc>https://example.com/sitemap-1.xml</loc>
        </sitemap>
    </sitemapindex>
    """
    is_index, child_indices, urls, lastmod_map = parse_sitemap_xml_details(sitemap_xml, sitemap_url="https://example.com/sitemap.xml")
    assert is_index is True
    assert child_indices == ["https://example.com/sitemap-1.xml"]
    assert urls == []

    urlset_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <url>
            <loc>https://example.com/page1</loc>
            <lastmod>2026-01-15</lastmod>
        </url>
    </urlset>
    """
    is_index2, child_indices2, urls2, lastmod_map2 = parse_sitemap_xml_details(urlset_xml, sitemap_url="https://example.com/sitemap.xml")
    assert is_index2 is False
    assert urls2 == ["https://example.com/page1"]
    assert lastmod_map2.get("https://example.com/page1") == "2026-01-15"


def test_page_metadata_extraction():
    meta = extract_page_metadata(SAMPLE_HTML, url="https://example.com/about")
    assert meta["title"] == "Acme Corp — Modern AI Solutions"
    assert meta["meta_description"] == "Acme Corp builds state-of-the-art AI readiness solutions for enterprise brands."
    assert meta["canonical_url"] == "https://example.com/about"
    assert meta["language"] == "en"


def test_page_content_and_contact_extraction():
    content = extract_page_content(SAMPLE_HTML, url="https://example.com/about")
    assert content["word_count"] > 10
    assert len(content["headings"]) == 2
    assert content["headings"][0]["text"] == "Welcome to Acme Corp"
    assert len(content["lists"]) == 1
    assert content["lists"][0] == ["Autonomous Data Auditing", "Generative Engine Optimization"]
    assert len(content["tables"]) == 1
    assert content["blockquotes"] == ["Innovating since 2012."]
    assert content["contacts"].emails == ["contact@example.com"]
    assert "+1-800-555-0199" in content["contacts"].phone_numbers[0]
    assert "Jan 15, 2026" in content["dates"].visible_dates


def test_image_extraction_and_tracking_filter():
    images = extract_page_images(SAMPLE_HTML, url="https://example.com/about")
    assert len(images) >= 2
    
    hero_img = next((img for img in images if "product-hero.jpg" in img.url), None)
    assert hero_img is not None
    assert hero_img.alt == "Acme AI Platform Hero"
    assert hero_img.width == 800
    assert hero_img.height == 600
    assert hero_img.caption == "Acme AI Platform Architecture"
    assert hero_img.is_tracking_or_icon is False

    tracking_img = next((img for img in images if "pixel.gif" in img.url), None)
    assert tracking_img is not None
    assert tracking_img.is_tracking_or_icon is True

    og_img = next((img for img in images if "og-hero.jpg" in img.url), None)
    assert og_img is not None


def test_links_resources_and_forms_extraction():
    res = extract_page_links_and_resources(SAMPLE_HTML, url="https://example.com/about")
    assert len(res["links"]) == 2
    assert "https://example.com/docs/guide.pdf" in res["internal_links"]
    assert "https://external.org/" in res["external_links"]

    assert len(res["documents"]) == 1
    assert res["documents"][0].file_type == "pdf"
    assert res["documents"][0].filename == "guide.pdf"

    assert len(res["forms"]) == 1
    form = res["forms"][0]
    assert form.action == "https://example.com/submit-lead"
    assert form.method == "post"
    assert len(form.inputs) == 2
    assert form.buttons == ["Get Started"]


def test_structured_data_extraction():
    sd = extract_structured_data(SAMPLE_HTML, url="https://example.com/about")
    assert sd["summary"]["detected_jsonld_count"] == 1
    assert sd["summary"]["detected_types"] == ["Organization"]
    assert len(sd["parsed_jsonld_objects"]) == 1
    assert sd["parsed_jsonld_objects"][0]["name"] == "Acme Corp"

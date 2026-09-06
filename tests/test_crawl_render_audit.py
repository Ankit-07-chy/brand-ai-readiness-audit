"""Unit tests for src/analysis/crawl_render_audit.py (CR-001 through CR-012)."""

import pytest
from src.analysis.crawl_render_audit import audit_crawl_render_skill
from src.models import FindingStatus, FindingSeverity


def test_collapsed_word_boundaries_test_case():
    """Test detecting collapsed word boundaries using the real-world test case 'Ibuildintelligentproductsandscalablewebexperiences.'."""
    html = """
    <!DOCTYPE html>
    <html>
    <head><title>Portfolio</title></head>
    <body>
        <h1>Ibuildintelligentproductsandscalablewebexperiences.</h1>
    </body>
    </html>
    """
    findings = audit_crawl_render_skill("https://example.com", html_content=html)
    finding_map = {f.check_id: f for f in findings}

    # CR-004 Text extractability flags suspicious word boundary collapse
    assert finding_map["CR-004"].status == FindingStatus.WARNING
    assert finding_map["CR-004"].evidence[0].observed["word_boundary_collapse_detected"] is True
    assert "Ibuildintelligentproductsandscalablewebexperiences" in finding_map["CR-004"].evidence[0].observed["suspicious_tokens"][0]

    # CR-007 Heading structure flags malformed H1 text
    assert finding_map["CR-007"].status == FindingStatus.WARNING
    assert "Ibuildintelligentproductsandscalablewebexperiences." in finding_map["CR-007"].evidence[0].observed["malformed_h1s"]


def test_normal_whitespace_and_clean_headings():
    """Test clean HTML with normal whitespace formatting."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Shivam Kumar — Software Engineering Intern</title>
        <meta name="description" content="Portfolio of Shivam Kumar building scalable web applications." />
        <link rel="canonical" href="https://example.com/" />
    </head>
    <body>
        <header>
            <nav><a href="/about">About</a> <a href="/projects">Projects</a></nav>
        </header>
        <main>
            <h1>I build intelligent products and scalable web experiences.</h1>
            <p>Welcome to my software engineering portfolio showcase.</p>
        </main>
    </body>
    </html>
    """
    findings = audit_crawl_render_skill("https://example.com/", html_content=html)
    finding_map = {f.check_id: f for f in findings}

    # CR-001 HTTP Status Pass
    assert finding_map["CR-001"].status == FindingStatus.PASS

    # CR-004 Text Extractability Pass
    assert finding_map["CR-004"].status == FindingStatus.PASS

    # CR-005 Title Pass
    assert finding_map["CR-005"].status == FindingStatus.PASS
    assert finding_map["CR-005"].evidence[0].observed["title"] == "Shivam Kumar — Software Engineering Intern"

    # CR-006 Meta Description Pass
    assert finding_map["CR-006"].status == FindingStatus.PASS
    assert "Shivam Kumar" in finding_map["CR-006"].evidence[0].observed["description"]

    # CR-007 H1 Pass
    assert finding_map["CR-007"].status == FindingStatus.PASS
    assert finding_map["CR-007"].evidence[0].observed["h1_texts"][0] == "I build intelligent products and scalable web experiences."

    # CR-008 Internal Links Pass
    assert finding_map["CR-008"].status == FindingStatus.PASS
    assert len(finding_map["CR-008"].evidence[0].observed["sample_internal_urls"]) == 2

    # CR-009 Canonical Pass
    assert finding_map["CR-009"].status == FindingStatus.PASS

    # CR-010 Content Discoverability Pass
    assert finding_map["CR-010"].status == FindingStatus.PASS
    assert "main" in finding_map["CR-010"].evidence[0].observed["sections_found"]

    # CR-012 Crawl Depth Readiness Pass
    assert finding_map["CR-012"].status == FindingStatus.PASS


def test_missing_meta_and_canonical():
    """Test handling of missing meta description and canonical link tags."""
    html = "<html><head><title>Test Page</title></head><body><h1>Heading</h1></body></html>"
    findings = audit_crawl_render_skill("https://example.com", html_content=html)
    finding_map = {f.check_id: f for f in findings}

    # CR-006 Meta description missing triggers low severity warning
    assert finding_map["CR-006"].status == FindingStatus.WARNING
    assert finding_map["CR-006"].severity == FindingSeverity.LOW

    # CR-009 Canonical link missing triggers low severity warning
    assert finding_map["CR-009"].status == FindingStatus.WARNING
    assert finding_map["CR-009"].severity == FindingSeverity.LOW


def test_rendered_vs_raw_content():
    """Test CR-011 comparison when rendered HTML content is provided vs absent."""
    raw_html = "<html><body><div id='app'></div></body></html>"
    rendered_html = "<html><body><div id='app'><h1>Rendered Header</h1><p>Lots of dynamic content populated by JavaScript single page app framework.</p></div></body></html>"

    # With rendered HTML passed
    findings_rendered = audit_crawl_render_skill(
        "https://example.com",
        html_content=raw_html,
        rendered_html_content=rendered_html,
    )
    finding_map_r = {f.check_id: f for f in findings_rendered}
    assert finding_map_r["CR-011"].status == FindingStatus.WARNING
    assert finding_map_r["CR-011"].evidence[0].observed["rendered_text_length"] > finding_map_r["CR-011"].evidence[0].observed["raw_text_length"]

    # Without rendered HTML passed
    findings_raw_only = audit_crawl_render_skill("https://example.com", html_content=raw_html)
    finding_map_raw = {f.check_id: f for f in findings_raw_only}
    assert finding_map_raw["CR-011"].status == FindingStatus.NOT_APPLICABLE

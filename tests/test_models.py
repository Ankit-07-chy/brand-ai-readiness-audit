"""Unit tests for src/models.py (Common Evidence & Finding Model)."""

import pytest
from pydantic import ValidationError

from src.models import (
    AuditReport,
    AuditSummary,
    Evidence,
    Finding,
    FindingSeverity,
    FindingStatus,
    calculate_summary,
)


def test_finding_status_and_severity_enums():
    """Verify supported enum values for status and severity."""
    assert set(e.value for e in FindingStatus) == {"pass", "fail", "warning", "not_applicable", "error"}
    assert set(e.value for e in FindingSeverity) == {"critical", "high", "medium", "low", "info"}


def test_evidence_model_valid():
    """Verify creating a valid Evidence instance."""
    ev = Evidence(
        source_url="https://example.com/robots.txt",
        evidence_type="http_header",
        observed={"User-agent": "GPTBot", "Disallow": "/"},
        expected={"User-agent": "GPTBot", "Allow": "/"},
        location="Line 4",
        details={"http_status": 200},
    )
    assert ev.source_url == "https://example.com/robots.txt"
    assert ev.evidence_type == "http_header"
    assert ev.observed == {"User-agent": "GPTBot", "Disallow": "/"}
    assert ev.location == "Line 4"


def test_evidence_model_validation_errors():
    """Verify Evidence raises validation errors for missing or invalid fields."""
    # Empty source_url
    with pytest.raises(ValidationError):
        Evidence(source_url="", evidence_type="dom", observed="data")

    # None observed data
    with pytest.raises(ValidationError):
        Evidence(source_url="https://example.com", evidence_type="dom", observed=None)


def test_finding_model_valid():
    """Verify creating a valid Finding instance with linked Evidence."""
    ev = Evidence(
        source_url="https://example.com",
        evidence_type="dom_snapshot",
        observed="<title>Example</title>",
    )
    finding = Finding(
        skill="crawl-render-audit",
        check_id="CR-001",
        title="GPTBot Allowed",
        status=FindingStatus.PASS,
        severity=FindingSeverity.HIGH,
        description="GPTBot is unblocked in robots.txt",
        evidence=[ev],
        recommendation="Maintain current robots.txt permissions for AI crawlers.",
    )
    assert finding.check_id == "CR-001"
    assert finding.status == FindingStatus.PASS
    assert len(finding.evidence) == 1
    assert finding.evidence[0].source_url == "https://example.com"


def test_finding_model_validation_errors():
    """Verify Finding raises validation errors for missing text fields or empty evidence."""
    ev = Evidence(source_url="https://example.com", evidence_type="dom", observed="data")

    # Missing skill
    with pytest.raises(ValidationError):
        Finding(
            skill="",
            check_id="CR-001",
            title="Title",
            status=FindingStatus.PASS,
            severity=FindingSeverity.INFO,
            description="Desc",
            evidence=[ev],
            recommendation="Rec",
        )

    # Invalid status value
    with pytest.raises(ValidationError):
        Finding(
            skill="skill-id",
            check_id="CR-001",
            title="Title",
            status="invalid_status",  # type: ignore
            severity=FindingSeverity.INFO,
            description="Desc",
            evidence=[ev],
            recommendation="Rec",
        )


def test_calculate_summary_all_pass():
    """Verify score is 100.0 when all checks pass."""
    ev = Evidence(source_url="https://example.com", evidence_type="test", observed="ok")
    findings = [
        Finding(
            skill="structured-data-audit",
            check_id=f"SD-00{i}",
            title=f"Check {i}",
            status=FindingStatus.PASS,
            severity=FindingSeverity.HIGH,
            description="Passed",
            evidence=[ev],
            recommendation="None",
        )
        for i in range(1, 4)
    ]
    summary = calculate_summary(findings)
    assert summary.total_checks == 3
    assert summary.passed == 3
    assert summary.failed == 0
    assert summary.warnings == 0
    assert summary.errors == 0
    assert summary.overall_score == 100.0


def test_calculate_summary_critical_failure_cap():
    """Verify overall score is capped at 40.0 if any Critical severity check fails."""
    ev = Evidence(source_url="https://example.com", evidence_type="test", observed="blocked")
    findings = [
        # Pass check
        Finding(
            skill="crawl-render-audit",
            check_id="CR-001",
            title="Sitemap Present",
            status=FindingStatus.PASS,
            severity=FindingSeverity.MEDIUM,
            description="Passed",
            evidence=[ev],
            recommendation="None",
        ),
        # Critical failure check
        Finding(
            skill="crawl-render-audit",
            check_id="CR-002",
            title="AI Crawlers Blocked",
            status=FindingStatus.FAIL,
            severity=FindingSeverity.CRITICAL,
            description="GPTBot blocked",
            evidence=[ev],
            recommendation="Unblock GPTBot in robots.txt",
        ),
    ]
    summary = calculate_summary(findings, critical_cap=40.0)
    assert summary.total_checks == 2
    assert summary.passed == 1
    assert summary.failed == 1
    assert summary.overall_score <= 40.0


def test_calculate_summary_not_applicable_ignored():
    """Verify not_applicable checks do not penalize overall score."""
    ev = Evidence(source_url="https://example.com", evidence_type="test", observed="n/a")
    findings = [
        Finding(
            skill="fact-quality-audit",
            check_id="FQ-001",
            title="E-commerce Pricing",
            status=FindingStatus.NOT_APPLICABLE,
            severity=FindingSeverity.HIGH,
            description="Site has no e-commerce products",
            evidence=[ev],
            recommendation="N/A",
        ),
        Finding(
            skill="fact-quality-audit",
            check_id="FQ-002",
            title="Brand Claim Clarity",
            status=FindingStatus.PASS,
            severity=FindingSeverity.HIGH,
            description="Claims are clear",
            evidence=[ev],
            recommendation="Maintain clarity",
        ),
    ]
    summary = calculate_summary(findings)
    assert summary.total_checks == 2
    assert summary.passed == 1
    assert summary.failed == 0
    assert summary.overall_score == 100.0


def test_audit_report_creation_and_serialization():
    """Verify AuditReport factory method, JSON serialization, and deserialization."""
    ev = Evidence(
        source_url="https://example.com",
        evidence_type="jsonld",
        observed={"@type": "Organization", "name": "Acme Corp"},
        expected={"@type": "Organization"},
        location="head > script[type='application/ld+json']",
    )
    finding = Finding(
        skill="entity-identity-audit",
        check_id="EI-001",
        title="Organization Schema",
        status=FindingStatus.PASS,
        severity=FindingSeverity.HIGH,
        description="Valid Organization JSON-LD found",
        evidence=[ev],
        recommendation="Keep Organization schema updated",
    )

    report = AuditReport.create(
        url="https://example.com",
        skills_run=["entity-identity-audit"],
        findings=[finding],
    )

    assert report.url == "https://example.com"
    assert report.summary.total_checks == 1
    assert report.summary.overall_score == 100.0

    # JSON Serialization & Deserialization
    json_str = report.model_dump_json()
    reconstituted = AuditReport.model_validate_json(json_str)

    assert reconstituted.url == report.url
    assert reconstituted.summary.overall_score == report.summary.overall_score
    assert len(reconstituted.findings) == 1
    assert reconstituted.findings[0].evidence[0].source_url == "https://example.com"

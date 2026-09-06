"""Deterministic page-role classifier returning structured PageRoleSignals."""

from typing import List, Optional
from urllib.parse import urlparse

from src.evidence.models import PageRoleSignals


def classify_page_role_signals(
    url: str,
    title: Optional[str] = None,
    headings: Optional[List[str]] = None,
    anchor_text: Optional[str] = None,
) -> PageRoleSignals:
    """Evaluates observable URL, title, heading, and anchor text signals to produce structured PageRoleSignals."""
    parsed = urlparse(url.lower().strip())
    path = parsed.path
    if not path or path == "/":
        return PageRoleSignals(
            signals=["root_path_slash"],
            classified_role="homepage",
        )

    path_lower = path.lower()
    title_lower = (title or "").lower()
    headings_lower = " ".join(headings or []).lower()
    anchor_lower = (anchor_text or "").lower()
    combined_text = f"{path_lower} {title_lower} {headings_lower} {anchor_lower}"

    # 1. Legal / Privacy / Terms
    legal_matches = [k for k in ("privacy", "terms", "legal", "disclaimer", "policy") if k in path_lower or k in title_lower]
    if legal_matches:
        return PageRoleSignals(
            signals=[f"legal_keyword:{k}" for k in legal_matches],
            classified_role="legal",
        )

    # 2. About / Team / Company
    about_matches = [k for k in ("about", "team", "company", "people", "who-we-are", "about us", "our team") if k in combined_text]
    if about_matches:
        return PageRoleSignals(
            signals=[f"about_keyword:{k}" for k in about_matches],
            classified_role="about",
        )

    # 3. Contact / Reach us
    contact_matches = [k for k in ("contact", "reach-us", "contact us", "get in touch") if k in combined_text]
    if contact_matches:
        return PageRoleSignals(
            signals=[f"contact_keyword:{k}" for k in contact_matches],
            classified_role="contact",
        )

    # 4. FAQ / Help
    faq_matches = [k for k in ("faq", "faqs", "help", "questions", "frequently asked questions") if k in combined_text]
    if faq_matches:
        return PageRoleSignals(
            signals=[f"faq_keyword:{k}" for k in faq_matches],
            classified_role="faq",
        )

    # 5. Documentation / Docs
    doc_matches = [k for k in ("docs", "documentation", "guide", "manual", "api-docs", "developer guide") if k in combined_text]
    if doc_matches:
        return PageRoleSignals(
            signals=[f"doc_keyword:{k}" for k in doc_matches],
            classified_role="documentation",
        )

    # 6. Product / Store / Shop
    prod_matches = [k for k in ("product", "products", "shop", "store", "pricing", "pricing plans") if k in combined_text]
    if prod_matches:
        return PageRoleSignals(
            signals=[f"product_keyword:{k}" for k in prod_matches],
            classified_role="product",
        )

    # 7. Service / Solutions
    service_matches = [k for k in ("service", "services", "solutions", "offerings", "our services") if k in combined_text]
    if service_matches:
        return PageRoleSignals(
            signals=[f"service_keyword:{k}" for k in service_matches],
            classified_role="service",
        )

    # 8. Project / Portfolio / Case Study
    proj_matches = [k for k in ("project", "projects", "portfolio", "case-study", "case-studies", "work", "selected work") if k in combined_text]
    if proj_matches:
        return PageRoleSignals(
            signals=[f"project_keyword:{k}" for k in proj_matches],
            classified_role="project",
        )

    # 9. Article / Blog / News
    article_matches = [k for k in ("blog", "article", "articles", "news", "posts", "blog post") if k in combined_text]
    if article_matches:
        return PageRoleSignals(
            signals=[f"article_keyword:{k}" for k in article_matches],
            classified_role="article",
        )

    return PageRoleSignals(
        signals=["no_explicit_role_keyword_matched"],
        classified_role="unknown",
    )


def classify_page_role(
    url: str,
    title: Optional[str] = None,
    headings: Optional[List[str]] = None,
    anchor_text: Optional[str] = None,
) -> str:
    """Backward-compatible function returning classified role string."""
    role_signals = classify_page_role_signals(url=url, title=title, headings=headings, anchor_text=anchor_text)
    return role_signals.classified_role

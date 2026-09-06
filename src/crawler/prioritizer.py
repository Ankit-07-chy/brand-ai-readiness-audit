"""Deterministic URL priority scoring module."""

from typing import List, Optional
from urllib.parse import urlparse

HIGH_VALUE_PATH_SIGNALS = {
    "about", "about-us", "company", "team", "people",
    "product", "products", "service", "services",
    "project", "projects", "portfolio", "case-study", "case-studies",
    "blog", "article", "articles", "news", "faq",
    "documentation", "docs", "pricing", "contact"
}

LOW_VALUE_PATH_SIGNALS = {
    "privacy", "terms", "legal", "login", "logout",
    "signup", "register", "cart", "checkout"
}


def calculate_url_priority(url: str, anchor_text: Optional[str] = None) -> int:
    """Computes a deterministic priority score for a URL based on path and anchor signals.
    
    Scores:
    - Homepage (/): 1000
    - High-value content path: 100
    - Neutral content path: 10
    - Low-value legal/action path: 1
    """
    parsed = urlparse(url.lower().strip())
    path = parsed.path
    if not path or path == "/":
        return 1000

    segments = set(path.strip("/").split("/"))
    anchor = (anchor_text or "").lower()

    # Check for low-value signals first
    if any(s in LOW_VALUE_PATH_SIGNALS for s in segments):
        return 1

    # Check for high-value signals in path or anchor text
    if any(s in HIGH_VALUE_PATH_SIGNALS for s in segments) or any(s in HIGH_VALUE_PATH_SIGNALS for s in anchor.split()):
        return 100

    # Default neutral content page
    return 10


def sort_urls_by_priority(url_items: List[tuple]) -> List[tuple]:
    """Sorts a list of (url, priority, depth, ...) items deterministically.
    
    Order: Priority descending, Depth ascending, URL length ascending, URL string ascending.
    """
    return sorted(url_items, key=lambda item: (-item[1], item[2], len(item[0]), item[0]))

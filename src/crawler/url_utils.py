"""URL utility functions for normalization, filtering, and domain verification."""

import re
from typing import Optional
from urllib.parse import urljoin, urlparse, urlunparse

IGNORABLE_SCHEMES = {"mailto:", "tel:", "javascript:", "data:", "file:", "ftp:"}

NON_HTML_EXTENSIONS = {
    # Images
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico", ".bmp", ".tiff",
    # Assets & Documents
    ".css", ".js", ".json", ".map", ".woff", ".woff2", ".ttf", ".eot",
    ".pdf", ".zip", ".gz", ".tar", ".tgz", ".rar", ".7z", ".exe", ".dmg",
    ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".mp3", ".mp4", ".wav", ".avi"
}

ACTION_KEYWORDS = {"login", "logout", "signup", "register", "cart", "checkout"}


def normalize_url(url: str, base_url: Optional[str] = None) -> str:
    """Normalizes a URL by resolving relative paths, stripping fragments, lowercasing host, and standardizing slashes."""
    if not url or not isinstance(url, str):
        return ""

    cleaned = url.strip()
    if base_url:
        cleaned = urljoin(base_url, cleaned)

    # Check scheme
    lower_val = cleaned.lower()
    for scheme in IGNORABLE_SCHEMES:
        if lower_val.startswith(scheme):
            return ""

    parsed = urlparse(cleaned)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return ""

    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()

    # Remove default port
    if ":" in netloc:
        host, port = netloc.split(":", 1)
        if (scheme == "http" and port == "80") or (scheme == "https" and port == "443"):
            netloc = host

    # Normalize path (remove fragment, strip double slashes)
    path = parsed.path
    if not path:
        path = "/"
    else:
        # Collapse multiple consecutive slashes
        path = re.sub(r"/{2,}", "/", path)
        # Strip trailing slash for non-root paths (e.g. /about/ -> /about)
        if len(path) > 1 and path.endswith("/"):
            path = path[:-1]

    # Reconstruct clean URL without fragment
    normalized = urlunparse((scheme, netloc, path, parsed.params, parsed.query, ""))
    return normalized


def extract_base_domain(url: str) -> str:
    """Extracts base domain (netloc) from a URL string."""
    parsed = urlparse(url.lower().strip())
    netloc = parsed.netloc
    if ":" in netloc:
        netloc = netloc.split(":", 1)[0]
    return netloc


def is_same_domain(url: str, base_domain: str) -> bool:
    """Checks whether target URL belongs to the same domain or subdomain as base_domain."""
    target_netloc = extract_base_domain(url)
    base = base_domain.lower().strip()
    if not target_netloc or not base:
        return False
    return target_netloc == base or target_netloc.endswith("." + base)


def is_crawlable_html_url(url: str, base_domain: Optional[str] = None, same_domain_only: bool = True) -> bool:
    """Determines whether a URL is a valid HTML page candidate for crawling."""
    if not url:
        return False

    normalized = normalize_url(url)
    if not normalized:
        return False

    parsed = urlparse(normalized)
    path_lower = parsed.path.lower()
    query_lower = parsed.query.lower()

    # 1. Domain check
    if same_domain_only and base_domain:
        if not is_same_domain(normalized, base_domain):
            return False

    # 2. Extension check
    for ext in NON_HTML_EXTENSIONS:
        if path_lower.endswith(ext):
            return False

    # 3. Action keywords check (e.g. login, logout, cart, checkout)
    for kw in ACTION_KEYWORDS:
        # Check path segments or query params
        path_segments = set(path_lower.strip("/").split("/"))
        if kw in path_segments or f"action={kw}" in query_lower:
            return False

    return True

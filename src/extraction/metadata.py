"""General Document Metadata Extractor."""

from html.parser import HTMLParser
import re
from typing import Any, Dict, List, Optional, Tuple

from src.evidence.models import Provenance


class MetadataHTMLParser(HTMLParser):
    """HTML Parser dedicated to head metadata, title, canonical, language, charset, and meta tags."""

    def __init__(self):
        super().__init__()
        self.language: Optional[str] = None
        self.charset: Optional[str] = None
        self.title_text: Optional[str] = None
        self.canonical_url: Optional[str] = None
        self.meta_description: Optional[str] = None
        self.meta_tags: List[Dict[str, str]] = []

        self._in_title = False
        self._title_buffer: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]):
        attr_dict = {k.lower(): (v or "") for k, v in attrs}
        tag_lower = tag.lower()

        if tag_lower == "html":
            lang = attr_dict.get("lang", "").strip()
            if lang:
                self.language = lang
        elif tag_lower == "title":
            self._in_title = True
            self._title_buffer = []
        elif tag_lower == "meta":
            self.meta_tags.append(attr_dict)
            name = attr_dict.get("name", "").lower()
            prop = attr_dict.get("property", "").lower()
            content = attr_dict.get("content", "").strip()
            charset_val = attr_dict.get("charset", "").strip()

            if charset_val:
                self.charset = charset_val
            elif "content-type" in attr_dict.get("http-equiv", "").lower() and content:
                match = re.search(r"charset=([a-zA-Z0-9_-]+)", content, re.IGNORECASE)
                if match:
                    self.charset = match.group(1)

            if (name == "description" or prop == "og:description") and content:
                if not self.meta_description:
                    self.meta_description = content
        elif tag_lower == "link":
            rel = attr_dict.get("rel", "").lower()
            href = attr_dict.get("href", "").strip()
            if "canonical" in rel and href:
                self.canonical_url = href

    def handle_endtag(self, tag: str):
        if tag.lower() == "title" and self._in_title:
            self.title_text = "".join(self._title_buffer).strip()
            self._in_title = False

    def handle_data(self, data: str):
        if self._in_title:
            self._title_buffer.append(data)


def extract_page_metadata(html_content: str, url: str) -> Dict[str, Any]:
    """Extracts page title, meta description, canonical, language, charset, and all head meta tags."""
    parser = MetadataHTMLParser()
    try:
        parser.feed(html_content)
    except Exception:
        pass

    return {
        "title": parser.title_text,
        "meta_description": parser.meta_description,
        "canonical_url": parser.canonical_url,
        "language": parser.language,
        "charset": parser.charset,
        "meta_tags": parser.meta_tags,
        "provenance": {
            "title": Provenance(source_url=url, location="<head> > <title>") if parser.title_text else None,
            "description": Provenance(source_url=url, location="<head> > <meta name='description'>") if parser.meta_description else None,
            "canonical": Provenance(source_url=url, location="<head> > <link rel='canonical'>") if parser.canonical_url else None,
        }
    }

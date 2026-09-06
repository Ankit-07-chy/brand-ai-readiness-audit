"""Generalized Image Evidence Extractor with asset filtering and provenance."""

from html.parser import HTMLParser
import re
from typing import List, Optional, Tuple
from urllib.parse import urlparse

from src.crawler.url_utils import normalize_url
from src.evidence.models import ImageEvidence, Provenance

TRACKING_PATTERNS = [
    r"1x1",
    r"pixel",
    r"tracking",
    r"favicon",
    r"badge",
    r"spinner",
    r"loader",
    r"blank\.gif",
    r"clear\.gif",
    r"spacer\.gif",
    r"analytics",
    r"telemetry",
]


class ImageHTMLParser(HTMLParser):
    """HTML Parser for discovering images, picture sources, captions, OpenGraph, and Twitter image tags."""

    def __init__(self, source_url: str):
        super().__init__()
        self.source_url = source_url
        self.images: List[ImageEvidence] = []
        self._tag_stack: List[Tuple[str, dict]] = []
        self._in_figure = False
        self._figure_images: List[ImageEvidence] = []
        self._in_figcaption = False
        self._figcaption_buffer: List[str] = []
        self._in_anchor_href: Optional[str] = None
        self._in_picture = False

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]):
        attr_dict = {k.lower(): (v or "") for k, v in attrs}
        tag_lower = tag.lower()
        self._tag_stack.append((tag_lower, attr_dict))

        if tag_lower == "a":
            href = attr_dict.get("href", "").strip()
            if href:
                self._in_anchor_href = href
        elif tag_lower == "picture":
            self._in_picture = True
        elif tag_lower == "figure":
            self._in_figure = True
            self._figure_images = []
        elif tag_lower == "figcaption":
            self._in_figcaption = True
            self._figcaption_buffer = []
        elif tag_lower in ("img", "source") and (tag_lower == "img" or self._in_picture):
            src_declared = attr_dict.get("src", "").strip()
            if not src_declared and attr_dict.get("srcset"):
                src_declared = attr_dict.get("srcset", "").strip().split()[0]
            if not src_declared and attr_dict.get("data-src"):
                src_declared = attr_dict.get("data-src", "").strip()

            if src_declared:
                resolved_img_url = normalize_url(src_declared, base_url=self.source_url) or src_declared
                alt = attr_dict.get("alt", "").strip() or None
                title = attr_dict.get("title", "").strip() or None
                width_val = parse_int(attr_dict.get("width"))
                height_val = parse_int(attr_dict.get("height"))
                srcset = attr_dict.get("srcset", "").strip() or None
                loading = attr_dict.get("loading", "").strip() or None

                is_tracking, filter_reason = check_is_tracking(resolved_img_url, alt, width_val, height_val)
                fmt = infer_image_format(resolved_img_url)

                source_type = "picture" if (self._in_picture and tag_lower == "img") else ("source" if tag_lower == "source" else "img")

                ev = ImageEvidence(
                    declared_url=src_declared,
                    resolved_url=resolved_img_url,
                    url=resolved_img_url,
                    source_page=self.source_url,
                    source_type=source_type,
                    alt=alt,
                    title=title,
                    declared_width=width_val,
                    declared_height=height_val,
                    intrinsic_width=None,
                    intrinsic_height=None,
                    srcset=srcset,
                    loading=loading,
                    format=fmt,
                    caption=None,
                    linked_href=normalize_url(self._in_anchor_href, base_url=self.source_url) if self._in_anchor_href else None,
                    is_tracking_or_icon=is_tracking,
                    filter_reason=filter_reason,
                    provenance=Provenance(
                        source_url=self.source_url,
                        location=f"<{tag_lower} src='{src_declared[:60]}'>",
                    ),
                    visual_analysis=None,
                )
                self.images.append(ev)
                if self._in_figure:
                    self._figure_images.append(ev)

        elif tag_lower == "meta":
            prop = (attr_dict.get("property") or attr_dict.get("name") or "").lower()
            content_declared = attr_dict.get("content", "").strip()
            if prop in ("og:image", "twitter:image") and content_declared:
                resolved_meta_img = normalize_url(content_declared, base_url=self.source_url) or content_declared
                if not any(img.declared_url == content_declared or img.resolved_url == resolved_meta_img for img in self.images):
                    is_tr, f_reason = check_is_tracking(resolved_meta_img, None, None, None)
                    ev = ImageEvidence(
                        declared_url=content_declared,
                        resolved_url=resolved_meta_img,
                        url=resolved_meta_img,
                        source_page=self.source_url,
                        source_type="og_image" if prop == "og:image" else "twitter_image",
                        alt=attr_dict.get("og:image:alt") or None,
                        format=infer_image_format(resolved_meta_img),
                        is_tracking_or_icon=is_tr,
                        filter_reason=f_reason,
                        provenance=Provenance(
                            source_url=self.source_url,
                            location=f"<meta property='{prop}'>",
                        ),
                        visual_analysis=None,
                    )
                    self.images.append(ev)

    def handle_endtag(self, tag: str):
        tag_lower = tag.lower()
        if self._tag_stack and self._tag_stack[-1][0] == tag_lower:
            self._tag_stack.pop()

        if tag_lower == "a" and self._in_anchor_href:
            self._in_anchor_href = None
        elif tag_lower == "picture" and self._in_picture:
            self._in_picture = False
        elif tag_lower == "figcaption" and self._in_figcaption:
            caption_text = "".join(self._figcaption_buffer).strip()
            if caption_text and self._figure_images:
                for img in self._figure_images:
                    img.caption = caption_text
            self._in_figcaption = False
        elif tag_lower == "figure" and self._in_figure:
            self._in_figure = False
            self._figure_images = []

    def handle_data(self, data: str):
        if self._in_figcaption:
            self._figcaption_buffer.append(data)


def parse_int(val: Optional[str]) -> Optional[int]:
    if not val:
        return None
    cleaned = re.sub(r"\D", "", val)
    return int(cleaned) if cleaned else None


def check_is_tracking(url: str, alt: Optional[str], width: Optional[int], height: Optional[int]) -> Tuple[bool, Optional[str]]:
    if width is not None and width <= 10 and height is not None and height <= 10:
        return True, "dimensions_<=_10px"
    url_lower = url.lower()
    alt_lower = (alt or "").lower()
    for pat in TRACKING_PATTERNS:
        if re.search(pat, url_lower) or re.search(pat, alt_lower):
            return True, f"filename_or_alt_matches_tracking_pattern:{pat}"
    return False, None


def infer_image_format(url: str) -> Optional[str]:
    path = urlparse(url).path.lower()
    for ext in (".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif", ".ico", ".bmp", ".avif"):
        if path.endswith(ext):
            return ext.lstrip(".")
    return None


def extract_page_images(html_content: str, url: str) -> List[ImageEvidence]:
    """Extracts generalized ImageEvidence collection from HTML page."""
    parser = ImageHTMLParser(source_url=url)
    try:
        parser.feed(html_content)
    except Exception:
        pass

    # Extract CSS background images using regex
    bg_urls = re.findall(r"background-image\s*:\s*url\((['\"]?)(.*?)\1\)", html_content, re.IGNORECASE)
    for _, bg_raw in bg_urls:
        bg_raw_clean = bg_raw.strip()
        if bg_raw_clean:
            bg_norm = normalize_url(bg_raw_clean, base_url=url) or bg_raw_clean
            if not any(img.declared_url == bg_raw_clean for img in parser.images):
                is_tr, f_reason = check_is_tracking(bg_norm, None, None, None)
                parser.images.append(ImageEvidence(
                    declared_url=bg_raw_clean,
                    resolved_url=bg_norm,
                    url=bg_norm,
                    source_page=url,
                    source_type="css_background",
                    format=infer_image_format(bg_norm),
                    is_tracking_or_icon=is_tr,
                    filter_reason=f_reason,
                    provenance=Provenance(source_url=url, location="CSS background-image"),
                    visual_analysis=None,
                ))

    return parser.images

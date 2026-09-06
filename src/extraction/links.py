"""General Links, Forms, and Resource Document Extractor."""

from html.parser import HTMLParser
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

from src.crawler.url_utils import (
    IGNORABLE_SCHEMES,
    NON_HTML_EXTENSIONS,
    extract_base_domain,
    is_same_domain,
    normalize_url,
)
from src.evidence.models import (
    DocumentEvidence,
    FormEvidence,
    FormInputField,
    LinkEvidence,
    Provenance,
)

DOCUMENT_EXTENSIONS = {
    ".pdf": "pdf",
    ".doc": "word",
    ".docx": "word",
    ".xls": "excel",
    ".xlsx": "excel",
    ".ppt": "powerpoint",
    ".pptx": "powerpoint",
    ".zip": "archive",
    ".gz": "archive",
    ".tar": "archive",
    ".rar": "archive",
    ".7z": "archive",
    ".csv": "csv",
    ".txt": "text",
}


class LinksFormsHTMLParser(HTMLParser):
    """HTML Parser for extracting anchors, downloadable document resources, and interactive forms."""

    def __init__(self, source_url: str, base_domain: str):
        super().__init__()
        self.source_url = source_url
        self.base_domain = base_domain

        self.links: List[LinkEvidence] = []
        self.documents: List[DocumentEvidence] = []
        self.forms: List[FormEvidence] = []

        self._in_anchor = False
        self._anchor_attr: Dict[str, str] = {}
        self._anchor_buffer: List[str] = []

        self._in_form = False
        self._form_attr: Dict[str, str] = {}
        self._form_inputs: List[FormInputField] = []
        self._form_buttons: List[str] = []
        self._current_label_text: Optional[str] = None
        self._in_label = False
        self._label_buffer: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]):
        attr_dict = {k.lower(): (v or "") for k, v in attrs}
        tag_lower = tag.lower()

        if tag_lower == "a":
            self._in_anchor = True
            self._anchor_attr = attr_dict
            self._anchor_buffer = []
        elif tag_lower == "form":
            self._in_form = True
            self._form_attr = attr_dict
            self._form_inputs = []
            self._form_buttons = []
        elif tag_lower == "label" and self._in_form:
            self._in_label = True
            self._label_buffer = []
        elif tag_lower in ("input", "textarea", "select") and self._in_form:
            inp_type = attr_dict.get("type", "text").lower()
            name = attr_dict.get("name", "").strip() or None
            inp_id = attr_dict.get("id", "").strip() or None
            placeholder = attr_dict.get("placeholder", "").strip() or None

            field = FormInputField(
                input_type=inp_type,
                name=name,
                id=inp_id,
                label=self._current_label_text,
                placeholder=placeholder,
            )
            self._form_inputs.append(field)
            if inp_type in ("submit", "button"):
                btn_val = attr_dict.get("value", "").strip()
                if btn_val:
                    self._form_buttons.append(btn_val)
        elif tag_lower == "button" and self._in_form:
            btn_txt = attr_dict.get("value", "").strip() or attr_dict.get("name", "").strip()
            if btn_txt:
                self._form_buttons.append(btn_txt)

    def handle_endtag(self, tag: str):
        tag_lower = tag.lower()

        if tag_lower == "a" and self._in_anchor:
            href = self._anchor_attr.get("href", "").strip()
            anchor_text = "".join(self._anchor_buffer).strip()

            if href and not any(href.lower().startswith(s) for s in IGNORABLE_SCHEMES):
                norm_href = normalize_url(href, base_url=self.source_url)
                if norm_href:
                    # Check if document resource
                    doc_ext = get_document_extension(norm_href)
                    if doc_ext:
                        fname = urlparse(norm_href).path.split("/")[-1]
                        doc_ev = DocumentEvidence(
                            url=norm_href,
                            source_page=self.source_url,
                            filename=fname,
                            file_type=DOCUMENT_EXTENSIONS.get(doc_ext, "binary"),
                            anchor_text=anchor_text or None,
                            provenance=Provenance(
                                source_url=self.source_url,
                                location=f"<a href='{href[:60]}'>",
                            ),
                        )
                        self.documents.append(doc_ev)

                    is_int = is_same_domain(norm_href, self.base_domain)
                    link_ev = LinkEvidence(
                        href=norm_href,
                        source_page=self.source_url,
                        anchor_text=anchor_text,
                        is_internal=is_int,
                        rel=self._anchor_attr.get("rel", "").strip() or None,
                        target=self._anchor_attr.get("target", "").strip() or None,
                        provenance=Provenance(
                            source_url=self.source_url,
                            location=f"<a href='{href[:60]}'>",
                        ),
                    )
                    self.links.append(link_ev)

            self._in_anchor = False

        elif tag_lower == "label" and self._in_label:
            self._current_label_text = "".join(self._label_buffer).strip()
            self._in_label = False

        elif tag_lower == "form" and self._in_form:
            action_raw = self._form_attr.get("action", "").strip()
            action_norm = normalize_url(action_raw, base_url=self.source_url) if action_raw else self.source_url
            method = self._form_attr.get("method", "get").lower()

            form_ev = FormEvidence(
                source_page=self.source_url,
                action=action_norm,
                method=method,
                inputs=list(self._form_inputs),
                buttons=list(self._form_buttons),
                provenance=Provenance(
                    source_url=self.source_url,
                    location=f"<form action='{action_raw[:60]}'>",
                ),
            )
            self.forms.append(form_ev)
            self._in_form = False

    def handle_data(self, data: str):
        if self._in_anchor:
            self._anchor_buffer.append(data)
        if self._in_label:
            self._label_buffer.append(data)


def get_document_extension(url: str) -> Optional[str]:
    path_lower = urlparse(url).path.lower()
    for ext in DOCUMENT_EXTENSIONS:
        if path_lower.endswith(ext):
            return ext
    return None


def extract_page_links_and_resources(html_content: str, url: str) -> Dict[str, Any]:
    """Extracts LinkEvidence, DocumentEvidence, and FormEvidence from an HTML page."""
    base_domain = extract_base_domain(url)
    parser = LinksFormsHTMLParser(source_url=url, base_domain=base_domain)
    try:
        parser.feed(html_content)
    except Exception:
        pass

    internal_urls = sorted(list(set(l.href for l in parser.links if l.is_internal)))
    external_urls = sorted(list(set(l.href for l in parser.links if not l.is_internal)))

    return {
        "links": parser.links,
        "internal_links": internal_urls,
        "external_links": external_urls,
        "documents": parser.documents,
        "forms": parser.forms,
    }

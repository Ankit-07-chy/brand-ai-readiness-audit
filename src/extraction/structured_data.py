"""Shared Extractor for Schema.org JSON-LD, Microdata, and OpenGraph Structured Data."""

from html.parser import HTMLParser
import json
from typing import Any, Dict, List, Optional, Set, Tuple

from src.evidence.models import Provenance


class StructuredDataHTMLParser(HTMLParser):
    """HTML Parser for extracting JSON-LD script payloads, Microdata items, and OpenGraph tags."""

    def __init__(self):
        super().__init__()
        self.jsonld_blocks: List[str] = []
        self.microdata_items: List[Dict[str, Any]] = []
        self.opengraph_tags: Dict[str, str] = {}

        self._in_jsonld = False
        self._jsonld_buffer: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]):
        attr_dict = {k.lower(): (v or "") for k, v in attrs}
        tag_lower = tag.lower()

        if tag_lower == "script":
            if attr_dict.get("type", "").strip().lower() == "application/ld+json":
                self._in_jsonld = True
                self._jsonld_buffer = []
        elif tag_lower == "meta":
            prop = attr_dict.get("property", "").lower() or attr_dict.get("name", "").lower()
            content = attr_dict.get("content", "").strip()
            if prop.startswith("og:") or prop.startswith("twitter:"):
                if content:
                    self.opengraph_tags[prop] = content

        if "itemscope" in attr_dict or "itemtype" in attr_dict or "itemprop" in attr_dict:
            self.microdata_items.append({
                "tag": tag_lower,
                "itemscope": "itemscope" in attr_dict,
                "itemtype": attr_dict.get("itemtype", ""),
                "itemprop": attr_dict.get("itemprop", ""),
                "content": attr_dict.get("content", ""),
            })

    def handle_endtag(self, tag: str):
        if tag.lower() == "script" and self._in_jsonld:
            j_txt = "".join(self._jsonld_buffer).strip()
            if j_txt:
                self.jsonld_blocks.append(j_txt)
            self._in_jsonld = False

    def handle_data(self, data: str):
        if self._in_jsonld:
            self._jsonld_buffer.append(data)


def extract_schema_objects(obj: Any) -> List[Dict[str, Any]]:
    """Recursively extracts dictionary objects containing @type or itemtype from nested structures."""
    results: List[Dict[str, Any]] = []
    if isinstance(obj, dict):
        if "@type" in obj or "itemtype" in obj or "type" in obj:
            results.append(obj)
        for key, val in obj.items():
            if key == "@graph" and isinstance(val, list):
                for item in val:
                    results.extend(extract_schema_objects(item))
            elif isinstance(val, (dict, list)):
                results.extend(extract_schema_objects(val))
    elif isinstance(obj, list):
        for item in obj:
            results.extend(extract_schema_objects(item))
    return results


def get_type_names(type_val: Any) -> List[str]:
    """Normalizes @type value(s) into a list of strings."""
    if isinstance(type_val, str):
        return [type_val]
    elif isinstance(type_val, list):
        return [str(t) for t in type_val if isinstance(t, str)]
    return []


def extract_structured_data(html_content: str, url: str) -> Dict[str, Any]:
    """Extracts JSON-LD blocks, detected schema types, Microdata items, and OpenGraph tags."""
    parser = StructuredDataHTMLParser()
    try:
        parser.feed(html_content)
    except Exception:
        pass

    detected_types: Set[str] = set()
    parsed_jsonld_objects: List[Any] = []
    jsonld_errors: List[str] = []

    for idx, raw_text in enumerate(parser.jsonld_blocks):
        try:
            data = json.loads(raw_text)
            parsed_jsonld_objects.append(data)
            schemas = extract_schema_objects(data)
            for s in schemas:
                for t in get_type_names(s.get("@type") or s.get("type")):
                    detected_types.add(t)
        except Exception as err:
            jsonld_errors.append(f"Block {idx}: {str(err)}")

    for m in parser.microdata_items:
        if m.get("itemtype"):
            detected_types.add(m["itemtype"].split("/")[-1])

    summary = {
        "detected_jsonld_count": len(parser.jsonld_blocks),
        "detected_types": sorted(list(detected_types)),
        "opengraph_tags_count": len(parser.opengraph_tags),
        "microdata_count": len(parser.microdata_items),
        "parse_errors": jsonld_errors,
    }

    return {
        "summary": summary,
        "jsonld_raw_blocks": parser.jsonld_blocks,
        "parsed_jsonld_objects": parsed_jsonld_objects,
        "microdata_items": parser.microdata_items,
        "opengraph_tags": parser.opengraph_tags,
        "provenance": Provenance(source_url=url, location="script[type='application/ld+json']"),
    }

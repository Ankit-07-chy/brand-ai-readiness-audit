"""General Evidence Extraction Package."""

from src.extraction.images import extract_page_images
from src.extraction.links import extract_page_links_and_resources
from src.extraction.metadata import extract_page_metadata
from src.extraction.page import extract_page_content
from src.extraction.structured_data import extract_structured_data, extract_schema_objects, get_type_names

__all__ = [
    "extract_page_metadata",
    "extract_page_content",
    "extract_page_images",
    "extract_page_links_and_resources",
    "extract_structured_data",
    "extract_schema_objects",
    "get_type_names",
]

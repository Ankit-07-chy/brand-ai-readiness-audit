"""Semantic Understanding Layer Interface & Adapter.

Defines the clean architectural boundary separating raw observable evidence
(WebsiteEvidence / PageEvidence) from semantic interpretation (entities, facts,
claims, topics, and actions).

Currently operates as a deterministic baseline adapter without LLM/OCR dependencies.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from src.evidence.models import PageEvidence, WebsiteEvidence


class ExtractedEntity(BaseModel):
    """Semantic entity representation."""
    name: str = Field(..., description="Canonical entity name")
    entity_type: str = Field(..., description="Entity category (Organization, Person, Product, etc.)")
    source_url: str = Field(..., description="Source page URL")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Observable entity attributes")


class ExtractedFact(BaseModel):
    """Factual proposition representation."""
    proposition: str = Field(..., description="Factual claim or proposition string")
    category: str = Field(default="general", description="Fact category (pricing, spec, policy, team, location)")
    source_url: str = Field(..., description="Source page URL")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score")


class SemanticUnderstandingAdapter:
    """Baseline adapter converting raw WebsiteEvidence / PageEvidence into structured semantic objects."""

    def __init__(self, website_evidence: WebsiteEvidence):
        self.evidence = website_evidence

    def extract_entities(self) -> List[ExtractedEntity]:
        """Extracts candidate entities from structured data and document metadata."""
        entities: List[ExtractedEntity] = []
        for p in self.evidence.pages:
            # From page title/headings
            if p.title:
                entities.append(ExtractedEntity(
                    name=p.title,
                    entity_type="WebPage",
                    source_url=p.url,
                    attributes={"canonical_url": p.canonical_url},
                ))
            # From contacts
            if p.contacts and (p.contacts.emails or p.contacts.phone_numbers):
                entities.append(ExtractedEntity(
                    name=f"ContactPoint ({p.url})",
                    entity_type="ContactPoint",
                    source_url=p.url,
                    attributes={
                        "emails": p.contacts.emails,
                        "phones": p.contacts.phone_numbers,
                    },
                ))
        return entities

    def extract_key_facts(self) -> List[ExtractedFact]:
        """Extracts factual propositions from headings and paragraph text blocks."""
        facts: List[ExtractedFact] = []
        for p in self.evidence.pages:
            for h in p.headings:
                facts.append(ExtractedFact(
                    proposition=h.get("text", ""),
                    category="heading",
                    source_url=p.url,
                    confidence=0.9,
                ))
        return facts

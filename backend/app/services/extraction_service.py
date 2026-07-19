from dataclasses import dataclass
from datetime import date
from functools import lru_cache

from dateutil import parser as date_parser

from app.data.extraction_patterns import (
    AGENCY_KEYWORDS,
    CASE_NUMBER_PATTERNS,
    REQUIRED_ACTION_PATTERNS,
)


@dataclass
class Entity:
    entity_type: str
    value: str
    confidence_score: float
    flagged_for_review: bool = False


DATE_CONFIDENCE_SPACY = 0.9
CASE_NUMBER_CONFIDENCE_REGEX = 0.92
AGENCY_CONFIDENCE_KEYWORD = 0.9
REQUIRED_ACTION_CONFIDENCE_REGEX = 0.75
CONFIDENCE_FLAG_THRESHOLD = 0.6


class ExtractionService:
    def __init__(self):
        self._nlp = None

    def _load(self):
        if self._nlp is None:
            import spacy

            self._nlp = spacy.load("en_core_web_sm")

    def _extract_deadline(self, doc) -> Entity | None:
        for ent in doc.ents:
            if ent.label_ == "DATE":
                try:
                    parsed = date_parser.parse(ent.text, fuzzy=True, default=date.today().replace(day=1))
                except (ValueError, OverflowError):
                    continue
                return Entity(
                    entity_type="deadline",
                    value=parsed.date().isoformat(),
                    confidence_score=DATE_CONFIDENCE_SPACY,
                    flagged_for_review=DATE_CONFIDENCE_SPACY < CONFIDENCE_FLAG_THRESHOLD,
                )
        return None

    def _extract_case_number(self, text: str, doc_type: str) -> Entity | None:
        patterns = CASE_NUMBER_PATTERNS.get(doc_type, [])
        for pattern in patterns:
            match = pattern.search(text)
            if match:
                value = match.group(1) if match.groups() else match.group(0)
                return Entity(
                    entity_type="case_number",
                    value=value,
                    confidence_score=CASE_NUMBER_CONFIDENCE_REGEX,
                )
        return None

    def _extract_agency(self, text: str, doc_type: str) -> Entity | None:
        keywords = AGENCY_KEYWORDS.get(doc_type, [])
        for kw in keywords:
            if kw.lower() in text.lower():
                return Entity(
                    entity_type="agency",
                    value=kw,
                    confidence_score=AGENCY_CONFIDENCE_KEYWORD,
                )
        return None

    def _extract_required_action(self, text: str) -> Entity | None:
        for pattern in REQUIRED_ACTION_PATTERNS:
            match = pattern.search(text)
            if match:
                phrase = match.group(1).strip().rstrip(".")
                return Entity(
                    entity_type="required_action",
                    value=phrase,
                    confidence_score=REQUIRED_ACTION_CONFIDENCE_REGEX,
                    flagged_for_review=REQUIRED_ACTION_CONFIDENCE_REGEX < CONFIDENCE_FLAG_THRESHOLD,
                )
        return None

    def extract(self, text: str, doc_type: str) -> list[Entity]:
        self._load()
        spacy_doc = self._nlp(text)

        entities: list[Entity] = []
        for extractor in (
            lambda: self._extract_deadline(spacy_doc),
            lambda: self._extract_case_number(text, doc_type),
            lambda: self._extract_agency(text, doc_type),
            lambda: self._extract_required_action(text),
        ):
            entity = extractor()
            if entity:
                entities.append(entity)

        return entities


@lru_cache(maxsize=1)
def get_extraction_service() -> ExtractionService:
    return ExtractionService()

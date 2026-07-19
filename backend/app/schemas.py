from datetime import datetime

from pydantic import BaseModel


class EntityOut(BaseModel):
    entity_type: str
    value: str | None
    confidence_score: float
    flagged_for_review: bool

    class Config:
        from_attributes = True


class UrgencyOut(BaseModel):
    score: float
    feature_breakdown: dict[str, float]


class ExplanationOut(BaseModel):
    literacy_level: str
    generated_text: str
    source_citations: list[str]


class TimelineEventOut(BaseModel):
    event_type: str
    related_document_id: int | None
    description: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentSummaryOut(BaseModel):
    id: int
    doc_type: str
    agency: str | None
    uploaded_at: datetime
    deadline: str | None
    urgency_score: float | None
    flagged_for_review: bool

    class Config:
        from_attributes = True


class TimelineResponse(BaseModel):
    case_id: int
    display_name: str
    documents: list[DocumentSummaryOut]
    events: list[TimelineEventOut]


class DocumentDetailOut(BaseModel):
    id: int
    case_id: int
    doc_type: str
    agency: str | None
    raw_text: str | None
    uploaded_at: datetime
    ocr_confidence: float | None
    document_flagged_for_review: bool
    entities: list[EntityOut]
    urgency: UrgencyOut | None
    explanation: ExplanationOut | None
    conflict_events: list[TimelineEventOut]


class CaseCreate(BaseModel):
    display_name: str


class CaseOut(BaseModel):
    id: int
    display_name: str

    class Config:
        from_attributes = True

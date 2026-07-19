from datetime import date, datetime

from sqlalchemy.orm import Session

from app.ml.urgency_features import build_features
from app.models import Document, ExplanationRecord, ExtractedEntity, UrgencyScore
from app.services.case_memory_service import get_case_memory_service
from app.services.classification_service import get_classification_service
from app.services.confidence_service import get_confidence_service
from app.services.extraction_service import get_extraction_service
from app.services.ingestion_service import get_ingestion_service
from app.services.rag_service import get_rag_service


def _parse_deadline(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value).date()
    except ValueError:
        return None


def process_new_document(db: Session, case_id: int, filename: str, file_bytes: bytes) -> Document:
    """Runs the full synchronous pipeline for a newly uploaded document:
    ingestion -> classification -> extraction -> confidence -> urgency ->
    RAG explanation -> case-memory conflict check. Persists everything and
    returns the created Document with all relations populated.
    """
    ingestion = get_ingestion_service().process(filename, file_bytes)
    raw_text = ingestion["raw_text"]
    ocr_confidence = ingestion["ocr_confidence"]

    confidence_service = get_confidence_service()
    document_flagged = confidence_service.should_flag_entire_document(ocr_confidence)

    classification = get_classification_service().classify(raw_text)
    doc_type = classification["doc_type"]

    document = Document(
        case_id=case_id,
        doc_type=doc_type,
        agency=None,
        raw_text=raw_text,
        ocr_confidence=ocr_confidence,
    )
    db.add(document)
    db.flush()

    extracted_entities = get_extraction_service().extract(raw_text, doc_type)
    confidence_service.apply_field_confidence(ocr_confidence, extracted_entities)

    for entity in extracted_entities:
        db.add(
            ExtractedEntity(
                document_id=document.id,
                entity_type=entity.entity_type,
                value=entity.value,
                confidence_score=entity.confidence_score,
                flagged_for_review=entity.flagged_for_review or document_flagged,
            )
        )

    agency_entity = next((e for e in extracted_entities if e.entity_type == "agency"), None)
    if agency_entity:
        document.agency = agency_entity.value

    deadline_entity = next((e for e in extracted_entities if e.entity_type == "deadline"), None)
    deadline_date = _parse_deadline(deadline_entity.value if deadline_entity else None)

    features = build_features(doc_type, raw_text, deadline_date)
    urgency_result = None
    try:
        urgency_result = get_urgency_service_safe().score(features)
    except FileNotFoundError:
        pass

    if urgency_result:
        import json

        db.add(
            UrgencyScore(
                document_id=document.id,
                score=urgency_result["score"],
                feature_breakdown=json.dumps(urgency_result["feature_breakdown"]),
            )
        )

    try:
        rag_result = get_rag_service().generate(raw_text, literacy_level="standard")
        import json

        db.add(
            ExplanationRecord(
                document_id=document.id,
                literacy_level="standard",
                generated_text=rag_result["text"],
                source_citations=json.dumps(rag_result["citations"]),
            )
        )
    except Exception:
        # Explanation generation depends on an external API (Groq); the rest
        # of the pipeline result should still be usable if it's unavailable.
        pass

    db.flush()

    get_case_memory_service().check_conflict(db, case_id, document)

    db.commit()
    db.refresh(document)
    return document


def get_urgency_service_safe():
    from app.services.urgency_service import get_urgency_service

    return get_urgency_service()

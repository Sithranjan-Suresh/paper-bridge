from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Case, Document, TimelineEvent
from app.schemas import DocumentDetailOut
from app.services.pipeline_service import PipelineError, process_new_document

router = APIRouter(tags=["documents"])


def _document_detail(document, db: Session) -> DocumentDetailOut:
    import json

    from app.schemas import EntityOut, ExplanationOut, TimelineEventOut, UrgencyOut

    explanation = None
    if document.explanations:
        latest = document.explanations[-1]
        explanation = ExplanationOut(
            literacy_level=latest.literacy_level,
            generated_text=latest.generated_text,
            source_citations=json.loads(latest.source_citations or "[]"),
        )

    urgency = None
    if document.urgency_score:
        urgency = UrgencyOut(
            score=document.urgency_score.score,
            feature_breakdown=json.loads(document.urgency_score.feature_breakdown or "{}"),
        )

    document_flagged = any(e.flagged_for_review for e in document.entities)

    conflict_events = (
        db.query(TimelineEvent)
        .filter(
            (TimelineEvent.document_id == document.id) | (TimelineEvent.related_document_id == document.id)
        )
        .filter(TimelineEvent.event_type.in_(["conflicts_with", "supersedes"]))
        .all()
    )

    return DocumentDetailOut(
        id=document.id,
        case_id=document.case_id,
        doc_type=document.doc_type,
        agency=document.agency,
        raw_text=document.raw_text,
        uploaded_at=document.uploaded_at,
        ocr_confidence=document.ocr_confidence,
        document_flagged_for_review=document_flagged,
        entities=[EntityOut.model_validate(e) for e in document.entities],
        urgency=urgency,
        explanation=explanation,
        conflict_events=[TimelineEventOut.model_validate(e) for e in conflict_events],
    )


@router.post("/cases/{case_id}/documents", response_model=DocumentDetailOut)
async def upload_document(case_id: int, file: UploadFile, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    file_bytes = await file.read()
    try:
        document = process_new_document(db, case_id, file.filename, file_bytes)
    except PipelineError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return _document_detail(document, db)


@router.get("/documents/{document_id}", response_model=DocumentDetailOut)
def get_document(document_id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return _document_detail(document, db)


@router.get("/documents/{document_id}/explanation")
def regenerate_explanation(document_id: int, literacy_level: str = "standard", db: Session = Depends(get_db)):
    import json

    from app.models import ExplanationRecord
    from app.services.rag_service import get_rag_service
    from app.schemas import ExplanationOut

    if literacy_level not in ("simple", "standard", "detailed"):
        raise HTTPException(status_code=400, detail="literacy_level must be one of: simple, standard, detailed")

    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    existing = next((e for e in document.explanations if e.literacy_level == literacy_level), None)
    if existing:
        return ExplanationOut(
            literacy_level=existing.literacy_level,
            generated_text=existing.generated_text,
            source_citations=json.loads(existing.source_citations or "[]"),
        )

    try:
        result = get_rag_service().generate(document.raw_text, literacy_level=literacy_level)
    except Exception as exc:
        raise HTTPException(
            status_code=502, detail="Explanation service is temporarily unavailable. Please try again shortly."
        ) from exc

    record = ExplanationRecord(
        document_id=document.id,
        literacy_level=literacy_level,
        generated_text=result["text"],
        source_citations=json.dumps(result["citations"]),
    )
    db.add(record)
    db.commit()

    return ExplanationOut(
        literacy_level=literacy_level,
        generated_text=result["text"],
        source_citations=result["citations"],
    )

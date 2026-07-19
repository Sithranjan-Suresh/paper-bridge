from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Case
from app.schemas import DocumentDetailOut
from app.services.pipeline_service import process_new_document

router = APIRouter(tags=["documents"])


def _document_detail(document) -> DocumentDetailOut:
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
        conflict_events=[],
    )


@router.post("/cases/{case_id}/documents", response_model=DocumentDetailOut)
async def upload_document(case_id: int, file: UploadFile, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    file_bytes = await file.read()
    document = process_new_document(db, case_id, file.filename, file_bytes)
    return _document_detail(document)

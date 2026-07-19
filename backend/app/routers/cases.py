from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Case, TimelineEvent
from app.schemas import CaseCreate, CaseOut, DocumentSummaryOut, TimelineResponse

router = APIRouter(prefix="/cases", tags=["cases"])


@router.post("", response_model=CaseOut)
def create_case(payload: CaseCreate, db: Session = Depends(get_db)):
    case = Case(display_name=payload.display_name)
    db.add(case)
    db.commit()
    db.refresh(case)
    return case


def _document_summary(document) -> DocumentSummaryOut:
    deadline = next((e.value for e in document.entities if e.entity_type == "deadline"), None)
    flagged = any(e.flagged_for_review for e in document.entities)
    return DocumentSummaryOut(
        id=document.id,
        doc_type=document.doc_type,
        agency=document.agency,
        uploaded_at=document.uploaded_at,
        deadline=deadline,
        urgency_score=document.urgency_score.score if document.urgency_score else None,
        flagged_for_review=flagged,
    )


@router.get("/{case_id}/timeline", response_model=TimelineResponse)
def get_case_timeline(case_id: int, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    documents = sorted(
        case.documents,
        key=lambda d: d.urgency_score.score if d.urgency_score else 0,
        reverse=True,
    )
    events = db.query(TimelineEvent).filter(TimelineEvent.case_id == case_id).all()

    return TimelineResponse(
        case_id=case.id,
        display_name=case.display_name,
        documents=[_document_summary(d) for d in documents],
        events=events,
    )

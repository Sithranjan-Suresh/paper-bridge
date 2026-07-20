from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Case, TimelineEvent
from app.schemas import CaseCreate, CaseOut, DocumentSummaryOut, TimelineResponse

router = APIRouter(prefix="/cases", tags=["cases"])


@router.get("/demo", response_model=CaseOut)
def get_demo_case(db: Session = Depends(get_db)):
    from app.seed import DEMO_CASE_NAME

    case = db.query(Case).filter(Case.display_name == DEMO_CASE_NAME).first()
    if not case:
        raise HTTPException(status_code=404, detail="Demo case not seeded")
    return case


@router.post("", response_model=CaseOut)
def create_case(payload: CaseCreate, db: Session = Depends(get_db)):
    case = Case(display_name=payload.display_name)
    db.add(case)
    db.commit()
    db.refresh(case)
    return case


def _derive_subject(document) -> str | None:
    """A short, distinguishing subject line for the timeline card — without
    this, two documents of the same type (e.g. an original and a rescheduled
    USCIS notice) are indistinguishable at a glance."""
    action = next((e.value for e in document.entities if e.entity_type == "required_action"), None)
    if not action:
        return None
    subject = action[0].upper() + action[1:] if action else action
    return subject if len(subject) <= 60 else subject[:57] + "…"


def _document_summary(document) -> DocumentSummaryOut:
    deadline = next((e.value for e in document.entities if e.entity_type == "deadline"), None)
    flagged = any(e.flagged_for_review for e in document.entities)
    return DocumentSummaryOut(
        id=document.id,
        doc_type=document.doc_type,
        agency=document.agency,
        subject=_derive_subject(document),
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

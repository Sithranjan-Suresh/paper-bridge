from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Case
from app.schemas import CaseCreate, CaseOut

router = APIRouter(prefix="/cases", tags=["cases"])


@router.post("", response_model=CaseOut)
def create_case(payload: CaseCreate, db: Session = Depends(get_db)):
    case = Case(display_name=payload.display_name)
    db.add(case)
    db.commit()
    db.refresh(case)
    return case

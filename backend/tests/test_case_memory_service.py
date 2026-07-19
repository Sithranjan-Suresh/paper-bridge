from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import Case, Document, ExtractedEntity
from app.services.case_memory_service import CaseMemoryService


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def service():
    return CaseMemoryService()


def _make_document(db, case_id, doc_type, agency, case_number, deadline, uploaded_at, required_action="Appear for appointment"):
    doc = Document(case_id=case_id, doc_type=doc_type, agency=agency, uploaded_at=uploaded_at)
    db.add(doc)
    db.flush()
    db.add(ExtractedEntity(document_id=doc.id, entity_type="case_number", value=case_number, confidence_score=0.9))
    db.add(ExtractedEntity(document_id=doc.id, entity_type="deadline", value=deadline, confidence_score=0.9))
    db.add(ExtractedEntity(document_id=doc.id, entity_type="required_action", value=required_action, confidence_score=0.9))
    db.flush()
    return doc


def test_conflict_fires_when_deadline_changes_for_same_case_number(db, service):
    case = Case(display_name="Test Case")
    db.add(case)
    db.flush()

    now = datetime.utcnow()
    doc1 = _make_document(db, case.id, "uscis_notice", "USCIS", "MSC123", "2026-01-10", now - timedelta(days=10))
    doc2 = _make_document(db, case.id, "uscis_notice", "USCIS", "MSC123", "2026-02-15", now)

    events = service.check_conflict(db, case.id, doc2)

    assert len(events) == 1
    assert events[0].event_type == "supersedes"
    assert events[0].related_document_id == doc1.id


def test_no_merge_when_case_numbers_differ_for_same_agency(db, service):
    case = Case(display_name="Test Case")
    db.add(case)
    db.flush()

    now = datetime.utcnow()
    _make_document(db, case.id, "uscis_notice", "USCIS", "MSC111", "2026-01-10", now - timedelta(days=10))
    doc2 = _make_document(db, case.id, "uscis_notice", "USCIS", "MSC222", "2026-02-15", now)

    events = service.check_conflict(db, case.id, doc2)

    # Different case numbers for the same agency must not be treated as related.
    assert len(events) == 0


def test_no_conflict_when_fields_are_unchanged(db, service):
    case = Case(display_name="Test Case")
    db.add(case)
    db.flush()

    now = datetime.utcnow()
    _make_document(db, case.id, "uscis_notice", "USCIS", "MSC123", "2026-01-10", now - timedelta(days=10))
    doc2 = _make_document(db, case.id, "uscis_notice", "USCIS", "MSC123", "2026-01-10", now)

    events = service.check_conflict(db, case.id, doc2)

    assert len(events) == 0

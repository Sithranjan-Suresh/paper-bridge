import json
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Case, Document, ExplanationRecord, ExtractedEntity, TimelineEvent, UrgencyScore

DEMO_CASE_NAME = "Demo Case — Martinez Family"


def _add_entities(db: Session, document_id: int, entities: list[dict]):
    for e in entities:
        db.add(
            ExtractedEntity(
                document_id=document_id,
                entity_type=e["entity_type"],
                value=e["value"],
                confidence_score=e["confidence_score"],
                flagged_for_review=e.get("flagged_for_review", False),
            )
        )


def _add_urgency(db: Session, document_id: int, score: float, breakdown: dict):
    db.add(
        UrgencyScore(
            document_id=document_id,
            score=score,
            feature_breakdown=json.dumps(breakdown),
        )
    )


def _add_explanation(db: Session, document_id: int, text: str, citations: list[str], literacy_level: str = "standard"):
    db.add(
        ExplanationRecord(
            document_id=document_id,
            literacy_level=literacy_level,
            generated_text=text,
            source_citations=json.dumps(citations),
        )
    )


def seed_demo_case(db: Session) -> None:
    existing = db.query(Case).filter(Case.display_name == DEMO_CASE_NAME).first()
    if existing:
        return

    now = datetime.utcnow()
    case = Case(display_name=DEMO_CASE_NAME, created_at=now - timedelta(days=30))
    db.add(case)
    db.flush()

    # --- Document 1: USCIS notice (initial biometrics appointment) ---
    doc1 = Document(
        case_id=case.id,
        doc_type="uscis_notice",
        agency="USCIS",
        raw_text=(
            "U.S. Citizenship and Immigration Services\n"
            "NOTICE OF ACTION - Form I-797C\n"
            "Case Number: MSC2190012345\n"
            "You are required to appear for a biometrics appointment on or before "
            + (now - timedelta(days=10)).strftime("%B %d, %Y")
            + ". Failure to appear may result in denial of your application."
        ),
        uploaded_at=now - timedelta(days=30),
        ocr_confidence=0.97,
    )
    db.add(doc1)
    db.flush()
    _add_entities(
        db,
        doc1.id,
        [
            {"entity_type": "case_number", "value": "MSC2190012345", "confidence_score": 0.96},
            {"entity_type": "deadline", "value": (now - timedelta(days=10)).strftime("%Y-%m-%d"), "confidence_score": 0.94},
            {"entity_type": "agency", "value": "USCIS", "confidence_score": 0.99},
            {"entity_type": "required_action", "value": "Appear for biometrics appointment", "confidence_score": 0.9},
        ],
    )
    _add_urgency(
        db,
        doc1.id,
        score=45.0,
        breakdown={
            "days_until_deadline": -0.35,
            "doc_type_base_severity": 0.4,
            "consequence_keywords": 0.25,
            "notice_stage": 0.1,
        },
    )
    _add_explanation(
        db,
        doc1.id,
        "This is a biometrics appointment notice from USCIS for case MSC2190012345. "
        "The original appointment deadline has passed — this letter has been superseded by a newer notice (see below).",
        ["uscis-biometrics-101"],
    )
    db.add(
        TimelineEvent(
            case_id=case.id,
            document_id=doc1.id,
            event_type="new",
            description="Initial USCIS biometrics notice uploaded.",
            created_at=now - timedelta(days=30),
        )
    )

    # --- Document 2: USCIS notice (rescheduled — conflicts with Document 1) ---
    doc2 = Document(
        case_id=case.id,
        doc_type="uscis_notice",
        agency="USCIS",
        raw_text=(
            "U.S. Citizenship and Immigration Services\n"
            "NOTICE OF ACTION - Form I-797C (RESCHEDULED)\n"
            "Case Number: MSC2190012345\n"
            "Your biometrics appointment has been rescheduled. You must appear on or before "
            + (now + timedelta(days=12)).strftime("%B %d, %Y")
            + ". This notice supersedes any prior appointment notice for this case."
        ),
        uploaded_at=now - timedelta(days=2),
        ocr_confidence=0.98,
    )
    db.add(doc2)
    db.flush()
    _add_entities(
        db,
        doc2.id,
        [
            {"entity_type": "case_number", "value": "MSC2190012345", "confidence_score": 0.97},
            {"entity_type": "deadline", "value": (now + timedelta(days=12)).strftime("%Y-%m-%d"), "confidence_score": 0.95},
            {"entity_type": "agency", "value": "USCIS", "confidence_score": 0.99},
            {"entity_type": "required_action", "value": "Appear for rescheduled biometrics appointment", "confidence_score": 0.92},
        ],
    )
    _add_urgency(
        db,
        doc2.id,
        score=78.0,
        breakdown={
            "days_until_deadline": 0.5,
            "doc_type_base_severity": 0.4,
            "consequence_keywords": 0.2,
            "notice_stage": 0.15,
        },
    )
    _add_explanation(
        db,
        doc2.id,
        "USCIS rescheduled your biometrics appointment for case MSC2190012345. "
        "You now have a new deadline of "
        + (now + timedelta(days=12)).strftime("%B %d, %Y")
        + ". This replaces the earlier appointment date — only this new date matters.",
        ["uscis-biometrics-101", "uscis-rescheduling"],
    )
    db.add(
        TimelineEvent(
            case_id=case.id,
            document_id=doc2.id,
            event_type="new",
            description="Rescheduled USCIS biometrics notice uploaded.",
            created_at=now - timedelta(days=2),
        )
    )
    db.add(
        TimelineEvent(
            case_id=case.id,
            document_id=doc2.id,
            event_type="supersedes",
            related_document_id=doc1.id,
            description=(
                "This notice supersedes the earlier USCIS biometrics notice (case MSC2190012345): "
                "the appointment deadline changed from "
                + (now - timedelta(days=10)).strftime("%B %d, %Y")
                + " to "
                + (now + timedelta(days=12)).strftime("%B %d, %Y")
                + "."
            ),
            created_at=now - timedelta(days=2),
        )
    )

    # --- Document 3: Medicaid/SNAP redetermination notice ---
    doc3 = Document(
        case_id=case.id,
        doc_type="medicaid_snap_notice",
        agency="Medicaid/SNAP",
        raw_text=(
            "Department of Health and Human Services\n"
            "SNAP/Medicaid Redetermination Notice\n"
            "Case Number: SNP-88213\n"
            "Your benefits will lapse if you do not submit your redetermination packet by "
            + (now + timedelta(days=20)).strftime("%B %d, %Y")
            + "."
        ),
        uploaded_at=now - timedelta(days=15),
        ocr_confidence=0.93,
    )
    db.add(doc3)
    db.flush()
    _add_entities(
        db,
        doc3.id,
        [
            {"entity_type": "case_number", "value": "SNP-88213", "confidence_score": 0.9},
            {"entity_type": "deadline", "value": (now + timedelta(days=20)).strftime("%Y-%m-%d"), "confidence_score": 0.88},
            {"entity_type": "agency", "value": "Medicaid/SNAP", "confidence_score": 0.97},
            {"entity_type": "required_action", "value": "Submit redetermination packet", "confidence_score": 0.85},
        ],
    )
    _add_urgency(
        db,
        doc3.id,
        score=62.0,
        breakdown={
            "days_until_deadline": 0.2,
            "doc_type_base_severity": 0.3,
            "consequence_keywords": 0.35,
            "notice_stage": 0.1,
        },
    )
    _add_explanation(
        db,
        doc3.id,
        "This is a redetermination notice for your SNAP/Medicaid case SNP-88213. "
        "Submit your renewal packet by "
        + (now + timedelta(days=20)).strftime("%B %d, %Y")
        + " or your benefits will lapse.",
        ["snap-redetermination-basics"],
    )
    db.add(
        TimelineEvent(
            case_id=case.id,
            document_id=doc3.id,
            event_type="new",
            description="Medicaid/SNAP redetermination notice uploaded.",
            created_at=now - timedelta(days=15),
        )
    )

    # --- Document 4: School enrollment notice ---
    doc4 = Document(
        case_id=case.id,
        doc_type="school_enrollment_notice",
        agency="School District",
        raw_text=(
            "Riverside Unified School District\n"
            "Enrollment Confirmation Required\n"
            "Student ID: RS-4471\n"
            "Please confirm enrollment documents by "
            + (now + timedelta(days=35)).strftime("%B %d, %Y")
            + " to secure your child's placement."
        ),
        uploaded_at=now - timedelta(days=8),
        ocr_confidence=0.95,
    )
    db.add(doc4)
    db.flush()
    _add_entities(
        db,
        doc4.id,
        [
            {"entity_type": "case_number", "value": "RS-4471", "confidence_score": 0.89},
            {"entity_type": "deadline", "value": (now + timedelta(days=35)).strftime("%Y-%m-%d"), "confidence_score": 0.86},
            {"entity_type": "agency", "value": "School District", "confidence_score": 0.95},
            {"entity_type": "required_action", "value": "Confirm enrollment documents", "confidence_score": 0.8},
        ],
    )
    _add_urgency(
        db,
        doc4.id,
        score=30.0,
        breakdown={
            "days_until_deadline": 0.1,
            "doc_type_base_severity": 0.2,
            "consequence_keywords": 0.1,
            "notice_stage": 0.05,
        },
    )
    _add_explanation(
        db,
        doc4.id,
        "Riverside Unified School District needs enrollment documents confirmed by "
        + (now + timedelta(days=35)).strftime("%B %d, %Y")
        + " for student RS-4471 to keep their school placement.",
        ["school-enrollment-basics"],
    )
    db.add(
        TimelineEvent(
            case_id=case.id,
            document_id=doc4.id,
            event_type="new",
            description="School enrollment notice uploaded.",
            created_at=now - timedelta(days=8),
        )
    )

    # --- Document 5: Housing authority notice (informational, no deadline) ---
    doc5 = Document(
        case_id=case.id,
        doc_type="housing_authority_notice",
        agency="Housing Authority",
        raw_text=(
            "Metro Housing Authority\n"
            "Informational Notice\n"
            "Voucher ID: HV-30291\n"
            "This letter confirms receipt of your annual recertification documents. No action is required at this time."
        ),
        uploaded_at=now - timedelta(days=4),
        ocr_confidence=0.6,
    )
    db.add(doc5)
    db.flush()
    _add_entities(
        db,
        doc5.id,
        [
            {"entity_type": "case_number", "value": "HV-30291", "confidence_score": 0.55, "flagged_for_review": True},
            {"entity_type": "agency", "value": "Housing Authority", "confidence_score": 0.7, "flagged_for_review": True},
            {"entity_type": "required_action", "value": "No action required", "confidence_score": 0.5, "flagged_for_review": True},
        ],
    )
    _add_urgency(
        db,
        doc5.id,
        score=5.0,
        breakdown={
            "days_until_deadline": 0.0,
            "doc_type_base_severity": 0.05,
            "consequence_keywords": 0.0,
            "notice_stage": 0.0,
        },
    )
    _add_explanation(
        db,
        doc5.id,
        "This is an informational notice from Metro Housing Authority confirming receipt of your documents. "
        "No action is needed. Some fields on this scan were low quality and are flagged for you to double-check.",
        ["housing-recert-basics"],
    )
    db.add(
        TimelineEvent(
            case_id=case.id,
            document_id=doc5.id,
            event_type="new",
            description="Housing authority informational notice uploaded (low OCR confidence, flagged for review).",
            created_at=now - timedelta(days=4),
        )
    )

    db.commit()


def run():
    db = SessionLocal()
    try:
        seed_demo_case(db)
    finally:
        db.close()


if __name__ == "__main__":
    run()

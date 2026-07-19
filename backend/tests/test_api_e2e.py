"""End-to-end test of the full pipeline through the HTTP API.

Requires build artifacts to be present:
    python -m app.ml.build_prototypes
    python -m app.ml.train_urgency_model
    python -m spacy download en_core_web_sm
(GROQ_API_KEY is optional — the pipeline degrades gracefully without an
explanation if the RAG call fails.)
"""

import importlib.util

import pytest
from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.main import app
from app.models import Case
from app.services.classification_service import PROTOTYPES_PATH
from app.services.urgency_service import MODEL_PATH

pytestmark = pytest.mark.skipif(
    not PROTOTYPES_PATH.exists()
    or not MODEL_PATH.exists()
    or importlib.util.find_spec("en_core_web_sm") is None,
    reason="ML build artifacts missing — see module docstring for setup steps",
)

SAMPLE_LETTER_TEXT = (
    "U.S. Citizenship and Immigration Services\n"
    "NOTICE OF ACTION - Form I-797C\n"
    "Case Number: MSC9999999999\n"
    "You are required to appear for a biometrics appointment on or before December 1, 2026. "
    "Failure to appear may result in denial of your application."
)


def _build_sample_pdf_bytes() -> bytes:
    import fitz

    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), SAMPLE_LETTER_TEXT)
    return doc.tobytes()


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def demo_case_id(client):
    db = SessionLocal()
    try:
        case = db.query(Case).filter(Case.display_name.like("Demo Case%")).first()
        assert case is not None, "demo case should be seeded on startup"
        return case.id
    finally:
        db.close()


def test_upload_document_returns_full_pipeline_result(client, demo_case_id):
    pdf_bytes = _build_sample_pdf_bytes()

    response = client.post(
        f"/cases/{demo_case_id}/documents",
        files={"file": ("letter.pdf", pdf_bytes, "application/pdf")},
    )

    assert response.status_code == 200
    body = response.json()

    assert body["doc_type"] == "uscis_notice"
    assert any(e["entity_type"] == "case_number" and e["value"] == "MSC9999999999" for e in body["entities"])
    assert body["urgency"] is not None
    assert 0 <= body["urgency"]["score"] <= 100


def test_timeline_reflects_newly_uploaded_document(client, demo_case_id):
    response = client.get(f"/cases/{demo_case_id}/timeline")
    assert response.status_code == 200
    body = response.json()

    assert body["case_id"] == demo_case_id
    assert len(body["documents"]) >= 1

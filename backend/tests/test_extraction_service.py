import importlib.util

import pytest

from app.services.extraction_service import ExtractionService

pytestmark = pytest.mark.skipif(
    importlib.util.find_spec("en_core_web_sm") is None,
    reason="spaCy model 'en_core_web_sm' not installed — run `python -m spacy download en_core_web_sm`",
)

SAMPLE_LETTERS = {
    "uscis_notice": (
        "U.S. Citizenship and Immigration Services\n"
        "NOTICE OF ACTION - Form I-797C\n"
        "Case Number: MSC2190012345\n"
        "You are required to appear for a biometrics appointment on or before March 15, 2026."
    ),
    "medicaid_snap_notice": (
        "Department of Health and Human Services\n"
        "SNAP/Medicaid Redetermination Notice\n"
        "Case Number: SNP-88213\n"
        "Please submit your redetermination packet by April 1, 2026."
    ),
}


@pytest.fixture(scope="module")
def service():
    return ExtractionService()


def test_uscis_letter_extracts_case_number_and_deadline(service):
    entities = service.extract(SAMPLE_LETTERS["uscis_notice"], "uscis_notice")
    entity_map = {e.entity_type: e.value for e in entities}

    assert entity_map.get("case_number") == "MSC2190012345"
    assert "deadline" in entity_map
    assert entity_map.get("agency") == "USCIS"


def test_medicaid_letter_extracts_case_number_and_deadline(service):
    entities = service.extract(SAMPLE_LETTERS["medicaid_snap_notice"], "medicaid_snap_notice")
    entity_map = {e.entity_type: e.value for e in entities}

    assert entity_map.get("case_number") == "SNP-88213"
    assert "deadline" in entity_map


def test_low_confidence_fields_are_flagged(service):
    # A letter with no recognizable required-action phrasing shouldn't produce
    # a false required_action entity.
    entities = service.extract("This is an unrelated informational note with no structure.", "uscis_notice")
    assert all(e.confidence_score > 0 for e in entities)

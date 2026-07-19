"""Requires classifier prototypes to be built first:
    python -m app.ml.build_prototypes
"""

import pytest

from app.services.classification_service import ClassificationService, PROTOTYPES_PATH

pytestmark = pytest.mark.skipif(
    not PROTOTYPES_PATH.exists(),
    reason="classifier prototypes not built — run `python -m app.ml.build_prototypes` first",
)

HELD_OUT_EXAMPLES = {
    "uscis_notice": "Notice from U.S. Citizenship and Immigration Services: your Form N-400 naturalization interview has been scheduled.",
    "medicaid_snap_notice": "Your household's Medicaid coverage is up for annual renewal; please return the enclosed verification forms.",
    "school_enrollment_notice": "The school district requires updated proof of address before your child's enrollment can be finalized.",
    "housing_authority_notice": "Your Section 8 housing voucher recertification paperwork has been received by the housing authority.",
}

OFF_TOPIC_TEXT = (
    "Congratulations! You've been selected to receive a free vacation cruise. "
    "Click here to claim your prize before it expires."
)


@pytest.fixture(scope="module")
def service():
    return ClassificationService()


@pytest.mark.parametrize("expected_type,text", list(HELD_OUT_EXAMPLES.items()))
def test_classifies_held_out_examples_correctly(service, expected_type, text):
    result = service.classify(text)
    assert result["doc_type"] == expected_type
    assert result["flagged_for_review"] is False


def test_off_topic_text_is_flagged_for_review(service):
    result = service.classify(OFF_TOPIC_TEXT)
    # An off-topic text shouldn't confidently match any of the 4 prototypes —
    # margin between top-1 and top-2 should be small enough to flag.
    assert result["flagged_for_review"] is True

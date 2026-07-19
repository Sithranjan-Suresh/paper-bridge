import pytest

from app.ml.urgency_features import FEATURE_NAMES
from app.services.urgency_service import UrgencyService, MODEL_PATH

pytestmark = pytest.mark.skipif(
    not MODEL_PATH.exists(),
    reason="urgency model not trained — run `python -m app.ml.train_urgency_model` first",
)


@pytest.fixture(scope="module")
def service():
    return UrgencyService()


def test_informational_document_scores_low(service):
    features = {
        "days_until_deadline": -1.0,  # no deadline present
        "doc_type_base_severity": 0.5,
        "consequence_keyword_score": 0.0,
        "notice_stage": 0.0,
    }
    result = service.score(features)
    assert result["score"] < 25


def test_overdue_high_severity_document_scores_high(service):
    features = {
        "days_until_deadline": 1.0,  # overdue
        "doc_type_base_severity": 0.8,
        "consequence_keyword_score": 1.0,
        "notice_stage": 1.0,
    }
    result = service.score(features)
    assert result["score"] > 70


def test_feature_breakdown_covers_all_features(service):
    features = {name: 0.5 for name in FEATURE_NAMES}
    result = service.score(features)
    assert set(result["feature_breakdown"].keys()) == set(FEATURE_NAMES)

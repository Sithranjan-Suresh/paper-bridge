"""Feature engineering for the urgency scoring model.

Produces a fixed-order feature vector consumed by both training
(train_urgency_model.py) and inference (UrgencyService).
"""

from datetime import date

from app.data.extraction_patterns import CONSEQUENCE_KEYWORDS, FINAL_NOTICE_KEYWORDS, FIRST_NOTICE_KEYWORDS

FEATURE_NAMES = [
    "days_until_deadline",
    "doc_type_base_severity",
    "consequence_keyword_score",
    "notice_stage",
]

# Base severity per document type, reflecting typical real-world stakes (0-1 scale).
DOC_TYPE_BASE_SEVERITY = {
    "uscis_notice": 0.8,
    "medicaid_snap_notice": 0.65,
    "housing_authority_notice": 0.5,
    "school_enrollment_notice": 0.35,
}

MAX_DAYS_HORIZON = 60  # deadlines further out than this are treated as equally "not urgent yet"


def _days_until_deadline_feature(deadline: date | None, reference: date) -> float:
    if deadline is None:
        return -1.0  # no deadline present -> informational, least urgent
    days = (deadline - reference).days
    if days < 0:
        return 1.0  # overdue -> maximally urgent
    clamped = max(0, min(days, MAX_DAYS_HORIZON))
    return 1.0 - (clamped / MAX_DAYS_HORIZON)


def _consequence_keyword_score(text: str) -> float:
    text_lower = text.lower()
    hits = sum(1 for kw in CONSEQUENCE_KEYWORDS if kw in text_lower)
    return min(hits / 3, 1.0)  # 3+ consequence keywords saturates the feature


def _notice_stage(text: str) -> float:
    text_lower = text.lower()
    if any(kw in text_lower for kw in FINAL_NOTICE_KEYWORDS):
        return 1.0
    if any(kw in text_lower for kw in FIRST_NOTICE_KEYWORDS):
        return 0.0
    return 0.5  # follow-up/unspecified


def build_features(
    doc_type: str,
    text: str,
    deadline: date | None,
    reference: date | None = None,
) -> dict[str, float]:
    reference = reference or date.today()
    return {
        "days_until_deadline": _days_until_deadline_feature(deadline, reference),
        "doc_type_base_severity": DOC_TYPE_BASE_SEVERITY.get(doc_type, 0.5),
        "consequence_keyword_score": _consequence_keyword_score(text),
        "notice_stage": _notice_stage(text),
    }


def features_to_vector(features: dict[str, float]) -> list[float]:
    return [features[name] for name in FEATURE_NAMES]

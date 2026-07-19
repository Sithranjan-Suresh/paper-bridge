"""Rule-augmented regex patterns for structured field extraction, per document type.

These patterns run alongside spaCy's pretrained NER to catch domain-specific
fields (case numbers, agency-specific phrasing) that a generic NER model won't
reliably surface on its own.
"""

import re

# Case-number formats per agency, ordered most-specific first.
CASE_NUMBER_PATTERNS: dict[str, list[re.Pattern]] = {
    "uscis_notice": [
        re.compile(r"\b[A-Z]{3}\d{10}\b"),  # e.g. MSC2190012345
        re.compile(r"\bCase Number:\s*([A-Z0-9\-]+)\b", re.IGNORECASE),
    ],
    "medicaid_snap_notice": [
        re.compile(r"\bSNP-\d+\b"),
        re.compile(r"\bCase (?:Number|#):\s*([A-Z0-9\-]+)\b", re.IGNORECASE),
    ],
    "school_enrollment_notice": [
        re.compile(r"\bRS-\d+\b"),
        re.compile(r"\bStudent ID:\s*([A-Z0-9\-]+)\b", re.IGNORECASE),
    ],
    "housing_authority_notice": [
        re.compile(r"\bHV-\d+\b"),
        re.compile(r"\bVoucher ID:\s*([A-Z0-9\-]+)\b", re.IGNORECASE),
    ],
}

AGENCY_KEYWORDS: dict[str, list[str]] = {
    "uscis_notice": ["USCIS", "U.S. Citizenship and Immigration Services", "Department of Homeland Security"],
    "medicaid_snap_notice": ["Medicaid", "SNAP", "Department of Health and Human Services", "Department of Social Services"],
    "school_enrollment_notice": ["School District", "Unified School District", "Office of Student Services"],
    "housing_authority_notice": ["Housing Authority", "Section 8", "Public Housing"],
}

REQUIRED_ACTION_PATTERNS: list[re.Pattern] = [
    re.compile(r"(?:required to|must|please)\s+([^.\n]+)", re.IGNORECASE),
    re.compile(r"(?:submit|complete|confirm|appear for|return)\s+([^.\n]+)", re.IGNORECASE),
]

CONSEQUENCE_KEYWORDS = [
    "denial", "denied", "termination", "terminate", "will lapse", "lapse",
    "failure to appear", "failure to respond", "adverse action", "ineligible",
]

FINAL_NOTICE_KEYWORDS = ["final notice", "last notice", "notice of intent to deny", "termination"]
FIRST_NOTICE_KEYWORDS = ["initial", "receipt notice", "welcome", "confirms receipt"]

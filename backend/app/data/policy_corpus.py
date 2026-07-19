"""Curated plain-language policy-explainer corpus used for RAG grounding.

Each passage has a stable citation id so generated explanations can cite
their source. Kept intentionally small and hand-curated so retrieval quality
is high and hallucination risk is low.
"""

POLICY_CORPUS: list[dict] = [
    {
        "id": "uscis-biometrics-101",
        "agency": "USCIS",
        "text": (
            "A USCIS biometrics appointment notice (Form I-797C) requires you to appear at an "
            "Application Support Center to have your fingerprints, photo, and signature taken. "
            "This step is required to continue processing most immigration applications. "
            "Missing the appointment without rescheduling can result in your case being denied "
            "for abandonment."
        ),
    },
    {
        "id": "uscis-rescheduling",
        "agency": "USCIS",
        "text": (
            "If USCIS sends a new appointment notice for the same case number, it replaces any "
            "earlier appointment notice. Only the most recent date and instructions apply — you "
            "do not need to attend an appointment listed on a superseded notice."
        ),
    },
    {
        "id": "uscis-rfe-101",
        "agency": "USCIS",
        "text": (
            "A Request for Evidence (RFE) means USCIS needs more documentation before deciding "
            "your case. You must respond by the deadline listed with exactly the evidence "
            "requested, or your application may be denied."
        ),
    },
    {
        "id": "uscis-notice-of-intent-to-deny",
        "agency": "USCIS",
        "text": (
            "A Notice of Intent to Deny is more serious than an RFE — USCIS is planning to deny "
            "your case unless you provide a compelling response by the deadline. This deadline is "
            "usually strict and cannot be extended."
        ),
    },
    {
        "id": "uscis-approval-101",
        "agency": "USCIS",
        "text": (
            "An approval notice (Form I-797) means USCIS has approved your petition or "
            "application. Keep this notice for your records; it may be required for future "
            "immigration or employment steps."
        ),
    },
    {
        "id": "snap-redetermination-basics",
        "agency": "Medicaid/SNAP",
        "text": (
            "SNAP and Medicaid benefits must be periodically redetermined to confirm you still "
            "qualify. If you do not submit the redetermination packet by the deadline, your "
            "benefits will stop even if you are still eligible — you would need to reapply from "
            "scratch."
        ),
    },
    {
        "id": "snap-adverse-action",
        "agency": "Medicaid/SNAP",
        "text": (
            "A Notice of Adverse Action means the agency plans to reduce or end your benefits. "
            "You usually have the right to request a hearing before the change takes effect if "
            "you act before the deadline listed."
        ),
    },
    {
        "id": "medicaid-renewal-basics",
        "agency": "Medicaid/SNAP",
        "text": (
            "Medicaid coverage must be renewed annually. Submitting your renewal late can create "
            "a gap in health coverage even if you are ultimately found eligible again."
        ),
    },
    {
        "id": "snap-income-verification",
        "agency": "Medicaid/SNAP",
        "text": (
            "If a SNAP notice asks for updated proof of income, provide recent pay stubs or an "
            "employer letter. Missing this deadline is one of the most common reasons benefits "
            "are cut off unnecessarily."
        ),
    },
    {
        "id": "school-enrollment-basics",
        "agency": "School District",
        "text": (
            "School enrollment confirmation secures your child's spot in their assigned school. "
            "Missing the confirmation deadline can result in the placement being given to another "
            "student on the waiting list."
        ),
    },
    {
        "id": "school-immunization-records",
        "agency": "School District",
        "text": (
            "Most school districts require up-to-date immunization records before a child can "
            "attend class. Provisional enrollment is sometimes allowed for a limited window while "
            "records are finalized."
        ),
    },
    {
        "id": "school-residency-proof",
        "agency": "School District",
        "text": (
            "Proof of residency (a utility bill or lease) is often required to confirm a child "
            "qualifies for their assigned school zone. Without it, enrollment may be delayed or "
            "reassigned."
        ),
    },
    {
        "id": "school-iep-meeting",
        "agency": "School District",
        "text": (
            "An Individualized Education Program (IEP) meeting is where the school and family "
            "agree on support services for a child with a disability. Attending is important "
            "because decisions made there shape the child's services for the school year."
        ),
    },
    {
        "id": "housing-recert-basics",
        "agency": "Housing Authority",
        "text": (
            "Housing Choice Voucher (Section 8) recipients must complete an annual recertification "
            "confirming household income and composition. Missing this can result in loss of "
            "voucher assistance."
        ),
    },
    {
        "id": "housing-inspection-notice",
        "agency": "Housing Authority",
        "text": (
            "Housing authorities periodically inspect subsidized units to confirm they meet "
            "habitability standards. Failing to allow a scheduled inspection can jeopardize "
            "continued assistance."
        ),
    },
    {
        "id": "housing-informational-notice",
        "agency": "Housing Authority",
        "text": (
            "Some housing authority letters are purely informational — confirming receipt of "
            "documents or providing an account update — and require no action from the "
            "household."
        ),
    },
    {
        "id": "housing-portability",
        "agency": "Housing Authority",
        "text": (
            "A portability request lets a voucher holder move their assistance to a different "
            "housing authority's jurisdiction. Processing can take time, so plan moves well "
            "ahead of any lease deadline."
        ),
    },
]

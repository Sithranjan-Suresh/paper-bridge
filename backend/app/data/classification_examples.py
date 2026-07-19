"""Labeled example texts used to build nearest-centroid classification prototypes.

Each document type has 8-12 short representative examples covering the range
of phrasing/structure the OCR pipeline is likely to produce for that type.
"""

CLASSIFICATION_EXAMPLES: dict[str, list[str]] = {
    "uscis_notice": [
        "U.S. Citizenship and Immigration Services Notice of Action Form I-797C. You are required to appear for a biometrics appointment.",
        "USCIS Case Number MSC2190012345. Your Form I-485 application is being processed. Please appear for your interview.",
        "Department of Homeland Security, U.S. Citizenship and Immigration Services. Receipt notice for Form I-130 petition.",
        "This notice confirms USCIS has received your application for naturalization. An appointment notice will follow.",
        "USCIS Notice of Intent to Deny. You must respond within 30 days with additional evidence for your immigration case.",
        "Request for Evidence (RFE) from USCIS regarding your pending Form I-765 Employment Authorization application.",
        "USCIS biometrics appointment rescheduled. Please appear at the Application Support Center on the date listed.",
        "Notice of Approval, USCIS Form I-797. Your petition has been approved. Please retain this notice for your records.",
        "USCIS is requesting additional documentation to continue processing your adjustment of status application.",
        "Your green card interview has been scheduled by USCIS. Bring the enclosed checklist of required documents.",
    ],
    "medicaid_snap_notice": [
        "Department of Health and Human Services SNAP/Medicaid Redetermination Notice. Submit your renewal packet by the deadline.",
        "Your Medicaid coverage will be reviewed. Please complete and return the enclosed eligibility redetermination form.",
        "SNAP benefits notice: your case is due for recertification. Failure to respond will result in termination of benefits.",
        "This notice informs you that your Medicaid case number has been assigned a new redetermination deadline.",
        "State Department of Social Services: your food assistance (SNAP) benefits will lapse without submission of income verification.",
        "Notice of Adverse Action: your Medicaid benefits may be reduced unless you submit requested documents.",
        "Your household's SNAP eligibility must be recertified. Please schedule your interview with your caseworker.",
        "Medicaid renewal reminder: submit your annual renewal application to avoid a gap in health coverage.",
        "This letter confirms your SNAP application was received and is under review by the eligibility office.",
        "Your EBT/SNAP case requires updated proof of income within the stated timeframe to continue benefits.",
        "It is time to renew your Medicaid coverage for the upcoming year. Return the completed verification packet by the due date.",
        "Please complete and mail back the enclosed forms to keep your family's Medicaid coverage active without a gap.",
    ],
    "school_enrollment_notice": [
        "Riverside Unified School District Enrollment Confirmation Required. Please confirm enrollment documents for your child.",
        "This letter is to notify you that your child's school enrollment packet is incomplete and must be finished by the deadline.",
        "School District Office of Student Services: registration documents are needed to secure your student's placement.",
        "Your child has been assigned to a school for the upcoming year. Please complete the enrollment confirmation form.",
        "Notice from the school district regarding required immunization records for continued enrollment.",
        "Please submit proof of residency to the school district office to finalize your child's class placement.",
        "This is a reminder that your student's enrollment verification is due before the start of the semester.",
        "School registrar notice: transcripts and prior school records are required to complete enrollment.",
        "Your child's Individualized Education Program (IEP) meeting has been scheduled by the school district.",
        "District enrollment office: please update your child's emergency contact and residency information.",
    ],
    "housing_authority_notice": [
        "Metro Housing Authority Informational Notice. This letter confirms receipt of your annual recertification documents.",
        "Your Housing Choice Voucher (Section 8) annual recertification is due. Please submit income documentation.",
        "Notice from the Public Housing Authority regarding a scheduled inspection of your unit.",
        "This letter informs you that your housing voucher payment standard has been updated for the coming year.",
        "Housing Authority eligibility review: please provide updated household composition and income information.",
        "Your application for public housing assistance has been placed on the waiting list.",
        "Notice of lease renewal terms from your local housing authority for your subsidized unit.",
        "This letter confirms your Housing Assistance Payment (HAP) contract has been processed.",
        "Housing Authority annual inspection notice: an inspector will visit your unit on the scheduled date.",
        "Your portability request to transfer your voucher to another housing authority has been received.",
    ],
}

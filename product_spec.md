# PaperBridge — Product Specification

## Product Requirements (must be true at submission)
1. A user can upload a document (image or PDF) of one of the 4 supported types and receive: document classification, extracted entities, an urgency score with explanation, and a grounded plain-language summary.
2. A user can view a Case Timeline showing all documents uploaded for a given family/case, sorted by urgency.
3. Uploading a new document that relates to an existing one in the timeline triggers a visible conflict/update flag when deadlines or required actions change.
4. Low-confidence extracted fields are visibly flagged as uncertain rather than presented as fact.
5. A literacy-level toggle changes the complexity of the generated explanation without re-uploading.
6. A pre-seeded demo case is available with zero setup, so judges can experience the full flow without uploading their own documents.
7. A public landing page communicates the problem, the product, and the differentiator (case memory vs. document explainer) at a professional visual standard.
8. The full app is deployed and reachable via a live public URL at submission time.

## User Stories & Acceptance Criteria

**US-1:** As a family member, I want to upload a letter and immediately understand what it means, so that I don't have to guess at consequences.
- AC: Upload completes in under ~15 seconds for a standard letter.
- AC: Output includes deadline (if present), required action, urgency score, and plain-language explanation.

**US-2:** As a family member, I want to see all my letters in one place, sorted by what's most urgent, so that I know what to deal with first.
- AC: Case Timeline displays all uploaded documents for the active case, sorted descending by urgency.
- AC: Each timeline entry shows document type, agency, and deadline at a glance.

**US-3:** As a family member, I want to be warned if a new letter changes something I already knew, so that I don't act on outdated information.
- AC: When a new document's extracted deadline/case-number relates to an existing timeline entry, a visible banner explains what changed.
- AC: The prior (now-superseded) information remains visible but is clearly marked as outdated.

**US-4:** As a family member, I want to know when the system isn't sure about something, so that I don't rely on a wrong answer for something important.
- AC: Any extracted field below a defined confidence threshold is visually flagged (e.g., "please verify").
- AC: Confidence flags never silently disappear — they persist until acknowledged.

**US-5:** As a family member with limited English proficiency, I want the explanation to match my reading level, so that I actually understand it.
- AC: Toggling literacy level regenerates the explanation without needing to re-upload the document.

**US-6:** As a judge, I want to experience the full product without setup, so that I can evaluate it within the demo window.
- AC: A "View Demo Case" entry point loads a pre-seeded, fully populated case with zero login/setup.

## Edge Cases
- Blurry/low-quality scan → OCR confidence low → entire document flagged for manual review rather than partial silent extraction.
- Document type doesn't match any of the 4 supported categories → system says so explicitly rather than forcing a bad classification.
- Two documents reference different, unrelated cases for the same uploaded family → system should not incorrectly merge timelines (match on case number/name, not just agency).
- No deadline present in a document (e.g., informational letter only) → urgency score reflects "informational" tier rather than a false urgency score.

## Feature Priority

**P0 (demo-blocking):**
- Upload → classification → extraction → urgency score → grounded explanation (single-document flow)
- Case Timeline view with pre-seeded demo case
- Conflict/update detection on new upload (the core differentiator)
- Confidence flagging
- Deployed, publicly reachable app

**P1 (strongly wanted):**
- Literacy-level toggle
- Explainability breakdown visualization for urgency score
- Landing page at premium visual polish

**P2 (nice to have, cut first if behind schedule):**
- Additional document types beyond the initial 4
- Anomaly/scam-letter detection
- Multi-family/caseworker view

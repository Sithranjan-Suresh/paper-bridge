# PaperBridge — Engineering Specification

Design only — no code. Every component below is free/open-source or free-tier, per project constraint.

## Overall Architecture

```
[Frontend: React + Tailwind]
        |
        v  (REST)
[Backend: FastAPI]
        |
        +--> Ingestion Service (OCR + layout parsing: Tesseract / PyMuPDF)
        |
        +--> Classification Service (sentence-transformers embeddings, local,
        |      nearest-centroid classifier over 4 document-type prototypes)
        |
        +--> Extraction Service (spaCy pretrained NER + rule-augmented
        |      patterns for dates, case numbers, agency names, required actions)
        |
        +--> Urgency Scoring Service (scikit-learn gradient-boosted / logistic
        |      model on engineered features; returns score + feature importances)
        |
        +--> RAG Explanation Service
        |      - retrieval: FAISS / in-memory cosine similarity over a curated
        |        plain-language policy-explainer corpus (local embeddings)
        |      - generation: Groq API call (free tier), prompted to explain
        |        using ONLY the retrieved passages, with citation
        |
        +--> Case Memory Service (entity resolution across documents for the
        |      same family/case; timeline construction; conflict/supersession
        |      detection by comparing new extracted fields against existing
        |      timeline entries for the same case)
        |
        +--> Confidence Service (combines OCR confidence + extraction-model
               confidence into a per-field confidence score; flags below threshold)
        |
        v
[SQLite: cases, documents, entities, timeline_events]
```

## Data Model

**Family/Case**
- id, display_name, created_at

**Document**
- id, case_id (FK), doc_type, agency, raw_text, uploaded_at, ocr_confidence

**ExtractedEntity**
- id, document_id (FK), entity_type (deadline / case_number / required_action / agency), value, confidence_score, flagged_for_review (bool)

**UrgencyScore**
- id, document_id (FK), score (0-100), feature_breakdown (JSON: feature name → weight/contribution)

**TimelineEvent**
- id, case_id (FK), document_id (FK), event_type (new / supersedes / conflicts_with), related_document_id (nullable FK), description

**ExplanationRecord**
- id, document_id (FK), literacy_level, generated_text, source_citations (JSON list of corpus passage IDs)

## API Design

- `POST /cases` — create a case (demo mode: pre-seeded case created at startup)
- `GET /cases/{case_id}/timeline` — returns all documents + timeline events for a case, sorted by urgency
- `POST /cases/{case_id}/documents` — upload a document (multipart file); triggers full pipeline synchronously (ingestion → classification → extraction → urgency → RAG explanation → case-memory conflict check → confidence flagging); returns full result object
- `GET /documents/{document_id}` — full detail: extracted entities, urgency breakdown, explanation, citations, confidence flags
- `GET /documents/{document_id}/explanation?literacy_level=simple|standard|detailed` — regenerate explanation at a given literacy level (uses cached retrieval, only re-runs generation)
- Auth: none required for demo (single shared demo case); if multi-case support is added later, a simple case-access token is sufficient — no full user auth system needed for submission

## Frontend Architecture

- **Routes:** `/` (landing page), `/case/:caseId` (Case Timeline), `/document/:documentId` (Document Detail)
- **Key components:** `TimelineList`, `TimelineEntry`, `ConflictBanner`, `UploadDropzone`, `ExtractionPanel`, `UrgencyBreakdown` (feature-importance bars), `ExplanationPanel` (with citation chips), `ConfidenceFlag`, `LiteracyToggle`
- **State management:** React Query (or simple fetch + local state) for server data; no global state library needed given the app's scope — avoid over-engineering here, time is better spent on visual polish

## Backend Architecture / Key Algorithms

- **Classification:** embed incoming document text; compute cosine similarity to 4 pre-computed prototype embeddings (one per document type, built from a handful of labeled examples per type); assign nearest type, low-margin cases flagged.
- **Urgency scoring features:** days-until-deadline, document-type base severity weight, presence of consequence-severity keywords (e.g., "denial," "termination," "will lapse") via a small keyword/classifier signal, whether the document is a first notice vs. a follow-up/final notice.
- **Conflict detection:** for each new document, look up existing timeline entries sharing the same case_id and same agency (or same case_number if extracted); compare deadline/required-action fields; if they differ, create a `TimelineEvent` of type `conflicts_with` or `supersedes` and surface it in the API response for the frontend banner.
- **RAG grounding:** retrieval limited to a small curated corpus (built ahead of time — plain-language explanations of common notice types per agency); generation prompt explicitly instructs the model to answer only from retrieved passages and to decline elaboration beyond them, reducing hallucination risk.

## External Integrations
- **Groq API** (free tier) — explanation generation only
- **sentence-transformers** — local model, no external call
- **spaCy** — local model, no external call
- **scikit-learn** — local, trained offline, loaded as a serialized model file

## Deployment Strategy
- Frontend: Vercel (free tier), connected to repo for auto-deploy
- Backend: Render or Fly.io (free tier); serialized models (spaCy, sentence-transformer, urgency model) bundled with the deployment image or downloaded at build time
- Database: SQLite file, seeded with the demo case on container start
- "Submitted and running" means: a public URL loads the landing page, a "View Demo Case" link loads a fully populated timeline with zero setup, and live upload of a new document (from the 4 supported types) works end-to-end against the deployed backend

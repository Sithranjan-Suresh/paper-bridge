# PaperBridge — Full Project Context

## Vision
**One sentence:** PaperBridge is the case memory immigrant and refugee families don't have — tracking government correspondence across agencies and time so no deadline gets missed.

**One paragraph:** Immigrant and refugee families don't receive one confusing letter — they receive a stream of them, from agencies that don't talk to each other (USCIS, Medicaid/SNAP, school districts, housing authorities), over weeks and months. No institution tracks the whole picture for them, so deadlines get missed not because any single letter was confusing, but because nobody connected letter #4 to letter #1. PaperBridge reads each letter with a real extraction and classification pipeline, scores its urgency with an explainable model, grounds its explanation in actual policy guidance, and — critically — remembers every prior letter for that family, flagging the moment a new one changes or conflicts with something already on record.

## Problem
- Families managing an active case with 2+ government agencies simultaneously receive correspondence asynchronously, with no shared record across agencies.
- Missed deadlines in this space have serious consequences: lapsed benefits, denied applications, missed enrollment windows.
- Existing "document explainer" tools treat every letter as an isolated event — the actual failure point is the *relationship* between letters over time, which nothing currently tracks.

## Target Users
Immigrant and refugee families actively managing correspondence from 2+ of: USCIS, Medicaid/SNAP, school enrollment, housing authority. Today they track this with loose paper piles, memory, or nothing at all. It's painful because the stakes (benefits, legal status, school access) are high and the coordination burden falls entirely on the family.

## User Journey (end-to-end)
1. Family receives a letter, photographs or scans it, uploads to PaperBridge.
2. System classifies document type/agency, extracts entities (deadline, case number, required action), scores urgency with a visible explanation, and generates a grounded plain-language summary.
3. The letter is added to the family's Case Timeline. If it relates to or conflicts with a prior letter, the system flags the relationship explicitly (e.g., a superseded deadline).
4. Family sees one prioritized, urgency-sorted view across every agency they're dealing with, and acts on the most urgent item first.
5. Low-confidence extractions are flagged for the family (or a caseworker) to double-check rather than silently trusted.

## Core Features (at submission)
- Document ingestion (OCR + layout parsing) for 4 document types: USCIS notice, Medicaid/SNAP, school enrollment, housing authority
- Embedding-based document-type classification
- Custom NER extraction (deadlines, case number, agency, required action)
- Explainable urgency scorer (classical ML, feature-importance breakdown shown to user)
- RAG-grounded explanation generation, with source citation
- Cross-document case memory: entity resolution + timeline + conflict/supersession detection
- Confidence flagging on low-certainty extractions
- Literacy-level toggle on explanations
- Premium marketing landing page + pre-seeded demo case for frictionless judging

## Key Differentiators
- **Case memory, not document memory** — the only submission in its category likely to reason across multiple documents rather than treating each upload as isolated.
- **Real, explainable ML** — a genuine classical-ML urgency model and NER pipeline, not a single LLM prompt doing everything.
- **Grounded, cited explanations** — reduces hallucination risk in a domain where a wrong answer has real consequences.
- **Responsible-AI framing** — confidence flagging is both a technical-depth signal and an appropriate design choice for a high-stakes domain.
- **Zero-cost infrastructure** — the entire pipeline runs on free-tier/open-source components, meaning it could genuinely scale to the population it's meant to serve without a funding dependency.

## Technical Overview
- **LLM inference:** Groq API (free tier) — used only for grounded explanation generation, not for extraction/classification/scoring (those are real ML components, see below)
- **Embeddings:** sentence-transformers (local, open-source, e.g. all-MiniLM-L6-v2) — no API cost
- **Vector retrieval:** FAISS or in-memory cosine similarity over a small curated policy-explainer corpus
- **NER/extraction:** spaCy pretrained + rule-augmented patterns for structured fields (dates, case numbers, agency names)
- **Urgency scoring:** scikit-learn gradient-boosted or logistic model on engineered features, trained on a small labeled synthetic set
- **OCR:** Tesseract / PyMuPDF (born-digital PDFs) — free, local
- **Backend:** FastAPI (Python)
- **Frontend:** React + Tailwind
- **Persistence:** SQLite (file-based, free)
- **Deployment:** frontend on Vercel free tier, backend on Render or Fly.io free tier

## Demo Flow
See demo script (Phase 4) — landing page → pre-seeded Case Timeline → open a letter (extraction/urgency/grounded explanation) → live upload → conflict-detection wow moment → confidence flag → literacy toggle → timeline updates.

## Success Metrics
- **Technical:** end-to-end pipeline works reliably across all 4 document types; conflict detection correctly fires on the scripted demo case; total processing latency low enough for a live demo (no long waits on stage).
- **Product:** a judge can complete the full demo journey unassisted in under 2 minutes without confusion; submission includes a live deployed link, demo video, and complete Devpost writeup mapped to every rubric section.

## Future Expansion
- SMS/WhatsApp deadline reminders for families without reliable app access
- Voice interface for lower-literacy or lower-tech-access users
- Caseworker/nonprofit-facing dashboard for managing multiple families' cases at once
- Community-contributed corpus to expand document-type and agency coverage beyond the initial 4

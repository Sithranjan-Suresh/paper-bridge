from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.database import Base


class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    display_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    documents = relationship("Document", back_populates="case", cascade="all, delete-orphan")
    timeline_events = relationship("TimelineEvent", back_populates="case", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    doc_type = Column(String, nullable=False)
    agency = Column(String, nullable=True)
    raw_text = Column(Text, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    ocr_confidence = Column(Float, nullable=True)

    case = relationship("Case", back_populates="documents")
    entities = relationship("ExtractedEntity", back_populates="document", cascade="all, delete-orphan")
    urgency_score = relationship("UrgencyScore", back_populates="document", uselist=False, cascade="all, delete-orphan")
    explanations = relationship("ExplanationRecord", back_populates="document", cascade="all, delete-orphan")


class ExtractedEntity(Base):
    __tablename__ = "extracted_entities"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    entity_type = Column(String, nullable=False)  # deadline / case_number / required_action / agency
    value = Column(String, nullable=True)
    confidence_score = Column(Float, nullable=False)
    flagged_for_review = Column(Boolean, default=False)

    document = relationship("Document", back_populates="entities")


class UrgencyScore(Base):
    __tablename__ = "urgency_scores"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    score = Column(Float, nullable=False)  # 0-100
    feature_breakdown = Column(Text, nullable=True)  # JSON string: feature name -> weight/contribution

    document = relationship("Document", back_populates="urgency_score")


class TimelineEvent(Base):
    __tablename__ = "timeline_events"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    event_type = Column(String, nullable=False)  # new / supersedes / conflicts_with
    related_document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    case = relationship("Case", back_populates="timeline_events")


class ExplanationRecord(Base):
    __tablename__ = "explanation_records"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    literacy_level = Column(String, nullable=False)  # simple / standard / detailed
    generated_text = Column(Text, nullable=False)
    source_citations = Column(Text, nullable=True)  # JSON list of corpus passage IDs

    document = relationship("Document", back_populates="explanations")

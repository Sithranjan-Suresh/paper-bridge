from sqlalchemy.orm import Session

from app.models import Document, ExtractedEntity, TimelineEvent


def _entity_map(db: Session, document_id: int) -> dict[str, str]:
    entities = db.query(ExtractedEntity).filter(ExtractedEntity.document_id == document_id).all()
    return {e.entity_type: e.value for e in entities}


class CaseMemoryService:
    """Resolves a new document against a case's existing timeline and detects
    conflicts/supersession by comparing deadline and required-action fields
    across documents that share the same case number (or, failing that, the
    same agency) within a case.
    """

    def find_related_documents(self, db: Session, case_id: int, new_document: Document) -> list[Document]:
        new_entities = _entity_map(db, new_document.id)
        new_case_number = new_entities.get("case_number")

        candidates = (
            db.query(Document)
            .filter(Document.case_id == case_id, Document.id != new_document.id)
            .all()
        )

        related = []
        for doc in candidates:
            doc_entities = _entity_map(db, doc.id)
            same_case_number = new_case_number and doc_entities.get("case_number") == new_case_number
            same_agency_only = not new_case_number and doc.agency == new_document.agency
            if same_case_number or same_agency_only:
                related.append(doc)
        return related

    def check_conflict(self, db: Session, case_id: int, new_document: Document) -> list[TimelineEvent]:
        """Compares the new document's entities against related documents already
        on the case timeline. Returns newly created TimelineEvent rows (not yet committed)."""
        related_docs = self.find_related_documents(db, case_id, new_document)
        if not related_docs:
            return []

        new_entities = _entity_map(db, new_document.id)
        new_deadline = new_entities.get("deadline")
        new_action = new_entities.get("required_action")

        created_events: list[TimelineEvent] = []
        for related_doc in related_docs:
            # Only compare against a document uploaded before the new one.
            if related_doc.uploaded_at >= new_document.uploaded_at:
                continue

            related_entities = _entity_map(db, related_doc.id)
            related_deadline = related_entities.get("deadline")
            related_action = related_entities.get("required_action")

            deadline_changed = new_deadline and related_deadline and new_deadline != related_deadline
            action_changed = new_action and related_action and new_action != related_action

            if deadline_changed or action_changed:
                description_parts = []
                if deadline_changed:
                    description_parts.append(f"deadline changed from {related_deadline} to {new_deadline}")
                if action_changed:
                    description_parts.append(f"required action changed from '{related_action}' to '{new_action}'")

                event = TimelineEvent(
                    case_id=case_id,
                    document_id=new_document.id,
                    event_type="supersedes",
                    related_document_id=related_doc.id,
                    description=(
                        f"This notice supersedes an earlier document (case {new_entities.get('case_number', 'n/a')}): "
                        + "; ".join(description_parts)
                        + "."
                    ),
                )
                db.add(event)
                created_events.append(event)

        return created_events


_case_memory_service = CaseMemoryService()


def get_case_memory_service() -> CaseMemoryService:
    return _case_memory_service

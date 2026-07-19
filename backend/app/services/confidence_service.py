FIELD_CONFIDENCE_THRESHOLD = 0.6
DOCUMENT_OCR_THRESHOLD = 0.65  # below this, skip partial extraction entirely


class ConfidenceService:
    def combine(self, ocr_confidence: float, extraction_confidence: float) -> float:
        """Combines OCR confidence and extraction-model confidence into a single
        per-field confidence score. Weighted toward extraction confidence since
        OCR errors on a well-extracted field are usually already reflected there,
        but a poor scan still caps the ceiling."""
        return round(min(ocr_confidence, 1.0) * 0.4 + min(extraction_confidence, 1.0) * 0.6, 3)

    def should_flag_field(self, combined_confidence: float) -> bool:
        return combined_confidence < FIELD_CONFIDENCE_THRESHOLD

    def apply_field_confidence(self, ocr_confidence: float, entities: list) -> list:
        """Mutates each entity's confidence_score to the combined score and sets
        flagged_for_review accordingly. Works on ORM ExtractedEntity instances or
        the ExtractionService.Entity dataclass — both expose confidence_score /
        flagged_for_review attributes."""
        for entity in entities:
            combined = self.combine(ocr_confidence, entity.confidence_score)
            entity.confidence_score = combined
            entity.flagged_for_review = self.should_flag_field(combined)
        return entities

    def should_flag_entire_document(self, ocr_confidence: float) -> bool:
        """If the scan quality itself is too low, the whole document should be
        flagged for manual review rather than silently trusting partial
        extraction (product_spec.md Edge Case: blurry/low-quality scan)."""
        return ocr_confidence < DOCUMENT_OCR_THRESHOLD


_confidence_service = ConfidenceService()


def get_confidence_service() -> ConfidenceService:
    return _confidence_service

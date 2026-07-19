import io


class IngestionService:
    """Extracts raw text (and a confidence signal) from an uploaded file.

    Born-digital PDFs are parsed directly with PyMuPDF (high confidence, no OCR
    needed). Everything else (images, scanned PDFs with no text layer) goes
    through Tesseract OCR, whose confidence score becomes the document's
    ocr_confidence.
    """

    def process(self, filename: str, file_bytes: bytes) -> dict:
        if filename.lower().endswith(".pdf"):
            text, confidence = self._process_pdf(file_bytes)
        else:
            text, confidence = self._process_image(file_bytes)

        return {"raw_text": text, "ocr_confidence": confidence}

    def _process_pdf(self, file_bytes: bytes) -> tuple[str, float]:
        import fitz  # PyMuPDF

        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text_parts = [page.get_text() for page in doc]
        text = "\n".join(text_parts).strip()

        if text:
            # Born-digital PDF with an extractable text layer.
            return text, 0.98

        # No text layer (scanned PDF) — rasterize pages and OCR them.
        ocr_texts = []
        confidences = []
        for page in doc:
            pix = page.get_pixmap(dpi=200)
            image_bytes = pix.tobytes("png")
            page_text, page_confidence = self._ocr_image_bytes(image_bytes)
            ocr_texts.append(page_text)
            confidences.append(page_confidence)

        combined_text = "\n".join(ocr_texts).strip()
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        return combined_text, avg_confidence

    def _process_image(self, file_bytes: bytes) -> tuple[str, float]:
        return self._ocr_image_bytes(file_bytes)

    def _ocr_image_bytes(self, image_bytes: bytes) -> tuple[str, float]:
        import pytesseract
        from PIL import Image

        image = Image.open(io.BytesIO(image_bytes))
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

        words = [w for w in data["text"] if w.strip()]
        confidences = [int(c) for c, w in zip(data["conf"], data["text"]) if w.strip() and int(c) >= 0]

        text = " ".join(words)
        avg_confidence = (sum(confidences) / len(confidences) / 100.0) if confidences else 0.0
        return text, avg_confidence


_ingestion_service = IngestionService()


def get_ingestion_service() -> IngestionService:
    return _ingestion_service

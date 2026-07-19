import pickle
from functools import lru_cache
from pathlib import Path

import numpy as np

PROTOTYPES_PATH = Path(__file__).parent.parent / "ml" / "artifacts" / "classifier_prototypes.pkl"
LOW_MARGIN_THRESHOLD = 0.08  # gap between top-1 and top-2 similarity below which we flag for review


class ClassificationService:
    def __init__(self, prototypes_path: Path = PROTOTYPES_PATH):
        self._prototypes_path = prototypes_path
        self._model = None
        self._prototypes: dict[str, np.ndarray] | None = None

    def _load(self):
        if self._prototypes is None:
            with open(self._prototypes_path, "rb") as f:
                self._prototypes = pickle.load(f)
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer("all-MiniLM-L6-v2")

    def classify(self, text: str) -> dict:
        """Returns {doc_type, confidence, margin, flagged_for_review}."""
        self._load()

        embedding = self._model.encode([text], normalize_embeddings=True)[0]

        similarities = {
            doc_type: float(np.dot(embedding, centroid))
            for doc_type, centroid in self._prototypes.items()
        }
        ranked = sorted(similarities.items(), key=lambda kv: kv[1], reverse=True)

        top_type, top_score = ranked[0]
        second_score = ranked[1][1] if len(ranked) > 1 else 0.0
        margin = top_score - second_score

        return {
            "doc_type": top_type,
            "confidence": top_score,
            "margin": margin,
            "flagged_for_review": margin < LOW_MARGIN_THRESHOLD,
            "all_scores": similarities,
        }


@lru_cache(maxsize=1)
def get_classification_service() -> ClassificationService:
    return ClassificationService()

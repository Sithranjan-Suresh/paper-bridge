import pickle
from functools import lru_cache
from pathlib import Path

from app.ml.urgency_features import FEATURE_NAMES, features_to_vector

MODEL_PATH = Path(__file__).parent.parent / "ml" / "artifacts" / "urgency_model.pkl"


class UrgencyService:
    def __init__(self, model_path: Path = MODEL_PATH):
        self._model_path = model_path
        self._model = None

    def _load(self):
        if self._model is None:
            with open(self._model_path, "rb") as f:
                self._model = pickle.load(f)

    def score(self, features: dict[str, float]) -> dict:
        """Returns {score, feature_breakdown} where feature_breakdown maps
        feature name -> estimated contribution to the final score."""
        self._load()

        vector = features_to_vector(features)
        predicted = float(self._model.predict([vector])[0])
        predicted = max(0.0, min(100.0, predicted))

        importances = self._model.feature_importances_
        raw_contributions = {
            name: importances[i] * vector[i] for i, name in enumerate(FEATURE_NAMES)
        }
        total_raw = sum(abs(v) for v in raw_contributions.values()) or 1.0
        # Scale raw contributions so they sum (in magnitude) proportionally to the
        # predicted score, giving an intuitive per-feature breakdown for the UI.
        feature_breakdown = {
            name: round((value / total_raw) * predicted, 2) for name, value in raw_contributions.items()
        }

        return {"score": round(predicted, 1), "feature_breakdown": feature_breakdown}


@lru_cache(maxsize=1)
def get_urgency_service() -> UrgencyService:
    return UrgencyService()

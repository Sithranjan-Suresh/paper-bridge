"""Trains the urgency scoring model on a small synthetic labeled dataset.

The synthetic labels follow a hand-designed scoring rubric that encodes domain
judgment (deadline proximity matters most, then document severity, then
consequence language, then notice stage). The gradient-boosted model is
trained to approximate this rubric so that inference produces smooth,
explainable feature-importance breakdowns rather than hard-coded rules.

Run:
    python -m app.ml.train_urgency_model
"""

import pickle
import random
from pathlib import Path

import numpy as np
from sklearn.ensemble import GradientBoostingRegressor

from app.ml.urgency_features import FEATURE_NAMES

MODEL_PATH = Path(__file__).parent / "artifacts" / "urgency_model.pkl"

# Rubric weights used to label synthetic training examples (0-100 scale).
RUBRIC_WEIGHTS = {
    "days_until_deadline": 45,
    "doc_type_base_severity": 25,
    "consequence_keyword_score": 20,
    "notice_stage": 10,
}


def _label(features: dict[str, float]) -> float:
    score = sum(features[name] * RUBRIC_WEIGHTS[name] for name in FEATURE_NAMES)
    # informational documents (days_until_deadline == -1) get pulled toward the floor
    if features["days_until_deadline"] < 0 and features["consequence_keyword_score"] == 0:
        score = min(score, 15)
    return max(0.0, min(100.0, score))


def generate_synthetic_dataset(n: int = 500, seed: int = 42) -> tuple[np.ndarray, np.ndarray]:
    rng = random.Random(seed)
    X, y = [], []

    for _ in range(n):
        features = {
            "days_until_deadline": rng.choice([rng.uniform(-1, 1), -1.0]),
            "doc_type_base_severity": rng.choice([0.35, 0.5, 0.65, 0.8]),
            "consequence_keyword_score": rng.choice([0.0, 0.33, 0.66, 1.0]),
            "notice_stage": rng.choice([0.0, 0.5, 1.0]),
        }
        X.append([features[name] for name in FEATURE_NAMES])
        y.append(_label(features))

    return np.array(X), np.array(y)


def train():
    X, y = generate_synthetic_dataset()
    model = GradientBoostingRegressor(n_estimators=150, max_depth=3, learning_rate=0.1, random_state=42)
    model.fit(X, y)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)

    print(f"Trained urgency model on {len(X)} synthetic examples. Saved to {MODEL_PATH}")
    print("Feature importances:", dict(zip(FEATURE_NAMES, model.feature_importances_)))


if __name__ == "__main__":
    train()

"""Builds nearest-centroid classification prototypes from labeled examples.

Run manually (or as part of the build step) whenever CLASSIFICATION_EXAMPLES changes:
    python -m app.ml.build_prototypes
"""

import pickle
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

from app.data.classification_examples import CLASSIFICATION_EXAMPLES

MODEL_NAME = "all-MiniLM-L6-v2"
OUTPUT_PATH = Path(__file__).parent / "artifacts" / "classifier_prototypes.pkl"


def build_prototypes() -> dict[str, np.ndarray]:
    model = SentenceTransformer(MODEL_NAME)
    prototypes: dict[str, np.ndarray] = {}

    for doc_type, examples in CLASSIFICATION_EXAMPLES.items():
        embeddings = model.encode(examples, normalize_embeddings=True)
        centroid = np.mean(embeddings, axis=0)
        centroid = centroid / np.linalg.norm(centroid)
        prototypes[doc_type] = centroid

    return prototypes


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    prototypes = build_prototypes()
    with open(OUTPUT_PATH, "wb") as f:
        pickle.dump(prototypes, f)
    print(f"Saved {len(prototypes)} prototypes to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

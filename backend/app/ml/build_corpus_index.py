"""Embeds the policy corpus and builds a FAISS index for retrieval.

Run manually (or as part of the build step) whenever POLICY_CORPUS changes:
    python -m app.ml.build_corpus_index
"""

import pickle
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from app.data.policy_corpus import POLICY_CORPUS

MODEL_NAME = "all-MiniLM-L6-v2"
INDEX_PATH = Path(__file__).parent / "artifacts" / "corpus.faiss"
METADATA_PATH = Path(__file__).parent / "artifacts" / "corpus_metadata.pkl"


def build_index():
    model = SentenceTransformer(MODEL_NAME)
    texts = [passage["text"] for passage in POLICY_CORPUS]
    embeddings = model.encode(texts, normalize_embeddings=True)
    embeddings = np.array(embeddings, dtype="float32")

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  # inner product on normalized vectors == cosine similarity
    index.add(embeddings)

    return index, POLICY_CORPUS


def main():
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    index, metadata = build_index()

    faiss.write_index(index, str(INDEX_PATH))
    with open(METADATA_PATH, "wb") as f:
        pickle.dump(metadata, f)

    print(f"Indexed {len(metadata)} corpus passages to {INDEX_PATH}")


if __name__ == "__main__":
    main()

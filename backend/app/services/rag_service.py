import os
import pickle
from functools import lru_cache
from pathlib import Path

import numpy as np

INDEX_PATH = Path(__file__).parent.parent / "ml" / "artifacts" / "corpus.faiss"
METADATA_PATH = Path(__file__).parent.parent / "ml" / "artifacts" / "corpus_metadata.pkl"

LITERACY_INSTRUCTIONS = {
    "simple": "Use very short sentences and simple everyday words. Aim for a 5th-grade reading level.",
    "standard": "Use clear, plain language suitable for a general adult audience.",
    "detailed": "Provide a more thorough explanation, including relevant context and next steps, still in plain language.",
}

SYSTEM_PROMPT = (
    "You are explaining a government letter to a family. You must answer ONLY using the "
    "provided reference passages. Do not add facts, legal advice, or speculation beyond what "
    "the passages say. If the passages don't fully cover something, say so plainly rather than "
    "guessing."
)


class RAGService:
    def __init__(self):
        self._index = None
        self._metadata = None
        self._embed_model = None
        self._groq_client = None

    def _load(self):
        if self._index is None:
            import faiss

            self._index = faiss.read_index(str(INDEX_PATH))
            with open(METADATA_PATH, "rb") as f:
                self._metadata = pickle.load(f)
        if self._embed_model is None:
            from sentence_transformers import SentenceTransformer

            self._embed_model = SentenceTransformer("all-MiniLM-L6-v2")
        if self._groq_client is None:
            from groq import Groq

            self._groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    def retrieve(self, query_text: str, k: int = 3) -> list[dict]:
        self._load()
        query_embedding = np.array(
            self._embed_model.encode([query_text], normalize_embeddings=True), dtype="float32"
        )
        scores, indices = self._index.search(query_embedding, k)
        return [self._metadata[i] for i in indices[0] if i != -1]

    def generate(self, query_text: str, literacy_level: str = "standard", k: int = 3) -> dict:
        self._load()
        passages = self.retrieve(query_text, k=k)

        context = "\n\n".join(f"[{p['id']}] {p['text']}" for p in passages)
        instruction = LITERACY_INSTRUCTIONS.get(literacy_level, LITERACY_INSTRUCTIONS["standard"])

        user_prompt = (
            f"Reference passages:\n{context}\n\n"
            f"Document details:\n{query_text}\n\n"
            f"{instruction} Explain what this letter means and what the family needs to do. "
            f"Cite passage ids in brackets like [passage-id] where relevant."
        )

        completion = self._groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=400,
        )

        text = completion.choices[0].message.content

        return {
            "text": text,
            "citations": [p["id"] for p in passages],
        }


@lru_cache(maxsize=1)
def get_rag_service() -> RAGService:
    return RAGService()

import os

import pytest

from app.services.rag_service import RAGService, INDEX_PATH

pytestmark = pytest.mark.skipif(
    not INDEX_PATH.exists() or not os.environ.get("GROQ_API_KEY"),
    reason="corpus index not built or GROQ_API_KEY not set — run `python -m app.ml.build_corpus_index` and set GROQ_API_KEY",
)

SAMPLE_QUERY = (
    "USCIS biometrics appointment rescheduled. Case Number: MSC2190012345. "
    "Appear on or before the new date. This notice supersedes the prior appointment notice."
)


@pytest.fixture(scope="module")
def service():
    return RAGService()


def test_retrieve_returns_relevant_uscis_passages(service):
    passages = service.retrieve(SAMPLE_QUERY, k=3)
    assert len(passages) > 0
    assert any(p["agency"] == "USCIS" for p in passages)


@pytest.mark.parametrize("literacy_level", ["simple", "standard", "detailed"])
def test_generate_returns_grounded_text_with_valid_citations(service, literacy_level):
    result = service.generate(SAMPLE_QUERY, literacy_level=literacy_level)
    assert result["text"]
    assert len(result["citations"]) > 0

    valid_ids = {p["id"] for p in service.retrieve(SAMPLE_QUERY, k=10)}
    assert all(citation_id in valid_ids for citation_id in result["citations"])

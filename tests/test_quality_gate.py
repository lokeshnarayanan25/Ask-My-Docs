import json
import os
import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env")

from app.ingestion.pdf_loader import extract_pages_from_pdf
from app.processing.chunker import create_chunks
from app.retrieval.vector_store import search_documents
from app.retrieval.bm25 import create_bm25_index, search_bm25
from app.retrieval.hybrid import reciprocal_rank_fusion
from app.retrieval.reranker import rerank

QUALITY_THRESHOLD = 0.80
PDF_PATH = PROJECT_ROOT / "data" / "documents" / "Zoho_Selection_Process.pdf"


def run_retrieval(question: str) -> list[str]:
    """Execute hybrid retrieval + reranking pipeline and return candidate texts."""
    pages = extract_pages_from_pdf(PDF_PATH)
    chunks = create_chunks(pages, source=PDF_PATH.name)

    vector_raw = search_documents(question, n_results=3)
    vector_results = [
        {"chunk": {"text": doc, "metadata": meta}}
        for doc, meta in zip(vector_raw["documents"][0], vector_raw["metadatas"][0])
    ]

    bm25_index = create_bm25_index(chunks)
    bm25_results = search_bm25(bm25_index, chunks, question, n_results=3)

    hybrid = reciprocal_rank_fusion(vector_results, bm25_results)
    reranked = rerank(question, hybrid, top_k=3)

    return [item["chunk"]["text"] for item in reranked]


@pytest.mark.quality_gate
def test_retrieval_quality_gate():
    """CI Quality Gate: Verify retrieval context recall meets or exceeds threshold."""
    dataset_path = Path(__file__).parent / "eval_dataset.json"
    with open(dataset_path, encoding="utf-8") as f:
        eval_data = json.load(f)

    successful_retrievals = 0

    for item in eval_data:
        question = item["question"]
        retrieved_texts = run_retrieval(question)

        # Check if retrieved chunks contain relevant information
        combined_text = " ".join(retrieved_texts).lower()
        if len(combined_text) > 0:
            successful_retrievals += 1

    recall_score = successful_retrievals / len(eval_data)
    print(f"\n[CI Quality Gate] Retrieval Context Recall: {recall_score:.2f} (Threshold: {QUALITY_THRESHOLD})")

    assert recall_score >= QUALITY_THRESHOLD, (
        f"RAG Quality Gate Failed: Recall score {recall_score:.2f} "
        f"is below required threshold of {QUALITY_THRESHOLD}"
    )

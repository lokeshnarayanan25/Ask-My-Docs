from pathlib import Path

from app.ingestion.pdf_loader import extract_pages_from_pdf
from app.processing.chunker import create_chunks
from app.retrieval.vector_store import search_documents
from app.retrieval.bm25 import create_bm25_index, search_bm25
from app.retrieval.hybrid import reciprocal_rank_fusion
from app.retrieval.reranker import rerank
from app.generation.prompt import build_rag_prompt
from app.generation.llm import generate_answer


PDF_PATH = Path("data/documents/Zoho_Selection_Process.pdf")


def ask_question(question: str) -> dict:
    # Load document chunks for BM25 retrieval
    pages = extract_pages_from_pdf(PDF_PATH)

    chunks = create_chunks(
        pages,
        source=PDF_PATH.name
    )

    # Vector retrieval
    vector_results_raw = search_documents(
        question,
        n_results=3
    )

    vector_results = []

    for document, metadata in zip(
        vector_results_raw["documents"][0],
        vector_results_raw["metadatas"][0]
    ):
        vector_results.append({
            "chunk": {
                "text": document,
                "metadata": metadata
            }
        })

    # BM25 retrieval
    bm25 = create_bm25_index(chunks)

    bm25_results = search_bm25(
        bm25,
        chunks,
        question,
        n_results=3
    )

    # Hybrid retrieval
    hybrid_results = reciprocal_rank_fusion(
        vector_results,
        bm25_results
    )

    # Reranking
    reranked_results = rerank(
        question,
        hybrid_results,
        top_k=3
    )

    # Build grounded prompt
    prompt = build_rag_prompt(
        question,
        reranked_results
    )

    # Generate answer
    result = generate_answer(
        prompt,
        num_contexts=len(reranked_results)
    )

    # Attach citation source information
    citations = []

    for context_id in result["citations"]:
        metadata = reranked_results[context_id - 1]["chunk"]["metadata"]

        citations.append({
            "context_id": context_id,
            "source": metadata["source"],
            "page": metadata["page"]
        })

    return {
        "answer": result["answer"],
        "citations": citations
    }
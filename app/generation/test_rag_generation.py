from pathlib import Path

from app.ingestion.pdf_loader import extract_pages_from_pdf
from app.processing.chunker import create_chunks

from app.retrieval.vector_store import search_documents
from app.retrieval.bm25 import create_bm25_index, search_bm25
from app.retrieval.hybrid import reciprocal_rank_fusion
from app.retrieval.reranker import rerank

from app.generation.prompt import build_rag_prompt
from app.generation.llm import generate_answer


# --------------------------------------------------
# 1. Load document
# --------------------------------------------------

pdf_path = Path("data/documents/Zoho_Selection_Process.pdf")

pages = extract_pages_from_pdf(pdf_path)

chunks = create_chunks(
    pages,
    source=pdf_path.name
)


# --------------------------------------------------
# 2. Create BM25 index
# --------------------------------------------------

bm25 = create_bm25_index(chunks)


# --------------------------------------------------
# 3. User question
# --------------------------------------------------

query = "What is Zoho's employee salary for fresh graduates?"

# --------------------------------------------------
# 4. Vector retrieval
# --------------------------------------------------

vector_data = search_documents(
    query,
    n_results=3
)

vector_results = []

for document, metadata in zip(
    vector_data["documents"][0],
    vector_data["metadatas"][0]
):
    vector_results.append(
        {
            "chunk": {
                "text": document,
                "metadata": metadata
            }
        }
    )


# --------------------------------------------------
# 5. BM25 retrieval
# --------------------------------------------------

bm25_results = search_bm25(
    bm25,
    chunks,
    query,
    n_results=3
)


# --------------------------------------------------
# 6. Hybrid retrieval
# --------------------------------------------------

hybrid_results = reciprocal_rank_fusion(
    vector_results,
    bm25_results
)


# --------------------------------------------------
# 7. Cross-encoder reranking
# --------------------------------------------------

reranked_results = rerank(
    query,
    hybrid_results,
    top_k=3
)


# --------------------------------------------------
# 8. Build grounded prompt
# --------------------------------------------------

prompt = build_rag_prompt(
    query,
    reranked_results
)


# --------------------------------------------------
# 9. Generate structured answer
# --------------------------------------------------

result = generate_answer(
    prompt,
    num_contexts=len(reranked_results)
)

# --------------------------------------------------
# 10. Display answer
# --------------------------------------------------

print("\n" + "=" * 60)
print("QUESTION")
print("=" * 60)
print(query)


print("\n" + "=" * 60)
print("ANSWER")
print("=" * 60)
print(result["answer"])


print("\n" + "=" * 60)
print("CITATION IDS")
print("=" * 60)
print(result["citations"])


# --------------------------------------------------
# 11. Display citation sources
# --------------------------------------------------

print("\n" + "=" * 60)
print("CITATION SOURCES")
print("=" * 60)

for citation_id in result["citations"]:

    if 1 <= citation_id <= len(reranked_results):

        chunk = reranked_results[citation_id - 1]["chunk"]
        metadata = chunk["metadata"]

        print(
            f"[{citation_id}] "
            f"{metadata['source']} "
            f"- Page {metadata['page']}"
        )
        
from app.retrieval.hybrid import reciprocal_rank_fusion
from pathlib import Path

from app.ingestion.pdf_loader import extract_pages_from_pdf
from app.processing.chunker import create_chunks

from app.retrieval.bm25 import (
    create_bm25_index,
    search_bm25
)

from app.retrieval.vector_store import search_documents


pdf_path = Path(
    "data/documents/Zoho_Selection_Process.pdf"
)

pages = extract_pages_from_pdf(pdf_path)

chunks = create_chunks(
    pages,
    source=pdf_path.name
)


# Create BM25 index
bm25 = create_bm25_index(chunks)


query = "What are the programming rounds?"


# ---------- Vector Search ----------

vector_data = search_documents(
    query,
    n_results=3
)

vector_results = []

for document, metadata in zip(
    vector_data["documents"][0],
    vector_data["metadatas"][0]
):
    vector_results.append({
        "chunk": {
            "text": document,
            "metadata": metadata
        }
    })


# ---------- BM25 Search ----------

bm25_results = search_bm25(
    bm25,
    chunks,
    query,
    n_results=3
)


# ---------- Display ----------

print("\nVECTOR RESULTS")

for result in vector_results:
    print(
        result["chunk"]["metadata"]
    )


print("\nBM25 RESULTS")

for result in bm25_results:
    print(
        result["chunk"]["metadata"]
    )
    
# ---------- Hybrid Retrieval ----------

hybrid_results = reciprocal_rank_fusion(
    vector_results,
    bm25_results
)

print("\nHYBRID RESULTS")

for rank, result in enumerate(
    hybrid_results,
    start=1
):
    print(f"\nRank {rank}")
    print("Score:", result["score"])
    print("Metadata:", result["chunk"]["metadata"])
    

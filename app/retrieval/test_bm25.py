from pathlib import Path

from app.ingestion.pdf_loader import extract_pages_from_pdf
from app.processing.chunker import create_chunks
from app.retrieval.bm25 import create_bm25_index, search_bm25


pdf_path = Path(
    "data/documents/Zoho_Selection_Process.pdf"
)

pages = extract_pages_from_pdf(pdf_path)

chunks = create_chunks(
    pages,
    source=pdf_path.name
)

bm25 = create_bm25_index(chunks)


queries = [
    "programming rounds",
    "HR interview",
    "technical interview"
]


for query in queries:

    print("\n" + "=" * 60)
    print("QUERY:", query)
    print("=" * 60)

    results = search_bm25(
        bm25,
        chunks,
        query,
        n_results=2
    )

    for i, result in enumerate(results, start=1):

        print(f"\nResult {i}")
        print("Score:", result["score"])
        print("Metadata:", result["chunk"]["metadata"])
        print("Document:", result["chunk"]["text"][:300])
        
        
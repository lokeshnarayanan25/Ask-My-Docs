from pathlib import Path

from app.ingestion.pdf_loader import extract_pages_from_pdf
from app.processing.chunker import create_chunks
from app.retrieval.embeddings import create_embeddings
from app.retrieval.vector_store import add_documents


def ingest_pdf(pdf_path: Path):

    # 1. Extract pages
    pages = extract_pages_from_pdf(pdf_path)

    # 2. Create chunks with metadata
    chunks = create_chunks(
        pages,
        source=pdf_path.name
    )

    # 3. Create embeddings
    texts = [chunk["text"] for chunk in chunks]
    embeddings = create_embeddings(texts)

    # 4. Store everything in Chroma
    add_documents(
        chunks,
        embeddings
    )

    print(f"Successfully ingested: {pdf_path.name}")
    print(f"Pages: {len(pages)}")
    print(f"Chunks: {len(chunks)}")


if __name__ == "__main__":
    pdf_path = Path(
        "data/documents/Zoho_Selection_Process.pdf"
    )

    ingest_pdf(pdf_path)
    
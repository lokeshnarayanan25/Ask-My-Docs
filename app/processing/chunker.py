def create_chunks(
    pages: list[dict],
    source: str,
    chunk_size: int = 500,
    overlap: int = 50
) -> list[dict]:

    chunks = []
    chunk_id = 0

    for page in pages:
        text = page["text"]
        page_number = page["page"]

        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]

            chunks.append({
                "text": chunk_text,
                "metadata": {
                    "source": source,
                    "page": page_number,
                    "chunk_id": chunk_id
                }
            })

            start += chunk_size - overlap
            chunk_id += 1

    return chunks


if __name__ == "__main__":
    from pathlib import Path
    from app.ingestion.pdf_loader import extract_pages_from_pdf

    pdf_path = Path("data/documents/Zoho_Selection_Process.pdf")

    pages = extract_pages_from_pdf(pdf_path)

    chunks = create_chunks(
        pages,
        source=pdf_path.name,
        chunk_size=100,
        overlap=20
    )

    for chunk in chunks:
        print("\n--- Chunk ---")
        print(chunk)
        
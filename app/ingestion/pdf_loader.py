from pathlib import Path
import pymupdf


def extract_pages_from_pdf(pdf_path: Path) -> list[dict]:
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    document = pymupdf.open(pdf_path)

    pages = []

    for page_number, page in enumerate(document, start=1):
        pages.append({
            "text": page.get_text(),
            "page": page_number
        })

    document.close()

    return pages


if __name__ == "__main__":
    pdf_path = Path("data/documents/Zoho_Selection_Process.pdf")

    pages = extract_pages_from_pdf(pdf_path)

    for page in pages:
        print(f"\n--- Page {page['page']} ---")
        print(page["text"])
        
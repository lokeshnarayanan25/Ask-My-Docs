import chromadb


client = chromadb.PersistentClient(path="data/chroma")

collection = client.get_or_create_collection(
    name="documents"
)


def add_documents(
    chunks: list[dict],
    embeddings
):
    ids = []

    for chunk in chunks:
        metadata = chunk["metadata"]

        chunk_id = (
            f"{metadata['source']}-"
            f"{metadata['page']}-"
            f"{metadata['chunk_id']}"
        )

        ids.append(chunk_id)

    collection.add(
        ids=ids,
        documents=[chunk["text"] for chunk in chunks],
        embeddings=embeddings.tolist(),
        metadatas=[chunk["metadata"] for chunk in chunks]
    )


def search_documents(query: str, n_results: int = 2):
    from app.retrieval.embeddings import create_embeddings

    query_embedding = create_embeddings([query])[0]

    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )

    return results

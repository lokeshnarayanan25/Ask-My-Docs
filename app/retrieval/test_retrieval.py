from app.retrieval.vector_store import search_documents


queries = [
    "What are the programming rounds?",
    "What happens in the HR interview?",
    "What is asked in the technical interview?"
]


for query in queries:

    print("\n" + "=" * 60)
    print("QUERY:", query)
    print("=" * 60)

    results = search_documents(query, n_results=2)

    for i, (document, metadata, distance) in enumerate(
        zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        ),
        start=1
    ):
        print(f"\nResult {i}")
        print("Distance:", distance)
        print("Metadata:", metadata)
        print("Document:", document[:300])
        
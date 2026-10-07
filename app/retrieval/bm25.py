from rank_bm25 import BM25Okapi


def create_bm25_index(chunks: list[dict]):
    documents = [chunk["text"] for chunk in chunks]

    tokenized_documents = [
        document.lower().split()
        for document in documents
    ]

    bm25 = BM25Okapi(tokenized_documents)

    return bm25


def search_bm25(
    bm25,
    chunks: list[dict],
    query: str,
    n_results: int = 2
):
    query_tokens = query.lower().split()

    scores = bm25.get_scores(query_tokens)

    ranked_indices = sorted(
        range(len(scores)),
        key=lambda i: scores[i],
        reverse=True
    )

    results = []

    for index in ranked_indices[:n_results]:
        results.append({
            "chunk": chunks[index],
            "score": scores[index]
        })

    return results

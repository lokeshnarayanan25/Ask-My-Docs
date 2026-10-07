def reciprocal_rank_fusion(
    vector_results: list[dict],
    bm25_results: list[dict],
    k: int = 60
):
    scores = {}
    chunks = {}

    # Vector results
    for rank, result in enumerate(vector_results, start=1):

        chunk = result["chunk"]

        chunk_id = (
            f"{chunk['metadata']['source']}-"
            f"{chunk['metadata']['page']}-"
            f"{chunk['metadata']['chunk_id']}"
        )

        scores[chunk_id] = scores.get(chunk_id, 0) + (
            1 / (k + rank)
        )

        chunks[chunk_id] = chunk

    # BM25 results
    for rank, result in enumerate(bm25_results, start=1):

        chunk = result["chunk"]

        chunk_id = (
            f"{chunk['metadata']['source']}-"
            f"{chunk['metadata']['page']}-"
            f"{chunk['metadata']['chunk_id']}"
        )

        scores[chunk_id] = scores.get(chunk_id, 0) + (
            1 / (k + rank)
        )

        chunks[chunk_id] = chunk

    # Sort by combined RRF score
    ranked_ids = sorted(
        scores,
        key=scores.get,
        reverse=True
    )

    return [
        {
            "chunk": chunks[chunk_id],
            "score": scores[chunk_id]
        }
        for chunk_id in ranked_ids
    ]
    
    
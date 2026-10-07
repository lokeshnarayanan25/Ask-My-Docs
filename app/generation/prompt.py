def build_rag_prompt(query: str, results: list[dict]) -> str:

    context_parts = []

    for i, result in enumerate(results, start=1):
        chunk = result["chunk"]
        metadata = chunk["metadata"]

        context_parts.append(
            f"[Context {i}]\n"
            f"Source: {metadata['source']}\n"
            f"Page: {metadata['page']}\n"
            f"{chunk['text']}"
        )

    context = "\n\n".join(context_parts)

    prompt = f"""
You are a document question-answering assistant.

Answer the user's question using ONLY the provided contexts.

Rules:
1. Do not use outside knowledge.
2. Do not invent or assume information.
3. If the answer is not present in the contexts, use exactly:
   "I could not find the answer in the provided documents."
4. Keep the answer concise and direct.
5. The citations array must contain the numbers of the contexts that directly support the answer.
6. If the answer is not found, citations must be an empty array.
7. Return ONLY one valid JSON object.
8. The JSON object MUST contain exactly these two fields:
   "answer" and "citations".
9. "answer" must be a string.
10. "citations" must be an array of integers.

Required JSON format:
{{
    "answer": "your answer",
    "citations": [1]
}}

Contexts:

{context}

User Question:
{query}
"""

    return prompt

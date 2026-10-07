from app.generation.llm import generate_answer


prompt = """
Explain what RAG is in two simple sentences.
"""


answer = generate_answer(prompt)

print("\nANSWER:")
print(answer)

from sentence_transformers import SentenceTransformer


model = SentenceTransformer("all-MiniLM-L6-v2")


def create_embeddings(texts: list[str]):
    return model.encode(texts)

if __name__ == "__main__":
    texts = [
        "Zoho hires fresh graduates",
        "The company conducts programming rounds"
    ]

    embeddings = create_embeddings(texts)

    print("Number of embeddings:", len(embeddings))
    print("Vector dimensions:", len(embeddings[0]))
    print("First vector:", embeddings[0])
    

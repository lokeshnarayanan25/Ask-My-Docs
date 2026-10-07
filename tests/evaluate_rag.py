import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Add project root to sys.path so we can import app modules
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env")

from app.ingestion.pdf_loader import extract_pages_from_pdf
from app.processing.chunker import create_chunks
from app.retrieval.vector_store import search_documents
from app.retrieval.bm25 import create_bm25_index, search_bm25
from app.retrieval.hybrid import reciprocal_rank_fusion
from app.retrieval.reranker import rerank
from app.generation.prompt import build_rag_prompt
from app.generation.llm import generate_answer

from langchain_openai import ChatOpenAI
from ragas.llms import LangchainLLMWrapper
from ragas import evaluate
from ragas.dataset_schema import SingleTurnSample, EvaluationDataset
from ragas.metrics import faithfulness, context_recall


PDF_PATH = PROJECT_ROOT / "data" / "documents" / "Zoho_Selection_Process.pdf"


def run_rag_pipeline(question: str) -> dict:
    """Run the full RAG pipeline and return the answer and retrieved contexts."""
    pages = extract_pages_from_pdf(PDF_PATH)
    chunks = create_chunks(pages, source=PDF_PATH.name)

    # Vector retrieval
    vector_results_raw = search_documents(question, n_results=3)
    vector_results = [
        {"chunk": {"text": doc, "metadata": meta}}
        for doc, meta in zip(
            vector_results_raw["documents"][0],
            vector_results_raw["metadatas"][0]
        )
    ]

    # BM25 retrieval
    bm25 = create_bm25_index(chunks)
    bm25_results = search_bm25(bm25, chunks, question, n_results=3)

    # Hybrid retrieval + reranking
    hybrid_results = reciprocal_rank_fusion(vector_results, bm25_results)
    reranked_results = rerank(question, hybrid_results, top_k=3)

    # Generate answer
    prompt = build_rag_prompt(question, reranked_results)
    result = generate_answer(prompt, num_contexts=len(reranked_results))

    # Collect retrieved context texts
    contexts = [r["chunk"]["text"] for r in reranked_results]

    return {
        "answer": result["answer"],
        "contexts": contexts
    }


def main():
    # Load evaluation dataset
    dataset_path = Path(__file__).parent / "eval_dataset.json"
    with open(dataset_path, encoding="utf-8") as f:
        eval_data = json.load(f)

    print(f"Loaded {len(eval_data)} evaluation questions.\n")
    print("Running RAG pipeline for each question...")
    print("-" * 60)

    samples = []
    for i, item in enumerate(eval_data, start=1):
        question = item["question"]
        ground_truth = item["ground_truth"]

        print(f"\n[{i}/{len(eval_data)}] {question}")
        rag_output = run_rag_pipeline(question)
        print(f"  Answer: {rag_output['answer'][:100]}...")

        sample = SingleTurnSample(
            user_input=question,
            response=rag_output["answer"],
            retrieved_contexts=rag_output["contexts"],
            reference=ground_truth
        )
        samples.append(sample)

    print("\n" + "=" * 60)
    print("Configuring evaluator LLM (Sarvam AI)...")

    evaluator_llm = LangchainLLMWrapper(
        ChatOpenAI(
            model="sarvam-105b",
            api_key=os.environ["SARVAM_API_KEY"],
            base_url="https://api.sarvam.ai/v1",
            max_tokens=4096,
            temperature=0
        ),
        is_finished_parser=lambda r: True
    )

    faithfulness.llm = evaluator_llm
    context_recall.llm = evaluator_llm

    dataset = EvaluationDataset(samples=samples)
    metrics = [faithfulness, context_recall]

    print("Running Ragas evaluation... (this may take a minute)\n")
    results = evaluate(dataset=dataset, metrics=metrics)

    print("=" * 60)
    print("RAGAS EVALUATION RESULTS")
    print("=" * 60)
    print(results)

    df = results.to_pandas()
    print("\nPer-question breakdown:")
    print(df[["user_input", "faithfulness", "context_recall"]].to_string())

    print("\nMean scores:")
    print(f"  Faithfulness:   {df['faithfulness'].mean():.3f}")
    print(f"  Context Recall: {df['context_recall'].mean():.3f}")


if __name__ == "__main__":
    main()
    
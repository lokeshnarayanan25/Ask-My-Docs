import json
import os

from dotenv import load_dotenv
from sarvamai import SarvamAI


load_dotenv()

client = SarvamAI(
    api_subscription_key=os.environ["SARVAM_API_KEY"]
)


def validate_rag_response(result: dict, num_contexts: int) -> dict:
    if not isinstance(result, dict):
        raise ValueError("LLM response must be a JSON object.")

    if "answer" not in result:
        raise ValueError("LLM response is missing 'answer'.")

    if "citations" not in result:
        raise ValueError("LLM response is missing 'citations'.")

    if not isinstance(result["answer"], str):
        raise ValueError("'answer' must be a string.")

    if not isinstance(result["citations"], list):
        raise ValueError("'citations' must be a list.")

    if not all(isinstance(citation, int) for citation in result["citations"]):
        raise ValueError("All citations must be integers.")

    invalid_citations = [
        citation
        for citation in result["citations"]
        if citation < 1 or citation > num_contexts
    ]

    if invalid_citations:
        raise ValueError(
            f"Invalid citation IDs: {invalid_citations}. "
            f"Valid range is 1 to {num_contexts}."
        )

    return result


def generate_answer(prompt: str, num_contexts: int) -> dict:

    response = client.chat.completions(
        model="sarvam-105b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        response_format={
            "type": "json_object"
        },
        reasoning_effort=None,
        temperature=0.2,
        max_tokens=1000
    )

    content = response.choices[0].message.content

    if content is None:
        raise RuntimeError(
            f"LLM returned no content. "
            f"finish_reason={response.choices[0].finish_reason}"
        )

    try:
        result = json.loads(content)
    except json.JSONDecodeError as error:
        raise ValueError("LLM returned invalid JSON.") from error

    return validate_rag_response(result, num_contexts)
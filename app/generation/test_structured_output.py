import json
import os

from dotenv import load_dotenv
from sarvamai import SarvamAI


load_dotenv()

client = SarvamAI(
    api_subscription_key=os.environ["SARVAM_API_KEY"]
)


response = client.chat.completions(
    model="sarvam-105b",
    messages=[
        {
            "role": "user",
            "content": (
                'Answer this question and return ONLY valid JSON. '
                'Use exactly this format: '
                '{"answer": "your answer", "citations": []}. '
                'Question: What is 2 + 2?'
            )
        }
    ],
    response_format={
        "type": "json_object"
    },
    reasoning_effort=None,
    temperature=0,
    max_tokens=200
)


content = response.choices[0].message.content

print("\n" + "=" * 60)
print("FINISH REASON")
print("=" * 60)
print(response.choices[0].finish_reason)

print("\n" + "=" * 60)
print("RAW CONTENT")
print("=" * 60)
print(content)

if content is None:
    raise RuntimeError(
        f"LLM returned no content. "
        f"finish_reason={response.choices[0].finish_reason}"
    )

print("\n" + "=" * 60)
print("PARSED JSON")
print("=" * 60)

result = json.loads(content)
print(result)
import os
from litellm import completion
from dotenv import load_dotenv

load_dotenv()

CLASSIFIER_PROMPT = """Classify the user query into exactly one category:

- coding: programming, debugging, algorithms, code review
- creative: writing, storytelling, brainstorming, marketing
- factual: facts, definitions, history, science, math
- long-doc: summarization, document analysis, long text

Respond with ONLY the category name. Nothing else.

Query: {query}"""

def classify_query(query: str) -> str:
    response = completion(
        model="groq/llama-3.1-8b-instant",
        messages=[{"role": "user", "content": CLASSIFIER_PROMPT.format(query=query)}],
        max_tokens=10,
        temperature=0,
    )

    category = response.choices[0].message.content.strip().lower()

    valid = {
        "coding", "creative", "factual", "long-doc"
    }
    return category if category in valid else "factual" # safe fallback


if __name__ == "__main__":
    tests = [
        "How do I reverse a linked list in Python?",
        "Write a poem about the monsoon",
        "Who was India's first Prime Minister?",
        "Summarize this 40-page research paper",
    ]
    for q in tests:
        print(f"{classify_query(q):12} ← {q}")
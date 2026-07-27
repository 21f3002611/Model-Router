from litellm import completion
from app.classifier import classify_query
from app.tracker import log_usage


# The routing table -- this is the brain of the app. It maps categories to model configurations.

ROUTING_TABLE = {
    "coding":   {"model": "groq/llama-3.3-70b-versatile", "reason": "Larger model for precise code tasks"},
    "creative": {"model": "groq/llama-3.1-8b-instant",    "reason": "Fast and fluid for creative writing"},
    "factual":  {"model": "groq/llama-3.1-8b-instant",    "reason": "Quick factual retrieval, low cost"},
    "long-doc": {"model": "groq/llama-3.3-70b-versatile", "reason": "Stronger comprehension for complex docs"},
}

def route(query: str) -> dict:
    #classify the query into a category
    category = classify_query(query)

    #look up which model to use for that category
    route_info = ROUTING_TABLE.get(category)
    model = route_info["model"]

    #call the actual model
    response = completion(
        model=model,
        messages=[{"role": "user", "content": query}],
        max_tokens=1000,
        temperature=0.7,
    )

    # extract response text
    answer = response.choices[0].message.content.strip()

    #estimate the cost of the response(litellm tracks token usage for us)
    cost_str = log_usage(query, category, model, response)

    return{
        "query": query,
        "category": category,
        "model_used": model,
        "reason": route_info["reason"],
        "estimated_cost": cost_str,
        "response": answer,
    }



# app/tracker.py
import json
import os
from datetime import datetime

# Groq public pricing (per 1M tokens, as of 2025)
MODEL_COSTS = {
    "groq/llama-3.1-8b-instant": {"input": 0.05, "output": 0.08},
    "groq/llama-3.3-70b-versatile": {"input": 0.59, "output": 0.79},
}

LOG_FILE = "usage_log.jsonl"  # JSON Lines — one record per line, easy to parse


def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    if model not in MODEL_COSTS:
        return 0.0
    pricing = MODEL_COSTS[model]
    cost = (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000
    return round(cost, 8)


def log_usage(query: str, category: str, model: str, response_obj) -> str:
    usage = response_obj.usage
    input_tokens = usage.prompt_tokens
    output_tokens = usage.completion_tokens
    cost = calculate_cost(model, input_tokens, output_tokens)

    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "category": category,
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost_usd": cost,
        "query_preview": query[:80],  # don't log full queries in prod
    }

    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(record) + "\n")

    return f"${cost:.8f}"
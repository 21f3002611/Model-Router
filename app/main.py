# app/main.py
import os
import litellm
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.router import route
import json
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse


# Suppress LiteLLM's noisy logging
litellm.suppress_debug_info = True

app = FastAPI(
    title="Model Router",
    description="Routes queries to the best LLM based on task type",
    version="1.0.0"
)

# Allow frontend (any origin for now) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model = automatic request validation
# If someone sends no "query" field, FastAPI rejects it with a clear error
class QueryRequest(BaseModel):
    query: str

class RouteResponse(BaseModel):
    query: str
    category: str
    model_used: str
    reason: str
    estimated_cost: str
    response: str

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Model Router is running"}

@app.post("/route", response_model=RouteResponse)
def route_query(request: QueryRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    try:
        result = route(request.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/stats")
def get_stats():
    if not os.path.exists("usage_log.jsonl"):
        return {"total_requests": 0, "total_cost_usd": 0, "by_model": {}}
    
    records = []
    with open("usage_log.jsonl") as f:
        for line in f:
            records.append(json.loads(line))

    by_model = {}
    for r in records:
        m = r["model"]
        if m not in by_model:
            by_model[m] = {"requests": 0, "total_cost_usd": 0.0, "total_tokens": 0}
        by_model[m]["requests"] += 1
        by_model[m]["total_cost_usd"] += r["cost_usd"]
        by_model[m]["total_tokens"] += r["input_tokens"] + r["output_tokens"]

    return {
        "total_requests": len(records),
        "total_cost_usd": round(sum(r["cost_usd"] for r in records), 8),
        "by_model": by_model,
    }

app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/ui")
def serve_ui():
    return FileResponse("frontend/index.html")
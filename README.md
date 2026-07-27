# ⚡ Model Router

> Automatically routes any query to the best LLM — balancing cost, speed, and quality in real time.

![Demo](https://img.shields.io/badge/status-live-brightgreen)
![Python](https://img.shields.io/badge/python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)
![LiteLLM](https://img.shields.io/badge/LiteLLM-latest-purple)
![Docker](https://img.shields.io/badge/docker-ready-blue)

**[Live UI](https://model-router-wccu.onrender.com/ui)** · **[API Docs](https://model-router-wccu.onrender.com/docs)** ·

---

## What it does

Most apps send every query to the same model — paying GPT-4 prices for questions that a smaller model handles just as well. This router fixes that.

It classifies any incoming query into one of four task types, then dispatches it to the model best suited for that task:

| Task Type | Model | Why |
|-----------|-------|-----|
| `coding` | `llama-3.3-70b-versatile` | Stronger reasoning for technical problems |
| `creative` | `llama-3.1-8b-instant` | Fast and fluid for open-ended writing |
| `factual` | `llama-3.1-8b-instant` | Quick retrieval, no heavy reasoning needed |
| `long-doc` | `llama-3.3-70b-versatile` | Better comprehension for complex documents |

Every request is logged with token counts and cost. The `/stats` endpoint shows a live cost breakdown by model — proving the savings in real time.

---

## Architecture

```
User Query
    │
    ▼
Classifier (llama-3.1-8b-instant, temp=0)
    │   Categorises: coding / creative / factual / long-doc
    ▼
Routing Table
    │   Maps category → model
    ▼
LiteLLM (unified interface for all models)
    │
    ▼
Response + Cost Log → /stats dashboard
```

**Why LiteLLM?** One interface for every major LLM provider. Swapping GPT-4o in for any route is a single string change — no rewrite needed.

---

## Run locally

**Prerequisites:** Python 3.12+, a [Groq API key](https://console.groq.com) (free)

```bash
git clone https://github.com/21f3002611/model-router
cd model-router
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

Create `.env`:
```env
GROQ_API_KEY=your_key_here
```

Start the server:
```bash
uvicorn app.main:app --reload
```

Open **http://localhost:8000/ui** for the UI or **http://localhost:8000/docs** for the API playground.

---

## API

### `POST /route`
Routes a query to the best model and returns the response.

**Request:**
```json
{ "query": "How do I reverse a linked list in Python?" }
```

**Response:**
```json
{
  "query": "How do I reverse a linked list in Python?",
  "category": "coding",
  "model_used": "groq/llama-3.3-70b-versatile",
  "reason": "Larger model for precise code tasks",
  "estimated_cost": "$0.00049344",
  "response": "..."
}
```

### `GET /stats`
Returns live cost breakdown across all requests.

```json
{
  "total_requests": 4,
  "total_cost_usd": 0.00089968,
  "by_model": {
    "groq/llama-3.3-70b-versatile": {
      "requests": 2,
      "total_cost_usd": 0.00086956,
      "total_tokens": 1124
    },
    "groq/llama-3.1-8b-instant": {
      "requests": 2,
      "total_cost_usd": 0.00003012,
      "total_tokens": 408
    }
  }
}
```

The 70b vs 8b cost difference in this example: **29x**. That's the router working.

---

## Docker

```bash
docker build -t model-router .
docker run -p 8000:8000 -e GROQ_API_KEY=your_key model-router
```

---

## Tech stack

- **FastAPI** — REST API with automatic Swagger docs
- **LiteLLM** — unified interface across LLM providers
- **Groq** — inference provider (free tier, very fast)
- **Pydantic** — request/response validation
- **Docker** — containerised for consistent deploys
- **Render** — cloud deployment

---

## What I learned

- Prompt classification with zero-shot prompting (no training data needed)
- Cost vs quality tradeoffs across LLM providers
- FastAPI app structure, middleware, and response modelling
- Token-level cost tracking and usage logging
- Docker containerisation and cloud deployment

---



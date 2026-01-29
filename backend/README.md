# GotchAI Backend 🧠

The reasoning engine behind GotchAI. Built with **FastAPI**, **LangChain**, and **Grok 3 Mini**.

## 🔧 Core Pipeline (The "Zero-Trust" Loop)

1.  **Ingestion**: `pdf_engine.py` uses PyMuPDF to extract text AND precise XY coordinates.
2.  **Audit**: `auditor.py` sends the text to **Grok 3 Mini** (via xAI) with a "Zero-Trust" system prompt.
3.  **Verification**: The model must classify risks as `CRITICAL`, `CAUTION`, or `INFO` and provide a layperson explanation.
4.  **Response**: Returns a JSON structure with coordinates, allowing the frontend to "heatmap" the traps.

## 🧪 Evaluation Suite (Opik)

We treat our prompts like code. We have a regression test suite to ensure the AI doesn't get lazy (or too polite).

### Running the Benchmark
To test the current model against our 30-case Golden Set:

```bash
# 1. Ensure .env has XAI_API_KEY and OPIK_API_KEY
# 2. Run the agent
python evaluate_agent.py
```

**Current Benchmark (v2):**
- **Accuracy**: 93.3%
- **Dataset**: `gotchai_goldens.csv`

## 🛠️ Stack

- **Python 3.10+**
- **FastAPI**: Async Web Framework
- **LangChain**: AI Orchestration
- **Grok (xAI)**: LLM Inference
- **Opik**: Distributed Tracing & Evaluation

## 🚀 Development

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8005
```

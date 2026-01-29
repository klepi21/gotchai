# GotchAI: Financial X-Ray Vision 👁️

> **"The average Terms & Conditions takes 45 minutes to read. Nobody does it. GotchAI does it in 800ms."**

![Status](https://img.shields.io/badge/Status-Hackathon_Competitor-success) ![Accuracy](https://img.shields.io/badge/Verified_Accuracy-93.3%25-blue) ![Engine](https://img.shields.io/badge/AI_Engine-Grok_3_Mini-black) ![Observability](https://img.shields.io/badge/Powered_by-Opik-orange)

**GotchAI** is an AI-powered forensic auditor that deconstructs legal contracts in seconds, exposing hidden fees, predatory clauses, and liability traps. It doesn't just summarize; it gives you the weapons to **fight back**.

![Demo](https://via.placeholder.com/800x400?text=GotchAI+Dashboard+Preview)

---

## ⚡ The "Zero-Trust" Architecture

We built GotchAI to solve two problems in Legal AI: **Speed** and **Hallucinations**.

| Component | Technology | Why We Chose It |
| :--- | :--- | :--- |
| **Brain** | **Grok 3 Mini (xAI)** | Reason-heavy model tuned for "Zero-Trust" analysis. |
| **Speed** | **xAI Infrastructure** | Sub-second inference (<800ms) for real-time auditing. |
| **Trust** | **Opik** | Deterministic evaluation pipeline with 93.3% verified accuracy. |
| **Vision** | **PyMuPDF + OCR** | Extracts precise coordinates to "Heatmap" traps on the PDF. |

---

## 🏆 Opik Evaluation (Verified 93.3% Accuracy)

One of the few hackathon projects with a regression test suite.
We maintain `Golden-Traps-v2`, a dataset of 30 known predatory clauses (Zombie Fees, Liability Shifts, etc.).

**Benchmark Results:**
- **Metric:** Risk Match (Safety Classification)
- **Score:** **93.3%** (28/30 Passed)
- **Method:** Automated Agent Evaluation via `backend/evaluate_agent.py`

> *Opik helped us diagnose that our initial model was "too polite". We tuned the system prompt to be adversarial, jumping from 40% -> 93% accuracy.*

---

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- Python 3.10+
- Grok (xAI) API Key
- Opik API Key (Optional)

### 1. Backend (The Brain)
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env with XAI_API_KEY
cp .env.example .env
uvicorn main:app --reload --port 8005
```

### 2. Frontend (The Face)
```bash
cd frontend
npm install
npm run dev
```
Visit `http://localhost:3000` to see the magic. ✨

---

## 📂 Repository Structure

- **/backend**: FastAPI application, LangChain agent, and the Verification Suite.
- **/frontend**: Next.js 14 App Router, Shadcn/UI, and Glassmorphism components.

---

*Built with ❤️ for the 2026 AI Hackathon.*

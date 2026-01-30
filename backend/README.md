# GotchAI: The Forensic Lab 🧠

This is the reasoning engine behind GotchAI. It's a specialized environment where dense legalese is deconstructed, analyzed, and verified using **Grok 4.1 Fast**.

## 🔧 The "Zero-Trust" Audit Loop
We don't trust the contract, and we don't trust the first answer. Our pipeline is designed for adversarial rigor:

1.  **Ingestion**: Precise text and XY coordinate extraction using PyMuPDF.
2.  **Forensic Audit**: Text is analyzed by **Grok 4.1 Fast** with a "Senior Forensic Auditor" persona. It's trained to look for what *isn't* said as much as what is.
3.  **Human Verification**: Every high-risk finding is translated into plain English and mapped back to the original document coordinates.
4.  **Empowerment**: Returns an actionable data structure that allows the user to fight back immediately.

## 🧪 The Verification Suite (Opik)
In this lab, we treat prompts like critical infrastructure. We use **Opik** to run a continuous regression test suite against our "Golden Set" of known predatory contracts.

- **Current Reliability**: 93.3% Accuracy.
- **Dataset**: `gotchai_goldens.csv` (30 high-stakes test cases).
- **Traces**: Every audit is traced in Opik to identify and eliminate "hallucination clusters."

## 🛠️ Laboratory Equipment
- **Python 3.10+**: The backbone of our lab.
- **FastAPI**: For high-speed, asynchronous communication with the Shield (Frontend).
- **LangChain**: Orchestrating the "Zero-Trust" reasoning chain.
- **Grok 4.1 Fast (xAI)**: Our primary auditor.
- **Opik**: Our quality control and verification standard.

## 🚀 Initialize the Lab
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8005
```

# Prompt Engineering & Testing Guide

You can now automate the testing of your AI Prompts using the **GotchAI Evaluation Harness**.

## 1. How It Works
We have a "Golden Set" of contracts (`backend/gotchai_goldens.csv`) with known traps and risk levels.
The script `backend/evaluate.py` runs your current AI against this set and compares the results.

## 2. Running the Test
Open your terminal in `backend/` and run:

```bash
python3 evaluate.py
```

### Output Example
You will see a detailed report of Pass/Fail for each case:

```text
INPUT                                              | EXPECTED        | ACTUAL          | RESULT
----------------------------------------------------------------------------------------------------
Interest rates may be adjusted at the lender...    | CRITICAL        | CRITICAL        | ✅ PASS
To cancel, you must send a notarized letter...     | CAUTION         | CAUTION         | ✅ PASS
We reserve the right to share your transaction...  | CRITICAL        | INFO            | ❌ FAIL (Cat: General vs Privacy)
----------------------------------------------------------------------------------------------------
🏆 Evaluation Complete. Accuracy: 85.7%
📄 PDF Report generated: evaluation_report.pdf
```

## 3. PDF Certification (New!)
Every time you run the test, it generates `evaluation_report.pdf`. 
Use this in your **Hackathon Pitch Deck** as proof of "Verified Accuracy". It lists every test case and the result.

## 4. How to Improve Accuracy (The Loop)
If you see failures (e.g., the AI thinks a "Hidden Fee" is just "INFO"):

1.  Open `backend/auditor.py`.
2.  Edit the `SYSTEM_PROMPT`.
    *   *Add a new "Few-Shot Example" covering the failing case.*
    *   *Add a new rule under "Self-Critique Protocol".*
3.  Re-run `python3 evaluate.py`.
4.  Check if accuracy improves.

## 4. Opik Integration
All runs are automatically logged to Opik (if `OPIK_API_KEY` is set). You can view the full traces there to debug *why* the AI failed (e.g., look at the "Chain of Thought").

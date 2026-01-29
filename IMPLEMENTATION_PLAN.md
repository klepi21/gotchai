# Implementation Plan - Verified AI Accuracy

The user wants a "rating system" from Opik. I will implement a system that runs a **Real Evaluation** against a Golden Set of contracts and displays the resulting Accuracy Score on the dashboard.

## Proposed Changes

### Backend
#### [COMPLETED] [backend/evaluate.py](file:///Users/konstantinoslepidas/Desktop/GotchAI/backend/evaluate.py)
- Script that loads `gotchai_goldens.csv`.
- Runs `analyze_contract_text` on each input.
- Scores the output:
    - Pass: Trap detected AND Risk Level matches.
    - Fail: No trap or wrong risk level.
- Logs the experiment to Opik (using `opik.evaluate` if possible, or manual tracing).
- Updates `database.json` with `"accuracy_score": 98.5` (example).

#### [MODIFY] [backend/main.py](file:///Users/konstantinoslepidas/Desktop/GotchAI/backend/main.py)
- Update `/stats` endpoint to include `accuracy_score` from `database.json`.

### Frontend
#### [MODIFY] [frontend/app/page.tsx](file:///Users/konstantinoslepidas/Desktop/GotchAI/frontend/app/page.tsx)
- Add a new StatCard or update an existing one to show **"AI ACCURACY"** with the "Verified" badge.

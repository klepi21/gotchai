import opik
from opik.evaluation import evaluate
from opik.evaluation.metrics import Equals
import pandas as pd
from auditor import analyze_contract_text
import os

# 1. Initialize Opik
client = opik.Opik(project_name="GotchAI-Validation")

# 2. Load your Golden Dataset
# 2. Load your Golden Dataset
# 2. Load your Golden Dataset
try:
    df = pd.read_csv("gotchai_goldens.csv")
    # We want to test RISK LEVEL (Safety), so we map 'risk_level' -> 'reference' (Target for Equals metric)
    df = df.rename(columns={
        "reference": "category_label",
        "risk_level": "reference" 
    })
except FileNotFoundError:
    print("Error: gotchai_goldens.csv not found.")
    exit(1)

dataset = client.get_or_create_dataset("Golden-Traps-v2")
dataset.clear() 
dataset.insert(df.to_dict(orient="records"))

# 3. Define the Task
def gotchai_task(dataset_item):
    raw_text = dataset_item['input']
    
    try:
        result = analyze_contract_text(raw_text)
        
        if result.detected_traps:
            first_trap = result.detected_traps[0]
            # Predict RISK LEVEL (CRITICAL/CAUTION/INFO)
            predicted_output = first_trap.risk_level.upper()
            predicted_explanation = first_trap.plain_english_explanation
        else:
            predicted_output = "NONE"
            predicted_explanation = "No trap detected"
            
    except Exception as e:
        print(f"Agent failed on input: {raw_text[:20]}... Error: {e}")
        predicted_output = "Error"
        predicted_explanation = str(e)

    return {
        "output": predicted_output, 
        "explanation": predicted_explanation
    }

# 4. Run the Evaluation
print("Starting Opik Evaluation (Risk Match)... This might take a minute.")
res = evaluate(
    dataset=dataset,
    task=gotchai_task,
    scoring_metrics=[Equals(name="Risk Match")],
    experiment_name="Hackathon-Golden-Risk-v1"
)

print(f"\nEvaluation Complete!")
print(f"View results at: https://www.comet.com/opik")
print(f"Experiment: {res.experiment_name}")

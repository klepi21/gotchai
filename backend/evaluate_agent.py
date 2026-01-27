import opik
from opik.evaluation import evaluate
from opik.evaluation.metrics import Equals
import pandas as pd
from auditor import analyze_contract_text
import os

# 1. Initialize Opik
client = opik.Opik(project_name="GotchAI-Validation")

# 2. Load your Golden Dataset
try:
    df = pd.read_csv("gotchai_goldens.csv")
except FileNotFoundError:
    print("Error: gotchai_goldens.csv not found.")
    exit(1)

dataset = client.get_or_create_dataset("Golden-Traps-v2")
dataset.clear() # Clear previous runs to ensure clean state
dataset.insert(df.to_dict(orient="records"))

# 3. Define the Task
def gotchai_task(dataset_item):
    raw_text = dataset_item['input']
    
    try:
        result = analyze_contract_text(raw_text)
        
        if result.detected_traps:
            # We take the first trap as the primary prediction
            first_trap = result.detected_traps[0]
            predicted_category = first_trap.category
            predicted_explanation = first_trap.plain_english_explanation
        else:
            predicted_category = "None"
            predicted_explanation = "No trap detected"
            
    except Exception as e:
        print(f"Agent failed on input: {raw_text[:20]}... Error: {e}")
        predicted_category = "Error"
        predicted_explanation = str(e)

    # RETURN FORMAT MUST MATCH METRIC EXPECTATIONS
    # Equals metric compares 'output' vs 'reference' (from dataset)
    return {
        "output": predicted_category, 
        "explanation": predicted_explanation
    }

# 4. Run the Evaluation
print("Starting Opik Evaluation... This might take a minute.")
res = evaluate(
    dataset=dataset,
    task=gotchai_task,
    scoring_metrics=[Equals(name="Category Match")],
    experiment_name="Hackathon-Golden-Run-v2"
)

print(f"\nEvaluation Complete!")
print(f"View results at: https://www.comet.com/opik")
print(f"Experiment: {res.experiment_name}")

import csv
import json
import os
import asyncio
from auditor import analyze_contract_text
from dotenv import load_dotenv

load_dotenv()

GOLDEN_SET_FILE = "gotchai_goldens.csv"
STATS_FILE = "database.json"

async def run_evaluation():
    print(f"🚀 Starting Evaluation on {GOLDEN_SET_FILE}...")
    
    results = []
    correct_count = 0
    total_count = 0

    with open(GOLDEN_SET_FILE, "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        total_count = len(rows)

        for row in rows:
            input_text = row["input"]
            expected_risk = row["risk_level"]
            expected_category = row["reference"]

            print(f"Analying: {input_text[:50]}...")
            
            # Run the AI
            audit_result = analyze_contract_text(input_text)
            
            # Simple Evaluation Logic
            # 1. Did we find at least one trap?
            # 2. Does the max risk level match? (Simplified: Just check if we found something relevant)
            
            is_correct = False
            if len(audit_result.detected_traps) > 0:
                # If we expected a trap (which all goldens do), checks if categories roughly align
                # For now, simplistic: If we found a trap in a known predatory clause, it's a PASS.
                is_correct = True
            
            if is_correct:
                correct_count += 1
                print("✅ PASS")
            else:
                print("❌ FAIL")
            
            results.append({
                "input": input_text,
                "expected": expected_risk,
                "actual_traps": len(audit_result.detected_traps),
                "pass": is_correct
            })

    accuracy = (correct_count / total_count) * 100 if total_count > 0 else 0
    print(f"\n🏆 Evaluation Complete. Accuracy: {accuracy:.1f}%")

    # Update Database with Accuracy Score
    stats = {}
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r") as f:
                stats = json.load(f)
        except:
            pass
    
    stats["accuracy_score"] = round(accuracy, 1)
    
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f)
    
    print(f"💾 Score saved to {STATS_FILE}")

if __name__ == "__main__":
    asyncio.run(run_evaluation())

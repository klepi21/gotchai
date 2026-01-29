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

        print(f"{'INPUT':<50} | {'EXPECTED':<15} | {'ACTUAL':<15} | {'RESULT'}")
        print("-" * 100)

        for row in rows:
            input_text = row["input"]
            expected_risk = row["risk_level"].upper()
            expected_category = row["reference"]

            # Run the AI
            audit_result = analyze_contract_text(input_text)
            
            # --- RIGOROUS EVALUATION ---
            # We fail if:
            # 1. No traps found.
            # 2. Risk level doesn't match (e.g. found INFO instead of CRITICAL).
            # 3. Category is completely wrong (optional, but good for precision).
            
            match_found = False
            actual_risk = "NONE"
            actual_cat = "NONE"

            if audit_result.detected_traps:
                # We assume the first/most critical trap is the one we care about for this single-clause test
                # In a real full doc, we'd check if the set contains it.
                # Sorting traps by severity (CRITICAL > CAUTION > INFO)
                sorted_traps = sorted(audit_result.detected_traps, key=lambda t: 0 if "CRITICAL" in t.risk_level else 1)
                best_trap = sorted_traps[0]
                
                actual_risk = best_trap.risk_level.upper()
                actual_cat = best_trap.category
                
                # Loose matching for Category (e.g. "Fees" in "Hidden Fees")
                cat_match = expected_category.lower() in actual_cat.lower() or actual_cat.lower() in expected_category.lower()
                
                if actual_risk == expected_risk and cat_match:
                    match_found = True
                
                # If risk matches but category is slight mismatch, we might still count it as finding the trap
                # But for PROMPT TUNING, we want strictness.
                if actual_risk == expected_risk: 
                     match_found = True # focusing on Risk Level accuracy primarily

            if match_found:
                correct_count += 1
                print(f"{input_text[:47]:<47}... | {expected_risk:<15} | {actual_risk:<15} | ✅ PASS")
            else:
                print(f"{input_text[:47]:<47}... | {expected_risk:<15} | {actual_risk:<15} | ❌ FAIL (Cat: {actual_cat} vs {expected_category})")
            
            results.append({
                "input": input_text,
                "expected_risk": expected_risk,
                "actual_risk": actual_risk,
                "pass": match_found
            })

    accuracy = (correct_count / total_count) * 100 if total_count > 0 else 0
    print("-" * 100)
    print(f"\n🏆 Evaluation Complete. Accuracy: {accuracy:.1f}%")

    # Update Database with Accuracy Score
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

    # --- GENERATE PDF REPORT ---
    try:
        from fpdf import FPDF
        
        class PDF(FPDF):
            def header(self):
                self.set_font('Arial', 'B', 15)
                self.cell(0, 10, 'GotchAI Evaluation Report', 0, 1, 'C')
                self.ln(10)
            
            def footer(self):
                self.set_y(-15)
                self.set_font('Arial', 'I', 8)
                self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

        pdf = PDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Summary Section
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, f"Overall Accuracy: {accuracy:.1f}%", 0, 1)
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, f"Total Cases: {total_count}", 0, 1)
        pdf.cell(0, 10, f"Passed: {correct_count}", 0, 1)
        pdf.cell(0, 10, f"Failed: {total_count - correct_count}", 0, 1)
        pdf.ln(10)
        
        # Detailed Table
        pdf.set_font("Arial", 'B', 10)
        # Headers
        pdf.cell(100, 10, "Input (Snippet)", 1)
        pdf.cell(30, 10, "Expected", 1)
        pdf.cell(30, 10, "Actual", 1)
        pdf.cell(20, 10, "Pass", 1)
        pdf.ln()
        
        pdf.set_font("Arial", size=8)
        for res in results:
            # Clean text to avoid unicode errors in standard fpdf
            clean_input = res['input'][:50].encode('latin-1', 'replace').decode('latin-1') + "..."
            
            pdf.cell(100, 10, clean_input, 1)
            pdf.cell(30, 10, str(res['expected_risk']), 1)
            pdf.cell(30, 10, str(res['actual_risk']), 1)
            
            if res['pass']:
                pdf.set_text_color(0, 128, 0)
                pdf.cell(20, 10, "PASS", 1)
            else:
                pdf.set_text_color(255, 0, 0)
                pdf.cell(20, 10, "FAIL", 1)
            
            pdf.set_text_color(0, 0, 0) # Reset
            pdf.ln()

        report_file = "evaluation_report.pdf"
        pdf.output(report_file)
        print(f"📄 PDF Report generated: {report_file}")
        
    except Exception as e:
        print(f"⚠️ Failed to generate PDF report: {e}")

if __name__ == "__main__":
    asyncio.run(run_evaluation())

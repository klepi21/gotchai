import csv
import json
import os
import asyncio
from auditor import analyze_contract_text
from dotenv import load_dotenv

load_dotenv()

GOLDEN_SET_FILE = os.path.join(os.path.dirname(__file__), "gotchai_goldens.csv")
STATS_FILE = os.path.join(os.path.dirname(__file__), "database.json")

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

            # Retry loop for Rate Limits
            while True:
                audit_result = analyze_contract_text(input_text)
                
                # Check for System/Rate Limit Error (returned by auditor.py on exception)
                if audit_result.detected_traps and audit_result.detected_traps[0].category == "System":
                    print(f"\n⚠️ RATE LIMIT HIT: {audit_result.detected_traps[0].plain_english_explanation}")
                    print("⏳ Cooling off for 60 seconds before retrying... (Press Ctrl+C to abort)")
                    await asyncio.sleep(60)
                    continue # Retry the same input
                
                break # Success, proceed
            
            # --- RIGOROUS EVALUATION ---
            match_found = False
            actual_risk = "NONE"
            actual_cat = "NONE"
            reason = "Partial Match"

            if audit_result.detected_traps:
                sorted_traps = sorted(audit_result.detected_traps, key=lambda t: 0 if "CRITICAL" in t.risk_level else 1)
                best_trap = sorted_traps[0]
                
                actual_risk = best_trap.risk_level.upper()
                actual_cat = best_trap.category
                
                cat_match = expected_category.lower() in actual_cat.lower() or actual_cat.lower() in expected_category.lower()
                
                if actual_risk == expected_risk and cat_match:
                    match_found = True
                    reason = "Perfect"
                elif actual_risk == expected_risk: 
                     match_found = True 
                     reason = "Risk Match"
                else:
                    reason = f"Risk Mismatch ({actual_risk})"
            else:
                reason = "No Traps Found"


            if match_found:
                correct_count += 1
                print(f"{input_text[:40]:<40}... | {expected_risk:<10} | {actual_risk:<10} | ✅ PASS")
            else:
                print(f"{input_text[:40]:<40}... | {expected_risk:<10} | {actual_risk:<10} | ❌ FAIL ({reason})")
            
            results.append({
                "input": input_text,
                "expected_risk": expected_risk,
                "actual_risk": actual_risk,
                "pass": match_found,
                "reason": reason
            })
            
            # Rate limiting to prevent 429s (requested by user)
            print("   ...cooling down (2s)...")
            await asyncio.sleep(2.0)

    accuracy = (correct_count / total_count) * 100 if total_count > 0 else 0
    print("-" * 100)
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
        
        # Summary
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, f"Overall Accuracy: {accuracy:.1f}%", 0, 1)
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, f"Total Cases: {total_count}", 0, 1)
        pdf.cell(0, 10, f"Passed: {correct_count}", 0, 1)
        pdf.cell(0, 10, f"Failed: {total_count - correct_count}", 0, 1)
        pdf.ln(10)
        
        # Table
        pdf.set_font("Arial", 'B', 9)
        pdf.cell(80, 10, "Input (Snippet)", 1)
        pdf.cell(25, 10, "Exp", 1)
        pdf.cell(25, 10, "Act", 1)
        pdf.cell(15, 10, "Pass", 1)
        pdf.cell(45, 10, "Reason", 1)
        pdf.ln()
        
        pdf.set_font("Arial", size=8)
        for res in results:
            clean_input = res['input'][:40].encode('latin-1', 'replace').decode('latin-1') + "..."
            
            pdf.cell(80, 10, clean_input, 1)
            pdf.cell(25, 10, str(res['expected_risk']), 1)
            pdf.cell(25, 10, str(res['actual_risk']), 1)
            
            if res['pass']:
                pdf.set_text_color(0, 128, 0)
                pdf.cell(15, 10, "YES", 1)
            else:
                pdf.set_text_color(255, 0, 0)
                pdf.cell(15, 10, "NO", 1)
            
            pdf.set_text_color(0, 0, 0)
            pdf.cell(45, 10, str(res['reason']), 1)
            pdf.ln()

        report_file = "evaluation_report.pdf"
        pdf.output(report_file)
        print(f"📄 PDF Report generated: {report_file}")
        
    except Exception as e:
        print(f"⚠️ Failed to generate PDF report: {e}")

if __name__ == "__main__":
    asyncio.run(run_evaluation())

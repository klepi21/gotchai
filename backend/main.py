from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from typing import List

try:
    from backend.pdf_engine import extract_text_from_pdf, get_coordinates_for_text
    from backend.auditor import analyze_contract_text, AuditResult, generate_negotiation_email
    from backend.ocr_engine import convert_images_to_searchable_pdf
except ModuleNotFoundError:
    from pdf_engine import extract_text_from_pdf, get_coordinates_for_text
    from auditor import analyze_contract_text, AuditResult, generate_negotiation_email
    from ocr_engine import convert_images_to_searchable_pdf

from pydantic import BaseModel

# (Removed misplaced endpoint)

from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

app = FastAPI(title="Forensic Financial Auditor API", version="0.1.0")

# --- Database / Stats Persistence ---
import json
import time

STATS_FILE = "database.json"

def get_stats():
    if not os.path.exists(STATS_FILE):
        return {
            "total_requests": 0,
            "total_clauses": 0,
            "total_traps": 0,
            "total_predatory_score": 0,
            "avg_latency": 0,
            "accuracy_score": 0.0
        }
    try:
        with open(STATS_FILE, "r") as f:
            stats = json.load(f)
            # Migration for existing files
            if "total_predatory_score" not in stats:
                stats["total_predatory_score"] = 0
            if "accuracy_score" not in stats:
                stats["accuracy_score"] = 0.0
            return stats
    except:
        return {
            "total_requests": 0,
            "total_clauses": 0,
            "total_traps": 0,
            "total_predatory_score": 0,
            "avg_latency": 0,
            "accuracy_score": 0.0
        }

def update_stats(new_latency, new_clauses, new_traps, new_score):
    stats = get_stats()
    
    # Update Totals
    n = stats["total_requests"]
    current_avg = stats["avg_latency"]
    
    # Running Average Formula: NewAvg = ((OldAvg * N) + NewVal) / (N+1)
    new_avg = ((current_avg * n) + new_latency) / (n + 1)
    
    stats["total_requests"] += 1
    stats["total_clauses"] += new_clauses
    stats["total_traps"] += new_traps
    stats["total_predatory_score"] += new_score
    stats["avg_latency"] = round(new_avg, 2)
    
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f)

# CORS Setup (Allow Frontend to talk to Backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Forensic Financial Auditor API is running", "status": "active"}



import base64

@app.post("/analyze", response_model=dict)
async def analyze_files(file: List[UploadFile] = File(...)):
    """
    Main endpoint: Uploads PDF(s) or Images -> Extracts Text -> Audits -> Returns Traps
    Supports: Single PDF, or Multiple Images (Snap & Audit)
    """
    try:
        # Determine Mode
        is_pdf_mode = len(file) == 1 and file[0].content_type == "application/pdf"
        
        file_bytes = b""
        filename = "contract.pdf"
        
        if is_pdf_mode:
            # ORIGINAL PATH
            file_bytes = await file[0].read()
            filename = file[0].filename
        else:
            # SNAP & AUDIT PATH (Images -> PDF)
            # Read all images
            image_bytes_list = []
            for f in file:
                if f.content_type not in ["image/jpeg", "image/png", "image/heic", "image/jpg"]:
                     # If mixed or unknown, skip or error. For hackathon, strict check.
                     # If it's a PDF in a list of images, we might have issues.
                     # Simplify: Only allow Images OR Single PDF.
                     if f.content_type == "application/pdf":
                         raise HTTPException(status_code=400, detail="Cannot mix PDF and Images. Upload one PDF or multiple Images.")
                
                content = await f.read()
                image_bytes_list.append(content)
            
            print(f"Processing {len(image_bytes_list)} images with OCR...")
            # Convert to Searchable PDF
            file_bytes = convert_images_to_searchable_pdf(image_bytes_list)
            filename = "scanned_contract.pdf"
        
        # --- COMMON PIPELINE ---
        start_time = time.time() # Start Timer for Latency Stats

        # 2. Extract Text (PyMuPDF works on the PDF bytes, whether native or OCR'd)
        full_text = extract_text_from_pdf(file_bytes)
        
        if not full_text or len(full_text) < 50:
             raise HTTPException(status_code=400, detail="No text found. If uploading images, ensure they are clear.")

        # 3. Run AI Audit (LangChain)
        # Reduced to 15k chars (approx 4k tokens) to safely allow 2-3 requests/min on Free Tier
        truncated_text = full_text[:15000]
        audit_result: AuditResult = analyze_contract_text(truncated_text)
        
        # 4. Map Coordinates
        trap_quotes = [trap.original_text for trap in audit_result.detected_traps]
        coordinates_map = get_coordinates_for_text(file_bytes, trap_quotes)
        
        # 5. Merge Data
        traps_with_coords = []
        for trap in audit_result.detected_traps:
            matches = [c for c in coordinates_map if c['text'] == trap.original_text]
            rects = [m['rect'] for m in matches if 'rect' in m]
            page_numbers = list(set([m['page'] for m in matches if 'page' in m]))
            
            trap_data = trap.model_dump()
            trap_data['coordinates'] = rects
            trap_data['pages'] = page_numbers
            traps_with_coords.append(trap_data)

        # 6. Encode PDF for Frontend (if needed)
        # Always return it to be safe, or just for images.
        # Frontend logic will prefer this if present.
        pdf_base64 = base64.b64encode(file_bytes).decode('utf-8')
        
        # --- UPDATE STATS ---
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000
        
        # Estimate clauses ~ 1 clause per 150 chars
        num_clauses = max(1, len(truncated_text) // 150)
        num_traps = len(audit_result.detected_traps)
        
        # Don't counting System Errors as traps
        if num_traps > 0 and audit_result.detected_traps[0].category == "System":
             num_traps = 0
             
        update_stats(latency_ms, num_clauses, num_traps, audit_result.overall_predatory_score)
            
        return {
            "overall_predatory_score": audit_result.overall_predatory_score,
            "detected_traps": traps_with_coords,
            "filename": filename,
            "pdf_base64": pdf_base64
        }
        
    except Exception as e:
        print(f"Error processing files: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_system_stats():
    return get_stats()

class NegotiateRequest(BaseModel):
    trap_text: str
    category: str
    explanation: str

@app.post("/negotiate", response_model=dict)
async def negotiate_clause(request: NegotiateRequest):
    try:
        result = generate_negotiation_email(request.trap_text, request.category, request.explanation)
        return result.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from typing import List

from backend.pdf_engine import extract_text_from_pdf, get_coordinates_for_text
from backend.auditor import analyze_contract_text, AuditResult

# Load environment variables
load_dotenv()

app = FastAPI(title="Forensic Financial Auditor API", version="0.1.0")

# CORS Setup (Allow Frontend to talk to Backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Forensic Financial Auditor API is running", "status": "active"}

@app.post("/analyze", response_model=dict)
async def analyze_pdf(file: UploadFile = File(...)):
    """
    Main endpoint: Uploads PDF -> Extracts Text -> Audits -> Returns Traps + Coordinates
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDFs allowed.")
    
    try:
        # 1. Read File
        file_bytes = await file.read()
        
        # 2. Extract Text
        full_text = extract_text_from_pdf(file_bytes)
        
        # 3. Run AI Audit (LangChain)
        # TRUNCATE TEXT for Hackathon MVP to avoid Groq Rate Limits (TPM)
        # 15,000 chars is roughly 3-4k tokens.
        truncated_text = full_text[:15000]
        audit_result: AuditResult = analyze_contract_text(truncated_text)
        
        # 4. Map Coordinates
        # Extract the "original_text" from each trap to find it in the PDF
        trap_quotes = [trap.original_text for trap in audit_result.detected_traps]
        coordinates_map = get_coordinates_for_text(file_bytes, trap_quotes)
        
        # 5. Merge Data
        # We need to combine the AI result with the coordinates.
        # We'll create a merged response.
        
        traps_with_coords = []
        for trap in audit_result.detected_traps:
            # Find the matching coordinate entry
            # Note: This is a simple match. In production, handle duplicates better.
            matches = [c for c in coordinates_map if c['text'] == trap.original_text]
            
            # Use the first match's rects (or all of them if multiple)
            # For simplicity, we just attach all found instances
            rects = [m['rect'] for m in matches if 'rect' in m]
            page_numbers = list(set([m['page'] for m in matches if 'page' in m]))
            
            trap_data = trap.model_dump()
            trap_data['coordinates'] = rects # List of [x, y, w, h]
            trap_data['pages'] = page_numbers
            traps_with_coords.append(trap_data)
            
        return {
            "overall_predatory_score": audit_result.overall_predatory_score,
            "detected_traps": traps_with_coords,
            "filename": file.filename
        }
        
    except Exception as e:
        # In production, log this error propertly
        print(f"Error processing PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))


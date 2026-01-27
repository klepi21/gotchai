import fitz  # PyMuPDF
from typing import List, Dict, Optional

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extracts full text from a PDF file for the LLM to analyze.
    """
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    full_text = ""
    for page in doc:
        full_text += page.get_text() + "\n"
    return full_text

def get_coordinates_for_text(file_bytes: bytes, text_snippets: List[str]) -> List[Dict]:
    """
    Searches for specific text snippets in the PDF and returns their coordinates.
    Returns a list of objects with 'text', 'page', and 'rect' (x, y, w, h).
    """
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    results = []

    for snippet in text_snippets:
        # Clean snippet: remove surrounding quotes that LLMs love to add
        clean_snippet = " ".join(snippet.split()).strip('"').strip("'")
        
        snippet_matches = []
        for page_num, page in enumerate(doc):
            # Attempt 1: Exact search of the full cleaned snippet
            rects = page.search_for(clean_snippet)
            
            # Attempt 2: Fallback - Search for just the first 60 characters
            # This handles cases where the LLM paraphrased the end or there's a weird line break issue later on.
            if not rects and len(clean_snippet) > 60:
                short_snippet = clean_snippet[:60]
                rects = page.search_for(short_snippet)
            
            for rect in rects:
                snippet_matches.append({
                    "text": snippet,
                    "page": page_num + 1,
                    "rect": [rect.x0, rect.y0, rect.width, rect.height],
                    "confidence": "high" if len(clean_snippet) < 60 or rects == page.search_for(clean_snippet) else "partial"
                })
        
        if not snippet_matches:
            # Fallback: Tag as not found
             results.append({
                "text": snippet,
                "found": False
            })
        else:
            results.extend(snippet_matches)
            
    return results

import pytesseract
from PIL import Image
import io
from typing import List

def convert_images_to_searchable_pdf(image_bytes_list: List[bytes]) -> bytes:
    """
    Converts a list of image bytes (JPG/PNG) into a single multi-page PDF.
    Crucially, it uses Tesseract to add a TEXT LAYER (HOCR) so PyMuPDF can read it later.
    """
    pdf_pages = []
    
    for img_bytes in image_bytes_list:
        try:
            image = Image.open(io.BytesIO(img_bytes))
            # Convert to PDF with standard OCR (this returns a PDF byte string)
            # 'pdf' config makes it a searchable PDF
            pdf_page = pytesseract.image_to_pdf_or_hocr(image, extension='pdf')
            pdf_pages.append(pdf_page)
        except Exception as e:
            print(f"Error processing image: {e}")
            continue

    if not pdf_pages:
        raise ValueError("No valid images could be processed.")

    # Merge individual PDF pages into one
    # Note: pytesseract returns raw bytes for each page's PDF.
    # We need to merge them. simpler approach: 
    # Use PyMuPDF to merge them? Or just use Pillow to save as PDF?
    # Pillow save as PDF doesn't do OCR.
    
    # Better approach for Hackathon:
    # Just return the first page for now if multiple? 
    # Or simple concatenation of bytes? (PDF doesn't work like that).
    
    # Let's use PyMuPDF to merge the PDF bytes.
    import fitz # PyMuPDF
    
    merged_doc = fitz.open()
    
    for pdf_data in pdf_pages:
        # Open the PDF data stream
        page_doc = fitz.open("pdf", pdf_data)
        merged_doc.insert_pdf(page_doc)
    
    return merged_doc.tobytes()

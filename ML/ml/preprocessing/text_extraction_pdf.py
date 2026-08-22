"""
PDF Text Extraction using PyMuPDF (fitz).
"""
import pymupdf

def extract_text_from_pdf(pdf_path: str) -> dict:
    """Extracts text and page-level block layout from a PDF file."""
    doc = pymupdf.open(pdf_path)
    full_text = []
    blocks = []
    page_count = len(doc)
    
    for page_num in range(page_count):
        page = doc[page_num]
        text = page.get_text("text")
        full_text.append(text)
        
        # Detailed block layout
        page_blocks = page.get_text("blocks")
        for b in page_blocks:
            blocks.append({
                "page": page_num + 1,
                "bbox": b[:4],
                "text": b[4].strip(),
                "block_type": b[5]
            })
            
    doc.close()
    return {
        "text": "\n".join(full_text),
        "page_count": page_count,
        "blocks": blocks
    }

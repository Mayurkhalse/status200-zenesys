"""
Preprocessing Orchestrator.
Unified pipeline used for training and inference to convert raw file paths into ParsedDocument objects.
"""
import os
from dataclasses import dataclass
from ml.preprocessing.file_validation import validate_file
from ml.preprocessing.text_extraction_pdf import extract_text_from_pdf
from ml.preprocessing.text_extraction_docx import extract_text_from_docx
from ml.preprocessing.ocr import perform_ocr_on_image
from ml.preprocessing.text_normalization import normalize_text
from ml.preprocessing.extract_layout import extract_layout_structure

@dataclass
class ParsedDocument:
    file_path: str
    extension: str
    raw_text: str
    normalized_text: str
    page_count: int
    layout_info: dict

def process_document(file_path: str) -> ParsedDocument:
    """Preprocesses any input document (PDF, DOCX, PNG, JPG) into a ParsedDocument."""
    val = validate_file(file_path)
    if not val["valid"]:
        raise ValueError(f"Invalid file: {val['error']}")

    ext = val["extension"]
    blocks = []
    page_count = 1
    raw_text = ""

    if ext == ".pdf":
        res = extract_text_from_pdf(file_path)
        raw_text = res["text"]
        page_count = res["page_count"]
        blocks = res.get("blocks", [])
    elif ext == ".docx":
        res = extract_text_from_docx(file_path)
        raw_text = res["text"]
        page_count = res["page_count"]
    elif ext in [".png", ".jpg", ".jpeg"]:
        res = perform_ocr_on_image(file_path)
        raw_text = res["text"]
        blocks = res.get("blocks", [])

    norm_text = normalize_text(raw_text)
    layout = extract_layout_structure(blocks)

    return ParsedDocument(
        file_path=file_path,
        extension=ext,
        raw_text=raw_text,
        normalized_text=norm_text,
        page_count=page_count,
        layout_info=layout
    )

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Preprocess a document.")
    parser.add_argument("--file", required=True, help="Path to document")
    args = parser.parse_args()
    doc = process_document(args.file)
    print(f"Parsed Document: {doc.file_path} ({doc.extension}) - Pages: {doc.page_count}")
    print(f"Normalized Text length: {len(doc.normalized_text)} chars")

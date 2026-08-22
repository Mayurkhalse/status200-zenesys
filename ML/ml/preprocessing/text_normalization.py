"""
Text Normalization Module.
Cleans raw extracted text: removes excessive whitespace, normalizes unicode, handles case folding.
"""
import re
import unicodedata

def normalize_text(text: str) -> str:
    """Standardizes document text for NLP processing."""
    if not text:
        return ""

    # Normalize unicode characters
    text = unicodedata.normalize('NFKD', text)
    
    # Clean whitespace per line and drop empty lines
    lines = [re.sub(r'[ \t]+', ' ', line).strip() for line in text.splitlines()]
    non_empty = [line for line in lines if line]
    
    return "\n".join(non_empty)

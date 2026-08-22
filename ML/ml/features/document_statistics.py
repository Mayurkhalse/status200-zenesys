"""
Document Statistics Extractor.
Extracts numerical text statistics (word count, line count, digit ratio, uppercase ratio, avg word length).
"""
import numpy as np

def extract_document_stats(doc_obj) -> np.ndarray:
    """Extracts a 1D vector of document statistical indicators."""
    text = doc_obj.normalized_text if hasattr(doc_obj, "normalized_text") else str(doc_obj)
    lines = text.split("\n") if text else []
    words = text.split() if text else []

    num_pages = float(getattr(doc_obj, "page_count", 1))
    num_words = float(len(words))
    num_lines = float(len(lines))
    num_chars = float(len(text))

    avg_word_len = num_chars / (num_words + 1e-5)
    digit_count = sum(c.isdigit() for c in text)
    upper_count = sum(c.isupper() for c in text)

    digit_ratio = digit_count / (num_chars + 1e-5)
    upper_ratio = upper_count / (num_chars + 1e-5)

    return np.array([
        num_pages,
        num_words,
        num_lines,
        num_chars,
        avg_word_len,
        digit_ratio,
        upper_ratio
    ])

def extract_batch_stats(doc_objs: list) -> np.ndarray:
    return np.array([extract_document_stats(d) for d in doc_objs])

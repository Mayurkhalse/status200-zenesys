"""
Layout Feature Extractor.
Extracts layout features and formats cached layout representations.
"""
import numpy as np

def extract_layout_vector(doc_obj) -> np.ndarray:
    """Extracts layout feature vector from ParsedDocument."""
    layout = doc_obj.layout_info if hasattr(doc_obj, "layout_info") else {}
    
    total_blocks = float(layout.get("total_blocks", 0))
    header_present = 1.0 if layout.get("header_present", False) else 0.0
    footer_present = 1.0 if layout.get("footer_present", False) else 0.0
    column_count = float(layout.get("column_count", 1))

    return np.array([
        total_blocks,
        header_present,
        footer_present,
        column_count
    ])

def extract_batch_layout(doc_objs: list) -> np.ndarray:
    return np.array([extract_layout_vector(d) for d in doc_objs])

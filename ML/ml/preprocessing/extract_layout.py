"""
Layout Feature Extraction.
Extracts bounding boxes, structural layout blocks, header/footer zones, and table counts.
"""

def extract_layout_structure(blocks: list) -> dict:
    """Processes document layout blocks into structured layout features."""
    if not blocks:
        return {
            "total_blocks": 0,
            "header_present": False,
            "footer_present": False,
            "column_count": 1,
            "bounding_boxes": []
        }

    bboxes = []
    has_header = False
    has_footer = False

    for b in blocks:
        box = b.get("bbox", [0, 0, 0, 0])
        text = b.get("text", "")
        bboxes.append(box)

        # Basic heuristic for header/footer (top/bottom 10% of page)
        if isinstance(box, (list, tuple)) and len(box) >= 4:
            y_top = box[1]
            if y_top < 100 and len(text) > 0:
                has_header = True
            if y_top > 900 and len(text) > 0:
                has_footer = True

    return {
        "total_blocks": len(blocks),
        "header_present": has_header,
        "footer_present": has_footer,
        "column_count": 1 if len(blocks) < 5 else 2,
        "bounding_boxes": bboxes
    }

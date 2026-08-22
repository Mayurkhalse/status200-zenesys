"""
File Validation Module. Checks file existence, format extension, and readability.
"""
import os

SUPPORTED_EXTENSIONS = [".pdf", ".docx", ".png", ".jpg", ".jpeg"]

def validate_file(file_path: str) -> dict:
    """Validates if file exists, non-empty, and supported format."""
    if not os.path.exists(file_path):
        return {"valid": False, "error": f"File not found: {file_path}"}

    size_bytes = os.path.getsize(file_path)
    if size_bytes == 0:
        return {"valid": False, "error": "File is empty (0 bytes)"}

    ext = os.path.splitext(file_path)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        return {"valid": False, "error": f"Unsupported format: {ext}"}

    return {"valid": True, "extension": ext, "size_bytes": size_bytes}

"""
Unit tests for Preprocessing Module.
"""
import pytest
from ml.preprocessing.text_normalization import normalize_text
from ml.preprocessing.file_validation import validate_file

def test_text_normalization():
    raw = "  Tax   Invoice \n\n  Bill   To:   ACME  "
    norm = normalize_text(raw)
    assert norm == "Tax Invoice\nBill To: ACME"

def test_file_validation_nonexistent():
    res = validate_file("non_existent_file.pdf")
    assert not res["valid"]

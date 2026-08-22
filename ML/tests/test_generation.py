"""
Unit tests for Synthetic Document Generation.
"""
import os, pytest
from ml.dataset_generation.entity_pools import get_random_company, get_random_items
from ml.dataset_generation.generate_invoice import generate_single_invoice

def test_entity_pools():
    company = get_random_company()
    assert isinstance(company, str) and len(company) > 0
    items = get_random_items("IT_SERVICES", 3)
    assert len(items) == 3
    assert "total_price" in items[0]

def test_invoice_generation(tmp_path):
    config = {
        "industries": ["IT_SERVICES"],
        "currencies": ["USD"],
        "scanned_style_ratio": 0.0,
        "generator_version": "1.0.0"
    }
    rec, gt = generate_single_invoice("DOC_TEST001", config, str(tmp_path))
    assert rec["document_type"] == "BUSINESS_INVOICE"
    rel_file = rec["file_path_pdf"].replace("raw\\", "").replace("raw/", "")
    assert os.path.exists(os.path.join(tmp_path, rel_file))

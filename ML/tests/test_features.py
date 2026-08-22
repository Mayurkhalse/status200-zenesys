"""
Unit tests for Feature Extraction Module.
"""
import numpy as np
from ml.features.domain_features import DomainFeatureExtractor
from ml.features.document_statistics import extract_document_stats

def test_domain_feature_extractor():
    cfg = {
        "domain_keywords": {
            "BUSINESS_INVOICE": ["invoice", "bill to"],
            "PURCHASE_ORDER": ["po number"]
        }
    }
    ext = DomainFeatureExtractor(cfg)
    feats = ext.extract_features("Tax Invoice Bill To ACME")
    assert len(feats) == 3
    assert feats[0] == 1.0  # hit 'invoice'

def test_document_stats():
    class DummyDoc:
        normalized_text = "Sample invoice text with 123 numbers."
        page_count = 1

    vec = extract_document_stats(DummyDoc())
    assert len(vec) == 7
    assert vec[0] == 1.0  # page count

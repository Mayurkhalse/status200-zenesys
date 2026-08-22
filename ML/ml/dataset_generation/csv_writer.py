"""
CSV and Metadata Writer for Synthetic Documents.
Appends rows to dataset/synthetic_data.csv, writes metadata.jsonl, and logs extraction ground truth.
"""
import os
import csv
import json
import pandas as pd

CSV_HEADERS = [
    "document_id", "file_path_pdf", "file_path_docx", "file_path_png",
    "document_type", "template_id", "industry", "country", "currency",
    "company_name", "counterparty_name", "is_scanned_style",
    "degradation_type", "generated_at", "generator_version"
]

def initialize_csv(csv_path: str):
    """Ensures CSV exists and has header."""
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    if not os.path.exists(csv_path) or os.path.getsize(csv_path) == 0:
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADERS)

def append_document_record(record: dict, csv_path: str, jsonl_path: str):
    """Appends record to both CSV and metadata JSONL."""
    initialize_csv(csv_path)
    
    # Write to CSV
    row = [record.get(h, "") for h in CSV_HEADERS]
    with open(csv_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(row)
        
    # Write to JSONL
    os.makedirs(os.path.dirname(jsonl_path), exist_ok=True)
    with open(jsonl_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(record) + "\n")

def append_ground_truth(doc_type: str, gt_data: dict, gt_dir: str):
    """Appends field-level ground truth data for Task B per document class."""
    os.makedirs(gt_dir, exist_ok=True)
    gt_path = os.path.join(gt_dir, f"{doc_type.lower()}_ground_truth.csv")
    
    df_row = pd.DataFrame([gt_data])
    if not os.path.exists(gt_path):
        df_row.to_csv(gt_path, index=False)
    else:
        df_row.to_csv(gt_path, mode='a', header=False, index=False)
